---
title: "22. 증명 가능하게 다루기 힘든 문제(Provably Intractable)와 오라클, P vs NP의 장벽"
date: 2026-07-12T17:00:00+09:00
draft: false
tags: ["theory-of-computation", "mit-18.404", "provably-intractable", "oracles", "bgs-theorem", "expspace"]
categories: ["theory-of-computation"]
description: "P나 PSPACE에 속하지 않아 현실적으로 해결 불가능함이 증명된 거듭제곱 정규식 동치성 문제($EQ_{\\text{REX}\\uparrow}$), 오라클 튜링 머신(Oracle TM)의 개념, 그리고 대각선 논법의 한계를 입증한 베이커-기브스-솔로베이(BGS) 정리를 공부합니다."
---

지난 21편에서는 시간과 공간 자원이 조금만 더 주어져도 확실하게 더 많은 문제를 해결할 수 있음을 규정하는 **위계 정리(Hierarchy Theorems)**를 공부했습니다.

이번 22번째 강의와 [강의 슬라이드](file:///Users/yeongjun/Develops/develop/static/references/theory-of-computation/lecture-22-provably-intractable-problems-oracles.pdf)에서는 위계 정리를 실전 문제에 적용하여 **"현실적인 시간과 공간 내에 푸는 것이 절대 불가능하다"**라고 완전히 입증된 자연스러운 문제와, 현대 컴퓨터 과학 최고의 난제인 P vs NP 문제가 왜 지금까지도 풀리지 않는지 그 수학적 장벽을 밝히는 **오라클 계산**을 공부하겠습니다.

---

## 1. 지수 복잡도 클래스와 증명 가능하게 어려운 문제

위계 정리에 따르면, 다음의 관계가 성립합니다.
- 시간 위계 정리: $\text{P} \subsetneq \text{EXPTIME}$
- 공간 위계 정리: $\text{PSPACE} \subsetneq \text{EXPSPACE}$

여기서 **EXPTIME**은 $O(2^{n^k})$ 지수 시간 문제들의 집합이고, **EXPSPACE**는 $O(2^{n^k})$ 지수 공간 문제들의 집합입니다.

만약 어떤 문제 $B$가 **EXPSPACE-완전(EXPSPACE-Complete)**임을 입증한다면, 공간 위계 정리에 의해 이 문제는 절대 PSPACE 공간이나 다항 시간(P) 내에 풀 수 없습니다 ($B \notin \text{PSPACE}$, $B \notin \text{P}$). 즉, 이 문제는 **증명 가능하게 다루기 힘든(Provably Intractable) 문제**가 됩니다.

---

## 2. 거듭제곱 정규 표현식 동치성 문제 ($EQ_{\text{REX}\uparrow}$)

일반 정규 표현식의 동치성 검사($EQ_{\text{REX}}$)는 PSPACE에 속합니다. 하지만 정규식에 **거듭제곱 기호(Exponentiation, $R^k$)**를 허용하면 난이도가 기하급수적으로 폭발합니다.

- **거듭제곱 정규 표현식**: $R^k$는 정규식 $R$을 $k$번 이어 붙인 것($R R \dots R$)을 뜻하며, 지수 $k$는 **이진수**로 작성됩니다. (예: $R^{100}$은 이진수로 써서 문자 7개 크기로 표현 가능)
- **정의**: $EQ_{\text{REX}\uparrow} = \{ \langle R_1, R_2 \rangle \mid R_1, R_2\text{는 거듭제곱이 포함된 동치인 정규 표현식이다} \}$

### 정리: $EQ_{\text{REX}\uparrow}$ 는 EXPSPACE-완전이다
이 문제가 EXPSPACE-완전이므로, $EQ_{\text{REX}\uparrow}$는 **PSPACE 공간 내에서도 풀 수 없는 매우 어려운 문제**입니다.

- **증명 아이디어**: 임의의 EXPSPACE 언어 $A$를 결정하는 튜링 머신 $M$(사용 공간 $2^{n^k}$)의 연산을 정규식으로 시뮬레이션하여 $A \le_{\text{P}} EQ_{\text{REX}\uparrow}$ 환원을 구현합니다.
- 입력 $w$가 주어졌을 때, $L(R_2) = \Delta^*$로 두고, $R_1$은 **\"$M$이 $w$를 거부하는 올바른 계산 이력이 '아닌' 모든 문자열\"**을 생성하도록 만듭니다.
- $M$의 사용 공간이 $2^{n^k}$이므로 이 계산 이력의 가로폭(설정의 크기)은 $2^{n^k}$입니다.
- 올바르지 않은 전이 규칙을 검사하려면, 격자판에서 거리가 정확히 $2^{n^k}-2$ 만큼 떨어진 두 위치의 문자가 서로 튜링 머신의 룰 $\delta$에 맞지 않음을 검사해야 합니다.
- **거듭제곱의 마법**: 거듭제곱이 없다면 $2^{n^k}-2$ 거리만큼 임의의 글자를 채우기 위해 $\Delta \dots \Delta$를 지수 개만큼 일일이 적어야 하므로 환원식 조립에 지수 시간이 걸려 환원이 불가능합니다. 하지만 거듭제곱이 있다면 단지 **$\Delta^{2^{n^k}-2}$**라고 적어주기만 하면 되므로 식의 길이가 다항식 크기 $O(n^k)$로 줄어들어 **다항 시간 내에 환원 조립이 가능**해집니다!

이 영리한 지수 결합 트릭 덕분에 $EQ_{\text{REX}\uparrow}$의 EXPSPACE-완전성이 입증됩니다.

---

## 3. 오라클 계산 (Computation with Oracles)

P vs NP 문제의 본질적인 해결 불가능성을 설명하기 위해, 수학자들은 **오라클(Oracle)**이라는 가상의 개념을 도입했습니다.

> **오라클 튜링 머신 (Oracle Turing Machine, $M^A$)**
> 특정 언어 $A$에 대해, "문자열 $x$가 $A$에 포함되는가?"라는 질문에 단 1단계 만에 (비용 없이 공짜로) 대답해 주는 **블랙박스(Oracle)**를 장착한 튜링 머신입니다.

- $\text{P}^A$: 오라클 $A$를 장착한 결정적 튜링 머신이 다항 시간 내에 풀 수 있는 언어들의 집합.
- $\text{NP}^A$: 오라클 $A$를 장착한 비결정적 튜링 머신이 다항 시간 내에 풀 수 있는 언어들의 집합.

예를 들어, $\text{NP} \subseteq \text{P}^{SAT}$ 입니다. SAT 오라클이 있다면 비결정론 없이도 다항 시간 내에 모든 NP 문제를 해결할 수 있기 때문입니다.

---

## 4. P vs NP 문제의 메타 수학적 장벽: BGS 정리 (Baker-Gill-Solovay)

1975년 시어도어 베이커(Theodore Baker), 존 기브스(John Gill), 로버트 솔로베이(Robert Solovay)는 복잡도 이론 역사상 가장 위대한 반격 중 하나인 **BGS 정리**를 발표합니다.

> **베이커-기브스-솔로베이 정리 (BGS Theorem)**
> 1. $\text{P}^A = \text{NP}^A$ 가 성립하는 오라클 $A$가 존재한다. (예: $A = TQBF$)
> 2. $\text{P}^B \neq \text{NP}^B$ 가 성립하는 오라클 $B$가 존재한다.

- **$\text{P}^{TQBF} = \text{NP}^{TQBF}$ 의 증명**:
  - $\text{NP}^{TQBF} \subseteq \text{NPSPACE}$ 임은 자명합니다 (오라클 질문을 푸는 데 다항식 공간만 쓰기 때문).
  - 새비치 정리에 의해 $\text{NPSPACE} = \text{PSPACE}$ 이고, TQBF가 PSPACE-완전이므로 $\text{PSPACE} \subseteq \text{P}^{TQBF}$ 입니다.
  - 따라서 $\text{P}^{TQBF} = \text{NP}^{TQBF}$ 가 성립합니다.

### 이 정리가 P vs NP 문제 해결에 주는 교훈
튜링 머신의 내부 구조를 뜯어보지 않고 기계의 시뮬레이션 동작만을 모사해 모순을 이끌어내는 대각선 논법(Diagonalization) 계열의 모든 증명 방식은, 오라클 블랙박스가 추가되더라도 증명의 논리 구조가 그대로 유지됩니다. 이를 **상대화(Relativization)**된다고 표현합니다.

하지만 BGS 정리는 오라클의 성질에 따라 P와 NP의 관계가 같아질 수도 있고 달라질 수도 있음을 보여줍니다. 즉, **"상대화가 가능한 모든 고전적 증명 기법(대각선 논법 포함)으로는 P vs NP 문제를 해결하는 것이 수학적으로 원천 불가능하다"**는 충격적인 결론에 도달합니다.

따라서 P vs NP를 증명하려면 오라클이 개입했을 때는 깨지지만 오라클이 없을 때만 정상 작동하는 **비상대화적(Non-relativizing)인 새로운 수학적 증명 도구**가 필요하며, 이것이 오늘날까지도 이 문제가 풀리지 않는 근본적인 장벽입니다.

---

## 요약 및 마치며

- **EXPSPACE-완전** 문제들은 공간 위계 정리에 의해 다항 공간 및 다항 시간에 풀 수 없음이 완전히 입증된 **증명 가능하게 다루기 힘든 문제**들입니다.
- **$EQ_{\text{REX}\uparrow}$**는 이진수 거듭제곱을 정규식에 허용하여, NTM 격자판 검사를 다항식 크기 식으로 환원할 수 있게 됨으로써 EXPSPACE-완전임이 증명되었습니다.
- **오라클 튜링 머신**은 특정 언어의 포함 여부를 단 1단계 만에 공짜로 대답해 주는 가상의 블랙박스를 탑재한 컴퓨터 모델입니다.
- **베이커-기브스-솔로베이(BGS) 정리**는 오라클에 따라 P=NP 혹은 P$\neq$NP가 둘 다 가능함을 밝혀, 대각선 논법 등의 **상대화(Relativization) 기법으로는 P vs NP의 벽을 절대 넘을 수 없음**을 선언했습니다.

계산 이론의 가장 깊고 철학적인 경계선인 오라클의 장벽을 마주했습니다.

다음 23번째 강의 요약에서는 컴퓨터 과학이 결정론을 극복하기 위해 무작위성을 도입하는 확률적 연산의 세계, 복잡도 클래스 **BPP**에 대해 알아보겠습니다!
