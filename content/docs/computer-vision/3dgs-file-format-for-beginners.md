---
title: "3D Gaussian Splatting 저장 포맷 입문"
date: 2026-05-13T09:00:00+09:00
draft: false
tags: ["3DGS", "Gaussian Splatting", "PLY", "3D", "입문"]
categories: ["computer-vision"]
description: "3D Gaussian Splatting이 장면을 어떻게 저장하는지, PLY 파일 구조와 각 속성의 의미를 초보자 눈높이에서 설명합니다."
math: true
---

## 3DGS가 뭔가요?

사진 몇 장으로 3D 장면을 복원하는 기술이 있습니다. 예전에는 **NeRF(Neural Radiance Field)**가 많이 쓰였지만, 2023년 등장한 **3D Gaussian Splatting(3DGS)**은 훨씬 빠른 렌더링 속도와 높은 화질로 주목받고 있습니다.

핵심 아이디어는 간단합니다. 장면을 수백만 개의 **반투명한 타원형 덩어리(Gaussian)**로 표현하는 것입니다. 카메라에서 보면 이 덩어리들이 겹쳐 보이면서 사진과 같은 이미지가 만들어집니다.

```
사진 여러 장
    ↓  학습 (최적화)
수백만 개의 3D Gaussian
    ↓  렌더링 (Splatting)
새로운 시점의 이미지
```

---

## Gaussian 하나가 담고 있는 정보

3DGS의 저장 포맷을 이해하려면 먼저 **Gaussian 하나가 무엇을 표현하는지** 알아야 합니다.

현실의 물체를 생각해 보세요. 어떤 물체든 세 가지 정보가 있으면 묘사할 수 있습니다.

| 질문 | 답 | 3DGS 속성 |
|---|---|---|
| 어디 있나요? | 공간 위치 | **위치 (xyz)** |
| 어떻게 생겼나요? | 크기, 방향 | **공분산 (covariance)** |
| 무슨 색인가요? | 색, 투명도 | **색상 (SH계수) + 불투명도 (opacity)** |

Gaussian 하나는 이 세 가지를 모두 담습니다.

---

## 저장 포맷: PLY 파일

3DGS는 학습이 끝나면 결과물을 **PLY(Polygon File Format)** 파일로 저장합니다. PLY는 원래 3D 메시(삼각형 망)를 저장하던 포맷이지만, 3DGS는 메시 대신 **점(point)마다 여러 속성을 붙이는 방식**으로 활용합니다.

### PLY 파일 헤더 보기

실제 3DGS PLY 파일을 열면 헤더가 이렇게 생겼습니다.

```
ply
format binary_little_endian 1.0
element vertex 3200000
property float x
property float y
property float z
property float nx
property float ny
property float nz
property float f_dc_0
property float f_dc_1
property float f_dc_2
property float f_rest_0
...
property float f_rest_44
property float opacity
property float scale_0
property float scale_1
property float scale_2
property float rot_0
property float rot_1
property float rot_2
property float rot_3
end_header
[이후 바이너리 데이터]
```

`element vertex 3200000`은 이 파일에 320만 개의 Gaussian이 있다는 뜻입니다. 각 Gaussian마다 위의 속성들이 순서대로 저장됩니다.

---

## 속성별 의미

### 위치: x, y, z

Gaussian의 중심 좌표입니다. 단위는 학습에 사용한 장면의 스케일에 따라 다릅니다.

```
x: 0.3241
y: -1.2045
z: 0.8821
```

### 법선: nx, ny, nz

원래 PLY 포맷에서 법선 벡터를 저장하던 자리입니다. 3DGS에서는 실제로 사용하지 않아 **항상 0**입니다. 포맷 호환성을 위해 남겨둔 자리입니다.

### 색상: f_dc와 f_rest (구면 조화 함수)

색상은 단순히 RGB 세 값이 아닙니다. 3DGS는 **구면 조화 함수(Spherical Harmonics, SH)**를 사용해서 **보는 방향에 따라 색이 달라지는 효과**를 표현합니다. 유리나 금속처럼 각도에 따라 색이 변하는 재질을 표현할 수 있습니다.

```
보는 방향 A → 파란색
보는 방향 B → 초록색
         ↑ 같은 Gaussian, 다른 색
```

| 속성 | 의미 |
|---|---|
| `f_dc_0`, `f_dc_1`, `f_dc_2` | SH 0차 계수 (방향 무관 기본 색, RGB 각 채널) |
| `f_rest_0` ~ `f_rest_44` | SH 1~3차 계수 (방향에 따른 색 변화) |

기본 구현(degree=3)에서는 채널당 16개 계수, RGB 3채널이므로 총 $3 \times 16 = 48$개입니다. `f_dc` 3개 + `f_rest` 45개 합이 48개가 됩니다.

> **처음엔 f_dc만 봐도 됩니다.** f_dc가 해당 Gaussian의 대표 색입니다. f_rest는 시점에 따른 미세한 색 변화를 담습니다.

### 불투명도: opacity

Gaussian이 얼마나 불투명한지를 나타냅니다. 파일에는 **로짓(logit) 값**으로 저장됩니다. 실제 불투명도(0~1)로 변환하려면 시그모이드 함수를 적용합니다.

$$\alpha = \sigma(\text{opacity}) = \frac{1}{1 + e^{-\text{opacity}}}$$

```python
import numpy as np

opacity_raw = 2.5          # 파일에 저장된 값
alpha = 1 / (1 + np.exp(-opacity_raw))  # → 0.924 (매우 불투명)
```

값이 클수록 불투명(1에 가까움), 작을수록 투명(0에 가까움)합니다.

### 크기: scale_0, scale_1, scale_2

Gaussian의 세 축 방향 크기입니다. 파일에는 **로그(log) 값**으로 저장됩니다.

$$s_i = e^{\text{scale}_i}$$

```python
scale_raw = [-3.2, -3.8, -4.1]
scale = np.exp(scale_raw)  # → [0.041, 0.022, 0.017] (단위: 장면 스케일)
```

세 값이 비슷하면 구에 가깝고, 차이가 크면 납작한 타원체가 됩니다. 벽면, 바닥처럼 평평한 표면은 한 축이 매우 작은 납작한 Gaussian으로 표현됩니다.

### 회전: rot_0, rot_1, rot_2, rot_3

Gaussian 타원체의 방향을 나타내는 **쿼터니언(quaternion)** 값입니다. 쿼터니언은 3D 회전을 4개 값으로 표현하는 방식입니다.

$$q = (w, x, y, z), \quad w^2 + x^2 + y^2 + z^2 = 1$$

파일에서 rot_0이 $w$, rot_1~3이 $x, y, z$에 해당합니다. 파일에 저장된 값은 정규화되지 않을 수 있으므로, 사용 전에 단위 쿼터니언으로 정규화해야 합니다.

---

## Python으로 PLY 파일 읽기

```python
from plyfile import PlyData
import numpy as np

plydata = PlyData.read("point_cloud.ply")
vertices = plydata["vertex"]

# 위치
xyz = np.stack([vertices["x"], vertices["y"], vertices["z"]], axis=-1)

# 색상 (f_dc만 사용, SH → RGB 근사)
# SH 0차 계수에서 RGB로 변환: C0 = 0.28209479177387814
C0 = 0.28209479177387814
rgb = np.stack([
    vertices["f_dc_0"] * C0 + 0.5,
    vertices["f_dc_1"] * C0 + 0.5,
    vertices["f_dc_2"] * C0 + 0.5,
], axis=-1).clip(0, 1)

# 불투명도
opacity = 1 / (1 + np.exp(-vertices["opacity"]))

# 크기
scale = np.exp(np.stack([
    vertices["scale_0"],
    vertices["scale_1"],
    vertices["scale_2"],
], axis=-1))

print(f"Gaussian 수: {len(xyz):,}")
print(f"위치 범위 (x): {xyz[:, 0].min():.2f} ~ {xyz[:, 0].max():.2f}")
print(f"불투명도 평균: {opacity.mean():.3f}")
```

---

## 파일 크기는 얼마나 될까?

Gaussian 하나당 속성이 많아서 파일이 꽤 큽니다.

| 속성 | 값 수 | 크기 (float32) |
|---|---|---|
| 위치 (xyz) | 3 | 12 bytes |
| 법선 (nx, ny, nz) | 3 | 12 bytes |
| 색상 (f_dc + f_rest) | 48 | 192 bytes |
| 불투명도 | 1 | 4 bytes |
| 크기 (scale) | 3 | 12 bytes |
| 회전 (rot) | 4 | 16 bytes |
| **합계** | **62** | **248 bytes** |

Gaussian 300만 개 기준으로 약 **744 MB**입니다. 실제 파일은 바이너리 압축 여부에 따라 다르지만, 수백 MB가 일반적입니다.

---

## 정리

| 속성 | 저장 형태 | 변환 방법 |
|---|---|---|
| 위치 (xyz) | 그대로 | 없음 |
| 색상 (f_dc) | SH 계수 | `× C0 + 0.5` |
| 불투명도 | logit | sigmoid |
| 크기 | log | exp |
| 회전 | 쿼터니언 | 정규화 후 사용 |

3DGS PLY 파일은 결국 **수백만 개의 타원체 목록**입니다. 각 타원체의 위치, 형태, 색, 투명도를 숫자로 나열한 것이 전부입니다. 렌더링 엔진은 이 목록을 카메라 시점에 맞춰 화면에 투영(Splatting)해서 이미지를 만들어냅니다.
