---
title: "간주곡: 전술, 귀납법, 증명 (Interlude: Tactics, Induction, and Proofs)"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "간주곡: 전술, 귀납법, 증명 (Interlude: Tactics, Induction, and Proofs)"
---

# Interlude: Tactics, Induction, and Proofs

## A Note on Proofs and User Interfaces

This book presents the process of writing proofs as if they are written in one go and submitted to Lean, which then replies with error messages that describe what remains to be done.
The actual process of interacting with Lean is much more pleasant.
Lean provides information about the proof as the cursor is moved through it and there are a number of interactive features that make proving easier.
Please consult the documentation of your Lean development environment for more information.

본 교재는 증명을 한 번에 작성하여 Lean에 제출하면 Lean이 남은 작업을 설명하는 오류 메시지로 응답하는 방식으로 증명 과정을 제시합니다. Lean과 실제로 상호작용하는 과정은 훨씬 더 즐겁습니다. Lean은 커서가 증명을 통해 이동할 때 증명에 대한 정보를 제공합니다. 증명을 더 쉽게 하도록 하는 많은 대화형 기능들이 있습니다. 더 많은 정보는 Lean 개발 환경의 설명서를 참조하세요.

The approach in this book that focuses on incrementally building a proof and showing the messages that result demonstrates the kinds of interactive feedback that Lean provides while writing a proof, even though it is much slower than the process used by experts.
At the same time, seeing incomplete proofs evolve towards completeness is a useful perspective on proving.
As your skill in writing proofs increases, Lean's feedback will come to feel less like errors and more like support for your own thought processes.
Learning the interactive approach is very important.

본 교재는 증명을 점진적으로 구축하고 그 결과로 나타나는 메시지들을 보여주는 방식을 취하는데, 이는 전문가들이 사용하는 과정보다 훨씬 느리지만 증명을 작성하는 동안 Lean이 제공하는 대화형 피드백의 종류를 보여줍니다. 동시에 불완전한 증명이 완전성으로 진화하는 것을 보는 것은 증명에 대한 유용한 관점입니다. 증명 작성 능력이 증가함에 따라, Lean의 피드백은 오류라기보다는 자신의 사고 과정에 대한 지원으로 느껴질 것입니다. 대화형 접근 방식을 배우는 것은 매우 중요합니다.

## Recursion and Induction

The functions `plusR_succ_left` and `plusR_zero_left` from the preceding chapter can be seen from two perspectives.
On the one hand, they are recursive functions that build up evidence for a proposition, just as other recursive functions might construct a list, a string, or any other data structure.
On the other, they also correspond to proofs by *mathematical induction*.

이전 장의 함수 `plusR_succ_left`와 `plusR_zero_left`는 두 가지 관점에서 볼 수 있습니다. 한편으로, 이들은 다른 재귀 함수가 리스트, 문자열 또는 다른 데이터 구조를 구성할 수 있는 것처럼, 명제에 대한 증거를 구축하는 재귀 함수입니다. 반면에, 이들은 또한 수학적 귀납법에 의한 증명에 해당합니다.

Mathematical induction is a proof technique where a statement is proven for *all* natural numbers in two steps:

수학적 귀납법은 명제를 두 가지 단계로 모든 자연수에 대해 증명하는 증명 기법입니다:

1. The statement is shown to hold for `0`. This is called the *base case*.
2. Under the assumption that the statement holds for some arbitrarily chosen number `n`, it is shown to hold for `n + 1`. This is called the *induction step*. The assumption that the statement holds for `n` is called the *induction hypothesis*.

1. 명제가 `0`에 대해 성립함을 보입니다. 이를 기저 경우(base case)라고 부릅니다.
2. 임의로 선택된 수 `n`에 대해 명제가 성립한다는 가정 하에, `n + 1`에 대해서도 성립함을 보입니다. 이를 귀납 단계(induction step)라고 부릅니다. 명제가 `n`에 대해 성립한다는 가정을 귀납 가설(induction hypothesis)이라고 부릅니다.

Because it's impossible to check the statement for *every* natural number, induction provides a means of writing a proof that could, in principle, be expanded to any particular natural number.
For example, if a concrete proof were desired for the number 3, then it could be constructed by using first the base case and then the induction step three times, to show the statement for 0, 1, 2, and finally 3.
Thus, it proves the statement for all natural numbers.

모든 자연수에 대해 명제를 검증하는 것이 불가능하므로, 귀납법은 원칙적으로 임의의 특정 자연수로 확장될 수 있는 증명을 작성하는 수단을 제공합니다. 예를 들어, 숫자 3에 대한 구체적인 증명을 원한다면, 먼저 기저 경우를 사용하고 그 다음 귀납 단계를 세 번 사용하여 0, 1, 2, 그리고 최종적으로 3에 대해 명제를 보임으로써 구성할 수 있습니다. 따라서 이는 모든 자연수에 대해 명제를 증명합니다.

## The Induction Tactic

Writing proofs by induction as recursive functions that use helpers such as `congrArg` does not always do a good job of expressing the intentions behind the proof.
While recursive functions indeed have the structure of induction, they should probably be viewed as an *encoding* of a proof.
Furthermore, Lean's tactic system provides a number of opportunities to automate the construction of a proof that are not available when writing the recursive function explicitly.
Lean provides an induction *tactic* that can carry out an entire proof by induction in a single tactic block.
Behind the scenes, Lean constructs the recursive function that corresponds the use of induction.

귀납법을 사용하는 증명을 `congrArg`와 같은 보조 함수를 사용하는 재귀 함수로 작성하는 것이 항상 증명 뒤의 의도를 잘 표현하지는 못합니다. 재귀 함수가 실제로 귀납법의 구조를 가지고 있지만, 이들은 증명의 인코딩으로 봐야 할 것입니다. 더욱이, Lean의 tactic 시스템은 재귀 함수를 명시적으로 작성할 때 사용할 수 없는 증명 구성을 자동화할 수 있는 많은 기회를 제공합니다. Lean은 단일 tactic 블록 내에서 귀납법으로 전체 증명을 수행할 수 있는 귀납법 tactic을 제공합니다. 내부적으로, Lean은 귀납법 사용에 해당하는 재귀 함수를 구성합니다.

To prove `plusR_zero_left` with the `induction` tactic, begin by writing its signature (using `theorem`, because this really is a proof).
Then, use `by induction k` as the body of the definition:

`induction` tactic으로 `plusR_zero_left`를 증명하려면, 그 signature를 먼저 작성하여 시작합니다(`theorem`을 사용합니다. 이것이 실제 증명이기 때문입니다). 그 다음, 정의의 본문으로 `by induction k`를 사용합니다:

```lean
theorem plusR_zero_left (k : Nat) : k = Nat.plusR 0 k := by
  induction k
```

The resulting message states that there are two goals:

```
unsolved goals
zero⊢ 0 = Nat.plusR 0 0

succn✝:Nata✝:n✝ = Nat.plusR 0 n✝⊢ n✝ + 1 = Nat.plusR 0 (n✝ + 1)
```

결과 메시지는 두 개의 목표(goal)가 있음을 나타냅니다.

A tactic block is a program that is run while the Lean type checker processes a file, somewhat like a much more powerful C preprocessor macro.
The tactics generate the actual program.

tactic 블록은 Lean type checker가 파일을 처리하는 동안 실행되는 프로그램으로, 훨씬 더 강력한 C preprocessor macro와 유사합니다. tactic들은 실제 프로그램을 생성합니다.

In the tactic language, there can be a number of goals.
Each goal consists of a type together with some assumptions.
These are analogous to using underscores as placeholders—the type in the goal represents what is to be proved, and the assumptions represent what is in-scope and can be used.
In the case of the goal `case zero`, there are no assumptions and the type is `Nat.zero = Nat.plusR 0 Nat.zero`—this is the theorem statement with `0` instead of `k`.
In the goal `case succ`, there are two assumptions, named `n✝` and `n_ih✝`.
Behind the scenes, the `induction` tactic creates a dependent pattern match that refines the overall type, and `n✝` represents the argument to `Nat.succ` in the pattern.
The assumption `n_ih✝` represents the result of calling the generated function recursively on `n✝`.
Its type is the overall type of the theorem, just with `n✝` instead of `k`.
The type to be fulfilled as part of the goal `case succ` is the overall theorem statement, with `Nat.succ n✝` instead of `k`.

tactic 언어에서는 여러 개의 목표가 있을 수 있습니다. 각 목표는 타입과 몇 가지 가정(assumption)들로 구성됩니다. 이들은 밑줄을 placeholder로 사용하는 것과 유사합니다—목표의 타입은 증명해야 할 것을 나타내고, 가정들은 범위 내에 있고 사용할 수 있는 것을 나타냅니다. `case zero` 목표의 경우, 가정이 없고 타입은 `Nat.zero = Nat.plusR 0 Nat.zero`입니다—이는 `k` 대신 `0`이 있는 정리 문입니다. `case succ` 목표에서는 `n✝`과 `n_ih✝`라는 두 개의 가정이 있습니다. 내부적으로, `induction` tactic은 전체 타입을 정제하는 종속 패턴 매칭을 생성하고, `n✝`는 패턴에서 `Nat.succ`에 대한 인수를 나타냅니다. 가정 `n_ih✝`는 생성된 함수를 `n✝`에 대해 재귀적으로 호출한 결과를 나타냅니다. 그 타입은 정리의 전체 타입과 같지만 `k` 대신 `n✝`을 가집니다. `case succ` 목표의 일부로 충족되어야 할 타입은 `k` 대신 `Nat.succ n✝`을 가진 전체 정리 문입니다.

The two goals that result from the use of the `induction` tactic correspond to the base case and the induction step in the description of mathematical induction.
The base case is `case zero`.
In `case succ`, `n_ih✝` corresponds to the induction hypothesis, while the whole of `case succ` is the induction step.

`induction` tactic의 사용으로 나타나는 두 개의 목표는 수학적 귀납법 설명에서의 기저 경우와 귀납 단계에 해당합니다. 기저 경우는 `case zero`입니다. `case succ`에서, `n_ih✝`는 귀납 가설에 해당하고, `case succ` 전체는 귀납 단계입니다.

The next step in writing the proof is to focus on each of the two goals in turn.
Just as `pure ()` can be used in a `do` block to indicate “do nothing”, the tactic language has a statement `skip` that also does nothing.
This can be used when Lean's syntax requires a tactic, but it's not yet clear which one should be used.
Adding `with` to the end of the `induction` statement provides a syntax that is similar to pattern matching:

증명을 작성하는 다음 단계는 두 개의 목표 각각에 차례로 초점을 맞추는 것입니다. `do` 블록에서 `pure ()`를 “아무것도 하지 않음”을 나타내기 위해 사용할 수 있는 것처럼, tactic 언어는 역시 아무것도 하지 않는 `skip` 문을 가지고 있습니다. 이는 Lean의 구문이 tactic을 요구하지만 어떤 것을 사용해야 할지 아직 명확하지 않을 때 사용할 수 있습니다. `induction` 문의 끝에 `with`을 추가하면 패턴 매칭과 유사한 구문을 제공합니다:

```lean
theorem plusR_zero_left (k : Nat) : k = Nat.plusR 0 k := by
  induction k with
  | zero => skip
  | succ n ih => skip
```

Each of the two `skip` statements has a message associated with it.
The first shows the base case:

```
unsolved goals
zero⊢ 0 = Nat.plusR 0 0
```

두 `skip` 문 각각에는 관련된 메시지가 있습니다. 첫 번째는 기저 경우를 보여줍니다.

The second shows the induction step:

```
unsolved goals
succn:Natih:n = Nat.plusR 0 n⊢ n + 1 = Nat.plusR 0 (n + 1)
```

두 번째는 귀납 단계를 보여줍니다.

In the induction step, the inaccessible names with daggers have been replaced with the names provided after `succ`, namely `n` and `ih`.

귀납 단계에서, dagger가 있는 접근 불가능한 이름들은 `succ` 다음에 제공된 이름(즉, `n`과 `ih`)으로 바뀌었습니다.

The cases after `induction ... with` are not patterns: they consist of the name of a goal followed by zero or more names.
The names are used for assumptions introduced in the goal; it is an error to provide more names than the goal introduces:

`induction ... with` 이후의 cases는 패턴이 아닙니다: 목표의 이름 다음에 0개 이상의 이름으로 구성됩니다. 이름들은 목표에서 도입된 가정들을 위해 사용됩니다; 목표가 도입하는 것보다 많은 이름을 제공하는 것은 오류입니다:

```lean
theorem plusR_zero_left (k : Nat) : k = Nat.plusR 0 k := by
  induction k with
  | zero => skip
  | succ n ih lots of names => skip
```

```
Too many variable names provided at alternative `succ`: 5 provided, but 2 expected
```

Focusing on the base case, the `rfl` tactic works just as well inside of the `induction` tactic as it does in a recursive function:

```lean
theorem plusR_zero_left (k : Nat) : k = Nat.plusR 0 k := by
  induction k with
  | zero => rfl
  | succ n ih => skip
```

기저 경우에 초점을 맞추면, `rfl` tactic은 `induction` tactic 내에서 재귀 함수 내에서처럼 잘 작동합니다.

In the recursive function version of the proof, a type annotation made the expected type something that was easier to understand.
In the tactic language, there are a number of specific ways to transform a goal to make it easier to solve.
The `unfold` tactic replaces a defined name with its definition:

증명의 재귀 함수 버전에서, 타입 annotation은 예상된 타입을 이해하기 더 쉬운 것으로 만들었습니다. tactic 언어에서는 목표를 해결하기 더 쉽도록 변환하는 많은 구체적인 방법들이 있습니다. `unfold` tactic은 정의된 이름을 그 정의로 대체합니다:

```lean
theorem plusR_zero_left (k : Nat) : k = Nat.plusR 0 k := by
  induction k with
  | zero => rfl
  | succ n ih =>
    unfold Nat.plusR
```

Now, the right-hand side of the equality in the goal has become `Nat.plusR 0 n + 1` instead of `Nat.plusR 0 (Nat.succ n)`:

```
unsolved goals
succn:Natih:n = Nat.plusR 0 n⊢ n + 1 = Nat.plusR 0 n + 1
```

이제 목표의 등식의 오른쪽은 `Nat.plusR 0 (Nat.succ n)` 대신 `Nat.plusR 0 n + 1`이 되었습니다.

Instead of appealing to functions like `congrArg` and operators like `▸`, there are tactics that allow equality proofs to be used to transform proof goals.
One of the most important is `rw`, which takes a list of equality proofs and replaces the left side with the right side in the goal.
This almost does the right thing in `plusR_zero_left`:

`congrArg`와 같은 함수들이나 `▸`와 같은 연산자들에 의존하는 대신, 등식 증명을 사용하여 증명 목표를 변환할 수 있는 tactic들이 있습니다. 가장 중요한 것 중 하나는 `rw`로, 등식 증명들의 리스트를 받아 목표에서 왼쪽을 오른쪽으로 대체합니다. 이것은 `plusR_zero_left`에서 거의 올바른 작업을 합니다:

```lean
theorem plusR_zero_left (k : Nat) : k = Nat.plusR 0 k := by
  induction k with
  | zero => rfl
  | succ n ih =>
    unfold Nat.plusR
    rw [ih]
```

However, the direction of the rewrite was incorrect.
Replacing `n` with `Nat.plusR 0 n` made the goal more complicated rather than less complicated:

```
unsolved goals
succn:Natih:n = Nat.plusR 0 n⊢ Nat.plusR 0 n + 1 = Nat.plusR 0 (Nat.plusR 0 n) + 1
```

하지만 rewrite의 방향이 잘못되었습니다. `n`을 `Nat.plusR 0 n`으로 대체하는 것은 목표를 더 간단하게 하기보다는 더 복잡하게 만들었습니다.

This can be remedied by placing a left arrow before `ih` in the call to `rw`, which instructs it to replace the right-hand side of the equality with the left-hand side:

```lean
theorem plusR_zero_left (k : Nat) : k = Nat.plusR 0 k := by
  induction k with
  | zero => rfl
  | succ n ih =>
    unfold Nat.plusR
    rw [←ih]
```

```
All goals completed! 🐙
```

이것은 `rw` 호출에서 `ih` 앞에 왼쪽 화살표를 배치함으로써 해결할 수 있습니다. 이것은 등식의 오른쪽을 왼쪽으로 대체하도록 지시합니다.

This rewrite makes both sides of the equation identical, and Lean takes care of the `rfl` on its own.
The proof is complete.

이 rewrite는 등식의 양쪽을 동일하게 만들고, Lean은 `rfl`을 자체적으로 처리합니다. 증명이 완료되었습니다.

## Tactic Golf

So far, the tactic language has not shown its true value.
The above proof is no shorter than the recursive function; it's merely written in a domain-specific language instead of the full Lean language.
But proofs with tactics can be shorter, easier, and more maintainable.
Just as a lower score is better in the game of golf, a shorter proof is better in the game of tactic golf.

지금까지, tactic 언어는 그 진정한 가치를 보여주지 못했습니다. 위의 증명은 재귀 함수보다 짧지 않습니다; 단지 전체 Lean 언어 대신 도메인 특화 언어로 작성되었을 뿐입니다. 하지만 tactic을 사용한 증명은 더 짧고, 더 쉽고, 더 유지보수하기 좋을 수 있습니다. 골프 게임에서 낮은 스코어가 더 나은 것처럼, tactic 골프 게임에서 더 짧은 증명이 더 나은 것입니다.

The induction step of `plusR_zero_left` can be proved using the simplification tactic `simp`.
Using `simp` on its own does not help:

`plusR_zero_left`의 귀납 단계는 단순화 tactic인 `simp`를 사용하여 증명할 수 있습니다. `simp`를 단독으로 사용하는 것은 도움이 되지 않습니다:

```lean
theorem plusR_zero_left (k : Nat) : k = Nat.plusR 0 k := by
  induction k with
  | zero => rfl
  | succ n ih =>
    simp
```

```
`simp` made no progress
```

However, `simp` can be configured to make use of a set of definitions.
Just like `rw`, these arguments are provided in a list.
Asking `simp` to take the definition of `Nat.plusR` into account leads to a simpler goal:

하지만 `simp`는 정의들의 집합을 사용하도록 설정할 수 있습니다. `rw`와 마찬가지로, 이러한 인수들은 리스트에 제공됩니다. `simp`가 `Nat.plusR`의 정의를 고려하도록 요청하면 더 간단한 목표로 이어집니다.

```lean
theorem plusR_zero_left (k : Nat) : k = Nat.plusR 0 k := by
  induction k with
  | zero => rfl
  | succ n ih =>
    simp [Nat.plusR]
```

```
unsolved goals
succn:Natih:n = Nat.plusR 0 n⊢ n = Nat.plusR 0 n
```

In particular, the goal is now identical to the induction hypothesis.
In addition to automatically proving simple equality statements, the simplifier automatically replaces goals like `Nat.succ A = Nat.succ B` with `A = B`.
Because the induction hypothesis `ih` has exactly the right type, the `exact` tactic can indicate that it should be used:

특히, 이제 목표는 귀납 가설과 동일합니다. 간단한 등식 문을 자동으로 증명하는 것 외에도, simplifier는 `Nat.succ A = Nat.succ B`와 같은 목표를 자동으로 `A = B`로 대체합니다. 귀납 가설 `ih`가 정확히 올바른 타입을 가지고 있기 때문에, `exact` tactic은 그것을 사용해야 함을 나타낼 수 있습니다:

```lean
theorem plusR_zero_left (k : Nat) : k = Nat.plusR 0 k := by
  induction k with
  | zero => rfl
  | succ n ih =>
    simp [Nat.plusR]
    exact ih
```

```
All goals completed! 🐙
```

However, the use of `exact` is somewhat fragile.
Renaming the induction hypothesis, which may happen while “golfing” the proof, would cause this proof to stop working.
The `assumption` tactic solves the current goal if *any* of the assumptions match it:

하지만 `exact`의 사용은 다소 취약합니다. 증명을 “golfing” 할 때 발생할 수 있는 귀납 가설의 이름 변경은 이 증명이 작동하지 않도록 할 것입니다. `assumption` tactic은 가정 중 어떤 것이라도 일치하면 현재 목표를 해결합니다:

```lean
theorem plusR_zero_left (k : Nat) : k = Nat.plusR 0 k := by
  induction k with
  | zero => rfl
  | succ n ih =>
    simp [Nat.plusR]
    assumption
```

```
All goals completed! 🐙
```

This proof is no shorter than the prior proof that used unfolding and explicit rewriting.
However, a series of transformations can make it much shorter, taking advantage of the fact that `simp` can solve many kinds of goals.
The first step is to drop the `with` at the end of `induction`.
For structured, readable proofs, the `with` syntax is convenient.
It complains if any cases are missing, and it shows the structure of the induction clearly.
But shortening proofs can often require a more liberal approach.

이 증명은 unfolding과 명시적 rewriting을 사용한 이전 증명보다 짧지 않습니다. 그러나 일련의 변환들은 `simp`가 많은 종류의 목표를 해결할 수 있다는 사실을 이용하여 그것을 훨씬 더 짧게 만들 수 있습니다. 첫 번째 단계는 `induction`의 끝에서 `with`을 제거하는 것입니다. 구조화된 읽기 쉬운 증명을 위해, `with` 구문은 편리합니다. 어떤 cases가 누락되면 불평하고, 귀납의 구조를 명확히 보여줍니다. 하지만 증명을 단축하려면 종종 더 관대한 접근 방식이 필요합니다.

Using `induction` without `with` simply results in a proof state with two goals.
The `case` tactic can be used to select one of them, just as in the branches of the `induction ... with` tactic.
In other words, the following proof is equivalent to the prior proof:

`with` 없이 `induction`을 사용하면 단순히 두 개의 목표가 있는 증명 상태를 초래합니다. `case` tactic은 `induction`...`with` tactic의 분기에서처럼 그 중 하나를 선택하는 데 사용될 수 있습니다. 즉, 다음 증명은 이전 증명과 동등합니다:

```lean
theorem plusR_zero_left (k : Nat) : k = Nat.plusR 0 k := by
  induction k
  case zero => rfl
  case succ n ih =>
    simp [Nat.plusR]
    assumption
```

```
All goals completed! 🐙
```

In a context with a single goal (namely, `k = Nat.plusR 0 k`), the `induction k` tactic yields two goals.
In general, a tactic will either fail with an error or take a goal and transform it into zero or more new goals.
Each new goal represents what remains to be proved.
If the result is zero goals, then the tactic was a success, and that part of the proof is done.

단일 목표(즉, `k = Nat.plusR 0 k`)를 가진 문맥에서, `induction k` tactic은 두 개의 목표를 생성합니다. 일반적으로, tactic은 오류로 실패하거나 목표를 받아 0개 이상의 새로운 목표로 변환합니다. 각각의 새로운 목표는 증명해야 할 것을 나타냅니다. 결과가 0개의 목표라면, tactic은 성공이고, 그 증명 부분은 완료된 것입니다.

The `<;>` operator takes two tactics as arguments, resulting in a new tactic.
`T1` `<;>` `T2` applies `T1` to the current goal, and then applies `T2` in *all* goals created by `T1`.
In other words, `<;>` enables a general tactic that can solve many kinds of goals to be used on multiple new goals all at once.
One such general tactic is `simp`.

`<;>` 연산자는 두 개의 tactic을 인수로 받아 새로운 tactic을 생성합니다. `T1` `<;>` `T2`는 `T1`을 현재 목표에 적용하고, 그 다음 `T1`이 생성한 모든 목표에 `T2`를 적용합니다. 즉, `<;>`는 많은 종류의 목표를 해결할 수 있는 일반적인 tactic을 여러 개의 새로운 목표에 한 번에 사용할 수 있게 합니다. 이러한 일반적인 tactic 중 하나는 `simp`입니다.

Because `simp` can both complete the proof of the base case and make progress on the proof of the induction step, using it with `induction` and `<;>` shortens the proof:

```lean
theorem plusR_zero_left (k : Nat) : k = Nat.plusR 0 k := by
  induction k <;> simp [Nat.plusR]
```

`simp`는 기저 경우의 증명을 완료하고 귀납 단계의 증명에 진전을 만들 수 있으므로, `induction`과 `<;>`와 함께 사용하면 증명을 단축합니다.

This results in only a single goal, the transformed induction step:

```
unsolved goals
succn✝:Nata✝:n✝ = Nat.plusR 0 n✝⊢ n✝ = Nat.plusR 0 n✝
```

이는 단 하나의 목표인 변환된 귀납 단계를 초래합니다.

Running `assumption` in this goal completes the proof:

이 목표에서 `assumption`을 실행하면 증명이 완료됩니다:

```lean
theorem plusR_zero_left (k : Nat) : k = Nat.plusR 0 k := by
  induction k <;> simp [Nat.plusR] <;> assumption
```

```
All goals completed! 🐙
```

Here, `exact` would not have been possible, because `ih` was never explicitly named.

여기서는 `ih`가 명시적으로 이름 지어지지 않았기 때문에 `exact`을 사용할 수 없었을 것입니다.

For beginners, this proof is not easier to read.
However, a common pattern for expert users is to take care of a number of simple cases with powerful tactics like `simp`, allowing them to focus the text of the proof on the interesting cases.
Additionally, these proofs tend to be more robust in the face of small changes to the functions and datatypes involved in the proof.
The game of tactic golf is a useful part of developing good taste and style when writing proofs.

초보자들에게, 이 증명은 읽기 더 쉽지 않습니다. 그러나 전문가 사용자들에게는 일반적인 패턴은 `simp`와 같은 강력한 tactic으로 여러 개의 간단한 경우들을 처리하여, 증명의 텍스트를 흥미로운 경우들에 집중할 수 있게 하는 것입니다. 추가로, 이러한 증명들은 증명에 관련된 함수들과 데이터타입들의 작은 변경에 대해 더 견고한 경향이 있습니다. tactic 골프 게임은 증명을 작성할 때 좋은 취향과 스타일을 개발하는 데 유용한 부분입니다.

## Induction on Other Datatypes

Mathematical induction proves a statement for natural numbers by providing a base case for `Nat.zero` and an induction step for `Nat.succ`.
The principle of induction is also valid for other datatypes.
Constructors without recursive arguments form the base cases, while constructors with recursive arguments form the induction steps.
The ability to carry out proofs by induction is the very reason why they are called *inductive* datatypes.

수학적 귀납법은 `Nat.zero`에 대한 기저 경우와 `Nat.succ`에 대한 귀납 단계를 제공하여 자연수에 대한 명제를 증명합니다. 귀납법의 원칙은 다른 데이터타입들에 대해서도 유효합니다. 재귀 인수 없는 생성자들은 기저 경우를 형성하고, 재귀 인수를 가진 생성자들은 귀납 단계를 형성합니다. 귀납법으로 증명을 수행할 수 있다는 능력이 그들이 귀납 데이터타입이라고 불리는 매우 이유입니다.

One example of this is induction on binary trees.
Induction on binary trees is a proof technique where a statement is proven for *all* binary trees in two steps:

이의 한 예는 이진 트리에 대한 귀납법입니다. 이진 트리에 대한 귀납법은 명제를 두 단계로 모든 이진 트리에 대해 증명하는 증명 기법입니다:

1. The statement is shown to hold for `BinTree.leaf`. This is called the base case.
2. Under the assumption that the statement holds for some arbitrarily chosen trees `l` and `r`, it is shown to hold for `BinTree.branch l x r`, where `x` is an arbitrarily-chosen new data point. This is called the *induction step*. The assumptions that the statement holds for `l` and `r` are called the *induction hypotheses*.

1. 명제가 `BinTree.leaf`에 대해 성립함을 보입니다. 이를 기저 경우라고 부릅니다.
2. 임의로 선택된 트리 `l`과 `r`에 대해 명제가 성립한다는 가정 하에, `BinTree.branch l x r`에 대해서도 성립함을 보입니다. 여기서 `x`는 임의로 선택된 새로운 데이터 포인트입니다. 이를 귀납 단계라고 부릅니다. `l`과 `r`에 대해 명제가 성립한다는 가정들을 귀납 가설들이라고 부릅니다.

`BinTree.count` counts the number of branches in a tree:

```lean
def BinTree.count : BinTree α → Nat
  | .leaf => 0
  | .branch l _ r =>
    1 + l.count + r.count
```

`BinTree.count`는 트리의 가지 수를 세는 함수입니다.

[Mirroring a tree](../ch04/) does not change the number of branches in it.
This can be proven using induction on trees.
The first step is to state the theorem and invoke `induction`:

트리를 뒤집기(mirroring)는 그 안의 가지 수를 변경하지 않습니다. 이는 트리에 대한 귀납법을 사용하여 증명할 수 있습니다. 첫 번째 단계는 정리를 진술하고 `induction`을 호출하는 것입니다:

```lean
theorem BinTree.mirror_count (t : BinTree α) :
    t.mirror.count = t.count := by
  induction t with
  | leaf => skip
  | branch l x r ihl ihr => skip
```

The base case states that counting the mirror of a leaf is the same as counting the leaf:

```
unsolved goals
leafα:Type⊢ leaf.mirror.count = leaf.count
```

기저 경우는 잎의 거울상의 수를 세는 것이 잎을 세는 것과 같다는 것을 진술합니다.

The induction step allows the assumption that mirroring the left and right subtrees won't affect their branch counts, and requests a proof that mirroring a branch with these subtrees also preserves the overall branch count:

```
unsolved goals
branchα:Typel:BinTree αx:αr:BinTree αihl:l.mirror.count = l.countihr:r.mirror.count = r.count⊢ (l.branch x r).mirror.count = (l.branch x r).count
```

귀납 단계는 좌측과 우측 부분트리를 뒤집기가 그들의 가지 수에 영향을 주지 않을 것이라는 가정을 허용하고, 이러한 부분트리를 가진 가지를 뒤집기도 전체 가지 수를 보존한다는 증명을 요청합니다.

The base case is true because mirroring `leaf` results in `leaf`, so the left and right sides are definitionally equal.
This can be expressed by using `simp` with instructions to unfold `BinTree.mirror`:

기저 경우는 참입니다. 왜냐하면 `leaf`를 뒤집기는 `leaf`를 낳기 때문입니다. 그래서 좌측과 우측은 정의상 같습니다. 이는 `BinTree.mirror`를 unfold하도록 지시하는 `simp`를 사용하여 표현할 수 있습니다:

```lean
theorem BinTree.mirror_count (t : BinTree α) :
    t.mirror.count = t.count := by
  induction t with
  | leaf => simp [BinTree.mirror]
  | branch l x r ihl ihr => skip
```

In the induction step, nothing in the goal immediately matches the induction hypotheses.
Simplifying using the definitions of `BinTree.count` and `BinTree.mirror` reveals the relationship:

```lean
theorem BinTree.mirror_count (t : BinTree α) :
    t.mirror.count = t.count := by
  induction t with
  | leaf => simp [BinTree.mirror]
  | branch l x r ihl ihr =>
    simp [BinTree.mirror, BinTree.count]
```

귀납 단계에서, 목표의 어떤 것도 귀납 가설과 즉시 일치하지 않습니다. `BinTree.count`와 `BinTree.mirror`의 정의를 사용하여 단순화하면 그 관계를 드러냅니다.

```
unsolved goals
branchα:Typel:BinTree αx:αr:BinTree αihl:l.mirror.count = l.countihr:r.mirror.count = r.count⊢ 1 + r.mirror.count + l.mirror.count = 1 + l.count + r.count
```

Both induction hypotheses can be used to rewrite the left-hand side of the goal into something almost like the right-hand side:

두 귀납 가설은 모두 목표의 좌측을 오른쪽과 유사한 것으로 rewrite하는 데 사용할 수 있습니다:

```lean
theorem BinTree.mirror_count (t : BinTree α) :
    t.mirror.count = t.count := by
  induction t with
  | leaf => simp [BinTree.mirror]
  | branch l x r ihl ihr =>
    simp [BinTree.mirror, BinTree.count]
    rw [ihl, ihr]
```

```
unsolved goals
branchα:Typel:BinTree αx:αr:BinTree αihl:l.mirror.count = l.countihr:r.mirror.count = r.count⊢ 1 + r.count + l.count = 1 + l.count + r.count
```

The `simp` tactic can use additional arithmetic identities when passed the `+arith` option.
It is enough to prove this goal, yielding:

`simp` tactic은 `+arith` 옵션을 전달받을 때 추가 산술 항등식을 사용할 수 있습니다. 이는 이 목표를 증명하기에 충분하며, 다음을 낳습니다:

```lean
theorem BinTree.mirror_count (t : BinTree α) :
    t.mirror.count = t.count := by
  induction t with
  | leaf => simp [BinTree.mirror]
  | branch l x r ihl ihr =>
    simp [BinTree.mirror, BinTree.count]
    rw [ihl, ihr]
    simp +arith
```

```
All goals completed! 🐙
```

In addition to definitions to be unfolded, the simplifier can also be passed names of equality proofs to use as rewrites while it simplifies proof goals.
`BinTree.mirror_count` can also be written:

unfold될 정의들 외에도, simplifier는 증명 목표를 단순화하는 동안 rewrite로 사용할 등식 증명들의 이름을 전달받을 수 있습니다. `BinTree.mirror_count`는 또한 다음과 같이 작성할 수 있습니다:

```lean
theorem BinTree.mirror_count (t : BinTree α) :
    t.mirror.count = t.count := by
  induction t with
  | leaf => simp [BinTree.mirror]
  | branch l x r ihl ihr =>
    simp +arith [BinTree.mirror, BinTree.count, ihl, ihr]
```

```
All goals completed! 🐙
```

As proofs grow more complicated, listing assumptions by hand can become tedious.
Furthermore, manually writing assumption names can make it more difficult to re-use proof steps for multiple subgoals.
The argument `*` to `simp` or `simp +arith` instructs them to use *all* assumptions while simplifying or solving the goal.
In other words, the proof could also be written:

증명이 더 복잡해지면, 가정들을 손으로 나열하는 것은 지루할 수 있습니다. 또한, 수동으로 가정 이름을 작성하는 것은 여러 부분목표들에 대해 증명 단계를 다시 사용하기 더 어렵게 만들 수 있습니다. `simp` 또는 `simp +arith`에 대한 `*` 인수는 목표를 단순화하거나 해결하는 동안 모든 가정을 사용하도록 지시합니다. 다시 말해, 증명을 다음과 같이 작성할 수도 있습니다:

```lean
theorem BinTree.mirror_count (t : BinTree α) :
    t.mirror.count = t.count := by
  induction t with
  | leaf => simp [BinTree.mirror]
  | branch l x r ihl ihr =>
    simp +arith [BinTree.mirror, BinTree.count, *]
```

```
All goals completed! 🐙
```

Because both branches are using the simplifier, the proof can be reduced to:

두 분기 모두 simplifier를 사용하고 있으므로, 증명을 다음과 같이 축약할 수 있습니다:

```lean
theorem BinTree.mirror_count (t : BinTree α) :
    t.mirror.count = t.count := by
  induction t <;> simp +arith [BinTree.mirror, BinTree.count, *]
```

```
All goals completed! 🐙
```

## Exercises

* Prove `plusR_succ_left` using the `induction ... with` tactic.
* Rewrite the proof of `plusR_succ_left` to use `<;>` in a single line.
* Prove that appending lists is associative using induction on lists:

  ```lean
  theorem List.append_assoc (xs ys zs : List α) :
      xs ++ (ys ++ zs) = (xs ++ ys) ++ zs
  ```
