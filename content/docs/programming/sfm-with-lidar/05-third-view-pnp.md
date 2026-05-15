---
title: "5편: 3번째 뷰 추가 — PnP"
date: 2026-05-15T00:00:00+09:00
draft: false
tags: ["SfM", "OpenCV", "PnP", "solvePnP", "Triangulation"]
categories: ["Programming"]
description: "이미 복원된 3D 포인트와 세 번째 이미지의 2D 대응점으로 solvePnP를 이용해 세 번째 카메라 pose를 추정합니다."
---

> 카메라 1, 2의 pose와 초기 3D 포인트가 확보된 상태입니다. 이제 세 번째 이미지를 등록합니다.

## PnP란

PnP(Perspective-n-Point)는 이미 알고 있는 3D 포인트 $X_i$와 새 이미지의 2D 투영점 $x_i$ 사이의 대응관계로 카메라 pose를 추정하는 문제입니다.

$$x_i = K [R | t] X_i$$

2-View 단계에서는 3D 포인트가 없어서 Essential Matrix가 필요했지만, 이제 3D 포인트가 있으므로 PnP로 바로 pose를 구할 수 있습니다. N-View SfM에서 세 번째 이후 모든 카메라가 이 방식으로 등록됩니다.

## 2D-3D 대응 구성

세 번째 이미지(frame 2)와 이미 복원된 3D 포인트 사이의 대응을 만들어야 합니다.

frame 1 ↔ frame 2 매칭(`pts1_2`, `pts2_1`)과 frame 0 ↔ frame 1 매칭에서 살아남은 3D 포인트를 연결합니다.

```python
def build_2d_3d_correspondences(pts3d, pts_prev, pts_next, inlier_mask_prev):
    """
    pts3d          : (M, 3) 이전 단계에서 복원된 3D 포인트
    pts_prev       : (M, 2) 3D 포인트에 대응하는 frame1 픽셀
    pts_next       : (N, 2) frame1 ↔ frame2 매칭의 frame1 쪽 픽셀
    inlier_mask_prev: (M,) bool — 유효한 3D 포인트 마스크
    """
    valid_pts3d = pts3d  # 이미 필터링된 상태
    valid_prev = pts_prev[inlier_mask_prev]

    # frame1 픽셀 좌표로 3D 포인트 ↔ frame2 픽셀 연결
    # 참고: 실제 SfM(COLMAP 등)에서는 여러 프레임에 걸친 Descriptor 매칭을 통해 
    # 'Feature Track(Track Graph)'을 구성하는 것이 정석입니다.
    # 본 튜토리얼에서는 복잡도를 낮추기 위해 픽셀 거리 기반의 휴리스틱을 사용합니다.
    correspondences_3d = []
    correspondences_2d = []

    for i, p1 in enumerate(valid_prev):
        # frame1↔frame2 매칭 중 같은 픽셀 탐색 (거리 기준)
        dists = np.linalg.norm(pts_next - p1, axis=1)
        j = np.argmin(dists)
        if dists[j] < 1.5:  # 1.5픽셀 이내
            correspondences_3d.append(valid_pts3d[i])
            correspondences_2d.append(pts_next[j])  # frame2 픽셀

    pts3d_corr = np.array(correspondences_3d, dtype=np.float64)
    pts2d_corr = np.array(correspondences_2d, dtype=np.float64)
    print(f"2D-3D 대응 수: {len(pts3d_corr)}")
    return pts3d_corr, pts2d_corr
```

## solvePnPRansac

```python
def estimate_pose_pnp(pts3d, pts2d, K):
    """
    pts3d: (N, 3) 3D 포인트
    pts2d: (N, 2) 이미지 픽셀 좌표
    K    : (3, 3) intrinsic
    반환 : R (3,3), t (3,1)
    """
    success, rvec, tvec, inliers = cv2.solvePnPRansac(
        pts3d.reshape(-1, 1, 3),
        pts2d.reshape(-1, 1, 2),
        K,
        distCoeffs=None,
        iterationsCount=1000,
        reprojectionError=2.0,
        confidence=0.999,
        flags=cv2.SOLVEPNP_ITERATIVE
    )

    if not success:
        raise RuntimeError("PnP 실패: 대응점 부족")

    R, _ = cv2.Rodrigues(rvec)
    print(f"PnP inliers: {len(inliers)} / {len(pts3d)}")
    return R, tvec, inliers.ravel()
```

## 세 번째 카메라 등록

```python
# 2D-3D 대응 구성
pts3d_corr, pts2d_corr = build_2d_3d_correspondences(
    pts3d_scaled, pts0_1[inlier_mask], pts1_2, inlier_mask
)

# PnP로 카메라 3 pose 추정
R3, t3, pnp_inliers = estimate_pose_pnp(pts3d_corr, pts2d_corr, K)

print(f"카메라 3 위치: {t3.ravel()}")
```

## 새 3D 포인트 추가

세 번째 카메라가 등록되었으니, frame 1 ↔ frame 2 쌍에서 아직 3D 포인트가 없는 매칭을 삼각측량해 추가합니다.

```python
def add_new_points(pts_a, pts_b, R_a, t_a, R_b, t_b, K):
    P_a = K @ np.hstack([R_a, t_a])
    P_b = K @ np.hstack([R_b, t_b])
    new_pts3d = triangulate(pts_a, pts_b, P_a, P_b)
    new_pts3d, _ = filter_points(new_pts3d, R_a, t_a, R_b, t_b)
    return new_pts3d

new_pts3d = add_new_points(pts1_2, pts2_1, R2, t2_scaled, R3, t3, K)

# 전체 포인트클라우드 합치기
all_pts3d = np.vstack([pts3d_scaled, new_pts3d])
print(f"전체 3D 포인트: {len(all_pts3d)}")
# 예: 전체 3D 포인트: 3217
```

## 복원된 카메라 Pose 정리

```python
camera_poses = {
    'frame0': {'R': R1, 't': t1},
    'frame1': {'R': R2, 't': t2_scaled},
    'frame2': {'R': R3, 't': t3},
}

for name, pose in camera_poses.items():
    # 카메라 중심 = -R^T t
    center = -pose['R'].T @ pose['t'].ravel()
    print(f"{name} 위치: {center}")
```

---

## 다음 편 예고

세 카메라의 pose와 전체 포인트클라우드를 Rerun SDK로 시각화하고, LiDAR GT와 비교합니다.
