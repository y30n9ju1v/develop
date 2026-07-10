---
title: "OpenSCENARIO 입문: 자율주행 시나리오를 처음 다루는 사람을 위한 안내"
date: 2026-05-11T14:00:00+09:00
draft: false
tags: ["자율주행", "OpenSCENARIO", "시뮬레이션", "ASAM", "시나리오", "입문"]
categories: ["autonomous"]
description: "OpenSCENARIO가 무엇인지, 왜 자율주행 시뮬레이션에서 쓰이는지, 어떤 구조로 시나리오를 표현하는지 초보자도 이해할 수 있게 설명합니다."
---

## OpenSCENARIO가 뭔가요?

자율주행 차량을 개발하려면 수없이 많은 상황을 테스트해야 합니다. "앞차가 갑자기 끼어들면?", "보행자가 횡단보도가 아닌 곳에서 튀어나오면?", "옆 차선 차가 급정거하면?" 같은 상황들을 실제 도로에서 전부 테스트하는 건 위험하고 비용도 막대합니다.

이런 **테스트 시나리오를 표준화된 형식으로 기술하는 언어**가 **OpenSCENARIO**입니다. ASAM(Automotive Standards and Methods)이 관리하는 국제 표준으로, CARLA, SUMO, IPG CarMaker, dSPACE 등 주요 시뮬레이터들이 지원합니다.

한 줄 요약: **"어떤 상황에서 어떤 일이 벌어지는지"를 XML로 적어두는 표준 형식**입니다.

---

## 왜 표준 형식이 필요한가요?

시뮬레이터마다 시나리오를 정의하는 방식이 다르면 문제가 생깁니다.

- A사가 CARLA용으로 만든 시나리오를 B사의 시뮬레이터에서 재사용할 수 없음
- 시뮬레이터를 교체하면 시나리오를 처음부터 다시 만들어야 함
- 규제 기관이 "이 시나리오를 통과해야 한다"고 요구할 때 기준이 모호해짐

OpenSCENARIO는 이 문제를 해결합니다. 한 번 작성한 시나리오를 여러 시뮬레이터에서 실행할 수 있고, 업계가 공통된 언어로 소통할 수 있습니다.

---

## OpenSCENARIO의 버전

현재 두 가지 주요 버전이 있습니다.

| 버전 | 특징 |
|---|---|
| **1.x** | XML 기반. 현재 업계에서 가장 널리 쓰임. CARLA, Autoware 등이 지원 |
| **2.x (OSC2)** | 장황한 XML을 버리고, Python이나 C++처럼 코딩하기 편한 **DSL(Domain Specific Language)** 구조를 채택해 개발자 친화적으로 변했습니다. 더 표현력이 강하지만 아직 도입 초기입니다. |

이 글에서는 실무에서 많이 쓰이는 **1.x 버전**을 기준으로 설명합니다.

---

## OpenSCENARIO의 핵심 개념

### 시나리오는 "언제", "누가", "무엇을 한다"

모든 시나리오는 결국 이 세 가지로 이루어집니다.

- **언제(Trigger)**: 어떤 조건이 충족되면
- **누가(Entity)**: 어떤 차량 또는 보행자가
- **무엇을(Action)**: 어떤 행동을 한다

예: *"자차가 교차로 50m 앞에 도달하면(Trigger), 옆 차선 차량이(Entity), 갑자기 끼어든다(Action)"*

---

## 파일 구조

OpenSCENARIO 1.x 파일은 크게 5개 섹션으로 나뉩니다.

```
OpenSCENARIO
├── FileHeader          # 파일 정보 (작성자, 버전, 날짜)
├── ParameterDeclarations  # 재사용 가능한 파라미터 정의
├── CatalogLocations    # 차량/보행자/도로 카탈로그 위치
├── RoadNetwork         # 사용할 도로 맵 (Lanelet2, OpenDRIVE 등)
└── Storyboard          # 실제 시나리오 내용 ← 핵심
    ├── Init            # 초기 상태 (각 객체의 시작 위치, 속도)
    └── Story           # 시나리오 전개
        └── Act
            ├── ManeuverGroup  # 누가
            │   └── Maneuver
            │       └── Event
            │           ├── Action  # 무엇을
            │           └── StartTrigger  # 언제
            └── StartTrigger
```

---

## 실제 예시: 앞차 급정거 시나리오는 어떻게 조립되나요

"자차가 일정 속도로 주행 중, 앞차가 급정거하는" 시나리오를 앞서 본 5개 섹션에 맞춰 채우면 이렇게 됩니다.

**ParameterDeclarations**에는 `EgoSpeed`, `LeadSpeed` 같은 재사용 값을 선언합니다. 본문에서는 이 값을 `$EgoSpeed`처럼 참조하는데, 값 자체를 하드코딩하지 않고 파라미터로 빼두면 같은 시나리오 구조로 속도만 다른 변형을 여러 개 만들 수 있습니다.

**Entities**에는 등장하는 모든 객체(자차 `Ego`, 앞차 `LeadVehicle`)를 선언합니다. 각 `Vehicle`은 바운딩 박스 크기, 최대 속도/가감속, 축거 같은 물리 제원까지 명시해야 합니다 — 시뮬레이터가 충돌 판정이나 동역학 계산을 하려면 이 값들이 필요하기 때문입니다.

**Storyboard**가 시나리오의 실제 본문이며, 세 단계로 나뉩니다.

1. **Init**: 두 차량을 `TeleportAction`으로 초기 위치(`LanePosition`으로 도로 ID·차선·s좌표 지정)에 배치하고, `SpeedAction`으로 초기 속도를 설정합니다. "시나리오가 시작되는 순간의 스냅샷"을 정의하는 구간입니다.
2. **Story → Act → ManeuverGroup → Maneuver → Event**: 실제 전개입니다. `Actors`로 "누가"(`LeadVehicle`)를 지정하고, `Action`으로 "무엇을"(속도를 0으로 줄이는 `SpeedAction`, 감속률 8.0으로 선형 감속)을 지정하고, `StartTrigger`로 "언제"(자차와의 종방향 거리가 `RelativeDistanceCondition`으로 30m 미만이 되는 순간)를 지정합니다. 이 다섯 단계 중첩이 XML을 장황하게 만드는 지점이지만, 각 계층은 "이 동작 묶음을 누가·언제·어떤 우선순위로 실행하는가"를 각각 독립적으로 제어하기 위한 것입니다 — 예를 들어 `priority="overwrite"`는 같은 Event가 다시 트리거되면 이전 실행을 덮어쓰라는 지정입니다.
3. **StopTrigger**: 시나리오 전체의 종료 조건입니다. 여기서는 시뮬레이션 시작 30초 후 종료하도록 `SimulationTimeCondition`을 씁니다.

이 파일 하나가 "언제(30m 이내 접근), 누가(앞차), 무엇을(급정거)"이라는 한 문장을 5단 중첩 구조로 정확하게, 그러나 장황하게 표현하고 있는 셈입니다. 이 장황함을 코드에 가까운 문법으로 줄이려는 시도가 뒤에서 다룰 [OpenSCENARIO 2.0](../openscenario-2-for-beginners/)입니다.

---

## 주요 개념 정리

### Entity (객체)

시나리오에 등장하는 모든 참여자입니다.

| 종류 | 예시 |
|---|---|
| `Vehicle` | 자차(Ego), 주변 차량 |
| `Pedestrian` | 보행자 |
| `MiscObject` | 장애물, 교통 콘 |

### Action (행동)

Entity가 취하는 행동입니다.

| 분류 | Action | 설명 |
|---|---|---|
| 종방향 | `SpeedAction` | 속도 변경 |
| 횡방향 | `LaneChangeAction` | 차선 변경 |
| 위치 | `TeleportAction` | 순간 이동 (초기화에 사용) |
| 가시성 | `VisibilityAction` | 객체 표시/숨김 |
| 인프라 | `TrafficSignalAction` | 신호등 상태 변경 |

### Trigger (조건)

Action이 시작되는 조건입니다.

| 종류 | 설명 | 예시 |
|---|---|---|
| `SimulationTimeCondition` | 시뮬레이션 경과 시간 | 10초 후 |
| `RelativeDistanceCondition` | 두 객체 사이 거리 | 앞차와 30m 이하 |
| `SpeedCondition` | 특정 속도 도달 | 자차가 50km/h 초과 |
| `ReachPositionCondition` | 특정 위치 도달 | 교차로 진입 |
| `CollisionCondition` | 충돌 발생 | 충돌 시 종료 |

---

## OpenSCENARIO를 실행하는 시뮬레이터

| 시뮬레이터 | 지원 버전 | 비고 |
|---|---|---|
| **CARLA** | 1.x | ScenarioRunner로 실행 |
| **Autoware** | 1.x | scenario_simulator_v2 사용 |
| **SUMO** | 1.x | libsumo 연동 |
| **dSPACE** | 1.x, 2.x | 상용 |
| **IPG CarMaker** | 1.x | 상용 |

오픈소스 환경에서 가장 접근하기 쉬운 조합은 **CARLA + ScenarioRunner**입니다.

---

## CARLA에서 실행해보기

CARLA ScenarioRunner는 `.xosc` 파일 경로를 인자로 받아 그대로 재생하는 방식으로 동작합니다. 별도의 통합 작업 없이 표준 파일 하나만 넘기면 되는 이 단순함이 OpenSCENARIO가 여러 시뮬레이터에서 공통으로 채택되는 이유이기도 합니다 — 시뮬레이터 입장에서는 자체 시나리오 포맷을 설계할 필요 없이 이 XML을 파싱하는 로더 하나만 구현하면 됩니다.

---

## 정리

| 개념 | 한 줄 요약 |
|---|---|
| **OpenSCENARIO** | 자율주행 테스트 시나리오를 표준 XML로 기술하는 형식 |
| **Entity** | 시나리오에 등장하는 차량, 보행자 등 |
| **Action** | Entity가 취하는 행동 (속도 변경, 차선 변경 등) |
| **Trigger** | Action이 시작되는 조건 (시간, 거리, 속도 등) |
| **Storyboard** | Init + Story + StopTrigger로 구성된 시나리오 본문 |

OpenSCENARIO의 핵심은 단순합니다. **"언제(Trigger), 누가(Entity), 무엇을 한다(Action)"** 이 세 가지를 XML로 조합하면 어떤 복잡한 상황도 표현할 수 있습니다. 처음에는 단순한 시나리오(앞차 급정거, 보행자 횡단)부터 작성해보고, 점차 조건을 복잡하게 만들어 가는 것을 추천합니다.

---

*관련 글: [자율주행 시뮬레이션을 위한 HD 맵 포맷: OpenDRIVE(XODR)와 Lanelet2](/docs/autonomous/hd-map-formats-xodr-lanelet2/), [OpenDRIVE 입문](/docs/autonomous/hd-map/opendrive-for-beginners/), [Lanelet2 입문](/docs/autonomous/hd-map/lanelet2-for-beginners/), [OpenDRIVE vs Lanelet2 비교](/docs/autonomous/hd-map/opendrive-vs-lanelet2/), [OpenSCENARIO 2.0 입문](/docs/autonomous/hd-map/openscenario-2-for-beginners/)*
