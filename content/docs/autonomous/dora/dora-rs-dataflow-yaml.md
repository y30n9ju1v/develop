---
title: "DORA 데이터플로우 YAML 작성법"
date: 2026-06-13T00:00:00+09:00
draft: false
tags: ["robotics", "dora", "dataflow", "yaml"]
categories: ["autonomous"]
description: "DORA 파이프라인을 정의하는 데이터플로우 YAML의 문법과 옵션을 예제 중심으로 정리합니다."
---

> 이 글은 [DORA 데이터플로우 YAML 문서](https://dora-rs.ai/dora/concepts/dataflow-yaml.html)를 참고해 작성했습니다.
> DORA가 처음이라면 먼저 [DORA 입문](dora-rs-for-beginners/)을 읽어보세요.

---

## 1. 기본 구조

DORA 파이프라인은 YAML 파일 하나로 정의합니다. 노드들의 방향 그래프(directed graph)를 선언하는 방식입니다.

```yaml
nodes:
  - id: sender        # 고유 ID (슬래시 불가)
    path: sender.py
    outputs:
      - message       # 이 노드가 발행하는 출력

  - id: receiver
    path: receiver.py
    inputs:
      message: sender/message   # <노드ID>/<출력ID> 형식으로 구독
```

실행:

```bash
# 로컬 실행
dora run dataflow.yml

# 분산 실행
dora up
dora start dataflow.yml
```

VS Code에서 자동완성을 쓰려면 파일 맨 위에 이 줄을 추가하세요.

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/dora-rs/dora/main/dora-schema.json
```

---

## 2. 루트 설정 옵션

```yaml
health_check_interval: 10.0   # 헬스체크 주기 (초, 기본값 5.0)
strict_types: false           # true면 타입 경고를 에러로 처리

nodes:
  - ...
```

---

## 3. 입력(inputs) 설정

입력은 **짧은 형식**과 **긴 형식** 두 가지로 쓸 수 있습니다.

```yaml
# 짧은 형식
inputs:
  image: camera/frames

# 긴 형식 (큐 동작 제어)
inputs:
  sensor_data:
    source: sensor/frames
    queue_size: 10                 # 버퍼 크기 (기본값 10)
    queue_policy: drop_oldest      # drop_oldest | backpressure
    input_timeout: 5.0             # 이 시간 동안 입력 없으면 서킷 브레이커 발동
```

---

## 4. 내장 타이머

별도 노드 없이 주기적 틱(tick)을 받을 수 있습니다.

```yaml
inputs:
  tick:      dora/timer/millis/100   # 100ms마다
  slow_tick: dora/timer/millis/1000  # 1초마다
  hz_tick:   dora/timer/hz/30        # 30Hz
```

---

## 5. 로그 집계

다른 노드의 로그를 입력으로 구독할 수 있습니다. 메시지는 JSON 문자열로 옵니다.

```yaml
inputs:
  all_logs:    dora/logs              # 모든 노드의 로그
  errors_only: dora/logs/error        # 에러 레벨 이상
  sensor_info: dora/logs/info/sensor  # sensor 노드의 info 이상
```

---

## 6. 노드 소스 종류

로컬 파일 외에도 Git 레포지토리나 모듈을 소스로 쓸 수 있습니다.

```yaml
# 로컬 파일
- id: my-node
  path: ./my_node.py

# Git 레포지토리 (dora build로 빌드 후 실행)
- id: rust-node
  git: https://github.com/dora-rs/dora.git
  branch: main
  build: cargo build -p example-node --release
  path: target/release/example-node

# 모듈 참조
- id: fast-pipeline
  module: modules/transform.module.yml
  params:
    speed: "2.0"
    mode: turbo
```

---

## 7. 환경 변수

```yaml
- id: sensor
  path: ./sensor
  env:
    DEBUG: true
    PORT: 8080
    RATE: 1.5
    HOST:
      __dora_env: HOST_VAR   # 호스트 환경 변수에서 읽어옴
```

`$VAR` 형태의 변수 확장도 지원하며, 빌드와 실행 양쪽에 모두 적용됩니다.

---

## 8. 로깅 설정

```yaml
- id: sensor
  path: ./sensor
  min_log_level: info          # 이 레벨 미만 로그 억제
  send_stdout_as: raw_output   # stdout/stderr를 출력으로 라우팅
  send_logs_as: log_entries    # 구조화 로그를 출력으로 라우팅
  max_log_size: "100MB"        # 파일 로테이션 크기
  max_rotated_files: 3         # 보관할 로그 파일 수
  outputs:
    - data
    - raw_output
    - log_entries
```

---

## 9. 장애 복구 설정

```yaml
- id: sensor
  path: ./sensor
  restart_policy: on-failure   # never | on-failure | always
  max_restarts: 5
  restart_delay: 1.0           # 첫 재시작 대기 시간 (초)
  max_restart_delay: 30.0      # 지수 백오프 상한
  restart_window: 300.0        # 이 시간 내 max_restarts 초과 시 포기
  health_check_timeout: 30.0   # 이 시간 동안 통신 없으면 강제 종료
```

| 정책 | 동작 |
|------|------|
| `never` | 자동 재시작 안 함 (기본값) |
| `on-failure` | 비정상 종료(exit code != 0) 시 재시작 |
| `always` | 사용자 중지 외 모든 종료 시 재시작 |

---

## 10. 타입 어노테이션

포트에 타입을 달면 `dora validate`로 파이프라인 연결을 정적 검증할 수 있습니다.

```yaml
- id: camera
  outputs:
    - image
  output_types:
    image: std/media/v1/Image      # URN 형식: std/<카테고리>/v<버전>/<타입>

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

```bash
dora validate dataflow.yml
```

---

## 11. 오퍼레이터 노드

독립 프로세스 대신 **Runtime 안에서 인프로세스**로 실행되는 노드입니다. Python 스크립트나 공유 라이브러리를 사용할 때 유용합니다.

```yaml
# 단일 오퍼레이터
- id: detector
  operator:
    python: detect.py
    build: pip install ultralytics
    inputs:
      image: camera/frames
    outputs:
      - bbox

# 복수 오퍼레이터 (하나의 Runtime 안에서 실행)
- id: runtime-node
  operators:
    - id: preprocessor
      shared-library: ../../target/debug/libpreprocess
      inputs:
        raw: sensor/data
      outputs:
        - processed
    - id: analyzer
      shared-library: ../../target/debug/libanalyze
      inputs:
        data: runtime-node/preprocessor/processed   # 같은 Runtime 내부 연결
      outputs:
        - result
```

---

## 12. 분산 배포

노드마다 실행할 머신을 지정할 수 있습니다. (`dora up` 이후 사용)

```yaml
- id: camera-driver
  _unstable_deploy:
    machine: robot-arm     # Daemon ID
  path: ./camera
  outputs:
    - frames

- id: ml-inference
  _unstable_deploy:
    machine: gpu-server
    distribute: scp        # local | scp | http
  inputs:
    frames: camera-driver/frames
```

---

## 13. ROS2 브리지

기존 ROS2 토픽/서비스를 DORA 파이프라인과 연결할 수 있습니다.

```yaml
# 토픽 구독
- id: camera_bridge
  ros2:
    topic: /camera/image_raw
    message_type: sensor_msgs/Image
    direction: subscribe
  outputs:
    - image

# 토픽 발행 + 구독 혼합
- id: robot_bridge
  ros2:
    topics:
      - topic: /camera/image_raw
        message_type: sensor_msgs/Image
        direction: subscribe
        output: image
      - topic: /cmd_vel
        message_type: geometry_msgs/Twist
        direction: publish
        input: velocity
    qos:
      reliable: true
  inputs:
    velocity: planner/cmd_vel
  outputs:
    - image

# 서비스 서버
- id: add_service
  ros2:
    service: /add_two_ints
    service_type: example_interfaces/AddTwoInts
    role: server
  inputs:
    request: client_node/request
  outputs:
    - response
```

---

## 14. 완성 예제

카메라 → 객체 감지 → 시각화 + 로그 저장 파이프라인입니다.

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/dora-rs/dora/main/dora-schema.json

health_check_interval: 10.0

_unstable_debug:
  enable_debug_inspection: true   # dora topic echo 등 디버그 명령 활성화

nodes:
  - id: webcam
    operator:
      python: webcam.py
      inputs:
        tick: dora/timer/millis/100   # 100ms마다 프레임 캡처
      outputs:
        - image

  - id: detector
    operator:
      python: detect.py
      build: pip install ultralytics
      inputs:
        image: webcam/image
      outputs:
        - bbox

  - id: plotter
    operator:
      python: plot.py
      inputs:
        image: webcam/image
        bbox: detector/bbox           # 두 노드의 출력을 동시에 구독

  - id: logger
    path: ./logger
    inputs:
      bbox: detector/bbox
    send_stdout_as: logs
    min_log_level: info
    restart_policy: on-failure        # 크래시 시 자동 재시작
    max_restarts: 3
    outputs:
      - logs
```

실행 및 디버그:

```bash
dora run dataflow.yml

# 다른 터미널에서 실시간 확인
dora topic echo detector/bbox
dora topic hz webcam/image
dora topic info
```
