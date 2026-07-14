---
title: "DORA 성능 벤치마킹: '10~17배 빠르다'는 어떻게 측정하는가"
date: 2026-07-14T00:00:00+09:00
draft: false
tags: ["robotics", "dora", "benchmarking", "performance", "latency", "ros2"]
categories: ["autonomous"]
description: "DORA와 ROS2의 지연시간 차이를 실제로 측정하는 방법론, 무엇을 재고 무엇을 재면 안 되는지, 그리고 우리 자신의 파이프라인에서 병목을 찾는 벤치마킹 절차를 정리합니다."
---

> 이 글은 시리즈 전체([DORA 입문](dora-rs-for-beginners/)부터 [실차 배포](dora-rs-real-hardware-deployment/)까지)에서 여러 번 언급된 "ROS2보다 빠르다"는 주장과 큐 길이·지연 메트릭을 실제로 측정하는 방법을 다룹니다.

[1편](dora-rs-for-beginners/)의 첫 문장은 "ROS2보다 10~17배 빠르다"였습니다. 이 숫자를 그대로 믿고 넘어가는 대신, **무엇을 어떻게 쟀길래 이런 숫자가 나오는지**, 그리고 이 숫자가 우리 자신의 파이프라인에도 그대로 적용되는지를 직접 측정하는 방법을 이 글에서 다룹니다.

---

## 1. 무엇을 재야 "빠르다"는 주장이 의미가 있는가

"빠르다"는 말은 최소 세 가지 다른 것을 가리킬 수 있고, 이걸 구분하지 않으면 벤치마크 자체가 무의미해집니다.

- **지연시간(Latency)**: 메시지 하나가 노드 A에서 노드 B로 도착하기까지 걸리는 시간. 제어 루프처럼 "얼마나 빨리 반응하는가"가 중요한 경우의 지표입니다.
- **처리량(Throughput)**: 단위 시간당 몇 개의 메시지를 처리할 수 있는가. LiDAR 포인트 클라우드처럼 대량의 데이터를 지속적으로 흘려보내야 하는 경우의 지표입니다.
- **CPU/메모리 오버헤드**: 같은 일을 하는 데 프레임워크 자체가 얼마나 많은 자원을 추가로 소모하는가. [실차 배포 편](dora-rs-real-hardware-deployment/#2-리소스-제약-온보드-컴퓨터는-서버가-아니다)에서 다룬 리소스 제약 상황에서 특히 중요합니다.

"DORA가 ROS2보다 10~17배 빠르다"는 벤치마크는 보통 **지연시간**을 가리키며, 그중에서도 노드 간 메시지 전달 자체의 지연(직렬화 + 통신 + 역직렬화)을 측정한 것입니다. 이 범위를 정확히 알아야, "우리 파이프라인의 인지 모델 추론 시간까지 10배 빨라진다"는 식의 잘못된 기대를 하지 않습니다 — 모델 추론 시간은 프레임워크와 무관하게 그대로입니다.

---

## 2. 지연시간을 직접 측정하는 최소 벤치마크

[노드 개발 편](dora-rs-node-development/)에서 만든 것과 비슷한, 아주 단순한 두 노드짜리 파이프라인으로 순수한 노드 간 지연을 잽니다.

```yaml
# bench-dataflow.yml
nodes:
  - id: sender
    path: target/release/sender
    outputs: [ping]

  - id: receiver
    path: target/release/receiver
    inputs:
      ping: sender/ping
    outputs: [pong]
```

```rust
// sender/src/main.rs — 매 메시지에 송신 시각을 실어 보낸다
use dora_node_api::{DoraNode, Event};
use std::time::{SystemTime, UNIX_EPOCH};

fn main() -> eyre::Result<()> {
    let (mut node, _events) = DoraNode::init_from_env()?;
    for _ in 0..10_000 {
        let now_ns = SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos() as u64;
        node.send_output("ping", Default::default(), now_ns.to_le_bytes().to_vec())?;
        std::thread::sleep(std::time::Duration::from_millis(1));
    }
    Ok(())
}
```

```rust
// receiver/src/main.rs — 받은 시각과 실어온 시각의 차이를 기록한다
use dora_node_api::{DoraNode, Event};
use std::time::{SystemTime, UNIX_EPOCH};

fn main() -> eyre::Result<()> {
    let (mut _node, mut events) = DoraNode::init_from_env()?;
    let mut latencies = Vec::new();

    while let Some(Event::Input { id, data, .. }) = events.recv() {
        if id.as_str() == "ping" {
            let sent_ns = u64::from_le_bytes(data[..8].try_into().unwrap());
            let now_ns = SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos() as u64;
            latencies.push(now_ns - sent_ns);
        }
    }
    // 10,000개 샘플이 모이면 p50/p99/max를 계산해 출력
    latencies.sort();
    println!("p50: {} us", latencies[latencies.len() / 2] / 1000);
    println!("p99: {} us", latencies[latencies.len() * 99 / 100] / 1000);
    println!("max: {} us", latencies.last().unwrap() / 1000);
    Ok(())
}
```

이 벤치마크가 재는 건 정확히 "`send_output` 호출부터 `events.recv()`로 그 데이터가 도착하기까지"입니다 — [1편](dora-rs-for-beginners/#4-핵심-기술-스택)에서 다룬 Zenoh 공유 메모리 전송과 Arrow 직렬화 오버헤드가 이 구간에 전부 포함됩니다. 반대로 노드 내부의 계산 시간(예제에서는 없음)은 이 측정에 들어가지 않습니다 — 이게 바로 "프레임워크 자체의 오버헤드"만 분리해서 재는 방법입니다.

---

## 3. ROS2와 비교할 때 반드시 맞춰야 할 조건

같은 벤치마크를 ROS2로 다시 짜서 숫자를 비교할 때, 조건이 안 맞으면 비교 자체가 무효가 됩니다.

- **메시지 크기**: 8바이트 타임스탬프 하나로 잰 지연과, LiDAR 포인트 클라우드(수 MB) 하나로 잰 지연은 완전히 다른 이야기입니다. [1편](dora-rs-for-beginners/#4-핵심-기술-스택)에서 강조한 Zenoh의 공유 메모리 전송(제로카피)은 메시지가 클수록 이득이 커지는 방식이라, 작은 메시지로 비교하면 DORA의 우위가 실제보다 작게 나오고, 큰 메시지로 비교하면 더 크게 나옵니다. **자신의 실제 워크로드와 비슷한 크기**로 재야 의미가 있습니다.
- **직렬화 방식**: ROS2의 기본 직렬화(CDR)와 DORA의 Arrow는 서로 다른 포맷입니다. "같은 프레임워크 조합, 다른 직렬화"를 비교하는 건지, "직렬화 방식 자체의 차이"까지 포함해서 비교하는 건지를 먼저 정해야 합니다. 흔히 인용되는 벤치마크 수치는 대개 각 프레임워크의 **기본 설정**을 그대로 비교한 것이라, "DORA가 원래 빠르다"보다는 "DORA의 기본 조합(Arrow + Zenoh)이 ROS2의 기본 조합(CDR + DDS)보다 이 워크로드에서 빠르다"에 가깝습니다.
- **같은 하드웨어, 같은 프로세스 우선순위**: [실차 배포 편](dora-rs-real-hardware-deployment/#3-실시간성-검증-평균적으로-빠르다는-충분하지-않다)에서 다룬 것처럼 스케줄링 우선순위나 CPU 코어 배정이 다르면 지연 분포 자체가 달라집니다. 벤치마크를 반복 가능하게 만들려면 두 프레임워크를 정확히 같은 조건(같은 머신, 같은 시각, 다른 프로세스 최소화)에서 돌려야 합니다.

이 조건들을 다 맞추지 않은 채 "DORA가 10~17배 빠르다"만 인용하면, 자신의 파이프라인에 적용했을 때 그 배율이 그대로 나오지 않아도 이상한 일이 아닙니다 — 그 숫자는 특정 메시지 크기, 특정 워크로드에서 측정된 값입니다.

---

## 4. p50만 보지 말고 분포 전체를 봐야 하는 이유

2절의 벤치마크 코드가 p50, p99, max를 전부 출력하는 이유는 [실차 배포 편](dora-rs-real-hardware-deployment/#3-실시간성-검증-평균적으로-빠르다는-충분하지-않다)에서 다룬 것과 같습니다 — 평균이나 중앙값(p50)이 아무리 좋아도, 꼬리(p99, max)가 길게 튀는 프레임워크라면 실시간성이 중요한 애플리케이션에는 위험합니다.

```
p50: 42 us
p99: 890 us     ← p50의 20배
max: 15,200 us  ← 어쩌다 한 번 15ms까지 튐
```

이런 분포가 나왔다면, "평균적으로 빠르다"는 결론과 별개로 "가끔 15ms까지 밀린다"는 사실도 함께 봐야 합니다. 이 튀는 값의 원인은 보통 OS 스케줄러가 다른 프로세스에 CPU를 뺏기거나, 메모리 할당이 지연되거나(2절 코드에서는 `Vec::new()` 이후 반복적인 `push`가 재할당을 유발할 수 있어, 정밀한 벤치마크라면 `Vec::with_capacity(10_000)`으로 미리 할당해야 이 노이즈를 제거할 수 있습니다), 시스템 전체가 부하 상태일 때입니다. p99/max가 이례적으로 크게 나온다면 벤치마크 코드 자체의 노이즈부터 의심하고, 그다음에 진짜 시스템 문제를 봐야 합니다.

---

## 5. 우리 파이프라인 전체를 벤치마킹하기: End-to-End 지연

2~4절이 "노드 하나에서 다음 노드까지"의 지연이었다면, 실전에서 중요한 건 보통 **그래프 전체를 관통하는 지연**입니다 — 센서 입력부터 최종 제어 명령까지 몇 ms가 걸리는가입니다. [관측/디버깅 편](dora-rs-observability-debugging/#4-타임스탬프로-인과관계-추적하기)에서 다룬 타임스탬프 추적이 여기서 측정 도구가 됩니다.

```
sensor-driver (t=0ms) → perception (t=12ms) → planning (t=15ms) → control (t=16ms)
                         └─ 12ms                └─ 3ms            └─ 1ms
```

각 구간의 지연을 더하면 전체 지연(이 예에서는 16ms)이 나오는데, 이걸 [회귀 테스트 편](dora-rs-av-regression-testing/#4-메트릭-수집)에서 다룬 대로 **씬 단위로 집계**해 두면, "이번 주에 배포한 인지 모델이 이전보다 전체 지연을 3ms 늘렸다"는 식의 회귀를 CI에서 자동으로 잡을 수 있습니다 — 벤치마킹이 일회성 측정이 아니라 [회귀 테스트 편](dora-rs-av-regression-testing/#8-ci-통합과-임계값-관리)에서 다룬 CI 임계값 관리 체계에 편입되는 지점입니다.

---

## 6. 정리

- "DORA가 ROS2보다 빠르다"는 주장은 보통 **노드 간 순수 통신 지연**을 가리키며, 모델 추론 시간 같은 애플리케이션 로직의 속도와는 무관합니다.
- 지연·처리량·오버헤드는 서로 다른 지표이므로, 벤치마킹 전에 "무엇을 재고 싶은가"를 먼저 정해야 합니다.
- 프레임워크 간 비교는 메시지 크기·직렬화 방식·하드웨어 조건을 맞추지 않으면 무효이며, 흔히 인용되는 배율은 특정 조건에서의 수치일 뿐입니다.
- p50만 보지 말고 p99/max까지 봐야 하며, 이 원칙은 [실차 배포 편](dora-rs-real-hardware-deployment/)에서 다룬 꼬리 지연 검증과 같은 이유에서입니다.
- 노드 간 지연을 넘어 **End-to-End 지연**을 씬 단위로 집계해 CI에 편입하면, 벤치마킹이 [회귀 테스트 편](dora-rs-av-regression-testing/)의 회귀 감지 체계와 자연스럽게 연결됩니다.

여기까지 총 여덟 편으로, DORA의 설계 철학부터 노드 개발·디버깅·실차 배포·성능 검증까지 한 바퀴를 돌았습니다. 이 순서(입문 → 파이프라인 설계 → 노드 개발 → 관측/디버깅 → 회귀 테스트 → 시뮬레이터 연동 → 실차 배포 → 벤치마킹)가 실제로 DORA 기반 자율주행 스택을 처음부터 구축할 때 밟게 될 흐름과 크게 다르지 않습니다.
