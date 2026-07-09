---
title: "Universes"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Universes"
---

# 5.5. Universes

In the interests of simplicity, this book has thus far papered over an important feature of Lean: *universes*.
A universe is a type that classifies other types.
Two of them are familiar: `Type` and `Prop`.
`Type` classifies ordinary types, such as `Nat`, `String`, `Int → String × Char`, and `IO Unit`.
`Prop` classifies propositions that may be true or false, such as `"nisse" = "elf"` or `3 > 2`.
The type of `Prop` is `Type`:

단순성을 위해 이 책은 지금까지 Lean의 중요한 기능인 *universes*를 간과해왔습니다.
universe는 다른 type들을 분류하는 type입니다.
이 중 두 가지는 익숙합니다: `Type`과 `Prop`입니다.
`Type`은 `Nat`, `String`, `Int → String × Char`, `IO Unit` 같은 일반 type들을 분류합니다.
`Prop`은 `"nisse" = "elf"` 또는 `3 > 2` 같은 참이거나 거짓일 수 있는 명제들을 분류합니다.
`Prop`의 type은 `Type`입니다:

`Prop : Type#check Prop`

```
Prop : Type
```

For technical reasons, more universes than these two are needed.
In particular, `Type` cannot itself be a `Type`.
This would allow a logical paradox to be constructed and undermine Lean's usefulness as a theorem prover.

기술적인 이유로, 이 두 가지 이상의 universes가 필요합니다.
특히, `Type`은 자기 자신을 `Type`으로 할 수 없습니다.
이는 논리적 역설을 구성할 수 있게 하며 theorem prover로서 Lean의 유용성을 훼손할 것입니다.

The formal argument for this is known as *Girard's Paradox*.
It is related to a better-known paradox known as *Russell's Paradox*, which was used to show that early versions of set theory were inconsistent.
In these set theories, a set can be defined by a property.
For example, one might have the set of all red things, the set of all fruit, the set of all natural numbers, or even the set of all sets.
Given a set, one can ask whether a given element is contained in it.
For instance, a bluebird is not contained in the set of all red things, but the set of all red things is contained in the set of all sets.
Indeed, the set of all sets even contains itself.

이에 대한 형식적 논증은 *Girard의 역설(Girard's Paradox)*로 알려져 있습니다.
이는 집합론의 초기 버전이 불일치함을 보이기 위해 사용된 더 유명한 *Russell의 역설(Russell's Paradox)*과 관련이 있습니다.
이러한 집합론들에서는 집합을 성질로 정의할 수 있습니다.
예를 들어, 모든 빨간 것들의 집합, 모든 과일의 집합, 모든 자연수의 집합, 또는 모든 집합의 집합을 가질 수 있습니다.
집합이 주어졌을 때, 특정 원소가 그것에 포함되는지 묻을 수 있습니다.
예를 들어, 파란새는 모든 빨간 것들의 집합에 포함되지 않지만, 모든 빨간 것들의 집합은 모든 집합의 집합에 포함됩니다.
실제로, 모든 집합의 집합은 자기 자신을 포함합니다.

What about the set of all sets that do not contain themselves?
It contains the set of all red things, as the set of all red things is not itself red.
It does not contain the set of all sets, because the set of all sets contains itself.
But does it contain itself?
If it does contain itself, then it cannot contain itself.
But if it does not, then it must.

그렇다면 자기 자신을 포함하지 않는 모든 집합들의 집합은 어떨까요?
모든 빨간 것들의 집합이 자신이 빨간 것이 아니기 때문에, 그것은 모든 빨간 것들의 집합을 포함합니다.
모든 집합의 집합이 자신을 포함하기 때문에, 그것은 모든 집합의 집합을 포함하지 않습니다.
그런데 그것이 자신을 포함하나요?
만약 자신을 포함한다면, 자신을 포함할 수 없습니다.
하지만 포함하지 않는다면, 포함해야 합니다.

This is a contradiction, which demonstrates that something was wrong with the initial assumptions.
In particular, allowing sets to be constructed by providing an arbitrary property is too powerful.
Later versions of set theory restrict the formation of sets to remove the paradox.

이것은 모순이며, 초기 가정에 뭔가 잘못되었음을 보여줍니다.
특히, 임의의 성질을 제공하여 집합을 구성하도록 허용하는 것은 너무 강력합니다.
집합론의 이후 버전들은 역설을 제거하기 위해 집합의 형성을 제한합니다.

A related paradox can be constructed in versions of dependent type theory that assign the type `Type` to `Type`.
To ensure that Lean has consistent logical foundations and can be used as a tool for mathematics, `Type` needs to have some other type.
This type is called `Type 1`:

유사한 역설은 `Type`에 type `Type`을 할당하는 dependent type theory의 버전들에서 구성될 수 있습니다.
Lean이 일관된 논리적 기초를 가지고 수학을 위한 도구로 사용될 수 있도록 보장하기 위해, `Type`은 다른 type을 가져야 합니다.
이 type을 `Type 1`이라고 부릅니다:

`Type : Type 1#check Type`

```
Type : Type 1
```

Similarly, `Type 1` is a `Type 2`,
`Type 2` is a `Type 3`,
`Type 3` is a `Type 4`, and so forth.

마찬가지로, `Type 1`은 `Type 2`이고,
`Type 2`는 `Type 3`이고,
`Type 3`은 `Type 4`이고, 이런 식으로 계속됩니다.

Function types occupy the smallest universe that can contain both the argument type and the return type.
This means that `Nat → Nat` is a `Type`, `Type → Type` is a `Type 1`, and `Type 3` is a `Type 1 → Type 2`.

Function type들은 argument type과 return type 모두를 포함할 수 있는 가장 작은 universe를 차지합니다.
즉, `Nat → Nat`이 `Type`이고, `Type → Type`이 `Type 1`이며, `Type 3`이 `Type 1 → Type 2`임입니다.

There is one exception to this rule.
If the return type of a function is a `Prop`, then the whole function type is in `Prop`, even if the argument is in a larger universe such as `Type` or even `Type 1`.
In particular, this means that predicates over values that have ordinary types are in `Prop`.
For example, the type `(n : Nat) → n = n + 0` represents a function from a `Nat` to evidence that it is equal to itself plus zero.
Even though `Nat` is in `Type`, this function type is in `Prop` due to this rule.
Similarly, even though `Type` is in `Type 1`, the function type `Type → 2 + 2 = 4` is still in `Prop`.

이 규칙에는 한 가지 예외가 있습니다.
function의 return type이 `Prop`이면, argument가 `Type` 또는 `Type 1` 같은 더 큰 universe에 있더라도 전체 function type은 `Prop`에 있습니다.
특히, 즉, ordinary type을 가지는 값들에 대한 predicate들이 `Prop`에 있음입니다.
예를 들어, type `(n : Nat) → n = n + 0`은 `Nat`에서 그것이 자신 더하기 영과 같다는 증명으로의 function을 나타냅니다.
`Nat`이 `Type`에 있음에도 불구하고, 이 function type은 이 규칙 때문에 `Prop`에 있습니다.
마찬가지로, `Type`이 `Type 1`에 있음에도 불구하고, function type `Type → 2 + 2 = 4`는 여전히 `Prop`에 있습니다.

## 5.5.1. User Defined Types

Structures and inductive datatypes can be declared to inhabit particular universes.
Lean then checks whether each datatype avoids paradoxes by being in a universe that's large enough to prevent it from containing its own type.
For instance, in the following declaration, `MyList` is declared to reside in `Type`, and so is its type argument `α`:

구조와 inductive datatype들은 특정 universe들에 속하도록 선언될 수 있습니다.
Lean은 각 datatype이 자신의 type을 포함하는 것을 방지할 수 있을 만큼 충분히 큰 universe에 있어서 역설을 회피하는지 확인합니다.
예를 들어, 다음 선언에서 `MyList`는 `Type`에 거주하도록 선언되며, 그 type argument `α`도 마찬가지입니다:

`inductive MyList (α : Type) : Type where
| nil : MyList α
| cons : α → MyList α → MyList α`

`MyList` itself is a `Type → Type`.
This means that it cannot be used to contain actual types, because then its argument would be `Type`, which is a `Type 1`:

`MyList` 자체는 `Type → Type`입니다.
즉, 그것이 실제 type들을 포함하는 데 사용될 수 없음입니다. 왜냐하면 그 argument가 `Type 1`인 `Type`이 되기 때문입니다:

`` def myListOfNat : MyList Application type mismatch: The argument
Type
has type
Type 1
of sort `Type 2` but is expected to have type
Type
of sort `Type 1` in the application
MyList TypeType :=
.cons Nat .nil ``

```
Application type mismatch: The argument
  Type
has type
  Type 1
of sort `Type 2` but is expected to have type
  Type
of sort `Type 1` in the application
  MyList Type
```

Updating `MyList` so that its argument is a `Type 1` results in a definition rejected by Lean:

`MyList`의 argument를 `Type 1`로 업데이트하면 Lean에 의해 거부되는 정의가 됩니다:

`` inductive MyList (α : Type 1) : Type where
| nil : MyList α
Invalid universe level in constructor `MyList.cons`: Parameter has type
α
at universe level
2
which is not less than or equal to the inductive type's resulting universe level
1| cons : α → MyList α → MyList α ``

```
Invalid universe level in constructor `MyList.cons`: Parameter has type
  α
at universe level
  2
which is not less than or equal to the inductive type's resulting universe level
  1
```

This error occurs because the argument to `cons` with type `α` is from a larger universe than `MyList`.
Placing `MyList` itself in `Type 1` solves this issue, but at the cost of `MyList` now being itself inconvenient to use in contexts that expect a `Type`.

이 오류는 type `α`를 가진 `cons`에 대한 argument가 `MyList`보다 더 큰 universe에서 나오기 때문에 발생합니다.
`MyList` 자체를 `Type 1`에 배치하면 이 문제가 해결되지만, `MyList`가 이제 `Type`을 기대하는 문맥에서 사용하기에 불편하다는 대가가 있습니다.

The specific rules that govern whether a datatype is allowed are somewhat complicated.
Generally speaking, it's easiest to start with the datatype in the same universe as the largest of its arguments.
Then, if Lean rejects the definition, increase its level by one, which will usually go through.

datatype이 허용되는지를 관리하는 구체적인 규칙들은 다소 복잡합니다.
일반적으로 말해서, datatype을 자신의 argument 중 가장 큰 것과 같은 universe에 시작하는 것이 가장 쉽습니다.
그러면 Lean이 정의를 거부하는 경우, 그 level을 1 증가시키면 보통 통과합니다.

## 5.5.2. Universe Polymorphism

Defining a datatype in a specific universe can lead to code duplication.
Placing `MyList` in `Type → Type` means that it can't be used for an actual list of types.
Placing it in `Type 1 → Type 1` means that it can't be used for a list of lists of types.
Rather than copy-pasting the datatype to create versions in `Type`, `Type 1`, `Type 2`, and so on, a feature called *universe polymorphism* can be used to write a single definition that can be instantiated in any of these universes.

특정 universe에서 datatype을 정의하면 코드 중복으로 이어질 수 있습니다.
`MyList`를 `Type → Type`에 배치하면 실제 type들의 list로 사용할 수 없습니다.
`Type 1 → Type 1`에 배치하면 type들의 list의 list로 사용할 수 없습니다.
`Type`, `Type 1`, `Type 2` 등의 버전을 만들기 위해 datatype을 복사-붙여넣기하는 대신, *universe polymorphism*이라는 기능을 사용하여 이러한 universe 중 어디든 인스턴스화될 수 있는 단일 정의를 작성할 수 있습니다.

Ordinary polymorphic types use variables to stand for types in a definition.
This allows Lean to fill in the variables differently, which enables these definitions to be used with a variety of types.
Similarly, universe polymorphism allows variables to stand for universes in a definition, enabling Lean to fill them in differently so that they can be used with a variety of universes.
Just as type arguments are conventionally named with Greek letters, universe arguments are conventionally named `u`, `v`, and `w`.

일반 polymorphic type들은 정의에서 type들을 나타내기 위해 변수들을 사용합니다.
이는 Lean이 변수들을 다르게 채울 수 있게 하여, 이러한 정의들이 다양한 type들과 함께 사용될 수 있게 합니다.
마찬가지로, universe polymorphism은 정의에서 universe들을 나타내기 위해 변수들을 허용하며, Lean이 그것들을 다르게 채울 수 있게 하여 다양한 universe들과 함께 사용될 수 있게 합니다.
type argument들이 관례적으로 그리스 문자로 명명되는 것처럼, universe argument들은 관례적으로 `u`, `v`, `w`로 명명됩니다.

This definition of `MyList` doesn't specify a particular universe level, but instead uses a variable `u` to stand for any level.
If the resulting datatype is used with `Type`, then `u` is `0`, and if it's used with `Type 3`, then `u` is `3`:

`MyList`의 이 정의는 특정 universe level을 지정하지 않고, 대신 변수 `u`를 사용하여 임의의 level을 나타냅니다.
결과 datatype이 `Type`과 함께 사용되면 `u`는 `0`이고, `Type 3`과 함께 사용되면 `u`는 `3`입니다:

`inductive MyList (α : Type u) : Type u where
| nil : MyList α
| cons : α → MyList α → MyList α`

With this definition, the same definition of `MyList` can be used to contain both actual natural numbers and the natural number type itself:

이 정의를 사용하면, 동일한 `MyList` 정의를 사용하여 실제 자연수와 자연수 type 자체를 모두 포함할 수 있습니다:

`def myListOfNumbers : MyList Nat :=
.cons 0 (.cons 1 .nil)
def myListOfNat : MyList Type :=
.cons Nat .nil`

It can even contain itself:

그것은 심지어 자신을 포함할 수도 있습니다:

`def myListOfList : MyList (Type → Type) :=
.cons MyList .nil`

It would seem that this would make it possible to write a logical paradox.
After all, the whole point of the universe system is to rule out self-referential types.
Behind the scenes, however, each occurrence of `MyList` is provided with a universe level argument.
In essence, the universe-polymorphic definition of `MyList` created a *copy* of the datatype at each level, and the level argument selects which copy is to be used.
These level arguments are written with a dot and curly braces, so `MyList.{0} : Type → Type`, `MyList.{1} : Type 1 → Type 1`, and `MyList.{2} : Type 2 → Type 2`.

논리적 역설을 작성하는 것이 가능해 보입니다.
결국, universe system의 전체 목적은 self-referential type들을 배제하는 것입니다.
그러나 뒤에서는 `MyList`의 각 발생이 universe level argument와 함께 제공됩니다.
본질적으로, `MyList`의 universe-polymorphic 정의는 각 level에서 datatype의 *copy*를 만들었고, level argument는 사용할 copy를 선택합니다.
이러한 level argument들은 점과 중괄호로 작성되므로 `MyList.{0} : Type → Type`, `MyList.{1} : Type 1 → Type 1`, `MyList.{2} : Type 2 → Type 2`입니다.

Writing the levels explicitly, the prior example becomes:

level들을 명시적으로 작성하면, 이전 예제는 다음과 같이 됩니다:

`def myListOfNumbers : MyList.{0} Nat :=
.cons 0 (.cons 1 .nil)
def myListOfNat : MyList.{1} Type :=
.cons Nat .nil
def myListOfList : MyList.{1} (Type → Type) :=
.cons MyList.{0} .nil`

When a universe-polymorphic definition takes multiple types as arguments, it's a good idea to give each argument its own level variable for maximum flexibility.
For example, a version of `Sum` with a single level argument can be written as follows:

universe-polymorphic 정의가 여러 type들을 argument로 취할 때, 최대 유연성을 위해 각 argument에 자신의 level 변수를 주는 것이 좋습니다.
예를 들어, 단일 level argument를 가진 `Sum`의 버전은 다음과 같이 작성될 수 있습니다:

`inductive Sum (α : Type u) (β : Type u) : Type u where
| inl : α → Sum α β
| inr : β → Sum α β`

This definition can be used at multiple levels:

이 정의는 여러 level들에서 사용될 수 있습니다:

`def stringOrNat : Sum String Nat := .inl "hello"
def typeOrType : Sum Type Type := .inr Nat`

However, it requires that both arguments be in the same universe:

그러나, 그것은 두 argument들이 같은 universe에 있기를 요구합니다:

`` def stringOrType : Sum String Application type mismatch: The argument
Type
has type
Type 1
of sort `Type 2` but is expected to have type
Type
of sort `Type 1` in the application
Sum String TypeType := .inr Nat ``

```
Application type mismatch: The argument
  Type
has type
  Type 1
of sort `Type 2` but is expected to have type
  Type
of sort `Type 1` in the application
  Sum String Type
```

This datatype can be made more flexible by using different variables for the two type arguments' universe levels, and then declaring that the resulting datatype is in the largest of the two:

이 datatype은 두 type argument들의 universe level에 대해 서로 다른 변수들을 사용함으로써 더 유연하게 만들 수 있으며, 그러면 결과 datatype이 둘 중 가장 큰 것에 있다고 선언합니다:

`inductive Sum (α : Type u) (β : Type v) : Type (max u v) where
| inl : α → Sum α β
| inr : β → Sum α β`

This allows `Sum` to be used with arguments from different universes:

이는 `Sum`이 서로 다른 universe들의 argument들과 함께 사용되도록 허용합니다:

`def stringOrType : Sum String Type := .inr Nat`

In positions where Lean expects a universe level, any of the following are allowed:

* A concrete level, like `0` or `1`
* A variable that stands for a level, such as `u` or `v`
* The maximum of two levels, written as `max` applied to the levels
* A level increase, written with `+ 1`

Lean이 universe level을 기대하는 위치에서, 다음 중 어느 것이든 허용됩니다:

* `0` 또는 `1` 같은 구체적인 level
* `u` 또는 `v` 같은 level을 나타내는 변수
* level들에 `max`를 적용하여 작성된 두 level의 최대값
* `+ 1`로 작성된 level 증가

### 5.5.2.1. Writing Universe-Polymorphic Definitions

Until now, every datatype defined in this book has been in `Type`, the smallest universe of data.
When presenting polymorphic datatypes from the Lean standard library, such as `List` and `Sum`, this book created non-universe-polymorphic versions of them.
The real versions use universe polymorphism to enable code re-use between type-level and non-type-level programs.

There are a few general guidelines to follow when writing universe-polymorphic types.
First off, independent type arguments should have different universe variables, which enables the polymorphic definition to be used with a wider variety of arguments, increasing the potential for code reuse.
Secondly, the whole type is itself typically either in the maximum of all the universe variables, or one greater than this maximum.
Try the smaller of the two first.
Finally, it's a good idea to put the new type in as small of a universe as possible, which allows it to be used more flexibly in other contexts.
Non-polymorphic types, such as `Nat` and `String`, can be placed directly in `Type 0`.

지금까지 이 책에서 정의된 모든 datatype은 `Type`(데이터의 가장 작은 universe)에 있었습니다.
Lean 표준 라이브러리의 `List`와 `Sum` 같은 polymorphic datatype들을 제시할 때, 이 책은 그들의 비-universe-polymorphic 버전들을 만들었습니다.
실제 버전들은 type-level과 비-type-level 프로그램 간의 코드 재사용을 가능하게 하기 위해 universe polymorphism을 사용합니다.

universe-polymorphic type들을 작성할 때 따를 몇 가지 일반적인 지침이 있습니다.
먼저, 독립적인 type argument들은 서로 다른 universe 변수들을 가져야 하며, 이는 polymorphic 정의가 더 다양한 argument들과 함께 사용될 수 있게 하여 코드 재사용의 가능성을 증가시킵니다.
둘째, 전체 type 자체는 일반적으로 모든 universe 변수들의 최대값이거나 이 최대값보다 하나 더 큰 값입니다.
먼저 더 작은 것을 시도해보세요.
마지막으로, 새로운 type을 가능한 한 작은 universe에 배치하는 것이 좋습니다. 이는 다른 문맥에서 더 유연하게 사용될 수 있게 합니다.
`Nat`과 `String` 같은 비-polymorphic type들은 `Type 0`에 직접 배치될 수 있습니다.

### 5.5.2.2. `Prop` and Polymorphism

Just as `Type`, `Type 1`, and so on describe types that classify programs and data, `Prop` classifies logical propositions.
A type in `Prop` describes what counts as convincing evidence for the truth of a statement.
Propositions are like ordinary types in many ways: they can be declared inductively, they can have constructors, and functions can take propositions as arguments.
However, unlike datatypes, it typically doesn't matter *which* evidence is provided for the truth of a statement, only *that* evidence is provided.
On the other hand, it is very important that a program not only return a `Nat`, but that it's the *correct* `Nat`.

`Type`, `Type 1` 등이 프로그램과 데이터를 분류하는 type들을 설명하는 것처럼, `Prop`은 논리적 명제들을 분류합니다.
`Prop`의 type은 명제의 참에 대한 설득력 있는 증명이 무엇인지를 설명합니다.
명제들은 많은 측면에서 일반 type들과 유사합니다: 귀납적으로 선언될 수 있으며, constructor들을 가질 수 있으며, function들이 명제들을 argument로 취할 수 있습니다.
그러나 datatype들과 달리, 일반적으로 명제의 참에 대해 *어떤* 증명이 제공되는지는 중요하지 않으며, *증명이* 제공되는지만 중요합니다.
반면에, 프로그램이 `Nat`을 반환할 뿐만 아니라 *올바른* `Nat`을 반환하는 것이 매우 중요합니다.

`Prop` is at the bottom of the universe hierarchy, and the type of `Prop` is `Type`.
This means that `Prop` is a suitable argument to provide to `List`, for the same reason that `Nat` is.
Lists of propositions have type `List Prop`:

`Prop`은 universe 계층의 맨 아래에 있으며, `Prop`의 type은 `Type`입니다.
즉, `Prop`이 `Nat`과 같은 이유로 `List`에 제공할 적절한 argument라는 것입니다.
명제들의 list는 type `List Prop`을 가집니다:

`def someTruePropositions : List Prop := [
1 + 1 = 2,
"Hello, " ++ "world!" = "Hello, world!"
]`

Filling out the universe argument explicitly demonstrates that `Prop` is a `Type`:

universe argument를 명시적으로 채우면 `Prop`이 `Type`임을 보여줍니다:

`def someTruePropositions : List.{0} Prop := [
1 + 1 = 2,
"Hello, " ++ "world!" = "Hello, world!"
]`

Behind the scenes, `Prop` and `Type` are united into a single hierarchy called `Sort`.
`Prop` is the same as `Sort 0`, `Type 0` is `Sort 1`, `Type 1` is `Sort 2`, and so forth.
In fact, `Type u` is the same as `Sort (u+1)`.
When writing programs with Lean, this is typically not relevant, but it may occur in error messages from time to time, and it explains the name of the `CoeSort` class.
Additionally, having `Prop` as `Sort 0` allows one more universe operator to become useful.
The universe level `imax u v` is `0` when `v` is `0`, or the larger of `u` or `v` otherwise.
Together with `Sort`, this allows the special rule for functions that return `Prop`s to be used when writing code that should be as portable as possible between `Prop` and `Type` universes.

뒤에서, `Prop`과 `Type`은 `Sort`라고 불리는 단일 계층으로 통합됩니다.
`Prop`은 `Sort 0`과 같고, `Type 0`은 `Sort 1`이고, `Type 1`은 `Sort 2`이고, 이런 식으로 계속됩니다.
실제로, `Type u`는 `Sort (u+1)`과 같습니다.
Lean으로 프로그램을 작성할 때, 이것은 일반적으로 관련이 없지만, 때때로 오류 메시지에서 나타날 수 있으며, `CoeSort` class의 이름을 설명합니다.
추가로, `Prop`을 `Sort 0`으로 가지면 하나 이상의 universe operator가 유용하게 될 수 있습니다.
universe level `imax u v`는 `v`가 `0`일 때 `0`이거나, 그렇지 않으면 `u` 또는 `v` 중 더 큰 값입니다.
`Sort`와 함께, 이는 `Prop`과 `Type` universe들 간에 가능한 한 이식 가능하기를 원하는 코드를 작성할 때 `Prop`을 반환하는 function들을 위한 특수 규칙이 사용될 수 있게 합니다.

## 5.5.3. Polymorphism in Practice

In the remainder of the book, definitions of polymorphic datatypes, structures, and classes will use universe polymorphism in order to be consistent with the Lean standard library.
This will enable the complete presentation of the `Functor`, `Applicative`, and `Monad` classes to be completely consistent with their actual definitions.

이 책의 나머지 부분에서, polymorphic datatype들, 구조들, 그리고 class들의 정의는 Lean 표준 라이브러리와 일관성을 유지하기 위해 universe polymorphism을 사용할 것입니다.
이는 `Functor`, `Applicative`, 그리고 `Monad` class들의 완전한 제시가 그들의 실제 정의와 완전히 일관되도록 할 것입니다.
