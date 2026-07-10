---
title: "7.2. 유니버스 디자인 패턴 (The Universe Design Pattern)"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "유니버스 디자인 패턴 (The Universe Design Pattern)"
---

# 7.2. The Universe Design Pattern

In Lean, types such as `Type`, `Type 3`, and `Prop` that classify other types are known as universes.
However, the term *universe* is also used for a design pattern in which a datatype is used to represent a subset of Lean's types, and a function converts the datatype's constructors into actual types.
The values of this datatype are called *codes* for their types.

Lean에서 `Type`, `Type 3`, `Prop` 같은 다른 타입을 분류하는 타입을 universes라고 합니다.
그러나 *universe*라는 용어는 또한 datatype이 Lean의 타입의 부분집합을 나타내는 데 사용되고, 함수가 datatype의 생성자를 실제 타입으로 변환하는 디자인 패턴을 위해 사용됩니다.
이 datatype의 값을 해당 타입의 *codes*라고 합니다.

Just like Lean's built-in universes, the universes implemented with this pattern are types that describe some collection of available types, even though the mechanism by which it is done is different.
In Lean, there are types such as `Type`, `Type 3`, and `Prop` that directly describe other types.
This arrangement is referred to as *universes à la Russell*.
The user-defined universes described in this section represent all of their types as *data*, and include an explicit function to interpret these codes into actual honest-to-goodness types.
This arrangement is referred to as *universes à la Tarski*.
While languages such as Lean that are based on dependent type theory almost always use Russell-style universes, Tarski-style universes are a useful pattern for defining APIs in these languages.

Lean의 내장 universes과 마찬가지로, 이 패턴으로 구현된 universes는 사용 가능한 타입의 모음을 설명하는 타입입니다. 비록 방법은 다르지만 말입니다.
Lean에서는 `Type`, `Type 3`, `Prop` 같은 다른 타입을 직접 설명하는 타입이 있습니다.
이 배열을 *universes à la Russell*이라고 합니다.
이 섹션에서 설명하는 사용자 정의 universes는 모든 타입을 *data*로 표현하고, 이러한 codes를 실제 타입으로 해석하는 명시적 함수를 포함합니다.
이 배열을 *universes à la Tarski*라고 합니다.
Lean 같은 dependent type theory에 기반한 언어는 거의 항상 Russell 스타일의 universes을 사용하지만, Tarski 스타일의 universes은 이러한 언어에서 APIs를 정의하기 위한 유용한 패턴입니다.

Defining a custom universe makes it possible to carve out a closed collection of types that can be used with an API.
Because the collection of types is closed, recursion over the codes allows programs to work for *any* type in the universe.
One example of a custom universe has the codes `nat`, standing for `Nat`, and `bool`, standing for `Bool`:

커스텀 universe를 정의하면 API와 함께 사용할 수 있는 닫힌 타입 모음을 만들 수 있습니다.
타입 모음이 닫혀 있기 때문에, codes에 대한 재귀는 프로그램이 universe의 *any* 타입에 대해 작동하도록 합니다.
커스텀 universe의 한 예는 `Nat`을 나타내는 `nat` 및 `Bool`을 나타내는 `bool` codes를 가집니다:

```lean
inductive NatOrBool where
  | nat | bool
abbrev NatOrBool.asType (code : NatOrBool) : Type :=
  match code with
  | .nat => Nat
  | .bool => Bool
```

Pattern matching on a code allows the type to be refined, just as pattern matching on the constructors of `Vect` allows the expected length to be refined.
For instance, a program that deserializes the types in this universe from a string can be written as follows:

Code에 대한 패턴 매칭은 `Vect`의 생성자에 대한 패턴 매칭이 예상 길이를 refine하는 것처럼 타입을 refine할 수 있게 합니다.
예를 들어, 이 universe의 타입을 문자열에서 역직렬화하는 프로그램은 다음과 같이 작성할 수 있습니다:

```lean
def decode (t : NatOrBool) (input : String) : Option t.asType :=
  match t with
  | .nat => input.toNat?
  | .bool =>
    match input with
    | "true" => some true
    | "false" => some false
    | _ => none
```

Dependent pattern matching on `t` allows the expected result type `t.asType` to be respectively refined to `NatOrBool.nat.asType` and `NatOrBool.bool.asType`, and these compute to the actual types `Nat` and `Bool`.

`t`에 대한 dependent pattern matching은 예상 결과 타입 `t.asType`이 각각 `NatOrBool.nat.asType`과 `NatOrBool.bool.asType`으로 refine되도록 하며, 이들은 실제 타입 `Nat`과 `Bool`로 계산됩니다.

Like any other data, codes may be recursive.
The type `NestedPairs` codes for any possible nesting of the pair and natural number types:

다른 데이터처럼, codes도 재귀적일 수 있습니다.
타입 `NestedPairs`는 쌍과 자연수 타입의 모든 가능한 중첩을 위한 codes입니다:

```lean
inductive NestedPairs where
  | nat : NestedPairs
  | pair : NestedPairs → NestedPairs → NestedPairs
abbrev NestedPairs.asType : NestedPairs → Type
  | .nat => Nat
  | .pair t1 t2 => asType t1 × asType t2
```

In this case, the interpretation function `NestedPairs.asType` is recursive.
This means that recursion over codes is required in order to implement `BEq` for the universe:

이 경우, 해석 함수 `NestedPairs.asType`은 재귀적입니다.
이는 universe에 대해 `BEq`을 구현하기 위해 codes에 대한 재귀가 필요함을 의미합니다:

```lean
def NestedPairs.beq (t : NestedPairs) (x y : t.asType) : Bool :=
match t with
| .nat => x == y
| .pair t1 t2 => beq t1 x.fst y.fst && beq t2 x.snd y.snd
instance {t : NestedPairs} : BEq t.asType where
beq x y := t.beq x y
```

Even though every type in the `NestedPairs` universe already has a `BEq` instance, type class search does not automatically check every possible case of a datatype in an instance declaration, because there might be infinitely many such cases, as with `NestedPairs`.
Attempting to appeal directly to the `BEq` instances rather than explaining to Lean how to find them by recursion on the codes results in an error:

`NestedPairs` universe의 모든 타입이 이미 `BEq` instance를 가지고 있더라도, 타입 클래스 검색은 instance 선언에서 datatype의 모든 가능한 경우를 자동으로 검사하지 않습니다. `NestedPairs`의 경우처럼 무한히 많은 경우가 있을 수 있기 때문입니다.
Codes에 대한 재귀로 그들을 찾는 방법을 Lean에 설명하지 않고 `BEq` instances에 직접 호소하려는 시도는 에러를 초래합니다:

```lean
instance {t : NestedPairs} : BEq t.asType where
beq x y := x == y
```

```
failed to synthesize
  BEq t.asType

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

The `t` in the error message stands for an unknown value of type `NestedPairs`.

에러 메시지의 `t`는 `NestedPairs` 타입의 미지수 값을 나타냅니다.

## 7.2.1. Type Classes vs Universes

Type classes allow an open-ended collection of types to be used with an API as long as they have implementations of the necessary interfaces.
In most cases, this is preferable.
It is hard to predict all use cases for an API ahead of time, and type classes are a convenient way to allow library code to be used with more types than the original author expected.

Type classes는 필요한 인터페이스의 구현이 있는 한 API와 함께 사용할 수 있는 열린 타입 모음을 허용합니다.
대부분의 경우 이것이 선호됩니다.
API의 모든 사용 경우를 미리 예측하기는 어렵고, type classes는 라이브러리 코드가 원래 작성자가 예상한 것보다 더 많은 타입과 함께 사용되도록 허용하는 편리한 방법입니다.

A universe à la Tarski, on the other hand, restricts the API to be usable only with a predetermined collection of types.
This is useful in a few situations:

반면 universe à la Tarski는 API가 미리 정해진 타입 모음과만 사용할 수 있도록 제한합니다.
이는 몇 가지 상황에서 유용합니다:

* When a function should act very differently depending on which type it is passed—it is impossible to pattern match on types themselves, but pattern matching on codes for types is allowed
* When an external system inherently limits the types of data that may be provided, and extra flexibility is not desired
* When additional properties of a type are required over and above the implementation of some operations

Type classes are useful in many of the same situations as interfaces in Java or C#, while a universe à la Tarski can be useful in cases where a sealed class might be used, but where an ordinary inductive datatype is not usable.

Type classes는 Java나 C#의 인터페이스와 많은 유사한 상황에서 유용하고, universe à la Tarski는 sealed class가 사용될 수 있지만 일반적인 inductive datatype이 사용 불가능한 경우에 유용할 수 있습니다.

## 7.2.2. A Universe of Finite Types

Restricting the types that can be used with an API to a predetermined collection can enable operations that would be impossible for an open-ended API.
For example, functions can't normally be compared for equality.
Functions should be considered equal when they map the same inputs to the same outputs.

API와 함께 사용할 수 있는 타입을 미리 정해진 모음으로 제한하면 열린 API에는 불가능한 작업을 수행할 수 있습니다.
예를 들어, 함수는 일반적으로 동일성에 대해 비교할 수 없습니다.
함수는 같은 입력을 같은 출력에 매핑할 때 같다고 간주되어야 합니다.
Checking this could take infinite amounts of time, because comparing two functions with type `Nat → Bool` would require checking that the functions returned the same `Bool` for each and every `Nat`.

이를 확인하는 데는 무한한 시간이 걸릴 수 있습니다. 왜냐하면 `Nat → Bool` 타입의 두 함수를 비교하려면 각 `Nat`에 대해 함수가 같은 `Bool`을 반환하는지 확인해야 하기 때문입니다.

In other words, a function from an infinite type is itself infinite.
Functions can be viewed as tables, and a function whose argument type is infinite requires infinitely many rows to represent each case.
But functions from finite types require only finitely many rows in their tables, making them finite.
Two functions whose argument type is finite can be checked for equality by enumerating all possible arguments, calling the functions on each of them, and then comparing the results.
Checking higher-order functions for equality requires generating all possible functions of a given type, which additionally requires that the return type is finite so that each element of the argument type can be mapped to each element of the return type.
This is not a *fast* method, but it does complete in finite time.

다시 말해, 무한 타입으로부터의 함수는 그 자체로 무한입니다.
함수는 테이블로 볼 수 있으며, 인자 타입이 무한인 함수는 각 경우를 나타내기 위해 무한히 많은 행을 필요합니다.
하지만 유한 타입으로부터의 함수는 테이블에서 유한히 많은 행만 필요하므로, 그 자체가 유한입니다.
인자 타입이 유한한 두 함수는 모든 가능한 인자를 나열하고, 각각에 대해 함수를 호출한 다음 결과를 비교하여 동등성을 확인할 수 있습니다.
고차 함수를 동등성에 대해 확인하려면 주어진 타입의 모든 가능한 함수를 생성해야 하며, 추가적으로 반환 타입이 유한이어야 각 인자 타입의 요소를 반환 타입의 각 요소로 매핑할 수 있습니다.
이는 *fast* 메서드가 아니지만, 유한한 시간 내에 완료됩니다.

One way to represent finite types is by a universe:

유한 타입을 나타내는 한 가지 방법은 universe를 사용하는 것입니다:

```lean
inductive Finite where
| unit : Finite
| bool : Finite
| pair : Finite → Finite → Finite
| arr : Finite → Finite → Finite
abbrev Finite.asType : Finite → Type
| .unit => Unit
| .bool => Bool
| .pair t1 t2 => asType t1 × asType t2
| .arr dom cod => asType dom → asType cod
```

In this universe, the constructor `arr` stands for the function type, which is written with an `arr`ow.

이 universe에서 생성자 `arr`은 함수 타입을 나타내며, `arr`ow로 작성됩니다.

Comparing two values from this universe for equality is almost the same as in the `NestedPairs` universe.
The only important difference is the addition of the case for `arr`, which uses a helper called `Finite.enumerate` to generate every value from the type coded for by `dom`, checking that the two functions return equal results for every possible input:

이 universe의 두 값을 동등성에 대해 비교하는 것은 `NestedPairs` universe의 경우와 거의 동일합니다.
유일한 중요한 차이는 `arr`의 경우 추가입니다. 이는 `Finite.enumerate`라는 helper를 사용하여 `dom`으로 코딩된 타입으로부터 모든 값을 생성하고, 두 함수가 모든 가능한 입력에 대해 같은 결과를 반환하는지 확인합니다:

```lean
def Finite.beq (t : Finite) (x y : t.asType) : Bool :=
match t with
| .unit => true
| .bool => x == y
| .pair t1 t2 => beq t1 x.fst y.fst && beq t2 x.snd y.snd
| .arr dom cod =>
dom.enumerate.all fun arg => beq cod (x arg) (y arg)
```

The standard library function `List.all` checks that the provided function returns `true` on every entry of a list.
This function can be used to compare functions on the Booleans for equality:

표준 라이브러리 함수 `List.all`은 제공된 함수가 리스트의 모든 항목에서 `true`를 반환하는지 확인합니다.
이 함수는 Booleans의 함수를 동등성에 대해 비교하는 데 사용할 수 있습니다:

```lean
#eval Finite.beq (.arr .bool .bool) (fun _ => true) (fun b => b == b)
```

```
true
```

It can also be used to compare functions from the standard library:

이는 또한 표준 라이브러리의 함수를 비교하는 데 사용할 수 있습니다:

```lean
#eval Finite.beq (.arr .bool .bool) (fun _ => true) not
```

```
false
```

It can even compare functions built using tools such as function composition:

이는 함수 합성 같은 도구를 사용하여 구축한 함수를 비교할 수도 있습니다:

```lean
#eval Finite.beq (.arr .bool .bool) id (not ∘ not)
```

```
true
```

This is because the `Finite` universe codes for Lean's *actual* function type, not a special analogue created by the library.

이는 `Finite` universe가 라이브러리에서 생성한 특별한 유사체가 아닌 Lean의 *actual* 함수 타입을 코딩하기 때문입니다.

The implementation of `enumerate` is also by recursion on the codes from `Finite`.

`enumerate`의 구현은 또한 `Finite`의 codes에 대한 재귀입니다.

```lean
def Finite.enumerate (t : Finite) : List t.asType :=
match t with
| .unit => [()]
| .bool => [true, false]
| .pair t1 t2 => t1.enumerate.product t2.enumerate
| .arr dom cod => dom.functions cod.enumerate
```

In the case for `Unit`, there is only a single value.
In the case for `Bool`, there are two values to return (`true` and `false`).
In the case for pairs, the result should be the Cartesian product of the values for the type coded for by `t1` and the values for the type coded for by `t2`.
In other words, every value from `dom` should be paired with every value from `cod`.
The helper function `List.product` can certainly be written with an ordinary recursive function, but here it is defined using `for` in the identity monad:

`Unit`의 경우, 단 하나의 값만 있습니다.
`Bool`의 경우, 반환할 두 개의 값이 있습니다 (`true`와 `false`).
쌍의 경우, 결과는 `t1`으로 코딩된 타입의 값과 `t2`로 코딩된 타입의 값의 데카르트 곱이어야 합니다.
다시 말해, `dom`의 모든 값은 `cod`의 모든 값과 쌍을 이루어야 합니다.
Helper 함수 `List.product`는 확실히 일반적인 재귀 함수로 작성할 수 있지만, 여기서는 identity monad에서 `for`를 사용하여 정의됩니다:

```lean
def List.product (xs : List α) (ys : List β) : List (α × β) := Id.run do
let mut out : List (α × β) := []
for x in xs do
for y in ys do
out := (x, y) :: out
pure out.reverse
```

Finally, the case of `Finite.enumerate` for functions delegates to a helper called `Finite.functions` that takes a list of all of the return values to target as an argument.

마지막으로, 함수에 대한 `Finite.enumerate`의 경우는 목표할 모든 반환 값의 리스트를 인자로 가지는 `Finite.functions`라는 helper에 위임합니다.

Generally speaking, generating all of the functions from some finite type to a collection of result values can be thought of as generating the functions' tables.
Each function assigns an output to each input, which means that a given function has `k` rows in its table when there are `k` possible arguments.
Because each row of the table could select any of `n` possible outputs, there are `n ^ k` potential functions to generate.

일반적으로, 어떤 유한 타입에서 결과 값의 모음으로의 모든 함수를 생성하는 것은 함수의 테이블을 생성하는 것으로 생각할 수 있습니다.
각 함수는 각 입력에 출력을 할당하며, 이는 `k`개의 가능한 인자가 있을 때 주어진 함수가 테이블에 `k`개의 행을 가진다는 의미입니다.
테이블의 각 행이 `n`개의 가능한 출력 중 하나를 선택할 수 있기 때문에, 생성할 수 있는 함수는 `n ^ k`개입니다.

Once again, generating the functions from a finite type to some list of values is recursive on the code that describes the finite type:

다시 한 번, 유한 타입에서 어떤 값의 리스트로의 함수를 생성하는 것은 유한 타입을 설명하는 code에 대한 재귀입니다:

```lean
def Finite.functions
(t : Finite)
(results : List α) : List (t.asType → α) :=
match t with
```

The table for functions from `Unit` contains one row, because the function can't pick different results based on which input it is provided.
This means that one function is generated for each potential input.

`Unit`으로부터의 함수의 테이블은 한 개의 행을 포함합니다. 왜냐하면 함수가 제공되는 입력에 따라 다른 결과를 선택할 수 없기 때문입니다.
이는 각 잠재적 입력에 대해 한 개의 함수가 생성된다는 의미입니다.

```lean
| .unit =>
results.map fun r =>
fun () => r
```

There are `n^2` functions from `Bool` when there are `n` result values, because each individual function of type `Bool → α` uses the `Bool` to select between two particular `α`s:

결과 값이 `n`개 있을 때 `Bool`으로부터의 함수는 `n^2`개이며, 이는 `Bool → α` 타입의 각 개별 함수가 `Bool`을 사용하여 두 개의 특정 `α` 중 하나를 선택하기 때문입니다:

```lean
| .bool =>
(results.product results).map fun (r1, r2) =>
fun
| true => r1
| false => r2
```

Generating the functions from pairs can be achieved by taking advantage of currying.
A function from a pair can be transformed into a function that takes the first element of the pair and returns a function that's waiting for the second element of the pair.
Doing this allows `Finite.functions` to be used recursively in this case:

쌍으로부터의 함수를 생성하는 것은 currying을 활용하여 달성할 수 있습니다.
쌍으로부터의 함수는 쌍의 첫 번째 요소를 취하고 쌍의 두 번째 요소를 기다리는 함수를 반환하는 함수로 변환될 수 있습니다.
이를 하면 이 경우에 `Finite.functions`을 재귀적으로 사용할 수 있습니다:

```lean
| .pair t1 t2 =>
let f1s := t1.functions <| t2.functions results
f1s.map fun f =>
fun (x, y) =>
f x y
```

Generating higher-order functions is a bit of a brain bender.
Each higher-order function takes a function as its argument.
This argument function can be distinguished from other functions based on its input/output behavior.
In general, the higher-order function can apply the argument function to every possible argument, and it can then carry out any possible behavior based on the result of applying the argument function.
This suggests a means of constructing the higher-order functions:

* Begin with a list of all possible arguments to the function that is itself an argument.
* For each possible argument, construct all possible behaviors that can result from the observation of applying the argument function to the possible argument. This can be done using `Finite.functions` and recursion over the rest of the possible arguments, because the result of the recursion represents the functions based on the observations of the rest of the possible arguments. `Finite.functions` constructs all the ways of achieving these based on the observation for the current argument.
* For potential behavior in response to these observations, construct a higher-order function that applies the argument function to the current possible argument. The result of this is then passed to the observation behavior.
* The base case of the recursion is a higher-order function that observes nothing for each result value—it ignores the argument function and simply returns the result value.

고차 함수를 생성하는 것은 다소 혼란스럽습니다.
각 고차 함수는 함수를 인자로 취합니다.
이 인자 함수는 입출력 동작을 기반으로 다른 함수와 구별될 수 있습니다.
일반적으로, 고차 함수는 인자 함수를 모든 가능한 인자에 적용할 수 있으며, 인자 함수 적용의 결과를 기반으로 어떤 가능한 동작이든 수행할 수 있습니다.
이는 고차 함수를 구축하는 수단을 제안합니다:

* 자신이 인자인 함수의 모든 가능한 인자의 리스트로 시작합니다.
* 각 가능한 인자에 대해, 인자 함수를 가능한 인자에 적용하는 것의 관찰로부터 나올 수 있는 모든 가능한 동작을 구축합니다. 이는 `Finite.functions`과 나머지 가능한 인자에 대한 재귀를 사용하여 수행할 수 있습니다. 왜냐하면 재귀의 결과는 나머지 가능한 인자의 관찰을 기반으로 한 함수를 나타내기 때문입니다. `Finite.functions`는 현재 인자에 대한 관찰을 기반으로 이들을 달성하는 모든 방법을 구축합니다.
* 이러한 관찰에 대한 응답의 잠재적 동작에 대해, 인자 함수를 현재 가능한 인자에 적용하는 고차 함수를 구축합니다. 그 결과는 관찰 동작으로 전달됩니다.
* 재귀의 기본 경우는 각 결과 값에 대해 아무것도 관찰하지 않는 고차 함수입니다—인자 함수를 무시하고 단순히 결과 값을 반환합니다.

Defining this recursive function directly causes Lean to be unable to prove that the whole function terminates.
However, using a simpler form of recursion called a *right fold* can be used to make it clear to the termination checker that the function terminates.
A right fold takes three arguments: a step function that combines the head of the list with the result of the recursion over the tail, a default value to return when the list is empty, and the list being processed.
It then analyzes the list, essentially replacing each `::` in the list with a call to the step function and replacing `[]` with the default value:

이 재귀 함수를 직접 정의하면 Lean이 전체 함수가 종료된다는 것을 증명할 수 없게 됩니다.
그러나 *right fold*이라고 불리는 더 간단한 형태의 재귀를 사용하여 함수가 종료된다는 것을 종료 검사기에 명확하게 할 수 있습니다.
Right fold은 세 가지 인자를 취합니다: 리스트의 head를 재귀의 결과와 결합하는 step 함수, 리스트가 비어있을 때 반환할 기본값, 그리고 처리 중인 리스트입니다.
그런 다음 리스트를 분석하여 본질적으로 리스트의 각 `::`을 step 함수에 대한 호출로 바꾸고 `[]`을 기본값으로 바꿉니다:

```lean
def foldr (f : α → β → β) (default : β) : List α → β
| [] => default
| a :: l => f a (foldr f default l)
```

Finding the sum of the `Nat`s in a list can be done with `foldr`:

리스트의 `Nat`들의 합을 찾는 것은 `foldr`로 수행할 수 있습니다:

```lean
[1, 2, 3, 4, 5].foldr (· + ·) 0
(1 :: 2 :: 3 :: 4 :: 5 :: []).foldr (· + ·) 0
(1 + 2 + 3 + 4 + 5 + 0)
15
```

With `foldr`, the higher-order functions can be created as follows:

`foldr`을 사용하면, 고차 함수를 다음과 같이 생성할 수 있습니다:

```lean
| .arr t1 t2 =>
let args := t1.enumerate
let base :=
results.map fun r =>
fun _ => r
args.foldr
(fun arg rest =>
(t2.functions rest).map fun more =>
fun f => more (f arg) f)
base
```

The complete definition of `Finite.functions` is:

`Finite.functions`의 완전한 정의는:

```lean
def Finite.functions
(t : Finite)
(results : List α) : List (t.asType → α) :=
match t with
| .unit =>
results.map fun r =>
fun () => r
| .bool =>
(results.product results).map fun (r1, r2) =>
fun
| true => r1
| false => r2
| .pair t1 t2 =>
let f1s := t1.functions <| t2.functions results
f1s.map fun f =>
fun (x, y) =>
f x y
| .arr t1 t2 =>
let args := t1.enumerate
let base :=
results.map fun r =>
fun _ => r
args.foldr
(fun arg rest =>
(t2.functions rest).map fun more =>
fun f => more (f arg) f)
base
```

Because `Finite.enumerate` and `Finite.functions` call each other, they must be defined in a `mutual` block.
In other words, right before the definition of `Finite.enumerate` is the `mutual` keyword:

`Finite.enumerate`과 `Finite.functions`가 서로 호출하기 때문에, 그들은 `mutual` 블록에서 정의되어야 합니다.
다시 말해, `Finite.enumerate` 정의 바로 앞에 `mutual` 키워드가 있습니다:

```lean
mutual
def Finite.enumerate (t : Finite) : List t.asType :=
match t with
```

and right after the definition of `Finite.functions` is the `end` keyword:

그리고 `Finite.functions` 정의 바로 뒤에 `end` 키워드가 있습니다:

```lean
| .arr t1 t2 =>
let args := t1.enumerate
let base :=
results.map fun r =>
fun _ => r
args.foldr
(fun arg rest =>
(t2.functions rest).map fun more =>
fun f => more (f arg) f)
base
end
```

This algorithm for comparing functions is not particularly practical.
The number of cases to check grows exponentially; even a simple type like `((Bool × Bool) → Bool) → Bool` describes 65536 distinct functions.
Why are there so many?
Based on the reasoning above, and using `\left| T \right|` to represent the number of values described by the type `T`, we should expect that
`\left| \left( \left( \mathtt{Bool} \times \mathtt{Bool} \right) \rightarrow \mathtt{Bool} \right) \rightarrow \mathtt{Bool} \right|`
is
`\left|\mathrm{Bool}\right|^{\left| \left( \mathtt{Bool} \times \mathtt{Bool} \right) \rightarrow \mathtt{Bool} \right| },`
which is
`2^{2^{\left| \mathtt{Bool} \times \mathtt{Bool} \right| }},`
which is

```lean
2^{2^4}
```

or 65536.
Nested exponentials grow quickly, and there are many higher-order functions.

함수를 비교하는 이 알고리즘은 특히 실용적이지 않습니다.
확인할 경우의 수는 지수적으로 증가합니다; `((Bool × Bool) → Bool) → Bool` 같은 간단한 타입도 65536개의 서로 다른 함수를 설명합니다.
왜 그렇게 많을까요?
위의 추론을 기반으로, 그리고 `\left| T \right|`를 타입 `T`에 의해 설명되는 값의 개수를 나타내기 위해 사용하면, 우리는 다음을 기대할 것입니다:
는
인데, 이는
이고,
또는 65536입니다.
중첩된 지수는 빠르게 증가하며, 많은 고차 함수가 있습니다.

## 7.2.3. Exercises

* Write a function that converts any value from a type coded for by `Finite` into a string. Functions should be represented as their tables.
* Add the empty type `Empty` to `Finite` and `Finite.beq`.
* Add `Option` to `Finite` and `Finite.beq`.
