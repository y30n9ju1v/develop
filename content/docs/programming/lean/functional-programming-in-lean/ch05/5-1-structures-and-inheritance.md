---
title: "5.1. 구조체와 상속"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "구조체와 상속"
---

# 5.1. Structures and Inheritance

In order to understand the full definitions of `Functor`, `Applicative`, and `Monad`, another Lean feature is necessary: structure inheritance.
Structure inheritance allows one structure type to provide the interface of another, along with additional fields.
This can be useful when modeling concepts that have a clear taxonomic relationship.
For example, take a model of mythical creatures.
Some of them are large, and some are small:

`Functor`, `Applicative`, `Monad`의 완전한 정의를 이해하기 위해 또 다른 Lean의 기능이 필요합니다: structure inheritance입니다.
Structure inheritance를 사용하면 하나의 structure 타입이 다른 structure의 인터페이스를 제공할 수 있으며, 추가 필드도 함께 제공됩니다.
이는 명확한 분류학적 관계를 가진 개념을 모델링할 때 유용할 수 있습니다.
예를 들어, 신화 속의 생물들을 모델링한다고 가정해봅시다.
그들 중 일부는 크고, 일부는 작습니다:

```lean
structure MythicalCreature where
  large : Bool
deriving Repr
```

Behind the scenes, defining the `MythicalCreature` structure creates an inductive type with a single constructor called `mk`:

내부적으로 `MythicalCreature` structure를 정의하면 `mk`라는 단일 constructor를 가진 inductive type이 생성됩니다:

```lean
#check MythicalCreature.mk
```

```
MythicalCreature.mk (large : Bool) : MythicalCreature
```

Similarly, a function `MythicalCreature.large` is created that actually extracts the field from the constructor:

마찬가지로 constructor에서 필드를 추출하는 `MythicalCreature.large` 함수가 생성됩니다:

```lean
#check MythicalCreature.large
```

```
MythicalCreature.large (self : MythicalCreature) : Bool
```

In most old stories, each monster can be defeated in some way.
A description of a monster should include this information, along with whether it is large:

대부분의 옛날 이야기에서 각 괴물은 어떤 방식으로든 격퇴될 수 있습니다.
괴물의 설명에는 이 정보와 함께 그것이 큰지 여부도 포함되어야 합니다:

```lean
structure Monster extends MythicalCreature where
  vulnerability : String
deriving Repr
```

The `extends MythicalCreature` in the heading states that every monster is also mythical.
To define a `Monster`, both the fields from `MythicalCreature` and the fields from `Monster` should be provided.
A troll is a large monster that is vulnerable to sunlight:

제목의 `extends MythicalCreature`는 모든 괴물도 신화 속의 생물이라는 것을 나타냅니다.
`Monster`를 정의하려면 `MythicalCreature`의 필드와 `Monster`의 필드를 모두 제공해야 합니다.
트롤은 햇빛에 취약한 대형 괴물입니다:

```lean
def troll : Monster where
  large := true
  vulnerability := "sunlight"
```

Behind the scenes, inheritance is implemented using composition.
The constructor `Monster.mk` takes a `MythicalCreature` as its argument:

내부적으로 inheritance는 composition을 사용하여 구현됩니다.
`Monster.mk` constructor는 `MythicalCreature`를 인자로 받습니다:

```lean
#check Monster.mk
```

```
Monster.mk (toMythicalCreature : MythicalCreature) (vulnerability : String) : Monster
```

In addition to defining functions to extract the value of each new field, a function `Monster.toMythicalCreature` is defined with type `Monster → MythicalCreature`.
This can be used to extract the underlying creature.

각 새로운 필드의 값을 추출하는 함수를 정의하는 것 외에도, `Monster → MythicalCreature` 타입의 `Monster.toMythicalCreature` 함수가 정의됩니다.
이는 기본 생물을 추출하는 데 사용될 수 있습니다.

Moving up the inheritance hierarchy in Lean is not the same thing as upcasting in object-oriented languages.
An upcast operator causes a value from a derived class to be treated as an instance of the parent class, but the value retains its identity and structure.
In Lean, however, moving up the inheritance hierarchy actually erases the underlying information.
To see this in action, consider the result of evaluating `troll.toMythicalCreature`:

Lean에서 inheritance 계층을 올라가는 것은 객체 지향 언어의 upcasting과 다릅니다.
Upcast 연산자는 파생 클래스의 값을 부모 클래스의 인스턴스로 처리하게 하지만, 값은 자신의 정체성과 구조를 유지합니다.
하지만 Lean에서는 inheritance 계층을 올라가는 것이 실제로 기본 정보를 지우는 것입니다.
이를 실제로 보기 위해 `troll.toMythicalCreature`를 평가한 결과를 생각해봅시다:

```lean
#eval troll.toMythicalCreature
```

```
{ large := true }
```

Only the fields of `MythicalCreature` remain.

`MythicalCreature`의 필드만 남습니다.

Just like the `where` syntax, curly-brace notation with field names also works with structure inheritance:

`where` 문법처럼, 필드명이 있는 중괄호 표기법도 structure inheritance와 함께 작동합니다:

```lean
def troll : Monster := {large := true, vulnerability := "sunlight"}
```

However, the anonymous angle-bracket notation that delegates to the underlying constructor reveals the internal details:

하지만 기본 constructor로 위임하는 익명의 angle-bracket 표기법은 내부 세부 사항을 드러냅니다:

```lean
def troll : Monster := ⟨true, "sunlight"⟩
```

```
Application type mismatch: The argument
  true
has type
  Bool
but is expected to have type
  MythicalCreature
in the application
  Monster.mk true
```

An extra set of angle brackets is required, which invokes `MythicalCreature.mk` on `true`:

추가 angle brackets 세트가 필요하며, 이는 `true`에 대해 `MythicalCreature.mk`를 호출합니다:

```lean
def troll : Monster := ⟨⟨true⟩, "sunlight"⟩
```

Lean's dot notation is capable of taking inheritance into account.
In other words, the existing `MythicalCreature.large` can be used with a `Monster`, and Lean automatically inserts the call to `Monster.toMythicalCreature` before the call to `MythicalCreature.large`.
However, this only occurs when using dot notation, and applying the field lookup function using normal function call syntax results in a type error:

Lean의 dot notation은 inheritance를 고려할 수 있습니다.
다시 말해, 기존의 `MythicalCreature.large`를 `Monster`와 함께 사용할 수 있으며, Lean은 `MythicalCreature.large` 호출 전에 자동으로 `Monster.toMythicalCreature` 호출을 삽입합니다.
하지만 이는 dot notation을 사용할 때만 발생하며, 일반 함수 호출 문법을 사용하여 필드 조회 함수를 적용하면 타입 오류가 발생합니다:

```lean
#eval MythicalCreature.large troll
```

```
Application type mismatch: The argument
  troll
has type
  Monster
but is expected to have type
  MythicalCreature
in the application
  MythicalCreature.large troll
```

Dot notation can also take inheritance into account for user-defined functions.
A small creature is one that is not large:

Dot notation은 사용자 정의 함수에 대해서도 inheritance를 고려할 수 있습니다.
작은 생물은 크지 않은 생물입니다:

```lean
def MythicalCreature.small (c : MythicalCreature) : Bool := !c.large
```

Evaluating `troll.small` yields `false`, while attempting to evaluate `MythicalCreature.small troll` results in:

`troll.small`을 평가하면 `false`가 나오지만, `MythicalCreature.small troll`을 평가하려고 하면 다음과 같은 결과가 됩니다:

```
Application type mismatch: The argument
  troll
has type
  Monster
but is expected to have type
  MythicalCreature
in the application
  MythicalCreature.small troll
```

## 5.1.1. Multiple Inheritance

A helper is a mythical creature that can provide assistance when given the correct payment:

도우미는 올바른 보상을 받으면 도움을 제공할 수 있는 신화 속의 생물입니다:

```lean
structure Helper extends MythicalCreature where
  assistance : String
  payment : String
deriving Repr
```

For example, a *nisse* is a kind of small elf that's known to help around the house when provided with tasty porridge:

예를 들어, *nisse*는 맛있는 죽을 받으면 집 주변을 돕는 것으로 알려진 작은 요정의 일종입니다:

```lean
def nisse : Helper where
  large := false
  assistance := "household tasks"
  payment := "porridge"
```

If domesticated, trolls make excellent helpers.
They are strong enough to plow a whole field in a single night, though they require model goats to keep them satisfied with their lot in life.
A monstrous assistant is a monster that is also a helper:

길들여지면 트롤은 훌륭한 도우미가 됩니다.
그들은 한 밤 안에 온 들판을 갈 수 있을 정도로 강하지만, 자신의 상황에 만족하게 유지하기 위해 장난감 염소가 필요합니다.
흉한 도우미는 괴물이면서 동시에 도우미입니다:

```lean
structure MonstrousAssistant extends Monster, Helper where
deriving Repr
```

A value of this structure type must fill in all of the fields from both parent structures:

이 structure 타입의 값은 두 부모 structure의 모든 필드를 채워야 합니다:

```lean
def domesticatedTroll : MonstrousAssistant where
  large := true
  assistance := "heavy labor"
  payment := "toy goats"
  vulnerability := "sunlight"
```

Both of the parent structure types extend `MythicalCreature`.
If multiple inheritance were implemented naïvely, then this could lead to a “diamond problem”, where it would be unclear which path to `large` should be taken from a given `MonstrousAssistant`.
Should it take `large` from the contained `Monster` or from the contained `Helper`?
In Lean, the answer is that the first specified path to the grandparent structure is taken, and the additional parent structures' fields are copied rather than having the new structure include both parents directly.

두 부모 structure 타입 모두 `MythicalCreature`를 extends합니다.
만약 multiple inheritance가 순진하게 구현된다면, 주어진 `MonstrousAssistant`에서 어떤 `large` 경로를 취해야 할지가 불명확한 “diamond problem”이 발생할 수 있습니다.
포함된 `Monster`에서 `large`를 취해야 할까요, 아니면 포함된 `Helper`에서 취해야 할까요?
Lean에서 답은 grandparent structure로의 첫 번째 지정된 경로가 취해지며, 추가 부모 structure의 필드는 복사되고 새로운 structure이 두 부모를 직접 포함하지 않는다는 것입니다.

This can be seen by examining the signature of the constructor for `MonstrousAssistant`:

이는 `MonstrousAssistant`의 constructor 시그니처를 검토하면 알 수 있습니다:

```lean
#check MonstrousAssistant.mk
```

```
MonstrousAssistant.mk (toMonster : Monster) (assistance payment : String) : MonstrousAssistant
```

It takes a `Monster` as an argument, along with the two fields that `Helper` introduces on top of `MythicalCreature`.
Similarly, while `MonstrousAssistant.toMonster` merely extracts the `Monster` from the constructor, `MonstrousAssistant.toHelper` has no `Helper` to extract.
The `#print` command exposes its implementation:

이는 `MythicalCreature` 위에 `Helper`가 도입하는 두 필드와 함께 인자로 `Monster`를 받습니다.
마찬가지로, `MonstrousAssistant.toMonster`는 단순히 constructor에서 `Monster`를 추출하지만, `MonstrousAssistant.toHelper`는 추출할 `Helper`가 없습니다.
`#print` 명령은 그 구현을 드러냅니다:

```lean
#print MonstrousAssistant.toHelper
```

```
@[reducible] def MonstrousAssistant.toHelper : MonstrousAssistant → Helper :=
fun self => { toMythicalCreature := self.toMythicalCreature, assistance := self.assistance, payment := self.payment }
```

This function constructs a `Helper` from the fields of `MonstrousAssistant`.
The `@[reducible]` attribute has the same effect as writing `abbrev`.

이 함수는 `MonstrousAssistant`의 필드로부터 `Helper`를 구성합니다.
`@[reducible]` 속성은 `abbrev`를 작성하는 것과 동일한 효과를 가집니다.

### 5.1.1.1. Default Declarations

When one structure inherits from another, default field definitions can be used to instantiate the parent structure's fields based on the child structure's fields.
If more size specificity is required than whether a creature is large or not, a dedicated datatype describing sizes can be used together with inheritance, yielding a structure in which the `large` field is computed from the contents of the `size` field:

한 structure이 다른 structure으로부터 상속될 때, 기본 필드 정의를 사용하여 자식 structure의 필드를 기반으로 부모 structure의 필드를 인스턴스화할 수 있습니다.
생물이 크기가 크거나 작은 것보다 더 많은 크기 구체성이 필요한 경우, 크기를 설명하는 전용 datatype을 inheritance와 함께 사용할 수 있으며, 이는 `large` 필드가 `size` 필드의 내용으로부터 계산되는 structure를 생성합니다:

```lean
inductive Size where
  | small
  | medium
  | large
deriving BEq

structure SizedCreature extends MythicalCreature where
  size : Size
  large := size == Size.large
```

This default definition is only a default definition, however.
Unlike property inheritance in a language like C# or Scala, the definitions in the child structure are only used when no specific value for `large` is provided, and nonsensical results can occur:

하지만 이 기본 정의는 기본 정의일 뿐입니다.
C# 또는 Scala와 같은 언어의 property inheritance와 달리, 자식 structure의 정의는 `large`에 대한 특정 값이 제공되지 않을 때만 사용되며, 말이 안 되는 결과가 발생할 수 있습니다:

```lean
def nonsenseCreature : SizedCreature where
  large := false
  size := .large
```

If the child structure should not deviate from the parent structure, there are a few options:

자식 structure이 부모 structure에서 벗어나지 않아야 한다면, 몇 가지 옵션이 있습니다:

1. Documenting the relationship, as is done for `BEq` and `Hashable`
2. Defining a proposition that the fields are related appropriately, and designing the API to require evidence that the proposition is true where it matters
3. Not using inheritance at all

1. `BEq`와 `Hashable`에서처럼 관계를 문서화하기
2. 필드가 적절히 관련되어 있다는 proposition을 정의하고, 중요한 곳에서 그 proposition이 참임을 보여주는 증거를 요구하도록 API를 설계하기
3. inheritance를 사용하지 않기

The second option could look like this:

두 번째 옵션은 다음과 같이 보일 수 있습니다:

```lean
abbrev SizesMatch (sc : SizedCreature) : Prop :=
  sc.large = (sc.size == Size.large)
```

Note that a single equality sign is used to indicate the equality *proposition*, while a double equality sign is used to indicate a function that checks equality and returns a `Bool`.
`SizesMatch` is defined as an `abbrev` because it should automatically be unfolded in proofs, so that `decide` can see the equality that should be proven.

단일 등호 기호는 equality *proposition*을 나타내기 위해 사용되고, 이중 등호 기호는 동등성을 확인하고 `Bool`을 반환하는 함수를 나타내기 위해 사용됩니다.
`SizesMatch`는 `abbrev`로 정의되어 있으므로 증명에서 자동으로 펼쳐져서 `decide`가 증명되어야 할 동등성을 볼 수 있습니다.

A *huldre* is a medium-sized mythical creature—in fact, they are the same size as humans.
The two sized fields on `huldre` match one another:

*huldre*는 중간 크기의 신화 속의 생물입니다. 사실 그들은 인간과 같은 크기입니다.
`huldre`의 두 개의 크기 필드는 서로 일치합니다:

```lean
def huldre : SizedCreature where
  size := .medium

example : SizesMatch huldre := by
  decide
```

```
All goals completed! 🐙
```

### 5.1.1.2. Type Class Inheritance

Behind the scenes, type classes are structures.
Defining a new type class defines a new structure, and defining an instance creates a value of that structure type.
They are then added to internal tables in Lean that allow it to find the instances upon request.
A consequence of this is that type classes may inherit from other type classes.

내부적으로 type classes는 structures입니다.
새로운 type class를 정의하면 새로운 structure을 정의하는 것이고, instance를 정의하면 그 structure 타입의 값을 생성합니다.
이들은 Lean의 내부 테이블에 추가되어 요청 시 instances를 찾을 수 있게 합니다.
따라서 type classes는 다른 type classes로부터 상속될 수 있습니다.

Because it uses precisely the same language features, type class inheritance supports all the features of structure inheritance, including multiple inheritance, default implementations of parent types' methods, and automatic collapsing of diamonds.
This is useful in many of the same situations that multiple interface inheritance is useful in languages like Java, C# and Kotlin.
By carefully designing type class inheritance hierarchies, programmers can get the best of both worlds: a fine-grained collection of independently-implementable abstractions, and automatic construction of these specific abstractions from larger, more general abstractions.

정확히 동일한 언어 기능을 사용하기 때문에 type class inheritance는 multiple inheritance, 부모 타입의 메서드의 기본 구현, diamond의 자동 축소를 포함한 structure inheritance의 모든 기능을 지원합니다.
이는 Java, C#, Kotlin과 같은 언어에서 multiple interface inheritance가 유용한 많은 상황에서 도움이 됩니다.
type class inheritance 계층 구조를 신중하게 설계함으로써 프로그래머들은 양쪽의 장점을 모두 얻을 수 있습니다: 독립적으로 구현 가능한 세밀한 추상화 집합과, 더 큰 일반적 추상화로부터 이러한 특정 추상화를 자동으로 구성하는 능력입니다.
