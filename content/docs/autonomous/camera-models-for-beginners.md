---
title: "자율주행 카메라 모델 입문: 핀홀과 피쉬아이"
date: 2026-05-11T20:00:00+09:00
draft: false
tags: ["자율주행", "카메라", "핀홀", "피쉬아이", "캘리브레이션", "입문"]
categories: ["자율주행"]
description: "자율주행에서 쓰이는 카메라 모델의 기초를 설명합니다. 핀홀 카메라 모델과 피쉬아이 카메라 모델의 원리, 렌즈 왜곡, 왜곡 보정 방법을 다룹니다."
math: true
---

## 왜 카메라 모델을 알아야 하나요?

자율주행 차량은 카메라로 찍은 이미지를 보고 차선, 신호등, 보행자를 인식합니다. 그런데 카메라가 찍은 이미지는 **3D 세계를 2D 평면에 투영한 결과**입니다. 이 과정에서 어떤 규칙으로 투영이 일어났는지 알아야 이미지를 올바르게 해석할 수 있습니다.

그 규칙을 수식으로 정의한 것이 **카메라 모델**입니다.

---

## 핀홀 카메라 모델

### 원리

핀홀 카메라는 가장 기본적인 카메라 모델입니다. 이름처럼 바늘구멍(pinhole)을 통해 빛이 들어오는 구조를 수식으로 표현한 것입니다.

```
3D 세계의 점 P(X, Y, Z)
         ↓
    핀홀(렌즈 중심)
         ↓
2D 이미지의 점 p(u, v)
```

핵심 아이디어는 간단합니다. **카메라에서 멀리 있는 물체는 작게, 가까이 있는 물체는 크게** 보입니다. 이 원근감을 수식으로 표현하면:

$$u = f_x \cdot \frac{X}{Z} + c_x, \quad v = f_y \cdot \frac{Y}{Z} + c_y$$

- $f_x, f_y$: x축, y축 초점 거리(focal length). 픽셀 단위
- $c_x, c_y$: 주점(principal point). 이미지의 광학 중심 좌표
- $Z$: 물체까지의 깊이(거리)

$f_x$와 $f_y$는 대부분의 카메라에서 비슷한 값이지만, 픽셀이 정사각형이 아닌 센서에서는 다를 수 있습니다.

### 카메라 내부 행렬 (Intrinsic Matrix)

위 수식을 행렬로 정리하면 **카메라 내부 행렬 K**가 됩니다.

$$K = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}$$

카메라 좌표계 기준의 3D 점 $\mathbf{P} = [X, Y, Z]^\top$를 2D 이미지 좌표로 변환하는 전체 수식:

$$s \begin{bmatrix} u \\ v \\ 1 \end{bmatrix} = K \begin{bmatrix} X \\ Y \\ Z \end{bmatrix}$$

여기서 $s = Z$는 스케일 인자입니다. 양변을 $s$로 나누면 앞의 투영 수식과 같아집니다.

> **카메라 좌표계와 월드 좌표계**: 위 수식은 카메라를 원점으로 하는 카메라 좌표계 기준입니다. 실제 세계의 좌표(월드 좌표계)에서 변환하려면 외부 행렬(rotation $R$, translation $\mathbf{t}$)도 함께 적용해야 합니다.
> $$s \begin{bmatrix} u \\ v \\ 1 \end{bmatrix} = K \left[ R \mid \mathbf{t} \right] \begin{bmatrix} X_w \\ Y_w \\ Z_w \\ 1 \end{bmatrix}$$

### 렌즈 왜곡

실제 렌즈는 완벽한 핀홀이 아니기 때문에 **왜곡(distortion)**이 생깁니다. 직선이 휘어 보이는 현상입니다.

| 왜곡 종류 | 모양 | 원인 |
|---|---|---|
| **방사 왜곡 (Radial)** | 중심에서 멀수록 직선이 안쪽/바깥쪽으로 휨 | 렌즈 곡률 |
| **접선 왜곡 (Tangential)** | 이미지가 한쪽으로 기울어짐 | 렌즈와 센서가 평행하지 않음 |

왜곡은 이미지 좌표에 왜곡을 **적용**하는 방향으로 모델링됩니다. 정규화된 좌표 $(x, y) = (X/Z, Y/Z)$에서 왜곡이 적용된 좌표 $(x', y')$는:

$$x' = x(1 + k_1 r^2 + k_2 r^4 + k_3 r^6) + 2p_1 xy + p_2(r^2 + 2x^2)$$

$$y' = y(1 + k_1 r^2 + k_2 r^4 + k_3 r^6) + p_1(r^2 + 2y^2) + 2p_2 xy$$

- $r^2 = x^2 + y^2$: 주점으로부터의 거리 제곱
- $k_1, k_2, k_3$: 방사 왜곡 계수
- $p_1, p_2$: 접선 왜곡 계수

실제 이미지 좌표는 왜곡이 적용된 후 $K$를 곱해서 구합니다: $u' = f_x x' + c_x$. **왜곡 보정(undistort)**은 이 과정의 역함수로, 수치적으로 반복 계산하거나 OpenCV가 대신 처리해줍니다.

왜곡 계수 $[k_1, k_2, p_1, p_2, k_3]$는 **카메라 캘리브레이션**으로 측정합니다.

### Python 코드: 핀홀 왜곡 보정

```python
import cv2
import numpy as np

# 카메라 내부 행렬과 왜곡 계수 (캘리브레이션으로 얻은 값)
K = np.array([[800,   0, 640],
              [  0, 800, 360],
              [  0,   0,   1]], dtype=np.float64)

dist_coeffs = np.array([-0.3, 0.1, 0.0, 0.0, 0.0])  # [k1, k2, p1, p2, k3]

img = cv2.imread("distorted.jpg")
h, w = img.shape[:2]

# 최적 카메라 행렬 계산 (왜곡 보정 후 유효 이미지 영역 최대화)
new_K, roi = cv2.getOptimalNewCameraMatrix(K, dist_coeffs, (w, h), alpha=1)

# 왜곡 보정
undistorted = cv2.undistort(img, K, dist_coeffs, newCameraMatrix=new_K)

cv2.imwrite("undistorted.jpg", undistorted)
```

---

## 피쉬아이 카메라 모델

### 핀홀과 무엇이 다른가요?

핀홀 모델에서 입사각 $\theta$가 90도에 가까워지면 $\tan(\theta) \to \infty$가 되어 수식이 발산합니다. 따라서 핀홀 모델은 실용적으로 **화각 160도 이하**에서만 사용 가능합니다.

**피쉬아이(fisheye) 카메라**는 화각이 **180도 이상**인 초광각 카메라입니다. 물고기 눈처럼 넓게 보인다고 해서 붙은 이름입니다. 보통 자율주행 차량의 앞/뒤/좌/우에 4개를 장착해서 Surround View(주변 전방위 영상)를 구성합니다.

```
핀홀 카메라: r = f·tan(θ) → θ→90° 이상에서 발산
피쉬아이 카메라: r = f·θ  → 180°까지 유한한 값
```

### 피쉬아이 투영 모델

가장 많이 쓰이는 모델은 **등거리 투영(equidistant projection)**입니다.

$$r = f \cdot \theta$$

- $\theta$: 광축(카메라 정면)과 입사광 사이의 각도
- $r$: 이미지 중심으로부터의 거리 (픽셀)
- $f$: 초점 거리

주요 피쉬아이 투영 모델 비교:

| 모델 | 수식 | 특징 |
|---|---|---|
| 등거리 (Equidistant) | $r = f\theta$ | 가장 일반적, OpenCV 기본 |
| 등면적 (Equisolid) | $r = 2f\sin(\theta/2)$ | 면적 보존 |
| 정사 (Orthographic) | $r = f\sin\theta$ | 구면 투영 |
| 스테레오그래픽 | $r = 2f\tan(\theta/2)$ | 각도 보존 |

### 피쉬아이 왜곡 계수: 핀홀과 다른 체계

피쉬아이 왜곡 계수는 핀홀의 $[k_1, k_2, p_1, p_2, k_3]$와 **완전히 다른 체계**입니다. OpenCV는 Kannala-Brandt 모델을 사용하며, 왜곡 계수가 $[k_1, k_2, k_3, k_4]$ 4개입니다.

투영 수식:

$$r(\theta) = f(\theta + k_1\theta^3 + k_2\theta^5 + k_3\theta^7 + k_4\theta^9)$$

핀홀 왜곡은 이미지 평면에서의 반경 $r$에 대한 보정인 반면, 피쉬아이 왜곡은 **입사각 $\theta$에 대한 보정**입니다. 이 때문에 피쉬아이 카메라를 핀홀 캘리브레이션(`cv2.calibrateCamera`)으로 처리하면 왜곡 계수가 완전히 다른 의미가 됩니다. 반드시 피쉬아이 전용 함수(`cv2.fisheye.calibrate`)를 사용해야 합니다.

### Python 코드: 피쉬아이 왜곡 보정

```python
import cv2
import numpy as np

# 피쉬아이 카메라 내부 행렬과 왜곡 계수 (캘리브레이션으로 얻은 값)
K = np.array([[400,   0, 640],
              [  0, 400, 360],
              [  0,   0,   1]], dtype=np.float64)

# Kannala-Brandt 왜곡 계수 k1~k4
D = np.array([-0.01, 0.0, 0.0, 0.0], dtype=np.float64)

img = cv2.imread("fisheye.jpg")
h, w = img.shape[:2]

# 새 카메라 행렬 (왜곡 보정 후 이미지 크기 결정)
new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
    K, D, (w, h), np.eye(3), balance=1.0)

# 보정 맵 생성
map1, map2 = cv2.fisheye.initUndistortRectifyMap(
    K, D, np.eye(3), new_K, (w, h), cv2.CV_16SC2)

# 왜곡 보정 적용
undistorted = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR)

cv2.imwrite("fisheye_undistorted.jpg", undistorted)
```

---

## 카메라 캘리브레이션

모든 수식에 등장하는 $K$와 왜곡 계수는 **카메라 캘리브레이션**으로 측정해야 합니다. 체커보드 패턴을 다양한 각도에서 찍어서 OpenCV가 자동으로 계산해줍니다.

### 핀홀 캘리브레이션

```python
import cv2
import numpy as np
import glob

CHECKERBOARD = (9, 6)

objpoints = []
imgpoints = []

objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

for fname in glob.glob("calib_images/*.jpg"):
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD)
    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)

ret, K, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None)

print("K:", K)
print("왜곡 계수 [k1,k2,p1,p2,k3]:", dist_coeffs)
```

### 피쉬아이 캘리브레이션

피쉬아이는 `cv2.fisheye.calibrate`를 사용합니다. 입력 형식이 핀홀과 다르므로 주의합니다.

```python
import cv2
import numpy as np
import glob

CHECKERBOARD = (9, 6)

objpoints = []
imgpoints = []

objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[0, :, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

for fname in glob.glob("calib_images/*.jpg"):
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD)
    if ret:
        objpoints.append(objp)
        imgpoints.append(corners.reshape(1, -1, 2))

K = np.zeros((3, 3))
D = np.zeros((4, 1))  # Kannala-Brandt k1~k4

cv2.fisheye.calibrate(
    objpoints, imgpoints, gray.shape[::-1],
    K, D,
    flags=cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_FIX_SKEW)

print("K:", K)
print("왜곡 계수 [k1,k2,k3,k4]:", D.ravel())
```

---

## 정리

| 개념 | 한 줄 요약 |
|---|---|
| **핀홀 카메라 모델** | 3D→2D 투영을 $s[u,v,1]^\top = K[X,Y,Z]^\top$로 표현 |
| **카메라 내부 행렬 K** | 초점 거리 $(f_x, f_y)$와 주점 $(c_x, c_y)$을 담은 3×3 행렬 |
| **핀홀 왜곡 계수** | $[k_1, k_2, p_1, p_2, k_3]$ — 방사 + 접선 왜곡 |
| **피쉬아이 카메라** | 화각 180도+. 핀홀 발산 문제 없이 $r = f\theta$로 투영 |
| **피쉬아이 왜곡 계수** | Kannala-Brandt $[k_1, k_2, k_3, k_4]$ — 핀홀과 다른 체계 |
| **카메라 캘리브레이션** | 체커보드로 $K$와 왜곡 계수를 실측. 핀홀/피쉬아이 함수 구분 필수 |

---

*관련 글: [Lanelet2 입문](/docs/autonomous/lanelet2-for-beginners/), [OpenDRIVE 입문](/docs/autonomous/opendrive-for-beginners/)*
