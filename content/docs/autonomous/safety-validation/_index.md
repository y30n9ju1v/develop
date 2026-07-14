---
title: "안전성 검증"
---

[데이터 인프라](../data-infra/) 시리즈가 쌓은 재구성·클로즈 루프 파이프라인이 "안전하다"는 주장으로 이어지려면 어떤 검증이 더 필요한지를 다룹니다.

1. **[Sim-to-Real 검증 방법론](sim-to-real-validation-methodology/)** — Reality Gap과 Performance Gap의 구분, MCRPG의 3단계 검증(Digital Twin/Parallel Execution/Real-World), MNCC 정량 지표, 그리고 오픈 루프 통과가 클로즈 루프 안전성을 보장하지 않는다는 NeuroNCAP의 실증 사례를 정리합니다.
2. **[SOTIF(ISO 21448): E2E 자율주행 모델의 안전성을 어떻게 주장하는가](sotif-safety-validation-for-e2e-av/)** — 부품 고장이 아니라 인지·판단 능력의 한계 자체가 위험이 되는 상황을 다루는 SOTIF의 4분면 모델, Triggering Condition, ODD 개념과, 이 시리즈의 파이프라인이 SOTIF 프로세스의 어디에 해당하는지 정리합니다.
3. **[희귀 사건 통계적 검증: Importance Sampling으로 억 마일 문제를 우회하기](importance-sampling-rare-event-safety-validation/)** — 자율주행 안전성 입증에 필요한 억 마일 문제를, 위험한 방향으로 분포를 왜곡해 샘플링하고 우도비로 되돌리는 Importance Sampling과 Cross-Entropy Method로 우회하는 원리를 정리합니다.
4. **[nuPlan과 CARLA Leaderboard: 클로즈 루프 평가는 실제로 무엇을 채점하는가](nuplan-carla-leaderboard-closed-loop-metrics/)** — nuPlan의 Open-Loop/Closed-Loop 3단계 평가와 Closed-Loop Score의 안전 위반 게이트 구조, CARLA Leaderboard의 Driving Score = Route Completion × Infraction Penalty 채점 공식, 그리고 벤치마크 점수가 채우지 못하는 지점을 정리합니다.
