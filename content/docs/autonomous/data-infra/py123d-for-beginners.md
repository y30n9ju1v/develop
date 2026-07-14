---
title: "py123d 입문: 자율주행 데이터셋의 공통어"
date: 2026-07-08T00:00:00+09:00
draft: false
tags: ["autonomous", "py123d", "apache-arrow", "nuscenes", "waymo", "argoverse", "dataset"]
categories: ["autonomous"]
description: "nuScenes, Waymo, Argoverse 2 등 파편화된 자율주행 데이터셋을 단 하나의 API로 다룰 수 있게 해주는 py123d의 설계 원리와 사용법을 소개합니다."
---

> 이 글은 [py123d GitHub](https://github.com/kesai-labs/py123d)과 논문 [123D: Unifying Multi-Modal Autonomous Driving Data at Scale](https://arxiv.org/html/2605.08084v1)을 참고해 작성했습니다.
> py123d가 내부적으로 쓰는 Apache Arrow가 생소하다면 먼저 **[Apache Arrow가 압도적으로 빠른 이유](../apache-arrow-internals/)**를 읽어보세요.

---

## 1. 문제: 데이터셋마다 다른 언어를 쓴다

자율주행 연구를 하다 보면 필연적으로 여러 데이터셋을 다루게 됩니다. nuScenes, Waymo, Argoverse 2, KITTI-360, PandaSet… 각각 방대한 데이터를 제공하지만, 한 프로젝트에서 이 데이터셋들을 함께 쓰려는 순간부터 고통이 시작됩니다.

- **좌표계가 제각각입니다.** X축이 앞을 가리키는 곳도 있고, Y축이 앞인 곳도 있습니다.
- **파일 포맷이 다릅니다.** nuScenes는 JSON, Waymo는 Protobuf, Argoverse 2는 Parquet를 씁니다.
- **센서 주기가 다릅니다.** 카메라는 12Hz, 라이다는 10~20Hz, 레이더는 13~20Hz로 각자 돌아갑니다. (데이터셋·하드웨어마다 다름. nuScenes 라이다는 20Hz, 레이더는 약 13Hz)
- **라벨 체계가 다릅니다.** nuScenes의 "car"와 Waymo의 "TYPE_VEHICLE"은 같은 물체지만 다른 이름입니다.
- **전용 패키지가 충돌합니다.** nuScenes SDK와 Waymo Open Dataset 패키지를 같은 환경에 설치하면 의존성이 꼬입니다.

결국 개발자는 데이터셋마다 별도의 파싱 코드를 작성하고, 모델을 다른 데이터셋으로 테스트할 때마다 파이프라인을 처음부터 다시 짭니다. 이 반복 작업이 자율주행 연구에서 가장 큰 낭비 중 하나입니다.

---

## 2. py123d: 데이터셋의 공통 번역기

**py123d**는 이 파편화 문제를 해결하는 오픈소스 Python 라이브러리입니다. 9개 데이터셋, 3,300시간 이상, 90,000km 이상의 주행 데이터를 **하나의 통일된 Apache Arrow 포맷**으로 변환하고, **단 하나의 API**로 접근할 수 있게 해줍니다.

지원 데이터셋:

| 종류 | 데이터셋 |
|------|---------|
| 수동 라벨 (고정밀) | nuScenes, Waymo Open Dataset, Argoverse 2, PandaSet, KITTI-360 |
| 자동 라벨 (대규모) | Waymo Open Motion, nuPlan, PAI-AV |
| 합성 데이터 | CARLA |

"자동 라벨" 카테고리는 사람이 직접 어노테이션한 게 아니라 자동화된 파이프라인으로 라벨링한 데이터셋입니다. 규모가 크지만 라벨 정밀도는 수동 라벨보다 낮습니다.

그 중 **PAI-AV**는 NVIDIA의 PhysicalAI-Autonomous-Vehicles 데이터셋으로, 이 목록에서 단연 가장 큰 규모입니다. 25개국, 2,500개 이상 도시에서 수집한 **1,700시간** 분량의 주행 데이터로, 20초짜리 클립 306,152개로 구성됩니다. 멀티카메라(전 클립), LiDAR(298,326개 클립), 레이더(160,761개 클립)를 포함하며 상업적 사용도 가능합니다. nuScenes(1,000개 씬)나 Waymo(1,000개 씬)와 비교하면 압도적인 규모 차이가 있습니다.

---

## 3. 모달리티: py123d가 다루는 데이터 종류

이 시리즈의 다른 글들(예: [py123d → NuRec](py123d-to-nurec/))은 `EgoStateSE3`, `ParsedCamera`, `ParsedLidar`, `BoxDetectionsSE3` 네 가지만 주로 다뤘는데, 이건 "특정 파이프라인(NuRec 재구성)에 필요한 최소 요건"으로 고른 부분집합입니다. [py123d GitHub 저장소](https://github.com/kesai-labs/py123d)의 README·체인지로그를 보면 실제로는 이보다 훨씬 다양한 모달리티를 다룹니다.

| 분류 | 클래스 | 내용 |
|---|---|---|
| 센서 | `ParsedCamera` | 여러 카메라 리그의 이미지 데이터 |
| 센서 | `ParsedLidar` | 라이다 포인트 클라우드 |
| 센서 | `Radar` | 레이더 데이터 (v0.6.0에서 추가, nuScenes·PAI-AV 파서 지원) |
| 상태/동역학 | `EgoState`(문서에 `EgoStateSE3`로도 표기됨) | 차량 pose + 속도·가속도 추론(`LogWriter`가 포즈로부터 계산) |
| 라벨 | `BoxDetectionsSE3` | 3D 바운딩 박스 검출(속도·가속도 추론 포함) |
| 라벨 | `BoxDetectionsSE2` | SE3 검출을 2D(SE2)로 투영한 버전 |
| 세그멘테이션 | 카메라 semantic/instance segmentation | KITTI-360, WOD-Perception 등에서 지원 |
| 세그멘테이션 | 라이다 semantic/instance segmentation | nuScenes, WOD-Perception, PandaSet 등에서 지원 |
| 지도 | `MapAPI` | HD맵, 차선 토폴로지를 `networkx.DiGraph`(전/후속 차선-차선그룹)로 제공 |
| 지도/기하 | `Polyline2D` / `PolylineSE2` / `PolylineSE3` | 차선·경로를 폴리라인으로 표현, `subline()` 등 |
| 지도 | `OccupancyMap2D` | 2D 점유 맵 표현 |
| 인프라 | 신호등(Traffic Lights) | 시간에 따른 신호 상태 라벨 |

**이름 표기에 주의할 점이 하나 있습니다.** README/체인지로그 원문은 `EgoState`("velocity/acceleration inference in `LogWriter` from poses for `EgoState`")라고 쓰는데, 이 시리즈의 다른 글들은 `EgoStateSE3`라고 써왔습니다. "SE3"가 클래스 이름 자체의 일부인지, 아니면 "SE3 표현을 쓰는 EgoState"라는 설명적 표현인지는 README만으로는 확실히 가르기 어렵습니다 — 실제로 코드를 짤 때는 이 이름을 그대로 믿지 말고 `py123d.datatypes` 모듈을 직접 import해서 정확한 클래스명과 필드를 확인하시길 권합니다.

---

## 4. 핵심 설계: 독립적인 타임스탬프 스트림

py123d의 가장 중요한 설계 결정은 **각 센서를 독립적인 타임스탬프 이벤트 스트림으로 저장**한다는 것입니다.

전통적인 방식은 모든 센서를 하나의 "프레임"으로 묶습니다.

```
프레임 0: {카메라, 라이다, 레이더, GPS}  ← 모두 동기화 필요
프레임 1: {카메라, 라이다, 레이더, GPS}
```

이 방식은 센서 주기가 다를 때 데이터를 맞추는 과정에서 정보 손실이 생기고, 새 센서를 추가하면 스키마 전체를 바꿔야 합니다.

py123d는 각 센서를 별도 스트림으로 관리합니다.

```
카메라 스트림:  [t=0.000, t=0.083, t=0.166, ...]  (12Hz)
라이다 스트림:  [t=0.000, t=0.050, t=0.100, ...]  (20Hz, nuScenes 기준)
레이더 스트림:  [t=0.000, t=0.077, t=0.154, ...]  (~13Hz, nuScenes 기준)
```

특정 시각에 접근할 때는 "가장 가까운 타임스탬프"를 찾는 방식으로 동기화합니다. 강제 동기화 없이 원본 캡처 주기 그대로 보존됩니다.

---

## 5. 디스크 복사 없음 — 단, 모달리티마다 다르다

py123d는 내부적으로 [Apache Arrow](../apache-arrow-internals/) IPC 포맷을 씁니다. 변환 후 만들어지는 Arrow 파일은 원본 센서 파일을 **디스크에 복사하지 않습니다.** 파일의 경로(포인터)만 Arrow 파일에 기록하고, 원본은 제자리에 둡니다.

하지만 "Zero-Copy"가 모든 모달리티에 동일하게 적용되는 건 아닙니다. 실제로 데이터를 읽을 때 모달리티마다 동작이 다릅니다.

| 모달리티 | 저장 방식 | 접근 시 동작 |
|---------|----------|------------|
| **카메라** (JPEG/PNG) | 원본 경로 포인터 | 파일 직접 읽기, 복사 없음 |
| **메타데이터·라벨** | Arrow IPC | 메모리 맵, 진짜 Zero-Copy |
| **라이다** (LAZ) | 원본 경로 포인터 | **LAZ 압축 해제 → numpy 배열** (CPU 비용 있음) |
| **라이다** (Arrow IPC) | Arrow IPC | 메모리 맵, Zero-Copy |
| **HD Map** | Arrow IPC (STR 공간 인덱싱) | 메모리 맵, Zero-Copy |

라이다를 LAZ로 저장하면 디스크 공간을 아낄 수 있지만(70~90% 압축), 읽을 때마다 압축 해제가 일어납니다. FiftyOne이나 Rerun은 LAZ를 직접 렌더링하지 않으므로, py123d가 내부적으로 LAZ를 압축 해제해 numpy XYZ 배열로 변환한 뒤 넘겨줍니다. **파일 복사는 없지만, 이 압축 해제 비용은 존재합니다.**

접근 빈도가 높은 라이다 데이터는 Arrow IPC 포맷으로 변환해두면 이 비용을 없앨 수 있습니다. py123d는 변환 시 코덱을 선택할 수 있어, 용량과 속도 사이의 트레이드오프를 조절할 수 있습니다.

LRU 캐시로 메모리 사용량이 실제로 접근한 데이터에만 비례합니다.

---

## 6. 통일된 좌표계

모든 데이터셋의 좌표계를 **ISO 8855** 표준으로 통일합니다.

- X축: 차량 전방
- Y축: 차량 좌측
- Z축: 위쪽

카메라는 **OpenCV 컨벤션**으로 통일합니다. 데이터셋마다 좌표 변환 코드를 따로 짤 필요가 없습니다.

ISO 8855가 무엇인지, SAE J670·CARLA·ROS와 어떻게 다른지는 [자율주행 좌표계 완전 정리](../iso-8855-coordinate-systems/)에서 자세히 다룹니다.

---

## 7. 설치와 변환

```bash
# 기본 설치
pip install py123d

# 데이터셋별 파서 추가 (필요한 것만)
pip install py123d[av2]       # Argoverse 2
pip install py123d[nuscenes]  # nuScenes
pip install py123d[waymo]     # Waymo
```

변환은 CLI 한 줄로 됩니다.

```bash
export PY123D_DATA_ROOT=/path/to/data

# Argoverse 2 변환
py123d-conversion dataset=av2-sensor-stream \
  dataset.parser.splits='[av2-sensor_val]'
```

---

## 8. API 사용법

변환된 데이터는 `SceneFilter`로 원하는 조건을 걸어 씬을 가져옵니다.

```python
from py123d import SceneFilter, get_filtered_scenes

# nuScenes와 Argoverse 2 훈련 데이터 중 0.5초 구간씩
scene_filter = SceneFilter(
    split_names=["av2-sensor_train", "nuscenes_train"],
    target_iteration_duration_s=0.5
)
scenes = get_filtered_scenes(scene_filter)
scene = scenes[0]

# Ego 상태 조회
ego = scene.get_ego_state_se3_at_iteration(iteration=0)

# 가장 가까운 타임스탬프의 카메라 이미지
camera = scene.get_camera_at_timestamp(
    timestamp=ego.timestamp,
    criteria="nearest"
)

# 반경 50m 이내 HD 맵 객체
nearby_map = scene.get_map_api().get_map_objects_in_radius(
    point=ego.center_3d,
    radius=50.0
)
```

반경 쿼리가 빠른 이유는 py123d가 HD Map을 Arrow IPC로 저장할 때 **STRtree(Sort-Tile-Recursive 공간 인덱스)**를 함께 빌드해두기 때문입니다. 점·선·다각형 벡터 데이터를 공간적으로 정렬하고 타일로 분할해두면, "반경 50m" 쿼리가 전체 맵을 순회하지 않고 인덱스만으로 후보를 좁힙니다. Zero-Copy Arrow 메모리 맵 위에서 이 인덱스가 동작하므로, 수백 MB 규모의 도시 맵도 수 밀리초 안에 쿼리할 수 있습니다.

nuScenes를 쓸 때와 Argoverse 2를 쓸 때 코드가 **완전히 동일**합니다.

---

## 9. 내장 시각화

별도 툴 없이 py123d만으로 3D 시각화를 할 수 있습니다.

```bash
# Viser 기반 인터랙티브 3D 뷰어
py123d-viser scene_filter=av2-sensor
```

다만 프로덕션 파이프라인에서는 [Rerun](../autonomous-data-pipeline/)처럼 타임라인 기반 시각화 툴과 연결하는 것이 더 강력합니다.

---

## 10. 다른 프레임워크와 비교

자율주행 데이터를 다루는 프레임워크가 py123d만 있는 건 아닙니다.

| 프레임워크 | 강점 | 한계 |
|-----------|------|------|
| **py123d** | 원시 센서 데이터 전체(카메라, 라이다, 맵, 라벨) 통합, Arrow 기반 | 비교적 신생 |
| **trajdata** | 궤적/예측 태스크에 최적화 | 원시 센서 데이터 미지원 |
| **MMDetection3D** | 3D 감지 모델 학습에 최적화 | 데이터 형식이 태스크에 종속적 |
| **각 데이터셋 SDK** | 해당 데이터셋에 가장 정확 | 다른 데이터셋과 혼용 불가 |

py123d의 포지션은 명확합니다. **"어떤 태스크를 하든, 어떤 데이터셋을 쓰든 동일한 인터페이스로"** 접근하는 것입니다.

---

## 11. 정리

| 문제 | py123d의 해법 |
|------|--------------|
| 데이터셋마다 다른 좌표계 | ISO 8855 / OpenCV 컨벤션으로 통일 |
| 데이터셋마다 다른 파일 포맷 | Apache Arrow IPC로 변환 |
| 센서 주기 불일치 | 독립 타임스탬프 스트림 + nearest 조회 |
| 테라바이트 복사 비용 | 경로 포인터만 저장, Zero-Copy 읽기 |
| 패키지 의존성 충돌 | 데이터셋별 extras로 선택 설치 |

py123d를 쓰면 데이터셋을 바꿀 때 코드를 고칠 필요가 없습니다. 데이터 파싱에 쓰던 시간을 모델과 알고리즘에 쏟을 수 있게 됩니다.

다음 글에서는 두 가지 방향으로 이어집니다.

- py123d를 FiftyOne, Rerun과 연결해 [실제 데이터 파이프라인을 구축하는 방법](../autonomous-data-pipeline/)
- nuScenes·Waymo·AV2 변환 코드를 분석하고 [사내 데이터셋용 커스텀 파서를 직접 작성하는 방법](../py123d-dataset-conversion/)
