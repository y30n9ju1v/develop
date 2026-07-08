---
title: "자율주행 좌표계 입문: Ego, World, Sensor 좌표계"
date: 2026-05-12T10:00:00+09:00
draft: false
tags: ["자율주행", "좌표계", "Ego", "카메라", "LiDAR", "입문"]
categories: ["자율주행"]
description: "자율주행에서 자주 등장하는 Ego, World, Sensor 좌표계의 개념과 관계를 초보자도 이해할 수 있게 설명합니다."
math: true
---

## 왜 좌표계가 여러 개인가요?

자율주행 코드를 처음 접하면 좌표계가 여러 개 등장해서 혼란스럽습니다.

- "이 물체가 카메라 기준으로 앞 10m에 있다"
- "이 물체가 차량 기준으로 오른쪽 2m에 있다"
- "이 물체가 지도 기준으로 위도 37.5도, 경도 127.0도에 있다"

세 문장 모두 같은 물체를 가리킬 수 있습니다. 기준점이 다를 뿐입니다. 자율주행 시스템은 카메라, LiDAR, GPS 등 여러 센서를 동시에 쓰는데, 각 센서가 서로 다른 기준점으로 위치를 측정합니다. 이 측정값들을 하나로 합치려면 좌표계 사이의 변환이 반드시 필요합니다.

---

## 세 가지 주요 좌표계

자율주행에서 가장 자주 등장하는 좌표계는 세 가지입니다.

| 좌표계 | 기준점 | 용도 |
|---|---|---|
| **World 좌표계** | 지도의 고정된 원점 | GPS 위치, HD 맵, 전역 경로 계획 |
| **Ego 좌표계** | 차량 중심 | 주변 물체의 상대 위치, 경로 추적 |
| **Sensor 좌표계** | 각 센서의 중심 | 센서 원시 데이터 |

---

## World 좌표계

**World 좌표계**는 지도 위의 고정된 원점을 기준으로 하는 좌표계입니다. 차량이 움직여도 원점은 바뀌지 않습니다.

실제로는 GPS 기반의 **UTM(Universal Transverse Mercator)** 좌표계나 **WGS84(위도/경도)** 좌표계를 많이 씁니다. Lanelet2 맵의 모든 좌표가 World 좌표계로 저장됩니다.

World 좌표계는 보통 **오른손 좌표계**로 정의합니다. UTM 기준으로 X=동(East), Y=북(North), Z=위(Up)가 일반적입니다.

**특징:**
- 차량이 움직여도 좌표가 바뀌지 않음
- HD 맵, 신호등, 차선 등 모든 고정 요소가 이 좌표계로 저장됨
- GPS로 측정한 차량 위치가 이 좌표계의 값

---

## Ego 좌표계

**Ego 좌표계**는 차량 자체를 원점으로 하는 좌표계입니다. 차량이 움직이면 원점도 함께 이동합니다.

원점은 프로젝트마다 다르게 정의됩니다. ROS에서는 `base_link`(차체 기준점), Autoware에서는 `base_footprint`(지면 투영점)를 씁니다. 같은 차라도 프레임워크가 다르면 원점이 달라지므로, 코드를 볼 때 반드시 어느 프레임이 원점인지 확인해야 합니다.

```
Ego 좌표계 (차량 위에서 내려다본 모습)

        X (앞)
        ↑
        │
        │    차량
  Y ←───┼───
(왼쪽)  │
        │
        Z (위쪽, 화면 밖으로)
```

자율주행에서 가장 흔히 쓰이는 축 방향:
- **X축**: 차량 전방
- **Y축**: 차량 왼쪽
- **Z축**: 위쪽

> **주의**: 이 축 방향은 표준이 아닙니다. ROS는 X=전방, Y=왼쪽, Z=위쪽을 쓰지만, 일부 시스템은 X=오른쪽, Y=전방을 쓰기도 합니다. 코드를 볼 때 반드시 해당 프로젝트의 좌표계 정의를 확인하세요.

**특징:**
- 차량 기준 상대 위치를 표현하기 쉬움. "앞 10m, 오른쪽 2m"가 직관적
- 차량이 이동하면 World 좌표계 기준 값이 계속 바뀜
- 충돌 회피, 경로 추적 등 제어 알고리즘에서 주로 사용

---

## Sensor 좌표계

각 센서는 자신의 장착 위치를 원점으로 하는 **Sensor 좌표계**를 가집니다.

- **카메라 좌표계** (OpenCV 기준): 렌즈 광학 중심이 원점. X=오른쪽, Y=아래, Z=전방. Y축이 아래를 향하는 이유는 이미지 픽셀 좌표가 왼쪽 위가 원점이고 아래로 증가하는 관례를 따르기 때문입니다.
- **LiDAR 좌표계**: 센서 회전 중심이 원점. X=전방, Y=왼쪽, Z=위쪽. 로봇공학의 오른손 좌표계 관례를 따릅니다.

```
카메라 좌표계 (OpenCV)    LiDAR 좌표계

 원점──── X (오른쪽)       Z (위쪽)
  │                        │
  Y (아래쪽)         Y ────원점──── X (전방)
  │                  (왼쪽)
  Z (전방, 화면 안으로)
```

카메라와 LiDAR는 **같은 물체를 서로 다른 좌표로 표현합니다**. 두 센서의 데이터를 합치려면 변환이 필요합니다.

> **ROS 사용자 주의**: ROS에서 카메라는 `camera_link`(X=전방, Z=위)와 `camera_optical_frame`(X=오른쪽, Y=아래, Z=전방) 두 프레임을 함께 씁니다. 이 글에서는 OpenCV와 동일한 `camera_optical_frame` 기준으로 설명합니다.

---

## 좌표계 변환: Rotation과 Translation

좌표계 사이의 변환은 두 가지 요소로 이루어집니다.

- **Translation(평행 이동)**: 원점이 얼마나 떨어져 있는가
- **Rotation(회전)**: 축이 얼마나 회전되어 있는가

예를 들어 카메라가 차량 앞범퍼 중앙에 달려 있고, 차량 앞을 향해 수평으로 장착되어 있다면:
- Translation: 차량 원점에서 카메라까지의 거리 (예: 앞으로 2m, 위로 1.5m)
- Rotation: 카메라가 차량 축 대비 회전된 각도 (예: 수평 장착이면 회전 없음)

이 두 가지를 행렬로 표현한 것이 **변환 행렬(Transformation Matrix)**입니다.

$$T = \begin{bmatrix} R & \mathbf{t} \\ \mathbf{0} & 1 \end{bmatrix}$$

> **실무 팁: 오일러 각과 쿼터니언**
> 수학적으로는 $3\times3$ 회전 행렬($R$)을 쓰지만, ROS(`tf2`)나 실제 코드에서는 메모리를 적게 쓰고 짐벌 락(Gimbal Lock) 현상을 피하기 위해 **오일러 각(Roll, Pitch, Yaw)**이나 4차원 벡터인 **쿼터니언(Quaternion, $x, y, z, w$)**을 훨씬 더 자주 사용합니다.

- $R$: 3×3 회전 행렬
- $\mathbf{t}$: 3×1 평행 이동 벡터
- 전체 행렬은 4×4

좌표 변환은 이렇게 적용합니다:

$$\begin{bmatrix} x' \\ y' \\ z' \\ 1 \end{bmatrix} = T \begin{bmatrix} x \\ y \\ z \\ 1 \end{bmatrix}$$

**역변환(B→A)**이 필요할 때는 $T^{-1}$을 씁니다. `np.linalg.inv(T)`로 계산해도 되지만, 회전 행렬의 성질을 이용한 방식이 수치적으로 더 안정적입니다:

$$T^{-1} = \begin{bmatrix} R^\top & -R^\top\mathbf{t} \\ \mathbf{0} & 1 \end{bmatrix}$$

---

## 전체 변환 흐름

자율주행 시스템에서 데이터가 처리되는 전형적인 변환 흐름입니다.

```
LiDAR 원시 데이터 (LiDAR 좌표계)
        ↓  T_lidar→ego (LiDAR→Ego 변환)
Ego 좌표계의 포인트 클라우드
        ↓  T_ego→world (차량 위치/방향으로 결정)
World 좌표계의 포인트 클라우드
        ↓  HD 맵과 매칭
위치 추정 결과
```

카메라와 LiDAR를 함께 쓰는 경우:

```
카메라 이미지 (Camera 좌표계)  +  LiDAR 포인트 (LiDAR 좌표계)
        ↓  T_camera→ego              ↓  T_lidar→ego
            ↘                      ↙
              Ego 좌표계에서 융합
```

---

## Extrinsic Calibration

센서 좌표계 → Ego 좌표계 변환에 필요한 $T$ 행렬을 측정하는 과정을 **Extrinsic Calibration(외부 캘리브레이션)**이라고 합니다. 카메라 렌즈 자체의 특성을 측정하는 Intrinsic Calibration과 구분됩니다.

| 캘리브레이션 종류 | 측정 대상 | 결과 |
|---|---|---|
| **Intrinsic** | 렌즈 특성 | $K$ 행렬, 왜곡 계수 |
| **Extrinsic** | 센서 장착 위치/방향 | $R$, $\mathbf{t}$ (변환 행렬) |

차량에 카메라를 새로 장착하거나 충격으로 위치가 바뀌면 Extrinsic Calibration을 다시 해야 합니다.

측정 방법은 보통 두 가지입니다. 첫째, 체커보드나 타깃 마커를 차량 앞에 놓고 카메라와 LiDAR가 동시에 관측한 결과를 비교해 $R$, $\mathbf{t}$를 추정합니다. 둘째, 차량의 CAD 설계 도면에서 센서 장착 위치를 직접 읽어 사용합니다. 전자가 더 정밀하고, 후자는 빠른 초기값으로 활용합니다.

> **참고**: LiDAR의 3D 포인트 클라우드를 Camera의 2D 이미지 위에 겹쳐서 그리기(Projection) 위해서는, 여기서 구한 **Extrinsic 행렬($T$)**로 포인트를 카메라 좌표계로 옮긴 뒤, 렌즈의 특성을 나타내는 **Intrinsic 행렬($K$)**을 한 번 더 곱해주어야 합니다. (관련 내용: [카메라 모델 입문](/docs/autonomous/sensor/camera-models-for-beginners/))

---

## Python 코드: 좌표계 변환

```python
import numpy as np

def make_transform_matrix(rotation, translation):
    """회전 행렬과 평행 이동 벡터로 4×4 변환 행렬 생성"""
    T = np.eye(4)
    T[:3, :3] = rotation
    T[:3, 3] = translation
    return T

def transform_points(points, T):
    """포인트 클라우드를 변환 행렬로 변환
    points: (N, 3) 배열
    T: (4, 4) 변환 행렬
    """
    # 동차 좌표로 변환 (N, 3) → (N, 4)
    ones = np.ones((len(points), 1))
    points_h = np.hstack([points, ones])

    # 변환 적용
    transformed = (T @ points_h.T).T

    return transformed[:, :3]


# 예시: LiDAR가 차량 앞 0.5m, 위 1.8m에 수평 장착된 경우
R = np.eye(3)  # 회전 없음 (수평 장착)
t = np.array([0.5, 0.0, 1.8])  # 앞 0.5m, 위 1.8m

T_lidar_to_ego = make_transform_matrix(R, t)

# LiDAR 좌표계의 포인트를 Ego 좌표계로 변환
lidar_points = np.array([
    [5.0, 0.0, 0.0],   # 전방 5m
    [10.0, 2.0, 0.0],  # 전방 10m, 왼쪽 2m
])

ego_points = transform_points(lidar_points, T_lidar_to_ego)
print("Ego 좌표계:", ego_points)
# [[5.5  0.   1.8]
#  [10.5  2.   1.8]]
```

---

## 정리

| 개념 | 한 줄 요약 |
|---|---|
| **World 좌표계** | 지도에 고정된 기준. GPS, HD 맵이 이 좌표계를 사용 |
| **Ego 좌표계** | 차량이 원점. 차량이 움직이면 원점도 이동 |
| **Sensor 좌표계** | 각 센서가 원점. 센서 원시 데이터가 이 좌표계로 표현됨 |
| **변환 행렬 T** | Rotation + Translation을 묶은 4×4 행렬. 좌표계 간 변환에 사용 |
| **Extrinsic Calibration** | 센서의 장착 위치/방향을 측정해서 변환 행렬 $T$를 구하는 과정 |

자율주행 코드에서 좌표계 버그는 매우 흔합니다. "이 좌표가 어느 좌표계 기준인가"를 항상 명시적으로 관리하는 습관이 중요합니다. 변수명에 `_ego`, `_world`, `_cam` 같은 접미사를 붙이는 것만으로도 혼란을 크게 줄일 수 있습니다.

---

*관련 글: [카메라 모델 입문](/docs/autonomous/sensor/camera-models-for-beginners/), [Lanelet2 입문](/docs/autonomous/hd-map/lanelet2-for-beginners/)*
