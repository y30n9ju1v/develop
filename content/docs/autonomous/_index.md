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
