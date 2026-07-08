---
title: "py123d 커스텀 파서 작성법: nuScenes·Waymo·AV2 변환 코드로 배우는 BaseLogParser"
date: 2026-07-08T00:00:00+09:00
draft: false
tags: ["autonomous", "py123d", "nuscenes", "waymo", "argoverse", "dataset", "apache-arrow"]
categories: ["autonomous"]
description: "nuScenes, Waymo, Argoverse 2를 py123d 스키마로 변환하는 실제 소스 코드를 분석하고, 이를 참고해 사내 데이터셋용 커스텀 파서를 작성하는 방법을 설명합니다."
---

> 이 글은 [py123d 입문](../py123d-for-beginners/)을 먼저 읽고 오면 더 수월합니다.
> py123d의 기본 개념(독립 타임스탬프 스트림, Arrow IPC, ISO 8855 좌표계)을 알고 있다고 가정합니다.

---

## 1. 왜 파서 코드를 직접 봐야 하나

py123d CLI로 공개 데이터셋을 변환하는 건 한 줄이면 됩니다.

```bash
py123d-conversion dataset=nuscenes dataset.parser.splits='[nuscenes_train]'
```

그런데 사내에서 직접 수집한 데이터셋은 이 명령어로 변환할 수 없습니다. py123d가 모르는 포맷이니까요. 사내 데이터를 변환하려면 **`BaseLogParser`를 직접 구현**해야 합니다.

이 글의 목표는 두 가지입니다.

1. nuScenes, Waymo, Argoverse 2 파서의 실제 코드를 읽으며 패턴을 이해한다.
2. 그 패턴을 그대로 따라 사내 데이터셋용 파서를 작성한다.

---

## 2. 변환 아키텍처 한눈에 보기

py123d의 변환 파이프라인은 두 계층으로 나뉩니다.

```
BaseDatasetParser          ← 데이터셋 전체를 관장
    └── get_log_parsers()  ← 로그(씬) 목록을 반환

BaseLogParser              ← 로그 하나를 담당
    ├── get_log_metadata() ← 로그 메타데이터
    ├── iter_modalities_sync()  ← 프레임 단위 동기화 이터레이터
    └── iter_modalities_async() ← 모달리티별 네이티브 레이트 이터레이터
```

`iter_modalities_sync`는 라이다 타임스탬프를 기준으로 모든 센서를 한 프레임에 묶어서 냅니다. `iter_modalities_async`는 카메라는 카메라 레이트(예: 12Hz), 라이다는 라이다 레이트(예: 20Hz)로 각각 독립적으로 냅니다. py123d는 내부에서 이 스트림들을 Arrow에 타임스탬프 인덱스로 저장해두고, 읽을 때 nearest 조회로 동기화합니다.

`BaseDatasetParser`에서 `get_map_parsers()`도 구현할 수 있지만, HD Map이 없는 데이터셋은 빈 리스트를 반환하면 됩니다.

---

## 3. Argoverse 2: 가장 단순한 구조

AV2 파서부터 봅니다. 포맷이 Parquet/Feather 기반이라 읽기 쉽고, 폴더 구조가 직관적입니다.

### 3.1 디렉터리 구조

```
<av2_sensor_root>/
  train/
    <log_uuid>/
      city_SE3_egovehicle.feather   # 이고 포즈 타임라인
      annotations.feather           # 3D 바운딩 박스 라벨
      calibration/
        egovehicle_SE3_sensor.feather  # 센서 캘리브레이션
      sensors/
        lidar/
          <timestamp_ns>.feather    # LiDAR 포인트 클라우드
        cameras/
          ring_front_center/
            <timestamp_ns>.jpg
          ...
```

### 3.2 `Av2SensorLogParser.iter_modalities_sync`

```python
def iter_modalities_sync(self) -> Iterator[ModalitiesSync]:
    # 1. 메타데이터 로드 (한 번만)
    ego_state_se3_metadata = AV2_SENSOR_EGO_STATE_SE3_METADATA
    box_detections_se3_metadata = AV2_SENSOR_BOX_DETECTIONS_SE3_METADATA
    pinhole_camera_metadatas = _get_av2_pinhole_camera_metadatas(self._source_log_path)
    lidar_merged_metadata = _get_av2_lidar_merged_metadata(self._source_log_path)

    # 2. 타임스탬프 기준으로 동기화 테이블 빌드
    sensor_df = build_sensor_dataframe(self._source_log_path)
    synchronization_df = build_synchronization_dataframe(...)
    lidar_timestamps_ns = np.sort([...])  # 라이다 타임스탬프를 기준축으로

    city_se3_egovehicle_df = pd.read_feather("city_SE3_egovehicle.feather")
    annotations_df = pd.read_feather("annotations.feather")

    # 3. 라이다 타임스탬프마다 한 프레임씩 yield
    for lidar_timestamp_ns in lidar_timestamps_ns:
        timestamp = Timestamp.from_ns(int(lidar_timestamp_ns))

        ego_state_se3 = _extract_av2_sensor_ego_state(city_se3_egovehicle_df, lidar_timestamp_ns, ...)
        box_detections_se3 = _extract_av2_sensor_box_detections(annotations_df, lidar_timestamp_ns, ...)
        parsed_cameras = _extract_av2_sensor_pinhole_cameras(lidar_timestamp_ns, ...)
        parsed_lidar = _extract_av2_sensor_lidar(self._source_log_path, lidar_timestamp_ns, ...)

        yield ModalitiesSync(
            timestamp=timestamp,
            modalities=[ego_state_se3, box_detections_se3, parsed_lidar, *parsed_cameras],
        )
```

핵심 패턴: **라이다 타임스탬프를 기준축으로 삼고, 그 시각에 가장 가까운 카메라 이미지를 찾아 하나의 `ModalitiesSync`로 묶는다.**

### 3.3 `iter_modalities_async`

```python
def iter_modalities_async(self) -> Iterator[BaseModality]:
    # 각 모달리티를 네이티브 레이트로 독립 yield
    yield from self._iter_ego_states_se3(ego_state_se3_metadata)
    yield from self._iter_box_detections_se3(box_detections_se3_metadata)
    yield from self._iter_lidar_merged(lidar_merged_metadata)
    for pinhole_camera_metadata in pinhole_camera_metadatas.values():
        yield from self._iter_pinhole_camera(pinhole_camera_metadata)
```

이 메서드에서는 순서가 중요하지 않습니다. py123d 내부 writer가 타임스탬프를 보고 Arrow에 알아서 정렬해서 씁니다.

---

## 4. nuScenes: 2Hz 키프레임 + 20Hz 스윕

nuScenes는 구조가 더 복잡합니다. **키프레임(2Hz)에만 라벨이 있고, 라이다는 20Hz로 찍습니다.** py123d는 이 두 모드를 모두 지원합니다.

### 4.1 NuScenesLogParser 구조

```python
class NuScenesLogParser(BaseLogParser):
    def get_log_metadata(self) -> LogMetadata:
        return LogMetadata(
            dataset="nuscenes",
            split=self._split,
            log_name=self._scene_name,
            location=self._location,
        )
```

### 4.2 키프레임 모드 (`iter_modalities_sync`)

```python
def _iter_sync_keyframes(self) -> Iterator[ModalitiesSync]:
    nusc = self._get_or_load_nusc()  # NuScenes SDK 객체 (lazy load)

    scene = nusc.get("scene", self._scene_token)
    sample_token = scene["first_sample_token"]

    while sample_token:
        sample = nusc.get("sample", sample_token)
        timestamp = Timestamp.from_us(sample["timestamp"])

        ego_state = extract_ego_state_from_sample(nusc, sample, can_bus, ego_metadata)
        box_detections = extract_nuscenes_box_detections(nusc, sample, box_detections_metadata)
        parsed_cameras = extract_nuscenes_cameras(nusc, sample, ...)
        parsed_lidar = extract_nuscenes_lidar(nusc, sample, ...)
        parsed_radar = extract_nuscenes_radar(nusc, sample, ...)

        modalities = [ego_state, box_detections, *parsed_cameras]
        if parsed_lidar is not None:
            modalities.append(parsed_lidar)
        if parsed_radar is not None:
            modalities.append(parsed_radar)

        yield ModalitiesSync(timestamp=timestamp, modalities=modalities)
        sample_token = sample["next"]  # 연결 리스트 순회
```

nuScenes는 샘플이 연결 리스트로 연결되어 있습니다. `sample["next"]`가 빈 문자열이면 마지막 샘플입니다.

### 4.3 10Hz 보간 모드

보간 모드(`nuscenes-interpolated_*` 스플릿)에서는 라이다 스윕(20Hz)을 기준으로 두 키프레임 사이를 SLERP로 보간합니다.

```python
# 보간 로직 핵심
prev_kf, next_kf = find_surrounding_keyframes(sweep["timestamp"], keyframe_samples)
delta = next_kf["timestamp"] - prev_kf["timestamp"]
t = (sweep["timestamp"] - prev_kf["timestamp"]) / delta

box_detections = interpolate_box_detections(
    keyframe_detections[prev_kf["token"]],
    keyframe_detections[next_kf["token"]],
    t,          # 0~1 사이의 보간 비율
    timestamp,  # 현재 스윕 타임스탬프
)
```

### 4.4 Async 모드: 모달리티별 네이티브 레이트

```python
def iter_modalities_async(self) -> Iterator[BaseModality]:
    try:
        yield from self._iter_ego_states_se3(ego_metadata)      # ~20Hz (라이다 스윕 기준)
        yield from self._iter_box_detections_se3(box_metadata)  # 2Hz (키프레임)
        yield from self._iter_lidars(lidar_metadata)             # ~20Hz
        yield from self._iter_radars(radar_metadata)             # ~13Hz
        for camera_type, camera_metadata in pinhole_cameras_metadata.items():
            yield from self._iter_pinhole_cameras(...)           # ~12Hz
    finally:
        self._release_nusc()  # NuScenes SDK 객체 해제 (메모리 절약)
```

`finally` 블록에서 NuScenes SDK 객체를 명시적으로 해제합니다. nuScenes는 초기화할 때 JSON 메타데이터를 전부 메모리에 올리기 때문에 파서 하나당 수백 MB를 씁니다. 병렬 변환 시 메모리 폭발을 막기 위한 패턴입니다.

### 4.5 Pickle 안전성

```python
def __getstate__(self) -> Dict[str, Any]:
    """NuScenes SDK 객체를 직렬화에서 제외"""
    state = self.__dict__.copy()
    state["_shared_nusc"] = None
    state["_owns_nusc"] = False
    return state
```

py123d는 내부적으로 Ray나 ProcessPool로 로그 파서를 worker에 분배합니다. NuScenes SDK는 pickle이 안 되므로 `__getstate__`에서 제외하고, worker에서 lazy하게 다시 로드합니다.

---

## 5. Waymo: Protobuf 파일 파싱

Waymo는 TFRecord + Protobuf 포맷입니다. py123d는 `waymo-open-dataset` 패키지 없이도 proto 파일을 직접 파싱합니다.

```python
# 라이다 타임스탬프는 프레임 시작 시각 (스윕 중간이 아님)
WOD_PERCEPTION_LIDAR_SWEEP_DURATION_US = 100_000  # 100ms = 10Hz
WOD_PERCEPTION_LIDAR_HALF_SWEEP_US = 50_000       # 포즈는 스윕 중간 기준
```

Waymo 라이다는 10Hz이고 한 스윕이 100ms 걸립니다. `frame.timestamp_micros`는 스윕 시작 시각이고, `frame.pose`는 스윕 중간(~50ms 후) 시각의 포즈입니다. py123d는 이 차이를 보정해서 저장합니다.

---

## 6. 패턴 정리: 세 파서의 공통점

세 파서를 보면 같은 패턴이 반복됩니다.

| 단계 | 하는 일 |
|------|---------|
| **`__init__`** | 경로와 스플릿만 저장. 실제 I/O는 하지 않음 |
| **`get_log_metadata`** | `LogMetadata(dataset=..., split=..., log_name=..., location=...)` 반환 |
| **`iter_modalities_sync`** | 라이다 타임스탬프를 기준축으로 한 프레임씩 `ModalitiesSync` yield |
| **`iter_modalities_async`** | 모달리티별로 `_iter_xxx` 메서드를 순차 yield |
| **`ParsedLidar`** | LiDAR는 경로 포인터만 넘김. 실제 로드는 writer가 나중에 함 |
| **`ParsedCamera`** | 카메라도 경로 포인터(JPEG) 또는 바이트스트링 |
| **Pickle 안전** | 무거운 SDK 객체는 `__getstate__`에서 제외, lazy reload |

---

## 7. 사내 데이터셋 커스텀 파서 작성

이제 이 패턴을 그대로 따라서 사내 데이터셋 파서를 작성합니다. 사내 데이터셋 구조를 다음과 같다고 가정합니다.

```
<data_root>/
  logs/
    <log_id>/
      ego_poses.json          # [{timestamp_us, tx, ty, tz, qx, qy, qz, qw}, ...]
      labels.json             # [{timestamp_us, boxes: [{cx, cy, cz, l, w, h, yaw, label}]}, ...]
      lidar/
        <timestamp_us>.pcd    # 또는 .laz
      camera_front/
        <timestamp_us>.jpg
      camera_left/
        <timestamp_us>.jpg
      camera_right/
        <timestamp_us>.jpg
      calib.json              # 센서 캘리브레이션
```

### 7.1 상수 정의

```python
# my_dataset/constants.py
from py123d.datatypes import (
    EgoStateSE3Metadata,
    BoxDetectionsSE3Metadata,
    LidarID,
    LidarMergedMetadata,
    CameraID,
    PinholeCameraMetadata,
    PinholeIntrinsics,
    PinholeDistortion,
)

MY_DATASET_EGO_STATE_METADATA = EgoStateSE3Metadata(
    dataset="my-dataset",
    coordinate_frame="iso8855",  # ISO 8855: X=front, Y=left, Z=up
)

MY_DATASET_BOX_DETECTIONS_METADATA = BoxDetectionsSE3Metadata(
    dataset="my-dataset",
    coordinate_frame="iso8855",
)

# 라이다 ID (여러 라이다가 있으면 각각 등록)
MY_LIDAR_ID = LidarID("top_lidar")

MY_LIDAR_METADATA = LidarMergedMetadata(
    dataset="my-dataset",
    lidar_ids=[MY_LIDAR_ID],
)

# 카메라 ID
CAM_FRONT = CameraID("camera_front")
CAM_LEFT = CameraID("camera_left")
CAM_RIGHT = CameraID("camera_right")
```

### 7.2 `BaseDatasetParser` 구현

```python
# my_dataset/my_dataset_parser.py
from pathlib import Path
from typing import List
from py123d.parser.base_dataset_parser import BaseDatasetParser, BaseLogParser, BaseMapParser

class MyDatasetParser(BaseDatasetParser):
    def __init__(self, data_root: str, splits: List[str]) -> None:
        self._data_root = Path(data_root)
        self._splits = splits

    def get_log_parsers(self) -> List["MyDatasetLogParser"]:
        log_parsers = []
        for split in self._splits:
            split_dir = self._data_root / "logs"
            for log_dir in sorted(split_dir.iterdir()):
                if log_dir.is_dir():
                    log_parsers.append(
                        MyDatasetLogParser(
                            log_dir=log_dir,
                            split=split,
                        )
                    )
        return log_parsers

    def get_map_parsers(self) -> List[BaseMapParser]:
        return []  # HD Map 없으면 빈 리스트
```

### 7.3 `BaseLogParser` 구현

```python
import json
import numpy as np
from pathlib import Path
from typing import Dict, Iterator, List, Optional
from py123d.datatypes import (
    EgoStateSE3, BoxDetectionsSE3, BoxDetectionSE3, BoxDetectionAttributes,
    Timestamp,
)
from py123d.geometry import PoseSE3, BoundingBoxSE3, Vector3D
from py123d.geometry.utils.rotation_utils import get_rotation_matrix_from_quaternion
from py123d.parser.base_dataset_parser import (
    BaseLogParser, ModalitiesSync, ParsedCamera, ParsedLidar,
)
from .constants import (
    MY_DATASET_EGO_STATE_METADATA, MY_DATASET_BOX_DETECTIONS_METADATA,
    MY_LIDAR_METADATA,
    CAM_FRONT, CAM_LEFT, CAM_RIGHT,
)


class MyDatasetLogParser(BaseLogParser):
    def __init__(self, log_dir: Path, split: str) -> None:
        # __init__에는 경로만 저장. 실제 I/O 하지 않음
        self._log_dir = log_dir
        self._split = split

    def get_log_metadata(self):
        from py123d.datatypes import LogMetadata
        return LogMetadata(
            dataset="my-dataset",
            split=self._split,
            log_name=self._log_dir.name,
            location="unknown",
        )

    def iter_modalities_sync(self) -> Iterator[ModalitiesSync]:
        # 1. 라이다 파일 타임스탬프 목록을 기준축으로
        lidar_dir = self._log_dir / "lidar"
        lidar_timestamps_us = sorted([
            int(f.stem) for f in lidar_dir.glob("*.laz")
        ])

        # 2. 보조 데이터 로드 (iter 시작 시 1회만)
        ego_pose_list = self._load_ego_poses()
        ego_pose_ts = np.array([p["timestamp_us"] for p in ego_pose_list], dtype=np.int64)
        labels = {lb["timestamp_us"]: lb["boxes"] for lb in self._load_labels()}
        calib = self._load_calib()

        for ts_us in lidar_timestamps_us:
            timestamp = Timestamp.from_us(ts_us)

            # 가장 가까운 ego pose 찾기
            nearest_idx = int(np.argmin(np.abs(ego_pose_ts - ts_us)))
            ego_pose_dict = ego_pose_list[nearest_idx]
            ego_state = self._make_ego_state(ego_pose_dict, timestamp)
            ego_to_global = ego_state.ego_to_global_se3  # PoseSE3

            # 3D box detections
            box_detections = self._make_box_detections(
                labels.get(ts_us, []), timestamp
            )

            # 카메라: 가장 가까운 타임스탬프 이미지 찾기
            parsed_cameras = self._find_nearest_cameras(ts_us, calib, ego_to_global)

            # 라이다: 경로 포인터만 (실제 로드는 writer가 함)
            parsed_lidar = ParsedLidar(
                metadata=MY_LIDAR_METADATA,
                start_timestamp=timestamp,
                end_timestamp=Timestamp.from_us(ts_us + 100_000),  # 100ms sweep
                dataset_root=self._log_dir,
                relative_path=f"lidar/{ts_us}.laz",
            )

            yield ModalitiesSync(
                timestamp=timestamp,
                modalities=[ego_state, box_detections, parsed_lidar, *parsed_cameras],
            )

    # ------------------------------------------------------------------
    # 헬퍼
    # ------------------------------------------------------------------

    def _load_ego_poses(self) -> List[dict]:
        with open(self._log_dir / "ego_poses.json") as f:
            return json.load(f)

    def _load_labels(self) -> List[dict]:
        label_path = self._log_dir / "labels.json"
        if not label_path.exists():
            return []
        with open(label_path) as f:
            return json.load(f)

    def _load_calib(self) -> dict:
        with open(self._log_dir / "calib.json") as f:
            return json.load(f)

    def _make_ego_state(self, pose_dict: dict, timestamp: Timestamp) -> EgoStateSE3:
        tx, ty, tz = pose_dict["tx"], pose_dict["ty"], pose_dict["tz"]
        qx, qy, qz, qw = pose_dict["qx"], pose_dict["qy"], pose_dict["qz"], pose_dict["qw"]

        # PoseSE3는 [qw, qx, qy, qz, tx, ty, tz] 순서를 기대함
        rotation = get_rotation_matrix_from_quaternion(np.array([qw, qx, qy, qz]))
        ego_to_global = PoseSE3(rotation=rotation, translation=np.array([tx, ty, tz]))

        return EgoStateSE3.from_imu(
            imu_se3=ego_to_global,
            metadata=MY_DATASET_EGO_STATE_METADATA,
            dynamic_state_se3=None,
            timestamp=timestamp,
        )

    def _make_box_detections(self, boxes: List[dict], timestamp: Timestamp) -> BoxDetectionsSE3:
        detections = []
        for b in boxes:
            center = Vector3D(x=b["cx"], y=b["cy"], z=b["cz"])
            size = Vector3D(x=b["l"], y=b["w"], z=b["h"])

            bbox = BoundingBoxSE3(
                center=center,
                size=size,
                yaw=b["yaw"],
            )
            detections.append(
                BoxDetectionSE3(
                    bounding_box=bbox,
                    attributes=BoxDetectionAttributes(label=b["label"]),
                )
            )
        return BoxDetectionsSE3(
            box_detections=detections,
            timestamp=timestamp,
            metadata=MY_DATASET_BOX_DETECTIONS_METADATA,
        )

    def _find_nearest_cameras(
        self,
        target_ts_us: int,
        calib: dict,
        ego_to_global: PoseSE3,
    ) -> List[ParsedCamera]:
        """각 카메라 폴더에서 target_ts_us에 가장 가까운 이미지를 찾아 ParsedCamera 반환"""
        from py123d.geometry.transform.transform_se3 import rel_to_abs_se3
        from py123d.datatypes.sensors.pinhole_camera import PinholeIntrinsics, PinholeDistortion

        parsed_cameras = []
        for cam_id, cam_name in [
            (CAM_FRONT, "camera_front"),
            (CAM_LEFT, "camera_left"),
            (CAM_RIGHT, "camera_right"),
        ]:
            cam_dir = self._log_dir / cam_name
            if not cam_dir.exists():
                continue

            cam_timestamps = sorted([int(f.stem) for f in cam_dir.glob("*.jpg")])
            if not cam_timestamps:
                continue
            nearest_ts = min(cam_timestamps, key=lambda t: abs(t - target_ts_us))

            # 카메라 포즈: cam_to_ego는 정적 캘리브레이션, ego_to_global은 해당 라이다 프레임 포즈
            cam_calib = calib[cam_name]
            cam_to_ego = PoseSE3(
                rotation=get_rotation_matrix_from_quaternion(
                    np.array(cam_calib["rotation_quat"])  # [qw, qx, qy, qz]
                ),
                translation=np.array(cam_calib["translation"]),
            )
            cam_to_global = rel_to_abs_se3(origin=ego_to_global, pose_se3=cam_to_ego)

            intr = cam_calib["intrinsics"]
            camera_metadata = PinholeCameraMetadata(
                camera_name=cam_name,
                camera_id=cam_id,
                intrinsics=PinholeIntrinsics(
                    fx=intr["fx"], fy=intr["fy"],
                    cx=intr["cx"], cy=intr["cy"],
                ),
                distortion=PinholeDistortion(k1=0.0, k2=0.0, p1=0.0, p2=0.0),
                width=intr["width"],
                height=intr["height"],
                camera_to_imu_se3=cam_to_ego,
            )

            parsed_cameras.append(
                ParsedCamera(
                    metadata=camera_metadata,
                    timestamp=Timestamp.from_us(nearest_ts),
                    camera_to_global_se3=cam_to_global,
                    dataset_root=self._log_dir,
                    relative_path=f"{cam_name}/{nearest_ts}.jpg",
                )
            )
        return parsed_cameras
```

### 7.4 변환 실행

```python
from my_dataset.my_dataset_parser import MyDatasetParser
from py123d.script.run_conversion import run_conversion

parser = MyDatasetParser(
    data_root="/path/to/my_data",
    splits=["train"],
)

run_conversion(
    dataset_parser=parser,
    output_root="/path/to/output",
    num_workers=8,
)
```

변환이 끝나면 `/path/to/output` 아래에 Arrow IPC 파일이 생깁니다. 이후에는 다른 py123d 데이터셋과 동일한 API로 접근할 수 있습니다.

```python
from py123d import SceneFilter, get_filtered_scenes

# 사내 데이터와 nuScenes를 함께 필터링
scene_filter = SceneFilter(
    split_names=["train", "nuscenes_val"],
)
scenes = get_filtered_scenes(scene_filter)
```

---

## 8. 자주 마주치는 문제

### 좌표계 변환

사내 데이터가 ISO 8855(X=front, Y=left, Z=up)가 아닌 경우, py123d 스키마에 넣기 전에 변환해야 합니다. Waymo 파서가 이 변환을 명시적으로 처리합니다.

```python
from py123d.parser.utils.sensor_utils.camera_conventions import (
    CameraConvention, convert_camera_convention
)

# ROS 카메라 컨벤션(Z=front) → OpenCV 컨벤션(Z=front, Y=down)으로 변환
rotation_ros_to_opencv = convert_camera_convention(
    from_convention=CameraConvention.ROS,
    to_convention=CameraConvention.OPENCV,
)
```

### PCD → LiDAR 처리

py123d는 PCD 파일을 네이티브로 지원하지 않습니다. 두 가지 방법이 있습니다.

- **LAZ로 변환 후 경로 포인터**: `ParsedLidar`에 `.laz` 경로를 넘김
- **읽어서 numpy로 넘기기**: `ParsedLidar` 대신 커스텀 모달리티 구현

운영 편의를 위해서는 변환 전처리 단계에서 PCD를 LAZ로 변환해두는 것이 낫습니다.

```bash
# libLAS로 PCD → LAZ 일괄 변환
for f in lidar/*.pcd; do
    las2las --input "$f" --output "${f%.pcd}.laz"
done
```

### Pickle 안전성

무거운 SDK 객체(예: nuScenes SDK, TFRecord reader)를 파서에서 멤버 변수로 들고 있으면 multiprocessing에서 문제가 생깁니다. nuScenes 파서처럼 `__getstate__`로 제외하고 lazy load 패턴을 씁니다.

```python
def __getstate__(self):
    state = self.__dict__.copy()
    state["_heavy_sdk_object"] = None
    return state

def _get_sdk(self):
    if self._heavy_sdk_object is None:
        self._heavy_sdk_object = HeavySDK(self._data_root)
    return self._heavy_sdk_object
```

---

## 9. 정리

| 단계 | 핵심 |
|------|------|
| `BaseDatasetParser.get_log_parsers()` | 로그 디렉터리를 순회해 `BaseLogParser` 목록 반환 |
| `BaseLogParser.get_log_metadata()` | `LogMetadata(dataset, split, log_name, location)` |
| `iter_modalities_sync()` | 라이다 타임스탬프 기준, `ModalitiesSync` yield |
| `iter_modalities_async()` | 모달리티별 네이티브 레이트로 독립 yield |
| `ParsedLidar` / `ParsedCamera` | 경로 포인터만 넘김, 실제 로드는 writer에 위임 |
| 좌표계 | ISO 8855 / OpenCV로 변환하고 넘김 |
| Pickle 안전 | 무거운 객체는 `__getstate__` 제외, lazy reload |

nuScenes, Waymo, Argoverse 2 파서가 모두 이 패턴을 따릅니다. 사내 파서도 같은 구조로 작성하면 변환 이후의 모든 다운스트림 파이프라인 — FiftyOne 큐레이션, Rerun 시각화, DORA 기반 클로즈 루프 테스트, [NuRec 신경 재구성](../py123d-to-nurec/) — 을 건드리지 않고 사내 데이터를 그대로 연결할 수 있습니다.
