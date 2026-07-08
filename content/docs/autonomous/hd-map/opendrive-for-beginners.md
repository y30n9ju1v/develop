---
title: "OpenDRIVE 입문: 자율주행 도로 모델을 처음 다루는 사람을 위한 안내"
date: 2026-05-11T16:00:00+09:00
draft: false
tags: ["자율주행", "HD맵", "OpenDRIVE", "XODR", "ASAM", "시뮬레이션", "입문"]
categories: ["자율주행"]
description: "OpenDRIVE가 무엇인지, 왜 자율주행 시뮬레이션에서 쓰이는지, 어떤 구조로 도로를 표현하는지 초보자도 이해할 수 있게 설명합니다."
---

## OpenDRIVE가 뭔가요?

자율주행 시뮬레이터는 현실과 똑같은 도로 환경이 필요합니다. 차선의 폭, 도로의 곡률, 경사, 교차로 구조까지 정밀하게 표현해야 차량이 올바르게 주행할 수 있습니다.

**OpenDRIVE**는 이런 **도로의 기하학적 구조와 논리적 구조를 표현하는 표준 파일 포맷**입니다. ASAM(Automotive Standards and Methods)이 관리하며, 확장자는 `.xodr`을 사용합니다.

CARLA, SUMO, IPG CarMaker, Vires VTD 등 대부분의 주요 시뮬레이터가 OpenDRIVE를 기본 도로 포맷으로 지원합니다.

한 줄 요약: **"도로의 모양과 구조를 수학적으로 정밀하게 기술하는 XML 형식"**입니다.

---

## 핵심 개념: Road와 Lane

### Road (도로)

OpenDRIVE의 가장 기본 단위는 **Road**입니다. 하나의 Road는 교차로와 교차로 사이, 또는 도로의 논리적 구간 하나를 의미합니다.

Road는 **Reference Line(기준선)**을 가집니다. 이 기준선을 기준으로 모든 차선이 양쪽으로 배치됩니다.

```
← 기준선(Reference Line) →

  차선 -2  차선 -1 | 기준선 | 차선 +1  차선 +2
  (왼쪽 방향)      |        | (오른쪽 방향)
```

### Lane (차선)

기준선을 중심으로 양쪽에 차선이 번호로 배치됩니다.

- **음수(-1, -2, ...)**: 기준선 오른쪽 (주행 방향과 동일)
- **양수(+1, +2, ...)**: 기준선 왼쪽 (주행 방향 반대)
- **0번**: 기준선 자체 (실제 차선 아님)

예를 들어 왕복 4차선 도로라면:

```
+2  +1  | 기준선 |  -1  -2
←←←←←←←|        |→→→→→→→
```

> **핵심 개념: 프레네 좌표계 (Frenet Coordinate System)**
> OpenDRIVE에서 도로 중심선을 따라가는 진행 방향 거리를 **$s$**, 중심선에서 수직으로 떨어진 거리를 **$t$** 좌표로 표현합니다. 이 $s-t$ (또는 $s-d$) 좌표계는 자율주행 모션 플래닝에서 가장 중요한 기하학적 기준인 **프레네 좌표계**와 정확히 일치합니다. Cartesian(X,Y) 좌표계보다 곡선 도로를 따라가는 경로를 계산하기가 압도적으로 유리합니다.

---

## 도로 형상을 수학으로 표현하는 방법

OpenDRIVE의 가장 큰 특징은 도로 형상을 **수학 함수**로 표현한다는 점입니다. 직선, 원호, 클로소이드(나선) 세 가지를 조합해서 어떤 도로 형상도 정밀하게 표현합니다.

| 형상 타입 | 설명 | 사용 예 |
|---|---|---|
| `line` | 직선 | 고속도로 직선 구간 |
| `arc` | 원호 (일정 곡률) | 일정한 반경의 커브 |
| `spiral` | 클로소이드 (변화하는 곡률) | 직선→커브 전환 구간 |
| `poly3` | 3차 다항식 | 복잡한 형상 |
| `paramPoly3` | 파라미터 3차 다항식 | 더 복잡한 형상 |

GPS 좌표를 일일이 나열하는 Lanelet2와 달리, OpenDRIVE는 수식 몇 줄로 수백 미터의 도로를 정확하게 표현할 수 있습니다.

---

## 파일 구조

OpenDRIVE `.xodr` 파일은 XML로 작성되며 크게 4개 섹션으로 구성됩니다.

```
OpenDRIVE
├── header          # 파일 정보 (버전, 작성 날짜, 지리 기준점)
├── road            # 도로 정의 (여러 개)
│   ├── link        # 앞뒤 도로 연결 정보
│   ├── planView    # 기준선 형상 (직선/원호/클로소이드)
│   ├── elevationProfile  # 고도 정보
│   ├── lateralProfile    # 횡단 경사 정보
│   └── lanes       # 차선 구성
│       └── laneSection
│           ├── left    # 기준선 왼쪽 차선들
│           ├── center  # 기준선 (0번 차선)
│           └── right   # 기준선 오른쪽 차선들
├── junction        # 교차로 정의
└── controller      # 신호 제어기
```

---

## 실제 파일 예시: 단순 직선 도로

아래는 길이 200m의 단순한 직선 2차선 도로입니다.

```xml
<?xml version="1.0" standalone="yes"?>
<OpenDRIVE>

  <header
    revMajor="1"
    revMinor="6"
    name="simple_road"
    version="1.00"
    date="2026-05-11T16:00:00"
    north="0.0" south="0.0" east="0.0" west="0.0">
  </header>

  <road name="StraightRoad" length="200.0" id="1" junction="-1">

    <!-- 앞뒤 도로 연결 (이 예시에서는 연결 없음) -->
    <link/>

    <!-- 기준선 형상: 원점에서 시작하는 200m 직선 -->
    <planView>
      <geometry s="0.0" x="0.0" y="0.0" hdg="0.0" length="200.0">
        <line/>
      </geometry>
    </planView>

    <!-- 고도: 평지 -->
    <elevationProfile>
      <elevation s="0.0" a="0.0" b="0.0" c="0.0" d="0.0"/>
    </elevationProfile>

    <!-- 차선 구성 -->
    <lanes>
      <laneSection s="0.0">

        <!-- 기준선 왼쪽: 반대 방향 차선 -->
        <left>
          <lane id="1" type="driving" level="false">
            <width sOffset="0.0" a="3.5" b="0.0" c="0.0" d="0.0"/>
            <roadMark sOffset="0.0" type="solid" weight="standard"
                      color="white" width="0.12"/>
          </lane>
        </left>

        <!-- 기준선 자체 (0번 차선, 실제 차선 아님) -->
        <center>
          <lane id="0" type="none" level="false">
            <roadMark sOffset="0.0" type="solid" weight="standard"
                      color="yellow" width="0.12"/>
          </lane>
        </center>

        <!-- 기준선 오른쪽: 주행 방향 차선 -->
        <right>
          <lane id="-1" type="driving" level="false">
            <width sOffset="0.0" a="3.5" b="0.0" c="0.0" d="0.0"/>
            <roadMark sOffset="0.0" type="broken" weight="standard"
                      color="white" width="0.12"/>
          </lane>
          <lane id="-2" type="driving" level="false">
            <width sOffset="0.0" a="3.5" b="0.0" c="0.0" d="0.0"/>
            <roadMark sOffset="0.0" type="solid" weight="standard"
                      color="white" width="0.12"/>
          </lane>
        </right>

      </laneSection>
    </lanes>

  </road>

</OpenDRIVE>
```

이 파일은 편도 2차선(기준선 오른쪽 -1, -2) + 반대 방향 1차선(기준선 왼쪽 +1), 총 3차선 도로를 표현합니다.

---

## 주요 속성 설명

### Lane 타입

| type 값 | 의미 |
|---|---|
| `driving` | 일반 주행 차선 |
| `shoulder` | 갓길 |
| `sidewalk` | 보도 |
| `biking` | 자전거 도로 |
| `parking` | 주차 구역 |
| `median` | 중앙 분리대 |
| `none` | 기준선(0번 차선) |

### 차선 경계선(roadMark) 타입

| type 값 | 의미 |
|---|---|
| `solid` | 실선 |
| `broken` | 점선 |
| `solid solid` | 이중 실선 |
| `curb` | 연석 |
| `none` | 없음 |

### 기준선 형상(geometry) 파라미터

직선(`line`)은 별도 파라미터가 없지만, 원호(`arc`)와 클로소이드(`spiral`)는 추가 파라미터가 필요합니다.

```xml
<!-- 반경 100m의 원호 -->
<geometry s="0.0" x="0.0" y="0.0" hdg="0.0" length="50.0">
  <arc curvature="0.01"/>  <!-- curvature = 1/반경 -->
</geometry>

<!-- 클로소이드: 곡률이 0에서 0.01로 변화 -->
<geometry s="0.0" x="0.0" y="0.0" hdg="0.0" length="30.0">
  <spiral curvStart="0.0" curvEnd="0.01"/>
</geometry>
```

---

## 교차로(Junction) 표현

교차로는 Road들이 만나는 지점입니다. OpenDRIVE에서 교차로는 별도의 `junction` 섹션으로 정의하고, 교차로 내부의 연결 경로를 `connection`으로 표현합니다.

```xml
<junction id="1" name="CrossIntersection">
  <!-- 도로 1의 -1차선 → 도로 2의 -1차선으로 연결 -->
  <connection id="0" incomingRoad="1" connectingRoad="10" contactPoint="start">
    <laneLink from="-1" to="-1"/>
  </connection>
  <!-- 도로 3의 -1차선 → 도로 2의 -1차선으로 연결 -->
  <connection id="1" incomingRoad="3" connectingRoad="11" contactPoint="start">
    <laneLink from="-1" to="-1"/>
  </connection>
</junction>
```

---

## OpenDRIVE를 어떻게 만드나요?

| 방법 | 도구 | 특징 |
|---|---|---|
| **GUI 편집기** | ROADRUNNER (MathWorks) | 직관적인 드래그 앤 드롭, 유료 |
| **뷰어** | esmini (오픈소스) | OpenDRIVE 뷰어 및 시뮬레이션 런타임, 무료 |
| **시뮬레이터 내보내기** | CARLA OpenDRIVE Editor | CARLA 맵을 .xodr로 내보내기 |
| **프로그래밍** | `scenariogeneration` (Python) | 코드로 맵 생성, 오픈소스 |
| **변환** | `lanelet2_plugin` | Lanelet2 → OpenDRIVE 변환 |

가장 쉽게 시작하는 방법은 **CARLA에 내장된 샘플 맵**을 열어보는 것입니다. CARLA는 Town01~Town15 등 다양한 샘플 맵을 `.xodr` 형식으로 제공합니다.

---

## Python으로 OpenDRIVE 읽기

`scenariogeneration` 라이브러리를 사용하면 Python으로 OpenDRIVE 파일을 생성하고 조작할 수 있습니다.

```python
from scenariogeneration import xodr

# 직선 도로 생성
road = xodr.create_road([xodr.Line(200)], id=1, left_lanes=1, right_lanes=2)

# 맵 생성 및 저장
odr = xodr.OpenDrive("simple_road")
odr.add_road(road)
odr.adjust_roads_and_lanes()
odr.write_xml("simple_road.xodr")
```

---

## CARLA에서 OpenDRIVE 맵 불러오기

```python
import carla

client = carla.Client("localhost", 2000)
world = client.get_world()

# 내장 맵 불러오기
world = client.load_world("Town03")

# 현재 맵의 OpenDRIVE 내용 출력
opendrive_content = world.get_map().to_opendrive()
print(opendrive_content[:500])
```

---

## 정리

| 개념 | 한 줄 요약 |
|---|---|
| **Road** | 교차로 사이의 도로 구간 하나 |
| **Reference Line** | 도로 중심의 기준선. 모든 차선이 이를 기준으로 배치됨 |
| **Lane** | 기준선 양쪽에 번호로 배치된 차선 (-1, -2... / +1, +2...) |
| **planView** | 기준선의 형상 (직선, 원호, 클로소이드) |
| **Junction** | 여러 Road가 만나는 교차로 |
| **roadMark** | 차선 경계선의 종류 (실선, 점선 등) |

OpenDRIVE는 처음에는 XML 구조가 복잡하게 느껴지지만, 핵심은 단순합니다. **기준선(Reference Line)을 수학 곡선으로 정의하고, 그 양쪽에 차선을 번호로 배치한다**는 것입니다. CARLA 샘플 맵의 `.xodr` 파일을 텍스트 에디터로 열어보면서 구조를 직접 확인해보는 것을 추천합니다.

---

*관련 글: [자율주행 시뮬레이션을 위한 HD 맵 포맷: OpenDRIVE(XODR)와 Lanelet2](/docs/autonomous/hd-map-formats-xodr-lanelet2/), [Lanelet2 입문](/docs/autonomous/hd-map/lanelet2-for-beginners/), [OpenSCENARIO 입문](/docs/autonomous/hd-map/openscenario-for-beginners/)*
