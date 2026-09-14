---
title: "Lanelet2 → OpenDRIVE 변환 파이프라인: 기준선·IR·검수"
date: 2026-07-18T00:00:00+09:00
draft: true
tags: ["자율주행", "HD맵", "OpenDRIVE", "Lanelet2", "IR", "지도검수", "회귀테스트"]
categories: ["autonomous"]
description: "Tier IV 기준 변환기를 출발점으로 Lanelet2 맵을 OpenDRIVE로 변환하고, IR·결정적 품질 게이트·웹 검토로 결과를 승인하는 운영 설계입니다."
---

## 목표와 원칙

Lanelet2는 실차 자율주행 스택에서 쓰기 좋고, OpenDRIVE는 CARLA 같은 시뮬레이터와 도로 기하 도구가 이해하기 좋습니다. 이 글의 목표는 두 포맷의 완벽한 상호변환이 아닙니다. **클로즈드 루프 회귀 테스트에 투입할 수 있는, 추적 가능하고 검수 가능한 OpenDRIVE 결과**를 만드는 것입니다.

핵심 원칙은 세 가지입니다.

1. 직접 변환기를 새로 쓰기 전에 검증된 변환기를 기준선으로 측정합니다.
2. 정확도·위상·규제 정보의 합격 여부는 결정적 코드가 판단합니다.
3. 사람·카메라 기반 모델·웹 뷰어는 애매한 블록을 검토하는 데 쓰며, 자동 승인 권한은 갖지 않습니다.

3D Gaussian Splatting(3DGS) 기반 회귀 테스트를 쓴다면 이 원칙은 더 중요합니다. 3DGS 씬과 OpenDRIVE 도로 모델이 서로 다른 좌표계나 형상을 가리키면, 인지는 현실적인 화면을 보고 플래닝과 제어는 틀린 도로를 참조하는 모순이 생깁니다.

## 가장 먼저 실행할 기준선

현재 기준선은 Tier IV의 Lanelet2 → OpenDRIVE 변환기입니다. Lanelet2 `.osm`을 OpenDRIVE 1.4 `.xodr`로 변환하고, 원본 Lanelet2 요소와 생성 road/lane의 대응 JSON, ASAM QC, 기하 분석 경로를 제공합니다.

저장소의 `tools/hd-map/run-lanelet2-opendrive-baseline.sh`는 이 기준선을 한 번에 실행합니다.

```bash
bash tools/hd-map/run-lanelet2-opendrive-baseline.sh path/to/map.osm
```

기본 출력 위치는 `artifacts/lanelet2-opendrive-baseline/`입니다.

| 산출물 | 용도 |
| --- | --- |
| `<map>.xodr` | 목표 OpenDRIVE 1.4 파일 |
| `<map>_mapping.json` | 원본 Lanelet2와 OpenDRIVE road/lane의 대응 |
| `<map>_qc.xqar` | ASAM QC 결과 |
| `<map>_analysis.xqar` | 원본과 결과의 기하 교차 검증 |
| 원본 `.osm`의 SHA-256·Tier IV 커밋 | 실행 재현과 결과 추적 |

Apple Silicon에서는 Tier IV가 포함한 CARLA wheel이 x86_64 전용이므로 스크립트가 x86_64 Linux 컨테이너를 사용합니다. 이 기준선은 CARLA/esmini 실기 로딩까지 실행하지 않습니다.

## 승인 파이프라인

```text
Lanelet2 .osm + CRS/원점/단위
        │
        ▼
Tier IV 기준 변환 ──────► .xodr + mapping.json
        │                         │
        ▼                         ▼
IR에 근거·보정 기록       QC / 파싱 / 기하 분석
        │                         │
        └──────────► 블록별 pass · warn · fail
                                  │
                    warn ───────► 웹 검토·IR 보정 패치
                                  │
                                  ▼
                         재변환·재검증·승인
```

변환기의 CLI 성공이나 XML 파싱 성공만으로 승인하지 않습니다. 실행마다 다음을 같은 `run_id`로 보관합니다.

- 입력 맵의 해시, CRS·원점·단위, 변환기 커밋·설정
- `.xodr`, mapping JSON, 전처리된 OSM이 있다면 그 파일
- QC, 파서, 시뮬레이터 로딩의 결과와 버전
- Road/Junction/tile별 기하·위상·규제 요소 보존 지표
- 원본·결과 오버레이와 사람이 남긴 보정 패치

## 품질 게이트

| 관문 | 결정적 검사 | 실패 시 처리 |
| --- | --- | --- |
| 구조 | XML 파싱, ASAM QC, OpenDRIVE 버전, CRS·단위 | `fail` |
| 위상 | lane 수, predecessor/successor, Junction laneLink, 고립 조각 | `fail` 또는 `warn` |
| 기하 | 위치 잔차, 곡률·이음새 연속성, 차선 폭, 라운드트립 거리 | 허용치 초과 시 `warn` |
| 규제 정보 | Signal 위치·validity, 정지선, 도로 마킹, 손실 속성 | 보존 불가 시 `warn` |
| 소비자 | esmini/CARLA 로딩과 최소 주행 시나리오 | `fail` |

`warn`은 통과가 아닙니다. 자동 승인을 멈추고, 해당 타일과 원본 ID를 웹 검토 큐로 보냅니다. 최종 허용치는 회귀 테스트가 감내할 위치 오차와 차량 거동 기준으로 정해야 하며, 공개 예제의 수치를 회사 맵의 승인 임계치로 재사용하지 않습니다.

## OpenDRIVE 지향 IR

IR은 Lanelet2의 점열을 복제하는 포맷이 아니라, OpenDRIVE로 내보낼 수 있는 도로 모델과 변환 근거를 함께 담는 계층입니다.

```text
Network
├── roads: reference line, elevation, superelevation, lane sections, links
├── junctions: connections, connecting roads, lane links
├── signals: road/s/t, validity, 원본 RegulatoryElement
└── provenance: 원본 ID, 지표, 손실, 보정, 승인 상태
```

중요한 규칙은 다음과 같습니다.

- `reference_line`은 평면 `(x, y)` 형상이고, `elevation_profile`은 별도 `z(s)`입니다.
- `superelevation`은 단순 횡단 기울기가 아니라 도로 좌표계의 roll angle(라디안)입니다. 경계 고도로 계산한 기울기는 부호 규약을 고정하고 `atan` 변환을 거쳐야 합니다.
- Signal은 Lanelet2의 RegulatoryElement 관계를 OpenDRIVE의 위치 `(road_id, s, t)`와 적용 범위(validity)로 분리합니다.
- 보정은 XODR XML을 직접 고치지 않고 IR 패치로 남깁니다. 그래야 재변환 때 근거와 수정 이력이 유지됩니다.

각 road에는 최소한 다음 provenance를 남깁니다.

```text
source_lanelet_ids, tile_id, fit method,
position/curvature/joint metrics,
lane-count check, dropped attributes,
topology warnings, deterministic gate,
vision findings (독립 카메라 관측이 있을 때만)
```

## 사람·딥러닝·LLM의 역할

정밀 수치와 차단 판정은 결정적 코드의 책임입니다. 같은 벡터 지도를 이미지로 다시 렌더링해 모델에 넣는 것은 독립 근거를 추가하지 않으므로 승인 근거로 쓰지 않습니다.

- **카메라 로그가 있을 때**: 원본/생성 지도를 실제 카메라 프레임에 투영해 차선, 정지선, 신호, 횡단보도 등의 불일치 위험을 요소별로 점수화합니다.
- **웹 검토**: 원본 경계·참조선·규제 정보·오차 지표를 한 타일에 겹쳐 사람이 검토합니다.
- **LLM**: 결정적 지표와 모델 소견을 읽기 쉬운 검토 사유로 요약할 수 있지만, 좌표 계산이나 승인·반려 판정은 맡지 않습니다.

현재 웹 뷰어와 스크린샷 생성은 스파이크로 확인됐지만, 실제 LLM 판정이 사람 판단과 얼마나 일치하는지는 아직 검증하지 않았습니다.

## 자체 익스포터를 쓸 조건

기본 경로는 다음입니다.

```text
Tier IV 변환 → IR에 매핑·품질 기록 → 필요한 블록만 보정·재생성
```

자체 피팅·익스포터는 다음 세 조건을 모두 만족할 때만 기준선을 대체합니다.

1. 기준선이 보존하지 못하는 요소 또는 오류가 실제 맵에서 발견됐습니다.
2. 그 오류가 결정적 지표와 목표 소비자(CARLA/esmini) 로딩에서 재현됩니다.
3. 자체 결과가 동일 입력·동일 OpenDRIVE 버전·동일 QC 조건에서 기준선보다 더 좋은 게이트 결과를 냅니다.

이 조건 전에는 자체 곡선 피팅, 클로소이드, Junction 생성 코드를 연구 자산으로 유지하되 운영 기본값으로 삼지 않습니다.

## 아직 승인되지 않은 항목

- 회사 실측 맵에서의 기준선 변환과 허용치 결정
- 최신 IR 보정 결과를 포함한 OpenDRIVE 라운드트립
- `superelevation` roll angle 직렬화와 검증
- Junction 그룹핑 오류와 laneLink의 자동 승인 기준
- esmini/CARLA의 실제 로딩·주행 검증
- 카메라 기반 위험 점수와 사람 판단의 일치도

첫 번째 실행은 회사 맵 하나를 기준선 스크립트에 통과시키는 일입니다. 그 결과의 `fail`과 `warn`만이 자체 IR 보정 또는 익스포터 확장이 필요한 구체적 근거가 됩니다.

## 실험 기록

참조선 피팅, 중심선 편향, 클로소이드, jerk, Junction 생성, 웹 뷰어를 탐색한 상세 실험과 실패 사례는 [Lanelet2 → OpenDRIVE 변환 스파이크 노트](../lanelet2-to-opendrive-spike-notes/)에 보존했습니다. 그 문서는 설계의 근거를 제공하지만, 현재 운영 절차의 승인 기준은 이 문서를 따릅니다.

---

*관련 글: [OpenDRIVE vs Lanelet2 비교](../opendrive-vs-lanelet2/), [Lanelet2 입문](../lanelet2-for-beginners/), [OpenDRIVE 입문](../opendrive-for-beginners/)*
