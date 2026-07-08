---
title: "데이터 인프라"
---

자율주행 데이터 파이프라인의 기반 기술과 구축 방법을 다룹니다.

1. **[Apache Arrow가 압도적으로 빠른 이유 4가지](apache-arrow-internals/)** — 컬럼 기반 레이아웃, SIMD, Null 비트맵, Zero-Copy 원리를 메모리 단에서 설명합니다.
2. **[파편화된 자율주행 데이터를 하나로: py123d + FiftyOne + Rerun](autonomous-data-pipeline/)** — 파편화된 데이터셋을 py123d로 표준화하고, FiftyOne으로 큐레이션하고, Rerun으로 시각화하는 파이프라인을 소개합니다.
3. **[Arrow로 관통하는 클로즈 루프 회귀 테스트 파이프라인](closed-loop-regression-with-dora/)** — py123d → FiftyOne → DORA → Rerun으로 이어지는 Apache Arrow 기반 회귀 테스트 구조를 소개합니다.
