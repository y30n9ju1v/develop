---
title: "HD 맵에서 센서로: Lanelet2 맵을 카메라 이미지에 투영하기"
date: 2026-05-12T14:00:00+09:00
draft: false
tags: ["자율주행", "Lanelet2", "카메라", "좌표변환", "Projection", "OpenCV", "입문"]
categories: ["자율주행"]
description: "World → Ego → Camera 좌표 변환을 총동원해서 Lanelet2 맵의 차선 경계선을 실제 카메라 이미지에 직접 그려봅니다."
math: true
---

## 이 글에서 하는 일

지금까지 배운 세 가지 이론을 하나로 연결합니다.

1. **Lanelet2**: 차선 경계선의 3D 좌표가 World 좌표계로 저장되어 있음
2. **좌표계 변환**: World → Ego → Camera 변환 행렬(Extrinsic)
3. **카메라 모델**: Camera 3D → 이미지 2D 투영 행렬(Intrinsic, K)

이 세 가지를 차례로 적용하면 **HD 맵의 차선이 카메라 이미지의 어느 픽셀에 보여야 하는지** 계산할 수 있습니다.

```
Lanelet2 맵 (World 좌표계)
        ↓  Extrinsic: World → Camera
카메라 좌표계의 3D 점
        ↓  Intrinsic: Camera 3D → 이미지 2D
이미지의 픽셀 좌표 (u, v)
        ↓  OpenCV로 선 그리기
완성된 투영 이미지
```

---

## 전체 수식 한눈에 보기

카메라 모델 글에서 배운 투영 수식입니다:

$$s \begin{bmatrix} u \\ v \\ 1 \end{bmatrix} = K \cdot \begin{bmatrix} X_c \\ Y_c \\ Z_c \end{bmatrix}$$

여기서 $(X_c, Y_c, Z_c)$는 **카메라 좌표계** 기준의 3D 점입니다. Lanelet2 맵에는 **World 좌표계** 기준의 좌표가 저장되어 있으므로, 먼저 변환이 필요합니다.

$$\begin{bmatrix} X_c \\ Y_c \\ Z_c \\ 1 \end{bmatrix} = T_{\text{world} \to \text{cam}} \begin{bmatrix} X_w \\ Y_w \\ Z_w \\ 1 \end{bmatrix}$$

$T_{\text{world} \to \text{cam}}$은 두 변환의 합성입니다:

$$T_{\text{world} \to \text{cam}} = T_{\text{ego} \to \text{cam}} \cdot T_{\text{world} \to \text{ego}}$$

- $T_{\text{world} \to \text{ego}}$: 차량의 현재 위치/방향 (GPS + IMU로 얻음)
- $T_{\text{ego} \to \text{cam}}$: 카메라의 차량 내 장착 위치/방향 (Extrinsic Calibration으로 측정)

> **핵심**: 이 두 행렬만 있으면 HD 맵의 모든 점을 이미지에 투영할 수 있습니다.

---

## 주의: 카메라 좌표계 축 방향

좌표계 글에서 언급했듯이, **OpenCV 카메라 좌표계**는 일반적인 자율주행 관례와 축 방향이 다릅니다.

| 좌표계 | X | Y | Z |
|---|---|---|---|
| Ego (ROS) | 전방 | 왼쪽 | 위 |
| Camera (OpenCV) | 오른쪽 | 아래 | 전방(광학축) |

Ego → Camera 변환 행렬을 만들 때 이 축 방향 차이를 반드시 반영해야 합니다. 코드에서 실수가 가장 많이 나는 부분입니다.

---

## Python 실습 코드

아래 코드는 실제 카메라 이미지와 Lanelet2 맵이 없어도 **시뮬레이션된 가상 환경**으로 동작하도록 작성했습니다. 개념 이해에 집중하세요.

```python
import numpy as np
import cv2


# ─────────────────────────────────────────
# 1. 카메라 파라미터 (Intrinsic)
# ─────────────────────────────────────────
IMAGE_W, IMAGE_H = 1280, 720

# 카메라 내부 행렬 K (캘리브레이션으로 얻는 값)
K = np.array([
    [800.0,   0.0, 640.0],
    [  0.0, 800.0, 360.0],
    [  0.0,   0.0,   1.0],
], dtype=np.float64)

# 왜곡 계수 (여기서는 왜곡 없다고 가정)
dist_coeffs = np.zeros(5)


# ─────────────────────────────────────────
# 2. 차량 현재 위치/방향 (World → Ego 역변환)
# ─────────────────────────────────────────
# 차량이 World 좌표계 기준으로 (10, 5, 0)에 있고
# yaw(heading) 방향이 0도 (정동쪽)라고 가정

def rotation_z(yaw_rad: float) -> np.ndarray:
    """Z축 기준 회전 행렬 (yaw)"""
    c, s = np.cos(yaw_rad), np.sin(yaw_rad)
    return np.array([
        [ c, -s, 0],
        [ s,  c, 0],
        [ 0,  0, 1],
    ], dtype=np.float64)

vehicle_pos_world = np.array([10.0, 5.0, 0.0])  # 차량 위치 (World)
vehicle_yaw = 0.0                                 # 차량 방향 (rad)

R_ego_in_world = rotation_z(vehicle_yaw)
t_ego_in_world = vehicle_pos_world

# World → Ego 변환 행렬 (차량 위치의 역변환)
# T_world_to_ego = T_ego_in_world^{-1}
R_w2e = R_ego_in_world.T
t_w2e = -R_w2e @ t_ego_in_world

T_world_to_ego = np.eye(4)
T_world_to_ego[:3, :3] = R_w2e
T_world_to_ego[:3,  3] = t_w2e


# ─────────────────────────────────────────
# 3. 카메라 장착 위치/방향 (Ego → Camera Extrinsic)
# ─────────────────────────────────────────
# 카메라가 차량 앞 2m, 위 1.5m에 수평 장착
# Ego 좌표계(X=전방, Y=왼쪽, Z=위) →
# Camera 좌표계(X=오른쪽, Y=아래, Z=전방)

# 카메라 위치 (Ego 좌표계 기준)
t_cam_in_ego = np.array([2.0, 0.0, 1.5])

# 축 방향 변환: Ego → Camera
# Ego X(전방) → Camera Z(전방)
# Ego Y(왼쪽) → Camera X의 반대 방향 → -X
# Ego Z(위)   → Camera Y의 반대 방향 → -Y
R_ego_to_cam = np.array([
    [ 0, -1,  0],   # Camera X = -Ego Y
    [ 0,  0, -1],   # Camera Y = -Ego Z
    [ 1,  0,  0],   # Camera Z =  Ego X
], dtype=np.float64)

T_ego_to_cam = np.eye(4)
T_ego_to_cam[:3, :3] = R_ego_to_cam
T_ego_to_cam[:3,  3] = -R_ego_to_cam @ t_cam_in_ego


# ─────────────────────────────────────────
# 4. 최종 World → Camera 변환 행렬
# ─────────────────────────────────────────
T_world_to_cam = T_ego_to_cam @ T_world_to_ego


# ─────────────────────────────────────────
# 5. Lanelet2 차선 경계선 좌표 (World 좌표계)
# ─────────────────────────────────────────
# 실제에서는 lanelet2 라이브러리로 읽어옵니다:
#
#   import lanelet2
#   from lanelet2.io import load, Origin
#   from lanelet2.projection import UtmProjector
#
#   projector = UtmProjector(Origin(37.5, 127.0))
#   lanelet_map = load("my_map.osm", projector)
#
#   for lanelet in lanelet_map.laneletLayer:
#       left_pts  = [(p.x, p.y, p.z) for p in lanelet.leftBound]
#       right_pts = [(p.x, p.y, p.z) for p in lanelet.rightBound]
#
# 여기서는 직선 도로 2개 차선을 직접 정의합니다.
# 차량(10, 5, 0) 기준으로 앞에 쭉 뻗은 차선

lane_lines_world = [
    # 왼쪽 차선 경계 (실선)
    np.array([
        [12.0,  6.8, 0.0],
        [20.0,  6.8, 0.0],
        [30.0,  6.8, 0.0],
        [40.0,  6.8, 0.0],
    ]),
    # 중앙선 (점선)
    np.array([
        [12.0,  5.0, 0.0],
        [20.0,  5.0, 0.0],
        [30.0,  5.0, 0.0],
        [40.0,  5.0, 0.0],
    ]),
    # 오른쪽 차선 경계 (실선)
    np.array([
        [12.0,  3.2, 0.0],
        [20.0,  3.2, 0.0],
        [30.0,  3.2, 0.0],
        [40.0,  3.2, 0.0],
    ]),
]


# ─────────────────────────────────────────
# 6. 3D 점 → 이미지 픽셀 투영 함수
# ─────────────────────────────────────────
def project_points(points_world: np.ndarray,
                   T_world_to_cam: np.ndarray,
                   K: np.ndarray,
                   img_w: int, img_h: int):
    """
    World 좌표계의 3D 점들을 이미지 픽셀 좌표로 투영합니다.
    카메라 뒤에 있는 점은 None을 반환합니다.
    이미지 밖의 점도 픽셀 좌표를 반환합니다 — 선 연결 시 자연스럽게 화면 가장자리까지 그려지도록.
    """
    # 동차 좌표 (N, 4)
    ones = np.ones((len(points_world), 1))
    pts_h = np.hstack([points_world, ones])  # (N, 4)

    # World → Camera 변환
    pts_cam = (T_world_to_cam @ pts_h.T).T   # (N, 4)
    pts_cam = pts_cam[:, :3]                  # (N, 3)

    result = []
    for X, Y, Z in pts_cam:
        # 카메라 뒤에 있는 점 제거 (Z <= 0)
        # Z가 음수이면 X/Z, Y/Z 부호가 반전되어 완전히 엉뚱한 픽셀이 찍힘
        if Z <= 0.1:
            result.append(None)
            continue

        # Intrinsic 투영: 3D → 2D
        u = K[0, 0] * (X / Z) + K[0, 2]
        v = K[1, 1] * (Y / Z) + K[1, 2]

        result.append((int(u), int(v)))

    return result


# ─────────────────────────────────────────
# 7. 이미지에 차선 그리기
# ─────────────────────────────────────────
# 빈 이미지 (실제에서는 카메라 프레임을 읽어옵니다)
img = np.zeros((IMAGE_H, IMAGE_W, 3), dtype=np.uint8)
img[:] = (30, 30, 30)  # 어두운 회색 배경

# 차선별 색상 정의
colors = [
    (255, 255, 255),  # 왼쪽 경계 — 흰색
    (0, 255, 255),    # 중앙선     — 노란색(BGR)
    (255, 255, 255),  # 오른쪽 경계 — 흰색
]

for lane_pts, color in zip(lane_lines_world, colors):
    pixel_pts = project_points(
        lane_pts, T_world_to_cam, K, IMAGE_W, IMAGE_H)

    # 유효한(None이 아닌) 연속 점들 사이를 선으로 연결
    # cv2.line은 이미지 밖 좌표를 자동으로 클리핑하므로 별도 처리 불필요
    prev = None
    for pt in pixel_pts:
        if pt is not None:
            if prev is not None:
                cv2.line(img, prev, pt, color, thickness=2)
            prev = pt
        else:
            prev = None  # 카메라 뒤 점에서 선을 끊음

cv2.imwrite("lanelet2_projection.png", img)
print("저장 완료: lanelet2_projection.png")
```

---

## 코드에서 핵심만 뽑아보면

### World → Camera 변환은 두 행렬의 곱

```python
T_world_to_cam = T_ego_to_cam @ T_world_to_ego
```

행렬 곱의 순서가 중요합니다. 오른쪽부터 적용됩니다. World 점에 먼저 `T_world_to_ego`를 곱해 Ego 좌표계로 옮긴 뒤, `T_ego_to_cam`을 곱해 Camera 좌표계로 옮깁니다.

### 투영의 핵심 두 줄

```python
u = K[0, 0] * (X / Z) + K[0, 2]   # fx * (X/Z) + cx
v = K[1, 1] * (Y / Z) + K[1, 2]   # fy * (Y/Z) + cy
```

카메라 모델 글의 수식 $u = f_x \cdot \frac{X}{Z} + c_x$가 그대로 코드가 됩니다.

### 카메라 뒤 점 제거

```python
if Z <= 0.1:
    result.append(None)
    continue
```

$Z \leq 0$인 점은 카메라 뒤에 있습니다. 이 점을 투영하면 $X/Z$, $Y/Z$ 값이 뒤집히거나 발산해서 전혀 엉뚱한 픽셀이 찍힙니다. 반드시 걸러야 합니다.

---

## 실제 데이터로 확장하기

위 코드를 실제 데이터와 연결하려면 세 곳만 바꾸면 됩니다.

### 1. 카메라 파라미터를 캘리브레이션 파일에서 읽기

```python
import yaml

with open("camera_info.yaml") as f:
    info = yaml.safe_load(f)

K = np.array(info["camera_matrix"]["data"]).reshape(3, 3)
dist_coeffs = np.array(info["distortion_coefficients"]["data"])
```

### 2. 차량 위치를 로컬라이제이션 결과에서 받기

ROS 환경이라면 `/localization/kinematic_state` 토픽(Autoware 기준)에서 pose를 받아 변환 행렬을 만듭니다.

```python
from scipy.spatial.transform import Rotation

# pose.position, pose.orientation은 ROS 메시지에서 받은 값
t = np.array([pose.position.x, pose.position.y, pose.position.z])
q = [pose.orientation.x, pose.orientation.y,
     pose.orientation.z, pose.orientation.w]

R = Rotation.from_quat(q).as_matrix()

T_ego_in_world = np.eye(4)
T_ego_in_world[:3, :3] = R
T_ego_in_world[:3,  3] = t

T_world_to_ego = np.linalg.inv(T_ego_in_world)
```

> **팁**: 역행렬은 `np.linalg.inv` 대신 좌표계 글에서 소개한 $T^{-1} = \begin{bmatrix} R^\top & -R^\top\mathbf{t} \\ \mathbf{0} & 1 \end{bmatrix}$ 공식을 쓰면 수치적으로 더 안정적입니다.

### 3. Lanelet2 맵에서 차선 좌표를 읽기

```python
import lanelet2
from lanelet2.io import load, Origin
from lanelet2.projection import UtmProjector

projector = UtmProjector(Origin(37.5, 127.0))
lanelet_map = load("my_map.osm", projector)

lane_lines_world = []
for lanelet in lanelet_map.laneletLayer:
    left  = np.array([[p.x, p.y, p.z] for p in lanelet.leftBound])
    right = np.array([[p.x, p.y, p.z] for p in lanelet.rightBound])
    lane_lines_world.append(left)
    lane_lines_world.append(right)
```

---

## 흔한 실수와 디버깅

| 증상 | 원인 |
|---|---|
| 차선이 이미지 전체를 가로지름 | 카메라 뒤의 점을 걸러내지 않음 |
| 차선이 좌우가 뒤집힘 | Ego → Camera 축 방향 변환 부호 오류 |
| 차선이 위아래가 뒤집힘 | Camera Y축이 아래 방향임을 반영하지 않음 |
| 차선이 전혀 보이지 않음 | 행렬 곱 순서 반대 (`T_ego_to_cam @ T_world_to_ego` ↔ 반대로 씀) |
| 차선이 실제보다 많이 치우침 | 차량 위치 또는 카메라 Extrinsic의 translation 오류 |

디버깅할 때는 차량 바로 앞 1~2m의 점 하나만 찍어보고, 예상 픽셀 위치와 비교하는 방법이 가장 빠릅니다.

---

## 왜곡 보정을 포함하려면

실제 카메라는 렌즈 왜곡이 있습니다. OpenCV의 `cv2.projectPoints`를 쓰면 왜곡까지 한 번에 처리됩니다.

`cv2.projectPoints`의 `rvec`/`tvec`는 **Object 좌표계 → Camera 좌표계** 변환입니다. 우리 코드에서 "Object 좌표계"가 곧 World 좌표계이므로 `T_world_to_cam`을 그대로 분해해서 넘깁니다.

```python
# T_world_to_cam의 R, t를 OpenCV 형식으로 변환
rvec, _ = cv2.Rodrigues(T_world_to_cam[:3, :3])  # 3×3 회전 → Rodrigues 벡터
tvec    = T_world_to_cam[:3, 3]                   # 평행 이동 벡터

pts_2d, _ = cv2.projectPoints(
    points_world.astype(np.float64),
    rvec, tvec, K, dist_coeffs
)
# pts_2d: (N, 1, 2) 형태 — pts_2d[:, 0, :] 로 (N, 2) 추출
```

`cv2.projectPoints`는 내부적으로 좌표 변환 → 왜곡 적용 → 픽셀 투영을 수행합니다. 왜곡 계수가 0이면 앞서 직접 작성한 코드와 동일한 결과가 나옵니다.

---

## 정리

| 단계 | 수식 | 코드 |
|---|---|---|
| World → Ego | $T_{\text{w}\to\text{e}}$ (차량 위치/방향의 역변환) | `T_world_to_ego` |
| Ego → Camera | $T_{\text{e}\to\text{c}}$ (카메라 장착 위치 + 축 변환) | `T_ego_to_cam` |
| 합성 변환 | $T_{\text{w}\to\text{c}} = T_{\text{e}\to\text{c}} \cdot T_{\text{w}\to\text{e}}$ | `T_ego_to_cam @ T_world_to_ego` |
| Camera → 픽셀 | $u = f_x(X/Z)+c_x,\ v = f_y(Y/Z)+c_y$ | `K[0,0]*(X/Z)+K[0,2]` |

이론 글에서 분리되어 있던 개념들이 단 하나의 파이프라인으로 합쳐집니다. 각 행렬이 어떤 역할을 하는지 이해하면, 카메라를 교체하거나 차량이 바뀌어도 해당 파라미터만 업데이트하면 됩니다.

---

*관련 글: [카메라 모델 입문](/docs/autonomous/sensor/camera-models-for-beginners/), [좌표계 입문](/docs/autonomous/sensor/ego-coordinate-system-for-beginners/), [Lanelet2 입문](/docs/autonomous/hd-map/lanelet2-for-beginners/)*
