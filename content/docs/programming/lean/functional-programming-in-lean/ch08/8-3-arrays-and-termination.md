---
title: "Arrays and Termination"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Arrays and Termination"
---

# Arrays and Termination

Because different types have different notions of ordering, inequality is governed by two type classes, called `LE` and `LT`.

서로 다른 타입이 서로 다른 순서 개념을 가지고 있으므로, 부등식은 `LE`와 `LT`라는 두 개의 타입 클래스로 규제됩니다.
The table in the section on [standard type classes](../ch03/) describes how these classes relate to the syntax:

[표준 타입 클래스](../ch03/)에 관한 섹션의 표는 이러한 클래스가 구문과 어떻게 관련되는지 설명합니다.

### 8.3.1.1. Inductively-Defined Propositions, Predicates, and Relations

`Nat.le` is an *inductively-defined relation*.

`Nat.le`은 *귀납적으로 정의된 관계(inductively-defined relation)*입니다.
Just as `inductive` can be used to create new datatypes, it can be used to create new propositions.

`inductive`를 새로운 데이터타입을 만드는 데 사용할 수 있듯이, 새로운 명제를 만드는 데도 사용할 수 있습니다.
When a proposition takes an argument, it is referred to as a *predicate* that may be true for some, but not all, potential arguments.

명제가 인수를 받을 때, 이를 일부 잠재적 인수에 대해 참일 수 있지만 모든 인수에 대해 참일 수는 없는 *술어(predicate)*라고 합니다.
Propositions that take multiple arguments are called *relations*.

여러 인수를 받는 명제를 *관계(relations)*라고 합니다.

Each constructor of an inductively defined proposition is a way to prove it.

귀납적으로 정의된 명제의 각 생성자는 이를 증명하는 방법입니다.
In other words, the declaration of the proposition describes the different forms of evidence that it is true.

다시 말해, 명제의 선언은 이것이 참임을 보여주는 다양한 형태의 증거를 설명합니다.
A proposition with no arguments that has a single constructor can be quite easy to prove:

인수가 없고 단일 생성자를 가진 명제는 증명하기 상당히 쉬울 수 있습니다:

`inductive EasyToProve : Prop where
| heresTheProof : EasyToProve`

The proof consists of using its constructor:

증명은 그 생성자를 사용하여 이루어집니다:

`theorem fairlyEasy : EasyToProve := by⊢ EasyToProve
constructorAll goals completed! 🐙`

In fact, the proposition `True`, which should always be easy to prove, is defined just like `EasyToProve`:

사실, 항상 증명하기 쉬워야 하는 명제 `True`는 `EasyToProve`처럼 정의됩니다:

`inductive True : Prop where
| intro : True`

Inductively-defined propositions that don't take arguments are not nearly as interesting as inductively-defined datatypes.

인수를 받지 않는 귀납적으로 정의된 명제는 귀납적으로 정의된 데이터타입만큼 흥미롭지 않습니다.
This is because data is interesting in its own right—the natural number `3` is different from the number `35`, and someone who has ordered 3 pizzas will be upset if 35 arrive at their door 30 minutes later.

이는 데이터가 그 자체로 흥미롭기 때문입니다. 자연수 `3`은 숫자 `35`와 다르며, 피자 3개를 주문한 사람은 30분 후에 35개가 도착하면 화가 날 것입니다.
The constructors of a proposition describe ways in which the proposition can be true, but once a proposition has been proved, there is no need to know *which* underlying constructors were used.

명제의 생성자는 명제가 참일 수 있는 방법을 설명하지만, 명제가 증명되면 *어떤* 기저 생성자가 사용되었는지 알 필요가 없습니다.
This is why most interesting inductively-defined types in the `Prop` universe take arguments.

이것이 `Prop` universe의 대부분의 흥미로운 귀납적으로 정의된 타입이 인수를 받는 이유입니다.

The inductively-defined predicate `IsThree` states that its argument is three:

귀납적으로 정의된 술어 `IsThree`는 그 인수가 3이라고 나타냅니다:

`inductive IsThree : Nat → Prop where
| isThree : IsThree 3`

The mechanism used here is just like [indexed families such as `HasCol`](Programming-with-Dependent-Types/Worked-Example___-Typed-Queries/#column-pointers), except the resulting type is a proposition that can be proved rather than data that can be used.

여기서 사용되는 메커니즘은 [indexed families such as `HasCol`](Programming-with-Dependent-Types/Worked-Example___-Typed-Queries/#column-pointers)과 같으나, 결과 타입은 사용할 수 있는 데이터가 아니라 증명될 수 있는 명제입니다.

Using this predicate, it is possible to prove that three is indeed three:

이 술어를 사용하면, 3이 실제로 3임을 증명할 수 있습니다:

`theorem three_is_three : IsThree 3 := by⊢ IsThree 3
constructorAll goals completed! 🐙`

Similarly, `IsFive` is a predicate that states that its argument is `5`:

마찬가지로, `IsFive`는 그 인수가 `5`라고 나타내는 술어입니다:

`inductive IsFive : Nat → Prop where
| isFive : IsFive 5`

If a number is three, then the result of adding two to it should be five.

숫자가 3이면, 여기에 2를 더한 결과는 5여야 합니다.
This can be expressed as a theorem statement:

이를 정리 명제로 표현할 수 있습니다:

`theorem three_plus_two_five : IsThree n → IsFive (n + 2) := unsolved goals
n:Nat⊢ IsThree n → IsFive (n + 2)byn:Nat⊢ IsThree n → IsFive (n + 2)
skipn:Nat⊢ IsThree n → IsFive (n + 2)`

The resulting goal has a function type:

결과 목표는 함수 타입을 가집니다:

```
unsolved goals
n:Nat⊢ IsThree n → IsFive (n + 2)
```

Thus, the `intro` tactic can be used to convert the argument into an assumption:

따라서 `intro` tactic을 사용하여 인수를 가정으로 변환할 수 있습니다:

`theorem three_plus_two_five : IsThree n → IsFive (n + 2) := unsolved goals
n:Natthree:IsThree n⊢ IsFive (n + 2)byn:Nat⊢ IsThree n → IsFive (n + 2)
intro threen:Natthree:IsThree n⊢ IsFive (n + 2)`

```
unsolved goals
n:Natthree:IsThree n⊢ IsFive (n + 2)
```

Given the assumption that `n` is three, it should be possible to use the constructor of `IsFive` to complete the proof:

`n`이 3이라는 가정이 주어졌을 때, `IsFive`의 생성자를 사용하여 증명을 완료할 수 있어야 합니다:

`` theorem three_plus_two_five : IsThree n → IsFive (n + 2) := byn:Nat⊢ IsThree n → IsFive (n + 2)
intro threen:Natthree:IsThree n⊢ IsFive (n + 2)
Tactic `constructor` failed: no applicable constructor found

n:Natthree:IsThree n⊢ IsFive (n + 2)constructorn:Natthree:IsThree n⊢ IsFive (n + 2) ``

However, this results in an error:

그러나 이는 오류를 초래합니다:

```
Tactic `constructor` failed: no applicable constructor found

n:Natthree:IsThree n⊢ IsFive (n + 2)
```

This error occurs because `n + 2` is not definitionally equal to `5`.

이 오류는 `n + 2`가 정의상 `5`와 같지 않기 때문에 발생합니다.
In an ordinary function definition, dependent pattern matching on the assumption `three` could be used to refine `n` to `3`.

일반적인 함수 정의에서는 가정 `three`에 대한 dependent pattern matching을 사용하여 `n`을 `3`으로 정제할 수 있습니다.
The tactic equivalent of dependent pattern matching is `cases`, which has a syntax similar to that of `induction`:

dependent pattern matching의 tactic 등가물은 `cases`이며, `induction`과 유사한 구문을 가집니다:

`theorem three_plus_two_five : IsThree n → IsFive (n + 2) := byn:Nat⊢ IsThree n → IsFive (n + 2)
intro threen:Natthree:IsThree n⊢ IsFive (n + 2)
cases three with
| isThree unsolved goals
isThree⊢ IsFive (3 + 2)=> skipisThree⊢ IsFive (3 + 2)`

In the remaining case, `n` has been refined to `3`:

```
unsolved goals
isThree⊢ IsFive (3 + 2)
```

Because `3 + 2` is definitionally equal to `5`, the constructor is now applicable:

`theorem three_plus_two_five : IsThree n → IsFive (n + 2) := byn:Nat⊢ IsThree n → IsFive (n + 2)
intro threen:Natthree:IsThree n⊢ IsFive (n + 2)
cases three with
| isThree =>isThree⊢ IsFive (3 + 2) constructorAll goals completed! 🐙`

The standard false proposition `False` has no constructors, making it impossible to provide direct evidence for.
The only way to provide evidence for `False` is if an assumption is itself impossible, similarly to how `nomatch` can be used to mark code that the type system can see is unreachable.
As described in [the initial Interlude on proofs](Interlude___-Propositions___-Proofs___-and-Indexing/#connectives), the negation `Not A` is short for `A → False`.
`Not A` can also be written `¬A`.

It is not the case that four is three:

`theorem four_is_not_three : ¬ IsThree 4 := unsolved goals
⊢ ¬IsThree 4by⊢ ¬IsThree 4
skip⊢ ¬IsThree 4`

The initial proof goal contains `Not`:

```
unsolved goals
⊢ ¬IsThree 4
```

The fact that it's actually a function type can be exposed using `unfold`:

`theorem four_is_not_three : ¬ IsThree 4 := unsolved goals
⊢ IsThree 4 → Falseby⊢ ¬IsThree 4
unfold Not⊢ IsThree 4 → False`

```
unsolved goals
⊢ IsThree 4 → False
```

Because the goal is a function type, `intro` can be used to convert the argument into an assumption.
There is no need to keep `unfold`, as `intro` can unfold the definition of `Not` itself:

`theorem four_is_not_three : ¬ IsThree 4 := unsolved goals
h:IsThree 4⊢ Falseby⊢ ¬IsThree 4
intro hh:IsThree 4⊢ False`

```
unsolved goals
h:IsThree 4⊢ False
```

In this proof, the `cases` tactic solves the goal immediately:

`theorem four_is_not_three : ¬ IsThree 4 := by⊢ ¬IsThree 4
intro hh:IsThree 4⊢ False
cases hAll goals completed! 🐙`

Just as a pattern match on a `Vect String 2` doesn't need to include a case for `Vect.nil`, a proof by cases over `IsThree 4` doesn't need to include a case for `isThree`.

### 8.3.1.2. Inequality of Natural Numbers

The definition of `Nat.le` has a parameter and an index:

`inductive Nat.le (n : Nat) : Nat → Prop
| refl : Nat.le n n
| step : Nat.le n m → Nat.le n (m + 1)`

The parameter `n` is the number that should be smaller, while the index is the number that should be greater than or equal to `n`.
The `refl` constructor is used when both numbers are equal, while the `step` constructor is used when the index is greater than `n`.

From the perspective of evidence, a proof that `n \leq k` consists of finding some number `d` such that `n + d = m`.
In Lean, the proof then consists of a `Nat.le.refl` constructor wrapped by `d` instances of `Nat.le.step`.
Each `step` constructor adds one to its index argument, so `d` `step` constructors adds `d` to the larger number.
For example, evidence that four is less than or equal to seven consists of three `step`s around a `refl`:

`theorem four_le_seven : 4 ≤ 7 :=
open Nat.le in
step (step (step refl))`

The strict less-than relation is defined by adding one to the number on the left:

`def Nat.lt (n m : Nat) : Prop :=
Nat.le (n + 1) m
instance : LT Nat where
lt := Nat.lt`

Evidence that four is strictly less than seven consists of two `step`'s around a `refl`:

`theorem four_lt_seven : 4 < 7 :=
open Nat.le in
step (step refl)`

This is because `4 < 7` is equivalent to `5 ≤ 7`.
