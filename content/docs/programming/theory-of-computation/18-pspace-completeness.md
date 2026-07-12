---
title: "18. 공간 복잡도(Space Complexity)와 새비치 정리, 그리고 TQBF의 PSPACE-완전성"
date: 2026-07-12T15:00:00+09:00
draft: false
tags: ["theory-of-computation", "mit-18.404", "space-complexity", "savitch-theorem", "tqbf", "pspace"]
categories: ["theory-of-computation"]
description: "결정적·비결정적 공간 복잡도 계층인 PSPACE와 NPSPACE의 동등성을 증명하는 새비치 정리(Savitch's Theorem), PSPACE-완전성(PSPACE-Completeness), 그리고 양화사가 포함된 부울 식 문제인 TQBF의 완벽성 증명을 공부합니다."
---

지난 16편에서는 복잡도 이론의 주춧돌인 쿡-레빈 정리와 SAT 문제의 NP-완전성 증명 과정을 살펴보고, 3SAT 역시 NP-완전임을 증명했습니다. 

지금까지는 컴퓨터 연산에 걸리는 "시간(Time)"의 제약을 위주로 보았다면, 이번에는 연산 중에 소모되는 메모리 즉 **"공간(Space)"**의 제약을 위주로 분석하는 공간 복잡도 계층을 다룹니다.

이번 18번째 강의와 [강의 슬라이드](file:///Users/yeongjun/Develops/develop/static/references/theory-of-computation/lecture-18-pspace-completeness.pdf)에서는 비결정론이 공간 사용에 큰 영향을 주지 못한다는 **새비치 정리**를 배우고, 공간 복잡도 최고의 난제 집합인 **PSPACE-완전성**과 **TQBF 문제**를 공부하겠습니다.

---

## 1. 공간 복잡도(SPACE Complexity)와 새비치 정리 (Savitch's Theorem)

시간 복잡도와 유사하게, 튜링 머신이 입력 $w$에 대해 사용하는 최대 테이프 셀(Cell)의 개수를 기준으로 공간 복잡도를 정의합니다.

- **$\text{SPACE}(f(n))$**: 결정적 1-테이프 튜링 머신이 $O(f(n))$ 공간을 사용하여 판정하는 언어들의 집합.
- **$\text{NSPACE}(f(n))$**: 비결정적 튜링 머신이 $O(f(n))$ 공간을 사용하여 판정하는 언어들의 집합.
- **$\text{PSPACE}$**: 다항식 크기의 공간만 사용하는 결정적 문제들의 집합 ($\bigcup_k \text{SPACE}(n^k)$).
- **$\text{NPSPACE}$**: 다항식 크기의 공간만 사용하는 비결정적 문제들의 집합 ($\bigcup_k \text{NSPACE}(n^k)$).

시간 복잡도에서는 아직 $\text{P} = \text{NP}$인지 밝혀내지 못했지만, **공간 복잡도에서는 비결정론적 공간과 결정론적 공간이 정확히 일치함**이 수학적으로 증명되어 있습니다. 그 도구가 바로 **새비치 정리**입니다.

### 새비치 정리 (Savitch's Theorem)
$$\text{NSPACE}(f(n)) \subseteq \text{SPACE}(f^2(n)) \quad (\text{단, } f(n) \ge n)$$

비결정적으로 작동하는 NSPACE 알고리즘은 결정적 튜링 머신으로 시뮬레이션할 때 **최대 제곱 배의 공간($f^2(n)$)**만 있으면 구현이 가능합니다.

- **핵심 알고리즘 (분할 정복 경로 찾기)**:
  두 설정 $c_i$와 $c_j$ 사이를 최대 $b$단계 내에 갈 수 있는지 테스트하는 재귀 함수 $M(c_i, c_j, b)$를 작성합니다.
  1. 만약 $b=1$이면, $c_i \to c_j$ 단일 단계 전이가 합법적인지 직접 확인합니다.
  2. 만약 $b>1$이면, 사용 가능한 모든 중간 설정 $c_{\text{mid}}$들에 대해 재귀적으로 $M(c_i, c_{\text{mid}}, b/2)$ 와 $M(c_{\text{mid}}, c_j, b/2)$를 둘 다 수행합니다.
  3. 두 재귀 호출이 모두 참을 반환하는 $c_{\text{mid}}$가 발견되면 수락합니다.

- **공간 복잡도 분석**:
  최대 가치 있는 경로의 길이는 상태 설정의 수인 $t = d^{f(n)}$ ($d$는 상수)개입니다. 
  - 재귀 호출의 최대 깊이는 $\log t = O(f(n))$이 됩니다.
  - 각 재귀 단계마다 중간 설정 $c_{\text{mid}}$ 하나를 테이프에 기록해야 하므로 레벨당 $O(f(n))$ 공간이 듭니다.
  - 따라서 전체 공간 복잡도는 **$\text{깊이} \times \text{레벨당 공간} = O(f^2(n))$**이 됩니다.

이 정리에 의해 다항식 공간에 대입하면 $\text{NPSPACE} \subseteq \text{PSPACE}$ 가 되므로, 결국 **$\text{PSPACE} = \text{NPSPACE}$** 임이 보장됩니다.

---

## 2. PSPACE-완전성(PSPACE-Completeness)과 환원의 제약

NP-완전성과 마찬가지로 PSPACE 계층에서 가장 어려운 문제들의 집합을 **PSPACE-완전(PSPACE-Complete)**이라고 부릅니다.

$$\text{언어 } B\text{가 PSPACE-Complete이다} \iff B \in \text{PSPACE} \quad \text{and} \quad \forall A \in \text{PSPACE}, A \le_{\text{P}} B$$

### 왜 PSPACE-환원이 아니라 다항 시간 환원을 쓸까?
환원(Reduction)의 세기는 증명하고자 하는 복잡도 클래스보다 **수학적으로 더 약해야(Weaker)** 복잡도 계층 분류의 의미가 있습니다. 

만약 환원 함수 자체에 다항 공간(PSPACE) 사용을 허용해 버린다면, PSPACE 내의 모든 일반적인 문제들이 서로를 다항 공간 내에서 마음대로 변환하여 해결할 수 있게 되어 PSPACE-완전성이라는 "가장 어려운 문제"를 골라내는 눈타겟이 완전히 무력화됩니다. 따라서 환원은 철저히 **다항 시간 환원($\le_{\text{P}}$)**만을 고수합니다.

---

## 3. 양화사 부울 식 문제: TQBF (True Quantified Boolean Formula)

부울 논리식에 모든 것을 뜻하는 **전칭 양화사($\forall$, For all)**와 존재를 뜻하는 **존재 양화사($\exists$, There exists)**를 변수 앞에 붙인 식을 QBF(Quantified Boolean Formula)라고 합니다.

- **QBF 예시**:
  - $\phi_1 = \forall x \exists y [(x \vee y) \wedge (\bar{x} \vee \bar{y})]$
    - $x=1$일 때는 $y=0$을 고르면 참이 되고, $x=0$일 때는 $y=1$을 고르면 참이 되므로, 이 식은 **참(TRUE)**입니다.
- **정의**: $\text{TQBF} = \{ \langle \phi \rangle \mid \phi\text{는 참인 QBF 식이다} \}$

이 TQBF 문제는 **PSPACE에 속합니다.** 양화사를 풀기 위해 변수마다 0과 1을 대입해 보며 참/거짓 분기를 재귀 탐색하면 되는데, 현재 탐색 중인 변수 할당 상태(최대 $n$개)만 테이프에 올려두고 재활용하면 되므로 공간은 단지 **다항식 크기($O(n)$)**만 사용하기 때문입니다.

---

## 4. TQBF의 PSPACE-완전성 증명 (양화사 $\forall$ 트릭)

쿡-레빈 정리의 격자판 태블로 공식을 TQBF 증명에 그대로 적용하려면 문제가 생깁니다. PSPACE 계산은 최대 $d^{n^k}$의 지수적인 단계를 실행할 수 있으므로, 태블로 격자판의 높이가 지수적으로 늘어나 식의 크기가 너무 커집니다.

새비치 정리의 분할 정복 공식인 $\phi_{c_i, c_j, b} = \exists c_{\text{mid}} [\phi_{c_i, c_{\text{mid}}, b/2} \wedge \phi_{c_{\text{mid}}, c_j, b/2}]$를 그대로 쓰더라도, 각 분할 단계마다 식의 개수가 2배씩 늘어나 최종 논리식의 길이가 여전히 지수적으로 폭발하게 됩니다.

### 해결책: 전칭 양화사($\forall$)를 통한 재귀 합치기 트릭
수학자들은 QBF의 강력한 무기인 $\forall$ 양화사를 도입하여 두 개의 재귀 조각을 하나로 묶어내는 기발한 한 수를 두었습니다.

$$\phi_{c_i, c_j, b} = \exists c_{\text{mid}} \forall (c_g, c_h) \in \{ (c_i, c_{\text{mid}}), (c_{\text{mid}}, c_j) \} \left[ \phi_{c_g, c_h, b/2} \right]$$

이 식을 수학적인 부울 식으로 풀어 쓰면 다음과 같습니다:
$$\phi_{c_i, c_j, b} = \exists c_{\text{mid}} \forall c_g \forall c_h \left[ ((c_g, c_h) = (c_i, c_{\text{mid}}) \vee (c_g, c_h) = (c_{\text{mid}}, c_j)) \to \phi_{c_g, c_h, b/2} \right]$$

이 변환을 적용하면, 재귀 레벨이 한 단계 깊어질 때마다 서브 공식의 개수가 2배로 증가하지 않고, **오직 상수 크기 만큼만 식이 추가**됩니다!
- 재귀의 깊이는 $\log t = O(n^k)$ 입니다.
- 매 단계마다 추가되는 공식의 크기도 변수 크기에 비례하는 다항식입니다.
- 결과적으로 전체 TQBF 공식의 총 크기는 **$O(n^k) \times O(n^k) = O(n^{2k})$ (다항식 크기)**로 극적으로 압축됩니다!

이 다항 시간 변환식 조립을 통해 PSPACE에 속한 임의의 모든 언어가 TQBF로 환원됨이 증명되었으며, **TQBF는 PSPACE-완전(PSPACE-Complete) 문제**가 되었습니다.

---

## 요약 및 마치며

- **새비치 정리**는 분할 정복 탐색 기법을 통해 비결정적 공간을 결정적 제곱 공간으로 시뮬레이션할 수 있음을 입증하여 **$\text{PSPACE} = \text{NPSPACE}$**를 증명합니다.
- **PSPACE-완전성** 정의에는 복잡도 계층 분류의 유효성을 위해 여전히 **다항 시간 환원($\le_{\text{P}}$)**이 사용됩니다.
- 한정 기호가 포함된 부울 식 문제인 **TQBF**는 다항 공간 내에서 분기 탐색이 가능하여 PSPACE에 포함됩니다.
- TQBF의 PSPACE-완전성 증명 과정에서 식의 크기가 지수적으로 폭발하는 문제를 방지하기 위해 **$\forall$ 양화사를 사용해 재귀적 하위 문제를 하나로 병합하는 트릭**이 사용되었습니다.

시간 복잡도의 한계를 넘어 메모리 공간 하에서의 완전성을 아름다운 논리식 유도로 증명했습니다. 

다음 19번째 강의 요약에서는 이 PSPACE-완전성의 대표적인 실생활 예시이자, 두 플레이어가 서로 공방을 벌이는 게임의 필승 전략 탐색 문제인 **일반화된 지리 게임(Generalized Geography)**에 대해 알아보겠습니다!
