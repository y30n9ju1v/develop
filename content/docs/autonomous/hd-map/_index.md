---
title: "HD 맵과 시뮬레이션"
---

HD 맵 포맷(Lanelet2, OpenDRIVE)과 자율주행 시뮬레이션 시나리오(OpenSCENARIO)를 다룹니다.

1. **[Lanelet2 입문](lanelet2-for-beginners/)** — HD 맵의 기본 구조(Point, LineString, Lanelet, RegulatoryElement)를 이해합니다.
2. **[OpenDRIVE 입문](opendrive-for-beginners/)** — 시뮬레이터용 도로 포맷 OpenDRIVE의 구조(Road, Lane, planView, Junction)를 이해합니다.
3. **[OpenDRIVE vs Lanelet2 비교](opendrive-vs-lanelet2/)** — 두 포맷의 설계 철학, 강점, 사용처를 나란히 비교하고 선택 기준을 정리합니다.
4. **[OpenSCENARIO 입문](openscenario-for-beginners/)** — 자율주행 테스트 시나리오를 표준 XML로 기술하는 OpenSCENARIO의 구조와 사용법을 익힙니다.
5. **[Lanelet2 맵을 카메라 이미지에 투영하기](lanelet2-projection-to-image/)** — World → Ego → Camera 변환을 총동원해 HD 맵 차선을 카메라 이미지에 그립니다.
6. **[OpenSCENARIO 2.0 입문](openscenario-2-for-beginners/)** — XML 대신 텍스트 DSL로 시나리오를 기술하는 OSC2의 문법과, 파라미터 공간을 통한 대규모 회귀 테스트 시나리오 생성 방법을 정리합니다.
7. **[Lanelet2 → OpenDRIVE 변환기 설계하기](lanelet2-to-opendrive-ir-design/)** — 실차용 Lanelet2 맵을 시뮬레이션용 OpenDRIVE로 바꾸기 위한 중간 표현(IR)을 설계하고, LLM을 변환 검증에 활용하는 파이프라인을 단계별로 정리합니다.
