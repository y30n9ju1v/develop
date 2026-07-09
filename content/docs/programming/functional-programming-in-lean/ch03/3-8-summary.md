---
title: "Summary"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Summary"
---

# 3.8. Summary

## 3.8.1. Type Classes and Overloading

Type classes are Lean's mechanism for overloading functions and operators.
A polymorphic function can be used with multiple types, but it behaves in the same manner no matter which type it is used with.
For example, a polymorphic function that appends two lists can be used no matter the type of the entries in the list, but it is unable to have different behavior depending on which particular type is found.
An operation that is overloaded with type classes, on the other hand, can also be used with multiple types.
However, each type requires its own implementation of the overloaded operation.
This means that the behavior can vary based on which type is provided.

Type class는 함수와 연산자를 오버로딩하기 위한 Lean의 메커니즘입니다. 다형(polymorphic) 함수는 여러 타입에 사용될 수 있지만, 어떤 타입을 사용하든 같은 방식으로 동작합니다. 예를 들어, 두 리스트를 연결하는 다형 함수는 리스트의 원소 타입이 무엇이든 사용할 수 있지만, 특정 타입에 따라 다른 동작을 할 수 없습니다. 반면 type class로 오버로딩된 연산은 여러 타입에 사용될 수 있으면서도, 각 타입마다 고유한 구현을 가집니다. 즉, 제공된 타입에 따라 동작이 달라질 수 있다는 것입니다.

A *type class* has a name, parameters, and a body that consists of a number of names with types.
The name is a way to refer to the overloaded operations, the parameters determine which aspects of the definitions can be overloaded, and the body provides the names and type signatures of the overloadable operations.
Each overloadable operation is called a *method* of the type class.
Type classes may provide default implementations of some methods in terms of the others, freeing implementors from defining each overload by hand when it is not needed.

Type class는 이름, 파라미터, 그리고 여러 이름과 타입으로 구성된 본문을 가집니다. 이름은 오버로딩된 연산을 참조하는 방법이고, 파라미터는 정의의 어떤 측면을 오버로딩할 수 있는지를 결정하며, 본문은 오버로드 가능한 연산의 이름과 타입 시그니처를 제공합니다. 오버로드 가능한 각 연산을 type class의 *method*라고 합니다. Type class는 어떤 메서드의 기본 구현을 다른 메서드의 관점에서 제공할 수 있으므로, 필요하지 않을 때 구현자가 각 오버로드를 직접 정의할 필요가 없습니다.

An *instance* of a type class provides implementations of the methods for given parameters.
Instances may be polymorphic, in which case they can work for a variety of parameters, and they may optionally provide more specific implementations of default methods in cases where a more efficient version exists for some particular type.

Type class의 *instance*는 주어진 파라미터에 대해 메서드들의 구현을 제공합니다. Instance는 다형일 수 있으며, 이 경우 다양한 파라미터에 대해 작동할 수 있고, 특정 타입에 대해 더 효율적인 버전이 있는 경우 기본 메서드의 더 구체적인 구현을 선택적으로 제공할 수 있습니다.

Type class parameters are either *input parameters* (the default), or *output parameters* (indicated by an `outParam` modifier).
Lean will not begin searching for an instance until all input parameters are no longer metavariables, while output parameters may be solved while searching for instances.
Parameters to a type class need not be types—they may also be ordinary values.
The `OfNat` type class, used to overload natural number literals, takes the overloaded `Nat` itself as a parameter, which allows instances to restrict the allowed numbers.

Type class의 파라미터는 *input parameters*(기본값) 또는 *output parameters*(`outParam` modifier로 표시)입니다. Lean은 모든 input parameter가 더 이상 metavariable이 아닐 때까지 instance 검색을 시작하지 않지만, output parameter는 instance를 검색하는 동안 해결될 수 있습니다. Type class의 파라미터는 타입일 필요가 없으며, 일반적인 값일 수도 있습니다. 자연수 리터럴을 오버로딩하기 위해 사용되는 `OfNat` type class는 오버로드된 `Nat` 자체를 파라미터로 가지며, 이는 instance가 허용된 수를 제한할 수 있게 합니다.

Instances may be marked with a `@[default_instance]` attribute.
When an instance is a default instance, then it will be chosen as a fallback when Lean would otherwise fail to find an instance due to the presence of metavariables in the type.

Instance는 `@[default_instance]` attribute로 표시될 수 있습니다. Instance가 기본 instance일 때, 타입에 metavariable이 있어서 Lean이 instance를 찾지 못하는 경우 대체 방안으로 선택됩니다.

## 3.8.2. Type Classes for Common Syntax

Most infix operators in Lean are overridden with a type class.
For instance, the addition operator corresponds to a type class called `Add`.
Most of these operators have a corresponding heterogeneous version, in which the two arguments need not have the same type.
These heterogeneous operators are overloaded using a version of the class whose name starts with `H`, such as `HAdd`.

Lean의 대부분의 infix 연산자는 type class로 오버라이드됩니다. 예를 들어, 덧셈 연산자는 `Add`라는 type class에 대응됩니다. 이러한 연산자들의 대부분은 대응하는 heterogeneous 버전을 가지고 있으며, 이 경우 두 인수가 같은 타입을 가질 필요가 없습니다. 이러한 heterogeneous 연산자는 `HAdd`와 같이 이름이 `H`로 시작하는 클래스의 버전을 사용하여 오버로딩됩니다.

Indexing syntax is overloaded using a type class called `GetElem`, which involves proofs.
`GetElem` has two output parameters, which are the type of elements to be extracted from the collection and a function that can be used to determine what counts as evidence that the index value is in bounds for the collection.
This evidence is described by a proposition, and Lean attempts to prove this proposition when array indexing is used.
When Lean is unable to check that list or array access operations are in bounds at compile time, the check can be deferred to run time by appending a `?` to the indexing syntax.

인덱싱 문법은 proof를 포함하는 `GetElem`이라는 type class로 오버로딩됩니다. `GetElem`은 두 개의 output parameter를 가지는데, 이는 컬렉션에서 추출할 원소의 타입과 인덱스 값이 컬렉션의 범위 내에 있다는 증거가 무엇인지를 결정하는 데 사용할 수 있는 함수입니다. 이 증거는 명제(proposition)로 기술되며, 배열 인덱싱이 사용될 때 Lean은 이 명제를 증명하려고 시도합니다. Lean이 컴파일 시간에 리스트나 배열 접근 연산이 범위 내에 있는지 확인할 수 없을 때, 인덱싱 문법에 `?`를 덧붙여서 검사를 런타임으로 연기할 수 있습니다.

## 3.8.3. Functors

A functor is a polymorphic type that supports a mapping operation.
This mapping operation transforms all elements “in place”, changing no other structure.
For instance, lists are functors and the mapping operation may neither drop, duplicate, nor mix up entries in the list.

Functor는 mapping 연산을 지원하는 다형 타입입니다. 이 mapping 연산은 모든 원소를 “제자리에서” 변환하며, 다른 구조는 변경하지 않습니다. 예를 들어, 리스트는 functor이며, mapping 연산은 리스트의 항목을 제거하거나, 복제하거나, 섞을 수 없습니다.

While functors are defined by having `map`, the `Functor` type class in Lean contains an additional default method that is responsible for mapping the constant function over a value, replacing all values whose type are given by polymorphic type variable with the same new value.
For some functors, this can be done more efficiently than traversing the entire structure.

Functor는 `map`을 가지는 것으로 정의되지만, Lean의 `Functor` type class는 추가적인 기본 메서드를 포함하는데, 이는 상수 함수를 값에 mapping하고, 다형 타입 변수로 주어진 타입의 모든 값을 같은 새로운 값으로 치환하는 역할을 합니다. 일부 functor의 경우, 이를 전체 구조를 순회하는 것보다 더 효율적으로 수행할 수 있습니다.

## 3.8.4. Deriving Instances

Many type classes have very standard implementations.
For instance, the Boolean equality class `BEq` is usually implemented by first checking whether both arguments are built with the same constructor, and then checking whether all their arguments are equal.
Instances for these classes can be created *automatically*.

많은 type class들은 매우 표준적인 구현을 가집니다. 예를 들어, 부울 동치성 클래스 `BEq`는 보통 먼저 두 인수가 같은 생성자로 만들어졌는지 확인하고, 그 다음 모든 인수가 같은지 확인하는 방식으로 구현됩니다. 이러한 클래스들의 instance는 *자동으로* 생성될 수 있습니다.

When defining an inductive type or a structure, a `deriving` clause at the end of the declaration will cause instances to be created automatically.
Additionally, the `deriving instance`﻿`...` ﻿`for`﻿`...` command can be used outside of the definition of a datatype to cause an instance to be generated.
Because each class for which instances can be derived requires special handling, not all classes are derivable.

Inductive type 또는 structure를 정의할 때, 선언의 끝에 `deriving` 절을 추가하면 instance가 자동으로 생성됩니다. 추가적으로, `deriving instance`﻿`...` ﻿`for`﻿`...` 명령을 데이터타입 정의 외부에서 사용하여 instance를 생성할 수 있습니다. Instance를 도출할 수 있는 각 클래스는 특별한 처리가 필요하므로, 모든 클래스가 도출 가능한 것은 아닙니다.

## 3.8.5. Coercions

Coercions allow Lean to recover from what would normally be a compile-time error by inserting a call to a function that transforms data from one type to another.
For example, the coercion from any type `α` to the type `Option α` allows values to be written directly, rather than with the `some` constructor, making `Option` work more like nullable types from object-oriented languages.

Coercion은 한 타입에서 다른 타입으로 데이터를 변환하는 함수를 호출하여 원래는 컴파일 시간 오류가 되는 상황에서 Lean이 복구할 수 있게 합니다. 예를 들어, 모든 타입 `α`에서 타입 `Option α`로의 coercion은 `some` 생성자를 사용하지 않고도 값을 직접 쓸 수 있게 하여, `Option`을 객체 지향 언어의 nullable 타입처럼 더 잘 작동하게 합니다.

There are multiple kinds of coercion.
They can recover from different kinds of errors, and they are represented by their own type classes.
The `Coe` class is used to recover from type errors.
When Lean has an expression of type `α` in a context that expects something with type `β`, Lean first attempts to string together a chain of coercions that can transform `α`s into `β`s, and only displays the error when this cannot be done.
The `CoeDep` class takes the specific value being coerced as an extra parameter, allowing either further type class search to be done on the value or allowing constructors to be used in the instance to limit the scope of the conversion.
The `CoeFun` class intercepts what would otherwise be a “not a function” error when compiling a function application, and allows the value in the function position to be transformed into an actual function if possible.

Coercion에는 여러 종류가 있습니다. 이들은 다양한 종류의 오류에서 복구할 수 있으며, 각각의 type class로 표현됩니다. `Coe` class는 타입 오류에서 복구하기 위해 사용됩니다. Lean이 타입 `α`의 식을 타입 `β`를 기대하는 문맥에서 만날 때, Lean은 먼저 `α`를 `β`로 변환할 수 있는 coercion의 체인을 연결하려고 시도하고, 이것이 불가능할 때만 오류를 표시합니다. `CoeDep` class는 coerce되는 특정 값을 추가 파라미터로 가지며, 이는 값에 대해 추가적인 type class 검색을 하거나 인스턴스에서 생성자를 사용하여 변환의 범위를 제한할 수 있게 합니다. `CoeFun` class는 함수 응용을 컴파일할 때 발생하는 “함수가 아님” 오류를 가로채고, 함수 위치의 값을 가능하다면 실제 함수로 변환할 수 있게 합니다.
