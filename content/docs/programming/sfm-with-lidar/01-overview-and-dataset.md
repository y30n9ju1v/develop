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

> **왜 스테레오인데 스케일을 모를까?**
>
> 두 카메라의 baseline(간격)이 정확히 알려진 **calibrated stereo**라면 절대 스케일 복원이 가능합니다. 하지만 일반적인 SfM처럼 임의의 두 사진에서 출발할 경우, Essential Matrix를 분해해서 얻는 translation `t`는 **방향만** 복원되고 크기는 1로 normalize됩니다. 수학적으로 `t`와 `λt` (λ > 0인 임의의 상수)는 동일한 Essential Matrix를 만들기 때문에 스케일을 구분할 방법이 없습니다. 이 시리즈에서는 baseline을 모르는 일반적인 케이스를 다루며, LiDAR depth가 그 절대 스케일을 제공하는 역할을 합니다.

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

> **참고**: 이 파이프라인은 **개념 이해에 최적화된 단순화된 버전**입니다. Essential Matrix로 R,t를 복원한 뒤 LiDAR로 스케일을 보정하는 방식인데, 실제 카메라+LiDAR 시스템에서는 LiDAR depth로 3D 포인트를 직접 생성하거나 Bundle Adjustment에 LiDAR를 constraint로 통합하는 방식이 더 일반적입니다. 이 시리즈의 목표는 SfM의 핵심 개념(Essential Matrix, triangulation, PnP)을 단계별로 이해하는 것입니다.

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

```python
from google.colab import drive
drive.mount('/content/drive')

import os

target = '/content/drive/MyDrive/dataset/ETH3D/data'
os.makedirs(target, exist_ok=True)

# 압축 해제 수행
!7z x "/content/drive/MyDrive/dataset/ETH3D/pipes_dslr_scan_eval.7z" -o"{target}" -y
!7z x "/content/drive/MyDrive/dataset/ETH3D/pipes_dslr_undistorted.7z" -o"{target}" -y
```

압축을 해제하면 다음 구조가 됩니다.

```
/content/drive/MyDrive/dataset/ETH3D/data/pipes
├── dslr_calibration_undistorted
│   ├── cameras.txt
│   ├── images.txt
│   └── points3D.txt
├── dslr_scan_eval
│   ├── scan1.ply
│   └── scan_alignment.mlp
└── images
    └── dslr_images_undistorted
        ├── DSC_0634.JPG
        ├── DSC_0635.JPG
        ├── DSC_0636.JPG
        ├── DSC_0637.JPG
        ├── DSC_0638.JPG
        ├── DSC_0639.JPG
        ├── DSC_0640.JPG
        ├── DSC_0641.JPG
        ├── DSC_0642.JPG
        ├── DSC_0643.JPG
        ├── DSC_0644.JPG
        ├── DSC_0645.JPG
        ├── DSC_0646.JPG
        └── DSC_0647.JPG
```

> **왜 이미지는 14장인데 LiDAR는 1개일까?**
>
> ETH3D는 카메라와 LiDAR가 동기화되어 함께 움직이는 자율주행 구조가 아닙니다. 카메라는 여러 위치에서 14장을 촬영했고, LiDAR는 지상 레이저 스캐너로 장면 전체를 한 번 스캔한 결과가 `scan_clean.ply` 1개입니다. 즉, LiDAR 포인트클라우드는 장면의 GT(Ground Truth) 역할을 합니다.
>
> 이 시리즈에서는 `scan_clean.ply`를 각 카메라 pose로 투영해 **카메라별 depth map을 합성**해서 사용합니다.
>
> ```
> scan_clean.ply (전체 포인트클라우드)
>     → 카메라 1 pose로 투영 → depth map 1
>     → 카메라 2 pose로 투영 → depth map 2
>     → ...
> ```

### 카메라 파라미터 형식

`cameras.txt`는 COLMAP 포맷으로 저장되어 있습니다.

```
# Camera list with one line of data per camera:
#   CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]
# Number of cameras: 1
0 PINHOLE 6220 4141 3430.27 3429.23 3119.2 2057.75
```

파라미터 의미:
- `6220 4141` — 가로, 세로 해상도
- `3430.27 3429.23` — 초점거리 fx, fy (픽셀 단위)
- `3119.2 2057.75` — 주점 cx, cy (이미지 중심)

> **참고: 카메라 모델(PINHOLE vs RADIAL)**
>
> COLMAP은 `PINHOLE` 외에도 `RADIAL`, `OPENCV` 등 다양한 카메라 모델을 지원합니다. `PINHOLE`은 렌즈 왜곡을 전혀 고려하지 않는 가장 단순한 모델로, 이미지가 이미 undistorted(왜곡 보정됨) 상태이거나 왜곡이 매우 작을 때 사용됩니다. 
> 본 튜토리얼의 데이터(`pipes_dslr_undistorted`)는 이름에서도 알 수 있듯이 왜곡이 보정된 이미지이므로 `PINHOLE` 모델을 사용합니다.

`images.txt`에는 각 이미지의 카메라 pose가 quaternion + translation 형태로 저장되어 있습니다.

```
# Image list with two lines of data per image:
#   IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME
#   POINTS2D[] as (X, Y, POINT3D_ID)
# Number of images: 14, mean observations per image: 557.643
14 0.554619 0.524856 -0.452905 0.460219 -0.173888 0.236895 1.27596 0 dslr_images_undistorted/DSC_0647.JPG
1234.5 567.8 42   892.3 234.1 -1   ...
```

각 이미지는 두 줄로 구성됩니다. 첫 번째 줄은 pose, 두 번째 줄은 `POINTS2D`로 `(X, Y, POINT3D_ID)` 세트가 반복됩니다. `X, Y`는 픽셀 좌표이고 `POINT3D_ID`는 `points3D.txt`의 대응 3D 포인트 ID입니다. `-1`은 아직 3D 포인트와 매칭되지 않은 픽셀을 의미합니다. 이 시리즈에서는 SIFT로 직접 feature를 추출하므로 `POINTS2D`는 사용하지 않습니다.

> **쿼터니언(Quaternion)이란?**
>
> 3D 회전을 표현하는 방법 중 하나입니다. 4개 숫자 `(w, x, y, z)`로 구성됩니다.
>
> | 표현 방식 | 숫자 개수 | 문제점 |
> |---|---|---|
> | 오일러 각 (roll, pitch, yaw) | 3개 | 짐벌락(gimbal lock) 발생 가능 |
> | 회전 행렬 | 9개 | 중복이 많고 누적 오차 생김 |
> | 쿼터니언 | 4개 | 짐벌락 없음, 수치적으로 안정적 |
>
> 직관적으로는 "어떤 축을 중심으로 얼마나 돌렸다"를 4개 숫자로 인코딩한 것입니다. `w`는 회전량(스칼라), `x y z`는 회전축 방향(벡터)입니다.
>
> ```
> # 예: Y축 중심으로 90도 회전
> w = cos(45°) ≈ 0.707,  x = 0,  y = sin(45°) ≈ 0.707,  z = 0
> ```
>
> 코드에서는 `scipy.spatial.transform.Rotation`으로 쉽게 회전 행렬로 변환해서 사용합니다.

---

## 환경 설정

```bash
pip install opencv-python numpy open3d scipy
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

def load_images(base_dir, names):
    images = {}
    for name in names:
        path = f"{base_dir}/{name}"
        img = cv2.imread(path)
        images[name] = img

    return images

def load_lidar_gt(ply_path):
    import open3d as o3d
    pcd = o3d.io.read_point_cloud(ply_path)
    points = np.asarray(pcd.points)
    return points
```

### 전체 로딩 확인

```python
import os

DATA_DIR = "/content/drive/MyDrive/dataset/ETH3D/data/pipes"

cameras = load_cameras(os.path.join(DATA_DIR, "dslr_calibration_undistorted/cameras.txt"))
poses   = load_images_poses(os.path.join(DATA_DIR, "dslr_calibration_undistorted/images.txt"))
lidar   = load_lidar_gt(os.path.join(DATA_DIR, "dslr_scan_eval/scan1.ply"))

img_names = sorted(poses.keys())[:3]
images = load_images(DATA_DIR, img_names)

K = cameras[0]
print(f"Intrinsic matrix:\n{K}")
print(f"사용할 이미지: {list(images.keys())}")
print(f"로드된 이미지 수: {len(images)}")
print(f"LiDAR 포인트 수: {len(lidar):,}")
```

출력 예시:

```
Intrinsic matrix:
[[3.43027e+03 0.00000e+00 3.11920e+03]
 [0.00000e+00 3.42923e+03 2.05775e+03]
 [0.00000e+00 0.00000e+00 1.00000e+00]]
사용할 이미지: ['dslr_images_undistorted/DSC_0634.JPG', 'dslr_images_undistorted/DSC_0635.JPG', 'dslr_images_undistorted/DSC_0636.JPG']
로드된 이미지 수: 3
LiDAR 포인트 수: 11,482,717
```

---

## 다음 편 예고

데이터 로딩이 완료되었으니, 다음 편에서는 세 장의 이미지에서 SIFT로 feature를 추출하고 BFMatcher + RANSAC으로 프레임 간 대응점을 찾습니다.
