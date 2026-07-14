---
title: "자율주행"
---

자율주행 시뮬레이션, HD 맵, 센서 인지, 로보틱스 프레임워크, 데이터 인프라에 관한 시리즈입니다.

- **[HD 맵과 시뮬레이션](hd-map/)** — Lanelet2, OpenDRIVE, OpenSCENARIO 포맷과 카메라 투영 실습
- **[센서와 좌표 변환](sensor/)** — 카메라·LiDAR 모델, 좌표계, 센서 퓨전 실습
- **[DORA 프레임워크](dora/)** — Rust 기반 로보틱스 프레임워크 DORA 아키텍처·YAML·타입·모듈·패턴
- **[데이터 인프라](data-infra/)** — Apache Arrow, py123d + FiftyOne + Rerun 파이프라인, 클로즈 루프 회귀 테스트
- **[안전성 검증](safety-validation/)** — Sim-to-Real 검증 방법론, SOTIF(ISO 21448), Importance Sampling 기반 희귀 사건 통계적 검증
- **[시뮬레이션 오케스트레이션](simulation/)** — K8s/Ray/Slurm 기반 클라우드 대규모 시나리오 병렬 실행, CPU/GPU 혼합 배치 스케줄링
