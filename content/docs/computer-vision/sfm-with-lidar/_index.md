---
title: "3-View SfM with LiDAR"
description: "Python과 OpenCV로 카메라 + LiDAR 데이터를 이용한 3-View Structure from Motion을 직접 구현하는 시리즈입니다."
---

Python과 OpenCV만으로 카메라 + LiDAR 데이터를 이용한 3-View SfM(Structure from Motion)을 바닥부터 구현합니다. 데이터셋은 ETH3D를 사용하며, 목표는 3DGS를 깊게 이해하기 위한 선행 지식으로서 SfM의 각 단계를 직접 구현하며 이해하는 것입니다.

## 시리즈 목록

- **[개요 및 데이터 준비](01-overview-and-dataset/)** — SfM 파이프라인 전체 흐름, ETH3D 데이터셋 구조 및 로딩
- **[Feature 추출 및 매칭](02-feature-extraction-and-matching/)** — SIFT, BFMatcher, RANSAC으로 프레임 간 대응점 찾기
- **[2-View Geometry](03-two-view-geometry/)** — Essential Matrix, 카메라 pose 복원, 초기 삼각측량
- **[LiDAR로 Scale 복원](04-lidar-scale-recovery/)** — depth map으로 scale ambiguity 해결
- **[3번째 뷰 추가: PnP](05-third-view-pnp/)** — solvePnP로 세 번째 카메라 등록 및 포인트 확장
- **[결과 시각화 및 정리](06-visualization-and-wrap-up/)** — Rerun SDK로 카메라 pose + 포인트클라우드 시각화, GT와 비교, 한계 및 다음 단계
