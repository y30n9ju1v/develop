---
title: "Type Classes and Polymorphism"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Type Classes and Polymorphism"
---

# 3.2. Type Classes and Polymorphism

It can be useful to write functions that work for *any* overloading of a given function.
For example, `IO.println` works for any type that has an instance of `ToString`.
This is indicated using square brackets around the required instance: the type of `IO.println` is `{α : Type} → [ToString α] → α → IO Unit`.
This type says that `IO.println` accepts an argument of type `α`, which Lean should determine automatically, and that there must be a `ToString` instance available for `α`.
It returns an `IO` action.

주어진 함수의 *모든* 오버로딩에 대해 작동하는 함수를 작성하는 것이 유용할 수 있습니다.
예를 들어, `IO.println`은 `ToString`의 instance를 가진 모든 타입에 대해 작동합니다.
이는 필요한 instance를 대괄호로 표시하는 방식으로 나타내며, `IO.println`의 타입은 `{α : Type} → [ToString α] → α → IO Unit`입니다.
이 타입은 `IO.println`이 타입 `α`의 인자를 받아들이며 (Lean이 자동으로 결정해야 함) `α`에 대해 사용 가능한 `ToString` instance가 있어야 함을 나타냅니다.
이는 `IO` action을 반환합니다.

## 3.2.1. Checking Polymorphic Functions' Types

Checking the type of a function that takes implicit arguments or uses type classes requires the use of some additional syntax.
Simply writing

암묵적 인자를 받거나 type class를 사용하는 함수의 타입을 확인하려면 추가 구문이 필요합니다.
단순히 작성하면

`IO.println : ?m.1 → IO Unit#check (IO.println)`

yields a type with metavariables:

```
IO.println : ?m.1 → IO Unit
```

This is because Lean does its best to discover implicit arguments, and the presence of metavariables indicates that it did not yet discover enough type information to do so.
To understand the signature of a function, this feature can be suppressed with an at-sign (`@`) before the function's name:

이는 Lean이 암묵적 인자를 발견하려고 최선을 다하기 때문이며, metavariable의 존재는 충분한 타입 정보를 아직 발견하지 못했음을 나타냅니다.
함수의 시그니처를 이해하려면 함수 이름 앞에 at-sign (`@`)을 사용하여 이 기능을 억제할 수 있습니다:

`@IO.println : {α : Type u_1} → [ToString α] → α → IO Unit#check @IO.println`

```
@IO.println : {α : Type u_1} → [ToString α] → α → IO Unit
```

There is a `u_1` after `Type`, which uses a feature of Lean that has not yet been introduced.
For now, ignore these parameters to `Type`.

`Type` 뒤의 `u_1`은 아직 소개되지 않은 Lean의 기능을 사용합니다.
지금은 `Type`의 이러한 매개변수를 무시하세요.

## 3.2.2. Defining Polymorphic Functions with Instance Implicits

A function that sums all entries in a list needs two instances: `Add` allows the entries to be added, and an `OfNat` instance for `0` provides a sensible value to return for the empty list:

리스트의 모든 항목을 합산하는 함수는 두 개의 instance가 필요합니다: `Add`는 항목들을 더할 수 있게 하고, `0`에 대한 `OfNat` instance는 빈 리스트에 반환할 적절한 값을 제공합니다:

`def List.sumOfContents [Add α] [OfNat α 0] : List α → α
| [] => 0
| x :: xs => x + xs.sumOfContents`

This function can be also defined with a `Zero α` requirement instead of `OfNat α 0`.
Both are equivalent, but `Zero α` can be easier to read:

이 함수는 `OfNat α 0` 대신 `Zero α` 요구사항으로도 정의될 수 있습니다.
둘 다 동등하지만, `Zero α`가 더 읽기 쉬울 수 있습니다:

`def List.sumOfContents [Add α] [Zero α] : List α → α
| [] => 0
| x :: xs => x + xs.sumOfContents`

This function can be used for a list of `Nat`s:

이 함수는 `Nat`의 리스트에 사용될 수 있습니다:

`def fourNats : List Nat := [1, 2, 3, 4]``10#eval fourNats.sumOfContents`

```
10
```

but not for a list of `Pos` numbers:

하지만 `Pos` 숫자의 리스트에는 사용할 수 없습니다:

`def fourPos : List Pos := [1, 2, 3, 4]``` #eval failed to synthesize
Zero Pos

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.fourPos.sumOfContents ``

```
failed to synthesize
  Zero Pos

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

The Lean standard library includes this function, where it is called `List.sum`.

Lean 표준 라이브러리는 `List.sum`이라고 불리는 이 함수를 포함합니다.

Specifications of required instances in square brackets are called *instance implicits*.
Behind the scenes, every type class defines a structure that has a field for each overloaded operation.
Instances are values of that structure type, with each field containing an implementation.
At a call site, Lean is responsible for finding an instance value to pass for each instance implicit argument.
The most important difference between ordinary implicit arguments and instance implicits is the strategy that Lean uses to find an argument value.
In the case of ordinary implicit arguments, Lean uses a technique called *unification* to find a single unique argument value that would allow the program to pass the type checker.
This process relies only on the specific types involved in the function's definition and the call site.
For instance implicits, Lean instead consults a built-in table of instance values.

대괄호로 표시된 필요한 instance의 사양을 *instance implicit*이라고 부릅니다.
내부적으로 모든 type class는 각 오버로딩된 연산에 대한 필드가 있는 구조를 정의합니다.
Instance는 그 구조 타입의 값이며, 각 필드는 구현을 포함합니다.
호출 지점에서 Lean은 각 instance implicit 인자에 대해 전달할 instance 값을 찾을 책임이 있습니다.
일반적인 암묵적 인자와 instance implicit 사이의 가장 중요한 차이점은 Lean이 인자 값을 찾는 데 사용하는 전략입니다.
일반적인 암묵적 인자의 경우 Lean은 프로그램이 type checker를 통과할 수 있게 하는 단일 고유 인자 값을 찾기 위해 *unification*이라는 기법을 사용합니다.
이 프로세스는 함수 정의 및 호출 지점에 관련된 특정 타입에만 의존합니다.
Instance implicit의 경우 Lean은 대신 내장 instance 값 테이블을 참조합니다.

Just as the `OfNat` instance for `Pos` took a natural number `n` as an automatic implicit argument, instances may also take instance implicit arguments themselves.
The [section on polymorphism](../ch01/) presented a polymorphic point type:

`Pos`의 `OfNat` instance가 자연수 `n`을 자동 암묵적 인자로 취한 것처럼, instance도 instance implicit 인자를 가질 수 있습니다.
[polymorphism에 대한 섹션](../ch01/)은 다형적 point 타입을 제시했습니다:

`structure PPoint (α : Type) where
x : α
y : α`

Addition of points should add the underlying `x` and `y` fields.
Thus, an `Add` instance for `PPoint` requires an `Add` instance for whatever type these fields have.
In other words, the `Add` instance for `PPoint` requires a further `Add` instance for `α`:

점들의 덧셈은 기본 `x`와 `y` 필드를 더해야 합니다.
따라서 `PPoint`의 `Add` instance는 이 필드들이 가진 모든 타입에 대해 `Add` instance가 필요합니다.
다시 말해, `PPoint`의 `Add` instance는 `α`에 대한 추가 `Add` instance가 필요합니다:

`instance [Add α] : Add (PPoint α) where
add p1 p2 := { x := p1.x + p2.x, y := p1.y + p2.y }`

When Lean encounters an addition of two points, it searches for and finds this instance.
It then performs a further search for the `Add α` instance.

Lean이 두 점의 덧셈을 만날 때, 이 instance를 찾습니다.
그 후 `Add α` instance에 대한 추가 검색을 수행합니다.

The instance values that are constructed in this way are values of the type class's structure type.
A successful recursive instance search results in a structure value that has a reference to another structure value.
An instance of `Add (PPoint Nat)` contains a reference to the instance of `Add Nat` that was found.

이런 방식으로 구성된 instance 값들은 type class의 구조 타입의 값들입니다.
성공적인 재귀적 instance 검색은 다른 구조 값에 대한 참조를 가진 구조 값을 결과로 합니다.
`Add (PPoint Nat)`의 instance는 찾아진 `Add Nat`의 instance에 대한 참조를 포함합니다.

This recursive search process means that type classes offer significantly more power than plain overloaded functions.
A library of polymorphic instances is a set of code building blocks that the compiler will assemble on its own, given nothing but the desired type.
Polymorphic functions that take instance arguments are latent requests to the type class mechanism to assemble helper functions behind the scenes.
The API's clients are freed from the burden of plumbing together all of the necessary parts by hand.

이 재귀적 검색 프로세스는 type class가 단순 오버로딩된 함수보다 훨씬 더 강력함을 의미합니다.
다형적 instance의 라이브러리는 컴파일러가 원하는 타입만 주어지면 자신이 조립할 코드 구성 블록의 집합입니다.
instance 인자를 취하는 다형적 함수들은 type class 메커니즘에 대한 숨겨진 요청으로, 백그라운드에서 helper 함수들을 조립하기 위한 것입니다.
API의 클라이언트들은 필요한 모든 부분을 손으로 연결하는 부담에서 해방됩니다.

## 3.2.3. Methods and Implicit Arguments

The type of `OfNat.ofNat` may be surprising.
It is `: {α : Type} → (n : Nat) → [OfNat α n] → α`, in which the `Nat` argument `n` occurs as an explicit function parameter.
In the declaration of the method, however, `ofNat` simply has type `α`.
This seeming discrepancy is because declaring a type class really results in the following:

`OfNat.ofNat`의 타입은 놀랄 수 있습니다.
이는 `: {α : Type} → (n : Nat) → [OfNat α n] → α`이며, 여기서 `Nat` 인자 `n`은 명시적 함수 매개변수로 나타납니다.
그러나 메서드의 선언에서 `ofNat`은 단순히 타입 `α`를 가집니다.
이 명백한 불일치는 type class를 선언하는 것이 실제로 다음을 결과로 하기 때문입니다:

* A structure type to contain the implementation of each overloaded operation
* A namespace with the same name as the class
* For each method, a function in the class's namespace that retrieves its implementation from an instance

This is analogous to the way that declaring a new structure also declares accessor functions.
The primary difference is that a structure's accessors take the structure value as an explicit parameter, while the type class methods take the instance value as an instance implicit to be found automatically by Lean.

* 각 오버로딩된 연산의 구현을 포함할 구조 타입
* 클래스와 동일한 이름의 namespace
* 각 메서드에 대해, instance에서 구현을 검색하는 클래스의 namespace의 함수

이는 새로운 구조를 선언하면 accessor 함수도 선언되는 방식과 유사합니다.
주요 차이점은 구조의 accessor는 구조 값을 명시적 매개변수로 취하는 반면, type class 메서드는 instance 값을 Lean이 자동으로 찾을 instance implicit으로 취한다는 것입니다.

In order for Lean to find an instance, its parameters must be available.
This means that each parameter to the type class must be a parameter to the method that occurs before the instance.
It is most convenient when these parameters are implicit, because Lean does the work of discovering their values.
For example, `Add.add` has the type `{α : Type} → [Add α] → α → α → α`.
In this case, the type parameter `α` can be implicit because the arguments to `Add.add` provide information about which type the user intended.
This type can then be used to search for the `Add` instance.

Lean이 instance를 찾기 위해서는 그 매개변수들이 사용 가능해야 합니다.
즉, type class의 각 매개변수가 instance 이전에 나타나는 메서드의 매개변수여야 함입니다.
이 매개변수들이 암묵적일 때 가장 편리한데, Lean이 그 값들을 발견하는 작업을 수행하기 때문입니다.
예를 들어, `Add.add`는 타입 `{α : Type} → [Add α] → α → α → α`를 가집니다.
이 경우, `Add.add`의 인자들이 사용자가 의도한 타입에 대한 정보를 제공하기 때문에 타입 매개변수 `α`는 암묵적일 수 있습니다.
이 타입은 그 후 `Add` instance를 검색하는 데 사용될 수 있습니다.

In the case of `OfNat.ofNat`, however, the particular `Nat` literal to be decoded does not appear as part of any other parameter's type.
This means that Lean would have no information to use when attempting to figure out the implicit parameter `n`.
The result would be a very inconvenient API.
Thus, in these cases, Lean uses an explicit parameter for the class's method.

그러나 `OfNat.ofNat`의 경우, 디코딩할 특정 `Nat` 리터럴은 다른 매개변수의 타입의 일부로 나타나지 않습니다.
즉, 암묵적 매개변수 `n`을 파악하려고 할 때 Lean이 사용할 정보가 없다는 것입니다.
결과는 매우 불편한 API가 될 것입니다.
따라서 이러한 경우 Lean은 클래스의 메서드에 대해 명시적 매개변수를 사용합니다.

## 3.2.4. Exercises

### 3.2.4.2. Recursive Instance Search Depth

There is a limit to how many times the Lean compiler will attempt a recursive instance search.
This places a limit on the size of even number literals defined in the previous exercise.
Experimentally determine what the limit is.

Lean 컴파일러가 재귀적 instance 검색을 시도할 수 있는 횟수에는 제한이 있습니다.
이는 이전 연습에서 정의된 even number literal의 크기에 제한을 둡니다.
실험적으로 이 제한이 무엇인지 결정하세요.
