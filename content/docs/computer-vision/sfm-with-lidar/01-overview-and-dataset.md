---
title: "1편: 개요 및 데이터 준비"
date: 2026-05-15T00:00:00+09:00
draft: false
tags: ["SfM", "LiDAR", "OpenCV", "Python", "ETH3D"]
categories: ["programming"]
description: "3-View SfM 파이프라인 전체 흐름을 이해하고, ETH3D 데이터셋을 다운로드하여 Python으로 로딩하는 방법을 정리합니다."
---

> **시리즈 시작에 앞서 💡**
> 이 시리즈는 Python과 OpenCV를 이용해 카메라 이미지와 LiDAR 데이터를 결합한 **3-View SfM(Structure from Motion)**을 직접 구현합니다. 
> 수학과 선형대수학 용어가 중간중간 등장하지만, 최대한 일상적인 비유를 들어 직관적으로 설명해 나가므로 두려워하실 필요가 전혀 없습니다! 
> 기본 파이썬 코딩 및 OpenCV 기초 사용 경험만 있다면 누구나 멋진 3차원 공간 복원을 완성할 수 있습니다.

---

## 1. SfM이란? 2D 사진을 3D 입체 세계로

**SfM(Structure from Motion)**은 여러 시점에서 촬영한 2D 이미지들을 컴퓨터로 비교 분석하여, 카메라가 움직인 궤적(**Motion, 회전 $R$과 이동 $t$**)과 촬영된 장면의 3D 입체 구조(**Structure, 3D 점 구름**)를 가상 세계 속에 동시에 만들어내는 놀라운 기법입니다.

요즈음 가상현실과 메타버스 기술로 각광받는 **3D Gaussian Splatting(3DGS)**이나 **NeRF** 역시, 이 SfM의 결과물(카메라 위치 및 대략적인 3D 모양)을 디딤돌 삼아 학습을 시작합니다. 즉, SfM을 이해하는 것은 3D 복원 분야의 핵심 첫 단추를 채우는 것과 같습니다.

```
 [입력] 여러 장의 2D 평면 사진  ───SfM 엔진 작동───► [출력] 카메라 촬영 위치(Pose) 
                                                      + 3차원 입체 점 구름(PointCloud)
```

---

## 2. 왜 하필 '3-View'이며, 'LiDAR'가 필요한가?

사진을 두 장만 쓰는 **2-View SfM**은 훌륭하지만 수학적으로 큰 한계가 있습니다. 바로 **절대 스케일(Absolute Scale)**을 알 수 없다는 점입니다.

> [!NOTE]  
> **스케일 모호성(Scale Ambiguity)의 직관적 비유**
> 
> 한쪽 눈을 감고, 책상 위에 놓인 **10cm짜리 장난감 미니어처 성**을 아주 가까이서 찍은 사진이 있습니다. 
> 그리고 유럽 여행을 가서 **100m짜리 진짜 거대한 고성**을 멀리서 찍은 사진이 있습니다. 
> 
> 이 두 장의 2D 사진만 컴퓨터에 툭 던져주면, 컴퓨터는 이것이 10cm짜리 장난감인지, 100m짜리 진짜 성인지 구별할 수 없습니다. 
> 왜냐하면 두 카메라 사이의 실제 이동 거리 비율이 수학적으로 완전히 정규화(1로 고정)되어 대수적으로 구분되지 않기 때문입니다. 이 문제를 **스케일 모호성**이라고 합니다.

이 시리즈에서는 이 절대 스케일을 찾기 위해 **LiDAR(라이다) Depth 데이터**를 투입합니다. 
1. **3-View(세 장의 이미지)**를 이용해 충분하고 안정적인 기하학적 3D 뼈대를 만들고,
2. **LiDAR**의 정확한 1:1 절대적 거리 값을 결합해 장난감 크기의 가상 3D 공간을 **진짜 미터(m) 단위의 실제 스케일**로 완벽하게 보정합니다.

---

## 3. 파이프라인 전체 흐름

우리가 함께 만들 SfM 엔진은 다음과 같이 유기적인 흐름을 밟아 완성됩니다.

```
┌──────────────────────────────────────────────────────────────┐
│ [1] 데이터 로딩 (1편)                                         │
│     - 이미지, 카메라 고유의 돋보기 효과(Intrinsic), LiDAR 데이터  │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ [2] 특징점 추출 및 매칭 (2편)                                 │
│     - SIFT로 각 프레임에서 점을 찾고 RANSAC으로 아웃라이어 정제   │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ [3] 2-View 기하학 & 초기 3D 복원 (3편)                          │
│     - 에센셜 행렬(E) 복원 -> 카메라 1, 2의 상대적 Pose + 삼각측량 │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ [4] LiDAR 스케일 절대 복원 (4편)                               │
│     - 잃어버린 스케일 인자(s)를 LiDAR depth 정보로 정밀 보정     │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ [5] 3번째 카메라 등록 (5편)                                    │
│     - PnP 알고리즘을 이용해 카메라 3의 Pose와 추가 3D 점 융합   │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ [6] 3D 시각화 및 검증 (6편)                                    │
│     - Rerun SDK를 통해 실시간으로 3D 맵과 카메라 궤적 확인        │
└──────────────────────────────────────────────────────────────┘
```

> [!NOTE]  
> **참고사항 (튜토리얼 최적화 구조)**
> 본 시리즈는 SfM의 뼈대 개념(에센셜 행렬, 삼각측량, PnP)을 단계별로 파악하도록 단순화한 버전입니다. 실제 상용 제품이나 정밀 로보틱스 시스템에서는 처음부터 카메라와 LiDAR를 물리적으로 정밀 캘리브레이션하여 번들 조정(Bundle Adjustment) 연산에 LiDAR 제약 조건을 함께 최적화하는 방식을 널리 사용합니다.

---

## 4. 데이터셋 준비: ETH3D Pipes (파이프 씬)

실습에는 세계적으로 정밀함이 공인된 벤치마크 데이터셋인 **ETH3D Pipes** 씬을 활용합니다.

* **이미지 14장:** 실내 환경 파이프 씬으로, 특징점 매칭이 선명하게 잘 일어나며 실습 연산량이 매우 가볍습니다.
* **LiDAR 포인트클라우드:** 실제 고정식 지상 레이저 3D 스캐너로 수천만 개의 점을 정밀 측량한 고정밀 GT(Ground Truth) 정보입니다.

> [!TIP]  
> **왜 카메라는 14장인데 LiDAR 스캔 데이터는 단 1개일까요?**
> 
> 카메라와 LiDAR가 차량에 탑재되어 한 몸으로 움직이는 실시간 주행 자율주행 데이터셋(예: KITTI)이 아니기 때문입니다. 
> 이 데이터셋은 방 한가운데에 고성능 3D 스캐너를 세워두고 공간 전체를 정밀하게 한 번 스캔해 둔 PLY 파일(`scan1.ply`)이 1개 있고, 
> 사람은 카메라를 들고 방 안을 돌아다니며 사진 14장을 촬영한 구조입니다. 
> 
> 따라서 우리는 이 전체 3D 스캔 데이터(`scan1.ply`)를 카메라 촬영 위치 좌표로 거꾸로 역투영하여, 각 사진별 **가상 LiDAR Depth Map**을 조립해 사용할 것입니다.

### 4.1 데이터 다운로드 및 Google Drive 압축 해제

Google Colab 환경이나 로컬 환경에서 아래 코드를 실행해 데이터를 손쉽게 내려받고 압축을 풉니다.

```python
from google.colab import drive
drive.mount('/content/drive')

import os

# 데이터가 저장될 대상 경로
target = '/content/drive/MyDrive/dataset/ETH3D/data'
os.makedirs(target, exist_ok=True)

# 다운로드받은 7z 압축 파일 압축 해제
!7z x "/content/drive/MyDrive/dataset/ETH3D/pipes_dslr_scan_eval.7z" -o"{target}" -y
!7z x "/content/drive/MyDrive/dataset/ETH3D/pipes_dslr_undistorted.7z" -o"{target}" -y
```

압축이 풀리면 다음과 같은 폴더 트리가 멋지게 구성됩니다.

```
/content/drive/MyDrive/dataset/ETH3D/data/pipes
├── dslr_calibration_undistorted
│   ├── cameras.txt         # 카메라 돋보기 효과(K) 스펙 데이터
│   ├── images.txt          # 실제 카메라 촬영 위치(Quaternion, Translation) 정답지
│   └── points3D.txt        # 미리 복원된 3D 점 구름
├── dslr_scan_eval
│   ├── scan1.ply           # 수천만 개로 구성된 진짜 LiDAR GT 점 구름
│   └── scan_alignment.mlp
└── images
    └── dslr_images_undistorted
        ├── DSC_0634.JPG     # 실습에 쓸 2D 이미지 데이터
        ├── DSC_0635.JPG
        └── ... (총 14장)
```

---

## 5. COLMAP 데이터 포맷 이해하기 (초보자용 해설)

COLMAP 포맷으로 된 텍스트 파일들은 처음에 열어보면 복잡한 숫자만 가득하여 매우 혼란스럽습니다. 하나씩 명쾌하게 쪼개서 정리해 드립니다.

### 5.1 `cameras.txt` (카메라의 물리적 스펙 행렬)
이 파일은 카메라 렌즈와 센서가 빛을 어떻게 픽셀로 변환하는지 기록해 둡니다.

```
#   CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]
0 PINHOLE 6220 4141 3430.27 3429.23 3119.2 2057.75
```

* **`0`**: 카메라 고유 번호 (ID)
* **`PINHOLE`**: 렌즈 왜곡이 이미 보정된 정밀한 핀홀 렌즈 모델
* **`6220 4141`**: 이미지 해상도 (가로 6220 픽셀, 세로 4141 픽셀)
* **`3430.27 3429.23`**: 렌즈 초점거리 ($f_x, f_y$). 렌즈가 빛을 꺾는 돋보기 배율을 픽셀 두께 단위로 계산한 값입니다.
* **`3119.2 2057.75`**: 센서 정중앙 주점 ($c_x, c_y$). 렌즈의 한가운데 광학적 중심이 이미지의 몇 번째 픽셀에 떨어지는지 나타냅니다. (보통 해상도의 딱 절반 지점 부근입니다)

이 값들을 이용해 우리는 3D 공간 연산의 꽃인 **카메라 내부 파라미터 행렬(Intrinsic Matrix, $K$)**을 조립합니다.

$$K = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}$$

---

### 5.2 `images.txt` (카메라의 자세와 3차원 위치 정답지)
이 파일에는 각 이미지가 우주 공간의 어느 좌표에서 찍혔는지($R, t$) 정보가 저장되어 있습니다.

```
#   IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME
14 0.554619 0.524856 -0.452905 0.460219 -0.173888 0.236895 1.27596 0 dslr_images_undistorted/DSC_0647.JPG
```

* **`14`**: 이미지의 고유 번호 (ID)
* **`0.554619 0.524856 -0.452905 0.460219`**: 카메라의 회전 상태를 나타내는 **쿼터니언(Quaternion)** 값 `[qw, qx, qy, qz]` 입니다.
* **`-0.173888 0.236895 1.27596`**: 카메라의 이동 거리 번역 벡터 `[tx, ty, tz]` 입니다.
* **`0`**: 이 사진을 촬영한 `cameras.txt` 상의 카메라 모델 번호
* **`dslr_images_undistorted/DSC_0647.JPG`**: 실제 사진 파일의 상대 경로

> [!TIP]  
> **쿼터니언(Quaternion)이란?**
> 
> 3차원 회전을 다룰 때 오일러 각(Roll, Pitch, Yaw)을 사용하면 컴퓨터 연산 도중 축이 겹쳐 회전 각도를 잃어버리는 **짐벌락(Gimbal Lock)** 현상이 생기게 됩니다. 
> 쿼터니언은 4개의 숫자 `(w, x, y, z)`를 하나의 수치로 묶어서, 꼬임 현상 없이 모든 3D 회전을 수학적으로 매우 안정적이고 완벽하게 표현하는 4차원 복소수 도구입니다. 
> 복잡한 계산은 SciPy 등 훌륭한 파이썬 라이브러리가 대신 처리해 주니 우리는 직관적 개념만 알고 넘어가면 충분합니다!

---

## 6. 개발 환경 설정

터미널을 열고 3D 및 공간 기하 연산에 특화된 필수 라이브러리를 설치합니다.

```bash
pip install opencv-python numpy open3d scipy
```

* **`open3d`**: LiDAR GT 스캔 데이터(`scan1.ply`)와 3D 포인트클라우드를 컴퓨터 공간에 시각화하고 정밀 연산하는 필수 3차원 데이터 라이브러리입니다.
* **`scipy`**: 쿼터니언 자세 값을 부드러운 $3 \times 3$ 회전 행렬로 1초 만에 조립 변환해 주는 강력한 파이썬 수학 패키지입니다.

---

## 7. 데이터 파싱 및 로딩 파이썬 코드 구현

이제 배운 COLMAP 규칙에 따라, 원시 텍스트 파일들을 읽어 깔끔한 NumPy 배열과 3D 데이터 구조로 가공하는 코드를 구현해 보겠습니다.

### 7.1 카메라 Intrinsic 파싱 코드

```python
import numpy as np

def load_cameras(cameras_txt):
    """
    cameras.txt 파일을 읽어 카메라 고유의 내부 파라미터 행렬 K를 조립합니다.
    """
    cameras = {}

    with open(cameras_txt) as f:
        for line in f:
            # 주석 및 빈 줄 스킵
            if line.startswith('#') or line.strip() == '':
                continue
            
            parts = line.split()
            cam_id = int(parts[0])
            
            # 파라미터 리스트에서 fx, fy, cx, cy 추출
            fx, fy, cx, cy = map(float, parts[4:8])
            
            # 3x3 Intrinsic Matrix K 구성
            K = np.array([[fx, 0,  cx],
                          [0,  fy, cy],
                          [0,  0,  1]])
            
            cameras[cam_id] = K
            
    return cameras
```

### 7.2 이미지 Pose (회전 R, 이동 t) 파싱 코드

```python
from scipy.spatial.transform import Rotation

def load_images_poses(images_txt):
    """
    images.txt 파일을 읽어 쿼터니언 회전 정보와 이동 벡터를 R, t 형태로 복원합니다.
    """
    poses = {}

    with open(images_txt) as f:
        # 빈 줄과 주석 제외하고 텍스트 라인 획득
        lines = [l for l in f if not l.startswith('#') and l.strip()]
        
    # COLMAP images.txt는 이미지당 2줄씩 정보가 할당되어 있습니다.
    # 첫째 줄은 pose 정보가 담겨 있고, 둘째 줄은 픽셀 정보이므로 2칸씩 스킵하며 파싱합니다.
    for i in range(0, len(lines), 2):
        parts = lines[i].split()
        img_id = int(parts[0])
        
        # 쿼터니언 파라미터 순서: qw, qx, qy, qz
        qw, qx, qy, qz = map(float, parts[1:5])
        # 이동 벡터 파라미터 순서: tx, ty, tz
        tx, ty, tz = map(float, parts[5:8])
        name = parts[9]

        # SciPy Rotation 클래스를 활용하여 쿼터니언을 3x3 회전행렬 R로 안정적으로 직렬 변환
        # SciPy는 쿼터니언 파라미터로 [qx, qy, qz, qw] 순서의 입력을 받습니다.
        R = Rotation.from_quat([qx, qy, qz, qw]).as_matrix()
        t = np.array([tx, ty, tz]).reshape(3, 1)  # (3, 1) 행렬 모양으로 규격화
        
        poses[name] = {'R': R, 't': t}
        
    return poses
```

### 7.3 이미지 파일 및 LiDAR 데이터 로드 코드

```python
import cv2
import open3d as o3d

def load_images(base_dir, names):
    """
    지정된 폴더에서 타겟 이미지들을 OpenCV 배열(BGR) 형태로 로드합니다.
    """
    images = {}
    for name in names:
        path = f"{base_dir}/images/{name}"
        img = cv2.imread(path)
        images[name] = img
    return images

def load_lidar_gt(ply_path):
    """
    open3d를 활용해 수천만 개의 3차원 포인트 데이터를 numpy 배열로 고속 적재합니다.
    """
    pcd = o3d.io.read_point_cloud(ply_path)
    points = np.asarray(pcd.points)  # (N, 3) 크기의 3D 포인트 클라우드 좌표 배열
    return points
```

---

## 8. 데이터 통합 로딩 및 검증 구동

설계한 함수들을 결합하여, 우리가 3-View 실습에 사용할 상위 3장의 타겟 프레임 이미지와 LiDAR 포인트들의 로딩 상태를 최종 점검합니다.

```python
import os

# Google Drive 저장소 또는 로컬 프로젝트 데이터 폴더 경로
DATA_DIR = "/content/drive/MyDrive/dataset/ETH3D/data/pipes"

# 1. 돋보기 스펙 행렬(Cameras) 로딩
cameras = load_cameras(os.path.join(DATA_DIR, "dslr_calibration_undistorted/cameras.txt"))
# 2. 모든 촬영 궤적 포즈(Poses) 로딩
poses   = load_images_poses(os.path.join(DATA_DIR, "dslr_calibration_undistorted/images.txt"))
# 3. 고정밀 3D 스캔 점 구름(LiDAR PCD) 로딩
lidar   = load_lidar_gt(os.path.join(DATA_DIR, "dslr_scan_eval/scan1.ply"))

# 3-View 실습에 사용할 맨 처음 정렬된 3장의 타겟 이미지 파일명 선택
img_names = sorted(poses.keys())[:3]
images = load_images(DATA_DIR, img_names)

# 카메라 모델 0에 할당된 돋보기 행렬 K 추출
K = cameras[0]

print("=========================================")
print(f"Intrinsic matrix K (돋보기 변환):\n{K}")
print(f"실습에 활용할 3장 이미지: {img_names}")
print(f"로딩 완료된 이미지 장수: {len(images)}장")
print(f"LiDAR 고정밀 지상 스캔 점 개수: {len(lidar):,}개")
print("=========================================")
```

실행 시 콘솔에 다음과 같은 기분 좋은 성공적인 적재 로그가 시원하게 출력됩니다.

```
=========================================
Intrinsic matrix K (돋보기 변환):
[[3430.27    0.   3119.2 ]
 [   0.   3429.23 2057.75]
 [   0.      0.      1.  ]]
실습에 활용할 3장 이미지: ['dslr_images_undistorted/DSC_0634.JPG', 'dslr_images_undistorted/DSC_0635.JPG', 'dslr_images_undistorted/DSC_0636.JPG']
로딩 완료된 이미지 장수: 3장
LiDAR 고정밀 지상 스캔 점 개수: 11,482,717개
=========================================
```

---

## 다음 편 예고

데이터 준비라는 중요한 첫 고개를 무사히 넘겼습니다! 

다음 **[2편: Feature 추출 및 매칭]**에서는 로드된 세 장의 이미지에서 **SIFT 특징 추출기**를 활용해 고유한 시각 열쇠들을 찾아내고, **BFMatcher와 RANSAC 기하학 필터**를 통해 이미지 사이에 완벽하게 포개어지는 1대1 매칭 쌍을 수천 개 찾아내는 본격적인 실습을 진행해 보겠습니다. 다음 장에서 뵙겠습니다!
