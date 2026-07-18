---
title: "Lanelet2 → OpenDRIVE 변환기 설계하기: IR과 LLM 검증"
date: 2026-07-18T00:00:00+09:00
draft: false
tags: ["자율주행", "HD맵", "OpenDRIVE", "Lanelet2", "IR", "DSL", "LLM", "회귀테스트"]
categories: ["autonomous"]
description: "실차용 Lanelet2 맵을 시뮬레이션용 OpenDRIVE로 변환하기 위한 중간 표현(IR)을 설계하고, LLM을 변환 검증에 활용하는 파이프라인을 단계별로 정리합니다."
---

## 왜 이 변환이 필요한가

실차 자율주행 스택은 보통 Lanelet2 맵을 씁니다 — LiDAR로 실측한 도로를 좌표 점 나열로 그대로 옮겨 담을 수 있고, 경로 계획 라이브러리가 처음부터 이 포맷을 염두에 두고 만들어졌기 때문입니다([Lanelet2 입문](../lanelet2-for-beginners/) 참고). 문제는 시뮬레이션입니다. CARLA, SUMO 같은 주요 시뮬레이터는 OpenDRIVE를 기본 포맷으로 쓰는데, 회사에 이미 있는 자산은 Lanelet2 맵뿐입니다. 실측 맵을 시뮬레이션에서 그대로 쓰려면 Lanelet2 → OpenDRIVE 변환이 필요합니다.

이 글은 그 변환기를 처음부터 설계해나가는 과정을 단계별로 정리합니다. 목표는 "완벽한 상호변환"이 아니라, **클로즈드 루프 회귀 테스트에 실제로 쓸 수 있을 만큼 정확한 변환**입니다.

정확도가 왜 이렇게까지 중요한지는 회귀 테스트에 쓰는 렌더링 방식과 맞물려 있습니다. 여기서 다루는 클로즈드 루프 회귀 테스트는 **3D Gaussian Splatting(3DGS)**로 실측 데이터를 사실적으로 복원한 씬 위에서 돌립니다. 3DGS로 복원된 장면은 원본 Lanelet2 실측 좌표계 그대로이므로, 그 위에 얹는 OpenDRIVE 도로 모델이 조금이라도 어긋나면 "인지 스택은 사실적인 3DGS 화면을 보고 판단하는데, 플래닝/컨트롤이 참조하는 도로 기하는 그 화면과 안 맞는" 모순이 생깁니다. 즉 맵 변환 정확도는 단순한 품질 문제가 아니라, 3DGS 씬과 도로 모델 간의 기하학적 정합성 문제입니다.

---

## 1단계: 기존 오픈소스 도구부터 조사한다

바퀴를 다시 발명하기 전에, 이미 있는 도구가 이 문제를 얼마나 풀어놨는지부터 확인했습니다.

| 도구 | 방향 | 상태 |
|---|---|---|
| [opendrive2lanelet](https://github.com/usdot-fhwa-stol/opendrive2lanelet) (TUM) | OpenDRIVE → Lanelet2 | 성숙, 논문으로 발표됨 |
| [odr2lanelet2](https://github.com/joel-mb/odr2lanelet2) | OpenDRIVE → Lanelet2 | 소규모 프로젝트 |
| [CommonRoad Scenario Designer](https://github.com/CommonRoad/commonroad-scenario-designer) | Lanelet2 ↔ CommonRoad, OpenDRIVE → CommonRoad | CommonRoad을 중간 포맷으로 씀 |

조사해보니 업계 도구는 거의 전부 **OpenDRIVE → Lanelet2** 방향(시뮬레이터 맵을 실차 스택으로 가져오는 방향)만 다루고 있었습니다. CommonRoad Scenario Designer도 CommonRoad → OpenDRIVE 익스포트는 지원하지 않아서, 결국 우리가 필요한 **반대 방향은 도구 생태계에 거의 비어 있다**는 결론이 나왔습니다.

더 파고들어 보니 이유가 명확했습니다. CommonRoad의 `Lanelet` 클래스도 `left_vertices`/`right_vertices`/`center_vertices`, 즉 좌표 점 나열로만 차선을 표현합니다 — Lanelet2와 표현 방식이 사실상 같은 종족입니다. 반면 OpenDRIVE → CommonRoad 변환기는 `PlanView`(참조선: 직선·원호·클로소이드·다항식 조합)와 `ParametricLane`(그 참조선 기준 s-좌표계의 폭 함수)을 먼저 만든 뒤, 최종 단계에서 좌표 점으로 샘플링해 CommonRoad에 담습니다. 즉 CommonRoad로 한 번 변환하고 나면 참조선 정보가 이미 사라진 상태라, CommonRoad을 경유해도 우리가 풀어야 할 핵심 난제(좌표 점 → 참조선 역추정)는 그대로 남습니다.

다만 이 조사가 헛수고였던 건 아닙니다. 성숙한 반대 방향 도구는 나중에 우리 변환기의 **라운드트립 검증**에 재활용할 수 있습니다 — 우리가 만든 OpenDRIVE를 opendrive2lanelet으로 다시 Lanelet2로 변환해 원본 좌표와 비교하면, 변환 전체를 결정적으로 검사하는 회로가 하나 생깁니다. 이 검사는 21단계에서 실제로 수행합니다.

---

## 2단계: IR을 어느 쪽 모델에 맞출지 정한다

두 포맷의 근본적인 차이는 [OpenDRIVE vs Lanelet2 비교](../opendrive-vs-lanelet2/)에서 다룬 그대로입니다 — OpenDRIVE는 참조선을 수식으로 표현하고 차선을 그 위의 폭 함수로 얹는 반면, Lanelet2는 좌표 점 나열이 곧 형상입니다.

중간 표현(IR)을 설계할 때 두 모델 중 어느 쪽을 IR의 뼈대로 삼을지가 첫 갈림길입니다. **OpenDRIVE 쪽 모델(참조선 + 파라메트릭 단면)을 IR의 핵심 스키마로 선택**했습니다. 이렇게 하면:

- IR → OpenDRIVE 익스포트는 손실 없는 직역에 가까워집니다.
- 어려운 작업(좌표 점 나열에서 참조선을 역추정하는 곡선 피팅)이 Lanelet2 → IR 한쪽 방향에만 집중됩니다.

반대로 IR을 Lanelet2 모델(폴리라인)에 맞췄다면, 이번엔 IR → OpenDRIVE 방향에서 매번 곡선 피팅을 해야 해서 문제가 그대로 이동할 뿐 해결되지 않습니다.

---

## 3단계: IR 스키마 초안을 잡는다

지리/토폴로지를 표현하는 부분과, 변환 과정의 근거를 남기는 부분을 처음부터 분리해서 설계했습니다.

### 지리/토폴로지 IR

```
Network
├── roads: [Road]
├── junctions: [Junction]
└── signals: [Signal]

Road
├── id
├── reference_line: ReferenceLine    # 참조선 (평면 형상)
├── elevation_profile: ElevationProfile   # 고도 (수직 형상) — 참조선과 독립적으로 관리
├── superelevation: SuperelevationProfile   # 횡단 경사(뱅크각) — 26단계에서 추가
├── lane_sections: [LaneSection]     # s-구간별 차선 단면
└── predecessor / successor: RoadLink | JunctionLink

ReferenceLine
└── segments: [LineSeg | ArcSeg | ParamPoly3Seg]   # 우선 Line + Arc만 지원

ElevationProfile
└── segments: [ElevPoly(s_start, coeffs: PolyCoeffs)]   # z(s) = a + b*ds + c*ds^2 + d*ds^3

SuperelevationProfile
└── segments: [SuperelevPoly(s_start, coeffs: PolyCoeffs)]   # cross_slope(s) = a + b*ds + c*ds^2 + d*ds^3 (무차원 기울기)

LaneSection
├── s_start
└── lanes: [Lane]

Lane
├── id            # OpenDRIVE 규약: 0=참조선, 음수=우측, 양수=좌측
├── type          # driving/shoulder/...
├── width: PolyCoeffs(a, b, c, d)   # s-로컬 3차다항식
├── road_mark: RoadMark             # 차선 경계 마킹
└── link: predecessor_id / successor_id

RoadMark
├── mark_type: "solid" | "dashed" | "none" | ...
└── color: "white" | "yellow" | ...

Junction
└── connections: [(incoming_road, connecting_road, lane_links)]

Signal
├── id
├── road_id, s, t                 # ref_line과 참조선의 교차점에서 계산 (참조선 피팅이 선행돼야 함)
├── kind: "traffic_light" | "speed_limit" | "right_of_way" | ...
├── applicable_lane_ids: [int]    # 이 Signal을 참조하는 원본 lanelet들 -> 변환된 Lane id
└── source_regulatory_element_id  # 프로버넌스
```

`Signal`은 Lanelet2의 `RegulatoryElement`(TrafficLight, SpeedLimit, RightOfWay 등)를 OpenDRIVE의 `signal`/`object` 모델로 옮기기 위한 타입입니다. Lanelet2는 "위치 + 적용 대상"을 하나의 관계(RegulatoryElement가 lanelet을 참조)로 묶는 반면, OpenDRIVE는 위치(s, t)와 적용 범위(validity)를 분리해서 표현하므로, 변환 시 이 둘을 명시적으로 갈라 담아야 합니다. `road_id, s, t`를 계산하려면 그 도로의 참조선이 이미 피팅되어 있어야 하므로, `Signal` 변환은 항상 B단계(참조선 피팅) 뒤에 오는 종속 단계입니다.

`elevation_profile`은 11단계 이후에 추가한 것으로, 참조선(x, y 평면 형상)과 별도로 z(s)를 관리합니다. OpenDRIVE 자체가 평면 형상과 고도를 독립된 두 레이어로 분리해서 표현하는 방식을 그대로 따른 것입니다 — 그래서 B단계(참조선 피팅)와 별개로 "고도 피팅"이라는 대칭적인 서브 단계가 하나 더 필요해집니다. 지금까지 스파이크에서 쓴 `latlon_to_local_xy`는 위도/경도만 평면 좌표로 바꾸고 z를 아예 다루지 않았다는 걸 확인했는데, 이게 정확히 이 누락을 만든 지점입니다 — z가 있는 노드라면 좌표 변환 단계에서부터 같이 뽑아야 합니다. 그리고 같은 논리로 처음엔 빠져 있던 누락이 하나 더 있었습니다: Lanelet2의 3D 경계선은 좌/우 경계의 z 차이로 횡단 경사(뱅크각)를 암묵적으로 담는데, 참조선 위의 z(s) 하나로는 이걸 표현할 수 없습니다. OpenDRIVE의 대응물은 `superelevation`이고, 26단계에서 실측을 거쳐 IR에 추가했습니다.

`road_mark`는 Lanelet2 경계 way의 `subtype`(`solid`/`dashed`) 태그를 거의 그대로 옮기면 되는, 상대적으로 간단한 매핑입니다. 차선 변경 가능 여부 판정과, 인지 스택이 3DGS 렌더링에서 보는 것과 일치하는 ground truth를 만드는 데 씁니다.

### 프로버넌스(변환 근거) IR

변환 결과 요소마다 "무엇으로부터 어떻게 만들어졌는지"를 구조화된 형태로 함께 냅니다.

```
RoadProvenance
├── road_id
├── source_lanelet_ids: [id]                   # 이 도로를 구성한 원본 lanelet들
├── fit_method: "arc" | "line" | "paramPoly3"
├── fit_residual_max_m / fit_residual_rms_m    # 참조선 피팅이 원본과 얼마나 벗어났는지
├── curvature_error_max                        # 위치 오차와 별개로, 곡률 오차 지표
├── joint_gap_max_m / joint_heading_jump_max_rad  # 세그먼트 이음새의 위치 갭·헤딩 꺾임 (4단계에서 정의, 18단계에서 실측)
├── lane_count_check: {source: n, derived: n}
├── dropped_attributes: [string]                # Signal로도 못 옮긴 나머지 규제 정보
├── mark_defaulted_count: n                     # road_mark를 애매한 태그라 기본값으로 채운 경계선 수
└── topology_warnings: [string]                 # 분기/합류가 Road/Junction 구조로 깔끔히 안 매핑된 경우
```

이렇게 나눈 이유는 다음 단계(LLM 검증)와 직결됩니다.

---

## 4단계: 정확도 우선순위를 정한다

이 변환의 최종 목적은 **클로즈드 루프 회귀 테스트**입니다. 시뮬레이션 속 차량 거동(조향, 곡률 추종, 차선 유지)이 실제 지도 형상과 어긋나면 회귀 테스트가 거짓 양성·거짓 음성을 만들어낼 수 있습니다. 앞서 언급했듯 씬 자체가 3DGS로 실측 좌표계를 그대로 복원한 것이기 때문에, 도로 모델이 그 좌표계에서 벗어나는 순간 "화면은 맞는데 도로 기하는 틀린" 상황이 됩니다. 그래서 스키마와 파이프라인 설계 모두에서 **곡선 피팅 정확도**를 최우선에 뒀습니다.

- `fit_residual`(위치 오차)에 명시적 허용치를 두고, 넘으면 변환을 실패로 처리합니다. 허용치는 회귀 테스트에서 감내 가능한 위치 오차를 먼저 정하고 거꾸로 계산합니다.
- 위치 오차만으로는 부족합니다. 곡률 오차는 조향 거동에 더 직접적으로 영향을 주므로 `curvature_error_max`를 프로버넌스에 별도로 둡니다.
- Line + Arc만으로 허용치를 못 맞추는 도로 세그먼트가 나오면, 그때 가서 paramPoly3를 추가하는 식으로 곡선 타입을 필요한 만큼만 확장합니다. 처음부터 모든 곡선 타입을 지원하려 하지 않습니다.
- 위치·곡률 "오차"와 별개로, **세그먼트 이음새의 연속성**을 별도 지표(`joint_gap_max_m`, `joint_heading_jump_max_rad`)로 둡니다. OpenDRIVE `planView`는 각 geometry가 (시작점, 헤딩, 길이)로 정의되어 이전 geometry의 끝에서 이어지는 체인 구조라, 구간별로 독립 피팅한 결과를 그대로 직렬화하면 이음새마다 위치 갭과 헤딩 꺾임이 생깁니다. `fit_residual`은 "각 구간이 자기 점들을 얼마나 잘 따라가는가"만 재기 때문에 이 불연속을 전혀 잡지 못합니다.

이음새 중에서도 line→arc 전환점의 **곡률 계단**(곡률이 0에서 1/r로 점프)은 조향 거동에 가장 직접적으로 영향을 주는 불연속입니다 — OpenDRIVE에 클로소이드(spiral) 타입이 있는 이유가 정확히 이것입니다. 그래서 "허용치를 못 맞추면 paramPoly3 추가"라는 확장 순서보다, "이음새에 연속성 제약을 건 피팅(인접 구간과 끝점·헤딩을 공유하는 최적화)이 필요한가"가 먼저 나올 질문입니다. 이 불연속은 18단계에서 실측하고, 전역 최적화 피팅으로 해결합니다.

토폴로지(교차로 연결 등) 오류는 틀리면 눈에 바로 띄어서 사람이 고치기 쉽지만, 곡률 오차는 조용히 결과를 왜곡시키기 때문에 더 위험하다고 판단했습니다.

---

## 5단계: LLM을 검증 파이프라인에 배치한다

LLM에게 원시 좌표 배열을 던지고 "이 변환이 맞았는지 봐줘"라고 요청하는 방식은 잘 작동하지 않습니다. 숫자 정밀도 비교는 LLM이 취약한 영역이기 때문입니다. 대신 **파이프라인과 LLM의 역할을 명확히 나눴습니다**.

- **파이프라인의 책임**: `fit_residual`, `curvature_error_max`, `lane_count_check` 같은 정량 지표를 계산해서 프로버넌스 IR에 박아두고, 원본 lanelet 경계선과 피팅된 참조선을 겹쳐 그린 top-down 오버레이 이미지를 도로 단위로 생성합니다.
- **LLM의 책임**: 그 정량 지표와 이미지를 보고 "이 수치가 이상해 보이는지", "시각적으로 그럴듯한지", "이 정도 손실(`dropped_attributes`)이면 시뮬레이션 목적상 괜찮은지"를 판단·요약합니다.

즉 정밀한 수치 계산은 결정적(deterministic)인 코드가 담당하고, LLM은 그 결과를 검토하고 이상 징후를 짚어내는 **리뷰어** 역할로 한정합니다. 이렇게 역할을 나누면 LLM이 잘하는 것(패턴 인식, 시각적 판단, 자연어 요약)만 쓰고, 잘 못하는 것(정밀 수치 비교)은 애초에 맡기지 않게 됩니다.

---

## 6단계: 스켈레톤 코드로 골격을 잡는다

세 알고리즘(그룹핑 → 참조선 피팅 → 곡률/폭 추출)을 실제로 짜기 전에, IR 데이터 구조와 각 단계의 함수 시그니처를 스켈레톤으로 먼저 잡았습니다. `numpy`/`scipy`만으로 구현 가능한 범위입니다.

### IR 데이터 구조

```python
from dataclasses import dataclass, field
import numpy as np

@dataclass
class LineSeg:
    start: np.ndarray   # (x, y)
    heading: float       # rad
    length: float

@dataclass
class ArcSeg:
    start: np.ndarray
    heading: float
    length: float
    curvature: float     # 1/radius, 부호로 좌/우 회전 구분

ReferenceLineSeg = LineSeg | ArcSeg

@dataclass
class ReferenceLine:
    segments: list[ReferenceLineSeg]

@dataclass
class PolyCoeffs:
    a: float
    b: float
    c: float
    d: float

@dataclass
class Lane:
    lane_id: int
    lane_type: str
    width: PolyCoeffs
    predecessor_id: int | None = None
    successor_id: int | None = None

@dataclass
class LaneSection:
    s_start: float
    lanes: list[Lane]

@dataclass
class Road:
    road_id: str
    reference_line: ReferenceLine
    lane_sections: list[LaneSection]

@dataclass
class RoadProvenance:
    road_id: str
    source_lanelet_ids: list[str]
    fit_method: str
    fit_residual_max_m: float
    fit_residual_rms_m: float
    curvature_error_max: float
    dropped_attributes: list[str] = field(default_factory=list)
    topology_warnings: list[str] = field(default_factory=list)
```

### A. Lanelet 그룹핑

```python
def group_lanelets_into_roads(routing_graph, lanelet_map) -> list[list[str]]:
    """좌우 인접(left/right) lanelet을 하나의 단면 후보로 묶고,
    종방향(successor/predecessor)으로 곡률·차선 수가 급변하지 않는 동안 이어붙인다.
    반환값: 도로 하나에 해당하는 lanelet id 목록의 리스트.
    """
    ...  # TODO: routing_graph.left(ll) / .right(ll) / .following(ll) 순회
```

### B. 참조선 피팅

```python
from scipy.optimize import least_squares

def simplify_polyline(points: np.ndarray, epsilon: float) -> np.ndarray:
    """Ramer-Douglas-Peucker로 곡률이 바뀌는 후보 꼭짓점만 남긴다."""
    ...

def fit_line(points: np.ndarray) -> tuple[LineSeg, float]:
    """최소자승 직선 피팅. 반환: (LineSeg, rms_residual)"""
    ...

def fit_arc(points: np.ndarray) -> tuple[ArcSeg, float]:
    """최소자승 원 피팅(Kasa/Coope 방식) 후 시작점·헤딩·길이로 변환.
    반환: (ArcSeg, rms_residual)"""
    ...

def fit_reference_line(centerline: np.ndarray, epsilon: float = 0.1) -> tuple[ReferenceLine, dict]:
    """구간별로 fit_line과 fit_arc를 모두 시도해 잔차가 작은 쪽을 채택한다.
    fit_residual은 등간격 s-샘플링이 아니라, 원본 각 점에서 피팅 곡선까지의
    최근접 거리(point-to-curve)로 계산한다 — 곡률이 급한 구간에서
    등간격 샘플링은 오차를 과소평가하기 쉽다.
    반환: (ReferenceLine, {"fit_residual_max_m": ..., "fit_residual_rms_m": ...})
    """
    breakpoints = simplify_polyline(centerline, epsilon)
    segments = []
    residuals = []
    for a, b in zip(breakpoints[:-1], breakpoints[1:]):
        chunk = centerline[a:b + 1]
        line_seg, line_res = fit_line(chunk)
        arc_seg, arc_res = fit_arc(chunk)
        seg, res = (line_seg, line_res) if line_res <= arc_res else (arc_seg, arc_res)
        segments.append(seg)
        residuals.append(res)
    return ReferenceLine(segments), {
        "fit_residual_max_m": max(residuals),
        "fit_residual_rms_m": float(np.sqrt(np.mean(np.square(residuals)))),
    }
```

### C. 곡률 오차와 차선 폭

```python
def discrete_curvature(points: np.ndarray) -> np.ndarray:
    """3점 유한차분으로 이산 곡률 κ(s)를 추정한다."""
    ...

def curvature_error(reference_line: ReferenceLine, centerline: np.ndarray) -> float:
    """피팅된 세그먼트의 이론 곡률과 discrete_curvature를 비교해 최대 오차를 낸다."""
    ...

def extract_lane_width(reference_line: ReferenceLine,
                        left_pts: np.ndarray, right_pts: np.ndarray) -> PolyCoeffs:
    """참조선의 각 s 지점에서 법선 방향으로 좌/우 경계를 투영해 폭 w(s)를 샘플링하고,
    LaneSection 구간 단위로 3차다항식을 최소자승 피팅한다."""
    ...
```

이 골격을 채우는 순서는 B(참조선 피팅) → C(곡률/폭) → A(그룹핑) 순으로 진행하는 게 낫습니다 — A는 B, C가 실제로 얼마나 정확한지 봐야 "도로를 어디서 끊을지" 기준(곡률 급변, 잔차 급증)을 구체적으로 정할 수 있기 때문입니다. (실제로 채운 구현 전체는 글 마지막 [부록](#부록-스파이크-전체-코드)에 있습니다.)

---

## 7단계: 샘플 맵으로 스파이크 검증

B, C 함수의 본문을 실제로 채우고(직선 SVD 피팅, Kasa 방식 원 피팅, Ramer-Douglas-Peucker 세그먼트 분할, 3점 유한차분 곡률), Lanelet2 공식 저장소가 제공하는 표준 예제 맵 [`mapping_example.osm`](https://github.com/fzi-forschungszentrum-informatik/Lanelet2/blob/master/lanelet2_maps/res/mapping_example.osm)(371개 lanelet, 독일 Karlsruhe 지역 도심 교차로)에 돌려봤습니다. (`lanelet2` 파이썬 바인딩은 빌드가 무거워서, 이번 스파이크는 OSM XML을 직접 파싱하는 경량 로더로 대체했습니다.)

**단일 lanelet 상세 검증**: 반경 1.4m짜리 급커브(교차로 모서리로 보이는 20m 구간)를 골라 피팅한 결과, `fit_residual_max_m = 2.0cm`, `fit_residual_rms_m = 0.5cm`가 나왔습니다. 급격한 곡률에서도 Line/Arc 조합이 경계선을 꽤 정확하게 따라갔습니다.

**전체 lanelet 분포**: 93개 lanelet(나머지는 길이가 너무 짧거나 way 참조가 애매해 제외)에 대해 같은 피팅을 돌려 분포를 냈습니다.

| 지표 | 평균 | p50 | p95 | 최댓값 |
|---|---|---|---|---|
| `fit_residual_max_m` | 2.65cm | 2.11cm | 6.74cm | 9.90cm |
| `fit_residual_rms_m` | 0.93cm | - | 2.08cm | - |

최댓값(9.9cm)이 나온 케이스도 110m짜리 긴 도로 하나였고, 나머지 대부분은 2~3cm 수준에 머물렀습니다. **이 샘플 맵 기준으로는 Line+Arc만으로 충분하고, paramPoly3까지 확장할 필요가 아직은 없어 보입니다.** 다만 이건 Lanelet2 공식 예제 맵(독일 Karlsruhe 지역) 결과이고, 실제 회사 맵(더 복잡한 교차로, LiDAR 실측 노이즈가 더 클 수 있는)으로 같은 검증을 반복해서 이 결론이 유지되는지 확인하는 작업이 남아 있습니다.

이 잔차 수치를 읽을 때 주의할 점도 세 가지 짚어둡니다.

1. **이음새 불연속은 측정에 안 들어가 있습니다.** 잔차는 구간별 독립 피팅의 point-to-curve 거리라, 4단계에서 말한 세그먼트 경계의 위치 갭·헤딩 꺾임·곡률 계단은 이 숫자에 전혀 반영되지 않습니다. 실제 OpenDRIVE 체인으로 직렬화했을 때의 오차는 이보다 나쁠 수 있습니다. (18단계에서 실측한 결과, 이음새 헤딩 꺾임이 평균 8.8°에 달했습니다.)
2. **중심선 자체에 편향이 있을 수 있습니다.** 중심선을 좌우 경계의 호길이 비율 재샘플링 후 포인트별 평균으로 만드는데, 커브에서는 안쪽 경계가 바깥쪽보다 짧아 짝이 어긋난 점끼리 평균됩니다. 위에서 검증한 반경 1.4m 급커브가 정확히 이 편향이 최대가 되는 조건이라, 한쪽 경계에서 법선 투영으로 반대쪽 점을 찾는 방식과 비교해 편향을 정량화하는 작업이 필요합니다 — 지금의 2cm 잔차가 이 편향을 포함한 값인지 아직 모릅니다. (20단계에서 실측한 결과, 최악 1.5m에 달하는 편향이 확인됐습니다.)
3. **곡률 오차는 아직 한 번도 측정하지 않았습니다.** 4단계에서 곡률 오차를 위치 오차보다 위험한 지표로 규정해놓고, 지금까지의 스파이크 결과는 전부 위치 잔차뿐입니다. `discrete_curvature`까지는 구현했지만, 피팅 세그먼트의 이론 곡률과 비교하는 `curvature_error`는 시그니처만 있는 상태입니다. 재샘플링된 30점 위의 3점 유한차분은 노이즈도 심해서, 실측할 때 측정 방법 자체(스무딩 창, 샘플 밀도)도 같이 정해야 합니다. (19단계에서 실측했습니다.)

---

## 8단계: 그룹핑(A) 알고리즘 구현과 검증

B, C가 lanelet 하나 단위로만 동작했으니, 이제 A(그룹핑)를 채워 여러 lanelet을 하나의 `Road`로 묶는 절차를 구현했습니다.

1. **좌우 인접**: 경계 way(LineString)를 공유하는 lanelet들을 union-find로 묶어 단면 클러스터(`LaneSection` 후보)를 만듭니다.
2. **종방향 연결**: 클러스터의 끝 node id가 다음 클러스터의 시작 node id와 일치하면 이어붙입니다. OSM은 연결된 lanelet들이 노드 id를 그대로 공유하므로, 좌표 근접 판정이 아니라 정확한 id 일치로 연결을 잡을 수 있습니다.
3. **Road 경계**: 차선 수가 바뀌거나, 클러스터가 둘 이상으로 분기/합류하는 지점에서 끊습니다.

같은 샘플 맵(371개 lanelet, 도심 교차로 밀집 지역)에 돌린 결과:

| 지표 | 값 |
|---|---|
| 단면 클러스터 수 | 247 (1차선 169 / 2차선 42 / 3차선 이상 36) |
| 분기점 / 합류점 | 64 / 63 |
| Road 개수 | 165 |
| Road당 평균 클러스터 수 | 1.48 (최대 18) |
| 단일 클러스터로 끝난 Road | 134개 / 165개 (81%) |

처음 보면 81%가 한 클러스터짜리로 끝난 게 그룹핑이 실패한 것처럼 보입니다. 그래서 이 134개가 교차로 근처인지 아니면 그냥 그래프가 중간에 끊긴 고립 구간인지를 따로 분석했습니다.

| 구분 | 개수 | 비율 |
|---|---|---|
| 교차로(분기/합류) 인접 | 116 | 87% |
| 고립(교차로와 무관) | 18 | 13% |

**87%는 교차로 바로 옆이었습니다.** OpenDRIVE는 원래 교차로마다 짧은 연결 도로(connecting road)를 여러 개 두는 구조라, 짧은 Road가 많이 나오는 건 버그가 아니라 이 표현 방식이 도심 교차로 밀집 지역에서 자연스럽게 만들어내는 패턴이었습니다.

나머지 13%(18개) 고립 조각은 원인을 더 파봤습니다. `subtype` 태그를 확인해보니:

| subtype | 개수 |
|---|---|
| `bicycle_lane` | 5 |
| `road` | 8 |
| `rail` | 2 |
| `crosswalk` | 1 |
| `walkway` | 2 |

10개(`bicycle_lane`, `rail`, `crosswalk`, `walkway`)는 애초에 차량용 도로망과 별개 네트워크라, Road 그래프에 안 이어지는 게 정상입니다. **문제는 `subtype: road`인데도 고립된 나머지 8개**입니다.

이 8개의 시작/끝 node 좌표를 다른 모든 lanelet의 끝점과 대조해보니, 절반(4개)은 실제로는 **오른쪽(right) 경계선에서만** 정확히 이어져 있었습니다 — 종방향 연결 판정을 왼쪽 경계선 node id만으로 했더니 놓친 겁니다. 나머지 4개는 최근접 거리가 1.8m~22m로, 진짜 위상 결측(맵 자체의 갭)으로 보였습니다.

그래서 왼쪽 또는 오른쪽 중 하나라도 일치하면 연결로 인정하도록 고쳐서 전체 맵에 다시 돌려봤는데, 여기서 예상 밖의 결과가 나왔습니다.

| 연결 판정 기준 | 분기점 | 합류점 | Road 개수 | 8개 중 회복 |
|---|---|---|---|---|
| 왼쪽만 일치 (기존) | 64 | 63 | 165 | 0 |
| 왼쪽 또는 오른쪽 각각 일치 (either) | 144 | 135 | 209 | 4 |
| 왼쪽 **그리고** 오른쪽 모두 일치 (both) | 21 | 25 | 184 | 0 |

`either` 기준은 8개 중 4개를 회복시킨 것처럼 보였지만, 동시에 분기점·합류점을 64→144로 두 배 이상 늘렸습니다 — 교차로에서 여러 방향의 lanelet들이 우연히 좌표를 공유하는 스퓨리어스 매치까지 "연결"로 잘못 인식한 겁니다. `both` 기준은 반대로 너무 엄격해서 원래 찾았던 연결까지 다 잃었습니다. **정확한 node id 일치만으로는 이 문제를 깔끔하게 풀 수 없다는 게 이번 스파이크의 결론입니다.** 실제로는 근접 거리와 진행 방향(heading) 일치 여부를 함께 봐야 하는데, 이건 Lanelet2 공식 `RoutingGraph` 라이브러리가 이미 정교하게 구현해 둔 기능입니다.

---

## 9단계: 공식 `RoutingGraph`로 최종 검증

`lanelet2` 파이썬 바인딩은 PyPI에 있지만 manylinux(Linux x86_64) 휠만 배포됩니다. macOS(Apple Silicon)에서는 conan으로 직접 소스 빌드해야 하는데 boost::python 공유 라이브러리 빌드 등 절차가 무거워서, 대신 Docker로 `--platform linux/amd64` Linux 컨테이너를 띄워 `pip install lanelet2`로 바로 설치했습니다.

공식 `RoutingGraph`로 앞서 찾은 8개 고립 lanelet(`subtype: road`)을 다시 확인한 결과:

| lanelet id | following | previous | 판정 |
|---|---|---|---|
| 43694 | 1 (→43685) | 0 | **연결됨** |
| 45078 | 1 (→45002) | 1 (←45076) | **연결됨** |
| 45260 | 0 | 2 (←42440, 45254) | **연결됨** |
| 45188 | 0 | 0 | 고립 (맵 자체의 갭) |
| 45208 | 0 | 0 | 고립 (맵 자체의 갭) |
| 45376 | 0 | 0 | 고립 (맵 자체의 갭) |
| 45378 | 0 | 0 | 고립 (맵 자체의 갭) |
| 45582 | 0 | 0 | 고립 (맵 자체의 갭) |

8개 중 3개는 실제로 연결되어 있었고, 5개는 공식 라이브러리 기준으로도 진짜 고립이었습니다 — 이 5개는 알고리즘 문제가 아니라 이 샘플 맵 자체의 위상 결측으로 최종 확인됐습니다.

더 중요한 발견은 따로 있습니다. 앞서 `either`(왼쪽 또는 오른쪽 일치) 기준이 회복시켰다고 판단한 4개(43694, 45078, 45260, 45582) 중 **45582는 공식 라이브러리 기준 `following=0, previous=0`으로 실제로는 연결되어 있지 않았습니다.** 제가 만든 휴리스틱이 스퓨리어스 매치를 진짜 연결로 착각한 구체적 사례입니다. 처음에 세웠던 "정확한 node id 매칭만으로는 부족하다"는 결론이 실측 데이터로 확인된 셈입니다 — A(그룹핑)는 직접 재구현 대신 공식 `RoutingGraph`를 쓰는 것으로 최종 확정합니다.

```python
import lanelet2
from lanelet2.projection import UtmProjector

origin = lanelet2.io.Origin(49.0, 8.4)
projector = UtmProjector(origin)
laneletMap = lanelet2.io.load("mapping_example.osm", projector)

traffic_rules = lanelet2.traffic_rules.create(
    lanelet2.traffic_rules.Locations.Germany,
    lanelet2.traffic_rules.Participants.Vehicle,
)
routing_graph = lanelet2.routing.RoutingGraph(laneletMap, traffic_rules)

for ll in laneletMap.laneletLayer:
    following = routing_graph.following(ll)   # 실제 종방향 successor
    previous = routing_graph.previous(ll)      # 실제 종방향 predecessor
    lefts = routing_graph.lefts(ll)            # 실제 좌측 인접
    rights = routing_graph.rights(ll)          # 실제 우측 인접
```

---

## 10단계: `RoutingGraph`를 A(그룹핑) 전체에 통합

`RoutingGraph`의 `left()`/`right()`/`adjacentLeft()`/`adjacentRight()`(횡방향)와 `following()`/`previous()`(종방향)를 그대로 써서 A(그룹핑) 전체를 다시 구현하고, 같은 샘플 맵에 돌렸습니다.

| 지표 | node id 매칭(기존) | `RoutingGraph`(신규) |
|---|---|---|
| 단면 클러스터 수 | 247 | 260 |
| 분기점 / 합류점 | 64 / 63 | **23 / 23** |
| Road 개수 | 165 | 134 |
| Road당 평균 클러스터 수 | 1.48 | **1.94** |

분기점·합류점이 64→23으로 크게 줄고 Road당 평균 클러스터 수도 늘었습니다 — 비주행 lanelet이 섞여서 생기던 노이즈가 사라지고, 더 긴 Road로 깔끔하게 이어붙는다는 뜻입니다. 여기까지는 예상대로 개선이었습니다.

그런데 "단일 클러스터로 끝난 Road" 안의 `subtype: road`(진짜 검토 대상) 개수를 다시 세보니, 오히려 8개 → **21개로 늘었습니다.** `following()`이 예상보다 더 엄격하게 연결을 판정하고 있다는 뜻이라, 원인을 추적했습니다.

새로 고립된 lanelet들의 태그를 열어보니 패턴이 보였습니다.

```
45208 {'location': 'urban', 'one_way': 'no', 'participant:bicycle': 'yes',
       'participant:pedestrian': 'yes', 'subtype': 'road', ...}
45576 {'location': 'urban', 'one_way': 'no', 'participant:bicycle': 'yes',
       'participant:pedestrian': 'yes', 'subtype': 'road', ...}
```

대부분이 `participant:bicycle: yes`, `participant:pedestrian: yes`가 같이 붙은 **혼합 통행 구간(자전거·보행자와 공유하는 저속 구역)**이었습니다. `Participants.Vehicle` 교통규칙의 `RoutingGraph`는 이런 구간을 표준 차량 경로 탐색에서 제외하도록 설계되어 있어서, 물리적으로 도로가 이어져 있어도 `following()`에는 안 잡힙니다.

이건 원래 발견하려던 버그가 아니라, **A(그룹핑)의 목적을 다시 짚게 하는 발견**이었습니다. `Participants.Vehicle` 규칙은 "법규상 허용된 차량 경로가 뭔가"를 답하도록 만들어진 것이지, "이 도로가 물리적으로 어떻게 생겼는가"를 답하도록 만들어진 게 아닙니다. 우리가 만드는 건 경로 탐색기가 아니라 시뮬레이션용 도로 형상(OpenDRIVE)이라, 혼합 통행 구간도 — 차량이 저속으로 지나갈 수 있는 구간이라면 — 지오메트리 상으로는 여전히 필요합니다. 즉 **A(그룹핑)를 "합법적 차량 경로 탐색"이 아니라 "물리적 도로 연결성"을 기준으로 다시 설계해야 한다**는 게 이번 단계의 결론입니다.

---

## 11단계: 신호등·규제 정보는 아직 IR에 없다

지금까지 다룬 건 전부 도로 형상(Road/ReferenceLine/LaneSection/Lane)이었고, 신호등·정지선·속도제한 같은 규제 정보는 IR에 자리가 없었습니다. 시뮬레이션에서 신호 준수 거동을 테스트하려면 이 정보가 반드시 필요하므로, 샘플 맵에 실제로 뭐가 들어있는지부터 확인했습니다.

```
전체 regulatory_element 수: 9
subtype 분포: {'traffic_light': 6, 'right_of_way': 2, 'speed_limit': 1}
```

`traffic_light` 하나(id=45218)를 열어보면 구조가 이렇습니다.

```
way 43606  role=ref_line   # 정지선 — 차량이 멈춰야 하는 위치를 가로지르는 선
way 49639  role=refers     # 신호등 물리적 형상(폴/헤드) geometry
way 44960  role=refers

이 regulatory_element를 참조하는 lanelet: 45134, 45136 (role=regulatory_element)
```

`ref_line`(정지선)이 참조선과 교차하는 지점의 s값을 구하면 OpenDRIVE `signal`의 위치가 되고, 이 규제 요소를 참조하는 lanelet들이 변환된 뒤의 `Lane` id가 곧 `validity`(적용 차선) 범위가 됩니다. 이 대응 관계를 반영해 IR에 `Signal` 타입을 추가했습니다 — 3단계의 IR 스키마를 참고하세요. `road_id, s, t` 계산이 참조선 피팅(B단계) 결과에 의존하므로, `Signal` 변환은 항상 도로 형상 변환 뒤에 오는 종속 작업입니다.

이번 단계에서는 스키마에 자리만 만들었고, `ref_line` ↔ 참조선 교차점 계산이나 `validity` 매핑 코드는 아직 스파이크하지 않았습니다.

---

## 12단계: 차선 마킹(`road_mark`) 변환 스파이크

`Signal`과 `elevation_profile` 중, 이 샘플 맵에 실제 데이터가 있는 `road_mark`부터 끝까지 검증해봤습니다. Lanelet2 경계 way의 `type`(물리적 형태)과 `subtype`(패턴)을 훑어보니 예상보다 다양했습니다.

```
type 분포: curbstone=325, road_border=238, virtual=187, line_thin=102, line_thick=85,
           pedestrian_marking=61, wall=36, zig-zag=13, fence=11, traffic_sign=11, ...
subtype 분포: dashed=124, solid=73, low=141, high=112, solid_dashed=2, dashed_solid=1, ...
```

`(type, subtype)` 조합을 OpenDRIVE `roadMark`(type, color)로 매핑하는 규칙을 짜서 `subtype: road`인 337개 lanelet의 좌우 경계선(674개)에 돌렸습니다. 처음엔 81%만 매핑되고 나머지는 `curbstone`(연석, subtype 없음)과 `virtual`(가상 경계 — 실제 도색은 없지만 편의상 `dashed`/`solid` 태그가 같이 붙어있어서 제 첫 규칙이 놓침) 같은 케이스에서 실패했습니다. 규칙을 두 가지로 보강했습니다.

- `virtual`/`road_border`/`curbstone`/`fence`/`wall`/`guard_rail`/`keepout`처럼 **애초에 도로 표시가 아닌 물리적 경계**는 `subtype`과 무관하게 `roadMark: none`으로 고정합니다.
- `zebra_marking`(횡단보도)/`pedestrian_marking`/`zig-zag`(자전거 우선구간)처럼 **차선 경계이지만 "마킹 패턴"이라는 개념 자체가 안 맞는 것**도 `none`으로 두고, 이런 요소는 별도로 OpenDRIVE의 `object`(횡단보도 등)로 다뤄야 한다는 점을 프로버넌스에 남기기로 했습니다.

재실행 결과 **674개 경계선 전부(100%) 매핑에 성공**했습니다.

```
roadMark 타입 분포: {'none': 474, 'broken': 131, 'solid': 63, 'broken_solid': 2, 'solid_broken': 4}
```

```python
"""
차선 마킹(RoadMark) 변환 스파이크.
Lanelet2 경계 way의 (type, subtype) 조합을 OpenDRIVE roadMark로 매핑한다.
"""
import xml.etree.ElementTree as ET
from collections import defaultdict


def load_osm_with_way_tags(path):
    tree = ET.parse(path)
    root = tree.getroot()

    way_tags = {}
    for w in root.findall("way"):
        way_tags[w.get("id")] = {t.get("k"): t.get("v") for t in w.findall("tag")}

    lanelets = []
    for rel in root.findall("relation"):
        tags = {t.get("k"): t.get("v") for t in rel.findall("tag")}
        if tags.get("type") != "lanelet":
            continue
        left_way = right_way = None
        for m in rel.findall("member"):
            if m.get("role") == "left":
                left_way = m.get("ref")
            elif m.get("role") == "right":
                right_way = m.get("ref")
        if left_way and right_way:
            lanelets.append({
                "id": rel.get("id"), "left": left_way, "right": right_way,
                "subtype": tags.get("subtype"),
            })

    return way_tags, lanelets


# subtype과 무관하게 "표시 없음"으로 취급하는 물리적 타입
NO_MARK_TYPES = {"virtual", "road_border", "curbstone", "fence", "wall", "guard_rail", "keepout"}

MARK_RULES = {
    ("line_thin", "dashed"): ("broken", "white"),
    ("line_thin", "solid"): ("solid", "white"),
    ("line_thick", "solid"): ("solid", "white"),
    ("line_thick", "dashed"): ("broken", "white"),
    ("line_thin", "solid_dashed"): ("solid_broken", "white"),
    ("line_thin", "dashed_solid"): ("broken_solid", "white"),
    ("line_thick", "solid_dashed"): ("solid_broken", "white"),
    ("line_thick", "dashed_solid"): ("broken_solid", "white"),
    ("zebra_marking", None): ("none", "standard"),      # 횡단보도 표시 — 차선 마킹이 아니라 별도 오브젝트로 다뤄야 함
    ("pedestrian_marking", None): ("none", "standard"),
    ("zig-zag", None): ("none", "standard"),            # 자전거 우선구간 지그재그 표시
}


def way_to_road_mark(way_tags, way_id):
    tags = way_tags.get(way_id, {})
    wtype, wsubtype = tags.get("type"), tags.get("subtype")
    if wtype in NO_MARK_TYPES:
        return ("none", "standard"), "매핑됨(물리적 경계, 표시 없음)"
    key = (wtype, wsubtype)
    if key in MARK_RULES:
        return MARK_RULES[key], "매핑됨"
    if wtype in ("zebra_marking", "pedestrian_marking") and (wtype, None) in MARK_RULES:
        return MARK_RULES[(wtype, None)], "매핑됨(subtype 무시)"
    if wtype in ("line_thin", "line_thick") and wsubtype is None:
        return ("solid", "white"), "매핑됨(subtype 없어 기본값 solid 적용, 검토 필요)"
    return None, f"미매핑 (type={wtype}, subtype={wsubtype})"


def main():
    way_tags, lanelets = load_osm_with_way_tags("/Users/yeongjun/Downloads/mapping_example.osm")

    road_lanelets = [ll for ll in lanelets if ll["subtype"] == "road"]
    print(f"subtype=road인 lanelet: {len(road_lanelets)}개 (전체 {len(lanelets)}개 중)")

    mapped, unmapped = 0, 0
    unmapped_reasons = defaultdict(int)
    mark_type_counts = defaultdict(int)

    for ll in road_lanelets:
        for side, way_id in (("left", ll["left"]), ("right", ll["right"])):
            mark, status = way_to_road_mark(way_tags, way_id)
            if mark is None:
                unmapped += 1
                unmapped_reasons[status] += 1
            else:
                mapped += 1
                mark_type_counts[mark[0]] += 1

    total = mapped + unmapped
    print(f"경계선 {total}개(좌우 합산) 중 매핑 성공 {mapped}개 ({mapped/total*100:.0f}%), 실패 {unmapped}개")
    print("roadMark 타입 분포:", dict(mark_type_counts))
    print("미매핑 사유:")
    for reason, count in sorted(unmapped_reasons.items(), key=lambda x: -x[1])[:10]:
        print(f"  {count:3d}개: {reason}")


if __name__ == "__main__":
    main()
```

한 가지 주석("subtype 없어 기본값 solid 적용, 검토 필요")은 실제로 이번 실행 결과에는 걸리지 않았지만, 다른 맵에서는 걸릴 수 있는 애매한 케이스를 위해 남겨뒀습니다 — `dropped_attributes`나 `topology_warnings`처럼, `RoadProvenance`에 "기본값을 적용한 케이스"를 남기는 필드가 하나 더 필요하다는 뜻이기도 합니다(예: `mark_defaulted_count`).

---

## 13단계: A(그룹핑)를 "물리적 연결성" 기준으로 재구현

10단계에서 확정한 방향대로, `Participants.Vehicle` 단독 대신 **Vehicle/Bicycle/Pedestrian 세 `RoutingGraph`의 `following()`/`previous()`/`left()`/`right()`를 합집합으로 묶어** A(그룹핑)를 다시 구현했습니다. 자전거·보행자 공유 구간은 최소 하나의 participant 그래프에서는 정상적으로 라우팅되므로, 셋을 합치면 스퓨리어스 매치 없이(각 그래프 자체가 이미 진짜 물리적 연결만 담고 있으므로) 물리적 연결성에 더 가까워질 거라는 가설이었습니다.

| 지표 | node id 매칭 | `RoutingGraph`(Vehicle만) | `RoutingGraph`(Vehicle+Bicycle+Pedestrian 합집합) |
|---|---|---|---|
| 분기점 / 합류점 | 64 / 63 | 23 / 23 | 25 / 26 |
| Road 개수 | 165 | 134 | **121** |
| Road당 평균 클러스터 수 | 1.48 | 1.94 | **2.08** |
| `subtype: road`인데 고립된 클러스터 | 8 | 21 | **14** |

분기점·합류점은 23→25로 거의 그대로였는데(스퓨리어스 매치가 다시 늘지 않았다는 뜻), Road당 평균 클러스터 수는 늘고 고립 클러스터는 줄었습니다 — 가설대로 실제 연결만 추가로 잡혔습니다. `subtype: road` 고립 클러스터는 21→14로 줄었지만 원래의 8(node id 매칭 기준)까지는 못 돌아왔는데, 그 8개 중 일부는 애초에 이 세 participant 어디에도 안 걸리는 진짜 데이터 결측(9단계에서 확인한 5개)이었기 때문입니다.

```python
"""
A. Lanelet2 -> Road 그룹핑, 다중 participant RoutingGraph 합집합 버전.

Participants.Vehicle 그래프는 자전거/보행자 공유 구간을 표준 차량 경로에서
제외한다(10단계). 이 스크립트는 Vehicle/Bicycle/Pedestrian 세 그래프의
following()/previous()를 합집합으로 묶어 "물리적 연결성"에 더 가깝게 만든다.
"""
from collections import defaultdict
import lanelet2
from lanelet2.projection import UtmProjector


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def build_graphs(lanelet_map):
    participants = [
        lanelet2.traffic_rules.Participants.Vehicle,
        lanelet2.traffic_rules.Participants.Bicycle,
        lanelet2.traffic_rules.Participants.Pedestrian,
    ]
    graphs = []
    for p in participants:
        tr = lanelet2.traffic_rules.create(lanelet2.traffic_rules.Locations.Germany, p)
        graphs.append(lanelet2.routing.RoutingGraph(lanelet_map, tr))
    return graphs


def union_following(graphs, ll):
    result = {}
    for g in graphs:
        for f in g.following(ll):
            result[f.id] = f
    return list(result.values())


def union_side_neighbor(graphs, ll, side):
    """side: 'left' | 'right'. 여러 그래프 중 하나라도 인접을 찾으면 채택한다."""
    for g in graphs:
        neighbor = getattr(g, side)(ll)
        if neighbor is not None:
            return neighbor
        adjacent = getattr(g, f"adjacent{side.capitalize()}")(ll)
        if adjacent is not None:
            return adjacent
    return None


def build_side_clusters(lanelet_map, graphs):
    uf = UnionFind()
    for ll in lanelet_map.laneletLayer:
        uf.find(ll.id)
        left = union_side_neighbor(graphs, ll, "left")
        right = union_side_neighbor(graphs, ll, "right")
        if left is not None:
            uf.union(ll.id, left.id)
        if right is not None:
            uf.union(ll.id, right.id)

    clusters = defaultdict(list)
    for ll in lanelet_map.laneletLayer:
        clusters[uf.find(ll.id)].append(ll.id)
    return list(clusters.values())


def build_cluster_graph(lanelet_map, graphs, clusters):
    cluster_of = {m: idx for idx, members in enumerate(clusters) for m in members}

    successors = defaultdict(set)
    predecessors = defaultdict(set)
    for idx, members in enumerate(clusters):
        for m in members:
            ll = lanelet_map.laneletLayer[m]
            for f in union_following(graphs, ll):
                if f.id in cluster_of:
                    j = cluster_of[f.id]
                    if j != idx:
                        successors[idx].add(j)
                        predecessors[j].add(idx)
    return successors, predecessors


def segment_into_roads(clusters, successors, predecessors):
    lane_count = {idx: len(members) for idx, members in enumerate(clusters)}
    visited = set()
    roads = []
    for start_idx in range(len(clusters)):
        if start_idx in visited:
            continue
        if len(predecessors[start_idx]) == 1:
            pred = next(iter(predecessors[start_idx]))
            if len(successors[pred]) == 1 and lane_count[pred] == lane_count[start_idx]:
                continue
        chain = [start_idx]
        visited.add(start_idx)
        cur = start_idx
        while (
            len(successors[cur]) == 1
            and len(predecessors[next(iter(successors[cur]))]) == 1
            and lane_count[next(iter(successors[cur]))] == lane_count[cur]
        ):
            nxt = next(iter(successors[cur]))
            if nxt in visited:
                break
            chain.append(nxt)
            visited.add(nxt)
            cur = nxt
        roads.append(chain)
    return roads


def main():
    origin = lanelet2.io.Origin(49.0, 8.4)
    projector = UtmProjector(origin)
    lanelet_map = lanelet2.io.load("/data/mapping_example.osm", projector)

    graphs = build_graphs(lanelet_map)
    print(f"lanelets={len(lanelet_map.laneletLayer)}")

    clusters = build_side_clusters(lanelet_map, graphs)
    lane_counts = [len(c) for c in clusters]
    print(f"단면 클러스터 수={len(clusters)}, 차선 수 분포: "
          f"1차선={lane_counts.count(1)}, 2차선={lane_counts.count(2)}, "
          f"3차선 이상={sum(1 for n in lane_counts if n >= 3)}")

    successors, predecessors = build_cluster_graph(lanelet_map, graphs, clusters)
    branch = sum(1 for i in range(len(clusters)) if len(successors[i]) >= 2)
    merge = sum(1 for i in range(len(clusters)) if len(predecessors[i]) >= 2)
    print(f"분기점(successor>=2)={branch}, 합류점(predecessor>=2)={merge}")

    roads = segment_into_roads(clusters, successors, predecessors)
    lens = [len(r) for r in roads]
    print(f"Road 개수={len(roads)}")
    print(f"Road당 평균 클러스터 수={sum(lens)/len(lens):.2f}, 최대={max(lens)}, "
          f"단일 클러스터={lens.count(1)}")

    ll_by_id = {ll.id: ll for ll in lanelet_map.laneletLayer}
    single_roads = [r[0] for r in roads if len(r) == 1]
    near_junction, isolated_idxs = 0, []
    for idx in single_roads:
        is_near = (
            len(successors[idx]) >= 2 or len(predecessors[idx]) >= 2
            or any(len(successors[p]) >= 2 for p in predecessors[idx])
            or any(len(predecessors[s]) >= 2 for s in successors[idx])
        )
        if is_near:
            near_junction += 1
        else:
            isolated_idxs.append(idx)
    print(f"단일 클러스터 Road {len(single_roads)}개 중 교차로 인접 {near_junction}개, "
          f"고립 {len(isolated_idxs)}개")

    subtype_counts = defaultdict(int)
    for idx in isolated_idxs:
        for m in clusters[idx]:
            subtype_counts[ll_by_id[m].attributes["subtype"]] += 1
    print(f"고립 클러스터의 subtype 분포: {dict(subtype_counts)}")

    road_only_isolated = [
        idx for idx in isolated_idxs
        if all(ll_by_id[m].attributes["subtype"] == "road" for m in clusters[idx])
    ]
    print(f"subtype=road인데 고립된 클러스터: {len(road_only_isolated)}개")


if __name__ == "__main__":
    main()
```

남은 14개는 다음 후보로 조사할 대상입니다 — Emergency/Train 같은 다른 participant까지 더 넣어볼지, 아니면 이쯤에서 "물리적 연결성"도 결국 완벽하지 않다는 걸 받아들이고 사람이 검토할 `topology_warnings` 목록으로 넘길지 판단이 필요합니다. 이번 세션에서는 후자 쪽에 가깝게, 남은 14개를 `RoadProvenance.topology_warnings`에 담아 LLM 검증 리포트로 넘기는 것으로 정리합니다 — 모든 위상 문제를 알고리즘만으로 완벽히 풀기보다, 사람/LLM이 검토할 수 있는 형태로 명시적으로 남기는 것도 5단계에서 세운 원칙과 일치합니다.

---

## 14단계: 감김 방향 버그 수정, 그리고 `Signal` 위치 계산 스파이크

`Signal`의 s/t 위치를 계산하려면 정지선(`ref_line`)이 lanelet 중심선과 만나는 지점을 구해야 합니다. 그런데 실제로 짧은 lanelet(교차로 진입 직전 몇 미터짜리) 몇 개를 테스트해보니 중심선 길이가 0에 가깝게 나오는 이상한 케이스가 나왔습니다.

원인을 추적해보니, **일부 lanelet은 왼쪽·오른쪽 경계선(way)이 서로 반대 방향으로 감겨** 있었습니다(왼쪽은 시작→끝, 오른쪽은 끝→시작). 지금까지 B단계에서 중심선을 `(left[i] + right[i]) / 2`로 포인트별 평균을 냈는데, 감김 방향이 반대면 서로 안 맞는 점끼리 평균을 내게 되어 중심선이 뭉개집니다. 두 경계선의 시작점 사이 거리와, 한쪽 시작점-다른쪽 끝점 사이 거리를 비교해 감김 방향을 맞추는 보정(`align_winding`)을 `resample_to_common_length`에 추가했습니다.

이 버그가 지금까지 7단계에서 낸 통계에도 영향을 줬습니다 — 감김 방향이 반대인 짧은 lanelet들이 길이 0에 가깝게 계산되면서 `length < 1.0m` 필터에 걸려 스캔에서 조용히 빠졌던 겁니다. 수정 후 재검증한 결과:

| 지표 | 수정 전 | 수정 후 |
|---|---|---|
| 스캔 성공 lanelet 수 | 93 | **113** |
| `fit_residual_max_m` mean / p95 / max | 2.65cm / 6.74cm / 9.90cm | 2.73cm / 7.15cm / **14.58cm** |
| `fit_residual_rms_m` mean / p95 | 0.93cm / 2.08cm | 1.00cm / 2.58cm |

20개 lanelet이 추가로 스캔에 포함됐고, 평균·중앙값은 거의 그대로였지만 최댓값이 9.9cm → 14.6cm로 조금 나빠졌습니다 — 새로 들어온 lanelet들이 교차로 바로 앞의 복잡한 형상이라 그런 것으로 보입니다. Line+Arc로 충분하다는 결론 자체는 유지되지만, 최악 케이스 허용치를 잡을 때는 이 14.6cm를 기준으로 삼아야 한다는 점을 짚어둡니다.

이 수정을 반영한 뒤, 정지선-중심선 교차점으로 `Signal.s`를 계산하는 스파이크를 6개 `traffic_light` regulatory_element(10개 적용 lanelet)에 돌렸습니다. 처음엔 선분 교차 판정만 썼는데 4개가 실패했습니다 — 확인해보니 **정지선이 lanelet 경계에 정확히 걸쳐 있어서** 교차점이 선분 내부가 아니라 끝점 부근에 있었기 때문이었습니다(지도 제작 시 정지선 위치에서 lanelet을 일부러 끊어두는 관례로 보입니다). 교차점이 없으면 가장 가까운 중심선 끝점으로 폴백하는 로직을 추가해 8/10(80%)까지 해결했습니다. 나머지 2개는 3m 넘게 떨어져 있어 억지로 맞추지 않고 `topology_warnings`로 남기기로 했습니다.

```
regulatory_element=45218 lanelet=45134: s=7.44m / 전체 7.44m (100% 지점, 교차)
regulatory_element=45218 lanelet=45136: s=0.00m / 전체 7.92m (0% 지점, 폴백(끝점, 거리 1.58m))
regulatory_element=45222 lanelet=44972: 정지선 위치를 못 찾음 (중심선 길이 6.6m)
regulatory_element=45224 lanelet=44968: s=0.00m / 전체 6.45m (0% 지점, 교차)
regulatory_element=45224 lanelet=44970: s=6.54m / 전체 6.54m (100% 지점, 교차)
regulatory_element=45226 lanelet=45014: s=0.00m / 전체 3.05m (0% 지점, 폴백(끝점, 거리 1.47m))
regulatory_element=45226 lanelet=45016: s=3.08m / 전체 3.08m (100% 지점, 교차)
regulatory_element=45232 lanelet=45070: s=0.00m / 전체 10.00m (0% 지점, 교차)
regulatory_element=45234 lanelet=45082: s=0.00m / 전체 9.97m (0% 지점, 교차)
regulatory_element=45234 lanelet=45088: 정지선 위치를 못 찾음 (중심선 길이 10.0m)
```

```python
"""
Signal 변환 스파이크: RegulatoryElement의 ref_line(정지선)이 lanelet 중심선과
교차하는 s값을 계산하고, 적용 lanelet 목록을 뽑는다.
"""
import xml.etree.ElementTree as ET
import numpy as np

from spike_fit import load_osm, latlon_to_local_xy, way_points, resample_to_common_length


def load_regulatory_elements(path):
    tree = ET.parse(path)
    root = tree.getroot()

    reg_elements = []
    for rel in root.findall("relation"):
        tags = {t.get("k"): t.get("v") for t in rel.findall("tag")}
        if tags.get("type") != "regulatory_element":
            continue
        ref_line = None
        refers = []
        for m in rel.findall("member"):
            if m.get("role") == "ref_line":
                ref_line = m.get("ref")
            elif m.get("role") == "refers":
                refers.append(m.get("ref"))
        reg_elements.append({
            "id": rel.get("id"), "subtype": tags.get("subtype"),
            "ref_line": ref_line, "refers": refers,
        })

    # 이 regulatory_element를 참조하는 lanelet 찾기
    applicable = {re["id"]: [] for re in reg_elements}
    for rel in root.findall("relation"):
        tags = {t.get("k"): t.get("v") for t in rel.findall("tag")}
        if tags.get("type") != "lanelet":
            continue
        for m in rel.findall("member"):
            if m.get("role") == "regulatory_element" and m.get("ref") in applicable:
                applicable[m.get("ref")].append(rel.get("id"))

    for re in reg_elements:
        re["applicable_lanelet_ids"] = applicable[re["id"]]

    return reg_elements


def segment_intersection(p1, p2, p3, p4):
    """선분 p1-p2와 p3-p4의 교점을 구한다. 없으면 None."""
    d1 = p2 - p1
    d2 = p4 - p3
    denom = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(denom) < 1e-9:
        return None
    t = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / denom
    u = ((p3[0] - p1[0]) * d1[1] - (p3[1] - p1[1]) * d1[0]) / denom
    if 0 <= t <= 1 and 0 <= u <= 1:
        return p1 + t * d1
    return None


def find_stopline_s(centerline: np.ndarray, ref_line_pts: np.ndarray, endpoint_tol: float = 2.0):
    """centerline(폴리라인) 위에서 ref_line(정지선, 보통 2점)이 가로지르는 지점의 s를 찾는다.
    정지선이 lanelet 경계에 정확히 걸쳐 있어 선분 교차 판정에 안 잡히는 경우가 흔해서,
    교차점이 없으면 정지선 중점과 가장 가까운 중심선 끝점(s=0 또는 s=끝)으로 폴백한다."""
    cum_s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(centerline, axis=0), axis=1))])
    for i in range(len(centerline) - 1):
        for j in range(len(ref_line_pts) - 1):
            hit = segment_intersection(
                centerline[i], centerline[i + 1], ref_line_pts[j], ref_line_pts[j + 1]
            )
            if hit is not None:
                partial = np.linalg.norm(hit - centerline[i])
                return cum_s[i] + partial, hit, "교차"

    stopline_mid = ref_line_pts.mean(axis=0)
    d_start = np.linalg.norm(stopline_mid - centerline[0])
    d_end = np.linalg.norm(stopline_mid - centerline[-1])
    nearest_d = min(d_start, d_end)
    if nearest_d <= endpoint_tol:
        if d_start < d_end:
            return 0.0, centerline[0], f"폴백(끝점, 거리 {nearest_d:.2f}m)"
        return cum_s[-1], centerline[-1], f"폴백(끝점, 거리 {nearest_d:.2f}m)"
    return None, None, None


def main():
    nodes, ways, lanelets = load_osm("/Users/yeongjun/Downloads/mapping_example.osm")
    ref_lat, ref_lon = next(iter(nodes.values()))
    xy = latlon_to_local_xy(nodes, ref_lat, ref_lon)
    ll_by_id = {ll["id"]: ll for ll in lanelets}

    reg_elements = load_regulatory_elements("/Users/yeongjun/Downloads/mapping_example.osm")
    traffic_lights = [re for re in reg_elements if re["subtype"] == "traffic_light"]
    print(f"traffic_light regulatory_element {len(traffic_lights)}개")

    for re in traffic_lights:
        if re["ref_line"] not in ways:
            print(f"  id={re['id']}: ref_line way {re['ref_line']}를 못 찾음")
            continue
        ref_line_pts = way_points(ways, xy, re["ref_line"])

        for ll_id in re["applicable_lanelet_ids"]:
            ll = ll_by_id.get(ll_id)
            if ll is None:
                continue
            left = way_points(ways, xy, ll["left"])
            right = way_points(ways, xy, ll["right"])
            left_r, right_r = resample_to_common_length(left, right, n=50)
            centerline = (left_r + right_r) / 2

            s, hit, method = find_stopline_s(centerline, ref_line_pts)
            total_len = np.sum(np.linalg.norm(np.diff(centerline, axis=0), axis=1))
            if s is None:
                print(f"  regulatory_element={re['id']} lanelet={ll_id}: 정지선 위치를 못 찾음 "
                      f"(중심선 길이 {total_len:.1f}m)")
            else:
                print(f"  regulatory_element={re['id']} lanelet={ll_id}: "
                      f"s={s:.2f}m / 전체 {total_len:.2f}m ({s/total_len*100:.0f}% 지점, {method})")


if __name__ == "__main__":
    main()
```

---

## 15단계: LLM 시각 검증 파이프라인을 실제로 돌려본다

5단계에서 세운 원칙("정량 지표는 코드가 계산하고, LLM은 그 지표와 시각화를 검토")을 실제로 구현해봤습니다. B단계(참조선 피팅)와 14단계(Signal 위치)의 결과를 인터랙티브 웹 뷰어로 만들고, 헤드리스 브라우저로 스크린샷을 찍어 비전 모델에게 검토받는 파이프라인입니다.

**뷰어**: 원본 lanelet 중심선(회색), 피팅된 참조선(Line=청록, Arc=주황), 신호등 위치(빨간 점)를 한 SVG 위에 겹쳐 그리고, 드래그/휠로 확대·축소하면서 도형을 클릭하면 잔차·s값 같은 상세 정보가 뜨는 페이지입니다. 데이터는 B, 12, 14단계에서 만든 파이프라인 결과를 JSON으로 내보내 그대로 임베드했습니다.

**데이터 export (`export_viz_data.py`)**: B, 12(road_mark), 14(Signal)단계의 결과를 뷰어가 읽을 JSON 하나로 합칩니다.

```python
"""
지금까지의 스파이크 결과(B: 참조선 피팅, road_mark, Signal)를 JSON으로 내보낸다.
웹 아티팩트에서 렌더링해 사람/LLM이 시각적으로 검증할 수 있게 한다.
"""
import json
import numpy as np

from spike_fit import (
    load_osm, latlon_to_local_xy, way_points, resample_to_common_length,
    fit_reference_line, discrete_curvature,
)
from spike_roadmark import load_osm_with_way_tags, way_to_road_mark
from spike_signal import load_regulatory_elements, find_stopline_s


def main():
    nodes, ways, lanelets = load_osm("/Users/yeongjun/Downloads/mapping_example.osm")
    ref_lat, ref_lon = next(iter(nodes.values()))
    xy = latlon_to_local_xy(nodes, ref_lat, ref_lon)
    way_tags, _ = load_osm_with_way_tags("/Users/yeongjun/Downloads/mapping_example.osm")

    lanelet_records = []
    fitted_records = []

    for ll in lanelets:
        try:
            left = way_points(ways, xy, ll["left"])
            right = way_points(ways, xy, ll["right"])
        except KeyError:
            continue
        if len(left) < 2 or len(right) < 2:
            continue

        left_r, right_r = resample_to_common_length(left, right, n=30)
        centerline = (left_r + right_r) / 2
        length = float(np.sum(np.linalg.norm(np.diff(centerline, axis=0), axis=1)))

        left_mark, _ = way_to_road_mark(way_tags, ll["left"])
        right_mark, _ = way_to_road_mark(way_tags, ll["right"])

        lanelet_records.append({
            "id": ll["id"],
            "subtype": ll["subtype"],
            "left": left_r.round(2).tolist(),
            "right": right_r.round(2).tolist(),
            "centerline": centerline.round(2).tolist(),
            "length_m": round(length, 2),
            "left_mark": left_mark[0] if left_mark else None,
            "right_mark": right_mark[0] if right_mark else None,
        })

        if ll["subtype"] == "road" and length >= 1.0:
            try:
                segments, stats = fit_reference_line(centerline, epsilon=0.15)
            except Exception:
                continue
            seg_records = []
            for kind, seg, chunk in segments:
                seg_records.append({
                    "kind": kind,
                    "points": chunk.round(3).tolist(),
                })
            fitted_records.append({
                "lanelet_id": ll["id"],
                "segments": seg_records,
                "fit_residual_max_m": round(stats["fit_residual_max_m"], 4),
                "fit_residual_rms_m": round(stats["fit_residual_rms_m"], 4),
            })

    # Signal
    ll_by_id = {ll["id"]: ll for ll in lanelets}
    reg_elements = load_regulatory_elements("/Users/yeongjun/Downloads/mapping_example.osm")
    signal_records = []
    for re in reg_elements:
        if re["subtype"] != "traffic_light" or re["ref_line"] not in ways:
            continue
        ref_line_pts = way_points(ways, xy, re["ref_line"])
        for ll_id in re["applicable_lanelet_ids"]:
            ll = ll_by_id.get(ll_id)
            if ll is None:
                continue
            left = way_points(ways, xy, ll["left"])
            right = way_points(ways, xy, ll["right"])
            left_r, right_r = resample_to_common_length(left, right, n=50)
            centerline = (left_r + right_r) / 2
            s, hit, method = find_stopline_s(centerline, ref_line_pts)
            signal_records.append({
                "regulatory_element_id": re["id"],
                "lanelet_id": ll_id,
                "position": hit.round(2).tolist() if hit is not None else None,
                "s": round(s, 2) if s is not None else None,
                "method": method,
            })

    data = {
        "lanelets": lanelet_records,
        "fitted": fitted_records,
        "signals": signal_records,
        "meta": {
            "source": "mapping_example.osm (Lanelet2 official sample, Karlsruhe)",
            "total_lanelets": len(lanelets),
            "fitted_count": len(fitted_records),
        },
    }

    with open("viz_data.json", "w") as f:
        json.dump(data, f)
    print(f"lanelets={len(lanelet_records)}, fitted={len(fitted_records)}, signals={len(signal_records)}")


if __name__ == "__main__":
    main()
```

**뷰어 소스 (`map_viewer_template.html`)**: `__DATA_JSON__` 자리에 위 스크립트가 만든 `viz_data.json` 내용을 그대로 끼워 넣으면 완성됩니다.

```html
<title>Lanelet2 → OpenDRIVE 변환 검증 뷰어</title>
<style>
  :root {
    --bg: #0b0e14;
    --panel: #12161f;
    --panel-2: #171c28;
    --line: #232838;
    --line-soft: #1a1f2c;
    --text: #e6e9f0;
    --text-muted: #8992a8;
    --text-faint: #565f78;
    --accent: #5ee6d0;
    --accent-dim: #35594f;
    --raw: #454e64;
    --warn: #f0a94e;
    --good: #7fd88f;
    --signal: #ff6b57;
    --mono: ui-monospace, "SF Mono", "Cascadia Code", "Roboto Mono", Consolas, monospace;
    --sans: ui-sans-serif, "Inter", "Segoe UI", -apple-system, sans-serif;
  }
  :root[data-theme="light"] {
    --bg: #f4f5f8;
    --panel: #ffffff;
    --panel-2: #eef0f5;
    --line: #d8dbe4;
    --line-soft: #e7e9ef;
    --text: #1a1e29;
    --text-muted: #5b6478;
    --text-faint: #9aa2b5;
    --accent: #0e8f7a;
    --accent-dim: #cdece5;
    --raw: #7b8399;
    --warn: #b8720c;
    --good: #2f8f4e;
    --signal: #d33f2c;
  }
  @media (prefers-color-scheme: light) {
    :root:not([data-theme="dark"]) {
      --bg: #f4f5f8;
      --panel: #ffffff;
      --panel-2: #eef0f5;
      --line: #d8dbe4;
      --line-soft: #e7e9ef;
      --text: #1a1e29;
      --text-muted: #5b6478;
      --text-faint: #9aa2b5;
      --accent: #0e8f7a;
      --accent-dim: #cdece5;
      --raw: #a7adbd;
      --warn: #b8720c;
      --good: #2f8f4e;
      --signal: #d33f2c;
    }
  }

  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0; height: 100%;
    background: var(--bg); color: var(--text);
    font-family: var(--sans);
    overflow: hidden;
  }

  .app {
    display: grid;
    grid-template-columns: 1fr 340px;
    grid-template-rows: 52px 1fr;
    grid-template-areas: "header header" "map sidebar";
    height: 100vh;
  }
  @media (max-width: 760px) {
    .app {
      grid-template-columns: 1fr;
      grid-template-rows: 52px 55vh 1fr;
      grid-template-areas: "header" "map" "sidebar";
    }
  }

  header {
    grid-area: header;
    display: flex; align-items: center; gap: 12px;
    padding: 0 16px;
    border-bottom: 1px solid var(--line);
    background: var(--panel);
  }
  header .title { font-weight: 600; font-size: 14px; letter-spacing: 0.01em; }
  header .subtitle {
    font-family: var(--mono); font-size: 11.5px; color: var(--text-muted);
  }
  header .spacer { flex: 1; }
  header .badge {
    font-family: var(--mono); font-size: 11px; color: var(--text-muted);
    border: 1px solid var(--line); border-radius: 3px; padding: 3px 8px;
  }

  .map-wrap {
    grid-area: map;
    position: relative;
    background:
      radial-gradient(circle at 50% 0%, var(--line-soft) 0%, var(--bg) 70%);
    overflow: hidden;
    cursor: grab;
  }
  .map-wrap.dragging { cursor: grabbing; }
  .map-wrap svg { display: block; width: 100%; height: 100%; }

  .hint {
    position: absolute; left: 12px; bottom: 12px;
    font-family: var(--mono); font-size: 10.5px; color: var(--text-faint);
    background: color-mix(in srgb, var(--panel) 80%, transparent);
    padding: 4px 8px; border-radius: 3px; pointer-events: none;
  }

  .zoom-controls {
    position: absolute; right: 12px; bottom: 12px;
    display: flex; flex-direction: column; gap: 1px;
    border: 1px solid var(--line); border-radius: 4px; overflow: hidden;
  }
  .zoom-controls button {
    width: 28px; height: 26px;
    background: var(--panel); color: var(--text);
    border: none; border-bottom: 1px solid var(--line);
    font-family: var(--mono); font-size: 14px; cursor: pointer;
  }
  .zoom-controls button:last-child { border-bottom: none; }
  .zoom-controls button:hover { background: var(--panel-2); }

  aside {
    grid-area: sidebar;
    border-left: 1px solid var(--line);
    background: var(--panel);
    overflow-y: auto;
    display: flex; flex-direction: column;
  }
  .sec {
    padding: 14px 16px;
    border-bottom: 1px solid var(--line);
  }
  .sec h2 {
    margin: 0 0 10px;
    font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.08em;
    color: var(--text-muted); font-weight: 600;
  }

  .stat-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
  }
  .stat {
    background: var(--panel-2); border-radius: 5px; padding: 8px 10px;
  }
  .stat .n {
    font-family: var(--mono); font-variant-numeric: tabular-nums;
    font-size: 18px; font-weight: 600; line-height: 1.1;
  }
  .stat .l { font-size: 10.5px; color: var(--text-muted); margin-top: 3px; }

  .toggle-row {
    display: flex; align-items: center; gap: 9px;
    padding: 6px 0; font-size: 12.5px; cursor: pointer;
    user-select: none;
  }
  .toggle-row input { accent-color: var(--accent); width: 14px; height: 14px; }
  .swatch { width: 18px; height: 3px; border-radius: 2px; flex-shrink: 0; }
  .swatch.dot { width: 9px; height: 9px; border-radius: 50%; }
  .toggle-row .lbl { flex: 1; }
  .toggle-row .cnt { font-family: var(--mono); color: var(--text-faint); font-size: 11px; }

  .residual-bar-row {
    display: flex; align-items: center; gap: 8px; font-size: 11.5px;
    padding: 3px 0; font-family: var(--mono); color: var(--text-muted);
  }
  .residual-bar-row .track {
    flex: 1; height: 6px; background: var(--panel-2); border-radius: 3px; overflow: hidden;
  }
  .residual-bar-row .fill { height: 100%; background: var(--accent); }
  .residual-bar-row .val { width: 46px; text-align: right; font-variant-numeric: tabular-nums; }

  .signal-list { display: flex; flex-direction: column; gap: 6px; }
  .signal-item {
    background: var(--panel-2); border-radius: 5px; padding: 7px 9px;
    font-size: 11.5px; cursor: pointer; border: 1px solid transparent;
  }
  .signal-item:hover { border-color: var(--line); }
  .signal-item .id-row {
    display: flex; justify-content: space-between; align-items: center;
    font-family: var(--mono); color: var(--text);
  }
  .signal-item .method {
    margin-top: 2px; font-size: 10.5px; color: var(--text-muted);
  }
  .pill {
    font-family: var(--mono); font-size: 9.5px; padding: 1px 6px; border-radius: 8px;
    text-transform: uppercase; letter-spacing: 0.04em;
  }
  .pill.ok { background: color-mix(in srgb, var(--good) 22%, transparent); color: var(--good); }
  .pill.warn { background: color-mix(in srgb, var(--warn) 22%, transparent); color: var(--warn); }
  .pill.bad { background: color-mix(in srgb, var(--signal) 22%, transparent); color: var(--signal); }

  #inspector {
    padding: 14px 16px;
    font-size: 12px;
    color: var(--text-muted);
    flex: 1;
  }
  #inspector .empty { font-style: normal; }
  #inspector .field { display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px dashed var(--line-soft); }
  #inspector .field .k { color: var(--text-muted); }
  #inspector .field .v { font-family: var(--mono); color: var(--text); font-variant-numeric: tabular-nums; }
  #inspector h3 { margin: 0 0 8px; font-size: 13px; color: var(--text); }

  .llm-note {
    padding: 12px 16px; font-size: 11px; line-height: 1.5; color: var(--text-faint);
    border-top: 1px solid var(--line);
  }
  .llm-note b { color: var(--text-muted); }

  ::-webkit-scrollbar { width: 8px; }
  ::-webkit-scrollbar-thumb { background: var(--line); border-radius: 4px; }
</style>

<div class="app">
  <header>
    <span class="title">Lanelet2 → OpenDRIVE 변환 검증 뷰어</span>
    <span class="subtitle">mapping_example.osm · Karlsruhe</span>
    <span class="spacer"></span>
    <span class="badge" id="hover-coord">x: — · y: —</span>
  </header>

  <div class="map-wrap" id="mapWrap">
    <svg id="svg" viewBox="0 0 100 100"></svg>
    <div class="hint">드래그로 이동 · 휠로 확대/축소 · 도형 클릭 시 우측에 상세 정보</div>
    <div class="zoom-controls">
      <button id="zoomIn">+</button>
      <button id="zoomOut">–</button>
      <button id="zoomReset">⤢</button>
    </div>
  </div>

  <aside>
    <div class="sec">
      <h2>데이터셋</h2>
      <div class="stat-grid">
        <div class="stat"><div class="n" id="stat-total">–</div><div class="l">전체 lanelet</div></div>
        <div class="stat"><div class="n" id="stat-fitted">–</div><div class="l">참조선 피팅됨</div></div>
        <div class="stat"><div class="n" id="stat-signals">–</div><div class="l">신호등(regulatory)</div></div>
        <div class="stat"><div class="n" id="stat-resolved">–</div><div class="l">위치 계산 성공</div></div>
      </div>
    </div>

    <div class="sec">
      <h2>레이어</h2>
      <label class="toggle-row">
        <input type="checkbox" id="layer-raw" checked>
        <span class="swatch" style="background:var(--raw)"></span>
        <span class="lbl">원본 경계선</span>
        <span class="cnt" id="cnt-raw">–</span>
      </label>
      <label class="toggle-row">
        <input type="checkbox" id="layer-line" checked>
        <span class="swatch" style="background:var(--accent)"></span>
        <span class="lbl">피팅: Line</span>
        <span class="cnt" id="cnt-line">–</span>
      </label>
      <label class="toggle-row">
        <input type="checkbox" id="layer-arc" checked>
        <span class="swatch" style="background:var(--warn)"></span>
        <span class="lbl">피팅: Arc</span>
        <span class="cnt" id="cnt-arc">–</span>
      </label>
      <label class="toggle-row">
        <input type="checkbox" id="layer-signal" checked>
        <span class="swatch dot" style="background:var(--signal)"></span>
        <span class="lbl">신호등 위치</span>
        <span class="cnt" id="cnt-signal">–</span>
      </label>
    </div>

    <div class="sec">
      <h2>참조선 피팅 잔차 (fit_residual_max_m)</h2>
      <div id="residual-bars"></div>
    </div>

    <div class="sec">
      <h2>신호등 위치 계산 결과</h2>
      <div class="signal-list" id="signal-list"></div>
    </div>

    <div id="inspector"><span class="empty" style="color:var(--text-faint)">지도에서 도형을 클릭하면 상세 정보가 여기 표시됩니다.</span></div>

    <div class="llm-note">
      <b>LLM 검증에 쓰는 법</b> — 이 페이지는 정적 페이지라 브라우저에서 직접 LLM을 호출하지 않습니다. 화면을 캡처하거나 좌측 하단 데이터를 내보내서, "이 피팅 결과가 원본 경계선과 시각적으로 잘 맞는지, 잔차 분포에 이상치가 있는지" 형태의 질문과 함께 LLM에게 넘겨 검토받으세요.
    </div>
  </aside>
</div>

<script id="data" type="application/json">__DATA_JSON__</script>
<script>
(function () {
  const DATA = JSON.parse(document.getElementById('data').textContent);
  const svg = document.getElementById('svg');
  const NS = 'http://www.w3.org/2000/svg';

  // ---- bounding box ----
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  DATA.lanelets.forEach(ll => {
    ll.left.concat(ll.right).forEach(([x, y]) => {
      if (x < minX) minX = x; if (x > maxX) maxX = x;
      if (y < minY) minY = y; if (y > maxY) maxY = y;
    });
  });
  const padX = (maxX - minX) * 0.03, padY = (maxY - minY) * 0.03;
  const vbX = minX - padX, vbY = minY - padY;
  const vbW = (maxX - minX) + padX * 2, vbH = (maxY - minY) + padY * 2;

  // y축 반전 (지리 좌표 y-up -> SVG y-down) — 전체 범위(vbY/vbH) 기준으로 고정한다.
  function flip(y) { return vbY + vbH - (y - vbY); }
  function pathFrom(points) {
    return points.map((p, i) => (i === 0 ? 'M' : 'L') + p[0] + ',' + flip(p[1])).join(' ');
  }

  // 초기 화면은 전체 bbox가 아니라 밀집 구역(1~99 백분위) 기준으로 맞춘다.
  // 극소수 이상치 lanelet(먼 rail 구간 등) 때문에 대부분 빈 화면이 나오는 것을 막기 위함.
  function percentile(arr, p) {
    const sorted = [...arr].sort((a, b) => a - b);
    return sorted[Math.floor(sorted.length * p)];
  }
  const allX = [], allY = [];
  DATA.lanelets.forEach(ll => ll.centerline.forEach(([x, y]) => { allX.push(x); allY.push(y); }));
  const coreMinX = percentile(allX, 0.01), coreMaxX = percentile(allX, 0.99);
  const coreMinY = percentile(allY, 0.01), coreMaxY = percentile(allY, 0.99);
  const corePadX = (coreMaxX - coreMinX) * 0.08, corePadY = (coreMaxY - coreMinY) * 0.08;
  const defaultView = {
    x: coreMinX - corePadX,
    y: flip(coreMaxY + corePadY),
    w: (coreMaxX - coreMinX) + corePadX * 2,
    h: (coreMaxY - coreMinY) + corePadY * 2,
  };

  svg.setAttribute('viewBox', `${defaultView.x} ${defaultView.y} ${defaultView.w} ${defaultView.h}`);

  const gRaw = document.createElementNS(NS, 'g');
  const gLine = document.createElementNS(NS, 'g');
  const gArc = document.createElementNS(NS, 'g');
  const gSignal = document.createElementNS(NS, 'g');
  [gRaw, gLine, gArc, gSignal].forEach(g => svg.appendChild(g));

  const strokeW = Math.max(vbW, vbH) / 900;

  let rawCount = 0, lineCount = 0, arcCount = 0;

  // 원본 경계선 (센터라인만 얇게 — 좌우 다 그리면 너무 빽빽함)
  DATA.lanelets.forEach(ll => {
    const el = document.createElementNS(NS, 'path');
    el.setAttribute('d', pathFrom(ll.centerline));
    el.setAttribute('fill', 'none');
    el.setAttribute('stroke', 'var(--raw)');
    el.setAttribute('stroke-width', strokeW);
    el.setAttribute('vector-effect', 'non-scaling-stroke');
    el.setAttribute('opacity', '0.7');
    el.dataset.kind = 'raw';
    el.dataset.id = ll.id;
    gRaw.appendChild(el);
    rawCount++;
  });

  // 피팅된 참조선 세그먼트
  DATA.fitted.forEach(f => {
    f.segments.forEach((seg, i) => {
      const el = document.createElementNS(NS, 'path');
      el.setAttribute('d', pathFrom(seg.points));
      el.setAttribute('fill', 'none');
      el.setAttribute('stroke', seg.kind === 'line' ? 'var(--accent)' : 'var(--warn)');
      el.setAttribute('stroke-width', strokeW * 1.7);
      el.setAttribute('vector-effect', 'non-scaling-stroke');
      el.setAttribute('stroke-linecap', 'round');
      el.dataset.kind = 'fitted';
      el.dataset.lanelet = f.lanelet_id;
      el.dataset.segKind = seg.kind;
      el.dataset.residualMax = f.fit_residual_max_m;
      el.dataset.residualRms = f.fit_residual_rms_m;
      el.style.cursor = 'pointer';
      (seg.kind === 'line' ? gLine : gArc).appendChild(el);
      if (seg.kind === 'line') lineCount++; else arcCount++;
    });
  });

  // 신호등
  let resolvedCount = 0;
  DATA.signals.forEach(s => {
    if (!s.position) return;
    resolvedCount++;
    const el = document.createElementNS(NS, 'circle');
    el.setAttribute('cx', s.position[0]);
    el.setAttribute('cy', flip(s.position[1]));
    el.classList.add('signal-marker');
    el.setAttribute('fill', 'var(--signal)');
    el.setAttribute('stroke', 'var(--bg)');
    el.setAttribute('vector-effect', 'non-scaling-stroke');
    el.setAttribute('stroke-width', 1.5);
    el.dataset.kind = 'signal';
    el.dataset.re = s.regulatory_element_id;
    el.dataset.lanelet = s.lanelet_id;
    el.dataset.s = s.s;
    el.dataset.method = s.method;
    el.style.cursor = 'pointer';
    gSignal.appendChild(el);
  });

  document.getElementById('stat-total').textContent = DATA.meta.total_lanelets;
  document.getElementById('stat-fitted').textContent = DATA.meta.fitted_count;
  document.getElementById('stat-signals').textContent = DATA.signals.length;
  document.getElementById('stat-resolved').textContent = resolvedCount + ' / ' + DATA.signals.length;
  document.getElementById('cnt-raw').textContent = rawCount;
  document.getElementById('cnt-line').textContent = lineCount;
  document.getElementById('cnt-arc').textContent = arcCount;
  document.getElementById('cnt-signal').textContent = resolvedCount;

  // ---- 잔차 히스토그램 (간단 버킷) ----
  const residuals = DATA.fitted.map(f => f.fit_residual_max_m);
  const buckets = [
    { label: '< 2cm', test: r => r < 0.02 },
    { label: '2–5cm', test: r => r >= 0.02 && r < 0.05 },
    { label: '5–10cm', test: r => r >= 0.05 && r < 0.10 },
    { label: '≥ 10cm', test: r => r >= 0.10 },
  ];
  const barsEl = document.getElementById('residual-bars');
  const maxCount = Math.max(...buckets.map(b => residuals.filter(b.test).length));
  buckets.forEach(b => {
    const n = residuals.filter(b.test).length;
    const row = document.createElement('div');
    row.className = 'residual-bar-row';
    row.innerHTML = `<span style="width:52px">${b.label}</span>
      <span class="track"><span class="fill" style="width:${(n / (maxCount || 1) * 100)}%"></span></span>
      <span class="val">${n}건</span>`;
    barsEl.appendChild(row);
  });

  // ---- 신호등 목록 ----
  const listEl = document.getElementById('signal-list');
  DATA.signals.forEach(s => {
    const item = document.createElement('div');
    item.className = 'signal-item';
    const pillClass = s.method === '교차' ? 'ok' : (s.method && s.method.startsWith('폴백') ? 'warn' : 'bad');
    const pillText = s.method === '교차' ? 'OK' : (s.method && s.method.startsWith('폴백') ? 'FALLBACK' : 'FAIL');
    item.innerHTML = `
      <div class="id-row"><span>re=${s.regulatory_element_id} · ll=${s.lanelet_id}</span><span class="pill ${pillClass}">${pillText}</span></div>
      <div class="method">${s.s !== null ? 's=' + s.s + 'm' : '위치 계산 실패'} ${s.method ? '· ' + s.method : ''}</div>
    `;
    item.addEventListener('click', () => focusOn(s.lanelet_id));
    listEl.appendChild(item);
  });

  // ---- pan/zoom ----
  const wrap = document.getElementById('mapWrap');
  let view = { ...defaultView };
  window.requestAnimationFrame(() => rescaleSignalMarkers()); // 최초 렌더 시 마커 크기 설정
  function applyView() {
    svg.setAttribute('viewBox', `${view.x} ${view.y} ${view.w} ${view.h}`);
    rescaleSignalMarkers();
  }
  function rescaleSignalMarkers() {
    const rect = wrap.getBoundingClientRect();
    if (!rect.width) return;
    const pxToWorld = view.w / rect.width;
    const targetScreenPx = 5;
    document.querySelectorAll('.signal-marker').forEach(el => {
      el.setAttribute('r', targetScreenPx * pxToWorld);
    });
  }

  let dragging = false, lastPx = null;
  wrap.addEventListener('mousedown', e => { dragging = true; lastPx = [e.clientX, e.clientY]; wrap.classList.add('dragging'); });
  window.addEventListener('mouseup', () => { dragging = false; wrap.classList.remove('dragging'); });
  window.addEventListener('mousemove', e => {
    const rect = wrap.getBoundingClientRect();
    const scale = view.w / rect.width;
    const gx = view.x + (e.clientX - rect.left) * scale;
    const gy = view.y + (e.clientY - rect.top) * (view.h / rect.height);
    document.getElementById('hover-coord').textContent = `x: ${gx.toFixed(1)} · y: ${(vbY + vbH - gy).toFixed(1)}`;
    if (!dragging) return;
    const dx = (e.clientX - lastPx[0]) * scale;
    const dy = (e.clientY - lastPx[1]) * (view.h / rect.height);
    view.x -= dx; view.y -= dy;
    lastPx = [e.clientX, e.clientY];
    applyView();
  });
  wrap.addEventListener('wheel', e => {
    e.preventDefault();
    const factor = e.deltaY > 0 ? 1.15 : 1 / 1.15;
    const rect = wrap.getBoundingClientRect();
    const px = (e.clientX - rect.left) / rect.width;
    const py = (e.clientY - rect.top) / rect.height;
    const newW = view.w * factor, newH = view.h * factor;
    view.x += (view.w - newW) * px;
    view.y += (view.h - newH) * py;
    view.w = newW; view.h = newH;
    applyView();
  }, { passive: false });

  document.getElementById('zoomIn').onclick = () => { view.w *= 0.8; view.h *= 0.8; view.x += view.w * 0.125; view.y += view.h * 0.125; applyView(); };
  document.getElementById('zoomOut').onclick = () => { view.x -= view.w * 0.125; view.y -= view.h * 0.125; view.w *= 1.25; view.h *= 1.25; applyView(); };
  document.getElementById('zoomReset').onclick = () => { view = { ...defaultView }; applyView(); };

  function focusOn(laneletId) {
    const ll = DATA.lanelets.find(l => l.id === laneletId);
    if (!ll) return;
    let mnx = Infinity, mny = Infinity, mxx = -Infinity, mxy = -Infinity;
    ll.left.concat(ll.right).forEach(([x, y]) => {
      if (x < mnx) mnx = x; if (x > mxx) mxx = x;
      if (y < mny) mny = y; if (y > mxy) mxy = y;
    });
    const cx = (mnx + mxx) / 2, cy = (mny + mxy) / 2;
    const span = Math.max(mxx - mnx, mxy - mny, 8) * 5;
    view = { x: cx - span / 2, y: flip(cy) - span / 2, w: span, h: span };
    applyView();
  }

  // ---- 레이어 토글 ----
  document.getElementById('layer-raw').addEventListener('change', e => gRaw.style.display = e.target.checked ? '' : 'none');
  document.getElementById('layer-line').addEventListener('change', e => gLine.style.display = e.target.checked ? '' : 'none');
  document.getElementById('layer-arc').addEventListener('change', e => gArc.style.display = e.target.checked ? '' : 'none');
  document.getElementById('layer-signal').addEventListener('change', e => gSignal.style.display = e.target.checked ? '' : 'none');

  // ---- inspector ----
  const inspector = document.getElementById('inspector');
  svg.addEventListener('click', e => {
    const t = e.target;
    if (t.dataset.kind === 'fitted') {
      inspector.innerHTML = `
        <h3>참조선 세그먼트</h3>
        <div class="field"><span class="k">lanelet id</span><span class="v">${t.dataset.lanelet}</span></div>
        <div class="field"><span class="k">타입</span><span class="v">${t.dataset.segKind}</span></div>
        <div class="field"><span class="k">fit_residual_max_m</span><span class="v">${(+t.dataset.residualMax * 100).toFixed(2)}cm</span></div>
        <div class="field"><span class="k">fit_residual_rms_m</span><span class="v">${(+t.dataset.residualRms * 100).toFixed(2)}cm</span></div>
      `;
    } else if (t.dataset.kind === 'signal') {
      inspector.innerHTML = `
        <h3>신호등 (traffic_light)</h3>
        <div class="field"><span class="k">regulatory_element</span><span class="v">${t.dataset.re}</span></div>
        <div class="field"><span class="k">lanelet id</span><span class="v">${t.dataset.lanelet}</span></div>
        <div class="field"><span class="k">s</span><span class="v">${t.dataset.s}m</span></div>
        <div class="field"><span class="k">계산 방식</span><span class="v">${t.dataset.method}</span></div>
      `;
    } else if (t.dataset.kind === 'raw') {
      const ll = DATA.lanelets.find(l => l.id === t.dataset.id);
      inspector.innerHTML = `
        <h3>원본 lanelet</h3>
        <div class="field"><span class="k">id</span><span class="v">${ll.id}</span></div>
        <div class="field"><span class="k">subtype</span><span class="v">${ll.subtype}</span></div>
        <div class="field"><span class="k">길이</span><span class="v">${ll.length_m}m</span></div>
        <div class="field"><span class="k">left mark</span><span class="v">${ll.left_mark ?? '–'}</span></div>
        <div class="field"><span class="k">right mark</span><span class="v">${ll.right_mark ?? '–'}</span></div>
      `;
    }
  });
  window.focusOnLanelet = focusOn;
})();
</script>
```

**캡처+검증 스크립트**: Playwright로 이 페이지를 headless Chromium에 띄우고 스크린샷을 찍은 뒤, 정량 지표 요약과 함께 Claude에게 넘겨 시각적 이상 여부를 판단받습니다.

```python
"""
LLM 시각 검증 파이프라인: 헤드리스 브라우저로 map_viewer.html을 캡처하고,
Claude(비전 지원 모델)에게 스크린샷 + 정량 지표를 같이 넘겨 검증 리포트를 받는다.

사용법:
  export ANTHROPIC_API_KEY=...
  python3 llm_visual_review.py --html map_viewer.html

의존성: pip install playwright anthropic && playwright install chromium
"""
import argparse
import base64
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


def capture_screenshots(html_path: str, out_dir: Path) -> list[tuple[str, Path]]:
    """전체 뷰 + 잔차가 가장 큰 lanelet 확대 뷰를 찍는다."""
    out_dir.mkdir(parents=True, exist_ok=True)
    shots = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.goto(f"file://{Path(html_path).resolve()}")
        page.wait_for_timeout(800)  # SVG 렌더링 대기

        # 1) 전체 뷰
        full_path = out_dir / "01_overview.png"
        page.screenshot(path=str(full_path))
        shots.append(("전체 지도 뷰 (원본 경계선 + 피팅된 참조선 + 신호등)", full_path))

        # 2) 잔차가 가장 큰 lanelet으로 확대
        worst_id = page.evaluate("""
            () => {
              const fitted = JSON.parse(document.getElementById('data').textContent).fitted;
              let worst = fitted[0];
              for (const f of fitted) if (f.fit_residual_max_m > worst.fit_residual_max_m) worst = f;
              return worst.lanelet_id;
            }
        """)
        page.evaluate(f"() => window.focusOnLanelet('{worst_id}')")
        el = page.query_selector(f'[data-kind="fitted"][data-lanelet="{worst_id}"]')
        if el:
            el.click(force=True)
        page.wait_for_timeout(300)
        worst_path = out_dir / "02_worst_residual.png"
        page.screenshot(path=str(worst_path))
        shots.append((f"잔차 최댓값 lanelet(id={worst_id}) 인스펙터 확인", worst_path))

        browser.close()

    return shots


def build_metrics_summary(html_path: str) -> str:
    html = Path(html_path).read_text()
    start = html.find('<script id="data" type="application/json">')
    start = html.find(">", start) + 1
    end = html.find("</script>", start)
    data = json.loads(html[start:end])

    residuals = [f["fit_residual_max_m"] for f in data["fitted"]]
    residuals.sort()
    n = len(residuals)
    signals_ok = sum(1 for s in data["signals"] if s.get("method") == "교차")
    signals_fallback = sum(1 for s in data["signals"] if (s.get("method") or "").startswith("폴백"))
    signals_fail = len(data["signals"]) - signals_ok - signals_fallback

    return f"""
- 전체 lanelet: {data['meta']['total_lanelets']}개, 참조선 피팅됨: {len(data['fitted'])}개
- fit_residual_max_m: mean={sum(residuals)/n:.4f} p50={residuals[n//2]:.4f} max={residuals[-1]:.4f}
- 신호등 위치 계산: 교차 성공 {signals_ok} / 끝점 폴백 {signals_fallback} / 실패 {signals_fail} (전체 {len(data['signals'])})
""".strip()


def call_llm_review(shots: list[tuple[str, Path]], metrics: str, model: str) -> str:
    import anthropic

    client = anthropic.Anthropic()
    content = [
        {
            "type": "text",
            "text": (
                "당신은 Lanelet2 -> OpenDRIVE 지도 변환 파이프라인의 QA 리뷰어입니다. "
                "아래는 파이프라인이 계산한 정량 지표와, 결과를 시각화한 스크린샷입니다.\n\n"
                f"[정량 지표]\n{metrics}\n\n"
                "스크린샷을 보고 다음을 판단해주세요:\n"
                "1. 피팅된 참조선(청록/주황)이 원본 경계선(회색)에서 시각적으로 벗어나 보이는 구간이 있는가?\n"
                "2. 신호등 위치(빨간 점)가 도로 위 합리적인 지점에 찍혀 있는가, 아니면 엉뚱한 곳에 있는가?\n"
                "3. 정량 지표와 시각적 인상이 일치하는가, 아니면 지표는 괜찮은데 그림으로 보면 이상한 부분이 있는가?\n"
                "간결하게 불릿으로 답하세요."
            ),
        }
    ]
    for label, path in shots:
        content.append({"type": "text", "text": f"--- {label} ---"})
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": base64.b64encode(path.read_bytes()).decode(),
            },
        })

    resp = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": content}],
    )
    return resp.content[0].text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", default="map_viewer.html")
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--skip-llm", action="store_true", help="스크린샷만 찍고 LLM 호출은 건너뛴다")
    args = ap.parse_args()

    out_dir = Path("review_shots")
    shots = capture_screenshots(args.html, out_dir)
    print(f"스크린샷 {len(shots)}장 저장: {out_dir}/")

    metrics = build_metrics_summary(args.html)
    print("\n[정량 지표]")
    print(metrics)

    if args.skip_llm:
        return

    print("\n[LLM 검증 리포트]")
    report = call_llm_review(shots, metrics, args.model)
    print(report)


if __name__ == "__main__":
    main()
```

API 키 없이 스크린샷 캡처까지 돌려보고, 그 이미지를 직접 검토한 결과 실제로 문제 세 가지를 찾았습니다.

1. **버그**: 밝은 테마에서 원본 경계선(회색)이 배경과 대비가 약해 거의 안 보였습니다.
2. **버그**: 확대(zoom)하면 선/마커가 월드 좌표 단위 고정 크기라 화면 비율을 무시하고 굵어졌습니다 — 신호등 4개가 거대한 원으로 뭉개져서 검증이 불가능한 상태였습니다. `vector-effect: non-scaling-stroke`와, 신호등 마커 반경을 현재 줌 배율에 맞춰 재계산하는 로직으로 고쳤습니다.
3. **버그 아님**: 전체 뷰가 듬성듬성 비어 보이는 건, `mapping_example.osm`이 하나의 연속된 동네가 아니라 **여러 예제 상황을 모아둔 합성 맵**이라 클러스터 사이에 실제 도로 연결이 없기 때문이었습니다(중심점 200m 이내엔 전체 포인트의 16%뿐). 정량 지표만으로는 알 수 없었던, 데이터셋 자체의 성격에 대한 판단이었습니다.

2번은 정량 지표(`fit_residual_max_m`)만 봐서는 절대 못 잡는 문제였습니다 — 잔차 자체는 정상인데 순전히 렌더링 문제였기 때문입니다. 이게 5단계에서 LLM을 검증에 넣기로 한 이유 그 자체입니다.

---

## 16단계: A+B+Signal 파이프라인 통합, `applicable_lane_ids` 최종 매핑

지금까지는 A(그룹핑), B(참조선 피팅), Signal(정지선 위치)을 각각 따로 스파이크했습니다. 이번엔 셋을 하나로 이었습니다.

1. 13단계의 다중 participant `RoutingGraph` 그룹핑으로 클러스터(LaneSection 후보)와 Road(클러스터 체인)를 만듭니다.
2. 각 Road에 대해, 체인에 속한 클러스터마다 대표 lanelet(첫 멤버)의 중심선을 순서대로 이어붙여 **Road 전체 중심선**을 만들고, 여기에 B단계의 `fit_reference_line`을 돌립니다 — 지금까지는 lanelet 하나 단위로만 피팅했는데, 여러 lanelet이 이어진 Road 단위로는 이번에 처음 확장했습니다.
3. 각 클러스터 안에서 멤버 lanelet들을 Road 참조선 기준 좌우 위치(`lateral_offset`)로 정렬해, OpenDRIVE 관례(음수=우측, 양수=좌측)에 맞는 `lane_id`를 부여합니다.
4. `lanelet_id -> (road_id, lane_id)` 매핑을 만들고, Signal의 `applicable_lane_ids`를 원본 lanelet id에서 이 최종 Lane id로 바꿉니다. `Signal.s`도 개별 lanelet이 아니라 Road 전체 중심선 기준으로 다시 계산합니다.

같은 샘플 맵에 돌린 결과:

```
클러스터 252개, Road 121개
Road 참조선 피팅 fit_residual_max_m: mean=0.0224 p95=0.0633 max=0.0985
lanelet -> Lane 매핑 371개 완료
```

Road 단위로 확장해도 잔차 수준(mean 2.24cm, p95 6.33cm)은 lanelet 단위로 피팅했을 때(7·14단계)와 비슷하게 유지됐습니다 — 여러 lanelet을 이어붙여도 Line+Arc 조합의 정확도가 무너지지 않는다는 뜻입니다.

Signal 재매핑 결과는 흥미로웠습니다.

```
re=45218 lanelet=45134 -> road_30.lane[+1]  s=10.54m (교차)
re=45218 lanelet=45136 -> road_30.lane[-1]  s=10.54m (교차)
re=45222 lanelet=44972 -> road_55.lane[+1]  s=36.82m (교차)
re=45224 lanelet=44968 -> road_55.lane[-2]  s=36.82m (교차)
re=45224 lanelet=44970 -> road_55.lane[-1]  s=36.82m (교차)
re=45226 lanelet=45014 -> road_24.lane[+3]  s=? (None)
re=45226 lanelet=45016 -> road_24.lane[+2]  s=? (None)
re=45232 lanelet=45070 -> road_41.lane[+3]  s=81.74m (교차)
re=45234 lanelet=45082 -> road_41.lane[+2]  s=81.74m (교차)
re=45234 lanelet=45088 -> road_41.lane[+1]  s=81.74m (교차)
```

14단계(lanelet 단위)에서는 8/10이 해결됐는데(6개 순수 교차 + 2개 끝점 폴백), 이번(Road 단위)에도 8/10이 해결됐지만 **내용이 달라졌습니다.** 이전에 실패했던 2건(44972, 45088)이 이번엔 순수 교차만으로 풀렸습니다 — Road 중심선이 여러 lanelet을 이어붙인 만큼 더 길어져서, 정지선이 원래는 인접 lanelet 쪽에 걸쳐 있던 경우까지 커버한 겁니다. 대신 이전엔 풀렸던 `re=45226`(정지선 하나, lanelet 45014·45016 둘 다)이 이번엔 둘 다 실패로 바뀌었습니다. 성공 건수는 같지만 실패하는 케이스 자체가 바뀐 게 이상해서, 원인을 더 파봤습니다(17단계).

```python
"""
A(그룹핑) + B(참조선 피팅) + Signal을 하나의 파이프라인으로 통합한다.

절차:
1. 13단계의 다중 participant RoutingGraph 그룹핑으로 클러스터(LaneSection 후보)와
   Road(클러스터 체인)를 만든다.
2. 각 Road에 대해, 체인에 속한 클러스터마다 대표 lanelet(첫 멤버)의 중심선을
   순서대로 이어붙여 Road 전체 중심선을 만들고, B단계 fit_reference_line으로
   참조선을 피팅한다 — 지금까지는 lanelet 하나 단위로만 피팅했는데, 이번에
   여러 lanelet이 이어진 Road 단위로 처음 확장한다.
3. 각 클러스터(LaneSection) 안에서 멤버 lanelet들을 참조선 기준 좌우 위치로
   정렬해 OpenDRIVE 관례(음수=우측, 양수=좌측)에 맞는 lane_id를 부여한다.
4. lanelet_id -> (road_id, lane_id) 매핑을 만들고, Signal의 applicable_lane_ids를
   원본 lanelet id에서 이 최종 Lane id로 바꾼다. Signal.s도 (개별 lanelet이 아니라)
   Road 전체 중심선 기준으로 다시 계산한다.
"""
from collections import defaultdict
import numpy as np
from scipy.optimize import least_squares
import lanelet2
from lanelet2.projection import UtmProjector
import xml.etree.ElementTree as ET

OSM_PATH = "/data/mapping_example.osm"


# ---- B: 참조선 피팅 — 부록 spike_fit.py와 동일한 함수들이므로 생략 ----
# (fit_line, fit_arc, simplify_polyline, fit_reference_line[잔차만 반환하는 축약판],
#  align_winding, resample_to_common_length)

def centerline_of(ll, coord_of):
    left = np.array([[p.x, p.y] for p in ll.leftBound])
    right = np.array([[p.x, p.y] for p in ll.rightBound])
    left_r, right_r = resample_to_common_length(left, right, n=30)
    return (left_r + right_r) / 2


# ---- Signal: segment_intersection / find_stopline_s는 14단계와 동일 (생략) ----

# ---- A: 그룹핑 — 13단계 코드와 동일 (UnionFind, build_graphs, union_side_neighbor,
#  build_side_clusters, union_following, build_cluster_graph, segment_into_roads) (생략) ----


# ---- 통합: Road 참조선 + Lane id 부여 + Signal 재매핑 ----

def lateral_offset(reference_centerline, point):
    """reference_centerline에서 point까지 최단거리와, 좌/우 부호를 계산한다."""
    dists = np.linalg.norm(reference_centerline - point, axis=1)
    i = int(np.argmin(dists))
    j = min(i + 1, len(reference_centerline) - 1)
    tangent = reference_centerline[j] - reference_centerline[max(i - 1, 0)]
    normal = np.array([-tangent[1], tangent[0]])
    normal = normal / (np.linalg.norm(normal) + 1e-9)
    to_point = point - reference_centerline[i]
    return float(np.dot(to_point, normal))  # +면 왼쪽, -면 오른쪽


def build_roads(lanelet_map, coord_of, clusters, roads_chain):
    """각 Road에 대해 참조선을 피팅하고, 클러스터별 Lane id를 부여한다."""
    ll_by_id = {ll.id: ll for ll in lanelet_map.laneletLayer}
    roads = []
    lanelet_to_lane = {}  # lanelet_id -> (road_id, lane_id)

    for road_idx, chain in enumerate(roads_chain):
        road_id = f"road_{road_idx}"
        # 클러스터 안 특정 lanelet 하나를 무작위로 대표로 삼으면(예: 멤버 리스트의 첫
        # 번째) 그 lanelet의 경로가 나머지 멤버와 미묘하게 달라 참조선이 실제 신호등
        # 위치에서 어긋나는 문제가 생긴다(17단계 참고). 대신 클러스터 내 모든 멤버
        # 중심선을 평균해 "차선 단면의 중앙"에 해당하는 대표 중심선을 만든다.
        pieces = []
        for cluster_idx in chain:
            member_centerlines = [centerline_of(ll_by_id[m], coord_of) for m in clusters[cluster_idx]]
            pieces.append(np.mean(member_centerlines, axis=0))
        road_centerline = np.concatenate(pieces, axis=0)

        stats = fit_reference_line(road_centerline, epsilon=0.15)

        for cluster_idx in chain:
            members = clusters[cluster_idx]
            offsets = []
            for m in members:
                cl = centerline_of(ll_by_id[m], coord_of)
                mid = cl[len(cl) // 2]
                offsets.append((m, lateral_offset(road_centerline, mid)))
            # 왼쪽(양수 offset)이 클수록 큰 양수 id, 오른쪽(음수)이 작을수록 큰 음수 id
            offsets.sort(key=lambda t: t[1])
            neg_id = -sum(1 for _, o in offsets if o < 0)
            for m, o in offsets:
                if o < 0:
                    lanelet_to_lane[m] = (road_id, neg_id)
                    neg_id += 1
            pos_id = 1
            for m, o in offsets:
                if o >= 0:
                    lanelet_to_lane[m] = (road_id, pos_id)
                    pos_id += 1

        roads.append({
            "road_id": road_id,
            "centerline": road_centerline,
            "fit_residual_max_m": stats["fit_residual_max_m"],
            "fit_residual_rms_m": stats["fit_residual_rms_m"],
            "lanelet_count": sum(len(clusters[c]) for c in chain),
        })

    return roads, lanelet_to_lane


# load_regulatory_elements: 14단계와 동일한 파싱의 축약판(ref_line,
# applicable_lanelet_ids만 수집) — 생략


def main():
    origin = lanelet2.io.Origin(49.0, 8.4)
    projector = UtmProjector(origin)
    lanelet_map = lanelet2.io.load(OSM_PATH, projector)

    coord_of = {}
    for pt in lanelet_map.pointLayer:
        coord_of[pt.id] = np.array([pt.x, pt.y])

    graphs = build_graphs(lanelet_map)
    clusters = build_side_clusters(lanelet_map, graphs)
    successors, predecessors = build_cluster_graph(lanelet_map, graphs, clusters)
    roads_chain = segment_into_roads(clusters, successors, predecessors)

    print(f"클러스터 {len(clusters)}개, Road {len(roads_chain)}개")

    roads, lanelet_to_lane = build_roads(lanelet_map, coord_of, clusters, roads_chain)

    residuals = [r["fit_residual_max_m"] for r in roads if r["lanelet_count"] > 0]
    print(f"Road 참조선 피팅 fit_residual_max_m: mean={np.mean(residuals):.4f} "
          f"p95={np.percentile(residuals, 95):.4f} max={np.max(residuals):.4f}")

    print(f"lanelet -> Lane 매핑 {len(lanelet_to_lane)}개 완료")

    # Signal 재계산: applicable_lane_ids를 최종 Lane id로 치환
    reg_elements = load_regulatory_elements(OSM_PATH)
    ways = {}
    tree = ET.parse(OSM_PATH)
    for w in tree.getroot().findall("way"):
        ways[w.get("id")] = [nd.get("ref") for nd in w.findall("nd")]

    road_by_id = {r["road_id"]: r for r in roads}

    print("\n=== Signal 재매핑 (원본 lanelet id -> 최종 Lane id) ===")
    for re in reg_elements:
        if re["subtype"] != "traffic_light" or re["ref_line"] not in ways:
            continue
        ref_line_pts = np.array([coord_of[int(n)] for n in ways[re["ref_line"]]])
        for ll_id_str in re["applicable_lanelet_ids"]:
            ll_id = int(ll_id_str)
            if ll_id not in lanelet_to_lane:
                print(f"  re={re['id']} lanelet={ll_id}: Lane 매핑 없음(그룹핑에서 누락)")
                continue
            road_id, lane_id = lanelet_to_lane[ll_id]
            road = road_by_id[road_id]
            s, method = find_stopline_s(road["centerline"], ref_line_pts)
            s_str = f"s={s:.2f}m" if s is not None else "s=?"
            print(f"  re={re['id']} lanelet={ll_id} -> {road_id}.lane[{lane_id:+d}]  {s_str} ({method})")


if __name__ == "__main__":
    main()
```

실행은 Docker 컨테이너 안에서 했습니다.

```bash
docker run --rm --platform linux/amd64 \
  -v /path/to/mapping_example.osm:/data/mapping_example.osm:ro \
  -v /path/to/spike_pipeline.py:/app/spike_pipeline.py:ro \
  python:3.11-slim bash -c "pip install --quiet lanelet2 scipy && python3 /app/spike_pipeline.py"
```

---

## 17단계: `road_24` Signal 실패 원인 — 대표 lanelet 선택 버그

`road_24`(re=45226이 참조하는 lanelet 45014, 45016이 속한 Road)를 직접 열어봤습니다.

```
road_24 체인: [53, 54]
  cluster 53: lanelets=[45192, 45014, 45016]
  cluster 54: lanelets=[45190, 45018, 45020]
road_24 중심선 길이: 60점, 전체 길이=7.34m
정지선(45226) 중점 <-> road_24 중심선 각 점 최단거리: 4.98m
```

원인을 찾았습니다. `build_roads`에서 Road 전체 중심선을 만들 때 각 클러스터의 대표 lanelet으로 `clusters[cluster_idx][0]`(멤버 리스트의 첫 번째)를 그냥 골랐는데, 이 순서는 union-find 순회 순서일 뿐 아무 의미가 없습니다. 클러스터 53의 멤버 `[45192, 45014, 45016]` 중 대표로 뽑힌 건 **신호등과 무관한 45192**였고, 이 lanelet의 경로가 45014·45016과 미묘하게 달라서 Road 중심선이 실제 정지선에서 4.98~5.69m나 떨어지게 됐습니다 — 2.0m 폴백 허용치를 넘어 매칭이 실패한 겁니다.

14단계(lanelet 단위)에서는 45014·45016 각각의 중심선을 직접 썼으니 문제가 없었는데, "클러스터당 대표 lanelet 하나만 쓴다"는 단순화가 이 케이스에서 어긋난 것이 원인이었습니다.

**수정**: 대표를 무작위로 고르는 대신, 클러스터 내 모든 멤버의 중심선을 평균해 "차선 단면의 중앙"에 해당하는 대표 중심선을 쓰도록 바꿨습니다(위 16단계 코드의 `build_roads`에 이미 반영). 재실행 결과:

```
re=45218 lanelet=45134 -> road_30.lane[+1]  s=7.68m (교차)
re=45218 lanelet=45136 -> road_30.lane[-1]  s=7.68m (교차)
re=45222 lanelet=44972 -> road_55.lane[+1]  s=30.67m (폴백(거리0.0m))
re=45224 lanelet=44968 -> road_55.lane[-2]  s=30.67m (폴백(거리0.0m))
re=45224 lanelet=44970 -> road_55.lane[-1]  s=30.67m (폴백(거리0.0m))
re=45226 lanelet=45014 -> road_24.lane[+2]  s=3.02m (교차)
re=45226 lanelet=45016 -> road_24.lane[+1]  s=3.02m (교차)
re=45232 lanelet=45070 -> road_41.lane[+2]  s=80.38m (교차)
re=45234 lanelet=45082 -> road_41.lane[+1]  s=80.38m (교차)
re=45234 lanelet=45088 -> road_41.lane[-1]  s=80.38m (교차)
```

**10/10 전부 해결됐습니다.** `road_55`는 교차 대신 폴백으로 바뀌었지만 거리 0.0m로 사실상 정확한 매칭이고, `road_24`는 순수 교차로 풀렸습니다. 참조선 피팅 잔차도 mean=2.27cm(수정 전 2.24cm)로 거의 그대로 유지됐습니다 — 대표 중심선을 평균으로 바꿔도 정확도가 떨어지지 않았습니다.

이 사례는 "정량 지표(잔차)가 괜찮아 보여도 파이프라인 설계상의 단순화가 특정 케이스에서 조용히 틀릴 수 있다"는 걸 보여줍니다 — `clusters[cluster_idx][0]`이라는 한 줄이, 신호등과 무관한 lanelet을 대표로 골라버리는 구체적인 실패로 이어졌습니다. 이런 종류의 버그는 전체 통계만 봐서는 안 보이고, 실패하는 개별 케이스를 하나씩 열어봐야 잡힙니다.

한 가지 더 짚어둘 것: 지금의 `Signal.s`는 이어붙인 원시 중심선(폴리라인) 위의 호길이입니다. 최종 OpenDRIVE의 s-좌표는 **피팅된 참조선** 기준이라 둘은 미세하게 다릅니다 — 잔차가 cm 수준이니 차이도 그 수준이겠지만, 정지선 위치는 회귀 테스트의 정지 거동 판정에 직접 들어가는 값이라 익스포트 시점에는 피팅 곡선 위에서 재계산해야 합니다.

---

## 18단계: 이음새 불연속 실측, 그리고 전역 G1 피팅

4단계에서 지표만 정의해두고 측정하지 않았던 이음새 불연속을 실측했습니다. 기존 독립 피팅(구간별로 line/arc를 따로 피팅)의 세그먼트 끝점·헤딩을 명시적으로 계산하도록 `fit_line`/`fit_arc`를 확장하고, 인접 세그먼트 간 지표를 쟀습니다. (이번 스캔부터는 `subtype: road`이면서 길이 1m 이상인 101개 lanelet 기준이라, 7·14단계와 표본이 조금 다릅니다. lanelet 단위 작업이라 `RoutingGraph`가 필요 없어서 Docker 없이 macOS에서 numpy/scipy만으로 돌렸습니다.)

| 지표 (이음새 147개) | mean | p50 | p95 | max |
|---|---|---|---|---|
| `joint_gap_m` | 1.6cm | 1.0cm | 3.9cm | 43.5cm |
| `joint_heading_jump` | 8.8° | 6.9° | 23.9° | 43.0° |
| `curvature_step` [1/m] | 0.024 | 0.012 | 0.085 | 0.170 |

우려가 사실로 확인됐습니다. 위치 갭은 대부분 cm 수준이지만, **헤딩 꺾임이 평균 8.8°, 최대 43°**입니다. `fit_residual` 2~3cm라는 숫자가 무색하게, 이 참조선을 그대로 직렬화하면 이음새마다 도로가 눈에 띄게 꺾입니다. "Line+Arc로 충분하다"던 7단계의 결론은 이음새를 재는 순간 절반만 맞는 얘기였습니다.

그래서 G1 연속(위치+헤딩 공유) 피팅을 두 가지 방식으로 시도했습니다.

**시도 1 — 탐욕(greedy) 체인: 실패.** 첫 구간은 자유 피팅하고, 이후 구간은 이전 끝점·끝헤딩에서 시작하도록 제약(직선은 남는 자유도 0, 원호는 곡률 하나)해 순서대로 피팅했습니다. 이음새는 정확히 0이 됐지만 잔차가 폭발했습니다 — mean 2.6cm → 22.4cm, 최악 1.38m. 원인은 명확합니다: 앞 구간의 헤딩 오차가 뒤로 그대로 전파되는데, 뒤 구간에는 그걸 만회할 자유도가 없습니다.

**시도 2 — 전역 최적화: 성공.** 발상을 바꿔, 참조선 체인 전체를 OpenDRIVE 네이티브 파라미터화 — 시작 pose (x₀, y₀, h₀) + 세그먼트별 (κᵢ, Lᵢ) — 로 놓고, 원본 점들과 체인 곡선 사이 거리를 한 번에 최소화했습니다. 이 표현에서는 G0/G1 연속이 "제약 조건"이 아니라 **표현 자체의 성질**이라 이음새가 항상 정확히 0이고, xodr 직렬화도 직역이 됩니다(21단계). |κ| < 1e-4인 세그먼트를 익스포트 때 line으로 취급하면 되므로 line/arc 구분이 파라미터에서 아예 사라지는 부수 효과도 있습니다.

| `fit_residual_max_m` | mean | p50 | p95 | max |
|---|---|---|---|---|
| 독립 피팅 (불연속) | 2.61cm | 2.24cm | 5.64cm | 14.58cm |
| greedy G1 | 22.45cm | 13.68cm | 93.54cm | 137.99cm |
| **전역 G1** | **5.58cm** | **4.57cm** | **13.57cm** | **21.18cm** |

전역 G1은 완전한 연속성을 평균 +3cm의 잔차 비용으로 삽니다. 세그먼트 분할을 더 잘게(ε=0.15 → 0.05, 평균 세그먼트 2.4 → 3.4개) 해봐도 5.6 → 4.5cm로 개선이 미미했는데, 이는 잔차 바닥이 분할 개수가 아니라 **"조각별 상수 곡률" 모델 자체의 한계**라는 뜻입니다 — 실제 도로에는 곡률이 연속적으로 변하는(클로소이드적인) 구간이 많기 때문입니다. 남은 곡률 계단(G2 불연속)도 mean 0.081, max 0.449 [1/m]로 실측됐습니다. 이 계단이 조향 시뮬레이션에서 문제가 되는 수준인지가 클로소이드 세그먼트 도입 여부를 정하는 기준이 될 겁니다.

```python
def chain_sample(params, n_segs, ds=0.25):
    """params = [x0, y0, h0, κ_1..K, L_1..K] 체인을 ds 간격으로 샘플링한다."""
    x, y, h = params[0], params[1], params[2]
    kappas = params[3:3 + n_segs]
    lengths = params[3 + n_segs:]
    pts = [np.array([x, y])]
    for k, L in zip(kappas, lengths):
        n = max(int(np.ceil(L / ds)), 2)
        s = np.linspace(0, L, n + 1)[1:]
        if abs(k) < 1e-9:
            xs, ys = x + s * np.cos(h), y + s * np.sin(h)
        else:
            xs = x + (np.sin(h + k * s) - np.sin(h)) / k
            ys = y - (np.cos(h + k * s) - np.cos(h)) / k
            h = h + k * L
        x, y = xs[-1], ys[-1]
        pts.append(np.stack([xs, ys], axis=1))
    return np.concatenate([pts[0][None, :]] + pts[1:], axis=0)


def point_to_polyline_dist(points, poly):
    """각 point에서 poly(폴리라인)까지의 최단거리 (선분 단위 정확 계산)."""
    a, b = poly[:-1], poly[1:]
    ab = b - a
    ab_len2 = np.sum(ab ** 2, axis=1) + 1e-12
    ap = points[:, None, :] - a[None, :, :]
    t = np.clip(np.sum(ap * ab[None, :, :], axis=2) / ab_len2[None, :], 0.0, 1.0)
    proj = a[None, :, :] + t[..., None] * ab[None, :, :]
    return np.linalg.norm(points[:, None, :] - proj, axis=2).min(axis=1)


def fit_reference_line_global(centerline: np.ndarray, epsilon: float = 0.15):
    """독립 피팅으로 초기값을 만들고, 체인 전체를 전역 최적화한다."""
    segs, _ = fit_reference_line_independent(centerline, epsilon)
    if not segs:
        return None, 0, None

    x0 = np.concatenate([
        segs[0]["start_pt"], [segs[0]["h_start"]],
        [s["curvature"] for s in segs],
        [max(s["length"], 0.2) for s in segs],
    ])
    n_segs = len(segs)
    total_len = sum(s["length"] for s in segs)

    def residual(params):
        poly = chain_sample(params, n_segs)
        d = point_to_polyline_dist(centerline, poly)
        # 끝점 앵커: 체인이 원본보다 심하게 짧거나 길게 미끄러지는 것을 막는다
        end_anchor = np.linalg.norm(poly[-1] - centerline[-1])
        start_anchor = np.linalg.norm(poly[0] - centerline[0])
        return np.concatenate([d, [end_anchor, start_anchor]])

    lo = np.concatenate([x0[:2] - 5.0, [x0[2] - 0.5],
                         np.full(n_segs, -2.0), np.full(n_segs, 0.05)])
    hi = np.concatenate([x0[:2] + 5.0, [x0[2] + 0.5],
                         np.full(n_segs, 2.0), np.full(n_segs, max(total_len * 2.0, 1.0))])
    sol = least_squares(residual, np.clip(x0, lo, hi), bounds=(lo, hi))

    poly = chain_sample(sol.x, n_segs, ds=0.1)
    d = point_to_polyline_dist(centerline, poly)
    kappas = sol.x[3:3 + n_segs]
    steps = np.abs(np.diff(kappas))
    return sol.x, n_segs, {
        "fit_residual_max_m": float(d.max()),
        "fit_residual_rms_m": float(np.sqrt(np.mean(d ** 2))),
        "curvature_step_max": float(steps.max()) if len(steps) else 0.0,
        "n_segs": n_segs,
    }
```

---

## 19단계: 곡률 오차 첫 실측

4단계에서 "위치 오차보다 위험하다"고 규정만 해놓고 한 번도 계산하지 않았던 `curvature_error`를 전역 G1 피팅 결과에 대해 처음 측정했습니다. 기준(참값 근사)은 원본 중심선의 이산 곡률인데, **측정 방법이 결과를 지배한다**는 것부터 확인됐습니다.

| `curvature_error_max` [1/m] | mean | p50 | p95 | max |
|---|---|---|---|---|
| 기준: 스무딩 없는 이산 곡률 | 0.291 | 0.180 | 1.004 | 2.120 |
| 기준: 5점 이동평균 후 이산 곡률 | 0.075 | 0.044 | 0.230 | 0.350 |

스무딩 전후 이산 곡률 차이(즉 측정 자체의 노이즈)의 lanelet별 최대가 mean 0.254 [1/m]로, 스무딩 없는 기준에서 잰 "오차" 0.291과 같은 자릿수입니다. 즉 **스무딩 없이 재면 곡률 오차의 대부분은 피팅 오차가 아니라 이산 곡률 추정 자체의 노이즈**입니다. 7단계 주의사항 3번이 예고한 그대로였고, `curvature_error`를 프로버넌스에 넣을 때는 기준 정의(스무딩 창, 샘플 밀도)를 지표 이름에 같이 박아야 다른 맵과 비교가 가능합니다. 스무딩 기준으로 남는 오차(mean 0.075, 전 구간 평균으로는 0.028)는 대부분 곡률 계단(18단계) 근처 구간에서 나옵니다.

```python
def smooth_points(points: np.ndarray, window: int = 5) -> np.ndarray:
    """이동평균 스무딩(끝점 유지). 이산 곡률의 노이즈를 억제한다."""
    if len(points) < window:
        return points
    kernel = np.ones(window) / window
    sm = points.copy()
    for d in range(2):
        sm[:, d] = np.convolve(points[:, d], kernel, mode="same")
    half = window // 2
    sm[:half], sm[-half:] = points[:half], points[-half:]
    return sm

# 측정 루프의 핵심: 각 원본 점에서 가장 가까운 체인 샘플의 세그먼트 κ를 찾아 비교
k_disc = discrete_curvature(smooth_points(centerline))[2:-2]   # 끝점 유한차분 제외
k_fit = np.abs(fitted_kappa_at_points(params, n_segs, centerline[2:-2]))
curvature_error = np.abs(k_fit - k_disc)
```

---

## 20단계: 중심선 pairing 편향 실측 — 범인은 곡률보다 경계 길이 불일치

7단계 주의사항 2번(호길이 비율 재샘플링 + 포인트별 평균 방식의 편향)을 실측했습니다. 평균 방식 중심선을 초기값으로, 각 점에서 로컬 접선의 법선을 세워 좌/우 경계 폴리라인과의 교점을 구하고 그 중점으로 갱신하는 **법선 투영 중심선**을 만들어, 두 중심선의 차이를 쟀습니다.

| pairing 편향 (lanelet별 max) | mean | p50 | p95 | max |
|---|---|---|---|---|
| `bias_max_m` | 15.8cm | 4.5cm | 63.2cm | **146.9cm** |

예상보다 훨씬 컸고, 원인 분석에서 반전이 있었습니다. 가설대로 급커브(r<10m)에서 편향이 커지긴 했지만(mean 27.8cm vs 완만한 구간 8.3cm), **최악 케이스(1.47m)는 최대 곡률 0.006 1/m(r≈157m)짜리 거의 직선 구간**이었습니다. 더 파보니 지배 요인은 곡률이 아니라 **좌우 경계의 길이 불일치**였습니다.

| 구분 | 개수 | bias_max mean | max |
|---|---|---|---|
| 경계 길이비 > 1.2 | 44 | 30.2cm | 146.9cm |
| 경계 길이비 ≤ 1.2 | 57 | 4.8cm | 33.8cm |

로그 길이비와 편향의 상관계수는 0.711, 최악 lanelet은 왼쪽 경계 24.4m / 오른쪽 경계 126.6m짜리 쐐기형(교차로 모서리)이었습니다. 호길이 '비율'로 두 경계의 점을 짝짓는 방식은 **두 경계의 길이가 비슷할 때만 성립하는 암묵적 가정**이었던 겁니다.

이 발견의 무게는 따로 짚어야 합니다: **지금까지의 모든 피팅 잔차는 이 편향된 중심선을 '정답'으로 놓고 잰 값**입니다. 잔차 5cm짜리 피팅이 실제 도로 중심에서는 1m 넘게 벗어나 있을 수 있다는 뜻이고, 3DGS 씬 정합이라는 최종 목적에는 잔차보다 이 편향이 더 큰 위협입니다. 중심선 계산을 법선 투영 방식(또는 lanelet2 공식 `centerline()`)으로 교체하고 지금까지의 수치를 전부 재실측하는 것이, 이 스파이크 이후의 새로운 최우선 작업이 됐습니다.

```python
def ray_polyline_intersection(origin, direction, poly):
    """origin에서 ±direction 직선과 poly의 교점 중 origin에 가장 가까운 것."""
    best, best_d = None, np.inf
    for a, b in zip(poly[:-1], poly[1:]):
        ab = b - a
        denom = direction[0] * ab[1] - direction[1] * ab[0]
        if abs(denom) < 1e-12:
            continue
        diff = a - origin
        t = (diff[0] * ab[1] - diff[1] * ab[0]) / denom               # 직선 파라미터(양방향)
        u = (diff[0] * direction[1] - diff[1] * direction[0]) / denom  # 선분 파라미터
        if 0.0 <= u <= 1.0 and abs(t) < best_d:
            best, best_d = a + u * ab, abs(t)
    return best


def normal_projection_centerline(centerline, left, right, n_iter=2):
    """중심선 각 점에서 법선을 세워 좌/우 경계와의 교점 중점으로 갱신한다."""
    cl = centerline.copy()
    for _ in range(n_iter):
        new = cl.copy()
        for i in range(len(cl)):
            j0, j1 = max(i - 1, 0), min(i + 1, len(cl) - 1)
            tangent = cl[j1] - cl[j0]
            norm = np.linalg.norm(tangent)
            if norm < 1e-9:
                continue
            normal = np.array([-tangent[1], tangent[0]]) / norm
            pl = ray_polyline_intersection(cl[i], normal, left)
            pr = ray_polyline_intersection(cl[i], normal, right)
            if pl is not None and pr is not None:
                new[i] = (pl + pr) / 2
        cl = new
    return cl
```

---

## 21단계: `.xodr` 익스포트와 opendrive2lanelet 라운드트립

마지막으로, 아직 한 번도 만들어보지 않았던 실제 OpenDRIVE 파일을 만들어 서드파티 도구에 태웠습니다. 전역 G1 피팅 결과는 OpenDRIVE `planView`와 표현이 1:1이라 직렬화가 직역입니다 — (x₀, y₀, h₀)가 첫 `<geometry>`의 속성이 되고, 세그먼트별 (κ, L)이 `<arc>`/`<line>`(|κ| < 1e-4)이 됩니다. lanelet 하나를 Road 하나로(참조선=중심선, 좌우 각각 폭 w(s)/2 차선, `junction="-1"`) 내보내 101개 Road짜리 xodr을 만들었습니다.

이 파일을 1단계에서 조사했던 TUM opendrive2lanelet(성숙한 반대 방향 변환기)에 넣어 lanelet으로 되돌리고, 돌아온 참조선(lane -1의 왼쪽 경계)을 **원본 Lanelet2 중심선**과 비교했습니다.

```
xodr 파싱: Road 101개 -> 변환된 lanelet 202개 (전부 매칭, 미매칭 0)

end-to-end 오차 (원본 중심선 <-> 라운드트립 참조선)
  road별 max:  mean=5.72cm p50=4.62cm p95=14.15cm max=21.53cm
  road별 mean: mean=1.82cm p95=4.24cm
```

18단계의 전역 G1 피팅 잔차(mean 5.58cm, max 21.18cm)와 사실상 같습니다 — **직렬화 + 서드파티 파싱이 더하는 오차는 mm 수준이고, 오차 예산 전체가 피팅에서 나온다**는 것이 확인됐습니다. "우리가 만든 xodr을 성숙한 외부 도구가 정상적으로 읽고, 기하가 보존된다"까지가 이번 스파이크의 결론입니다. 전 구간이 결정적 코드로만 이루어진 검증 회로라, LLM 시각 검증(15단계)과 정확히 상호 보완됩니다.

한계도 명확합니다. (1) lanelet 단위 Road라 Junction이 없습니다 — 교차로 모델링은 여전히 미착수. (2) esmini/CARLA 실기 로딩은 아직 안 돌렸습니다(opendrive2lanelet 파싱 통과로 문법·기하 유효성은 상당 부분 확인됐지만, 시뮬레이터가 실제로 받아들이는지는 별개). (3) 라운드트립 환경은 버전 조합이 까다로웠습니다 — macOS venv에 python 3.9 + `numpy<2` + `opendrive2lanelet==1.2.1` + `commonroad-io==2020.2`로 고정해야 돌아갑니다.

```python
# 익스포터 핵심: 전역 G1 파라미터 -> <planView> 직역
def road_xml(road_id, params, n_segs, width_coeffs):
    x, y, h = params[0], params[1], params[2]
    kappas = params[3:3 + n_segs]
    lengths = params[3 + n_segs:3 + 2 * n_segs]
    geoms, s = [], 0.0
    for k, L in zip(kappas, lengths):
        body = "<line/>" if abs(k) < 1e-4 else f'<arc curvature="{k:.10f}"/>'
        geoms.append(f'<geometry s="{s:.6f}" x="{x:.6f}" y="{y:.6f}" '
                     f'hdg="{h:.10f}" length="{L:.6f}">{body}</geometry>')
        if abs(k) < 1e-4:
            x, y = x + L * np.cos(h), y + L * np.sin(h)
        else:
            x = x + (np.sin(h + k * L) - np.sin(h)) / k
            y = y - (np.cos(h + k * L) - np.cos(h)) / k
            h = h + k * L
        s += L
    # ... <lanes>: 좌/우 각각 <width a b c d> = w(s)/2 3차 다항식 (본문 생략)


# 라운드트립 비교 핵심 (rt_venv에서 실행)
from opendrive2lanelet.opendriveparser.parser import parse_opendrive
from opendrive2lanelet.network import Network

odr = parse_opendrive(etree.parse("roundtrip_map.xodr").getroot())
net = Network()
net.load_opendrive(odr)
lanelets = net.export_commonroad_scenario().lanelet_network.lanelets

for key, centerline in originals.items():           # 원본 Lanelet2 중심선들
    # 원본 중심선과 가장 가까운 left boundary(=lane -1의 왼쪽 = 참조선)를 찾아 거리 측정
    d = min(point_to_polyline_dist(centerline, np.asarray(l.left_vertices)).mean()
            for l in candidate_lanelets)
```

---

## 22단계: 두 번째 실측 맵 — 고도 피팅과 결론 재현성 검증

여기까지는 전부 Lanelet2 공식 예제 맵(`mapping_example.osm`, 독일 Karlsruhe) 하나로만 검증했습니다. 이번엔 실제 `ele`(고도) 태그가 들어있는 다른 맵 — Autoware 플래닝 시뮬레이터 샘플맵으로 보이는 `lanelet2_map.osm`(노드 4,499개 전부 ele 보유, 고도 18.7~25.2m, subtype=road lanelet 183개) — 을 손에 넣어 두 가지를 확인했습니다: (1) 그동안 미뤄뒀던 고도 피팅을 처음 실측하는 것, (2) 지금까지의 결론이 **다른 맵에서도** 재현되는지 보는 것.

### 22-1. `elevation_profile` 첫 피팅

3단계 IR 설계 그대로 z(s)를 3차 다항식(`a + b·ds + c·ds² + d·ds³`)으로 최소자승 피팅했습니다. 중심선은 좌우 경계의 ele를 각각 호길이 보간한 뒤 평균했고, s는 참조선과 같은 관례(구간 로컬 좌표 ds = s - s_start)를 씁니다.

| 지표 | mean | p50 | p95 | max |
|---|---|---|---|---|
| `z_fit_residual_max_m` | 1.01cm | 0.76cm | 2.79cm | 7.69cm |
| `z_fit_residual_rms_m` | 0.46cm | - | 1.44cm | - |
| lanelet 평균 경사 \|Δz/Δs\| | 0.36% | 0.33% | 0.87% | 1.33% |

잔차가 xy 참조선 피팅보다도 작습니다 — 도로 경사가 완만(대부분 1% 이내)해서 3차 다항식 하나로 lanelet 전체를 무리 없이 덮습니다. 급경사·과속방지턱처럼 짧은 구간에 곡률이 몰리는 지형이 아니라면, "elevation_profile은 참조선처럼 구간을 여러 번 쪼갤 필요 없이 lanelet당 다항식 하나로 충분하다"는 잠정 결론을 내릴 수 있습니다. 다만 이 결론은 인접 lanelet 간 **경사 이음새**(18단계에서 xy에 대해 쟀던 것과 같은 종류의 불연속)를 재지 않은 상태입니다 — 그러려면 A(그룹핑)로 Road 체인을 먼저 만들어야 하는데, `RoutingGraph`가 필요해 이번 스파이크 범위 밖으로 남겨뒀습니다.

```python
def fit_elevation_cubic(s, z):
    """z(s) = a + b*ds + c*ds^2 + d*ds^3, ds = s - s[0] (참조선 로컬 좌표계와 동일 관례)."""
    ds = s - s[0]
    deg = 3 if len(ds) >= 4 else 1
    coeffs = np.polyfit(ds, z, deg)
    res = z - np.polyval(coeffs, ds)
    return coeffs[::-1], float(np.max(np.abs(res))), float(np.sqrt(np.mean(res ** 2)))
```

### 22-2. 기존 결론 재현성 — 절반은 재현, 절반은 갈라짐

같은 맵에 18·20단계의 xy 스파이크를 다시 돌렸습니다.

| 지표 | Karlsruhe(1차) | Autoware 샘플맵(2차) |
|---|---|---|
| 독립 피팅 `fit_residual_max_m` mean | 2.61cm | **1.06cm** |
| 이음새 `heading_jump` mean / max | 8.8° / 43° | 2.2° / 44° |
| 전역 G1 전환 비용(잔차 증가분 mean) | +3.0cm | **+0.19cm** |
| pairing 편향 `bias_max` mean / max | 15.8cm / 147cm | **2.0cm / 32cm** |

**"Line+Arc로 충분하다", "전역 G1 연속성이 싸게 먹힌다"는 결론은 재현됐고, 오히려 이 맵에서 더 강하게 성립합니다** — 도면이 훨씬 깔끔해서(합성/정밀 제작된 Autoware 데모맵으로 보이며, LiDAR 실측 노이즈가 있는 Karlsruhe 맵과 성격이 다릅니다) 잔차도, 이음새 꺾임도, G1 전환 비용도 전반적으로 더 작습니다.

**그런데 pairing 편향의 "지배 요인"은 재현되지 않았습니다.** 20단계에서는 편향과 좌우 경계 길이비의 로그가 상관계수 0.71로 강하게 얽혀 있었는데, 이 맵에서는 그 상관이 0.37로 약해지고 대신 **곡률과의 상관이 0.52로 더 강합니다** — 최악 케이스(32cm)도 길이비 불일치가 아니라 반경 6.2m 급커브였습니다.

| 구분 | 개수 | bias_max mean |
|---|---|---|
| 경계 길이비 > 1.2 | 75 | 3.3cm |
| 경계 길이비 ≤ 1.2 | 88 | 0.9cm |

두 맵을 합쳐 읽으면: **pairing 편향 자체(호길이 비율 평균 방식의 한계)는 두 맵 모두에서 재현되는 일반적인 문제**지만, **어느 요인이 더 크게 기여하는지는 맵의 성격에 따라 달라집니다** — 실측 노이즈가 크고 교차로 모서리처럼 좌우 경계 길이가 크게 다른 맵(Karlsruhe)에서는 길이 불일치가, 곡률 자체가 급한 맵(Autoware 샘플)에서는 곡률이 지배합니다. "경계 길이 불일치가 지배 요인"이라고 20단계에서 내린 결론은 **한 맵에서만 성립하는 일반화 과잉**이었던 셈이라, 프로버넌스의 편향 원인 필드도 하나로 뭉뚱그리지 말고 두 요인을 모두 추적해야 합니다.

---

## 23단계: 중심선을 실제로 법선 투영으로 바꿔보니 — 편향은 잡고 잔차는 놓쳤다

'남은 빈틈' 1번을 실제로 실행했습니다. 20단계의 `normal_projection_centerline`(중심선 각 점에서 법선을 세워 좌/우 경계와의 교점 중점으로 갱신)을 두 맵의 파이프라인에 실제로 꽂고, 독립 피팅·전역 G1·곡률 오차를 다시 냈습니다. 결과는 기대와 달랐습니다 — 두 가지를 새로 배웠습니다.

### 23-1. 법선 투영 자체에 견고성 결함이 있었다

Autoware 샘플맵에 돌리자마자 **중심선이 14.6m 튀는 lanelet**이 나왔습니다(lanelet 95). 원인은 20단계에 구현한 `ray_polyline_intersection`에 거리 상한이 없었다는 것 — 좌우 경계 길이가 크게 다른(39.5m vs 31.7m) 쐐기형 lanelet의 끝점 근처에서, 법선이 가까운 경계가 아니라 폴리라인 반대편의 먼 지점과 교차해버렸습니다. 로컬 폭(그 지점 좌우 경계까지의 평균 거리)의 3배를 넘는 교점은 버리고, 실패하면 평균 방식으로 조용히 폴백하도록 고쳤습니다. 이 수정 하나로 이상치는 14.6m → 0.32m(20단계에서 잰 정상 범위)로 돌아왔습니다. 다만 폴백이 드문 일이 아니었습니다 — 전체 포인트의 6.9%(Autoware)~14.9%(Karlsruhe)가 법선 투영에 실패해 평균 방식으로 되돌아갔습니다.

```python
def normal_projection_centerline_bounded(centerline, left, right, n_iter=2, max_factor=3.0):
    """max_factor: 로컬 폭(현재 평균 중심선 기준 좌우 거리) 대비 허용 교점 거리 배수."""
    cl = centerline.copy()
    for _ in range(n_iter):
        new = cl.copy()
        for i in range(len(cl)):
            j0, j1 = max(i - 1, 0), min(i + 1, len(cl) - 1)
            tangent = cl[j1] - cl[j0]
            norm = np.linalg.norm(tangent)
            if norm < 1e-9:
                continue
            normal = np.array([-tangent[1], tangent[0]]) / norm
            local_half_width = (np.linalg.norm(left[i] - cl[i]) + np.linalg.norm(right[i] - cl[i])) / 2
            cap = max(local_half_width * max_factor, 0.5)

            pl = ray_polyline_intersection(cl[i], normal, left)
            pr = ray_polyline_intersection(cl[i], normal, right)
            ok_l = pl is not None and np.linalg.norm(pl - cl[i]) <= cap
            ok_r = pr is not None and np.linalg.norm(pr - cl[i]) <= cap
            if ok_l and ok_r:
                new[i] = (pl + pr) / 2
            # 실패하면 이번 반복에서 이 점은 건드리지 않는다 — 평균 방식 값 유지
        cl = new
    return cl
```

### 23-2. 버그를 고쳐도, 편향 제거가 잔차 개선으로 이어지지 않았다

이게 진짜 반전입니다. 거리 상한을 넣어 견고성 결함을 없앤 뒤에도, **법선 투영 중심선으로 다시 피팅한 잔차가 평균 중심선보다 나아지지 않고 오히려 나빠졌습니다** — 적어도 노이즈가 있는 맵에서는.

| 지표 | Karlsruhe (노이즈 있는 실측 맵) | Autoware 샘플맵 (깨끗한 맵) |
|---|---|---|
| 전역 G1 `fit_residual_max_m` — 평균 중심선 | 5.6cm | 1.2cm |
| 전역 G1 `fit_residual_max_m` — 법선투영(수정판) | **9.6cm** (+4.0cm) | 1.2cm (±0.0cm) |
| `curvature_error_max`(스무딩 기준) — 평균 중심선 | 7.5cm⁻¹→ 0.075 [1/m] | (19단계에서 미측정) |
| `curvature_error_max`(스무딩 기준) — 법선투영(수정판) | **0.219 [1/m]** (약 3배) | 0.057 [1/m] |

pairing 편향(20단계가 측정한 "평균 방식과 법선 투영의 차이") 자체는 정확히 없앴습니다 — 정의상 법선 투영이 새 기준이니 편향은 0이 됩니다. 하지만 **참조선 피팅이 맞추려는 목표가 부드러운 곡선이 아니라 점마다 독립적으로 계산된, 약간 들쭉날쭉한 점렬로 바뀌면서 오히려 피팅이 어려워졌습니다.** 30개 점을 하나씩 로컬 접선 기반으로 투영하다 보니 인접 점 사이에 작은 고주파 잡음이 생기고, 이게 line/arc 피팅과 곡률 추정 모두에 잡음으로 얹힙니다. 깨끗한 Autoware 맵에서는 이 잡음이 작아서 거의 중립이었지만, 이미 노이즈가 있는 Karlsruhe 실측 맵에서는 잡음 위에 잡음이 쌓여 잔차가 오히려 커졌습니다.

**결론: "평균 대신 법선 투영으로 중심선을 미리 계산해두고 그 위에 참조선을 피팅한다"는 2단계 파이프라인 자체가 틀린 접근이었습니다.** 편향은 없앴지만 그 대가로 노이즈를 얻었을 뿐, 최종 목표(참조선이 실제 도로 중심을 정확히 따라가는 것)에는 순수하게 더 가까워지지 않았습니다. 더 나은 방향은 중심선을 별도 단계로 만들지 않고, **참조선 피팅 자체를 좌/우 경계 폴리라인 둘 다에 대한 대칭 목적함수**(예: 원본 중심선이 아니라 좌/우 경계까지의 거리 합이 같아지도록 하는 항을 `point_to_polyline_dist` 잔차에 추가)로 바꾸는 것입니다 — 18단계의 전역 최적화 틀을 그대로 쓰되, 맞추는 대상만 "미리 만든 중심선"에서 "좌우 경계 자체"로 바꾸는 확장입니다.

---

## 24단계: 참조선을 좌우 경계에 직접 대칭 피팅 — 이번엔 통했다

23단계 끝에서 제안한 방향을 그대로 실행했습니다. 중심선이라는 중간 산출물을 아예 만들지 않고, 18단계의 전역 파라메트릭 곡선(시작 pose + 세그먼트별 κ·L)을 **좌/우 경계 폴리라인까지의 거리가 같아지도록** 직접 최적화합니다. 23단계의 실패 원인이 "30개 점을 하나씩 독립적으로 투영하면서 생긴 고주파 잡음"이었으니, 애초에 그런 점렬을 만드는 단계 자체를 없애면 매끄러움은 파라메트릭 표현이 공짜로 보장해줄 거라는 계산이었습니다.

초기값은 기존처럼 평균 중심선 + 전역 G1 피팅으로 잡고(국소 최적화라 좋은 시작점이 필요합니다), 목적함수만 `d_left(s) - d_right(s)`(곡선 위 각 점에서 좌/우 경계까지 거리 차이)로 바꿔 재최적화합니다. 초기해에서 너무 벗어나지 않도록 약한 정규화 항도 더했습니다.

한 가지 구현 함정이 있었습니다 — 기존 `chain_sample`은 세그먼트 길이 `L`에 비례해 샘플 개수를 정하는데(`L/ds`), 최적화 도중 `L`이 바뀌면 잔차 벡터 길이도 바뀌어서 `least_squares`가 `could not broadcast input array from shape (42,) into shape (43,)` 에러를 냅니다. 세그먼트당 샘플 개수를 고정하는 `chain_sample_fixed`로 바꿔서 해결했습니다.

측정 지표도 바꿨습니다. "평균 중심선 기준 잔차"는 이제 비교용으로만 남기고, 진짜 품질 지표는 **대칭 잔차**(`|d_left - d_right|`) — 이 곡선이 실제로 도로 중앙에 있는지를 직접 잽니다. 비교 기준선으로 "평균 중심선 자체의 대칭 잔차"(즉 기존 방식이 애초에 얼마나 비대칭이었는지)도 같이 냈습니다.

| 지표 | Karlsruhe (101개) | Autoware (163개) |
|---|---|---|
| 평균 중심선 자체의 대칭 잔차 — mean/max | 30cm / 132cm | 1.4cm / 6.9cm |
| **경계 대칭 피팅 후 대칭 잔차 — mean/p95/max** | **6.6cm / 14.5cm / 39.8cm** | **1.5cm / 3.6cm / 8.4cm** |

Karlsruhe에서 mean 30cm → 6.6cm로 확실히 줄었고, 무엇보다 최악 케이스가 132cm → 40cm로 3배 이상 좁혀졌습니다. 원래 깨끗했던 Autoware 맵에서도 mean 1.4cm → 1.5cm로 거의 그대로 — 퇴보 없이 유지됩니다. 23단계의 점별 투영이 노이즈를 더해 상황을 악화시켰던 것과 정반대로, 이번엔 노이즈 있는 맵일수록 개선 폭이 더 컸습니다.

전체 실행 중 두 개의 큰 이상치("평균 중심선 기준 잔차")가 나와서 각각 조사했습니다.

- **Karlsruhe 12.36m 이상치**: 확인해보니 **20단계에서 이미 "pairing 편향 최악 사례"로 지목했던 바로 그 lanelet**(id=9037740909199276460, 좌측 경계 24.4m / 우측 경계 126.6m로 5배 넘게 차이 나는 극단적 쐐기형)이었습니다. 새 피팅의 대칭 잔차는 0.40m로 정상 범위이고, 옛 평균 중심선(75m, 좌우 경계 길이의 단순 평균이라는 편향된 정의) 기준으로 크게 벗어난 건 **그 편향을 제대로 고쳤다는 증거**입니다.
- **Autoware 1.85m 이상치**: 좌우 경계 길이가 거의 같은데(39.7m/40.2m) 벌어졌습니다. 그런데 대칭 잔차는 1.9cm로 오히려 데이터셋 평균보다 좋습니다. 즉 이 케이스는 좌우 인덱스 매칭이 어긋나 옛 평균 중심선 쪽이 이상하게 휘어 있었던 경우로 보이고, 새 피팅이 진짜 대칭 곡선을 제대로 찾아낸 것입니다.

두 이상치 모두 "새 방법이 틀렸다"가 아니라 "옛 기준이 틀렸었다"는 걸 재확인해줬습니다. **20·22·23단계에 걸쳐 정의조차 흔들리던 "도로 중심선"이 이 단계에서 처음으로 명확한 기준(좌우 경계 등거리)과 그 기준을 만족하는 안정적인 수치로 확정됐습니다.**

```python
def chain_sample_fixed(params, n_segs, n_per_seg=15):
    """chain_sample과 동일하지만, 세그먼트당 샘플 개수를 길이(L)와 무관하게
    고정한다. least_squares는 반복마다 잔차 벡터 길이가 같아야 하는데,
    원래 chain_sample은 L/ds로 샘플 수를 정해서 최적화 도중 L이 바뀌면
    잔차 길이도 바뀌어 버린다."""
    x, y, h = params[0], params[1], params[2]
    kappas = params[3:3 + n_segs]
    lengths = params[3 + n_segs:]
    pts = [np.array([x, y])]
    for k, L in zip(kappas, lengths):
        s = np.linspace(0, L, n_per_seg + 1)[1:]
        if abs(k) < 1e-9:
            xs, ys = x + s * np.cos(h), y + s * np.sin(h)
        else:
            xs = x + (np.sin(h + k * s) - np.sin(h)) / k
            ys = y - (np.cos(h + k * s) - np.cos(h)) / k
            h = h + k * L
        x, y = xs[-1], ys[-1]
        pts.append(np.stack([xs, ys], axis=1))
    return np.concatenate([pts[0][None, :]] + pts[1:], axis=0)


def fit_reference_line_boundary_symmetric(left, right, epsilon=0.15, reg_weight=0.05):
    """좌/우 경계 폴리라인에 참조선을 직접 대칭 피팅한다.
    중심선이라는 중간 산출물을 만들지 않으므로, 23단계의 점별 투영이
    만들어낸 고주파 잡음이 애초에 생기지 않는다."""
    centerline = (left + right) / 2
    x0, n_segs, stats0 = fit_reference_line_global(centerline, epsilon=epsilon)  # 18단계, 초기값용
    if x0 is None:
        return None, None, None

    def residual(params):
        poly = chain_sample_fixed(params, n_segs)
        d_left = point_to_polyline_dist(poly, left)
        d_right = point_to_polyline_dist(poly, right)
        sym = d_left - d_right                       # 0이면 완전 대칭(도로 중심)
        reg = reg_weight * (params - x0)              # 초기해에서 너무 안 벗어나게
        return np.concatenate([sym, reg])

    total_len = float(np.sum(x0[3 + n_segs:3 + 2 * n_segs]))
    lo = np.concatenate([x0[:2] - 3.0, [x0[2] - 0.3],
                         np.full(n_segs, -2.0), np.full(n_segs, 0.05)])
    hi = np.concatenate([x0[:2] + 3.0, [x0[2] + 0.3],
                         np.full(n_segs, 2.0), np.full(n_segs, max(total_len * 2.0, 1.0))])
    sol = least_squares(residual, np.clip(x0, lo, hi), bounds=(lo, hi))

    poly = chain_sample_fixed(sol.x, n_segs, n_per_seg=60)  # 평가용은 촘촘하게
    d_left = point_to_polyline_dist(poly, left)
    d_right = point_to_polyline_dist(poly, right)
    sym_res = np.abs(d_left - d_right)
    d_centerline = point_to_polyline_dist(poly, centerline)  # 옛 지표(비교용)
    return sol.x, n_segs, {
        "fit_residual_max_m": float(d_centerline.max()),
        "sym_residual_max_m": float(sym_res.max()),           # 새 지표: 대칭성
        "sym_residual_rms_m": float(np.sqrt(np.mean(sym_res ** 2))),
    }
```

---

## 25단계: 클로소이드 도입 판단 — "충분하다"던 결론을 뒤집다

24단계에서 참조선 정의(경계 대칭 피팅)가 확정됐으니, '남은 빈틈' 1번이었던 클로소이드 도입 여부를 이제 판단할 수 있습니다. 먼저 18단계의 곡률 계단 수치는 옛 방식(평균 중심선 기준) 기준이라 24단계 방식으로 다시 쟀습니다.

곡률 계단을 그냥 [1/m] 단위로 보면 "이 정도면 큰가 작은가"를 판단하기 어렵습니다. 그래서 회귀 테스트가 실제로 신경 쓰는 물리량으로 바꿨습니다 — 곡률이 Δκ만큼 순간적으로 튀는 지점을 속도 v로 지나가면, 횡가속도가 **Δa = v² · Δκ** 만큼 즉각 점프합니다. 조향 컨트롤러 입장에서는 스텝 입력이나 마찬가지입니다.

| 속도 | Δa > 2 m/s² 비율 (Karlsruhe) | Δa > 4 m/s² 비율 (Karlsruhe) |
|---|---|---|
| 18km/h | 48.3% | 25.2% |
| 29km/h | 75.5% | 55.1% |
| 50km/h | 87.8% | 79.6% |

(Autoware 샘플맵도 방향은 같고 크기만 작습니다 — 18km/h에서 24.2%/12.1%, 50km/h에서 55.6%/43.7%.)

승용차 급조향 수준(4 m/s²)을 넘는 순간 가속도 점프가 도심 속도(18km/h)에서도 이음새의 4분의 1, 시속 50km에서는 5개 중 4개꼴로 발생합니다. **이건 7단계에서 "이 정도 데이터로는 paramPoly3 없이도 Line+Arc로 충분해 보인다"고 내렸던 결론을 사실상 뒤집는 결과입니다.** 그때는 위치 잔차(2~3cm)만 보고 판단했는데, 곡률 불연속이 만드는 동역학적 충격은 위치 잔차와는 다른 이야기였습니다. **판단: 클로소이드가 필요합니다.**

다만 "필요하다"와 "쉽게 넣을 수 있다"는 별개였습니다. 곡률 계단이 가장 큰 케이스(1.31 [1/m], 거의 직선(κ≈0.014)에서 반경 0.76m짜리 급커브(κ≈1.32)로 전환)에 길이 3m 고정 클로소이드를 끼워 넣어봤더니, 대칭 잔차가 0.03m → **1.23m로 오히려 폭발했습니다.**

```python
def spiral_sample(x0, y0, h0, k0, k1, L, s_query):
    """선형 곡률 램프(클로소이드) 위 s_query 지점들의 (x, y, 최종 heading).
    닫힌 형태가 없어서 heading을 촘촘히 적분한 뒤 s_query에 보간한다."""
    n_fine = max(len(s_query) * 20, 200)
    s_fine = np.linspace(0, L, n_fine)
    theta_fine = h0 + k0 * s_fine + 0.5 * (k1 - k0) / L * s_fine ** 2
    x_fine = x0 + np.concatenate([[0], cumulative_trapezoid(np.cos(theta_fine), s_fine)])
    y_fine = y0 + np.concatenate([[0], cumulative_trapezoid(np.sin(theta_fine), s_fine)])
    x_q = np.interp(s_query, s_fine, x_fine)
    y_q = np.interp(s_query, s_fine, y_fine)
    theta_end = h0 + k0 * L + 0.5 * (k1 - k0) / L * L ** 2
    return x_q, y_q, theta_end
```

전환 길이를 3m로 고정한 게 문제였습니다 — 곡률이 그렇게 크게 튀는 구간(거의 직선에서 반경 1m 미만 커브로)을 3m 안에 욱여넣으니 경로 자체가 원래 경계에서 크게 벗어난 겁니다. **전환 길이도 피팅 대상에 포함시켜야 한다는 게 이번 스파이크의 결론입니다** — 다음 시도는 24단계의 전역 최적화에 클로소이드 세그먼트(κ_start, κ_end, L 전부 자유 변수)를 추가해서, 대칭 잔차와 곡률 연속성을 동시에 최적화하는 것입니다. (이 최악 케이스 자체가 반경 0.76m라는 이례적인 값이라, 보도 경계 모서리 같은 비정상 지오메트리일 가능성도 있어 대표성은 더 봐야 합니다.)

---

## 26단계: `superelevation`(횡단 경사) 첫 실측

'남은 빈틈'에는 Junction 생성과 나란히 남아 있었지만, Junction은 A(그룹핑) + `RoutingGraph` + 커넥팅 로드 지오메트리까지 새로 설계해야 하는 큰 작업인 반면, superelevation은 22단계에서 이미 만든 고도 피팅 인프라(`load_osm_with_ele`, `resample_xyz_to_common_length`, `fit_elevation_cubic`)를 거의 그대로 재사용할 수 있어서 먼저 처리했습니다.

정의는 간단합니다. 왼쪽 경계 고도 `z_left(s)`, 오른쪽 경계 고도 `z_right(s)`, 그 지점의 도로 폭 `w(s)`가 있으면, 횡단 경사(무차원 기울기)는

```
cross_slope(s) = (z_left(s) - z_right(s)) / w(s)
```

OpenDRIVE의 `<superelevation>`도 `elevation_profile`과 똑같이 s에 대한 3차 다항식이라, 피팅 코드도 그대로 재사용했습니다 — `fit_elevation_cubic`에 z(s) 대신 `cross_slope(s)`를 넣기만 하면 됩니다. (A(그룹핑) 없이 lanelet 단위로만 쟀으므로, "고도 이음새"는 여전히 이번 스코프 밖입니다 — Road 체인이 있어야 잴 수 있는 건 22단계와 동일합니다.)

Autoware 샘플맵(22단계와 같은, ele 데이터가 있는 유일한 맵)의 subtype=road lanelet 163개에 돌린 결과:

| 지표 | mean | p50 | p95 | max |
|---|---|---|---|---|
| lanelet당 최대 \|cross_slope\| | 2.50% | 2.45% | 3.56% | 4.57% |
| cross_slope(s) 피팅 잔차(max) | 0.47% | - | 1.15% | 1.87% |

무시할 수 있는 크기가 아니었습니다. 통상 도로 설계의 슈퍼일리베이션 범위가 2~8%(급커브 구간은 10%+)인데, **이 맵 lanelet의 87.7%가 이미 2%를 넘습니다.** 3차 다항식 피팅 잔차도 작아서(mean 0.47%), `elevation_profile`과 같은 방식으로 무리 없이 모델링됩니다. z(s) 하나만 담던 22단계의 IR로는 이 뱅크각이 통째로 사라졌을 거라는 뜻이고, 3DGS 씬은 이 뱅크각을 그대로 담고 있을 테니 방치하면 도로 모델이 씬과 옆으로 기울어 어긋나는 문제였습니다. `Road.superelevation` 필드를 IR 스키마(3단계)에 추가했습니다.

```python
def cross_slope_of(left_r, leftz_r, right_r, rightz_r):
    """cross_slope(s) = (z_left - z_right) / width(s). +면 왼쪽이 높다."""
    width = np.linalg.norm(left_r - right_r, axis=1)
    width = np.maximum(width, 0.1)  # 폭 0 근처에서 발산 방지
    return (leftz_r - rightz_r) / width


# 실행 루프의 핵심 — 나머지는 22단계 iter_road_centerlines_3d와 거의 동일
for ll, centerline, left_r, leftz_r, right_r, rightz_r in iter_road_boundaries_3d():
    s = s_of(centerline)
    slope = cross_slope_of(left_r, leftz_r, right_r, rightz_r)
    coeffs, max_r, rms_r = fit_elevation_cubic(s, slope)  # z(s) 대신 slope(s)를 피팅
```

---

## 27단계: 클로소이드 전환 길이를 자유 변수로 — 잔차는 잡았는데 승차감을 놓쳤다

25단계에서 전환 길이를 고정값(3m)으로 넣었다가 잔차가 폭발했던 문제를, 이번엔 길이 `L` 자체를 대칭 잔차 최소화 대상으로 넣어 풀어봤습니다. 25단계의 최악 케이스(lanelet 45326, 곡률 계단 1.31 [1/m])에 1차원 최소자승으로 최적 `L`을 찾았더니:

| | 고정 L=3m (25단계) | 자유 L 최적화 |
|---|---|---|
| 대칭 잔차 | 1.23m | **0.014m** |
| 전환 길이 | 3m | 0.204m |

잔차는 확실히 잡혔습니다 — 0.2m 근방부터 30m까지 길이를 촘촘히 스캔해봐도 최적화 결과와 일치하는 지점에서 최솟값이 나와서, 국소해 함정도 아니었습니다. 두 맵에서 곡률 계단이 있는 lanelet 15개씩(총 30개)에 일반화해봐도 자유 L이 고정 L보다 나빴던 케이스는 **0건**이었고, 평균 잔차도 Karlsruhe 98cm→2cm, Autoware 64cm→0.8cm로 확실히 개선됐습니다.

여기서 멈췄으면 "해결됐다"고 썼을 텐데, 최적 길이 분포를 보니 뭔가 이상했습니다 — 평균 0.28m, 최악 케이스는 0.204m로 **너무 짧습니다.** 25단계에서 클로소이드를 도입하려던 이유가 "곡률이 순간적으로 튀면 횡가속도가 스텝 함수처럼 점프해서 승차감이 나쁘다"는 것이었는데, 전환 길이가 20cm라면 그 램프도 사실상 순간적인 것 아닌가 싶어서 확인해봤습니다.

곡률이 `Δκ`만큼 길이 `L`에 걸쳐 선형으로 변하면, 등속 주행 시 횡가속도 변화율(jerk)은 `da/dt ≈ v³ · (Δκ/L)`입니다. 최악 케이스(Δκ=1.31, L*=0.204m, v=8m/s)를 넣으면:

```
곡률 변화율 dκ/ds = 1.306 / 0.204 ≈ 6.4 [1/m²]
jerk = 8³ × 6.4 ≈ 3,278 m/s³
```

편안한 승차감 한계(~2~4 m/s³)의 **거의 1,000배**입니다. 최악 케이스만 그런가 싶어 30개 표본 전체로 jerk를 다시 냈더니:

| | Karlsruhe (15개) | Autoware (15개) |
|---|---|---|
| jerk [m/s³] (v=8m/s) — mean/max | 715 / 2,057 | 450 / 988 |
| 편안한 한계(4 m/s³) 이내 비율 | **0.0%** | **0.0%** |

**30개 표본 전부가 편안한 승차감 한계를 벗어났습니다.** 최악 케이스만의 문제가 아니라 일반적인 현상이었습니다. 원인은 명확합니다 — "대칭 잔차를 최소화하는 길이"는 정의상 좌/우 경계에 최대한 딱 맞게 붙는 최단 경로를 찾으려 하고, 그건 "곡률을 부드럽게 바꾸는 것"과 정반대 방향입니다. **기하학적으로 경계에 잘 맞는 것과, 동역학적으로 편안한 것은 이 문제에서 서로 경쟁하는 목적함수였습니다.**

```python
def optimal_spiral_length(x0, y0, h0, k0, k1, left, right, n_per_seg=30,
                           l_lo=0.1, l_hi=50.0, l_init=3.0):
    """대칭 잔차를 최소화하는 전환 길이 L을 1차원 최소자승으로 찾는다."""
    def residual(L_arr):
        L = float(np.clip(L_arr[0], l_lo, l_hi))
        s_q = np.linspace(0, L, n_per_seg)
        xs, ys, _ = spiral_sample(x0, y0, h0, k0, k1, L, s_q)
        pts = np.stack([xs, ys], axis=1)
        d_left = point_to_polyline_dist(pts, left)
        d_right = point_to_polyline_dist(pts, right)
        return d_left - d_right

    sol = least_squares(residual, x0=[l_init], bounds=([l_lo], [l_hi]))
    return float(sol.x[0])
```

**결론: 전환 길이는 잔차 최소화가 아니라 jerk 예산으로 정해야 합니다.** `L = v³·Δκ / jerk_max`처럼 물리적으로 정한 뒤, 그 길이에서 잔차가 얼마나 나오는지를 결과로 받아들이는 방향이 맞습니다. 최악 케이스로 역산해보면 `L = 8³×1.306/4 ≈ 167m`인데, 이 정도 길이는 이 지도의 어떤 lanelet보다도 깁니다 — 그 말은 이 특정 곡률 점프(반경 0.76m 코너)는 **애초에 시속 29km 주행으로 편안하게 지나갈 수 있는 지오메트리가 아니라는 뜻**입니다. 25단계에서 이미 "보도 경계 모서리 같은 비정상 지오메트리일 가능성"을 의심했었는데, 이번 계산이 그 의심을 정량적으로 뒷받침합니다 — 저속 진입로나 주차장 모서리처럼 애초에 급감속이 전제된 구간일 가능성이 높습니다.

더 근본적으로는, 이 문제를 27단계처럼 **피팅이 끝난 뒤 이음새를 사후 패치하는 방식**으로는 한계가 있다는 것도 드러났습니다. 24단계의 전역 최적화 자체에 곡률 변화율(또는 jerk) 페널티 항을 넣어서, 애초에 "부드럽게 변하는 곡률"을 선호하도록 피팅하는 게 다음으로 시도할 방향입니다 — 세그먼트를 다 맞춘 다음 이음새만 땜질하는 게 아니라, 처음부터 매끄러움을 목적함수에 넣는 것입니다.

---

## 남은 빈틈: 다음 스파이크의 우선순위

18~27단계에서 이 목록의 아홉 항목 — 세그먼트 연속성, 곡률 오차, pairing 편향, xodr 출력 + 라운드트립 검증, 고도 피팅, 중심선 재정의, 클로소이드 도입 판단, superelevation, 클로소이드 전환 길이 자유화 — 을 전부 스파이크했습니다. superelevation은 26단계에서 해결됐지만, 클로소이드 전환 길이는 27단계에서 "잔차 최소화"라는 목적함수 자체가 틀렸다는 게 드러나 다시 원점으로 돌아갔습니다. 갱신된 목록을 중요한 순서대로 다시 정리합니다.

**1. 곡률 변화율(jerk) 페널티를 전역 최적화에 직접 넣기 — 최우선.** 27단계에서 "사후 패치로 전환 길이만 최적화"하는 방식은 잔차는 잡아도 jerk가 표본 전부(30/30)에서 편안한 한계를 벗어난다는 게 드러났습니다. 24단계의 전역 최적화 자체에 `dκ/ds`(또는 jerk) 페널티 항을 넣어서, 세그먼트를 다 맞춘 뒤 이음새를 땜질하는 게 아니라 처음부터 매끄러운 곡률 변화를 선호하도록 피팅 목적함수를 다시 설계해야 합니다.

**2. Junction 생성.** 실제 OpenDRIVE `<junction>` 은 여전히 스키마 한 줄 외에 아무것도 없습니다. A(그룹핑)로 Road 체인을 만드는 게 선행 조건이라, **고도 이음새(경사 불연속) 측정**도 이 작업과 함께 처리할 수 있습니다 — 26단계는 lanelet 단위로만 쟀고, Road 체인 간 이음새는 여전히 미측정입니다.

**3. esmini/CARLA 실기 로딩.** opendrive2lanelet 파싱은 통과했지만, 시뮬레이터가 이 xodr을 실제로 로딩·주행하는지는 별개 문제입니다. 24단계에서 확정된 새 중심선 기준으로 xodr을 다시 익스포트해서 라운드트립도 재검증해야 하고, 이제 `superelevation`(26단계)까지 반영해서 내보내야 합니다.

**4. 회사 실측 맵 검증.** 두 공개 맵에서도 결론이 갈렸던 만큼(20·22·23단계), 회사 맵은 세 번째 데이터 포인트로서 더 중요해졌습니다. 24~27단계 결론이 회사 맵에서도 유지되는지가 특히 중요합니다.

우선순위를 이렇게 두는 이유 — 27단계에서 사후 패치 방식의 한계가 확인됐으니, 1(피팅 자체에 jerk 페널티 통합)이 곡률 정확도와 승차감을 동시에 좌우하는 진짜 최우선 과제입니다. 2(Junction)가 그다음인 이유는 A(그룹핑) 작업이 고도 이음새 측정과 4의 회사 맵 검증 모두의 선행 조건이기 때문입니다.

---

## 부록: 스파이크 전체 코드

본문에 전부 싣지 않은 스파이크 코드를 모아둔 부록입니다. `numpy`, `scipy`, `matplotlib`만 있으면 그대로 실행됩니다 — Docker(`--platform linux/amd64` 컨테이너에서 `pip install lanelet2`)가 필요한 것은 `RoutingGraph`를 쓰는 13·16단계뿐입니다. 10단계의 Vehicle 단독 `RoutingGraph` 버전은 13단계 코드에서 `participants` 리스트를 `Vehicle` 하나로 줄인 것과 같아 따로 싣지 않습니다.

### B, C: 참조선 피팅 + 곡률 오차 (`spike_fit.py`)

```python
"""
Lanelet2 -> OpenDRIVE IR 스파이크 (B: 참조선 피팅, C: 곡률 오차).
Lanelet2 공식 예제 맵 mapping_example.osm으로 검증한다.
https://github.com/fzi-forschungszentrum-informatik/Lanelet2/blob/master/lanelet2_maps/res/mapping_example.osm

의존성: numpy, scipy, matplotlib
(lanelet2 파이썬 바인딩은 빌드가 무거워서, OSM XML을 직접 파싱하는 경량 로더로 대체했다.)
"""
import xml.etree.ElementTree as ET
import numpy as np
from scipy.optimize import least_squares
import matplotlib.pyplot as plt

OSM_PATH = "/Users/yeongjun/Downloads/mapping_example.osm"


# ---- OSM 파싱 ----

def load_osm(path):
    tree = ET.parse(path)
    root = tree.getroot()

    nodes = {}
    for n in root.findall("node"):
        nodes[n.get("id")] = (float(n.get("lat")), float(n.get("lon")))

    ways = {}
    for w in root.findall("way"):
        refs = [nd.get("ref") for nd in w.findall("nd")]
        ways[w.get("id")] = refs

    lanelets = []
    for rel in root.findall("relation"):
        tags = {t.get("k"): t.get("v") for t in rel.findall("tag")}
        if tags.get("type") != "lanelet":
            continue
        left_way = right_way = None
        for m in rel.findall("member"):
            if m.get("role") == "left":
                left_way = m.get("ref")
            elif m.get("role") == "right":
                right_way = m.get("ref")
        if left_way and right_way:
            lanelets.append({
                "id": rel.get("id"), "left": left_way, "right": right_way,
                "subtype": tags.get("subtype"),
            })

    return nodes, ways, lanelets


def latlon_to_local_xy(nodes, ref_lat, ref_lon):
    """작은 영역이므로 등장방형(equirectangular) 근사로 미터 좌표로 투영한다."""
    R = 6378137.0
    ref_lat_rad = np.radians(ref_lat)
    xy = {}
    for nid, (lat, lon) in nodes.items():
        dlat = np.radians(lat - ref_lat)
        dlon = np.radians(lon - ref_lon)
        x = dlon * R * np.cos(ref_lat_rad)
        y = dlat * R
        xy[nid] = np.array([x, y])
    return xy


def way_points(ways, xy, way_id):
    return np.array([xy[n] for n in ways[way_id]])


def align_winding(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """b가 a와 반대 방향으로 감겨 있으면 뒤집는다.
    a[0]이 b[0]보다 b[-1]에 더 가까우면 반대 방향으로 판단한다.
    (14단계 참고: 일부 짧은 lanelet은 좌우 경계선이 반대 방향으로 감겨 있어,
    이 보정 없이 포인트별 평균을 내면 중심선이 뭉개진다.)"""
    d_start = np.linalg.norm(a[0] - b[0])
    d_end = np.linalg.norm(a[0] - b[-1])
    return b[::-1] if d_end < d_start else b


def resample_to_common_length(a: np.ndarray, b: np.ndarray, n: int = 50):
    """호 길이 기준으로 두 폴리라인을 같은 개수의 점으로 재샘플링한다.
    두 경계선의 감김 방향이 반대인 경우를 먼저 맞춘 뒤 샘플링한다."""
    b = align_winding(a, b)
    def resample(pts, n):
        seg_len = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        s = np.concatenate([[0], np.cumsum(seg_len)])
        total = s[-1]
        if total == 0:
            return np.repeat(pts[:1], n, axis=0)
        query = np.linspace(0, total, n)
        x = np.interp(query, s, pts[:, 0])
        y = np.interp(query, s, pts[:, 1])
        return np.stack([x, y], axis=1)
    return resample(a, n), resample(b, n)


# ---- B. 참조선 피팅 ----

def fit_line(points: np.ndarray):
    """최소자승 직선 피팅(SVD). 반환: (LineSeg dict, rms_residual, max_residual)."""
    centroid = points.mean(axis=0)
    centered = points - centroid
    _, _, vt = np.linalg.svd(centered)
    direction = vt[0]
    heading = np.arctan2(direction[1], direction[0])

    proj = centered @ direction
    start = centroid + proj.min() * direction
    length = proj.max() - proj.min()

    normal = np.array([-direction[1], direction[0]])
    residuals = centered @ normal
    rms = float(np.sqrt(np.mean(residuals ** 2)))
    max_res = float(np.max(np.abs(residuals)))
    return {"start": start, "heading": heading, "length": length}, rms, max_res


def fit_arc(points: np.ndarray):
    """Kasa 방식 최소자승 원 피팅 후 시작점/헤딩/길이/곡률로 변환.
    반환: (ArcSeg dict, rms_residual, max_residual)."""
    x, y = points[:, 0], points[:, 1]

    def residual(params):
        cx, cy, r = params
        return np.sqrt((x - cx) ** 2 + (y - cy) ** 2) - r

    x0 = np.array([x.mean(), y.mean(), np.ptp(x) / 2 + 1e-3])
    sol = least_squares(residual, x0)
    cx, cy, r = sol.x

    angles = np.unwrap(np.arctan2(y - cy, x - cx))
    a0, a1 = angles[0], angles[-1]
    curvature = 1.0 / r if a1 > a0 else -1.0 / r
    length = abs(a1 - a0) * r
    tangent_dir = 1 if a1 > a0 else -1
    heading = a0 + tangent_dir * np.pi / 2

    dist_res = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) - r
    rms = float(np.sqrt(np.mean(dist_res ** 2)))
    max_res = float(np.max(np.abs(dist_res)))
    return (
        {"start": points[0], "heading": heading, "length": length,
         "curvature": curvature, "center": (cx, cy), "radius": r},
        rms, max_res,
    )


def simplify_polyline(points: np.ndarray, epsilon: float):
    """Ramer-Douglas-Peucker. 반환: 남긴 점들의 정렬된 인덱스 배열."""
    def rdp(idxs):
        if len(idxs) < 3:
            return idxs
        start, end = points[idxs[0]], points[idxs[-1]]
        line_vec = end - start
        line_len = np.linalg.norm(line_vec)
        if line_len == 0:
            dists = np.linalg.norm(points[idxs[1:-1]] - start, axis=1)
        else:
            normal = np.array([-line_vec[1], line_vec[0]]) / line_len
            dists = np.abs((points[idxs[1:-1]] - start) @ normal)
        if len(dists) == 0:
            return idxs
        max_i = np.argmax(dists)
        if dists[max_i] > epsilon:
            split = idxs[1:-1][max_i]
            left = rdp(idxs[: idxs.index(split) + 1])
            right = rdp(idxs[idxs.index(split):])
            return left[:-1] + right
        return [idxs[0], idxs[-1]]

    idxs = rdp(list(range(len(points))))
    return np.array(sorted(set(idxs)))


def fit_reference_line(centerline: np.ndarray, epsilon: float = 0.15):
    """구간별로 fit_line과 fit_arc를 모두 시도해 잔차가 작은 쪽을 채택한다.
    fit_residual은 등간격 s-샘플링이 아니라, 원본 각 점에서 피팅 곡선까지의
    최근접 거리(point-to-curve)로 계산한다."""
    breakpoints = simplify_polyline(centerline, epsilon)
    segments = []
    residuals_rms, residuals_max = [], []
    for a, b in zip(breakpoints[:-1], breakpoints[1:]):
        chunk = centerline[a:b + 1]
        if len(chunk) < 3:
            continue
        line_seg, line_rms, line_max = fit_line(chunk)
        arc_seg, arc_rms, arc_max = fit_arc(chunk)
        if line_rms <= arc_rms:
            segments.append(("line", line_seg, chunk))
            residuals_rms.append(line_rms)
            residuals_max.append(line_max)
        else:
            segments.append(("arc", arc_seg, chunk))
            residuals_rms.append(arc_rms)
            residuals_max.append(arc_max)
    return segments, {
        "fit_residual_max_m": max(residuals_max) if residuals_max else 0.0,
        "fit_residual_rms_m": float(np.sqrt(np.mean(np.square(residuals_rms)))) if residuals_rms else 0.0,
    }


# ---- C. 곡률 오차 ----

def discrete_curvature(points: np.ndarray):
    """3점 유한차분(메넬라우스 공식)으로 이산 곡률 κ(s)를 추정한다."""
    curv = np.zeros(len(points))
    for i in range(1, len(points) - 1):
        p0, p1, p2 = points[i - 1], points[i], points[i + 1]
        a = np.linalg.norm(p1 - p0)
        b = np.linalg.norm(p2 - p1)
        c = np.linalg.norm(p2 - p0)
        area2 = abs((p1[0] - p0[0]) * (p2[1] - p0[1]) - (p2[0] - p0[0]) * (p1[1] - p0[1]))
        curv[i] = 0 if a * b * c == 0 else 2 * area2 / (a * b * c)
    return curv


# ---- 실행: 단일 lanelet 상세 검증 + 시각화, 전체 분포 스캔 ----

def fit_one_lanelet(nodes, ways, xy, lanelets, min_length=15.0, min_curv=0.02):
    """커브가 섞인 lanelet 하나를 찾아 상세 피팅 결과를 낸다."""
    for ll in lanelets:
        try:
            left = way_points(ways, xy, ll["left"])
            right = way_points(ways, xy, ll["right"])
        except KeyError:
            continue
        if len(left) < 4 or len(right) < 4:
            continue
        left_r, right_r = resample_to_common_length(left, right, n=50)
        centerline = (left_r + right_r) / 2
        length = np.sum(np.linalg.norm(np.diff(centerline, axis=0), axis=1))
        curv = discrete_curvature(centerline)
        if length > min_length and np.max(np.abs(curv)) > min_curv:
            return ll, centerline, left_r, right_r
    ll = lanelets[0]
    left = way_points(ways, xy, ll["left"])
    right = way_points(ways, xy, ll["right"])
    left_r, right_r = resample_to_common_length(left, right, n=50)
    return ll, (left_r + right_r) / 2, left_r, right_r


def scan_all_lanelets(nodes, ways, xy, lanelets):
    """전체 lanelet에 대해 fit_residual 분포를 낸다."""
    max_residuals, rms_residuals, lengths = [], [], []
    for ll in lanelets:
        try:
            left = way_points(ways, xy, ll["left"])
            right = way_points(ways, xy, ll["right"])
        except KeyError:
            continue
        if len(left) < 3 or len(right) < 3:
            continue
        left_r, right_r = resample_to_common_length(left, right, n=30)
        centerline = (left_r + right_r) / 2
        length = np.sum(np.linalg.norm(np.diff(centerline, axis=0), axis=1))
        if length < 1.0:
            continue
        try:
            segments, stats = fit_reference_line(centerline, epsilon=0.15)
        except Exception:
            continue
        max_residuals.append(stats["fit_residual_max_m"])
        rms_residuals.append(stats["fit_residual_rms_m"])
        lengths.append(length)
    return np.array(max_residuals), np.array(rms_residuals), lengths


def main():
    nodes, ways, lanelets = load_osm(OSM_PATH)
    print(f"nodes={len(nodes)} ways={len(ways)} lanelets={len(lanelets)}")

    ref_lat, ref_lon = next(iter(nodes.values()))
    xy = latlon_to_local_xy(nodes, ref_lat, ref_lon)

    print("\n=== 단일 lanelet 상세 검증 ===")
    ll, centerline, left_r, right_r = fit_one_lanelet(nodes, ways, xy, lanelets)
    print(f"선택된 lanelet id={ll['id']}, "
          f"중심선 길이={np.sum(np.linalg.norm(np.diff(centerline, axis=0), axis=1)):.2f}m")

    segments, stats = fit_reference_line(centerline, epsilon=0.15)
    print(f"세그먼트 수: {len(segments)}")
    print(f"fit_residual_max_m: {stats['fit_residual_max_m']:.4f}")
    print(f"fit_residual_rms_m: {stats['fit_residual_rms_m']:.4f}")

    orig_curv = discrete_curvature(centerline)
    max_curv = np.max(np.abs(orig_curv))
    print(f"원본 최대 곡률(1/m): {max_curv:.4f} (반경 {1 / max(max_curv, 1e-6):.1f}m)")

    seg_types = [s[0] for s in segments]
    print(f"세그먼트 타입 분포: line={seg_types.count('line')}, arc={seg_types.count('arc')}")

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(left_r[:, 0], left_r[:, 1], "b--", alpha=0.4, label="left bound")
    ax.plot(right_r[:, 0], right_r[:, 1], "g--", alpha=0.4, label="right bound")
    ax.plot(centerline[:, 0], centerline[:, 1], "k.", markersize=3, label="centerline (원본)")
    for kind, seg, chunk in segments:
        color = "red" if kind == "line" else "orange"
        ax.plot(chunk[:, 0], chunk[:, 1], color=color, linewidth=2)
    ax.set_aspect("equal")
    ax.legend()
    ax.set_title(
        f"lanelet {ll['id']} reference line fit\n"
        f"residual max={stats['fit_residual_max_m']*100:.1f}cm rms={stats['fit_residual_rms_m']*100:.1f}cm"
    )
    fig.savefig("spike_fit_result.png", dpi=120)

    print("\n=== 전체 lanelet 분포 (B/C 스캔) ===")
    max_res, rms_res, lengths = scan_all_lanelets(nodes, ways, xy, lanelets)
    print(f"성공: {len(max_res)} / 전체: {len(lanelets)}")
    print(f"fit_residual_max_m: mean={max_res.mean():.4f} p50={np.percentile(max_res,50):.4f} "
          f"p95={np.percentile(max_res,95):.4f} max={max_res.max():.4f}")
    print(f"fit_residual_rms_m: mean={rms_res.mean():.4f} p95={np.percentile(rms_res,95):.4f}")
    worst = int(np.argmax(max_res))
    print(f"최악 케이스 fit_residual_max_m={max_res[worst]:.4f}, lanelet 길이={lengths[worst]:.1f}m")


if __name__ == "__main__":
    main()
```

### A: 그룹핑 (`spike_group.py`)

```python
"""
A. Lanelet2 -> Road 그룹핑 스파이크.

전략:
1. 좌우 인접(side-adjacency): 두 lanelet이 경계 way를 공유하면 같은 단면
   (LaneSection) 후보로 묶는다. Union-Find로 클러스터링.
2. 종방향 인접(longitudinal adjacency): 한 클러스터의 끝 node id가 다음 클러스터의
   시작 node id와 일치하면 이어붙인다. OSM은 연결된 lanelet들이 노드 id를 그대로
   공유하므로, 좌표 근접이 아니라 정확한 id 일치로 연결을 판정한다.
3. Road 경계: 차선 수가 바뀌거나, 클러스터가 둘 이상으로 분기/합류하는 지점에서 끊는다.

이 스파이크에서 확인한 것: 왼쪽 경계선 node id만으로 연결을 판정하면 일부 실제
연결(오른쪽 경계선에서만 정확히 이어지는 경우)을 놓친다. 그렇다고 왼쪽 '또는'
오른쪽 중 하나만 맞아도 연결로 인정하면, 교차로에서 우연히 좌표가 겹치는
스퓨리어스 매치가 급증한다. 왼쪽 '그리고' 오른쪽 모두 일치해야 한다는 조건은
반대로 너무 엄격해서 진짜 연결까지 잃는다. 세 방식을 모두 비교해서 이 사실을
확인하는 것이 이 스크립트의 목적이다 — 결론적으로 정확한 node id 매칭만으로는
부족하고, 근접 거리 + 진행 방향(heading) 일치까지 봐야 하는데 이건 Lanelet2
공식 RoutingGraph 라이브러리가 이미 구현해 둔 기능이다.
"""
from collections import defaultdict

from spike_fit import load_osm, latlon_to_local_xy, way_points, resample_to_common_length


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def build_side_clusters(lanelets):
    """boundary way를 공유하는 lanelet들을 하나의 단면 클러스터로 묶는다."""
    uf = UnionFind()
    way_to_lanelets = defaultdict(list)
    for ll in lanelets:
        way_to_lanelets[ll["left"]].append(ll["id"])
        way_to_lanelets[ll["right"]].append(ll["id"])
        uf.find(ll["id"])

    for ll_ids in way_to_lanelets.values():
        for a, b in zip(ll_ids[:-1], ll_ids[1:]):
            uf.union(a, b)

    clusters = defaultdict(list)
    for ll in lanelets:
        clusters[uf.find(ll["id"])].append(ll["id"])
    return list(clusters.values())


def lanelet_endpoints(ways, ll, sides=("left",)):
    """지정한 side(들)의 시작/끝 node id 집합을 낸다."""
    starts, ends = set(), set()
    for side in sides:
        nodes = ways[ll[side]]
        starts.add(nodes[0])
        ends.add(nodes[-1])
    return starts, ends


def build_cluster_graph(lanelets, ways, clusters, mode="left"):
    """클러스터 단위 successor/predecessor 그래프를 만든다.
    mode: "left"(왼쪽만), "either"(왼쪽 또는 오른쪽), "both"(왼쪽 그리고 오른쪽)."""
    ll_by_id = {ll["id"]: ll for ll in lanelets}

    left_s, left_e, right_s, right_e = {}, {}, {}, {}
    for idx, members in enumerate(clusters):
        ls, le, rs, re = set(), set(), set(), set()
        for m in members:
            ll = ll_by_id[m]
            s, e = lanelet_endpoints(ways, ll, sides=("left",))
            ls |= s; le |= e
            s, e = lanelet_endpoints(ways, ll, sides=("right",))
            rs |= s; re |= e
        left_s[idx], left_e[idx], right_s[idx], right_e[idx] = ls, le, rs, re

    successors = defaultdict(set)
    predecessors = defaultdict(set)
    for i in range(len(clusters)):
        for j in range(len(clusters)):
            if i == j:
                continue
            left_match = bool(left_e[i] & left_s[j])
            right_match = bool(right_e[i] & right_s[j])
            if mode == "left":
                connected = left_match
            elif mode == "either":
                connected = left_match or right_match
            elif mode == "both":
                connected = left_match and right_match
            else:
                raise ValueError(mode)
            if connected:
                successors[i].add(j)
                predecessors[j].add(i)
    return successors, predecessors


def segment_into_roads(clusters, successors, predecessors):
    """차선 수가 바뀌거나 분기/합류가 있는 지점에서 Road를 끊는다."""
    lane_count = {idx: len(members) for idx, members in enumerate(clusters)}

    visited = set()
    roads = []
    for start_idx in range(len(clusters)):
        if start_idx in visited:
            continue
        if len(predecessors[start_idx]) == 1:
            pred = next(iter(predecessors[start_idx]))
            if len(successors[pred]) == 1 and lane_count[pred] == lane_count[start_idx]:
                continue

        chain = [start_idx]
        visited.add(start_idx)
        cur = start_idx
        while (
            len(successors[cur]) == 1
            and len(predecessors[next(iter(successors[cur]))]) == 1
            and lane_count[next(iter(successors[cur]))] == lane_count[cur]
        ):
            nxt = next(iter(successors[cur]))
            if nxt in visited:
                break
            chain.append(nxt)
            visited.add(nxt)
            cur = nxt
        roads.append(chain)

    return roads


def analyze_single_clusters(clusters, successors, predecessors, roads, ways, xy, lanelets):
    """단일 클러스터 Road가 교차로 인접인지, 순수 고립인지 구분한다."""
    ll_by_id = {ll["id"]: ll for ll in lanelets}
    single_roads = [r[0] for r in roads if len(r) == 1]

    near_junction, isolated_idxs = 0, []
    for idx in single_roads:
        is_near = (
            len(successors[idx]) >= 2 or len(predecessors[idx]) >= 2
            or any(len(successors[p]) >= 2 for p in predecessors[idx])
            or any(len(predecessors[s]) >= 2 for s in successors[idx])
        )
        if is_near:
            near_junction += 1
        else:
            isolated_idxs.append(idx)

    print(f"단일 클러스터 Road {len(single_roads)}개 중 교차로 인접 {near_junction}개, "
          f"고립 {len(isolated_idxs)}개")

    subtype_counts = defaultdict(int)
    for idx in isolated_idxs:
        for m in clusters[idx]:
            subtype_counts[ll_by_id[m]["subtype"]] += 1
    print(f"고립 클러스터의 subtype 분포: {dict(subtype_counts)}")

    road_subtype_isolated = [
        idx for idx in isolated_idxs
        if all(ll_by_id[m]["subtype"] == "road" for m in clusters[idx])
    ]
    return road_subtype_isolated


def main():
    nodes, ways, lanelets = load_osm("/Users/yeongjun/Downloads/mapping_example.osm")
    ref_lat, ref_lon = next(iter(nodes.values()))
    xy = latlon_to_local_xy(nodes, ref_lat, ref_lon)
    print(f"lanelets={len(lanelets)}")

    clusters = build_side_clusters(lanelets)
    lane_counts = [len(c) for c in clusters]
    print(f"단면 클러스터 수={len(clusters)}, 차선 수 분포: "
          f"1차선={lane_counts.count(1)}, 2차선={lane_counts.count(2)}, "
          f"3차선 이상={sum(1 for n in lane_counts if n >= 3)}")

    print("\n=== 연결 판정 기준별 비교 (left / either / both) ===")
    for mode in ("left", "either", "both"):
        successors, predecessors = build_cluster_graph(lanelets, ways, clusters, mode=mode)
        branch = sum(1 for i in range(len(clusters)) if len(successors[i]) >= 2)
        merge = sum(1 for i in range(len(clusters)) if len(predecessors[i]) >= 2)
        roads = segment_into_roads(clusters, successors, predecessors)
        lens = [len(r) for r in roads]
        print(f"[{mode:6s}] 분기점={branch:3d} 합류점={merge:3d} "
              f"Road수={len(roads):3d} 단일클러스터={lens.count(1):3d}")

    print("\n=== mode=left 기준 고립 Road 원인 분석 ===")
    successors, predecessors = build_cluster_graph(lanelets, ways, clusters, mode="left")
    roads = segment_into_roads(clusters, successors, predecessors)
    road_subtype_isolated = analyze_single_clusters(
        clusters, successors, predecessors, roads, ways, xy, lanelets
    )
    print(f"subtype=road인데 고립된 클러스터: {len(road_subtype_isolated)}개")

    print("\n=== mode=either 기준으로 재검증: 위 고립 클러스터 중 몇 개가 회복되나 ===")
    successors_e, predecessors_e = build_cluster_graph(lanelets, ways, clusters, mode="either")
    recovered = sum(
        1 for idx in road_subtype_isolated
        if len(successors_e[idx]) + len(predecessors_e[idx]) > 0
    )
    print(f"{len(road_subtype_isolated)}개 중 {recovered}개 회복 "
          f"(단, either 기준은 전체 분기/합류점을 두 배 넘게 늘리는 부작용이 있음 — 위 비교표 참고)")


if __name__ == "__main__":
    main()
```

### 18~21단계: 연속성·곡률·편향·라운드트립 보조 코드

핵심 함수(`chain_sample`, `point_to_polyline_dist`, `fit_reference_line_global`, `smooth_points`, `ray_polyline_intersection`, `normal_projection_centerline`, `road_xml`의 planView 부분, 라운드트립 파싱)는 본문 18~21단계에 있습니다. 여기에는 본문에서 생략한 나머지 — 끝점/헤딩을 명시적으로 계산하는 확장 피팅, 이음새 지표, greedy 체인 피팅(실패 사례), 곡률 조회, 폭 다항식, 라운드트립 매칭 루프 — 를 싣습니다. `load_osm`/`latlon_to_local_xy`/`way_points`/`align_winding`/`resample_to_common_length`는 위 `spike_fit.py`의 것을 그대로 재사용합니다.

```python
def _wrap_angle(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


# ---- 맵 스캔 이터레이터: subtype=road, 길이 1m 이상 (18~21단계 공통) ----

def iter_road_centerlines(n_resample=30, min_length=1.0):
    nodes, ways, lanelets = load_osm()
    ref_lat, ref_lon = next(iter(nodes.values()))
    xy = latlon_to_local_xy(nodes, ref_lat, ref_lon)
    for ll in lanelets:
        if ll["subtype"] != "road":
            continue
        try:
            left = way_points(ways, xy, ll["left"])
            right = way_points(ways, xy, ll["right"])
        except KeyError:
            continue
        if len(left) < 3 or len(right) < 3:
            continue
        left_r, right_r = resample_to_common_length(left, right, n=n_resample)
        centerline = (left_r + right_r) / 2
        if np.sum(np.linalg.norm(np.diff(centerline, axis=0), axis=1)) < min_length:
            continue
        yield ll, centerline, left_r, right_r


# ---- 18단계: 끝점/헤딩을 명시적으로 계산하는 확장 피팅 ----
# 기존 fit_line/fit_arc는 잔차만 반환해서 이음새를 잴 수 없었다.
# seg dict: kind, start_pt, end_pt, h_start, h_end, curvature(0=line), length, rms, max

def fit_line_free(points):
    centroid = points.mean(axis=0)
    centered = points - centroid
    _, _, vt = np.linalg.svd(centered)
    d = vt[0]
    if np.dot(d, points[-1] - points[0]) < 0:   # 진행 방향과 부호 정렬
        d = -d
    proj = centered @ d
    start_pt = centroid + proj[0] * d
    end_pt = centroid + proj[-1] * d
    normal = np.array([-d[1], d[0]])
    res = centered @ normal
    h = float(np.arctan2(d[1], d[0]))
    return {"kind": "line", "start_pt": start_pt, "end_pt": end_pt,
            "h_start": h, "h_end": h, "curvature": 0.0,
            "length": float(np.linalg.norm(end_pt - start_pt)),
            "rms": float(np.sqrt(np.mean(res ** 2))), "max": float(np.max(np.abs(res)))}


def fit_arc_free(points):
    x, y = points[:, 0], points[:, 1]

    def residual(params):
        cx, cy, r = params
        return np.sqrt((x - cx) ** 2 + (y - cy) ** 2) - r

    sol = least_squares(residual, np.array([x.mean(), y.mean(), np.ptp(x) / 2 + 1e-3]))
    cx, cy, r = sol.x
    C, r = np.array([cx, cy]), abs(r)
    theta = np.unwrap(np.arctan2(y - cy, x - cx))
    dtheta = theta[-1] - theta[0]
    sign = 1.0 if dtheta > 0 else -1.0          # +: ccw(좌회전)
    start_pt = C + r * np.array([np.cos(theta[0]), np.sin(theta[0])])
    end_pt = C + r * np.array([np.cos(theta[-1]), np.sin(theta[-1])])
    res = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) - r
    return {"kind": "arc", "start_pt": start_pt, "end_pt": end_pt,
            "h_start": _wrap_angle(float(theta[0] + sign * np.pi / 2)),
            "h_end": _wrap_angle(float(theta[-1] + sign * np.pi / 2)),
            "curvature": float(sign / r), "length": float(abs(dtheta) * r),
            "center": C, "radius": float(r),
            "rms": float(np.sqrt(np.mean(res ** 2))), "max": float(np.max(np.abs(res)))}


def fit_reference_line_independent(centerline, epsilon=0.15):
    """구간별 독립 피팅(기존 방식)을 확장 피팅으로 다시 구현한 것."""
    breakpoints = simplify_polyline(centerline, epsilon)
    segments = []
    for a, b in zip(breakpoints[:-1], breakpoints[1:]):
        chunk = centerline[a:b + 1]
        if len(chunk) < 3:
            continue
        line_seg, arc_seg = fit_line_free(chunk), fit_arc_free(chunk)
        seg = line_seg if line_seg["rms"] <= arc_seg["rms"] else arc_seg
        segments.append(seg)
    stats = {
        "fit_residual_max_m": max((s["max"] for s in segments), default=0.0),
        "fit_residual_rms_m": float(np.sqrt(np.mean([s["rms"] ** 2 for s in segments]))) if segments else 0.0,
    }
    return segments, stats


def joint_metrics(segments):
    """인접 세그먼트 간 위치 갭, 헤딩 꺾임, 곡률 계단."""
    gaps, heading_jumps, curvature_steps = [], [], []
    for prev, nxt in zip(segments[:-1], segments[1:]):
        gaps.append(float(np.linalg.norm(nxt["start_pt"] - prev["end_pt"])))
        heading_jumps.append(abs(_wrap_angle(nxt["h_start"] - prev["h_end"])))
        curvature_steps.append(abs(nxt["curvature"] - prev["curvature"]))
    return gaps, heading_jumps, curvature_steps


# ---- 18단계 시도 1: greedy G1 체인 피팅 (실패 사례 — 기록용) ----
# 이전 끝점 p0·끝헤딩 h0에 다음 구간의 시작을 고정한다. 직선은 남는 자유도 0,
# 원호는 곡률 하나. 결과: 앞 구간의 헤딩 오차가 전파되어 잔차 폭발 (본문 참고).

def fit_line_chained(points, p0, h0):
    d = np.array([np.cos(h0), np.sin(h0)])
    normal = np.array([-d[1], d[0]])
    rel = points - p0
    res = rel @ normal
    end_pt = p0 + max(float(rel[-1] @ d), 0.0) * d
    return {"kind": "line", "start_pt": p0, "end_pt": end_pt,
            "h_start": h0, "h_end": h0, "curvature": 0.0,
            "length": float(np.linalg.norm(end_pt - p0)),
            "rms": float(np.sqrt(np.mean(res ** 2))), "max": float(np.max(np.abs(res)))}


def fit_arc_chained(points, p0, h0):
    t0 = np.array([np.cos(h0), np.sin(h0)])
    n0 = np.array([-t0[1], t0[0]])              # 좌측 법선. κ>0(좌회전)이면 중심이 이쪽

    def residual(kappa):
        k = kappa[0] if abs(kappa[0]) > 1e-9 else 1e-9
        C = p0 + n0 / k
        return np.linalg.norm(points - C, axis=1) - abs(1.0 / k)

    free = fit_arc_free(points) if len(points) >= 3 else None
    chord = points[-1] - points[0]
    turn_sign = 1.0 if (t0[0] * chord[1] - t0[1] * chord[0]) >= 0 else -1.0
    k0 = turn_sign * (abs(free["curvature"]) if free else 1e-3)
    sol = least_squares(residual, np.array([k0]))
    k = sol.x[0] if abs(sol.x[0]) > 1e-9 else 1e-9

    C, r = p0 + n0 / k, abs(1.0 / k)
    theta_s = np.arctan2(p0[1] - C[1], p0[0] - C[0])
    theta_e = np.arctan2(points[-1][1] - C[1], points[-1][0] - C[0])
    dtheta = _wrap_angle(theta_e - theta_s)
    end_pt = C + r * np.array([np.cos(theta_s + dtheta), np.sin(theta_s + dtheta)])
    res = residual([k])
    return {"kind": "arc", "start_pt": p0, "end_pt": end_pt,
            "h_start": h0, "h_end": _wrap_angle(h0 + dtheta),
            "curvature": float(k), "length": float(abs(dtheta) * r),
            "rms": float(np.sqrt(np.mean(res ** 2))), "max": float(np.max(np.abs(res)))}


def fit_reference_line_chained(centerline, epsilon=0.15):
    breakpoints = simplify_polyline(centerline, epsilon)
    segments, p0, h0 = [], None, None
    for a, b in zip(breakpoints[:-1], breakpoints[1:]):
        chunk = centerline[a:b + 1]
        if len(chunk) < 3:
            continue
        if p0 is None:                            # 첫 구간만 자유 피팅
            line_seg, arc_seg = fit_line_free(chunk), fit_arc_free(chunk)
        else:
            line_seg, arc_seg = fit_line_chained(chunk, p0, h0), fit_arc_chained(chunk, p0, h0)
        seg = line_seg if line_seg["rms"] <= arc_seg["rms"] else arc_seg
        segments.append(seg)
        p0, h0 = seg["end_pt"], seg["h_end"]
    return segments


# ---- 19단계: 각 원본 점에 대응하는 피팅 곡률 조회 ----

def fitted_kappa_at_points(params, n_segs, query_points):
    """전역 G1 체인을 샘플링하고, 각 query point에서 가장 가까운 샘플의 세그먼트 κ."""
    x, y, h = params[0], params[1], params[2]
    kappas, lengths = params[3:3 + n_segs], params[3 + n_segs:]
    samples, sample_kappa = [], []
    for k, L in zip(kappas, lengths):
        n = max(int(np.ceil(L / 0.1)), 2)
        s = np.linspace(0, L, n + 1)[1:]
        if abs(k) < 1e-9:
            xs, ys = x + s * np.cos(h), y + s * np.sin(h)
        else:
            xs = x + (np.sin(h + k * s) - np.sin(h)) / k
            ys = y - (np.cos(h + k * s) - np.cos(h)) / k
            h = h + k * L
        x, y = xs[-1], ys[-1]
        samples.append(np.stack([xs, ys], axis=1))
        sample_kappa.append(np.full(len(s), k))
    samples = np.concatenate(samples, axis=0)
    sample_kappa = np.concatenate(sample_kappa)
    d = np.linalg.norm(query_points[:, None, :] - samples[None, :, :], axis=2)
    return sample_kappa[np.argmin(d, axis=1)]


# ---- 21단계: 차선 폭 다항식 + <lanes> 직렬화 ----

def fit_width_poly(centerline, left_r, right_r):
    """s(중심선 호길이)에 대한 전체 폭 w(s)의 3차 다항식 계수 (a, b, c, d)."""
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(centerline, axis=0), axis=1))])
    w = np.linalg.norm(left_r - right_r, axis=1)
    coeffs = np.polyfit(s, w, 3 if len(s) >= 4 else 1)[::-1]   # 낮은 차수부터
    out = np.zeros(4)
    out[:len(coeffs)] = coeffs
    return out

# road_xml의 <lanes> 부분 (본문에서 생략한 부분). 좌/우 각각 폭 w(s)/2:
#   <lanes><laneSection s="0.0">
#     <left><lane id="1" type="driving"><width sOffset="0.0" a b c d/></lane></left>
#     <center><lane id="0" type="none"/></center>
#     <right><lane id="-1" type="driving"><width sOffset="0.0" a b c d/></lane></right>
#   </laneSection></lanes>


# ---- 21단계: 라운드트립 매칭 루프 (rt_venv에서 실행) ----

def roundtrip_compare(originals, lanelets):
    """originals: {road_id: 원본 중심선}, lanelets: 변환되어 돌아온 commonroad lanelet들.
    각 원본 중심선과 가장 가까운 left boundary(=lane -1의 왼쪽 = 참조선)를 찾아 거리 측정."""
    left_bounds = [np.asarray(l.left_vertices) for l in lanelets]
    e2e_max, e2e_mean = [], []
    for key, centerline in originals.items():
        best_d, best = None, None
        for lb in left_bounds:
            # 빠른 필터: 중간점 기준 3m 밖이면 후보에서 제외
            if np.min(np.linalg.norm(lb - centerline[len(centerline) // 2], axis=1)) > 3.0:
                continue
            d = point_to_polyline_dist(centerline, lb)
            if best_d is None or d.mean() < best_d:
                best_d, best = d.mean(), d
        if best is not None:
            e2e_max.append(best.max())
            e2e_mean.append(best.mean())
    return np.array(e2e_max), np.array(e2e_mean)
```

라운드트립 환경(macOS)은 버전 조합이 까다로워 그대로 적어둡니다.

```bash
python3 -m venv rt_venv     # python 3.9
./rt_venv/bin/pip install "numpy<2" opendrive2lanelet "commonroad-io==2020.2"
```

### 22단계: 고도 피팅 + 두 번째 맵 재현성 검증 (`spike_elevation.py`)

18~21단계와 동일한 `spike_fit.py`(단, `OSM_PATH`를 이 맵으로 교체) 위에서 돌립니다. `fit_elevation_cubic`은 본문(22-1단계)에 실었고, 여기서는 ele를 포함한 로더와 3D 중심선 구성만 싣습니다.

```python
def load_osm_with_ele(path):
    tree = ET.parse(path)
    root = tree.getroot()

    nodes, ele = {}, {}
    for n in root.findall("node"):
        nid = n.get("id")
        nodes[nid] = (float(n.get("lat")), float(n.get("lon")))
        for t in n.findall("tag"):
            if t.get("k") == "ele":
                ele[nid] = float(t.get("v"))

    ways = {w.get("id"): [nd.get("ref") for nd in w.findall("nd")] for w in root.findall("way")}

    lanelets = []
    for rel in root.findall("relation"):
        tags = {t.get("k"): t.get("v") for t in rel.findall("tag")}
        if tags.get("type") != "lanelet":
            continue
        left_way = right_way = None
        for m in rel.findall("member"):
            if m.get("role") == "left":
                left_way = m.get("ref")
            elif m.get("role") == "right":
                right_way = m.get("ref")
        if left_way and right_way:
            lanelets.append({"id": rel.get("id"), "left": left_way, "right": right_way,
                              "subtype": tags.get("subtype")})
    return nodes, ele, ways, lanelets


def way_points_z(ways, xy, ele, way_id):
    """way의 (x, y, z) 폴리라인. ele가 없는 노드는 이웃 값으로 선형 보간한다."""
    ids = ways[way_id]
    pts = np.array([xy[n] for n in ids])
    z = np.array([ele.get(n, np.nan) for n in ids])
    if np.isnan(z).any():
        valid = ~np.isnan(z)
        idx = np.arange(len(z))
        z[~valid] = np.interp(idx[~valid], idx[valid], z[valid])
    return pts, z


def resample_xyz_to_common_length(a_xy, a_z, b_xy, b_z, n=30):
    """resample_to_common_length과 동일한 감김 정렬 + 호길이 재샘플링을 z까지 확장."""
    if np.linalg.norm(a_xy[0] - b_xy[-1]) < np.linalg.norm(a_xy[0] - b_xy[0]):
        b_xy, b_z = b_xy[::-1], b_z[::-1]

    def resample(pts, z, n):
        s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
        query = np.linspace(0, s[-1], n)
        return (np.stack([np.interp(query, s, pts[:, 0]), np.interp(query, s, pts[:, 1])], axis=1),
                np.interp(query, s, z))

    a_r, az_r = resample(a_xy, a_z, n)
    b_r, bz_r = resample(b_xy, b_z, n)
    return a_r, az_r, b_r, bz_r


def iter_road_centerlines_3d(n_resample=30, min_length=1.0):
    nodes, ele, ways, lanelets = load_osm_with_ele(OSM_PATH)
    ref_lat, ref_lon = next(iter(nodes.values()))
    xy = latlon_to_local_xy(nodes, ref_lat, ref_lon)
    for ll in lanelets:
        if ll["subtype"] != "road":
            continue
        try:
            left_xy, left_z = way_points_z(ways, xy, ele, ll["left"])
            right_xy, right_z = way_points_z(ways, xy, ele, ll["right"])
        except KeyError:
            continue
        if len(left_xy) < 3 or len(right_xy) < 3:
            continue
        left_r, leftz_r, right_r, rightz_r = resample_xyz_to_common_length(
            left_xy, left_z, right_xy, right_z, n=n_resample
        )
        centerline = (left_r + right_r) / 2
        centerline_z = (leftz_r + rightz_r) / 2
        if np.sum(np.linalg.norm(np.diff(centerline, axis=0), axis=1)) < min_length:
            continue
        yield ll, centerline, centerline_z
```

### 23단계: 법선 투영(수정판) 기준 재실측 (`spike_recenter_bounded.py`)

`normal_projection_centerline_bounded`는 본문(23-1단계)에 실었습니다. `ray_polyline_intersection`은 20단계 코드와 동일합니다. 나머지는 두 맵을 순회하며 평균 중심선 vs 법선투영 중심선의 잔차를 나란히 내는 실행부입니다.

```python
def iter_road_centerlines_both(osm_path, n_resample=30, min_length=1.0):
    nodes, ways, lanelets = load_osm(osm_path)
    ref_lat, ref_lon = next(iter(nodes.values()))
    xy = latlon_to_local_xy(nodes, ref_lat, ref_lon)
    for ll in lanelets:
        if ll["subtype"] != "road":
            continue
        try:
            left = way_points(ways, xy, ll["left"])
            right = way_points(ways, xy, ll["right"])
        except KeyError:
            continue
        if len(left) < 3 or len(right) < 3:
            continue
        left_r, right_r = resample_to_common_length(left, right, n=n_resample)
        cl_avg = (left_r + right_r) / 2
        if polyline_length(cl_avg) < min_length:
            continue
        cl_bounded = normal_projection_centerline_bounded(cl_avg, left_r, right_r)
        yield ll, cl_avg, cl_bounded, left_r, right_r


def run_map(osm_path, label):
    rows = []
    for ll, cl_avg, cl_bnd, left_r, right_r in iter_road_centerlines_both(osm_path):
        _, sa = fit_reference_line_independent(cl_avg)
        _, sb = fit_reference_line_independent(cl_bnd)
        _, na, ga = fit_reference_line_global(cl_avg)   # 18단계 전역 G1
        _, nb, gb = fit_reference_line_global(cl_bnd)
        if ga is None or gb is None:
            continue
        rows.append({"indep_avg": sa["fit_residual_max_m"], "indep_bnd": sb["fit_residual_max_m"],
                      "global_avg": ga["fit_residual_max_m"], "global_bnd": gb["fit_residual_max_m"]})
    # ... mean/p95/max 집계는 이전 단계들과 동일한 패턴 (본문 표 참고)
```

### 25단계: 클로소이드 도입 판단 (`spike_clothoid_decision.py`)

`spiral_sample`은 본문에 실었습니다. 나머지는 24단계 결과에서 곡률 계단을 뽑아 횡가속도로 환산하는 부분과, 최악 이음새를 찾아 삽입 데모를 돌리는 실행부입니다.

```python
def curvature_steps_of(params, n_segs):
    kappas = params[3:3 + n_segs]
    return np.abs(np.diff(kappas))


def insert_spiral_at_worst_joint(left, right, spiral_len=3.0, n_per_seg=20):
    """가장 곡률 계단이 큰 이음새를 찾아, 그 사이에 길이 spiral_len짜리
    클로소이드를 끼워넣고 나머지 구조는 그대로 유지한 채 위치 잔차를 잰다."""
    params, n_segs, stats = fit_reference_line_boundary_symmetric(left, right)  # 24단계
    if stats is None or n_segs < 2:
        return None

    steps = curvature_steps_of(params, n_segs)
    worst_i = int(np.argmax(steps))

    x, y, h = params[0], params[1], params[2]
    kappas = params[3:3 + n_segs]
    lengths = params[3 + n_segs:3 + 2 * n_segs]
    for k, L in zip(kappas[:worst_i + 1], lengths[:worst_i + 1]):   # 이음새 지점까지 원래 체인을 따라간다
        if abs(k) < 1e-9:
            x, y = x + L * np.cos(h), y + L * np.sin(h)
        else:
            x = x + (np.sin(h + k * L) - np.sin(h)) / k
            y = y - (np.cos(h + k * L) - np.cos(h)) / k
            h = h + k * L

    k_before, k_after = kappas[worst_i], kappas[worst_i + 1]
    s_q = np.linspace(0, spiral_len, n_per_seg)
    xs, ys, h_end = spiral_sample(x, y, h, k_before, k_after, spiral_len, s_q)
    spiral_pts = np.stack([xs, ys], axis=1)
    d_left_s = point_to_polyline_dist(spiral_pts, left)
    d_right_s = point_to_polyline_dist(spiral_pts, right)
    return {
        "worst_step_1pm": float(steps[worst_i]),
        "spiral_sym_residual": float(np.abs(d_left_s - d_right_s).max()),
    }


# 속도별 횡가속도 점프 환산 (본문 표를 만든 핵심 계산)
TEST_SPEEDS_MS = [5.0, 8.0, 13.9]  # 18/29/50km/h
for v in TEST_SPEEDS_MS:
    da = curvature_steps * v * v          # Δa = v² · Δκ
    frac_over_2 = np.mean(da > 2.0)       # 급조향 승차감 한계 대비 비율
    frac_over_4 = np.mean(da > 4.0)
```

### 27단계: 클로소이드 전환 길이 자유화 + jerk 일반화 검증 (`spike_clothoid_free_length.py`)

`optimal_spiral_length`은 본문에 실었습니다. 나머지는 25단계 결과에서 최악 이음새의 pose를 복원하는 부분과, 여러 lanelet에 걸쳐 고정 L 대 자유 L을 일괄 비교하는 실행부입니다.

```python
def worst_joint_pose_and_kappas(left, right):
    """24단계 피팅 결과에서 최악 곡률 계단 이음새의 pose(x,y,h)와 (k_before, k_after)를 구한다."""
    params, n_segs, stats = fit_reference_line_boundary_symmetric(left, right)
    if stats is None or n_segs < 2:
        return None
    steps = curvature_steps_of(params, n_segs)   # 25단계
    worst_i = int(np.argmax(steps))

    x, y, h = params[0], params[1], params[2]
    kappas = params[3:3 + n_segs]
    lengths = params[3 + n_segs:3 + 2 * n_segs]
    for k, L in zip(kappas[:worst_i + 1], lengths[:worst_i + 1]):
        if abs(k) < 1e-9:
            x, y = x + L * np.cos(h), y + L * np.sin(h)
        else:
            x = x + (np.sin(h + k * L) - np.sin(h)) / k
            y = y - (np.cos(h + k * L) - np.cos(h)) / k
            h = h + k * L
    return x, y, h, float(kappas[worst_i]), float(kappas[worst_i + 1]), float(steps[worst_i])


def scan_generalization(osm_path, label, n_lanelets=15):
    """최악이 아니라, 곡률 계단이 있는 여러 lanelet에 일반적으로 통하는지 확인."""
    cases = []
    for ll in lanelets:  # subtype=road, 곡률 계단 >= 0.05 [1/m]인 lanelet만
        result = worst_joint_pose_and_kappas(left_r, right_r)
        x, y, h, k0, k1, step = result

        s_q = np.linspace(0, 3.0, 30)                        # 고정 L=3m (25단계 재현)
        xs, ys, _ = spiral_sample(x, y, h, k0, k1, 3.0, s_q)
        pts = np.stack([xs, ys], axis=1)
        fixed_res = np.abs(point_to_polyline_dist(pts, left_r)
                            - point_to_polyline_dist(pts, right_r)).max()

        L_opt = optimal_spiral_length(x, y, h, k0, k1, left_r, right_r)  # 자유 L
        cases.append({"step": step, "fixed_res": fixed_res, "L_opt": L_opt})
        if len(cases) >= n_lanelets:
            break
    # ... mean/p95/max 집계, jerk = v^3 * step / L_opt 계산은 본문 표 참고
```

---

## 지금까지 정한 것, 아직 정하지 않은 것

**정한 것** — 27단계를 설계 결정만 남기고 추리면 다음과 같습니다. (각 결정의 근거와 실측 수치는 해당 단계 참고.)

- **방향**: Lanelet2 → OpenDRIVE 변환 도구는 생태계에 사실상 없어서 직접 만듭니다. 대신 성숙한 반대 방향 도구(opendrive2lanelet)는 라운드트립 검증에 재활용합니다(1단계).
- **IR**: OpenDRIVE 모델(참조선 + 파라메트릭 단면)을 뼈대로 삼아, 어려운 문제(곡선 피팅)를 Lanelet2 → IR 한쪽 방향에 몰아넣습니다. 지리/토폴로지 정보와 프로버넌스(변환 근거·지표)를 분리해 설계합니다(2~3단계).
- **정확도**: 위치 잔차(point-to-curve)에 허용치를 두되, 곡률 오차와 이음새 연속성을 별도 지표로 둡니다. 곡선 타입은 Line+Arc부터 시작해 필요한 만큼만 확장합니다(4단계). 샘플 맵 기준 독립 피팅 잔차 mean 2~3cm, 최악 14.6cm — 감김 방향 버그(14단계)와 대표 lanelet 선택 버그(17단계)를 잡은 뒤의 수치입니다.
- **피팅 방식(B) 확정 — 전역 G1**: 독립 피팅은 이음새 헤딩 꺾임이 평균 8.8°(최대 43°)에 달해 그대로 쓸 수 없고, 탐욕 체인 피팅은 헤딩 오차 전파로 잔차가 폭발합니다(최악 1.4m). 참조선 체인 전체를 OpenDRIVE 네이티브 파라미터화(시작 pose + 세그먼트별 κ·L)로 놓는 전역 최적화로 확정 — 이음새 정확히 0, 잔차 mean 5.6cm/최악 21cm(18단계). 곡률 오차도 처음 실측했고, 기준 정의(스무딩)가 지표의 일부여야 한다는 것을 확인했습니다(19단계).
- **검증 회로 완성**: 실제 `.xodr`을 익스포트해 TUM opendrive2lanelet으로 되돌리는 라운드트립을 돌렸습니다 — end-to-end 오차가 피팅 잔차와 사실상 동일(직렬화+파싱 오차 mm 수준), 101개 Road 전부 매칭(21단계).
- **고도 피팅 첫 실측 + 두 번째 맵 검증**: 실제 `ele` 태그가 있는 다른 맵(Autoware 샘플맵)으로 `elevation_profile`을 처음 피팅했습니다 — 경사가 완만해(대부분 1% 이내) lanelet당 3차 다항식 하나로 충분했습니다(잔차 mean 1.0cm). 같은 맵에 18·20단계를 재실행해, "Line+Arc로 충분하다"는 결론은 더 강하게 재현됐지만, pairing 편향의 "지배 요인"(20단계는 경계 길이 불일치, 이 맵은 곡률)은 재현되지 않았습니다 — 맵마다 다르다는 것 자체가 새로운 결론입니다(22단계).
- **중심선 "선-보정 후 피팅" 접근은 기각, "경계 직접 대칭 피팅"으로 확정**: pairing 편향을 없애려고 법선 투영 중심선을 실제로 파이프라인에 꽂아봤습니다. 도중에 거리 상한 없는 구현이 14.6m짜리 중심선 이탈을 내는 견고성 결함을 발견해 고쳤지만(23단계), 고친 뒤에도 노이즈 있는 맵(Karlsruhe)에서는 잔차가 오히려 나빠졌습니다(전역 G1 max +4.0cm, 곡률 오차 약 3배) — "중심선을 미리 보정하고 그 위에 참조선을 피팅"하는 2단계 구조 자체를 기각했습니다. 대신 중심선이라는 중간 산출물 없이 참조선을 좌/우 경계에 직접 대칭 피팅(`|d_left - d_right|` 최소화)했더니 이번엔 통했습니다 — Karlsruhe 대칭 잔차 mean 30cm→6.6cm, 최악 132cm→40cm, 원래 깨끗했던 Autoware는 퇴보 없이 유지(1.4cm→1.5cm). 발견된 이상치 2건도 조사해보니 새 방법의 결함이 아니라 옛 평균 중심선 정의 자체의 결함이 드러난 것으로 확인됐습니다(24단계). **20단계 이래 흔들리던 "도로 중심선" 정의가 이 시점에서 확정됐습니다.**
- **검증 역할 분담**: 정밀 수치는 결정적 코드가 계산하고, LLM은 지표·시각화를 검토하는 리뷰어로 한정합니다(5단계). 이 원칙이 실제로 작동한다는 것도 확인했습니다 — 정량 지표로는 절대 못 잡는 렌더링 버그 2개를 시각 검토로 잡았습니다(15단계).
- **그룹핑(A)**: node id 매칭 휴리스틱은 실측으로 한계를 확인했고(8~9단계), 공식 `RoutingGraph`를 쓰되 "합법적 차량 경로"가 아니라 "물리적 도로 연결성" 기준(Vehicle/Bicycle/Pedestrian 합집합)으로 재구현했습니다(10, 13단계). 그래도 남는 고립 조각은 알고리즘으로 완벽히 풀기보다 `topology_warnings`로 사람/LLM 검토에 넘깁니다.
- **규제 정보**: `Signal`(정지선 s + 적용 차선), `road_mark`(경계 태그 매핑 — 샘플 맵 100% 성공), `elevation_profile`(z(s))을 IR에 추가했고, 통합 파이프라인에서 Signal 위치 계산 10/10을 확인했습니다(11~12, 14, 16~17단계).
- **클로소이드 필요성 확정, "7단계 결론" 수정**: 곡률 계단을 횡가속도 점프(Δa=v²Δκ)로 환산해보니, 도심 속도(18km/h)에서도 이음새의 48%가 승차감 한계(2 m/s²)를 넘고 시속 50km에서는 80%가 급조향 수준(4 m/s²)을 넘습니다. 위치 잔차만 보고 "Line+Arc로 충분하다"던 7단계 결론을 사실상 뒤집는 결과라, 클로소이드 도입이 필요하다고 판단했습니다. 다만 전환 길이를 고정값(3m)으로 넣어봤더니 최악 케이스에서 잔차가 0.03m→1.23m로 폭발해, 전환 길이 자체도 자유 변수로 최적화해야 한다는 게 다음 과제로 남았습니다(25단계).
- **`superelevation`(횡단 경사) 추가**: 22단계 고도 피팅 인프라를 재사용해 `cross_slope(s) = (z_left - z_right) / w(s)`를 처음 측정했습니다 — Autoware 샘플맵 기준 lanelet당 최대 횡단 경사 mean 2.5%, 최악 4.6%, **lanelet의 87.7%가 실제 도로 설계 슈퍼일리베이션 범위(2~8%)에 들어갔습니다.** `elevation_profile`과 같은 3차 다항식으로 잘 피팅되고(잔차 mean 0.47%), IR에 `Road.superelevation` 필드로 추가했습니다(26단계).
- **클로소이드 전환 길이 "잔차 최소화"는 틀린 목적함수였다**: 25단계의 고정 길이(3m) 삽입 실패를 고쳐보려고 전환 길이를 자유 변수로 최적화했더니, 대칭 잔차는 확실히 잡혔습니다(최악 케이스 1.23m→0.014m, 두 맵 30개 표본에서 자유 L이 고정 L보다 나쁜 경우 0건). 하지만 최적 길이가 평균 0.28m로 지나치게 짧아서 jerk(횡가속도 변화율)로 환산해보니 **30개 표본 전부가 편안한 승차감 한계(4 m/s³)를 벗어났습니다**(v=8m/s 기준 mean 450~715 m/s³) — 경계에 딱 맞는 최단 경로를 찾는 것과 곡률을 부드럽게 바꾸는 것은 서로 경쟁하는 목적함수였습니다. 사후 패치가 아니라 24단계 전역 최적화 자체에 jerk 페널티를 넣어야 한다는 게 새 결론입니다(27단계).

**아직 정하지 않은 것 / 남은 작업**

- **곡률 변화율(jerk) 페널티를 전역 최적화에 직접 넣기** — 27단계에서 사후 패치(전환 길이만 최적화) 방식이 잔차와 승차감을 동시에 만족시킬 수 없다는 게 확인됐습니다. 24단계 피팅 목적함수 자체를 다시 설계하는 게 최우선 과제입니다('남은 빈틈' 1번).
- **Junction 생성**(connecting road 지오메트리 + `laneLink`) — 여전히 미착수. A(그룹핑)로 Road 체인을 만드는 게 선행 조건이고, **고도 이음새**(lanelet 간 경사 불연속, 26단계는 lanelet 단위로만 재서 미측정)도 여기 얹을 수 있습니다('남은 빈틈' 2번).
- **esmini/CARLA 실기 로딩 + 라운드트립 재검증** — opendrive2lanelet 파싱은 통과했지만(21단계) 시뮬레이터 로딩은 미확인이고, 21단계의 xodr 익스포트도 24단계 새 중심선과 26단계 superelevation을 반영해 다시 만들어 재검증해야 합니다('남은 빈틈' 3번).
- **회사 실측 맵 검증** — 두 공개 맵에서도 pairing 편향의 지배 요인이 갈렸던 만큼(20·22·23단계), 회사 맵은 세 번째 데이터 포인트로서 더 중요해졌습니다. 24~27단계 결론이 회사 맵에서도 유지되는지가 특히 중요합니다('남은 빈틈' 4번).
- 회귀 테스트에서 실제로 감내 가능한 위치/곡률 오차 허용치의 수치 확정 — 이제 중심선 기준이 확정됐으니, 24단계 수치(대칭 잔차 mean 1.5~6.6cm)와 25·27단계의 횡가속도/jerk 수치를 3DGS 씬 정합 오차 허용 범위와 대조해봐야 합니다.
- `call_llm_review`를 실제 LLM으로 돌려서 사람이 직접 본 판단과 일치하는지 확인하는 건 지금 범위에서 제외합니다 — 사내 GPU에 vLLM을 띄운 뒤에 그쪽 환경에서 진행할 계획입니다.

다음 글에서는 '남은 빈틈'의 1번(전역 최적화에 jerk 페널티 통합)과 2번(A(그룹핑) 기반 Junction 생성 스파이크)을 다룰 예정입니다.

---

*관련 글: [OpenDRIVE vs Lanelet2 비교](../opendrive-vs-lanelet2/), [Lanelet2 입문](../lanelet2-for-beginners/), [OpenDRIVE 입문](../opendrive-for-beginners/)*
