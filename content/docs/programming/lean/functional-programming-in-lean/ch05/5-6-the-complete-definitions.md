---
title: "완전한 정의"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "완전한 정의"
---

# 5.6. The Complete Definitions

Now that all the relevant language features have been presented, this section describes the complete, honest definitions of `Functor`, `Applicative`, and `Monad` as they occur in the Lean standard library.
For the sake of understanding, no details are omitted.

관련된 모든 언어 기능이 제시되었으므로, 이 섹션은 Lean 표준 라이브러리에서 나타나는 `Functor`, `Applicative`, `Monad`의 완전하고 정확한 정의를 설명합니다.
이해를 위해 어떤 세부 사항도 생략되지 않습니다.

## 5.6.1. Functor

The complete definition of the `Functor` class makes use of universe polymorphism and a default method implementation:

`Functor` 클래스의 완전한 정의는 universe 다형성과 기본 메서드 구현을 사용합니다:

```lean
class Functor (f : Type u → Type v) : Type (max (u+1) v) where
  map : {α β : Type u} → (α → β) → f α → f β
  mapConst : {α β : Type u} → α → f β → f α :=
    Function.comp map (Function.const _)
```

In this definition, `Function.comp` is function composition, which is typically written with the `∘` operator.
`Function.const` is the *constant function*, which is a two-argument function that ignores its second argument.
Applying this function to only one argument produces a function that always returns the same value, which is useful when an API demands a function but a program doesn't need to compute different results for different arguments.

이 정의에서 `Function.comp`는 함수 합성(function composition)이며, 일반적으로 `∘` 연산자로 작성됩니다.
`Function.const`는 *상수 함수(constant function)*로, 두 번째 인자를 무시하는 두 인자 함수입니다.
이 함수를 하나의 인자에만 적용하면 항상 같은 값을 반환하는 함수를 생성하며, API가 함수를 요구하지만 프로그램이 다양한 인자에 대해 다른 결과를 계산할 필요가 없을 때 유용합니다.
A simple version of `Function.const` can be written as follows:

`Function.const`의 간단한 버전은 다음과 같이 작성할 수 있습니다:

```lean
def simpleConst (x : α) (_ : β) : α := x
```

Using it with one argument as the function argument to `List.map` demonstrates its utility:

하나의 인자를 가지고 `List.map`의 함수 인자로 사용하면 그 유용성을 알 수 있습니다:

```lean
#eval [1, 2, 3].map (simpleConst "same")
```

```
["same", "same", "same"]
```

The actual function has the following signature:

```
Function.const.{u, v} {α : Sort u} (β : Sort v) (a : α) : β → α
```

Here, the type argument `β` is an explicit argument, so the default definition of `mapConst` provides an `_` argument that instructs Lean to find a unique type to pass to `Function.const` that would cause the program to type check.
`Function.comp map (Function.const _)` is equivalent to `fun (x : α) (y : f β) => map (fun _ => x) y`.

여기서 타입 인자 `β`는 명시적 인자(explicit argument)이므로, `mapConst`의 기본 정의는 Lean에게 프로그램이 타입 검사를 통과하도록 `Function.const`에 전달할 유일한 타입을 찾도록 지시하는 `_` 인자를 제공합니다.
`Function.comp map (Function.const _)`는 `fun (x : α) (y : f β) => map (fun _ => x) y`와 동치입니다.

The `Functor` type class inhabits a universe that is the greater of `u+1` and `v`.
Here, `u` is the level of universes accepted as arguments to `f`, while `v` is the universe returned by `f`.
To see why the structure that implements the `Functor` type class must be in a universe that's larger than `u`, begin with a simplified definition of the class:

`Functor` type class는 `u+1`과 `v` 중 더 큰 값의 universe에 있습니다.
여기서 `u`는 `f`의 인자로 받는 universe들의 수준이고, `v`는 `f`가 반환하는 universe입니다.
`Functor` type class를 구현하는 구조가 `u`보다 큰 universe에 있어야 하는 이유를 보기 위해, 클래스의 간단한 정의로부터 시작합니다:

```lean
class Functor (f : Type u → Type v) : Type (max (u+1) v) where
  map : {α β : Type u} → (α → β) → f α → f β
```

This type class's structure type is equivalent to the following inductive type:

이 type class의 구조 타입은 다음의 귀납적 타입과 동치입니다:

```lean
inductive Functor (f : Type u → Type v) : Type (max (u+1) v) where
  | mk : ({α β : Type u} → (α → β) → f α → f β) → Functor f
```

The implementation of the `map` method that is passed as an argument to `mk` contains a function that takes two types in `Type u` as arguments.
This means that the type of the function itself is in `Type (u+1)`, so `Functor` must also be at a level that is at least `u+1`.
Similarly, other arguments to the function have a type built by applying `f`, so it must also have a level that is at least `v`.
All the type classes in this section share this property.

`mk`의 인자로 전달되는 `map` 메서드의 구현에는 `Type u`의 두 타입을 인자로 받는 함수가 포함되어 있습니다.
이는 함수 자체의 타입이 `Type (u+1)`에 있다는 의미이므로, `Functor`도 최소한 `u+1` 수준에 있어야 합니다.
유사하게, 함수의 다른 인자들은 `f`를 적용하여 생성된 타입을 가지므로, 최소한 `v` 수준에 있어야 합니다.
이 섹션의 모든 type class들은 이 속성을 공유합니다.

## 5.6.2. Applicative

The `Applicative` type class is actually built from a number of smaller classes that each contain some of the relevant methods.
The first are `Pure` and `Seq`, which contain `pure` and `seq` respectively:

`Applicative` type class는 실제로는 각각 관련 메서드의 일부를 포함하는 여러 개의 더 작은 클래스들로부터 구성됩니다.
먼저 `pure`와 `seq`를 각각 포함하는 `Pure`와 `Seq`가 있습니다:

```lean
class Pure (f : Type u → Type v) : Type (max (u+1) v) where
  pure {α : Type u} : α → f α

class Seq (f : Type u → Type v) : Type (max (u+1) v) where
  seq : {α β : Type u} → f (α → β) → (Unit → f α) → f β
```

In addition to these, `Applicative` also depends on `SeqRight` and an analogous `SeqLeft` class:

이 외에도 `Applicative`는 `SeqRight`와 유사한 `SeqLeft` 클래스에도 의존합니다:

```lean
class SeqRight (f : Type u → Type v) : Type (max (u+1) v) where
  seqRight : {α β : Type u} → f α → (Unit → f β) → f β

class SeqLeft (f : Type u → Type v) : Type (max (u+1) v) where
  seqLeft : {α β : Type u} → f α → (Unit → f β) → f α
```

The `seqRight` function, which was introduced in the [section about alternatives and validation](Functors___-Applicative-Functors___-and-Monads/Alternatives/#alternative), is easiest to understand from the perspective of effects.
`E1 *> E2`, which desugars to `SeqRight.seqRight E1 (fun () => E2)`, can be understood as first executing `E1`, and then `E2`, resulting only in `E2`'s result.
Effects from `E1` may result in `E2` not being run, or being run multiple times.
Indeed, if `f` has a `Monad` instance, then `E1 *> E2` is equivalent to `do let _ ← E1; E2`, but `seqRight` can be used with types like `Validate` that are not monads.

`seqRight` 함수는 [alternatives와 validation에 대한 섹션](Functors___-Applicative-Functors___-and-Monads/Alternatives/#alternative)에서 소개되었으며, 효과(effect)의 관점에서 가장 쉽게 이해할 수 있습니다.
`E1 *> E2`는 `SeqRight.seqRight E1 (fun () => E2)`로 desugars되며, 먼저 `E1`을 실행한 다음 `E2`를 실행하고 `E2`의 결과만 반환하는 것으로 이해할 수 있습니다.
`E1`의 효과는 `E2`가 실행되지 않거나 여러 번 실행되는 결과를 초래할 수 있습니다.
실제로 `f`가 `Monad` 인스턴스를 가지면, `E1 *> E2`는 `do let _ ← E1; E2`와 동치이지만, `seqRight`는 monad이 아닌 `Validate`와 같은 타입들과도 함께 사용될 수 있습니다.

Its cousin `seqLeft` is very similar, except the leftmost expression's value is returned.
`E1 <* E2` desugars to `SeqLeft.seqLeft E1 (fun () => E2)`.
`SeqLeft.seqLeft` has type `f α → (Unit → f β) → f α`, which is identical to that of `seqRight` except for the fact that it returns `f α`.
`E1 <* E2` can be understood as a program that first executes `E1`, and then `E2`, returning the original result for `E1`.
If `f` has a `Monad` instance, then `E1 <* E2` is equivalent to `do let x ← E1; _ ← E2; pure x`.
Generally speaking, `seqLeft` is useful for specifying extra conditions on a value in a validation or parser-like workflow without changing the value itself.

그 사촌 `seqLeft`는 매우 유사하지만, 맨 왼쪽 표현식의 값이 반환된다는 점이 다릅니다.
`E1 <* E2`는 `SeqLeft.seqLeft E1 (fun () => E2)`로 desugars됩니다.
`SeqLeft.seqLeft`는 `f α`를 반환한다는 점을 제외하고는 `seqRight`의 타입 `f α → (Unit → f β) → f α`와 동일합니다.
`E1 <* E2`는 먼저 `E1`을 실행한 다음 `E2`를 실행하고 `E1`의 원래 결과를 반환하는 프로그램으로 이해할 수 있습니다.
`f`가 `Monad` 인스턴스를 가지면, `E1 <* E2`는 `do let x ← E1; _ ← E2; pure x`와 동치입니다.
일반적으로 `seqLeft`는 값 자체를 변경하지 않으면서 validation이나 parser 같은 워크플로우에서 값에 대한 추가 조건을 지정할 때 유용합니다.

The definition of `Applicative` extends all these classes, along with `Functor`:

`Applicative`의 정의는 `Functor`와 함께 이 모든 클래스들을 확장합니다:

```lean
class Applicative (f : Type u → Type v)
    extends Functor f, Pure f, Seq f, SeqLeft f, SeqRight f where
  map := fun x y => Seq.seq (pure x) fun _ => y
  seqLeft := fun a b => Seq.seq (Functor.map (Function.const _) a) b
  seqRight := fun a b => Seq.seq (Functor.map (Function.const _ id) a) b
```

A complete definition of `Applicative` requires only definitions for `pure` and `seq`.
This is because there are default definitions for all of the methods from `Functor`, `SeqLeft`, and `SeqRight`.
The `mapConst` method of `Functor` has its own default implementation in terms of `Functor.map`.
These default implementations should only be overridden with new functions that are behaviorally equivalent, but more efficient.
The default implementations should be seen as specifications for correctness as well as automatically-created code.

`Applicative`의 완전한 정의는 `pure`와 `seq`에 대한 정의만 필요합니다.
이는 `Functor`, `SeqLeft`, `SeqRight`의 모든 메서드에 대한 기본 정의가 있기 때문입니다.
`Functor`의 `mapConst` 메서드는 `Functor.map`의 관점에서 자체 기본 구현을 가집니다.
이러한 기본 구현은 동작 면에서 동일하지만 더 효율적인 새로운 함수로만 오버라이드되어야 합니다.
기본 구현은 정확성의 명세일 뿐만 아니라 자동으로 생성된 코드로도 볼 수 있습니다.

The default implementation for `seqLeft` is very compact.
Replacing some of the names with their syntactic sugar or their definitions can provide another view on it, so:

`seqLeft`의 기본 구현은 매우 간결합니다.
일부 이름을 그들의 syntactic sugar 또는 정의로 바꾸면 다른 관점을 제공할 수 있으므로:

```lean
Seq.seq (Functor.map (Function.const _) a) b
```

becomes

```lean
fun a b => Seq.seq ((fun x _ => x) <$> a) b
```

다음이 된다.

`(fun x _ => x) <$> a`는 어떻게 이해해야 할까요?
여기서 `a`는 타입 `f α`를 가지며, `f`는 functor입니다.
`f`가 `List`라면, `(fun x _ => x) <$> [1, 2, 3]`은 `[fun _ => 1, fun _ => 2, fun _ => 3]`으로 평가됩니다.
`f`가 `Option`이라면, `(fun x _ => x) <$> some "hello"`는 `some (fun _ => "hello")`로 평가됩니다.
각 경우에서, functor의 값들은 원래 값을 반환하고 인자를 무시하는 함수로 대체됩니다.
`seq`와 결합될 때, 이 함수는 `seq`의 두 번째 인자의 값들을 버립니다.

The default implementation for `seqRight` is very similar, except `Function.const` has an additional argument `id`.
This definition can be understood similarly, by first introducing some standard syntactic sugar and then replacing some names with their definitions:

`seqRight`의 기본 구현은 매우 유사하지만, `Function.const`가 추가 인자 `id`를 가진다는 점이 다릅니다.
이 정의는 유사하게 이해할 수 있으며, 먼저 표준 syntactic sugar를 도입한 다음 일부 이름을 그들의 정의로 바꾸면 됩니다:

```lean
fun a b => Seq.seq (Functor.map (Function.const _ id) a) b
```

becomes

```lean
fun a b => Seq.seq ((fun _ => id) <$> a) b
```

becomes

```lean
fun a b => Seq.seq ((fun _ => fun x => x) <$> a) b
```

becomes

```lean
fun a b => Seq.seq ((fun _ x => x) <$> a) b
```

이는 차례로 다음과 같이, 다음과 같이, 그리고 마지막으로 다음과 같이 변합니다.

`(fun _ x => x) <$> a`는 어떻게 이해해야 할까요?
다시 한 번, 예시가 유용합니다.
`(fun _ x => x) <$> [1, 2, 3]`은 `[fun x => x, fun x => x, fun x => x]`과 동치이고, `(fun _ x => x) <$> some "hello"`는 `some (fun x => x)`과 동치입니다.
다시 말해, `(fun _ x => x) <$> a`는 `a`의 전체 모양은 보존하지만, 각 값을 항등 함수(identity function)로 대체합니다.
효과의 관점에서, `a`의 부작용(side effects)은 발생하지만, `seq`와 함께 사용될 때 값들은 버려집니다.

## 5.6.3. Monad

Just as the constituent operations of `Applicative` are split into their own type classes, `Bind` has its own class as well:

`Applicative`의 구성 연산들이 자신의 type class로 분리되는 것처럼, `Bind`도 자신의 클래스를 가집니다:

```lean
class Bind (m : Type u → Type v) where
  bind : {α β : Type u} → m α → (α → m β) → m β
```

`Monad` extends `Applicative` with `Bind`:

`Monad`는 `Bind`를 포함하여 `Applicative`를 확장합니다:

```lean
class Monad (m : Type u → Type v) : Type (max (u+1) v)
    extends Applicative m, Bind m where
  map f x := bind x (Function.comp pure f)
  seq f x := bind f fun y => Functor.map y (x ())
  seqLeft x y := bind x fun a => bind (y ()) (fun _ => pure a)
  seqRight x y := bind x fun _ => y ()
```

Tracing the collection of inherited methods and default methods from the entire hierarchy shows that a `Monad` instance requires only implementations of `bind` and `pure`.
In other words, `Monad` instances automatically yield implementations of `seq`, `seqLeft`, `seqRight`, `map`, and `mapConst`.
From the perspective of API boundaries, any type with a `Monad` instance gets instances for `Bind`, `Pure`, `Seq`, `Functor`, `SeqLeft`, and `SeqRight`.

전체 계층 구조에서 상속된 메서드와 기본 메서드의 모음을 추적하면, `Monad` 인스턴스는 `bind`와 `pure`의 구현만 필요함을 보여줍니다.
다시 말해, `Monad` 인스턴스는 자동으로 `seq`, `seqLeft`, `seqRight`, `map`, `mapConst`의 구현을 생성합니다.
API 경계의 관점에서, `Monad` 인스턴스를 가진 모든 타입은 `Bind`, `Pure`, `Seq`, `Functor`, `SeqLeft`, `SeqRight`의 인스턴스를 얻습니다.

## 5.6.4. Exercises

1. Understand the default implementations of `map`, `seq`, `seqLeft`, and `seqRight` in `Monad` by working through examples such as `Option` and `Except`. In other words, substitute their definitions for `bind` and `pure` into the default definitions, and simplify them to recover the versions `map`, `seq`, `seqLeft`, and `seqRight` that would be written by hand.
2. On paper or in a text file, prove to yourself that the default implementations of `map` and `seq` satisfy the contracts for `Functor` and `Applicative`. In this argument, you're allowed to use the rules from the `Monad` contract as well as ordinary expression evaluation.

1. `Option`과 `Except` 같은 예제를 통해 작업하면서 `Monad`의 `map`, `seq`, `seqLeft`, `seqRight`의 기본 구현을 이해합니다. 다시 말해, `bind`과 `pure`의 정의를 기본 정의에 대입한 다음 단순화하여 손으로 작성했을 `map`, `seq`, `seqLeft`, `seqRight` 버전을 회복합니다.
2. 종이나 텍스트 파일에 `map`과 `seq`의 기본 구현이 `Functor`와 `Applicative`의 계약을 만족함을 증명합니다. 이 논증에서는 `Monad` 계약의 규칙뿐만 아니라 일반적인 식 평가를 사용할 수 있습니다.
