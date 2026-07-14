---
title: "DORA 노드 직접 만들기: Rust와 Python API 실습"
date: 2026-07-14T00:00:00+09:00
draft: false
tags: ["robotics", "dora", "rust", "python", "node", "tutorial"]
categories: ["autonomous"]
description: "dora-rs SDK로 실제로 동작하는 노드를 Rust와 Python 양쪽으로 작성하고, dora build/dora run으로 실행하며, 입출력 정의와 빌드·배포 사이클을 실습합니다."
---

> DORA가 처음이라면 [DORA 입문](dora-rs-for-beginners/)과 [데이터플로우 YAML](dora-rs-dataflow-yaml/)을 먼저 읽어보세요. 이 글은 그 두 편에서 개념으로만 다뤘던 "노드"를 실제 코드로 만들어봅니다.

지금까지 시리즈에서 노드는 "데이터플로우 그래프의 한 칸"이라는 개념으로만 등장했습니다. 이 글은 그 칸 하나를 실제로 채워봅니다 — Rust 노드와 Python 노드를 각각 만들고, 둘을 YAML로 엮어 실행하고, 개발 사이클에서 반복하게 될 빌드·재시작 흐름까지 따라갑니다.

---

## 1. 예제로 만들 파이프라인

카메라 프레임을 흉내 내는 소스 노드 하나와, 그 프레임에서 밝기 평균을 계산하는 처리 노드 하나로 아주 작은 파이프라인을 만듭니다.

```
camera-source (Rust)  ──frame──>  brightness (Python)  ──avg──>  logger (Rust)
```

Rust로 소스와 로거를, Python으로 처리 노드를 짜는 이유는 단순합니다 — DORA의 멀티언어 지원이 실제로 어떻게 동작하는지, 그리고 [1편](dora-rs-for-beginners/)에서 다룬 Arrow 포맷이 언어 경계를 넘을 때 무슨 역할을 하는지를 눈으로 확인하기 위해서입니다.

---

## 2. 프로젝트 구조

```
brightness-demo/
├── dataflow.yml
├── camera-source/       # Rust 노드
│   ├── Cargo.toml
│   └── src/main.rs
├── brightness/          # Python 노드
│   ├── brightness.py
│   └── requirements.txt
└── logger/              # Rust 노드
    ├── Cargo.toml
    └── src/main.rs
```

노드마다 독립된 디렉터리를 갖는 게 관례입니다. 각 노드는 자기 언어의 표준 프로젝트 구조(Rust는 `Cargo.toml`, Python은 스크립트 + `requirements.txt`)를 그대로 쓰고, DORA는 이 위에 "입력을 받고 출력을 내보내는" 최소한의 API만 얹습니다.

---

## 3. Rust 노드 작성: `camera-source`

```toml
# camera-source/Cargo.toml
[package]
name = "camera-source"
version = "0.1.0"
edition = "2021"

[dependencies]
dora-node-api = "0.3"
arrow = "50"
```

```rust
// camera-source/src/main.rs
use dora_node_api::{self, DoraNode, Event};
use arrow::array::UInt8Array;

fn main() -> eyre::Result<()> {
    let (mut node, mut events) = DoraNode::init_from_env()?;

    loop {
        match events.recv() {
            Some(Event::Input { id, .. }) if id.as_str() == "tick" => {
                // 실제로는 카메라 드라이버에서 프레임을 읽어오지만,
                // 예제에서는 640x480 그레이스케일 랜덤 값으로 대체합니다.
                let frame: Vec<u8> = (0..640 * 480).map(|_| rand::random()).collect();
                let array = UInt8Array::from(frame);
                node.send_output("frame", Default::default(), array)?;
            }
            Some(Event::Stop) => break,
            _ => {}
        }
    }
    Ok(())
}
```

이 코드에서 DORA API가 실제로 강제하는 건 딱 두 가지입니다.

1. **`DoraNode::init_from_env()`**: 이 노드가 어느 입력을 구독하고 어느 출력을 낼 수 있는지는 코드가 아니라 YAML이 결정합니다. `init_from_env()`가 실행 시점에 그 YAML 설정을 환경 변수로 전달받아 노드를 초기화합니다 — [2편](dora-rs-dataflow-yaml/)에서 다룬 "선언형 파이프라인"이 실제 코드 레벨에서 이렇게 구현됩니다.
2. **`events.recv()`로 들어오는 입력을 기다린다**: DORA 노드는 스스로 루프를 도는 게 아니라, 이벤트(입력이 도착하거나, 정지 신호가 오거나)를 받아서 반응하는 구조입니다. `tick`이라는 입력 이름은 [2편](dora-rs-dataflow-yaml/#2-내장-타이머)에서 다룬 내장 타이머가 보내는 것이고, 이 노드는 그 타이머가 울릴 때마다 프레임 하나를 생성합니다.

`send_output`에 넘긴 `UInt8Array`가 Arrow 배열이라는 점이 중요합니다 — [1편](dora-rs-for-beginners/#4-핵심-기술-스택)에서 "Arrow가 언어 간 공통 메모리 포맷"이라고 했던 게 바로 이 지점에서 쓰입니다. Rust에서 만든 이 배열이 뒤에서 볼 Python 노드로 그대로 넘어가는데, 그 사이에 직렬화·역직렬화가 일어나지 않습니다.

---

## 4. Python 노드 작성: `brightness`

```python
# brightness/brightness.py
from dora import Node
import numpy as np

node = Node()

for event in node:
    if event["type"] == "INPUT" and event["id"] == "frame":
        frame = event["value"].to_numpy()  # Arrow 배열 -> NumPy, 제로카피
        avg = float(np.mean(frame))
        node.send_output("avg", np.array([avg], dtype=np.float32))
```

Rust 쪽 `send_output("frame", ...)`과 Python 쪽 `event["id"] == "frame"`이 이름으로 짝지어진다는 걸 알 수 있습니다 — 이 이름 매칭이 YAML의 `inputs`/`outputs` 선언과 정확히 대응합니다(5절에서 확인합니다). `to_numpy()` 호출이 "제로카피"라고 적어둔 이유는, 이 변환이 Arrow 버퍼의 메모리를 복사하지 않고 NumPy가 그 메모리를 그대로 가리키도록 뷰(view)만 만들기 때문입니다 — [1편](dora-rs-for-beginners/#4-핵심-기술-스택)에서 다룬 "Arrow + Zenoh 조합의 시너지"가 노드 간 전송뿐 아니라 노드 안에서 언어별 라이브러리(NumPy)로 넘어가는 순간에도 그대로 이어집니다.

Python 노드는 Rust처럼 `main` 함수나 명시적인 이벤트 루프 매칭(`match`)을 쓰지 않고 `for event in node`로 단순화되어 있는데, 이건 DORA가 각 언어의 관용적인 문법에 맞춰 SDK를 따로 제공하기 때문입니다 — 내부에서 하는 일(이벤트를 기다렸다가 반응)은 Rust 쪽과 동일합니다.

---

## 5. 파이프라인을 YAML로 엮기

```yaml
# dataflow.yml
nodes:
  - id: camera-source
    build: cargo build -p camera-source --release
    path: target/release/camera-source
    inputs:
      tick: dora/timer/millis/33
    outputs:
      - frame

  - id: brightness
    build: pip install -r brightness/requirements.txt
    path: python
    args: brightness/brightness.py
    inputs:
      frame: camera-source/frame
    outputs:
      - avg

  - id: logger
    build: cargo build -p logger --release
    path: target/release/logger
    inputs:
      avg: brightness/avg
```

이 YAML이 두 언어로 짠 세 노드를 하나의 그래프로 엮는 유일한 지점입니다 — Rust 노드도 Python 노드도 서로의 존재를 코드에서 전혀 모르고, `inputs`에 적힌 `<노드id>/<출력이름>` 문자열만으로 연결됩니다. `tick: dora/timer/millis/33`은 [2편](dora-rs-dataflow-yaml/#2-내장-타이머)에서 다룬 내장 타이머를 33ms(약 30fps) 주기로 붙인 것입니다.

---

## 6. 빌드하고 실행하기

```bash
dora build dataflow.yml     # 각 노드의 build 커맨드를 순서대로 실행
dora up                     # coordinator + daemon 기동 (1편의 4계층 아키텍처 중 두 계층)
dora start dataflow.yml     # 그래프를 daemon에 등록하고 실행 시작
dora logs camera-source     # 특정 노드의 stdout/stderr 스트림 확인
dora stop
```

`dora build`는 각 노드의 `build` 필드에 적힌 커맨드(Rust는 `cargo build`, Python은 `pip install`)를 그대로 실행합니다 — DORA가 언어별 빌드 시스템을 대신해주는 게 아니라, 기존 빌드 시스템을 그래프 정의 안에 끌어다 쓰는 방식입니다. `dora up`이 [1편](dora-rs-for-beginners/#5-4계층-아키텍처)에서 다룬 Coordinator와 Daemon을 실제로 띄우는 명령이고, `dora start`가 그 위에 우리 그래프를 얹어 Runtime과 Node 프로세스들을 생성합니다.

개발 중에는 보통 코드를 고치고 → `dora build` → `dora stop; dora start dataflow.yml`을 반복합니다. 노드 하나만 바꿨다면 그 노드의 `build` 커맨드만 다시 실행되므로(변경되지 않은 노드는 캐시된 빌드 결과를 그대로 씀), 그래프가 커져도 반복 주기가 크게 느려지지 않습니다.

---

## 7. 흔히 겪는 실수 세 가지

- **입출력 이름 오타**: `camera-source/frame`을 `camera-source/frames`로 잘못 적으면, YAML 파싱은 통과하지만 실행 시점에 `brightness` 노드가 영원히 입력을 받지 못해 조용히 멈춰 있습니다. `dora logs`로 그래프가 시작됐는지 확인해도 이 문제는 에러 메시지 없이 나타나는 경우가 많아, 이름 문자열은 한 글자도 다르면 안 된다는 걸 처음엔 놓치기 쉽습니다.
- **입력 없이 이벤트 루프를 빠져나가는 코드**: Rust 예제의 `Event::Stop` 매칭을 빠뜨리면, `dora stop`을 실행해도 노드 프로세스가 종료되지 않고 좀비로 남을 수 있습니다.
- **Python 노드에서 무거운 import를 이벤트 루프 안에 두는 것**: `numpy`나 모델 로딩 같은 무거운 초기화는 `for event in node` 루프 **밖**에서 한 번만 실행되어야 합니다. 루프 안에 두면 입력이 들어올 때마다 매번 다시 실행되어, [1편](dora-rs-for-beginners/#2-왜-만들어졌나요)에서 강조한 "빠른 프레임워크"라는 이점이 노드 코드 한 줄 때문에 무색해집니다.

---

## 8. 정리

- DORA 노드는 언어에 상관없이 **"입력 이벤트를 기다렸다가 출력을 낸다"**는 동일한 패턴을 따르며, Rust와 Python은 각자의 관용적 문법으로 이 패턴을 감싼 SDK를 제공합니다.
- 노드 간 연결은 코드가 아니라 **YAML의 `inputs`/`outputs` 이름 매칭**으로만 이루어지고, 노드는 서로의 언어나 구현을 전혀 알 필요가 없습니다.
- Arrow 배열이 노드 사이를 오갈 때는 물론, 노드 안에서 NumPy 같은 언어별 라이브러리로 넘어갈 때도 **제로카피**로 이어지는 게 [1편](dora-rs-for-beginners/)에서 다룬 기술 스택 조합이 실제 코드에서 드러나는 지점입니다.
- `dora build` → `dora up` → `dora start`가 개발 사이클의 기본 반복 단위이고, 노드별 독립 빌드 덕분에 그래프가 커져도 반복 속도가 크게 나빠지지 않습니다.

다음 글에서는 이렇게 만든 파이프라인이 실행 중에 오류가 나거나 예상과 다르게 동작할 때, `dora logs` 너머로 무엇을 더 들여다볼 수 있는지 — CLI 관측 도구와 디버깅 방법을 다룹니다.
