---
title: "Additional Conveniences"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Additional Conveniences"
---

# Additional Conveniences

## 3.7.1. Constructor Syntax for Instances

Behind the scenes, type classes are structure types and instances are values of these types.
The only differences are that Lean stores additional information about type classes, such as which parameters are output parameters, and that instances are registered for searching.
While values that have structure types are typically defined using either `⟨...⟩` syntax or with braces and fields, and instances are typically defined using `where`, both syntaxes work for both kinds of definition.

내부적으로 type class는 structure type이고 instance는 이 type의 값입니다.
유일한 차이점은 Lean이 어떤 매개변수가 output parameter인지와 같은 type class에 대한 추가 정보를 저장하고, instance가 검색을 위해 등록된다는 것입니다.
structure type을 가진 값은 일반적으로 `⟨...⟩` 문법이나 중괄호와 필드를 사용하여 정의되고, instance는 일반적으로 `where`를 사용하여 정의되지만, 두 문법 모두 두 가지 종류의 정의에 작동합니다.

For example, a forestry application might represent trees as follows:

예를 들어, 임업 응용 프로그램은 다음과 같이 나무를 나타낼 수 있습니다:

`structure Tree : Type where
latinName : String
commonNames : List String
def oak : Tree :=
⟨"Quercus robur", ["common oak", "European oak"]⟩
def birch : Tree :=
{ latinName := "Betula pendula",
commonNames := ["silver birch", "warty birch"]
}
def sloe : Tree where
latinName := "Prunus spinosa"
commonNames := ["sloe", "blackthorn"]`

All three syntaxes are equivalent.

세 가지 문법 모두 동등합니다.

Similarly, type class instances can be defined using all three syntaxes:

마찬가지로, type class instance는 세 가지 문법 모두를 사용하여 정의할 수 있습니다:

`class Display (α : Type) where
displayName : α → String
instance : Display Tree :=
⟨Tree.latinName⟩
instance : Display Tree :=
{ displayName := Tree.latinName }
instance : Display Tree where
displayName t := t.latinName`

The `where` syntax is typically used for instances, while structures use either the curly-brace syntax or the `where` syntax.
The `⟨...⟩` syntax can be useful when emphasizing that a structure type is very much like a tuple in which the fields happen to be named, but the names are not important at the moment.
However, there are situations where it can make sense to use other alternatives.
In particular, a library might provide a function that constructs an instance value.
Placing a call to this function after `:=` in an instance declaration is the easiest way to use such a function.

`where` 문법은 일반적으로 instance에 사용되고, structure는 중괄호 문법이나 `where` 문법 중 하나를 사용합니다.
`⟨...⟩` 문법은 structure type이 필드가 이름을 가진 tuple과 매우 유사하지만, 지금 당장 이름이 중요하지 않다는 것을 강조할 때 유용할 수 있습니다.
그러나 다른 대안을 사용하는 것이 타당한 상황이 있습니다.
특히, library가 instance 값을 구성하는 함수를 제공할 수 있습니다.
instance 선언에서 `:=` 뒤에 이 함수에 대한 호출을 배치하는 것이 이러한 함수를 사용하는 가장 쉬운 방법입니다.

## 3.7.2. Examples

When experimenting with Lean code, definitions can be more convenient to use than `#eval` or `#check` commands.
First off, definitions don't produce any output, which can help keep the reader's focus on the most interesting output.
Secondly, it's easiest to write most Lean programs by starting with a type signature, allowing Lean to provide more assistance and better error messages while writing the program itself.
On the other hand, `#eval` and `#check` are easiest to use in contexts where Lean is able to determine the type from the provided expression.
Thirdly, `#eval` cannot be used with expressions whose types don't have `ToString` or `Repr` instances, such as functions.
Finally, multi-step `do` blocks, `let`-expressions, and other syntactic forms that take multiple lines are particularly difficult to write with a type annotation in `#eval` or `#check`, simply because the required parenthesization can be difficult to predict.

Lean 코드를 실험할 때, definition은 `#eval`이나 `#check` 명령보다 사용하기가 더 편할 수 있습니다.
우선, definition은 어떤 출력도 생성하지 않아서 독자의 초점을 가장 흥미로운 출력에 유지하는 데 도움이 될 수 있습니다.
둘째, 대부분의 Lean 프로그램은 type signature로 시작하여 작성하는 것이 가장 쉬우며, 프로그램 자체를 작성하는 동안 Lean이 더 많은 지원과 더 나은 오류 메시지를 제공하도록 합니다.
한편, `#eval`과 `#check`는 Lean이 제공된 expression에서 type을 결정할 수 있는 context에서 가장 쉽게 사용됩니다.
셋째, `#eval`은 function처럼 `ToString`이나 `Repr` instance를 갖지 않는 type의 expression에는 사용될 수 없습니다.
마지막으로, multi-step `do` block, `let`-expression 및 여러 줄을 차지하는 다른 syntactic form은 필요한 괄호화가 예측하기 어려울 수 있다는 단순한 이유 때문에 `#eval`이나 `#check`에서 type annotation과 함께 작성하기가 특히 어렵습니다.

To work around these issues, Lean supports the explicit indication of examples in a source file.
An example is like a definition without a name.
For instance, a non-empty list of birds commonly found in Copenhagen's green spaces can be written:

이러한 문제를 해결하기 위해 Lean은 source file에 예제를 명시적으로 표시하는 것을 지원합니다.
예제는 이름이 없는 definition과 같습니다.
예를 들어, Copenhagen의 녹지에서 흔히 발견되는 새의 비어있지 않은 목록은 다음과 같이 작성할 수 있습니다:

`example : NonEmptyList String :=
{ head := "Sparrow",
tail := ["Duck", "Swan", "Magpie", "Eurasian coot", "Crow"]
}`

Examples may define functions by accepting arguments:

예제는 인수를 받아들임으로써 함수를 정의할 수 있습니다:

`example (n : Nat) (k : Nat) : Bool :=
n + k == k + n`

While this creates a function behind the scenes, this function has no name and cannot be called.
Nonetheless, this is useful for demonstrating how a library can be used with arbitrary or unknown values of some given type.
In source files, `example` declarations are best paired with comments that explain how the example illustrates the concepts of the library.

이것은 내부적으로 함수를 생성하지만, 이 함수는 이름이 없고 호출할 수 없습니다.
그럼에도 불구하고, 이것은 library가 주어진 type의 임의의 또는 미지의 값으로 사용될 수 있는 방법을 보여주는 데 유용합니다.
source file에서 `example` 선언은 예제가 library의 개념을 어떻게 설명하는지를 설명하는 주석과 함께 짝을 이루는 것이 가장 좋습니다.
