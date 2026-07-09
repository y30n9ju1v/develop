---
title: "Ch.7: 의존 타입으로 프로그래밍"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Ch.7: 의존 타입으로 프로그래밍"
---

# 7. Programming with Dependent Types

In most statically-typed programming languages, there is a hermetic seal between the world of types and the world of programs.
Types and programs have different grammars and they are used at different times.
Types are typically used at compile time, to check that a program obeys certain invariants.
Programs are used at run time, to actually perform computations.
When the two interact, it is usually in the form of a type-case operator like an “instance-of” check or a casting operator that provides the type checker with information that was otherwise unavailable, to be verified at run time.
In other words, the interaction consists of types being inserted into the world of programs, where they gain some limited run-time meaning.

대부분의 정적 타입 프로그래밍 언어에서는 타입의 세계와 프로그램의 세계 사이에 철저한 경계가 있습니다.
타입과 프로그램은 서로 다른 문법을 가지고 있으며 다른 시점에 사용됩니다.
타입은 일반적으로 컴파일 시점에 프로그램이 특정 불변식을 따르는지 확인하는 데 사용됩니다.
프로그램은 실행 시점에 실제 계산을 수행하는 데 사용됩니다.
둘이 상호작용할 때는 일반적으로 “instance-of” 검사 또는 캐스팅 연산자 같은 타입 케이스 연산자 형태로 진행되며, 이는 타입 검사기에 런타임에 검증될 정보를 제공합니다.
즉, 상호작용은 타입이 프로그램의 세계에 삽입되어 제한된 런타임 의미를 얻는 형태로 이루어집니다.

Lean does not impose this strict separation.
In Lean, programs may compute types and types may contain programs.
Placing programs in types allows their full computational power to be used at compile time, and the ability to return types from functions makes types into first-class participants in the programming process.

Lean은 이런 엄격한 경계를 두지 않습니다.
Lean에서는 프로그램이 타입을 계산할 수 있고 타입이 프로그램을 포함할 수 있습니다.
프로그램을 타입 안에 배치하면 이들의 전체 계산 능력을 컴파일 시점에 사용할 수 있으며, 함수에서 타입을 반환하는 능력은 타입을 프로그래밍 프로세스의 1급 객체로 만듭니다.

*Dependent types* are types that contain non-type expressions.
A common source of dependent types is a named argument to a function.
For example, the function `natOrStringThree` returns either a natural number or a string, depending on which `Bool` it is passed:

*Dependent types*는 비타입 표현식을 포함하는 타입입니다.
Dependent types의 일반적인 출처는 함수의 명명된 인자입니다.
예를 들어, `natOrStringThree` 함수는 전달받는 `Bool`에 따라 자연수 또는 문자열을 반환합니다:

`def natOrStringThree (b : Bool) : if b then Nat else String :=
match b with
| true => (3 : Nat)
| false => "three"`

Further examples of dependent types include:

Dependent types vastly increase the power of a type system.
The flexibility of return types that branch on argument values enables programs to be written that cannot easily be given types in other type systems.
At the same time, dependent types allow a type signature to restrict which values may be returned from a function, enabling strong invariants to be enforced at compile time.

Dependent types는 타입 시스템의 힘을 매우 크게 증가시킵니다.
인자 값에 따라 분기하는 반환 타입의 유연성은 다른 타입 시스템에서 쉽게 타입을 지정할 수 없는 프로그램을 작성할 수 있게 합니다.
동시에, dependent types는 타입 시그니처가 함수에서 반환될 수 있는 값을 제한하도록 허용하여 강한 불변식을 컴파일 시점에 강제할 수 있게 합니다.

However, programming with dependent types can be quite complex, and it requires a whole set of skills above and beyond functional programming.
Expressive specifications can be complicated to fulfill, and there is a real risk of tying oneself in knots and being unable to complete the program.
On the other hand, this process can lead to new understanding, which can be expressed in a refined type that can be fulfilled.
While this chapter scratches the surface of dependently typed programming, it is a deep topic that deserves an entire book of its own.

그러나 dependent types을 사용한 프로그래밍은 상당히 복잡할 수 있으며, 함수형 프로그래밍 이상의 다양한 기술이 필요합니다.
표현력 있는 명세는 구현하기 복잡할 수 있으며, 자신을 옭아매고 프로그램을 완성하지 못할 위험이 실제로 존재합니다.
반면, 이 과정은 개선된 타입으로 표현할 수 있는 새로운 이해로 이어질 수 있습니다.
이 챕터는 dependent types 프로그래밍의 표면만 긁고 있지만, 그것은 자신의 책 전체를 할애할 가치가 있는 깊이 있는 주제입니다.

1. [7.1. Indexed Families](7-1-indexed-families/)
2. [7.2. The Universe Design Pattern](7-2-the-universe-design-pattern/)
3. [7.3. Worked Example: Typed Queries](7-3-worked-example-typed-queries/)
4. [7.4. Indices, Parameters, and Universe Levels](7-4-indices-parameters-and-universe-levels/)
5. [7.5. Pitfalls of Programming with Dependent Types](7-5-pitfalls-of-programming-with-dependent-types/)
6. [Interlude: Tactics, Induction, and Proofs](interlude-tactics-induction-and-proofs/)
7. [7.6. Summary](7-6-summary/)
