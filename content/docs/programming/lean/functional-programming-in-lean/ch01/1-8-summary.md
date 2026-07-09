---
title: "1.8. 요약"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "1장에서 다룬 표현식 평가, 함수, 타입, 데이터타입, 재귀 개념 요약"
---

# 1.8. Summary

## 1.8.1. Evaluating Expressions

In Lean, computation occurs when expressions are evaluated.
This follows the usual rules of mathematical expressions: sub-expressions are replaced by their values following the usual order of operations, until the entire expression has become a value.
When evaluating an `if` or a `match`, the expressions in the branches are not evaluated until the value of the condition or the match subject has been found.

Lean에서는 expression이 평가될 때 계산이 발생합니다.
이는 수학 식의 일반적인 규칙을 따릅니다: 부분 식(sub-expression)이 연산 순서에 따라 그들의 값으로 치환되며, 전체 식이 하나의 값이 될 때까지 이 과정이 반복됩니다.
`if` 또는 `match`를 평가할 때, 분기의 expression들은 조건 또는 match 대상의 값이 결정될 때까지 평가되지 않습니다.

Once they have been given a value, variables never change.
Similarly to mathematics but unlike most programming languages, Lean variables are simply placeholders for values, rather than addresses to which new values can be written.
Variables' values may come from global definitions with `def`, local definitions with `let`, as named arguments to functions, or from pattern matching.

변수에 값이 주어지면 절대 변하지 않습니다.
수학과 마찬가지로, 대부분의 프로그래밍 언어와는 달리 Lean의 변수는 새로운 값을 쓸 수 있는 주소가 아니라, 단순히 값의 자리 표시자(placeholder)입니다.
변수의 값은 `def`로 정의된 전역 정의, `let`으로 정의된 지역 정의, 함수의 이름이 지정된 인자, 또는 pattern matching에서 올 수 있습니다.

## 1.8.2. Functions

Functions in Lean are first-class values, meaning that they can be passed as arguments to other functions, saved in variables, and used like any other value.
Every Lean function takes exactly one argument.
To encode a function that takes more than one argument, Lean uses a technique called currying, where providing the first argument returns a function that expects the remaining arguments.
To encode a function that takes no arguments, Lean uses the `Unit` type, which is the least informative possible argument.

Lean의 function은 first-class value입니다. 즉, 다른 function의 인자로 전달되고, 변수에 저장되고, 다른 값처럼 사용될 수 있습니다.
모든 Lean function은 정확히 하나의 인자를 받습니다.
하나 이상의 인자를 받는 function을 표현하기 위해, Lean은 currying이라는 기법을 사용합니다. 첫 번째 인자를 제공하면 나머지 인자를 기대하는 function을 반환합니다.
인자를 받지 않는 function을 표현하기 위해, Lean은 `Unit` type을 사용합니다. 이는 가장 정보가 적은 인자입니다.

There are three primary ways of creating functions:

1. Anonymous functions are written using `fun`.
   For instance, a function that swaps the fields of a `Point` can be written `fun (point : Point) => { x := point.y, y := point.x : Point }`
2. Very simple anonymous functions are written by placing one or more centered dots `·` inside of parentheses.
   Each centered dot becomes an argument to the function, and the parentheses delimit its body.
   For instance, a function that subtracts one from its argument can be written as `(· - 1)` instead of as `fun x => x - 1`.
3. Functions can be defined using `def` or `let` by adding an argument list or by using pattern-matching notation.

Function을 만드는 세 가지 주요 방법이 있습니다:

1. Anonymous function은 `fun`을 사용하여 작성됩니다.
   예를 들어, `Point`의 필드를 교환하는 function은 `fun (point : Point) => { x := point.y, y := point.x : Point }`로 작성할 수 있습니다.
2. 매우 단순한 anonymous function은 괄호 안에 하나 이상의 centered dot `·`를 배치하여 작성됩니다.
   각 centered dot은 function의 인자가 되고, 괄호는 본문을 구분합니다.
   예를 들어, 인자에서 1을 빼는 function은 `fun x => x - 1` 대신 `(· - 1)`로 작성할 수 있습니다.
3. Function은 `def` 또는 `let`을 사용하여 인자 목록을 추가하거나 pattern-matching 표기법을 사용하여 정의할 수 있습니다.

## 1.8.3. Types

Lean checks that every expression has a type.
Types, such as `Int`, `Point`, `{α : Type} → Nat → α → List α`, and `Option (String ⊕ (Nat × String))`, describe the values that may eventually be found for an expression.
Like other languages, types in Lean can express lightweight specifications for programs that are checked by the Lean compiler, obviating the need for certain classes of unit test.
Unlike most languages, Lean's types can also express arbitrary mathematics, unifying the worlds of programming and theorem proving.
While using Lean for proving theorems is mostly out of scope for this book, *[Theorem Proving in Lean 4](https://leanprover.github.io/theorem_proving_in_lean4/)* contains more information on this topic.

Lean은 모든 expression이 type을 가지는지 확인합니다.
`Int`, `Point`, `{α : Type} → Nat → α → List α`, 그리고 `Option (String ⊕ (Nat × String))`와 같은 type들은 expression에 대해 최종적으로 발견될 수 있는 값들을 설명합니다.
다른 언어들처럼, Lean의 type은 Lean 컴파일러에 의해 확인되는 가벼운 프로그램 명세를 표현할 수 있으며, 특정 종류의 단위 테스트가 필요하지 않게 합니다.
대부분의 언어와 달리, Lean의 type은 임의의 수학을 표현할 수 있으며, 프로그래밍과 theorem proving의 세계를 통일합니다.
이 책에서는 theorem 증명에 Lean을 사용하는 것이 대부분 범위를 벗어나지만, *[Theorem Proving in Lean 4](https://leanprover.github.io/theorem_proving_in_lean4/)*에는 이 주제에 대한 더 많은 정보가 있습니다.

Some expressions can be given multiple types.
For instance, `3` can be an `Int` or a `Nat`.
In Lean, this should be understood as two separate expressions, one with type `Nat` and one with type `Int`, that happen to be written in the same way, rather than as two different types for the same thing.

일부 expression은 여러 type을 가질 수 있습니다.
예를 들어, `3`은 `Int` 또는 `Nat`일 수 있습니다.
Lean에서 이는 같은 것에 대한 두 가지 서로 다른 type으로 이해되기보다는, type `Nat`을 가진 하나와 type `Int`를 가진 하나라는 두 개의 별개 expression으로 이해되어야 하며, 단지 같은 방식으로 작성되어 있을 뿐입니다.

Lean is sometimes able to determine types automatically, but types must often be provided by the user.
This is because Lean's type system is so expressive.
Even when Lean can find a type, it may not find the desired type—`3` could be intended to be used as an `Int`, but Lean will give it the type `Nat` if there are no further constraints.
In general, it is a good idea to write most types explicitly, only letting Lean fill out the very obvious types.
This improves Lean's error messages and helps make programmer intent more clear.

Lean은 때때로 type을 자동으로 결정할 수 있지만, 종종 사용자가 type을 제공해야 합니다.
이는 Lean의 type system이 매우 표현력이 풍부하기 때문입니다.
Lean이 type을 찾을 수 있는 경우에도, 원하는 type을 찾지 못할 수 있습니다. 예를 들어, `3`은 `Int`로 사용되도록 의도되었을 수 있지만, 추가 제약이 없으면 Lean은 `Nat` type을 부여합니다.
일반적으로 대부분의 type을 명시적으로 작성하고 매우 명백한 type만 Lean이 채우도록 하는 것이 좋습니다.
이는 Lean의 오류 메시지를 개선하고 프로그래머의 의도를 더 명확하게 합니다.

Some functions or datatypes take types as arguments.
They are called *polymorphic*.
Polymorphism allows programs such as one that calculates the length of a list without caring what type the entries in the list have.
Because types are first class in Lean, polymorphism does not require any special syntax, so types are passed just like other arguments.
Naming an argument in a function type allows later types to mention that name, and when the function is applied to an argument, the type of the resulting term is found by replacing the argument's name with the actual value it was applied to.

일부 function이나 datatype은 type을 인자로 받습니다.
이들을 *polymorphic*이라고 부릅니다.
Polymorphism은 목록의 항목이 어떤 type을 가지는지 신경 쓰지 않고 목록의 길이를 계산하는 것과 같은 프로그램을 가능하게 합니다.
Lean에서 type이 first class이기 때문에, polymorphism은 특별한 문법이 필요하지 않으며, type은 다른 인자들처럼 전달됩니다.
function type에서 인자의 이름을 지정하면 나중의 type이 그 이름을 참조할 수 있고, function이 인자에 적용될 때, 결과 항의 type은 인자의 이름을 실제로 적용된 값으로 치환하여 찾습니다.

## 1.8.4. Structures and Inductive Types

Brand new datatypes can be introduced to Lean using the `structure` or `inductive` features.
These new types are not considered to be equivalent to any other type, even if their definitions are otherwise identical.
Datatypes have *constructors* that explain the ways in which their values can be constructed, and each constructor takes some number of arguments.
Constructors in Lean are not the same as constructors in object-oriented languages: Lean's constructors are inert holders of data, rather than active code that initializes an allocated object.

`structure` 또는 `inductive` 기능을 사용하여 Lean에 완전히 새로운 datatype을 도입할 수 있습니다.
이러한 새로운 type들은 정의가 그 외의 것에서 동일하더라도 다른 어떤 type과도 동등한 것으로 간주되지 않습니다.
Datatype은 그 값을 구성할 수 있는 방식들을 설명하는 *constructor*를 가지며, 각 constructor는 어떤 수의 인자를 받습니다.
Lean의 constructor는 객체지향 언어의 constructor와 같지 않습니다: Lean의 constructor는 할당된 객체를 초기화하는 활성 코드가 아니라, 데이터의 불활성 보유자입니다.

Typically, `structure` is used to introduce a product type (that is, a type with just one constructor that takes any number of arguments), while `inductive` is used to introduce a sum type (that is, a type with many distinct constructors).
Datatypes defined with `structure` are provided with one accessor function for each field.
Both structures and inductive datatypes may be consumed with pattern matching, which exposes the values stored inside of constructors using a subset of the syntax used to call said constructors.
Pattern matching means that knowing how to create a value implies knowing how to consume it.

일반적으로, `structure`는 product type(즉, 정확히 하나의 constructor를 가지며 어떤 수의 인자를 받는 type)을 도입하는 데 사용되고, `inductive`는 sum type(즉, 많은 서로 다른 constructor를 가진 type)을 도입하는 데 사용됩니다.
`structure`로 정의된 datatype에는 각 필드마다 하나의 accessor function이 제공됩니다.
structure와 inductive datatype 모두 pattern matching으로 사용될 수 있으며, 이는 그 constructor들을 호출하는 데 사용되는 문법의 일부를 사용하여 constructor 내부에 저장된 값을 노출합니다.
Pattern matching은 값을 만드는 방법을 알면 그것을 사용하는 방법도 안다는 의미입니다.

## 1.8.5. Recursion

A definition is recursive when the name being defined is used in the definition itself.
Because Lean is an interactive theorem prover in addition to being a programming language, there are certain restrictions placed on recursive definitions.
In Lean's logical side, circular definitions could lead to logical inconsistency.

재귀 정의는 정의되는 이름이 정의 자체에서 사용될 때입니다.
Lean은 프로그래밍 언어일 뿐만 아니라 대화형 theorem prover이기 때문에, 재귀 정의에 대한 특정 제약이 있습니다.
Lean의 논리적 측면에서, 순환 정의는 논리적 모순으로 이어질 수 있습니다.

재귀 정의가 Lean의 논리적 측면을 훼손하지 않도록 보장하기 위해, Lean은 모든 재귀 function이 호출되는 인자에 관계없이 종료됨을 증명할 수 있어야 합니다.
실제로, 즉, 재귀 호출이 모두 입력의 구조적으로 더 작은 부분에 대해 수행되며 항상 기본 경우에 대한 진행을 보장하거나, 또는 사용자가 function이 항상 종료됨을 나타내는 다른 증거를 제공해야 함입니다.
마찬가지로, 재귀 inductive type은 그 type *로부터* function을 취하는 constructor를 가질 수 없습니다. 왜냐하면 이는 비종료 function을 인코딩할 수 있게 하기 때문입니다.
