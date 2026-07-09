---
title: "3.5. 표준 Class들"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "산술, 비교, 해싱, functor 등 Lean의 표준 type class 오버로딩"
---

# 3.5. Standard Classes

This section presents a variety of operators and functions that can be overloaded using type classes in Lean.
Each operator or function corresponds to a method of a type class.
Unlike C++, infix operators in Lean are defined as abbreviations for named functions; this means that overloading them for new types is not done using the operator itself, but rather using the underlying name (such as `HAdd.hAdd`).

이 섹션은 Lean에서 type class를 사용하여 오버로드할 수 있는 다양한 연산자와 함수를 소개합니다.
각 연산자 또는 함수는 type class의 메서드에 대응합니다.
C++와 달리, Lean의 infix 연산자는 명명된 함수의 축약형으로 정의됩니다. 즉, 새로운 타입에 대해 연산자를 오버로드할 때는 연산자 자체가 아니라 (`HAdd.hAdd`와 같은) 기본 이름을 사용합니다.

## 3.5.1. Arithmetic

Most arithmetic operators are available in a heterogeneous form, where the arguments may have different type and an output parameter decides the type of the resulting expression.
For each heterogeneous operator, there is a corresponding homogeneous version that can found by removing the letter `h`, so that `HAdd.hAdd` becomes `Add.add`.
The following arithmetic operators are overloaded:

대부분의 산술 연산자는 heterogeneous 형태로 사용 가능하며, 이 경우 인자들이 다른 타입을 가질 수 있고 output 매개변수가 결과 표현식의 타입을 결정합니다.
각 heterogeneous 연산자마다 대응하는 homogeneous 버전이 있으며, 문자 `h`를 제거하여 찾을 수 있습니다. 예를 들어 `HAdd.hAdd`는 `Add.add`가 됩니다.
다음 산술 연산자들이 오버로드됩니다.

## 3.5.2. Bitwise Operators

Lean contains a number of standard bitwise operators that are overloaded using type classes.
There are instances for fixed-width types such as `UInt8`, `UInt16`, `UInt32`, `UInt64`, and `USize`.
The latter is the size of words on the current platform, typically 32 or 64 bits.
The following bitwise operators are overloaded:

Lean은 type class를 사용하여 오버로드되는 여러 표준 bitwise 연산자를 포함합니다.
`UInt8`, `UInt16`, `UInt32`, `UInt64`, `USize`와 같은 고정 너비 타입에 대한 instance들이 있습니다.
후자는 현재 플랫폼의 word 크기이며, 일반적으로 32 또는 64 비트입니다.
다음 bitwise 연산자들이 오버로드됩니다.

Because the names `And` and `Or` are already taken as the names of logical connectives, the homogeneous versions of `HAnd` and `HOr` are called `AndOp` and `OrOp` rather than `And` and `Or`.

`And`와 `Or`는 이미 논리 결합자(logical connective)의 이름으로 사용되고 있기 때문에, `HAnd`와 `HOr`의 homogeneous 버전은 `And`와 `Or` 대신 `AndOp`과 `OrOp`라고 합니다.

## 3.5.3. Equality and Ordering

Testing equality of two values typically uses the `BEq` class, which is short for “Boolean equality”.
Due to Lean's use as a theorem prover, there are really two kinds of equality operators in Lean:

두 값의 equality를 테스트할 때는 일반적으로 “Boolean equality”를 줄인 `BEq` class를 사용합니다.
Lean이 theorem prover로 사용되기 때문에, Lean에는 실제로 두 가지 종류의 equality 연산자가 있습니다:

* *Boolean equality* is the same kind of equality that is found in other programming languages. It is a function that takes two values and returns a `Bool`. Boolean equality is written with two equals signs, just as in Python and C#. Because Lean is a pure functional language, there's no separate notions of reference vs value equality—pointers cannot be observed directly.
* *Propositional equality* is the mathematical statement that two things are equal. Propositional equality is not a function; rather, it is a mathematical statement that admits proof. It is written with a single equals sign. A statement of propositional equality is like a type that classifies evidence of this equality.

* *Boolean equality*는 다른 프로그래밍 언어에서 찾을 수 있는 것과 같은 종류의 equality입니다. 두 개의 값을 받아 `Bool`을 반환하는 함수입니다. Boolean equality는 Python이나 C#처럼 두 개의 등호로 표기됩니다. Lean이 pure functional 언어이기 때문에, reference와 value equality의 구분이 없습니다. 포인터는 직접 관찰할 수 없습니다.
* *Propositional equality*는 두 개의 것이 같다는 수학적 진술입니다. Propositional equality는 함수가 아니라, 증명을 인정하는 수학적 진술입니다. 한 개의 등호로 표기됩니다. Propositional equality 진술은 이 equality의 증거를 분류하는 타입과 같습니다.

Both notions of equality are important, and used for different purposes.
Boolean equality is useful in programs, when a decision needs to be made about whether two values are equal.
For example, `"Octopus" == "Cuttlefish"` evaluates to `false`, and `"Octopodes" == "Octo".append "podes"` evaluates to `true`.
Some values, such as functions, cannot be checked for equality.
For example, `(fun (x : Nat) => 1 + x) == (Nat.succ ·)` yields the error:

두 equality 개념 모두 중요하며 다른 목적으로 사용됩니다.
Boolean equality는 두 값이 같은지에 대한 결정이 필요할 때 프로그램에서 유용합니다.
예를 들어, `"Octopus" == "Cuttlefish"`는 `false`로 평가되고, `"Octopodes" == "Octo".append "podes"`는 `true`로 평가됩니다.
함수와 같은 일부 값은 equality를 확인할 수 없습니다.
예를 들어, `(fun (x : Nat) => 1 + x) == (Nat.succ ·)`는 다음 에러를 생성합니다:

```
failed to synthesize
  BEq (Nat → Nat)

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

As this message indicates, `==` is overloaded using a type class.
The expression `x == y` is actually shorthand for `BEq.beq x y`.

이 메시지가 나타내듯이, `==`는 type class를 사용하여 오버로드됩니다.
표현식 `x == y`는 사실 `BEq.beq x y`의 축약형입니다.

Propositional equality is a mathematical statement rather than an invocation of a program.
Because propositions are like types that describe evidence for some statement, propositional equality has more in common with types like `String` and `Nat → List Int` than it does with Boolean equality.
This means that it can't automatically be checked.
However, the equality of any two expressions can be stated in Lean, so long as they have the same type.
The statement `(fun (x : Nat) => 1 + x) = (Nat.succ ·)` is a perfectly reasonable statement.
From the perspective of mathematics, two functions are equal if they map equal inputs to equal outputs, so this statement is even true, though it requires a one-line proof to convince Lean of this fact.

Propositional equality는 프로그램 실행이 아니라 수학적 진술입니다.
Proposition은 어떤 진술의 증거를 설명하는 타입과 같기 때문에, propositional equality는 Boolean equality보다는 `String`이나 `Nat → List Int`와 같은 타입에 더 많은 공통점을 가집니다.
이는 자동으로 확인할 수 없다는 의미입니다.
그러나 두 표현식이 같은 타입을 가지는 한, Lean에서 임의의 두 표현식의 equality를 진술할 수 있습니다.
진술 `(fun (x : Nat) => 1 + x) = (Nat.succ ·)`는 완벽히 합리적인 진술입니다.
수학의 관점에서, 두 함수는 같은 입력을 같은 출력으로 매핑할 때 같으므로, 이 진술은 사실이며, Lean이 이를 확신하기 위해 한 줄의 증명이 필요합니다.

Generally speaking, when using Lean as a programming language, it's easiest to stick to Boolean functions rather than propositions.
However, as the names `true` and `false` for `Bool`'s constructors suggest, this difference is sometimes blurred.
Some propositions are *decidable*, which means that they can be checked just like a Boolean function.
The function that checks whether the proposition is true or false is called a *decision procedure*, and it returns *evidence* of the truth or falsity of the proposition.
Some examples of decidable propositions include equality and inequality of natural numbers, equality of strings, and “ands” and “ors” of propositions that are themselves decidable.

일반적으로 Lean을 프로그래밍 언어로 사용할 때는 proposition보다 Boolean 함수를 사용하는 것이 가장 쉽습니다.
그러나 `Bool`의 생성자인 `true`와 `false`의 이름에서 시사하듯이, 이 차이는 때때로 모호해집니다.
어떤 proposition은 *decidable*이며, 이는 Boolean 함수처럼 확인할 수 있다는 의미입니다.
proposition이 참인지 거짓인지 확인하는 함수를 *decision procedure*라고 하며, proposition의 참 또는 거짓에 대한 *증거*를 반환합니다.
Decidable proposition의 예에는 자연수의 equality와 부등호, 문자열의 equality, 그리고 자신이 decidable인 proposition들의 “and”와 “or”가 포함됩니다.

In Lean, `if` works with decidable propositions.
For example, `2 < 4` is a proposition:

Lean에서 `if`는 decidable proposition과 함께 작동합니다.
예를 들어, `2 < 4`는 proposition입니다:

```lean
#check 2 < 4
```

```
2 < 4 : Prop
```

Nonetheless, it is perfectly acceptable to write it as the condition in an `if`.
For example, `if 2 < 4 then 1 else 2` has type `Nat` and evaluates to `1`.

그럼에도 불구하고, `if`의 조건으로 작성하는 것은 완전히 받아들일 수 있습니다.
예를 들어, `if 2 < 4 then 1 else 2`는 타입 `Nat`을 가지며 `1`로 평가됩니다.

Not all propositions are decidable.
If they were, then computers would be able to prove any true proposition just by running the decision procedure, and mathematicians would be out of a job.
More specifically, decidable propositions have an instance of the `Decidable` type class, which contains the decision procedure.
Trying to use a proposition that isn't decidable as if it were a `Bool` results in a failure to find the `Decidable` instance.
For example, `if (fun (x : Nat) => 1 + x) = (Nat.succ ·) then "yes" else "no"` results in:

모든 proposition이 decidable한 것은 아닙니다.
만약 그랬다면 컴퓨터는 단순히 decision procedure를 실행하여 참인 모든 proposition을 증명할 수 있을 것이고, 수학자들은 일자리를 잃을 것입니다.
더 구체적으로, decidable proposition은 decision procedure를 포함하는 `Decidable` type class의 instance를 가집니다.
Decidable하지 않은 proposition을 `Bool`인 것처럼 사용하려고 하면 `Decidable` instance를 찾는 데 실패합니다.
예를 들어, `if (fun (x : Nat) => 1 + x) = (Nat.succ ·) then "yes" else "no"`는 다음을 야기합니다:

```
failed to synthesize
  Decidable ((fun x => 1 + x) = fun x => x.succ)

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

The following propositions, that are usually decidable, are overloaded with type classes:

일반적으로 decidable한 다음 proposition들이 type class로 오버로드됩니다.

Because defining new propositions hasn't yet been demonstrated, it may be difficult to define completely new instances of `LT` and `LE`.
However, they can be defined in terms of existing instances.
`LT` and `LE` instances for `Pos` can use the existing instances for `Nat`:

새로운 proposition을 정의하는 것이 아직 설명되지 않았기 때문에, `LT`와 `LE`의 완전히 새로운 instance를 정의하기 어려울 수 있습니다.
그러나 이들은 기존 instance 측면에서 정의될 수 있습니다.
`Pos`에 대한 `LT`와 `LE` instance는 `Nat`에 대한 기존 instance를 사용할 수 있습니다:

```lean
instance : LT Pos where
  lt x y := LT.lt x.toNat y.toNat
instance : LE Pos where
  le x y := LE.le x.toNat y.toNat
```

These propositions are not decidable by default because Lean doesn't unfold the definitions of propositions while synthesizing an instance.
This can be bridged using the `inferInstanceAs` operator, which finds an instance for a given class if it exists:

이러한 proposition들은 기본적으로 decidable하지 않습니다. Lean이 instance를 합성할 때 proposition의 정의를 펼치지(unfold) 않기 때문입니다.
이는 주어진 class에 대한 instance를 찾는 `inferInstanceAs` operator를 사용하여 해결할 수 있습니다:

```lean
instance {x : Pos} {y : Pos} : Decidable (x < y) :=
  inferInstanceAs (Decidable (x.toNat < y.toNat))
instance {x : Pos} {y : Pos} : Decidable (x ≤ y) :=
  inferInstanceAs (Decidable (x.toNat ≤ y.toNat))
```

The type checker confirms that the definitions of the propositions match.
Confusing them results in an error:

Type checker는 proposition의 정의가 일치하는지 확인합니다.
이들을 혼동하면 에러가 발생합니다:

```lean
instance {x : Pos} {y : Pos} : Decidable (x ≤ y) :=
  inferInstanceAs (Decidable (x.toNat < y.toNat))
```

```
Type mismatch
  inferInstanceAs (Decidable (x.toNat < y.toNat))
has type
  Decidable (x.toNat < y.toNat)
but is expected to have type
  Decidable (x ≤ y)
```

Comparing values using `<`, `==`, and `>` can be inefficient.
Checking first whether one value is less than another, and then whether they are equal, can require two traversals over large data structures.
To solve this problem, Java and C# have standard `compareTo` and `CompareTo` methods (respectively) that can be overridden by a class in order to implement all three operations at the same time.
These methods return a negative integer if the receiver is less than the argument, zero if they are equal, and a positive integer if the receiver is greater than the argument.
Rather than overloading the meaning of integers, Lean has a built-in inductive type that describes these three possibilities:

`<`, `==`, `>`를 사용하여 값을 비교하는 것은 비효율적일 수 있습니다.
먼저 한 값이 다른 값보다 작은지 확인하고, 그 다음 같은지 확인하는 것은 큰 데이터 구조에 대해 두 번의 순회를 요구할 수 있습니다.
이 문제를 해결하기 위해 Java와 C#은 표준 `compareTo`와 `CompareTo` 메서드(각각)를 가지고 있으며, 이들은 세 가지 연산을 동시에 구현하기 위해 class에 의해 오버라이드될 수 있습니다.
이 메서드들은 receiver가 argument보다 작으면 음수, 같으면 0, 크면 양수를 반환합니다.
정수의 의미를 오버로드하는 대신, Lean은 이 세 가지 가능성을 설명하는 built-in inductive 타입을 가집니다:

```lean
inductive Ordering where
  | lt
  | eq
  | gt
```

The `Ord` type class can be overloaded to produce these comparisons.
For `Pos`, an implementation can be:

`Ord` type class는 이러한 비교들을 생성하도록 오버로드될 수 있습니다.
`Pos`에 대해, 구현은 다음과 같을 수 있습니다:

```lean
def Pos.comp : Pos → Pos → Ordering
  | Pos.one, Pos.one => Ordering.eq
  | Pos.one, Pos.succ _ => Ordering.lt
  | Pos.succ _, Pos.one => Ordering.gt
  | Pos.succ n, Pos.succ k => comp n k
instance : Ord Pos where
  compare := Pos.comp
```

In situations where `compareTo` would be the right approach in Java, use `Ord.compare` in Lean.

Java에서 `compareTo`가 올바른 접근이 될 상황에서는 Lean에서 `Ord.compare`을 사용합니다.

## 3.5.4. Hashing

Java and C# have `hashCode` and `GetHashCode` methods, respectively, that compute a hash of a value for use in data structures such as hash tables.
The Lean equivalent is a type class called `Hashable`:

Java와 C#은 각각 `hashCode`와 `GetHashCode` 메서드를 가지고 있으며, 이들은 해시 테이블과 같은 데이터 구조에서 사용하기 위해 값의 해시를 계산합니다.
Lean의 동등 개념은 `Hashable`이라는 type class입니다:

```lean
class Hashable (α : Type) where
  hash : α → UInt64
```

If two values are considered equal according to a `BEq` instance for their type, then they should have the same hashes.
In other words, if `x == y` then `hash x == hash y`.
If `x ≠ y`, then `hash x` won't necessarily differ from `hash y` (after all, there are infinitely more `Nat` values than there are `UInt64` values), but data structures built on hashing will have better performance if unequal values are likely to have unequal hashes.
This is the same expectation as in Java and C#.

두 값이 그들의 타입에 대한 `BEq` instance에 따라 같다고 간주되면, 같은 해시를 가져야 합니다.
다시 말해, `x == y`이면 `hash x == hash y`입니다.
`x ≠ y`인 경우, `hash x`가 반드시 `hash y`와 다를 필요는 없습니다(결국, `Nat` 값이 `UInt64` 값보다 훨씬 더 많습니다). 그러나 해싱으로 만들어진 데이터 구조는 같지 않은 값들이 같지 않은 해시를 가질 가능성이 높으면 더 좋은 성능을 가질 것입니다.
이는 Java와 C#에서와 같은 기대입니다.

The standard library contains a function `mixHash` with type `UInt64 → UInt64 → UInt64` that can be used to combine hashes for different fields for a constructor.
A reasonable hash function for an inductive datatype can be written by assigning a unique number to each constructor, and then mixing that number with the hashes of each field.
For example, a `Hashable` instance for `Pos` can be written:

표준 라이브러리는 `UInt64 → UInt64 → UInt64` 타입의 `mixHash` 함수를 포함하고 있으며, constructor의 서로 다른 필드에 대한 해시를 결합하는 데 사용될 수 있습니다.
Inductive datatype에 대한 합리적인 해시 함수는 각 constructor에 고유한 번호를 할당한 다음 그 번호를 각 필드의 해시와 혼합하여 작성할 수 있습니다.
예를 들어, `Pos`에 대한 `Hashable` instance는 다음과 같이 작성할 수 있습니다:

```lean
def hashPos : Pos → UInt64
  | Pos.one => 0
  | Pos.succ n => mixHash 1 (hashPos n)
instance : Hashable Pos where
  hash := hashPos
```

## 3.5.5. Deriving Standard Classes

Instance of classes like `BEq` and `Hashable` are often quite tedious to implement by hand.
Lean includes a feature called *instance deriving* that allows the compiler to automatically construct well-behaved instances of many type classes.
In fact, the `deriving Repr` phrase in the definition of `Firewood` in the [first section on polymorphism](../ch01/) is an example of instance deriving.

`BEq`와 `Hashable`과 같은 class들의 instance는 종종 손으로 구현하기에는 상당히 번거롭습니다.
Lean은 컴파일러가 많은 type class들의 well-behaved instance를 자동으로 구성할 수 있게 해주는 *instance deriving*이라는 기능을 포함합니다.
사실, [polymorphism에 대한 첫 번째 섹션](../ch01/)의 `Firewood` 정의에서 `deriving Repr` 구문은 instance deriving의 예시입니다.

Instances can be derived in two ways.
The first can be used when defining a structure or inductive type.
In this case, add `deriving` to the end of the type declaration followed by the names of the classes for which instances should be derived.
For a type that is already defined, a standalone `deriving` command can be used.
Write `deriving instance C1, C2, ... for T` to derive instances of `C1, C2, ...` for the type `T` after the fact.

Instance는 두 가지 방법으로 derive될 수 있습니다.
첫 번째는 structure 또는 inductive 타입을 정의할 때 사용할 수 있습니다.
이 경우, 타입 선언의 끝에 `deriving`을 추가하고 instance가 derive될 class들의 이름을 따릅니다.
이미 정의된 타입의 경우, 독립적인 `deriving` 명령을 사용할 수 있습니다.
`deriving instance C1, C2, ... for T`를 작성하여 타입 `T`에 대해 `C1, C2, ...`의 instance를 나중에 derive합니다.

`BEq` and `Hashable` instances can be derived for `Pos` and `NonEmptyList` using a very small amount of code:

`BEq`와 `Hashable` instance는 매우 적은 양의 코드를 사용하여 `Pos`와 `NonEmptyList`에 대해 derive될 수 있습니다:

```lean
deriving instance BEq, Hashable for Pos
deriving instance BEq, Hashable for NonEmptyList
```

Instances can be derived for at least the following classes:

Instance는 최소한 다음 class들에 대해 derive될 수 있습니다.

In some cases, however, the derived `Ord` instance may not produce precisely the ordering desired in an application.
When this is the case, it's fine to write an `Ord` instance by hand.
The collection of classes for which instances can be derived can be extended by advanced users of Lean.

그러나 어떤 경우에는, derive된 `Ord` instance가 정확히 애플리케이션에서 원하는 ordering을 생성하지 못할 수 있습니다.
이 경우, `Ord` instance를 손으로 작성하는 것이 좋습니다.
Instance가 derive될 수 있는 class들의 모음은 Lean의 고급 사용자에 의해 확장될 수 있습니다.

Aside from the clear advantages in programmer productivity and code readability, deriving instances also makes code easier to maintain, because the instances are updated as the definitions of types evolve.
When reviewing changes to code, modifications that involve updates to datatypes are much easier to read without line after line of formulaic modifications to equality tests and hash computation.

프로그래머 생산성과 코드 가독성의 명백한 장점 외에도, instance를 derive하면 코드를 유지하기가 더 쉬워집니다. 왜냐하면 타입의 정의가 진화함에 따라 instance가 업데이트되기 때문입니다.
코드의 변경 사항을 검토할 때, 데이터타입 업데이트를 포함하는 수정 사항은 equality 테스트 및 해시 계산에 대한 짤막한 수정 사항이 없이도 훨씬 더 읽기 쉽습니다.

## 3.5.6. Appending

Many datatypes have some sort of append operator.
In Lean, appending two values is overloaded with the type class `HAppend`, which is a heterogeneous operation like that used for arithmetic operations:

많은 데이터타입은 어떤 종류의 append 연산자를 가지고 있습니다.
Lean에서, 두 값을 append하는 것은 arithmetic 연산에 사용되는 것과 같은 heterogeneous 연산인 type class `HAppend`로 오버로드됩니다:

```lean
class HAppend (α : Type) (β : Type) (γ : outParam Type) where
  hAppend : α → β → γ
```

The syntax `xs ++ ys` desugars to `HAppend.hAppend xs ys`.
For homogeneous cases, it's enough to implement an instance of `Append`, which follows the usual pattern:

문법 `xs ++ ys`는 `HAppend.hAppend xs ys`로 desugars됩니다.
Homogeneous 경우에는 일반적인 패턴을 따르는 `Append`의 instance를 구현하면 충분합니다:

```lean
instance : Append (NonEmptyList α) where
  append xs ys :=
    { head := xs.head, tail := xs.tail ++ ys.head :: ys.tail }
```

After defining the above instance,

위의 instance를 정의한 후,

```lean
#eval idahoSpiders ++ idahoSpiders
```

has the following output:

다음 output을 가집니다:

```
{ head := "Banded Garden Spider",
  tail := ["Long-legged Sac Spider",
           "Wolf Spider",
           "Hobo Spider",
           "Cat-faced Spider",
           "Banded Garden Spider",
           "Long-legged Sac Spider",
           "Wolf Spider",
           "Hobo Spider",
           "Cat-faced Spider"] }
```

Similarly, a definition of `HAppend` allows non-empty lists to be appended to ordinary lists:

마찬가지로, `HAppend`의 정의는 non-empty list들이 ordinary list에 append될 수 있게 합니다:

```lean
instance : HAppend (NonEmptyList α) (List α) (NonEmptyList α) where
  hAppend xs ys :=
    { head := xs.head, tail := xs.tail ++ ys }
```

With this instance available,

이 instance가 사용 가능하면,

```lean
#eval idahoSpiders ++ ["Trapdoor Spider"]
```

results in

다음이 나타납니다

```
{ head := "Banded Garden Spider",
  tail := ["Long-legged Sac Spider", "Wolf Spider", "Hobo Spider", "Cat-faced Spider", "Trapdoor Spider"] }
```

## 3.5.7. Functors

A polymorphic type is a *functor* if it has an overload for a function named `map` that transforms every element contained in it by a function.
While most languages use this terminology, C#'s equivalent of `map` is called `System.Linq.Enumerable.Select`.
For example, mapping a function over a list constructs a new list in which each entry from the starting list has been replaced by the result of the function on that entry.
Mapping a function `f` over an `Option` leaves `none` untouched, and replaces `some x` with `some (f x)`.

Polymorphic 타입은 포함된 모든 원소를 함수로 변환하는 `map`이라는 함수에 대한 overload를 가지고 있으면 *functor*입니다.
대부분의 언어들이 이 용어를 사용하지만, C#의 `map` 동등물은 `System.Linq.Enumerable.Select`라고 불립니다.
예를 들어, list에 함수를 매핑하면 시작 list의 각 항목이 그 항목에 대한 함수의 결과로 대체된 새로운 list를 만듭니다.
`Option`에 함수 `f`를 매핑하면 `none`을 그대로 두고, `some x`를 `some (f x)`로 대체합니다.

Here are some examples of functors and how their `Functor` instances overload `map`:

다음은 functor와 이들의 `Functor` instance가 `map`을 오버로드하는 방법의 몇 가지 예입니다:

* `Functor.map (· + 5) [1, 2, 3]` evaluates to `[6, 7, 8]`
* `Functor.map toString (some (List.cons 5 List.nil))` evaluates to `some "[5]"`
* `Functor.map List.reverse [[1, 2, 3], [4, 5, 6]]` evaluates to `[[3, 2, 1], [6, 5, 4]]`

Because `Functor.map` is a bit of a long name for this common operation, Lean also provides an infix operator for mapping a function, namely `<$>`.
The prior examples can be rewritten as follows:

`Functor.map`은 이 일반적인 연산에 대해 조금 긴 이름이기 때문에, Lean은 함수를 매핑하기 위한 infix 연산자인 `<$>`도 제공합니다.
위의 예들은 다음과 같이 다시 쓸 수 있습니다:

* `(· + 5) <$> [1, 2, 3]` evaluates to `[6, 7, 8]`
* `toString <$> (some (List.cons 5 List.nil))` evaluates to `some "[5]"`
* `List.reverse <$> [[1, 2, 3], [4, 5, 6]]` evaluates to `[[3, 2, 1], [6, 5, 4]]`

An instance of `Functor` for `NonEmptyList` requires specifying the `map` function.

`NonEmptyList`에 대한 `Functor`의 instance는 `map` 함수를 지정해야 합니다.

```lean
instance : Functor NonEmptyList where
  map f xs := { head := f xs.head, tail := f <$> xs.tail }
```

Here, `map` uses the `Functor` instance for `List` to map the function over the tail.
This instance is defined for `NonEmptyList` rather than for `NonEmptyList α` because the argument type `α` plays no role in resolving the type class.
A `NonEmptyList` can have a function mapped over it *no matter what the type of entries is*.
If `α` were a parameter to the class, then it would be possible to make versions of `Functor` that only worked for `NonEmptyList Nat`, but part of being a functor is that `map` works for any entry type.

여기서, `map`은 `List`에 대한 `Functor` instance를 사용하여 tail에 함수를 매핑합니다.
이 instance는 `NonEmptyList α`가 아니라 `NonEmptyList`에 대해 정의됩니다. 왜냐하면 argument 타입 `α`는 type class를 해결하는 데 역할을 하지 않기 때문입니다.
`NonEmptyList`는 *항목의 타입이 무엇이든 상관없이* 함수를 매핑할 수 있습니다.
만약 `α`가 class의 매개변수였다면, `NonEmptyList Nat`에서만 작동하는 `Functor` 버전을 만드는 것이 가능했을 것입니다. 하지만 functor의 일부는 `map`이 모든 항목 타입에서 작동한다는 것입니다.

Here is an instance of `Functor` for `PPoint`:

다음은 `PPoint`에 대한 `Functor`의 instance입니다:

```lean
instance : Functor PPoint where
  map f p := { x := f p.x, y := f p.y }
```

In this case, `f` has been applied to both `x` and `y`.

이 경우, `f`는 `x`와 `y` 모두에 적용되었습니다.

Even when the type contained in a functor is itself a functor, mapping a function only goes down one layer.
That is, when using `map` on a `NonEmptyList (PPoint Nat)`, the function being mapped should take `PPoint Nat` as its argument rather than `Nat`.

Functor에 포함된 타입이 그 자체로 functor인 경우에도, 함수를 매핑하는 것은 한 층만 내려갑니다.
즉, `NonEmptyList (PPoint Nat)`에 `map`을 사용할 때, 매핑되는 함수는 `Nat`보다는 `PPoint Nat`을 인자로 받아야 합니다.

The definition of the `Functor` class uses one more language feature that has not yet been discussed: default method definitions.
Normally, a class will specify some minimal set of overloadable operations that make sense together, and then use polymorphic functions with instance implicit arguments that build on the overloaded operations to provide a larger library of features.
For example, the function `concat` can concatenate any non-empty list whose entries are appendable:

`Functor` class의 정의는 아직 논의되지 않은 하나의 언어 기능을 더 사용합니다: default method definitions입니다.
일반적으로, class는 함께 의미를 이루는 일부 최소한의 오버로드 가능한 연산들을 지정하고, 그 다음 오버로드된 연산을 기반으로 더 큰 기능 라이브러리를 제공하는 instance implicit argument를 가진 polymorphic 함수를 사용합니다.
예를 들어, `concat` 함수는 항목이 appendable한 모든 non-empty list를 연결할 수 있습니다:

```lean
def concat [Append α] (xs : NonEmptyList α) : α :=
  let rec catList (start : α) : List α → α
    | [] => start
    | (z :: zs) => catList (start ++ z) zs
  catList xs.head xs.tail
```

However, for some classes, there are operations that can be more efficiently implemented with knowledge of the internals of a datatype.

In these cases, a default method definition can be provided.
A default method definition provides a default implementation of a method in terms of the other methods.
However, instance implementors may choose to override this default with something more efficient.
Default method definitions contain `:=` in a `class` definition.

그러나 어떤 class들의 경우, datatype의 내부에 대한 지식으로 더 효율적으로 구현될 수 있는 연산들이 있습니다.

이 경우들에서, default method definition을 제공할 수 있습니다.
Default method definition은 다른 method들의 관점에서 method의 기본 구현을 제공합니다.
그러나 instance 구현자는 이 기본값을 더 효율적인 것으로 오버라이드하기로 선택할 수 있습니다.
Default method definition은 `class` 정의에서 `:=`를 포함합니다.

In the case of `Functor`, some types have a more efficient way of implementing `map` when the function being mapped ignores its argument.
Functions that ignore their arguments are called *constant functions* because they always return the same value.
Here is the definition of `Functor`, in which `mapConst` has a default implementation:

`Functor`의 경우, 어떤 타입들은 매핑되는 함수가 그 인자를 무시할 때 `map`을 구현하는 더 효율적인 방법을 가집니다.
인자를 무시하는 함수들은 항상 같은 값을 반환하기 때문에 *constant function*라고 합니다.
다음은 `mapConst`가 기본 구현을 가지는 `Functor`의 정의입니다:

```lean
class Functor (f : Type → Type) where
  map : {α β : Type} → (α → β) → f α → f β
  mapConst {α β : Type} (x : α) (coll : f β) : f α :=
    map (fun _ => x) coll
```

Just as a `Hashable` instance that doesn't respect `BEq` is buggy, a `Functor` instance that moves around the data as it maps the function is also buggy.
For example, a buggy `Functor` instance for `List` might throw away its argument and always return the empty list, or it might reverse the list.
A bad `Functor` instance for `PPoint` might place `f x` in both the `x` and the `y` fields, or swap them.
Specifically, `Functor` instances should follow two rules:

`BEq`를 존중하지 않는 `Hashable` instance가 buggy인 것처럼, 함수를 매핑할 때 데이터를 이리저리 움직이는 `Functor` instance도 buggy입니다.
예를 들어, buggy `Functor` instance for `List`는 인자를 버리고 항상 빈 list를 반환하거나, list를 역순으로 만들 수 있습니다.
나쁜 `Functor` instance for `PPoint`는 `f x`를 `x`와 `y` 필드 모두에 배치하거나, 이들을 바꿀 수 있습니다.
구체적으로, `Functor` instance들은 다음 두 가지 규칙을 따라야 합니다:

1. Mapping the identity function should result in the original argument.
2. Mapping two composed functions should have the same effect as composing their mapping.

More formally, the first rule says that `id <$> x` equals `x`.
The second rule says that `map (fun y => f (g y)) x` equals `map f (map g x)`.
The composition `f ∘ g` can also be written `fun y => f (g y)`.
These rules prevent implementations of `map` that move the data around or delete some of it.

1. Identity 함수를 매핑하면 원본 인자를 결과로 가져야 합니다.
2. 두 개의 합성된 함수를 매핑하는 것은 이들의 매핑을 합성하는 것과 같은 효과를 가져야 합니다.

더 정형적으로, 첫 번째 규칙은 `id <$> x`가 `x`와 같다고 말합니다.
두 번째 규칙은 `map (fun y => f (g y)) x`가 `map f (map g x)`와 같다고 말합니다.
합성 `f ∘ g`는 `fun y => f (g y)`로도 쓸 수 있습니다.
이 규칙들은 데이터를 이리저리 움직이거나 일부를 삭제하는 `map`의 구현을 방지합니다.

## 3.5.8. Messages You May Meet

Lean is not able to derive instances for all classes.
For example, the code

```lean
deriving instance ToString for NonEmptyList
```

results in the following error:

Lean은 모든 class에 대해 instance를 derive할 수 없습니다.
예를 들어, 다음 코드는 다음 에러를 야기합니다:

```
No deriving handlers have been implemented for class `ToString`
```

Invoking `deriving instance` causes Lean to consult an internal table of code generators for type class instances.
If the code generator is found, then it is invoked on the provided type to create the instance.
This message, however, means that no code generator was found for `ToString`.

`deriving instance`를 호출하면 Lean은 type class instance들에 대한 code generator들의 내부 테이블을 참고합니다.
Code generator가 발견되면, 제공된 타입에 대해 instance를 생성하도록 호출됩니다.
그러나 이 메시지는 `ToString`에 대한 code generator가 발견되지 않았다는 의미입니다.
