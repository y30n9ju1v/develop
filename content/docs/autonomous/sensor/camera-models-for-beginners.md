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

핵심 아이디어는 단순합니다. **멀리 있는 물체는 작게, 가까이 있는 물체는 크게** 보입니다. 예를 들어 10m 앞의 사람과 20m 앞의 사람을 찍으면, 20m 사람이 절반 크기로 찍힙니다. 이 원근감은 물체의 깊이 $Z$로 나누는 것으로 표현됩니다.

여기에 렌즈의 확대 배율($f_x, f_y$)과 이미지 중심 위치($c_x, c_y$)를 더하면 최종 픽셀 좌표가 됩니다:

$$u = f_x \cdot \frac{X}{Z} + c_x, \quad v = f_y \cdot \frac{Y}{Z} + c_y$$

- $f_x, f_y$: 초점 거리(focal length). 렌즈 배율을 픽셀 단위로 표현한 값. 클수록 피사체가 크게 찍힘
- $c_x, c_y$: 주점(principal point). 광학 중심이 이미지 정중앙에서 얼마나 벗어났는지
- $Z$: 카메라에서 물체까지의 거리

$f_x$와 $f_y$는 대부분 같은 값입니다. 픽셀이 정사각형이 아닌 센서에서는 달라질 수 있지만, 현대 카메라에서는 거의 동일합니다.

> **실무 팁: 화각(FOV) 계산하기**
> 내부 행렬의 초점 거리($f_x$)와 이미지의 너비 해상도($W$)를 알면, 카메라의 가로 화각(Field of View)을 간단히 계산할 수 있습니다. 
> $\text{FOV} \approx 2 \cdot \arctan(\frac{W}{2 f_x})$

### 카메라 내부 행렬 (Intrinsic Matrix)

위 수식의 파라미터 $f_x, f_y, c_x, c_y$는 카메라마다 고유한 값입니다. 이 네 값을 하나의 행렬로 묶은 것이 **카메라 내부 행렬 K**입니다. 코드에서 카메라를 다룰 때 항상 등장하는 핵심 행렬입니다.

$$K = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}$$

이 행렬을 쓰면 앞의 투영 수식을 다음처럼 간결하게 표현할 수 있습니다:

$$s \begin{bmatrix} u \\ v \\ 1 \end{bmatrix} = K \begin{bmatrix} X \\ Y \\ Z \end{bmatrix}$$

수식 자체는 동일합니다. $s = Z$로 양변을 나누면 앞의 투영 수식과 같아집니다.

> **참고**: 위 수식은 카메라가 원점인 카메라 좌표계 기준입니다. 실제 차량에 장착된 카메라는 위치와 방향이 있으므로, 월드 좌표계에서 변환하려면 외부 행렬(카메라의 위치와 방향)도 함께 사용합니다. 이 내용은 이 글의 범위를 벗어나므로 생략합니다.

### 렌즈 왜곡

지금까지의 핀홀 모델은 이상적인 렌즈를 가정합니다. 하지만 실제 렌즈는 **왜곡(distortion)**이 생깁니다. 격자 무늬를 찍으면 직선이 휘어 보이는 현상입니다.

왜곡에는 두 종류가 있습니다:

| 왜곡 종류 | 모양 | 원인 |
|---|---|---|
| **방사 왜곡 (Radial)** | 중심에서 멀수록 직선이 안쪽/바깥쪽으로 휨 | 실제 렌즈의 투영이 이상적인 핀홀 모델과 다름 |
| **접선 왜곡 (Tangential)** | 이미지가 한쪽으로 기울어짐 | 렌즈와 이미지 센서가 완전히 평행하지 않은 조립 오차 |

실용적으로는 방사 왜곡이 훨씬 크고 중요합니다. 접선 왜곡은 현대 카메라에서 매우 작아 무시할 수 있는 수준인 경우가 많습니다.

> **하드웨어 팁: 글로벌 셔터 vs 롤링 셔터**
> 렌즈 왜곡과는 별개로, 카메라가 고속으로 움직이는 자율주행 환경에서는 이미지가 비스듬하게 찢어지는 젤로 현상(Jello effect)이 발생할 수 있습니다. 이를 막기 위해 자율주행 차량은 센서의 모든 픽셀을 동시에 캡처하는 **글로벌 셔터(Global Shutter)** 카메라를 주로 사용합니다. (일반 스마트폰 카메라는 롤링 셔터)

#### 방사 왜곡이 생기는 이유

이상적인 핀홀 모델은 모든 각도에서 $r = f\tan\theta$가 정확히 성립한다고 가정합니다. 그런데 실제 렌즈는 광학 설계 특성상 가장자리로 갈수록 이 관계에서 벗어납니다. 이 **반경 방향(radial) 편차**가 방사 왜곡입니다.

방사 왜곡의 방향은 두 가지입니다:

| 종류 | 모양 | 발생 상황 |
|---|---|---|
| **배럴(Barrel) 왜곡** | 이미지가 바깥으로 부풀음 | 광각렌즈에 흔함 |
| **핀쿠션(Pincushion) 왜곡** | 이미지가 안쪽으로 당겨짐 | 망원렌즈에 흔함 |

자율주행 전방 카메라는 주로 배럴 왜곡이, 피쉬아이는 그 극단적인 경우입니다.

#### 왜곡 수식

왜곡은 픽셀 좌표 $(u, v)$가 아닌 그 이전 단계인 **정규화 좌표** $(x, y) = (X/Z, Y/Z)$에서 적용됩니다. 정규화 좌표에 왜곡을 적용한 뒤 $K$를 곱하면 최종 픽셀 좌표가 됩니다.

방사 왜곡 항만 보면 다음과 같습니다:

$$x' = x(1 + k_1 r^2 + k_2 r^4 + k_3 r^6)$$
$$y' = y(1 + k_1 r^2 + k_2 r^4 + k_3 r^6)$$

- $r^2 = x^2 + y^2$: 중심에서의 거리 제곱. 멀수록 왜곡이 강해짐
- $k_1, k_2, k_3$: 방사 왜곡 계수. $k_1$이 가장 영향이 크고, $k_2, k_3$는 멀리 갈수록 미세한 추가 보정
- $k_1 < 0$이면 배럴 왜곡, $k_1 > 0$이면 핀쿠션 왜곡

접선 왜곡까지 포함한 전체 수식에는 $p_1, p_2$ 계수가 추가됩니다. OpenCV에서 왜곡 계수 벡터 순서는 $[k_1, k_2, p_1, p_2, k_3]$입니다.

**왜곡 보정(undistort)**은 이 왜곡 수식의 역과정입니다. OpenCV가 수치적으로 처리해줍니다. 왜곡 계수 $[k_1, k_2, p_1, p_2, k_3]$는 **카메라 캘리브레이션**으로 측정합니다.

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

### 핀홀의 한계와 피쉬아이

핀홀 투영 수식 $r = f\tan\theta$에서 입사각 $\theta$가 90도에 가까워지면 $\tan\theta \to \infty$가 되어 수식이 발산합니다. 핀홀 모델은 **화각 90도 이하**에서 안정적으로 동작합니다.

자율주행 차량은 앞/뒤/좌/우 4대의 카메라로 주변 360도를 커버해야 합니다. 카메라 한 대가 최소 90도 이상의 화각을 가져야 합니다. 여기서 핀홀 모델의 한계에 부딪힙니다.

**피쉬아이(fisheye) 카메라**는 화각이 **180도 이상**인 초광각 카메라입니다. 자율주행 차량에서는 앞/뒤/좌/우 4개를 장착해 **Surround View**를 구성합니다.

```
핀홀:     r = f·tan(θ)  → θ→90° 에서 발산
피쉬아이:  r = f·θ      → 180°까지 유한한 값
```

### 피쉬아이 투영 모델

피쉬아이는 핀홀과 다른 투영 수식을 씁니다. 가장 널리 쓰이는 모델은 **등거리 투영(equidistant projection)**으로, 각도와 이미지 반경이 선형으로 비례합니다:

$$r = f \cdot \theta$$

각도가 2배 커지면 이미지에서의 거리도 정확히 2배 커집니다. 이 덕분에 180도에 달하는 넓은 시야를 이미지 안에 고르게 담을 수 있습니다. 실무에서는 이 등거리 모델이 사실상 표준이며, OpenCV도 이 모델을 기본으로 사용합니다.

### 피쉬아이 왜곡 계수: 핀홀과 다른 체계

실제 피쉬아이 렌즈도 이상적인 $r = f\theta$에서 벗어납니다. 이 오차를 보정하는 왜곡 계수가 필요한데, 핀홀의 $[k_1, k_2, p_1, p_2, k_3]$와 **완전히 다른 체계**입니다.

핀홀 왜곡은 이미지 평면의 반경에 대한 보정이지만, 피쉬아이 왜곡은 **입사각 $\theta$에 대한 보정**입니다. OpenCV는 Kannala-Brandt 모델을 사용하며 계수가 $[k_1, k_2, k_3, k_4]$ 4개입니다:

$$r(\theta) = f(\theta + k_1\theta^3 + k_2\theta^5 + k_3\theta^7 + k_4\theta^9)$$

이 차이 때문에 피쉬아이 카메라를 핀홀 캘리브레이션(`cv2.calibrateCamera`)으로 처리하면 왜곡 계수가 완전히 다른 의미가 됩니다. 반드시 피쉬아이 전용 함수(`cv2.fisheye.calibrate`)를 사용해야 합니다.

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

$K$와 왜곡 계수는 카메라마다 다르며, 같은 기종이라도 개체마다 미세하게 다를 수 있습니다. 이 값들을 실제로 측정하는 과정이 **카메라 캘리브레이션**입니다.

방법은 간단합니다. 격자 크기를 알고 있는 **체커보드 패턴**을 다양한 각도와 위치에서 찍으면, OpenCV가 $K$와 왜곡 계수를 자동으로 계산합니다. 핀홀은 최소 **15~20장**, 피쉬아이는 **30장 이상** 찍는 것을 권장합니다. 장수가 부족하면 계산 결과가 불안정합니다.

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

> **주의**: `cv2.findChessboardCorners`는 피쉬아이의 심한 왜곡 환경에서 코너 검출이 실패하는 경우가 많습니다. 실무에서는 `cv2.findChessboardCornersSB`(더 강인한 버전) 또는 ChArUco 보드를 권장합니다.

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
| **핀홀 카메라 모델** | 멀리 있을수록 작게 찍히는 원근감을 수식으로 표현 |
| **카메라 내부 행렬 K** | 초점 거리 $(f_x, f_y)$와 주점 $(c_x, c_y)$을 담은 카메라 고유의 행렬 |
| **방사 왜곡** | 렌즈 가장자리로 갈수록 생기는 직선 휨. $k_1 < 0$이면 배럴, $k_1 > 0$이면 핀쿠션 |
| **피쉬아이 카메라** | 화각 180도+. $r = f\theta$로 투영해 핀홀의 발산 문제를 피함 |
| **피쉬아이 왜곡 계수** | Kannala-Brandt $[k_1, k_2, k_3, k_4]$ — 핀홀과 다른 체계, 전용 함수 필수 |
| **카메라 캘리브레이션** | 체커보드 촬영으로 $K$와 왜곡 계수를 측정. 핀홀 15~20장, 피쉬아이 30장 이상 |

---

*관련 글: [Lanelet2 입문](/docs/autonomous/lanelet2-for-beginners/), [OpenDRIVE 입문](/docs/autonomous/opendrive-for-beginners/)*
