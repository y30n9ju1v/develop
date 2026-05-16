---
title: "3편: 2-View Geometry"
date: 2026-05-15T02:00:00+09:00
draft: false
tags: ["SfM", "OpenCV", "Essential Matrix", "Triangulation", "Epipolar Geometry"]
categories: ["Programming"]
description: "Essential Matrix로 두 카메라의 상대 pose를 복원하고 초기 3D 포인트를 삼각측량합니다."
---

> 이전 편에서 찾은 대응점으로 카메라 1과 2 사이의 상대 pose (R, t)를 복원하고, 초기 3D 포인트를 생성합니다.

## Essential Matrix: 두 카메라 사이의 관계도

> **💡 직관적으로 이해하기**
> 친구 두 명이 서로 다른 위치에서 같은 사과를 사진 찍었다고 해보겠습니다. 
> 첫 번째 친구가 서 있는 위치와 카메라 방향(카메라 1)을 기준으로 할 때, 두 번째 친구가 "어디로 얼마나 걸어가서, 어느 방향으로 카메라를 돌렸는지"를 나타내는 정보가 필요합니다. 이 **위치 이동(Translation)과 회전(Rotation) 정보를 하나의 수학적 상자에 담아둔 것**이 바로 **Essential Matrix (에센셜 행렬, E)** 입니다.

두 카메라의 대응점 사이에는 다음 기하학적 제약이 성립합니다.

$$\mathbf{x}_2^T E \mathbf{x}_1 = 0$$

여기서 $\mathbf{x}_1$, $\mathbf{x}_2$는 각 이미지의 정규화 좌표(normalized coordinate), $E$는 Essential Matrix입니다.

> **정규화 좌표(normalized coordinate)란?**
>
> 카메라 intrinsic(K)을 제거한 좌표입니다. 픽셀 좌표 `(u, v)`를 K의 역행렬로 변환하면 카메라 렌즈와 해상도의 영향을 없앤 순수한 방향 벡터가 됩니다.
>
> ```
> 픽셀 좌표: (u, v)
> 정규화 좌표: x = K⁻¹ [u, v, 1]ᵀ
>
> 예) u=3119, v=2057, K의 fx=3430, cx=3119, cy=2057 이면:
>     x = [(3119-3119)/3430, (2057-2057)/3430, 1] = [0, 0, 1]  # 이미지 중심
> ```
>
> 정규화 좌표를 쓰는 이유는 Essential Matrix가 카메라 종류에 무관한 순수 기하학적 관계(R, t)만 담게 하기 위해서입니다.

> **왜 이 제약이 성립할까? (Epipolar Geometry)**
>
> 복잡한 수식 전에 머릿속으로 그림을 그려봅시다. 
> 내 오른쪽 눈(카메라 1), 왼쪽 눈(카메라 2), 그리고 내 앞에 있는 모니터(3D 점 P)를 상상해 보세요. 이 세 개의 점을 선으로 연결하면 공중에 떠 있는 커다란 **하나의 삼각형(평면)** 이 만들어집니다. 이것을 **Epipolar Plane(에피폴라 평면)** 이라고 부릅니다.
>
> 정리하자면, 카메라 1의 원점(O₁), 카메라 2의 원점(O₂), 그리고 3D 점(P) — 이 세 점은 항상 **하나의 평면(epipolar plane)** 위에 있습니다.
>
> ```
> (위에서 본 모습)
>
> O₁ ----t---- O₂
>  \           /
>   \         /
>    \       /
>     \     /
>        P
> ```
>
> 같은 평면 위의 세 벡터는 **스칼라 삼중적(scalar triple product)이 0**이어야 합니다.
>
> 스칼라 삼중적 `a · (b × c)`은 세 벡터가 이루는 평행육면체의 부피입니다. 세 벡터가 같은 평면에 있으면 부피가 0이 됩니다. O₁, O₂, P가 항상 같은 평면에 있으므로 이 값이 0이 됩니다.
>
> $$\mathbf{x}_2 \cdot (\mathbf{t} \times R\mathbf{x}_1) = 0$$
>
> 여기서 `t`는 O₁→O₂ translation, `R`은 두 카메라 간 회전입니다. 이를 행렬로 정리하면 $E = [t]_\times R$ 이 되고 ($[t]_\times$는 `t`의 skew-symmetric matrix), 결국 $\mathbf{x}_2^T E \mathbf{x}_1 = 0$ 이 됩니다.
>
> 한 줄 요약: **"두 카메라와 3D 점이 항상 한 평면을 이루기 때문에, 그 평면 조건을 수식으로 쓰면 $\mathbf{x}_2^T E \mathbf{x}_1 = 0$이 된다"**

> **예제로 확인하기**
>
> 카메라 1이 원점, 카메라 2가 오른쪽으로 1m 이동하고 회전 없는 상황을 가정합니다.
>
> ```
> t = [1, 0, 0],  R = I
> E = [t]× R = [[ 0,  0,  0],
>               [ 0,  0, -1],
>               [ 0,  1,  0]]
> ```
>
> `[t]×`는 벡터 `t = [tx, ty, tz]`를 다음 규칙으로 행렬화한 것입니다 (skew-symmetric matrix):
>
> ```
> [t]× = [[ 0,  -tz,  ty],
>          [ tz,   0, -tx],
>          [-ty,  tx,   0]]
> ```
>
> `t = [1, 0, 0]` (tx=1, ty=0, tz=0) 을 대입하면 위 E가 나옵니다. `R = I` 이므로 `E = [t]× I = [t]×` 입니다. 이 행렬화의 의미는 `t × v` (크로스 곱)를 행렬 곱 `[t]× v`로 표현한 것입니다.
>
> **왜 skew-symmetric matrix로 변환할까?**
>
> 크로스 곱을 행렬 곱으로 바꾸기 위해서입니다. epipolar constraint 원형은 크로스 곱과 내적이 섞여 있어 정리하기 어렵습니다.
>
> ```
> x2 · (t × Rx1) = 0          # 크로스 곱 + 내적 혼재
>
> t × v = [t]× v 로 치환하면:
>
> x2ᵀ ([t]× R) x1 = 0         # 행렬 곱만 남음
> x2ᵀ  E  x1      = 0         # E = [t]× R 로 정의
> ```
>
> 크로스 곱 `t × v`를 전개하면:
>
> ```
> t × v = [ty·vz - tz·vy,
>           tz·vx - tx·vz,
>           tx·vy - ty·vx]
> ```
>
> 각 행에서 v의 성분을 밖으로 꺼내면:
>
> ```
> 1번째 행: ty·vz - tz·vy  =   0·vx + (-tz)·vy +  ty·vz
> 2번째 행: tz·vx - tx·vz  =  tz·vx +   0·vy + (-tx)·vz
> 3번째 행: tx·vy - ty·vx  = (-ty)·vx + tx·vy +   0·vz
> ```
>
> 계수만 모으면:
>
> ```
> [[ 0,  -tz,  ty],   [vx]
>  [ tz,   0, -tx], × [vy]  =  [t]× v
>  [-ty,  tx,   0]]   [vz]
> ```
>
> 이게 바로 `[t]×` 입니다. 대각이 0이고 `A = -Aᵀ`인 skew-symmetric 구조는 의도한 게 아니라 크로스 곱을 전개하다 보니 자연스럽게 나온 모양입니다.
>
> 3D 점 P = (2, 0, 5) 에 대해:
>
> ```
> x1 = [2/5, 0/5, 1] = [0.4, 0, 1]   # 카메라 1 normalized
> x2 = [1/5, 0/5, 1] = [0.2, 0, 1]   # 카메라 2 normalized (P를 카메라 2 기준으로 변환하면 (1,0,5))
>
> E x1 = [0, -1, 0]
> x2ᵀ (E x1) = 0.2×0 + 0×(-1) + 1×0 = 0  ✓
> ```
>
> 잘못 매칭된 점이라면 이 값이 0이 아닌 값이 나오고, RANSAC이 해당 매칭을 outlier로 걸러냅니다.

> **용어 짚고 가기: Epipolar Line과 Epipole**
> 카메라 1의 중심과 3D 점 P를 잇는 광선이 카메라 2의 이미지 평면에 투영된 선을 **Epipolar Line**이라고 합니다. 점 $\mathbf{x}_1$에 대응하는 점 $\mathbf{x}_2$는 반드시 이 선 위에 존재해야 한다는 것이 에피폴라 기하학의 핵심 제약입니다. 두 카메라의 중심을 이은 선이 각 이미지 평면과 만나는 점은 **Epipole**이라고 부릅니다.

**Fundamental Matrix vs Essential Matrix:**
- Fundamental Matrix $F$: pixel 좌표 사이의 관계 (intrinsic 무관)
- Essential Matrix $E$: 정규화 좌표 사이의 관계 (intrinsic 포함) → $E = K_2^T F K_1$

Essential Matrix를 쓰는 이유는 여기서 직접 $R$, $t$를 분해할 수 있기 때문입니다.

## Essential Matrix 추정 및 Pose 복원

```python
def recover_pose(pts_a, pts_b, K):
    """
    pts_a, pts_b: (N, 2) pixel 좌표
    K: (3, 3) intrinsic matrix
    반환: R (3,3), t (3,1), inlier mask
    """
    # 고해상도 이미지(6K)를 고려하여 threshold를 3.0으로 설정
    E, mask = cv2.findEssentialMat(
        pts_a, pts_b, K,
        method=cv2.RANSAC,
        prob=0.999,
        threshold=3.0
    )

    _, R, t, mask_pose = cv2.recoverPose(E, pts_a, pts_b, K, mask=mask)
    return R, t, mask_pose.ravel().astype(bool)
```

`recoverPose`는 $E$에서 가능한 4가지 (R, t) 조합 중 3D 포인트가 두 카메라 앞에 오는 해를 자동으로 선택하고, 유효하지 않은 대응점을 걸러내는 `mask_pose`를 반환합니다. 삼각측량 시 이 마스크를 반드시 적용해야 합니다.

> **왜 4가지 해가 나올까?**
>
> Essential Matrix를 SVD로 분해하면 R과 t 각각 2가지 후보가 나옵니다.
>
> ```
> R: R₁ 또는 R₂  (2가지)
> t: +t 또는 -t   (2가지)
> → 조합: 2 × 2 = 4가지
> ```
>
> 4가지 중 실제로 의미 있는 해는 하나입니다 — 3D 점이 두 카메라 **앞**에 있어야 하기 때문입니다. 카메라 뒤에 3D 점이 복원되는 경우는 물리적으로 불가능하므로 나머지 3개는 자동으로 제거됩니다.

> **💡 핵심 개념: Scale Ambiguity (스케일 모호성)**
>
> 사진만으로는 우리가 찍은 것이 "실제 10m 크기의 커다란 집"인지, 아니면 "10cm 크기의 정교한 장난감 집"인지 알 방법이 없습니다. 복원된 `t`는 방향만 맞고 크기(scale)가 없습니다. 이 문제는 4편에서 LiDAR depth로 해결합니다.

## 카메라 Pose 초기화

카메라 1을 world 좌표계의 원점으로 설정합니다.

```python
# 카메라 1: world 원점
R1 = np.eye(3)
t1 = np.zeros((3, 1))

# 카메라 2: 카메라 1 기준 상대 pose
R2, t2, inlier_mask = recover_pose(pts0_1, pts1_0, K)

# Projection matrix: P = K [R | t]
# 3D 점 X를 2D 픽셀로 투영: x = P X = K[R|t] X
P1 = K @ np.hstack([R1, t1])  # (3, 4)
P2 = K @ np.hstack([R2, t2])  # (3, 4)
```

## 삼각측량 (Triangulation): 2D 사진에서 3D 공간으로

> **💡 직관적으로 이해하기**
> 밤하늘에 떠 있는 별 하나를 두 사람이 서로 다른 위치에서 각자의 손가락으로 가리키고 있다고 상상해 보세요. 두 사람의 눈에서 손가락 끝을 향해 뻗어나가는 두 개의 가상의 레이저 선이 만나는 교차점, 그곳이 바로 별의 실제 3D 위치입니다. 이것이 삼각측량의 기본 원리입니다.

두 카메라에서 같은 3D 점을 바라보는 두 광선(ray)의 교점을 구합니다. 즉, 2D 이미지 좌표계에 있던 점들을 3D 공간 좌표로 복원하는 과정입니다.

$$\lambda_1 \mathbf{x}_1 = P_1 \mathbf{X}, \quad \lambda_2 \mathbf{x}_2 = P_2 \mathbf{X}$$

`cv2.triangulatePoints`는 DLT(Direct Linear Transform)로 이를 풉니다.

> **동차 좌표(Homogeneous Coordinate)란?**
>
> 3D 점 `(X, Y, Z)`를 `(X, Y, Z, W)` 4개 숫자로 표현하는 방식입니다. 실제 좌표는 W로 나눠서 얻습니다.
>
> ```
> 동차 좌표: [2, 4, 10, 2]  →  실제 좌표: [2/2, 4/2, 10/2] = [1, 2, 5]
> ```
>
> 쓰는 이유는 투영(projection), 회전, 이동 변환을 **하나의 행렬 곱**으로 통일해서 표현할 수 있기 때문입니다. `triangulatePoints`가 4D로 반환하는 것도 이 때문입니다.

```python
def triangulate(pts_a, pts_b, P1, P2, mask=None):
    if mask is not None:
        pts_a = pts_a[mask]
        pts_b = pts_b[mask]

    # triangulatePoints는 (2, N) 입력을 받음
    pts4d = cv2.triangulatePoints(P1, P2, pts_a.T, pts_b.T)  # (4, N)

    # 동차 좌표(homogeneous) → 3D 좌표
    # triangulatePoints는 [X, Y, Z, W] 형태로 반환. 실제 좌표는 각 성분을 W로 나눈 값
    pts3d = (pts4d[:3] / pts4d[3]).T  # (N, 3)
    return pts3d
```

## 포인트 품질 필터링

삼각측량 결과 중 신뢰할 수 없는 포인트를 제거합니다.

```python
def filter_points(pts3d, pts_a, pts_b, K, R1, t1, R2, t2, max_depth=50.0, max_reproj_err=2.0):
    """카메라 앞에 있고 너무 멀지 않으며, 투영 오차가 작은 포인트만 유지"""
    # 1. Depth 검증 (Z > 0)
    pts_cam1 = (R1 @ pts3d.T + t1).T
    depth1 = pts_cam1[:, 2]

    # 카메라 2 기준 depth
    pts_cam2 = (R2 @ pts3d.T + t2).T
    depth2 = pts_cam2[:, 2]

    depth_mask = (depth1 > 0) & (depth2 > 0) & (depth1 < max_depth) & (depth2 < max_depth)

    # 2. 재투영 오차(Reprojection Error) 검증
    # 카메라 1에 투영 (projectPoints는 rotation vector를 받으므로 Rodrigues로 변환)
    proj1, _ = cv2.projectPoints(pts3d, cv2.Rodrigues(R1)[0], t1, K, None)
    err1 = np.linalg.norm(pts_a - proj1.squeeze(), axis=1)

    # 카메라 2에 투영
    proj2, _ = cv2.projectPoints(pts3d, cv2.Rodrigues(R2)[0], t2, K, None)
    err2 = np.linalg.norm(pts_b - proj2.squeeze(), axis=1)

    reproj_mask = (err1 < max_reproj_err) & (err2 < max_reproj_err)

    # 최종 마스크
    mask = depth_mask & reproj_mask
    print(f"유효 포인트: {mask.sum()} / {len(pts3d)}")
    return pts3d[mask], mask
```

## 전체 흐름

```python
# 1. Pose 복원
R2, t2, inlier_mask = recover_pose(pts0_1, pts1_0, K)

# 2. Projection matrix
R1 = np.eye(3)
t1 = np.zeros((3, 1))
P1 = K @ np.hstack([R1, t1])
P2 = K @ np.hstack([R2, t2])

# 3. 삼각측량
pts3d_init = triangulate(pts0_1, pts1_0, P1, P2, mask=inlier_mask)

# 4. 필터링 (재투영 오차 검증을 위해 inlier 마스크가 적용된 2D 포인트 사용)
valid_pts0_1 = pts0_1[inlier_mask]
valid_pts1_0 = pts1_0[inlier_mask]

pts3d_init, valid_mask = filter_points(
    pts3d_init, valid_pts0_1, valid_pts1_0, K, 
    R1, t1, R2, t2
)

print(f"초기 3D 포인트 수: {len(pts3d_init)}")
# 예: 초기 3D 포인트 수: 1842
```

---

## 다음 편 예고

복원된 `t2`의 크기가 임의적입니다 (scale ambiguity). 다음 편에서 LiDAR depth map으로 절대 스케일을 복원합니다.
