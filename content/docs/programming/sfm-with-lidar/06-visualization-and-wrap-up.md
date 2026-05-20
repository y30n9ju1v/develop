---
title: "6편: 결과 시각화 및 정리"
date: 2026-05-15T05:00:00+09:00
draft: true
tags: ["SfM", "Rerun", "시각화", "LiDAR", "3DGS"]
categories: ["Programming"]
description: "Rerun SDK로 카메라 pose와 포인트클라우드를 시각화하고, LiDAR GT와 비교하며 시리즈를 마무리합니다."
---

> 복원된 카메라 pose 3개와 포인트클라우드를 Rerun SDK로 시각화하고, LiDAR GT와 나란히 비교합니다.

## Rerun SDK 소개

[Rerun](https://rerun.io)은 컴퓨터 비전과 로보틱스용 시각화 도구입니다. Open3D보다 설정이 간단하고, 이미지 + 3D 포인트 + 카메라 pose를 한 화면에서 동시에 볼 수 있습니다.

```bash
pip install rerun-sdk
```

## 초기화

```python
import rerun as rr
import numpy as np

rr.init("sfm_pipes", spawn=False)
rr.notebook_show()
```

`rr.notebook_show()`는 Colab 셀 안에 Rerun viewer를 인라인으로 임베드합니다. 이후 `rr.log()`로 데이터를 로깅하면 viewer가 실시간으로 업데이트됩니다.

> **참고**: 로컬 환경에서는 `spawn=True`로 바꾸면 별도 Rerun viewer 앱이 자동으로 실행됩니다.

## 포인트클라우드 로깅

```python
def log_pointcloud(name, points, colors=None, radii=0.01):
    rr.log(name, rr.Points3D(
        positions=points,
        colors=colors,
        radii=radii
    ))

# SfM 결과 포인트클라우드
log_pointcloud("world/sfm_points", all_pts3d,
               colors=np.full((len(all_pts3d), 3), [100, 180, 255], dtype=np.uint8))

# LiDAR GT 포인트클라우드 (서브샘플링)
lidar_sub = lidar_points[::10]  # 10배 다운샘플
log_pointcloud("world/lidar_gt", lidar_sub,
               colors=np.full((len(lidar_sub), 3), [255, 200, 100], dtype=np.uint8),
               radii=0.005)
```

## 카메라 Pose 로깅

Rerun에서 카메라는 세 가지를 한 entity에 함께 로깅합니다:
1. `Transform3D` — 카메라의 위치와 방향
2. `Pinhole` — intrinsic (렌즈 모델)
3. `Image` — 실제 이미지 (선택)

ETH3D는 COLMAP 컨벤션을 따르므로 카메라 pose가 world → camera 변환으로 저장되어 있습니다. Rerun은 camera → world 변환을 기대하므로 역변환이 필요합니다.

```python
import cv2
from scipy.spatial.transform import Rotation

def log_camera(entity, R_cw, t_cw, K, image, width, height, frame_idx):
    """
    R_cw, t_cw: world → camera 변환 (COLMAP 컨벤션)
    """
    rr.set_time("frame", sequence=frame_idx)

    # camera → world 변환으로 역변환
    R_wc = R_cw.T
    t_wc = -R_cw.T @ t_cw.ravel()

    # quaternion 변환 (scipy: xyzw 순서, Rerun도 xyzw)
    quat_xyzw = Rotation.from_matrix(R_wc).as_quat()

    rr.log(entity, rr.Transform3D(
        translation=t_wc,
        quaternion=rr.RotationQuat(xyzw=quat_xyzw)
    ))
    rr.log(entity, rr.Pinhole(
        image_from_camera=K,
        width=width,
        height=height
    ))
    rr.log(f"{entity}/image", rr.Image(
        cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    ))
```

## 세 카메라 모두 로깅

```python
H, W = list(images.values())[0].shape[:2]

camera_data = [
    ("world/camera_0", R1, t1, images[name0], 0),
    ("world/camera_1", R2, t2_scaled, images[name1], 1),
    ("world/camera_2", R3, t3, images[name2], 2),
]

for entity, R, t, img, idx in camera_data:
    log_camera(entity, R, t, K, img, W, H, idx)
```

## LiDAR GT와 비교

```python
# 시각적 비교를 위해 SfM과 GT를 함께 로깅
rr.set_time("frame", sequence=0)

# Rerun viewer에서 world/sfm_points (파란색) vs world/lidar_gt (노란색) 비교
print("Rerun viewer에서 world/ 아래 두 포인트클라우드를 비교하세요.")
```

정량적 비교는 SfM 포인트와 LiDAR 포인트 사이의 평균 거리로 측정합니다.

```python
def evaluate_reconstruction(sfm_pts, lidar_pts, threshold=0.05):
    import open3d as o3d

    sfm_pcd = o3d.geometry.PointCloud()
    sfm_pcd.points = o3d.utility.Vector3dVector(sfm_pts)

    lidar_pcd = o3d.geometry.PointCloud()
    lidar_pcd.points = o3d.utility.Vector3dVector(lidar_pts)

    dists = np.asarray(sfm_pcd.compute_point_cloud_distance(lidar_pcd))
    print(f"평균 오차: {dists.mean():.4f}m")
    print(f"중앙값 오차: {np.median(dists):.4f}m")
    print(f"5cm 이내 비율: {(dists < threshold).mean() * 100:.1f}%")

evaluate_reconstruction(all_pts3d, lidar_points)
```

---

## 시리즈 결과 정리

이 시리즈에서 구현한 내용:

| 단계 | 구현 내용 | 핵심 함수 |
|------|-----------|-----------|
| 데이터 로딩 | ETH3D COLMAP 포맷 파싱 | `load_cameras`, `load_images_poses` |
| Feature 추출/매칭 | SIFT + BFMatcher + RANSAC | `cv2.SIFT_create`, `findFundamentalMat` |
| 2-View Geometry | Essential Matrix → R, t | `cv2.findEssentialMat`, `recoverPose` |
| 삼각측량 | 초기 3D 포인트 생성 | `cv2.triangulatePoints` |
| Scale 복원 | LiDAR depth 비율 | 직접 구현 |
| PnP | 3번째 카메라 등록 | `cv2.solvePnPRansac` |
| 시각화 | 카메라 + 포인트클라우드 | `rerun-sdk` |

## 3-View SfM의 한계

- **Bundle Adjustment 없음:** 카메라 pose와 3D 포인트를 동시에 최적화하지 않아 오차가 누적됩니다. `g2o`나 `scipy.optimize`로 추가할 수 있습니다.
- **3장 제한:** N장으로 확장하려면 루프 클로저와 incremental mapping이 필요합니다.
- **Scale 추정 불안정:** LiDAR 포인트가 sparse하거나 카메라-LiDAR가 직접 캘리브레이션되지 않았다면 오차가 커집니다.

## SfM과 3DGS의 연결

이 시리즈에서 직접 구현한 각 단계가 3DGS에서 어떤 의미를 갖는지 정리합니다.

| SfM 결과 | 3DGS에서의 역할 |
|----------|----------------|
| 카메라 pose (R, t) | 각 학습 이미지의 시점 정보 — 렌더링 시 카메라 위치로 사용 |
| 카메라 intrinsic K | 투영 변환의 기반 — Gaussian을 이미지 평면에 splatting할 때 사용 |
| Sparse 포인트클라우드 | 3D Gaussian의 초기 위치 — 여기서 Gaussian이 grow/prune됨 |
| 절대 스케일 (LiDAR) | Gaussian의 크기와 밀도 초기화에 영향 |

SfM이 "어디서 찍었는가"와 "공간이 어떻게 생겼는가"를 알아내는 과정이라면, 3DGS는 그 위에서 "각 위치에서 보면 어떻게 보이는가"를 Gaussian으로 표현하고 최적화하는 과정입니다. SfM 없이는 3DGS의 초기화 자체가 불가능하고, SfM의 품질이 3DGS 결과에 직접 영향을 줍니다.
