---
title: "동치 증명하기 (Proving Equivalence)"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "동치 증명하기 (Proving Equivalence)"
---

# Proving Equivalence

Programs that have been rewritten to use tail recursion and an accumulator can look quite different from the original program.
The original recursive function is often much easier to understand, but it runs the risk of exhausting the stack at run time.
After testing both versions of the program on examples to rule out simple bugs, proofs can be used to show once and for all that the programs are equivalent.

꼬리 재귀와 누적자를 사용하도록 다시 작성된 프로그램은 원본 프로그램과 상당히 다르게 보일 수 있습니다.
원본 재귀 함수는 종종 훨씬 더 이해하기 쉽지만, 런타임에 스택이 소진될 위험이 있습니다.
간단한 버그를 배제하기 위해 프로그램의 두 버전을 예제에서 테스트한 후, 프로그램이 동등함을 한 번에 표시하기 위해 증명을 사용할 수 있습니다.

## 8.2.1. Proving `sum` Equal

To prove that both versions of `sum` are equal, begin by writing the theorem statement with a stub proof:

두 버전의 `sum`이 동등함을 증명하려면, 스텁 증명(stub proof)과 함께 정리(theorem) 명제문을 작성하여 시작합니다:

```lean
theorem non_tail_sum_eq_tail_sum : NonTail.sum = Tail.sum := by
  skip
```

As expected, Lean describes an unsolved goal:

예상대로 Lean은 해결되지 않은 목표를 설명합니다:

```
unsolved goals
⊢ NonTail.sum = Tail.sum
```

The `rfl` tactic cannot be applied here because `NonTail.sum` and `Tail.sum` are not definitionally equal.

`NonTail.sum`과 `Tail.sum`이 정의상 동등하지 않기 때문에 `rfl` tactic을 여기에 적용할 수 없습니다.
Functions can be equal in more ways than just definitional equality, however.

그러나 함수는 정의상 동등성 이상의 많은 방식으로 같을 수 있습니다.
It is also possible to prove that two functions are equal by proving that they produce equal outputs for the same input.

같은 입력에 대해 같은 결과를 생성함을 증명함으로써 두 함수가 같음을 증명하는 것도 가능합니다.
In other words, `f = g` can be proved by proving that `f(x) = g(x)` for all possible inputs `x`.

다시 말해, 모든 가능한 입력 `x`에 대해 `f(x) = g(x)`임을 증명함으로써 `f = g`를 증명할 수 있습니다.
This principle is called *function extensionality*.

이 원리를 *function extensionality*(함수 확장성)이라고 합니다.
Function extensionality is exactly the reason why `NonTail.sum` equals `Tail.sum`: they both sum lists of numbers.

Function extensionality가 정확히 `NonTail.sum`이 `Tail.sum`과 같은 이유입니다: 둘 다 숫자 목록을 합산합니다.

In Lean's tactic language, function extensionality is invoked using `funext`, followed by a name to be used for the arbitrary argument.

Lean의 tactic 언어에서 function extensionality는 `funext`를 사용하여 호출되며, 그 뒤에 임의 인수에 사용할 이름이 따릅니다.
The arbitrary argument is added as an assumption to the context, and the goal changes to require a proof that the functions applied to this argument are equal:

임의 인수가 컨텍스트에 가정으로 추가되고, 목표는 이 인수에 적용된 함수들이 같음을 증명하도록 변경됩니다:

```lean
theorem non_tail_sum_eq_tail_sum : NonTail.sum = Tail.sum := by
  funext xs
```

```
unsolved goals
hxs:List Nat⊢ NonTail.sum xs = Tail.sum xs
```

This goal can be proved by induction on the argument `xs`.

이 목표는 인수 `xs`에 대한 귀납법으로 증명할 수 있습니다.
Both `sum` functions return `0` when applied to the empty list, which serves as a base case.

두 `sum` 함수 모두 빈 목록에 적용될 때 `0`을 반환하며, 이는 기저 사례(base case)로 작용합니다.
Adding a number to the beginning of the input list causes both functions to add that number to the result, which serves as an induction step.

입력 목록의 시작에 숫자를 추가하면 두 함수 모두 그 숫자를 결과에 더하며, 이는 귀납 단계(induction step)로 작용합니다.
Invoking the `induction` tactic results in two goals:

`induction` tactic을 호출하면 두 개의 목표가 생성됩니다:

```lean
theorem non_tail_sum_eq_tail_sum : NonTail.sum = Tail.sum := by
  funext xs
  induction xs with
  | nil => skip
  | cons y ys ih => skip
```

```
unsolved goals
h.nil⊢ NonTail.sum [] = Tail.sum []
```

```
unsolved goals
h.consy:Natys:List Natih:NonTail.sum ys = Tail.sum ys⊢ NonTail.sum (y :: ys) = Tail.sum (y :: ys)
```

The base case for `nil` can be solved using `rfl`, because both functions return `0` when passed the empty list:

`nil`에 대한 기저 사례는 `rfl`을 사용하여 해결할 수 있습니다. 왜냐하면 두 함수 모두 빈 목록을 전달받으면 `0`을 반환하기 때문입니다:

```lean
theorem non_tail_sum_eq_tail_sum : NonTail.sum = Tail.sum := by
  funext xs
  induction xs with
  | nil => rfl
  | cons y ys ih => skip
```

The first step in solving the induction step is to simplify the goal, asking `simp` to unfold `NonTail.sum` and `Tail.sum`:

귀납 단계를 해결하는 첫 번째 단계는 목표를 단순화하여 `simp`에게 `NonTail.sum`과 `Tail.sum`을 전개하도록 요청하는 것입니다:

```lean
theorem non_tail_sum_eq_tail_sum : NonTail.sum = Tail.sum := by
  funext xs
  induction xs with
  | nil => rfl
  | cons y ys ih =>
    simp [NonTail.sum, Tail.sum]
```

```
unsolved goals
h.consy:Natys:List Natih:NonTail.sum ys = Tail.sum ys⊢ y + NonTail.sum ys = Tail.sumHelper 0 (y :: ys)
```

Unfolding `Tail.sum` revealed that it immediately delegates to `Tail.sumHelper`, which should also be simplified:

`Tail.sum`을 전개하면 이것이 즉시 `Tail.sumHelper`에 위임함이 드러나며, 이것도 단순화되어야 합니다:

```lean
theorem non_tail_sum_eq_tail_sum : NonTail.sum = Tail.sum := by
  funext xs
  induction xs with
  | nil => rfl
  | cons y ys ih =>
    simp [NonTail.sum, Tail.sum, Tail.sumHelper]
```

In the resulting goal, `sumHelper` has taken a step of computation and added `y` to the accumulator:

결과 목표에서 `sumHelper`는 계산의 한 단계를 거쳤으며 누적자(accumulator)에 `y`를 추가했습니다:

```
unsolved goals
h.consy:Natys:List Natih:NonTail.sum ys = Tail.sum ys⊢ y + NonTail.sum ys = Tail.sumHelper y ys
```

Rewriting with the induction hypothesis removes all mentions of `NonTail.sum` from the goal:

귀납 가설(induction hypothesis)을 사용하여 다시 쓰면 목표에서 `NonTail.sum`의 모든 언급이 제거됩니다:

```lean
theorem non_tail_sum_eq_tail_sum : NonTail.sum = Tail.sum := by
  funext xs
  induction xs with
  | nil => rfl
  | cons y ys ih =>
    simp [NonTail.sum, Tail.sum, Tail.sumHelper]
    rw [ih]
```

```
unsolved goals
h.consy:Natys:List Natih:NonTail.sum ys = Tail.sum ys⊢ y + Tail.sum ys = Tail.sumHelper y ys
```

This new goal states that adding some number to the sum of a list is the same as using that number as the initial accumulator in `sumHelper`.

이 새 목표는 리스트의 합에 어떤 숫자를 더하는 것이 그 숫자를 `sumHelper`의 초기 누적자로 사용하는 것과 같음을 나타냅니다.

For the sake of clarity, this new goal can be proved as a separate theorem:

명확성을 위해 이 새 목표는 별도의 정리로 증명될 수 있습니다:

```lean
theorem helper_add_sum_accum (xs : List Nat) (n : Nat) :
    n + Tail.sum xs = Tail.sumHelper n xs := by
  skip
```

```
unsolved goals
xs:List Natn:Nat⊢ n + Tail.sum xs = Tail.sumHelper n xs
```

Once again, this is a proof by induction where the base case uses `rfl`:

다시 한 번, 이것은 기저 사례가 `rfl`을 사용하는 귀납법에 의한 증명입니다:

```lean
theorem helper_add_sum_accum (xs : List Nat) (n : Nat) :
    n + Tail.sum xs = Tail.sumHelper n xs := by
  induction xs with
  | nil => rfl
  | cons y ys ih => skip
```

```
unsolved goals
consn y:Natys:List Natih:n + Tail.sum ys = Tail.sumHelper n ys⊢ n + Tail.sum (y :: ys) = Tail.sumHelper n (y :: ys)
```

Because this is an inductive step, the goal should be simplified until it matches the induction hypothesis `ih`.

이것이 귀납 단계이기 때문에 목표는 귀납 가설 `ih`와 일치할 때까지 단순화되어야 합니다.
Simplifying, using the definitions of `Tail.sum` and `Tail.sumHelper`, results in the following:

`Tail.sum`과 `Tail.sumHelper`의 정의를 사용하여 단순화하면 다음과 같은 결과가 나옵니다:

```lean
theorem helper_add_sum_accum (xs : List Nat) (n : Nat) :
    n + Tail.sum xs = Tail.sumHelper n xs := by
  induction xs with
  | nil => rfl
  | cons y ys ih =>
    simp [Tail.sum, Tail.sumHelper]
```

```
unsolved goals
consn y:Natys:List Natih:n + Tail.sum ys = Tail.sumHelper n ys⊢ n + Tail.sumHelper y ys = Tail.sumHelper (y + n) ys
```

Ideally, the induction hypothesis could be used to replace `Tail.sumHelper (y + n) ys`, but they don't match.

이상적으로는 귀납 가설을 사용하여 `Tail.sumHelper (y + n) ys`를 대체할 수 있지만, 일치하지 않습니다.
The induction hypothesis can be used for `Tail.sumHelper n ys`, not `Tail.sumHelper (y + n) ys`.

귀납 가설은 `Tail.sumHelper n ys`에는 사용할 수 있지만, `Tail.sumHelper (y + n) ys`에는 사용할 수 없습니다.
In other words, this proof is stuck.

다시 말해, 이 증명은 막혔습니다.
## 8.2.2. A Second Attempt

Rather than attempting to muddle through the proof, it's time to take a step back and think.

증명을 무리하게 해치려고 하는 대신, 한 발 물러나서 생각해야 할 때입니다.
Why is it that the tail-recursive version of the function is equal to the non-tail-recursive version?

왜 함수의 꼬리 재귀 버전이 비꼬리 재귀 버전과 같을까요?
Fundamentally speaking, at each entry in the list, the accumulator grows by the same amount as would be added to the result of the recursion.

기본적으로 말하면, 리스트의 각 항목에서 누적자는 재귀 결과에 더해질 것과 같은 양만큼 증가합니다.
This insight can be used to write an elegant proof.

이 통찰력을 사용하여 우아한 증명을 작성할 수 있습니다.
Crucially, the proof by induction must be set up such that the induction hypothesis can be applied to *any* accumulator value.

결정적으로, 귀납법에 의한 증명은 귀납 가설을 *모든* 누적자 값에 적용할 수 있도록 설정되어야 합니다.

Discarding the prior attempt, the insight can be encoded as the following statement:

이전 시도를 버리고, 이 통찰력을 다음 명제로 인코딩할 수 있습니다:

```lean
theorem non_tail_sum_eq_helper_accum (xs : List Nat) :
    (n : Nat) → n + NonTail.sum xs = Tail.sumHelper n xs := by
  skip
```

In this statement, it's very important that `n` is part of the type that's after the colon.

이 명제에서 중요한 것은 `n`이 콜론 뒤의 타입의 일부라는 것입니다.
The resulting goal begins with `∀ (n : Nat)`, which is short for “For all `n`”:

```
unsolved goals
xs:List Nat⊢ ∀ (n : Nat), n + NonTail.sum xs = Tail.sumHelper n xs
```

Using the induction tactic results in goals that include this “for all” statement:

```lean
theorem non_tail_sum_eq_helper_accum (xs : List Nat) :
    (n : Nat) → n + NonTail.sum xs = Tail.sumHelper n xs := by
  induction xs with
  | nil => skip
  | cons y ys ih => skip
```

In the `nil` case, the goal is:

`nil` 경우의 목표는:

```
unsolved goals
nil⊢ ∀ (n : Nat), n + NonTail.sum [] = Tail.sumHelper n []
```

For the induction step for `cons`, both the induction hypothesis and the specific goal contain the “for all `n`”:

```
unsolved goals
consy:Natys:List Natih:∀ (n : Nat), n + NonTail.sum ys = Tail.sumHelper n ys⊢ ∀ (n : Nat), n + NonTail.sum (y :: ys) = Tail.sumHelper n (y :: ys)
```

In other words, the goal has become more challenging to prove, but the induction hypothesis is correspondingly more useful.

다시 말해, 목표는 증명하기 더 어려워졌지만, 귀납 가설은 그에 따라 더 유용합니다.

A mathematical proof for a statement that beings with “for all `x`” should assume some arbitrary `x`, and prove the statement.
“Arbitrary” means that no additional properties of `x` are assumed, so the resulting statement will work for *any* `x`.
In Lean, a “for all” statement is a dependent function: no matter which specific value it is applied to, it will return evidence of the proposition.
Similarly, the process of picking an arbitrary `x` is the same as using `fun x => ...`.

마찬가지로 임의의 `x`를 선택하는 과정은 `fun x => ...`를 사용하는 것과 같습니다.
In the tactic language, this process of selecting an arbitrary `x` is performed using the `intro` tactic, which produces the function behind the scenes when the tactic script has completed.

tactic 언어에서 임의의 `x`를 선택하는 이 과정은 `intro` tactic을 사용하여 수행되며, tactic 스크립트가 완료되었을 때 함수를 백그라운드에서 생성합니다.
The `intro` tactic should be provided with the name to be used for this arbitrary value.

`intro` tactic에는 이 임의 값에 사용할 이름이 제공되어야 합니다.

Using the `intro` tactic in the `nil` case removes the `∀ (n : Nat),` from the goal, and adds an assumption `n : Nat`:

`nil` 경우에서 `intro` tactic을 사용하면 목표에서 `∀ (n : Nat),`이 제거되고 가정 `n : Nat`이 추가됩니다:

```lean
theorem non_tail_sum_eq_helper_accum (xs : List Nat) :
    (n : Nat) → n + NonTail.sum xs = Tail.sumHelper n xs := by
  induction xs with
  | nil => intro n
  | cons y ys ih => skip
```

```
unsolved goals
niln:Nat⊢ n + NonTail.sum [] = Tail.sumHelper n []
```

Both sides of this propositional equality are definitionally equal to `n`, so `rfl` suffices:

이 명제 동등성의 양쪽은 정의상 `n`과 같으므로 `rfl`만으로 충분합니다:

```lean
theorem non_tail_sum_eq_helper_accum (xs : List Nat) :
    (n : Nat) → n + NonTail.sum xs = Tail.sumHelper n xs := by
  induction xs with
  | nil =>
    intro n
    rfl
  | cons y ys ih => skip
```

The `cons` goal also contains a “for all”:

This suggests the use of `intro`.

이는 `intro`의 사용을 제안합니다.

```lean
theorem non_tail_sum_eq_helper_accum (xs : List Nat) :
    (n : Nat) → n + NonTail.sum xs = Tail.sumHelper n xs := by
  induction xs with
  | nil =>
    intro n
    rfl
  | cons y ys ih =>
    intro n
```

```
unsolved goals
consy:Natys:List Natih:∀ (n : Nat), n + NonTail.sum ys = Tail.sumHelper n ysn:Nat⊢ n + NonTail.sum (y :: ys) = Tail.sumHelper n (y :: ys)
```

The proof goal now contains both `NonTail.sum` and `Tail.sumHelper` applied to `y :: ys`.

증명 목표는 이제 `NonTail.sum`과 `Tail.sumHelper` 모두를 `y :: ys`에 적용한 것을 포함합니다.
The simplifier can make the next step more clear:

단순화기(simplifier)는 다음 단계를 더 명확하게 할 수 있습니다:

```lean
theorem non_tail_sum_eq_helper_accum (xs : List Nat) :
    (n : Nat) → n + NonTail.sum xs = Tail.sumHelper n xs := by
  induction xs with
  | nil =>
    intro n
    rfl
  | cons y ys ih =>
    intro n
    simp [NonTail.sum, Tail.sumHelper]
```

```
unsolved goals
consy:Natys:List Natih:∀ (n : Nat), n + NonTail.sum ys = Tail.sumHelper n ysn:Nat⊢ n + (y + NonTail.sum ys) = Tail.sumHelper (y + n) ys
```

This goal is very close to matching the induction hypothesis.

이 목표는 귀납 가설과 일치하는 데 매우 가깝습니다.
There are two ways in which it does not match:

일치하지 않는 두 가지 방식이 있습니다:

* The left-hand side of the equation is `n + (y + NonTail.sum ys)`, but the induction hypothesis needs the left-hand side to be a number added to `NonTail.sum ys`.
  In other words, this goal should be rewritten to `(n + y) + NonTail.sum ys`, which is valid because addition of natural numbers is associative.
* When the left side has been rewritten to `(y + n) + NonTail.sum ys`, the accumulator argument on the right side should be `n + y` rather than `y + n` in order to match.
  This rewrite is valid because addition is also commutative.

The associativity and commutativity of addition have already been proved in Lean's standard library.

덧셈의 결합 법칙과 교환 법칙은 이미 Lean의 표준 라이브러리에서 증명되었습니다.
The proof of associativity is named `Nat.add_assoc`, and its type is `(n m k : Nat) → (n + m) + k = n + (m + k)`, while the proof of commutativity is called `Nat.add_comm` and has type `(n m : Nat) → n + m = m + n`.

결합 법칙의 증명은 `Nat.add_assoc`으로 명명되고 그 타입은 `(n m k : Nat) → (n + m) + k = n + (m + k)`이며, 교환 법칙의 증명은 `Nat.add_comm`으로 불리고 타입은 `(n m : Nat) → n + m = m + n`입니다.
Normally, the `rw` tactic is provided with an expression whose type is an equality.

일반적으로 `rw` tactic에는 동등성 타입을 가진 표현식이 제공됩니다.
However, if the argument is instead a dependent function whose return type is an equality, it attempts to find arguments to the function that would allow the equality to match something in the goal.

그러나 인수가 반환 타입이 동등성인 dependent function인 경우, 동등성이 목표의 무언가와 일치하도록 하는 함수 인수를 찾으려고 시도합니다.
There is only one opportunity to apply associativity, though the direction of the rewrite must be reversed because the right side of the equality in `(n + m) + k = n + (m + k)` is the one that matches the proof goal:

결합 법칙을 적용할 기회는 단 한 번이지만, `(n + m) + k = n + (m + k)`의 동등성에서 오른쪽이 증명 목표와 일치하므로 다시 쓰는 방향을 반대로 해야 합니다:

```lean
theorem non_tail_sum_eq_helper_accum (xs : List Nat) :
    (n : Nat) → n + NonTail.sum xs = Tail.sumHelper n xs := by
  induction xs with
  | nil =>
    intro n
    rfl
  | cons y ys ih =>
    intro n
    simp [NonTail.sum, Tail.sumHelper]
    rw [←Nat.add_assoc]
```

```
unsolved goals
consy:Natys:List Natih:∀ (n : Nat), n + NonTail.sum ys = Tail.sumHelper n ysn:Nat⊢ n + y + NonTail.sum ys = Tail.sumHelper (y + n) ys
```

Rewriting directly with `rw [Nat.add_comm]`, however, leads to the wrong result.

그러나 `rw [Nat.add_comm]`으로 직접 다시 쓰면 잘못된 결과가 나옵니다.
The `rw` tactic guesses the wrong location for the rewrite, leading to an unintended goal:

`rw` tactic은 다시 쓰기 위치를 잘못 추측하여 의도하지 않은 목표를 만듭니다:

```lean
theorem non_tail_sum_eq_helper_accum (xs : List Nat) :
    (n : Nat) → n + NonTail.sum xs = Tail.sumHelper n xs := by
  induction xs with
  | nil =>
    intro n
    rfl
  | cons y ys ih =>
    intro n
    simp [NonTail.sum, Tail.sumHelper]
    rw [←Nat.add_assoc]
    rw [Nat.add_comm]
```

```
unsolved goals
consy:Natys:List Natih:∀ (n : Nat), n + NonTail.sum ys = Tail.sumHelper n ysn:Nat⊢ NonTail.sum ys + (n + y) = Tail.sumHelper (y + n) ys
```

This can be fixed by explicitly providing `y` and `n` as arguments to `Nat.add_comm`:

이는 `y`와 `n`을 `Nat.add_comm`의 인수로 명시적으로 제공하여 수정할 수 있습니다:

```lean
theorem non_tail_sum_eq_helper_accum (xs : List Nat) :
    (n : Nat) → n + NonTail.sum xs = Tail.sumHelper n xs := by
  induction xs with
  | nil =>
    intro n
    rfl
  | cons y ys ih =>
    intro n
    simp [NonTail.sum, Tail.sumHelper]
    rw [←Nat.add_assoc]
    rw [Nat.add_comm y n]
```

```
unsolved goals
consy:Natys:List Natih:∀ (n : Nat), n + NonTail.sum ys = Tail.sumHelper n ysn:Nat⊢ n + y + NonTail.sum ys = Tail.sumHelper (n + y) ys
```

The goal now matches the induction hypothesis.

이제 목표가 귀납 가설과 일치합니다.
In particular, the induction hypothesis's type is a dependent function type.

특히 귀납 가설의 타입은 dependent function 타입입니다.
Applying `ih` to `n + y` results in exactly the desired type.

`ih`를 `n + y`에 적용하면 정확히 원하는 타입이 됩니다.
The `exact` tactic completes a proof goal if its argument has exactly the desired type:

`exact` tactic은 인수가 정확히 원하는 타입을 가지면 증명 목표를 완료합니다:

```lean
theorem non_tail_sum_eq_helper_accum (xs : List Nat) :
    (n : Nat) → n + NonTail.sum xs = Tail.sumHelper n xs := by
  induction xs with
  | nil =>
    intro n
    rfl
  | cons y ys ih =>
    intro n
    simp [NonTail.sum, Tail.sumHelper]
    rw [←Nat.add_assoc]
    rw [Nat.add_comm y n]
    exact ih (n + y)
```

The actual proof requires only a little additional work to get the goal to match the helper's type.

실제 증명은 목표를 helper의 타입과 일치시키기 위해 약간의 추가 작업만 필요합니다.
The first step is still to invoke function extensionality:

첫 번째 단계는 여전히 function extensionality를 호출하는 것입니다:

```lean
theorem non_tail_sum_eq_tail_sum : NonTail.sum = Tail.sum := by
  funext xs
```

The next step is unfold `Tail.sum`, exposing `Tail.sumHelper`:

다음 단계는 `Tail.sum`을 전개하여 `Tail.sumHelper`를 노출합니다:

```lean
theorem non_tail_sum_eq_tail_sum : NonTail.sum = Tail.sum := by
  funext xs
  simp [Tail.sum]
```

```
unsolved goals
hxs:List Nat⊢ NonTail.sum xs = Tail.sumHelper 0 xs
```

Having done this, the types almost match.

이렇게 하면 타입이 거의 일치합니다.
However, the helper has an additional addend on the left side.

그러나 helper는 왼쪽에 추가 피가산수(addend)를 가지고 있습니다.
In other words, the proof goal is `NonTail.sum xs = Tail.sumHelper 0 xs`, but applying `non_tail_sum_eq_helper_accum` to `xs` and `0` yields the type `0 + NonTail.sum xs = Tail.sumHelper 0 xs`.

다시 말해, 증명 목표는 `NonTail.sum xs = Tail.sumHelper 0 xs`이지만, `non_tail_sum_eq_helper_accum`을 `xs`와 `0`에 적용하면 타입 `0 + NonTail.sum xs = Tail.sumHelper 0 xs`가 생성됩니다.
Another standard library proof, `Nat.zero_add`, has type `(n : Nat) → 0 + n = n`.

또 다른 표준 라이브러리 증명인 `Nat.zero_add`는 타입 `(n : Nat) → 0 + n = n`을 가집니다.
Applying this function to `NonTail.sum xs` results in an expression with type `0 + NonTail.sum xs = NonTail.sum xs`, so rewriting from right to left results in the desired goal:

이 함수를 `NonTail.sum xs`에 적용하면 타입 `0 + NonTail.sum xs = NonTail.sum xs`를 가진 표현식이 생성되므로, 오른쪽에서 왼쪽으로 다시 쓰면 원하는 목표가 됩니다:

```lean
theorem non_tail_sum_eq_tail_sum : NonTail.sum = Tail.sum := by
  funext xs
  simp [Tail.sum]
  rw [←Nat.zero_add (NonTail.sum xs)]
```

```
unsolved goals
hxs:List Nat⊢ 0 + NonTail.sum xs = Tail.sumHelper 0 xs
```

Finally, the helper can be used to complete the proof:

마지막으로 helper를 사용하여 증명을 완료할 수 있습니다:

```lean
theorem non_tail_sum_eq_tail_sum : NonTail.sum = Tail.sum := by
  funext xs
  simp [Tail.sum]
  rw [←Nat.zero_add (NonTail.sum xs)]
  exact non_tail_sum_eq_helper_accum xs 0
```

This proof demonstrates a general pattern that can be used when proving that an accumulator-passing tail-recursive function is equal to the non-tail-recursive version.

이 증명은 누적자를 전달하는 꼬리 재귀 함수가 비꼬리 재귀 버전과 같음을 증명할 때 사용할 수 있는 일반적인 패턴을 보여줍니다.
The first step is to discover the relationship between the starting accumulator argument and the final result.

첫 번째 단계는 시작 누적자 인수와 최종 결과 사이의 관계를 발견하는 것입니다.
For instance, beginning `Tail.sumHelper` with an accumulator of `n` results in the final sum being added to `n`, and beginning `Tail.reverseHelper` with an accumulator of `ys` results in the final reversed list being prepended to `ys`.

예를 들어, 누적자 `n`을 사용하여 `Tail.sumHelper`를 시작하면 최종 합이 `n`에 추가되고, 누적자 `ys`를 사용하여 `Tail.reverseHelper`를 시작하면 최종 역순 리스트가 `ys`에 앞에 붙습니다.
The second step is to write down this relationship as a theorem statement and prove it by induction.

두 번째 단계는 이 관계를 정리 명제로 작성하고 귀납법으로 증명하는 것입니다.
While the accumulator is always initialized with some neutral value in practice, such as `0` or `[]`, this more general statement that allows the starting accumulator to be any value is what's needed to get a strong enough induction hypothesis.

실제로 누적자는 항상 `0` 또는 `[]`와 같은 중립 값으로 초기화되지만, 시작 누적자를 모든 값으로 허용하는 이 더 일반적인 명제가 충분히 강한 귀납 가설을 얻기 위해 필요합니다.
Finally, using this helper theorem with the actual initial accumulator value results in the desired proof.

마지막으로 이 helper 정리를 실제 초기 누적자 값과 함께 사용하면 원하는 증명이 됩니다.
For example, in `non_tail_sum_eq_tail_sum`, the accumulator is specified to be `0`.

예를 들어, `non_tail_sum_eq_tail_sum`에서 누적자는 `0`으로 지정됩니다.
This may require rewriting the goal to make the neutral initial accumulator values occur in the right place.

이는 중립 초기 누적자 값이 올바른 위치에서 발생하도록 목표를 다시 작성해야 할 수 있습니다.

## 8.2.3. Functional Induction

The proof of `non_tail_sum_eq_helper_accum` follows the implementation of `Tail.sumHelper` closely.

`non_tail_sum_eq_helper_accum`의 증명은 `Tail.sumHelper`의 구현을 밀접하게 따릅니다.
There is not, however, a perfect match between the implementation and the structure expected by mathematical induction, which makes it necessary to manage the assumption `n` carefully.

그러나 구현과 수학적 귀납법이 기대하는 구조 사이에 완벽한 일치가 없어 가정 `n`을 신중하게 관리해야 합니다.
This is a small amount of work in the case of `non_tail_sum_eq_helper_accum`, but proofs about functions whose definitions are further from the structure expected by `induction` require more bookkeeping.

이는 `non_tail_sum_eq_helper_accum`의 경우 소량의 작업이지만, 정의가 `induction`이 기대하는 구조에서 더 멀리 있는 함수에 대한 증명은 더 많은 기록 유지가 필요합니다.

In addition to proving theorems about recursive functions by induction on one of the arguments, Lean supports proofs by induction on the recursive call structure of functions.

Lean은 인수 중 하나에 대한 귀납법으로 재귀 함수에 대한 정리를 증명하는 것 외에도 함수의 재귀 호출 구조에 대한 귀납법으로 증명을 지원합니다.
This *functional induction* results in a base case for each branch of the function's control flow that does not include a recursive call, and inductive steps for each branch that does.

이 *functional induction*은 재귀 호출을 포함하지 않는 함수의 제어 흐름의 각 분기에 대한 기저 사례와 포함하는 각 분기에 대한 귀납 단계를 초래합니다.
A proof by functional induction should demonstrate that the theorem holds for the non-recursive branches, and that if the theorem holds for the result of each recursive call, then it also holds for the result of the recursive branch.
