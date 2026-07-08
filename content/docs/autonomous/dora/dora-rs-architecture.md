---
title: "DORA 아키텍처: Coordinator, Daemon, Runtime, Node"
date: 2026-06-13T00:00:00+09:00
draft: false
tags: ["robotics", "dora", "rust", "architecture"]
categories: ["autonomous"]
description: "DORA의 4계층 아키텍처(Coordinator, Daemon, Runtime, Node)가 어떻게 맞물려 동작하는지 정리합니다."
---

> 이 글은 [DORA 아키텍처 문서](https://dora-rs.ai/dora/concepts/architecture.html)를 참고해 작성했습니다.
> DORA가 처음이라면 먼저 [DORA 입문](dora-rs-for-beginners/)을 읽어보세요.

---

## 1. 4계층 스택

DORA는 아래에서 위로 쌓이는 4계층 구조로 설계되어 있습니다.

```
┌──────────────────────────────────────┐
│  4. Orchestration  CLI + Coordinator │  ← 분산 배포, 전체 조율
├──────────────────────────────────────┤
│  3. Execution      Daemon + Runtime  │  ← 머신별 프로세스 관리
├──────────────────────────────────────┤
│  2. Core Libraries dora-core + APIs  │  ← 공유 메모리, 노드 API
├──────────────────────────────────────┤
│  1. Protocol       Apache Arrow      │  ← 메시지 직렬화 포맷
└──────────────────────────────────────┘
```

---

## 2. Coordinator (조율자)

**시스템 전체에 하나만 존재**하며, 분산 배포 시 모든 Daemon을 조율합니다.

- **Axum 기반 WebSocket 서버** (포트 6013)
- CLI 명령을 받아 Daemon에게 전달
- Daemon 등록 관리, 아티팩트 배포, 실시간 이벤트 스트리밍
- 상태 저장: 인메모리 또는 영속적 `redb` 백엔드 선택 가능

로컬에서 `dora run`만 쓸 때는 Coordinator가 필요 없습니다. `dora up`으로 네트워크 모드를 시작할 때 활성화됩니다.

---

## 3. Daemon (데몬)

**머신마다 하나씩** 실행되며, 그 머신 위의 노드 생명주기를 관리합니다.

- 비동기 Tokio 이벤트 루프로 동작
- 아래 네 가지 신호를 하나로 합산(merge)해서 처리합니다:
  - Coordinator 명령
  - 실행 중인 노드의 상태
  - 다른 Daemon으로부터 오는 Zenoh 메시지
  - 주기 타이머
- 노드를 **자식 프로세스**로 생성하고 TCP 또는 공유 메모리로 통신 감시
- Coordinator와는 WebSocket으로 연결, 끊기면 지수 백오프(1s~30s)로 자동 재연결

---

## 4. Runtime (런타임)

**인프로세스(in-process) 오퍼레이터**를 실행하는 레이어입니다.

- Python 오퍼레이터는 PyO3로, 네이티브 라이브러리는 dlopen으로 로드
- 단일 스레드 Tokio 런타임 + 별도 오퍼레이터 스레드 구조
- 두 스레드는 bounded `flume` 채널로 통신

Runtime을 쓰지 않으면 각 노드가 독립 프로세스로 실행됩니다. Runtime을 쓰면 여러 오퍼레이터가 **한 프로세스 안에서** 동작해 프로세스 간 통신 비용이 사라집니다.

---

## 5. Node (노드)

**독립 프로세스**로 실행되는 기본 실행 단위입니다.

- 환경 변수로 자신의 설정을 읽어옴
- Daemon에 등록 → 이벤트 구독 → 데이터 수신/발행

메시지 크기에 따라 전송 방식이 자동으로 달라집니다:

| 메시지 크기 | 전송 방식 |
|-------------|-----------|
| 4KiB 미만 | TCP (8바이트 길이 접두사 + bincode 직렬화) |
| 4KiB 이상 | 제로카피 공유 메모리 (128바이트 정렬, atomic acquire/release) |

---

## 6. 통신 흐름

```
CLI ──WebSocket──→ Coordinator ──WebSocket──→ Daemon ──TCP/SharedMem──→ Node
                                                  │
                                           Zenoh pub-sub
                                                  │
                                             Daemon (다른 머신)
```

Daemon 간 통신은 Zenoh를 사용하며, 토픽 패턴은 다음과 같습니다.

```
dora/{network_id}/{dataflow_id}/output/{node_id}/{output_id}
```

---

## 7. 장애 내성

| 기능 | 동작 |
|------|------|
| **재시작 정책** | Never / OnFailure / Always, 지수 백오프 설정 가능 |
| **헬스 모니터링** | 5초마다 하트비트·헬스체크, 2초마다 메트릭 수집 |
| **서킷 브레이커** | 입력 타임아웃 → Degraded 상태 전환, 복구 시 `InputRecovered` 이벤트 발생 |
| **에러 전파 추적** | 업스트림 실패가 다운스트림 크래시를 유발했는지 기록 |

---

## 8. 주요 상수

| 항목 | 값 |
|------|----|
| Coordinator WebSocket 포트 | 6013 |
| 제로카피 임계값 | 4,096 bytes |
| TCP 메시지 최대 크기 | 64 MiB |
| 하트비트 간격 | 5초 |
| 메트릭 수집 간격 | 2초 |
| 기본 헬스체크 타임아웃 | 5초 |

---

## 9. 정리

```
Coordinator (1개) — 전체 조율
    └─ Daemon (머신당 1개) — 노드 생명주기
            ├─ Runtime — 인프로세스 오퍼레이터
            └─ Node (프로세스) — 실제 실행 단위
                    ↕ Apache Arrow (제로카피)
```

로컬 개발 시에는 `dora run` 하나로 Daemon이 직접 노드들을 관리합니다. 분산 배포 시에는 `dora up`으로 Coordinator를 띄우고, 각 머신의 Daemon이 Coordinator에 연결해 조율을 받습니다.
