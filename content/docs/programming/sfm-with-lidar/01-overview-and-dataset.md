---
title: "1편: 개요 및 데이터 준비"
date: 2026-05-15T00:00:00+09:00
draft: false
tags: ["SfM", "LiDAR", "OpenCV", "Python", "ETH3D"]
categories: ["Programming"]
description: "3-View SfM 파이프라인 전체 흐름을 이해하고, ETH3D 데이터셋을 다운로드하여 Python으로 로딩하는 방법을 정리합니다."
---

> 이 시리즈는 Python과 OpenCV를 이용해 카메라 + LiDAR 데이터로 3-View SfM을 직접 구현합니다. 선형대수 기초와 Python/OpenCV 기본 사용 경험이 있다고 가정합니다.

## SfM이란

SfM(Structure from Motion)은 여러 장의 2D 이미지로부터 카메라의 움직임(Motion)과 3D 구조(Structure)를 동시에 복원하는 기법입니다. 3DGS는 SfM의 출력인 카메라 pose와 sparse 포인트클라우드를 초기값으로 사용하기 때문에, SfM을 이해하는 것이 3DGS를 깊게 이해하기 위한 첫 단계입니다.

입력과 출력을 간단히 정리하면:

```
입력: N장의 이미지 (+ 선택적으로 LiDAR depth)
출력: - 각 카메라의 pose (R, t)
      - 3D 포인트클라우드
```

## 왜 3-View인가

2-View SfM은 두 카메라 사이의 상대적인 pose는 복원할 수 있지만 **절대 스케일**을 알 수 없습니다. 카메라만으로는 장면이 1m짜리인지 100m짜리인지 구분하지 못합니다.

3-View로 확장하면:
- 더 많은 3D 포인트를 안정적으로 복원할 수 있고
- LiDAR depth를 활용해 절대 스케일을 복원할 수 있으며
- N-View SfM으로 확장하는 기본 구조를 이해할 수 있습니다

## 파이프라인 전체 흐름

```
[1] 데이터 로딩
     이미지, 카메라 intrinsic, LiDAR depth map
        ↓
[2] Feature 추출 및 매칭 (SIFT + BFMatcher + RANSAC)
     프레임 간 대응점 (pixel ↔ pixel)
        ↓
[3] 2-View Geometry (Essential Matrix)
     카메라 1, 2의 상대 pose (R, t) + 초기 3D 포인트
        ↓
[4] LiDAR Scale 복원
     depth map으로 절대 스케일 보정
        ↓
[5] 3번째 뷰 등록 (PnP)
     카메라 3의 pose + 추가 3D 포인트
        ↓
[6] 시각화 및 검증 (Rerun SDK)
     카메라 pose + 포인트클라우드 vs LiDAR GT 비교
```

## 데이터셋: ETH3D Pipes 씬

이 시리즈에서는 [ETH3D](https://www.eth3d.net/datasets) high-res multi-view 데이터셋의 **Pipes 씬**을 사용합니다.

Pipes를 선택한 이유:
- 이미지 14장으로 시리즈 전체에서 가장 작은 씬
- 실내 환경이라 feature 매칭이 안정적
- 카메라 intrinsic, LiDAR GT 포인트클라우드 모두 제공
- SfM 결과를 GT와 정량적으로 비교 가능

### 데이터 다운로드

ETH3D 사이트에서 Pipes 씬의 두 가지 파일을 받습니다.

- **이미지 + 카메라 파라미터:** `pipes_dslr_undistorted.7z`
- **LiDAR GT 포인트클라우드:** `pipes_dslr_scan_eval.7z`

```bash
# 7z 압축 해제 (p7zip 필요)
# macOS: brew install p7zip
# Ubuntu: sudo apt install p7zip-full

7z x pipes_dslr_undistorted.7z -o./data/pipes
7z x pipes_dslr_scan_eval.7z   -o./data/pipes
```

압축을 해제하면 다음 구조가 됩니다.

```
data/pipes/
├── images/
│   ├── dslr_images_undistorted/
│   │   ├── DSC_0001.JPG
│   │   ├── DSC_0002.JPG
│   │   └── ...  (14장)
├── cameras.txt       # 카메라 intrinsic
├── images.txt        # 각 이미지의 pose (COLMAP 포맷)
├── points3D.txt      # COLMAP sparse 포인트 (참고용)
└── scan_clean.ply    # LiDAR GT 포인트클라우드
```

### 카메라 파라미터 형식

`cameras.txt`는 COLMAP 포맷으로 저장되어 있습니다.

```
# Camera list with one line of data per camera:
# CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]
1 PINHOLE 6048 4032 4618.9 4618.9 3024.0 2016.0
```

파라미터 의미:
- `4618.9 4618.9` — 초점거리 fx, fy (픽셀 단위)
- `3024.0 2016.0` — 주점 cx, cy (이미지 중심)

`images.txt`에는 각 이미지의 카메라 pose가 quaternion + translation 형태로 저장되어 있습니다.

```
# IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME
1 0.9998 0.0012 -0.0178 0.0063 -0.1234 0.0567 1.2345 1 DSC_0001.JPG
```

---

## 환경 설정

```bash
pip install opencv-python numpy open3d rerun-sdk matplotlib
```

## 데이터 로딩 코드

### cameras.txt 파싱

```python
import numpy as np

def load_cameras(cameras_txt):
    cameras = {}
    with open(cameras_txt) as f:
        for line in f:
            if line.startswith('#') or line.strip() == '':
                continue
            parts = line.split()
            cam_id = int(parts[0])
            # PINHOLE: fx fy cx cy
            fx, fy, cx, cy = map(float, parts[4:8])
            K = np.array([[fx, 0, cx],
                          [0, fy, cy],
                          [0,  0,  1]])
            cameras[cam_id] = K
    return cameras
```

### images.txt 파싱

```python
from scipy.spatial.transform import Rotation

def load_images_poses(images_txt):
    poses = {}
    with open(images_txt) as f:
        lines = [l for l in f if not l.startswith('#') and l.strip()]
    # images.txt는 두 줄씩: pose 라인 + 포인트 라인
    for i in range(0, len(lines), 2):
        parts = lines[i].split()
        img_id = int(parts[0])
        qw, qx, qy, qz = map(float, parts[1:5])
        tx, ty, tz = map(float, parts[5:8])
        name = parts[9]

        R = Rotation.from_quat([qx, qy, qz, qw]).as_matrix()
        t = np.array([tx, ty, tz])
        poses[name] = {'R': R, 't': t}
    return poses
```

### 이미지 및 LiDAR 로딩

```python
import cv2

def load_images(image_dir, names):
    images = {}
    for name in names:
        path = f"{image_dir}/{name}"
        img = cv2.imread(path)
        images[name] = img
    return images

def load_lidar_gt(ply_path):
    import open3d as o3d
    pcd = o3d.io.read_point_cloud(ply_path)
    points = np.asarray(pcd.points)  # (N, 3)
    return points
```

### 전체 로딩 확인

```python
import os

DATA_DIR = "./data/pipes"
IMAGE_DIR = os.path.join(DATA_DIR, "images/dslr_images_undistorted")

cameras = load_cameras(os.path.join(DATA_DIR, "cameras.txt"))
poses   = load_images_poses(os.path.join(DATA_DIR, "images.txt"))
lidar   = load_lidar_gt(os.path.join(DATA_DIR, "scan_clean.ply"))

# 14장 중 3장만 선택 (연속된 프레임)
img_names = sorted(poses.keys())[:3]
images = load_images(IMAGE_DIR, img_names)

K = cameras[1]
print(f"Intrinsic matrix:\n{K}")
print(f"사용할 이미지: {img_names}")
print(f"LiDAR 포인트 수: {len(lidar):,}")
```

출력 예시:

```
Intrinsic matrix:
[[4618.9    0.  3024. ]
 [   0.  4618.9 2016. ]
 [   0.     0.     1. ]]
사용할 이미지: ['DSC_0001.JPG', 'DSC_0002.JPG', 'DSC_0003.JPG']
LiDAR 포인트 수: 2,847,392
```

---

## 다음 편 예고

데이터 로딩이 완료되었으니, 다음 편에서는 세 장의 이미지에서 SIFT로 feature를 추출하고 BFMatcher + RANSAC으로 프레임 간 대응점을 찾습니다.
