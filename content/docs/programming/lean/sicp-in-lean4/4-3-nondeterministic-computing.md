---
title: "4.3. 스킴의 변주 — 비결정적 계산 (Variations on a Scheme — Nondeterministic Computing)"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["sicp", "lean", "lean4", "scheme", "nondeterminism", "backtracking", "monads", "termination"]
categories: ["programming"]
description: "SICP 4장 3절의 아이디어(amb, 자동 탐색, 되추적)를 Lean 4의 List 모나드와 명시적 성공/실패 continuation으로 다시 짜 봅니다."
---

An expression that can have several possible values, where the language itself figures out which one to commit to based on constraints checked later, is a strange thing to want — but it's exactly what SICP builds next, extending its evaluator so that "pick a number, and if it later turns out wrong, go back and pick a different one" becomes something a program can express directly rather than something the programmer has to hand-code as search.

여러 값을 가질 수 있는 식이 있고, 언어 자체가 나중에 검사되는 제약 조건에 따라 어느 값으로 확정할지 알아서 결정해준다는 것은 이상한 요구처럼 들립니다 — 하지만 SICP가 다음으로 만드는 것이 정확히 이것입니다. "숫자를 하나 고르고, 나중에 틀렸다고 밝혀지면 되돌아가 다른 걸 고른다"는 동작을, 프로그래머가 직접 탐색 코드를 짜지 않고도 프로그램이 곧바로 표현할 수 있도록 평가기를 확장합니다.

Lean has no built-in `amb`, and can't get one for free the way it gets laziness or generic dispatch — nondeterministic choice with backtracking is an *effect*, and in Lean every effect has to be represented as a concrete type. There are two honest ways to model it, and they correspond to the two readings SICP itself points out: "an expression stands for all its possible values at once" (model choice as a `List` of outcomes) versus "an expression commits to one value and can be forced to reconsider" (model choice as an explicit success/failure continuation, exactly mirroring the `amb` evaluator's own implementation).

Lean에는 내장된 `amb`가 없고, 지연 평가나 제네릭 디스패치처럼 공짜로 얻을 수도 없습니다 — 되추적이 있는 비결정적 선택은 하나의 *효과*이고, Lean에서는 모든 효과가 구체적인 타입으로 표현되어야 합니다. 이를 모델링하는 정직한 방법은 두 가지이며, 이는 SICP 자신이 짚은 두 가지 해석과 정확히 대응합니다 — "식은 자신의 가능한 모든 값을 동시에 나타낸다"(선택을 결과들의 `List`로 모델링) 대 "식은 한 값에 확정되지만, 다시 생각해보도록 강제될 수 있다"(선택을 명시적 성공/실패 continuation으로 모델링 — `amb` 평가기 자체의 구현과 정확히 같은 방식).

---

## 4.3.1. `amb`를 `List` 모나드로 읽기

The simplest honest translation of `amb` doesn't need an evaluator at all: Lean's `List` already has a `Monad` instance where `do`-notation explores every combination of choices, and `List.filter`/a `guard`-style check plays the role of `require`. `an-element-of` becomes nothing more than "the list itself," and `prime-sum-pair` becomes a direct transcription with no interpreter to build:

`amb`를 가장 단순하게 정직히 옮기는 방법은 평가기가 아예 필요 없습니다 — Lean의 `List`에는 이미 모든 선택의 조합을 탐색해주는 `Monad` 인스턴스가 있고, `List.filter`나 `guard` 방식의 검사가 `require` 역할을 합니다. `an-element-of`는 그저 "리스트 자체"가 되고, `prime-sum-pair`는 인터프리터를 만들 필요 없이 그대로 옮겨집니다.

```lean
def isPrime (n : Nat) : Bool :=
  n > 1 && (List.range n).drop 2 |>.all (fun d => n % d != 0)

def primeSumPairs (list1 list2 : List Nat) : List (Nat × Nat) := do
  let a ← list1
  let b ← list2
  guard (isPrime (a + b))
  pure (a, b)

#eval primeSumPairs [1, 3, 5, 8] [20, 35, 110]
-- [(1, 20), (3, 20), (3, 110), (8, 35)]
```

This is the same "generate and test" picture SICP already drew for finite sequences in its data-abstraction chapter, and that's not a coincidence — SICP itself flags that the nondeterministic reading and the all-answers-at-once reading are two views of the same computation. What the `List` version gives up is exactly the thing that makes `amb` feel different: there's no notion of "the first answer, and if it's wrong, backtrack to find the next one," because every answer is already sitting in the list before anyone asked for the first.

이는 SICP가 이미 데이터 추상화 장에서 유한 시퀀스에 대해 그렸던 것과 같은 "생성하고 검사하기" 그림이고, 이는 우연이 아닙니다 — SICP 자신도 비결정적 해석과 "모든 답을 한번에" 해석이 같은 계산을 보는 두 관점이라고 짚습니다. `List` 버전이 포기하는 것은 정확히 `amb`를 다르게 느껴지게 만드는 그 부분입니다 — "첫 번째 답, 틀렸으면 되돌아가 다음 답을 찾는다"는 개념이 없습니다. 왜냐하면 누가 첫 번째 답을 요청하기도 전에 모든 답이 이미 리스트 안에 놓여 있기 때문입니다.

Every piece of `primeSumPairs` is ordinary structural recursion under the hood — `List.range`, `drop`, `all`, and the monadic bind for `List` are all defined by recursing on a strictly shrinking list — so nothing here needs `partial`. But that innocence is fragile: replace `list1` with `an-integer-starting-from`'s natural translation, an infinite list of naturals, and the `List` monad approach breaks immediately, because Lean's `List α` is inductively finite by definition. There is no `List` containing every natural number; building one isn't slow, it's impossible.

`primeSumPairs`의 모든 부분은 내부적으로 평범한 구조적 재귀입니다 — `List.range`, `drop`, `all`, 그리고 `List`의 모나드 바인드 모두 항상 줄어드는 리스트에 대한 재귀로 정의되어 있습니다 — 그래서 여기 어디에도 `partial`이 필요 없습니다. 하지만 이 순진함은 깨지기 쉽습니다 — `list1`을 `an-integer-starting-from`을 그대로 옮긴, 무한한 자연수 리스트로 바꾸는 순간 `List` 모나드 접근은 즉시 무너집니다. Lean의 `List α`는 정의상 귀납적으로 유한하기 때문입니다. 모든 자연수를 담은 `List`는 존재하지 않습니다 — 그런 걸 만드는 게 느린 게 아니라 아예 불가능합니다.

---

## 4.3.2. `amb`를 되추적으로 읽기 — 성공/실패 continuation

To get the other reading of `amb` — one answer at a time, backtracking on demand — we have to build, in miniature, exactly the mechanism SICP builds in [4.3.3]: an evaluator whose "execution procedures" take a success continuation and a failure continuation instead of just returning a value. We don't need a full metacircular evaluator to see the idea; a small combinator library gets the essential shape across. A nondeterministic computation of type `α` is a function that, given a success continuation (which receives a value and *another* failure continuation to resume the search) and a failure continuation (a zero-argument action to try the next alternative), drives the search:

`amb`의 다른 해석 — 한 번에 하나씩 답을 내고, 요청 시 되추적하는 방식 — 을 얻으려면, SICP가 [4.3.3]에서 만드는 바로 그 메커니즘을 축소판으로 직접 만들어야 합니다 — "실행 절차"가 단순히 값을 반환하는 대신 성공 continuation과 실패 continuation을 받는 평가기입니다. 완전한 메타순환 평가기까지 필요하지는 않습니다 — 작은 콤비네이터 라이브러리만으로 핵심 형태를 보여줄 수 있습니다. 타입 `α`의 비결정적 계산은, 성공 continuation(값과 탐색을 재개할 *또 다른* 실패 continuation을 받음)과 실패 continuation(다음 대안을 시도하는 인자 없는 동작)이 주어졌을 때 탐색을 진행하는 함수입니다.

```lean
abbrev Amb (α : Type) := (α → (Unit → IO Unit) → IO Unit) → (Unit → IO Unit) → IO Unit

def ambChoice (choices : List α) : Amb α :=
  fun succeed fail =>
    let rec tryNext : List α → IO Unit
      | [] => fail ()
      | c :: cs => succeed c (fun _ => tryNext cs)
    tryNext choices

def ambRequire (p : Bool) : Amb Unit :=
  fun succeed fail => if p then succeed () fail else fail ()

def ambBind (m : Amb α) (f : α → Amb β) : Amb β :=
  fun succeed fail => m (fun a fail2 => f a succeed fail2) fail

def anElementOf (xs : List Nat) : Amb Nat := ambChoice xs

def primeSumPair (list1 list2 : List Nat) : Amb (Nat × Nat) :=
  ambBind (anElementOf list1) (fun a =>
  ambBind (anElementOf list2) (fun b =>
  ambBind (ambRequire (isPrime (a + b))) (fun _ =>
  fun succeed fail => succeed (a, b) fail)))

def runFirst (m : Amb (Nat × Nat)) : IO Unit :=
  m (fun v _ => IO.println s!"found: {v}") (fun _ => IO.println "no more values")

#eval runFirst (primeSumPair [1, 3, 5, 8] [20, 35, 110])
-- found: (1, 20)
```

Notice how closely `ambBind` mirrors SICP's `sequentially`, and how `ambChoice`'s `tryNext` mirrors `analyze-amb`'s own `try-next` loop almost line for line — the continuation-passing shape isn't an artifact of Scheme, it's the shape backtracking search has in *any* language, and Lean just makes you write the continuations out explicitly instead of the evaluator doing it implicitly on your behalf.

`ambBind`가 SICP의 `sequentially`와 얼마나 가깝게 대응하는지, 그리고 `ambChoice`의 `tryNext`가 `analyze-amb`의 `try-next` 루프와 거의 한 줄 한 줄 대응하는지 눈여겨보세요 — 이 continuation-전달 형태는 Scheme만의 특징이 아니라, 되추적 탐색이 *어떤* 언어에서든 갖는 형태입니다. Lean은 그저 평가기가 여러분 대신 암묵적으로 해주던 일을, 여러분이 continuation을 직접 명시적으로 써넣도록 만들 뿐입니다.

`ambChoice`'s `tryNext` recurses structurally on the shrinking list `choices`, so it needs no `partial` — but the whole `Amb` type is built from functions that call each other in continuation-passing style, and Lean's termination checker doesn't attempt to prove termination through an indirection like that; if you tried to build `anIntegerStartingFrom` in this style, generating an unbounded choice sequence on demand, that constructor would have to be `partial`, for the same reason `countDistinct` needed it in the [previous post](../3-3-modeling-with-mutable-data/): the recursion's shrinking measure lives in the caller's search strategy, not in the shape of the data being pattern-matched.

`ambChoice`의 `tryNext`는 줄어드는 리스트 `choices`에 대해 구조적으로 재귀하므로 `partial`이 필요 없습니다 — 하지만 `Amb` 타입 전체는 continuation-전달 스타일로 서로를 호출하는 함수들로 만들어져 있고, Lean의 종료성 검사기는 이런 간접 호출을 통한 종료성은 증명하려 하지 않습니다. 만약 이 스타일로 `anIntegerStartingFrom`을 만들어 무한히 이어지는 선택 시퀀스를 그때그때 생성하려 한다면, 그 생성자는 `partial`이어야 합니다 — [이전 글](../3-3-modeling-with-mutable-data/)에서 `countDistinct`가 `partial`이 필요했던 것과 같은 이유입니다. 재귀가 줄어든다는 척도가 패턴 매칭되는 데이터의 모양이 아니라, 호출자의 탐색 전략 안에 있기 때문입니다.

`ambBind`의 중첩 호출(`ambBind (anElementOf list1) (fun a => ambBind (anElementOf list2) (fun b => …))`)은 정확히 `Monad`가 일반화하는 모양입니다. `Amb`에 `Monad` 인스턴스를 하나 얹으면, `pure`는 "선택지 없이 바로 성공하는" 경우를, `bind`는 `ambBind` 그 자체를 옮기면 됩니다:

`ambBind`'s nested calls (`ambBind (anElementOf list1) (fun a => ambBind (anElementOf list2) (fun b => …))`) are exactly the shape `Monad` generalizes. Giving `Amb` a `Monad` instance is a matter of transcribing `pure` as "succeed immediately with no choice involved" and `bind` as `ambBind` itself:

```lean
instance : Monad Amb where
  pure x := fun succeed fail => succeed x fail
  bind m f := fun succeed fail => m (fun a fail2 => f a succeed fail2) fail
```

`primeSumPair`가 `do` 표기법으로 다시 쓰이면 다음과 같습니다.

`primeSumPair` rewritten with `do` notation:

```lean
def primeSumPairDo (list1 list2 : List Nat) : Amb (Nat × Nat) := do
  let a ← anElementOf list1
  let b ← anElementOf list2
  ambRequire (isPrime (a + b))
  pure (a, b)

#eval runFirst (primeSumPairDo [1, 3, 5, 8] [20, 35, 110])
-- found: (1, 20)
```

`Amb`가 왜 모나드인지는 이제 타입만 봐도 알 수 있습니다 — `pure`와 `bind`가 SICP의 `analyze-amb`가 각 절 사이에 성공 continuation을 실 꿰듯 이어붙이는 것과 정확히 같은 일을 하기 때문입니다. `do` 표기법은 그 실 꿰기를 대신 써주는 문법일 뿐, `ambBind`가 하던 일을 무엇 하나 바꾸지 않습니다.

Why `Amb` is a monad becomes visible just from the types now — `pure` and `bind` do exactly what SICP's `analyze-amb` does when it threads a success continuation from one clause to the next. `do` notation is only syntax for that threading; it changes nothing about what `ambBind` was already doing.

---

## 4.3.3. 되추적과 부작용 — `IO.Ref`가 다시 등장하는 곳

SICP's assignment case is where the two evaluator concerns of this series collide: a variable assignment made on one branch of the search has to be *undone* if that branch later fails and the search backtracks past it, which means every `set!` needs to install its own tiny failure continuation that reverses the assignment before propagating the failure onward.

SICP의 대입 케이스는 이 시리즈의 두 평가기 관심사가 충돌하는 지점입니다 — 탐색의 한 가지에서 이루어진 변수 대입은, 그 가지가 나중에 실패해서 탐색이 그 지점을 지나 되추적하면 *되돌려져야* 합니다. 즉 모든 `set!`은 실패를 전파하기 전에 대입을 되돌리는 자신만의 작은 실패 continuation을 설치해야 합니다.

Since Lean already forces mutation through `IO.Ref` (as this series established in [3.3](../3-3-modeling-with-mutable-data/)), backtracking-aware assignment in our `Amb` combinators is just "wrap the mutation in a success continuation that remembers the old value, and a matching failure continuation that restores it":

Lean은 이미 변경을 `IO.Ref`를 통해서만 하도록 강제하므로([3.3](../3-3-modeling-with-mutable-data/)에서 확립한 대로), 우리 `Amb` 콤비네이터에서 되추적을 인식하는 대입은 그저 "이전 값을 기억하는 성공 continuation으로 변경을 감싸고, 그 값을 복원하는 짝이 되는 실패 continuation을 다는 것"입니다.

```lean
def ambSet (r : IO.Ref Nat) (newVal : Nat) : Amb Unit :=
  fun succeed fail =>
    fun _ => do
      let oldVal ← r.get
      r.set newVal
      succeed () (fun _ => do r.set oldVal; fail ())
```

The parallel to SICP's own `analyze-assignment` is exact: the success continuation captures `oldVal` before mutating, and the failure continuation it hands back undoes the mutation before calling the original `fail`. Nothing here is Lean-specific insight so much as confirmation that SICP's continuation-passing design translates faithfully once you're willing to make the effect (`IO.Ref`) explicit in the type, rather than leaving it as an implicit capability of the host language's `set!`.

SICP 자신의 `analyze-assignment`와 정확히 대응합니다 — 성공 continuation은 변경 전에 `oldVal`을 붙잡아두고, 그것이 돌려주는 실패 continuation은 원래의 `fail`을 호출하기 전에 변경을 되돌립니다. 여기엔 Lean 고유의 특별한 통찰이라기보다, 효과(`IO.Ref`)를 호스트 언어의 암묵적인 `set!` 능력으로 남겨두는 대신 타입에 명시적으로 드러내기만 하면 SICP의 continuation-전달 설계가 충실히 옮겨진다는 확인이 담겨 있습니다.

**연습문제 4.35 (Lean 버전).** SICP는 `an-integer-between`으로 피타고라스 삼조를 찾는 것을 제안합니다. 유한한 탐색 범위이므로 이는 `List` 모나드로 곧바로 옮겨집니다 — `guard`가 `require`를 대신하고, `List.range`가 유한 선택지를 제공합니다.

```lean
def pythagoreanTriples (low high : Nat) : List (Nat × Nat × Nat) := do
  let i ← List.range (high + 1) |>.filter (· ≥ low)
  let j ← List.range (high + 1) |>.filter (· ≥ i)
  let k ← List.range (high + 1) |>.filter (· ≥ j)
  guard (i * i + j * j = k * k)
  pure (i, j, k)

#eval pythagoreanTriples 1 20
-- [(3, 4, 5), (5, 12, 13), (6, 8, 10), (8, 15, 17), (9, 12, 15), (12, 16, 20)]
```

이 정의의 재귀는 전부 `List.range`와 `filter` 안에 갇혀 있고 둘 다 구조적으로 종료하므로, 여기에도 `partial`은 필요 없습니다. 다만 SICP의 `an-integer-starting-from` 버전(위·아래 경계가 없는 탐색)으로 이 문제를 다시 풀려 한다면, 4.3.2절에서 짚었던 것과 같은 이유로 `List` 모나드는 쓸 수 없고, 무한 선택을 표현하는 `partial` `Amb` 생성자로 넘어가야 합니다 — SICP가 4.3절 전체에서 반복하는 "언제 되추적이 유한한 List로 충분하고, 언제 진짜 continuation 기반 탐색이 필요한가"라는 질문이 Lean에서는 타입 수준의 선택(`List` 대 `Amb`)이자 종료성 수준의 선택(구조적 재귀 대 `partial`)으로 그대로 드러납니다.

The next post in this series follows SICP into [4.4](../4-4-logic-programming/), where the language stops choosing one value among alternatives and starts searching for *all* the ways a set of logical relations can be satisfied at once — the query language that turns nondeterministic search into something closer to Prolog.

이 시리즈의 다음 글은 SICP를 따라 [4.4](../4-4-logic-programming/)로 넘어갑니다. 거기서는 언어가 대안 중 하나를 고르는 것을 넘어, 논리적 관계들의 집합을 동시에 만족시키는 *모든* 방법을 찾기 시작합니다 — 비결정적 탐색을 Prolog에 가까운 것으로 바꾸는 질의 언어입니다.
