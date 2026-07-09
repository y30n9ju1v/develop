---
title: "LiDAR 포인트 클라우드: 구조, 포맷, 전처리"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["autonomous", "lidar", "point-cloud", "laz", "las", "pcd", "apache-arrow", "voxel"]
categories: ["autonomous"]
description: "LiDAR가 어떻게 동작하고, x/y/z/intensity 4열이 왜 기본 구조인지, LAZ와 Arrow IPC 중 언제 무엇을 쓰는지, 그리고 전처리 핵심 3가지를 정리합니다."
---

> LiDAR 센서 동작 원리, 포인트 클라우드의 물리적 의미, 날씨 취약성 등 하드웨어 입문은 [LiDAR 포인트 클라우드 입문](/docs/autonomous/sensor/lidar-point-cloud-for-beginners/)을 먼저 읽으세요. 이 글은 파이프라인 관점(포맷 선택, Arrow 통합, 전처리)에 집중합니다.

> 이 글에서 다루는 Arrow RecordBatch, Zero-Copy, 컬럼 기반 접근의 원리는 [Apache Arrow가 압도적으로 빠른 이유](../apache-arrow-internals/)에서 자세히 설명합니다.

DORA 시뮬레이터 통합 글에서 LiDAR 데이터는 "x/y/z/intensity 열을 가진 Arrow RecordBatch"로 표현하라고 했습니다. py123d-for-beginners에서는 LAZ 파일을 쓰면 압축 해제 비용이 있다고 했습니다. 커스텀 파서 글에서는 `.laz` 파일 경로를 `ParsedLidar`에 넘겼습니다.

이 선택들이 왜 이렇게 됐는지, LiDAR가 무엇인지부터 정리합니다.

---

## 1. LiDAR가 데이터를 만드는 방법

**LiDAR(Light Detection and Ranging)**는 레이저 펄스를 쏘고 반사되어 돌아오는 시간을 측정해 거리를 계산하는 센서입니다.

### 회전형 LiDAR (Spinning LiDAR)

자율주행에 가장 많이 쓰이는 방식입니다. Velodyne, Ouster, Hesai 등이 이 방식입니다.

내부에 여러 개의 레이저 다이오드가 수직으로 쌓인 채로 수평 360도 회전합니다. 레이저 하나가 하나의 **빔(ring)**입니다. 빔이 64개이면 64채널 LiDAR입니다.

한 바퀴 회전하는 동안 각 빔이 방위각마다 레이저를 쏘고 반사를 받아 거리를 측정합니다. 이 결과가 **하나의 스캔(sweep)**입니다.

```
채널 수   ← 수직 해상도 (높을수록 밀도 높음)
회전 속도 ← 초당 스캔 횟수 (10Hz = 초당 10번 360도 회전)
포인트 수 ← 채널 수 × 수평 해상도
```

10Hz LiDAR 64채널의 경우: 스캔 하나에 약 12만~13만 포인트가 생깁니다. 이것이 100ms 동안 측정됩니다.

### 솔리드 스테이트 LiDAR

기계적으로 회전하는 부품이 없습니다. MEMS 미러나 OPA(Optical Phased Array)로 레이저 방향을 제어합니다. 내구성이 높고 소형화가 용이하지만, 커버 범위가 제한적입니다. 최근 양산 차량에 탑재되는 방식입니다.

---

## 2. 포인트 하나의 구조

LiDAR 포인트 하나는 최소 다음 정보를 가집니다.

| 필드 | 의미 | 타입 |
|------|------|------|
| **x** | 포인트의 X 좌표 (ISO 8855: 전방) | float32 |
| **y** | 포인트의 Y 좌표 (ISO 8855: 좌측) | float32 |
| **z** | 포인트의 Z 좌표 (ISO 8855: 위) | float32 |
| **intensity** | 반사 강도 (0~255 또는 0~1) | float32 |

**intensity가 중요한 이유**: 반사 강도는 물체의 재질을 반영합니다. 차선 도색(흰색/노란색)은 아스팔트보다 반사율이 높아 intensity가 높습니다. 도로 표지판의 반사 테이프도 intensity가 높습니다. 이 채널을 보면 라이다만으로도 차선과 표지판을 감지하는 단서가 됩니다.

**추가 필드(선택적)**:
- `ring`: 해당 포인트를 만든 빔의 인덱스 (0~63). 수직 구조 이해에 유용
- `timestamp`: 포인트가 측정된 정확한 시각 (스캔 내 서브 타임스탬프). 차량이 움직이면서 측정하기 때문에 스캔 안에서도 포인트마다 차량 위치가 다름
- `object_idx`, `object_tag`: CARLA semantic LiDAR에서 제공. 어떤 액터에서 반사됐는지 GT 레이블

---

## 3. 왜 Arrow RecordBatch가 자연스러운가

LiDAR 포인트 클라우드를 저장할 때 **행 기반**(포인트마다 [x, y, z, intensity] 묶음)과 **열 기반**(x 배열, y 배열, z 배열, intensity 배열)의 두 가지 구조가 있습니다.

Arrow RecordBatch는 열 기반입니다. LiDAR 처리에서 이것이 유리한 이유:

**지면 제거(Ground Removal)**: z 좌표가 특정 임계값 이하인 포인트를 제거합니다. z 열만 읽으면 됩니다. 행 기반이라면 포인트마다 x, y, z, intensity를 모두 읽은 뒤 z만 봐야 합니다.

**강도 기반 필터링**: intensity가 특정값 이상인 포인트만 추출합니다. intensity 열만 읽습니다.

**3D 거리 계산**: `sqrt(x² + y²)` — x열과 y열만 씁니다.

Arrow의 컬럼 기반 레이아웃 덕분에 필요한 열만 CPU 캐시에 올라오고, SIMD로 벡터 연산까지 자동 적용됩니다.

DORA 시뮬레이터 연동 글에서 "perception 노드가 보통 특정 열만 씁니다. 포인트 필터링에는 z만, 강도 기반 필터링에는 intensity만"이라고 한 이유가 이것입니다.

---

## 4. 파일 포맷

### LAS / LAZ

**LAS(LASer)**: 지형 측량·항공 LiDAR 업계의 표준 포맷입니다. 포인트마다 x/y/z/intensity와 메타데이터를 바이너리로 저장합니다.

**LAZ**: LAS의 압축 버전입니다. 70~90%의 크기 절감이 가능합니다. nuScenes, AV2, py123d가 기본적으로 LAZ를 씁니다.

LAZ의 단점: 읽을 때마다 압축 해제가 필요합니다. FiftyOne과 Rerun은 LAZ를 직접 렌더링하지 못해 py123d가 중간에서 numpy 배열로 변환합니다. 파일 복사는 없지만 CPU 비용은 있습니다.

### PCD (Point Cloud Data)

ROS와 PCL(Point Cloud Library)의 기본 포맷입니다. ASCII와 바이너리 두 종류가 있습니다. 헤더에 필드 이름, 타입, 크기를 선언하는 구조라 커스텀 필드를 추가하기 쉽습니다.

사내 수집 데이터나 KITTI 포맷이 PCD인 경우가 많습니다. py123d는 PCD를 네이티브로 지원하지 않아 `ParsedLidar`에 넘기기 전에 LAZ로 변환하거나 numpy 배열로 직접 넘겨야 합니다.

### Arrow IPC

반복 접근하는 데이터를 가장 빠르게 읽는 방법입니다. 압축 해제 비용이 없고, mmap으로 Zero-Copy 읽기가 가능합니다. py123d 변환 시 코덱을 `arrow_ipc`로 선택하면 LAZ 대신 Arrow IPC로 저장합니다.

**LAZ vs Arrow IPC 선택 기준**:

| 상황 | 권장 포맷 |
|------|---------|
| 장기 보관, 디스크 절약 우선 | LAZ |
| 학습 루프, 회귀 테스트처럼 반복 읽기 | Arrow IPC |
| DORA 파이프라인 실시간 처리 | Arrow RecordBatch (메모리) |

---

## 5. 핵심 전처리 3가지

### 지면 제거 (Ground Removal)

포인트 클라우드의 상당 부분은 도로 표면입니다. 도로 포인트는 물체 감지에 노이즈가 되고, 처리 속도를 늦춥니다.

**높이 임계값 방법**: z가 특정값 이하인 포인트를 제거합니다. 빠르지만 경사진 도로에서 부정확합니다.

**RANSAC 평면 피팅**: 랜덤 샘플링으로 평면 방정식을 추정하고, 평면에 가까운 포인트를 지면으로 분류합니다. 경사로에서도 잘 동작하지만 계산 비용이 있습니다.

### Voxel Grid 다운샘플링

포인트 클라우드를 3D 그리드로 나누고, 각 셀(voxel)에서 포인트를 하나로 대표합니다. 보통 셀의 중심점 또는 centroid를 씁니다.

```
전: 130,000 포인트
후 (voxel size=0.2m): ~15,000 포인트
```

다운샘플링 후에도 물체의 전반적인 형태가 보존됩니다. 사용 이유:

- **Rerun 원격 전송**: 130,000 포인트를 매 프레임 네트워크로 보내면 대역폭을 금방 초과합니다. 15,000 포인트로 줄이면 시각화에는 충분하고 전송량은 1/9로 줍니다.
- **추론 속도**: ML 모델 입력으로 전체 포인트를 쓰면 느립니다. 다운샘플링으로 균일한 밀도를 확보하면 처리 속도와 성능이 균형을 이룹니다.

### ROI 필터링

관심 영역(Region of Interest) 이외의 포인트를 제거합니다.

- **거리 필터**: 차량 기준 반경 50m 이상은 제거 (너무 멀어 감지 의미 없음)
- **높이 필터**: 지면 아래(-1m 미만)나 너무 높은(5m 이상) 포인트 제거
- **각도 필터**: 특정 방위각 범위만 남기기 (후방 사각지대 제외 등)

---

## 6. LiDAR 타임스탬프의 섬세함

회전형 LiDAR는 100ms 동안 360도를 회전하며 포인트를 측정합니다. 이 100ms 동안 차량도 이동합니다. 60km/h로 주행하면 100ms에 약 1.7m 이동합니다.

스캔의 **시작 시각에 측정된 포인트**와 **종료 시각에 측정된 포인트**는 서로 다른 차량 위치에서 측정된 것입니다. 이를 보정하지 않으면 포인트 클라우드가 약간 회전된 형태로 일그러집니다.

이 보정을 **모션 보상(Motion Compensation)**이라 합니다. 각 포인트의 서브 타임스탬프와 IMU 데이터를 결합해 스캔 시작 시각의 차량 좌표계로 모든 포인트를 정렬합니다.

py123d `ParsedLidar`에 `start_timestamp`와 `end_timestamp`가 별도로 있는 이유입니다. Waymo 파서에서 스윕 시작 시각과 포즈 시각의 50ms 차이를 보정하는 이유이기도 합니다.

---

## 7. 포맷 선택 요약

```
LiDAR 데이터 흐름 예시:

실차 수집 / CARLA  →  LAZ 파일 (장기 보관)
                                ↓
           py123d ParsedLidar (경로 포인터만)
                                ↓
           변환 시 Arrow IPC (반복 읽기용)
                         OR
           DORA 파이프라인 안에서
           Arrow RecordBatch (메모리, 컬럼 단위 처리)
                                ↓
           전처리 (지면 제거, 다운샘플링, ROI 필터)
                                ↓
           Perception 모델 입력
```

각 포맷이 쓰이는 이유가 있습니다. LAZ는 저장 효율, Arrow IPC는 읽기 효율, Arrow RecordBatch는 처리 효율을 위한 선택입니다.

---

*관련 글: [LiDAR 포인트 클라우드 입문](/docs/autonomous/sensor/lidar-point-cloud-for-beginners/), [센서 퓨전 기초: LiDAR 포인트를 카메라 이미지에 투영하기](/docs/autonomous/sensor/lidar-to-camera-projection/), [Apache Arrow가 압도적으로 빠른 이유](../apache-arrow-internals/)*
