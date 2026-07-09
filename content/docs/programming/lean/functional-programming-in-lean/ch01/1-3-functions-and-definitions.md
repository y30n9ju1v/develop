---
title: "함수와 정의"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "함수와 정의"
---

# 1.3. Functions and Definitions

In Lean, definitions are introduced using the `def` keyword.
For instance, to define the name `hello` to refer to the string `"Hello"`, write:

```lean
def hello := "Hello"
```

In Lean, new names are defined using the colon-equal operator `:=` rather than `=`.
This is because `=` is used to describe equalities between existing expressions, and using two different operators helps prevent confusion.

Lean에서 정의는 `def` 키워드를 사용하여 도입됩니다.
예를 들어, 이름 `hello`를 문자열 `"Hello"`를 참조하도록 정의하려면, 다음과 같이 작성합니다.

Lean에서 새로운 이름은 `=` 대신 콜론-같음 연산자 `:=`를 사용하여 정의됩니다.
이는 `=`이 기존 표현식 간의 동등성을 설명하는 데 사용되기 때문이며, 두 개의 다른 연산자를 사용하는 것이 혼동을 방지하는 데 도움이 됩니다.

In the definition of `hello`, the expression `"Hello"` is simple enough that Lean is able to determine the definition's type automatically.
However, most definitions are not so simple, so it will usually be necessary to add a type.
This is done using a colon after the name being defined:

```lean
def lean : String := "Lean"
```

Now that the names have been defined, they can be used, so

```lean
#eval String.append hello (String.append " " lean)
```

outputs

```
"Hello Lean"
```

In Lean, defined names may only be used after their definitions.

`hello`의 정의에서, 표현식 `"Hello"`는 충분히 단순하여 Lean이 정의의 타입을 자동으로 결정할 수 있습니다.
하지만 대부분의 정의는 그렇게 단순하지 않으므로, 일반적으로 타입을 추가해야 합니다.
이는 정의되는 이름 뒤에 콜론을 사용하여 수행됩니다.

Lean에서 정의된 이름은 그들의 정의 후에만 사용할 수 있습니다.

In many languages, definitions of functions use a different syntax than definitions of other values.
For instance, Python function definitions begin with the `def` keyword, while other definitions are defined with an equals sign.
In Lean, functions are defined using the same `def` keyword as other values.
Nonetheless, definitions such as `hello` introduce names that refer *directly* to their values, rather than to zero-argument functions that return equivalent results each time they are called.

많은 언어에서 함수의 정의는 다른 값의 정의와 다른 문법을 사용합니다.
예를 들어, Python 함수 정의는 `def` 키워드로 시작하고, 다른 정의는 등호로 정의됩니다.
Lean에서 함수는 다른 값과 같은 `def` 키워드를 사용하여 정의됩니다.
그럼에도 불구하고, `hello`와 같은 정의는 이름을 그들의 값에 *직접* 참조하도록 도입하며, 호출될 때마다 동등한 결과를 반환하는 영인수 함수가 아닙니다.

## 1.3.1. Defining Functions

There are a variety of ways to define functions in Lean. The simplest is to place the function's arguments before the definition's type, separated by spaces. For instance, a function that adds one to its argument can be written:

```lean
def add1 (n : Nat) : Nat := n + 1
```

Testing this function with `#eval` gives `8`, as expected:

```lean
#eval add1 7
```

```
8
```

Just as functions are applied to multiple arguments by writing spaces between each argument, functions that accept multiple arguments are defined with spaces between the arguments' names and types. The function `maximum`, whose result is equal to the greatest of its two arguments, takes two `Nat` arguments `n` and `k` and returns a `Nat`.

```lean
def maximum (n : Nat) (k : Nat) : Nat :=
  if n < k then
    k
  else n
```

Similarly, the function `spaceBetween` joins two strings with a space between them.

```lean
def spaceBetween (before : String) (after : String) : String :=
  String.append before (String.append " " after)
```

Lean에서 함수를 정의하는 다양한 방법이 있습니다. 가장 간단한 방법은 함수의 인수를 정의의 타입 앞에 공백으로 구분하여 배치하는 것입니다. 예를 들어, 인수에 1을 더하는 함수는 다음과 같이 작성할 수 있습니다.

이 함수를 `#eval`로 테스트하면 예상대로 `8`을 제공합니다.

함수가 각 인수 사이에 공백을 작성하여 여러 인수에 적용되는 것처럼, 여러 인수를 수용하는 함수는 인수의 이름과 타입 사이에 공백을 사용하여 정의됩니다. 함수 `maximum`은 결과가 두 인수 중 가장 큰 것과 같으며, 두 개의 `Nat` 인수 `n`과 `k`를 가지고 `Nat`을 반환합니다.

마찬가지로, 함수 `spaceBetween`은 두 문자열을 그 사이에 공백과 함께 연결합니다.

When a defined function like `maximum` has been provided with its arguments, the result is determined by first replacing the argument names with the provided values in the body, and then evaluating the resulting body. For example:

```
maximum (5 + 8) (2 * 7)
maximum 13 14
if 13 < 14 then 14 else 13
14
```

Expressions that evaluate to natural numbers, integers, and strings have types that say this (`Nat`, `Int`, and `String`, respectively).
This is also true of functions.
A function that accepts a `Nat` and returns a `Bool` has type `Nat → Bool`, and a function that accepts two `Nat`s and returns a `Nat` has type `Nat → Nat → Nat`.

`maximum`과 같은 정의된 함수에 인수가 제공되면, 결과는 본문의 인수 이름을 제공된 값으로 대체한 다음, 결과 본문을 평가하여 결정됩니다.

자연수, 정수, 문자열로 평가되는 표현식은 이를 나타내는 타입을 가집니다(`Nat`, `Int`, `String` 각각).
이는 함수에도 해당합니다.
`Nat`을 받고 `Bool`을 반환하는 함수는 타입 `Nat → Bool`을 가지며, 두 개의 `Nat`을 받고 `Nat`을 반환하는 함수는 타입 `Nat → Nat → Nat`을 가집니다.

As a special case, Lean returns a function's signature when its name is used directly with `#check`.
Entering `#check add1` yields `add1 (n : Nat) : Nat`.
However, Lean can be “tricked” into showing the function's type by writing the function's name in parentheses, which causes the function to be treated as an ordinary expression, so `#check (add1)` yields `add1 : Nat → Nat` and `#check (maximum)` yields `maximum : Nat → Nat → Nat`.
This arrow can also be written with an ASCII alternative arrow `->`, so the preceding function types can be written `example : Nat -> Nat := add1` and `example : Nat -> Nat -> Nat := maximum`, respectively.

특수한 경우로, Lean은 이름이 `#check`와 함께 직접 사용될 때 함수의 서명을 반환합니다.
`#check add1`을 입력하면 `add1 (n : Nat) : Nat`를 산출합니다.
하지만 Lean은 함수의 이름을 괄호로 작성하여 함수의 타입을 표시하도록 “속여질” 수 있으며, 이는 함수를 일반 표현식으로 처리하게 하므로 `#check (add1)`은 `add1 : Nat → Nat`를 산출하고 `#check (maximum)`은 `maximum : Nat → Nat → Nat`를 산출합니다.
이 화살표는 ASCII 대체 화살표 `->`로도 작성할 수 있으므로, 앞의 함수 타입은 `example : Nat -> Nat := add1`과 `example : Nat -> Nat -> Nat := maximum`으로 각각 작성될 수 있습니다.

Behind the scenes, all functions actually expect precisely one argument.
Functions like `maximum` that seem to take more than one argument are in fact functions that take one argument and then return a new function.
This new function takes the next argument, and the process continues until no more arguments are expected.
This can be seen by providing one argument to a multiple-argument function: `#check maximum 3` yields `maximum 3 : Nat → Nat` and `#check spaceBetween "Hello "` yields `spaceBetween "Hello " : String → String`.
Using a function that returns a function to implement multiple-argument functions is called *currying* after the mathematician Haskell Curry.
Function arrows associate to the right, which means that `Nat → Nat → Nat` should be parenthesized `Nat → (Nat → Nat)`.

뒤에서 모든 함수는 실제로 정확히 하나의 인수를 기대합니다.
`maximum`과 같이 하나 이상의 인수를 받는 것처럼 보이는 함수는 실제로 하나의 인수를 받은 다음 새 함수를 반환하는 함수입니다.
이 새 함수는 다음 인수를 받고, 더 이상 인수가 필요하지 않을 때까지 이 과정이 계속됩니다.
이는 여러 인수를 가진 함수에 하나의 인수를 제공함으로써 확인할 수 있습니다: `#check maximum 3`은 `maximum 3 : Nat → Nat`를 산출하고 `#check spaceBetween "Hello "`는 `spaceBetween "Hello " : String → String`을 산출합니다.
함수를 반환하는 함수를 사용하여 여러 인수를 가진 함수를 구현하는 것을 수학자 Haskell Curry의 이름을 따서 *커링(currying)*이라고 합니다.
함수 화살표는 오른쪽으로 결합되므로, `Nat → Nat → Nat`을 `Nat → (Nat → Nat)`으로 괄호 처리해야 합니다.

### 1.3.1.1. Exercises

* Define the function `joinStringsWith` with type `String → String → String → String` that creates a new string by placing its first argument between its second and third arguments. `joinStringsWith ", " "one" "and another"` should evaluate to `"one, and another"`.
* What is the type of `joinStringsWith ": "`? Check your answer with Lean.
* Define a function `volume` with type `Nat → Nat → Nat → Nat` that computes the volume of a rectangular prism with the given height, width, and depth.

* 타입이 `String → String → String → String`인 함수 `joinStringsWith`를 정의하세요. 이 함수는 첫 번째 인수를 두 번째와 세 번째 인수 사이에 배치하여 새 문자열을 만듭니다. `joinStringsWith ", " "one" "and another"`는 `"one, and another"`로 평가되어야 합니다.
* `joinStringsWith ": "`의 타입은 무엇입니까? Lean으로 답을 확인하세요.
* 타입이 `Nat → Nat → Nat → Nat`인 함수 `volume`을 정의하세요. 이 함수는 주어진 높이, 너비, 깊이를 가진 직육면체의 부피를 계산합니다.

## 1.3.2. Defining Types

Most typed programming languages have some means of defining aliases for types, such as C's `typedef`.
In Lean, however, types are a first-class part of the language—they are expressions like any other.
This means that definitions can refer to types just as well as they can refer to other values.

For example, if `String` is too much to type, a shorter abbreviation `Str` can be defined:

```lean
def Str : Type := String
```

It is then possible to use `Str` as a definition's type instead of `String`:

```lean
def aStr : Str := "This is a string."
```

The reason this works is that types follow the same rules as the rest of Lean.
Types are expressions, and in an expression, a defined name can be replaced with its definition.
Because `Str` has been defined to mean `String`, the definition of `aStr` makes sense.

대부분의 타입 프로그래밍 언어는 C의 `typedef`와 같이 타입에 대한 별칭을 정의하는 일부 수단을 가지고 있습니다.
그러나 Lean에서는 타입이 언어의 일급 부분입니다. 즉, 다른 표현식처럼 표현식입니다.
즉, 정의가 다른 값을 참조할 수 있는 것처럼 타입도 참조할 수 있습니다.

예를 들어, `String`을 입력하기에 너무 길면, 더 짧은 약자 `Str`을 정의할 수 있습니다.

그러면 `String` 대신 `Str`을 정의의 타입으로 사용할 수 있습니다.

이것이 작동하는 이유는 타입이 Lean의 나머지 부분과 같은 규칙을 따르기 때문입니다.
타입은 표현식이며, 표현식에서 정의된 이름을 그 정의로 바꿀 수 있습니다.
`Str`이 `String`을 의미하도록 정의되었기 때문에, `aStr`의 정의는 의미가 있습니다.

### 1.3.2.1. Messages You May Meet

Experimenting with using definitions for types is made more complicated by the way that Lean supports overloaded integer literals.
If `Nat` is too short, a longer name `NaturalNumber` can be defined:

```lean
def NaturalNumber : Type := Nat
```

However, using `NaturalNumber` as a definition's type instead of `Nat` does not have the expected effect.
In particular, the definition:

```lean
def thirtyEight : NaturalNumber := 38
```

results in the following error:

```
failed to synthesize
  OfNat NaturalNumber 38
numerals are polymorphic in Lean, but the numeral `38` cannot be used in a context where the expected type is
  NaturalNumber
due to the absence of the instance above

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

This error occurs because Lean allows number literals to be *overloaded*.
When it makes sense to do so, natural number literals can be used for new types, just as if those types were built in to the system.
This is part of Lean's mission of making it convenient to represent mathematics, and different branches of mathematics use number notation for very different purposes.
The specific feature that allows this overloading does not replace all defined names with their definitions before looking for overloading, which is what leads to the error message above.

타입에 정의를 사용하는 것을 실험하는 것은 Lean이 오버로드된 정수 리터럴을 지원하는 방식으로 인해 더 복잡해집니다.
`Nat`이 너무 짧으면, 더 긴 이름 `NaturalNumber`를 정의할 수 있습니다.

하지만 `Nat` 대신 `NaturalNumber`를 정의의 타입으로 사용하는 것은 예상된 효과를 갖지 않습니다.
특히, 정의:

```lean
def thirtyEight : NaturalNumber := 38
```

는 다음 오류를 초래합니다.

```
failed to synthesize
  OfNat NaturalNumber 38
numerals are polymorphic in Lean, but the numeral `38` cannot be used in a context where the expected type is
  NaturalNumber
due to the absence of the instance above

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

이 오류는 Lean이 숫자 리터럴을 *오버로드*할 수 있기 때문에 발생합니다.
적절할 때, 자연수 리터럴을 새로운 타입에 사용할 수 있으며, 마치 그 타입이 시스템에 내장된 것처럼입니다.
이는 수학을 표현하는 것을 편리하게 만드는 것이 Lean의 사명의 일부이며, 수학의 다양한 분야는 매우 다른 목적으로 숫자 표기법을 사용합니다.
이 오버로딩을 허용하는 특정 기능은 오버로딩을 찾기 전에 모든 정의된 이름을 그들의 정의로 대체하지 않으므로, 이것이 위의 오류 메시지로 이어지는 것입니다.

One way to work around this limitation is by providing the type `Nat` on the right-hand side of the definition, causing `Nat`'s overloading rules to be used for `38`:

```lean
def thirtyEight : NaturalNumber := (38 : Nat)
```

The definition is still type-correct because `NaturalNumber` is the same type as `Nat`—by definition!

Another solution is to define an overloading for `NaturalNumber` that works equivalently to the one for `Nat`.
This requires more advanced features of Lean, however.

Finally, defining the new name for `Nat` using `abbrev` instead of `def` allows overloading resolution to replace the defined name with its definition.
Definitions written using `abbrev` are always unfolded.
For instance,

```lean
abbrev N : Type := Nat
```

and

```lean
def thirtyNine : N := 39
```

are accepted without issue.

Behind the scenes, some definitions are internally marked as being unfoldable during overload resolution, while others are not.
Definitions that are to be unfolded are called *reducible*.
Control over reducibility is essential to allow Lean to scale: fully unfolding all definitions can result in very large types that are slow for a machine to process and difficult for users to understand.
Definitions produced with `abbrev` are marked as reducible.

이 제한을 우회하는 한 가지 방법은 정의의 오른쪽에 타입 `Nat`을 제공하여, `Nat`의 오버로딩 규칙이 `38`에 사용되도록 하는 것입니다.

정의는 여전히 타입이 올바릅니다. 왜냐하면 `NaturalNumber`는 `Nat`과 같은 타입이기 때문입니다. 정의에 의해!

다른 해결책은 `Nat`의 것과 동등하게 작동하는 `NaturalNumber`에 대한 오버로딩을 정의하는 것입니다.
하지만 이것은 Lean의 더 고급 기능이 필요합니다.

마지막으로, `def` 대신 `abbrev`를 사용하여 `Nat`의 새로운 이름을 정의하면 오버로딩 해결이 정의된 이름을 그 정의로 대체할 수 있습니다.
`abbrev`를 사용하여 작성된 정의는 항상 전개됩니다.
예를 들어,

```lean
abbrev N : Type := Nat
```

그리고

```lean
def thirtyNine : N := 39
```

는 문제없이 허용됩니다.

뒤에서, 일부 정의는 오버로드 해결 중에 전개 가능한 것으로 내부적으로 표시되고, 다른 것은 그렇지 않습니다.
전개될 정의를 *축약 가능(reducible)*이라고 합니다.
축약 가능성에 대한 제어는 Lean이 확장될 수 있도록 하는 데 필수적입니다: 모든 정의를 완전히 전개하면 매우 큰 타입이 결과될 수 있으며, 이는 기계가 처리하기에 느리고 사용자가 이해하기 어렵습니다.
`abbrev`로 생성된 정의는 축약 가능으로 표시됩니다.
