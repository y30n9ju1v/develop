---
title: "9. 매핑 환원(Mapping Reducibility)과 프로그램 분석의 한계"
date: 2026-07-12T08:00:00+09:00
draft: false
tags: ["theory-of-computation", "mit-18.404", "reducibility", "mapping-reduction", "unrecognizability"]
categories: ["theory-of-computation"]
description: "어려운 문제를 변환하여 해결하는 환원(Reduction)의 형식 정의인 매핑 환원(Mapping Reducibility), 튜링 머신 공백성($E_{\\text{TM}}$) 및 동치성($EQ_{\\text{TM}}$) 문제의 판정·인식 불가능성 증명을 학습합니다."
---

지난 8편에서는 게오르크 칸토어의 대각선 논법을 바탕으로 컴퓨터가 풀 수 없는 문제인 **수락 문제($A_{\text{TM}}$)**와 **정지 문제($HALT_{\text{TM}}$)**의 판정 불가능성(Undecidability)을 증명했습니다.

이때 한 문제를 다른 문제로 변형하여 해결하는 **환원(Reduction)**이라는 개념을 직관적으로 사용했습니다. 

이번 9번째 강의와 [강의 슬라이드](file:///Users/yeongjun/Develops/develop/static/references/theory-of-computation/lecture-09-reducibility.pdf)에서는 환원을 수학적으로 엄밀히 규정한 **매핑 환원(Mapping Reducibility)**에 대해 배우고, 이를 이용해 튜링 머신 자체를 분석하는 정적 분석 문제들이 얼마나 극단적으로 계산 불가능한 영역에 있는지를 증명합니다.

---

## 1. 환원의 또 다른 응용: 공백성 문제 ($E_{\text{TM}}$)의 판정 불가능성

환원의 개념을 복습하기 위해, 튜링 머신의 언어가 완전히 비어 있는지 검사하는 **공백성 문제($E_{\text{TM}}$)**를 증명해 봅시다.

$$E_{\text{TM}} = \{ \langle M \rangle \mid M\text{은 튜링 머신이고, } L(M) = \emptyset \}$$

이 문제가 판정 가능하다고 가정하고 판정기 $R$이 존재한다고 합시다. 우리는 이 $R$을 부품으로 사용하여 판정 불가능한 수락 문제($A_{\text{TM}}$)를 해결하는 판정기 $S$를 만들 수 있습니다.

### 판정기 $S$의 설계
$$S = \text{"인풋 } \langle M, w \rangle \text{에 대해:}$$
1. 다음과 같이 작동하는 새로운 튜링 머신 $M_w$를 테이프 위에 임시로 조립한다.
   $$M_w = \text{"인풋 } x\text{에 대해:}$$
   1. 만약 $x \neq w$ 이면, **거부**한다.
   2. 만약 $x = w$ 이면, 실제 $M$을 $w$에 대해 시뮬레이션하고 $M$의 결과에 따라 수락/거부한다."
2. 공백성 판정기 $R$에 $\langle M_w \rangle$를 넣어 실행한다.
3. $R$이 "비어 있음(YES)"을 반환하면, $M$이 $w$를 수락하지 않는다는 의미이므로 $S$는 **거부**한다.
   $R$이 "비어 있지 않음(NO)"을 반환하면, $M$이 $w$를 수락한다는 의미이므로 $S$는 **수락**한다."

기계 $M_w$는 입력값 $x$가 우리가 알고자 하는 $w$와 다르면 무조건 거부하므로, $M$이 $w$를 수락할 때만 $L(M_w) = \{w\}$ (비어 있지 않음)이 되고, $M$이 $w$를 거부하거나 루프를 돌면 $L(M_w) = \emptyset$ (비어 있음)이 됩니다.

따라서 $R$이 있으면 $A_{\text{TM}}$을 판정할 수 있어 모순이 발생하므로, $E_{\text{TM}}$은 **판정 불가능(Undecidable)**합니다.

---

## 2. 매핑 환원 (Mapping Reducibility) 이란?

수학자들은 환원의 과정을 형식화하기 위해 **매핑 환원**을 정의했습니다.

### 계산 가능한 함수 (Computable Function)
어떤 함수 $f: \Sigma^* \to \Sigma^*$가 있을 때, 튜링 머신 $F$가 입력 $w$에 대해 계산을 시작해 테이프 위에 $f(w)$만 남겨두고 정지한다면, 이 함수 $f$를 **계산 가능한 함수**라고 부릅니다.

### 매핑 환원성 ($A \le_m B$)
> 두 언어 $A$와 $B$가 있을 때, 모든 문자열 $w$에 대해 다음 조건을 만족하는 계산 가능한 함수 $f$가 존재한다면, **$A$는 $B$로 매핑 환원 가능하다($A \le_m B$)**고 정의합니다.
> $$w \in A \iff f(w) \in B$$

```
   w ───[ f ]───> f(w)
   in             in
   A              B
```

매핑 환원은 매우 직관적입니다. $A$에 속하는 문자열을 $f$ 함수에 넣으면 무조건 $B$에 속하는 문자열로 바뀌고, $A$에 속하지 않는 문자열은 $B$에 속하지 않는 문자열로 바뀝니다.

### 매핑 환원의 성질
1. $A \le_m B$ 이고 $B$가 판정 가능(Decidable)하면, $A$도 판정 가능하다.
2. $A \le_m B$ 이고 $A$가 판정 불가능(Undecidable)하면, $B$도 판정 불가능하다.
3. $A \le_m B$ 이고 $B$가 인식 가능(Turing-Recognizable)하면, $A$도 인식 가능하다.
4. $A \le_m B$ 이고 $A$가 인식 불가능(Turing-Unrecognizable)하면, $B$도 인식 불가능하다.

### 주의: 매핑 환원은 방향이 있다

$A \le_m B$가 성립한다고 해서 그 역인 $B \le_m A$나, $A \le_m \overline{A}$ 같은 관계가 자동으로 성립하는 것은 아닙니다. 매핑 환원은 "$A$의 답을 $B$의 답으로 그대로 번역해 주는 함수 $f$가 존재하는가"를 묻는 일방향적인 관계이기 때문에, 실제로 $A_{\text{TM}} \le_m \overline{A_{\text{TM}}}$은 성립하지 않습니다(만약 성립한다면 $A_{\text{TM}}$이 인식 가능하면서 동시에 $\overline{A_{\text{TM}}}$도 인식 가능해져야 하는데, 이는 앞서 증명한 $\overline{A_{\text{TM}}}$의 인식 불가능성과 모순됩니다). 즉, 환원이 어느 방향으로 성립하는지는 매번 별도로 증명해야 하는 사실입니다.

---

## 3. $E_{\text{TM}}$의 인식 불가능성 증명

매핑 환원성 4번 성질을 이용하면 어떤 문제가 아예 프로그램 설계조차 불가능한 **인식 불가능(Unrecognizable)** 영역에 있음을 증명할 수 있습니다.

### 정리: $E_{\text{TM}}$은 튜링 인식 불가능하다.
- **증명**: 우리는 이미 인식 불가능하다고 증명된 $\overline{A_{\text{TM}}}$을 $E_{\text{TM}}$으로 매핑 환원시킬 것입니다 ($\overline{A_{\text{TM}}} \le_m E_{\text{TM}}$).
- **환원 함수 $f$ 설계**: 입력 $\langle M, w \rangle$를 받아 위에서 정의했던 기계인 $\langle M_w \rangle$의 코드를 출력하는 함수 $f$를 만듭니다.
  $$f(\langle M, w \rangle) = \langle M_w \rangle$$
- **조건 검증**:
  - $\langle M, w \rangle \in \overline{A_{\text{TM}}}$ (즉, $M$이 $w$를 수락하지 않음)
  - $\iff L(M_w) = \emptyset$ (오직 $w$만 수락할 기회를 주었는데 그것마저 거절당함)
  - $\iff \langle M_w \rangle \in E_{\text{TM}}$
- $w \in A \iff f(w) \in B$의 매핑 환원 정의를 완벽히 충족합니다.
- 따라서 $\overline{A_{\text{TM}}}$이 인식 불가능하므로, **$E_{\text{TM}}$ 역시 튜링 인식 불가능**합니다.

---

## 4. 극단적인 계산 불가능: 동치성 문제 ($EQ_{\text{TM}}$)

두 튜링 머신(프로그램)이 완벽히 같은 동작을 하는지 검사하는 **동치성 문제($EQ_{\text{TM}}$)**는 계산 이론의 심연을 보여줍니다.

$$EQ_{\text{TM}} = \{ \langle M_1, M_2 \rangle \mid M_1, M_2\text{는 튜링 머신이고, } L(M_1) = L(M_2) \}$$

이 문제는 판정이 안 될 뿐만 아니라, **문제 자체($EQ_{\text{TM}}$)와 그 여집합($\overline{EQ_{\text{TM}}}$)이 둘 다 튜링 인식조차 불가능**합니다.

### 증명 스케치
1. **$\overline{A_{\text{TM}}} \le_m EQ_{\text{TM}}$ 임을 증명**:
   - 입력 $\langle M, w \rangle$를 받아 두 튜링 머신 $\langle T_w, T_{\text{reject}} \rangle$을 만듭니다.
   - $T_{\text{reject}}$: 모든 입력을 거부하는 멍청한 기계 ($L(T_{\text{reject}}) = \emptyset$).
   - $T_w$: 자신의 입력은 무시하고 무조건 내부적으로 $M$에 $w$를 대입해 시뮬레이션하는 기계. ($M$이 $w$를 수락하면 모든 입력을 수락하므로 $L(T_w) = \Sigma^*$, 수락하지 않으면 $L(T_w) = \emptyset$).
   - 대입해 보면, $M$이 $w$를 수락하지 않음 $\iff L(T_w) = \emptyset = L(T_{\text{reject}}) \iff \langle T_w, T_{\text{reject}} \rangle \in EQ_{\text{TM}}$.
   - 매핑 환원이 성립하므로, **$EQ_{\text{TM}}$은 인식 불가능**합니다.

2. **$\overline{A_{\text{TM}}} \le_m \overline{EQ_{\text{TM}}}$ 임을 증명**:
   - 이번에는 $T_{\text{reject}}$ 대신 모든 입력을 수락하는 $T_{\text{accept}}$ ($L(T_{\text{accept}}) = \Sigma^*$)를 짝으로 지어줍니다.
   - 대입해 보면, $M$이 $w$를 수락하지 않음 $\iff L(T_w) = \emptyset \neq \Sigma^* = L(T_{\text{accept}}) \iff \langle T_w, T_{\text{accept}} \rangle \in \overline{EQ_{\text{TM}}}$.
   - 매핑 환원이 성립하므로, **$\overline{EQ_{\text{TM}}}$ 역시 인식 불가능**합니다.

### 이 결과가 말해주는 것
두 프로그램이 완벽히 같은지($EQ_{\text{TM}}$) 검사하는 문제는, 같은 것을 골라내는 일도(Recognize), 다른 것을 골라내는 일도($\overline{EQ_{\text{TM}}}$) 프로그램화할 수 없는 **극단적인 난제**임을 수학적으로 보여줍니다.

---

## 요약 및 마치며

- **$E_{\text{TM}}$**은 수락 문제를 공백성 문제로 변환(환원)함으로써 판정 불가능함이 증명됩니다.
- **매핑 환원($A \le_m B$)**은 계산 가능한 변환 함수 $f$를 통해 문제를 직접 일대일 대응시켜 난이도를 비교하는 엄밀한 수학적 도구입니다.
- 매핑 환원을 통해 $\overline{A_{\text{TM}}}$이 $E_{\text{TM}}$으로 환원됨을 보여 **$E_{\text{TM}}$의 튜링 인식 불가능성**을 증명했습니다.
- **$EQ_{\text{TM}}$**과 그 여집합 **$\overline{EQ_{\text{TM}}}$**은 둘 다 튜링 인식조차 불가능하여, 정적 프로그램 분석의 한계가 얼마나 거대한지 확인했습니다.

현대 정적 분석기나 컴파일러 최적화 도구들이 "두 프로그램이 완전히 동일한 일을 하는지"를 프로그램 수준에서 자동으로 검사할 수 없는 근본적인 이유가 여기에 있습니다. 

다음 10번째 강의 요약에서는 계산 이론의 또 다른 거대한 보편 정리이자, 튜링 머신의 성질에 대한 질문들이 전부 판정 불가능함을 선언하는 **라이스 정리(Rice's Theorem)**와 **선형 유계 오토마타(LBA)**에 대해 알아보겠습니다!
