---
title: "데이터 인프라"
---

자율주행 데이터 파이프라인의 기반 기술과 구축 방법을 다룹니다.

### 기초 개념

1. **[자율주행 스택 전체 구조: Perception → Prediction → Planning → Control](av-stack-overview/)** — 자율주행 소프트웨어가 어떤 모듈로 구성되고 어떻게 데이터가 흐르는지 — 이 시리즈 전체의 맥락이 되는 스택 구조를 정리합니다.
2. **[자율주행 좌표계 완전 정리: ISO 8855와 실무 변환](iso-8855-coordinate-systems/)** — ISO 8855, SAE J670, CARLA/UE4, ROS, OpenCV 카메라 좌표계 차이와 각 경계에서의 실무 변환을 정리합니다.
3. **[3D 변환의 언어: SE3와 쿼터니언](se3-transform-quaternion/)** — PoseSE3가 무엇인지, compose·inverse가 실제로 무슨 계산인지, SLERP 보간까지 직관적으로 정리합니다.
4. **[카메라 캘리브레이션: 내부 파라미터와 외부 파라미터](camera-calibration/)** — 핀홀 카메라 모델, fx/fy/cx/cy, SE3 외부 파라미터, FTheta까지 — py123d 파서와 NuRec 연동에서 등장하는 카메라 캘리브레이션 개념을 정리합니다.
5. **[LiDAR 포인트 클라우드: 구조, 포맷, 전처리](lidar-point-cloud/)** — LiDAR가 어떻게 동작하고, x/y/z/intensity 4열이 왜 기본 구조인지, LAZ와 Arrow IPC 중 언제 무엇을 쓰는지, 그리고 전처리 핵심 3가지를 정리합니다.

### 데이터 인프라

6. **[Apache Arrow가 압도적으로 빠른 이유 4가지](apache-arrow-internals/)** — 컬럼 기반 레이아웃, SIMD, Null 비트맵, Zero-Copy 원리를 메모리 단에서 설명합니다.
7. **[py123d 입문: 자율주행 데이터셋의 공통어](py123d-for-beginners/)** — nuScenes, Waymo, Argoverse 2 등을 단 하나의 API로 다루는 py123d의 설계 원리와 사용법을 소개합니다.
8. **[파편화된 자율주행 데이터를 하나로: py123d + FiftyOne + Rerun](autonomous-data-pipeline/)** — 파편화된 데이터셋을 py123d로 표준화하고, FiftyOne으로 큐레이션하고, Rerun으로 시각화하는 파이프라인을 소개합니다.
9. **[py123d 커스텀 파서 작성법](py123d-dataset-conversion/)** — nuScenes·Waymo·AV2 변환 코드를 분석하고, 사내 데이터셋용 `BaseLogParser`를 직접 구현합니다.
10. **[py123d → NVIDIA NuRec(NCore): 자율주행 데이터를 신경 재구성 파이프라인으로](py123d-to-nurec/)** — py123d 표준 포맷을 NCore V4로 변환해 NuRec 신경 재구성 파이프라인에 연결하는 방법을 설명합니다.
11. **[Arrow로 관통하는 E2E 회귀 테스트 파이프라인](closed-loop-regression-with-dora/)** — py123d → FiftyOne → DORA → Rerun으로 이어지는 Apache Arrow 기반 회귀 테스트 구조를 소개합니다.
12. **[Arrow Flight: gRPC로 이기종 PC 간 데이터를 Zero-Copy에 가깝게 전송하기](arrow-flight-network-transfer/)** — 같은 머신 안에서만 통하던 Arrow의 Zero-Copy를, gRPC 기반 Arrow Flight가 네트워크 너머로 어떻게 확장하는지 정리합니다.

수천 개 시나리오를 클라우드에서 병렬 실행하는 오케스트레이션은 별도 시리즈로 분리했습니다. **[시뮬레이션 오케스트레이션](../simulation/)**을 참고하세요.
