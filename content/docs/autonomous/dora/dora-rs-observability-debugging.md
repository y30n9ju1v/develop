---
title: "DORA 파이프라인 관측과 디버깅: CLI, 로그, Rerun"
date: 2026-07-14T00:00:00+09:00
draft: false
tags: ["robotics", "dora", "observability", "debugging", "logging", "rerun"]
categories: ["autonomous"]
description: "dora logs/dora list 같은 CLI 도구로 파이프라인 상태를 확인하고, 노드가 조용히 멈추거나 역압에 걸리는 상황을 진단하며, Rerun으로 데이터 흐름 자체를 시각화하는 방법을 정리합니다."
---

> [DORA 노드 직접 만들기](dora-rs-node-development/)에서 만든 파이프라인을 계속 예제로 씁니다. 아직 안 읽었다면 먼저 보고 오는 걸 권합니다.

[이전 글](dora-rs-node-development/) 8절에서 "입출력 이름을 오타 내면 에러 없이 조용히 멈춘다"는 문제를 짚었습니다. 이런 종류의 실패는 DORA뿐 아니라 데이터플로우 구조를 가진 프레임워크 전반의 공통된 함정입니다 — 그래프의 각 노드는 독립적으로 잘 돌고 있는데, 그래프 **전체**가 원하는 대로 동작하지 않는 상황을 무엇으로 진단할지가 이 글의 주제입니다.

---

## 1. 가장 먼저 볼 것: `dora list`와 `dora logs`

```bash
dora list
```

```
dataflow: brightness-demo (running)
  camera-source   [running]
  brightness      [running]
  logger          [running]
```

이 명령이 보여주는 건 딱 "프로세스가 살아 있는가"입니다. 세 노드가 전부 `running`이어도 데이터가 실제로 흐르고 있다는 보장은 없습니다 — 프로세스는 떠 있지만 입력을 영원히 기다리며 멈춰 있는 상태도 `running`으로 표시되기 때문입니다.

```bash
dora logs brightness
```

각 노드는 자기 stdout/stderr를 daemon에 남기고, `dora logs <노드id>`로 그 스트림을 볼 수 있습니다. [이전 글](dora-rs-node-development/) 8절의 오타 문제를 이 명령으로 진단하는 과정을 따라가 보면:

1. `dora logs camera-source` — 프레임을 정상적으로 보내고 있다는 로그가 보임 (문제 없음)
2. `dora logs brightness` — 아무 로그도 없음, 즉 `for event in node` 루프에 한 번도 진입하지 못했거나 입력을 한 번도 못 받았다는 신호
3. 이 시점에서 코드가 아니라 **YAML의 이름 매칭**을 의심하게 됨 — 실제로 `camera-source/frame`과 `frame: camera-source/frames`처럼 한 글자가 어긋나 있었다면 여기서 잡힘

이 진단 순서 자체가 중요합니다 — 노드가 `running`인데 로그가 조용하다면, 코드 버그보다 **YAML 배선 문제**를 먼저 의심하는 게 순서상 빠릅니다.

---

## 2. 역압(Backpressure)이 걸렸는지 확인하기

[2편](dora-rs-dataflow-yaml/#3-큐-정책과-역압backpressure)에서 다룬 큐 정책은, 노드가 입력을 처리하는 속도보다 입력이 더 빨리 들어오면 큐가 쌓인다고 했습니다. 이 상태는 `running`이지만 실질적으로 지연이 계속 누적되는 상태라, 로그만 봐서는 "잘 돌고는 있는데 느리다"는 것과 구분하기 어렵습니다.

```bash
dora top
```

`dora top`은 각 노드의 CPU, 메모리 사용량 및 **큐 깊이(Queue Depth)**를 실시간 TUI로 보여줍니다. `brightness` 노드의 큐 깊이가 계속 늘어나는지를 여기서 확인합니다. 큐가 계속 쌓이고 있다면 원인은 보통 셋 중 하나입니다.

- **처리 자체가 느림**: `brightness.py`의 `np.mean` 호출 자체는 빠르지만, 만약 이 자리에 무거운 모델 추론이 들어갔다면 입력 주기(33ms)보다 처리 시간이 길어질 수 있습니다.
- **[이전 글](dora-rs-node-development/) 8절에서 지적한 "무거운 import를 루프 안에 두는" 실수**: 매 이벤트마다 불필요한 초기화가 반복되어 처리 시간이 부풀려집니다.
- **다운스트림 노드가 느려서 역류**: `logger` 노드가 느리면, 큐 정책에 따라 `brightness`까지 영향을 받을 수 있습니다 — 역압은 한 노드만 보고는 원인을 못 찾고, 그래프를 따라 다운스트림까지 같이 봐야 하는 경우가 많습니다.

---

## 3. 데이터 자체를 눈으로 보기: Rerun

로그와 메트릭은 "노드가 실행되고 있는가", "큐가 쌓이는가"는 알려주지만, "지금 흐르고 있는 데이터 값 자체가 이상한가"는 알려주지 않습니다. [회귀 테스트 편](dora-rs-av-regression-testing/#10-rerun으로-실패-시나리오-분석)에서 실패 시나리오 분석 도구로 다뤘던 **Rerun**은 회귀 테스트 상황에만 국한되지 않고, 개발 중 파이프라인 디버깅에도 그대로 씁니다.

```python
# brightness/brightness.py에 로깅 추가
import rerun as rr

rr.init("brightness-demo", spawn=True)

for event in node:
    if event["type"] == "INPUT" and event["id"] == "frame":
        frame = event["value"].to_numpy().reshape(480, 640)
        avg = float(np.mean(frame))
        rr.log("camera/frame", rr.Image(frame))
        rr.log("brightness/avg", rr.Scalar(avg))
        node.send_output("avg", np.array([avg], dtype=np.float32))
```

이렇게 한 줄씩 끼워 넣으면, 노드 코드 자체는 그대로 두고도 실행 중인 프레임 이미지와 그 평균값의 시간에 따른 그래프를 Rerun 뷰어에서 동시에 볼 수 있습니다. `dora logs`가 "무슨 일이 일어났다"는 텍스트라면, Rerun은 "그 값이 실제로 이랬다"는 그림입니다 — 예를 들어 밝기 평균이 항상 0에 가깝게 나온다면, 로그에는 에러가 안 남지만 Rerun의 이미지 뷰를 보는 순간 프레임 자체가 새까맣다는 게(카메라 소스 로직 버그) 바로 드러납니다.

Rerun을 파이프라인 전체가 아니라 **의심되는 노드 하나에만** 먼저 붙이는 게 실용적입니다 — 모든 노드에 로깅을 다 넣으면 뷰어 자체가 무거워지고, 정작 봐야 할 신호가 다른 노드들의 시각화에 묻히기 쉽습니다.

---

## 4. 타임스탬프로 인과관계 추적하기

여러 노드가 얽힌 그래프에서 "이 이상한 출력이 어느 입력 때문에 생겼는가"를 추적하려면, DORA가 각 메시지에 자동으로 붙이는 타임스탬프가 실마리가 됩니다. [시뮬레이터 연동 편](dora-rs-simulator-integration/#5-타임스탬프-처리)에서 다룬 타임스탬프 처리 원칙이 여기서도 그대로 쓰입니다 — `brightness`의 이상한 출력 하나를 발견했다면, 그 출력의 타임스탬프와 같은 시각의 `camera-source` 로그(또는 Rerun에 남긴 프레임 이미지)를 대조해 "그 순간 입력이 원래 이상했는지, 아니면 처리 과정에서 망가졌는지"를 구분할 수 있습니다.

만약 특정 시간대에 발생한 문제라면, `dora logs <dataflow> <node>` 출력 내용(또는 `grep` 등으로 필터링된 결과)이나 OpenTelemetry 연동 대시보드(예: Grafana Loki 등)에서 해당 시각의 타임스탬프 로그를 직접 잘라내어 추적해야 합니다.

이런 식으로 특정 시각 구간만 잘라 보는 것도, 타임스탬프가 노드 간에 일관되게 붙어 있어야만 의미가 있습니다 — [시뮬레이터 연동 편](dora-rs-simulator-integration/#5-타임스탬프-처리)에서 강조했던 "시뮬레이션 시간 vs 실제 시간" 구분이 여기서도 디버깅의 전제 조건으로 다시 등장합니다.

---

## 5. 흔한 증상과 먼저 확인할 곳 매핑

| 증상 | 먼저 확인할 것 |
|---|---|
| 노드가 `running`인데 로그가 아예 없음 | YAML의 `inputs`/`outputs` 이름 매칭 (1절) |
| 지연이 점점 누적됨 | 큐 길이 메트릭, 다운스트림 노드 처리 속도 (2절) |
| 출력 값이 이상함 (에러는 없음) | Rerun으로 실제 데이터 시각화 (3절) |
| 특정 시점에만 이상 동작 | 타임스탬프로 노드 간 로그 대조 (4절) |
| 전체가 멈춤 | `dora list`로 어느 노드가 죽었는지, `dora logs`로 그 노드의 마지막 로그 확인 |

---

## 6. 정리

- `dora list`는 "프로세스가 살아 있는가"만 알려주고, `dora logs`는 "무슨 일이 있었는가"를 텍스트로 알려줍니다 — 데이터 흐름 자체가 멈췄는지는 이 둘의 조합(로그 없음 + running)으로 추론해야 합니다.
- 역압은 로그에 에러로 남지 않으므로, 큐 길이 메트릭을 직접 확인하고 원인을 다운스트림까지 따라가야 합니다.
- Rerun은 회귀 테스트 실패 분석 도구를 넘어, 개발 중 "값 자체가 맞는지"를 확인하는 범용 디버깅 도구로 쓸 수 있습니다.
- 여러 노드에 걸친 문제는 타임스탬프로 인과관계를 추적해야 하며, 이건 시뮬레이터 연동에서 다룬 시간 동기화 원칙과 같은 축 위에 있습니다.

다음 글에서는 이렇게 로컬에서 만들고 디버깅한 파이프라인을 시뮬레이터가 아니라 **실제 차량/로봇 하드웨어**에 올릴 때 새로 생기는 문제 — 리소스 제약, 실시간성 검증, 시뮬레이션과의 괴리 — 를 다룹니다.
