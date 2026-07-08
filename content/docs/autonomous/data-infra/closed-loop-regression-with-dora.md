---
title: "Arrow로 관통하는 자율주행 클로즈 루프 회귀 테스트 파이프라인"
date: 2026-07-08T00:00:00+09:00
draft: false
tags: ["autonomous", "dora", "apache-arrow", "closed-loop", "regression-test", "rerun", "py123d"]
categories: ["autonomous"]
description: "py123d → FiftyOne → DORA → Rerun으로 이어지는 Apache Arrow 기반 클로즈 루프 회귀 테스트 파이프라인을 소개합니다."
---

앞선 두 글에서 Apache Arrow가 왜 빠른지, 그리고 **[py123d + FiftyOne + Rerun](autonomous-data-pipeline/)** 조합이 자율주행 데이터 파이프라인을 어떻게 통일하는지 살펴봤습니다.

오늘은 여기서 한 발 더 나아갑니다. **[DORA](../../dora/dora-rs-for-beginners/)** 역시 내부적으로 Apache Arrow를 노드 간 메시지 포맷으로 사용합니다. 덕분에 데이터 큐레이션부터 자율주행 스택 실행, 결과 시각화까지 **Arrow 하나가 파이프라인 전체를 끊김 없이 관통**하는 구조를 만들 수 있습니다.

---

## 1. 클로즈 루프 테스트가 뭔가요?

자율주행 소프트웨어를 테스트하는 방법은 크게 두 가지입니다.

**오픈 루프(Open-loop)**: 녹화된 센서 데이터를 재생하면서 알고리즘 출력만 확인합니다. 빠르고 간단하지만, 알고리즘의 결정이 다음 장면에 영향을 주지 않습니다. 실제 차량이 핸들을 꺾으면 카메라 앵글이 바뀌는데, 오픈 루프에서는 그냥 녹화된 앵글이 재생됩니다.

**클로즈 루프(Closed-loop)**: 알고리즘의 출력(조향, 가속)이 시뮬레이션 환경에 피드백되어 다음 센서 데이터가 바뀝니다. 실제 주행에 가까운 방식이며, "이 시나리오에서 내 스택이 올바르게 반응하는가"를 검증할 수 있습니다.

회귀 테스트(Regression Test)는 코드가 바뀔 때마다 이 클로즈 루프를 자동으로 돌려서 이전보다 성능이 떨어지지 않았는지 확인하는 작업입니다.

---

## 2. 전체 파이프라인 구조

```
[1] py123d          — 데이터셋 표준화 (Arrow)
        ↓
[2] FiftyOne        — 테스트 시나리오 큐레이션
        ↓
[3] DORA            — 자율주행 스택 실행 (Arrow)
        ↓
[4] Rerun           — 실행 결과 시각화 (Arrow IPC)
```

각 단계가 Arrow 포맷을 공유하기 때문에 단계 사이에 변환이 없습니다. 파이프라인이 하나의 거대한 Arrow 고속도로 위에서 동작합니다.

---

## 3. 각 단계별 역할

### 1단계: 시나리오 풀 구성 (`py123d`)

`py123d`로 nuScenes, Waymo, 사내 수집 데이터를 공통 Arrow 스키마로 통합합니다. 이 시점에서 모든 데이터셋은 동일한 좌표계, 동일한 타임스탬프 스트림 구조를 갖습니다.

회귀 테스트에 쓸 시나리오 풀은 여기서 만들어집니다. 특정 날씨·시간대·교통 상황 등 조건을 기준으로 수천 개의 주행 클립이 Arrow 포맷으로 대기합니다.

### 2단계: 테스트 시나리오 큐레이션 (`FiftyOne`)

모든 클립을 다 돌릴 필요는 없습니다. **FiftyOne**으로 테스트할 시나리오를 선별합니다.

- 이전 버전에서 실패한 케이스
- 특정 엣지 케이스 조건(야간, 역광, 보행자 밀집)
- 모델 신뢰도가 낮았던 프레임이 포함된 클립

선별된 시나리오는 DORA가 읽을 수 있는 Arrow 포맷 재생 목록으로 내보냅니다.

### 3단계: 자율주행 스택 실행 (`DORA`)

**DORA**는 선별된 시나리오를 Arrow 메시지로 재생하면서 자율주행 스택을 실제로 구동합니다.

```yaml
nodes:
  - id: scenario-player
    path: ./scenario_player.py
    inputs:
      tick: dora/timer/millis/100
    outputs:
      - lidar          # Arrow 포맷 포인트 클라우드
      - camera_front   # Arrow 포맷 이미지
      - gt_boxes       # Ground Truth 바운딩 박스

  - id: perception
    path: ./perception_stack.py
    inputs:
      lidar: scenario-player/lidar
      camera: scenario-player/camera_front
    outputs:
      - pred_boxes     # 예측 바운딩 박스

  - id: evaluator
    path: ./evaluator.py
    inputs:
      pred: perception/pred_boxes
      gt: scenario-player/gt_boxes
    outputs:
      - metrics        # IoU, mAP 등 평가 지표
```

`scenario-player` 노드가 시나리오를 재생하면, `perception` 노드가 실시간으로 추론하고, `evaluator` 노드가 Ground Truth와 비교해 지표를 계산합니다. 모든 노드 간 통신은 Arrow이므로 직렬화 비용이 없습니다.

클로즈 루프 구조에서는 `scenario-player`가 `perception`의 출력(예측 경로, 제어 명령)을 받아 다음 프레임을 생성할 수도 있습니다. 알고리즘의 결정이 다음 장면에 반영되는 진짜 클로즈 루프가 됩니다.

### 4단계: 결과 시각화 및 비교 (`Rerun`)

**Rerun**도 Arrow IPC를 표준 전송 포맷으로 씁니다. DORA 노드에서 Rerun SDK를 호출하면 추가 변환 없이 결과가 바로 시각화됩니다.

타임라인에 Ground Truth 박스와 예측 박스를 겹쳐 놓고, 어느 시각에 어느 노드에서 오차가 발생했는지 프레임 단위로 확인할 수 있습니다. 회귀 테스트 결과를 리뷰할 때 숫자 지표만 보는 게 아니라, 실제 주행 장면을 재생하면서 확인할 수 있습니다.

---

## 4. Arrow가 파이프라인 전체를 관통한다는 것의 의미

이 파이프라인에서 Arrow는 단순한 빠른 포맷이 아닙니다. **각 툴이 같은 언어를 쓴다**는 의미입니다.

| 툴 | Arrow 활용 |
|----|-----------|
| py123d | 데이터셋을 Arrow 스키마로 표준화 |
| DORA | 노드 간 메시지를 Arrow로 전달 |
| Rerun | Arrow IPC로 시각화 데이터 수신 |

py123d에서 만들어진 Arrow 버퍼가 DORA 노드를 거쳐 Rerun까지 복사 없이 전달됩니다. 중간에 JSON 파싱도, Protobuf 역직렬화도 없습니다.

또한 파이프라인의 어느 단계가 바뀌어도 영향이 최소화됩니다. 새 센서가 추가되면 py123d 스키마만 업데이트하면 되고, 시각화 방식이 바뀌어도 DORA 노드 코드는 그대로입니다. 각 레이어가 Arrow 인터페이스로만 연결되어 있기 때문입니다.

---

## 5. 정리

```
데이터셋 표준화  →  시나리오 선별  →  스택 실행  →  결과 시각화
   py123d             FiftyOne          DORA           Rerun
  (Arrow)                             (Arrow)       (Arrow IPC)
```

클로즈 루프 회귀 테스트는 코드가 바뀔 때마다 "내 자율주행 스택이 이전보다 나빠지지 않았는가"를 자동으로 확인하는 안전망입니다. 그리고 이 안전망을 Arrow 하나로 꿰어놓으면, 테스트 파이프라인 자체의 오버헤드가 사라집니다. 데이터를 읽고, 실행하고, 시각화하는 모든 과정이 같은 메모리 포맷 위에서 끊김 없이 돌아갑니다.
