---
title: "3.3. Instance Search 제어하기"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "output parameter와 default instance로 instance search 제어하기"
---

# 3.3. Controlling Instance Search

An instance of the `Add` class is sufficient to allow two expressions with type `Pos` to be conveniently added, producing another `Pos`.
However, in many cases, it can be useful to be more flexible and allow *heterogeneous* operator overloading, where the arguments may have different types.
For example, adding a `Nat` to a `Pos` or a `Pos` to a `Nat` will always yield a `Pos`:

`Add` 클래스의 instance는 `Pos` 타입을 가진 두 식을 편리하게 더해서 다른 `Pos`를 생성할 수 있게 하기에 충분합니다.
그러나 많은 경우에 더 유연하게 하고, 인자들이 다른 타입을 가질 수 있는 *heterogeneous* operator overloading을 허용하는 것이 유용할 수 있습니다.
예를 들어, `Nat`를 `Pos`에 더하거나 `Pos`를 `Nat`에 더하면 항상 `Pos`를 생성합니다:

```lean
def addNatPos : Nat → Pos → Pos
  | 0, p => p
  | n + 1, p => Pos.succ (addNatPos n p)
def addPosNat : Pos → Nat → Pos
  | p, 0 => p
  | p, n + 1 => Pos.succ (addPosNat p n)
```

These functions allow natural numbers to be added to positive numbers, but they cannot be used with the `Add` type class, which expects both arguments to `add` to have the same type.

이 함수들은 자연수를 양수에 더할 수 있게 하지만, `add`의 두 인자가 같은 타입을 가져야 한다고 기대하는 `Add` type class와 함께 사용될 수 없습니다.

## 3.3.1. Heterogeneous Overloadings

As mentioned in the section on [overloaded addition](../ch03/), Lean provides a type class called `HAdd` for overloading addition heterogeneously.
The `HAdd` class takes three type parameters: the two argument types and the return type.
Instances of `HAdd Nat Pos Pos` and `HAdd Pos Nat Pos` allow ordinary addition notation to be used to mix the types:

[overloaded addition](../ch03/) 섹션에서 언급했듯이, Lean은 heterogeneous하게 덧셈을 overload하기 위한 `HAdd`라는 type class를 제공합니다.
`HAdd` 클래스는 세 개의 type parameter를 가집니다: 두 개의 인자 타입과 반환 타입입니다.
`HAdd Nat Pos Pos`와 `HAdd Pos Nat Pos`의 instance들은 보통의 덧셈 표기법을 사용하여 타입들을 섞을 수 있게 합니다:

```lean
instance : HAdd Nat Pos Pos where
  hAdd := addNatPos
instance : HAdd Pos Nat Pos where
  hAdd := addPosNat
```

Given the above two instances, the following examples work:

```lean
#eval (3 : Pos) + (5 : Nat)
```

```
8
```

```lean
#eval (3 : Nat) + (5 : Pos)
```

```
8
```

The definition of the `HAdd` type class is very much like the following definition of `HPlus` with the corresponding instances:

`HAdd` type class의 정의는 다음의 해당 instance들을 포함한 `HPlus`의 정의와 매우 유사합니다:

```lean
class HPlus (α : Type) (β : Type) (γ : Type) where
  hPlus : α → β → γ
instance : HPlus Nat Pos Pos where
  hPlus := addNatPos
instance : HPlus Pos Nat Pos where
  hPlus := addPosNat
```

However, instances of `HPlus` are significantly less useful than instances of `HAdd`.
When attempting to use these instances with `#eval`, an error occurs:

그러나 `HPlus`의 instance들은 `HAdd`의 instance들보다 훨씬 덜 유용합니다.
이 instance들을 `#eval`과 함께 사용하려고 할 때, 오류가 발생합니다:

```lean
#eval toString (HPlus.hPlus (3 : Pos) (5 : Nat))
```

```
typeclass instance problem is stuck
  HPlus Pos Nat ?m.6

Note: Lean will not try to resolve this typeclass instance problem because the third type argument to `HPlus` is a metavariable. This argument must be fully determined before Lean will try to resolve the typeclass.

Hint: Adding type annotations and supplying implicit arguments to functions can give Lean more information for typeclass resolution. For example, if you have a variable `x` that you intend to be a `Nat`, but Lean reports it as having an unresolved type like `?m`, replacing `x` with `(x : Nat)` can get typeclass resolution un-stuck.
```

The message indicates that this happens because there is a metavariable in the type, and Lean has no way to solve it.

이 메시지는 타입에 metavariable이 있고 Lean이 이를 풀 수 없기 때문에 이런 일이 발생함을 나타냅니다.

As discussed in [the initial description of polymorphism](../ch01/), metavariables represent unknown parts of a program that could not be inferred.
When an expression is written following `#eval`, Lean attempts to determine its type automatically.
In this case, it could not.
Because the third type parameter for `HPlus` was unknown, Lean couldn't carry out type class instance search, but instance search is the only way that Lean could determine the expression's type.
That is, the `HPlus Pos Nat Pos` instance can only apply if the expression should have type `Pos`, but there's nothing in the program other than the instance itself to indicate that it should have this type.

[polymorphism의 초기 설명](../ch01/)에서 논의했듯이, metavariable들은 추론할 수 없었던 프로그램의 알 수 없는 부분을 나타냅니다.
`#eval` 다음에 식이 작성되면, Lean은 자동으로 그 타입을 결정하려고 시도합니다.
이 경우 그럴 수 없었습니다.
`HPlus`의 세 번째 type parameter가 알 수 없었기 때문에, Lean은 type class instance search를 수행할 수 없었지만, instance search는 Lean이 식의 타입을 결정할 수 있는 유일한 방법입니다.
즉, `HPlus Pos Nat Pos` instance는 식이 타입 `Pos`를 가져야 할 때만 적용될 수 있지만, instance 자신 외에 그것이 이 타입을 가져야 함을 나타내는 프로그램의 다른 것은 없습니다.

One solution to the problem is to ensure that all three types are available by adding a type annotation to the whole expression:

이 문제의 한 해결책은 전체 식에 type annotation을 추가하여 세 가지 타입 모두가 이용 가능하도록 하는 것입니다:

```lean
#eval (HPlus.hPlus (3 : Pos) (5 : Nat) : Pos)
```

```
8
```

However, this solution is not very convenient for users of the positive number library.

그러나 이 해결책은 양수 라이브러리 사용자들에게 매우 편리하지는 않습니다.

## 3.3.2. Output Parameters

This problem can also be solved by declaring `γ` to be an *output parameter*.
Most type class parameters are inputs to the search algorithm: they are used to select an instance.
For example, in an `OfNat` instance, both the type and the natural number are used to select a particular interpretation of a natural number literal.
However, in some cases, it can be convenient to start the search process even when some of the type parameters are not yet known, and use the instances that are discovered in the search to determine values for metavariables.
The parameters that aren't needed to start instance search are outputs of the process, which is declared with the `outParam` modifier:

이 문제는 `γ`를 *output parameter*로 선언하여 해결할 수도 있습니다.
대부분의 type class parameter들은 search algorithm의 입력입니다: instance를 선택하는 데 사용됩니다.
예를 들어, `OfNat` instance에서, 타입과 자연수 모두 자연수 literal의 특정 해석을 선택하는 데 사용됩니다.
그러나 어떤 경우에는, 일부 type parameter들이 아직 알려지지 않았을 때에도 search process를 시작하는 것이 편할 수 있고, search에서 발견된 instance들을 사용하여 metavariable들의 값을 결정할 수 있습니다.
instance search를 시작하는 데 필요하지 않은 parameter들은 process의 출력이며, `outParam` modifier로 선언됩니다:

```lean
class HPlus (α : Type) (β : Type) (γ : outParam Type) where
  hPlus : α → β → γ
```

With this output parameter, type class instance search is able to select an instance without knowing `γ` in advance.
For instance:

이 output parameter를 사용하면, type class instance search는 미리 `γ`를 알지 못한 채 instance를 선택할 수 있습니다.
예를 들어:

```lean
#eval HPlus.hPlus (3 : Pos) (5 : Nat)
```

```
8
```

It might be helpful to think of output parameters as defining a kind of function.
Any given instance of a type class that has one or more output parameters provides Lean with instructions for determining the outputs from the inputs.
The process of searching for an instance, possibly recursively, ends up being more powerful than mere overloading.
Output parameters can determine other types in the program, and instance search can assemble a collection of underlying instances into a program that has this type.

output parameter들을 일종의 함수를 정의하는 것으로 생각하는 것이 도움이 될 수 있습니다.
하나 이상의 output parameter를 가진 type class의 어떤 instance든지 Lean에 입력에서 출력을 결정하는 방법에 대한 지시를 제공합니다.
instance를 검색하는 과정(아마도 재귀적으로)은 단순한 overloading보다 더 강력하게 끝납니다.
Output parameter들은 프로그램의 다른 타입들을 결정할 수 있고, instance search는 기초가 되는 instance들의 모음을 이 타입을 가진 프로그램으로 조립할 수 있습니다.

## 3.3.3. Default Instances

Deciding whether a parameter is an input or an output controls the circumstances under which Lean will initiate type class search.
In particular, type class search does not occur until all inputs are known.
However, in some cases, output parameters are not enough, and instance search should also occur when some inputs are unknown.
This is a bit like default values for optional function arguments in Python or Kotlin, except default *types* are being selected.

parameter가 입력인지 출력인지 결정하는 것은 Lean이 type class search를 시작할 조건을 제어합니다.
특히, type class search는 모든 입력이 알려질 때까지 발생하지 않습니다.
그러나 어떤 경우에는 output parameter들만으로는 충분하지 않으며, instance search는 일부 입력이 알 수 없을 때도 발생해야 합니다.
이는 Python이나 Kotlin의 선택 함수 인자에 대한 기본값과 비슷하지만, 기본 *타입*이 선택되고 있다는 점을 제외하고는 말입니다.

*Default instances* are instances that are available for instance search *even when not all their inputs are known*.
When one of these instances can be used, it will be used.
This can cause programs to successfully type check, rather than failing with errors related to unknown types and metavariables.
On the other hand, default instances can make instance selection less predictable.
In particular, if an undesired default instance is selected, then an expression may have a different type than expected, which can cause confusing type errors to occur elsewhere in the program.
Be selective about where default instances are used!

*Default instance*는 모든 입력이 알려지지 않았을 때에도 instance search에 이용 가능한 instance들입니다.
이 instance들 중 하나를 사용할 수 있으면, 사용됩니다.
이로 인해 프로그램들은 알 수 없는 타입과 metavariable들과 관련된 오류로 실패하는 대신 성공적으로 type check될 수 있습니다.
한편, default instance들은 instance selection을 덜 예측 가능하게 할 수 있습니다.
특히, 원하지 않은 default instance가 선택되면, 식이 예상과 다른 타입을 가질 수 있고, 이는 프로그램의 다른 곳에서 혼동스러운 type error들이 발생할 수 있습니다.
default instance들이 사용되는 곳에 대해 선택적으로 접근하세요!

One example of where default instances can be useful is an instance of `HPlus` that can be derived from an `Add` instance.
In other words, ordinary addition is a special case of heterogeneous addition in which all three types happen to be the same.
This can be implemented using the following instance:

default instance들이 유용할 수 있는 한 가지 예는 `Add` instance에서 도출될 수 있는 `HPlus`의 instance입니다.
다시 말해, 보통의 덧셈은 세 가지 타입이 모두 같은 heterogeneous addition의 특수한 경우입니다.
이는 다음 instance를 사용하여 구현될 수 있습니다:

```lean
instance [Add α] : HPlus α α α where
  hPlus := Add.add
```

With this instance, `hPlus` can be used for any addable type, like `Nat`:

이 instance를 사용하면, `hPlus`는 `Nat`처럼 addable인 모든 타입에 사용될 수 있습니다:

```lean
#eval HPlus.hPlus (3 : Nat) (5 : Nat)
```

```
8
```

However, this instance will only be used in situations where the types of both arguments are known.
For example,

그러나 이 instance는 두 인자의 타입이 모두 알려진 상황에서만 사용됩니다.
예를 들어,

```lean
#check HPlus.hPlus (5 : Nat) (3 : Nat)
```

yields the type

```
HPlus.hPlus 5 3 : Nat
```

as expected, but

```lean
#check HPlus.hPlus (5 : Nat)
```

yields a type that contains two metavariables, one for the remaining argument and one for the return type:

대부분의 경우, 누군가 덧셈에 한 인자를 제공할 때, 다른 인자는 같은 타입을 가질 것입니다.
이 instance를 default instance로 만들려면, `default_instance` attribute를 적용하세요:

```
HPlus.hPlus 5 : ?m.2 → ?m.3
```

```lean
@[default_instance]
instance [Add α] : HPlus α α α where
  hPlus := Add.add
```

In the vast majority of cases, when someone supplies one argument to addition, the other argument will have the same type.
To make this instance into a default instance, apply the `default_instance` attribute:

With this default instance, the example has a more useful type:

이 default instance를 사용하면, 예시는 더 유용한 타입을 가집니다:

```lean
#check HPlus.hPlus (5 : Nat)
```

yields

```
HPlus.hPlus 5 : Nat → Nat
```

Each operator that exists in overloadable heterogeneous and homogeneous versions follows the pattern of a default instance that allows the homogeneous version to be used in contexts where the heterogeneous is expected.
The infix operator is replaced with a call to the heterogeneous version, and the homogeneous default instance is selected when possible.

overloadable heterogeneous과 homogeneous 버전으로 존재하는 각 operator는 heterogeneous가 예상되는 context에서 homogeneous 버전을 사용할 수 있게 하는 default instance의 패턴을 따릅니다.
infix operator는 heterogeneous 버전의 호출로 대체되고, homogeneous default instance는 가능할 때 선택됩니다.

Similarly, simply writing `5` gives a `Nat` rather than a type with a metavariable that is waiting for more information in order to select an `OfNat` instance.
This is because the `OfNat` instance for `Nat` is a default instance.

유사하게, 단순히 `5`를 작성하는 것은 `OfNat` instance를 선택하기 위해 더 많은 정보를 기다리는 metavariable을 가진 타입이 아니라 `Nat`을 제공합니다.
이는 `Nat`에 대한 `OfNat` instance가 default instance이기 때문입니다.

Default instances can also be assigned *priorities* that affect which will be chosen in situations where more than one might apply.
For more information on default instance priorities, please consult the Lean manual.

Default instance들은 또한 하나 이상이 적용될 수 있는 상황에서 어느 것이 선택될지에 영향을 미치는 *priority*를 할당할 수 있습니다.
default instance priority에 대한 더 많은 정보를 원하면, Lean 매뉴얼을 참고하세요.

## 3.3.4. Exercises

Define an instance of `HMul (PPoint α) α (PPoint α)` that multiplies both projections by the scalar.
It should work for any type `α` for which there is a `Mul α` instance.
For example,

두 projection을 scalar로 곱하는 `HMul (PPoint α) α (PPoint α)`의 instance를 정의합니다.
`Mul α` instance가 있는 모든 타입 `α`에 대해 작동해야 합니다.
예를 들어,

```lean
#eval {x := 2.5, y := 3.7 : PPoint Float} * 2.0
```

should yield

```
{ x := 5.000000, y := 7.400000 }
```
