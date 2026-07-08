---
title: "자율주행"
---

자율주행 시뮬레이션, HD 맵, 센서 인지에 관한 입문 시리즈입니다.

## 시리즈 읽는 순서

### HD 맵과 시뮬레이션

1. **[Lanelet2 입문](lanelet2-for-beginners/)** — HD 맵이 무엇인지, Lanelet2의 기본 구조(Point, LineString, Lanelet, RegulatoryElement)를 이해합니다.
2. **[OpenDRIVE 입문](opendrive-for-beginners/)** — 시뮬레이터용 도로 포맷 OpenDRIVE의 구조(Road, Lane, planView, Junction)를 이해합니다.
3. **[OpenDRIVE vs Lanelet2 비교](opendrive-vs-lanelet2/)** — 두 포맷의 설계 철학, 강점, 사용처를 나란히 비교하고 선택 기준을 정리합니다.
4. **[OpenSCENARIO 입문](openscenario-for-beginners/)** — 자율주행 테스트 시나리오를 표준 XML로 기술하는 OpenSCENARIO의 구조와 사용법을 익힙니다.

### 센서와 좌표 변환

5. **[카메라 모델 입문](camera-models-for-beginners/)** — 핀홀·피쉬아이 카메라 모델의 원리, 렌즈 왜곡, 왜곡 보정을 다룹니다.
6. **[좌표계 입문](ego-coordinate-system-for-beginners/)** — Ego, World, Sensor 좌표계의 개념과 변환 행렬 사용법을 다룹니다.
7. **[LiDAR 포인트 클라우드 입문](lidar-point-cloud-for-beginners/)** — 포인트 클라우드 데이터 구조, Voxel Grid, 날씨 취약성 등 LiDAR 실무 지식을 다룹니다.

### 센서 퓨전 실습

8. **[Lanelet2 맵을 카메라 이미지에 투영하기](lanelet2-projection-to-image/)** — World → Ego → Camera 변환을 총동원해 HD 맵 차선을 카메라 이미지에 그립니다.
9. **[센서 퓨전 기초: LiDAR 포인트를 카메라 이미지에 투영하기](lidar-to-camera-projection/)** — LiDAR 포인트 클라우드를 카메라 이미지 위에 겹치고 거리에 따라 색상을 칠하는 실습입니다.

### 프레임워크

10. **[DORA 입문](dora-rs-for-beginners/)** — ROS2보다 10~17배 빠른 Rust 기반 로보틱스 프레임워크 DORA의 구조와 특징을 소개합니다.
11. **[DORA 아키텍처](dora-rs-architecture/)** — Coordinator·Daemon·Runtime·Node 4계층 구조와 컴포넌트 간 통신 흐름을 정리합니다.
12. **[DORA 데이터플로우 YAML 작성법](dora-rs-dataflow-yaml/)** — 파이프라인 YAML 문법, 타이머·로그·오퍼레이터·분산 배포·ROS2 브리지까지 예제 중심으로 정리합니다.
13. **[DORA 타입 시스템](dora-rs-types/)** — 타입 URN 체계, 내장 타입 카탈로그, 호환성 규칙, 정적/런타임 검증 방법을 정리합니다.
14. **[DORA 모듈](dora-rs-modules/)** — 노드 서브그래프를 재사용 가능한 단위로 묶는 모듈의 정의, 파라미터, 중첩 방법을 정리합니다.
15. **[DORA 통신 패턴](dora-rs-patterns/)** — Topic, Service, Action, Streaming 네 가지 패턴의 동작 방식과 메타데이터 규약을 정리합니다.

### 데이터 인프라

16. **[파편화된 자율주행 데이터를 하나로: py123d + FiftyOne + Rerun](autonomous-data-pipeline/)** — 파편화된 자율주행 데이터셋을 py123d로 표준화하고, FiftyOne으로 큐레이션하고, Rerun으로 시각화하는 모던 파이프라인을 소개합니다.
