---
title: "2. 하향식 구문 분석: CFG, 재귀 하강, LL(1)"
date: 2026-07-14T00:00:00+09:00
draft: false
tags: ["compilers", "mit-6035", "parsing", "cfg", "ll1", "recursive-descent"]
categories: ["programming"]
description: "토큰 나열이 문법적으로 올바른지 판단하고 그 구조를 트리로 세우는 구문 분석을, 문맥 자유 문법(CFG)과 재귀 하강 파서, 그리고 예측 파싱 테이블을 쓰는 LL(1) 방식으로 정리합니다."
---

[1편](01-lexical-analysis/)에서 `if (n == 0) { return 1; }`이 `IF LPAREN ID EQEQ INT RPAREN LBRACE RETURN INT SEMI RBRACE`라는 토큰 나열로 바뀌었습니다. 이 글은 이 토큰 나열을 받아 "문법적으로 올바른 프로그램인가"를 판단하고, 그 문법 구조를 트리로 세우는 **구문 분석(Parsing)**의 첫 번째 방식 — 위에서 아래로 트리를 만들어가는 **하향식(Top-down) 파싱**을 다룹니다.

---

## 1. 토큰 나열의 문법을 정의하는 언어: 문맥 자유 문법(CFG)

[1편](01-lexical-analysis/)의 정규 표현식이 토큰 하나의 모양을 정의했다면, 이번엔 토큰들이 어떤 순서로 나와야 올바른 프로그램이 되는지를 정의해야 합니다. 정규 표현식은 이 일에 부족합니다 — `(` 개수와 `)` 개수가 같아야 한다는 규칙조차 정규 표현식으로는 표현할 수 없습니다(중첩 깊이를 셀 방법이 없기 때문입니다). 이 표현력의 문제를 **문맥 자유 문법(Context-Free Grammar, CFG)**이 해결합니다.

MiniLang의 일부를 CFG로 적으면 이렇습니다.

```
Stmt   → IF LPAREN Expr RPAREN Block ELSE Block
       | RETURN Expr SEMI

Block  → LBRACE Stmt* RBRACE

Expr   → Expr STAR Expr
       | Expr MINUS Expr
       | Expr EQEQ Expr
       | ID
       | INT
       | ID LPAREN Expr RPAREN
```

`Expr → Expr STAR Expr`처럼 규칙이 자기 자신을 참조할 수 있다는 점이 정규 표현식과의 결정적 차이입니다 — 이 **재귀** 덕분에 `n * fact(n - 1)`처럼 임의로 깊게 중첩된 식도 표현할 수 있습니다.

---

## 2. CFG로 파스 트리 만들기

`n == 0`이라는 식을 위 문법으로 유도해보면, `Expr → Expr EQEQ Expr → ID EQEQ INT`라는 유도 과정이 나오고, 이를 트리로 그리면 이렇게 됩니다.

```
        Expr
      /  |   \
   Expr EQEQ Expr
    |          |
    ID        INT
   (n)         (0)
```

이 트리가 **파스 트리(Parse Tree)**입니다. [1편](01-lexical-analysis/)의 토큰 나열이 평평한 리스트였다면, 파스 트리는 그 토큰들 사이의 **구조적 관계**(무엇이 무엇의 하위 표현식인지)를 드러냅니다. 이 구조가 있어야 [4편](04-semantic-analysis/)에서 "이 식의 타입이 무엇인가"를 각 하위 노드부터 재귀적으로 계산할 수 있습니다.

---

## 3. 모호함: 같은 토큰 나열에 트리가 두 개 이상 나올 수 있다

`n - fact(n) * 2`라는 식을 앞의 문법으로 유도하면, 뺄셈을 먼저 묶을 수도, 곱셈을 먼저 묶을 수도 있어 트리가 **두 가지** 나옵니다.

```
트리 A (뺄셈이 바깥):        트리 B (곱셈이 바깥):
        Expr                        Expr
      /  |   \                    /  |   \
   Expr MINUS Expr           Expr STAR  Expr
    |          |   \          |    |     |
    n        Expr STAR Expr  (잘못됨: 전체가 곱셈으로 묶임 — n - fact(n)이 통째로 곱해짐)
             fact(n)   2
```

두 트리 중 트리 A(곱셈이 뺄셈보다 먼저 묶이는 것)가 우리가 의도한 산술 우선순위와 맞습니다. 이 문법은 **모호(Ambiguous)**합니다 — 같은 문자열에 두 개 이상의 파스 트리가 대응하기 때문입니다. 모호한 문법은 파서 입장에서 "어느 트리를 만들어야 할지" 결정할 수 없다는 실전 문제로 이어집니다.

### 우선순위와 결합 방향을 문법 구조 자체에 인코딩하기

이 모호함을 해소하는 표준 방법은, 연산자 우선순위 단계마다 별도의 non-terminal을 두는 것입니다.

```
Expr   → Expr MINUS Term | Term            (덧셈/뺄셈 단계 — 가장 느슨하게 묶임)
Term   → Term STAR Factor | Factor          (곱셈/나눗셈 단계 — 더 강하게 묶임)
Factor → ID | INT | ID LPAREN Expr RPAREN | LPAREN Expr RPAREN
```

`Term`이 `Factor`들을 먼저 묶고, 그 결과가 `Expr` 단계에서 다시 묶이므로, `n - fact(n) * 2`는 `fact(n) * 2`가 먼저 하나의 `Term`으로 묶인 뒤에야 `Expr` 단계에서 `n`과 뺄셈으로 묶입니다 — 문법의 계층 구조 자체가 우선순위를 강제하므로, 이제 파스 트리는 유일하게 정해집니다.

---

## 4. 재귀 하강 파서: 문법 규칙을 그대로 함수로

**재귀 하강(Recursive Descent)**은 CFG의 각 non-terminal을 함수 하나로 그대로 옮기는, 가장 직접적인 파서 구현 방식입니다.

```python
def parse_expr():
    left = parse_term()
    while peek() == MINUS:
        consume(MINUS)
        right = parse_term()
        left = Node("Expr", left, right)
    return left

def parse_term():
    left = parse_factor()
    while peek() == STAR:
        consume(STAR)
        right = parse_factor()
        left = Node("Term", left, right)
    return left

def parse_factor():
    if peek() == ID:
        name = consume(ID)
        if peek() == LPAREN:
            consume(LPAREN); arg = parse_expr(); consume(RPAREN)
            return Node("Call", name, arg)
        return Node("Var", name)
    elif peek() == INT:
        return Node("Const", consume(INT))
```

`parse_expr`이 `parse_term`을 호출하고, `parse_term`이 `parse_factor`를 호출하는 이 호출 순서 자체가 3절에서 정한 문법 계층(`Expr → Term → Factor`)을 그대로 반영합니다. `peek()`(다음 토큰을 미리 보되 소비하지 않음)로 "지금 어느 규칙을 적용해야 하는지"를 결정하는데, 이 결정이 **항상 유일하게** 내려질 수 있어야 재귀 하강이 성립합니다 — 이게 바로 다음 절의 주제입니다.

---

## 5. 재귀 하강이 실패하는 경우: 좌재귀와 예측 불가능성

재귀 하강은 강력하지만 모든 CFG에 적용할 수 있는 건 아닙니다. 두 가지 대표적인 함정이 있습니다.

**좌재귀(Left Recursion)**: `Expr → Expr MINUS Term`처럼 규칙의 맨 앞에 자기 자신이 나오는 경우, `parse_expr`이 자기 자신을 맨 처음에 호출하려 하면서 토큰을 하나도 소비하지 않고 무한 재귀에 빠집니다. 4절의 구현이 `while` 루프로 이 문제를 우회했다는 걸 눈치채셨을 텐데, 이건 좌재귀 규칙을 반복문으로 바꿔 쓰는 표준 변형입니다 — 모든 좌재귀 문법이 이렇게 간단히 바뀌는 건 아니고, 일반적인 좌재귀 제거 알고리즘이 따로 있습니다.

**예측 불가능성**: `peek()`으로 다음 토큰 하나만 보고 어느 규칙을 적용할지 정해야 하는데, 두 규칙이 같은 토큰으로 시작한다면 하나만 미리 보는 것으로는 결정할 수 없습니다. 예를 들어 `Stmt → IF ... | ID SEMI`(단순 대입문)처럼 서로 다른 토큰으로 시작하면 문제가 없지만, 만약 두 대안이 같은 시작 토큰을 공유한다면(예: `ID LPAREN` 시작이 함수 호출인지 다른 구성 요소인지) 토큰 하나만으로는 구별이 안 됩니다.

이 "다음 토큰 하나만 보고 결정할 수 있는가"라는 성질을 형식화한 게 **LL(1)** 문법입니다 — 왼쪽에서 오른쪽으로 입력을 읽고(Left-to-right), 왼쪽 유도를 하며(Leftmost derivation), 앞을 1개 토큰만 본다(1 lookahead)는 뜻입니다.

---

## 6. First/Follow 집합과 예측 파싱 테이블

재귀 하강을 손으로 짜는 대신, "이 non-terminal에서 이 토큰을 보면 어느 규칙을 적용해야 하는가"를 표로 미리 만들어두고 그 표를 그대로 따라가는 방식이 **예측 파싱(Predictive Parsing)**입니다. 이 표를 만들려면 두 집합을 계산해야 합니다.

- **First(X)**: non-terminal `X`가 유도할 수 있는 문자열이 시작될 수 있는 토큰들의 집합. `First(Factor) = {ID, INT, LPAREN}`.
- **Follow(X)**: `X` 바로 뒤에 나올 수 있는 토큰들의 집합. `Follow(Expr)`은 `Expr`이 쓰이는 문맥(예: `RPAREN` 직전, `SEMI` 직전)에 따라 정해집니다.

이 두 집합으로 예측 파싱 테이블을 채웁니다 — 행은 non-terminal, 열은 다음 토큰이고, 각 칸에 "이 조합이면 이 규칙을 적용하라"가 들어갑니다.

```
             ID              INT             LPAREN
Factor    Factor→ID      Factor→INT     Factor→LPAREN Expr RPAREN
```

파서는 스택에 non-terminal을 쌓아두고, 스택 맨 위와 다음 입력 토큰으로 이 표를 찾아 규칙을 적용하는 걸 반복합니다. 표의 어느 칸이 **두 개 이상의 규칙**으로 채워진다면, 그 문법은 LL(1)이 아니라는 뜻이고 — 이 경우가 바로 5절에서 다룬 "토큰 하나로는 예측 불가능한" 상황이 표 위에 구체적으로 드러난 것입니다.

---

## 7. MiniLang이 LL(1)로 충분한가

MiniLang의 `if`/`return`/함수 호출 정도의 문법은 대부분 LL(1)로 무리 없이 처리됩니다 — 각 문장이 서로 다른 키워드(`IF`, `RETURN`)로 시작하고, 3절에서 우선순위 계층을 나눠 좌재귀도 반복문으로 처리했기 때문입니다. 하지만 실제 프로그래밍 언어(C의 선언과 식 사이의 모호함, 표현식 문법의 복잡한 우선순위 단계)로 가면 LL(1)의 한계에 부딪히는 경우가 흔해지고, 이때 쓰는 게 다음 편에서 다룰 더 강력한 파싱 방식 — **상향식(Bottom-up) 파싱**입니다.

---

## 8. 정리

- **CFG**는 정규 표현식으로 표현할 수 없는 중첩 구조(괄호 짝, 우선순위 계층)를 표현하는 문법 정의 언어입니다.
- 문법이 **모호**하면 같은 토큰 나열에 여러 파스 트리가 대응하며, 연산자 우선순위 단계마다 non-terminal을 나누는 것으로 이 모호함을 해소할 수 있습니다.
- **재귀 하강** 파서는 CFG의 각 규칙을 함수 하나로 그대로 옮긴 구현이지만, **좌재귀**와 **다음 토큰 하나로 예측 불가능한 경우**에는 그대로 쓸 수 없습니다.
- **First/Follow 집합**으로 만든 **예측 파싱 테이블**이 "이 non-terminal에서 이 토큰을 보면 어느 규칙을 쓸지"를 명시적으로 정의하며, 표의 칸이 겹치면 그 문법은 **LL(1)**이 아닙니다.

다음 편에서는 하향식 파싱이 예측하지 못하는 문법까지 다루는 **상향식 파싱(LR)**을 다루고, `yacc`/`bison` 같은 파서 생성기가 실제로 어떻게 이 표를 자동으로 만들어내는지 확인합니다.
