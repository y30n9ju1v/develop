---
title: "OpenSCENARIO 입문: 자율주행 시나리오를 처음 다루는 사람을 위한 안내"
date: 2026-05-11T14:00:00+09:00
draft: false
tags: ["자율주행", "OpenSCENARIO", "시뮬레이션", "ASAM", "시나리오", "입문"]
categories: ["자율주행"]
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

## 실제 예시: 앞차 급정거 시나리오

아래는 "자차가 일정 속도로 주행 중, 앞차가 급정거하는" 시나리오입니다.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<OpenSCENARIO>

  <FileHeader
    description="앞차 급정거 시나리오"
    author="test_engineer"
    revMajor="1"
    revMinor="0"
    date="2026-05-11T14:00:00"/>

  <!-- 재사용 파라미터 -->
  <!-- 참조 시 $ParamName 또는 ${ParamName} 형식을 쓰며, 시뮬레이터마다 다를 수 있음 -->
  <ParameterDeclarations>
    <ParameterDeclaration name="EgoSpeed" parameterType="double" value="60"/>
    <ParameterDeclaration name="LeadSpeed" parameterType="double" value="60"/>
  </ParameterDeclarations>

  <!-- 도로 맵 지정 -->
  <RoadNetwork>
    <LogicFile filepath="my_map.xodr"/>
  </RoadNetwork>

  <!-- 시나리오에 등장하는 객체 선언 -->
  <Entities>
    <ScenarioObject name="Ego">
      <Vehicle name="vehicle.tesla.model3" vehicleCategory="car">
        <BoundingBox>
          <Center x="1.5" y="0.0" z="0.9"/>
          <Dimensions width="2.1" length="4.5" height="1.8"/>
        </BoundingBox>
        <Performance maxSpeed="69.444" maxAcceleration="10.0" maxDeceleration="10.0"/>
        <Axles>
          <FrontAxle maxSteering="0.5" wheelDiameter="0.6" trackWidth="1.8" positionX="3.1" positionZ="0.3"/>
          <RearAxle maxSteering="0.0" wheelDiameter="0.6" trackWidth="1.8" positionX="0.0" positionZ="0.3"/>
        </Axles>
        <Properties/>
      </Vehicle>
    </ScenarioObject>
    <ScenarioObject name="LeadVehicle">
      <Vehicle name="vehicle.audi.a2" vehicleCategory="car">
        <BoundingBox>
          <Center x="1.5" y="0.0" z="0.9"/>
          <Dimensions width="2.0" length="4.2" height="1.8"/>
        </BoundingBox>
        <Performance maxSpeed="69.444" maxAcceleration="10.0" maxDeceleration="10.0"/>
        <Axles>
          <FrontAxle maxSteering="0.5" wheelDiameter="0.6" trackWidth="1.8" positionX="3.1" positionZ="0.3"/>
          <RearAxle maxSteering="0.0" wheelDiameter="0.6" trackWidth="1.8" positionX="0.0" positionZ="0.3"/>
        </Axles>
        <Properties/>
      </Vehicle>
    </ScenarioObject>
  </Entities>

  <Storyboard>

    <!-- 1. 초기 상태: 각 차량의 시작 위치와 속도 -->
    <Init>
      <Actions>
        <!-- 자차(Ego) 초기화 -->
        <Private entityRef="Ego">
          <PrivateAction>
            <TeleportAction>
              <Position>
                <LanePosition roadId="1" laneId="-1" s="10.0"/>
              </Position>
            </TeleportAction>
          </PrivateAction>
          <PrivateAction>
            <LongitudinalAction>
              <SpeedAction>
                <SpeedActionDynamics dynamicsShape="step" value="0" dynamicsDimension="time"/>
                <SpeedActionTarget>
                  <AbsoluteTargetSpeed value="$EgoSpeed"/>
                </SpeedActionTarget>
              </SpeedAction>
            </LongitudinalAction>
          </PrivateAction>
        </Private>

        <!-- 앞차(LeadVehicle) 초기화 -->
        <Private entityRef="LeadVehicle">
          <PrivateAction>
            <TeleportAction>
              <Position>
                <LanePosition roadId="1" laneId="-1" s="50.0"/>
              </Position>
            </TeleportAction>
          </PrivateAction>
          <PrivateAction>
            <LongitudinalAction>
              <SpeedAction>
                <SpeedActionDynamics dynamicsShape="step" value="0" dynamicsDimension="time"/>
                <SpeedActionTarget>
                  <AbsoluteTargetSpeed value="$LeadSpeed"/>
                </SpeedActionTarget>
              </SpeedAction>
            </LongitudinalAction>
          </PrivateAction>
        </Private>
      </Actions>
    </Init>

    <!-- 2. 시나리오 전개 -->
    <Story name="MainStory">
      <Act name="BrakeAct">
        <ManeuverGroup name="LeadVehicleGroup" maximumExecutionCount="1">
          <Actors selectTriggeringEntities="false">
            <EntityRef entityRef="LeadVehicle"/>
          </Actors>

          <Maneuver name="BrakeManeuver">
            <Event name="BrakeEvent" priority="overwrite">

              <!-- 무엇을: 앞차가 급정거 (속도를 0으로 줄임) -->
              <Action name="BrakeAction">
                <PrivateAction>
                  <LongitudinalAction>
                    <SpeedAction>
                      <SpeedActionDynamics
                        dynamicsShape="linear"
                        value="8.0"
                        dynamicsDimension="rate"/>
                      <SpeedActionTarget>
                        <AbsoluteTargetSpeed value="0"/>
                      </SpeedActionTarget>
                    </SpeedAction>
                  </LongitudinalAction>
                </PrivateAction>
              </Action>

              <!-- 언제: 자차와 앞차의 거리가 30m 이하가 되면 -->
              <StartTrigger>
                <ConditionGroup>
                  <Condition name="DistanceCondition" delay="0" conditionEdge="rising">
                    <ByEntityCondition>
                      <TriggeringEntities triggeringEntitiesRule="any">
                        <EntityRef entityRef="Ego"/>
                      </TriggeringEntities>
                      <EntityCondition>
                        <RelativeDistanceCondition
                          entityRef="LeadVehicle"
                          relativeDistanceType="longitudinal"
                          value="30.0"
                          freespace="true"
                          rule="lessThan"/>
                      </EntityCondition>
                    </ByEntityCondition>
                  </Condition>
                </ConditionGroup>
              </StartTrigger>

            </Event>
          </Maneuver>
        </ManeuverGroup>

        <StartTrigger/>
      </Act>
    </Story>

    <!-- 3. 종료 조건: 시뮬레이션 시작 후 30초가 지나면 종료 -->
    <StopTrigger>
      <ConditionGroup>
        <Condition name="EndTime" delay="0" conditionEdge="rising">
          <ByValueCondition>
            <SimulationTimeCondition value="30" rule="greaterThan"/>
          </ByValueCondition>
        </Condition>
      </ConditionGroup>
    </StopTrigger>

  </Storyboard>
</OpenSCENARIO>
```

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

CARLA ScenarioRunner를 설치했다면 아래 명령으로 시나리오를 실행할 수 있습니다.

```bash
# ScenarioRunner 실행
python scenario_runner.py \
  --openscenario my_scenario.xosc \
  --reloadWorld
```

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

*관련 글: [자율주행 시뮬레이션을 위한 HD 맵 포맷: OpenDRIVE(XODR)와 Lanelet2](/docs/autonomous/hd-map-formats-xodr-lanelet2/), [OpenDRIVE 입문](/docs/autonomous/opendrive-for-beginners/), [Lanelet2 입문](/docs/autonomous/lanelet2-for-beginners/), [OpenDRIVE vs Lanelet2 비교](/docs/autonomous/opendrive-vs-lanelet2/)*
