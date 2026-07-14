---
title: "NCore V4 입문: NuRec가 읽는 컴포넌트 기반 센서 데이터 포맷"
date: 2026-07-14T00:00:00+09:00
draft: false
tags: ["autonomous", "nvidia", "ncore", "nurec", "neural-reconstruction", "zarr", "sensor-data"]
categories: ["autonomous"]
description: "NVIDIA NCore의 V4 컴포넌트 기반 데이터 포맷이 무엇이고, 어떤 컴포넌트로 구성되며, Python API로 어떻게 읽는지 초보자 기준으로 정리합니다."
---

> 이 글은 [NVIDIA NCore GitHub 저장소](https://github.com/NVIDIA/ncore)와 [공식 문서](https://nvidia.github.io/ncore/)를 참고해 작성했습니다.
> NCore가 실제로 어디에 쓰이는지(NuRec 신경 재구성 파이프라인과의 관계)는 [py123d → NVIDIA NuRec(NCore)](../py123d-to-nurec/)에서 이어서 다룹니다. 이 글은 그 앞 단계 — NCore V4 포맷 자체가 무엇인지에 집중합니다.

---

## 1. NCore가 뭔가

**NCore**는 NVIDIA가 만든 오픈소스 라이브러리로, 로보틱스·자율주행 분야의 멀티센서 데이터를 다루기 위한 **데이터 표현, API, 도구 모음**입니다. 공식 저장소는 NCore를 "데이터 기반 신경 재구성(neural reconstruction)을 지원하는 데이터 표현, API, 도구"라고 소개합니다.

카메라·라이다·레이더 같은 여러 센서에서 수집한 주행 로그를 **하나의 표준화된 포맷**으로 담아두고, 그 위에서 3D 재구성(NeRF/3DGS 기반 NuRec 같은 파이프라인)이나 학습 데이터셋 변환을 할 수 있게 해주는 게 NCore의 역할입니다. `pip install nvidia-ncore`로 설치할 수 있고, Apache 2.0 라이선스로 공개되어 있습니다.

---

## 2. 왜 "V4"인가: 컴포넌트 기반 설계

NCore의 데이터 포맷은 버전이 있고, 현재(이 글 작성 시점) 최신·표준 포맷이 **V4**입니다. V4가 이전 버전들과 다른 핵심은 **컴포넌트 기반(component-based)** 구조라는 점입니다. 공식 문서는 이렇게 설명합니다.

> "NCore's latest V4 component-based data format enables modular, independently-managed generic data components with flexible composition and scalability."

이 말을 풀면 이렇습니다 — 예전 방식처럼 "포즈, 카메라, 라이다, 라벨을 전부 하나의 파일/스키마에 뭉쳐 넣는" 대신, V4는 각 데이터 종류를 **독립된 컴포넌트**로 분리합니다. 포즈면 포즈끼리, 카메라면 카메라끼리 따로 저장하고, 필요한 컴포넌트만 골라 조합해서 하나의 시퀀스를 구성합니다.

이렇게 나누는 이유는 세 가지입니다.

- **독립적으로 버전을 올릴 수 있다**: 카메라 컴포넌트의 스키마가 바뀌어도 포즈 컴포넌트는 그대로 둘 수 있습니다.
- **필요한 것만 조합할 수 있다**: 라이다가 없는 데이터셋이면 라이다 컴포넌트를 아예 빼고 조합하면 됩니다.
- **같은 종류의 데이터를 여러 버전으로 공존시킬 수 있다**: 예를 들어 "공장 출고 캘리브레이션"과 "온라인으로 재보정한 캘리브레이션"을 별도의 컴포넌트 인스턴스(`factory`, `online_refined`)로 동시에 저장해 둘 수 있습니다.

---

## 3. V4의 9가지 기본 컴포넌트

NCore V4는 아래 9개의 컴포넌트 타입을 기본으로 제공합니다.

| 컴포넌트 | 담는 내용 |
|---|---|
| `PosesComponent` | 좌표계 사이의 정적/동적 강체 변환(리지드 트랜스폼) |
| `IntrinsicsComponent` | 카메라·라이다 캘리브레이션(내부 파라미터) |
| `MasksComponent` | 정적 센서 마스크(현재는 카메라만) |
| `CameraSensorComponent` | 카메라 프레임 데이터(이미지) |
| `LidarSensorComponent` | 라이다 포인트 클라우드(레이 지오메트리 포함) |
| `RadarSensorComponent` | 레이더 감지 결과와 레이 번들 |
| `CuboidsComponent` | 3D 바운딩 박스 트랙 관측값 |
| `PointCloudsComponent` | 미리 계산된, 타입이 붙은 포인트 클라우드 |
| `CameraLabelsComponent` | 이미지에 정렬된 라벨(깊이, 옵티컬 플로우, 세그멘테이션 등) |

이 목록에서 눈여겨볼 점은 "라벨"조차 하나의 컴포넌트로 분리되어 있다는 것입니다 — `CameraLabelsComponent`는 깊이(DEPTH), 플로우(FLOW), 세그멘테이션(SEGMENTATION), 마스크(MASK) 등 여러 종류의 라벨을 태그된 유니온(tagged union) 형태로 담을 수 있습니다. 즉 "이 시퀀스에 깊이 라벨은 있는데 세그멘테이션은 없다"는 상황도 컴포넌트 단위로 자연스럽게 표현됩니다.

필요하다면 `ComponentWriter`/`ComponentReader`를 직접 구현해 **커스텀 컴포넌트**를 추가할 수도 있습니다. 다른 조직의 컴포넌트와 이름이 겹치지 않도록, `com.myorg.velocity`처럼 역도메인(reverse-domain) 이름 규칙을 쓰도록 문서가 권장합니다.

---

## 4. 디스크 위에서는 이렇게 생겼다

V4 컴포넌트들은 **Zarr**(청크 단위로 저장되고 압축되는 배열 저장 포맷)를 기본 저장소로 씁니다. 디렉터리 형태(`.zarr`)로 두거나, 인덱스가 붙은 tar 아카이브(`.zarr.itar`) 하나로 묶어 배포할 수 있습니다.

```
ncore4[-{component_group_name}].zarr[.itar]/
├── {sequence_meta_data}
│   ├── sequence_id: str
│   ├── version: str            # 현재 "v4"
│   ├── sequence_timestamp_interval_us: {start, stop}
│   └── component_group_name: str
└── {component_type}/
    └── {component_instance_name}/
        ├── {component_meta_data}
        │   ├── component_name: str
        │   ├── component_instance_name: str
        │   └── component_version: str
        └── {component_specific_data}...
```

몇 가지 실용적인 포인트입니다.

- 기본 컴포넌트 그룹 이름은 `default`이고, 다른 그룹은 `ncore4-{component_group_name}.zarr[.itar]` 형태의 별도 아카이브로 분리할 수 있습니다 — 예를 들어 카메라·포즈는 기본 아카이브에, 용량이 큰 라이다는 `ncore4-lidar_top_360fov.zarr.itar`처럼 별도 아카이브에 두는 식입니다.
- 이미지 같은 인코딩된 데이터는 PNG/JPEG로, 커스텀 수치 데이터는 `generic_data/` 아래 이름이 붙은 NumPy 배열로 저장할 수 있습니다.
- 라이다 프레임은 **레이 지오메트리(ray_bundle)**와 **리턴 값(ray_bundle_returns)**을 분리해서 저장합니다 — 레이 방향·타임스탬프는 한 번만 기록하고, 실제로 그 레이가 맞고 돌아온 거리·강도 값은 따로 담는 구조입니다.

---

## 5. 센서 모델: "이 카메라가 정확히 어떻게 세상을 투영하는가"

NCore는 데이터를 저장만 하는 게 아니라, 각 센서가 3D 공간을 2D(또는 레이)로 어떻게 투영하는지에 대한 **GPU 가속 센서 모델**도 함께 제공합니다. 신경 재구성(NuRec 같은)이 정확한 결과를 내려면 "이 픽셀이 실제로 어느 방향의 광선에 대응하는가"를 정밀하게 알아야 하기 때문입니다.

카메라 모델은 네 가지가 있습니다.

- **FTheta**: NVIDIA의 다항식 왜곡 기반 모델로, 일반 렌즈부터 초광각 렌즈까지 지원합니다.
- **Ideal Pinhole**: 왜곡이 없는 이상적인 원근 투영 모델로, 이미지를 "똑바로 펴는"(rectification) 기준점으로 주로 쓰입니다.
- **OpenCV Pinhole**: 방사형·접선·박막 프리즘 왜곡 계수를 쓰는 표준 핀홀 모델입니다.
- **OpenCV Fisheye**: 초광각/어안 렌즈용 다항식 왜곡 모델입니다.

라이다는 **Row-Offset Structured Spinning LiDAR 모델**을 지원하며, Hesai P128 같은 회전형 라이다에 대응합니다 — 행(row)별 고도각과 열(column)별 방위각을 오프셋과 함께 파라미터화해서, 구면 좌표와 3D 레이 방향 사이를 변환합니다.

---

## 6. Python으로 실제로 읽어보기

`ncore.data.v4` 패키지가 V4 포맷을 읽는 API를 제공합니다. 시퀀스 하나를 여는 최소 코드는 이렇게 생겼습니다.

```python
from pathlib import Path
from ncore.data.v4 import SequenceComponentGroupsReader, SequenceLoaderV4

component_group_path = Path("<PATH>/ncore-demo/sequence-ncore4.json")
group_reader = SequenceComponentGroupsReader([component_group_path])
loader = SequenceLoaderV4(group_reader)

print(f"sequence-id: {loader.sequence_id}")
print(f"camera sensors: {loader.camera_ids}")
print(f"lidar sensors: {loader.lidar_ids}")
```

`SequenceComponentGroupsReader`가 3절에서 본 여러 컴포넌트(아카이브 여러 개로 나뉘어 있을 수 있는)를 하나의 논리적 시퀀스로 묶어주고, `SequenceLoaderV4`가 그 위에 "카메라 ID 목록을 달라", "포즈 그래프를 달라" 같은 편의 API를 얹습니다.

특정 카메라의 특정 프레임 이미지를 꺼내는 건 이렇게 합니다.

```python
camera_sensors = {
    camera_id: loader.get_camera_sensor(camera_id)
    for camera_id in loader.camera_ids
}
camera_image = camera_sensors["camera_front_wide_120fov"].get_frame_image_array(20)
```

라이다 포인트 클라우드는 모션 보상(motion compensation) 여부를 옵션으로 선택할 수 있습니다 — 라이다가 한 바퀴 도는 동안 차량이 계속 움직이므로, 그 움직임을 보정할지 말지를 고를 수 있는 것입니다.

```python
lidar = loader.get_lidar_sensor(loader.lidar_ids[0])
point_cloud = lidar.get_frame_point_cloud(frame_index=0, motion_compensation=True)
```

포즈(좌표계 변환)는 `loader.pose_graph`를 통해 접근하며, 센서와 차량(rig) 사이, 그리고 rig와 월드 사이의 SE(3) 변환 행렬과 타임스탬프를 제공합니다.

---

## 7. 함께 제공되는 도구들

NCore는 포맷과 API만 제공하는 게 아니라, 실제로 데이터를 들여다보고 변환하는 도구도 함께 배포합니다.

- **시각화/내보내기 도구**와 **인터랙티브 3D 뷰어**로 시퀀스를 직접 눈으로 확인할 수 있습니다.
- **시퀀스 메타데이터 도구**로 센서 구성, 길이, 컴포넌트 종류를 빠르게 조회할 수 있습니다.
- **라이다 모델 평가 도구**로 5절의 라이다 센서 모델이 실제 데이터에 얼마나 잘 맞는지 검증할 수 있습니다.
- **데이터셋 변환기**가 KITTI, nuScenes, Waymo Open Dataset, Argoverse 2, Colmap, 그리고 NVIDIA의 Physical-AI-AV(PAI) 데이터셋을 NCore V4로 변환하는 걸 지원합니다.

이 변환기 목록에서 알 수 있듯, NCore V4는 "NVIDIA 데이터셋 전용 포맷"이 아니라 **여러 공개 데이터셋을 흡수할 수 있는 공통 표현**으로 설계되어 있습니다.

---

## 8. NuRec과의 관계

지금까지 다룬 NCore V4는 그 자체로 완결된 데이터 포맷이지만, 실전에서 자주 마주치는 맥락은 **NuRec**(NVIDIA의 신경 재구성 파이프라인)의 입력 포맷이라는 점입니다 — 주행 로그를 NCore V4로 담아두면, NuRec이 그 데이터를 읽어 NeRF/3DGS 기반으로 3D 환경을 재구성하고, 그 결과를 시뮬레이션에 쓸 수 있습니다. NuRec이 그 재구성을 정확히 어떻게 계산하는지는 [NuRec 입문](../nurec-neural-reconstruction-for-beginners/)에서 다룹니다.

자율주행 데이터가 보통 nuScenes나 Waymo, 혹은 사내 포맷처럼 제각각인 상태로 존재한다는 걸 생각하면, "그 데이터를 NCore V4로 어떻게 변환해서 NuRec에 넣는가"가 다음으로 자연스럽게 이어지는 질문입니다 — 이 변환 과정(좌표계 차이, 카메라 모델 차이, 라벨 체계 차이 포함)은 [py123d → NVIDIA NuRec(NCore)](../py123d-to-nurec/)에서 이어서 다룹니다.

---

## 9. 변환에 꼭 필요한 데이터는 무엇인가

3절에서 본 9개 컴포넌트를 전부 채워야 하는 건 아닙니다. NCore 문서가 "이건 필수, 이건 선택"이라고 명시하진 않지만, **Gaussian Splatting 재구성이 원리상 요구하는 것**과 **자율주행 도메인에서 실질적으로 필요한 것**을 나눠보면 우선순위가 분명해집니다.

### 9.1 재구성 자체에 수학적으로 반드시 필요한 3가지

[NuRec 입문](../nurec-neural-reconstruction-for-beginners/)에서 다뤘듯, Gaussian Splatting은 "여러 각도에서 찍은 사진들과 앞뒤가 맞도록 가우시안을 최적화한다"는 원리로 동작합니다. 이 최적화가 성립하려면 각 이미지에 대해 다음 세 가지가 반드시 있어야 합니다.

- **카메라 이미지(`CameraSensorComponent`)**: 최적화할 대상 자체입니다. 여러 프레임, 가능하면 여러 카메라(전방/측방)에서 겹치는 각도로 찍혀야 합니다 — 한 방향만 찍으면 그 반대편은 애초에 재구성할 근거가 없습니다.
- **포즈(`PosesComponent`)**: "이 사진이 정확히 어느 위치·방향에서 찍혔는가"입니다. 이게 없으면 여러 사진을 하나의 좌표계에 맞춰 놓을 방법이 없습니다 — rig→world 궤적(동적 포즈)과 센서→rig 고정 오프셋(정적 포즈) 둘 다 필요합니다.
- **캘리브레이션(`IntrinsicsComponent`)**: 5절에서 다룬 카메라 모델 파라미터입니다 — "이 픽셀이 실제로 어느 방향의 광선에 대응하는가"입니다. 이게 틀리면 가우시안이 엉뚱한 위치에 배치됩니다.

이 셋 중 하나라도 없으면 재구성 자체가 성립하지 않습니다. 나머지 컴포넌트는 전부 이 셋을 "보정"하거나 "품질을 높이는" 역할입니다.

### 9.2 AV 도메인에서 사실상 필수인 2가지

- **라이다(`LidarSensorComponent`)**: 이론적으로는 이미지만으로도 재구성이 가능하지만, 자율주행 데이터는 일반 사진측량(photogrammetry)처럼 물체 주변을 360도로 도는 게 아니라 **한 방향으로만 스쳐 지나가며** 찍습니다. 이런 좁은 시야각(sparse view)에서는 이미지만으로 정확한 3D 형태를 복원하기 어렵고, 라이다의 정확한 거리 정보가 없으면 재구성이 실제 스케일과 어긋나거나 왜곡되기 쉽습니다.
- **큐보이드(`CuboidsComponent`)**: Gaussian Splatting은 기본적으로 정적인 장면을 가정합니다. 그런데 주행 로그에는 움직이는 차·보행자가 찍혀 있습니다. 이 동적 객체를 표시해두지 않으면, 최적화 과정에서 "같은 위치인데 프레임마다 다른 게 보인다"는 모순이 생겨 고스트처럼 흐릿하게 겹친 아티팩트가 남습니다. 큐보이드로 동적 객체를 따로 분리해야 배경은 깨끗하게 재구성되고, 움직이는 물체는 따로 다뤄질 수 있습니다.

### 9.3 있으면 품질이 좋아지지만 없어도 되는 것

- **레이더(`RadarSensorComponent`)**: 라이다를 보완하는 정도로, 없어도 재구성 자체는 됩니다.
- **마스크(`MasksComponent`)**: 카메라 후드나 워터마크처럼 항상 가려지는 영역을 재구성에서 제외하는 용도 — 없으면 그 영역이 그냥 이상하게 재구성될 뿐, 전체를 막지는 않습니다.
- **카메라 라벨(`CameraLabelsComponent`, 깊이/세그멘테이션 등)**: 있으면 재구성 최적화에 추가 supervision(감독 신호)을 줘서 품질과 수렴 속도를 높일 수 있지만, 필수는 아닙니다.

정리하면 **최소 요건은 "카메라 이미지 + 포즈 + 캘리브레이션" 세 가지**이고, 자율주행 도메인에서 실전 품질을 내려면 **라이다와 동적 객체 큐보이드**가 사실상 추가로 필요합니다 — 이 다섯 가지가 [py123d → NuRec](../py123d-to-nurec/) 변환 코드가 실제로 다루는 4개 모달리티(EgoState/포즈, Cuboid, Lidar, Camera)와 정확히 일치합니다.

### 9.4 이 데이터, 전부 사람이 직접 만들어야 하나?

여기서 헷갈리기 쉬운 지점이 있습니다 — 위에서 "필요하다"고 한 컴포넌트가 전부 **원본 센서 로그**여야 하는 건 아닙니다. 실제로 3절의 컴포넌트 설명을 다시 보면, `PointCloudsComponent`는 "**Pre-computed** point clouds with typed attributes"라고 되어 있습니다 — 이미 사전 계산을 거친 파생 데이터라는 뜻입니다.

즉 변환 파이프라인은 크게 두 종류의 입력을 다룹니다.

- **원본 센서 데이터를 그대로 담는 컴포넌트**: 카메라 이미지, 라이다 raw 포인트, 포즈(GPS/IMU/휠 오도메트리에서 온 궤적)처럼, 차량이 실제로 기록한 값을 거의 그대로 옮겨 담는 컴포넌트입니다.
- **다른 모델·도구를 거쳐 나온 파생 데이터를 담는 컴포넌트**: 큐보이드(3D 객체 검출/트래킹 모델의 출력), 카메라 라벨의 깊이·세그멘테이션(별도의 깊이 추정·세그멘테이션 네트워크 출력), `PointCloudsComponent`(멀티뷰 스테레오나 SfM 등으로 미리 계산된 포인트 클라우드)처럼, **변환 전에 다른 파이프라인 단계를 한 번 거쳐야 나오는 값**입니다.

바꿔 말하면, "큐보이드가 필요하다"는 건 "사람이 손으로 바운딩 박스를 그려야 한다"는 뜻이 아니라 — 이미 갖고 있는 자율주행 스택의 인지(perception) 출력이나 별도 오프라인 3D 검출 모델의 결과를 NCore 포맷으로 옮겨 담기만 하면 된다는 뜻에 가깝습니다. 다만 NuRec/NCore 공식 문서가 "이 auxiliary 데이터를 자동으로 생성해준다"고 명시적으로 확인해주지는 않으므로, 큐보이드·깊이·세그멘테이션을 만드는 모델(사내 검출기든, TAO 같은 NVIDIA 도구든)은 변환 파이프라인 앞단에 **별도로 준비해둬야 하는 단계**로 보는 게 안전합니다.

---

## 10. 정리

- **NCore**는 로보틱스·자율주행 멀티센서 데이터를 위한 NVIDIA의 데이터 표현·API·도구 라이브러리이고, **V4**는 그 현재 데이터 포맷 버전입니다.
- V4의 핵심은 **컴포넌트 기반 설계** — 포즈, 카메라, 라이다, 라벨 등을 독립된 컴포넌트로 분리해 저장·버전 관리·조합할 수 있게 합니다.
- 컴포넌트는 **Zarr**(디렉터리 또는 `.zarr.itar` 아카이브)로 저장되고, 파이썬에서는 `ncore.data.v4`의 `SequenceComponentGroupsReader`/`SequenceLoaderV4`로 읽습니다.
- FTheta·OpenCV Pinhole/Fisheye 카메라 모델과 Row-Offset Spinning 라이다 모델이 GPU 가속으로 함께 제공되어, 신경 재구성에 필요한 정밀한 센서 투영을 지원합니다.
- KITTI·nuScenes·Waymo·Argoverse 2 등 여러 공개 데이터셋을 NCore V4로 변환하는 도구가 이미 마련되어 있어, NCore가 NVIDIA 전용 포맷이 아니라 공통 데이터 계층으로 쓰일 수 있게 설계되어 있습니다.
- 변환에 **꼭 필요한 건 카메라·포즈·캘리브레이션 세 가지**이고, 라이다와 큐보이드는 AV 도메인 품질을 위해 사실상 필수이며, 나머지는 있으면 좋은 보조 데이터입니다.
- 큐보이드·깊이·세그멘테이션 같은 컴포넌트는 원본 센서 로그가 아니라 **별도의 검출·추정 모델을 거친 파생 데이터**이므로, 변환 전에 이 auxiliary 데이터를 만들어내는 단계를 따로 준비해야 합니다.
