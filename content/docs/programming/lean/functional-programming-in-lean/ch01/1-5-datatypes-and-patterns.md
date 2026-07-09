---
title: "1.5. 데이터타입과 패턴"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "데이터타입과 패턴"
---

# Datatypes and Patterns

데이터타입과 패턴

# 1.5. Datatypes and Patterns

Structures enable multiple independent pieces of data to be combined into a coherent whole that is represented by a brand new type.
Types such as structures that group together a collection of values are called *product types*.
Many domain concepts, however, can't be naturally represented as structures.
For instance, an application might need to track user permissions, where some users are document owners, some may edit documents, and others may only read them.
A calculator has a number of binary operators, such as addition, subtraction, and multiplication.
Structures do not provide an easy way to encode multiple choices.

구조체는 여러 독립적인 데이터 조각을 새로운 타입으로 표현되는 응집된 전체로 결합할 수 있게 합니다.
값의 모음을 함께 그룹화하는 구조체와 같은 타입을 *곱 타입(product types)*이라고 합니다.
그러나 많은 영역 개념은 구조체로 자연스럽게 표현될 수 없습니다.
예를 들어, 애플리케이션이 사용자 권한을 추적해야 할 수 있으며, 일부 사용자는 문서 소유자이고, 일부는 문서를 편집할 수 있으며, 다른 사용자는 문서를 읽을 수만 있습니다.
계산기는 덧셈, 뺄셈, 곱셈과 같은 여러 이진 연산자를 가지고 있습니다.
구조체는 여러 선택을 인코딩하는 쉬운 방법을 제공하지 않습니다.

Similarly, while a structure is an excellent way to keep track of a fixed set of fields, many applications require data that may contain an arbitrary number of elements.
Most classic data structures, such as trees and lists, have a recursive structure, where the tail of a list is itself a list, or where the left and right branches of a binary tree are themselves binary trees.
In the aforementioned calculator, the structure of expressions themselves is recursive.
The summands in an addition expression may themselves be multiplication expressions, for instance.

마찬가지로, 구조체가 고정된 필드 세트를 추적하는 훌륭한 방법이지만, 많은 애플리케이션은 임의의 수의 요소를 포함할 수 있는 데이터가 필요합니다.
트리와 리스트와 같은 대부분의 고전적인 데이터 구조는 재귀적 구조를 가지고 있으며, 여기서 리스트의 꼬리는 그 자체로 리스트이거나, 이진 트리의 왼쪽과 오른쪽 분기는 그 자체로 이진 트리입니다.
앞서 언급한 계산기에서, 표현식 자체의 구조는 재귀적입니다.
예를 들어, 덧셈 표현식의 피가산수는 그 자체로 곱셈 표현식일 수 있습니다.

Datatypes that allow choices are called *sum types* and datatypes that can include instances of themselves are called *recursive datatypes*.
Recursive sum types are called *inductive datatypes*, because mathematical induction may be used to prove statements about them.
When programming, inductive datatypes are consumed through pattern matching and recursive functions.

선택을 허용하는 데이터타입을 *합 타입(sum types)*이라고 하며, 그들 자체의 인스턴스를 포함할 수 있는 데이터타입을 *재귀 데이터타입(recursive datatypes)*이라고 합니다.
재귀 합 타입을 *귀납 데이터타입(inductive datatypes)*이라고 합니다. 왜냐하면 수학적 귀납법을 사용하여 그들에 대한 명제를 증명할 수 있기 때문입니다.
프로그래밍할 때, 귀납 데이터타입은 패턴 매칭과 재귀 함수를 통해 소비됩니다.

Many of the built-in types are actually inductive datatypes in the standard library.
For instance, `Bool` is an inductive datatype:

```lean
inductive Bool where
| false : Bool
| true : Bool
```

This definition has two main parts.
The first line provides the name of the new type (`Bool`), while the remaining lines each describe a constructor.
As with constructors of structures, constructors of inductive datatypes are mere inert receivers of and containers for other data, rather than places to insert arbitrary initialization and validation code.
Unlike structures, inductive datatypes may have multiple constructors.
Here, there are two constructors, `true` and `false`, and neither takes any arguments.
Just as a structure declaration places its names in a namespace named after the declared type, an inductive datatype places the names of its constructors in a namespace.
In the Lean standard library, `true` and `false` are re-exported from this namespace so that they can be written alone, rather than as `Bool.true` and `Bool.false`, respectively.

내장 타입의 대부분은 실제로 표준 라이브러리의 귀납 데이터타입입니다.
예를 들어, `Bool`은 귀납 데이터타입입니다.

이 정의는 두 가지 주요 부분을 가지고 있습니다.
첫 번째 줄은 새로운 타입의 이름(`Bool`)을 제공하고, 나머지 줄은 각각 생성자를 설명합니다.
구조체의 생성자와 마찬가지로, 귀납 데이터타입의 생성자는 단순한 다른 데이터의 불활성 수신자 및 컨테이너이며, 임의의 초기화 및 유효성 검사 코드를 삽입할 장소가 아닙니다.
구조체와 달리, 귀납 데이터타입은 여러 생성자를 가질 수 있습니다.
여기에는 `true`과 `false` 두 개의 생성자가 있으며, 둘 다 인수를 받지 않습니다.
구조체 선언이 선언된 타입의 이름을 따서 명명된 네임스페이스에 이름을 배치하는 것처럼, 귀납 데이터타입은 그 생성자의 이름을 네임스페이스에 배치합니다.
Lean 표준 라이브러리에서, `true`과 `false`는 이 네임스페이스에서 다시 내보내지므로, `Bool.true`과 `Bool.false`가 아니라 단독으로 작성할 수 있습니다.

From a data modeling perspective, inductive datatypes are used in many of the same contexts where a sealed abstract class might be used in other languages.
In languages like C# or Java, one might write a similar definition of `Bool`:

```
abstract class Bool {}
class True : Bool {}
class False : Bool {}
```

However, the specifics of these representations are fairly different. In particular, each non-abstract class creates both a new type and new ways of allocating data. In the object-oriented example, `True` and `False` are both types that are more specific than `Bool`, while the Lean definition introduces only the new type `Bool`.

데이터 모델링 관점에서, 귀납 데이터타입은 다른 언어에서 봉인된 추상 클래스가 사용될 수 있는 많은 동일한 맥락에서 사용됩니다.
C# 또는 Java와 같은 언어에서는 `Bool`의 유사한 정의를 작성할 수 있습니다.

그러나 이들 표현의 세부 사항은 상당히 다릅니다. 특히 각 비추상 클래스는 새로운 타입과 데이터를 할당하는 새로운 방법을 모두 생성합니다. 객체 지향 예제에서, `True`와 `False`는 모두 `Bool`보다 더 구체적인 타입이지만, Lean 정의는 새로운 타입 `Bool`만을 도입합니다.

The type `Nat` of non-negative integers is an inductive datatype:

```lean
inductive Nat where
| zero : Nat
| succ (n : Nat) : Nat
```

Here, `zero` represents 0, while `succ` represents the successor of some other number.
The `Nat` mentioned in `succ`'s declaration is the very type `Nat` that is in the process of being defined.
*Successor* means “one greater than”, so the successor of five is six and the successor of 32,185 is 32,186.
Using this definition, `4` is represented as `Nat.succ (Nat.succ (Nat.succ (Nat.succ Nat.zero)))`.
This definition is almost like the definition of `Bool` with slightly different names.
The only real difference is that `succ` is followed by `(n : Nat)`, which specifies that the constructor `succ` takes an argument of type `Nat` which happens to be named `n`.
The names `zero` and `succ` are in a namespace named after their type, so they must be referred to as `Nat.zero` and `Nat.succ`, respectively.

음이 아닌 정수의 타입 `Nat`은 귀납 데이터타입입니다.

여기서 `zero`는 0을 나타내고, `succ`는 다른 수의 후자를 나타냅니다.
`succ`의 선언에서 언급된 `Nat`은 정의 과정에 있는 `Nat` 타입 그 자체입니다.
*후자(Successor)*는 “1 더 큰”을 의미하므로, 5의 후자는 6이고 32,185의 후자는 32,186입니다.
이 정의를 사용하면, `4`는 `Nat.succ (Nat.succ (Nat.succ (Nat.succ Nat.zero)))`로 표현됩니다.
이 정의는 약간 다른 이름을 가진 `Bool`의 정의와 거의 같습니다.
유일한 실질적인 차이는 `succ`가 `(n : Nat)`로 따라오며, 생성자 `succ`가 `n`이라는 이름을 가진 `Nat` 타입의 인수를 받음을 명시합니다.
이름 `zero`과 `succ`은 그들의 타입 이름을 따서 명명된 네임스페이스에 있으므로, 각각 `Nat.zero`과 `Nat.succ`으로 참조되어야 합니다.

Argument names, such as `n`, may occur in Lean's error messages and in feedback provided when writing mathematical proofs.
Lean also has an optional syntax for providing arguments by name.
Generally, however, the choice of argument name is less important than the choice of a structure field name, as it does not form as large a part of the API.

`n`과 같은 인수 이름은 Lean의 오류 메시지와 수학 증명을 작성할 때 제공되는 피드백에 나타날 수 있습니다.
Lean은 또한 이름으로 인수를 제공하기 위한 선택적 구문을 가지고 있습니다.
일반적으로, 인수 이름의 선택은 구조체 필드 이름의 선택보다 덜 중요합니다. 왜냐하면 API의 큰 부분을 형성하지 않기 때문입니다.

In C# or Java, `Nat` could be defined as follows:

C# 또는 Java에서, `Nat`은 다음과 같이 정의될 수 있습니다:

```
abstract class Nat {}
class Zero : Nat {}
class Succ : Nat {
    public Nat n;
    public Succ(Nat pred) {
        n = pred;
    }
}
```

Just as in the `Bool` example above, this defines more types than the Lean equivalent.
Additionally, this example highlights how Lean datatype constructors are much more like subclasses of an abstract class than they are like constructors in C# or Java, as the constructor shown here contains initialization code to be executed.

위의 `Bool` 예제에서와 마찬가지로, 이것은 Lean과 동치인 것보다 더 많은 타입을 정의합니다.
또한, 이 예제는 Lean 데이터타입 생성자가 C# 또는 Java의 생성자보다 추상 클래스의 하위 클래스와 훨씬 더 유사함을 강조합니다. 여기서 보여진 생성자가 실행할 초기화 코드를 포함하기 때문입니다.

Sum types are also similar to using a string tag to encode discriminated unions in TypeScript.
In TypeScript, `Nat` could be defined as follows:

```
interface Zero {
    tag: "zero";
}

interface Succ {
    tag: "succ";
    predecessor: Nat;
}

type Nat = Zero | Succ;
```

Just like C# and Java, this encoding ends up with more types than in Lean, because `Zero` and `Succ` are each a type on their own.
It also illustrates that Lean constructors correspond to objects in JavaScript or TypeScript that include a tag that identifies the contents.

합 타입은 또한 TypeScript에서 판별된 합집합(discriminated union)을 인코딩하기 위해 문자열 태그를 사용하는 것과도 유사합니다.
TypeScript에서, `Nat`은 다음과 같이 정의될 수 있습니다.

C#과 Java와 마찬가지로, 이 인코딩은 Lean보다 더 많은 타입으로 끝납니다. `Zero`와 `Succ`이 각각 그 자신의 타입이기 때문입니다.
또한 Lean 생성자가 내용을 식별하는 태그를 포함하는 JavaScript 또는 TypeScript의 객체와 일치함을 보여줍니다.

## 1.5.1. Pattern Matching

In many languages, these kinds of data are consumed by first using an instance-of operator to check which subclass has been received and then reading the values of the fields that are available in the given subclass.
The instance-of check determines which code to run, ensuring that the data needed by this code is available, while the fields themselves provide the data.
In Lean, both of these purposes are simultaneously served by *pattern matching*.

많은 언어에서, 이러한 종류의 데이터는 먼저 instance-of 연산자를 사용하여 어떤 하위 클래스가 수신되었는지 확인한 다음 주어진 하위 클래스에서 사용 가능한 필드의 값을 읽음으로써 소비됩니다.
instance-of 검사는 실행할 코드를 결정하고 이 코드에 필요한 데이터가 사용 가능함을 보장하지만, 필드 자체는 데이터를 제공합니다.
Lean에서, 이 두 가지 목적은 모두 *패턴 매칭(pattern matching)*에 의해 동시에 제공됩니다.

An example of a function that uses pattern matching is `isZero`, which is a function that returns `true` when its argument is `Nat.zero`, or false otherwise.

```lean
def isZero (n : Nat) : Bool :=
match n with
| Nat.zero => true
| Nat.succ k => false
```

The `match` expression is provided the function's argument `n` for destructuring.
If `n` was constructed by `Nat.zero`, then the first branch of the pattern match is taken, and the result is `true`.
If `n` was constructed by `Nat.succ`, then the second branch is taken, and the result is `false`.

Step-by-step, evaluation of `isZero Nat.zero` proceeds as follows:

Evaluation of `isZero 5` proceeds similarly:

패턴 매칭을 사용하는 함수의 예는 `isZero`이며, 인수가 `Nat.zero`일 때 `true`를 반환하고, 그 외에는 false를 반환하는 함수입니다.

`match` 표현식은 함수의 인수 `n`을 분해(destructuring)하기 위해 제공됩니다.
`n`이 `Nat.zero`로 구성되었으면, 패턴 매칭의 첫 번째 분기가 취해지고, 결과는 `true`입니다.
`n`이 `Nat.succ`로 구성되었으면, 두 번째 분기가 취해지고, 결과는 `false`입니다.

단계별로, `isZero Nat.zero`의 평가는 다음과 같이 진행됩니다.

`isZero 5`의 평가는 유사하게 진행됩니다.

The `k` in the second branch of the pattern in `isZero` is not decorative.
It makes the `Nat` that is the argument to `Nat.succ` visible, with the provided name.
That smaller number can then be used to compute the final result of the expression.

Just as the successor of some number `n` is one greater than `n` (that is, `n + 1`), the predecessor of a number is one less than it.
If `pred` is a function that finds the predecessor of a `Nat`, then it should be the case that the following examples find the expected result:

```lean
#eval pred 5
```

```
4
```

```lean
#eval pred 839
```

```
838
```

Because `Nat` cannot represent negative numbers, `Nat.zero` is a bit of a conundrum.
Usually, when working with `Nat`, operators that would ordinarily produce a negative number are redefined to produce `zero` itself:

```lean
#eval pred 0
```

```
0
```

To find the predecessor of a `Nat`, the first step is to check which constructor was used to create it.
If it was `Nat.zero`, then the result is `Nat.zero`.
If it was `Nat.succ`, then the name `k` is used to refer to the `Nat` underneath it.
And this `Nat` is the desired predecessor, so the result of the `Nat.succ` branch is `k`.

```lean
def pred (n : Nat) : Nat :=
match n with
| Nat.zero => Nat.zero
| Nat.succ k => k
```

`isZero`의 패턴의 두 번째 분기의 `k`는 장식이 아닙니다.
`Nat.succ`의 인수인 `Nat`을 제공된 이름으로 표시합니다.
그 더 작은 수는 표현식의 최종 결과를 계산하는 데 사용될 수 있습니다.

어떤 수 `n`의 후자는 `n`보다 1 크다(즉, `n + 1`)는 것처럼, 수의 전자(predecessor)는 그것보다 1 작습니다.
`pred`가 `Nat`의 전자를 찾는 함수라면, 다음 예제가 예상된 결과를 찾아야 합니다.

`Nat`은 음수를 나타낼 수 없으므로, `Nat.zero`는 약간의 어려움입니다.
일반적으로 `Nat`으로 작업할 때, 보통 음수를 산출하는 연산자는 `zero` 자체를 산출하도록 재정의됩니다.

`Nat`의 전자를 찾으려면, 첫 번째 단계는 그것을 생성하는 데 어떤 생성자가 사용되었는지 확인하는 것입니다.
`Nat.zero`였다면, 결과는 `Nat.zero`입니다.
`Nat.succ`였다면, 이름 `k`는 그 아래의 `Nat`을 참조하는 데 사용됩니다.
그리고 이 `Nat`은 원하는 전자이므로, `Nat.succ` 분기의 결과는 `k`입니다.

Applying this function to `5` yields the following steps:

이 함수를 `5`에 적용하면 다음 단계를 산출합니다.

Pattern matching can be used with structures as well as with sum types.
For instance, a function that extracts the third dimension from a `Point3D` can be written as follows:

```lean
def depth (p : Point3D) : Float :=
match p with
| { x:= h, y := w, z := d } => d
```

In this case, it would have been much simpler to just use the `Point3D.z` accessor, but structure patterns are occasionally the simplest way to write a function.

패턴 매칭은 합 타입뿐만 아니라 구조체와도 함께 사용될 수 있습니다.
예를 들어, `Point3D`에서 세 번째 차원을 추출하는 함수는 다음과 같이 작성할 수 있습니다.

이 경우, 단순히 `Point3D.z` 접근자를 사용하는 것이 훨씬 더 간단했을 것이지만, 구조체 패턴은 때때로 함수를 작성하는 가장 간단한 방법입니다.

## 1.5.2. Recursive Functions

Definitions that refer to the name being defined are called *recursive definitions*.
Inductive datatypes are allowed to be recursive; indeed, `Nat` is an example of such a datatype because `succ` demands another `Nat`.
Recursive datatypes can represent arbitrarily large data, limited only by technical factors like available memory.
Just as it would be impossible to write down one constructor for each natural number in the datatype definition, it is also impossible to write down a pattern match case for each possibility.

Recursive datatypes are nicely complemented by recursive functions.
A simple recursive function over `Nat` checks whether its argument is even.
In this case, `Nat.zero` is even.
Non-recursive branches of the code like this one are called *base cases*.
The successor of an odd number is even, and the successor of an even number is odd.
This means that a number built with `Nat.succ` is even if and only if its argument is not even.

```lean
def even (n : Nat) : Bool :=
match n with
| Nat.zero => true
| Nat.succ k => not (even k)
```

This pattern of thought is typical for writing recursive functions on `Nat`.
First, identify what to do for `Nat.zero`.
Then, determine how to transform a result for an arbitrary `Nat` into a result for its successor, and apply this transformation to the result of the recursive call.
This pattern is called *structural recursion*.

정의되는 이름을 참조하는 정의를 *재귀 정의(recursive definitions)*라고 합니다.
귀납 데이터타입은 재귀적이어야 합니다. 실제로 `Nat`은 `succ`가 다른 `Nat`을 요구하기 때문에 이러한 데이터타입의 예입니다.
재귀 데이터타입은 임의로 큰 데이터를 나타낼 수 있으며, 사용 가능한 메모리와 같은 기술적 요소에 의해서만 제한됩니다.
데이터타입 정의에서 각 자연수에 대해 하나의 생성자를 적어 두는 것이 불가능한 것처럼, 각 가능성에 대해 패턴 매칭 경우를 적어 두는 것도 불가능합니다.

재귀 데이터타입은 재귀 함수에 의해 훌륭히 보완됩니다.
`Nat` 위의 간단한 재귀 함수는 그 인수가 짝수인지 확인합니다.
이 경우, `Nat.zero`는 짝수입니다.
이와 같은 코드의 비재귀 분기를 *기본 경우(base cases)*라고 합니다.
홀수의 후자는 짝수이고, 짝수의 후자는 홀수입니다.
즉, `Nat.succ`로 구축된 수가 짝수인 것과 그 인수가 짝수가 아닌 것이 동치라는 것입니다.

이러한 생각의 패턴은 `Nat`에서 재귀 함수를 작성하는 전형입니다.
먼저 `Nat.zero`에 대해 수행할 작업을 식별합니다.
그런 다음 임의의 `Nat`에 대한 결과를 그 후자에 대한 결과로 변환하는 방법을 결정하고, 이 변환을 재귀 호출의 결과에 적용합니다.
이 패턴을 *구조 재귀(structural recursion)*라고 합니다.

Unlike many languages, Lean ensures by default that every recursive function will eventually reach a base case.
From a programming perspective, this rules out accidental infinite loops.
But this feature is especially important when proving theorems, where infinite loops cause major difficulties.
A consequence of this is that Lean will not accept a version of `even` that attempts to invoke itself recursively on the original number:

많은 언어와 달리, Lean은 기본적으로 모든 재귀 함수가 결국 기본 경우에 도달함을 보장합니다.
프로그래밍 관점에서, 이는 우발적인 무한 루프를 배제합니다.
하지만 이 기능은 무한 루프가 주요 어려움을 초래하는 정리를 증명할 때 특히 중요합니다.
이것의 결과는 Lean이 원본 수에서 자신을 재귀적으로 호출하려고 시도하는 `even`의 버전을 허용하지 않는다는 것입니다:

```lean
def evenLoops (n : Nat) : Bool :=
match n with
| Nat.zero => true
| Nat.succ k => not (evenLoops n)
```

```
fail to show termination for
  evenLoops
with errors
failed to infer structural recursion:
Not considering parameter n of evenLoops:
  it is unchanged in the recursive calls
no parameters suitable for structural recursion

well-founded recursion cannot be used, `evenLoops` does not take any (non-fixed) arguments
```

The important part of the error message is that Lean could not determine that the recursive function always reaches a base case (because it doesn't).

오류 메시지의 중요한 부분은 Lean이 재귀 함수가 항상 기본 경우에 도달함을 결정할 수 없다는 것입니다(그렇지 않기 때문입니다).

```
fail to show termination for
  evenLoops
with errors
failed to infer structural recursion:
Not considering parameter n of evenLoops:
  it is unchanged in the recursive calls
no parameters suitable for structural recursion

well-founded recursion cannot be used, `evenLoops` does not take any (non-fixed) arguments
```

Even though addition takes two arguments, only one of them needs to be inspected.
To add zero to a number `n`, just return `n`.
To add the successor of `k` to `n`, take the successor of the result of adding `k` to `n`.

```lean
def plus (n : Nat) (k : Nat) : Nat :=
match k with
| Nat.zero => n
| Nat.succ k' => Nat.succ (plus n k')
```

In the definition of `plus`, the name `k'` is chosen to indicate that it is connected to, but not identical with, the argument `k`.
For instance, walking through the evaluation of `plus 3 2` yields the following steps:

덧셈이 두 개의 인수를 가지지만, 그 중 하나만 검사해야 합니다.
0을 수 `n`에 더하려면, 단순히 `n`을 반환합니다.
`k`의 후자를 `n`에 더하려면, `k`를 `n`에 더한 결과의 후자를 취합니다.

`plus`의 정의에서, 이름 `k'`은 그것이 인수 `k`와 연결되어 있지만 동일하지 않음을 나타내도록 선택됩니다.
예를 들어, `plus 3 2`의 평가를 단계적으로 진행하면 다음 단계를 산출합니다.

Not every function can be easily written using structural recursion.
The understanding of addition as iterated `Nat.succ`, multiplication as iterated addition, and subtraction as iterated predecessor suggests an implementation of division as iterated subtraction.
In this case, if the numerator is less than the divisor, the result is zero.
Otherwise, the result is the successor of dividing the numerator minus the divisor by the divisor.

모든 함수를 구조 재귀를 사용하여 쉽게 작성할 수 있는 것은 아닙니다.
덧셈을 반복된 `Nat.succ`로, 곱셈을 반복된 덧셈으로, 뺄셈을 반복된 전자로 이해하면 나눗셈을 반복된 뺄셈으로 구현할 것을 제안합니다.
이 경우, 피제수가 제수보다 작으면, 결과는 0입니다.
그렇지 않으면, 결과는 피제수 빼기 제수를 제수로 나눈 결과의 후자입니다.

```lean
def div (n : Nat) (k : Nat) : Nat :=
if n < k then
0
else Nat.succ (div (n - k) k)
```

```
fail to show termination for
  div
with errors
failed to infer structural recursion:
Not considering parameter k of div:
  it is unchanged in the recursive calls
Cannot use parameter k:
  failed to eliminate recursive application
    div (n - k) k

failed to prove termination, possible solutions:
  - Use `have`-expressions to prove the remaining goals
  - Use `termination_by` to specify a different well-founded relation
  - Use `decreasing_by` to specify your own tactic for discharging this kind of goal
k n:Nat h✝:¬n < k ⊢ n - k < n
```

As long as the second argument is not `0`, this program terminates, as it always makes progress towards the base case.
However, it is not structurally recursive, because it doesn't follow the pattern of finding a result for zero and transforming a result for a smaller `Nat` into a result for its successor.
In particular, the recursive invocation of the function is applied to the result of another function call, rather than to an input constructor's argument.
Thus, Lean rejects it with the following message:

두 번째 인수가 `0`이 아닌 한, 이 프로그램은 항상 기본 경우를 향해 진행하므로 종료됩니다.
그러나 0에 대한 결과를 찾고 더 작은 `Nat`의 결과를 그 후자의 결과로 변환하는 패턴을 따르지 않기 때문에 구조적으로 재귀적이지 않습니다.
특히, 함수의 재귀 호출은 입력 생성자의 인수가 아니라 다른 함수 호출의 결과에 적용됩니다.
따라서 Lean은 다음 메시지와 함께 거부합니다:

```
fail to show termination for
  div
with errors
failed to infer structural recursion:
Not considering parameter k of div:
  it is unchanged in the recursive calls
Cannot use parameter k:
  failed to eliminate recursive application
    div (n - k) k

failed to prove termination, possible solutions:
  - Use `have`-expressions to prove the remaining goals
  - Use `termination_by` to specify a different well-founded relation
  - Use `decreasing_by` to specify your own tactic for discharging this kind of goal
k n:Nath✝:¬n < k⊢ n - k < n
```

This message means that `div` requires a manual proof of termination.
This topic is explored in [the final chapter](Programming___-Proving___-and-Performance/More-Inequalities/#division-as-iterated-subtraction).

이 메시지는 `div`가 종료의 수동 증명을 필요로 함을 의미합니다.
이 주제는 [최종 장](Programming___-Proving___-and-Performance/More-Inequalities/#division-as-iterated-subtraction)에서 탐색됩니다.
