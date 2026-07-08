---
title: "센서 퓨전 기초: LiDAR 포인트를 카메라 이미지에 투영하기"
date: 2026-05-12T17:00:00+09:00
draft: false
tags: ["자율주행", "센서퓨전", "LiDAR", "카메라", "Projection", "Depth", "OpenCV", "입문"]
categories: ["자율주행"]
description: "Extrinsic/Intrinsic 변환을 이용해 LiDAR 포인트 클라우드를 카메라 이미지 위에 겹쳐 그리고, 거리(Depth)에 따라 색상을 칠하는 Python 실습입니다."
math: true
---

## 이 글에서 하는 일

LiDAR는 정확한 3D 거리 정보를 줍니다. 카메라는 풍부한 색상과 질감 정보를 줍니다. 두 센서의 강점을 합치는 첫 번째 단계가 **LiDAR 포인트를 카메라 이미지 위에 겹쳐 그리는 것**입니다.

각 포인트에 **거리(Depth)에 따른 색상**을 입히면, 이미지의 어느 픽셀이 얼마나 먼지를 한눈에 볼 수 있습니다. 딥러닝 모델의 입력 데이터를 만들거나, 캘리브레이션 결과를 검증할 때도 필수적으로 쓰입니다.

```
LiDAR 포인트 클라우드 (3D)   +   카메라 이미지 (2D)
             ↓
   Extrinsic: LiDAR → Camera 좌표계 변환
             ↓
   Intrinsic: Camera 3D → 이미지 픽셀 투영
             ↓
   거리(depth)에 따른 컬러맵 적용
             ↓
   LiDAR 포인트가 이미지 위에 색점으로 표시된 결과
```

Lanelet2 투영 글과 파이프라인이 동일합니다. 차이는 투영할 대상이 **맵의 차선**에서 **LiDAR 포인트**로 바뀐 것뿐입니다.

---

## 전체 변환 흐름 복습

좌표계 글에서 배운 흐름입니다. LiDAR 포인트는 **LiDAR 좌표계**에서 시작합니다.

$$\underbrace{P_{\text{lidar}}}_{\text{LiDAR 좌표계}} \xrightarrow{T_{\text{lidar}\to\text{cam}}} \underbrace{P_{\text{cam}}}_{\text{Camera 좌표계}} \xrightarrow{K} \underbrace{(u, v)}_{\text{픽셀 좌표}}$$

$T_{\text{lidar}\to\text{cam}}$은 두 단계의 합성입니다:

$$T_{\text{lidar}\to\text{cam}} = T_{\text{ego}\to\text{cam}} \cdot T_{\text{lidar}\to\text{ego}}$$

- $T_{\text{lidar}\to\text{ego}}$: LiDAR 장착 위치/방향 (Extrinsic Calibration)
- $T_{\text{ego}\to\text{cam}}$: 카메라 장착 위치/방향 (Extrinsic Calibration)

> **Lanelet2 투영과의 차이**: Lanelet2 글에서는 World → Ego → Camera 경로를 썼습니다. 이번에는 LiDAR가 이미 차량(Ego)에 붙어 있으므로 LiDAR → Ego → Camera 경로를 씁니다. 구조는 동일하고 출발 좌표계만 다릅니다.

---

## 주의: 두 센서의 축 방향 차이

LiDAR와 카메라는 축 방향이 다릅니다. 변환 행렬에 이 차이가 정확히 반영되어야 합니다.

| 좌표계 | X | Y | Z |
|---|---|---|---|
| LiDAR | 전방 | 왼쪽 | 위 |
| Camera (OpenCV) | 오른쪽 | 아래 | 전방(광학축) |

---

## Python 실습 코드

실제 LiDAR 데이터 없이도 동작하는 **시뮬레이션 코드**입니다. 실제 데이터 연결 방법은 뒤에서 따로 설명합니다.

```python
import numpy as np
import cv2


# ─────────────────────────────────────────
# 1. 카메라 파라미터 (Intrinsic)
# ─────────────────────────────────────────
IMAGE_W, IMAGE_H = 1280, 720

K = np.array([
    [800.0,   0.0, 640.0],
    [  0.0, 800.0, 360.0],
    [  0.0,   0.0,   1.0],
], dtype=np.float64)

dist_coeffs = np.zeros(5)


# ─────────────────────────────────────────
# 2. LiDAR → Camera 변환 행렬 (Extrinsic)
# ─────────────────────────────────────────
# 가정:
#   LiDAR: 차량 앞 0.0m, 위 1.8m (차체 중앙 기준)
#   카메라: 차량 앞 2.0m, 위 1.5m
#   두 센서 모두 수평 장착 (회전 없음)
#
# LiDAR 좌표계  (X=전방, Y=왼쪽, Z=위)
# Camera 좌표계 (X=오른쪽, Y=아래, Z=전방)

# LiDAR → Ego 변환 (LiDAR 장착 위치)
t_lidar_in_ego = np.array([0.0, 0.0, 1.8])
R_lidar_to_ego = np.eye(3)  # 수평 장착, 회전 없음

T_lidar_to_ego = np.eye(4)
T_lidar_to_ego[:3, :3] = R_lidar_to_ego
T_lidar_to_ego[:3,  3] = t_lidar_in_ego

# Ego → Camera 변환 (카메라 장착 위치 + 축 방향 변환)
t_cam_in_ego = np.array([2.0, 0.0, 1.5])

# 축 방향 변환:
#   Ego X(전방)  → Camera Z(전방)
#   Ego Y(왼쪽) → Camera -X (오른쪽의 반대)
#   Ego Z(위)   → Camera -Y (아래의 반대)
R_ego_to_cam = np.array([
    [ 0, -1,  0],
    [ 0,  0, -1],
    [ 1,  0,  0],
], dtype=np.float64)

T_ego_to_cam = np.eye(4)
T_ego_to_cam[:3, :3] = R_ego_to_cam
T_ego_to_cam[:3,  3] = -R_ego_to_cam @ t_cam_in_ego

# 최종 변환: LiDAR → Camera
T_lidar_to_cam = T_ego_to_cam @ T_lidar_to_ego


# ─────────────────────────────────────────
# 3. 가상 LiDAR 포인트 생성
# ─────────────────────────────────────────
# 실제에서는 .bin 파일이나 ROS 토픽에서 읽어옵니다:
#   points = np.fromfile("000000.bin", dtype=np.float32).reshape(-1, 4)
#
# 여기서는 차량 전방에 격자 형태로 점을 생성합니다.
# LiDAR 좌표계: X=전방, Y=왼쪽, Z=위
rng = np.random.default_rng(seed=42)

x = np.linspace(3.0, 40.0, 60)    # 전방 3~40m
y = np.linspace(-8.0, 8.0, 30)    # 좌우 8m
xx, yy = np.meshgrid(x, y)

# 지면 포인트 (z ≈ -1.8m + 약간의 노이즈)
z_ground = -1.8 + rng.normal(0, 0.05, xx.shape)

# 전방 15m에 세워진 가상 장애물 (박스)
obstacle_x = np.full(20, 15.0) + rng.normal(0, 0.05, 20)
obstacle_y = rng.uniform(-1.0, 1.0, 20)
obstacle_z = rng.uniform(-1.8, 0.5, 20)

ground_pts = np.column_stack([
    xx.ravel(), yy.ravel(), z_ground.ravel(),
    rng.uniform(0.1, 0.4, xx.size)  # intensity (지면은 낮음)
])

obstacle_pts = np.column_stack([
    obstacle_x, obstacle_y, obstacle_z,
    rng.uniform(0.5, 0.9, 20)  # intensity (장애물은 높음)
])

points = np.vstack([ground_pts, obstacle_pts]).astype(np.float32)
print(f"총 포인트 수: {len(points)}")


# ─────────────────────────────────────────
# 4. 포인트 클라우드 → 이미지 투영
# ─────────────────────────────────────────
def depth_to_color(depth: float, min_depth: float = 0.5, max_depth: float = 40.0):
    """
    거리(depth)를 HSV 컬러맵으로 변환합니다.
    가까울수록 빨강(Hue=0), 멀수록 파랑(Hue=240).
    """
    t = np.clip((depth - min_depth) / (max_depth - min_depth), 0.0, 1.0)
    # t=0(가까움) → Hue=0(빨강), t=1(멀음) → Hue=240(파랑)
    hue = int(t * 240)
    hsv = np.uint8([[[hue, 255, 255]]])
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return tuple(int(c) for c in bgr[0, 0])


# 이미지 준비 (실제에서는 카메라 프레임)
img = np.zeros((IMAGE_H, IMAGE_W, 3), dtype=np.uint8)
img[:] = (20, 20, 20)

xyz = points[:, :3]  # (N, 3) — x, y, z만 사용

# 동차 좌표로 변환
ones = np.ones((len(xyz), 1))
pts_h = np.hstack([xyz, ones])          # (N, 4)

# LiDAR → Camera 좌표계 변환
pts_cam = (T_lidar_to_cam @ pts_h.T).T  # (N, 4)
pts_cam = pts_cam[:, :3]                # (N, 3)

# 카메라 앞에 있는 점만 처리 (Z > 0)
front_mask = pts_cam[:, 2] > 0.1
pts_cam_front = pts_cam[front_mask]

# depth = 카메라 광학축 기준 거리 (Camera Z값)
depths = pts_cam_front[:, 2]

# Intrinsic 투영
u = K[0, 0] * (pts_cam_front[:, 0] / depths) + K[0, 2]
v = K[1, 1] * (pts_cam_front[:, 1] / depths) + K[1, 2]

# 이미지 범위 안에 있는 점만 그리기
in_frame = (u >= 0) & (u < IMAGE_W) & (v >= 0) & (v < IMAGE_H)
u_valid = u[in_frame].astype(int)
v_valid = v[in_frame].astype(int)
d_valid = depths[in_frame]

# 멀리 있는 점부터 그려서 가까운 점이 위에 오도록 (z-ordering)
order = np.argsort(d_valid)[::-1]

for idx in order:
    color = depth_to_color(d_valid[idx])
    cv2.circle(img, (u_valid[idx], v_valid[idx]), radius=3, color=color, thickness=-1)

cv2.imwrite("lidar_projection.png", img)
print("저장 완료: lidar_projection.png")
```

---

## 코드 포인트 해설

### depth = Camera 좌표계의 Z값

```python
depths = pts_cam_front[:, 2]
```

카메라 좌표계에서 Z축은 광학 앞 방향입니다. 따라서 **Camera Z = 센서에서 물체까지의 깊이(depth)**입니다. 이 값이 작을수록 가깝고(빨간색), 클수록 멀리(파란색) 있습니다.

### 멀리 있는 점부터 그리기 (Z-ordering)

```python
order = np.argsort(d_valid)[::-1]
```

가까운 점이 먼 점 위에 덮여야 자연스럽습니다. 멀리 있는 점(큰 depth)부터 먼저 그리고, 가까운 점을 나중에 그려서 겹치면 가까운 점이 위에 보이게 합니다.

### 컬러맵: HSV 활용

```python
hue = int((1.0 - t) * 120)
```

Hue(색조) 0은 빨강, 120은 초록, 240은 파랑입니다. `t * 240`으로 설정하면 가까울수록(t=0) Hue=0(빨강), 멀수록(t=1) Hue=240(파랑)이 됩니다. 이 범위를 좁히면(예: `t * 120`) 초록까지만 쓰는 빨강-초록 그라디언트를 만들 수 있습니다.

---

## 실제 데이터로 확장하기

### KITTI 데이터셋으로 바로 실행하기

KITTI는 자율주행 연구에서 가장 많이 쓰이는 공개 데이터셋으로, LiDAR `.bin`과 카메라 이미지, 캘리브레이션 파일을 함께 제공합니다.

```python
import numpy as np
import cv2

def load_kitti_calib(calib_path: str):
    """KITTI calib_velo_to_cam.txt 파일에서 T_lidar_to_cam과 P2를 읽어옵니다."""
    data = {}
    with open(calib_path) as f:
        for line in f:
            key, *vals = line.split()
            data[key.rstrip(":")] = np.array(vals, dtype=np.float64)

    # LiDAR → (rectified) Camera 변환
    Tr = data["Tr_velo_to_cam"].reshape(3, 4)
    T_lidar_to_cam = np.eye(4)
    T_lidar_to_cam[:3, :] = Tr

    # P2: 3×4 투영 행렬 (rectified camera 2 기준)
    # K와 달리 스테레오 보정 오프셋이 포함되어 있으므로 P2 전체를 투영에 사용
    P2 = data["P2"].reshape(3, 4)

    return T_lidar_to_cam, P2


T_lidar_to_cam, P2 = load_kitti_calib("calib_velo_to_cam.txt")
points = np.fromfile("000000.bin", dtype=np.float32).reshape(-1, 4)
img = cv2.imread("000000.png")
IMAGE_H, IMAGE_W = img.shape[:2]

# KITTI 투영: P2 (3×4)를 직접 사용
# pts_cam_h: (N, 4) 동차 좌표 (카메라 좌표계)
# pts_2d = (P2 @ pts_cam_h.T).T  →  (N, 3), u = col0/col2, v = col1/col2
```

> **KITTI `P2` 행렬**: `P2`는 단순 $K$ 행렬이 아니라 스테레오 보정(rectification)과 카메라 오프셋까지 포함한 **3×4 투영 행렬**입니다. 앞 3열만 잘라서 $K$로 쓰면 오프셋 오차가 생기므로, `P2` 전체를 보정된 카메라 좌표에 곱해서 투영해야 합니다.

### ROS 환경에서 실시간으로 처리하기

```python
import rospy
import numpy as np
import cv2
from sensor_msgs.msg import PointCloud2, Image
import sensor_msgs.point_cloud2 as pc2
from cv_bridge import CvBridge

bridge = CvBridge()
latest_image = None

def image_callback(msg):
    global latest_image
    latest_image = bridge.imgmsg_to_cv2(msg, "bgr8")

def lidar_callback(msg):
    if latest_image is None:
        return

    # PointCloud2 메시지에서 x, y, z 추출
    pts = np.array([
        [p[0], p[1], p[2]] for p in pc2.read_points(msg, field_names=("x", "y", "z"))
    ])

    # 이후 투영 로직 적용 ...

rospy.init_node("lidar_projection")
rospy.Subscriber("/camera/image_raw", Image, image_callback)
rospy.Subscriber("/lidar/points", PointCloud2, lidar_callback)
rospy.spin()
```

> **타임스탬프 동기화**: LiDAR와 카메라는 촬영 시각이 정확히 같지 않습니다. 시간 차이가 크면 빠르게 움직이는 물체의 투영이 어긋납니다. ROS에서는 `message_filters.ApproximateTimeSynchronizer`로 두 토픽을 시간 기준으로 동기화합니다.

---

## 흔한 실수와 디버깅

| 증상 | 원인 |
|---|---|
| 포인트가 이미지와 전혀 다른 위치에 찍힘 | Extrinsic의 translation 부호 또는 축 방향 오류 |
| 포인트가 좌우 반전으로 찍힘 | LiDAR Y축(왼쪽) ↔ Camera X축(오른쪽) 부호 처리 오류 |
| 포인트가 위아래 반전으로 찍힘 | LiDAR Z축(위) ↔ Camera Y축(아래) 부호 처리 오류 |
| 포인트가 이미지 전체에 퍼짐 | 카메라 뒤(Z ≤ 0) 포인트를 걸러내지 않음 |
| 가까운 점이 멀리 있는 점 아래에 깔림 | Z-ordering 미적용 |
| 색상이 모두 동일한 색임 | depth 범위(`min_depth`, `max_depth`) 설정 오류 |

**빠른 검증 방법**: 차량 바로 앞 5m 정도에만 있는 점 몇 개를 골라 투영하고, 이미지에서 예상 위치(화면 중앙 아래쪽)에 찍히는지 확인합니다.

---

## 정리

| 단계 | 핵심 |
|---|---|
| **LiDAR → Camera 변환** | $T_{\text{lidar}\to\text{cam}} = T_{\text{ego}\to\text{cam}} \cdot T_{\text{lidar}\to\text{ego}}$ |
| **깊이 필터링** | Camera Z ≤ 0인 점은 반드시 제거 |
| **Intrinsic 투영** | $u = f_x(X/Z) + c_x$, $v = f_y(Y/Z) + c_y$ |
| **Depth 컬러링** | depth → HSV Hue 매핑. 가까울수록 따뜻한 색(빨강), 멀수록 차가운 색(파랑) |
| **Z-ordering** | 멀리 있는 점부터 그려야 가까운 점이 앞에 보임 |

LiDAR의 3D 거리 정보와 카메라의 시각적 맥락이 결합된 이 시각화는 센서 퓨전의 출발점입니다. 다음 단계로는 각 픽셀에 depth 값을 채운 **Depth Map**을 만들거나, LiDAR 포인트의 color를 카메라 이미지에서 가져와 **컬러 포인트 클라우드**를 만드는 방향으로 확장할 수 있습니다.

---

*관련 글: [LiDAR 포인트 클라우드 입문](/docs/autonomous/sensor/lidar-point-cloud-for-beginners/), [카메라 모델 입문](/docs/autonomous/sensor/camera-models-for-beginners/), [좌표계 입문](/docs/autonomous/sensor/ego-coordinate-system-for-beginners/), [Lanelet2 맵을 카메라 이미지에 투영하기](/docs/autonomous/hd-map/lanelet2-projection-to-image/)*
