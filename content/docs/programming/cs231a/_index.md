---
title: "CS231A: Computer Vision"
description: "Stanford CS231A 강의 노트를 바탕으로 컴퓨터 비전의 핵심 수학적 기초를 정리한 시리즈입니다."
---

Stanford CS231A(Computer Vision: From 3D Reconstruction to Recognition) 강의 노트를 한국어로 정리한 시리즈입니다. 카메라 모델부터 시작해 3D 재구성, 인식까지 컴퓨터 비전의 수학적 기초를 다룹니다.

## 시리즈 목록

- **[카메라 모델](01-camera-models/)** — 핀홀 카메라, 렌즈, 내부/외부 파라미터, 카메라 캘리브레이션
- **[단일 뷰 계측](02-single-view-metrology/)** — 2D 변환 계층, 무한점/무한선, 소실점과 지평선, 단일 이미지 캘리브레이션
- **[에피폴라 기하학](03-epipolar-geometry/)** — 에피폴라 기하학, 본질/기본 행렬, 8점 알고리즘, 이미지 정류
- **[스테레오 시스템과 SfM](04-stereo-systems-and-structure-from-motion/)** — 삼각측량, 어파인/투영 SfM, Tomasi-Kanade 인수분해, 번들 조정
- **[능동 스테레오와 체적 스테레오](05-active-volumetric-stereo/)** — 능동 스테레오, 공간 조각, 그림자 조각, 복셀 채색
- **[피팅과 매칭](06-fitting-matching/)** — 최소제곱법, 강건 비용 함수, RANSAC, Hough 변환
- **[표현과 표현 학습](07-representation-learning/)** — 상태·마르코프 성질, 생성/판별 모델, 전통/학습 표현, 오토인코더
- **[단안 깊이 추정과 특징 추적](08-monocular-depth-estimation/)** — 시차-깊이 관계, 지도/비지도/자기지도 깊이 추정, 밀집 서술자 특징 추적
- **[광학 흐름과 장면 흐름](09-optical-flow/)** — 모션 필드, 밝기 항상성·소운동 가정, 광학 흐름 제약 방정식, 개구부 문제, Lucas-Kanade
- **[최적 추정: 베이즈 필터와 칼만 필터](10-optimal-estimation/)** — POMDP 상태 추정, 베이즈 필터 유도, 이산 베이즈 필터, 칼만 필터, 확장 칼만 필터(EKF)
