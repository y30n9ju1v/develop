---
title: "3.1. 양수"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "양수를 표현하는 타입 클래스"
---

# 3.1. Positive Numbers

In some applications, only positive numbers make sense.
For example, compilers and interpreters typically use one-indexed line and column numbers for source positions, and a datatype that represents only non-empty lists will never report a length of zero.
Rather than relying on natural numbers, and littering the code with assertions that the number is not zero, it can be useful to design a datatype that represents only positive numbers.

일부 애플리케이션에서는 양수만 의미가 있습니다. 예를 들어, 컴파일러와 인터프리터는 일반적으로 소스 위치에 대해 1부터 시작하는 행과 열 번호를 사용하며, 비어있지 않은 리스트만 나타내는 데이터타입은 길이가 0인 경우를 보고하지 않습니다. 자연수에 의존하고 숫자가 0이 아님을 확인하는 assertion으로 코드를 오염시키는 대신, 양수만을 나타내는 데이터타입을 설계하는 것이 유용할 수 있습니다.

One way to represent positive numbers is very similar to `Nat`, except with `one` as the base case instead of `zero`:

양수를 나타내는 한 가지 방법은 `Nat`과 매우 유사하지만, `zero` 대신 `one`을 기본 경우로 사용합니다:

```lean
inductive Pos : Type where
| one : Pos
| succ : Pos → Pos
```

This datatype represents exactly the intended set of values, but it is not very convenient to use.
For example, numeric literals are rejected:

이 데이터타입은 의도한 값들의 집합을 정확히 나타내지만, 사용하기에는 매우 불편합니다. 예를 들어, 숫자 리터럴이 거부됩니다:

```lean
def seven : Pos := 7
```

```
failed to synthesize
  OfNat Pos 7
numerals are polymorphic in Lean, but the numeral `7` cannot be used in a context where the expected type is
  Pos
due to the absence of the instance above

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

Instead, the constructors must be used directly:

대신, constructor를 직접 사용해야 합니다:

```lean
def seven : Pos :=
  Pos.succ (Pos.succ (Pos.succ (Pos.succ (Pos.succ (Pos.succ Pos.one)))))
```

Similarly, addition and multiplication are not easy to use:

마찬가지로, 덧셈과 곱셈도 사용하기 쉽지 않습니다:

```lean
def fourteen : Pos := seven + seven
```

```
failed to synthesize
  HAdd Pos Pos ?m.3

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

```lean
def fortyNine : Pos := seven * seven
```

```
failed to synthesize
  HMul Pos Pos ?m.3

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

Each of these error messages begins with `failed to synthesize`.
This indicates that the error is due to an overloaded operation that has not been implemented, and it describes the type class that must be implemented.

이 오류 메시지들은 모두 `failed to synthesize`로 시작합니다. 이는 오류가 구현되지 않은 overloaded operation 때문임을 나타내며, 구현되어야 하는 type class를 설명합니다.

## 3.1.1. Classes and Instances

A type class consists of a name, some parameters, and a collection of *methods*.
The parameters describe the types for which overloadable operations are being defined, and the methods are the names and type signatures of the overloadable operations.
Once again, there is a terminology clash with object-oriented languages.
In object-oriented programming, a method is essentially a function that is connected to a particular object in memory, with special access to the object's private state.
Objects are interacted with via their methods.
In Lean, the term “method” refers to an operation that has been declared to be overloadable, with no special connection to objects or values or private fields.

Type class는 이름, 일부 매개변수, 그리고 *method*들의 모음으로 구성됩니다. 매개변수는 overloadable operation이 정의되는 타입들을 설명하며, method는 overloadable operation의 이름과 타입 시그니처입니다. 다시 한 번, 객체 지향 언어와의 용어 충돌이 있습니다. 객체 지향 프로그래밍에서 method는 메모리의 특정 객체와 연결되어 있고 객체의 private state에 특별히 접근할 수 있는 함수입니다. 객체는 method를 통해 상호작용합니다. Lean에서 “method”라는 용어는 overloadable로 선언된 operation을 의미하며, 객체, 값, 또는 private field와의 특별한 연결이 없습니다.

One way to overload addition is to define a type class named `Plus`, with an addition method named `plus`.
Once an instance of `Plus` for `Nat` has been defined, it becomes possible to add two `Nat`s using `Plus.plus`:

덧셈을 overload하는 한 가지 방법은 `plus`라는 덧셈 method를 가진 `Plus`라는 type class를 정의하는 것입니다. `Nat`에 대한 `Plus`의 instance가 정의되면, `Plus.plus`를 사용하여 두 `Nat`을 더할 수 있습니다:

```lean
#eval Plus.plus 5 3
```

```
8
```

Adding more instances allows `Plus.plus` to take more types of arguments.

더 많은 instance를 추가하면 `Plus.plus`가 더 많은 타입의 인자를 받을 수 있습니다.

In the following type class declaration, `Plus` is the name of the class, `α : Type` is the only argument, and `plus : α → α → α` is the only method:

다음 type class 선언에서 `Plus`는 클래스의 이름이고, `α : Type`은 유일한 인자이며, `plus : α → α → α`는 유일한 method입니다:

```lean
class Plus (α : Type) where
  plus : α → α → α
```

This declaration says that there is a type class `Plus` that overloads operations with respect to a type `α`.
In particular, there is one overloaded operation called `plus` that takes two `α`s and returns an `α`.

이 선언은 타입 `α`에 대해 operation을 overload하는 type class `Plus`가 있음을 의미합니다. 특히, 두 개의 `α`를 받아 `α`를 반환하는 `plus`라는 하나의 overloaded operation이 있습니다.

Type classes are first class, just as types are first class.
In particular, a type class is another kind of type.
The type of `Plus` is `Type → Type`, because it takes a type as an argument (`α`) and results in a new type that describes the overloading of `Plus`'s operation for `α`.

Type class는 타입이 first class인 것처럼 first class입니다. 특히, type class는 다른 종류의 타입입니다. `Plus`의 타입은 `Type → Type`입니다. 왜냐하면 타입을 인자로 받고 (`α`), `α`에 대한 `Plus`의 operation의 overloading을 설명하는 새로운 타입을 결과로 내기 때문입니다.

To overload `plus` for a particular type, write an instance:

특정 타입에 대해 `plus`를 overload하려면 instance를 작성합니다:

```lean
instance : Plus Nat where
  plus := Nat.add
```

The colon after `instance` indicates that `Plus Nat` is indeed a type.
Each method of class `Plus` should be assigned a value using `:=`.
In this case, there is only one method: `plus`.

`instance` 뒤의 콜론은 `Plus Nat`이 실제로 타입임을 나타냅니다. class `Plus`의 각 method는 `:=`를 사용하여 값을 할당해야 합니다. 이 경우, 유일한 method는 `plus`입니다.

By default, type class methods are defined in a namespace with the same name as the type class.
It can be convenient to `open` the namespace so that users don't need to type the name of the class first.
Parentheses in an `open` command indicate that only the indicated names from the namespace are to be made accessible:

기본적으로, type class method는 type class와 같은 이름의 namespace에 정의됩니다. 사용자가 먼저 클래스의 이름을 입력할 필요가 없도록 namespace를 `open`하는 것이 편할 수 있습니다. `open` 명령의 괄호는 namespace의 지정된 이름만 접근 가능하게 해야 함을 나타냅니다:

```lean
open Plus (plus)
#eval plus 5 3
```

```
8
```

Defining an addition function for `Pos` and an instance of `Plus Pos` allows `plus` to be used to add both `Pos` and `Nat` values:

`Pos`에 대한 덧셈 함수와 `Plus Pos`의 instance를 정의하면 `plus`를 사용하여 `Pos`와 `Nat` 값을 모두 더할 수 있습니다:

```lean
def Pos.plus : Pos → Pos → Pos
  | Pos.one, k => Pos.succ k
  | Pos.succ n, k => Pos.succ (n.plus k)

instance : Plus Pos where
  plus := Pos.plus

def fourteen : Pos := plus seven seven
```

Because there is not yet an instance of `Plus Float`, attempting to add two floating-point numbers with `plus` fails with a familiar message:

아직 `Plus Float`의 instance가 없기 때문에, `plus`로 두 부동소수점 수를 더하려고 시도하면 친숙한 메시지와 함께 실패합니다:

```lean
#eval plus 5.2 917.25861
```

```
failed to synthesize
  Plus Float

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

These errors mean that Lean was unable to find an instance for a given type class.

이 오류들은 Lean이 주어진 type class에 대한 instance를 찾을 수 없음을 의미합니다.

## 3.1.2. Overloaded Addition

Lean's built-in addition operator is syntactic sugar for a type class called `HAdd`, which flexibly allows the arguments to addition to have different types.
`HAdd` is short for *heterogeneous addition*.
For example, an `HAdd` instance can be written to allow a `Nat` to be added to a `Float`, resulting in a new `Float`.
When a programmer writes `x + y`, it is interpreted as meaning `HAdd.hAdd x y`.

Lean의 내장된 덧셈 연산자는 `HAdd`라는 type class에 대한 syntactic sugar이며, 덧셈의 인자가 서로 다른 타입을 가질 수 있도록 유연하게 허용합니다. `HAdd`는 *heterogeneous addition*의 약자입니다. 예를 들어, `Nat`을 `Float`에 더할 수 있도록 하여 새로운 `Float`을 얻는 `HAdd` instance를 작성할 수 있습니다. 프로그래머가 `x + y`를 쓰면, `HAdd.hAdd x y`를 의미하는 것으로 해석됩니다.

While an understanding of the full generality of `HAdd` relies on features that are discussed in [another section in this chapter](../ch03/), there is a simpler type class called `Add` that does not allow the types of the arguments to be mixed.
The Lean libraries are set up so that an instance of `Add` will be found when searching for an instance of `HAdd` in which both arguments have the same type.

`HAdd`의 전체 일반성을 이해하는 것은 [이 장의 다른 섹션](../ch03/)에서 논의되는 기능에 의존하지만, 인자의 타입을 혼합하지 않는 `Add`라는 더 간단한 type class가 있습니다. Lean 라이브러리는 두 인자가 같은 타입을 가지는 `HAdd`의 instance를 검색할 때 `Add`의 instance가 발견되도록 설정되어 있습니다.

Defining an instance of `Add Pos` allows `Pos` values to use ordinary addition syntax:

`Add Pos`의 instance를 정의하면 `Pos` 값이 일반적인 덧셈 문법을 사용할 수 있습니다:

```lean
instance : Add Pos where
  add := Pos.plus

def fourteen : Pos := seven + seven
```

## 3.1.3. Conversion to Strings

Another useful built-in class is called `ToString`.
Instances of `ToString` provide a standard way of converting values from a given type into strings.
For example, a `ToString` instance is used when a value occurs in an interpolated string, and it determines how the `IO.println` function used at the [beginning of the description of `IO`](../ch02/) will display a value.

또 다른 유용한 내장 클래스는 `ToString`입니다. `ToString`의 instance는 주어진 타입의 값을 문자열로 변환하는 표준적인 방법을 제공합니다. 예를 들어, `ToString` instance는 값이 interpolated string에 나타날 때 사용되며, [`IO`의 설명 시작 부분](../ch02/)에서 사용되는 `IO.println` 함수가 값을 표시하는 방식을 결정합니다.

For example, one way to convert a `Pos` into a `String` is to reveal its inner structure.
The function `posToString` takes a `Bool` that determines whether to parenthesize uses of `Pos.succ`, which should be `true` in the initial call to the function and `false` in all recursive calls.

예를 들어, `Pos`를 `String`으로 변환하는 한 가지 방법은 그 내부 구조를 드러내는 것입니다. `posToString` 함수는 `Pos.succ`의 사용에 괄호를 붙일지를 결정하는 `Bool`을 받습니다. 이는 함수의 초기 호출에서는 `true`이고 모든 재귀 호출에서는 `false`여야 합니다.

```lean
def posToString (atTop : Bool) (p : Pos) : String :=
  let paren s := if atTop then s else "(" ++ s ++ ")"
  match p with
  | Pos.one => "Pos.one"
  | Pos.succ n => paren s!"Pos.succ {posToString false n}"
```

Using this function for a `ToString` instance:

`ToString` instance에 이 함수를 사용하면:

```lean
instance : ToString Pos where
  toString := posToString true
```

results in informative, yet overwhelming, output:

그 결과는 유익하지만 압도적인 출력입니다:

```lean
#eval s!"There are {seven}"
```

```
"There are Pos.succ (Pos.succ (Pos.succ (Pos.succ (Pos.succ (Pos.succ Pos.one)))))"
```

On the other hand, every positive number has a corresponding `Nat`.
Converting it to a `Nat` and then using the `ToString Nat` instance (that is, the overloading of `ToString` for `Nat`) is a quick way to generate much shorter output:

반면에, 모든 양수는 해당하는 `Nat`을 가지고 있습니다. 이를 `Nat`으로 변환한 다음 `ToString Nat` instance를 사용하면 (즉, `Nat`에 대한 `ToString`의 overloading), 훨씬 짧은 출력을 빠르게 생성할 수 있습니다:

```lean
def Pos.toNat : Pos → Nat
  | Pos.one => 1
  | Pos.succ n => n.toNat + 1

instance : ToString Pos where
  toString x := toString (x.toNat)
```

```lean
#eval s!"There are {seven}"
```

```
"There are 7"
```

When more than one instance is defined, the most recent takes precedence.
Additionally, if a type has a `ToString` instance, then it can be used to display the result of `#eval` so `#eval seven` outputs `7`.

둘 이상의 instance가 정의되면 가장 최근의 것이 우선합니다. 추가로, 타입이 `ToString` instance를 가지면, `#eval`의 결과를 표시하는 데 사용될 수 있으므로 `#eval seven`은 `7`을 출력합니다.

## 3.1.4. Overloaded Multiplication

For multiplication, there is a type class called `HMul` that allows mixed argument types, just like `HAdd`.
Just as `x + y` is interpreted as `HAdd.hAdd x y`, `x * y` is interpreted as `HMul.hMul x y`.
For the common case of multiplication of two arguments with the same type, a `Mul` instance suffices.

곱셈의 경우, `HAdd`처럼 혼합된 인자 타입을 허용하는 `HMul`이라는 type class가 있습니다. `x + y`가 `HAdd.hAdd x y`로 해석되는 것처럼, `x * y`는 `HMul.hMul x y`로 해석됩니다. 같은 타입의 두 인자를 곱하는 일반적인 경우에는 `Mul` instance로 충분합니다.

An instance of `Mul` allows ordinary multiplication syntax to be used with `Pos`:

`Mul`의 instance는 `Pos`에서 일반적인 곱셈 문법을 사용할 수 있게 합니다:

```lean
def Pos.mul : Pos → Pos → Pos
  | Pos.one, k => k
  | Pos.succ n, k => n.mul k + k

instance : Mul Pos where
  mul := Pos.mul
```

With this instance, multiplication works as expected:

이 instance를 사용하면 곱셈이 예상대로 작동합니다:

```lean
#eval [seven * Pos.one,
       seven * seven,
       Pos.succ Pos.one * seven]
```

```
[7, 49, 14]
```

## 3.1.5. Literal Numbers

It is quite inconvenient to write out a sequence of constructors for positive numbers.
One way to work around the problem would be to provide a function to convert a `Nat` into a `Pos`.
However, this approach has downsides.
First off, because `Pos` cannot represent `0`, the resulting function would either convert a `Nat` to a bigger number, or it would return `Option Pos`.
Neither is particularly convenient for users.
Secondly, the need to call the function explicitly would make programs that use positive numbers much less convenient to write than programs that use `Nat`.
Having a trade-off between precise types and convenient APIs means that the precise types become less useful.

양수에 대한 constructor의 시퀀스를 써내려가는 것은 상당히 불편합니다. 문제를 해결하는 한 가지 방법은 `Nat`을 `Pos`로 변환하는 함수를 제공하는 것입니다. 그러나 이 접근 방식에는 단점이 있습니다. 먼저, `Pos`가 `0`을 나타낼 수 없기 때문에, 결과 함수는 `Nat`을 더 큰 수로 변환하거나 `Option Pos`를 반환할 것입니다. 둘 다 사용자에게 특별히 편하지 않습니다. 둘째, 함수를 명시적으로 호출해야 한다는 필요는 양수를 사용하는 프로그램을 `Nat`을 사용하는 프로그램보다 훨씬 덜 편하게 만들 것입니다. 정확한 타입과 편리한 API 사이의 트레이드오프를 갖는 것은 정확한 타입이 덜 유용해진다는 것을 의미합니다.

There are three type classes that are used to overload numeric literals: `Zero`, `One`, and `OfNat`.
Because many types have values that are naturally written with `0`, the `Zero` class allow these specific values to be overridden.
It is defined as follows:

numeric literal을 overload하는 데 사용되는 세 가지 type class가 있습니다: `Zero`, `One`, `OfNat`. 많은 타입이 `0`으로 자연스럽게 쓰이는 값을 가지고 있기 때문에, `Zero` class는 이러한 특정 값을 재정의할 수 있게 합니다. 다음과 같이 정의됩니다:

```lean
class Zero (α : Type) where
  zero : α
```

Because `0` is not a positive number, there should be no instance of `Zero Pos`.

`0`은 양수가 아니기 때문에, `Zero Pos`의 instance가 있어서는 안 됩니다.

Similarly, many types have values that are naturally written with `1`.
The `One` class allows these to be overridden:

마찬가지로, 많은 타입이 `1`로 자연스럽게 쓰이는 값을 가지고 있습니다. `One` class는 이러한 값을 재정의할 수 있게 합니다:

```lean
class One (α : Type) where
  one : α
```

An instance of `One Pos` makes perfect sense:

`One Pos`의 instance는 완벽한 의미가 있습니다:

```lean
instance : One Pos where
  one := Pos.one
```

With this instance, `1` can be used for `Pos.one`:

이 instance를 사용하면, `1`을 `Pos.one`에 사용할 수 있습니다:

```lean
#eval (1 : Pos)
```

```
1
```

In Lean, natural number literals are interpreted using a type class called `OfNat`:

Lean에서 natural number literal은 `OfNat`이라는 type class를 사용하여 해석됩니다:

```lean
class OfNat (α : Type) (_ : Nat) where
  ofNat : α
```

This type class takes two arguments: `α` is the type for which a natural number is overloaded, and the unnamed `Nat` argument is the actual literal number that was encountered in the program.
The method `ofNat` is then used as the value of the numeric literal.
Because the class contains the `Nat` argument, it becomes possible to define only instances for those values where the number makes sense.

이 type class는 두 개의 인자를 받습니다: `α`는 natural number가 overload되는 타입이고, 이름 없는 `Nat` 인자는 프로그램에서 만난 실제 literal number입니다. method `ofNat`은 numeric literal의 값으로 사용됩니다. class가 `Nat` 인자를 포함하고 있기 때문에, 숫자가 의미 있는 값들에 대해서만 instance를 정의할 수 있게 됩니다.

`OfNat` demonstrates that the arguments to type classes do not need to be types.
Because types in Lean are first-class participants in the language that can be passed as arguments to functions and given definitions with `def` and `abbrev`, there is no barrier that prevents non-type arguments in positions where a less-flexible language could not permit them.
This flexibility allows overloaded operations to be provided for particular values as well as particular types.
Additionally, it allows the Lean standard library to arrange for there to be a `Zero α` instance whenever there's an `OfNat α 0` instance, and vice versa.
Similarly, an instance of `One α` implies an instance of `OfNat α 1`, just as an instance of `OfNat α 1` implies an instance of `One α`.

`OfNat`은 type class의 인자가 타입일 필요가 없음을 보여줍니다. Lean의 타입은 함수의 인자로 전달될 수 있고 `def`와 `abbrev`로 정의될 수 있는 first-class 참여자이기 때문에, 덜 유연한 언어가 허용할 수 없는 위치에서 non-type 인자를 방지하는 장벽이 없습니다. 이 유연성은 특정 값뿐만 아니라 특정 타입에 대해서도 overloaded operation을 제공할 수 있게 합니다. 또한, Lean 표준 라이브러리가 `OfNat α 0` instance가 있을 때마다 `Zero α` instance가 있도록 하고 그 반대도 마찬가지로 배치할 수 있게 합니다. 마찬가지로, `One α`의 instance는 `OfNat α 1`의 instance를 암시하고, `OfNat α 1`의 instance는 `One α`의 instance를 암시합니다.

A sum type that represents natural numbers less than four can be defined as follows:

4 미만의 natural number를 나타내는 sum type은 다음과 같이 정의할 수 있습니다:

```lean
inductive LT4 where
  | zero
  | one
  | two
  | three
```

While it would not make sense to allow *any* literal number to be used for this type, numbers less than four clearly make sense:

이 타입에 *어떤* literal number도 사용하는 것이 의미 있지는 않겠지만, 4 미만의 수는 분명히 의미가 있습니다:

```lean
instance : OfNat LT4 0 where
  ofNat := LT4.zero
instance : OfNat LT4 1 where
  ofNat := LT4.one
instance : OfNat LT4 2 where
  ofNat := LT4.two
instance : OfNat LT4 3 where
  ofNat := LT4.three
```

With these instances, the following examples work:

이 instance들을 사용하면, 다음 예제들이 작동합니다:

```lean
#eval (3 : LT4)
```

```
LT4.three
```

```lean
#eval (0 : LT4)
```

```
LT4.zero
```

On the other hand, out-of-bounds literals are still not allowed:

반면에, out-of-bounds literal은 여전히 허용되지 않습니다:

```lean
#eval (4 : LT4)
```

```
failed to synthesize
  OfNat LT4 4
numerals are polymorphic in Lean, but the numeral `4` cannot be used in a context where the expected type is
  LT4
due to the absence of the instance above

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

For `Pos`, the `OfNat` instance should work for *any* `Nat` other than `Nat.zero`.
Another way to phrase this is to say that for all natural numbers `n`, the instance should work for `n + 1`.
Just as names like `α` automatically become implicit arguments to functions that Lean fills out on its own, instances can take automatic implicit arguments.
In this instance, the argument `n` stands for any `Nat`, and the instance is defined for a `Nat` that's one greater:

`Pos`의 경우, `OfNat` instance는 `Nat.zero` 외의 *모든* `Nat`에 대해 작동해야 합니다. 이를 다르게 표현하면, 모든 자연수 `n`에 대해, instance는 `n + 1`에 대해 작동해야 한다는 것입니다. `α`와 같은 이름이 자동으로 Lean이 채우는 함수의 implicit argument가 되는 것처럼, instance도 automatic implicit argument를 받을 수 있습니다. 이 instance에서, 인자 `n`은 모든 `Nat`을 나타내고, instance는 하나 더 큰 `Nat`에 대해 정의됩니다:

```lean
instance : OfNat Pos (n + 1) where
  ofNat :=
    let rec natPlusOne : Nat → Pos
      | 0 => Pos.one
      | k + 1 => Pos.succ (natPlusOne k)
    natPlusOne n
```

Because `n` stands for a `Nat` that's one less than what the user wrote, the helper function `natPlusOne` returns a `Pos` that's one greater than its argument.
This makes it possible to use natural number literals for positive numbers, but not for zero:

`n`이 사용자가 쓴 것보다 1 작은 `Nat`을 나타내기 때문에, helper function `natPlusOne`은 자신의 인자보다 1 더 큰 `Pos`를 반환합니다. 이는 양수에 대해 natural number literal을 사용하는 것을 가능하게 하지만, 0에 대해서는 불가능합니다:

```lean
def eight : Pos := 8
def zero : Pos := 0
```

```
failed to synthesize
  OfNat Pos 0
numerals are polymorphic in Lean, but the numeral `0` cannot be used in a context where the expected type is
  Pos
due to the absence of the instance above

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

## 3.1.6. Exercises

### 3.1.6.1. Another Representation

An alternative way to represent a positive number is as the successor of some `Nat`.
Replace the definition of `Pos` with a structure whose constructor is named `succ` that contains a `Nat`:

```lean
structure Pos where
  succ ::
  pred : Nat
```

Define instances of `Add`, `Mul`, `ToString`, and `OfNat` that allow this version of `Pos` to be used conveniently.

이 버전의 `Pos`를 편리하게 사용할 수 있도록 `Add`, `Mul`, `ToString`, `OfNat`의 instance를 정의합니다.

### 3.1.6.2. Even Numbers

Define a datatype that represents only even numbers. Define instances of `Add`, `Mul`, and `ToString` that allow it to be used conveniently.
`OfNat` requires a feature that is introduced in [the next section](../ch03/).

짝수만을 나타내는 데이터타입을 정의합니다. 이를 편리하게 사용할 수 있도록 `Add`, `Mul`, `ToString`의 instance를 정의합니다. `OfNat`은 [다음 섹션](../ch03/)에서 소개되는 기능이 필요합니다.

### 3.1.6.3. HTTP Requests

An HTTP request begins with an identification of a HTTP method, such as `GET` or `POST`, along with a URI and an HTTP version.
Define an inductive type that represents an interesting subset of the HTTP methods, and a structure that represents HTTP responses.
Responses should have a `ToString` instance that makes it possible to debug them.
Use a type class to associate different `IO` actions with each HTTP method, and write a test harness as an `IO` action that calls each method and prints the result.

HTTP 요청은 `GET` 또는 `POST`와 같은 HTTP method의 식별과 URI 및 HTTP 버전으로 시작합니다. HTTP method의 흥미로운 부분 집합을 나타내는 inductive type과 HTTP 응답을 나타내는 structure를 정의합니다. 응답은 디버깅을 가능하게 하는 `ToString` instance를 가져야 합니다. type class를 사용하여 각 HTTP method와 다른 `IO` action을 연결하고, 각 method를 호출하고 결과를 출력하는 `IO` action으로 test harness를 작성합니다.
