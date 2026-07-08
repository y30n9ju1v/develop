---
title: "DORA 통신 패턴: Topic, Service, Action, Streaming"
date: 2026-06-13T00:00:00+09:00
draft: false
tags: ["robotics", "dora", "patterns", "pub-sub", "service", "action", "streaming"]
categories: ["autonomous"]
description: "DORA의 네 가지 통신 패턴(Topic, Service, Action, Streaming)의 동작 방식과 메타데이터 규약을 정리합니다."
---

> 이 글은 [DORA 패턴 문서](https://dora-rs.ai/dora/concepts/patterns.html)를 참고해 작성했습니다.

---

## 1. 개요

DORA는 모든 통신을 데이터플로우(pub/sub) 위에 구현합니다. 네 가지 패턴은 별도 인프라가 아니라 **메시지 메타데이터 규약**으로 구분됩니다.

| 패턴 | 응답 필요 | 장시간 | 취소 가능 | 실시간 스트림 |
|------|-----------|--------|-----------|---------------|
| **Topic** | 아니오 | — | — | 아니오 |
| **Service** | 예 | 아니오 | 아니오 | 아니오 |
| **Action** | 예 | 예 | 선택 | 아니오 |
| **Streaming** | 아니오 | 예 | flush로 | 예 |

---

## 2. Topic (Pub/Sub)

가장 기본적인 패턴입니다. 발행자는 데이터를 내보내고, 구독자는 받습니다. 상관관계 추적이 필요 없습니다.

**적합한 상황**: 센서 데이터 스트리밍, 주기적 상태 발행, 단방향 이벤트

```yaml
nodes:
  - id: camera
    outputs:
      - image

  - id: detector
    inputs:
      image: camera/image
```

별도 메타데이터 없이 데이터를 그냥 발행하면 됩니다.

---

## 3. Service (Request/Reply)

클라이언트가 요청을 보내고 **정확히 하나의 응답**을 기대하는 패턴입니다.

**적합한 상황**: 설정 조회, 계산 요청, 단발성 명령

### 동작 방식

1. 클라이언트가 `request_id` (UUID v7)를 메타데이터에 담아 요청 발송
2. 서버가 요청 처리 후 **동일한 `request_id`를 그대로 응답에 포함**해 발송
3. 클라이언트가 `request_id`로 자신의 요청과 응답을 매칭

`request_id`를 응답에 그대로 반환하지 않으면 클라이언트가 응답을 매칭할 수 없습니다.

### YAML

```yaml
nodes:
  - id: client
    outputs:
      - request
    inputs:
      response: server/response

  - id: server
    inputs:
      request: client/request
    outputs:
      - response
```

### Python 코드 패턴

```python
# 클라이언트
node.send_service_request("request", params={"key": "value"}, data=payload)

# 서버
event = node.next()
request_id = event["metadata"]["request_id"]   # 요청에서 꺼내서
node.send_output("response", data=result, metadata={"request_id": request_id})  # 그대로 반환
```

---

## 4. Action (Goal/Feedback/Result)

**장시간 동작**하면서 중간 피드백을 보내고 최종 결과를 반환하는 패턴입니다. 취소도 지원합니다.

**적합한 상황**: 경로 탐색, 파일 업로드, 로봇 팔 동작 수행

### 핵심 메타데이터

| 메타데이터 | 설명 |
|------------|------|
| `goal_id` | 동작을 식별하는 UUID v7 |
| `goal_status` | 최종 상태: `succeeded` / `aborted` / `canceled` |

`goal_status` 값은 **소문자 그대로** 사용해야 합니다. 대소문자 구분이 있습니다.

### 동작 흐름

```
클라이언트 ──goal_id 포함 목표 전송──→ 서버
           ←──피드백 (goal_id 포함)────
           ←──피드백 (goal_id 포함)────
           ←──최종 결과 (goal_status)──
```

### 취소

취소는 `goal_id`를 메타데이터에 담아 취소 메시지를 보내는 방식입니다. 서버는 주기적으로 취소 요청이 들어왔는지 확인하고 `goal_status: canceled`로 응답합니다.

### YAML

```yaml
nodes:
  - id: planner
    outputs:
      - goal
      - cancel
    inputs:
      feedback: navigator/feedback
      result: navigator/result

  - id: navigator
    inputs:
      goal: planner/goal
      cancel: planner/cancel
    outputs:
      - feedback
      - result
```

### Python 코드 패턴

```python
import uuid

# 클라이언트: 목표 전송
goal_id = str(uuid.uuid7())
node.send_output("goal", data=target, metadata={"goal_id": goal_id})

# 서버: 피드백 및 결과 전송
goal_id = event["metadata"]["goal_id"]
node.send_output("feedback", data=progress, metadata={"goal_id": goal_id})
node.send_output("result", data=final, metadata={"goal_id": goal_id, "goal_status": "succeeded"})
```

---

## 5. Streaming (세션/세그먼트/청크)

오디오, 비디오, 센서 데이터처럼 **실시간으로 흘러가는 스트림**을 처리하는 패턴입니다. 스트림 중간에 새 스트림이 시작되면 이전 스트림의 큐를 즉시 비울 수 있습니다.

**적합한 상황**: STT/TTS 파이프라인, 영상 스트리밍, LiDAR 실시간 처리

### 핵심 메타데이터

| 메타데이터 | 설명 |
|------------|------|
| `session_id` | 전체 대화/세션 식별자 |
| `segment_id` | 세션 내 논리 단위 (예: 발화 하나) |
| `seq` | 세그먼트 내 청크 순번 |
| `fin` | `true`면 세그먼트의 마지막 청크 |
| `flush` | `true`면 수신자의 큐에서 오래된 메시지 즉시 제거 |

### flush 동작

`flush: true`가 담긴 메시지가 도착하면, 수신자의 입력 큐에서 **그보다 오래된 메시지가 모두 제거된 뒤** flush 메시지가 전달됩니다. 덕분에 새 발화가 시작되면 이전 발화 처리를 즉시 중단할 수 있습니다.

### Python 코드 패턴

```python
import uuid

session_id = str(uuid.uuid7())
segment_id = str(uuid.uuid7())

# 스트림 전송 (발신 측)
for i, chunk in enumerate(audio_chunks):
    is_last = (i == len(audio_chunks) - 1)
    node.send_output("audio", data=chunk, metadata={
        "session_id": session_id,
        "segment_id": segment_id,
        "seq": i,
        "fin": is_last,
    })

# 새 발화 시작 시 이전 세그먼트 플러시
new_segment_id = str(uuid.uuid7())
node.send_output("audio", data=first_chunk, metadata={
    "session_id": session_id,
    "segment_id": new_segment_id,
    "seq": 0,
    "fin": False,
    "flush": True,    # 이전 세그먼트 큐 즉시 비움
})
```

---

## 6. 패턴 선택 가이드

```
응답이 필요한가?
├── 아니오 → 실시간 스트림인가?
│            ├── 아니오 → Topic
│            └── 예    → Streaming
└── 예    → 장시간 동작인가?
             ├── 아니오 → Service
             └── 예    → Action
```

---

## 7. 정리

네 패턴 모두 DORA의 기본 데이터플로우 위에 메타데이터 규약으로 구현됩니다. 별도 라이브러리나 미들웨어 없이, YAML 연결과 메시지 메타데이터만으로 복잡한 통신 패턴을 표현할 수 있습니다.

| 패턴 | 핵심 메타데이터 | 언제 |
|------|----------------|------|
| Topic | 없음 | 단방향 데이터 흐름 |
| Service | `request_id` | 단발 요청/응답 |
| Action | `goal_id`, `goal_status` | 장시간 동작 + 피드백 |
| Streaming | `session_id`, `segment_id`, `seq`, `fin`, `flush` | 실시간 스트림 + 인터럽트 |
