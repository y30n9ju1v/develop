---
title: "4.2. 스킴의 변주 — 지연 평가 (Variations on a Scheme — Lazy Evaluation)"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["sicp", "lean", "lean4", "scheme", "laziness", "thunk", "memoization", "evaluation-strategy"]
categories: ["programming"]
description: "SICP 4장 2절의 아이디어(정상 순서/응용 순서, thunk, 메모이제이션, 지연 리스트)를 Lean 4의 Thunk와 평가 전략 관점에서 다시 짜 봅니다."
---

Chapter 3 reached for `delay` and `force` as a special-purpose escape hatch, invoked only where a stream was being built. This section asks what happens if that escape hatch becomes the *default* evaluation rule instead of an exception to it — if every argument to every procedure is automatically wrapped in a promise rather than computed on the spot, so laziness stops being something the programmer opts into by hand and becomes a property of the language itself. SICP explores this by rewriting the evaluator; we'll explore the same question by asking what Lean, a language that deliberately kept `Thunk` as an opt-in library type rather than baking it into every function call, would look like if it had made the opposite choice.

3장은 `delay`와 `force`를 스트림을 만들 때만 호출되는 특수 목적의 탈출구로 사용했습니다. 이 절은 그 탈출구가 예외가 아니라 *기본* 평가 규칙이 되면 무슨 일이 벌어지는지를 묻습니다 — 모든 절차의 모든 인자가 그 자리에서 계산되는 대신 자동으로 약속으로 감싸진다면, 지연성은 프로그래머가 손으로 선택해서 켜는 것이 아니라 언어 자체의 속성이 됩니다. SICP는 평가기를 다시 씀으로써 이를 탐구하고, 우리는 `Thunk`를 모든 함수 호출에 굽어 넣지 않고 일부러 선택적인(opt-in) 라이브러리 타입으로 남겨둔 언어인 Lean이 만약 반대 선택을 했다면 어떤 모습이었을지를 물어봄으로써 같은 질문을 탐구합니다.

---

## 4.2.1. 정상 순서와 응용 순서

An *applicative-order* language computes every argument before a call happens; a *normal-order* language postpones each argument's computation until something actually inspects its value. Lean, like Scheme, is applicative-order by default: passing `1 / 0` in `Nat` arithmetic as an unused argument still forces the division (well-defined here since `Nat` division by zero is total and returns `0`, but the point generalizes to anything that could `panic!` or fail to terminate). The cleanest way to see the applicative/normal-order gap directly is a function that ignores one of its arguments entirely:

*응용 순서(applicative-order)* 언어는 호출이 일어나기 전에 모든 인자를 계산합니다. *정상 순서(normal-order)* 언어는 무언가가 실제로 그 값을 들여다볼 때까지 각 인자의 계산을 미룹니다. Lean은 Scheme과 마찬가지로 기본적으로 응용 순서입니다 — 쓰이지 않는 인자로 `Nat` 산술의 `1 / 0`을 넘겨도 나눗셈은 강제로 실행됩니다(여기서는 `Nat`의 0으로 나누기가 전역 함수이고 `0`을 반환하므로 잘 정의되지만, 요점은 `panic!`하거나 종료하지 않을 수 있는 어떤 것에도 일반화됩니다). 응용/정상 순서 사이의 간극을 가장 명확히 보는 방법은 인자 하나를 완전히 무시하는 함수입니다.

```lean
partial def loopForever : Nat := loopForever

def try' (a b : Nat) : Nat := if a = 0 then 1 else b

#eval try' 0 5
-- 1

-- #eval try' 0 loopForever  -- 절대 끝나지 않는다: b는 쓰이지 않지만 Lean은 그것을 미리 계산하려 든다
```

Under Lean's ordinary evaluation, calling `try' 0 loopForever` never returns, even though `b` is dead in the branch actually taken, because Lean computes arguments before the function body runs — precisely the applicative-order behavior SICP's `try` example is designed to expose. Making this non-strict requires making the caller do the delaying explicitly, since Lean itself won't do it automatically:

Lean의 일반적인 평가 방식에서는, 실제로 실행되는 분기에서 `b`가 죽은 값인데도 `try' 0 loopForever`를 호출하면 결코 반환되지 않습니다. Lean이 함수 본문이 실행되기 전에 인자를 계산해버리기 때문입니다 — 이는 정확히 SICP의 `try` 예제가 드러내려는 응용 순서 행동입니다. 이를 비엄격(non-strict)하게 만들려면 호출자가 명시적으로 지연시켜야 합니다. Lean 자신은 이를 자동으로 해주지 않기 때문입니다.

```lean
def tryLazy (a : Nat) (b : Thunk Nat) : Nat := if a = 0 then 1 else b.get

#eval tryLazy 0 (Thunk.mk (fun _ => loopForever))
-- 1
```

`b.get` is only reached in the `else` branch, and Lean's `if`/`then`/`else` short-circuits the branch not taken, so `b`'s `Thunk.mk` closure is simply never invoked when `a = 0`. This is precisely SICP's point about `cons` (and, by extension, about `if` itself) being one of the procedures worth making non-strict: the branch never entered has an argument whose value is never needed, and forcing it anyway wastes work at best and diverges at worst.

`b.get`은 `else` 분기에서만 도달되고, Lean의 `if`/`then`/`else`는 선택되지 않은 분기를 완전히 건너뛰므로 `a = 0`일 때 `b`의 `Thunk.mk` 클로저는 아예 호출되지 않습니다. 이는 정확히 SICP가 `cons`(그리고 확장하면 `if` 자신)를 비엄격하게 만들 가치가 있다고 짚는 지점입니다 — 진입하지 않는 분기에는 값이 필요 없는 인자가 있고, 그것을 그래도 강제 평가하면 잘해야 낭비, 최악의 경우 발산으로 이어집니다.

The `unless` pattern generalizes this to an ordinary procedure rather than a special form. Because Lean's `if` is already special syntax (not a function value you could pass to `map`), the honest way to make `unless` first-class is exactly what SICP does for procedures whose non-strictness matters: wrap the arguments you want delayed in `Thunk` at the call site.

`unless` 패턴은 이를 특수 형식이 아니라 평범한 절차로 일반화합니다. Lean의 `if`가 이미 특수 구문이라(그래서 `map`에 넘길 수 있는 함수 값이 아니라) `unless`를 일급으로 만드는 정직한 방법은, 비엄격성이 중요한 절차에 대해 SICP가 하는 것과 정확히 같습니다 — 호출 지점에서 지연시키고 싶은 인자를 `Thunk`로 감싸는 것입니다.

```lean
def unless (condition : Bool) (usual exceptional : Thunk α) : α :=
  if condition then exceptional.get else usual.get

def safeDivide (a b : Nat) : Nat :=
  unless (b == 0)
    (Thunk.mk (fun _ => a / b))
    (Thunk.mk (fun _ => panic! "division by zero, returning 0"))

#eval safeDivide 10 2
-- 5
```

**연습문제 4.25 (Lean 버전):** SICP는 `unless`로 `factorial`을 정의하면 응용 순서 언어에서는 무한 루프에 빠지지만 정상 순서 언어에서는 잘 동작한다고 지적합니다. Lean에서 `unless`를 위와 같이 `Thunk` 기반으로 정의했을 때, 재귀 호출 `factorial (n - 1)`을 `Thunk.mk`로 감싸지 않고 그냥 넘기면 무슨 일이 벌어지는지 직접 확인해 봅시다.

```lean
partial def factorialBad (n : Nat) : Nat :=
  unless (n == 1) (Thunk.mk (fun _ => n * factorialBad (n - 1))) (Thunk.mk (fun _ => 1))
  -- 이 정의는 실제로 잘 동작한다 — factorialBad (n - 1)이 Thunk 안에 있으므로
  -- unless의 usual.get이 호출될 때만 강제된다.

#eval factorialBad 5
-- 120
```

Lean's version actually works fine — because `Thunk.mk (fun _ => ...)` genuinely delays the recursive call until `.get` forces it, exactly the discipline SICP's normal-order language performs automatically. The version that would loop forever is the one where a caller forgets the `Thunk.mk` wrapper and hands `unless` an already-evaluated `n * factorialBad (n - 1)`: Lean would then evaluate that argument to build the `Thunk` — but `Thunk.mk` itself is what makes an argument non-strict, and a bare recursive call passed without it would simply be evaluated by Lean's ordinary applicative-order call convention before `unless` ever runs, recursing forever just as SICP's applicative-order `factorial` does.

Lean 버전은 사실 잘 동작합니다 — `Thunk.mk (fun _ => ...)`가 재귀 호출을 `.get`이 강제할 때까지 정말로 지연시키기 때문인데, 이는 정확히 SICP의 정상 순서 언어가 자동으로 수행하는 규율입니다. 영원히 루프에 빠지는 버전은 호출자가 `Thunk.mk` 래퍼를 깜빡하고 이미 평가된 `n * factorialBad (n - 1)`을 `unless`에 그대로 건네는 경우입니다 — 그러면 Lean은 `Thunk`를 만들기 위해 그 인자를 평가하게 되는데, `Thunk.mk` 자체가 인자를 비엄격하게 만들어주는 장치이므로, 그것 없이 건네진 맨 재귀 호출은 `unless`가 실행되기도 전에 Lean의 평범한 응용 순서 호출 관례에 따라 평가되어, SICP의 응용 순서 `factorial`이 그러듯 영원히 재귀합니다.

---

## 4.2.2. 지연 평가를 갖춘 인터프리터

SICP builds an entire lazy metacircular evaluator to make non-strictness the language's default rather than something a caller opts into per-argument. We can capture the essential mechanism — a *thunk* that packages an unevaluated expression with its environment, and *forcing* that runs and caches it — directly with `Thunk`, without writing a full interpreter: a `thunk` in SICP's sense and a `Thunk` in Lean's sense are, again, nearly the same object under nearly the same name.

SICP는 비엄격성을 호출자가 인자마다 선택하는 것이 아니라 언어의 기본 규칙으로 만들기 위해 지연 평가를 하는 완전한 메타순환 평가기를 만듭니다. 그 핵심 메커니즘 — 평가되지 않은 표현식을 환경과 함께 포장한 *thunk*, 그리고 그것을 실행하고 캐시하는 *forcing* — 을 완전한 인터프리터를 쓰지 않고도 `Thunk`로 직접 포착할 수 있습니다. SICP가 말하는 thunk와 Lean이 말하는 `Thunk`는 이번에도 거의 같은 이름 아래 거의 같은 객체입니다.

```lean
-- SICP의 evaluated-thunk?/force-it 로직은 Thunk.get의 캐싱 동작 그 자체다.
def sicpForceIt (t : Thunk α) : α := t.get

def demoThunk : IO Unit := do
  let counter ← IO.mkRef 0
  let expensive := Thunk.mk (fun _ => Id.run do
    -- 이 클로저 안의 계산은 처음 .get이 호출될 때 딱 한 번만 실행된다.
    1 + 1)
  IO.println s!"before force: {counter.get}"
  IO.println s!"forced once: {expensive.get}"
  IO.println s!"forced twice: {expensive.get}"

#eval demoThunk
-- before force: <IO.Ref 값이므로 #eval에서는 IO 실행 시점에 출력>
-- forced once: 2
-- forced twice: 2
```

SICP's `force-it` distinguishes a fresh `thunk` from an `evaluated-thunk`, mutating the former into the latter with `set-car!`/`set-cdr!` the first time it's forced. `Thunk.get` does exactly this bookkeeping internally, without exposing the two states as separate constructors the way SICP's list-based representation does — from the caller's side, there is only ever one type, `Thunk α`, and the question "has this been forced yet" is answered by the implementation, not by pattern-matching a tag.

SICP의 `force-it`은 갓 만들어진 `thunk`와 `evaluated-thunk`를 구분하고, 처음 강제될 때 `set-car!`/`set-cdr!`로 전자를 후자로 변경합니다. `Thunk.get`은 이 부기(bookkeeping)를 내부적으로 정확히 수행하는데, SICP의 리스트 기반 표현처럼 두 상태를 별개의 생성자로 드러내지 않습니다 — 호출자 쪽에서는 오직 하나의 타입 `Thunk α`만 있고, "이게 이미 강제됐는가"라는 질문은 태그를 패턴 매치해서가 아니라 구현이 답해줍니다.

The one thing `Thunk.get`'s built-in caching doesn't let us observe directly is what an *unmemoized* force would look like — SICP's footnote about call-by-name versus call-by-need. To make that comparison, we have to opt back out of `Thunk`'s memoization and reach for `Unit → α`, an ordinary function that genuinely reruns its body on every call:

`Thunk.get`의 내장 캐싱이 우리에게 직접 보여주지 않는 한 가지는 *메모이제이션되지 않은* 강제 평가가 어떤 모습일지입니다 — call-by-name과 call-by-need에 대한 SICP의 각주입니다. 그 비교를 하려면 `Thunk`의 메모이제이션에서 다시 벗어나 `Unit → α`, 즉 호출될 때마다 정말로 본문을 다시 실행하는 평범한 함수를 써야 합니다.

```lean
def demoUnmemoized : IO Unit := do
  let counter ← IO.mkRef 0
  let expensive : Unit → IO Nat := fun _ => do
    counter.modify (· + 1)
    pure 42
  let r1 ← expensive ()
  let r2 ← expensive ()
  IO.println s!"forced twice, ran {← counter.get} times, values {r1} {r2}"

#eval demoUnmemoized
-- forced twice, ran 2 times, values 42 42
```

**연습문제 4.27 (Lean 버전):** 원문은 `id` 절차가 대입으로 `count`를 증가시키는 부작용을 가질 때, 메모이제이션이 이 부작용이 몇 번 일어나는지를 좌우한다는 것을 보입니다. `Thunk`의 내장 메모이제이션과, 매번 다시 실행되는 평범한 함수를 나란히 놓고 `IO.Ref` 카운터로 그 차이를 직접 세어 봅시다.

```lean
def idEffect (counter : IO.Ref Nat) (x : Nat) : IO Nat := do
  counter.modify (· + 1)
  pure x

def demoMemoVsNot : IO Unit := do
  let counter1 ← IO.mkRef 0
  let counter2 ← IO.mkRef 0
  -- 메모이제이션되는 쪽: Thunk 하나를 두 번 강제해도 idEffect는 한 번만 실행된다.
  let memoized : Thunk Nat := Thunk.mk (fun _ => (idEffect counter1 10).run')
  let _ := memoized.get
  let _ := memoized.get
  -- 메모이제이션되지 않는 쪽: 호출할 때마다 idEffect가 다시 실행된다.
  let _ ← idEffect counter2 10
  let _ ← idEffect counter2 10
  IO.println s!"memoized thunk ran idEffect {← counter1.get} time(s)"
  IO.println s!"unmemoized calls ran idEffect {← counter2.get} time(s)"

#eval demoMemoVsNot
-- memoized thunk ran idEffect 1 time(s)
-- unmemoized calls ran idEffect 2 time(s)
```

`counter1` stops at 1 because the second `memoized.get` returns the cached result without re-running the closure — this is SICP's `count` staying at 1 after `w`'s first reference forces `id`'s effect once, no matter how many further times `w` is inspected. `counter2` reaches 2 because plain function calls carry no cache at all — every invocation is a fresh run, exactly the call-by-name behavior SICP contrasts with call-by-need. Neither answer is "more correct" than the other; they're two different, equally coherent semantics, and the confusion SICP's footnote warns about arises precisely from forgetting which one a given piece of code is assuming.

`counter1`이 1에서 멈추는 이유는 두 번째 `memoized.get`이 클로저를 다시 실행하지 않고 캐시된 결과를 돌려주기 때문입니다 — 이는 `w`에 대한 첫 참조가 `id`의 부작용을 한 번 강제한 후, `w`를 아무리 더 들여다봐도 SICP의 `count`가 1에 머무르는 것과 같습니다. `counter2`가 2에 도달하는 이유는 평범한 함수 호출에는 아무런 캐시도 없기 때문입니다 — 매 호출이 새로운 실행이고, 이는 정확히 SICP가 call-by-need와 대비시키는 call-by-name 행동입니다. 어느 쪽 답도 다른 쪽보다 "더 옳지" 않습니다 — 둘은 서로 다르지만 각자 동등하게 정합적인 의미론이고, SICP의 각주가 경고하는 혼란은 정확히 주어진 코드가 둘 중 어느 것을 가정하고 있는지를 잊어버리는 데서 생깁니다.

---

## 4.2.3. 지연 리스트로서의 스트림

SICP's final move is to notice that once every argument is delayed uniformly, streams and lists collapse into the same thing — there's no need for a separate `cons-stream` once plain `cons` is non-strict in both of its arguments. Lean's `Thunk`-based `LStream` from the [previous post](../3-5-streams/) only delayed the *tail*, matching SICP's `cons-stream`; going one step further and delaying the *head* too gives us SICP's "lazier than streams" lazy pair, where even inspecting whether a list is empty needn't force anything about its first element's value:

SICP의 마지막 움직임은, 모든 인자가 균일하게 지연되고 나면 스트림과 리스트가 같은 것으로 무너져 내린다는 것을 알아채는 데 있습니다 — 평범한 `cons`가 두 인자 모두에서 비엄격하다면 별도의 `cons-stream`이 필요 없습니다. [이전 글](../3-5-streams/)의 `Thunk` 기반 `LStream`은 *꼬리*만 지연시켰고, 이는 SICP의 `cons-stream`에 대응합니다. 여기서 한 발 더 나아가 *머리*도 지연시키면 SICP가 말하는 "스트림보다도 더 게으른" 지연 쌍을 얻는데, 리스트가 비어있는지 확인하는 것조차 첫 원소의 값에 대해 아무것도 강제하지 않습니다.

```lean
inductive LazyList (α : Type) where
  | nil : LazyList α
  | cons : Thunk α → Thunk (LazyList α) → LazyList α

partial def LazyList.mk (x : Thunk α) (rest : Thunk (LazyList α)) : LazyList α :=
  .cons x rest

partial def LazyList.map (f : α → β) : LazyList α → LazyList β
  | .nil => .nil
  | .cons x t => .cons (Thunk.mk (fun _ => f x.get)) (Thunk.mk (fun _ => map f t.get))

partial def LazyList.toListN : Nat → LazyList α → List α
  | 0, _ => []
  | _, .nil => []
  | n + 1, .cons x t => x.get :: toListN n t.get

partial def onesLL : LazyList Nat := .cons (Thunk.mk (fun _ => 1)) (Thunk.mk (fun _ => onesLL))

#eval LazyList.toListN 4 onesLL
-- [1, 1, 1, 1]
```

Structurally this looks like the previous post's `LStream` with an extra `Thunk` wrapped around the head — `partial` is needed for exactly the same reason, since `onesLL` refers to itself inside a `Thunk` closure with no decreasing measure Lean's checker can see. What's new is that `LazyList.map`'s head, `f x.get`, is itself wrapped in a fresh `Thunk` rather than computed immediately: forcing an element of the mapped list runs `f` on demand, and forcing a *later* element doesn't require anything to have run for earlier ones. This is the concrete cash value of SICP's remark that lazy pairs let you compute the length of a list without knowing any of its elements' values — walking `LazyList.nil`/`.cons` to count spine length never touches a single `Thunk α` head, only the `Thunk (LazyList α)` tails.

구조적으로 이것은 이전 글의 `LStream`에 머리를 감싸는 `Thunk`가 하나 더 추가된 모양입니다 — `partial`이 필요한 이유도 정확히 같습니다. `onesLL`이 Lean의 검사기가 볼 수 있는 감소 척도 없이 `Thunk` 클로저 안에서 자기 자신을 참조하기 때문입니다. 새로운 점은 `LazyList.map`의 머리인 `f x.get`이 즉시 계산되는 게 아니라 그 자체로 새로운 `Thunk`에 감싸인다는 것입니다 — 매핑된 리스트의 한 원소를 강제하면 `f`가 필요할 때 실행되고, *나중* 원소를 강제하는 것이 앞선 원소들에 대해 무언가가 실행됐음을 요구하지 않습니다. 이것이 SICP의 말 — 지연 쌍을 쓰면 원소 값을 하나도 모른 채로 리스트의 길이를 계산할 수 있다 — 의 구체적인 가치입니다. `LazyList.nil`/`.cons`를 걸으며 스파인 길이를 세는 것은 `Thunk α` 머리를 단 하나도 건드리지 않고, 오직 `Thunk (LazyList α)` 꼬리만 건드립니다.

**연습문제 4.32 (Lean 버전):** 3장의 `LStream`(꼬리만 지연)과 이번 절의 `LazyList`(머리와 꼬리 모두 지연)의 차이를 드러내는 예를 만들어 봅시다. 원소 자체는 계산하는 데 오래 걸리지만 리스트의 *개수*만 세고 싶은 상황을 생각해 보세요.

```lean
partial def LazyList.lengthUpto (n : Nat) : LazyList α → Nat
  | .nil => 0
  | .cons _ t => if n = 0 then 0 else 1 + lengthUpto (n - 1) t.get

partial def slowSquares : LazyList Nat :=
  .cons (Thunk.mk (fun _ => Id.run do
           -- "비싼" 계산이라고 상상해 보자
           37 * 37))
        (Thunk.mk (fun _ => slowSquares))

#eval LazyList.lengthUpto 3 slowSquares
-- 3, 그리고 37 * 37은 단 한 번도 강제되지 않는다
```

With the strict-tail-only `LStream` from the earlier post, `.head?` still had to pattern-match a concrete, already-evaluated value sitting in the `cons` cell to report it existed — there was no delay to skip. With `LazyList`, `lengthUpto` never calls `.get` on the `Thunk α` at all, only on the `Thunk (LazyList α)` tail needed to keep recursing; the "expensive" head computation genuinely never runs. This is a real, observable difference in what work gets skipped, not just a cosmetic variation on the same idea — and it's exactly the gap SICP is pointing at when it calls lazy pairs "even lazier" than chapter 3's streams.

앞 글의 꼬리만 엄격한 `LStream`에서는 `.head?`가 여전히 `cons` 셀에 이미 놓여 있는 구체적이고 이미 평가된 값을 패턴 매치해서 그것이 존재한다고 보고해야 했습니다 — 건너뛸 지연이 없었습니다. `LazyList`에서는 `lengthUpto`가 `Thunk α`에 대해 `.get`을 전혀 호출하지 않고, 재귀를 계속하는 데 필요한 `Thunk (LazyList α)` 꼬리에 대해서만 호출합니다 — "비싼" 머리 계산은 정말로 한 번도 실행되지 않습니다. 이는 같은 아이디어의 겉치레 변형이 아니라, 어떤 작업이 건너뛰어지는지에 대한 진짜로 관찰 가능한 차이입니다 — 그리고 이것이 정확히 SICP가 지연 쌍을 3장의 스트림보다도 "더 게으르다"고 부를 때 가리키는 간극입니다.

---

Zooming out across this section: SICP's lazy evaluator makes non-strictness the default by threading thunks through every procedure call in a hand-written interpreter, at the cost of an incompatible change to the language itself — ordinary Scheme code stops meaning quite the same thing once every argument is silently delayed. Lean took the opposite bet, keeping evaluation strict everywhere and pushing laziness into a single library type, `Thunk`, that a programmer opts into explicitly at exactly the points where it matters. Nothing here says one design is better; SICP's [Exercise 4.31](#) even points toward Lean's answer directly, proposing per-parameter strictness annotations as an "upward-compatible" alternative to changing the whole language's default. What's worth carrying forward is that the same three ideas — a promise that defers computation, a force that fulfills it, and a cache that keeps a promise from being fulfilled twice — show up in both settings under almost identical names, because they're really one idea, not two coincidentally similar ones.

이 절 전체를 훑어보면, SICP의 지연 평가기는 손으로 쓴 인터프리터의 모든 절차 호출에 thunk를 실어 나름으로써 비엄격성을 기본값으로 만드는데, 그 대가로 언어 자체에 호환되지 않는 변화를 일으킵니다 — 모든 인자가 조용히 지연되고 나면 평범한 Scheme 코드는 더 이상 예전과 완전히 같은 의미를 갖지 않습니다. Lean은 반대 쪽에 걸었습니다 — 평가는 어디서나 엄격하게 유지하고, 지연성은 프로그래머가 정말로 중요한 지점에서 명시적으로 선택하는 단 하나의 라이브러리 타입 `Thunk`로 밀어넣었습니다. 여기서 어느 설계가 더 낫다고 말할 것은 없습니다 — SICP의 연습문제 4.31조차 언어 전체의 기본값을 바꾸는 대신 매개변수별 엄격성 주석을 "상위 호환" 대안으로 제안하며 Lean의 답을 직접 가리킵니다. 가져갈 만한 것은, 계산을 미루는 약속(promise)과 그것을 이행하는 강제(force)와 약속이 두 번 이행되지 않게 막는 캐시라는 같은 세 가지 아이디어가 두 환경 모두에서 거의 똑같은 이름으로 나타난다는 사실입니다 — 이것이 우연히 닮은 두 아이디어가 아니라 사실 하나의 아이디어이기 때문입니다.
