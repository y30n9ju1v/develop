---
title: "nuPlan과 CARLA Leaderboard: 클로즈 루프 평가는 실제로 무엇을 채점하는가"
date: 2026-07-14T00:00:00+09:00
draft: false
tags: ["autonomous", "nuplan", "carla", "closed-loop", "benchmark", "safety-validation"]
categories: ["autonomous"]
description: "nuPlan의 Closed-Loop Score와 CARLA Leaderboard의 Driving Score가 각각 어떤 세부 지표를 어떤 방식으로 합산하는지, 그리고 '점수를 잘 받는 것'과 '실제로 안전한 것' 사이의 간극을 정리합니다."
---

> 이 글은 [nuPlan 논문(arXiv:2106.11810)](https://ar5iv.labs.arxiv.org/html/2106.11810), [CARLA Leaderboard 2.0 공식 평가 기준 문서](https://leaderboard.carla.org/evaluation_v2_0/), [CARLA Leaderboard 2.1 평가 기준 문서](https://leaderboard.carla.org/evaluation_v2_1/)를 참고해 작성했습니다.
> [Sim-to-Real 검증 방법론](sim-to-real-validation-methodology/)에서 다룬 오픈 루프/클로즈 루프 구분과 [SOTIF](sotif-safety-validation-for-e2e-av/)의 4분면 모델을 이미 알고 있다는 걸 전제로 씁니다.

---

## 1. 문제: "벤치마크 1등"이 무엇을 증명하는가

nuPlan Challenge나 CARLA Leaderboard에서 좋은 점수를 받았다는 뉴스를 보면 자연스럽게 "이 모델이 안전하게 잘 주행한다"고 받아들이게 됩니다. 그런데 이 점수가 정확히 **무엇을 어떻게 합산한 숫자인지** 뜯어보면, 실무에서 이 벤치마크를 어디까지 신뢰할 수 있고 어디서부터 별도 검증이 필요한지가 훨씬 분명해집니다. 이 글은 그 두 벤치마크의 채점 방식을 실제 정의 그대로 뜯어봅니다.

---

## 2. nuPlan: 세 단계로 나뉜 평가 모드

nuPlan은 평가를 난이도가 다른 **세 모드**로 나눕니다 — 뒤로 갈수록 "실제 도로에 더 가까운" 조건입니다.

| 모드 | 배경 에이전트의 동작 | 무엇을 테스트하는가 |
|---|---|---|
| **Open-Loop (OLS)** | 로그를 그대로 재생 | 계획된 경로가 전문가(사람) 운전자의 실제 경로를 얼마나 잘 모방하는가 |
| **Closed-Loop Non-Reactive (CLS-NR)** | 다른 차량은 기록된 궤적을 그대로 재생(내 모델의 행동에 반응하지 않음) | 내 모델이 스스로 낸 궤적을 실제로 추종했을 때 결과가 어떻게 달라지는가 |
| **Closed-Loop Reactive (CLS-R)** | 다른 차량이 IDM(Intelligent Driver Model) + MOBIL 차선변경 휴리스틱으로 내 모델에 반응 | 내 모델의 판단이 주변 교통 흐름 자체를 바꿀 때도 견고한가 |

이 세 단계 구분이 중요한 이유는, [Sim-to-Real 검증 방법론](sim-to-real-validation-methodology/)에서 다룬 "오픈 루프 통과가 클로즈 루프 안전성을 보장하지 않는다"는 문제를 nuPlan이 벤치마크 설계 단계에서부터 명시적으로 분리해뒀기 때문입니다. Open-Loop만 잘 나오고 Closed-Loop이 나쁜 모델은, 정확히 NeuroNCAP이 보여준 것과 같은 "누적 드리프트에 취약한 모델"일 가능성이 높습니다.

---

## 3. nuPlan의 Closed-Loop Score: 여러 지표를 곱해서 하나로 만든다

Closed-Loop Score(CLS)는 여러 세부 지표를 조합한 하나의 숫자입니다. 핵심 구조는 **"게이트(gate) 역할을 하는 안전 위반 항목"**과 **"정도 차이를 반영하는 연속값 지표"**를 나누는 것입니다.

- **No At-Fault Collisions**: 3단계 점수 — 차량/보행자와의 과실 충돌이나 물체와의 다중 충돌이면 0점, 물체와의 단일 충돌이면 0.5점, 그 외에는 1점.
- **Progress**: 경로를 얼마나 완주했는지의 비율.
- **Comfort**: jerk, 가속도, 조향 속도, 차량 진동으로 측정하는 승차감.
- **Time-to-Collision(TTC)**, 도로 이탈, 역주행, 제한 속도 준수 여부 등도 함께 포함됩니다.

여기서 중요한 설계가 **"multiplier" 페널티**입니다 — 충돌이 발생하거나, 도로를 이탈하거나, 경로 진행에 실패하면 그 시나리오의 점수 자체가 0으로 강제됩니다. 즉 "승차감은 매끄러웠는데 충돌이 있었다"는 식으로 다른 지표가 충돌 항목을 상쇄하지 못하도록, 안전 관련 위반을 **곱셈 게이트**로 처리한 것입니다. 이건 SOTIF의 언어로 보면, "잔여 위험(충돌)이 발생한 시나리오는 다른 어떤 성능 지표로도 그 위험을 가릴 수 없다"는 원칙을 채점 공식에 그대로 반영한 것입니다.

---

## 4. CARLA Leaderboard: Driving Score = Route Completion × Infraction Penalty

CARLA Leaderboard는 구조가 더 단순합니다 — 최종 지표인 **Driving Score**는 딱 두 값의 곱입니다.

```
Driving Score = Route Completion × Infraction Penalty   (최대 100)
```

**Route Completion**은 경로를 얼마나 완주했는지의 백분율입니다. 도로를 이탈해 주행한 구간은 완주 거리에서 제외됩니다.

**Infraction Penalty**는 1.0에서 시작해서, 위반이 발생할 때마다 정해진 계수를 **곱해서** 깎이는 구조입니다(Leaderboard 2.0 기준 대표적인 계수):

| 위반 유형 | 페널티 계수 |
|---|---|
| 보행자 충돌 | 0.50 |
| 차량 충돌 | 0.60 |
| 고정 구조물 충돌 | 0.65 |
| 적신호 위반 | 0.70 |
| 긴급차량 미양보 | 0.70 |
| 정지 신호 위반 | 0.80 |
| 시나리오 타임아웃 | 0.70 |
| 최소 속도 미달 | 최대 0.70 |

같은 유형의 위반이 두 번 나오면 계수가 **거듭제곱으로** 적용됩니다(예: 차량 충돌 2회 = 0.60²). 곱셈 구조라서 위반이 누적될수록 점수가 기하급수적으로 떨어집니다 — nuPlan의 "게이트" 방식과는 다르지만, 결국 "안전 위반은 다른 어떤 좋은 수치로도 상쇄되지 않는다"는 같은 설계 철학을 곱셈으로 구현한 것입니다.

흥미로운 디테일 하나 — 도로 이탈은 Route Completion에서 그 구간을 빼는 동시에 Infraction Penalty에서도 동일 비율만큼 깎이기 때문에, 두 효과가 서로 상쇄되어 **Driving Score 자체에는 순효과가 없습니다**. 이런 세부 규칙까지 알아야 "이 모델이 왜 이 점수를 받았는지"를 제대로 해석할 수 있습니다.

---

## 5. 두 벤치마크가 답하지 않는 것

이 두 벤치마크는 매우 구체적이고 재현 가능한 채점 기준을 제공하지만, 몇 가지는 명시적으로 답하지 않습니다.

- **얼마나 많이, 얼마나 다양하게 테스트해야 충분한가**는 벤치마크 자체가 정하지 않습니다 — 벤치마크의 고정된 route/scenario 세트를 통과하는 것과, 실제 ODD 전체를 충분히 커버하는 시나리오 공간을 설계하는 것은 별개의 질문입니다.
- **점수가 통계적으로 얼마나 확신할 수 있는 값인가**는 다루지 않습니다 — 고정된 route 몇 개를 도는 것만으로는 [희귀 사건 통계적 검증](importance-sampling-rare-event-safety-validation/)이 다루는 "억 마일 문제"의 답이 되지 못합니다. 벤치마크 점수가 높다는 것과, 실제 배포 환경에서의 사고율이 통계적으로 낮다는 것은 다른 수준의 주장입니다.
- **배경 에이전트의 행동 모델(IDM/MOBIL 같은 규칙 기반 모델)이 실제 인간 운전자의 다양성을 얼마나 잘 대표하는가**도 검증 대상입니다 — 이건 정확히 [Sim-to-Real 검증 방법론](sim-to-real-validation-methodology/)의 Reality Gap 문제이고, 벤치마크의 "클로즈 루프"가 진짜 실차의 클로즈 루프와 같은 통계적 특성을 갖는지는 별도로 확인해야 합니다.

즉 nuPlan/CARLA Leaderboard 점수는 **"정해진 시나리오 집합 안에서, 정해진 채점 규칙으로 측정한 상대적 순위"**이지, 그 자체로 "이 모델은 안전하다"는 SOTIF 수준의 주장을 완성해주지는 않습니다. 이 시리즈의 다른 글들이 다루는 시나리오 커버리지 설계, 통계적 검증, Sim-to-Real 정합성 확인이 있어야 벤치마크 점수를 실제 안전성 주장으로 연결할 수 있습니다.

---

## 6. 정리

- **nuPlan**은 Open-Loop/Closed-Loop Non-Reactive/Closed-Loop Reactive 세 단계로 평가 난이도를 나누고, Closed-Loop Score는 충돌·이탈 같은 안전 위반을 **곱셈 게이트**로 처리해 다른 지표가 이를 상쇄하지 못하게 설계되어 있습니다.
- **CARLA Leaderboard**의 Driving Score는 Route Completion과 Infraction Penalty의 곱이고, Infraction Penalty는 위반 유형별 계수가 위반 횟수만큼 거듭제곱으로 깎이는 구조입니다.
- 두 벤치마크 모두 "안전 위반은 다른 성능으로 상쇄되지 않는다"는 설계 철학을 공유하지만, **얼마나 테스트하면 충분한지, 점수가 통계적으로 얼마나 확실한지, 배경 에이전트가 실제 도로를 얼마나 잘 대표하는지**는 벤치마크 바깥의 문제로 남습니다.
