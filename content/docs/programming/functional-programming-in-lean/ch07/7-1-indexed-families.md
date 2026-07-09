---
title: "Indexed Families"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Indexed Families"
---

# 7.1. Indexed Families

Polymorphic inductive types take type arguments.
For instance, `List` takes an argument that determines the type of the entries in the list, and `Except` takes arguments that determine the types of the exceptions or values.
These type arguments, which are the same in every constructor of the datatype, are referred to as *parameters*.

다형성 inductive types은 타입 인자를 가집니다.
예를 들어, `List`는 리스트의 항목 타입을 결정하는 인자를 가지고, `Except`는 예외 또는 값의 타입을 결정하는 인자를 가집니다.
데이터타입의 모든 생성자에서 동일한 이러한 타입 인자를 *parameters*라고 합니다.

Arguments to inductive types need not be the same in every constructor, however.
Inductive types in which the arguments to the type vary based on the choice of constructor are called *indexed families*, and the arguments that vary are referred to as *indices*.
The “hello world” of indexed families is a type of lists that contains the length of the list in addition to the type of entries, conventionally referred to as “vectors”:

그러나 inductive types의 인자는 모든 생성자에서 동일할 필요가 없습니다.
생성자 선택에 따라 타입 인자가 변하는 inductive types을 *indexed families*라고 하며, 변하는 인자를 *indices*라고 합니다.
Indexed families의 “hello world”는 항목 타입뿐만 아니라 리스트의 길이도 포함하는 리스트 타입으로, 관례적으로 “vectors”라고 불립니다:

`inductive Vect (α : Type u) : Nat → Type u where
| nil : Vect α 0
| cons : α → Vect α n → Vect α (n + 1)`

The type of a vector of three `String`s includes the fact that it contains three `String`s:

세 개의 `String`의 vector 타입은 그것이 세 개의 `String`을 포함한다는 사실을 포함합니다:

`example : Vect String 3 :=
.cons "one" (.cons "two" (.cons "three" .nil))`

Function declarations may take some arguments before the colon, indicating that they are available in the entire definition, and some arguments after, indicating a desire to pattern-match on them and define the function case by case.
Inductive datatypes have a similar principle: the argument `α` is named at the top of the datatype declaration, prior to the colon, which indicates that it is a parameter that must be provided as the first argument in all occurrences of `Vect` in the definition, while the `Nat` argument occurs after the colon, indicating that it is an index that may vary.
Indeed, the three occurrences of `Vect` in the `nil` and `cons` constructor declarations consistently provide `α` as the first argument, while the second argument is different in each case.

함수 선언은 콜론 전에 일부 인자를 가질 수 있으며, 이는 정의 전체에서 사용 가능함을 나타내고, 일부 인자는 콜론 후에 오며, 이는 패턴 매칭을 하고 함수를 경우별로 정의하려는 의도를 나타냅니다.
Inductive datatypes은 유사한 원칙을 가집니다: 인자 `α`는 데이터타입 선언의 맨 위에 콜론 전에 명명되어 있으며, 이는 정의의 모든 `Vect` 발생에서 첫 번째 인자로 제공되어야 하는 parameter임을 나타내고, `Nat` 인자는 콜론 후에 나타나 이것이 변할 수 있는 index임을 나타냅니다.
실제로, `nil`과 `cons` 생성자 선언의 `Vect` 세 개 발생은 일관되게 `α`를 첫 번째 인자로 제공하는 반면, 두 번째 인자는 각 경우에 다릅니다.

The declaration of `nil` states that it is a constructor of type `Vect α 0`.
This means that using `Vect.nil` in a context expecting a `Vect String 3` is a type error, just as `[1, 2, 3]` is a type error in a context that expects a `List String`:

`nil`의 선언은 그것이 `Vect α 0` 타입의 생성자임을 나타냅니다.
이는 `Vect String 3`을 기대하는 문맥에서 `Vect.nil`을 사용하는 것이 타입 에러라는 의미이며, `List String`을 기대하는 문맥에서 `[1, 2, 3]`이 타입 에러인 것과 같습니다:

`example : Vect String 3 := Type mismatch
Vect.nil
has type
Vect ?m.3 0
but is expected to have type
Vect String 3Vect.nil`

```
Type mismatch
  Vect.nil
has type
  Vect ?m.3 0
but is expected to have type
  Vect String 3
```

The mismatch between `0` and `3` in this example plays exactly the same role as any other type mismatch, even though `0` and `3` are not themselves types.
The metavariable in the message can be ignored because its presence indicates that `Vect.nil` can have any element type.

이 예제의 `0`과 `3` 사이의 불일치는 `0`과 `3`이 타입 자체가 아니더라도 다른 타입 불일치와 정확히 같은 역할을 합니다.
메시지의 metavariable은 무시할 수 있으며, 그 존재는 `Vect.nil`이 어떤 element type이든 가질 수 있음을 나타냅니다.

Indexed families are called *families* of types because different index values can make different constructors available for use.
In some sense, an indexed family is not a type; rather, it is a collection of related types, and the choice of index values also chooses a type from the collection.
Choosing the index `5` for `Vect` means that only the constructor `cons` is available, and choosing the index `0` means that only `nil` is available.

Indexed families는 다른 index 값이 사용 가능한 생성자들을 다르게 만들 수 있기 때문에 타입의 *families*라고 불립니다.
어떤 의미에서 indexed family는 타입이 아니라, 관련된 타입들의 모음이며, index 값의 선택은 또한 모음에서 타입을 선택합니다.
`Vect`에 대해 index `5`를 선택하는 것은 `cons` 생성자만 사용 가능함을 의미하고, index `0`을 선택하는 것은 `nil`만 사용 가능함을 의미합니다.

If the index is not yet known (e.g. because it is a variable), then no constructor can be used until it becomes known.
Using `n` for the length allows neither `Vect.nil` nor `Vect.cons`, because there's no way to know whether the variable `n` should stand for a `Nat` that matches `0` or `n + 1`:

Index가 아직 알려지지 않았다면 (예를 들어 변수이기 때문에), 그것이 알려질 때까지 어떤 생성자도 사용할 수 없습니다.
길이에 `n`을 사용하면 `Vect.nil`과 `Vect.cons` 모두 허용되지 않습니다. 왜냐하면 변수 `n`이 `0`과 일치하는 `Nat`을 나타내야 하는지 `n + 1`을 나타내야 하는지 알 수 없기 때문입니다:

`example : Vect String n := Type mismatch
Vect.nil
has type
Vect ?m.2 0
but is expected to have type
Vect String nVect.nil`

```
Type mismatch
  Vect.nil
has type
  Vect ?m.2 0
but is expected to have type
  Vect String n
```

`example : Vect String n := Type mismatch
Vect.cons "Hello" (Vect.cons "world" Vect.nil)
has type
Vect String (0 + 1 + 1)
but is expected to have type
Vect String nVect.cons "Hello" (Vect.cons "world" Vect.nil)`

```
Type mismatch
  Vect.cons "Hello" (Vect.cons "world" Vect.nil)
has type
  Vect String (0 + 1 + 1)
but is expected to have type
  Vect String n
```

Having the length of the list as part of its type means that the type becomes more informative.
For example, `Vect.replicate` is a function that creates a `Vect` with a number of copies of a given value.
The type that says this precisely is:

리스트의 길이를 타입의 일부로 가지는 것은 타입을 더욱 정보적이게 만들어 줍니다.
예를 들어, `Vect.replicate`는 주어진 값의 복사본 여러 개를 가진 `Vect`를 생성하는 함수입니다.
이를 정확히 나타내는 타입은:

`def Vect.replicate (n : Nat) (x : α) : Vect α n := don't know how to synthesize placeholder
context:
α:Type u_1n:Natx:α⊢ Vect α n_`

The argument `n` appears as the length of the result.
The message associated with the underscore placeholder describes the task at hand:

인자 `n`은 결과의 길이로 나타납니다.
underscore placeholder와 관련된 메시지는 현재 작업을 설명합니다:

```
don't know how to synthesize placeholder
context:
α:Type u_1n:Natx:α⊢ Vect α n
```

When working with indexed families, constructors can only be applied when Lean can see that the constructor's index matches the index in the expected type.
However, neither constructor has an index that matches `n`—`nil` matches `Nat.zero`, and `cons` matches `Nat.succ`.
Just as in the example type errors, the variable `n` could stand for either, depending on which `Nat` is provided to the function as an argument.
The solution is to use pattern matching to consider both of the possible cases:

Indexed families를 다룰 때, 생성자는 Lean이 생성자의 index가 예상 타입의 index와 일치함을 볼 수 있을 때만 적용할 수 있습니다.
그러나 어떤 생성자도 `n`과 일치하는 index를 가지지 않습니다—`nil`은 `Nat.zero`와 일치하고, `cons`는 `Nat.succ`과 일치합니다.
예제 타입 에러와 마찬가지로, 변수 `n`은 함수에 인자로 제공되는 `Nat`에 따라 둘 중 하나를 나타낼 수 있습니다.
해결책은 패턴 매칭을 사용하여 가능한 두 경우를 모두 고려하는 것입니다:

`def Vect.replicate (n : Nat) (x : α) : Vect α n :=
match n with
| 0 => don't know how to synthesize placeholder
context:
α:Type u_1n:Natx:α⊢ Vect α 0_
| k + 1 => don't know how to synthesize placeholder
context:
α:Type u_1n:Natx:αk:Nat⊢ Vect α (k + 1)_`

Because `n` occurs in the expected type, pattern matching on `n` *refines* the expected type in the two cases of the match.
In the first underscore, the expected type has become `Vect α 0`:

```
don't know how to synthesize placeholder
context:
α:Type u_1n:Natx:α⊢ Vect α 0
```

In the second underscore, it has become `Vect α (k + 1)`:

```
don't know how to synthesize placeholder
context:
α:Type u_1n:Natx:αk:Nat⊢ Vect α (k + 1)
```

When pattern matching refines the type of a program in addition to discovering the structure of a value, it is called *dependent pattern matching*.

`n`이 예상 타입에 나타나므로, `n`에 대한 패턴 매칭은 match의 두 경우에서 예상 타입을 *refines*합니다.
첫 번째 underscore에서 예상 타입은 `Vect α 0`이 되었습니다.

두 번째 underscore에서는 `Vect α (k + 1)`이 되었습니다.

패턴 매칭이 값의 구조를 발견하는 것 외에도 프로그램의 타입을 refine할 때, 그것을 *dependent pattern matching*이라고 합니다.

The refined type makes it possible to apply the constructors.
The first underscore matches `Vect.nil`, and the second matches `Vect.cons`:

`def Vect.replicate (n : Nat) (x : α) : Vect α n :=
match n with
| 0 => .nil
| k + 1 => .cons don't know how to synthesize placeholder
context:
α:Type u_1n:Natx:αk:Nat⊢ α_ don't know how to synthesize placeholder
context:
α:Type u_1n:Natx:αk:Nat⊢ Vect α k_`

The first underscore under the `.cons` should have type `α`.
There is an `α` available, namely `x`:

```
don't know how to synthesize placeholder
context:
α:Type u_1n:Natx:αk:Nat⊢ α
```

The second underscore should be a `Vect α k`, which can be produced by a recursive call to `replicate`:

```
don't know how to synthesize placeholder
context:
α:Type u_1n:Natx:αk:Nat⊢ Vect α k
```

Refined type은 생성자를 적용할 수 있게 만듭니다.
첫 번째 underscore는 `Vect.nil`과 일치하고, 두 번째는 `Vect.cons`와 일치합니다.

`.cons` 아래의 첫 번째 underscore는 `α` 타입을 가져야 합니다.
사용 가능한 `α`가 있습니다. 바로 `x`입니다.

두 번째 underscore는 `Vect α k`여야 하며, 이는 `replicate`에 대한 재귀 호출로 생성할 수 있습니다.

Here is the final definition of `replicate`:

`def Vect.replicate (n : Nat) (x : α) : Vect α n :=
match n with
| 0 => .nil
| k + 1 => .cons x (replicate k x)`

In addition to providing assistance while writing the function, the informative type of `Vect.replicate` also allows client code to rule out a number of unexpected functions without having to read the source code.
A version of `replicate` for lists could produce a list of the wrong length:

함수를 작성하는 동안 도움을 제공하는 것 외에도, `Vect.replicate`의 정보적인 타입은 또한 클라이언트 코드가 소스 코드를 읽을 필요 없이 많은 예상치 못한 함수를 배제할 수 있게 합니다.
리스트를 위한 `replicate` 버전은 잘못된 길이의 리스트를 생성할 수 있습니다:

`def  (n : Nat) (x : α) : List α :=
match n with
| 0 => []
| k + 1 => x :: x :: replicate k x`

However, making this mistake with `Vect.replicate` is a type error:

그러나 `Vect.replicate`으로 이러한 실수를 하는 것은 타입 에러입니다:

`def Vect.replicate (n : Nat) (x : α) : Vect α n :=
match n with
| 0 => .nil
| k + 1 => .cons x Application type mismatch: The argument
cons x (replicate k x)
has type
Vect α (k + 1)
but is expected to have type
Vect α k
in the application
cons x (cons x (replicate k x))(.cons x (replicate k x))`

```
Application type mismatch: The argument
  cons x (replicate k x)
has type
  Vect α (k + 1)
but is expected to have type
  Vect α k
in the application
  cons x (cons x (replicate k x))
```

The function `List.zip` combines two lists by pairing the first entry in the first list with the first entry in the second list, the second entry in the first list with the second entry in the second list, and so forth.
`List.zip` can be used to pair the three highest peaks in the US state of Oregon with the three highest peaks in Denmark:

`List.zip` 함수는 첫 번째 리스트의 첫 번째 항목과 두 번째 리스트의 첫 번째 항목을 쌍으로 만들고, 첫 번째 리스트의 두 번째 항목과 두 번째 리스트의 두 번째 항목을 쌍으로 만드는 식으로 두 리스트를 결합합니다.
`List.zip`은 미국 오리건 주의 가장 높은 세 개의 봉우리와 덴마크의 가장 높은 세 개의 봉우리를 쌍으로 만드는 데 사용할 수 있습니다:

`["Mount Hood",
"Mount Jefferson",
"South Sister"].zip ["Møllehøj", "Yding Skovhøj", "Ejer Bavnehøj"]`

The result is a list of three pairs:

결과는 세 개 쌍의 리스트입니다:

`[("Mount Hood", "Møllehøj"),
("Mount Jefferson", "Yding Skovhøj"),
("South Sister", "Ejer Bavnehøj")]`

It's somewhat unclear what should happen when the lists have different lengths.
Like many languages, Lean chooses to ignore the extra entries in one of the lists.
For instance, combining the heights of the five highest peaks in Oregon with those of the three highest peaks in Denmark yields three pairs.
In particular,

리스트의 길이가 다를 때 어떤 일이 발생해야 하는지는 다소 불명확합니다.
많은 언어와 마찬가지로 Lean은 리스트 중 하나의 추가 항목을 무시하기로 선택합니다.
예를 들어, 오리건 주의 가장 높은 5개 봉우리의 높이를 덴마크의 가장 높은 3개 봉우리의 높이와 결합하면 세 개의 쌍이 생깁니다.
특히,

`[3428.8, 3201, 3158.5, 3075, 3064].zip [170.86, 170.77, 170.35]`

evaluates to

다음과 같이 계산됩니다

`[(3428.8, 170.86), (3201, 170.77), (3158.5, 170.35)]`

While this approach is convenient because it always returns an answer, it runs the risk of throwing away data when the lists unintentionally have different lengths.
F# takes a different approach: its version of `List.zip` throws an exception when the lengths don't match, as can be seen in this `fsi` session:

이 접근 방식은 항상 답을 반환하기 때문에 편리하지만, 리스트가 의도치 않게 다른 길이를 가질 때 데이터를 버릴 위험이 있습니다.
F#은 다른 접근 방식을 취합니다: 길이가 일치하지 않으면 예외를 throw하는 `List.zip` 버전입니다. 다음 `fsi` 세션에서 볼 수 있습니다:

```
> List.zip [3428.8; 3201.0; 3158.5; 3075.0; 3064.0] [170.86; 170.77; 170.35];;
```

```
System.ArgumentException: The lists had different lengths.
list2 is 2 elements shorter than list1 (Parameter 'list2')
   at Microsoft.FSharp.Core.DetailedExceptions.invalidArgDifferentListLength[?](String arg1, String arg2, Int32 diff) in /builddir/build/BUILD/dotnet-v3.1.424-SDK/src/fsharp.3ef6f0b514198c0bfa6c2c09fefe41a740b024d5/src/fsharp/FSharp.Core/local.fs:line 24
   at Microsoft.FSharp.Primitives.Basics.List.zipToFreshConsTail[a,b](FSharpList`1 cons, FSharpList`1 xs1, FSharpList`1 xs2) in /builddir/build/BUILD/dotnet-v3.1.424-SDK/src/fsharp.3ef6f0b514198c0bfa6c2c09fefe41a740b024d5/src/fsharp/FSharp.Core/local.fs:line 918
   at Microsoft.FSharp.Primitives.Basics.List.zip[T1,T2](FSharpList`1 xs1, FSharpList`1 xs2) in /builddir/build/BUILD/dotnet-v3.1.424-SDK/src/fsharp.3ef6f0b514198c0bfa6c2c09fefe41a740b024d5/src/fsharp/FSharp.Core/local.fs:line 929
   at Microsoft.FSharp.Collections.ListModule.Zip[T1,T2](FSharpList`1 list1, FSharpList`1 list2) in /builddir/build/BUILD/dotnet-v3.1.424-SDK/src/fsharp.3ef6f0b514198c0bfa6c2c09fefe41a740b024d5/src/fsharp/FSharp.Core/list.fs:line 466
   at <StartupCode$FSI_0006>.$FSI_0006.main@()
Stopped due to error
```

This avoids accidentally discarding information, but crashing a program comes with its own difficulties.
The Lean equivalent, which would use the `Option` or `Except` monads, would introduce a burden that may not be worth the safety.

이는 실수로 정보를 버리는 것을 피하지만, 프로그램이 충돌하는 것은 자체적인 어려움이 있습니다.
`Option` 또는 `Except` monads을 사용하는 Lean의 동등한 방법은 안전의 가치가 없을 수 있는 부담을 소개합니다.

Using `Vect`, however, it is possible to write a version of `zip` with a type that requires that both arguments have the same length:

그러나 `Vect`를 사용하면 두 인자가 같은 길이를 가져야 하는 타입의 `zip` 버전을 작성할 수 있습니다:

`def Vect.zip : Vect α n → Vect β n → Vect (α × β) n
| .nil, .nil => .nil
| .cons x xs, .cons y ys => .cons (x, y) (zip xs ys)`

This definition only has patterns for the cases where either both arguments are `Vect.nil` or both arguments are `Vect.cons`, and Lean accepts the definition without a “missing cases” error like the one that results from a similar definition for `List`:

이 정의는 두 인자가 모두 `Vect.nil`이거나 두 인자가 모두 `Vect.cons`인 경우에만 패턴을 가지며, Lean은 `List`의 유사한 정의로 인한 “missing cases” 에러 없이 정의를 수락합니다:

`def List.zip : List α → List β → List (α × β)
Missing cases:
(List.cons _ _), []
[], (List.cons _ _)| [], [] => []
| x :: xs, y :: ys => (x, y) :: zip xs ys`

```
Missing cases:
(List.cons _ _), []
[], (List.cons _ _)
```

This is because the constructor used in the first pattern, `nil` or `cons`, *refines* the type checker's knowledge about the length `n`.
When the first pattern is `nil`, the type checker can additionally determine that the length was `0`, so the only possible choice for the second pattern is `nil`.
Similarly, when the first pattern is `cons`, the type checker can determine that the length was `k+1` for some `Nat` `k`, so the only possible choice for the second pattern is `cons`.
Indeed, adding a case that uses `nil` and `cons` together is a type error, because the lengths don't match:

이는 첫 번째 패턴에서 사용되는 생성자 `nil` 또는 `cons`가 길이 `n`에 대한 타입 검사기의 지식을 *refines*하기 때문입니다.
첫 번째 패턴이 `nil`일 때, 타입 검사기는 추가적으로 길이가 `0`이었음을 결정할 수 있으므로, 두 번째 패턴의 유일한 가능한 선택은 `nil`입니다.
마찬가지로, 첫 번째 패턴이 `cons`일 때, 타입 검사기는 길이가 어떤 `Nat` `k`에 대해 `k+1`이었음을 결정할 수 있으므로, 두 번째 패턴의 유일한 가능한 선택은 `cons`입니다.
실제로, `nil`과 `cons`를 함께 사용하는 경우를 추가하는 것은 타입 에러입니다. 왜냐하면 길이가 일치하지 않기 때문입니다:

`def Vect.zip : Vect α n → Vect β n → Vect (α × β) n
| .nil, .nil => .nil
| .nil, Type mismatch
Vect.cons y ys
has type
Vect ?m.10 (?m.16 + 1)
but is expected to have type
Vect β 0.cons y ys => .nil
| .cons x xs, .cons y ys => .cons (x, y) (zip xs ys)`

```
Type mismatch
  Vect.cons y ys
has type
  Vect ?m.10 (?m.16 + 1)
but is expected to have type
  Vect β 0
```

The refinement of the length can be observed by making `n` into an explicit argument:

길이의 refinement는 `n`을 명시적 인자로 만들어 관찰할 수 있습니다:

`def Vect.zip : (n : Nat) → Vect α n → Vect β n → Vect (α × β) n
| 0, .nil, .nil => .nil
| k + 1, .cons x xs, .cons y ys => .cons (x, y) (zip k xs ys)`

## 7.1.1. Exercises

Getting a feel for programming with dependent types requires experience, and the exercises in this section are very important.
For each exercise, try to see which mistakes the type checker can catch, and which ones it can't, by experimenting with the code as you go.
This is also a good way to develop a feel for the error messages.

Dependent types을 사용한 프로그래밍에 대한 감각을 갖는 것은 경험이 필요하며, 이 섹션의 연습은 매우 중요합니다.
각 연습마다, 코드를 실험하면서 타입 검사기가 잡을 수 있는 실수와 잡을 수 없는 실수를 파악해 봅시다.
이것은 또한 에러 메시지에 대한 감각을 개발하는 좋은 방법입니다.

* Double-check that `Vect.zip` gives the right answer when combining the three highest peaks in Oregon with the three highest peaks in Denmark.
  Because `Vect` doesn't have the syntactic sugar that `List` has, it can be helpful to begin by defining `oregonianPeaks : Vect String 3` and `danishPeaks : Vect String 3`.
* Define a function `Vect.map` with type `(α → β) → Vect α n → Vect β n`.
* Define a function `Vect.zipWith` that combines the entries in a `Vect` one at a time with a function.
  It should have the type `(α → β → γ) → Vect α n → Vect β n → Vect γ n`.
* Define a function `Vect.unzip` that splits a `Vect` of pairs into a pair of `Vect`s. It should have the type `Vect (α × β) n → Vect α n × Vect β n`.
* Define a function `Vect.push` that adds an entry to the *end* of a `Vect`. Its type should be `Vect α n → α → Vect α (n + 1)` and `#eval Vect.push (.cons "snowy" .nil) "peaks"` should yield `Vect.cons "snowy" (Vect.cons "peaks" (Vect.nil))`.
* Define a function `Vect.reverse` that reverses the order of a `Vect`.
* Define a function `Vect.drop` with the following type: `(n : Nat) → Vect α (k + n) → Vect α k`.
  Verify that it works by checking that `#eval danishPeaks.drop 2` yields `Vect.cons "Ejer Bavnehøj" (Vect.nil)`.
* Define a function `Vect.take` with type `(n : Nat) → Vect α (k + n) → Vect α n` that returns the first `n` entries in the `Vect`. Check that it works on an example.
