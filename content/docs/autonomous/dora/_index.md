---
title: "DORA 프레임워크"
---

ROS2보다 10~17배 빠른 Rust 기반 로보틱스 프레임워크 DORA를 다룹니다.

1. **[DORA 입문: 설계 철학과 아키텍처](dora-rs-for-beginners/)** — DORA가 왜 만들어졌는지, DDS 대신 Zenoh를 쓴 이유, Rust를 선택한 이유, Coordinator·Daemon·Runtime·Node 4계층 아키텍처를 정리합니다.
2. **[DORA 파이프라인 설계: 데이터플로우와 통신 패턴](dora-rs-dataflow-yaml/)** — 선언형 YAML 파이프라인 개념, 타이머·큐·재시작 정책, 모듈·동적 토폴로지, Topic·Service·Action·Streaming 네 가지 통신 패턴을 정리합니다.
3. **[DORA로 자율주행 E2E 회귀 테스트 구성하기](dora-rs-av-regression-testing/)** — 시나리오 재생부터 지표 수집, ML 비결정성 처리, CI 통합까지 자율주행 스택 회귀 테스트 파이프라인을 구성하는 방법을 정리합니다.
4. **[CARLA 시뮬레이터와 DORA 연동하기](dora-rs-simulator-integration/)** — 센서 데이터 Arrow 포맷 변환, 제어 명령 피드백, 틱 동기화, 도메인 갭까지 클로즈 루프 시뮬레이션 연동 방법을 정리합니다.
