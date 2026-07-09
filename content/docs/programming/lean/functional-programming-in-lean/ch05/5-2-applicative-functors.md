---
title: "어플리커티브 펑터"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "어플리커티브 펑터"
---

# 5.2. Applicative Functors

An *applicative functor* is a functor that has two additional operations available: `pure` and `seq`.
`pure` is the same operator used in `Monad`, because `Monad` in fact inherits from `Applicative`.
`seq` is much like `map`: it allows a function to be used in order to transform the contents of a datatype.
However, with `seq`, the function is itself contained in the datatype: `f (α → β) → (Unit → f α) → f β`.
Having the function under the type `f` allows the `Applicative` instance to control how the function is applied, while `Functor.map` unconditionally applies a function.
The second argument has a type that begins with `Unit →` to allow the definition of `seq` to short-circuit in cases where the function will never be applied.

*applicative functor*는 `pure`와 `seq`이라는 두 가지 추가 연산을 사용할 수 있는 functor입니다.
`pure`는 `Monad`에서 사용되는 동일한 연산자이며, 이는 `Monad`가 실제로 `Applicative`를 상속받기 때문입니다.
`seq`는 `map`과 매우 유사하며, 함수를 사용하여 데이터타입의 내용을 변환할 수 있게 합니다.
그러나 `seq`에서는 함수 자체가 데이터타입 내에 포함됩니다: `f (α → β) → (Unit → f α) → f β`.
함수를 타입 `f` 아래에 두면 `Applicative` 인스턴스가 함수의 적용 방식을 제어할 수 있으며, `Functor.map`은 무조건 함수를 적용합니다.
두 번째 인수가 `Unit →`로 시작하는 타입을 가지는 것은 함수가 절대 적용되지 않는 경우에 `seq`의 정의가 단락될 수 있도록 하기 위함입니다.

The value of this short-circuiting behavior can be seen in the instance of `Applicative Option`:

```lean
instance : Applicative Option where
  pure x := .some x
  seq f x :=
    match f with
    | none => none
    | some g => g <$> x ()
```

이 단락 회로 동작의 가치는 `Applicative Option`의 인스턴스에서 볼 수 있습니다.

In this case, if there is no function for `seq` to apply, then there is no need to compute its argument, so `x` is never called.
The same consideration informs the instance of `Applicative` for `Except`:

이 경우, `seq`가 적용할 함수가 없으면 인수를 계산할 필요가 없으므로 `x`는 절대 호출되지 않습니다.
동일한 고려사항이 `Except`에 대한 `Applicative` 인스턴스를 안내합니다:

```lean
instance : Applicative (Except ε) where
  pure x := .ok x
  seq f x :=
    match f with
    | .error e => .error e
    | .ok g => g <$> x ()
```

이 단락 회로 동작은 함수 자체가 아니라 함수를 *감싸는* `Option` 또는 `Except` 구조에만 의존합니다.

Monads can be seen as a way of capturing the notion of sequentially executing statements into a pure functional language.
The result of one statement can affect which further statements run.
This can be seen in the type of `bind`: `m α → (α → m β) → m β`.
The first statement's resulting value is an input into a function that computes the next statement to execute.
Successive uses of `bind` are like a sequence of statements in an imperative programming language, and `bind` is powerful enough to implement control structures like conditionals and loops.

Monad는 순차적으로 문장을 실행하는 개념을 순수 함수형 언어로 포착하는 방법으로 볼 수 있습니다.
한 문장의 결과는 다음에 실행될 문장들에 영향을 줄 수 있습니다.
이는 `bind`의 타입에서 볼 수 있습니다: `m α → (α → m β) → m β`.
첫 번째 문장의 결과 값은 다음 문장을 계산하는 함수에 대한 입력이 됩니다.
`bind`를 연속적으로 사용하는 것은 명령형 프로그래밍 언어의 문장 수열과 같으며, `bind`는 조건부와 루프 같은 제어 구조를 구현할 수 있을 정도로 강력합니다.

Following this analogy, `Applicative` captures function application in a language that has side effects.
The arguments to a function in languages like Kotlin or C# are evaluated from left to right.
Side effects performed by earlier arguments occur before those performed by later arguments.
A function is not powerful enough to implement custom short-circuiting operators that depend on the specific *value* of an argument, however.

이 비유를 따르면, `Applicative`는 부작용이 있는 언어에서 함수 적용을 포착합니다.
Kotlin이나 C#과 같은 언어에서 함수의 인수는 왼쪽에서 오른쪽으로 평가됩니다.
이전 인수에 의해 수행되는 부작용은 나중의 인수에 의해 수행되는 것보다 먼저 발생합니다.
그러나 함수는 인수의 특정 *값*에 의존하는 사용자 정의 단락 회로 연산자를 구현할 수 있을 정도로 강력하지 않습니다.

Typically, `seq` is not invoked directly.
Instead, the operator `<*>` is used.
This operator wraps its second argument in `fun () => ...`, simplifying the call site.
In other words, `E1 <*> E2` is syntactic sugar for `Seq.seq E1 (fun () => E2)`.

일반적으로 `seq`는 직접 호출되지 않습니다.
대신 연산자 `<*>`가 사용됩니다.
이 연산자는 두 번째 인수를 `fun () => ...`로 감싸서 호출 위치를 단순화합니다.
다시 말해, `E1 <*> E2`는 `Seq.seq E1 (fun () => E2)`에 대한 구문 설탕입니다.

The key feature that allows `seq` to be used with multiple arguments is that a multiple-argument Lean function is really a single-argument function that returns another function that's waiting for the rest of the arguments.
In other words, if the first argument to `seq` is awaiting multiple arguments, then the result of the `seq` will be awaiting the rest.
For example, `some Plus.plus` can have the type `Option (Nat → Nat → Nat)`.
Providing one argument, `some Plus.plus <*> some 4`, results in the type `Option (Nat → Nat)`.
This can itself be used with `seq`, so `some Plus.plus <*> some 4 <*> some 7` has the type `Option Nat`.

`seq`가 여러 인수와 함께 사용될 수 있게 하는 핵심 특성은 여러 인수를 가진 Lean 함수가 실제로는 나머지 인수를 기다리는 다른 함수를 반환하는 단일 인수 함수라는 것입니다.
다시 말해, `seq`의 첫 번째 인수가 여러 인수를 기다리고 있다면, `seq`의 결과는 나머지를 기다릴 것입니다.
예를 들어, `some Plus.plus`는 `Option (Nat → Nat → Nat)` 타입을 가질 수 있습니다.
한 개의 인수를 제공하면, `some Plus.plus <*> some 4`는 `Option (Nat → Nat)` 타입을 결과로 합니다.
이것을 `seq`와 함께 사용할 수 있으므로, `some Plus.plus <*> some 4 <*> some 7`은 `Option Nat` 타입을 가집니다.

Not every functor is applicative.
`Pair` is like the built-in product type `Prod`:

```lean
structure Pair (α β : Type) : Type where
  first : α
  second : β
```

모든 functor가 applicative는 아닙니다.
`Pair`는 내장된 곱 타입 `Prod`와 같습니다.

Like `Except`, `Pair` has type `Type → Type → Type`.
This means that `Pair α` has type `Type → Type`, and a `Functor` instance is possible:

`Except`처럼, `Pair`는 `Type → Type → Type` 타입을 가집니다.
이는 `Pair α`가 `Type → Type` 타입을 가지며, `Functor` 인스턴스가 가능하다는 의미입니다:

```lean
instance : Functor (Pair α) where
  map f x := ⟨x.first, f x.second⟩
```

이 인스턴스는 `Functor` 계약을 따릅니다.

This instance obeys the `Functor` contract.

확인할 두 가지 속성은 `id <$> Pair.mk x y` `=` `Pair.mk x y`이고 `f <$> g <$> Pair.mk x y` `=` `(f ∘ g) <$> Pair.mk x y`라는 것입니다.
첫 번째 속성은 왼쪽의 평가 과정을 단계적으로 따라가서 오른쪽으로 평가되는 것을 확인하면 됩니다.

The two properties to check are that `id <$> Pair.mk x y` `=` `Pair.mk x y` and that `f <$> g <$> Pair.mk x y` `=` `(f ∘ g) <$> Pair.mk x y`.
The first property can be checked by just stepping through the evaluation of the left side, and noticing that it evaluates to the right side:

`id <$> Pair.mk x y` → `Pair.mk x (id y)` → `Pair.mk x y`

두 번째는 양쪽을 단계적으로 따라가서 동일한 결과를 얻는지 확인합니다.

The second can be checked by stepping through both sides, and noting that they yield the same result:

`f <$> g <$> Pair.mk x y` → `f <$> Pair.mk x (g y)` → `Pair.mk x (f (g y))`

`(f ∘ g) <$> Pair.mk x y` → `Pair.mk x ((f ∘ g) y)` → `Pair.mk x (f (g y))`

그러나 `Applicative` 인스턴스를 정의하려는 시도는 그리 잘 작동하지 않습니다.
`pure`의 정의가 필요합니다.

Attempting to define an `Applicative` instance, however, does not work so well.
It will require a definition of `pure`:

```lean
def Pair.pure (x : β) : Pair α β := _
```

```
don't know how to synthesize placeholder
context:
β α : Type
x : β
⊢ Pair α β
```

There is a value with type `β` in scope (namely `x`), and the error message from the underscore suggests that the next step is to use the constructor `Pair.mk`:

```lean
def Pair.pure (x : β) : Pair α β := Pair.mk _ x
```

```
don't know how to synthesize placeholder for argument `first`
context:
β α : Type
x : β
⊢ α
```

Unfortunately, there is no `α` available.
Because `pure` would need to work for *all possible types* `α` to define an instance of `Applicative (Pair α)`, this is impossible.
After all, a caller could choose `α` to be `Empty`, which has no values at all.

불행히도 사용 가능한 `α`가 없습니다.
`Applicative (Pair α)`의 인스턴스를 정의하기 위해 `pure`가 *모든 가능한 타입* `α`에 대해 작동해야 하므로 이는 불가능합니다.
결국 호출자가 `α`를 값이 전혀 없는 `Empty`로 선택할 수 있기 때문입니다.

## 5.2.1. A Non-Monadic Applicative

When validating user input to a form, it's generally considered to be best to provide many errors at once, rather than one error at a time.
This allows the user to have an overview of what is needed to please the computer, rather than feeling badgered as they correct the errors field by field.

폼에 사용자 입력을 검증할 때, 일반적으로 한 번에 여러 오류를 제공하는 것이 한 번에 하나씩 제공하는 것보다 낫다고 간주됩니다.
이를 통해 사용자는 컴퓨터를 만족시키기 위해 필요한 것을 개괄적으로 파악할 수 있으며, 필드별로 오류를 수정할 때 계속 괴롭힘을 받는 느낌을 피할 수 있습니다.

Ideally, validating user input will be visible in the type of the function that's doing the validating.
It should return a datatype that is specific—checking that a text box contains a number should return an actual numeric type, for instance.
A validation routine could throw an exception when the input does not pass validation.
Exceptions have a major drawback, however: they terminate the program at the first error, making it impossible to accumulate a list of errors.

이상적으로 사용자 입력의 검증은 검증을 수행하는 함수의 타입에서 보일 수 있어야 합니다.
구체적인 데이터타입을 반환해야 합니다. 예를 들어, 텍스트 상자에 숫자가 포함되어 있는지 확인하면 실제 숫자 타입을 반환해야 합니다.
검증 루틴은 입력이 검증을 통과하지 못할 때 예외를 던질 수 있습니다.
그러나 예외에는 주요 단점이 있습니다: 첫 번째 오류에서 프로그램을 종료하므로 오류 목록을 누적하는 것이 불가능합니다.

On the other hand, the common design pattern of accumulating a list of errors and then failing when it is non-empty is also problematic.
A long nested sequences of `if` statements that validate each sub-section of the input data is hard to maintain, and it's easy to lose track of an error message or two.
Ideally, validation can be performed using an API that enables a new value to be returned yet automatically tracks and accumulates error messages.

반면에 오류 목록을 누적한 다음 비어있지 않을 때 실패하는 일반적인 디자인 패턴도 문제가 있습니다.
입력 데이터의 각 하위 섹션을 검증하는 길게 중첩된 `if` 문 수열은 유지하기 어렵고, 하나 또는 두 개의 오류 메시지를 놓치기 쉽습니다.
이상적으로 검증은 새 값을 반환할 수 있으면서 자동으로 오류 메시지를 추적하고 누적하는 API를 사용하여 수행할 수 있어야 합니다.

An applicative functor called `Validate` provides one way to implement this style of API.
Like the `Except` monad, `Validate` allows a new value to be constructed that characterizes the validated data accurately.
Unlike `Except`, it allows multiple errors to be accumulated, without a risk of forgetting to check whether the list is empty.

`Validate`라는 applicative functor는 이 스타일의 API를 구현하는 한 가지 방법을 제공합니다.
`Except` monad처럼, `Validate`는 검증된 데이터를 정확하게 특징짓는 새 값을 구성할 수 있게 합니다.
`Except`와 달리, 목록이 비어있는지 확인하는 것을 잊을 위험이 없으면서 여러 오류를 누적할 수 있습니다.

### 5.2.1.1. User Input

As an example of user input, take the following structure:

```lean
structure RawInput where
  name : String
  birthYear : String
```

사용자 입력의 예로, 다음 구조를 고려하세요.

The business logic to be implemented is the following:

1. The name may not be empty
2. The birth year must be numeric and non-negative
3. The birth year must be greater than 1900, and less than or equal to the year in which the form is validated

구현할 비즈니스 로직은 다음과 같습니다:

1. 이름은 비워둘 수 없습니다
2. 출생 연도는 숫자여야 하고 음수가 아니어야 합니다
3. 출생 연도는 1900보다 커야 하고, 폼이 검증되는 연도 이하여야 합니다

Representing these as a datatype will require a new feature, called *subtypes*.
With this tool in hand, a validation framework can be written that uses an applicative functor to track errors, and these rules can be implemented in the framework.

이들을 데이터타입으로 표현하려면 *subtypes*라는 새로운 기능이 필요합니다.
이 도구를 사용하면 applicative functor를 사용하여 오류를 추적하고 이러한 규칙을 프레임워크에 구현할 수 있는 검증 프레임워크를 작성할 수 있습니다.

### 5.2.1.2. Subtypes

Representing these conditions is easiest with one additional Lean type, called `Subtype`:

```lean
structure Subtype {α : Type} (p : α → Prop) where
  val : α
  property : p val
```

이 조건들을 표현하는 것은 `Subtype`이라는 하나의 추가 Lean 타입으로 가장 쉽습니다.

This structure has two type parameters: an implicit parameter that is the type of data `α`, and an explicit parameter `p` that is a predicate over `α`.
A *predicate* is a logical statement with a variable in it that can be replaced with a value to yield an actual statement, like the [parameter to `GetElem`](../ch03/) that describes what it means for an index to be in bounds for a lookup.
In the case of `Subtype`, the predicate slices out some subset of the values of `α` for which the predicate holds.
The structure's two fields are, respectively, a value from `α` and evidence that the value satisfies the predicate `p`.
Lean has special syntax for `Subtype`.
If `p` has type `α → Prop`, then the type `Subtype p` can also be written `{x : α // p x}`, or even `{x // p x}` when the type `α` can be inferred automatically.

이 구조는 두 가지 타입 매개변수를 가집니다: 데이터의 타입 `α`인 암시적 매개변수와 `α`에 대한 술어(predicate)인 명시적 매개변수 `p`.
*predicate*는 값으로 대체될 수 있는 변수가 포함된 논리 명제로, [인덱스가 조회에 대해 범위 내에 있는지를 설명하는 `GetElem` 매개변수](../ch03/)와 같습니다.
`Subtype`의 경우, 술어는 술어가 유지되는 `α` 값의 일부 부분집합을 선택합니다.
구조의 두 필드는 각각 `α`의 값과 해당 값이 술어 `p`를 만족한다는 증거입니다.
Lean은 `Subtype`을 위한 특수 구문을 가지고 있습니다.
`p`가 `α → Prop` 타입을 가진다면, `Subtype p` 타입은 `{x : α // p x}`로 쓸 수 있고, 타입 `α`를 자동으로 추론할 수 있을 때는 `{x // p x}`로도 쓸 수 있습니다.

[Representing positive numbers as inductive types](../ch03/) is clear and easy to program with.
However, it has a key disadvantage.
While `Nat` and `Int` have the structure of ordinary inductive types from the perspective of Lean programs, the compiler treats them specially and uses fast arbitrary-precision number libraries to implement them.
This is not the case for additional user-defined types.
However, a subtype of `Nat` that restricts it to non-zero numbers allows the new type to use the efficient representation while still ruling out zero at compile time:

[양수를 귀납적 타입으로 표현하는 것](../ch03/)은 명확하고 프로그래밍하기 쉽습니다.
그러나 이는 핵심적인 단점이 있습니다.
`Nat`과 `Int`는 Lean 프로그램의 관점에서 일반적인 귀납적 타입의 구조를 가지지만, 컴파일러는 이들을 특별히 취급하고 빠른 임의 정밀도 숫자 라이브러리를 사용하여 구현합니다.
추가 사용자 정의 타입의 경우는 그렇지 않습니다.
그러나 0이 아닌 숫자로 제한하는 `Nat`의 서브타입은 새로운 타입이 컴파일 시간에 0을 배제하면서도 효율적인 표현을 사용할 수 있게 합니다:

```lean
def FastPos : Type := {x : Nat // x > 0}
```

가장 작은 빠른 양수는 여전히 1입니다.
이제 귀납적 타입의 생성자가 아니라 꺾인 괄호로 구성된 구조의 인스턴스입니다.
첫 번째 인수는 기본 `Nat`이고, 두 번째 인수는 해당 `Nat`이 0보다 크다는 증거입니다:

```lean
def one : FastPos := ⟨1, by decide⟩
```

```
⊢ 1 > 0
decide
All goals completed! 🐙
```

명제 `1 > 0`는 결정 가능하므로 `decide` 타틱은 필요한 증거를 생성합니다.
`OfNat` 인스턴스는 `Pos`에 대한 것과 매우 유사하지만, `n + 1 > 0`이라는 증거를 제공하기 위해 짧은 타틱 증명을 사용합니다.

The proposition `1 > 0` is decidable, so the `decide` tactic produces the necessary evidence.
The `OfNat` instance is very much like that for `Pos`, except it uses a short tactic proof to provide evidence that `n + 1 > 0`:

```lean
instance : OfNat FastPos (n + 1) where
  ofNat := ⟨n + 1, by simp⟩
```

```
n : Nat
⊢ n + 1 > 0
simp
All goals completed! 🐙
```

여기서 `simp`는 `decide`가 구체적인 값을 필요로 하지만 문제의 명제가 `n + 1 > 0`이기 때문에 필요합니다.

Here, `simp` is needed because `decide` requires concrete values, but the proposition in question is `n + 1 > 0`.

Subtypes are a two-edged sword.
They allow efficient representation of validation rules, but they transfer the burden of maintaining these rules to the users of the library, who have to *prove* that they are not violating important invariants.
Generally, it's a good idea to use them internally to a library, providing an API to users that automatically ensures that all invariants are satisfied, with any necessary proofs being internal to the library.

Subtype은 양날의 검입니다.
검증 규칙의 효율적인 표현을 허용하지만, 이러한 규칙을 유지하는 부담을 중요한 불변량을 위반하지 않는다는 것을 *증명*해야 하는 라이브러리의 사용자에게 이전합니다.
일반적으로 라이브러리 내부에서 이들을 사용하고 사용자에게 모든 불변량이 만족되도록 자동으로 보장하는 API를 제공하고, 필요한 모든 증명이 라이브러리 내부에 있는 것이 좋습니다.

Checking whether a value of type `α` is in the subtype `{x : α // p x}` usually requires that the proposition `p x` be decidable.
The [section on equality and ordering classes](../ch03/) describes how decidable propositions can be used with `if`.
When `if` is used with a decidable proposition, a name can be provided.
In the `then` branch, the name is bound to evidence that the proposition is true, and in the `else` branch, it is bound to evidence that the proposition is false.
This comes in handy when checking whether a given `Nat` is positive:

타입 `α`의 값이 서브타입 `{x : α // p x}`에 있는지 확인하려면 일반적으로 명제 `p x`가 결정 가능해야 합니다.
[등호 및 순서 클래스에 대한 섹션](../ch03/)은 결정 가능한 명제를 `if`와 함께 사용하는 방법을 설명합니다.
`if`가 결정 가능한 명제와 함께 사용될 때, 이름을 제공할 수 있습니다.
`then` 분기에서 이름은 명제가 참이라는 증거에 바인딩되고, `else` 분기에서는 명제가 거짓이라는 증거에 바인딩됩니다.
이는 주어진 `Nat`이 양수인지 확인할 때 편리합니다:

```lean
def Nat.asFastPos? (n : Nat) : Option FastPos :=
  if h : n > 0 then
    some ⟨n, h⟩
  else none
```

`then` 분기에서 `h`는 `n > 0`이라는 증거에 바인딩되며, 이 증거는 `Subtype`의 생성자에 두 번째 인수로 사용될 수 있습니다.

In the `then` branch, `h` is bound to evidence that `n > 0`, and this evidence can be used as the second argument to `Subtype`'s constructor.

### 5.2.1.3. Validated Input

The validated user input is a structure that expresses the business logic using multiple techniques:

* The structure type itself encodes the year in which it was checked for validity, so that `CheckedInput 2019` is not the same type as `CheckedInput 2020`
* The birth year is represented as a `Nat` rather than a `String`
* Subtypes are used to constrain the allowed values in the name and birth year fields

검증된 사용자 입력은 여러 기법을 사용하여 비즈니스 로직을 표현하는 구조입니다:

* 구조 타입 자체는 검증된 연도를 인코딩하므로, `CheckedInput 2019`는 `CheckedInput 2020`과 동일한 타입이 아닙니다
* 출생 연도는 `String`이 아닌 `Nat`로 표현됩니다
* Subtype은 이름 및 출생 연도 필드에서 허용되는 값을 제한하는 데 사용됩니다

```lean
structure CheckedInput (thisYear : Nat) : Type where
  name : {n : String // n ≠ ""}
  birthYear : {y : Nat // y > 1900 ∧ y ≤ thisYear}
```

입력 검증자는 현재 연도와 `RawInput`을 인수로 취하여 검증된 입력 또는 최소 하나의 검증 실패를 반환해야 합니다.
이는 `Validate` 타입으로 표현됩니다.

An input validator should take the current year and a `RawInput` as arguments, returning either a checked input or at least one validation failure.
This is represented by the `Validate` type:

```lean
inductive Validate (ε α : Type) : Type where
  | ok : α → Validate ε α
  | errors : NonEmptyList ε → Validate ε α
```

`Except`와 매우 유사해 보입니다.
유일한 차이점은 `errors` 생성자가 하나 이상의 실패를 포함할 수 있다는 것입니다.

It looks very much like `Except`.
The only difference is that the `errors` constructor may contain more than one failure.

`Validate` is a functor.
Mapping a function over it transforms any successful value that might be present, just as in the `Functor` instance for `Except`:

```lean
instance : Functor (Validate ε) where
  map f
    | .ok x => .ok (f x)
    | .errors errs => .errors errs
```

`Validate`는 functor입니다.
함수를 매핑하면 `Except`의 `Functor` 인스턴스와 마찬가지로 있을 수 있는 모든 성공 값이 변환됩니다.

The `Applicative` instance for `Validate` has an important difference from the instance for `Except`: while the instance for `Except` terminates at the first error encountered, the instance for `Validate` is careful to accumulate all errors from *both* the function and the argument branches:

`Validate`의 `Applicative` 인스턴스는 `Except`의 인스턴스와 중요한 차이점이 있습니다: `Except`의 인스턴스는 첫 번째 오류에서 종료되지만, `Validate`의 인스턴스는 함수 및 인수 분기 *모두*에서 모든 오류를 누적하도록 주의합니다:

```lean
instance : Applicative (Validate ε) where
  pure := .ok
  seq f x :=
    match f with
    | .ok g => g <$> (x ())
    | .errors errs =>
      match x () with
      | .ok _ => .errors errs
      | .errors errs' => .errors (errs ++ errs')
```

`.errors`를 `NonEmptyList`의 생성자와 함께 사용하는 것은 약간 장황합니다.
`reportError`와 같은 도우미는 코드를 더 읽기 쉽게 만듭니다.
이 애플리케이션에서 오류 보고서는 필드 이름과 메시지의 쌍으로 구성됩니다.

Using `.errors` together with the constructor for `NonEmptyList` is a bit verbose.
Helpers like `reportError` make code more readable.
In this application, error reports will consist of field names paired with messages:

```lean
def Field := String

def reportError (f : Field) (msg : String) : Validate (Field × String) α :=
  .errors { head := (f, msg), tail := [] }
```

`Validate`의 `Applicative` 인스턴스는 각 필드의 검사 절차를 독립적으로 작성한 다음 구성할 수 있게 합니다.
이름을 확인하는 것은 문자열이 비어있지 않음을 보장한 다음 이 사실을 `Subtype` 형식의 증거로 반환하는 것으로 구성됩니다.
이는 증거 바인딩 버전의 `if`를 사용합니다.

The `Applicative` instance for `Validate` allows the checking procedures for each field to be written independently and then composed.
Checking a name consists of ensuring that a string is non-empty, then returning evidence of this fact in the form of a `Subtype`.
This uses the evidence-binding version of `if`:

```lean
def checkName (name : String) :
    Validate (Field × String) {n : String // n ≠ ""} :=
  if h : name = "" then
    reportError "name" "Required"
  else pure ⟨name, h⟩
```

`then` 분기에서 `h`는 `name = ""`이라는 증거에 바인딩되고, `else` 분기에서는 `¬name = ""`이라는 증거에 바인딩됩니다.

In the `then` branch, `h` is bound to evidence that `name = ""`, while it is bound to evidence that `¬name = ""` in the `else` branch.

It's certainly the case that some validation errors make other checks impossible.
For example, it makes no sense to check whether the birth year field is greater than 1900 if a confused user wrote the word `"syzygy"` instead of a number.
Checking the allowed range of the number is only meaningful after ensuring that the field in fact contains a number.
This can be expressed using the function `andThen`:

확실히 일부 검증 오류는 다른 검사를 불가능하게 만듭니다.
예를 들어, 혼란스러운 사용자가 숫자 대신 `"syzygy"` 단어를 쓴 경우 출생 연도 필드가 1900보다 큰지 확인하는 것은 의미가 없습니다.
숫자의 허용 범위를 확인하는 것은 필드가 실제로 숫자를 포함하는지 확인한 후에만 의미가 있습니다.
이는 `andThen` 함수를 사용하여 표현할 수 있습니다:

```lean
def Validate.andThen (val : Validate ε α)
    (next : α → Validate ε β) : Validate ε β :=
  match val with
  | .errors errs => .errors errs
  | .ok x => next x
```

이 함수의 타입 시그니처는 `Monad` 인스턴스에서 `bind`로 사용하기에 적합하지만, 그렇게 하지 않을 좋은 이유가 있습니다.
[`Applicative` 계약을 설명하는 섹션](Functors___-Applicative-Functors___-and-Monads/The-Applicative-Contract/#additional-stipulations)에서 설명합니다.

While this function's type signature makes it suitable to be used as `bind` in a `Monad` instance, there are good reasons not to do so.
They are described [in the section that describes the `Applicative` contract](Functors___-Applicative-Functors___-and-Monads/The-Applicative-Contract/#additional-stipulations).

To check that the birth year is a number, a built-in function called `String.toNat? : String → Option Nat` is useful.
It's most user-friendly to eliminate leading and trailing whitespace first using `String.trim`:

```lean
def checkYearIsNat (year : String) : Validate (Field × String) Nat :=
  match year.trim.toNat? with
  | none => reportError "birth year" "Must be digits"
  | some n => pure n
```

출생 연도가 숫자인지 확인하기 위해 `String.toNat? : String → Option Nat`이라고 불리는 내장 함수가 유용합니다.
가장 사용자 친화적인 방법은 먼저 `String.trim`을 사용하여 앞뒤의 공백을 제거하는 것입니다.

Testing `checkInput` shows that it can indeed return multiple pieces of feedback:

`checkInput`을 테스트하면 실제로 여러 피드백을 반환할 수 있음을 알 수 있습니다:

```lean
#eval checkInput 2023 {name := "David", birthYear := "1984"}
```

```
Validate.ok { name := "David", birthYear := 1984 }
```

```lean
#eval checkInput 2023 {name := "", birthYear := "2045"}
```

```
Validate.errors { head := ("name", "Required"), tail := [("birth year", "Must be no later than 2023")] }
```

```lean
#eval checkInput 2023 {name := "David", birthYear := "syzygy"}
```

```
Validate.errors { head := ("birth year", "Must be digits"), tail := [] }
```

Form validation with `checkInput` illustrates a key advantage of `Applicative` over `Monad`.
Because `>>=` provides enough power to modify the rest of the program's execution based on the value from the first step, it *must* receive a value from the first step to pass on.
If no value is received (e.g. because an error has occurred), then `>>=` cannot execute the rest of the program.
`Validate` demonstrates why it can be useful to run the rest of the program anyway: in cases where the earlier data isn't needed, running the rest of the program can yield useful information (in this case, more validation errors).
`Applicative`'s `<*>` may run both of its arguments before recombining the results.
Similarly, `>>=` forces sequential execution.
Each step must complete before the next may run.
This is generally useful, but it makes it impossible to have parallel execution of different threads that naturally emerges from the program's actual data dependencies.
A more powerful abstraction like `Monad` increases the flexibility that's available to the API consumer, but it decreases the flexibility that is available to the API implementor.

`checkInput`을 사용한 폼 검증은 `Applicative`가 `Monad`보다 가지는 핵심 이점을 보여줍니다.
`>>=`는 첫 번째 단계의 값을 기반으로 프로그램의 나머지 실행을 수정할 수 있는 충분한 성능을 제공하므로, 전달할 첫 번째 단계의 값을 *반드시* 수신해야 합니다.
값을 받지 못하면 (예: 오류가 발생했으므로) `>>=`는 프로그램의 나머지를 실행할 수 없습니다.
`Validate`는 어쨌든 프로그램의 나머지를 실행하는 것이 왜 유용할 수 있는지를 보여줍니다: 이전 데이터가 필요하지 않은 경우, 프로그램의 나머지를 실행하면 유용한 정보 (이 경우 더 많은 검증 오류)를 얻을 수 있습니다.
`Applicative`의 `<*>`는 결과를 다시 결합하기 전에 두 인수를 모두 실행할 수 있습니다.
마찬가지로 `>>=`는 순차 실행을 강제합니다.
각 단계는 다음 단계가 실행되기 전에 완료되어야 합니다.
이는 일반적으로 유용하지만, 프로그램의 실제 데이터 종속성에서 자연스럽게 나타나는 다양한 스레드의 병렬 실행을 불가능하게 만듭니다.
`Monad`와 같은 더 강력한 추상화는 API 소비자에게 제공되는 유연성을 증가시키지만, API 구현자에게 제공되는 유연성은 감소시킵니다.
