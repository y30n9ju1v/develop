---
title: "4. 의미 분석: 심볼 테이블과 타입 검사"
date: 2026-07-14T00:00:00+09:00
draft: false
tags: ["compilers", "cs143", "semantic-analysis", "type-checking", "symbol-table", "scope"]
categories: ["programming"]
description: "구문적으로는 올바르지만 의미가 잘못된 프로그램(정의 안 된 변수, 타입 불일치)을 잡아내는 의미 분석을, 스코프별 심볼 테이블과 AST를 순회하는 타입 검사 규칙으로 정리합니다."
---

[2~3편](02-parsing-top-down/)에서 만든 파스 트리는 "문법적으로 올바른가"만 확인합니다. 하지만 `x + 1`이라는 식은 `x`가 정의되어 있지 않아도, `x`가 함수 타입이라도 문법적으로는 완벽합니다. 이 글은 파스 트리(정확히는 파스 트리에서 문법적 잡음을 걷어낸 **추상 구문 트리, AST**)를 받아 "이 프로그램이 실제로 말이 되는가"를 검사하는 **의미 분석(Semantic Analysis)**을 다룹니다.

---

## 1. 파스 트리에서 AST로: 필요한 구조만 남기기

[3편](03-parsing-bottom-up/)에서 `yacc` 규칙 옆의 액션이 파스 트리 노드를 만든다고 했는데, 실전에서는 파스 트리를 그대로 쓰지 않고 **추상 구문 트리(Abstract Syntax Tree, AST)**로 정제합니다. 예를 들어 `LPAREN Expr RPAREN`(괄호로 감싼 식)이라는 파스 트리 규칙은 괄호 토큰 자체를 트리에 남길 필요가 없습니다 — 괄호는 우선순위를 강제하기 위한 문법적 장치였을 뿐, 그 우선순위는 이미 트리의 중첩 구조 자체에 반영되어 있기 때문입니다.

```
파스 트리: (n - 1)                AST: (n - 1)
   Expr                              BinOp(-)
  / | \                              /    \
LPAREN Expr RPAREN     →         Var(n)  Const(1)
        |
       Expr
      / | \
   Var  MINUS Const
   (n)         (1)
```

AST는 이후 모든 단계(의미 분석, 코드 생성)가 실제로 다루는 자료구조입니다. MiniLang의 `fact` 함수는 이런 AST로 표현됩니다.

```
FuncDef("fact", ["n"],
  If(BinOp(==, Var("n"), Const(0)),
     Block([Return(Const(1))]),
     Block([Return(BinOp(*, Var("n"), Call("fact", [BinOp(-, Var("n"), Const(1))])))])))
```

---

## 2. 첫 번째 질문: 이 이름은 어디서 왔는가 (스코프와 심볼 테이블)

`fact` 함수 본문에서 `n`을 쓸 수 있는 건 `n`이 함수의 매개변수로 선언되어 있기 때문입니다. 만약 본문에서 `m`을 썼다면, 그건 어디에도 선언되지 않은 이름이므로 에러여야 합니다. 이 "이름이 지금 이 위치에서 유효한가"를 추적하는 자료구조가 **심볼 테이블(Symbol Table)**입니다.

```
심볼 테이블 (fact 함수 진입 시):
  n → { kind: parameter, type: Int }
```

스코프가 중첩되는 언어(블록마다 새 변수를 선언할 수 있는 경우)라면, 심볼 테이블도 스코프를 따라 중첩되어야 합니다. AST를 순회하며 새 블록에 들어갈 때 새 스코프를 열고, 블록을 나올 때 그 스코프를 닫는 식으로 구현합니다.

```python
def check_block(block, scopes):
    scopes.push_new_scope()          # 이 블록만의 새 스코프 시작
    for stmt in block.stmts:
        check_stmt(stmt, scopes)
    scopes.pop_scope()               # 블록이 끝나면 그 안에서 선언된 이름들은 사라짐

def check_var(name, scopes):
    for scope in reversed(scopes):   # 가장 안쪽 스코프부터 바깥쪽으로 찾음
        if name in scope:
            return scope[name]
    error(f"undefined variable: {name}")
```

`reversed(scopes)`로 안쪽부터 바깥쪽 순서로 찾는다는 게 중요합니다 — 이게 바로 "안쪽 블록에서 선언한 변수가 같은 이름의 바깥 변수를 가린다(shadowing)"는 규칙을 구현하는 부분입니다.

---

## 3. 두 번째 질문: 이 식의 결과는 무슨 타입인가 (타입 검사)

이름이 정의되어 있다는 걸 확인했다면, 다음은 **타입 검사(Type Checking)**입니다 — AST의 각 노드마다 "이 식은 어떤 타입의 값을 만들어내는가"를 계산하고, 그 계산 과정에서 규칙이 어긋나는 지점을 찾아냅니다. 이 계산은 AST를 재귀적으로 순회하며 진행됩니다 — 정확히 [2편](02-parsing-top-down/)의 재귀 하강 파서가 문법 규칙을 따라 함수를 호출했던 것과 같은 재귀 구조입니다.

```python
def type_of(expr, scopes):
    match expr:
        case Const(n):
            return Int
        case Var(name):
            return lookup(name, scopes).type
        case BinOp(op, left, right):
            lt = type_of(left, scopes)
            rt = type_of(right, scopes)
            if op in ["+", "-", "*"]:
                if lt != Int or rt != Int:
                    error(f"'{op}' requires Int operands, got {lt} and {rt}")
                return Int
            elif op == "==":
                if lt != rt:
                    error(f"cannot compare {lt} with {rt}")
                return Bool
        case Call(name, args):
            func_sig = lookup(name, scopes)
            if len(args) != len(func_sig.param_types):
                error(f"{name} expects {len(func_sig.param_types)} args, got {len(args)}")
            for arg, expected_type in zip(args, func_sig.param_types):
                if type_of(arg, scopes) != expected_type:
                    error(f"argument type mismatch in call to {name}")
            return func_sig.return_type
```

`BinOp(*, Var("n"), Call("fact", ...))`을 이 함수로 검사하는 과정을 따라가 보면:

1. `Var("n")`의 타입을 구함 → 심볼 테이블에서 `n`은 `Int` (2절)
2. `Call("fact", [...])`의 타입을 구함 → `fact`의 반환 타입을 심볼 테이블에서 찾음 → `Int`, 인자 개수와 타입도 함께 확인
3. 두 하위 타입이 모두 `Int`이므로, `*` 연산자 규칙에 따라 전체 타입도 `Int`

이렇게 **아래(잎, 상수/변수)에서부터 위(전체 식)로** 타입을 조립해나가는 방식을 상향식 타입 추론이라 부르는데, 이 방향이 AST의 구조와 자연스럽게 맞아떨어집니다 — 각 노드의 타입은 그 자식 노드들의 타입이 이미 계산된 뒤에야 결정할 수 있기 때문입니다.

---

## 4. 함수 자신을 호출하는 경우: 재귀 함수와 사전 등록

`fact` 함수 본문 안에서 `fact` 자신을 호출합니다. 만약 2절의 심볼 테이블을 "함수 본문을 검사하면서 그 함수 이름을 등록"하는 순서로 짠다면, 본문을 검사하는 시점에는 아직 `fact` 자신이 심볼 테이블에 없어 "정의되지 않은 함수"라는 잘못된 에러가 납니다.

이 문제는 프로그램의 모든 최상위 함수 시그니처(이름, 매개변수 타입, 반환 타입)를 **먼저 한 번 전부 훑어 심볼 테이블에 등록**하고, 그다음에 각 함수 본문을 검사하는 **두 단계 처리**로 해결합니다.

```
1단계: 모든 함수 선언을 훑어 시그니처만 등록
  fact: (Int) -> Int

2단계: 각 함수 본문을 실제로 타입 검사
  fact 본문을 검사할 때, fact 자신이 이미 심볼 테이블에 있으므로 재귀 호출이 정상 처리됨
```

이 두 단계 구조는 서로 다른 순서로 선언된 함수들이 서로를 호출하는 상호 재귀(mutual recursion)에도 그대로 적용됩니다 — 순서와 무관하게 먼저 전부 등록해두기 때문입니다.

---

## 5. `if`/`else` 두 분기의 타입이 다르면?

MiniLang의 `if (n == 0) { return 1; } else { return n * fact(n - 1); }`을 보면, 두 분기가 모두 `return`으로 끝나고 둘 다 `Int`를 반환합니다. 만약 한쪽이 `Int`를 반환하고 다른 쪽이 `Bool`을 반환한다면, 이 함수 전체의 반환 타입이 무엇인지 모호해집니다 — 이런 경우 타입 검사기는 두 분기의 타입을 비교해 일치하지 않으면 에러를 내거나(엄격한 언어), 두 타입을 모두 포괄하는 공통 타입을 찾으려 시도합니다(더 유연한 언어). MiniLang처럼 단순한 언어에서는 "두 분기의 반환 타입이 정확히 일치해야 한다"는 규칙으로 충분합니다.

---

## 6. 의미 분석이 끝나면 무엇이 남는가

의미 분석을 통과한 AST는 이제 다음 두 가지를 보장합니다.

1. **모든 이름이 스코프 규칙에 맞게 정의되어 있다** (2절)
2. **모든 식과 연산이 타입 규칙을 지킨다** (3~5절)

이 보장이 왜 중요하냐면, [5편](05-intermediate-representation-stack-machine/)부터 시작하는 코드 생성 단계는 **더 이상 이 검사를 반복하지 않기 때문**입니다 — 코드 생성기는 "이 변수가 존재하고, 이 연산의 피연산자 타입이 맞다"는 걸 이미 보장된 사실로 가정하고 곧바로 기계어에 대응하는 코드를 만드는 데 집중합니다. 의미 분석이 이 보장을 확실히 하지 못하면, 그 오류는 코드 생성 단계에서 잡히지 않고 그대로 실행 가능한(하지만 잘못된) 코드로 새어나갑니다.

---

## 7. 정리

- 의미 분석은 파스 트리를 정제한 **AST** 위에서, 문법적으로는 옳지만 **의미적으로 잘못된** 프로그램(미정의 변수, 타입 불일치)을 잡아냅니다.
- **심볼 테이블**은 스코프를 따라 중첩되며, 이름을 찾을 때 안쪽 스코프부터 바깥쪽으로 검색해 shadowing을 구현합니다.
- **타입 검사**는 AST를 재귀적으로 순회하며 각 노드의 타입을 자식 노드로부터 상향식으로 조립합니다.
- 재귀·상호 재귀 함수를 다루려면 함수 시그니처를 **본문 검사 전에 미리 전부 등록**하는 두 단계 처리가 필요합니다.
- 의미 분석이 통과시킨 AST는 이후 단계가 "이름과 타입이 전부 올바르다"는 사실을 그대로 신뢰하고 진행할 수 있게 해주는 전제 조건입니다.

다음 편에서는 이렇게 타입 검사까지 끝난 AST를 받아, 실행 가능한 코드로 낮추는 첫 단계 — 스택 기반 추상 머신을 타겟으로 하는 **중간 표현과 코드 생성**을 다룹니다.
