---
title: "Summary"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Summary"
---

# 5.7. Summary

## 5.7.1. Type Classes and Structures

Behind the scenes, type classes are represented by structures.
Defining a class defines a structure, and additionally creates an empty table of instances.
Defining an instance creates a value that either has the structure as its type or is a function that can return the structure, and additionally adds an entry to the table.
Instance search consists of constructing an instance by consulting the instance tables.
Both structures and classes may provide default values for fields (which are default implementations of methods).

내부적으로, 타입 클래스는 구조체로 표현됩니다. 클래스를 정의하면 구조체를 정의하고, 추가적으로 빈 인스턴스 테이블을 생성합니다. 인스턴스를 정의하면 구조체를 타입으로 가지거나 구조체를 반환할 수 있는 함수의 값을 생성하고, 추가적으로 테이블에 항목을 추가합니다. 인스턴스 검색은 인스턴스 테이블을 참고하여 인스턴스를 구성하는 것으로 이루어집니다. 구조체와 클래스 모두 필드에 대한 기본값(메서드의 기본 구현)을 제공할 수 있습니다.

## 5.7.2. Structures and Inheritance

Structures may inherit from other structures.
Behind the scenes, a structure that inherits from another structure contains an instance of the original structure as a field.
In other words, inheritance is implemented with composition.
When multiple inheritance is used, only the unique fields from the additional parent structures are used to avoid a diamond problem, and the functions that would normally extract the parent value are instead organized to construct one.
Record dot notation takes structure inheritance into account.

구조체는 다른 구조체로부터 상속할 수 있습니다. 내부적으로, 다른 구조체로부터 상속하는 구조체는 원래 구조체의 인스턴스를 필드로 포함합니다. 즉, 상속은 composition으로 구현됩니다. 여러 상속을 사용할 때는, diamond 문제를 피하기 위해 추가 부모 구조체에서 고유한 필드만 사용되고, 일반적으로 부모 값을 추출하는 함수들은 대신 하나를 구성하도록 정렬됩니다. Record dot 표기법은 구조체 상속을 고려합니다.

Because type classes are just structures with some additional automation applied, all of these features are available in type classes.
Together with default methods, this can be used to create a fine-grained hierarchy of interfaces that nonetheless does not impose a large burden on clients, because the small classes that the large classes inherit from can be automatically implemented.

타입 클래스는 추가적인 자동화가 적용된 구조체일 뿐이므로, 이러한 모든 기능은 타입 클래스에서 사용 가능합니다. 기본 메서드와 함께, 이를 사용하여 클라이언트에 큰 부담을 주지 않으면서도 세밀한 인터페이스 계층을 만들 수 있습니다. 왜냐하면 큰 클래스가 상속하는 작은 클래스들이 자동으로 구현될 수 있기 때문입니다.

## 5.7.3. Applicative Functors

An applicative functor is a functor with two additional operations:

* `pure`, which is the same operator as that for `Monad`
* `seq`, which allows a function to be applied in the context of the functor.

Applicative Functor는 두 가지 추가 연산이 있는 Functor입니다:

* `pure`, `Monad`와 동일한 연산자
* `seq`, Functor의 context에서 함수를 적용할 수 있게 하는 연산

While monads can represent arbitrary programs with control flow, applicative functors can only run function arguments from left to right.
Because they are less powerful, they provide less control to programs written against the interface, while the implementor of the method has a greater degree of freedom.
Some useful types can implement `Applicative` but not `Monad`.

Monad가 제어 흐름이 있는 임의의 프로그램을 나타낼 수 있는 반면, Applicative Functor는 함수 인수를 왼쪽에서 오른쪽으로만 실행할 수 있습니다. 덜 강력하기 때문에, 인터페이스에 대해 작성된 프로그램에 덜 제어할 수 있게 하는 반면, 메서드의 구현자는 더 큰 자유도를 갖습니다. 일부 유용한 타입은 `Applicative`는 구현할 수 있지만 `Monad`는 구현할 수 없습니다.

In fact, the type classes `Functor`, `Applicative`, and `Monad` form a hierarchy of power.
Moving up the hierarchy, from `Functor` towards `Monad`, allows more powerful programs to be written, but fewer types implement the more powerful classes.
Polymorphic programs should be written to use as weak of an abstraction as possible, while datatypes should be given instances that are as powerful as possible.
This maximizes code re-use.
The more powerful type classes extend the less powerful ones, which means that an implementation of `Monad` provides implementations of `Functor` and `Applicative` for free.

실제로, `Functor`, `Applicative`, `Monad` 타입 클래스는 강력함의 계층을 형성합니다. `Functor`에서 `Monad`로 향해 계층을 올라가면 더 강력한 프로그램을 작성할 수 있지만, 더 강력한 클래스를 구현하는 타입은 더 적습니다. 다형 프로그램은 가능한 한 약한 추상화를 사용하도록 작성되어야 하는 반면, 데이터타입은 가능한 한 강력한 인스턴스를 주어야 합니다. 이는 코드 재사용을 최대화합니다. 더 강력한 타입 클래스는 덜 강력한 것들을 확장하므로, `Monad`의 구현은 `Functor`와 `Applicative`의 구현을 자유롭게 제공합니다.

Each class has a set of methods to be implemented and a corresponding contract that specifies additional rules for the methods.
Programs that are written against these interfaces expect that the additional rules are followed, and may be buggy if they are not.
The default implementations of `Functor`'s methods in terms of `Applicative`'s, and of `Applicative`'s in terms of `Monad`'s, will obey these rules.

각 클래스는 구현해야 할 메서드 집합과 메서드에 대한 추가 규칙을 지정하는 해당 계약을 가지고 있습니다. 이러한 인터페이스에 대해 작성된 프로그램은 추가 규칙을 따르도록 예상하며, 그렇지 않으면 버그가 있을 수 있습니다. `Applicative`의 관점에서 `Functor`의 메서드의 기본 구현과 `Monad`의 관점에서 `Applicative`의 구현은 이러한 규칙을 따릅니다.

## 5.7.4. Universes

To allow Lean to be used as both a programming language and a theorem prover, some restrictions on the language are necessary.
This includes restrictions on recursive functions that ensure that they all either terminate or are marked as `partial` and written to return types that are not uninhabited.
Additionally, it must be impossible to represent certain kinds of logical paradoxes as types.

Lean을 프로그래밍 언어와 정리 증명기 모두로 사용할 수 있도록 하기 위해 언어에 대한 몇 가지 제한이 필요합니다. 여기에는 모두 종료되거나 `partial`로 표시되고 무인 타입이 아닌 타입을 반환하도록 작성되는 재귀 함수에 대한 제한이 포함됩니다. 추가적으로, 특정 종류의 논리적 역설을 타입으로 표현할 수 없어야 합니다.

One of the restrictions that rules out certain paradoxes is that every type is assigned to a *universe*.
Universes are types such as `Prop`, `Type`, `Type 1`, `Type 2`, and so forth.
These types describe other types—just as `0` and `17` are described by `Nat`, `Nat` is itself described by `Type`, and `Type` is described by `Type 1`.
The type of functions that take a type as an argument must be a larger universe than the argument's universe.

특정 역설을 배제하는 제한 중 하나는 모든 타입이 *universe*에 할당된다는 것입니다. Universe는 `Prop`, `Type`, `Type 1`, `Type 2` 등의 타입입니다. 이러한 타입은 다른 타입을 설명합니다. `0`과 `17`이 `Nat`으로 설명되듯이, `Nat`은 그 자체로 `Type`으로 설명되고, `Type`은 `Type 1`로 설명됩니다. 타입을 인수로 취하는 함수의 타입은 인수의 universe보다 큰 universe여야 합니다.

Because each declared datatype has a universe, writing code that uses types like data would quickly become annoying, requiring each polymorphic type to be copy-pasted to take arguments from `Type 1`.
A feature called *universe polymorphism* allows Lean programs and datatypes to take universe levels as arguments, just as ordinary polymorphism allows programs to take types as arguments.
Generally speaking, Lean libraries should use universe polymorphism when implementing libraries of polymorphic operations.

각 선언된 데이터타입이 universe를 가지므로, 데이터처럼 타입을 사용하는 코드를 작성하면 금방 번거로워지며, 각 다형 타입이 `Type 1`에서 인수를 취하도록 복사-붙여넣기되어야 합니다. *universe polymorphism*이라는 기능을 사용하면 Lean 프로그램과 데이터타입이 universe 수준을 인수로 취할 수 있습니다. 일반적인 다형성이 프로그램이 타입을 인수로 취할 수 있게 하듯이 말입니다. 일반적으로, Lean 라이브러리는 다형 연산의 라이브러리를 구현할 때 universe polymorphism을 사용해야 합니다.
