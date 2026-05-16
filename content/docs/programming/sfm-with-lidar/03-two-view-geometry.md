---
title: "3편: 2-View Geometry"
date: 2026-05-15T02:00:00+09:00
draft: false
tags: ["SfM", "OpenCV", "Essential Matrix", "Triangulation", "Epipolar Geometry"]
categories: ["Programming"]
description: "Essential Matrix로 두 카메라의 상대 pose를 복원하고 초기 3D 포인트를 삼각측량합니다."
---

> 이전 편에서 찾은 대응점으로 카메라 1과 2 사이의 상대 pose (R, t)를 복원하고, 초기 3D 포인트를 생성합니다.

## Essential Matrix

두 카메라의 대응점 사이에는 다음 기하학적 제약이 성립합니다.

$$\mathbf{x}_2^T E \mathbf{x}_1 = 0$$

여기서 $\mathbf{x}_1$, $\mathbf{x}_2$는 각 이미지의 정규화 좌표(normalized coordinate), $E$는 Essential Matrix입니다.

> **왜 이 제약이 성립할까?**
>
> 카메라 1의 원점(O₁), 카메라 2의 원점(O₂), 그리고 3D 점(P) — 이 세 점은 항상 **하나의 평면(epipolar plane)** 위에 있습니다.
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
> $$\mathbf{x}_2 \cdot (\mathbf{t} \times R\mathbf{x}_1) = 0$$
>
> 여기서 `t`는 O₁→O₂ translation, `R`은 두 카메라 간 회전입니다. 이를 행렬로 정리하면 $E = [t]_\times R$ 이 되고 ($[t]_\times$는 `t`의 skew-symmetric matrix), 결국 $\mathbf{x}_2^T E \mathbf{x}_1 = 0$ 이 됩니다.
>
> 한 줄 요약: **"두 카메라와 3D 점이 항상 한 평면을 이루기 때문에, 그 평면 조건을 수식으로 쓰면 $\mathbf{x}_2^T E \mathbf{x}_1 = 0$이 된다"**

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

`recoverPose`는 $E$에서 가능한 4가지 (R, t) 조합 중 3D 포인트가 두 카메라 앞에 오는 해를 자동으로 선택합니다. 이 과정에서 유효하지 않은 대응점을 걸러내는 `mask_pose`를 반환하므로, 삼각측량 시 이 마스크를 반드시 적용해야 합니다.

**주의:** 복원된 `t`는 방향만 맞고 크기(scale)가 없습니다. 이 문제는 4편에서 LiDAR로 해결합니다.

## 카메라 Pose 초기화

카메라 1을 world 좌표계의 원점으로 설정합니다.

```python
# 카메라 1: world 원점
R1 = np.eye(3)
t1 = np.zeros((3, 1))

# 카메라 2: 카메라 1 기준 상대 pose
R2, t2, inlier_mask = recover_pose(pts0_1, pts1_0, K)

# Projection matrix: P = K [R | t]
P1 = K @ np.hstack([R1, t1])  # (3, 4)
P2 = K @ np.hstack([R2, t2])  # (3, 4)
```

## 삼각측량 (Triangulation)

두 카메라에서 같은 3D 점을 바라보는 두 광선(ray)의 교점을 구합니다.

$$\lambda_1 \mathbf{x}_1 = P_1 \mathbf{X}, \quad \lambda_2 \mathbf{x}_2 = P_2 \mathbf{X}$$

`cv2.triangulatePoints`는 DLT(Direct Linear Transform)로 이를 풉니다.

```python
def triangulate(pts_a, pts_b, P1, P2, mask=None):
    if mask is not None:
        pts_a = pts_a[mask]
        pts_b = pts_b[mask]

    # triangulatePoints는 (2, N) 입력을 받음
    pts4d = cv2.triangulatePoints(P1, P2, pts_a.T, pts_b.T)  # (4, N)

    # 동차 좌표 → 3D 좌표
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
