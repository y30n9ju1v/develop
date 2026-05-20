---
title: "Ch.1: 카메라 모델"
date: 2026-05-20T00:00:00+09:00
draft: false
tags: ["computer-vision", "camera-model", "pinhole-camera", "camera-calibration", "cs231a"]
categories: ["computer-vision"]
description: "핀홀 카메라 모델부터 렌즈, 내부/외부 파라미터, 카메라 캘리브레이션까지 카메라를 수학적으로 모델링하는 방법을 정리합니다."
---

> **시리즈 시작에 앞서**
> 이 시리즈는 Stanford CS231A 강의 노트를 바탕으로 컴퓨터 비전의 수학적 기초를 정리합니다.
> 카메라가 3D 세계를 2D 이미지로 어떻게 변환하는지, 그 원리를 수식과 함께 차근차근 살펴봅니다.

---

## 1. 소개

카메라는 컴퓨터 비전에서 가장 핵심적인 도구입니다. 우리 주변의 세계를 기록하고, 그 결과물인 사진을 다양한 응용에 활용하는 메커니즘이죠. 따라서 컴퓨터 비전의 첫 번째 질문은 자연스럽게 이것이 됩니다.

> **카메라를 어떻게 수학적으로 모델링할 것인가?**

---

## 2. 핀홀 카메라 (Pinhole Camera)

### 2.1 기본 원리

가장 단순한 카메라 시스템을 설계해봅시다. 3D 물체와 필름(센서) 사이에 작은 구멍(aperture)이 뚫린 장벽(barrier)을 배치하는 것입니다.

장벽이 없다면, 필름의 모든 점은 3D 물체의 모든 점에서 방출되는 빛의 영향을 받습니다. 하지만 장벽이 있으면, 하나(또는 소수)의 빛줄기만 구멍을 통과해 필름에 도달합니다. 따라서 3D 물체의 점과 필름의 점 사이에 **일대일 대응**이 성립하고, 필름은 물체의 "이미지"를 기록하게 됩니다. 이것이 **핀홀 카메라 모델(pinhole camera model)**입니다.

### 2.2 수학적 구성

핀홀 카메라를 좀 더 형식적으로 구성하면 다음과 같습니다.

- **이미지 평면(image plane) / 망막 평면(retinal plane)**: 필름에 해당하는 평면
- **핀홀 O (center of the camera)**: 구멍의 위치, 카메라의 중심
- **초점 거리 f (focal length)**: 이미지 평면과 핀홀 O 사이의 거리

> **가상 이미지 평면(virtual image/retinal plane)**이란?
>
> 망막 평면을 O와 3D 물체 사이에, O로부터 거리 f인 위치에 놓을 수도 있습니다. 이 경우 이미지 평면의 상과 가상 이미지 평면의 상은 스케일(닮음 변환)이 다를 뿐 동일합니다.

카메라 좌표계 $\begin{bmatrix} \mathbf{i} & \mathbf{j} & \mathbf{k} \end{bmatrix}$를 핀홀 O를 중심으로 정의하되, 축 $\mathbf{k}$가 이미지 평면에 수직이고 이미지 평면 방향을 향하도록 합니다. 이를 **카메라 기준 좌표계(camera coordinate system)**라 합니다. $C'$와 O를 잇는 선을 카메라의 **광축(optical axis)**이라 합니다.

### 2.3 투영 방정식 (Projection Equation)

3D 점 $P = \begin{bmatrix} x & y & z \end{bmatrix}^T$가 이미지 평면 위의 점 $P' = \begin{bmatrix} x' & y' \end{bmatrix}^T$로 투영될 때, 삼각형의 닮음(similar triangles)을 이용하면 다음을 얻습니다.

$$P' = \begin{bmatrix} x' \\ y' \end{bmatrix}^T = \begin{bmatrix} f\dfrac{x}{z} & f\dfrac{y}{z} \end{bmatrix}^T \tag{1}$$

### 2.4 조리개 크기의 영향

핀홀 모델의 큰 가정 중 하나는 조리개가 하나의 점이라는 것입니다. 하지만 현실에서 조리개는 유한한 크기를 가집니다.

| 조리개 크기 | 효과 |
|---|---|
| 커질수록 | 더 많은 빛줄기 통과 → 이미지 흐림(blur) |
| 작아질수록 | 빛줄기 감소 → 선명하지만 어두운 이미지 |

이것이 핀홀 카메라의 근본적인 딜레마입니다. **선명하면서도 밝은 이미지를 어떻게 얻을 수 있을까?**

---

## 3. 카메라와 렌즈 (Cameras and Lenses)

### 3.1 렌즈의 역할

현대 카메라에서는 핀홀 대신 **렌즈(lens)**를 사용해 선명함과 밝기의 충돌을 해결합니다. 적절히 배치된 렌즈는 다음 성질을 만족합니다.

> 3D 점 $P$에서 방출된 모든 빛줄기가 렌즈에 의해 굴절되어 이미지 평면의 단일 점 $P'$로 수렴한다.

이로써 작은 조리개로 인해 대부분의 빛이 차단되는 문제가 해소됩니다. 단, 이 성질은 모든 3D 점에 대해 성립하지 않고, 특정 깊이에 있는 점 $P$에 대해서만 성립합니다. 그보다 가깝거나 먼 다른 점 $Q$의 이미지는 흐릿해집니다. 이것이 바로 사진/컴퓨터 그래픽스에서 말하는 **피사계 심도(depth of field)**입니다.

### 3.2 초점 거리와 파축 굴절 모델

렌즈는 광축에 평행한 모든 빛줄기를 **초점(focal point)**이라는 하나의 점으로 모읍니다. 렌즈 중심과 초점 사이의 거리가 **초점 거리 $f$**입니다. 렌즈 중심을 통과하는 빛줄기는 굴절되지 않습니다.

이를 이용해 핀홀 모델과 유사한 투영 관계를 유도할 수 있습니다.

$$P' = \begin{bmatrix} x' \\ y' \end{bmatrix} = \begin{bmatrix} z'\dfrac{x}{z} \\ z'\dfrac{y}{z} \end{bmatrix} \tag{2}$$

핀홀 모델에서는 $z' = f$이지만, 렌즈 기반 모델에서는 $z' = f + z_0$입니다. 이 모델은 **파축 굴절 모델(paraxial refraction model)** 또는 **박막 렌즈 근사(thin lens approximation)**라고 합니다.

### 3.3 방사형 왜곡 (Radial Distortion)

파축 굴절 모델은 박막 렌즈 근사를 사용하기 때문에 여러 종류의 수차(aberration)가 발생할 수 있습니다. 가장 일반적인 것이 **방사형 왜곡(radial distortion)**으로, 광축으로부터의 거리에 따라 이미지 배율이 증가하거나 감소하는 현상입니다.

- **핀쿠션 왜곡(pincushion distortion)**: 배율이 증가할 때
- **배럴 왜곡(barrel distortion)**: 배율이 감소할 때 (어안렌즈에서 주로 발생)

방사형 왜곡은 렌즈의 서로 다른 부분이 서로 다른 초점 거리를 가지기 때문에 발생합니다.

---

## 4. 디지털 이미지 공간으로 (Going to Digital Image Space)

앞서 유도한 $\mathbb{R}^3 \to \mathbb{R}^2$ 투영(사영 변환, projective transformation)은 실제 디지털 이미지와 몇 가지 차이가 있습니다.

1. 디지털 이미지의 좌표계는 이미지 평면의 좌표계와 다릅니다.
2. 디지털 이미지는 연속적이지 않고 이산적인 픽셀로 구성됩니다.
3. 물리적 센서는 왜곡 등의 비선형성을 도입할 수 있습니다.

이를 보정하기 위해 추가적인 변환들을 도입합니다.

### 4.1 카메라 행렬 모델과 동차 좌표계

#### 4.1.1 카메라 행렬 모델 소개

**원점 오프셋 $(c_x, c_y)$**: 이미지 평면 좌표계의 원점 $C'$는 이미지 중앙에 있지만, 디지털 이미지 좌표계의 원점은 보통 이미지의 좌하단 모서리에 있습니다. 따라서 이 두 좌표계는 $\begin{bmatrix} c_x, c_y \end{bmatrix}^T$만큼 오프셋됩니다.

$$P' = \begin{bmatrix} x' \\ y' \end{bmatrix} = \begin{bmatrix} f\dfrac{x}{z} + c_x \\ f\dfrac{y}{z} + c_y \end{bmatrix} \tag{3}$$

**픽셀 단위 변환 $k, l$**: 디지털 이미지의 좌표는 픽셀 단위이지만, 이미지 평면의 좌표는 물리적 단위(예: cm)입니다. 이를 맞추기 위해 파라미터 $k, l$ (단위: pixels/cm)을 도입합니다. $k = l$이면 **정사각형 픽셀(square pixels)**이라 합니다. $\alpha = fk$, $\beta = fl$로 정의하면,

$$P' = \begin{bmatrix} x' \\ y' \end{bmatrix} = \begin{bmatrix} \alpha\dfrac{x}{z} + c_x \\ \beta\dfrac{y}{z} + c_y \end{bmatrix} \tag{4}$$

이 투영은 $z$로 나누는 연산 때문에 **선형 변환이 아닙니다**. 그러나 행렬-벡터 곱으로 표현하면 유도가 편리해집니다. 이를 위한 해법이 바로 동차 좌표계입니다.

#### 4.1.2 동차 좌표계 (Homogeneous Coordinates)

유클리드 벡터 $(v_1, \ldots, v_n)$을 동차 좌표계로 변환하려면 새 차원에 1을 추가해 $(v_1, \ldots, v_n, 1)$로 만듭니다. 반대로, 임의의 동차 좌표 $(v_1, \ldots, v_n, w)$를 유클리드 좌표로 변환하면 $\left(\dfrac{v_1}{w}, \ldots, \dfrac{v_n}{w}\right)$가 됩니다.

동차 좌표를 이용하면 투영 변환을 행렬-벡터 곱으로 표현할 수 있습니다.

$$P'_h = \begin{bmatrix} \alpha x + c_x z \\ \beta y + c_y z \\ z \end{bmatrix} = \begin{bmatrix} \alpha & 0 & c_x & 0 \\ 0 & \beta & c_y & 0 \\ 0 & 0 & 1 & 0 \end{bmatrix} \begin{bmatrix} x \\ y \\ z \\ 1 \end{bmatrix} = \begin{bmatrix} \alpha & 0 & c_x & 0 \\ 0 & \beta & c_y & 0 \\ 0 & 0 & 1 & 0 \end{bmatrix} P_h \tag{5}$$

이제부터는 특별한 언급이 없으면 동차 좌표를 사용합니다. 3D 공간의 점과 이미지 좌표의 관계를 행렬-벡터 관계로 표현하면,

$$P' = \begin{bmatrix} x' \\ y' \\ z \end{bmatrix} = \begin{bmatrix} \alpha & 0 & c_x & 0 \\ 0 & \beta & c_y & 0 \\ 0 & 0 & 1 & 0 \end{bmatrix} \begin{bmatrix} x \\ y \\ z \\ 1 \end{bmatrix} = \begin{bmatrix} \alpha & 0 & c_x & 0 \\ 0 & \beta & c_y & 0 \\ 0 & 0 & 1 & 0 \end{bmatrix} P = MP \tag{6}$$

이 변환을 분해하면,

$$P' = MP = \begin{bmatrix} \alpha & 0 & c_x \\ 0 & \beta & c_y \\ 0 & 0 & 1 \end{bmatrix} \begin{bmatrix} I & 0 \end{bmatrix} P = K \begin{bmatrix} I & 0 \end{bmatrix} P \tag{7}$$

행렬 $K$를 **카메라 행렬(camera matrix)**이라 합니다.

#### 4.1.3 완전한 카메라 행렬 모델

카메라 행렬 $K$에는 두 가지 파라미터가 더 있습니다.

**스큐(skewness)**: 카메라 좌표계의 두 축 사이의 각도가 정확히 90°가 아닐 때 발생합니다. 대부분의 카메라는 스큐가 0이지만, 센서 제조 오차로 약간 발생할 수 있습니다. 스큐를 포함한 완전한 카메라 행렬은,

$$K = \begin{bmatrix} \alpha & -\alpha \cot\theta & c_x \\ 0 & \dfrac{\beta}{\sin\theta} & c_y \\ 0 & 0 & 1 \end{bmatrix} \tag{8}$$

카메라 행렬 $K$는 **5개의 자유도(degrees of freedom)**를 가집니다: 초점 거리 2개, 오프셋 2개, 스큐 1개. 이 파라미터들을 통틀어 **내부 파라미터(intrinsic parameters)**라 합니다. 이는 카메라 고유의 특성으로, 카메라의 제조 특성 등에 관계됩니다.

### 4.2 외부 파라미터 (Extrinsic Parameters)

지금까지는 3D 카메라 기준 좌표계의 점 $P$를 2D 이미지 평면으로 매핑하는 방법을 설명했습니다. 하지만 3D 세계 정보가 다른 좌표계(월드 좌표계)로 주어질 수도 있습니다. 이 경우, 월드 기준 좌표계와 카메라 기준 좌표계를 연결하는 추가 변환이 필요합니다. 이 변환은 **회전 행렬 $R$**과 **이동 벡터 $T$**로 표현됩니다. 월드 좌표 $P_w$가 주어지면 카메라 좌표는,

$$P = \begin{bmatrix} R & T \\ 0 & 1 \end{bmatrix} P_w \tag{9}$$

이를 식 (7)에 대입하면,

$$P' = K \begin{bmatrix} R & T \end{bmatrix} P_w = MP_w \tag{10}$$

$R$과 $T$는 카메라 외부 특성에 해당하므로 **외부 파라미터(extrinsic parameters)**라 합니다.

> **전체 투영 행렬 $M$ 정리**
>
> $3 \times 4$ 투영 행렬 $M$은 **11개의 자유도**를 가집니다.
> - 내부 파라미터 (카메라 행렬 $K$): 5개
> - 외부 파라미터 (회전 $R$): 3개
> - 외부 파라미터 (이동 $T$): 3개

---

## 5. 카메라 캘리브레이션 (Camera Calibration)

3D 세계에서 디지털 이미지로의 변환을 정확히 알기 위해서는 카메라의 내부 파라미터를 사전에 알아야 합니다. 임의의 카메라가 주어졌을 때 이 파라미터들을 이미지로부터 추정하는 문제를 **카메라 캘리브레이션(camera calibration)**이라 합니다.

구체적으로는 식 (10)에서 내부 파라미터 $K$와 외부 파라미터 $R, T$를 구하는 것입니다.

### 5.1 캘리브레이션 리그 (Calibration Rig)

캘리브레이션은 보통 체커보드 패턴 같은 **캘리브레이션 리그(calibration rig)**를 사용합니다. 리그는 알려진 치수의 패턴으로 구성되며, 월드 기준 좌표계(원점 $O_w$, 축 $\mathbf{i}_w, \mathbf{j}_w, \mathbf{k}_w$)를 정의합니다.

리그의 알려진 패턴에서 월드 좌표의 점 $P_1, \ldots, P_n$을 알 수 있고, 카메라로 촬영한 이미지에서 이에 대응하는 점 $p_1, \ldots, p_n$을 찾을 수 있습니다.

### 5.2 선형 방정식 시스템 구성

$n$개의 대응점으로부터 다음과 같은 방정식을 세울 수 있습니다. 행벡터 $m_1, m_2, m_3$를 가진 카메라 행렬 $M$에 대해,

$$p_i = \begin{bmatrix} u_i \\ v_i \end{bmatrix} = MP_i = \begin{bmatrix} \frac{m_1 P_i}{m_3 P_i} \\ \frac{m_2 P_i}{m_3 P_i} \end{bmatrix} \tag{11}$$

각 대응점은 두 개의 방정식을 제공합니다.

$$u_i(m_3 P_i) - m_1 P_i = 0$$
$$v_i(m_3 P_i) - m_2 P_i = 0$$

$n$개의 대응점 전체에 대해 행렬-벡터 곱으로 정리하면,

$$\begin{bmatrix} P_1^T & 0^T & -u_1 P_1^T \\ 0^T & P_1^T & -v_1 P_1^T \\ \vdots & \vdots & \vdots \\ P_n^T & 0^T & -u_n P_n^T \\ 0^T & P_n^T & -v_n P_n^T \end{bmatrix} \begin{bmatrix} m_1^T \\ m_2^T \\ m_3^T \end{bmatrix} = \mathbf{P}m = 0 \tag{12}$$

카메라 행렬은 11개의 미지수를 가지므로, 최소 **6개의 대응점**이 필요합니다 ($2n > 11$). 실제로는 측정 노이즈 때문에 더 많이 사용합니다.

### 5.3 SVD를 이용한 풀이

$2n > 11$이면 연립방정식이 과결정(overdetermined)됩니다. $m = 0$은 항상 자명한 해이고, $m$이 해이면 $km$($k \in \mathbb{R}$)도 해입니다. 따라서 다음 최소화 문제를 풀어 해를 구합니다.

$$\underset{m}{\text{minimize}} \quad \|\mathbf{P}m\|^2 \quad \text{subject to} \quad \|m\|^2 = 1 \tag{13}$$

이 문제는 **특이값 분해(SVD)**로 풀 수 있습니다. $\mathbf{P} = UDV^T$로 분해하면, 해 $m$은 $V$의 마지막 열입니다.

### 5.4 내부/외부 파라미터 복원

SVD로 구한 $m$을 행렬 $M$으로 재구성합니다. $M$은 스케일만큼의 오차를 포함하므로, 실제 카메라 행렬의 값은 $M$의 어떤 스칼라 배입니다.

$$\rho M = \begin{bmatrix} \alpha r_1^T - \alpha \cot\theta\, r_2^T + c_x r_3^T & \alpha t_x - \alpha \cot\theta\, t_y + c_x t_z \\ \frac{\beta}{\sin\theta} r_2^T + c_y r_3^T & \frac{\beta}{\sin\theta} t_y + c_y t_z \\ r_3^T & t_z \end{bmatrix} \tag{14}$$

여기서 $r_1^T, r_2^T, r_3^T$는 $R$의 세 행입니다. $M = \begin{bmatrix} A & b \end{bmatrix} = \begin{bmatrix} a_1^T \\ a_2^T \\ a_3^T \end{bmatrix} \begin{bmatrix} b_1 \\ b_2 \\ b_3 \end{bmatrix}$으로 표기하면, 내부 파라미터는,

$$\rho = \pm \frac{1}{\|a_3\|}$$

$$c_x = \rho^2 (a_1 \cdot a_3)$$

$$c_y = \rho^2 (a_2 \cdot a_3)$$

$$\theta = \cos^{-1}\!\left(-\frac{(a_1 \times a_3) \cdot (a_2 \times a_3)}{\|a_1 \times a_3\| \cdot \|a_2 \times a_3\|}\right)$$

$$\alpha = \rho^2 \|a_1 \times a_3\| \sin\theta$$

$$\beta = \rho^2 \|a_2 \times a_3\| \sin\theta \tag{15}$$

외부 파라미터는,

$$r_1 = \frac{a_2 \times a_3}{\|a_2 \times a_3\|}, \quad r_2 = r_3 \times r_1, \quad r_3 = \rho a_3, \quad T = \rho K^{-1} b \tag{16}$$

### 5.5 퇴화 구성 (Degenerate Configurations)

모든 $n$개의 대응점 집합이 동작하는 것은 아닙니다. 예를 들어 점 $P_i$들이 같은 평면 위에 있으면 시스템을 풀 수 없습니다. 이처럼 풀 수 없는 점 배치를 **퇴화 구성(degenerate configurations)**이라 합니다. 일반적으로는 두 이차 곡면(quadric surfaces)의 교선 위에 점들이 놓인 경우가 퇴화 구성에 해당합니다.

---

## 6. 캘리브레이션에서 왜곡 처리 (Handling Distortion)

지금까지는 왜곡이 없는 이상적인 렌즈를 가정했습니다. 실제 렌즈는 직선 투영(rectilinear projection)에서 벗어날 수 있으며, 이를 처리하려면 더 발전된 방법이 필요합니다.

왜곡은 렌즈의 물리적 대칭성 때문에 방사형 대칭인 경우가 많습니다. 방사형 왜곡을 등방성 변환으로 모델링하면,

$$QP_i = \begin{bmatrix} \frac{1}{\lambda} & 0 & 0 \\ 0 & \frac{1}{\lambda} & 0 \\ 0 & 0 & 1 \end{bmatrix} MP_i = \begin{bmatrix} u_i \\ v_i \end{bmatrix} = p_i \tag{17}$$

이를 연립방정식으로 재구성하면 비선형 시스템이 되어, **비선형 최적화** 기법이 필요합니다. 단, 방사형 왜곡에서는 두 좌표의 비율 $u_i/v_i$가 영향받지 않는다는 점을 이용해 문제를 단순화할 수 있습니다.

$$\frac{u_i}{v_i} = \frac{m_1 P_i}{m_2 P_i} \tag{18}$$

이를 선형 방정식 시스템으로 만들면,

$$Ln = \begin{bmatrix} v_1 P_1^T & -u_1 P_1^T \\ \vdots & \vdots \\ v_n P_n^T & -u_n P_n^T \end{bmatrix} \begin{bmatrix} m_1^T \\ m_2^T \end{bmatrix} \tag{19}$$

$m_1$과 $m_2$를 추정하면, $m_3$는 $m_1, m_2, \lambda$의 비선형 함수로 표현되며, 원래 문제보다 훨씬 단순한 비선형 최적화 문제로 해결할 수 있습니다.

---

## 부록 A: 강체 변환 (Rigid Transformations)

기본적인 강체 변환에는 회전, 이동, 스케일링이 있습니다.

### 회전 (Rotation)

3D 공간에서의 회전은 각 좌표축을 기준으로 한 회전으로 표현할 수 있습니다. 관례적으로 반시계 방향이 양의 방향입니다.

**오일러 각(Euler angles)**은 각 자유도에서의 회전량을 나타내지만, **짐벌 락(gimbal lock)**이라는 특이점 문제가 생길 수 있습니다.

**회전 행렬(rotation matrix)**은 이를 피하기 위한 더 일반적인 표현으로, 행렬식이 1인 정방 직교 행렬입니다. 벡터 $v$의 회전 결과는 $v' = Rv$입니다. 각 축에 대한 회전 행렬은,

$$R_x(\alpha) = \begin{bmatrix} 1 & 0 & 0 \\ 0 & \cos\alpha & -\sin\alpha \\ 0 & \sin\alpha & \cos\alpha \end{bmatrix}$$

$$R_y(\beta) = \begin{bmatrix} \cos\beta & 0 & \sin\beta \\ 0 & 1 & 0 \\ -\sin\beta & 0 & \cos\beta \end{bmatrix}$$

$$R_z(\gamma) = \begin{bmatrix} \cos\gamma & -\sin\gamma & 0 \\ \sin\gamma & \cos\gamma & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

z축 → y축 → x축 순서로 회전하는 변환은 행렬 곱 $R_x R_y R_z$로 표현됩니다.

### 이동 (Translation)

이동 벡터 $t = \begin{bmatrix} t_x & t_y & t_z \end{bmatrix}^T$에 의한 점 $P$의 이동,

$$P' = P + t$$

동차 좌표를 이용해 이동 행렬로 표현하면,

$$T = \begin{bmatrix} 1 & 0 & 0 & t_x \\ 0 & 1 & 0 & t_y \\ 0 & 0 & 1 & t_z \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

회전 후 이동을 결합하면,

$$\begin{bmatrix} v' \\ 1 \end{bmatrix} = \begin{bmatrix} R & t \\ 0 & 1 \end{bmatrix} \begin{bmatrix} v \\ 1 \end{bmatrix}$$

### 스케일링 (Scaling)

$$S = \begin{bmatrix} S_x & 0 & 0 \\ 0 & S_y & 0 \\ 0 & 0 & S_z \end{bmatrix}$$

스케일링 → 회전 → 이동 순서의 최종 변환 행렬,

$$T = \begin{bmatrix} RS & t \\ 0 & 1 \end{bmatrix}$$

> 이 모든 변환(회전, 이동, 스케일링)은 **아핀 변환(affine transformations)**의 예입니다. **사영 변환(projective transformation)**은 $T$의 마지막 행이 $\begin{bmatrix} 0 & 0 & 0 & 1 \end{bmatrix}$이 아닌 경우에 발생합니다.

---

## 부록 B: 다양한 카메라 모델 (Different Camera Models)

### 약 원근 모델 (Weak Perspective Model)

**약 원근 모델(weak perspective model)**에서는 먼저 점들을 직교 투영으로 기준 평면에 투영한 뒤, 사영 변환으로 이미지 평면에 투영합니다.

카메라 중심에서 거리 $z_o$에 있는 기준 평면 $\Pi$에 대해, 점 $P, Q, R$을 직교 투영으로 평면에 투영합니다. 이는 깊이 편차가 카메라 거리에 비해 작을 때 합리적인 근사입니다.

각 점의 깊이를 $z_o$로 근사하면, 투영은 단순한 **일정 배율**로 줄어듭니다. 배율은 초점 거리 $f'$를 $z_o$로 나눈 값입니다.

$$x' = \frac{f'}{z_0} x \qquad y' = \frac{f'}{z_0} y$$

투영 행렬도 단순해집니다.

$$M = \begin{bmatrix} A & b \\ 0 & 1 \end{bmatrix}$$

일반 카메라 모델의 마지막 행이 $\begin{bmatrix} v & 1 \end{bmatrix}$인 것과 달리, 약 원근 모델에서는 $\begin{bmatrix} 0 & 0 & 0 & 1 \end{bmatrix}$입니다.

$$P' = MP = \begin{bmatrix} m_1 \\ m_2 \\ m_3 \end{bmatrix} P = \begin{bmatrix} m_1 P \\ m_2 P \\ 1 \end{bmatrix} \tag{20}$$

이미지 평면의 점이 결국 원래 3D 점의 배율(magnification)이 됩니다. 깊이와 무관하게 사영 변환의 비선형성이 사라지고, 약 원근 변환은 단순한 확대/축소가 됩니다.

### 직교 투영 모델 (Orthographic Projection Model)

약 원근 모델을 더 단순화한 것이 **직교(아핀) 투영 모델(orthographic/affine projection model)**입니다. 광학 중심이 무한대에 있어 투영 광선이 망막 평면에 수직이 됩니다. 결과적으로 깊이를 완전히 무시합니다.

$$x' = x, \qquad y' = y$$

직교 투영 모델은 건축이나 산업 디자인에서 자주 사용됩니다.

> **요약**
>
> 약 원근 모델은 수학이 훨씬 단순해지는 대신 정밀도가 약간 떨어집니다. 하지만 물체가 카메라에서 멀리 있고 크기가 작은 경우에는 매우 정확한 결과를 냅니다.
