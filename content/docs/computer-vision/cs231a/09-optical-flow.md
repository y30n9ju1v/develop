---
title: "Ch.9: 광학 흐름과 장면 흐름"
date: 2026-05-20T00:00:00+09:00
draft: false
tags: ["computer-vision", "optical-flow", "lucas-kanade", "cs231a"]
categories: ["computer-vision"]
description: "광학 흐름의 정의와 모션 필드의 차이, 밝기 항상성 가정과 소운동 가정에서 유도되는 광학 흐름 제약 방정식, 개구부 문제, Lucas-Kanade 최소제곱법을 다룹니다."
---

> 이 글은 Stanford CS231A (Computer Vision: From 3D Reconstruction to Recognition) 강의 노트 시리즈의 아홉 번째 글입니다.
> - [카메라 모델](../01-camera-models/)
> - [단일 뷰 계측](../02-single-view-metrology/)
> - [에피폴라 기하학](../03-epipolar-geometry/)
> - [스테레오 시스템과 SfM](../04-stereo-systems-and-structure-from-motion/)
> - [능동 스테레오와 체적 스테레오](../05-active-volumetric-stereo/)
> - [피팅과 매칭](../06-fitting-matching/)
> - [표현과 표현 학습](../07-representation-learning/)
> - [단안 깊이 추정과 특징 추적](../08-monocular-depth-estimation/)

## 1. 광학 흐름 개요

**광학 흐름(optical flow)**은 비디오에서 카메라(관찰자)와 장면(물체, 표면, 에지) 사이의 상대적 움직임으로 인한 각 픽셀의 **겉보기 움직임**을 나타내는 2D 벡터 필드다. 카메라가 움직이거나, 장면이 움직이거나, 둘 다 움직일 수 있다.

### 1.1 모션 필드

광학 흐름은 **모션 필드(motion field)**와 혼동하지 말아야 한다. 모션 필드는 장면의 3D 운동 벡터를 이미지 평면에 투영한 2D 벡터 필드다.

3D 공간의 점을 대문자 $\mathbf{X} = (X, Y, Z)^T$, 이미지 평면 상의 투영점을 소문자 $\mathbf{x} = (x, y)^T$라 할 때, 핀홀 카메라 투영 식은 다음과 같다 (초점거리 $f$).

$$x = f\frac{X}{Z}, \quad y = f\frac{Y}{Z}$$

양변을 시간 $t$에 대해 미분하여 픽셀 $(x, y)$에서의 모션 필드 $\mathbf{u} = (u, v)^T$를 유도하면 다음과 같다.

$$\mathbf{u} = \begin{pmatrix} u \\ v \end{pmatrix} = \begin{pmatrix} \frac{dx}{dt} \\ \frac{dy}{dt} \end{pmatrix} = \mathbf{M}\mathbf{V} \tag{1}$$

여기서 $\mathbf{V} = \left[\frac{dX}{dt}, \frac{dY}{dt}, \frac{dZ}{dt}\right]^T$는 3D 점의 물리적 속도를 나타내며, 투영 편미분 행렬 $\mathbf{M} \in \mathbb{R}^{2 \times 3}$은 다음과 같이 정의된다.

$$\mathbf{M} = \begin{pmatrix} \frac{f}{Z} & 0 & -\frac{x}{Z} \\ 0 & \frac{f}{Z} & -\frac{y}{Z} \end{pmatrix}$$

모션 필드는 이미지 평면에 투영된 3D 운동의 이상적인 2D 표현으로, 직접 관측할 수 없는 "정답"이다. 잡음이 있는 영상 관측으로부터 추정할 수 있는 것은 광학 흐름(겉보기 운동)뿐이다.

### 광학 흐름 vs. 모션 필드

광학 흐름이 모션 필드와 항상 같지는 않다.

| 상황 | 모션 필드 | 광학 흐름 |
|------|-----------|-----------|
| 고정 광원 아래에서 균일하게 회전하는 구 | 0이 아님 | 0 (텍스처 변화 없음) |
| 고정된 균일한 구 + 광원이 주위를 이동 | 0 | 0이 아님 (밝기 변화 발생) |

두 경우 모두 밝기 변화가 실제 물리적 운동을 정확히 반영하지 않는다는 것을 보여준다.

---

## 2. 광학 흐름 계산

비디오를 시간에 따라 캡처된 프레임의 순서열로 정의한다. $I(x, y, t)$는 시간 $t$의 프레임에서 픽셀 $(x, y)$의 밝기 강도를 나타낸다.

**밀집 광학 흐름(dense optical flow)**에서는 모든 시간 $t$와 모든 픽셀 $(x, y)$에 대해 픽셀의 겉보기 속도를 계산한다.

$$u(x,y,t) = \frac{\Delta x}{\Delta t}, \quad v(x,y,t) = \frac{\Delta y}{\Delta t}$$

각 픽셀의 광학 흐름 벡터는 $\mathbf{u} = [u, v]^T$로 표현된다.

### 2.1 기본 가정

**가정 1: 밝기 항상성(brightness constancy)**

동일한 물체의 겉보기 밝기는 프레임 간에 변하지 않는다.

$$I(x, y, t) = I(x + \Delta x,\ y + \Delta y,\ t + \Delta t) \tag{2}$$

편의상 $\Delta t = 1$(연속 프레임)로 설정하면 속도가 변위와 같아진다: $u = \Delta x$, $v = \Delta y$.

**가정 2: 소운동(small motion)**

프레임 간 움직임 $(\Delta x, \Delta y)$이 작다고 가정한다. 이를 이용해 $I$를 1차 테일러 급수로 선형화할 수 있다.

$$I(x + \Delta x,\ y + \Delta y,\ t + \Delta t) \approx I(x,y,t) + \frac{\partial I}{\partial x}\Delta x + \frac{\partial I}{\partial y}\Delta y + \frac{\partial I}{\partial t}\Delta t \tag{3}$$

### 2.2 광학 흐름 제약 방정식

식 (3)을 식 (2)에 대입하면 **광학 흐름 제약 방정식(optical flow constraint equation)**을 얻는다.

$$0 = \frac{\partial I}{\partial x}\Delta x + \frac{\partial I}{\partial y}\Delta y + \frac{\partial I}{\partial t}\Delta t = I_x u + I_y v + I_t \tag{4}$$

이를 정리하면:

$$-I_t = I_x u + I_y v = \nabla I^T \mathbf{u} = \nabla I \cdot \vec{\mathbf{u}} \tag{5}$$

여기서 $\nabla I = [I_x, I_y]^T \in \mathbb{R}^{2 \times 1}$은 강도의 공간 기울기, $\vec{\mathbf{u}} \in \mathbb{R}^{2 \times 1}$은 구하고자 하는 흐름 벡터다.

이는 $\mathbf{A}\mathbf{x} = \mathbf{b}$ 형태의 선형 시스템이다. 그러나 $\nabla I$가 가로로 긴 행렬(fat matrix)이므로 미지수 $u, v$ 두 개에 제약 방정식이 하나뿐인 **과소결정(under-constrained)** 시스템이다.

### 2.3 법선 흐름과 개구부 문제

광학 흐름 제약은 $\nabla I$ 방향의 성분, 즉 **법선 흐름(normal flow)**만 알려준다.

$$\frac{\nabla I}{\|\nabla I\|} \cdot \mathbf{u} = \frac{-I_t}{\|\nabla I\|} \tag{6}$$

$(u, v)$의 해 집합은 직선 위에 놓인다. $\nabla I$ 방향의 성분(법선 흐름)은 알지만, 에지 방향의 성분은 알 수 없다. 이것이 바로 **개구부 문제(aperture problem)**다.

> **개구부 문제**: 작은 구멍(개구부)을 통해 움직이는 물체를 볼 때, 에지에 수직인 성분만 감지할 수 있고 에지 방향 성분은 감지할 수 없다. 물체가 실제로는 대각선으로 이동해도, 개구부를 통해서는 수직 이동처럼 보일 수 있다.

---

## 3. Lucas-Kanade 방법

개구부 문제를 해결하기 위해 **공간 평활성 가정(spatial smoothness assumption)**을 도입한다: 이웃하는 픽셀들은 장면에서 같은 표면에 속하므로 동일한 광학 흐름 $\mathbf{u}$를 공유한다.

현재 픽셀 주변에 $N \times N$ 이웃을 정의하면, 각 픽셀 $p_i = [x_i, y_i]^T$에 대한 제약이 생긴다:

$$\nabla I(\mathbf{p}_i)^T \mathbf{u} = -I_t(\mathbf{p}_i)$$

$N^2 > 2$이면 다음과 같은 연립 방정식을 얻는다.

$$\mathbf{A}\mathbf{u} = \mathbf{b}$$

$$\begin{pmatrix} I_x(\mathbf{p}_1) & I_y(\mathbf{p}_1) \\ \vdots & \vdots \\ I_x(\mathbf{p}_{N^2}) & I_y(\mathbf{p}_{N^2}) \end{pmatrix} \begin{pmatrix} u \\ v \end{pmatrix} = -\begin{pmatrix} I_t(\mathbf{p}_1) \\ \vdots \\ I_t(\mathbf{p}_{N^2}) \end{pmatrix} \tag{7}$$

이 과결정(overdetermined) 시스템의 최소제곱해는 다음과 같다.

$$\mathbf{u}_{ls} = (\mathbf{A}^T\mathbf{A})^{-1}\mathbf{A}^T\mathbf{b}$$

### 3.1 정규 방정식

$$\mathbf{A}^T\mathbf{A}\mathbf{u} = \mathbf{A}^T\mathbf{b}$$

$$\begin{pmatrix} \sum I_x^2 & \sum I_x I_y \\ \sum I_x I_y & \sum I_y^2 \end{pmatrix} \mathbf{u} = -\begin{pmatrix} \sum I_x I_t \\ \sum I_y I_t \end{pmatrix} \tag{8}$$

합산은 이웃 내의 각 픽셀에 대해 이루어진다.

### 3.2 가해성 조건

시스템이 잘 풀리려면 $\mathbf{A}^T\mathbf{A}$가 다음 조건을 만족해야 한다.

| 조건 | 설명 |
|------|------|
| **작지 않아야 함** | 저텍스처 영역은 기울기 크기가 작아 고유값이 작고 $\mathbf{u}$ 추정이 불안정 |
| **잘 조건화(well-conditioned)** | 에지에서는 기울기가 한 방향으로 쏠려 조건수가 커 측정 오류에 취약 |

**이상적인 영역**: 방향이 다양한 고텍스처 영역(코너 등)—다양한 방향의 큰 기울기가 존재해 $\mathbf{A}^T\mathbf{A}$가 잘 조건화됨.

### 3.3 코너의 중요성

에지(직선)만 있는 경우: 법선 흐름 벡터가 하나뿐이므로 제약선이 하나 → 개구부 문제 발생.

**코너**가 있는 경우: 서로 다른 방향의 두 에지 → 법선 흐름 벡터와 제약선이 두 개 → 두 제약선의 교점에서 $\mathbf{u}$의 유일한 해를 구할 수 있다.

따라서 이웃 크기 $N$을 키우면 다양한 공간 구조를 포함할 가능성이 높아지지만, 트레이드오프가 존재한다: $N$이 너무 크면 서로 다른 표면에 속하는 픽셀(운동 경계)을 포함할 수 있어 $\mathbf{u}$가 이웃 전체에서 상수라는 가정이 깨진다.

---

## 4. Lucas-Kanade의 한계

전통적인 Lucas-Kanade 공식화는 다음 이유로 실용적 강건성이 부족하다.

- **큰 카메라 움직임**: 소운동 가정 위반
- **가려짐(occlusion)**: 밝기 항상성 가정 위반
- **조명 변화**: 밝기 항상성 가정 위반
- **운동 경계**: 공간 평활성 가정 위반

이러한 한계를 극복하기 위해 피라미드 Lucas-Kanade, Horn-Schunck 전역 최적화, 딥러닝 기반 방법(FlowNet, PWC-Net 등)이 개발되었다.

---

## 요약

| 개념 | 핵심 내용 |
|------|-----------|
| **광학 흐름** | 겉보기 운동의 2D 벡터 필드; 모션 필드(실제 3D 투영)와 다를 수 있음 |
| **밝기 항상성** | $I(x,y,t) = I(x+\Delta x, y+\Delta y, t+\Delta t)$ |
| **광학 흐름 제약** | $I_x u + I_y v + I_t = 0$ — 하나의 방정식으로 두 미지수 |
| **법선 흐름** | 제약 방정식으로 알 수 있는 것: $\nabla I$ 방향 성분만 |
| **개구부 문제** | 에지 방향 성분을 알 수 없는 모호성 |
| **Lucas-Kanade** | 공간 평활성 가정으로 $N \times N$ 이웃을 과결정 LS로 풀기 |
| **이상적인 영역** | 방향이 다양한 고텍스처 영역(코너); $\mathbf{A}^T\mathbf{A}$가 잘 조건화됨 |
