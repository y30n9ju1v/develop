---
title: "4편: LiDAR로 Scale 복원"
date: 2026-05-15T03:00:00+09:00
draft: true
tags: ["SfM", "LiDAR", "Scale Ambiguity", "OpenCV", "ETH3D"]
categories: ["programming"]
description: "카메라 SfM의 근본적인 한계인 scale ambiguity를 LiDAR depth로 해결합니다."
---

> 3편에서 복원한 3D 포인트는 실제 크기를 모릅니다. LiDAR GT 포인트클라우드를 이용해 절대 스케일을 복원합니다.

## Scale Ambiguity란

카메라 SfM은 본질적으로 스케일을 알 수 없습니다. 카메라 두 대 사이의 거리가 1m인지 10m인지 이미지만으로는 구분이 불가능합니다.

`cv2.recoverPose`가 반환하는 `t`는 단위 벡터입니다. 즉:

$$\hat{t} = \frac{t}{\|t\|}$$

실제 이동 거리 $s$(scale)를 곱해야 올바른 translation을 얻습니다.

$$t_{\text{real}} = s \cdot \hat{t}$$

## LiDAR로 Scale 복원하기

ETH3D는 LiDAR GT 포인트클라우드(`scan_clean.ply`)를 제공합니다. 이 포인트들은 실제 미터 단위의 3D 좌표를 갖습니다.

핵심 아이디어:
1. SfM으로 복원한 3D 포인트 $X_{\text{sfm}}$와 LiDAR 포인트 $X_{\text{lidar}}$ 중 대응하는 쌍을 찾는다
2. 두 집합의 거리 비율로 스케일 $s$를 추정한다

$$s = \frac{\|X_{\text{lidar}}\|}{\|X_{\text{sfm}}\|}$$

## 방법 1: Depth 비율로 직접 추정

카메라 1의 이미지 픽셀 위치에서 LiDAR depth와 SfM depth를 비교합니다.

```python
def estimate_scale_from_depth(pts3d_sfm, pts2d, lidar_points, K, R, t, n_samples=200):
    """
    pts3d_sfm : (N, 3) SfM 3D 포인트 (단위 스케일)
    pts2d     : (N, 2) 대응하는 이미지 픽셀 좌표
    lidar_points: (M, 3) LiDAR GT 포인트클라우드
    K         : (3, 3) intrinsic
    """
    import open3d as o3d

    # LiDAR 포인트를 KD-tree로 인덱싱
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(lidar_points)
    tree = o3d.geometry.KDTreeFlann(pcd)

    # 각 SfM 포인트를 이미지에 투영해 LiDAR depth와 비교
    scales = []
    for i in range(min(n_samples, len(pts3d_sfm))):
        # SfM depth (카메라 좌표계)
        pt_cam = R @ pts3d_sfm[i] + t.ravel()
        sfm_depth = pt_cam[2]
        if sfm_depth <= 0:
            continue

        # 같은 픽셀에서 LiDAR와 가장 가까운 포인트의 depth
        px, py = pts2d[i]
        # 픽셀 → 카메라 ray
        ray = np.linalg.inv(K) @ np.array([px, py, 1.0])
        ray /= np.linalg.norm(ray)

        # KD-tree로 ray 방향 근처 LiDAR 포인트 탐색
        [k, idx, _] = tree.search_knn_vector_3d(R @ (ray * sfm_depth) + t.ravel(), 5)
        if k == 0:
            continue

        lidar_pt = lidar_points[idx[0]]
        lidar_depth = (R @ lidar_pt + t.ravel())[2]
        if lidar_depth <= 0:
            continue

        scales.append(lidar_depth / sfm_depth)

    if not scales:
        raise ValueError("스케일 추정 실패: 유효한 샘플 없음")

    # 중앙값으로 outlier에 강인하게 추정
    scale = float(np.median(scales))
    print(f"추정 스케일: {scale:.4f} (샘플 {len(scales)}개)")
    return scale
```

## 방법 2: 3D-3D 매칭과 Umeyama 알고리즘 (더 정확)

위 방법 1은 Ray-casting으로 간단히 스케일을 구하지만, 이상적인 방법은 **SfM 3D 포인트와 이에 대응하는 LiDAR 3D 포인트 쌍**을 만든 후 **Similarity Transformation (Scale, Rotation, Translation)**을 한 번에 추정하는 것입니다.

> **주의:** Open3D의 기본 `registration_icp` 함수는 Rigid Transformation(회전, 이동)만 추정하며 Scale은 추정하지 못합니다. 스케일까지 복원하려면 **Umeyama 알고리즘**을 사용하여 두 3D 점군 사이의 최적의 스케일 $s$, 회전 $R$, 이동 $t$를 닫힌 형태(Closed-form)로 계산해야 합니다.

Umeyama 알고리즘은 두 점군 $\{x_i\}$ (SfM)와 $\{y_i\}$ (LiDAR) 사이의 다음 목적함수를 최소화합니다.

$$\min_{s, R, t} \frac{1}{n} \sum_{i=1}^{n} \| y_i - (s R x_i + t) \|^2$$

SVD를 이용한 닫힌 형태(Closed-form) 해가 존재합니다.

$$s = \frac{\text{tr}(D \Sigma)}{\sigma_x^2}, \quad R = U D V^T, \quad t = \mu_y - s R \mu_x$$

여기서 $\Sigma = \frac{1}{n} \sum (y_i - \mu_y)(x_i - \mu_x)^T$ 이고, $U \Sigma V^T = \text{SVD}(\Sigma)$, $D = \text{diag}(1, \ldots, 1, \det(UV^T))$ 입니다.

```python
def umeyama(src, dst):
    """
    src: (N, 3) SfM 3D 포인트
    dst: (N, 3) 대응하는 LiDAR 3D 포인트
    반환: s (float), R (3,3), t (3,)
    """
    n, m = src.shape
    mu_src = src.mean(axis=0)
    mu_dst = dst.mean(axis=0)

    src_centered = src - mu_src
    dst_centered = dst - mu_dst

    sigma_src = (src_centered ** 2).sum() / n  # 분산

    cov = (dst_centered.T @ src_centered) / n  # (3, 3) 공분산

    U, D, Vt = np.linalg.svd(cov)

    # 반사(reflection) 방지
    sign = np.eye(m)
    if np.linalg.det(U) * np.linalg.det(Vt) < 0:
        sign[m - 1, m - 1] = -1

    R = U @ sign @ Vt
    s = np.trace(np.diag(D) @ sign) / sigma_src
    t = mu_dst - s * R @ mu_src

    return s, R, t


def find_correspondences_for_umeyama(pts3d_sfm, lidar_points, max_dist=0.5):
    """KD-tree로 SfM 포인트마다 가장 가까운 LiDAR 포인트를 찾아 대응 쌍 구성"""
    import open3d as o3d

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(lidar_points)
    tree = o3d.geometry.KDTreeFlann(pcd)

    src, dst = [], []
    for pt in pts3d_sfm:
        [k, idx, dist] = tree.search_knn_vector_3d(pt, 1)
        if dist[0] ** 0.5 < max_dist:
            src.append(pt)
            dst.append(lidar_points[idx[0]])

    print(f"대응 쌍: {len(src)}개")
    return np.array(src), np.array(dst)


# 사용 예시
# 방법 1로 대략적인 스케일을 먼저 적용한 후 Umeyama로 정밀 보정
# pts0_1, inlier_mask는 3편 recover_pose()의 결과값입니다
rough_scale = estimate_scale_from_depth(pts3d_init, pts0_1[inlier_mask], lidar_points, K, R1, t1)
pts3d_rough = pts3d_init * rough_scale

src_pts, dst_pts = find_correspondences_for_umeyama(pts3d_rough, lidar_points)
s, R_align, t_align = umeyama(src_pts, dst_pts)

# SfM 포인트클라우드에 Similarity Transformation 적용
pts3d_aligned = (s * (R_align @ pts3d_rough.T)).T + t_align
print(f"Umeyama 추가 스케일: {s:.4f}")
```

## 스케일 적용

```python
# 방법 1로 스케일 추정
scale = estimate_scale_from_depth(pts3d_init, pts0_1[inlier_mask], lidar_points, K, R1, t1)

# 복원된 translation에 스케일 적용
t2_scaled = t2 * scale

# 3D 포인트에 스케일 적용
pts3d_scaled = pts3d_init * scale

print(f"t2 크기 (스케일 적용 전): {np.linalg.norm(t2):.4f}")
print(f"t2 크기 (스케일 적용 후): {np.linalg.norm(t2_scaled):.4f}m")
```

출력 예시:
```
추정 스케일: 3.2471 (샘플 187개)
t2 크기 (스케일 적용 전): 1.0000
t2 크기 (스케일 적용 후): 3.2471m
```

---

## 다음 편 예고

스케일이 복원된 상태에서 세 번째 이미지의 카메라 pose를 `cv2.solvePnP`로 추정하고, 새 3D 포인트를 추가합니다.
