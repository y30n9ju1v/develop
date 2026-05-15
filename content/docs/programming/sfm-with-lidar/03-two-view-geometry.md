---
title: "3편: 2-View Geometry"
date: 2026-05-15T00:00:00+09:00
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

`recoverPose`는 $E$에서 가능한 4가지 (R, t) 조합 중 3D 포인트가 두 카메라 앞에 오는 해를 자동으로 선택합니다.

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
def filter_points(pts3d, R1, t1, R2, t2, max_depth=50.0):
    """카메라 앞에 있고 너무 멀지 않은 포인트만 유지"""
    # 카메라 1 기준 depth
    pts_cam1 = (R1 @ pts3d.T + t1).T
    depth1 = pts_cam1[:, 2]

    # 카메라 2 기준 depth
    pts_cam2 = (R2 @ pts3d.T + t2).T
    depth2 = pts_cam2[:, 2]

    mask = (depth1 > 0) & (depth2 > 0) & (depth1 < max_depth) & (depth2 < max_depth)
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

# 4. 필터링
pts3d_init, valid_mask = filter_points(pts3d_init, R1, t1.ravel(), R2, t2.ravel())

print(f"초기 3D 포인트 수: {len(pts3d_init)}")
# 예: 초기 3D 포인트 수: 1842
```

---

## 다음 편 예고

복원된 `t2`의 크기가 임의적입니다 (scale ambiguity). 다음 편에서 LiDAR depth map으로 절대 스케일을 복원합니다.
