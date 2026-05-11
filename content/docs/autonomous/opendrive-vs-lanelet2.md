---
title: "OpenDRIVE vs Lanelet2: 두 HD 맵 포맷 비교 분석"
date: 2026-05-11T18:00:00+09:00
draft: false
tags: ["자율주행", "HD맵", "OpenDRIVE", "XODR", "Lanelet2", "비교", "입문"]
categories: ["자율주행"]
description: "자율주행의 두 대표 HD 맵 포맷 OpenDRIVE와 Lanelet2를 초보자도 이해할 수 있도록 개념, 구조, 강점, 사용처를 비교 분석합니다."
---

## 들어가며

자율주행을 공부하다 보면 HD 맵 포맷으로 **OpenDRIVE**와 **Lanelet2** 두 가지를 자주 접하게 됩니다. 둘 다 도로 정보를 담는 파일인데, 왜 두 가지가 존재하는지, 어떤 상황에서 무엇을 써야 하는지 처음에는 헷갈립니다.

이 글에서는 두 포맷을 같은 기준으로 나란히 비교해서 차이를 명확하게 정리합니다.

---

## 한 줄 요약

| | OpenDRIVE | Lanelet2 |
|---|---|---|
| **한 줄 요약** | 도로의 **형상**을 정밀하게 그리는 포맷 | 도로에서 **어떻게 주행할지**를 표현하는 포맷 |

---

## 탄생 배경

### OpenDRIVE
2004년 독일 시뮬레이션 회사 VIRES가 개발했습니다. 처음부터 **시뮬레이터용 도로 모델**을 목적으로 만들어졌습니다. 이후 ASAM이 인수해 국제 표준으로 발전시켰습니다. 현재 버전은 1.8입니다.

### Lanelet2
2018년 독일 FZI 연구소가 개발했습니다. ROS 기반 자율주행 연구 환경에서 **경로 계획과 행동 판단**에 필요한 정보를 효율적으로 표현하기 위해 만들어졌습니다. 이전 버전인 Lanelet(2014)의 후속작입니다.

---

## 도로를 표현하는 방식이 다르다

두 포맷의 가장 근본적인 차이는 **도로를 어떻게 표현하느냐**입니다.

### OpenDRIVE: 수학 곡선 기반

도로의 중심선(Reference Line)을 **수학 함수**로 표현합니다. 직선, 원호, 클로소이드(나선)를 조합해서 어떤 도로 형상도 정밀하게 표현할 수 있습니다.

```
기준선(Reference Line)을 수식으로 정의
→ 양쪽에 차선을 번호로 배치 (-1, -2, +1, +2...)
→ 각 차선의 폭, 경계선 종류를 기준선 위치(s값)에 따라 기술
```

장점: GPS 좌표를 일일이 찍지 않아도 수식 몇 줄로 수백 미터 도로를 정확하게 표현할 수 있습니다.

### Lanelet2: GPS 좌표 점 기반

차선 경계를 **실제 GPS 좌표 점들의 나열**로 표현합니다. 왼쪽 경계선과 오른쪽 경계선의 좌표를 직접 찍어서 차선 구간(Lanelet) 하나를 만듭니다.

```
왼쪽 경계선: [좌표1, 좌표2, 좌표3, ...]
오른쪽 경계선: [좌표A, 좌표B, 좌표C, ...]
→ 두 선 사이가 Lanelet 하나
```

장점: LiDAR로 실측한 데이터를 그대로 쓸 수 있어 실제 도로를 빠르게 반영할 수 있습니다.

---

## 핵심 구성 요소 비교

### 기본 단위

| | OpenDRIVE | Lanelet2 |
|---|---|---|
| 최소 단위 | Point (s, t 좌표) | Point (GPS 좌표) |
| 선 단위 | 수식(geometry) | LineString (점의 나열) |
| 구간 단위 | Road + LaneSection | Lanelet |
| 영역 단위 | Junction | Area |
| 규칙 단위 | Signal, Object | RegulatoryElement |

### 같은 도로를 표현하는 방식 차이

왕복 2차선, 길이 100m의 직선 도로를 예로 들면:

**OpenDRIVE 방식**
```xml
<road length="100.0" id="1">
  <planView>
    <geometry s="0" x="0" y="0" hdg="0" length="100">
      <line/>   <!-- 직선이므로 수식 한 줄 -->
    </geometry>
  </planView>
  <lanes>
    <laneSection s="0">
      <left>
        <lane id="1" type="driving">
          <width a="3.5"/>   <!-- 차선 폭 3.5m -->
        </lane>
      </left>
      <right>
        <lane id="-1" type="driving">
          <width a="3.5"/>
        </lane>
      </right>
    </laneSection>
  </lanes>
</road>
```

**Lanelet2 방식**
```xml
<!-- 왼쪽 경계선: 실제 좌표를 일일이 찍음 -->
<way id="10">
  <nd ref="1"/>  <!-- (0, 3.5) -->
  <nd ref="2"/>  <!-- (50, 3.5) -->
  <nd ref="3"/>  <!-- (100, 3.5) -->
</way>

<!-- 오른쪽 경계선 -->
<way id="11">
  <nd ref="4"/>  <!-- (0, 0) -->
  <nd ref="5"/>  <!-- (50, 0) -->
  <nd ref="6"/>  <!-- (100, 0) -->
</way>

<!-- Lanelet: 두 경계선으로 차선 구간 정의 -->
<relation id="100">
  <member type="way" ref="10" role="left"/>
  <member type="way" ref="11" role="right"/>
  <tag k="type" v="lanelet"/>
</relation>
```

직선 도로 하나를 표현하는 데 OpenDRIVE는 수식 한 줄, Lanelet2는 좌표 여러 개가 필요합니다. 하지만 복잡한 실제 도로에서는 Lanelet2가 실측 데이터를 그대로 쓸 수 있어 오히려 편합니다.

---

## 강점과 약점

### OpenDRIVE

**강점**
- 도로 형상을 수학적으로 정밀하게 표현
- 파일 크기가 작음 (수식으로 표현하므로)
- 대부분의 상용 시뮬레이터가 지원
- 경사, 횡단 경사 등 3D 정보 표현이 강함

**약점**
- 학습 곡선이 가파름 (s좌표계, 수식 이해 필요)
- 실제 도로 데이터를 직접 넣기 어려움
- 경로 계획 알고리즘과 바로 연동하기 불편
- ROS 생태계 지원이 약함

### Lanelet2

**강점**
- ROS 생태계와 자연스럽게 연동
- 실측 LiDAR 데이터를 바로 활용 가능
- 경로 계획 라이브러리가 내장되어 있음
- 구조가 직관적 (좌표 기반)
- Autoware, Apollo 등 오픈소스 스택이 기본 지원

**약점**
- 도로 형상 표현이 덜 정밀 (좌표 밀도에 의존)
- 복잡한 교차로 표현이 어려울 수 있음
- 상용 시뮬레이터 지원이 OpenDRIVE보다 적음
- 파일 크기가 커질 수 있음

---

## 규칙(신호등·속도 제한)을 표현하는 방식

도로의 규칙 정보를 표현하는 방식도 두 포맷이 다릅니다.

### OpenDRIVE: Signal과 Object

신호등, 속도 제한 표지판 등을 `signal` 요소로 표현합니다. 도로 기준선 위의 위치(s값)와 횡방향 오프셋(t값)으로 위치를 지정합니다.

```xml
<signals>
  <signal s="150.0" t="-2.0" id="1" name="SpeedLimit"
          dynamic="no" orientation="+" zOffset="2.0"
          type="274" subtype="50" value="50" unit="km/h"
          height="0.6" width="0.6"/>
</signals>
```

어느 차선에 적용되는지는 `validity` 요소로 지정하며, 적용 범위가 복잡할수록 표현이 번거로워집니다.

### Lanelet2: RegulatoryElement

신호등, 속도 제한 등을 **RegulatoryElement**로 표현하고 관련 Lanelet에 직접 연결합니다. "이 Lanelet을 달리는 차는 이 규칙을 따른다"는 관계가 명확합니다.

| RegulatoryElement | 의미 |
|---|---|
| `TrafficLight` | 신호등 + 정지선 |
| `TrafficSign` | 도로 표지판 |
| `SpeedLimit` | 속도 제한 |
| `RightOfWay` | 양보/우선 통행 |
| `AllWayStop` | 전방향 정지 |

```xml
<relation id="200">
  <member type="way" ref="50" role="refers"/>      <!-- 신호등 위치 -->
  <member type="way" ref="51" role="ref_line"/>    <!-- 정지선 -->
  <member type="relation" ref="100" role="refers"/> <!-- 적용 Lanelet -->
  <tag k="type" v="regulatory_element"/>
  <tag k="subtype" v="traffic_light"/>
</relation>
```

경로 계획 알고리즘이 Lanelet을 순회하면서 RegulatoryElement를 자동으로 확인할 수 있어 코드 연동이 훨씬 편합니다.

---

## 경로 계획에서의 차이

자율주행에서 가장 중요한 작업 중 하나인 **경로 계획**에서 두 포맷의 차이가 극명하게 드러납니다.

### OpenDRIVE로 경로 계획하기

OpenDRIVE 자체에는 경로 계획 기능이 없습니다. 도로 형상 데이터를 읽어서 별도의 그래프로 변환한 후 A*나 Dijkstra 같은 알고리즘을 적용해야 합니다.

```
OpenDRIVE 파일
→ 파서로 Road, Lane 구조 읽기
→ 직접 그래프 구성 (Lane을 노드, Lane 연결을 엣지로)
→ 경로 탐색 알고리즘 적용
```

### Lanelet2로 경로 계획하기

Lanelet2는 **처음부터 경로 계획을 위해 설계**되었습니다. 공식 라이브러리에 경로 계획 기능이 내장되어 있어, 맵을 불러온 뒤 바로 경로 탐색이 가능합니다.

```
Lanelet2 파일
→ load()로 맵 불러오기
→ RoutingGraph 자동 생성 (Lanelet 연결 관계 분석)
→ getRoute()로 즉시 경로 탐색
```

자세한 코드는 아래 "코드로 다루는 방법" 섹션을 참고하세요.

---

## 코드로 다루는 방법

### OpenDRIVE: scenariogeneration + CARLA

Python `scenariogeneration` 라이브러리로 `.xodr` 파일을 코드로 생성할 수 있습니다.

```python
from scenariogeneration import xodr

# 직선 도로 생성 후 파일로 저장
road = xodr.create_road([xodr.Line(200)], id=1, left_lanes=1, right_lanes=2)

odr = xodr.OpenDrive("my_road")
odr.add_road(road)
odr.adjust_roads_and_lanes()
odr.write_xml("my_road.xodr")
```

CARLA에서는 내장 샘플 맵을 불러오거나, 현재 맵을 OpenDRIVE 형식으로 내보낼 수 있습니다.

```python
import carla

client = carla.Client("localhost", 2000)
# CARLA 내장 샘플 맵 불러오기
world = client.load_world("Town03")
# 현재 맵을 OpenDRIVE 형식으로 내보내기
print(world.get_map().to_opendrive()[:300])
```

### Lanelet2: Python 라이브러리

공식 Python 바인딩으로 맵을 불러오고 경로를 탐색합니다.

```python
import lanelet2
from lanelet2.io import load
from lanelet2.projection import UtmProjector
from lanelet2.routing import RoutingGraph

# 맵 불러오기
projector = UtmProjector(lanelet2.io.Origin(37.5, 127.0))
map = load("my_map.osm", projector)

# 모든 Lanelet 출력
for lanelet in map.laneletLayer:
    print(f"id={lanelet.id}, speed_limit={lanelet.attributes.get('speed_limit')}")

# 경로 탐색
traffic_rules = lanelet2.traffic_rules.create(
    lanelet2.traffic_rules.Locations.Germany,
    lanelet2.traffic_rules.Participants.Vehicle)
graph = RoutingGraph(map, traffic_rules)
route = graph.getRoute(map.laneletLayer[100], map.laneletLayer[200])
```

---

## 맵 제작 도구 비교

| | OpenDRIVE | Lanelet2 |
|---|---|---|
| **GUI 편집기** | RoadRunner (MathWorks, 유료) | JOSM + Lanelet2 플러그인 (무료) |
| **웹 기반 편집기** | - | Vector Map Builder (Autoware 재단) |
| **코드로 생성** | `scenariogeneration` (Python) | 직접 OSM XML 작성 |
| **시뮬레이터 내보내기** | CARLA, SUMO | CARLA, LGSVL |
| **실측 데이터 활용** | 어려움 | LiDAR 포인트 클라우드에서 반자동 생성 가능 |

---

## 어떤 시뮬레이터가 무엇을 쓰나요?

| 시뮬레이터 | 기본 포맷 | 비고 |
|---|---|---|
| **CARLA** | OpenDRIVE | 내장 맵이 모두 .xodr |
| **SUMO** | OpenDRIVE | net.xml로 변환해서 사용 |
| **Autoware** | Lanelet2 | 기본 맵 포맷 |
| **Apollo** | 자체 포맷 (Apollo HD Map) | 내부적으로 protobuf 기반 자체 포맷 사용. OpenDRIVE 변환 파이프라인 제공 |
| **LGSVL** | OpenDRIVE + Lanelet2 | 둘 다 지원 |
| **dSPACE** | OpenDRIVE | 상용 |
| **IPG CarMaker** | OpenDRIVE | 상용 |

---

## 변환은 가능한가요?

두 포맷 사이의 변환 도구가 존재하지만, **완벽한 변환은 어렵습니다**. 표현 방식이 근본적으로 달라서 정보 손실이 발생할 수 있습니다.

| 변환 방향 | 도구 | 주의사항 |
|---|---|---|
| OpenDRIVE → Lanelet2 | `opendrive2lanelet` (Python) | 복잡한 교차로에서 수동 수정 필요 |
| Lanelet2 → OpenDRIVE | 공식 도구 없음, 커스텀 스크립트 | 형상 정밀도 손실 가능 |

```bash
# opendrive2lanelet 설치 및 변환
pip install opendrive2lanelet
opendrive2lanelet --opendrive input.xodr --lanelet2 output.osm
```

> **주의**: `opendrive2lanelet` 패키지는 현재 활발히 유지보수되지 않습니다. 2025년 기준 가장 현실적인 변환 방법은 MathWorks RoadRunner에서 두 포맷을 모두 내보내거나, CARLA 맵을 기준으로 각각 내보내는 방식입니다.

---

## 무엇을 선택해야 할까요?

아래 질문에 따라 선택하세요.

**OpenDRIVE를 선택하세요, 만약:**
- CARLA, SUMO 같은 시뮬레이터를 주로 사용한다
- 도로 형상의 정밀도가 중요하다 (경사, 곡률 등)
- 상용 시뮬레이터 환경에서 일한다
- 시나리오 기반 테스트(OpenSCENARIO)를 많이 한다

**Lanelet2를 선택하세요, 만약:**
- Autoware, ROS 기반 자율주행 스택을 개발한다
- 실제 도로를 LiDAR로 측량해서 맵을 만든다
- 경로 계획, 행동 판단 알고리즘을 직접 개발한다
- 오픈소스 환경에서 빠르게 프로토타입을 만든다

**둘 다 알아야 합니다, 만약:**
- 자율주행 시스템 전체를 개발한다
- 시뮬레이션(OpenDRIVE)과 실차 테스트(Lanelet2)를 모두 담당한다

---

## 정리

| 비교 항목 | OpenDRIVE | Lanelet2 |
|---|---|---|
| **설계 목적** | 시뮬레이터용 도로 모델 | 경로 계획 및 행동 판단 |
| **형상 표현** | 수학 곡선 (정밀) | GPS 좌표 나열 (직관적) |
| **파일 형식** | XML (.xodr) | OSM XML (.osm) |
| **표준 관리** | ASAM (국제 표준) | 오픈소스 (FZI) |
| **경로 계획** | 직접 구현 필요 | 라이브러리 내장 |
| **ROS 연동** | 별도 변환 필요 | 네이티브 지원 |
| **주요 사용처** | CARLA, SUMO, 상용 시뮬레이터 | Autoware, Apollo |
| **학습 난이도** | 높음 (s좌표계, 수식) | 낮음 (GPS 좌표 기반) |

두 포맷은 경쟁 관계가 아니라 **서로 다른 문제를 해결하는 보완 관계**입니다. 시뮬레이터에서 도로를 정밀하게 표현할 때는 OpenDRIVE, 실제 도로에서 차량이 어떻게 주행할지 결정할 때는 Lanelet2가 적합합니다. 자율주행을 깊이 다루다 보면 결국 두 가지를 모두 다루게 됩니다.

---

*관련 글: [OpenDRIVE 입문](/docs/autonomous/opendrive-for-beginners/), [Lanelet2 입문](/docs/autonomous/lanelet2-for-beginners/), [OpenSCENARIO 입문](/docs/autonomous/openscenario-for-beginners/)*
