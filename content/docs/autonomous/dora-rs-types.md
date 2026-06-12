---
title: "DORA 타입 시스템"
date: 2026-06-13T00:00:00+09:00
draft: false
tags: ["robotics", "dora", "types", "arrow"]
categories: ["autonomous"]
description: "DORA의 타입 URN 체계, 내장 타입 카탈로그, 타입 호환성 규칙, 정적/런타임 검증 방법을 정리합니다."
---

> 이 글은 [DORA 타입 시스템 문서](https://dora-rs.ai/dora/concepts/types.html)를 참고해 작성했습니다.

---

## 1. 타입 URN 형식

DORA는 포트 타입을 URN으로 표현합니다.

```
std/<카테고리>/v<버전>/<타입명>
```

예시:

```
std/core/v1/Float32
std/media/v1/Image
std/vision/v1/BoundingBox
```

타입 어노테이션은 선택 사항입니다. 달지 않은 포트는 동적 타입으로 동작합니다.

---

## 2. 내장 타입 카탈로그

### 2.1 기본 타입 (`std/core/v1`)

| 타입 | 설명 |
|------|------|
| `Float32`, `Float64` | 부동소수점 |
| `Int32`, `Int64` | 정수 |
| `UInt8`, `UInt32`, `UInt64` | 부호 없는 정수 |
| `String` | 문자열 |
| `Bytes` | 임의 바이트 (모든 타입과 호환되는 범용 싱크) |
| `Bool` | 불리언 |

### 2.2 수학 타입 (`std/math/v1`)

| 타입 | 설명 |
|------|------|
| `Vector3` | 3차원 벡터 |
| `Quaternion` | 회전 표현 |
| `Pose` | 위치 + 자세 |
| `Transform` | 좌표 변환 |

### 2.3 제어 타입 (`std/control/v1`)

| 타입 | 설명 |
|------|------|
| `Twist` | 선속도 + 각속도 |
| `JointState` | 관절 상태 |
| `Odometry` | 주행 거리계 |

### 2.4 미디어 타입 (`std/media/v1`)

| 타입 | 설명 |
|------|------|
| `Image` | 이미지 프레임 |
| `CompressedImage` | 압축 이미지 |
| `PointCloud` | 포인트 클라우드 |
| `AudioFrame` | 오디오 프레임 |

### 2.5 비전 타입 (`std/vision/v1`)

| 타입 | 설명 |
|------|------|
| `BoundingBox` | 바운딩 박스 |
| `Detection` | 객체 감지 결과 |
| `Segmentation` | 세그멘테이션 마스크 |

---

## 3. 파라미터가 있는 타입

일부 타입은 파라미터로 세부 형식을 지정할 수 있습니다.

```
std/media/v1/AudioFrame[sample_type=f32,channels=2]
```

호환성 규칙:
- **같은 베이스 타입 + 한쪽이 파라미터 없음** → 호환 (와일드카드로 취급)
- **파라미터 값이 다름** → 불호환

---

## 4. 타입 어노테이션 작성법

```yaml
- id: camera
  outputs:
    - image
  output_types:
    image: std/media/v1/Image

- id: detector
  inputs:
    image: camera/image
  input_types:
    image: std/media/v1/Image
  outputs:
    - bbox
  output_types:
    bbox: std/vision/v1/BoundingBox
```

---

## 5. 타입 호환성 규칙

### 암묵적 확장(widening) 변환

더 넓은 타입으로의 변환은 자동으로 허용됩니다.

```
UInt8 → UInt32 → UInt64
```

### Bytes는 범용 싱크

어떤 타입이든 `Bytes`를 받는 포트에 연결할 수 있습니다. 직렬화된 바이트를 그대로 처리하고 싶을 때 사용합니다.

### 사용자 정의 호환 규칙

`type_rules` 필드로 커스텀 호환 규칙을 추가할 수 있습니다.

```yaml
type_rules:
  - from: myproject/sensors/v1/RawFrame
    to: std/media/v1/Image
```

---

## 6. 검증 방법

### 6.1 정적 검증 (빌드/배포 전)

```bash
# 타입 불일치 경고
dora validate dataflow.yml

# 타입 불일치를 에러로 처리
dora build dataflow.yml --strict-types
```

또는 YAML 루트에서 설정:

```yaml
strict_types: true

nodes:
  - ...
```

검증 항목:
- 키 존재 여부
- URN 해석 가능 여부
- 엣지 타입 호환성
- 구조체 필드 스키마

### 6.2 런타임 타입 체크 (선택 사항)

기본적으로 런타임 오버헤드가 없습니다. 필요할 때만 환경 변수로 활성화합니다.

```bash
DORA_RUNTIME_TYPE_CHECK=warn dora run dataflow.yml   # 경고만
DORA_RUNTIME_TYPE_CHECK=error dora run dataflow.yml  # 에러로 처리
```

---

## 7. 사용자 정의 타입

프로젝트 내 `types/` 디렉터리에 YAML 파일을 작성해 커스텀 타입을 정의합니다. 디렉터리 구조가 URN 접두사가 됩니다.

```
types/
└── myproject/
    └── sensors/
        └── v1.yml    →  URN: myproject/sensors/v1/<TypeName>
```

---

## 8. Arrow IPC 프레이밍

출력별로 와이어 포맷을 지정할 수 있습니다.

```yaml
- id: sensor
  outputs:
    - image
  output_framing:
    image: arrow-ipc   # 또는 'raw' (기본값)
```

`arrow-ipc`는 Apache Arrow IPC 형식으로 직렬화해 다른 Arrow 도구와 상호운용할 때 유용합니다.

---

## 9. 정리

| 상황 | 권장 방법 |
|------|-----------|
| 빠른 프로토타이핑 | 타입 어노테이션 없이 동적 타입 사용 |
| 팀 협업 / 다수 노드 | `output_types` / `input_types` 선언 |
| CI/CD 파이프라인 | `dora validate` + `strict_types: true` |
| 디버깅 | `DORA_RUNTIME_TYPE_CHECK=warn` |
| ROS2 등 외부 도구 연동 | `output_framing: arrow-ipc` |
