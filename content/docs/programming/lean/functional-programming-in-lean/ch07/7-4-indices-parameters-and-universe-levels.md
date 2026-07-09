---
title: "7.4. 인덱스, 파라미터, 유니버스 레벨 (Indices, Parameters, and Universe Levels)"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "인덱스, 파라미터, 유니버스 레벨 (Indices, Parameters, and Universe Levels)"
---

# 7.4. Indices, Parameters, and Universe Levels

The distinction between indices and parameters of an inductive type is more than just a way to describe arguments to the type that either vary or do not between the constructors.
Whether an argument to an inductive type is a parameter or an index also matters when it comes time to determine the relationships between their universe levels.
In particular, an inductive type may have the same universe level as a parameter, but it must be in a larger universe than its indices.
This restriction is necessary to ensure that Lean can be used as a theorem prover as well as a programming language—without it, Lean's logic would be inconsistent.
Experimenting with error messages is a good way to illustrate these rules, as well as the precise rules that determine whether an argument to a type is a parameter or an index.

귀납 타입의 인덱스와 파라미터의 구분은 생성자 간에 변하거나 변하지 않는 타입에 대한 인수를 설명하는 방식 이상의 의미를 가집니다.
귀납 타입의 인수가 파라미터인지 인덱스인지 여부는 유니버스 레벨 간의 관계를 결정할 때도 중요합니다.
특히, 귀납 타입은 파라미터와 동일한 유니버스 레벨을 가질 수 있지만, 인덱스보다는 더 큰 유니버스에 있어야 합니다.
이 제한은 Lean을 정리 증명기뿐만 아니라 프로그래밍 언어로 사용할 수 있도록 보장하기 위해 필요합니다—이것이 없으면 Lean의 논리는 일관성이 없을 것입니다.
오류 메시지를 실험하는 것은 이러한 규칙뿐만 아니라 인수가 파라미터인지 인덱스인지를 결정하는 정확한 규칙을 설명하는 좋은 방법입니다.

Generally speaking, the definition of an inductive type takes its parameters before a colon and its indices after the colon.
Parameters are given names like function arguments, whereas indices only have their types described.
This can be seen in the definition of `Vect`:

일반적으로, 귀납 타입의 정의는 콜론 전에 파라미터를 취하고 콜론 후에 인덱스를 취합니다.
파라미터는 함수 인수처럼 이름이 주어지는 반면, 인덱스는 타입만 설명됩니다.
이는 `Vect`의 정의에서 볼 수 있습니다:

```lean
inductive Vect (α : Type u) : Nat → Type u where
  | nil : Vect α 0
  | cons : α → Vect α n → Vect α (n + 1)
```

In this definition, `α` is a parameter and the `Nat` is an index.
Parameters may be referred to throughout the definition (for example, `Vect.cons` uses `α` for the type of its first argument), but they must always be used consistently.
Because indices are expected to change, they are assigned individual values at each constructor, rather than being provided as arguments at the top of the datatype definition.

이 정의에서 `α`는 파라미터이고 `Nat`은 인덱스입니다.
파라미터는 정의 전체에서 참조될 수 있습니다(예를 들어, `Vect.cons`는 첫 인수의 타입으로 `α`를 사용합니다). 그러나 항상 일관되게 사용되어야 합니다.
인덱스는 변경될 것으로 예상되기 때문에, 데이터타입 정의의 최상단에서 인수로 제공되기보다는 각 생성자에서 개별 값이 할당됩니다.

A very simple datatype with a parameter is `WithParameter`:

```lean
inductive WithParameter (α : Type u) : Type u where
  | test : α → WithParameter α
```

파라미터를 가진 매우 간단한 데이터타입은 `WithParameter`입니다.

유니버스 레벨 `u`는 파라미터와 귀납 타입 자체 모두에 사용될 수 있으며, 이는 파라미터가 데이터타입의 유니버스 레벨을 증가시키지 않음을 보여줍니다.

The universe level `u` can be used for both the parameter and for the inductive type itself, illustrating that parameters do not increase the universe level of a datatype.
Similarly, when there are multiple parameters, the inductive type receives whichever universe level is greater:

```lean
inductive WithTwoParameters (α : Type u) (β : Type v) : Type (max u v) where
  | test : α → β → WithTwoParameters α β
```

마찬가지로 여러 파라미터가 있을 때, 귀납 타입은 더 큰 유니버스 레벨을 받습니다.

Because parameters do not increase the universe level of a datatype, they can be more convenient to work with.
Lean attempts to identify arguments that are described like indices (after the colon), but used like parameters, and turn them into parameters:
Both of the following inductive datatypes have their parameter written after the colon:

파라미터가 데이터타입의 유니버스 레벨을 증가시키지 않기 때문에, 작업하기 더 편할 수 있습니다.
Lean은 인덱스처럼 설명되지만(콜론 후) 파라미터처럼 사용되는 인수를 식별하고 이를 파라미터로 변환하려고 시도합니다:
다음의 귀납 데이터타입 모두 콜론 후에 파라미터가 작성되어 있습니다:

```lean
inductive WithParameterAfterColon : Type u → Type u where
  | test : α → WithParameterAfterColon α
```

```lean
inductive WithParameterAfterColon2 : Type u → Type u where
  | test1 : α → WithParameterAfterColon2 α
  | test2 : WithParameterAfterColon2 α
```

When a parameter is not named in the initial datatype declaration, different names may be used for it in each constructor, so long as they are used consistently.
The following declaration is accepted:

파라미터가 초기 데이터타입 선언에서 이름이 지정되지 않으면, 각 생성자에서 다양한 이름을 사용할 수 있습니다. 단, 일관되게 사용되어야 합니다.
다음 선언이 수락됩니다:

```lean
inductive WithParameterAfterColonDifferentNames : Type u → Type u where
  | test1 : α → WithParameterAfterColonDifferentNames α
  | test2 : β → WithParameterAfterColonDifferentNames β
```

However, this flexibility does not extend to datatypes that explicitly declare the names of their parameters:

그러나 이 유연성은 명시적으로 파라미터 이름을 선언하는 데이터타입으로 확장되지 않습니다:

```lean
inductive WithParameterBeforeColonDifferentNames (α : Type u) : Type u where
  | test1 : α → WithParameterBeforeColonDifferentNames α
  | test2 : β → WithParameterBeforeColonDifferentNames β
```

```
Mismatched inductive type parameter in
  WithParameterBeforeColonDifferentNames β
The provided argument
  β
is not definitionally equal to the expected parameter
  α

Note: The value of parameter `α` must be fixed throughout the inductive declaration. Consider making this parameter an index if it must vary.
```

Similarly, attempting to name an index results in an error:

마찬가지로 인덱스 이름을 지정하려고 하면 오류가 발생합니다:

```lean
inductive WithNamedIndex (α : Type u) : Type (u + 1) where
  | test1 : WithNamedIndex α
  | test2 : WithNamedIndex α → WithNamedIndex α → WithNamedIndex (α × α)
```

```
Mismatched inductive type parameter in
  WithNamedIndex (α × α)
The provided argument
  α × α
is not definitionally equal to the expected parameter
  α

Note: The value of parameter `α` must be fixed throughout the inductive declaration. Consider making this parameter an index if it must vary.
```

Using an appropriate universe level and placing the index after the colon results in a declaration that is acceptable:

적절한 유니버스 레벨을 사용하고 인덱스를 콜론 뒤에 배치하면 수락할 수 있는 선언이 됩니다:

```lean
inductive WithIndex : Type u → Type (u + 1) where
  | test1 : WithIndex α
  | test2 : WithIndex α → WithIndex α → WithIndex (α × α)
```

Even though Lean can sometimes determine that an argument after the colon in an inductive type declaration is a parameter when it is used consistently in all constructors, all parameters are still required to come before all indices.
Attempting to place a parameter after an index results in the argument being considered an index itself, which would require the universe level of the datatype to increase:

Lean이 귀납 타입 선언에서 콜론 뒤의 인수가 모든 생성자에서 일관되게 사용될 때 파라미터라고 판단할 수 있더라도, 모든 파라미터는 여전히 모든 인덱스 앞에 와야 합니다.
파라미터를 인덱스 뒤에 배치하려고 하면 인수가 자체적으로 인덱스로 간주되어 데이터타입의 유니버스 레벨을 증가시켜야 합니다:

```lean
inductive ParamAfterIndex : Nat → Type u → Type u where
  | test1 : ParamAfterIndex 0 γ
  | test2 : ParamAfterIndex n γ → ParamAfterIndex k γ → ParamAfterIndex (n + k) γ
```

```
Invalid universe level in constructor `ParamAfterIndex.test1`: Parameter `γ` has type
  Type u
at universe level
  u+2
which is not less than or equal to the inductive type's resulting universe level
  u+1
```

Parameters need not be types.
This example shows that ordinary datatypes such as `Nat` may be used as parameters:

파라미터가 반드시 타입일 필요는 없습니다.
이 예제는 `Nat`과 같은 일반 데이터타입이 파라미터로 사용될 수 있음을 보여줍니다:

```lean
inductive NatParam (n : Nat) : Nat → Type u where
  | five : NatParam 4 5
```

```
Mismatched inductive type parameter in
  NatParam 4 5
The provided argument
  4
is not definitionally equal to the expected parameter
  n

Note: The value of parameter `n` must be fixed throughout the inductive declaration. Consider making this parameter an index if it must vary.
```

Using the `n` as suggested causes the declaration to be accepted:

제안한 대로 `n`을 사용하면 선언이 수락됩니다:

```lean
inductive NatParam (n : Nat) : Nat → Type u where
  | five : NatParam n 5
```

What can be concluded from these experiments?
The rules of parameters and indices are as follows:

1. Parameters must be used identically in each constructor's type.
2. All parameters must come before all indices.
3. The universe level of the datatype being defined must be at least as large as the largest parameter, and strictly larger than the largest index.
4. Named arguments written before the colon are always parameters, while arguments after the colon are typically indices. Lean may determine that the usage of arguments after the colon makes them into parameters if they are used consistently in all constructors and don't come after any indices.

이 실험들로부터 무엇을 결론 지을 수 있을까요?
파라미터와 인덱스의 규칙은 다음과 같습니다:

1. 파라미터는 각 생성자의 타입에서 동일하게 사용되어야 합니다.
2. 모든 파라미터는 모든 인덱스 앞에 와야 합니다.
3. 정의되는 데이터타입의 유니버스 레벨은 최소한 가장 큰 파라미터만큼 커야 하며, 가장 큰 인덱스보다 훨씬 더 커야 합니다.
4. 콜론 앞에 작성된 명명된 인수는 항상 파라미터이며, 콜론 뒤의 인수는 일반적으로 인덱스입니다. Lean은 콜론 뒤의 인수 사용이 모든 생성자에서 일관되게 사용되고 어떤 인덱스 뒤에도 오지 않는 경우 이들을 파라미터로 만드는 것으로 판단할 수 있습니다.

When in doubt, the Lean command `#print` can be used to check how many of a datatype's arguments are parameters.
For example, for `Vect`, it points out that the number of parameters is 1:

의심스러울 때, Lean 명령 `#print`를 사용하여 데이터타입의 인수 중 몇 개가 파라미터인지 확인할 수 있습니다.
예를 들어, `Vect`의 경우, 파라미터의 개수가 1임을 나타냅니다:

```lean
#print Vect
```

```
inductive Vect.{u} : Type u → Nat → Type u
number of parameters: 1
constructors:
Vect.nil : {α : Type u} → Vect α 0
Vect.cons : {α : Type u} → {n : Nat} → α → Vect α n → Vect α (n + 1)
```

It is worth thinking about which arguments should be parameters and which should be indices when choosing the order of arguments to a datatype.
Having as many arguments as possible be parameters helps keep universe levels under control, which can make a complicated program easier to type check.
One way to make this possible is to ensure that all parameters come before all indices in the argument list.

데이터타입의 인수 순서를 선택할 때 어떤 인수가 파라미터이어야 하고 어떤 인수가 인덱스이어야 하는지 생각할 가치가 있습니다.
가능한 한 많은 인수가 파라미터가 되도록 하면 유니버스 레벨을 제어하에 유지할 수 있으며, 이는 복잡한 프로그램을 더 쉽게 타입 체크할 수 있게 합니다.
이를 가능하게 하는 한 가지 방법은 인수 목록의 모든 파라미터가 모든 인덱스 앞에 오도록 하는 것입니다.

Additionally, even though Lean is capable of determining that arguments after the colon are nonetheless parameters by their usage, it's a good idea to write parameters with explicit names.
This makes the intention clear to readers, and it causes Lean to report an error if the argument is mistakenly used inconsistently across the constructors.

또한, Lean이 콜론 뒤의 인수가 사용에 의해 파라미터라는 것을 결정할 수 있더라도, 명시적 이름으로 파라미터를 작성하는 것이 좋습니다.
이는 읽는 사람에게 의도를 명확하게 하고, 인수가 생성자 전체에서 실수로 일관되지 않게 사용되는 경우 Lean이 오류를 보고하도록 합니다.
