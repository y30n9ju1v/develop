---
title: "Sim-to-Real 검증 방법론: 시뮬레이션 성능이 실차 성능을 예측하는가"
date: 2026-07-14T00:00:00+09:00
draft: false
tags: ["autonomous", "sim-to-real", "closed-loop", "nurec", "dora", "safety-validation"]
categories: ["autonomous"]
description: "Reality Gap과 Performance Gap을 구분하는 MCRPG 방법론, 3단계 검증(Digital Twin/Parallel Execution/Real-World), MNCC 같은 정량 지표, 그리고 오픈 루프 통과가 클로즈 루프 안전성을 보장하지 못한다는 NeuroNCAP의 실증 사례를 정리합니다."
---

> 이 글은 [Closing Sim2Real Gaps: A Versatile Development and Validation Platform for Autonomous Driving Stacks](https://www.mdpi.com/1424-8220/26/4/1338)(Sensors, 2026)와 [NeuroNCAP: Photorealistic Closed-loop Safety Testing for Autonomous Driving](https://arxiv.org/abs/2404.07762)를 참고해 작성했습니다.
> 이 시리즈에서 다룬 [NCore V4](../data-infra/ncore-v4-for-beginners/)·[NuRec](../data-infra/nurec-neural-reconstruction-for-beginners/)의 재구성 파이프라인과 [DORA 회귀 테스트](../dora/dora-rs-av-regression-testing/)의 클로즈 루프 구조를 이미 알고 있다는 걸 전제로 씁니다.

---

## 1. 문제: 시뮬레이션을 통과했다고 실차에서도 통과할까

[NuRec 입문](../data-infra/nurec-neural-reconstruction-for-beginners/)에서 3D Gaussian Splatting으로 실제 주행 로그를 사진처럼 재구성할 수 있다는 걸 봤고, [DORA 회귀 테스트](../dora/dora-rs-av-regression-testing/)에서 그 재구성된 환경 위에서 클로즈 루프 테스트를 돌리는 파이프라인까지 봤습니다. 그런데 이 파이프라인이 완성되었다고 해서 "시뮬레이션에서 통과한 모델은 실차에서도 안전하다"고 바로 말할 수 있을까요?

정확히 이 질문에 답하려는 최근 연구들이, 시뮬레이션-실차 간극을 하나의 뭉뚱그린 개념이 아니라 **서로 다른 원인을 가진 두 개의 별도 간극**으로 나눠서 다룹니다.

---

## 2. Reality Gap과 Performance Gap: 두 가지 다른 종류의 간극

**Reality Gap(RG)**은 시뮬레이션 안의 차량이 **실제 차량과 다르게 행동한다는 사실 자체**입니다 — 조명, 텍스처, 차량 동역학(타이어 마찰, 관성), 다른 에이전트(보행자·차량)의 행동 패턴이 시뮬레이터와 실제 도로에서 다르기 때문에 생깁니다.

**Performance Gap(PG)**은 그 위에서 한 걸음 더 나아간 질문입니다 — "이 자율주행 스택이 시뮬레이션에서 낸 성능 수치(충돌률, 승차감 등)가, 실제로 그 차를 실도로에 풀었을 때 낼 성능과 얼마나 다른가"입니다.

이 둘을 나누는 이유는 실무적으로 중요합니다 — Reality Gap이 작아도(차량이 시뮬레이션과 실제에서 거의 똑같이 움직여도) Performance Gap은 클 수 있습니다. 예를 들어 시뮬레이션의 조향각 오차가 실제와 1도 이내로 거의 같더라도, 그 1도 차이가 특정 시나리오(좁은 골목, 급커브)에서만 누적되어 실제로는 안전 마진을 깎아먹는 식으로 성능 지표에 반영될 수 있습니다. 그래서 "차량이 비슷하게 움직이는가"와 "결과적으로 성능이 비슷한가"를 따로 재야 합니다.

---

## 3. 3단계 검증: Digital Twin → Parallel Execution → Real-World

이 두 간극을 점진적으로 좁혀가는 절차가 **MCRPG(Methodology for Closing Reality and Performance Gaps)**입니다. 파라미터 튜닝, 교차 도메인 지표, 그리고 세 단계의 검증을 반복하며 RG와 PG를 동시에 줄여나갑니다.

```
1단계: Digital Twin
   실제 도로 구간을 최대한 정밀하게 시뮬레이터 안에 복제한다.
   (이 시리즈에서는 NuRec의 3D Gaussian Splatting 재구성이 이 단계에 해당)
   ↓
2단계: Parallel Execution
   같은 시나리오를 시뮬레이터와 실차에서 "동시에" 돌리며,
   같은 시각에 두 환경의 신호(조향각, 속도, 감지 결과)를 나란히 비교한다.
   ↓
3단계: Real-World
   시뮬레이션에서 검증된 스택을 실제 도로에 배포하고,
   앞 단계에서 예측한 성능과 실제 성능의 차이를 다시 측정해 피드백한다.
```

2단계(Parallel Execution)가 이 방법론의 핵심입니다 — 시뮬레이션 따로, 실차 따로 돌린 뒤 최종 결과만 비교하는 게 아니라, **같은 시나리오를 동시에 재생하면서 매 순간의 신호를 정렬해 비교**합니다. 이렇게 해야 "이 시나리오 전체에서는 비슷했는데, 정확히 이 교차로 진입 순간부터 어긋나기 시작했다"는 식으로 간극이 벌어지는 지점을 구체적으로 짚어낼 수 있습니다.

---

## 4. 정량 지표: MNCC로 "비슷하게 움직였는가"를 재기

Reality Gap을 사람이 눈으로 보고 "비슷해 보인다"고 판단하는 대신, 이 방법론은 **MNCC(Maximum Normalized Cross-Correlation)**라는 정량 지표를 씁니다. 조향각, 속도, 물체 감지 결과 같은 여러 신호(멀티모달)에 대해, 시뮬레이션 신호와 실차 신호를 시간축으로 정렬해가며 서로 얼마나 강하게 상관되는지를 계산합니다 — 두 신호가 완벽히 같은 모양이면 1에 가깝고, 무관하면 0에 가깝습니다.

이 지표가 유용한 이유는 "값이 정확히 같은가"보다 "**패턴이 같은가**"를 재기 때문입니다 — 시뮬레이션의 조향각이 실차보다 약간의 시간 지연을 두고 따라오더라도(예: 센서 처리 지연 차이), 지연을 보정해 정렬한 뒤에는 두 신호의 모양 자체가 일치한다면 MNCC는 이걸 "정렬만 다를 뿐 근본적으로 같은 거동"으로 잡아냅니다. 이렇게 계산한 **Reality Alignment**(MNCC 기반)와, 별도로 안전·승차감·주행 효율을 다루는 **Ego-Vehicle Performance** 지표를 함께 쓰는 "이중 지표 체계"가 이 방법론의 실제 측정 도구입니다.

---

## 5. 왜 오픈 루프 통과만으로는 부족한가: NeuroNCAP의 실증

[DORA 회귀 테스트 편](../dora/dora-rs-av-regression-testing/#9-오픈-루프와-클로즈-루프)에서 "오픈 루프는 근본적으로 누적 드리프트나 경로 이탈 버그를 잡지 못한다"고 짚었는데, 이걸 실제 데이터로 보여준 연구가 **NeuroNCAP**입니다.

NeuroNCAP은 NeRF 기반 시뮬레이터로 실제 주행 센서 데이터를 학습해 새로운 시나리오를 재구성하고, Euro NCAP(유럽 신차 안전성 평가 프로그램)에서 영감을 받은 **안전이 걸린 시나리오**로 자율주행 모델을 클로즈 루프로 테스트합니다. 논문의 핵심 발견은 이렇습니다.

> "최신 end-to-end planner들은 일반적인 주행 시나리오를 오픈 루프로 평가할 때는 뛰어난 성능을 보이지만, 우리의 안전이 걸린 시나리오를 클로즈 루프로 다룰 때는 심각한 결함을 드러낸다."

즉 "평소 주행에서 예측을 잘한다"는 오픈 루프 지표(예: 궤적 예측 오차)가 좋다고 해서, "위험한 순간에 실제로 충돌을 피하는가"라는 클로즈 루프 안전성까지 보장하지 않는다는 걸 실제 모델로 확인한 것입니다 — 앞서 다룬 Performance Gap이 시뮬레이션-실차 사이에서만 생기는 게 아니라, **같은 시뮬레이션 안에서도 오픈 루프 지표와 클로즈 루프 지표 사이**에 벌어질 수 있다는 걸 보여주는 사례이기도 합니다.

---

## 6. 이 블로그의 파이프라인에 적용하면

지금까지 이 시리즈가 쌓아온 조각들을 이 방법론의 3단계에 대응시켜보면 이렇습니다.

| MCRPG 단계 | 이 시리즈에서 대응하는 것 |
|---|---|
| 1단계: Digital Twin | [NCore V4](../data-infra/ncore-v4-for-beginners/) 포맷으로 담은 실도로 로그를 [NuRec](../data-infra/nurec-neural-reconstruction-for-beginners/)이 3D Gaussian Splatting으로 재구성 |
| 2단계: Parallel Execution | [DORA-CARLA/NuRec 클로즈 루프 연동](../dora/dora-rs-simulator-integration/)에서 재생과 실시간 센서 스트림을 나란히 비교 |
| 3단계: Real-World | [DORA를 실차에 올리기](../dora/dora-rs-real-hardware-deployment/)에서 다룬 watchdog·꼬리 지연 검증이 실차 배포 이후의 안전 계층 |

여기서 빠져 있던 조각이 바로 이 글의 4~5절입니다 — 지금까지는 "재구성이 사진처럼 정확한가"(NuRec의 novel view synthesis 품질)와 "클로즈 루프가 구조적으로 동작하는가"(DORA 파이프라인)만 다뤘지, **"그 재구성 위에서 낸 성능이 실차 성능을 얼마나 잘 예측하는가"를 MNCC 같은 지표로 정량화하는 단계**는 없었습니다. 이 지표를 [DORA 회귀 테스트](../dora/dora-rs-av-regression-testing/)의 CI 임계값 관리 체계에 추가하면, "이번 주 배포로 시뮬레이션 성능은 좋아졌는데 Reality Alignment(MNCC)가 떨어졌다"처럼 **시뮬레이션 성능 개선이 실제로 실차 예측력까지 개선했는지**를 회귀 테스트 차원에서 감시할 수 있게 됩니다.

---

## 7. 정리

- **Reality Gap**(시뮬레이션과 실제가 다르게 행동하는가)과 **Performance Gap**(그 위에서 낸 성능 수치가 실제로도 유효한가)은 서로 다른 원인을 가진 별개의 간극이며, 하나가 작다고 다른 하나도 작다는 보장이 없습니다.
- **MCRPG**는 Digital Twin → Parallel Execution → Real-World라는 3단계를 반복하며 두 간극을 점진적으로 좁히는 방법론이고, 그중 **Parallel Execution**(같은 시나리오를 동시에 재생하며 신호를 정렬해 비교) 단계가 간극이 벌어지는 지점을 구체적으로 짚어내는 핵심입니다.
- **MNCC** 같은 정량 지표가 "패턴이 얼마나 비슷한가"를 시간 정렬까지 고려해 측정하고, 여기에 안전·승차감·효율을 다루는 성능 지표를 더한 이중 체계로 검증합니다.
- **NeuroNCAP**은 오픈 루프에서 잘하는 E2E 모델이 클로즈 루프 안전 시나리오에서는 심각하게 실패할 수 있다는 걸 실제로 보여줘서, Performance Gap이 시뮬레이션-실차 사이뿐 아니라 같은 시뮬레이션의 오픈/클로즈 루프 사이에도 존재한다는 걸 확인시켜 줍니다.
- 이 시리즈가 이미 쌓은 NCore/NuRec 재구성과 DORA 클로즈 루프 파이프라인 위에, MNCC 같은 정량적 Reality Alignment 지표를 CI 회귀 테스트에 추가하는 것이 다음으로 채워야 할 조각입니다.

이 글이 "시뮬레이션 성능이 실차 성능을 예측하는가"를 다뤘다면, 그다음 질문은 "그래서 이 검증 결과가 안전하다는 주장으로 이어지는가"입니다. 이 질문에 답하는 업계 표준 프레임워크(SOTIF, ISO 21448)는 [별도 글](../sotif-safety-validation-for-e2e-av/)에서 다룹니다.
