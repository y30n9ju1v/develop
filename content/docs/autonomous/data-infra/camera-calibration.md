---
title: "카메라 캘리브레이션: 내부 파라미터와 외부 파라미터"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["autonomous", "camera", "calibration", "intrinsics", "extrinsics", "pinhole", "ftheta"]
categories: ["autonomous"]
description: "핀홀 카메라 모델, 내부 파라미터(fx, fy, cx, cy), 외부 파라미터(SE3), FTheta까지 — py123d 파서와 NuRec 연동에서 등장하는 카메라 캘리브레이션 개념을 정리합니다."
---

> 핀홀·피쉬아이·FTheta 모델의 원리, 왜곡 계수 체계, OpenCV 캘리브레이션 코드는 [카메라 모델 입문](/docs/autonomous/sensor/camera-models-for-beginners/)을 먼저 읽으세요. 이 글은 파이프라인 관점(py123d PinholeCameraMetadata, SE3 외부 파라미터, 카메라-LiDAR 합성)에 집중합니다.

> 이 글은 [SE3 변환과 쿼터니언](../se3-transform-quaternion/)을 먼저 읽으면 외부 파라미터 부분이 더 자연스럽게 이해됩니다.

py123d 파서를 작성하다 보면 `PinholeIntrinsics(fx, fy, cx, cy)`, `camera_to_imu_se3`, `PinholeDistortion(k1, k2, p1, p2)` 같은 값을 채워야 합니다. CARLA 시뮬레이터 연동에서는 120fov 광각 카메라와 30fov 망원 카메라의 차이를 이야기합니다. NuRec 변환에서는 nuScenes의 Pinhole 모델이 NCore의 FTheta 모델과 다르다고 합니다.

캘리브레이션을 모르면 이 값들이 그냥 숫자처럼 느껴집니다. 이 글은 그 숫자가 무엇을 의미하는지 직관부터 설명합니다.

---

## 1. 카메라는 3D 세계를 2D로 투영한다

카메라의 본질적인 역할은 **3D 공간을 2D 이미지 평면으로 투영**하는 것입니다. 깊이 정보가 이 과정에서 사라집니다. LiDAR와 달리 카메라만으로는 물체가 얼마나 멀리 있는지 직접 알 수 없습니다.

캘리브레이션은 이 투영 과정을 수학적으로 모델링하는 것입니다. 모델이 있으면:

- 이미지의 픽셀 좌표 → 카메라 좌표계의 광선(ray) 방향을 계산할 수 있습니다.
- LiDAR 포인트(3D)를 카메라 이미지 위에 투영할 수 있습니다 (컬러 포인트 클라우드).
- 두 카메라의 에피폴라 기하학을 이용해 깊이를 추정할 수 있습니다 (스테레오 비전).

---

## 2. 핀홀 카메라 모델

가장 기본적이고 널리 쓰이는 모델입니다. 이름은 빛이 바늘구멍(pinhole) 하나를 통해 들어와 반대편 필름에 상을 맺는 것에서 왔습니다.

### 투영 과정

3D 점 P = (X, Y, Z)가 카메라 좌표계에 있을 때 (카메라가 원점, Z가 광축 방향), 이미지 픽셀 좌표 (u, v)는:

```
u = fx · (X/Z) + cx
v = fy · (Y/Z) + cy
```

또는 행렬로:

```
⎡ u ⎤       ⎡ fx   0  cx ⎤   ⎡ X/Z ⎤
⎢ v ⎥  =    ⎢  0  fy  cy ⎥ · ⎢ Y/Z ⎥
⎣ 1 ⎦       ⎣  0   0   1 ⎦   ⎣  1  ⎦
```

가운데 3×3 행렬이 **내부 파라미터 행렬 K** (Camera Intrinsic Matrix)입니다.

---

## 3. 내부 파라미터 (Intrinsics)

### 초점 거리: fx, fy

**fx, fy**는 픽셀 단위의 초점 거리입니다. 렌즈에서 이미지 센서까지의 물리적 거리를 픽셀 크기로 나눈 값입니다.

**직관**: fx가 클수록 같은 거리의 물체가 이미지에서 더 크게 보입니다. 망원 렌즈일수록 fx가 큽니다.

```
시야각(FoV) ↕ ←→ fx ↕
좁은 시야각 (망원)  = 큰 fx
넓은 시야각 (광각)  = 작은 fx
```

수평 FoV와 fx의 관계:
```
FoV_horizontal = 2 · arctan(width / (2 · fx))
```

CARLA의 30fov 카메라(망원)와 120fov 카메라(광각)의 차이가 바로 fx 값의 차이입니다. 30fov는 fx가 크고, 120fov는 fx가 작습니다.

fx ≠ fy인 경우는 이미지 센서의 픽셀이 정사각형이 아닐 때 발생합니다. 최근 카메라는 대부분 fx ≈ fy입니다.

### 주점: cx, cy

**cx, cy**는 이미지 좌표계의 원점, 즉 광축이 이미지 평면과 만나는 점(principal point)의 픽셀 좌표입니다.

이상적으로는 이미지의 정중앙이어야 하지만, 제조 오차로 인해 실제로는 약간 벗어납니다. 1280×720 이미지에서 cx = 641.2, cy = 359.8처럼 중앙에서 조금 어긋납니다.

### 왜곡 계수: k1, k2, p1, p2

현실의 렌즈는 핀홀처럼 완벽하지 않습니다. 렌즈 중앙과 가장자리에서 빛이 굴절되는 정도가 달라 **렌즈 왜곡(Lens Distortion)**이 생깁니다.

**방사 왜곡(Radial Distortion)**: 이미지가 배럴처럼 부풀거나(배럴 왜곡) 핀쿠션처럼 오므라드는 현상입니다. k1, k2로 표현합니다.

```
배럴 왜곡 (k1 < 0): 이미지 가장자리가 바깥으로 부풀어 오름
핀쿠션 왜곡 (k1 > 0): 이미지 가장자리가 안쪽으로 오므라듦
```

**접선 왜곡(Tangential Distortion)**: 렌즈가 이미지 센서와 완벽하게 평행하지 않아 생기는 왜곡입니다. p1, p2로 표현합니다.

광각 렌즈일수록 왜곡이 심합니다. 딥러닝 모델을 학습할 때 왜곡 보정(undistortion)을 먼저 적용할지, 아니면 모델이 왜곡된 이미지를 직접 학습할지는 팀마다 다른 선택을 합니다.

---

## 4. 외부 파라미터 (Extrinsics)

내부 파라미터가 "카메라 렌즈의 광학적 특성"이라면, 외부 파라미터는 **"카메라가 차량에서 어떤 위치와 방향으로 달려 있는가"**입니다.

외부 파라미터는 SE3 변환으로 표현합니다. py123d에서 `camera_to_imu_se3`가 이것입니다.

```
camera_to_imu_se3: 카메라 좌표계 → 차량 IMU 좌표계 (ISO 8855)
```

예를 들어 전방 카메라가 차량 루프에 달려 있다면:
- 이동(translation): IMU 위치 대비 전방으로 1.5m, 위로 0.8m
- 회전(rotation): 카메라가 약간 아래를 향해 있으면 약간의 pitch

이 값이 있으면 카메라로 감지한 물체의 좌표를 차량 기준 좌표로 변환할 수 있습니다.

### 멀티카메라 리그

자율주행 차량은 보통 전방, 후방, 좌측, 우측 카메라를 함께 씁니다. 각 카메라마다 `camera_to_imu_se3`가 있고, IMU가 공통 기준 프레임 역할을 합니다.

```
camera_front_to_imu_se3
camera_rear_to_imu_se3
camera_left_to_imu_se3
camera_right_to_imu_se3
```

IMU 프레임을 공통 기준으로 삼기 때문에, 두 카메라 사이의 관계는:
```
camera_A_to_camera_B = camera_B_to_imu^{-1} · camera_A_to_imu
```

IMU 위치 하나만 기준으로 잡으면 모든 카메라 쌍의 관계가 자동으로 결정됩니다.

---

## 5. 카메라-LiDAR 외부 캘리브레이션

LiDAR와 카메라를 함께 쓸 때는 두 센서 사이의 변환도 알아야 합니다.

```
lidar_to_imu_se3: LiDAR 좌표계 → 차량 IMU 좌표계
camera_to_imu_se3: 카메라 좌표계 → 차량 IMU 좌표계

camera_to_lidar = lidar_to_imu^{-1} · camera_to_imu
```

이 관계를 알면 LiDAR 포인트를 카메라 이미지 위에 투영할 수 있습니다. 포인트마다 `(X, Y, Z)_lidar → (X, Y, Z)_camera → (u, v)_image`로 변환하면 이미지 위에 색깔 점이 찍힌 컬러 포인트 클라우드가 만들어집니다.

---

## 6. 핀홀 너머: FTheta 모델

핀홀 모델은 FoV가 약 90도 이하일 때 잘 동작합니다. FoV가 넓어질수록 수차가 커지고, 180도 이상의 어안 렌즈(Fisheye)는 핀홀 모델로 아예 표현할 수 없습니다.

자율주행 차량이 주변 전체를 커버하려면 120도 이상의 광각 카메라가 필요합니다. NVIDIA Hyperion 플랫폼(PAI-AV, NCore)은 **FTheta 카메라 모델**을 씁니다.

FTheta 모델에서는 이미지 좌표가 다음과 같이 계산됩니다:

```
θ = arctan(sqrt(X² + Y²) / Z)  ← 광축(Z)과 이루는 각도
r = f(θ)                        ← θ의 다항식 함수
u = r · X/sqrt(X²+Y²) + cx
v = r · Y/sqrt(X²+Y²) + cy
```

핀홀에서는 `r = f · tan(θ)`이지만, FTheta에서는 `r = f(θ) = a1·θ + a2·θ³ + ...`처럼 다항식으로 근사합니다. 가장자리로 갈수록 더 많이 왜곡되는 광각 렌즈의 특성을 표현합니다.

**py123d → NuRec 변환에서 이게 중요한 이유**: nuScenes와 AV2는 핀홀 카메라입니다. NuRec가 요구하는 NCore 포맷은 FTheta 카메라를 가정합니다. 핀홀 파라미터를 FTheta로 수학적으로 변환하는 공식이 없기 때문에, 실 차량에 달린 카메라가 광각 렌즈라면 처음부터 FTheta로 캘리브레이션해야 NuRec 파이프라인에 바로 넣을 수 있습니다.

---

## 7. py123d 파서에서의 위치

파서 작성 시 캘리브레이션 값을 어떻게 채우는지:

```python
PinholeCameraMetadata(
    camera_name="camera_front",
    camera_id=CAM_FRONT,
    intrinsics=PinholeIntrinsics(
        fx=intr["fx"], fy=intr["fy"],   # ← 초점 거리
        cx=intr["cx"], cy=intr["cy"],   # ← 주점
    ),
    distortion=PinholeDistortion(
        k1=0.0, k2=0.0, p1=0.0, p2=0.0  # ← 왜곡 계수
    ),
    width=intr["width"],                 # ← 이미지 해상도
    height=intr["height"],
    camera_to_imu_se3=cam_to_ego,       # ← SE3 외부 파라미터
)
```

`calib.json`에서 읽은 `fx, fy, cx, cy` 값이 핀홀 모델의 내부 파라미터이고, `cam_to_ego` SE3가 외부 파라미터입니다. 이 두 가지가 있으면 해당 카메라의 모든 기하학적 특성이 완전히 정의됩니다.

---

## 8. 정리

| 파라미터 | 의미 | 정해지는 방법 |
|---------|------|------------|
| **fx, fy** | 초점 거리 (픽셀) → 시야각 결정 | 렌즈+센서 사양, 캘리브레이션 보정 |
| **cx, cy** | 주점 (광축이 이미지와 만나는 점) | 이상적으론 이미지 중앙, 실제론 약간 어긋남 |
| **k1, k2, p1, p2** | 렌즈 왜곡 계수 | 캘리브레이션으로 측정 |
| **camera_to_imu_se3** | 카메라 → 차량 기준 SE3 | 물리적 측정 + 캘리브레이션 |
| **카메라 모델** | Pinhole / FTheta / FisheyeMEI | 렌즈 종류에 따라 선택 |

캘리브레이션은 "이 카메라가 세상을 보는 수학적 규칙"입니다. 이 규칙을 정확히 알아야 카메라 이미지에서 3D 세계를 복원하고, LiDAR와 융합하고, 여러 카메라의 시야를 일관되게 연결할 수 있습니다.
