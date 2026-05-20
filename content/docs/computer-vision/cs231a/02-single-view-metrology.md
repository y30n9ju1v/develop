---
title: "Ch.2: 단일 뷰 계측"
date: 2026-05-20T00:00:00+09:00
draft: false
tags: ["computer-vision", "single-view-metrology", "vanishing-point", "homography", "cs231a"]
categories: ["computer-vision"]
description: "2D 변환의 계층 구조, 무한점과 무한선, 소실점과 지평선을 이용해 단 한 장의 이미지에서 3D 세계 구조를 복원하는 방법을 정리합니다."
---

> 이전 편에서는 카메라의 내부/외부 파라미터를 이용해 3D 세계를 2D 이미지로 변환하는 방법을 살펴봤습니다. 이번에는 반대 방향의 문제를 다룹니다.
>
> **카메라 파라미터를 알고 있을 때, 단 한 장의 이미지에서 3D 세계의 구조를 복원할 수 있을까?**

---

## 1. 소개

이미지로부터 무엇을 알아낼 수 있는지 이해하려면, 먼저 2D 공간의 다양한 변환들을 알아야 합니다. 이 변환들은 **보존하는 성질에 따라 계층 구조**를 이룹니다.

---

## 2. 2D 변환의 계층 구조

### 등거리 변환 (Isometric Transformations)

**거리(distance)를 보존**하는 변환입니다. 가장 기본적인 형태는 회전 $R$과 이동 $t$로 표현됩니다.

$$\begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} = \begin{bmatrix} R & t \\ 0 & 1 \end{bmatrix} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$

### 유사 변환 (Similarity Transformations)

**형태(shape)를 보존**하는 변환입니다. 등거리 변환에 스케일링을 추가한 것으로, 길이의 비율과 각도도 보존합니다.

$$\begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} = \begin{bmatrix} SR & t \\ 0 & 1 \end{bmatrix} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}, \quad S = \begin{bmatrix} s & 0 \\ 0 & s \end{bmatrix}$$

$s = 1$일 때 등거리 변환과 동일합니다. 즉, 등거리 변환은 유사 변환의 특수한 경우입니다.

### 아핀 변환 (Affine Transformations)

**점, 직선, 평행성(parallelism)을 보존**하는 변환입니다. 벡터 $v$에 대해 아핀 변환 $T$는,

$$T(v) = Av + t$$

동차 좌표계에서는,

$$\begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} = \begin{bmatrix} A & t \\ 0 & 1 \end{bmatrix} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$

모든 유사 변환(그리고 등거리 변환)은 아핀 변환의 특수한 경우입니다.

### 사영 변환 / 호모그래피 (Projective Transformations / Homographies)

**직선을 직선으로 매핑**하지만, 평행성은 보존하지 않는 변환입니다. 동차 좌표계에서,

$$\begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} = \begin{bmatrix} A & t \\ v & b \end{bmatrix} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$

아핀 변환에 $v$가 추가되어 자유도가 더 생긴 형태입니다. 평행성은 보존하지 않지만, **점들의 공선성(collinearity)**은 보존합니다(직선을 직선으로 매핑하므로).

#### 교차비 (Cross Ratio)

사영 변환 하에서 불변으로 유지되는 중요한 양이 있습니다. 한 직선 위의 네 점 $P_1, P_2, P_3, P_4$에 대한 **교차비**입니다.

$$\text{cross ratio} = \frac{\|P_3 - P_1\| \|P_4 - P_2\|}{\|P_3 - P_2\| \|P_4 - P_1\|} \tag{1}$$

교차비가 사영 변환 하에서 불변임을 증명하는 것은 연습문제로 남겨집니다.

> **변환 계층 요약**
>
> | 변환 | 보존하는 성질 |
> |---|---|
> | 등거리 (Isometric) | 거리 |
> | 유사 (Similarity) | 형태, 길이 비율, 각도 |
> | 아핀 (Affine) | 점, 직선, 평행성 |
> | 사영 (Projective) | 직선의 직선성, 교차비 |
>
> 위로 갈수록 더 제한적(보존하는 것이 많고), 아래로 갈수록 더 일반적입니다.

---

## 3. 무한의 점과 선 (Points and Lines at Infinity)

이미지에서 구조를 파악하는 데 직선이 매우 중요합니다. 2D와 3D 모두에서 직선의 정의를 알아야 합니다.

### 2D 직선의 표현

2D 직선은 동차 벡터 $\ell = \begin{bmatrix} a & b & c \end{bmatrix}^T$로 표현할 수 있습니다. $-a/b$는 기울기를, $-c/b$는 y절편을 나타냅니다. 공식적으로 2D 직선은,

$$\forall p = \begin{bmatrix} x \\ y \end{bmatrix} \in \ell, \quad \begin{bmatrix} a & b & c \end{bmatrix} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix} = 0 \tag{2}$$

### 두 직선의 교점

일반적으로 두 직선 $\ell$과 $\ell'$은 점 $x$에서 교차합니다. 이 점은 두 직선의 **외적(cross product)**으로 정의됩니다.

**증명**: 교점 $x$는 두 직선 위에 모두 있어야 하므로 $x^T \ell = 0$이고 $x^T \ell' = 0$이어야 합니다. $x = \ell \times \ell'$으로 정의하면, 외적의 정의에 의해 $x$는 $\ell$과 $\ell'$ 모두에 수직입니다. 수직의 정의에 따라 $x^T \ell = 0$이고 $x^T \ell' = 0$이 성립합니다. $\square$

### 무한점 (Points at Infinity)과 평행선

평행선은 교차하지 않는다는 것이 일상적인 지식입니다. 그러나 이 정의를 다시 쓰면 평행선은 **무한대에서 교차**한다고 볼 수 있습니다.

동차 좌표에서 무한점은 $\begin{bmatrix} x & y & 0 \end{bmatrix}^T$로 표현됩니다. 마지막 좌표가 0이므로 유클리드 좌표로 변환하면 무한대가 됩니다.

두 평행선 $\ell$과 $\ell'$은 기울기가 같으므로 $a/b = a'/b'$입니다. 동차 좌표로 교점을 계산하면,

$$\ell \times \ell' \propto \begin{bmatrix} b \\ -a \\ 0 \end{bmatrix} = x_\infty \tag{3}$$

즉, 두 평행선은 무한점 $x_\infty$에서 교차합니다. 이 점을 **이상점(ideal point)**이라고도 합니다. 같은 기울기 $-a/b$를 가진 모든 평행선은 하나의 이상점을 통과합니다.

$$\ell^T x_\infty = \begin{bmatrix} a & b & c \end{bmatrix} \begin{bmatrix} b \\ -a \\ 0 \end{bmatrix} = 0 \tag{4}$$

### 무한선 (Lines at Infinity)

여러 쌍의 평행선을 생각해봅시다. 각 쌍의 평행선은 하나의 무한점 $\{x_{\infty,1}, \ldots, x_{\infty,n}\}$에서 교차합니다. 이 모든 무한점들을 지나는 선 $\ell_\infty$는 $\forall i, \ell_\infty^T x_{\infty,i} = 0$을 만족해야 합니다. 이로부터 $\ell_\infty = \begin{bmatrix} 0 & 0 & c \end{bmatrix}^T$임을 알 수 있고, $c$는 임의 값이므로 간단히,

$$\ell_\infty = \begin{bmatrix} 0 & 0 & 1 \end{bmatrix}^T$$

로 정의합니다.

### 변환과 무한점의 관계

**사영 변환 $H$**를 무한점 $p_\infty$에 적용하면,

$$p' = Hp_\infty = \begin{bmatrix} A & t \\ v & b \end{bmatrix} \begin{bmatrix} 1 \\ 1 \\ 0 \end{bmatrix} = \begin{bmatrix} p'_x \\ p'_y \\ p'_z \end{bmatrix} \tag{5}$$

마지막 요소가 0이 아닐 수 있으므로, **사영 변환은 무한점을 유한점으로 매핑**할 수 있습니다.

반면 **아핀 변환**은 무한점을 무한점으로 그대로 매핑합니다.

$$p' = Hp_\infty = \begin{bmatrix} A & t \\ 0 & 1 \end{bmatrix} \begin{bmatrix} 1 \\ 1 \\ 0 \end{bmatrix} = \begin{bmatrix} p'_x \\ p'_y \\ 0 \end{bmatrix} \tag{6}$$

사영 변환을 직선 $\ell$에 적용해 새 직선 $\ell'$을 얻을 때는 $\ell' = H^{-T} \ell$입니다. 마찬가지로, **사영 변환은 무한선을 무한선이 아닌 선으로 매핑**할 수 있으며, 아핀 변환은 무한선을 무한선으로 유지합니다.

---

## 4. 소실점과 소실선 (Vanishing Points and Lines)

지금까지 2D에서의 무한점과 무한선을 살펴봤습니다. 이제 3D에서의 동등한 개념을 소개합니다.

### 3D에서의 평면, 직선, 점

**평면**은 벡터 $\begin{bmatrix} a & b & c & d \end{bmatrix}^T$로 표현됩니다. $(a, b, c)$는 법선 벡터이고 $d$는 원점에서 평면까지의 거리입니다. 공식적으로 평면은 다음을 만족하는 모든 점 $x$의 집합입니다.

$$x^T \begin{bmatrix} a \\ b \\ c \\ d \end{bmatrix} = ax_1 + bx_2 + cx_3 + d = 0 \tag{7}$$

3D에서 **직선**은 두 평면의 교선으로 정의됩니다. 4개의 자유도(정의된 절편 위치와 세 차원의 기울기)를 가져 표현이 복잡합니다.

**점**은 2D와 유사하게 정의됩니다. 3D에서의 **무한점**은 3D 평행선들의 교점입니다.

### 소실점 (Vanishing Point)

3D의 무한점 $x_\infty$에 사영 변환을 적용하면 이미지 평면의 점 $p_\infty$를 얻는데, 이 점은 더 이상 동차 좌표에서 무한점이 아닙니다. 이 점 $p_\infty$를 **소실점(vanishing point)**이라 합니다.

카메라 기준 좌표계에서 3D 평행선들의 방향을 $d = (a, b, c)$라 하면, 이미지의 소실점 $v$는,

$$v = Kd \tag{8}$$

역으로, 소실점에서 3D 방향을 복원할 수 있습니다.

$$d = \frac{K^{-1}v}{\|K^{-1}v\|} \tag{9}$$

### 소실선 / 지평선 (Vanishing Line / Horizon Line)

평면 $\Pi$를 평행선의 집합으로 볼 때, 각 집합의 평행선은 하나의 무한점에서 교차합니다. 이 무한점들을 모두 지나는 선이 $\Pi$에 연관된 **무한선** $\ell_\infty$입니다. 무한선은 두 평행 평면이 교차하는 선으로도 정의됩니다.

$\ell_\infty$의 이미지 평면으로의 사영 변환은 더 이상 무한선이 아니며, 이를 **소실선** 또는 **지평선(horizon line)** $\ell_\text{horiz}$라 합니다. 지평선은 이미지에서 대응하는 소실점들을 잇는 선입니다.

$$\ell_\text{horiz} = H_P^{-T} \ell_\infty \tag{10}$$

지평선의 개념은 수학적으로 파악하기 어려운 이미지의 성질을 직관적으로 이해하는 데 도움을 줍니다. 예를 들어, 이미지 좌표에서 평행하지 않은 지면의 선들이 3D 세계에서는 평행하다는 것을 자연스럽게 인식할 수 있습니다.

### 지평선과 평면의 법선 관계

3D 평면의 법선 $n$과 이미지의 지평선 $\ell_\text{horiz}$ 사이에는 유용한 관계가 있습니다.

$$n = K^T \ell_\text{horiz} \tag{11}$$

카메라가 캘리브레이션되어 있고 평면과 연관된 지평선을 인식할 수 있다면, 해당 평면의 방향(orientation)을 추정할 수 있습니다.

### 무한대 평면 (Plane at Infinity)

두 개 이상의 소실선 집합으로 정의되는 평면을 **무한대 평면** $\Pi_\infty$라 합니다. 동차 좌표에서 $\begin{bmatrix} 0 & 0 & 0 & 1 \end{bmatrix}^T$로 표현됩니다.

### 소실점으로 두 선 사이의 각도 계산

3D의 두 평행선 집합의 방향을 $d_1$, $d_2$라 하고, 이에 대응하는 소실점을 $v_1$, $v_2$라 하면, 두 방향 사이의 각도 $\theta$는,

$$\cos\theta = \frac{d_1 \cdot d_2}{\|d_1\| \|d_2\|} = \frac{v_1^T \omega v_2}{\sqrt{v_1^T \omega v_1} \sqrt{v_2^T \omega v_2}} \tag{12}$$

여기서 $\omega = (KK^T)^{-1}$입니다.

### 소실선으로 두 평면 사이의 각도 계산

3D의 두 평면은 각각 소실선 $\ell_1$, $\ell_2$를 가지며, 각 평면의 법선은 $n_i = K^T \ell_i$입니다. 두 평면 사이의 각도는 두 법선 벡터 사이의 각도로 구할 수 있습니다.

$$\cos\theta = \frac{n_1 \cdot n_2}{\|n_1\| \|n_2\|} = \frac{\ell_1^T \omega^{-1} \ell_2}{\sqrt{\ell_1^T \omega^{-1} \ell_1} \sqrt{\ell_2^T \omega^{-1} \ell_2}} \tag{13}$$

---

## 5. 단일 뷰 계측 예제 (Single View Metrology Example)

이 모든 개념을 결합하면, **단 한 장의 이미지로 카메라를 캘리브레이션**하는 것이 가능합니다.

### 문제 설정

이미지에서 두 개의 평면을 식별할 수 있다고 가정합시다. 각 평면에서 평행선 쌍을 찾아 소실점 $v_1$, $v_2$를 추정하고, 이 두 평면이 3D에서 수직이라는 사실을 알고 있다고 합시다.

식 (12)로부터, 두 방향이 수직이면 $v_1^T \omega v_2 = 0$이 됩니다.

### 제약 조건 분석

그런데 $\omega$는 카메라 행렬 $K$에 의존하고, $K$가 미지수입니다. 충분한 제약 조건이 있을까요?

- $K$는 **5개의 자유도**를 가집니다.
- 소실점 쌍 하나($v_1 \omega v_2 = 0$)는 **1개의 제약**만 제공합니다.

두 쌍으로는 제약이 부족합니다. 서로 수직인 세 번째 소실점 $v_3$를 추가하면 $v_1^T \omega v_2 = v_1^T \omega v_3 = v_2^T \omega v_3 = 0$, 즉 **3개의 제약**이 생깁니다. 여전히 5개 중 3개뿐입니다.

### 영점 스큐 + 정사각형 픽셀 가정

카메라가 **영점 스큐(zero-skew)**와 **정사각형 픽셀(square pixels)**을 가진다고 가정하면 2개의 추가 제약이 생겨 총 5개를 만족합니다. 이 가정 하에서 $\omega$는,

$$\omega = \begin{bmatrix} \omega_1 & 0 & \omega_4 \\ 0 & \omega_1 & \omega_5 \\ \omega_4 & \omega_5 & \omega_6 \end{bmatrix} \tag{14}$$

$\omega$에는 4개의 변수가 있지만, $\omega$는 스케일만큼의 오차를 포함하므로 실제 변수는 **3개**로 줄어듭니다. 3개의 제약으로 이를 풀 수 있습니다.

### 단일 이미지 캘리브레이션 과정 요약

```
1. 이미지에서 서로 수직인 세 평면을 식별
2. 각 평면에서 평행선 쌍을 찾아 소실점 v1, v2, v3 추정
3. v1ᵀωv2 = v1ᵀωv3 = v2ᵀωv3 = 0 으로 3개의 제약 확보
4. 영점 스큐 + 정사각형 픽셀 가정으로 총 5개 제약 충족
5. ω를 풀고 Cholesky 분해로 K 계산
6. K로 3D 기하학적 구조 복원 (평면 방향, 선 방향 등)
```

$K$가 구해지면, 이미지에서 파악한 모든 평면의 방향을 계산하는 등 장면의 3D 기하학을 복원할 수 있습니다.

> **핵심 결론**
>
> 단 한 장의 이미지로도 적절한 기하학적 가정(수직 평면, 영점 스큐, 정사각형 픽셀)을 활용하면 카메라를 캘리브레이션하고 장면의 3D 구조를 추론할 수 있습니다. 이것이 **단일 뷰 계측(Single View Metrology)**의 핵심입니다.
