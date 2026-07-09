---
title: "Ch.3: 오버로딩과 타입 클래스"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Ch.3: 오버로딩과 타입 클래스"
---

# 3. Overloading and Type Classes

In many languages, the built-in datatypes get special treatment.
For example, in C and Java, `+` can be used to add `float`s and `int`s, but not arbitrary-precision numbers from a third-party library.
Similarly, numeric literals can be used directly for the built-in types, but not for user-defined number types.
Other languages provide an *overloading* mechanism for operators, where the same operator can be given a meaning for a new type.
In these languages, such as C++ and C#, a wide variety of built-in operators can be overloaded, and the compiler uses the type checker to select a particular implementation.

많은 언어에서 기본 데이터 타입은 특별한 대우를 받습니다.
예를 들어, C와 Java에서는 `+`를 `float`과 `int`를 더하는 데 사용할 수 있지만, 타사 라이브러리의 임의 정밀도 숫자는 더할 수 없습니다.
마찬가지로 숫자 리터럴은 기본 타입에 대해 직접 사용할 수 있지만, 사용자 정의 숫자 타입에는 사용할 수 없습니다.
다른 언어들은 operator *overloading* 메커니즘을 제공하는데, 같은 operator에 새 타입에 대한 의미를 부여할 수 있습니다.
C++과 C#과 같은 언어들에서는 다양한 기본 operator들을 overload할 수 있으며, 컴파일러는 type checker를 사용하여 특정 구현을 선택합니다.

In addition to numeric literals and operators, many languages allow overloading of functions or methods.
In C++, Java, C# and Kotlin, multiple implementations of a method are allowed, with differing numbers and types of arguments.
The compiler uses the number of arguments and their types to determine which overload was intended.

숫자 리터럴과 operator 외에도 많은 언어들은 함수 또는 메서드의 overloading을 허용합니다.
C++, Java, C#, Kotlin에서는 인자의 개수와 타입이 다른 메서드의 여러 구현이 허용됩니다.
컴파일러는 인자의 개수와 타입을 사용하여 어떤 overload가 의도되었는지 결정합니다.

Function and operator overloading has a key limitation: polymorphic functions can't restrict their type arguments to types for which a given overload exists.
For example, an overloaded method might be defined for strings, byte arrays, and file pointers, but there's no way to write a second method that works for any of these.
Instead, this second method must itself be overloaded for each type that has an overload of the original method, resulting in many boilerplate definitions instead of a single polymorphic definition.
Another consequence of this restriction is that some operators (such as equality in Java) end up being defined for *every* combination of arguments, even when it is not necessarily sensible to do so.
If programmers are not very careful, this can lead to programs that crash at runtime or silently compute an incorrect result.

함수와 operator overloading은 핵심 제한이 있습니다: polymorphic 함수는 주어진 overload가 존재하는 타입으로만 자신의 type argument를 제한할 수 없습니다.
예를 들어, overload된 메서드가 문자열, 바이트 배열, 파일 포인터에 대해 정의될 수 있지만, 이 중 어느 것이든 작동하는 두 번째 메서드를 작성할 방법이 없습니다.
대신 이 두 번째 메서드는 원본 메서드의 overload를 가진 각 타입에 대해 스스로 overload되어야 하므로, 단일 polymorphic 정의 대신 많은 boilerplate 정의가 발생합니다.
이 제한의 또 다른 결과는 일부 operator들(예: Java의 equality)이 종종 *모든* 인자 조합에 대해 정의되게 되는데, 이것이 반드시 합리적인 것은 아닙니다.
프로그래머가 매우 신중하지 않으면, 이는 런타임에 프로그램 충돌이나 자동으로 잘못된 결과를 계산하는 것으로 이어질 수 있습니다.

Lean implements overloading using a mechanism called *type classes*, pioneered in Haskell, that allows overloading of operators, functions, and literals in a manner that works well with polymorphism.
A type class describes a collection of overloadable operations.
To overload these operations for a new type, an *instance* is created that contains an implementation of each operation for the new type.
For example, a type class named `Add` describes types that allow addition, and an instance of `Add` for `Nat` provides an implementation of addition for `Nat`.

Lean은 Haskell에서 개척한 *type class*라는 메커니즘을 사용하여 overloading을 구현하며, 이는 polymorphism과 잘 작동하는 방식으로 operator, 함수, 리터럴의 overloading을 허용합니다.
type class는 overloadable한 연산들의 모음을 설명합니다.
새로운 타입에 대해 이러한 연산들을 overload하려면, 새로운 타입에 대한 각 연산의 구현을 포함하는 *instance*가 생성됩니다.
예를 들어, `Add`라는 이름의 type class는 덧셈을 허용하는 타입들을 설명하고, `Nat`에 대한 `Add`의 instance는 `Nat`에 대한 덧셈의 구현을 제공합니다.

The terms *class* and *instance* can be confusing for those who are used to object-oriented languages, because they are not closely related to classes and instances in object-oriented languages.
However, they do share common roots: in everyday language, the term “class” refers to a group that shares some common attributes.
While classes in object-oriented programming certainly describe groups of objects with common attributes, the term additionally refers to a specific mechanism in a programming language for describing such a group.
Type classes are also a means of describing types that share common attributes (namely, implementations of certain operations), but they don't really have anything else in common with classes as found in object-oriented programming.

*class*와 *instance*라는 용어는 객체 지향 언어에 익숙한 사람들에게 혼동을 줄 수 있습니다. 왜냐하면 객체 지향 언어의 class와 instance와 밀접한 관련이 없기 때문입니다.
그러나 공통의 근원을 공유합니다: 일상 언어에서 “class”라는 용어는 공통 속성을 공유하는 그룹을 의미합니다.
객체 지향 프로그래밍의 class가 확실히 공통 속성을 가진 객체 그룹을 설명하는 반면, 용어는 추가적으로 그러한 그룹을 설명하기 위한 프로그래밍 언어의 특정 메커니즘을 의미합니다.
Type class는 또한 공통 속성(즉, 특정 연산의 구현들)을 공유하는 타입들을 설명하는 수단이지만, 객체 지향 프로그래밍의 class와 정말로 공통점이 없습니다.

A Lean type class is much more analogous to a Java or C# *interface*.
Both type classes and interfaces describe a conceptually related set of operations that are implemented for a type or collection of types.
Similarly, an instance of a type class is akin to the code in a Java or C# class that is prescribed by the implemented interfaces, rather than an instance of a Java or C# class.
Unlike Java or C#'s interfaces, types can be given instances for type classes that the author of the type does not have access to.
In this way, they are very similar to Rust traits.

Lean type class는 Java 또는 C# *interface*와 훨씬 더 유사합니다.
Type class와 interface 모두 타입 또는 타입들의 모음에 대해 구현되는 개념적으로 관련된 연산들의 집합을 설명합니다.
마찬가지로, type class의 instance는 Java 또는 C# class의 instance보다는 구현된 interface에 의해 규정된 Java 또는 C# class의 코드와 유사합니다.
Java 또는 C#의 interface와 달리, 타입의 저자가 접근할 수 없는 type class에 대해 타입에 instance를 부여할 수 있습니다.
이러한 방식으로, 그들은 Rust trait와 매우 유사합니다.

1. [3.1. Positive Numbers](3-1-positive-numbers/)
2. [3.2. Type Classes and Polymorphism](3-2-type-classes-and-polymorphism/)
3. [3.3. Controlling Instance Search](3-3-controlling-instance-search/)
4. [3.4. Arrays and Indexing](3-4-arrays-and-indexing/)
5. [3.5. Standard Classes](3-5-standard-classes/)
6. [3.6. Coercions](3-6-coercions/)
7. [3.7. Additional Conveniences](3-7-additional-conveniences/)
8. [3.8. Summary](3-8-summary/)
