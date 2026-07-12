---
title: "19. 게임, 일반화된 지리(Generalized Geography) 및 로그 공간(Logspace) 복잡도"
date: 2026-07-12T15:00:00+09:00
draft: false
tags: ["theory-of-computation", "mit-18.404", "complexity-theory", "games", "generalized-geography", "pspace-complete", "logspace"]
categories: ["theory-of-computation"]
description: "QBF 논리식을 두 플레이어의 대결로 묘사하는 포뮬러 게임(Formula Game)을 통해 게임과 복잡도의 긴밀한 연결 관계를 이해하고, Generalized Geography의 PSPACE-완전성 증명 및 입력 외에 O(log n) 작업 메모리만 사용하는 로그 공간 복잡도(L, NL)의 다양한 성질을 공부합니다."
---

지난 18편에서는 PSPACE = NPSPACE임을 증명하는 새비치 정리(Savitch's Theorem)와 PSPACE-완전(PSPACE-Complete) 문제의 대표격인 TQBF 문제에 대해 공부했습니다. 

이번 19번째 강의와 [강의 슬라이드](file:///Users/yeongjun/Develops/develop/static/references/theory-of-computation/lecture-19-games-generalized-geography.pdf)에서는 PSPACE의 또 다른 강력한 표현 도구인 **게임 이론(Game Theory)**과 그래프에서의 한붓그리기 끝말잇기 게임인 **일반화된 지리 게임(Generalized Geography)**, 그리고 선형 공간보다도 작은 메모리를 사용하는 극단적인 최적화의 세계인 **로그 공간 복잡도(Log space)**에 대해 알아보겠습니다.

---

## 1. 게임과 복잡도: 포뮬러 게임(The Formula Game)

복잡도 이론에서 PSPACE에 해당하는 문제들은 종종 **"두 플레이어가 번갈아가며 수를 두는 대칭적 게임"**의 형태를 띱니다. 승리하기 위한 필승 전략(Winning Strategy / Forced Win)이 존재하는지 묻는 문제가 다항 공간(PSPACE)의 본질과 어떻게 연결되는지 알아봅시다.

### 양화사(Quantifier)와 게임의 관계
우리는 QBF(Quantified Boolean Formula) 식 $\phi$가 참인지 묻는 TQBF 문제를 배웠습니다.
$$\phi = \exists x_1 \forall x_2 \exists x_3 \dots (\exists/\forall) x_k [\psi]$$

이 식의 논리 연산 구조는 정확히 두 명이 참여하는 게임의 형식을 띱니다.
- **플레이어 $\exists$ (Existential Player)**: 식의 전체 결과를 참(True)으로 만들기 위해 노력하는 플레이어입니다. 존재 한정기($\exists$)가 붙은 변수들의 참/거짓 값을 결정합니다.
- **플레이어 $\forall$ (Universal Player)**: 식의 결과를 거짓(False)으로 만들기 위해 방해하는 플레이어입니다. 모든 한정기($\forall$)가 붙은 변수들의 참/거짓 값을 결정합니다.

두 플레이어는 식에 나타난 한정기의 순서대로 번갈아가며 변수의 값을 할당해 나갑니다. 모든 변수의 대입이 끝났을 때:
- 식 $\psi$의 최종 연산 결과가 참(True)이면 **플레이어 $\exists$**가 승리합니다.
- 최종 결과가 거짓(False)이면 **플레이어 $\forall$**가 승리합니다.

> **핵심 클레임 (Claim)**
> **"플레이어 $\exists$가 상대방이 어떤 수를 두든 항상 이길 수 있는 필승 전략(Forced Win)을 가진다"**는 사실은 **"QBF 식 $\phi$가 수학적으로 참(True)이다"**라는 말과 완전히 동치입니다.
> 
> $$\{ \langle \phi \rangle \mid \text{포뮬러 게임에서 플레이어 } \exists\text{가 필승 전략을 가진다} \} = \text{TQBF}$$

이 포뮬러 게임을 통해 우리는 복잡한 논리 기호의 연산을 '턴제 게임의 필승 경로 탐색' 문제로 직관적으로 해석할 수 있게 됩니다.

---

## 2. 일반화된 지리 게임(Generalized Geography, GG)

포뮬러 게임의 강력한 게임적 직관을 그래프 이론에 적용하여, 지리 문제 해결의 복잡도를 알아보겠습니다.

### A. 게임 룰
실제 '지리 게임(Geography Game)'은 끝말잇기와 비슷합니다. (예: Boston ➔ Nebraska ➔ Arkansas ➔ ...).
이를 일반화한 **일반화된 지리 게임(Generalized Geography)**은 다음과 같이 유향 그래프 상에서 진행됩니다.

1. 임의의 유향 그래프 $G$와 시작 노드 $a$가 주어집니다.
2. 두 플레이어(Player I, Player II)가 번갈아 가며 노드를 선택하여 하나의 단순 경로(Simple Path)를 만들어 나갑니다.
3. **가장 중요한 규칙**: 이미 경로에 포함되어 방문한 노드는 **재방문할 수 없습니다 (No repeats allowed)**.
4. 자기 차례에 갈 수 있는 이웃 노드가 없어 **더 이상 이동할 수 없게 된(Stuck) 플레이어가 패배**합니다.

> **Check-in 19.1: 아래와 같은 그래프 G에서 시작 노드 a가 주어졌을 때 필승 전략을 가지는 플레이어는 누구인가?**
> - **구조**: $a$에서 두 노드(상, 하)로 갈 수 있고, 상/하 노드는 서로를 거쳐 우측 단말 노드로 수렴하는 형태입니다.
> - **해설**: Player I이 $a$에서 어디로 이동하든, Player II는 그 즉시 우측 단말 노드로 선점하여 이동해 버릴 수 있습니다. 그러면 Player I은 경로가 막혀(Stuck) 첫 턴 만에 패배하게 됩니다. 따라서 이 게임의 승자는 항상 **Player II**가 됩니다.

$$\text{GG} = \{ \langle G, a \rangle \mid G\text{에서 시작점 } a\text{로 게임을 시작할 때, Player I이 필승 전략을 가진다} \}$$

### B. GG는 PSPACE-완전(PSPACE-complete)이다
- **GG ∈ PSPACE**: 재귀적으로 한 단계씩 모든 가능한 다음 수를 탐색하며 깊이 우선 탐색(DFS)을 활용하면, 게임 트리를 공간 재사용 방식으로 $O(n^2)$ 공간 내에 완벽히 탐색할 수 있습니다.
- **$\text{TQBF} \le_{\text{P}} \text{GG}$**: QBF의 포뮬러 게임을 일반화된 지리 게임의 그래프 구조로 환원(Reduction)하여 하한선을 증명합니다.

### C. 환원 가젯(Gadget)의 구성 방식
QBF 논리식 $\phi = \exists x_1 \forall x_2 \exists x_3 \dots [c_1 \wedge c_2 \wedge \dots \wedge c_k]$ 가 주어졌을 때, 그래프 $G$를 구성하는 핵심 원리는 다음과 같습니다.

#### 1. 변수 선택부 (Variable selection Gadget)
각 변수 $x_i$에 대해 아래와 같이 갈림길 노드를 만듭니다.

```
       [ x_i 선택 노드 ]
        /            \
    [ x_i = T ]    [ x_i = F ]
        \            /
       [ x_i+1 선택 노드 ]
```

- 만약 $x_i$가 $\exists$이면 Player I(식의 참을 원하는 사람)이 갈림길 중 하나를 선택하여 경로를 진행합니다.
- 만약 $x_i$가 $\forall$이면 Player II(식의 거짓을 원하는 사람)가 갈림길 중 하나를 선택하여 경로를 진행합니다.
- 이 선택 과정을 통해 자연스럽게 변수의 참/거짓 값 할당이 결정되며, 방문된 노드($x_i = \text{True}$ 혹은 $\text{False}$)는 규칙에 의해 게임에서 두 번 다시 밟을 수 없는 비활성 노드가 됩니다.

#### 2. 검증 대결부 (Endgame Gadget)
변수 대입이 모두 끝나면, 경로는 "검증 단계"로 돌입합니다.

1. **Player II의 차례**: Player II는 $\phi$가 거짓이라고 우기고 있으므로, "그 대입 값으로는 $c_j$ 절을 만족하지 못한다!"라고 주장하며 절 노드 $c_j$ 중 하나를 골라 들어갑니다.
2. **Player I의 차례**: Player I은 $c_j$가 거짓이 아니라고 주장해야 합니다. 따라서 절 $c_j$ 안의 리터럴 중 **참(True)으로 설정된 변수 노드**를 선택해 이동합니다.
3. **거짓말 탐지 메커니즘**:
   - 만약 Player I이 **진짜 참인 리터럴**을 골랐다면, 그 변수 노드는 앞의 '변수 선택 단계'에서 이미 지나갔던 노드입니다. 규칙상 이미 방문한 노드는 갈 수 없으므로, 다음 차례인 **Player II가 경로가 막혀(Stuck) 패배**하게 됩니다. (즉, 참이 입증되어 Player I 승리)
   - 만약 Player I이 **거짓인 리터럴**을 골라 억지를 부렸다면, 그 변수 노드는 아직 방문되지 않은 노드입니다. 따라서 Player II가 그 노드로 이동할 수 있으며, 그 직후 갈 곳이 없는 **Player I이 경로가 막혀 패배**합니다.

이 가젯들은 변수 수와 절 수에 비례하는 다항 시간 내에 손쉽게 만들어지므로 환원성이 증명됩니다. 이로써 **Generalized Geography는 대표적인 PSPACE-완전 문제**로 규명됩니다.

---

## 3. 로그 공간 복잡도 (Logspace: L과 NL)

다항 공간 PSPACE의 경계를 넘어, 메모리 절약의 극단인 **선형 미만 공간(Sublinear Space)**을 탐구해 보겠습니다.

### A. 2-테이프 튜링 머신 모델
입력의 크기가 $n$일 때 $O(\log n)$ 메모리만 사용하고자 할 때, 입력 데이터를 보관하는 것만으로 이미 $n$개의 공간이 소비되어 모순이 발생합니다.
따라서 로그 공간 복잡도를 정의할 때는 다음과 같이 역할을 분리한 **2-테이프 튜링 머신**을 표준 하드웨어 모델로 삼습니다.

1. **입력 테이프 (Input Tape)**: 입력 데이터를 읽기만 할 수 있는 **Read-only 테이프**입니다. 이 테이프가 차지하는 셀의 개수는 공간 복잡도 측정에서 완전히 배제합니다.
2. **작업 테이프 (Work Tape)**: 읽고 쓰기가 모두 가능한 **Read/Write 테이프**입니다. **오직 이 작업 테이프에서 사용한 셀의 개수만을 공간 복잡도로 인정합니다.**

> **로그 공간의 힘: 포인터(Pointer)의 활용**
> 길이 $n$의 입력 데이터의 임의의 위치를 가리키는 포인터(Index) 값은 $0$부터 $n$까지의 숫자입니다. 이 숫자를 이진수로 메모리에 기록하려면 오직 $\log_2 n$ 비트만 있으면 됩니다. 즉, **작업 테이프에서 $O(\log n)$ 공간을 쓸 수 있다는 것은 입력의 위치를 가리키는 상수(Constant) 개수의 포인터를 조작할 수 있다**는 막강한 실용적 의미를 가집니다.

- **$\text{L}$**: $O(\log n)$ 작업 공간을 사용하는 결정적 2-테이프 TM으로 판정 가능한 언어들의 집합.
  - 예: 회문(Palindrome) 판별 문제 $\{ w w^R \mid w \in \Sigma^* \}$. 입력의 시작점과 끝점을 가리키는 포인터 2개만 유지하고 서로 좁혀가며 검사하면 되므로 $\text{L}$에 속합니다.
- **$\text{NL}$**: $O(\log n)$ 작업 공간을 사용하는 비결정적 2-테이프 TM으로 판정 가능한 언어들의 집합.
  - 예: 경로 존재 여부를 묻는 $\text{PATH}$ 문제. 현재 방문 중인 노드의 번호(포인터, 크기 $O(\log n)$) 하나만 저장해 두고, 다음 노드로 비결정적으로 점프하며 타깃 노드에 도달하는지 확인하면 되므로 $\text{NL}$에 속합니다.

---

## 4. 로그 공간의 주요 수학적 성질

로그 공간 복잡도 클래스는 다항 시간 클래스 P와 다음과 같은 깊은 관계를 맺고 있습니다.

### 정리 1: $\text{L} \subseteq \text{P}$
- **증명**: NTM이 사용하는 공간이 $c \log n$일 때 발생할 수 있는 고유한 상태(Configuration)의 총개수를 헤아려 봅시다.
  $$\text{Configuration 수} = (\text{상태 수 } |Q|) \times (\text{입력 헤드 위치 } n) \times (\text{작업 헤드 위치 } c \log n) \times (\text{알파벳 조합 수 } d^{c \log n})$$
  여기서 $d^{c \log n} = n^{c \log d}$ 이므로, 전체 식을 곱하면 $O(n \cdot \log n \cdot n^k) = O(n^{k+1})$ 과 같이 **다항식 개수**가 도출됩니다.
  결정론적 판정기는 상태를 중복해서 밟을 수 없으므로 다항식 수준의 단계 수 내에 무조건 끝나야 합니다. 따라서 $\text{L} \subseteq \text{P}$ 입니다.

### 정리 2: $\text{NL} \subseteq \text{P}$
- **증명**: 공간 $O(\log n)$을 쓰는 비결정적 머신 $M$의 모든 상태(Configuration)를 노드로 삼고, 한 단계에 전이 가능한 관계를 간선으로 삼는 **상태 그래프(Configuration Graph) $G_{M,w}$**를 구축합니다.
  - 이 그래프의 노드 개수는 정리 1에 의해 다항식 수($O(n^k)$)입니다.
  - 이 다항식 크기의 그래프 상에서 너비 우선 탐색(BFS)이나 깊이 우선 탐색(DFS)을 돌려 시작 상태에서 수락 상태로 가는 경로가 존재하는지 판정합니다.
  - BFS/DFS 알고리즘은 노드 수에 대해 다항 시간에 돌릴 수 있으므로, $\text{NL}$에 속한 임의의 언어는 항상 다항 시간 내에 판정 가능합니다. 즉, **$\text{NL} \subseteq \text{P}$**가 증명됩니다.

### Savitch 정리의 적용: $\text{NL} \subseteq \text{SPACE}(\log^2 n)$
새비치 정리($\text{NSPACE}(f(n)) \subseteq \text{SPACE}(f^2(n))$)는 로그 공간에도 예외 없이 적용됩니다. 

> **Check-in 19.3: PATH ∈ NL 이다. PATH 문제의 결정적 공간 복잡도의 상한선 중 가장 잘 알려진 것은 무엇인가?**
> - **정답**: **$\text{SPACE}(\log^2 n)$**
> - **해설**: $\text{PATH}$가 $\text{NL}$에 포함되므로 새비치 정리를 그대로 적용하면 비결정론 $O(\log n)$ 공간은 결정론적 $O(\log^2 n)$ 공간으로 무조건 시뮬레이션될 수 있습니다.

---

## 요약 및 마치며

- **포뮬러 게임**을 통해 양화사 식 TQBF 문제를 플레이어 $\exists$와 $\forall$의 승패 구도로 해석하여 게임과 계산 복잡도의 연결 고리를 확립했습니다.
- **일반화된 지리 게임(Generalized Geography)**은 중복 방문 금지 규칙을 통해 포뮬러 게임을 시뮬레이션하여 **PSPACE-완전성**을 입증하는 훌륭한 모델이 됩니다.
- **로그 공간 복잡도(L, NL)**는 입력 데이터를 제외하고 상수 개의 포인터($O(\log n)$) 수준의 임시 공간만 사용하여 문제를 해결하는 지극히 타이트한 클래스입니다.
- 상태 분석을 통해 $\text{L} \subseteq \text{NL} \subseteq \text{P} \subseteq \text{PSPACE}$의 포함 관계가 성립하며, 새비치 정리에 의해 $\text{NL} \subseteq \text{SPACE}(\log^2 n)$ 임이 보장됩니다.

시간과 공간, 그리고 게임을 거쳐 메모리 절약의 극단인 Logspace까지 섭렵하며 복잡도 계층을 더욱 촘촘히 엮어냈습니다. 다음 20번째 강의 요약에서는 로그 공간 비결정론의 한계를 규정하는 **클래스 L, NL의 보집합 관계(NL = coNL)와 이모-스옙세니 정리(Immerman-Szelepcsényi Theorem)**에 대해 자세히 학습해 보겠습니다!
