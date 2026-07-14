---
title: "py123d → NVIDIA NuRec(NCore): 자율주행 데이터를 신경 재구성 파이프라인으로"
date: 2026-07-08T00:00:00+09:00
draft: false
tags: ["autonomous", "py123d", "nvidia", "nurec", "ncore", "neural-reconstruction", "apache-arrow"]
categories: ["autonomous"]
description: "py123d로 표준화한 자율주행 데이터를 NVIDIA NuRec(NCore V4) 포맷으로 변환하는 방법과, 이 과정에서 발생하는 좌표계·카메라 모델·LiDAR 포맷 이슈를 설명합니다."
---

> 이 글은 [py123d 커스텀 파서 작성법](../py123d-dataset-conversion/)을 먼저 읽고 오면 좋습니다.
> py123d의 `BaseLogParser` 구조와 `ParsedLidar`, `ParsedCamera` 패턴을 알고 있다고 가정합니다.
> NCore V4 포맷 자체(컴포넌트 구조, Zarr 저장 방식, 센서 모델)가 처음이라면 [NCore V4 입문](../ncore-v4-for-beginners/)을 먼저 보는 걸 권합니다 — 이 글은 그 포맷을 py123d에서 변환해 넣는 방법에 집중합니다.

---

## 1. NuRec가 뭔가

**NuRec**는 NVIDIA가 개발한 신경 재구성(Neural Reconstruction) 파이프라인입니다. 자율주행 주행 로그에서 NeRF/3DGS 기반으로 주변 환경을 3D로 재구성하고, 그 결과를 시뮬레이션에 씁니다. 실제 도로를 달리며 수집한 데이터로 photorealistic한 가상 환경을 만들 수 있기 때문에, "현실을 시뮬레이터에 복사한다"는 개념으로 이해하면 됩니다. NuRec이 3D Gaussian Splatting으로 실제로 무엇을 계산하는지, novel view synthesis가 왜 어려운지는 [NuRec 입문](../nurec-neural-reconstruction-for-beginners/)에서 자세히 다룹니다.

NuRec가 입력으로 받는 포맷이 **NCore V4**입니다. NCore는 NVIDIA PhysicalAI-Autonomous-Vehicles(PAI-AV) 데이터셋의 내부 포맷이기도 하며, 하나의 주행 클립을 다음과 같은 구조로 저장합니다.

```
clips/
  <clip_id>/
    pai_<clip_id>.json                               # 시퀀스 매니페스트 (포즈 + 캘리브레이션)
    pai_<clip_id>.ncore4.zarr.itar                  # 기본 컴포넌트 (카메라, 큐보이드, 포즈)
    pai_<clip_id>.ncore4-lidar_top_360fov.zarr.itar # LiDAR 포인트 클라우드 (LAZ)
```

핵심 포맷은 세 가지입니다.

| 데이터 | 포맷 | 특징 |
|--------|------|------|
| 포즈 + 캘리브레이션 | JSON 매니페스트 | rig→world SE3 트라젝토리, 정적 센서-to-rig 포즈 |
| 카메라 이미지 | Zarr ITAR (내부 JPEG) | 시퀀스별 바이트스트림 |
| LiDAR 포인트 클라우드 | Zarr ITAR (내부 LAZ) | 스윕 단위, start/end 타임스탬프 쌍 |
| 3D 박스 라벨 | Zarr ITAR (내부 Protobuf) | `CuboidTrackObservation` |

---

## 2. py123d가 NCore를 이미 읽는다

py123d에는 NCore V4 파서(`NCoreParser`)가 내장되어 있습니다. 즉, **NCore → py123d 방향**은 이미 구현되어 있습니다. py123d를 통해 PAI-AV/NCore 데이터를 다른 데이터셋과 동일한 API로 읽을 수 있습니다.

```python
from py123d.parser.ncore.ncore_parser import NCoreParser

parser = NCoreParser(
    splits=["ncore_train"],
    ncore_data_root="/path/to/ncore_data",
)
log_parsers = parser.get_log_parsers()

# NCoreLogParser는 BaseLogParser 구현체
for lp in log_parsers:
    for frame in lp.iter_modalities_sync():
        print(frame.timestamp, len(frame.modalities))
```

이 글에서 다루는 방향은 반대입니다. nuScenes, Waymo, 사내 데이터 등 **py123d로 표준화한 데이터를 NCore V4 포맷으로 쓰는 것**, 즉 NuRec 파이프라인에 입력으로 넣는 방법입니다.

---

## 3. 변환 방향과 전략

```
원본 데이터 (nuScenes / Waymo / 사내)
         ↓ BaseLogParser → py123d Arrow IPC
    py123d 포맷
         ↓ NCore Writer (이 글의 주제)
    NCore V4 (.json + .zarr.itar)
         ↓
    NuRec 신경 재구성
```

py123d는 NCore Writer를 공식 지원하지는 않습니다. NCore V4 쓰기는 `nvidia-ncore` 패키지의 Writer API를 직접 써야 합니다. 하지만 py123d 스키마가 NCore 스키마와 대응 관계가 명확하기 때문에, 변환 레이어를 작성하기 어렵지 않습니다.

---

## 4. NCore V4 내부 구조 이해

NCore 파서 소스에서 읽어낼 수 있는 핵심 구조입니다.

### 4.1 좌표 프레임

NCore는 `rig` 프레임을 기준으로 합니다. `rig` = 리어 액슬(rear axle) 위치입니다. py123d는 ISO 8855(X=front, Y=left, Z=up) 기준의 IMU 프레임을 쓰므로, 두 프레임 사이 오프셋 변환이 필요합니다.

```python
# NCoreLogParser._open_clip_context에서
# NCore → py123d 변환 시 적용되는 오프셋
ego_state_metadata = _build_ego_state_metadata_from_manifest(
    seq_reader.generic_meta_data
)
# rear_axle_to_imu_se3 = PoseSE3.identity()  ← NCore에서는 rig = rear axle
# center_to_imu_se3    ← 매니페스트의 vehicle-bbox.centroid에서 읽음
```

py123d → NCore 변환 시에는 반대로, py123d의 ego center를 NCore의 rear axle 기준으로 역변환합니다.

### 4.2 카메라 모델

NCore는 **FTheta 카메라 모델**을 씁니다. nuScenes/AV2는 Pinhole, PAI-AV는 FTheta입니다.

```python
# NCore가 쓰는 카메라 ID (PAI-AV Hyperion 8.x 플랫폼)
PHYSICAL_AI_AV_CAMERA_ID_MAPPING = {
    "camera_front_wide_120fov":  CameraID.FTCAM_F0,
    "camera_front_tele_30fov":   CameraID.FTCAM_TELE_F0,
    "camera_cross_left_120fov":  CameraID.FTCAM_L0,
    "camera_cross_right_120fov": CameraID.FTCAM_R0,
    "camera_rear_left_70fov":    CameraID.FTCAM_L1,
    "camera_rear_right_70fov":   CameraID.FTCAM_R1,
    "camera_rear_tele_30fov":    CameraID.FTCAM_TELE_B0,
}
```

사내 데이터가 Pinhole 카메라라면 NCore에 넣기 전에 FTheta 파라미터로 캘리브레이션을 변환하거나, NCore의 Pinhole 지원 여부를 확인해야 합니다.

### 4.3 LiDAR 타임스탬프

NCore의 LiDAR는 스윕 단위로 저장되며 `(start_us, end_us)` 쌍을 키로 씁니다. py123d의 `ParsedLidar`도 `start_timestamp`/`end_timestamp`를 갖기 때문에 직접 매핑됩니다.

```python
# NCore 파서 소스에서
lidar_frame_start_ts = np.asarray(lidar_reader.frames_timestamps_us[:, 0], dtype=np.int64)
lidar_frame_end_ts   = np.asarray(lidar_reader.frames_timestamps_us[:, 1], dtype=np.int64)

# py123d → NCore 쓰기 방향
parsed_lidar = ParsedLidar(
    start_timestamp=Timestamp.from_us(start_us),
    end_timestamp=Timestamp.from_us(end_us),
    ...
)
# NCore Writer에는 iteration=end_us로 키를 건넴
```

### 4.4 3D 박스 타임스탬프 윈도우

NCore는 박스를 스윕 윈도우(start~end) 안에 속하는 것들로 묶습니다. 라벨이 스윕 시작 기준으로 정렬됩니다.

```python
# 스윕 윈도우 안에 있는 큐보이드만 골라내는 NCore 패턴
mask = (cuboid_obs_ts >= sweep_start_us) & (cuboid_obs_ts <= sweep_end_us)
```

py123d의 `BoxDetectionsSE3`는 단일 타임스탬프에 라벨을 묶기 때문에, NCore 변환 시 스윕 시작 타임스탬프와 가장 가까운 박스를 골라 윈도우 안에 넣으면 됩니다.

---

## 5. py123d → NCore 변환 코드

> **주의**: `nvidia-ncore` 패키지의 Writer API는 내부 도구 수준으로, 공개 문서화가 제한적입니다. 아래 코드는 NCore 파서 소스(`ncore_parser.py`)의 Reader API를 역으로 분석해 작성한 **구조 참고용 의사 코드**입니다. 실제 패키지 버전에 따라 클래스명과 메서드 시그니처가 다를 수 있으므로, 사용 전 `nvidia-ncore` 패키지 문서를 확인하세요.

```bash
pip install py123d[ncore] nvidia-ncore
```

### 5.1 변환 구조

py123d `BaseLogParser` → NCore V4 파일의 데이터 흐름은 다음과 같습니다.

```
iter_modalities_sync()
  ├── EgoStateSE3      → PosesComponent (rig→world 4x4 행렬, timestamp_us)
  ├── BoxDetectionsSE3 → CuboidsComponent (center, lwh, yaw, label, track_id)
  ├── ParsedLidar      → LidarSensorComponent (LAZ 바이트, start/end timestamp)
  └── ParsedCamera     → CameraSensorComponent (JPEG 바이트, timestamp)
```

```python
from pathlib import Path
from py123d.parser.base_dataset_parser import BaseLogParser
from py123d.datatypes import EgoStateSE3, BoxDetectionsSE3
from py123d.parser.base_dataset_parser import ParsedLidar, ParsedCamera

# nvidia-ncore Writer API — 버전별로 클래스명 확인 필요
from ncore.data.v4 import (
    SequenceComponentGroupsWriter,
    PosesComponent,
    CuboidsComponent,
    LidarSensorComponent,
    CameraSensorComponent,
)


def convert_log_to_ncore(log_parser: BaseLogParser, output_dir: Path, clip_id: str) -> None:
    clip_dir = output_dir / "clips" / clip_id
    clip_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = clip_dir / f"pai_{clip_id}.json"
    writer = SequenceComponentGroupsWriter(manifest_path)

    poses_writer = writer.open_component_writer(PosesComponent.Writer)
    lidar_writer = writer.open_component_writer(LidarSensorComponent.Writer)
    cuboids_writer = writer.open_component_writer(CuboidsComponent.Writer)
    cam_writers: dict = {}

    for frame in log_parser.iter_modalities_sync():
        for modality in frame.modalities:
            if isinstance(modality, EgoStateSE3):
                # py123d는 ISO 8855 center 기준, NCore는 rear axle(rig) 기준
                # center_to_imu_se3의 역변환으로 rig 포즈 계산
                center_offset = modality.metadata.center_to_imu_se3
                ego_to_global = modality.ego_to_global_se3
                rig_to_world = ego_to_global.compose(center_offset.inverse())
                poses_writer.add_dynamic_pose(
                    src_frame="rig",
                    tgt_frame="world",
                    timestamp_us=modality.timestamp.us,
                    transformation_matrix=rig_to_world.to_transformation_matrix(),
                )

            elif isinstance(modality, BoxDetectionsSE3):
                for box in modality.box_detections:
                    bbox = box.bounding_box_se3
                    cuboids_writer.add_observation(
                        timestamp_us=modality.timestamp.us,
                        class_id=box.attributes.label.name.lower(),
                        track_id=box.attributes.track_token or "0",
                        center_xyz=bbox.center.to_array(),
                        dimensions_lwh=[bbox.size.x, bbox.size.y, bbox.size.z],
                        yaw=bbox.yaw,
                        reference_frame_id="world",
                    )

            elif isinstance(modality, ParsedLidar):
                # ParsedLidar는 경로 포인터 — LAZ 파일을 직접 읽어서 넘김
                laz_path = modality._dataset_root / modality._relative_path
                with open(laz_path, "rb") as f:
                    laz_bytes = f.read()
                lidar_writer.add_frame(
                    start_timestamp_us=modality.start_timestamp.us,
                    end_timestamp_us=modality.end_timestamp.us,
                    data=laz_bytes,
                )

            elif isinstance(modality, ParsedCamera):
                cam_name = modality.metadata.camera_name
                if cam_name not in cam_writers:
                    cam_writers[cam_name] = writer.open_component_writer(
                        CameraSensorComponent.Writer, sensor_id=cam_name
                    )
                # JPEG 경로 또는 바이트스트링으로 넘어옴
                if modality.has_file_path:
                    jpeg_path = modality._dataset_root / modality._relative_path
                    with open(jpeg_path, "rb") as f:
                        jpeg_bytes = f.read()
                else:
                    jpeg_bytes = modality._byte_string
                cam_writers[cam_name].add_frame(
                    timestamp_us=modality.timestamp.us,
                    encoded_image_data=jpeg_bytes,
                )

    writer.finalize()
```

### 5.2 전체 데이터셋 일괄 변환

```python
from py123d.parser.nuscenes.nuscenes_parser import NuScenesParser

def convert_dataset_to_ncore(
    dataset_parser,
    output_dir: Path,
) -> None:
    log_parsers = dataset_parser.get_log_parsers()
    print(f"총 {len(log_parsers)}개 로그 변환 시작")

    for lp in log_parsers:
        meta = lp.get_log_metadata()
        clip_id = meta.log_name
        print(f"  변환 중: {clip_id}")
        try:
            convert_log_to_ncore(lp, output_dir, clip_id)
        except Exception as e:
            print(f"  오류 ({clip_id}): {e}")
            continue

    print("변환 완료")


# nuScenes → NCore
nuscenes_parser = NuScenesParser(
    splits=["nuscenes_val"],
    nuscenes_data_root="/data/nuscenes",
)
convert_dataset_to_ncore(nuscenes_parser, Path("/output/ncore"))

# 사내 데이터 → NCore (커스텀 파서 사용)
from my_dataset.my_dataset_parser import MyDatasetParser
my_parser = MyDatasetParser(data_root="/data/my_fleet", splits=["train"])
convert_dataset_to_ncore(my_parser, Path("/output/ncore"))
```

---

## 6. 주요 변환 이슈

### 6.1 카메라 모델: Pinhole → FTheta

NuRec는 FTheta 모델을 가정합니다. nuScenes와 Waymo는 Pinhole 카메라입니다. **Pinhole 파라미터를 FTheta로 변환할 수는 없습니다.** 수학적으로 다른 모델이기 때문입니다.

실용적인 접근은 두 가지입니다.

- **광각 카메라를 FTheta로 교체 캘리브레이션**: 실제 카메라가 FTheta 특성을 가지는 경우, FTheta 캘리브레이션 도구로 파라미터를 새로 추출합니다.
- **NCore Pinhole 지원 확인**: 최신 NCore 버전은 Pinhole도 지원할 수 있습니다. `nvidia-ncore` 패키지 문서를 확인하세요.

사내 수집 데이터라면 처음부터 FTheta 캘리브레이션을 하는 것이 NuRec 파이프라인에 가장 자연스럽습니다.

### 6.2 LiDAR: PCD → LAZ

py123d가 LiDAR를 numpy로 노출하면, NCore에 넣기 위해 다시 LAZ로 인코딩해야 합니다. 압축 해제 → 재압축이므로 성능 비용이 있습니다. 대용량 플릿 데이터라면 원본 LiDAR를 LAZ로 미리 변환해두는 편이 낫습니다.

```bash
# libLAS로 일괄 변환 (PCD → LAZ)
for f in lidar/*.pcd; do
    las2las --input "$f" --output "${f%.pcd}.laz"
done
```

py123d로 변환할 때 LAZ 경로를 `ParsedLidar`에 넘기면, NCore 변환 시 재압축 없이 LAZ 파일을 그대로 복사할 수 있습니다.

### 6.3 라벨 클래스 매핑

nuScenes의 `car`, Waymo의 `TYPE_VEHICLE`, 사내 데이터의 `sedan`은 모두 다른 이름이지만 같은 물체입니다. NCore는 PAI-AV 12-class 체계를 씁니다.

```python
# NCore / PAI-AV 클래스 체계
PHYSICAL_AI_AV_LABEL_CLASS_MAPPING = {
    "automobile":        PhysicalAIAVBoxDetectionLabel.AUTOMOBILE,
    "heavy_truck":       PhysicalAIAVBoxDetectionLabel.HEAVY_TRUCK,
    "bus":               PhysicalAIAVBoxDetectionLabel.BUS,
    "train_or_tram_car": PhysicalAIAVBoxDetectionLabel.TRAIN_OR_TRAM_CAR,
    "trolley_bus":       PhysicalAIAVBoxDetectionLabel.TROLLEY_BUS,
    "other_vehicle":     PhysicalAIAVBoxDetectionLabel.OTHER_VEHICLE,
    "trailer":           PhysicalAIAVBoxDetectionLabel.TRAILER,
    "person":            PhysicalAIAVBoxDetectionLabel.PERSON,
    "stroller":          PhysicalAIAVBoxDetectionLabel.STROLLER,
    "rider":             PhysicalAIAVBoxDetectionLabel.RIDER,
    "animal":            PhysicalAIAVBoxDetectionLabel.ANIMAL,
    "protruding_object": PhysicalAIAVBoxDetectionLabel.PROTRUDING_OBJECT,
}
```

py123d는 각 데이터셋의 라벨을 데이터셋별 enum으로 저장합니다. NCore 변환 전에 소스 데이터셋 라벨을 PAI-AV 체계로 매핑하는 변환 테이블을 작성해야 합니다.

```python
# nuScenes → PAI-AV 라벨 매핑 예시
NUSCENES_TO_PAIAV = {
    "car":            "automobile",
    "truck":          "heavy_truck",
    "bus":            "bus",
    "motorcycle":     "rider",
    "bicycle":        "rider",
    "pedestrian":     "person",
    "trailer":        "trailer",
    "construction_vehicle": "other_vehicle",
    "traffic_cone":   "protruding_object",
    "barrier":        "protruding_object",
}
```

---

## 7. 전체 파이프라인

지금까지 나온 글들을 종합하면 전체 파이프라인이 완성됩니다.

```
원본 데이터 (nuScenes / Waymo / 사내)
         ↓  [1] BaseLogParser (데이터셋마다 1회)
    py123d Arrow IPC
         ├──→ [2] FiftyOne      데이터 큐레이션 (엣지 케이스 선별)
         ├──→ [3] Rerun         3D 시각화 (타임라인 기반)
         ├──→ [4] DORA          클로즈 루프 회귀 테스트
         └──→ [5] NCore V4      NuRec 신경 재구성 → 시뮬레이터 환경 생성
```

사내 데이터가 한 번 py123d 포맷으로 변환되면, 이후의 모든 다운스트림 파이프라인은 데이터셋과 무관하게 재사용됩니다. NuRec로 신경 재구성한 가상 환경에서 DORA 클로즈 루프 테스트를 돌리고, Rerun으로 결과를 시각화하는 흐름이 하나의 파이프라인 안에서 Arrow 포맷으로 연결됩니다.

---

## 8. 정리

| 항목 | py123d | NCore V4 |
|------|--------|----------|
| 포즈 기준 | ISO 8855 IMU (center) | rig (rear axle) |
| 카메라 모델 | Pinhole / FisheyeMEI / FTheta | FTheta (Hyperion 플랫폼) |
| LiDAR 포맷 | LAZ 경로 포인터 / Arrow IPC | LAZ (Zarr ITAR) |
| 박스 타임스탬프 | 단일 타임스탬프 | 스윕 윈도우 (start~end) |
| 라벨 체계 | 데이터셋별 enum | PAI-AV 12-class |

NCore V4 변환에서 가장 손이 많이 가는 부분은 카메라 모델 호환성과 라벨 매핑입니다. 처음부터 FTheta 카메라로 수집하고 PAI-AV 라벨 체계를 사내 기준으로 삼으면, 이후 NuRec 파이프라인 연동이 훨씬 수월해집니다.
