---
title: "3.6. 강제 변환(Coercion)"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "타입 클래스 인스턴스로 확장 가능한 암묵적 타입 변환 메커니즘"
---

# 3.6. Coercions

In mathematics, it is common to use the same symbol to stand for different aspects of some object in different contexts.
For example, if a ring is referred to in a context where a set is expected, then it is understood that the ring's underlying set is what's intended.
In programming languages, it is common to have rules to automatically translate values of one type into values of another type.
Java allows a `byte` to be automatically promoted to an `int`, and Kotlin allows a non-nullable type to be used in a context that expects a nullable version of the type.

수학에서 서로 다른 맥락에서 같은 기호를 객체의 다양한 측면을 나타내기 위해 사용하는 것이 일반적입니다.
예를 들어, 집합이 예상되는 맥락에서 환(ring)이 참조되면, 환의 기초적인 집합이 의도된 것으로 이해됩니다.
프로그래밍 언어에서는 한 타입의 값을 다른 타입의 값으로 자동으로 변환하는 규칙을 갖는 것이 일반적입니다.
Java는 `byte`를 자동으로 `int`로 승격(promote)시킬 수 있으며, Kotlin은 nullable 타입을 예상하는 맥락에서 non-nullable 타입을 사용할 수 있게 합니다.

In Lean, both purposes are served by a mechanism called *coercions*.
When Lean encounters an expression of one type in a context that expects a different type, it will attempt to coerce the expression before reporting a type error.
Unlike Java, C, and Kotlin, the coercions are extensible by defining instances of type classes.

Lean에서는 *coercion*이라는 메커니즘으로 두 가지 목적을 모두 제공합니다.
Lean이 한 타입의 식을 다른 타입을 예상하는 맥락에서 만나면, 타입 오류를 보고하기 전에 식을 강제 변환(coerce)하려고 시도합니다.
Java, C, Kotlin과는 달리, coercion은 type class의 인스턴스를 정의함으로써 확장 가능합니다.

## 3.6.2. Positive Numbers

Every positive number corresponds to a natural number.
The function `Pos.toNat` that was defined earlier converts a `Pos` to the corresponding `Nat`:

모든 양수는 자연수에 대응됩니다.
앞서 정의된 함수 `Pos.toNat`은 `Pos`를 대응하는 `Nat`로 변환합니다:

```lean
def Pos.toNat : Pos → Nat
  | Pos.one => 1
  | Pos.succ n => n.toNat + 1
```

The function `List.drop`, with type `{α : Type} → Nat → List α → List α`, removes a prefix of a list.
Applying `List.drop` to a `Pos`, however, leads to a type error:

타입이 `{α : Type} → Nat → List α → List α`인 함수 `List.drop`은 리스트의 접두사를 제거합니다.
그러나 `List.drop`을 `Pos`에 적용하면 타입 오류가 발생합니다:

```lean
[1, 2, 3, 4].drop (2 : Pos)
```

```
Application type mismatch: The argument
  2
has type
  Pos
but is expected to have type
  Nat
in the application
  List.drop 2
```

Because the author of `List.drop` did not make it a method of a type class, it can't be overridden by defining a new instance.

`List.drop`의 작성자가 이를 type class의 메서드로 만들지 않았으므로, 새로운 인스턴스를 정의하여 오버라이드할 수 없습니다.

The type class `Coe` describes overloaded ways of coercing from one type to another:

Type class `Coe`는 한 타입에서 다른 타입으로 강제 변환하는 오버로드된 방법들을 설명합니다:

```lean
class Coe (α : Type) (β : Type) where
  coe : α → β
```

An instance of `Coe Pos Nat` is enough to allow the prior code to work:

`Coe Pos Nat`의 인스턴스 하나로 앞의 코드가 작동하도록 충분합니다:

```lean
instance : Coe Pos Nat where
  coe x := x.toNat
```

```lean
#eval [1, 2, 3, 4].drop (2 : Pos)
```

```
[3, 4]
```

Using `#check` shows the result of the instance search that was used behind the scenes:

`#check`를 사용하면 백그라운드에서 사용된 인스턴스 검색의 결과를 보여줍니다:

```lean
#check [1, 2, 3, 4].drop (2 : Pos)
```

```
List.drop (Pos.toNat 2) [1, 2, 3, 4] : List Nat
```

## 3.6.3. Chaining Coercions

When searching for coercions, Lean will attempt to assemble a coercion out of a chain of smaller coercions.
For example, there is already a coercion from `Nat` to `Int`.
Because of that instance, combined with the `Coe Pos Nat` instance, the following code is accepted:

Coercion을 검색할 때, Lean은 더 작은 coercion들의 체인으로부터 coercion을 조립하려고 시도합니다.
예를 들어, `Nat`에서 `Int`로의 coercion이 이미 존재합니다.
그 인스턴스가 `Coe Pos Nat` 인스턴스와 결합되어, 다음 코드가 수락됩니다:

```lean
def oneInt : Int := Pos.one
```

This definition uses two coercions: from `Pos` to `Nat`, and then from `Nat` to `Int`.

이 정의는 두 개의 coercion을 사용합니다: `Pos`에서 `Nat`으로, 그 다음 `Nat`에서 `Int`로.

The Lean compiler does not get stuck in the presence of circular coercions.
For example, even if two types `A` and `B` can be coerced to one another, their mutual coercions can be used to find a path:

Lean 컴파일러는 순환 coercion이 있어도 멈추지 않습니다.
예를 들어, 두 타입 `A`와 `B`가 서로 강제 변환될 수 있더라도, 그들의 상호 coercion이 경로를 찾는 데 사용될 수 있습니다:

```lean
inductive A where
  | a
inductive B where
  | b
instance : Coe A B where
  coe _ := B.b
instance : Coe B A where
  coe _ := A.a
instance : Coe Unit A where
  coe _ := A.a
def coercedToB : B := ()
```

Remember: the double parentheses `()` is short for the constructor `Unit.unit`.
After deriving a `Repr B` instance with `deriving instance Repr for B`,

기억하세요: 이중 괄호 `()`는 생성자 `Unit.unit`의 축약형입니다.
`deriving instance Repr for B`로 `Repr B` 인스턴스를 유도한 후,

```lean
#eval coercedToB
```

results in:

`Option` 타입은 C#과 Kotlin의 nullable 타입과 유사하게 사용될 수 있습니다: `none` 생성자는 값의 부재를 나타냅니다.
Lean 표준 라이브러리는 모든 타입 `α`에서 `Option α`로의 coercion을 정의하며, 이는 값을 `some`으로 감싸줍니다.
이는 option 타입을 nullable 타입과 더욱 유사한 방식으로 사용할 수 있게 하며, `some`을 생략할 수 있기 때문입니다.
예를 들어, 리스트의 마지막 항목을 찾는 함수 `List.last?`는 반환 값 `x` 주변에 `some` 없이 작성될 수 있습니다:

```
B.b
```

```lean
def List.last? : List α → Option α
  | [] => none
  | [x] => x
  | _ :: x :: xs => last? (x :: xs)
```

The `Option` type can be used similarly to nullable types in C# and Kotlin: the `none` constructor represents the absence of a value.
The Lean standard library defines a coercion from any type `α` to `Option α` that wraps the value in `some`.
This allows option types to be used in a manner even more similar to nullable types, because `some` can be omitted.
For instance, the function `List.last?` that finds the last entry in a list can be written without a `some` around the return value `x`:

Instance search finds the coercion, and inserts a call to `coe`, which wraps the argument in `some`.
These coercions can be chained, so that nested uses of `Option` don't require nested `some` constructors:

인스턴스 검색이 coercion을 찾고, `coe` 호출을 삽입하며, 이는 인자를 `some`으로 감싸줍니다.
이러한 coercion들은 체인될 수 있어서, `Option`의 중첩된 사용이 중첩된 `some` 생성자를 필요로 하지 않습니다:

```lean
def perhapsPerhapsPerhaps : Option (Option (Option String)) :=
  "Please don't tell me"
```

Coercions are only activated automatically when Lean encounters a mismatch between an inferred type and a type that is imposed from the rest of the program.
In cases with other errors, coercions are not activated.
For example, if the error is that an instance is missing, coercions will not be used:

Coercion은 Lean이 추론된 타입과 프로그램의 나머지 부분에서 강제된 타입 간의 불일치를 만날 때만 자동으로 활성화됩니다.
다른 오류가 있는 경우, coercion은 활성화되지 않습니다.
예를 들어, 오류가 인스턴스 누락인 경우, coercion은 사용되지 않습니다:

```lean
def perhapsPerhapsPerhapsNat : Option (Option (Option Nat)) :=
  392
```

```
failed to synthesize
  OfNat (Option (Option (Option Nat))) 392
numerals are polymorphic in Lean, but the numeral `392` cannot be used in a context where the expected type is
  Option (Option (Option Nat))
due to the absence of the instance above

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

This can be worked around by manually indicating the desired type to be used for `OfNat`:

이는 `OfNat`에 사용할 원하는 타입을 수동으로 지정함으로써 해결할 수 있습니다:

```lean
def perhapsPerhapsPerhapsNat : Option (Option (Option Nat)) :=
  (392 : Nat)
```

Additionally, coercions can be manually inserted using an up arrow:

또한, coercion은 위쪽 화살표를 사용하여 수동으로 삽입할 수 있습니다:

```lean
def perhapsPerhapsPerhapsNat : Option (Option (Option Nat)) :=
  ↑(392 : Nat)
```

In some cases, this can be used to ensure that Lean finds the right instances.
It can also make the programmer's intentions more clear.

어떤 경우에는, 이를 사용하여 Lean이 올바른 인스턴스를 찾도록 보장할 수 있습니다.
또한 프로그래머의 의도를 더욱 명확하게 할 수 있습니다.

## 3.6.4. Non-Empty Lists and Dependent Coercions

An instance of `Coe α β` makes sense when the type `β` has a value that can represent each value from the type `α`.
Coercing from `Nat` to `Int` makes sense, because the type `Int` contains all the natural numbers, but a coercion from `Int` to `Nat` is a poor idea because `Nat` does not contain the negative numbers.
Similarly, a coercion from non-empty lists to ordinary lists makes sense because the `List` type can represent every non-empty list:

`Coe α β`의 인스턴스는 타입 `β`가 타입 `α`의 각 값을 나타낼 수 있는 값을 가질 때 의미가 있습니다.
`Nat`에서 `Int`로의 coercion은 의미가 있습니다. 왜냐하면 타입 `Int`가 모든 자연수를 포함하기 때문입니다. 하지만 `Int`에서 `Nat`로의 coercion은 좋지 않습니다. `Nat`가 음수를 포함하지 않기 때문입니다.
유사하게, 빈 리스트가 아닌 리스트에서 일반 리스트로의 coercion은 의미가 있습니다. `List` 타입이 모든 빈 리스트가 아닌 리스트를 나타낼 수 있기 때문입니다:

```lean
instance : Coe (NonEmptyList α) (List α) where
  coe
    | { head := x, tail := xs } => x :: xs
```

This allows non-empty lists to be used with the entire `List` API.

이는 빈 리스트가 아닌 리스트가 전체 `List` API와 함께 사용될 수 있게 합니다.

On the other hand, it is impossible to write an instance of `Coe (List α) (NonEmptyList α)`, because there's no non-empty list that can represent the empty list.
This limitation can be worked around by using another version of coercions, which are called *dependent coercions*.
Dependent coercions can be used when the ability to coerce from one type to another depends on which particular value is being coerced.
Just as the `OfNat` type class takes the particular `Nat` being overloaded as a parameter, dependent coercion takes the value being coerced as a parameter:

한편, `Coe (List α) (NonEmptyList α)`의 인스턴스를 작성하는 것은 불가능합니다. 빈 리스트를 나타낼 수 있는 빈 리스트가 아닌 리스트가 없기 때문입니다.
이러한 제한은 *dependent coercion*이라고 불리는 coercion의 다른 버전을 사용하여 해결할 수 있습니다.
Dependent coercion은 한 타입에서 다른 타입으로의 coercion 능력이 강제 변환되는 특정 값에 따라 달라질 때 사용될 수 있습니다.
`OfNat` type class가 오버로드되는 특정 `Nat`을 매개변수로 취하는 것처럼, dependent coercion은 강제 변환되는 값을 매개변수로 취합니다:

```lean
class CoeDep (α : Type) (x : α) (β : Type) where
  coe : β
```

This is a chance to select only certain values, either by imposing further type class constraints on the value or by writing certain constructors directly.
For example, any `List` that is not actually empty can be coerced to a `NonEmptyList`:

이는 값에 더 이상의 type class 제약을 부과하거나 특정 생성자를 직접 작성하여 특정 값만 선택할 수 있는 기회입니다.
예를 들어, 실제로 비어있지 않은 모든 `List`는 `NonEmptyList`로 강제 변환될 수 있습니다:

```lean
instance : CoeDep (List α) (x :: xs) (NonEmptyList α) where
  coe := { head := x, tail := xs }
```

## 3.6.5. Coercing to Types

In mathematics, it is common to have a concept that consists of a set equipped with additional structure.
For example, a monoid is some set `S`, an element `s` of `S`, and an associative binary operator on `S`, such that `s` is neutral on the left and right of the operator.
`S` is referred to as the “carrier set” of the monoid.
The natural numbers with zero and addition form a monoid, because addition is associative and adding zero to any number is the identity.
Similarly, the natural numbers with one and multiplication also form a monoid.
Monoids are also widely used in functional programming: lists, the empty list, and the append operator form a monoid, as do strings, the empty string, and string append:

수학에서는 추가적인 구조를 갖춘 집합으로 구성된 개념을 갖는 것이 일반적입니다.
예를 들어, monoid는 어떤 집합 `S`, `S`의 원소 `s`, 그리고 `S` 위의 결합 이항 연산자로 이루어져 있으며, `s`는 연산자의 좌측과 우측에서 중립적입니다.
`S`는 monoid의 “carrier set”이라고 합니다.
0과 덧셈을 갖는 자연수는 monoid를 형성합니다. 덧셈이 결합적이고 어떤 수에 0을 더하는 것이 항등원이기 때문입니다.
유사하게, 1과 곱셈을 갖는 자연수도 monoid를 형성합니다.
Monoid는 함수형 프로그래밍에서도 광범위하게 사용됩니다: 리스트, 빈 리스트, append 연산자는 monoid를 형성하며, 문자열, 빈 문자열, 문자열 append도 마찬가지입니다:

```lean
structure Monoid where
  Carrier : Type
  neutral : Carrier
  op : Carrier → Carrier → Carrier
def natMulMonoid : Monoid :=
  { Carrier := Nat, neutral := 1, op := (· * ·) }
def natAddMonoid : Monoid :=
  { Carrier := Nat, neutral := 0, op := (· + ·) }
def stringMonoid : Monoid :=
  { Carrier := String, neutral := "", op := String.append }
def listMonoid (α : Type) : Monoid :=
  { Carrier := List α, neutral := [], op := List.append }
```

Given a monoid, it is possible to write the `foldMap` function that, in a single pass, transforms the entries in a list into a monoid's carrier set and then combines them using the monoid's operator.
Because monoids have a neutral element, there is a natural result to return when the list is empty, and because the operator is associative, clients of the function don't have to care whether the recursive function combines elements from left to right or from right to left.

Monoid가 주어지면, 한 번의 패스에서 리스트의 항목들을 monoid의 carrier set으로 변환한 다음 monoid의 연산자를 사용하여 결합하는 `foldMap` 함수를 작성할 수 있습니다.
Monoid는 중립 원소를 가지기 때문에, 리스트가 비어있을 때 반환할 자연스러운 결과가 있으며, 연산자가 결합적이기 때문에 함수의 사용자는 재귀 함수가 좌에서 우로 결합하는지 우에서 좌로 결합하는지 신경 쓸 필요가 없습니다.

```lean
def foldMap (M : Monoid) (f : α → M.Carrier) (xs : List α) : M.Carrier :=
  let rec go (soFar : M.Carrier) : List α → M.Carrier
    | [] => soFar
    | y :: ys => go (M.op soFar (f y)) ys
  go M.neutral xs
```

Even though a monoid consists of three separate pieces of information, it is common to just refer to the monoid's name in order to refer to its set.
Instead of saying “Let A be a monoid and let *x* and *y* be elements of its carrier set”, it is common to say “Let *A* be a monoid and let *x* and *y* be elements of *A*”.
This practice can be encoded in Lean by defining a new kind of coercion, from the monoid to its carrier set.

Monoid가 세 개의 별도 정보 조각으로 구성되어 있음에도 불구하고, monoid의 이름만 참조하여 그 집합을 참조하는 것이 일반적입니다.
“A를 monoid라고 하고 *x*와 *y*를 그 carrier set의 원소라고 하자”라고 말하는 대신에 “*A*를 monoid라고 하고 *x*와 *y*를 *A*의 원소라고 하자”라고 말하는 것이 일반적입니다.
이러한 관행은 monoid에서 그 carrier set으로의 coercion의 새로운 종류를 정의함으로써 Lean에서 인코딩될 수 있습니다.

The `CoeSort` class is just like the `Coe` class, with the exception that the target of the coercion must be a *sort*, namely `Type` or `Prop`.
The term *sort* in Lean refers to these types that classify other types—`Type` classifies types that themselves classify data, and `Prop` classifies propositions that themselves classify evidence of their truth.
Just as `Coe` is checked when a type mismatch occurs, `CoeSort` is used when something other than a sort is provided in a context where a sort would be expected.

`CoeSort` 클래스는 coercion의 대상이 *sort*, 즉 `Type` 또는 `Prop`이어야 한다는 예외를 제외하고는 `Coe` 클래스와 같습니다.
Lean의 *sort* 용어는 다른 타입을 분류하는 타입들을 의미합니다. `Type`은 자신이 데이터를 분류하는 타입을 분류하고, `Prop`은 자신이 진실의 증거를 분류하는 명제를 분류합니다.
`Coe`가 타입 불일치가 발생할 때 검사되는 것처럼, `CoeSort`는 sort가 예상되는 맥락에서 sort가 아닌 다른 것이 제공될 때 사용됩니다.

The coercion from a monoid into its carrier set extracts the carrier:

Monoid에서 그 carrier set으로의 coercion은 carrier를 추출합니다:

```lean
instance : CoeSort Monoid Type where
  coe m := m.Carrier
```

With this coercion, the type signatures become less bureaucratic:

이 coercion으로, 타입 시그니처는 덜 복잡해집니다:

```lean
def foldMap (M : Monoid) (f : α → M) (xs : List α) : M :=
  let rec go (soFar : M) : List α → M
    | [] => soFar
    | y :: ys => go (M.op soFar (f y)) ys
  go M.neutral xs
```

Another useful example of `CoeSort` is used to bridge the gap between `Bool` and `Prop`.
As discussed in [the section on ordering and equality](../ch03/), Lean's `if` expression expects the condition to be a decidable proposition rather than a `Bool`.
Programs typically need to be able to branch based on Boolean values, however.
Rather than have two kinds of `if` expression, the Lean standard library defines a coercion from `Bool` to the proposition that the `Bool` in question is equal to `true`:

`CoeSort`의 또 다른 유용한 예는 `Bool`과 `Prop` 사이의 간격을 메우기 위해 사용됩니다.
[순서 및 동등성에 관한 섹션](../ch03/)에서 논의된 바와 같이, Lean의 `if` 식은 조건이 `Bool`이 아닌 결정 가능한 명제일 것을 기대합니다.
그러나 프로그램은 일반적으로 부울 값을 기반으로 분기할 수 있어야 합니다.
두 종류의 `if` 식을 갖는 대신에, Lean 표준 라이브러리는 `Bool`에서 해당 `Bool`이 `true`와 같다는 명제로의 coercion을 정의합니다:

```lean
instance : CoeSort Bool Prop where
  coe b := b = true
```

In this case, the sort in question is `Prop` rather than `Type`.

이 경우, 해당 sort는 `Type`이 아닌 `Prop`입니다.

## 3.6.6. Coercing to Functions

Many datatypes that occur regularly in programming consist of a function along with some extra information about it.
For example, a function might be accompanied by a name to show in logs or by some configuration data.
Additionally, putting a type in a field of a structure, similarly to the `Monoid` example, can make sense in contexts where there is more than one way to implement an operation and more manual control is needed than type classes would allow.
For example, the specific details of values emitted by a JSON serializer may be important because another application expects a particular format.
Sometimes, the function itself may be derivable from just the configuration data.

프로그래밍에서 정기적으로 발생하는 많은 데이터타입은 함수와 그에 대한 추가 정보로 구성됩니다.
예를 들어, 함수는 로그에 표시할 이름이나 일부 구성 데이터를 동반할 수 있습니다.
또한, `Monoid` 예제와 유사하게 구조의 필드에 타입을 넣는 것은 연산을 구현하는 여러 방법이 있고 type class가 허용하는 것보다 더 많은 수동 제어가 필요한 맥락에서 의미가 있을 수 있습니다.
예를 들어, JSON serializer에서 방출된 값의 특정 세부 사항은 다른 응용 프로그램이 특정 형식을 기대하기 때문에 중요할 수 있습니다.
때때로 함수 자체는 구성 데이터만으로부터 유도될 수 있습니다.

A type class called `CoeFun` can transform values from non-function types to function types.
`CoeFun` has two parameters: the first is the type whose values should be transformed into functions, and the second is an output parameter that determines exactly which function type is being targeted.

`CoeFun`이라는 type class는 non-function 타입의 값을 함수 타입으로 변환할 수 있습니다.
`CoeFun`은 두 개의 매개변수를 가집니다: 첫 번째는 값이 함수로 변환되어야 하는 타입이고, 두 번째는 정확히 어떤 함수 타입을 대상으로 하는지 결정하는 출력 매개변수입니다.

```lean
class CoeFun (α : Type) (makeFunctionType : outParam (α → Type)) where
  coe : (x : α) → makeFunctionType x
```

The second parameter is itself a function that computes a type.
In Lean, types are first-class and can be passed to functions or returned from them, just like anything else.

두 번째 매개변수는 타입을 계산하는 함수 자체입니다.
Lean에서는 타입이 first-class이며, 다른 어떤 것처럼 함수에 전달되거나 반환될 수 있습니다.

For example, a function that adds a constant amount to its argument can be represented as a wrapper around the amount to add, rather than by defining an actual function:

예를 들어, 인자에 일정한 양을 더하는 함수는 실제 함수를 정의하는 것이 아니라 추가할 양을 둘러싼 래퍼로 표현될 수 있습니다:

```lean
structure Adder where
  howMuch : Nat
```

A function that adds five to its argument has a `5` in the `howMuch` field:

인자에 5를 더하는 함수는 `howMuch` 필드에 `5`를 가지고 있습니다:

```lean
def add5 : Adder := ⟨5⟩
```

This `Adder` type is not a function, and applying it to an argument results in an error:

이 `Adder` 타입은 함수가 아니며, 인자에 적용하면 오류가 발생합니다:

```lean
#eval add5 3
```

```
Function expected at
  add5
but this term has type
  Adder

Note: Expected a function because this term is being applied to the argument
  3
```

Defining a `CoeFun` instance causes Lean to transform the adder into a function with type `Nat → Nat`:

`CoeFun` 인스턴스를 정의하면 Lean은 adder를 `Nat → Nat` 타입의 함수로 변환합니다:

```lean
instance : CoeFun Adder (fun _ => Nat → Nat) where
  coe a := (· + a.howMuch)
```

```lean
#eval add5 3
```

```
8
```

Because all `Adder`s should be transformed into `Nat → Nat` functions, the argument to `CoeFun`'s second parameter was ignored.

모든 `Adder`가 `Nat → Nat` 함수로 변환되어야 하기 때문에, `CoeFun`의 두 번째 매개변수에 대한 인자가 무시되었습니다.

When the value itself is needed to determine the right function type, then `CoeFun`'s second parameter is no longer ignored.
For example, given the following representation of JSON values:

값 자체가 올바른 함수 타입을 결정하는 데 필요할 때, `CoeFun`의 두 번째 매개변수는 더 이상 무시되지 않습니다.
예를 들어, JSON 값의 다음 표현이 주어진 경우:

```lean
inductive JSON where
  | true : JSON
  | false : JSON
  | null : JSON
  | string : String → JSON
  | number : Float → JSON
  | object : List (String × JSON) → JSON
  | array : List JSON → JSON
```

a JSON serializer is a structure that tracks the type it knows how to serialize along with the serialization code itself:

JSON serializer는 serialize하는 방법을 알고 있는 타입을 serialization 코드 자체와 함께 추적하는 구조입니다:

```lean
structure Serializer where
  Contents : Type
  serialize : Contents → JSON
```

A serializer for strings need only wrap the provided string in the `JSON.string` constructor:

문자열용 serializer는 제공된 문자열을 `JSON.string` 생성자로 감싸기만 하면 됩니다:

```lean
def Str : Serializer :=
  { Contents := String,
    serialize := JSON.string
  }
```

Viewing JSON serializers as functions that serialize their argument requires extracting the inner type of serializable data:

JSON serializer를 인자를 serialize하는 함수로 보기 위해서는 serialize 가능한 데이터의 내부 타입을 추출해야 합니다:

```lean
instance : CoeFun Serializer (fun s => s.Contents → JSON) where
  coe s := s.serialize
```

Given this instance, a serializer can be applied directly to an argument:

이 인스턴스가 주어지면, serializer를 인자에 직접 적용할 수 있습니다:

```lean
def buildResponse (title : String) (R : Serializer)
    (record : R.Contents) : JSON :=
  JSON.object [
    ("title", JSON.string title),
    ("status", JSON.number 200),
    ("record", R record)
  ]
```

The serializer can be passed directly to `buildResponse`:

Serializer는 `buildResponse`에 직접 전달될 수 있습니다:

```lean
#eval buildResponse "Functional Programming in Lean" Str "Programming is fun!"
```

```
JSON.object
  [("title", JSON.string "Functional Programming in Lean"),
   ("status", JSON.number 200.000000),
   ("record", JSON.string "Programming is fun!")]
```

### 3.6.6.1. Aside: JSON as a String

It can be a bit difficult to understand JSON when encoded as Lean objects.
To help make sure that the serialized response was what was expected, it can be convenient to write a simple converter from `JSON` to `String`.
The first step is to simplify the display of numbers.
`JSON` doesn't distinguish between integers and floating point numbers, and the type `Float` is used to represent both.
In Lean, `Float.toString` includes a number of trailing zeros:

JSON이 Lean 객체로 인코딩될 때 이해하기가 조금 어려울 수 있습니다.
직렬화된 응답이 예상대로인지 확인하는 데 도움이 되도록, `JSON`에서 `String`으로의 간단한 변환기를 작성하는 것이 편할 수 있습니다.
첫 번째 단계는 숫자의 표시를 단순화하는 것입니다.
`JSON`은 정수와 부동 소수점 숫자를 구분하지 않으며, `Float` 타입은 둘 다를 나타내기 위해 사용됩니다.
Lean에서 `Float.toString`은 여러 개의 후행 영(trailing zero)을 포함합니다:

```lean
#eval (5 : Float).toString
```

```
"5.000000"
```

The solution is to write a little function that cleans up the presentation by dropping all trailing zeros, followed by a trailing decimal point:

해결책은 모든 후행 영을 삭제하고 후행 소수점을 제거하여 표시를 정리하는 작은 함수를 작성하는 것입니다:

```lean
def dropDecimals (numString : String) : String :=
  if numString.contains '.' then
    let noTrailingZeros := numString.dropRightWhile (· == '0')
    noTrailingZeros.dropRightWhile (· == '.')
  else numString
```

With this definition, `dropDecimals (5 : Float).toString` yields `5`, and `dropDecimals (5.2 : Float).toString` yields `5.2`.

이 정의를 사용하면, `dropDecimals (5 : Float).toString`은 `5`를 생성하고, `dropDecimals (5.2 : Float).toString`은 `5.2`를 생성합니다.

The next step is to define a helper function to append a list of strings with a separator in between them:

다음 단계는 그들 사이에 구분 기호가 있는 문자열 목록을 추가하는 도우미 함수를 정의하는 것입니다:

```lean
def String.separate (sep : String) (strings : List String) : String :=
  match strings with
  | [] => ""
  | x :: xs => String.join (x :: xs.map (sep ++ ·))
```

This function is useful to account for comma-separated elements in JSON arrays and objects.
`", ".separate ["1", "2"]` yields `"1, 2"`, `", ".separate ["1"]` yields `"1"`, and `", ".separate []` yields `""`.
In the Lean standard library, this function is called `String.intercalate`.

이 함수는 JSON 배열 및 객체의 쉼표로 구분된 요소를 처리하는 데 유용합니다.
`", ".separate ["1", "2"]`는 `"1, 2"`를 생성하고, `", ".separate ["1"]`은 `"1"`을 생성하며, `", ".separate []`는 `""`를 생성합니다.
Lean 표준 라이브러리에서 이 함수는 `String.intercalate`라고 불립니다.

Finally, a string escaping procedure is needed for JSON strings, so that the Lean string containing `"Hello!"` can be output as `"\"Hello!\""`.
Fortunately, the Lean compiler contains an internal function for escaping JSON strings already, called `Lean.Json.escape`.
To access this function, add `import Lean` to the beginning of your file.

마지막으로, JSON 문자열에 대한 문자열 이스케이프 절차가 필요하므로, `"Hello!"`를 포함하는 Lean 문자열을 `"\"Hello!\""`로 출력할 수 있습니다.
다행히 Lean 컴파일러는 `Lean.Json.escape`라는 JSON 문자열을 이스케이프하기 위한 내부 함수를 이미 포함하고 있습니다.
이 함수에 액세스하려면 파일의 시작 부분에 `import Lean`을 추가합니다.

The function that emits a string from a `JSON` value is declared `partial` because Lean cannot see that it terminates.
This is because recursive calls to `asString` occur in functions that are being applied by `List.map`, and this pattern of recursion is complicated enough that Lean cannot see that the recursive calls are actually being performed on smaller values.
In an application that just needs to produce JSON strings and doesn't need to mathematically reason about the process, having the function be `partial` is not likely to cause problems.

`JSON` 값에서 문자열을 방출하는 함수는 Lean이 종료를 볼 수 없기 때문에 `partial`로 선언됩니다.
이는 `asString`에 대한 재귀 호출이 `List.map`으로 적용되는 함수에서 발생하고, 이러한 재귀 패턴이 복잡하여 Lean이 재귀 호출이 실제로 더 작은 값에서 수행되는 것을 볼 수 없기 때문입니다.
JSON 문자열을 생성하기만 하면 되고 프로세스에 대해 수학적으로 추론할 필요가 없는 응용 프로그램에서는 함수가 `partial`인 것이 문제를 일으킬 가능성이 낮습니다.

```lean
partial def JSON.asString (val : JSON) : String :=
  match val with
  | true => "true"
  | false => "false"
  | null => "null"
  | string s => "\"" ++ Lean.Json.escape s ++ "\""
  | number n => dropDecimals n.toString
  | object members =>
    let memberToString mem :=
      "\"" ++ Lean.Json.escape mem.fst ++ "\": " ++ asString mem.snd
    "{" ++ ", ".separate (members.map memberToString) ++ "}"
  | array elements =>
    "[" ++ ", ".separate (elements.map asString) ++ "]"
```

With this definition, the output of serialization is easier to read:

이 정의를 사용하면 serialization의 출력을 더 쉽게 읽을 수 있습니다:

```lean
#eval (buildResponse "Functional Programming in Lean" Str "Programming is fun!").asString
```

```
"{\"title\": \"Functional Programming in Lean\", \"status\": 200, \"record\": \"Programming is fun!\"}"
```

## 3.6.7. Messages You May Meet

Natural number literals are overloaded with the `OfNat` type class.
Because coercions fire in cases where types don't match, rather than in cases of missing instances, a missing `OfNat` instance for a type does not cause a coercion from `Nat` to be applied:

자연수 리터럴은 `OfNat` type class로 오버로드됩니다.
Coercion은 인스턴스가 누락된 경우가 아닌 타입이 일치하지 않는 경우에 발생하기 때문에, 타입에 대한 누락된 `OfNat` 인스턴스는 `Nat`에서의 coercion이 적용되게 하지 않습니다:

```lean
def perhapsPerhapsPerhapsNat : Option (Option (Option Nat)) :=
  392
```

```
failed to synthesize
  OfNat (Option (Option (Option Nat))) 392
numerals are polymorphic in Lean, but the numeral `392` cannot be used in a context where the expected type is
  Option (Option (Option Nat))
due to the absence of the instance above

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

## 3.6.8. Design Considerations

Coercions are a powerful tool that should be used responsibly.
On the one hand, they can allow an API to naturally follow the everyday rules of the domain being modeled.
This can be the difference between a bureaucratic mess of manual conversion functions and a clear program.
As Abelson and Sussman wrote in the preface to *Structure and Interpretation of Computer Programs* (MIT Press, 1996),

Coercion은 책임감 있게 사용해야 하는 강력한 도구입니다.
한편으로는 API가 모델링 중인 도메인의 일상적인 규칙을 자연스럽게 따르도록 할 수 있습니다.
이는 수동 변환 함수의 복잡한 혼란과 명확한 프로그램 사이의 차이가 될 수 있습니다.
Abelson과 Sussman이 *Structure and Interpretation of Computer Programs* (MIT Press, 1996)의 서문에서 작성했듯이,

> Programs must be written for people to read, and only incidentally for machines to execute.

Coercion을 현명하게 사용하면 도메인 전문가와의 의사소통의 기초가 될 수 있는 읽기 쉬운 코드를 달성하기 위한 귀중한 수단입니다.
그러나 coercion에 크게 의존하는 API는 여러 중요한 제한 사항이 있습니다.
자신의 라이브러리에서 coercion을 사용하기 전에 이러한 제한 사항을 신중하게 생각해보세요.

Coercions, used wisely, are a valuable means of achieving readable code that can serve as the basis for communication with domain experts.
APIs that rely heavily on coercions have a number of important limitations, however.
Think carefully about these limitations before using coercions in your own libraries.

First off, coercions are only applied in contexts where enough type information is available for Lean to know all of the types involved, because there are no output parameters in the coercion type classes. This means that a return type annotation on a function can be the difference between a type error and a successfully applied coercion.
For example, the coercion from non-empty lists to lists makes the following program work:

첫째, coercion은 coercion type class에 출력 매개변수가 없기 때문에 Lean이 관련된 모든 타입을 알기에 충분한 타입 정보가 있는 맥락에서만 적용됩니다. 즉, 함수의 반환 타입 주석이 타입 오류와 성공적으로 적용된 coercion 사이의 차이를 만들 수 있습니다.
예를 들어, 빈 리스트가 아닌 리스트에서 리스트로의 coercion은 다음 프로그램을 작동하게 합니다:

```lean
def lastSpider : Option String :=
  List.getLast? idahoSpiders
```

On the other hand, if the type annotation is omitted, then the result type is unknown, so Lean is unable to find the coercion:

반면에 타입 주석을 생략하면 결과 타입이 알려지지 않아 Lean이 coercion을 찾을 수 없습니다:

```lean
def lastSpider :=
  List.getLast? idahoSpiders
```

```
Application type mismatch: The argument
  idahoSpiders
has type
  NonEmptyList String
but is expected to have type
  List ?m.3
in the application
  List.getLast? idahoSpiders
```

More generally, when a coercion is not applied for some reason, the user receives the original type error, which can make it difficult to debug chains of coercions.

더 일반적으로, 어떤 이유로든 coercion이 적용되지 않으면 사용자는 원래의 타입 오류를 받으며, 이는 coercion 체인을 디버깅하기 어렵게 만들 수 있습니다.

Finally, coercions are not applied in the context of field accessor notation.
This means that there is still an important difference between expressions that need to be coerced and those that don't, and this difference is visible to users of your API.

마지막으로, coercion은 필드 접근자 표기법의 맥락에서 적용되지 않습니다.
이는 강제 변환이 필요한 식과 그렇지 않은 식 사이에 여전히 중요한 차이가 있으며, 이러한 차이는 API 사용자에게 보입니다.
