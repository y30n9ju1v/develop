---
title: "2.1. 데이터 추상화 입문 (Introduction to Data Abstraction)"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["sicp", "lean", "lean4", "scheme", "data-abstraction", "structures"]
categories: ["programming"]
description: "SICP 2장 1절의 아이디어(데이터 추상화, 유리수 연산, pair, 추상화 장벽, 데이터의 의미, 구간 연산)를 Lean 4의 구조체와 곱 타입으로 다시 짜 봅니다."
---

Chapter 1 was entirely about procedures — how to name them, compose them, pass them around. [Chapter 2](../1-3-higher-order-procedures/) opens by asking the same question of *data*: can we abstract away the details of how a compound value is built, so that the code using it only ever talks about "what it means to be a rational number," never "how a rational number happens to be stored"? SICP calls this discipline *data abstraction*, and this post follows its first section in Lean, where — unlike Scheme's single all-purpose `cons` cell — the language hands us more than one way to draw that boundary.

1장은 온전히 절차에 관한 것이었습니다 — 이름 붙이는 법, 조합하는 법, 넘겨주는 법. [2장](../1-3-higher-order-procedures/)은 같은 질문을 *데이터*에 던지며 시작합니다 — 복합 값이 실제로 어떻게 만들어지는지의 세부 사항을 감춰서, 그것을 쓰는 코드가 "유리수라는 게 무엇을 의미하는지"만 이야기하고 "유리수가 어떻게 저장되어 있는지"는 전혀 신경 쓰지 않게 만들 수 있을까요? SICP는 이 원칙을 *데이터 추상화(data abstraction)*라고 부르는데, 이 글은 그 첫 절을 Lean에서 따라가 봅니다. Scheme의 만능 `cons` 셀 하나와 달리, Lean은 이 경계를 긋는 방법을 하나 이상 손에 쥐여줍니다.

The general shape of the idea: pick a *constructor* and a handful of *selectors*, write every other operation purely in terms of those, and treat the choice of concrete representation as an implementation detail that can change later without disturbing anything above it.

아이디어의 일반적인 모양은 이렇습니다 — *생성자(constructor)*와 소수의 *선택자(selector)*를 고르고, 그 밖의 모든 연산을 오직 그것들만으로 작성하며, 구체적인 표현 방식의 선택은 나중에 바뀌어도 그 위의 어떤 것도 건드리지 않는 구현 세부 사항으로 취급합니다.

---

## 2.1.1. 예제: 유리수 연산

Suppose three procedures already exist, even though we haven't decided how a rational number is actually stored: `makeRat n d` builds a rational number from a numerator and denominator, `numer x` extracts the numerator, `denom x` extracts the denominator. This is *wishful thinking* as a design technique — assume the interface first, and every arithmetic rule follows immediately from ordinary fraction algebra:

유리수가 실제로 어떻게 저장되는지 아직 정하지 않았더라도, 세 절차가 이미 존재한다고 가정해 봅시다 — `makeRat n d`는 분자와 분모로 유리수를 만들고, `numer x`는 분자를, `denom x`는 분모를 꺼냅니다. 이것이 설계 기법으로서의 *희망적 사고(wishful thinking)*입니다 — 인터페이스를 먼저 가정하면, 모든 산술 규칙은 평범한 분수 대수학으로부터 곧바로 따라 나옵니다.

```lean
def addRat (x y : Int × Int) : Int × Int :=
  (numer x * denom y + numer y * denom x, denom x * denom y)

def subRat (x y : Int × Int) : Int × Int :=
  (numer x * denom y - numer y * denom x, denom x * denom y)

def mulRat (x y : Int × Int) : Int × Int :=
  (numer x * numer y, denom x * denom y)

def divRat (x y : Int × Int) : Int × Int :=
  (numer x * denom y, denom x * numer y)

def equalRat (x y : Int × Int) : Bool :=
  numer x * denom y == numer y * denom x
```

Here we've already committed to representing a rational number as `Int × Int` — Lean's built-in pair type — because Lean requires every `def` to state a concrete type up front; we can't write these five procedures purely against an as-yet-unspecified abstraction the way Scheme's untyped `cons`/`car`/`cdr` let SICP do. The commitment is shallow, though: everything below still goes through `numer` and `denom` rather than `.fst`/`.snd` directly, so the abstraction barrier is intact even though its type is pinned down earlier than in Scheme.

여기서는 이미 유리수를 `Int × Int` — Lean의 내장 쌍 타입 — 로 표현하기로 정했습니다. Lean은 모든 `def`가 구체적인 타입을 미리 밝히도록 요구하므로, SICP가 Scheme의 타입 없는 `cons`/`car`/`cdr`로 했던 것처럼 아직 정해지지 않은 추상화만을 상대로 이 다섯 절차를 쓸 수는 없습니다. 다만 이 확정은 얕습니다 — 아래의 모든 코드는 여전히 `.fst`/`.snd`가 아니라 `numer`, `denom`을 거치므로, 타입이 Scheme보다 일찍 고정되었을 뿐 추상화 장벽 자체는 그대로 유지됩니다.

### 쌍(Pair)

Scheme reaches for a single primitive, `cons`, to glue any two values together, whatever their types happen to be — `(cons 1 "two")` is perfectly legal. Lean's analogous primitive is `Prod`, written `α × β`, constructed with `(x, y)` and taken apart with `.fst`/`.snd`:

Scheme는 값의 타입이 무엇이든 상관없이 둘을 붙이는 원시 연산 하나 — `cons` — 를 씁니다. `(cons 1 "two")`도 완전히 유효합니다. Lean에서 이에 대응하는 원시 연산은 `Prod`이며, `α × β`로 쓰고 `(x, y)`로 만들고 `.fst`/`.snd`로 분해합니다.

```lean
def pairXY : Int × Int := (1, 2)

#eval pairXY.fst
-- 1

#eval pairXY.snd
-- 2

def nested : (Int × Int) × (Int × Int) := ((1, 2), (3, 4))

#eval nested.fst.fst
-- 1

#eval nested.snd.fst
-- 3
```

The one place this diverges from Scheme: `1` and `"two"` living in the same `cons` cell is exactly the kind of thing Lean's `Int × String` type signature makes explicit rather than silently permitting — a pair's component types are part of its type, not something discovered only when you try to use the wrong one.

Scheme와 갈라지는 한 지점은 이렇습니다 — `1`과 `"two"`가 같은 `cons` 셀에 들어가는 것은, Lean에서는 `Int × String`이라는 타입 시그니처가 명시적으로 드러내는 것이지, 조용히 허용되다가 잘못 쓸 때야 발견되는 것이 아닙니다. 쌍의 각 구성 요소 타입은 쌍의 타입 자체에 포함됩니다.

### 유리수 표현하기

A rational number, then, is just a pair of integers, and `makeRat`/`numer`/`denom` are the thinnest possible wrapper around `Prod`:

그렇다면 유리수는 그저 정수 쌍이고, `makeRat`/`numer`/`denom`은 `Prod` 위에 씌울 수 있는 가장 얇은 래퍼입니다.

```lean
def makeRat (n d : Int) : Int × Int := (n, d)
def numer (x : Int × Int) : Int := x.fst
def denom (x : Int × Int) : Int := x.snd

def printRat (x : Int × Int) : IO Unit :=
  IO.println s!"{numer x}/{denom x}"

#eval printRat (addRat (makeRat 1 2) (makeRat 1 3))
-- 5/6

#eval printRat (addRat (makeRat 1 3) (makeRat 1 3))
-- 6/9
```

Just as in SICP, this version doesn't reduce to lowest terms — `1/3 + 1/3` prints `6/9` instead of `2/3`. Reusing the `gcd` from [1.2](../1-2-procedures-and-processes/) fixes this purely by changing `makeRat`, with no changes anywhere else:

SICP에서와 마찬가지로, 이 버전은 기약분수로 약분하지 않습니다 — `1/3 + 1/3`은 `2/3`이 아니라 `6/9`로 출력됩니다. [1.2절](../1-2-procedures-and-processes/)의 `gcd`를 재사용하면, 다른 곳은 전혀 건드리지 않고 오직 `makeRat`만 바꿔서 이를 고칠 수 있습니다.

```lean
def gcdInt (a b : Int) : Int :=
  Int.ofNat (Nat.gcd a.natAbs b.natAbs)

def makeRat' (n d : Int) : Int × Int :=
  let g := gcdInt n d
  (n / g, d / g)

#eval printRat (addRat (makeRat' 1 3) (makeRat' 1 3))
-- 2/3
```

`addRat`, `subRat`, and the rest never mention `gcdInt` — they only ever call `numer`/`denom`/`makeRat`, so swapping in `makeRat'` is invisible to them. This is the abstraction barrier already paying for itself.

`addRat`, `subRat` 등은 `gcdInt`를 한 번도 언급하지 않습니다 — 오직 `numer`/`denom`/`makeRat`만 호출하므로, `makeRat'`로 바꿔치기해도 그것들 입장에서는 아무 일도 일어나지 않습니다. 추상화 장벽이 벌써 제 몫을 하고 있는 셈입니다.

**연습문제 2.1 (Lean 버전)**: 부호가 있는 분자·분모를 정규화하는 `makeRat`을 작성하세요 — 유리수가 양수면 분자·분모 모두 양수, 음수면 분자만 음수가 되어야 합니다.

```lean
def makeRatSigned (n d : Int) : Int × Int :=
  let g := gcdInt n d
  let sign : Int := if d < 0 then -1 else 1
  (sign * n / g, sign * d / g)
```

---

## 2.1.2. 추상화 장벽

Picture the rational-number system as a stack of layers, each separated by a horizontal *abstraction barrier*. Code that uses rational numbers only ever calls `addRat`/`subRat`/`mulRat`/`divRat`/`equalRat`; those, in turn, only ever call `makeRat`/`numer`/`denom`; those, in turn, only ever call `Prod`'s constructor and projections. Nothing above a barrier needs to know what's below it, so long as the interface at that barrier stays fixed.

유리수 시스템을 여러 층으로 쌓인 스택으로 그려보면, 각 층은 수평의 *추상화 장벽(abstraction barrier)*으로 나뉩니다. 유리수를 쓰는 코드는 오직 `addRat`/`subRat`/`mulRat`/`divRat`/`equalRat`만 호출하고, 이들은 다시 오직 `makeRat`/`numer`/`denom`만 호출하며, 이들은 다시 오직 `Prod`의 생성자와 투영만 호출합니다. 그 장벽에서의 인터페이스가 고정되어 있는 한, 장벽 위의 어떤 것도 그 아래에 뭐가 있는지 알 필요가 없습니다.

The alternative implementation from the previous section — reduce at construction time versus reduce at access time — is the clearest possible demonstration of why this matters. Deferring the `gcd` to the selectors instead of the constructor changes nothing about `addRat` and friends:

앞 절의 대안 구현 — 생성 시점에 약분할지, 접근 시점에 약분할지 — 이 이것이 왜 중요한지를 가장 명확하게 보여줍니다. `gcd`를 생성자 대신 선택자로 미루어도 `addRat`을 비롯한 나머지는 전혀 달라지지 않습니다.

```lean
def makeRatDeferred (n d : Int) : Int × Int := (n, d)

def numerDeferred (x : Int × Int) : Int :=
  x.fst / gcdInt x.fst x.snd

def denomDeferred (x : Int × Int) : Int :=
  x.snd / gcdInt x.fst x.snd
```

Whether it's better to reduce eagerly (once, at construction) or lazily (every time a component is read) depends on how often a given rational number's parts get accessed relative to how often new ones get built — exactly the kind of decision the abstraction barrier lets us defer or revisit without touching `addRat` at all.

즉시 약분하는 것(생성 시 한 번)과 지연 약분하는 것(구성 요소를 읽을 때마다) 중 무엇이 더 나은지는, 주어진 유리수의 구성 요소가 얼마나 자주 접근되는지가 새로 만들어지는 빈도에 비해 얼마나 되는지에 달려 있습니다 — 추상화 장벽이 `addRat`을 전혀 건드리지 않고도 미루거나 다시 검토할 수 있게 해주는 바로 그런 종류의 결정입니다.

**연습문제 2.2 (Lean 버전)**: 평면 위의 선분을 점의 쌍으로 표현합니다. 점은 좌표의 쌍입니다.

```lean
def makePoint (x y : Float) : Float × Float := (x, y)
def xPoint (p : Float × Float) : Float := p.fst
def yPoint (p : Float × Float) : Float := p.snd

def makeSegment (start «end» : Float × Float) : (Float × Float) × (Float × Float) :=
  (start, «end»)
def startSegment (s : (Float × Float) × (Float × Float)) : Float × Float := s.fst
def endSegment (s : (Float × Float) × (Float × Float)) : Float × Float := s.snd

def midpointSegment (s : (Float × Float) × (Float × Float)) : Float × Float :=
  let a := startSegment s
  let b := endSegment s
  (average (xPoint a) (xPoint b), average (yPoint a) (yPoint b))
```

(`average`는 [1.1절](../1-1-elements-of-programming/)에서 정의한 그 절차입니다.) `midpointSegment`는 `startSegment`/`endSegment`/`xPoint`/`yPoint`만 호출할 뿐, 점과 선분이 실제로 중첩된 `Prod`라는 사실을 전혀 알 필요가 없습니다 — 추상화 장벽이 여기서도 그대로 작동합니다.

---

## 2.1.3. 데이터란 무엇을 의미하는가

"Data" can't just mean "whatever the selectors and constructor happen to compute" — not every triple of procedures qualifies as a valid rational-number implementation. What actually matters is a *behavioral condition*: for any integer `n` and nonzero integer `d`, if `x = makeRat n d`, then `numer x / denom x` must equal `n / d`. Any triple of procedures satisfying that condition is an adequate representation, regardless of how it's built internally — the condition, not the implementation, is what defines the data.

"데이터"가 그저 "선택자와 생성자가 우연히 계산해내는 것"만을 의미할 수는 없습니다 — 아무 절차 세 개나 유리수 구현으로 자격을 갖추는 건 아닙니다. 실제로 중요한 것은 *행동 조건(behavioral condition)*입니다 — 임의의 정수 `n`과 0이 아닌 정수 `d`에 대해, `x = makeRat n d`라면 `numer x / denom x`는 반드시 `n / d`와 같아야 합니다. 이 조건을 만족하는 절차 세 개는 내부적으로 어떻게 만들어졌든 적절한 표현이며 — 구현이 아니라 이 조건이 데이터를 정의합니다.

The same reasoning applies one level down, to pairs themselves: all `cons`/`car`/`cdr` need to satisfy is that `car (cons x y) = x` and `cdr (cons x y) = y`. SICP's famous demonstration is that this condition can be met *without any built-in pair structure at all* — a pair can be a procedure that remembers `x` and `y` and dispatches on an index:

같은 논리가 한 단계 아래, 쌍 자체에도 적용됩니다 — `cons`/`car`/`cdr`가 만족해야 할 것은 오직 `car (cons x y) = x`이고 `cdr (cons x y) = y`라는 것뿐입니다. SICP의 유명한 시연은 이 조건이 *내장된 쌍 구조가 전혀 없이도* 충족될 수 있다는 것입니다 — 쌍은 `x`와 `y`를 기억하고 인덱스에 따라 분기하는 절차일 수 있습니다.

```lean
def consProc (x y : α) : Nat → α
  | 0 => x
  | _ => y

def carProc (z : Nat → α) : α := z 0
def cdrProc (z : Nat → α) : α := z 1

#eval carProc (consProc 1 2)
-- 1

#eval cdrProc (consProc 1 2)
-- 2
```

The subtlety worth flagging: `consProc` needs `x` and `y` to share a type `α`, since `Nat → α` has to name one return type for both branches of the match. Scheme's dynamically-typed `cons` never faced this constraint — `(cons 1 "two")` dispatches to whichever value was asked for, with no requirement that the two share a type. Exercise 2.4's alternative encoding sidesteps the issue entirely by pushing the choice of what to do with `x` and `y` into the caller:

짚어둘 만한 미묘한 점 — `consProc`은 `x`와 `y`가 타입 `α`를 공유해야 합니다. `Nat → α`가 매치의 두 분기 모두에 대해 하나의 반환 타입을 이름 붙여야 하기 때문입니다. Scheme의 동적 타입 `cons`는 이런 제약을 전혀 마주치지 않았습니다 — `(cons 1 "two")`는 요청받은 값이 무엇이든 그쪽으로 분기하며, 둘이 타입을 공유해야 한다는 요구가 없습니다. 연습문제 2.4의 대안 인코딩은 `x`와 `y`로 무엇을 할지의 선택을 호출자 쪽으로 밀어냄으로써 이 문제를 완전히 비켜갑니다.

```lean
def consLambda (x y : α) : (α → α → α) → α :=
  fun m => m x y

def carLambda (z : (α → α → α) → α) : α :=
  z (fun p _ => p)

def cdrLambda (z : (α → α → α) → α) : α :=
  z (fun _ q => q)

#eval carLambda (consLambda 1 2)
-- 1

#eval cdrLambda (consLambda 1 2)
-- 2
```

This is exactly the point SICP is making, sharpened by Lean's type checker: the ability to manipulate procedures as first-class values already gives you the ability to represent compound data, with no separate "pair" primitive required at all. This encoding of pairs as procedures is a special case of a more general technique called *message passing*, which becomes a central tool once we start modeling objects with internal state.

이것이 정확히 SICP가 짚는 지점이고, Lean의 타입 검사기가 그것을 한층 더 날카롭게 만듭니다 — 절차를 일급 값으로 다룰 수 있는 능력이 이미 복합 데이터를 표현할 수 있는 능력을 준다는 것이고, 별도의 "쌍" 원시 연산이 전혀 필요 없다는 것입니다. 쌍을 절차로 인코딩하는 이 방식은 *메시지 패싱(message passing)*이라 불리는 더 일반적인 기법의 특수한 경우이며, 내부 상태를 가진 객체를 모델링하기 시작하면 핵심 도구가 됩니다.

---

## 2.1.4. 응용 연습문제: 구간 연산

Alyssa's problem: represent a physical measurement's uncertainty as an *interval* — a lower and upper bound — and define arithmetic on intervals so that adding, multiplying, or dividing two uncertain quantities produces a correctly-bounded uncertain result.

Alyssa의 문제 — 물리적 측정값의 불확실성을 *구간(interval)*(하한과 상한)으로 표현하고, 구간에 대한 산술을 정의해 두 불확실한 값을 더하거나 곱하거나 나누면 올바르게 경계 지어진 불확실한 결과가 나오게 하는 것입니다.

Where the rational-number example reached for a raw pair, an interval is a natural fit for Lean's `structure` — a named record type with its own constructor and field-projection selectors built in, rather than something we have to hand-roll on top of `Prod`:

유리수 예제가 날것의 쌍을 썼던 것과 달리, 구간은 Lean의 `structure`에 자연스럽게 들어맞습니다 — `Prod` 위에 직접 손으로 쌓아야 하는 것이 아니라, 자기만의 생성자와 필드 투영 선택자가 내장된 이름 붙은 레코드 타입입니다.

```lean
structure Interval where
  lower : Float
  upper : Float

def makeInterval (a b : Float) : Interval := ⟨a, b⟩

def addInterval (x y : Interval) : Interval :=
  ⟨x.lower + y.lower, x.upper + y.upper⟩

def mulInterval (x y : Interval) : Interval :=
  let p1 := x.lower * y.lower
  let p2 := x.lower * y.upper
  let p3 := x.upper * y.lower
  let p4 := x.upper * y.upper
  ⟨min (min p1 p2) (min p3 p4), max (max p1 p2) (max p3 p4)⟩

def divInterval (x y : Interval) : Interval :=
  mulInterval x ⟨1.0 / y.upper, 1.0 / y.lower⟩
```

`x.lower` and `x.upper` *are* the selectors here, and the anonymous-constructor notation `⟨_, _⟩` *is* `makeInterval` — Lean's `structure` gives the constructor/selector abstraction barrier as a built-in language feature rather than something SICP has to assemble by hand from `cons`. This is a second, genuinely different way to draw the same boundary we drew with `Int × Int` and `numer`/`denom` for rational numbers, and it's worth noticing that nothing about `addInterval` or `mulInterval` would need to change if we later swapped this `structure` for a plain `Float × Float` pair with matching accessor functions — the abstraction barrier holds regardless of which Lean feature implements the concrete layer underneath it.

여기서 `x.lower`와 `x.upper`가 곧 선택자이고, 익명 생성자 표기법 `⟨_, _⟩`가 곧 `makeInterval`입니다 — Lean의 `structure`는 SICP가 `cons`로부터 손수 조립해야 했던 생성자/선택자 추상화 장벽을 언어의 내장 기능으로 제공합니다. 이는 유리수에서 `Int × Int`와 `numer`/`denom`으로 그었던 것과 같은 경계를, 진짜로 다른 방식으로 긋는 두 번째 사례입니다. 그리고 나중에 이 `structure`를 대응하는 접근자 함수를 가진 평범한 `Float × Float` 쌍으로 바꿔치기하더라도 `addInterval`이나 `mulInterval`은 전혀 달라질 필요가 없다는 점도 눈여겨볼 만합니다 — 그 아래의 구체적인 층을 Lean의 어떤 기능이 구현하든, 추상화 장벽은 그대로 유지됩니다.

**연습문제 2.7 (Lean 버전)**: `Interval` 구조체가 이미 `lower`/`upper` 필드 접근자를 제공하므로, 별도의 선택자를 정의할 필요 없이 그대로 `upperBound`/`lowerBound`라는 이름으로 재노출할 수 있습니다.

```lean
def upperBound (i : Interval) : Float := i.upper
def lowerBound (i : Interval) : Float := i.lower
```

**연습문제 2.10 (Lean 버전)**: 0을 가로지르는 구간으로 나누는 것은 정의되지 않으므로, 이 실패 가능성을 `Option`으로 타입에 드러냅니다 — [1.3절](../1-3-higher-order-procedures/)의 이분법에서 `error` 대신 `Option`을 썼던 것과 같은 결정입니다.

```lean
def divIntervalSafe (x y : Interval) : Option Interval :=
  if y.lower <= 0 && 0 <= y.upper then none
  else some (divInterval x y)
```

---

## 정리

| SICP 개념 | Scheme | Lean 4 |
|---|---|---|
| 쌍(pair) | `cons`/`car`/`cdr` (타입 없음) | `Prod`(`α × β`), `(x, y)`, `.fst`/`.snd` |
| 생성자·선택자 | 직접 정의한 절차들 | `Prod` 기반 함수, 또는 `structure`의 필드 접근자 |
| 추상화 장벽 | 절차 계층으로 표현 | 함수 계층 + 타입 시그니처로 한 번 더 굳어짐 |
| 데이터의 정의 | "조건을 만족하는 절차들의 모음" | 동일 — 조건을 만족하면 `Prod`든 `structure`든 절차 인코딩이든 무방 |
| 쌍의 절차적 표현 | 인덱스로 분기하는 클로저 | `Nat → α`(동일 타입 필요) 또는 `(α → α → α) → α` |
| 오류 신호 | 조건 없음 명시 안 함 | `Option`으로 타입에 드러냄 |

이 절에서 SICP가 강조하는 것은 결국 "구체적 표현이 무엇이든, 인터페이스가 조건을 만족하면 그걸로 충분하다"는 것입니다. Lean에서는 이 인터페이스가 `Prod`, 손으로 짠 절차, 또는 `structure`라는 세 가지 서로 다른 언어 기능으로 구현될 수 있음을 직접 보여줄 수 있었고, 타입 시그니처 덕분에 그 경계가 한 번 더 명시적으로 굳어졌습니다. 다음 글에서는 2.2절 — 리스트와 계층적 데이터, 그리고 이를 다루는 `map`/`filter`/`fold` 같은 시퀀스 연산 — 을 다룹니다.
