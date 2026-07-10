---
title: "Lanelet2 입문: 자율주행 지도를 처음 다루는 사람을 위한 안내"
date: 2026-05-11T10:00:00+09:00
draft: false
tags: ["자율주행", "HD맵", "Lanelet2", "ROS", "Autoware", "입문"]
categories: ["autonomous"]
description: "Lanelet2가 무엇인지, 왜 자율주행에서 쓰이는지, 어떤 구조로 되어 있는지 초보자도 이해할 수 있게 설명합니다."
---

## Lanelet2가 뭔가요?

자율주행 차량이 도로를 달리려면 GPS 좌표 이상의 정보가 필요합니다. "이 차선은 직진 전용이다", "여기서는 우회전이 금지다", "이 구간은 보행자 횡단보도다" 같은 **의미 정보(semantic information)**가 있어야 차가 올바른 판단을 내릴 수 있습니다.

**Lanelet2**는 이런 도로 정보를 컴퓨터가 이해할 수 있는 형태로 저장하는 **HD 맵 포맷**입니다. 독일 FZI 연구소에서 개발했고, ROS(Robot Operating System) 생태계에서 가장 많이 쓰입니다. Autoware, Apollo 같은 오픈소스 자율주행 스택이 Lanelet2를 기본 맵 포맷으로 사용합니다.

---

## 왜 일반 지도(네이버 지도, 구글 지도)로는 안 되나요?

일반 지도는 사람이 길을 찾는 용도입니다. "A에서 B까지 몇 분"을 알려주면 충분합니다.

자율주행 차량은 다릅니다. 차선 단위로 어디를 달려야 하는지, 신호등이 어디 있는지, 정지선이 정확히 어디인지를 **센티미터 단위**로 알아야 합니다. 일반 지도는 이런 정밀도를 제공하지 않습니다.

| | 일반 지도 | HD 맵 (Lanelet2) |
|---|---|---|
| 정밀도 | 수 미터 | 수 센티미터 |
| 차선 정보 | 없음 | 있음 |
| 신호등·정지선 위치 | 없음 | 있음 |
| 주행 가능 방향 | 없음 | 있음 |
| 용도 | 내비게이션 | 자율주행 경로 계획 |

---

## Lanelet2의 핵심 개념: Lanelet

Lanelet2에서 가장 중요한 개념은 **Lanelet**입니다.

Lanelet 하나는 **차량이 주행할 수 있는 차선 구간 하나**를 나타냅니다. 쉽게 말하면 "왼쪽 경계선 + 오른쪽 경계선 + 이 구간의 규칙"입니다.

```
왼쪽 경계선 (LineString)
─────────────────────────────────→
      ← 주행 방향 →
─────────────────────────────────→
오른쪽 경계선 (LineString)
```

예를 들어 3차선 도로라면 Lanelet이 3개 있고, 각각 독립적인 차선 구간을 표현합니다.

---

## Lanelet2의 구성 요소

Lanelet2 맵은 아래 4가지 기본 요소로 만들어집니다.

### 1. Point (점)

지도의 가장 작은 단위입니다. GPS 좌표(위도, 경도, 고도)로 이루어집니다.

```
Point: id=1, x=127.0, y=37.5, z=0.0
```

### 2. LineString (선)

Point들을 이어 만든 선입니다. 차선 경계선, 정지선, 보도 경계 등을 표현합니다.

```
LineString: id=10
  → Point(1) → Point(2) → Point(3)
```

LineString에는 **타입(type)** 속성이 붙습니다.

| type 값 | 의미 |
|---|---|
| `solid` | 실선 (차선 변경 불가) |
| `dashed` | 점선 (차선 변경 가능) |
| `stop_line` | 정지선 |
| `virtual` | 가상 경계 (교차로 내부 등) |

### 3. Lanelet (차선 구간)

앞서 설명한 핵심 요소입니다. 왼쪽 LineString과 오른쪽 LineString으로 이루어집니다.

```
Lanelet: id=100
  leftBound  → LineString(10)
  rightBound → LineString(11)
  attributes:
    location: urban
    turn_direction: straight
    speed_limit: 50
```

Lanelet끼리는 **앞뒤로 연결**되어 차량이 이동 가능한 경로 그래프를 만듭니다.

### 4. Area (영역)

Lanelet이 선형 구간을 표현한다면, Area는 **면적으로 된 공간**을 표현합니다. 주차장, 교차로 내부, 보행자 구역 등이 해당합니다.

---

## 전체 구조 한눈에 보기 (3계층 아키텍처)

Lanelet2 맵은 데이터를 논리적으로 분리하기 위해 **3계층(Layer) 구조**를 가집니다.

1. **Physical Layer**: `Point`, `LineString`처럼 도로의 실제 물리적 형상을 표현
2. **Relational Layer**: `Lanelet`, `Area`, `RegulatoryElement`처럼 차선과 교통 규칙의 관계를 표현
3. **Topological Layer**: 차량이 실제로 이동할 수 있는 경로를 연결한 **Routing Graph**(경로 그래프)

```
Map
├── Points          # GPS 좌표 점들
├── LineStrings     # 점들을 이은 선 (차선 경계, 정지선 등)
├── Lanelets        # 차선 구간 (왼쪽 선 + 오른쪽 선 + 속성)
│   ├── Lanelet A → Lanelet B → Lanelet C   (직진)
│   └── Lanelet A → Lanelet D               (우회전)
├── Areas           # 면적 공간 (주차장, 교차로 등)
└── RegulatoryElements  # 규제 정보 (신호등, 속도 제한, 우선순위 등)
```

---

## RegulatoryElement: 규칙을 붙이는 방법

Lanelet 자체는 차선의 모양만 담습니다. 신호등, 정지 의무, 속도 제한 같은 **규칙**은 **RegulatoryElement**로 따로 붙입니다.

예를 들어 신호등 규제는 이렇게 표현합니다.

```
RegulatoryElement: TrafficLight
  refers    → 신호등 위치 (LineString)
  ref_line  → 정지선 (LineString)
  applies   → Lanelet(100), Lanelet(101)
```

이렇게 하면 Lanelet 100, 101로 주행하는 차량은 이 신호등을 따라야 한다는 의미가 됩니다.

주요 RegulatoryElement 종류:

| 종류 | 의미 |
|---|---|
| `TrafficLight` | 신호등 |
| `TrafficSign` | 도로 표지판 |
| `SpeedLimit` | 속도 제한 |
| `RightOfWay` | 양보/우선 통행 |
| `AllWayStop` | 전방향 정지 |

---

## 파일 형식: OSM XML

Lanelet2 맵은 **.osm** 파일로 저장됩니다. 새로운 포맷을 발명하는 대신 OpenStreetMap이 쓰는 XML 스키마를 그대로 빌려 씁니다. OSM의 세 가지 기본 요소 `node`(점), `way`(선), `relation`(관계)이 각각 Lanelet2의 `Point`, `LineString`, `Lanelet`/`RegulatoryElement`에 대응합니다.

이 대응 관계가 실용적인 이유는 두 가지입니다. 첫째, OSM 생태계의 편집기(JOSM 등)와 파서를 그대로 재사용할 수 있어 도구를 처음부터 만들 필요가 없습니다. 둘째, `relation`이 다른 `relation`을 멤버로 참조할 수 있다는 OSM의 특성 덕분에, RegulatoryElement가 Lanelet을 참조하고 Lanelet이 다시 LineString을 참조하는 **계층적 참조 구조**를 별도 확장 없이 표현할 수 있습니다. 즉 Lanelet2가 OSM 포맷을 고른 것은 "익숙해서"가 아니라, 관계 기반 구조가 Lanelet2의 3계층 아키텍처와 자연스럽게 맞아떨어지기 때문입니다.

---

## Lanelet2를 어떻게 사용하나요?

Lanelet2는 공식 C++ 라이브러리와 Python 바인딩을 제공하며, 맵을 불러오면 곧바로 두 가지 핵심 기능을 쓸 수 있습니다.

**좌표 투영(Projection)**: `.osm` 파일에는 위도·경도로 된 GPS 좌표가 저장되어 있지만, 실제 주행 계획에는 미터 단위의 평면 좌표(local x, y)가 필요합니다. 맵을 불러올 때 기준점(Origin)을 지정하면 UTM 투영법 등으로 이 변환을 자동으로 처리합니다.

**경로 그래프 생성(Routing Graph)**: 맵을 불러오는 즉시 Lanelet 간의 연결 관계를 분석해 그래프를 구성하고, 여기에 국가별 교통 규칙(우측통행 여부, 차선 변경 허용 규칙 등)을 적용해 "이 Lanelet에서 저 Lanelet까지 갈 수 있는가"를 바로 질의할 수 있습니다. 이 부분이 Lanelet2와 OpenDRIVE의 결정적 차이입니다 — [OpenDRIVE vs Lanelet2 비교](../opendrive-vs-lanelet2/)에서 더 자세히 다룹니다.

Autoware Universe는 Lanelet2를 기본 맵 포맷으로 사용해 경로 계획, 신호등 인식, 차선 변경 판단에 직접 활용하며, ROS 환경에서는 `lanelet2_rviz_plugin`으로 맵을 시각화합니다.

---

## Lanelet2 맵은 어떻게 만드나요?

| 방법 | 설명 |
|---|---|
| **JOSM** | OpenStreetMap 편집기. Lanelet2 플러그인을 설치하면 맵을 직접 그릴 수 있음 |
| **Vector Map Builder** | Autoware 재단이 제공하는 웹 기반 맵 편집 도구 |
| **실측 데이터 변환** | LiDAR로 수집한 포인트 클라우드에서 반자동으로 생성 |
| **시뮬레이터 내보내기** | CARLA, LGSVL 등에서 Lanelet2 포맷으로 맵 내보내기 가능 |

---

## 정리

| 개념 | 한 줄 요약 |
|---|---|
| **Point** | GPS 좌표 하나 |
| **LineString** | 점들을 이은 선 (차선 경계, 정지선 등) |
| **Lanelet** | 주행 가능한 차선 구간 하나 (왼쪽 선 + 오른쪽 선 + 속성) |
| **Area** | 주차장·교차로처럼 면으로 표현되는 공간 |
| **RegulatoryElement** | 신호등·속도 제한 같은 규칙 |

Lanelet2는 처음에는 생소하게 느껴지지만, 핵심은 단순합니다. **차선 구간(Lanelet)들이 연결된 그래프** 위에서 자율주행 차량이 경로를 계획하고 규칙을 따른다는 것입니다.

다음 단계로는 실제 Lanelet2 라이브러리를 설치하고, 샘플 맵을 불러와서 Python으로 Lanelet 목록을 출력해보는 것을 추천합니다.

---

*관련 글: [자율주행 시뮬레이션을 위한 HD 맵 포맷: OpenDRIVE(XODR)와 Lanelet2](/docs/autonomous/hd-map-formats-xodr-lanelet2/), [OpenDRIVE 입문](/docs/autonomous/hd-map/opendrive-for-beginners/), [OpenDRIVE vs Lanelet2 비교](/docs/autonomous/hd-map/opendrive-vs-lanelet2/), [OpenSCENARIO 입문](/docs/autonomous/hd-map/openscenario-for-beginners/)*
