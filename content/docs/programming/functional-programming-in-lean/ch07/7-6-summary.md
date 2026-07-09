---
title: "Summary"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Summary"
---

# 7.6. Summary

## 7.6.1. Dependent Types

Dependent types, where types contain non-type code such as function calls and ordinary data constructors, lead to a massive increase in the expressive power of a type system.
The ability to *compute* a type from the *value* of an argument means that the return type of a function can vary based on which argument is provided.
This can be used, for example, to have the result type of a database query depend on the database's schema and the specific query issued, without needing any potentially-failing cast operations on the result of the query.
When the query changes, so does the type that results from running it, enabling immediate compile-time feedback.

함수 호출과 일반 데이터 생성자 같은 비타입 코드를 포함하는 종속 타입(dependent types)은 타입 시스템의 표현력을 대폭 증가시킵니다.
인자의 *값*으로부터 타입을 *계산*할 수 있다는 것은 함수의 반환 타입이 제공되는 인자에 따라 달라질 수 있다는 의미입니다.
예를 들어, 데이터베이스 쿼리의 결과 타입이 데이터베이스 스키마와 특정 쿼리에 따라 달라지도록 할 수 있으며, 쿼리 결과에 대한 실패할 수 있는 캐스트 연산이 필요하지 않습니다.
쿼리가 변경되면 그 결과 타입도 변경되어, 즉시 컴파일 타임 피드백을 가능하게 합니다.

When a function's return type depends on a value, analyzing the value with pattern matching can result in the type being *refined*, as a variable that stands for a value is replaced by the constructors in the pattern.
The type signature of a function documents the way that the return type depends on the argument value, and pattern matching then explains how the return type can be fulfilled for each potential argument.

함수의 반환 타입이 어떤 값에 따라 달라질 때, 패턴 매칭으로 그 값을 분석하면 값을 나타내는 변수가 패턴의 생성자로 대체되면서 타입이 *세밀해집니다*(refined).
함수의 타입 서명은 반환 타입이 인자 값에 어떻게 의존하는지를 문서화하며, 패턴 매칭은 가능한 각 인자에 대해 반환 타입이 어떻게 충족될 수 있는지를 설명합니다.

Ordinary code that occurs in types is run during type checking, though `partial` functions that might loop infinitely are not called.
Mostly, this computation follows the rules of ordinary evaluation that were introduced in [the very beginning of this book](../ch01/), with expressions being progressively replaced by their values until a final value is found.
Computation during type checking has an important difference from run-time computation: some values in types may be *variables* whose values are not yet known.
In these cases, pattern-matching gets “stuck” and does not proceed until or unless a particular constructor is selected, e.g. by pattern matching.
Type-level computation can be seen as a kind of partial evaluation, where only the parts of the program that are sufficiently known need to be evaluated and other parts are left alone.

타입에 나타나는 일반 코드는 타입 검사 중에 실행되지만, 무한 루프에 빠질 수 있는 `partial` 함수는 호출되지 않습니다.
대부분 이러한 계산은 [이 책의 맨 처음](../ch01/)에서 소개된 일반 평가의 규칙을 따르며, 최종 값을 찾을 때까지 식이 점진적으로 해당 값으로 대체됩니다.
타입 검사 중의 계산은 런타임 계산과 중요한 차이가 있습니다: 타입의 일부 값은 아직 알려지지 않은 *변수*일 수 있습니다.
이러한 경우, 패턴 매칭이 “멈추게” 되며, 특정 생성자가 선택될 때까지(예: 패턴 매칭으로) 진행되지 않습니다.
타입 레벨 계산은 충분히 알려진 프로그램의 부분만 평가해야 하고 나머지는 그대로 두는 부분 평가(partial evaluation)의 한 종류로 볼 수 있습니다.

## 7.6.2. The Universe Pattern

A common pattern when working with dependent types is to section off some subset of the type system.
For example, a database query library might be able to return varying-length strings, fixed-length strings, or numbers in certain ranges, but it will never return a function, a user-defined datatype, or an `IO` action.
A domain-specific subset of the type system can be defined by first defining a datatype with constructors that match the structure of the desired types, and then defining a function that interprets values from this datatype into honest-to-goodness types.
The constructors are referred to as *codes* for the types in question, and the entire pattern is sometimes referred to as a *universe à la Tarski*, or just as a *universe* when context makes it clear that universes such as `Type 3` or `Prop` are not what's meant.

종속 타입으로 작업할 때의 일반적인 패턴은 타입 시스템의 일부 부분집합을 분리하는 것입니다.
예를 들어, 데이터베이스 쿼리 라이브러리는 가변 길이 문자열, 고정 길이 문자열, 또는 특정 범위의 숫자를 반환할 수 있지만, 함수, 사용자 정의 데이터타입, 또는 `IO` 동작을 반환하지는 않을 것입니다.
도메인 특화 타입 시스템의 부분집합은 원하는 타입의 구조와 일치하는 생성자를 가진 데이터타입을 먼저 정의한 후, 이 데이터타입의 값을 실제 타입으로 해석하는 함수를 정의함으로써 정의할 수 있습니다.
생성자들은 해당 타입에 대한 *코드*라고 불리며, 이 전체 패턴은 때때로 *Tarski 유니버스*(universe à la Tarski) 또는 `Type 3`이나 `Prop` 같은 유니버스가 의도되지 않았음이 명확할 때 단순히 *유니버스*라고 불립니다.

Custom universes are an alternative to defining a type class with instances for each type of interest.
Type classes are extensible, but extensibility is not always desired.
Defining a custom universe has a number of advantages over using the types directly:

* Generic operations that work for *any* type in the universe, such as equality testing and serialization, can be implemented by recursion on codes.
* The types accepted by external systems can be represented precisely, and the definition of the code datatype serves to document what can be expected.
* Lean's pattern matching completeness checker ensures that no codes are forgotten, while solutions based on type classes defer missing instance errors to client code.

사용자 정의 유니버스는 각 타입 관심사에 대해 인스턴스를 가진 타입 클래스를 정의하는 것의 대안입니다.
타입 클래스는 확장 가능하지만, 확장성이 항상 필요한 것은 아닙니다.
사용자 정의 유니버스를 정의하는 것은 타입을 직접 사용하는 것보다 여러 장점이 있습니다:

* 동등성 검사 및 직렬화와 같이 유니버스의 *모든* 타입에 대해 작동하는 일반 연산은 코드에 대한 재귀로 구현할 수 있습니다.
* 외부 시스템에서 수용하는 타입을 정확하게 표현할 수 있으며, 코드 데이터타입의 정의는 무엇을 기대할 수 있는지를 문서화합니다.
* Lean의 패턴 매칭 완전성 검사기는 어떤 코드도 잊혀지지 않도록 보장하며, 타입 클래스에 기반한 솔루션은 누락된 인스턴스 오류를 클라이언트 코드로 연기합니다.

## 7.6.3. Indexed Families

Datatypes can take two separate kinds of arguments: *parameters* are identical in each constructor of the datatype, while *indices* may vary between constructors.
For a given choice of index, only some constructors of the datatype are available.
As an example, `Vect.nil` is available only when the length index is `0`, and `Vect.cons` is available only when the length index is `n+1` for some `n`.
While parameters are typically written as named arguments before the colon in a datatype declaration, and indices as arguments in a function type after the colon, Lean can infer when an argument after the colon is used as a parameter.

데이터타입은 두 가지 별도의 인자 종류를 가질 수 있습니다: *매개변수*(parameters)는 데이터타입의 각 생성자에서 동일하며, *인덱스*(indices)는 생성자 사이에서 변할 수 있습니다.
주어진 인덱스 선택에 대해, 데이터타입의 일부 생성자만 사용 가능합니다.
예를 들어, `Vect.nil`은 길이 인덱스가 `0`일 때만 사용 가능하며, `Vect.cons`는 길이 인덱스가 어떤 `n`에 대해 `n+1`일 때만 사용 가능합니다.
매개변수는 일반적으로 데이터타입 선언에서 콜론 앞의 명명된 인자로 작성되고, 인덱스는 콜론 뒤의 함수 타입의 인자로 작성되지만, Lean은 콜론 뒤의 인자가 매개변수로 사용될 때를 추론할 수 있습니다.

Indexed families allow the expression of complicated relationships between data, all checked by the compiler.
The datatype's invariants can be encoded directly, and there is no way to violate them, not even temporarily.
Informing the compiler about the datatype's invariants brings a major benefit: the compiler can now inform the programmer about what must be done to satisfy them.
The strategic use of compile-time errors, especially those resulting from underscores, can make it possible to offload some of the programming thought process to Lean, freeing up the programmer's mind to worry about other things.

인덱스 패밀리는 데이터 간의 복잡한 관계를 표현하는 것을 가능하게 하며, 모두 컴파일러에 의해 검사됩니다.
데이터타입의 불변식을 직접 인코딩할 수 있으며, 임시적으로도 이를 위반할 방법이 없습니다.
컴파일러에 데이터타입의 불변식을 알리는 것은 주요 이점을 가져옵니다: 컴파일러는 이제 이를 만족시키기 위해 무엇을 해야 하는지를 프로그래머에게 알릴 수 있습니다.
특히 언더스코어로부터 나오는 것들을 포함하여 컴파일 타임 오류를 전략적으로 사용하면, 프로그래밍 사고 과정의 일부를 Lean으로 이관하고 프로그래머의 마음을 다른 것들에 대해 걱정할 수 있도록 자유롭게 할 수 있습니다.

Encoding invariants using indexed families can lead to difficulties.
First off, each invariant requires its own datatype, which then requires its own support libraries.
`List.zip` and `Vect.zip` are not interchangeable, after all.
This can lead to code duplication.
Secondly, convenient use of indexed families requires that the recursive structure of functions used in types match the recursive structure of the programs being type checked.
Programming with indexed families is the art of arranging for the right coincidences to occur.
While it's possible to work around missing coincidences with appeals to equality proofs, it is difficult, and it leads to programs littered with cryptic justifications.
Thirdly, running complicated code on large values during type checking can lead to compile-time slowdowns.
Avoiding these slowdowns for complicated programs can require specialized techniques.

인덱스 패밀리를 사용하여 불변식을 인코딩하는 것은 어려움을 초래할 수 있습니다.
먼저, 각 불변식은 자신의 데이터타입을 요구하고, 이는 자신의 지원 라이브러리를 요구합니다.
결국 `List.zip`과 `Vect.zip`은 상호 교환 가능하지 않습니다.
이는 코드 중복으로 이어질 수 있습니다.
둘째, 인덱스 패밀리의 편리한 사용은 타입에서 사용되는 함수의 재귀 구조가 타입 검사되는 프로그램의 재귀 구조와 일치해야 합니다.
인덱스 패밀리를 사용한 프로그래밍은 올바른 우연이 발생하도록 배치하는 예술입니다.
누락된 우연을 동등성 증명에 호소하여 해결하는 것이 가능하지만, 어렵고, 이는 암호 같은 정당화로 가득 찬 프로그램으로 이어집니다.
셋째, 타입 검사 중에 큰 값에 대해 복잡한 코드를 실행하면 컴파일 타임 둔화로 이어질 수 있습니다.
복잡한 프로그램에 대해 이러한 둔화를 피하는 것은 전문화된 기술이 필요할 수 있습니다.

## 7.6.4. Definitional and Propositional Equality

Lean's type checker must, from time to time, check whether two types should be considered interchangeable.
Because types can contain arbitrary programs, it must therefore be able to check arbitrary programs for equality.
However, there is no efficient algorithm to check arbitrary programs for fully-general mathematical equality.
To work around this, Lean contains two notions of equality:

* *Definitional equality* is an underapproximation of equality that essentially checks for equality of syntactic representation modulo computation and renaming of bound variables. Lean automatically checks for definitional equality in situations where it is required.
* *Propositional equality* must be explicitly proved and explicitly invoked by the programmer. In return, Lean automatically checks that the proofs are valid and that the invocations accomplish the right goal.

Lean의 타입 검사기는 때때로 두 타입이 상호 교환 가능한 것으로 간주되어야 하는지를 확인해야 합니다.
타입은 임의의 프로그램을 포함할 수 있기 때문에, 임의의 프로그램의 동등성을 확인할 수 있어야 합니다.
그러나 완전히 일반적인 수학적 동등성에 대해 임의의 프로그램을 확인할 수 있는 효율적인 알고리즘이 없습니다.
이를 해결하기 위해 Lean은 두 가지 동등성 개념을 포함합니다:

* *정의적 동등성*(definitional equality)은 본질적으로 계산과 바인딩된 변수의 이름 바꾸기를 고려한 구문 표현의 동등성을 확인하는 동등성의 하위 근사입니다. Lean은 필요한 상황에서 정의적 동등성을 자동으로 확인합니다.
* *명제적 동등성*(propositional equality)은 명시적으로 증명되고 프로그래머에 의해 명시적으로 호출되어야 합니다. 대신 Lean은 증명이 유효하고 호출이 올바른 목표를 달성하는 것을 자동으로 확인합니다.

The two notions of equality represent a division of labor between programmers and Lean itself.
Definitional equality is simple, but automatic, while propositional equality is manual, but expressive.
Propositional equality can be used to unstick otherwise-stuck programs in types.

두 가지 동등성 개념은 프로그래머와 Lean 자체 사이의 역할 분담을 나타냅니다.
정의적 동등성은 단순하지만 자동이며, 명제적 동등성은 수동이지만 표현력이 풍부합니다.
명제적 동등성은 타입에서 다른 방법으로는 고착된 프로그램을 풀기 위해 사용될 수 있습니다.

However, the frequent use of propositional equality to unstick type-level computation is typically a code smell.
It typically means that coincidences were not well-engineered, and it's usually a better idea to either redesign the types and indices or to use a different technique to enforce the needed invariants.
When propositional equality is instead used to prove that a program meets a specification, or as part of a subtype, there is less reason to be suspicious.

그러나 타입 레벨 계산을 풀기 위해 명제적 동등성을 자주 사용하는 것은 일반적으로 코드 냄새입니다.
이는 일반적으로 우연이 잘 설계되지 않았음을 의미하며, 일반적으로 타입과 인덱스를 다시 설계하거나 필요한 불변식을 강제하는 다른 기술을 사용하는 것이 더 나은 아이디어입니다.
명제적 동등성이 대신 프로그램이 사양을 만족하는지 증명하거나 부분 타입의 일부로 사용될 때, 의심할 이유가 덜합니다.
