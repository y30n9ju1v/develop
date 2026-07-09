---
title: "1.6. 다형성"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "다형성"
---

# 1.6. Polymorphism

Just as in most languages, types in Lean can take arguments.
For instance, the type `List Nat` describes lists of natural numbers, `List String` describes lists of strings, and `List (List Point)` describes lists of lists of points.
This is very similar to `List<Nat>`, `List<String>`, or `List<List<Point>>` in a language like C# or Java.
Just as Lean uses a space to pass an argument to a function, it uses a space to pass an argument to a type.

In functional programming, the term *polymorphism* typically refers to datatypes and definitions that take types as arguments.
This is different from the object-oriented programming community, where the term typically refers to subclasses that may override some behavior of their superclass.
In this book, “polymorphism” always refers to the first sense of the word.
These type arguments can be used in the datatype or definition, which allows the same datatype or definition to be used with any type that results from replacing the arguments' names with some other types.

대부분의 언어에서와 마찬가지로, Lean의 타입도 인수를 받을 수 있습니다.
예를 들어, 타입 `List Nat`은 자연수 리스트를 설명하고, `List String`은 문자열 리스트를 설명하며, `List (List Point)`는 점 리스트의 리스트를 설명합니다.
이는 C# 또는 Java와 같은 언어의 `List<Nat>`, `List<String>`, 또는 `List<List<Point>>`과 매우 유사합니다.
Lean이 공백을 사용하여 함수에 인수를 전달하는 것처럼, 타입에 인수를 전달하기 위해 공백을 사용합니다.

함수형 프로그래밍에서 *다형성(polymorphism)*이라는 용어는 일반적으로 타입을 인수로 받는 데이터타입과 정의를 의미합니다.
즉, 객체 지향 프로그래밍 커뮤니티와 다르며, 여기서 이 용어는 일반적으로 슈퍼클래스의 일부 동작을 재정의할 수 있는 하위 클래스입니다.
이 책에서 “다형성”은 항상 첫 번째 의미를 의미합니다.
이러한 타입 인수는 데이터타입 또는 정의에서 사용될 수 있으며, 인수의 이름을 다른 타입으로 대체한 결과인 모든 타입과 함께 동일한 데이터타입 또는 정의를 사용할 수 있습니다.

The `Point` structure requires that both the `x` and `y` fields are `Float`s.
There is, however, nothing about points that require a specific representation for each coordinate.
A polymorphic version of `Point`, called `PPoint`, can take a type as an argument, and then use that type for both fields:

```lean
structure PPoint (α : Type) where
x : α
y : α
```

Just as a function definition's arguments are written immediately after the name being defined, a structure's arguments are written immediately after the structure's name.
It is customary to use Greek letters to name type arguments in Lean when no more specific name suggests itself.
`Type` is a type that describes other types, so `Nat`, `List String`, and `PPoint Int` all have type `Type`.

`Point` 구조체는 `x`과 `y` 필드가 모두 `Float`이어야 합니다.
그러나 각 좌표에 대한 특정 표현이 필요한 점에 대해 특별한 것은 없습니다.
`PPoint`라고 불리는 `Point`의 다형 버전은 타입을 인수로 받을 수 있고, 그 타입을 두 필드 모두에 사용할 수 있습니다:

```lean
structure PPoint (α : Type) where
x : α
y : α
```

함수 정의의 인수가 정의되는 이름 직후에 작성되는 것처럼, 구조체의 인수는 구조체의 이름 직후에 작성됩니다.
더 구체적인 이름이 없을 때 Lean에서 타입 인수의 이름을 지정하기 위해 그리스 문자를 사용하는 것이 관례입니다.
`Type`은 다른 타입을 설명하는 타입이므로, `Nat`, `List String`, `PPoint Int` 모두 타입 `Type`을 가집니다.

Just like `List`, `PPoint` can be used by providing a specific type as its argument:

```lean
def natOrigin : PPoint Nat :=
{ x := Nat.zero, y := Nat.zero }
```

In this example, both fields are expected to be `Nat`s.
Just as a function is called by replacing its argument variables with its argument values, providing `PPoint` with the type `Nat` as an argument yields a structure in which the fields `x` and `y` have the type `Nat`, because the argument name `α` has been replaced by the argument type `Nat`.
Types are ordinary expressions in Lean, so passing arguments to polymorphic types (like `PPoint`) doesn't require any special syntax.

`List`처럼, `PPoint`는 특정 타입을 인수로 제공하여 사용될 수 있습니다.

이 예제에서, 두 필드 모두 `Nat`이어야 합니다.
함수가 인수 변수를 인수 값으로 대체하여 호출되는 것처럼, `PPoint`에 타입 `Nat`을 인수로 제공하면 필드 `x`과 `y`이 타입 `Nat`을 가지는 구조체가 생성됩니다. 왜냐하면 인수 이름 `α`가 인수 타입 `Nat`으로 대체되었기 때문입니다.
타입은 Lean의 일반 표현식이므로, 다형 타입(예: `PPoint`)에 인수를 전달하는 것은 특수한 구문이 필요하지 않습니다.

Definitions may also take types as arguments, which makes them polymorphic.
The function `replaceX` replaces the `x` field of a `PPoint` with a new value.
In order to allow `replaceX` to work with *any* polymorphic point, it must be polymorphic itself.
This is achieved by having its first argument be the type of the point's fields, with later arguments referring back to the first argument's name.

```lean
def replaceX (α : Type) (point : PPoint α) (newX : α) : PPoint α :=
{ point with x := newX }
```

In other words, when the types of the arguments `point` and `newX` mention `α`, they are referring to *whichever type was provided as the first argument*.
This is similar to the way that function argument names refer to the values that were provided when they occur in the function's body.

정의도 타입을 인수로 받을 수 있으며, 이는 그들을 다형으로 만듭니다.
함수 `replaceX`는 `PPoint`의 `x` 필드를 새로운 값으로 바꿉니다.
`replaceX`가 *모든* 다형 점과 작동하도록 허용하려면, 그것 자체가 다형이어야 합니다.
이는 첫 번째 인수가 점의 필드의 타입이고, 나중 인수가 첫 번째 인수의 이름을 참조하도록 함으로써 달성됩니다.

다시 말해, 인수 `point`와 `newX`의 타입이 `α`를 언급할 때, 그들은 *첫 번째 인수로 제공된 타입*을 참조합니다.
이는 함수 인수 이름이 함수의 본문에서 나타날 때 제공된 값을 참조하는 방식과 유사합니다.

This can be seen by asking Lean to check the type of `replaceX`, and then asking it to check the type of `replaceX Nat`.

```lean
#check replaceX
```

```
replaceX : (α : Type) → PPoint α → α → PPoint α
```

`replaceX`의 타입을 확인하고, `replaceX Nat`의 타입을 확인하면 볼 수 있습니다.

This function type includes the *name* of the first argument, and later arguments in the type refer back to this name.
Just as the value of a function application is found by replacing the argument name with the provided argument value in the function's body, the type of a function application is found by replacing the argument's name with the provided value in the function's return type.
Providing the first argument, `Nat`, causes all occurrences of `α` in the remainder of the type to be replaced with `Nat`:

이 함수 타입은 첫 번째 인수의 *이름*을 포함하고, 타입의 나중 인수들은 이 이름을 참조합니다.
함수 적용의 값이 함수의 본문에서 인수 이름을 제공된 인수 값으로 대체하여 찾아지는 것처럼, 함수 적용의 타입은 함수의 반환 타입에서 인수의 이름을 제공된 값으로 대체하여 찾아집니다.
첫 번째 인수 `Nat`을 제공하면, 타입의 나머지 부분에서 `α`의 모든 발생이 `Nat`으로 대체됩니다:

```lean
#check replaceX Nat
```

```
replaceX Nat : PPoint Nat → Nat → PPoint Nat
```

Because the remaining arguments are not explicitly named, no further substitution occurs as more arguments are provided:

나머지 인수들이 명시적으로 이름지어지지 않았으므로, 더 많은 인수가 제공될 때 추가 대체가 발생하지 않습니다:

```lean
#check replaceX Nat natOrigin
```

```
replaceX Nat natOrigin : Nat → PPoint Nat
```

```lean
#check replaceX Nat natOrigin 5
```

```
replaceX Nat natOrigin 5 : PPoint Nat
```

The fact that the type of the whole function application expression was determined by passing a type as an argument has no bearing on the ability to evaluate it.

전체 함수 적용 표현식의 타입이 타입을 인수로 전달하여 결정된다는 사실은 그것을 평가하는 능력에 영향을 주지 않습니다.

```lean
#eval replaceX Nat natOrigin 5
```

```
{ x := 5, y := 0 }
```

Polymorphic functions work by taking a named type argument and having later types refer to the argument's name.
However, there's nothing special about type arguments that allows them to be named.
Given a datatype that represents positive or negative signs:

다형 함수는 이름지어진 타입 인수를 받고 나중 타입들이 그 인수의 이름을 참조하도록 작동합니다.
그러나 타입 인수가 이름지어질 수 있도록 하는 특별한 것은 없습니다.
양수 또는 음수 부호를 나타내는 데이터타입이 주어지면:

```lean
inductive Sign where
| pos
| neg
```

it is possible to write a function whose argument is a sign.
If the argument is positive, the function returns a `Nat`, while if it's negative, it returns an `Int`:

부호를 인수로 받는 함수를 작성할 수 있습니다.
인수가 양수이면 함수는 `Nat`을 반환하고, 음수이면 `Int`를 반환합니다:

```lean
def posOrNegThree (s : Sign) :
match s with | Sign.pos => Nat | Sign.neg => Int :=
match s with
| Sign.pos => (3 : Nat)
| Sign.neg => (-3 : Int)
```

Because types are first class and can be computed using the ordinary rules of the Lean language, they can be computed by pattern-matching against a datatype.
When Lean is checking this function, it uses the fact that the `match`-expression in the function's body corresponds to the `match`-expression in the type to make `Nat` be the expected type for the `pos` case and to make `Int` be the expected type for the `neg` case.

타입이 일급이고 Lean 언어의 일반적인 규칙을 사용하여 계산될 수 있으므로, 데이터타입에 대해 패턴 매칭을 하여 계산될 수 있습니다.
Lean이 이 함수를 검사할 때, 함수의 본문의 `match` 표현식이 타입의 `match` 표현식과 일치한다는 사실을 사용하여 `pos` 경우에 `Nat`이 예상 타입이 되도록 하고 `neg` 경우에 `Int`이 예상 타입이 되도록 합니다.

Applying `posOrNegThree` to `pos` results in the argument name `s` in both the body of the function and its return type being replaced by `pos`.
Evaluation can occur both in the expression and its type:

`posOrNegThree`를 `pos`에 적용하면 함수의 본문과 반환 타입 모두에서 인수 이름 `s`가 `pos`로 대체됩니다.
평가는 표현식과 그 타입 모두에서 발생할 수 있습니다.

## 1.6.1. Linked Lists

Lean's standard library includes a canonical linked list datatype, called `List`, and special syntax that makes it more convenient to use.
Lists are written in square brackets.
For instance, a list that contains the prime numbers less than 10 can be written:

```lean
def primesUnder10 : List Nat := [2, 3, 5, 7]
```

Behind the scenes, `List` is an inductive datatype, defined like this:

```lean
inductive List (α : Type) where
| nil : List α
| cons : α → List α → List α
```

The actual definition in the standard library is slightly different, because it uses features that have not yet been presented, but it is substantially similar.

Lean의 표준 라이브러리는 `List`라는 표준 연결 리스트 데이터타입과 사용을 더 편리하게 하는 특수한 구문을 포함합니다.
리스트는 대괄호로 작성됩니다.
예를 들어, 10 미만의 소수를 포함하는 리스트는 다음과 같이 작성할 수 있습니다.

뒤에서, `List`는 귀납 데이터타입이며, 다음과 같이 정의됩니다.

표준 라이브러리의 실제 정의는 아직 제시되지 않은 기능을 사용하기 때문에 약간 다르지만, 본질적으로 유사합니다.
This definition says that `List` takes a single type as its argument, just as `PPoint` did.
This type is the type of the entries stored in the list.
According to the constructors, a `List α` can be built with either `nil` or `cons`.
The constructor `nil` represents empty lists and the constructor `cons` is used for non-empty lists.
The first argument to `cons` is the head of the list, and the second argument is its tail.
A list that contains `n` entries contains `n` `cons` constructors, the last of which has `nil` as its tail.

이 정의는 `PPoint`처럼 `List`가 단일 타입을 인수로 받음을 나타냅니다.
이 타입은 리스트에 저장된 항목들의 타입입니다.
생성자에 따르면, `List α`는 `nil` 또는 `cons`로 구성될 수 있습니다.
생성자 `nil`은 빈 리스트를 나타내고, 생성자 `cons`는 비어있지 않은 리스트를 위해 사용됩니다.
`cons`의 첫 번째 인수는 리스트의 머리(head)이고, 두 번째 인수는 꼬리(tail)입니다.
`n`개의 항목을 포함하는 리스트는 `n`개의 `cons` 생성자를 포함하며, 마지막 것은 `nil`을 꼬리로 가집니다.

The `primesUnder10` example can be written more explicitly by using `List`'s constructors directly:

```lean
def explicitPrimesUnder10 : List Nat :=
List.cons 2 (List.cons 3 (List.cons 5 (List.cons 7 List.nil)))
```

These two definitions are completely equivalent, but `primesUnder10` is much easier to read than `explicitPrimesUnder10`.

Functions that consume `List`s can be defined in much the same way as functions that consume `Nat`s.
Indeed, one way to think of a linked list is as a `Nat` that has an extra data field dangling off each `succ` constructor.
From this point of view, computing the length of a list is the process of replacing each `cons` with a `succ` and the final `nil` with a `zero`.
Just as `replaceX` took the type of the fields of the point as an argument, `length` takes the type of the list's entries.
For example, if the list contains strings, then the first argument is `String`: `length String ["Sourdough", "bread"]`.
It should compute like this:

`List`를 소비하는 함수는 `Nat`을 소비하는 함수와 거의 같은 방식으로 정의할 수 있습니다.
실제로, 연결 리스트를 생각하는 한 가지 방법은 각 `succ` 생성자에서 튀어나온 추가 데이터 필드를 가진 `Nat`입니다.
이 관점에서, 리스트의 길이를 계산하는 것은 각 `cons`를 `succ`으로, 마지막 `nil`을 `zero`로 대체하는 과정입니다.
`replaceX`가 점의 필드의 타입을 인수로 받은 것처럼, `length`는 리스트의 항목들의 타입을 받습니다.
예를 들어, 리스트에 문자열이 포함되면, 첫 번째 인수는 `String`입니다: `length String ["Sourdough", "bread"]`.
계산 결과는 다음과 같아야 합니다.

The definition of `length` is both polymorphic (because it takes the list entry type as an argument) and recursive (because it refers to itself).
Generally, functions follow the shape of the data: recursive datatypes lead to recursive functions, and polymorphic datatypes lead to polymorphic functions.

`length`의 정의는 다형적(리스트 항목 타입을 인수로 받기 때문에)이면서 동시에 재귀적(자신을 참조하기 때문에)입니다.
일반적으로, 함수들은 데이터의 모양을 따릅니다: 재귀적 데이터타입은 재귀적 함수를 야기하고, 다형 데이터타입은 다형 함수를 야기합니다.

```lean
def length (α : Type) (xs : List α) : Nat :=
match xs with
| List.nil => Nat.zero
| List.cons y ys => Nat.succ (length α ys)
```

Names such as `xs` and `ys` are conventionally used to stand for lists of unknown values.
The `s` in the name indicates that they are plural, so they are pronounced “exes” and “whys” rather than “x s” and “y s”.

To make it easier to read functions on lists, the bracket notation `[]` can be used to pattern-match against `nil`, and an infix `::` can be used in place of `cons`:

```lean
def length (α : Type) (xs : List α) : Nat :=
match xs with
| [] => 0
| y :: ys => Nat.succ (length α ys)
```

## 1.6.2. Implicit Arguments

Both `replaceX` and `length` are somewhat bureaucratic to use, because the type argument is typically uniquely determined by the later values.
Indeed, in most languages, the compiler is perfectly capable of determining type arguments on its own, and only occasionally needs help from users.
This is also the case in Lean.
Arguments can be declared *implicit* by wrapping them in curly braces instead of parentheses when defining a function.
For example, a version of `replaceX` with an implicit type argument looks like this:

```lean
def replaceX {α : Type} (point : PPoint α) (newX : α) : PPoint α :=
{ point with x := newX }
```

It can be used with `natOrigin` without providing `Nat` explicitly, because Lean can *infer* the value of `α` from the later arguments:

`replaceX`와 `length` 모두 타입 인수가 일반적으로 나중의 값에 의해 고유하게 결정되기 때문에 다소 관료적으로 사용됩니다.
실제로, 대부분의 언어에서 컴파일러는 타입 인수를 스스로 결정할 수 있으며, 사용자의 도움이 필요한 경우는 드뭅니다.
Lean도 마찬가지입니다.
함수를 정의할 때 괄호 대신 중괄호로 인수를 감싸서 인수를 *암시적*으로 선언할 수 있습니다.
예를 들어, 암시적 타입 인수를 가진 `replaceX` 버전은 다음과 같습니다.

`Nat`을 명시적으로 제공하지 않고도 `natOrigin`과 함께 사용할 수 있습니다. Lean이 나중 인수에서 `α`의 값을 *추론*할 수 있기 때문입니다:

```lean
#eval replaceX natOrigin 5
```

```
{ x := 5, y := 0 }
```

Similarly, `length` can be redefined to take the entry type implicitly:

마찬가지로, `length`는 항목 타입을 암시적으로 받도록 재정의할 수 있습니다:

```lean
def length {α : Type} (xs : List α) : Nat :=
match xs with
| [] => 0
| y :: ys => Nat.succ (length ys)
```

This `length` function can be applied directly to `primesUnder10`:

이 `length` 함수는 `primesUnder10`에 직접 적용될 수 있습니다:

```lean
#eval length primesUnder10
```

```
4
```

In the standard library, Lean calls this function `List.length`, which means that the dot syntax that is used for structure field access can also be used to find the length of a list:

표준 라이브러리에서, Lean은 이 함수를 `List.length`라고 부르며, 이는 구조체 필드 접근에 사용되는 점 표기법이 또한 리스트의 길이를 찾는 데도 사용될 수 있음을 의미합니다:

```lean
#eval primesUnder10.length
```

```
4
```

Just as C# and Java require type arguments to be provided explicitly from time to time, Lean is not always capable of finding implicit arguments.
In these cases, they can be provided using their names.
For example, a version of `List.length` that only works for lists of integers can be specified by setting `α` to `Int`:

C#과 Java가 때때로 타입 인수를 명시적으로 제공하도록 요구하는 것처럼, Lean도 항상 암시적 인수를 찾을 수 있는 것은 아닙니다.
이러한 경우들에, 그들은 이름을 사용하여 제공될 수 있습니다.
예를 들어, 정수 리스트에만 작동하는 `List.length` 버전은 `α`를 `Int`로 설정하여 지정할 수 있습니다:

```lean
#check List.length (α := Int)
```

```
List.length : List Int → Nat
```

## 1.6.3. More Built-In Datatypes

In addition to lists, Lean's standard library contains a number of other structures and inductive datatypes that can be used in a variety of contexts.

리스트 외에도, Lean의 표준 라이브러리는 다양한 컨텍스트에서 사용될 수 있는 다른 구조체와 귀납 데이터타입들을 포함합니다.

### 1.6.3.1. `Option`

Not every list has a first entry—some lists are empty.
Many operations on collections may fail to find what they are looking for.
For instance, a function that finds the first entry in a list may not find any such entry.
It must therefore have a way to signal that there was no first entry.

Many languages have a `null` value that represents the absence of a value.
Instead of equipping existing types with a special `null` value, Lean provides a datatype called `Option` that equips some other type with an indicator for missing values.
For instance, a nullable `Int` is represented by `Option Int`, and a nullable list of strings is represented by the type `Option (List String)`.
Introducing a new type to represent nullability means that the type system ensures that checks for `null` cannot be forgotten, because an `Option Int` can't be used in a context where an `Int` is expected.

모든 리스트가 첫 번째 항목을 가지지는 않습니다. 일부 리스트는 비어 있습니다.
모음에 대한 많은 연산은 찾고 있는 것을 찾지 못할 수 있습니다.
예를 들어, 리스트의 첫 번째 항목을 찾는 함수는 그러한 항목을 찾지 못할 수 있습니다.
따라서 첫 번째 항목이 없었음을 신호하는 방법이 있어야 합니다.

많은 언어는 값의 부재를 나타내는 `null` 값을 가지고 있습니다.
기존 타입에 특수 `null` 값을 갖추는 대신, Lean은 `Option`이라는 데이터타입을 제공하여 다른 타입에 누락된 값에 대한 표시기를 갖춥니다.
예를 들어, 널 가능 `Int`는 `Option Int`로 표현되고, 널 가능 문자열 리스트는 타입 `Option (List String)`으로 표현됩니다.
널 가능성을 나타내기 위해 새로운 타입을 도입하는 것은 `Option Int`가 `Int`가 예상되는 컨텍스트에서 사용될 수 없기 때문에 타입 시스템이 `null` 검사를 잊을 수 없음을 보장합니다.

`Option` has two constructors, called `some` and `none`, that respectively represent the non-null and null versions of the underlying type.
The non-null constructor, `some`, contains the underlying value, while `none` takes no arguments:

`Option`은 `some`과 `none`이라는 두 개의 생성자를 가지는데, 이들은 각각 기저 타입의 non-null과 null 버전을 나타냅니다.
non-null 생성자인 `some`은 기저 값을 포함하고, `none`은 인수를 받지 않습니다:

```lean
inductive Option (α : Type) : Type where
| none : Option α
| some (val : α) : Option α
```

The `Option` type is very similar to nullable types in languages like C# and Kotlin, but it is not identical.
In these languages, if a type (say, `Boolean`) always refers to actual values of the type (`true` and `false`), the type `Boolean?` or `Nullable<Boolean>` additionally admits the `null` value.
Tracking this in the type system is very useful: the type checker and other tooling can help programmers remember to check for `null`, and APIs that explicitly describe nullability through type signatures are more informative than ones that don't.
However, these nullable types differ from Lean's `Option` in one very important way, which is that they don't allow multiple layers of optionality.
`Option (Option Int)` can be constructed with `none`, `some none`, or `some (some 360)`.
Kotlin, on the other hand, treats `T??` as being equivalent to `T?`.

`Option` 타입은 C#과 Kotlin 같은 언어의 nullable 타입과 매우 유사하지만, 동일하지는 않습니다.
이 언어들에서, 타입이 (예를 들어, `Boolean`) 항상 타입의 실제 값을 참조하면 (`true`와 `false`), 타입 `Boolean?` 또는 `Nullable<Boolean>`은 추가로 `null` 값을 인정합니다.
타입 시스템에서 이를 추적하는 것은 매우 유용합니다: 타입 체커와 다른 도구들이 프로그래머들이 `null`을 검사하도록 기억하는 것을 도울 수 있고, 타입 서명을 통해 명시적으로 nullability를 설명하는 API는 그렇지 않은 것들보다 더 정보적입니다.
그러나, 이러한 nullable 타입들은 Lean의 `Option`과 한 가지 매우 중요한 방식에서 다르며, 그것은 여러 계층의 옵션성을 허용하지 않는다는 것입니다.
`Option (Option Int)`은 `none`, `some none`, 또는 `some (some 360)`으로 구성될 수 있습니다.
반면에 Kotlin은 `T??`을 `T?`과 동등하게 취급합니다.
This subtle difference is rarely relevant in practice, but it can matter from time to time.

이 미묘한 차이는 실제로는 거의 관련이 없지만, 때때로 중요할 수 있습니다.

To find the first entry in a list, if it exists, use `List.head?`.
The question mark is part of the name, and is not related to the use of question marks to indicate nullable types in C# or Kotlin.
In the definition of `List.head?`, an underscore is used to represent the tail of the list.
In patterns, underscores match anything at all, but do not introduce variables to refer to the matched data.
Using underscores instead of names is a way to clearly communicate to readers that part of the input is ignored.

리스트에서 첫 번째 항목을 찾으려면 (존재한다면), `List.head?`를 사용합니다.
물음표는 이름의 일부이며, C# 또는 Kotlin에서 nullable 타입을 나타내기 위해 물음표를 사용하는 것과는 관련이 없습니다.
`List.head?`의 정의에서, 언더스코어는 리스트의 꼬리를 나타내는 데 사용됩니다.
패턴에서, 언더스코어는 모든 것을 매칭하지만, 매칭된 데이터를 참조하기 위한 변수를 도입하지 않습니다.
이름 대신 언더스코어를 사용하는 것은 입력의 일부가 무시된다는 것을 독자에게 명확하게 전달하는 방법입니다.

```lean
def List.head? {α : Type} (xs : List α) : Option α :=
match xs with
| [] => none
| y :: _ => some y
```

A Lean naming convention is to define operations that might fail in groups using the suffixes `?` for a version that returns an `Option`, `!` for a version that crashes when provided with invalid input, and `D` for a version that returns a default value when the operation would otherwise fail.
Following this pattern, `List.head` requires the caller to provide mathematical evidence that the list is not empty, `List.head?` returns an `Option`, `List.head!` crashes the program when passed an empty list, and `List.headD` takes a default value to return in case the list is empty.
The question mark and exclamation mark are part of the name, not special syntax, as Lean's naming rules are more liberal than many languages.

Lean 명명 규칙은 `?` 접미사를 사용하여 실패할 수 있는 연산들을 그룹으로 정의하는 것으로, `Option`을 반환하는 버전의 경우, `!`는 잘못된 입력이 제공될 때 충돌하는 버전의 경우, `D`는 연산이 실패할 때 기본값을 반환하는 버전의 경우입니다.
이 패턴을 따르면, `List.head`는 호출자가 리스트가 비어있지 않다는 수학적 증거를 제공해야 하고, `List.head?`는 `Option`을 반환하며, `List.head!`는 빈 리스트가 전달될 때 프로그램을 충돌시키고, `List.headD`는 리스트가 비어있을 경우 반환할 기본값을 받습니다.
물음표와 느낌표는 특수 구문이 아니라 이름의 일부이며, Lean의 명명 규칙은 많은 언어보다 더 자유롭습니다.

Because `head?` is defined in the `List` namespace, it can be used with accessor notation:

`head?`가 `List` namespace에 정의되어 있기 때문에, 접근자 표기법과 함께 사용될 수 있습니다:

```lean
#eval primesUnder10.head?
```

```
some 2
```

However, attempting to test it on the empty list leads to two errors:

```lean
#eval [].head?
```

```
don't know how to synthesize implicit argument `α`
  @List.nil ?m.3
context:
⊢ Type ?u.71735
```

```
don't know how to synthesize implicit argument `α`
  @_root_.List.head? ?m.3 []
context:
⊢ Type ?u.71735
```

This is because Lean was unable to fully determine the expression's type.
In particular, it could neither find the implicit type argument to `List.head?`, nor the implicit type argument to `List.nil`.
In Lean's output, `?m.XYZ` represents a part of a program that could not be inferred.
These unknown parts are called *metavariables*, and they occur in some error messages.
In order to evaluate an expression, Lean needs to be able to find its type, and the type was unavailable because the empty list does not have any entries from which the type can be found.
Explicitly providing a type allows Lean to proceed:

이것은 Lean이 표현식의 타입을 완전히 결정할 수 없었기 때문입니다.
특히, `List.head?`의 암시적 타입 인수나 `List.nil`의 암시적 타입 인수를 모두 찾을 수 없었습니다.
Lean의 출력에서, `?m.XYZ`는 추론될 수 없는 프로그램의 일부를 나타냅니다.
이러한 알 수 없는 부분들을 *메타변수(metavariables)*라고 하며, 이들은 일부 에러 메시지에서 발생합니다.
표현식을 평가하기 위해, Lean은 그 타입을 찾을 수 있어야 하며, 빈 리스트는 타입을 찾을 수 있는 항목이 없기 때문에 타입을 사용할 수 없었습니다.
명시적으로 타입을 제공하면 Lean이 진행할 수 있습니다:

```lean
#eval [].head? (α := Int)
```

```
none
```

The type can also be provided with a type annotation:

타입은 타입 주석으로도 제공될 수 있습니다:

```lean
#eval ([] : List Int).head?
```

```
none
```

The error messages provide a useful clue.
Both messages use the *same* metavariable to describe the missing implicit argument, which means that Lean has determined that the two missing pieces will share a solution, even though it was unable to determine the actual value of the solution.

에러 메시지는 유용한 단서를 제공합니다.
두 메시지 모두 누락된 암시적 인수를 설명하기 위해 *동일한* 메타변수를 사용하는데, 즉, 실제 해결책의 값을 결정할 수는 없었지만 두 누락된 부분이 해결책을 공유할 것이라고 Lean이 결정했다는 것입니다.

### 1.6.3.2. `Prod`

The `Prod` structure, short for “Product”, is a generic way of joining two values together.
For instance, a `Prod Nat String` contains a `Nat` and a `String`.
In other words, `PPoint Nat` could be replaced by `Prod Nat Nat`.
`Prod` is very much like C#'s tuples, the `Pair` and `Triple` types in Kotlin, and `tuple` in C++.
Many applications are best served by defining their own structures, even for simple cases like `Point`, because using domain terminology can make it easier to read the code.
Additionally, defining structure types helps catch more errors by assigning different types to different domain concepts, preventing them from being mixed up.

`Prod` 구조체는 “곱”의 약자로, 두 값을 함께 연결하는 일반적인 방법입니다.
예를 들어, `Prod Nat String`은 `Nat`과 `String`을 포함합니다.
다시 말해, `PPoint Nat`은 `Prod Nat Nat`으로 대체될 수 있습니다.
`Prod`는 C#의 튜플, Kotlin의 `Pair`과 `Triple` 타입, C++의 `tuple`과 매우 유사합니다.
많은 애플리케이션은 `Point`와 같은 간단한 경우에도 자신만의 구조체를 정의하는 것이 좋으며, 도메인 용어를 사용하면 코드를 더 쉽게 읽을 수 있기 때문입니다.
또한 구조체 타입을 정의하면 서로 다른 도메인 개념에 서로 다른 타입을 할당하여 더 많은 오류를 잡을 수 있으며, 혼동되지 않도록 방지합니다.

On the other hand, there are some cases where it is not worth the overhead of defining a new type.
Additionally, some libraries are sufficiently generic that there is no more specific concept than “pair”.
Finally, the standard library contains a variety of convenience functions that make it easier to work with the built-in pair type.

반면에, 새로운 타입을 정의하는 오버헤드의 가치가 없는 경우들이 있습니다.
또한, 일부 라이브러리는 충분히 일반적이어서 “pair”보다 더 구체적인 개념이 없습니다.
마지막으로, 표준 라이브러리는 기본 제공 pair 타입으로 작업하기를 더 쉽게 하는 다양한 편의 함수를 포함합니다.

The structure `Prod` is defined with two type arguments:

`Prod` 구조체는 두 개의 타입 인수로 정의됩니다:

```lean
structure Prod (α : Type) (β : Type) : Type where
fst : α
snd : β
```

Lists are used so frequently that there is special syntax to make them more readable.
For the same reason, both the product type and its constructor have special syntax.
The type `Prod α β` is typically written `α × β`, mirroring the usual notation for a Cartesian product of sets.
Similarly, the usual mathematical notation for pairs is available for `Prod`.
In other words, instead of writing:

리스트는 너무 자주 사용되어서 읽기 쉽게 하기 위한 특수 구문이 있습니다.
같은 이유로, product 타입과 그 생성자 모두 특수한 구문을 가집니다.
타입 `Prod α β`는 일반적으로 `α × β`로 작성되며, 집합의 Cartesian product에 대한 관례적인 표기법을 반영합니다.
마찬가지로, pair에 대한 관례적인 수학 표기법이 `Prod`에 사용될 수 있습니다.
다시 말해, 다음과 같이 작성하는 대신:

```lean
def fives : String × Int := { fst := "five", snd := 5 }
```

it suffices to write:

다음과 같이 쓰면 충분합니다:

```lean
def fives : String × Int := ("five", 5)
```

Both notations are right-associative.

두 표기법 모두 우결합성입니다.
This means that the following definitions are equivalent:

이는 다음 정의들이 동등함을 의미합니다:

```lean
def sevens : String × Int × Nat := ("VII", 7, 4 + 3)
def sevens : String × (Int × Nat) := ("VII", (7, 4 + 3))
```

In other words, all products of more than two types, and their corresponding constructors, are actually nested products and nested pairs behind the scenes.

다시 말해, 두 개 이상의 타입의 모든 product들과 그들의 해당하는 생성자들은 실제로 내부에서 중첩된 product들과 중첩된 pair들입니다.

### 1.6.3.3. `Sum`

The `Sum` datatype is a generic way of allowing a choice between values of two different types.
For instance, a `Sum String Int` is either a `String` or an `Int`.
Like `Prod`, `Sum` should be used either when writing very generic code, for a very small section of code where there is no sensible domain-specific type, or when the standard library contains useful functions.
In most situations, it is more readable and maintainable to use a custom inductive type.

`Sum` 데이터타입은 두 가지 다른 타입의 값 중에서 선택할 수 있게 하는 일반적인 방법입니다.
예를 들어, `Sum String Int`는 `String` 또는 `Int`입니다.
`Prod`와 마찬가지로, `Sum`은 매우 일반적인 코드를 작성할 때, 합리적인 도메인별 타입이 없는 코드의 매우 작은 섹션에 대해, 또는 표준 라이브러리에 유용한 함수가 포함되어 있을 때 사용되어야 합니다.
대부분의 상황에서 사용자 정의 귀납 타입을 사용하는 것이 더 읽기 쉽고 유지할 수 있습니다.

Values of type `Sum α β` are either the constructor `inl` applied to a value of type `α` or the constructor `inr` applied to a value of type `β`:

`Sum α β` 타입의 값들은 `α` 타입의 값에 적용된 생성자 `inl`이거나 `β` 타입의 값에 적용된 생성자 `inr`입니다:

```lean
inductive Sum (α : Type) (β : Type) : Type where
| inl : α → Sum α β
| inr : β → Sum α β
```

These names are abbreviations for “left injection” and “right injection”, respectively.
Just as the Cartesian product notation is used for `Prod`, a “circled plus” notation is used for `Sum`, so `α ⊕ β` is another way to write `Sum α β`.
There is no special syntax for `Sum.inl` and `Sum.inr`.

이 이름들은 각각 “left injection”과 “right injection”의 약자입니다.
Cartesian product 표기법이 `Prod`에 사용되는 것처럼, “circled plus” 표기법이 `Sum`에 사용되므로, `α ⊕ β`는 `Sum α β`를 작성하는 다른 방법입니다.
`Sum.inl`과 `Sum.inr`에 특수한 구문은 없습니다.

As an example, if pet names can either be dog names or cat names, then a type for them can be introduced as a sum of strings:

예시로, 애완동물 이름이 개 이름이거나 고양이 이름이라면, 그들을 위한 타입은 문자열의 합으로 도입될 수 있습니다:

```lean
def PetName : Type := String ⊕ String
```

In a real program, it would usually be better to define a custom inductive datatype for this purpose with informative constructor names.
Here, `Sum.inl` is to be used for dog names, and `Sum.inr` is to be used for cat names.
These constructors can be used to write a list of animal names:

실제 프로그램에서는, 보통 정보적인 생성자 이름을 가진 사용자 정의 귀납 데이터타입을 정의하는 것이 더 나을 것입니다.
여기서, `Sum.inl`은 개 이름을 위해 사용되고, `Sum.inr`은 고양이 이름을 위해 사용됩니다.
이 생성자들은 동물 이름의 리스트를 작성하는 데 사용될 수 있습니다:

```lean
def animals : List PetName :=
[Sum.inl "Spot", Sum.inr "Tiger", Sum.inl "Fifi",
Sum.inl "Rex", Sum.inr "Floof"]
```

Pattern matching can be used to distinguish between the two constructors.
For instance, a function that counts the number of dogs in a list of animal names (that is, the number of `Sum.inl` constructors) looks like this:

패턴 매칭을 사용하여 두 생성자를 구분할 수 있습니다.
예를 들어, 동물 이름 리스트에서 개의 개수를 세는 함수 (즉, `Sum.inl` 생성자의 개수)는 다음과 같습니다:

```lean
def howManyDogs (pets : List PetName) : Nat :=
match pets with
| [] => 0
| Sum.inl _ :: morePets => howManyDogs morePets + 1
| Sum.inr _ :: morePets => howManyDogs morePets
```

Function calls are evaluated before infix operators, so `howManyDogs morePets + 1` is the same as `(howManyDogs morePets) + 1`.
As expected, `#eval howManyDogs animals` yields `3`.

함수 호출은 중위 연산자 전에 평가되므로, `howManyDogs morePets + 1`은 `(howManyDogs morePets) + 1`과 동일합니다.
예상대로, `#eval howManyDogs animals`는 `3`을 산출합니다.

### 1.6.3.4. `Unit`

`Unit` is a type with just one argumentless constructor, called `unit`.
In other words, it describes only a single value, which consists of said constructor applied to no arguments whatsoever.
`Unit` is defined as follows:

```lean
inductive Unit : Type where
| unit : Unit
```

On its own, `Unit` is not particularly useful.
However, in polymorphic code, it can be used as a placeholder for data that is missing.
For instance, the following inductive datatype represents arithmetic expressions:

```lean
inductive ArithExpr (ann : Type) : Type where
| int : ann → Int → ArithExpr ann
| plus : ann → ArithExpr ann → ArithExpr ann → ArithExpr ann
| minus : ann → ArithExpr ann → ArithExpr ann → ArithExpr ann
| times : ann → ArithExpr ann → ArithExpr ann → ArithExpr ann
```

The type argument `ann` stands for annotations, and each constructor is annotated.
Expressions coming from a parser might be annotated with source locations, so a return type of `ArithExpr SourcePos` ensures that the parser put a `SourcePos` at each subexpression.
Expressions that don't come from the parser, however, will not have source locations, so their type can be `ArithExpr Unit`.

`Unit`은 `unit`이라는 단 하나의 인수 없는 생성자를 가진 타입입니다.
다시 말해, 이는 단일 값만 설명하며, 인수 없이 적용된 생성자로 구성됩니다.
`Unit`은 다음과 같이 정의됩니다:

```lean
inductive Unit : Type where
| unit : Unit
```

자체적으로 `Unit`은 특별히 유용하지 않습니다.
그러나 다형 코드에서, 누락된 데이터에 대한 자리 표시자로 사용될 수 있습니다.
예를 들어, 다음의 귀납 데이터타입은 산술 표현식을 나타냅니다.

타입 인수 `ann`은 주석을 나타내며, 각 생성자는 주석이 달립니다.
파서에서 오는 표현식은 소스 위치로 주석이 달릴 수 있으므로, `ArithExpr SourcePos`의 반환 타입은 파서가 각 부분식에 `SourcePos`를 넣었음을 보장합니다.
파서에서 오지 않는 표현식은 소스 위치를 갖지 않으므로, 그들의 타입은 `ArithExpr Unit`일 수 있습니다.

Additionally, because all Lean functions have arguments, zero-argument functions in other languages can be represented as functions that take a `Unit` argument.
In a return position, the `Unit` type is similar to `void` in languages derived from C.
In the C family, a function that returns `void` will return control to its caller, but it will not return any interesting value.
By being an intentionally uninteresting value, `Unit` allows this to be expressed without requiring a special-purpose `void` feature in the type system.
Unit's constructor can be written as empty parentheses: `() : Unit`.

또한, 모든 Lean 함수가 인수를 가지기 때문에, 다른 언어의 인수 없는 함수는 `Unit` 인수를 받는 함수로 표현될 수 있습니다.
반환 위치에서, `Unit` 타입은 C로부터 파생된 언어의 `void`와 유사합니다.
C 계열에서, `void`를 반환하는 함수는 호출자에게 제어를 반환하지만, 흥미로운 값을 반환하지는 않습니다.
의도적으로 흥미롭지 않은 값이 됨으로써, `Unit`은 타입 시스템에서 특수 목적의 `void` 기능이 필요하지 않고도 이를 표현할 수 있게 합니다.
Unit의 생성자는 빈 괄호로 작성될 수 있습니다: `() : Unit`.

### 1.6.3.5. `Empty`

The `Empty` datatype has no constructors whatsoever.
Thus, it indicates unreachable code, because no series of calls can ever terminate with a value at type `Empty`.

`Empty` is not used nearly as often as `Unit`.
However, it is useful in some specialized contexts.
Many polymorphic datatypes do not use all of their type arguments in all of their constructors.
For instance, `Sum.inl` and `Sum.inr` each use only one of `Sum`'s type arguments.
Using `Empty` as one of the type arguments to `Sum` can rule out one of the constructors at a particular point in a program.
This can allow generic code to be used in contexts that have additional restrictions.

`Empty` 데이터타입은 생성자가 전혀 없습니다.
따라서 도달할 수 없는 코드를 나타냅니다. 왜냐하면 함수 호출 시리즈가 `Empty` 타입의 값으로 종료될 수 없기 때문입니다.

`Empty`는 `Unit`만큼 자주 사용되지 않습니다.
그러나 일부 특수한 컨텍스트에서 유용합니다.
많은 다형 데이터타입은 모든 생성자에서 모든 타입 인수를 사용하지 않습니다.
예를 들어, `Sum.inl`과 `Sum.inr`은 각각 `Sum`의 타입 인수 중 하나만 사용합니다.
`Sum`의 타입 인수 중 하나로 `Empty`를 사용하면 프로그램의 특정 지점에서 생성자 중 하나를 배제할 수 있습니다.
이는 일반 코드가 추가 제한이 있는 컨텍스트에서 사용될 수 있도록 허용합니다.

### 1.6.3.6. Naming: Sums, Products, and Units

Generally speaking, types that offer multiple constructors are called *sum types*, while types whose single constructor takes multiple arguments are called *product types*.
These terms are related to sums and products used in ordinary arithmetic.
The relationship is easiest to see when the types involved contain a finite number of values.
If `α` and `β` are types that contain `n` and `k` distinct values, respectively, then `α ⊕ β` contains `n + k` distinct values and `α × β` contains `n \times k` distinct values.
For instance, `Bool` has two values: `true` and `false`, and `Unit` has one value: `Unit.unit`.
The product `Bool × Unit` has the two values `(true, Unit.unit)` and `(false, Unit.unit)`, and the sum `Bool ⊕ Unit` has the three values `Sum.inl true`, `Sum.inl false`, and `Sum.inr Unit.unit`.

일반적으로 말해서, 여러 생성자를 제공하는 타입을 *합 타입(sum types)*이라고 하고, 단일 생성자가 여러 인수를 받는 타입을 *곱 타입(product types)*이라고 합니다.
이러한 용어는 일반 산술에서 사용되는 합과 곱과 관련이 있습니다.
관계는 관련된 타입이 유한한 수의 값을 포함할 때 가장 쉽게 볼 수 있습니다.
`α`과 `β`가 각각 `n`과 `k`개의 서로 다른 값을 포함하는 타입이면, `α ⊕ β`는 `n + k`개의 서로 다른 값을 포함하고 `α × β`는 `n \times k`개의 서로 다른 값을 포함합니다.
예를 들어, `Bool`은 `true`과 `false` 두 개의 값을 가지고, `Unit`은 `Unit.unit` 하나의 값을 가집니다.
곱 `Bool × Unit`은 `(true, Unit.unit)`과 `(false, Unit.unit)` 두 개의 값을 가지고, 합 `Bool ⊕ Unit`은 `Sum.inl true`, `Sum.inl false`, `Sum.inr Unit.unit` 세 개의 값을 가집니다.
Similarly, `2 \times 1 = 2`, and `2 + 1 = 3`.

마찬가지로, `2 \times 1 = 2`, `2 + 1 = 3`입니다.

## 1.6.4. Messages You May Meet

Not all definable structures or inductive types can have the type `Type`.
In particular, if a constructor takes an arbitrary type as an argument, then the inductive type must have a different type.
These errors usually state something about “universe levels”.

모든 정의 가능한 구조체 또는 귀납 타입이 `Type` 타입을 가질 수는 없습니다.
특히, 생성자가 임의의 타입을 인수로 받으면, 귀납 타입은 다른 타입을 가져야 합니다.
이 에러들은 보통 “universe levels”에 대해 언급합니다.
For example, for this inductive type:

```lean
inductive MyType : Type where
| ctor : (α : Type) → α → MyType
```

Lean gives the following error:

```
Invalid universe level in constructor `MyType.ctor`: Parameter `α` has type
  Type
at universe level
  2
which is not less than or equal to the inductive type's resulting universe level
  1
```

A later chapter describes why this is the case, and how to modify definitions to make them work.
For now, try making the type an argument to the inductive type as a whole, rather than to the constructor.

나중의 장에서는 이것이 왜 이런지, 그리고 정의를 수정하여 작동하게 하는 방법을 설명합니다.
지금은, 생성자가 아니라 귀납 타입 전체에 인수로 타입을 만드는 것을 시도해보십시오.

Similarly, if a constructor's argument is a function that takes the datatype being defined as an argument, then the definition is rejected.
For example:

마찬가지로, 생성자의 인수가 정의되는 데이터타입을 인수로 받는 함수라면, 정의는 거부됩니다.
예를 들어:

```lean
inductive MyType : Type where
| ctor : (MyType → Int) → MyType
```

yields the message:

```
(kernel) arg #1 of 'MyType.ctor' has a non positive occurrence of the datatypes being declared
```

For technical reasons, allowing these datatypes could make it possible to undermine Lean's internal logic, making it unsuitable for use as a theorem prover.

기술적인 이유로, 이러한 데이터타입을 허용하면 Lean의 내부 논리를 훼손할 수 있게 되어, 정리 증명기로 사용하기에 부적합해질 수 있습니다.

Recursive functions that take two parameters should not match against the pair, but rather match each parameter independently.
Otherwise, the mechanism in Lean that checks whether recursive calls are made on smaller values is unable to see the connection between the input value and the argument in the recursive call.
For example, this function that determines whether two lists have the same length is rejected:

두 개의 매개변수를 받는 재귀 함수는 pair에 대해 매칭하지 말고, 대신 각 매개변수를 독립적으로 매칭해야 합니다.
그렇지 않으면, 재귀 호출이 더 작은 값에 대해 이루어지는지 확인하는 Lean의 메커니즘이 입력 값과 재귀 호출의 인수 사이의 연결을 볼 수 없습니다.
예를 들어, 두 개의 리스트가 같은 길이를 가지는지 결정하는 이 함수는 거부됩니다:

```lean
def sameLength (xs : List α) (ys : List β) : Bool :=
match (xs, ys) with
| ([], []) => true
| (x :: xs', y :: ys') => sameLength xs' ys'
| _ => false
```

The error message is:

에러 메시지는:

```
fail to show termination for
  sameLength
with errors
failed to infer structural recursion:
Not considering parameter α of sameLength:
  it is unchanged in the recursive calls
Not considering parameter β of sameLength:
  it is unchanged in the recursive calls
Cannot use parameter xs:
  failed to eliminate recursive application
    sameLength xs' ys'
Cannot use parameter ys:
  failed to eliminate recursive application
    sameLength xs' ys'

Could not find a decreasing measure.
The basic measures relate at each recursive call as follows:
(<, ≤, =: relation proved, ? all proofs failed, _: no proof attempted)
              xs ys
1) 1816:28-46  ?  ?
Please use `termination_by` to specify a decreasing measure.
```

The problem can be fixed through nested pattern matching:

문제는 중첩된 패턴 매칭을 통해 해결될 수 있습니다:

```lean
def sameLength (xs : List α) (ys : List β) : Bool :=
match xs with
| [] =>
  match ys with
  | [] => true
  | _ => false
| x :: xs' =>
  match ys with
  | y :: ys' => sameLength xs' ys'
  | _ => false
```

[Simultaneous matching](../ch01/), described in the next section, is another way to solve the problem that is often more elegant.

다음 섹션에서 설명하는 [동시 매칭(Simultaneous matching)](../ch01/)은 종종 더 우아한 문제 해결 방법입니다.

Forgetting an argument to an inductive type can also yield a confusing message.
For example, when the argument `α` is not passed to `MyType` in `ctor`'s type:

```lean
inductive MyType (α : Type) : Type where
| ctor : α → MyType
```

Lean replies with the following error:

```
type expected, got
  (MyType : Type → Type)
```

The error message is saying that `MyType`'s type, which is `Type → Type`, does not itself describe types.
`MyType` requires an argument to become an actual honest-to-goodness type.

The same message can appear when type arguments are omitted in other contexts, such as in a type signature for a definition:

```lean
inductive MyType (α : Type) : Type where
| ctor : α → MyType α

def ofFive : MyType := ctor 5
```

```
type expected, got
  (MyType : Type → Type)
```

Evaluating expressions that use polymorphic types may trigger a situation in which Lean is incapable of displaying a value.
The `#eval` command evaluates the provided expression, using the expression's type to determine how to display the result.
For some types, such as functions, this process fails, but Lean is perfectly capable of automatically generating display code for most other types.
There is no need, for example, to provide Lean with any specific display code for `WoodSplittingTool`:

```lean
inductive WoodSplittingTool where
| axe
| maul
| froe
```

```lean
#eval WoodSplittingTool.axe
```

```
WoodSplittingTool.axe
```

There are limits to the automation that Lean uses here, however.
`allTools` is a list of all three tools:

```lean
def allTools : List WoodSplittingTool := [
  WoodSplittingTool.axe,
  WoodSplittingTool.maul,
  WoodSplittingTool.froe
]
```

Evaluating it leads to an error:

```lean
#eval allTools
```

```
could not synthesize a `ToExpr`, `Repr`, or `ToString` instance for type
  List WoodSplittingTool
```

This is because Lean attempts to use code from a built-in table to display a list, but this code demands that display code for `WoodSplittingTool` already exists.
This error can be worked around by instructing Lean to generate this display code when a datatype is defined, instead of at the last moment as part of `#eval`, by adding `deriving Repr` to its definition:

```lean
inductive Firewood where
| birch
| pine
| beech
deriving Repr
```

Evaluating a list of `Firewood` succeeds:

```lean
def allFirewood : List Firewood := [
  Firewood.birch,
  Firewood.pine,
  Firewood.beech
]
```

```lean
#eval allFirewood
```

```
[Firewood.birch, Firewood.pine, Firewood.beech]
```

## 1.6.5. Exercises

* Write a function to find the last entry in a list. It should return an `Option`.
* Write a function that finds the first entry in a list that satisfies a given predicate. Start the definition with `def List.findFirst? {α : Type} (xs : List α) (predicate : α → Bool) : Option α := …`.
* Write a function `Prod.switch` that switches the two fields in a pair for each other. Start the definition with `def Prod.switch {α β : Type} (pair : α × β) : β × α := …`.
* Rewrite the `PetName` example to use a custom datatype and compare it to the version that uses `Sum`.
* Write a function `zip` that combines two lists into a list of pairs. The resulting list should be as long as the shortest input list. Start the definition with `def zip {α β : Type} (xs : List α) (ys : List β) : List (α × β) := …`.
* Write a polymorphic function `take` that returns the first `n` entries in a list, where `n` is a `Nat`. If the list contains fewer than `n` entries, then the resulting list should be the entire input list. `#eval take 3 ["bolete", "oyster"]` should yield `["bolete", "oyster"]`, and `#eval take 1 ["bolete", "oyster"]` should yield `["bolete"]`.
* Using the analogy between types and arithmetic, write a function that distributes products over sums. In other words, it should have type `α × (β ⊕ γ) → (α × β) ⊕ (α × γ)`.
* Using the analogy between types and arithmetic, write a function that turns multiplication by two into a sum. In other words, it should have type `Bool × α → α ⊕ α`.
