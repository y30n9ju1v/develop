---
title: "5. 구문"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "metaprogramming"]
categories: ["programming"]
description: "Lean 4 Syntax 타입: 구체적 구문 트리와 syntax rule 정의 방법"
---

This chapter is concerned with the means to declare and operate on syntax
in Lean. Since there are a multitude of ways to operate on it, we will
not go into great detail about this yet and postpone quite a bit of this to
later chapters.

이 챕터는 Lean에서 syntax를 선언하고 조작하는 방법을 다룹니다. 이를 조작하는 방법이 다양하기 때문에, 아직 자세히 다루지 않고 상당 부분을 이후 챕터로 미룰 것입니다.


Some readers might be familiar with the `infix` or even the `notation`
commands, for those that are not here is a brief recap:

일부 독자들은 `infix` 또는 `notation` 명령에 익숙할 수 있습니다. 익숙하지 않은 분들을 위해 간단히 요약합니다:

```
import Lean

-- XOR, denoted \oplus
infixl:60 " ⊕ " => fun l r => (!l && r) || (l && !r)

#eval true ⊕ true -- false
#eval true ⊕ false -- true
#eval false ⊕ true -- true
#eval false ⊕ false -- false

-- with `notation`, "left XOR"
notation:10 l:10 " LXOR " r:11 => (!l && r)

#eval true LXOR true -- false
#eval true LXOR false -- false
#eval false LXOR true -- true
#eval false LXOR false -- false
```

As we can see the `infixl` command allows us to declare a notation for
a binary operation that is infix, meaning that the operator is in between
the operands (as opposed to e.g. before which would be done using the `prefix` command).
The `l` at the end of `infixl` means that the notation is left associative so `a ⊕ b ⊕ c`
gets parsed as `(a ⊕ b) ⊕ c` as opposed to `a ⊕ (b ⊕ c)` (which would be achieved by `infixr`).
On the right hand side, it expects a function that operates on these two parameters
and returns some value. The `notation` command, on the other hand, allows us some more
freedom: we can just "mention" the parameters right in the syntax definition
and operate on them on the right hand side. It gets even better though, we can
in theory create syntax with 0 up to as many parameters as we wish using the
`notation` command, it is hence also often referred to as "mixfix" notation.

보다시피 `infixl` 명령은 이항 연산에 대한 infix 표기법을 선언할 수 있게 해줍니다. infix란 연산자가 피연산자들 사이에 위치하는 것을 의미합니다 (예를 들어, `prefix` 명령을 사용하면 연산자가 앞에 오는 것과 대비됩니다). `infixl` 끝의 `l`은 표기법이 좌결합적임을 의미하므로 `a ⊕ b ⊕ c`는 `a ⊕ (b ⊕ c)` (`infixr`로 구현)가 아닌 `(a ⊕ b) ⊕ c`로 파싱됩니다. 우변에는 두 매개변수를 받아 어떤 값을 반환하는 함수가 옵니다. 반면 `notation` 명령은 더 많은 자유를 제공합니다. syntax 정의 안에 매개변수를 직접 "언급"하고 우변에서 그것들을 사용할 수 있습니다. 더 나아가, `notation` 명령을 사용하면 이론상 0개부터 원하는 만큼의 매개변수를 갖는 syntax를 만들 수 있으므로, 이를 "mixfix" 표기법이라고도 자주 부릅니다.

The two unintuitive parts about these two are:

* The fact that we are leaving spaces around our operators: " ⊕ ", " LXOR ".
  This is so that, when Lean pretty prints our syntax later on, it also
  uses spaces around the operators, otherwise the syntax would just be presented
  as `l⊕r` as opposed to `l ⊕ r`.
* The `60` and `10` right after the respective commands -- these denote the operator
  precedence, meaning how strong they bind to their arguments, let's see this in action:

이 두 가지에서 직관적이지 않은 부분이 두 가지 있습니다:

* 연산자 주위에 공백을 남긴다는 점: " ⊕ ", " LXOR ". 이렇게 하면 Lean이 나중에 syntax를 pretty print할 때도 연산자 주위에 공백을 사용합니다. 그렇지 않으면 `l ⊕ r` 대신 `l⊕r`로 표시됩니다.
* 각 명령 바로 뒤의 `60`과 `10` -- 이것들은 연산자 우선순위를 나타내며, 인수에 얼마나 강하게 결합하는지를 의미합니다. 실제로 확인해 보겠습니다:

```
#eval true ⊕ false LXOR false -- false
#eval (true ⊕ false) LXOR false -- false
#eval true ⊕ (false LXOR false) -- true
```

As we can see, the Lean interpreter analyzed the first term without parentheses
like the second instead of the third one. This is because the `⊕` notation
has higher precedence than `LXOR` (`60 > 10` after all) and is thus evaluated before it.
This is also how you might implement rules like `*` being evaluated before `+`.

보다시피 Lean 인터프리터는 괄호 없는 첫 번째 항을 세 번째가 아닌 두 번째처럼 분석합니다. 이는 `⊕` 표기법이 `LXOR`보다 높은 우선순위(`60 > 10`)를 가지므로 먼저 평가되기 때문입니다. 이것은 `*`가 `+`보다 먼저 평가되는 것과 같은 규칙을 구현하는 방법이기도 합니다.

Lastly at the `notation` example there are also these `:precedence` bindings
at the arguments: `l:10` and `r:11`. This conveys that the left argument must have
precedence at least 10 or greater, and the right argument must have precedence at 11
or greater. The way the arguments are assigned their respective precedence is by looking at
the precedence of the rule that was used to parse them. Consider for example
`a LXOR b LXOR c`. Theoretically speaking this could be parsed in two ways:

1. `(a LXOR b) LXOR c`
2. `a LXOR (b LXOR c)`

Since the arguments in parentheses are parsed by the `LXOR` rule with precedence
10 they will appear as arguments with precedence 10 to the outer `LXOR` rule:

1. `(a LXOR b):10 LXOR c`
2. `a LXOR (b LXOR c):10`

However if we check the definition of `LXOR`: `notation:10 l:10 " LXOR " r:11`
we can see that the right hand side argument requires a precedence of at least 11
or greater, thus the second parse is invalid and we remain with: `(a LXOR b) LXOR c`
assuming that:

* `a` has precedence 10 or higher
* `b` has precedence 11 or higher
* `c` has precedence 11 or higher

Thus `LXOR` is a left associative notation. Can you make it right associative?

NOTE: If parameters of a notation are not explicitly given a precedence they will implicitly be tagged with precedence 0.

마지막으로 `notation` 예제에는 인수에 대한 `:precedence` 바인딩도 있습니다: `l:10`과 `r:11`. 이는 왼쪽 인수의 우선순위가 최소 10 이상이어야 하고, 오른쪽 인수의 우선순위는 11 이상이어야 함을 나타냅니다. 인수에 각각의 우선순위가 할당되는 방식은 해당 인수를 파싱하는 데 사용된 규칙의 우선순위를 살펴보는 것입니다. 예를 들어 `a LXOR b LXOR c`를 생각해봅시다. 이론적으로 두 가지 방식으로 파싱될 수 있습니다:

1. `(a LXOR b) LXOR c`
2. `a LXOR (b LXOR c)`

괄호 안의 인수들은 우선순위 10의 `LXOR` 규칙으로 파싱되므로, 외부 `LXOR` 규칙에 대해 우선순위 10의 인수로 나타납니다:

1. `(a LXOR b):10 LXOR c`
2. `a LXOR (b LXOR c):10`

그런데 `LXOR`의 정의인 `notation:10 l:10 " LXOR " r:11`을 보면, 우변 인수는 11 이상의 우선순위를 요구하므로 두 번째 파싱은 유효하지 않습니다. 따라서 다음을 가정할 때 `(a LXOR b) LXOR c`만 남습니다:

* `a`의 우선순위가 10 이상
* `b`의 우선순위가 11 이상
* `c`의 우선순위가 11 이상

따라서 `LXOR`는 좌결합 표기법입니다. 우결합으로 만들 수 있을까요?

참고: notation의 매개변수에 우선순위가 명시적으로 주어지지 않으면 암묵적으로 우선순위 0이 부여됩니다.

As a last remark for this section: Lean will always attempt to obtain the longest
matching parse possible, this has three important implications.
First a very intuitive one, if we have a right associative operator `^`
and Lean sees something like `a ^ b ^ c`, it will first parse the `a ^ b`
and then attempt to keep parsing (as long as precedence allows it) until
it cannot continue anymore. Hence Lean will parse this expression as `a ^ (b ^ c)`
(as we would expect it to).

Secondly, if we have a notation where precedence does not allow to figure
out how the expression should be parenthesized, for example:

이 섹션의 마지막 주의사항으로: Lean은 항상 가능한 가장 긴 파싱을 얻으려 시도합니다. 이는 세 가지 중요한 함의를 가집니다. 첫 번째는 매우 직관적인 것으로, 우결합 연산자 `^`가 있고 Lean이 `a ^ b ^ c`와 같은 식을 보면, 먼저 `a ^ b`를 파싱한 뒤 더 이상 계속할 수 없을 때까지(우선순위가 허용하는 한) 계속 파싱하려 합니다. 따라서 Lean은 이 식을 우리가 예상하는 대로 `a ^ (b ^ c)`로 파싱합니다.

두 번째로, 우선순위만으로 식의 괄호화를 결정할 수 없는 표기법이 있는 경우, 예를 들면:

```
notation:65 lhs:65 " ~ " rhs:65 => (lhs - rhs)
```

An expression like `a ~ b ~ c` will be parsed as `a ~ (b ~ c)` because
Lean attempts to find the longest parse possible. As a general rule of thumb:
If precedence is ambiguous Lean will default to right associativity.

`a ~ b ~ c`와 같은 식은 Lean이 가능한 가장 긴 파싱을 찾으려 하기 때문에 `a ~ (b ~ c)`로 파싱됩니다. 일반적인 경험 법칙으로: 우선순위가 모호하면 Lean은 기본적으로 우결합을 선택합니다.

```
#eval 5 ~ 3 ~ 3 -- 5 because this is parsed as 5 - (3 - 3)
```

Lastly, if we define overlapping notation such as:

마지막으로, 다음과 같이 겹치는 표기법을 정의하는 경우:

```
-- define `a ~ b mod rel` to mean that a and b are equivalent with respect to some equivalence relation rel
notation:65 a:65 " ~ " b:65 " mod " rel:65 => rel a b
```

Lean will prefer this notation over parsing `a ~ b` as defined above and
then erroring because it doesn't know what to do with `mod` and the
relation argument:

Lean은 위에서 정의한 대로 `a ~ b`를 파싱한 후 `mod`와 관계 인수를 처리하는 방법을 몰라 오류를 발생시키는 것보다 이 표기법을 선호합니다:

```
#check 0 ~ 0 mod Eq -- 0 = 0 : Prop
```

This is again because it is looking for the longest possible parser which
in this case involves also consuming `mod` and the relation argument.

이것 역시 가능한 가장 긴 파서를 찾기 때문이며, 이 경우에는 `mod`와 관계 인수도 함께 소비하는 것을 포함합니다.


With the above `infix` and `notation` commands, you can get quite far with
declaring ordinary mathematical syntax already. Lean does however allow you to
introduce arbitrarily complex syntax as well. This is done using two main commands
`syntax` and `declare_syntax_cat`. A `syntax` command allows you add a new
syntax rule to an already existing so-called "syntax category". The most common syntax
categories are:

* `term`, this category will be discussed in detail in the elaboration chapter,
  for now you can think of it as "the syntax of everything that has a value"
* `command`, this is the category for top-level commands like `#check`, `def` etc.
* TODO: ...

Let's see this in action:

위의 `infix`와 `notation` 명령만으로도 일반적인 수학적 syntax를 선언하는 데 꽤 멀리 갈 수 있습니다. 그러나 Lean은 임의로 복잡한 syntax도 도입할 수 있게 해줍니다. 이는 두 가지 주요 명령 `syntax`와 `declare_syntax_cat`을 사용하여 수행됩니다. `syntax` 명령은 이미 존재하는 소위 "syntax category"에 새 syntax 규칙을 추가할 수 있게 해줍니다. 가장 일반적인 syntax category는 다음과 같습니다:

* `term`: 이 category는 elaboration 챕터에서 자세히 다룰 것입니다. 지금은 "값을 가지는 모든 것의 syntax"라고 생각하면 됩니다
* `command`: `#check`, `def` 등과 같은 최상위 명령들을 위한 category입니다
* TODO: ...

실제로 확인해 보겠습니다:

```
syntax "MyTerm" : term
```

We can now write `MyTerm` in place of things like `1 + 1` and it will be
*syntactically* valid, this does not mean the code will compile yet,
it just means that the Lean parser can understand it:

이제 `1 + 1`과 같은 것들 대신 `MyTerm`을 쓸 수 있으며, 이것은 *문법적으로* 유효합니다. 아직 코드가 컴파일된다는 의미는 아니며, 단지 Lean 파서가 이를 이해할 수 있다는 것을 의미합니다:

```
#check_failure MyTerm
-- elaboration function for 'termMyTerm' has not been implemented
--   MyTerm
```

Note: `#check_failure` command allows incorrectly typed terms to be indicated without error.

참고: `#check_failure` 명령은 타입이 잘못된 항을 오류 없이 표시할 수 있게 해줍니다.

Implementing this so-called "elaboration function", which will actually
give meaning to this syntax in terms of Lean's fundamental `Expr` type,
is topic of the elaboration chapter.

소위 "elaboration 함수"를 구현하는 것, 즉 Lean의 기본 `Expr` 타입으로 이 syntax에 실제 의미를 부여하는 것은 elaboration 챕터의 주제입니다.

The `notation` and `infix` commands are utilities that conveniently bundle syntax declaration
with macro definition (for more on macros, see the macro chapter),
where the contents left of the `=>` declare the syntax.
All the previously mentioned principles from `notation` and `infix` regarding precedence
fully apply to `syntax` as well.

`notation`과 `infix` 명령은 syntax 선언과 macro 정의(macro에 대한 자세한 내용은 macro 챕터를 참조)를 편리하게 묶어주는 유틸리티입니다. 여기서 `=>` 왼쪽의 내용이 syntax를 선언합니다. 우선순위에 관한 `notation`과 `infix`의 앞서 언급된 모든 원칙들은 `syntax`에도 완전히 적용됩니다.

We can, of course, also involve other syntax into our own declarations
in order to build up syntax trees. For example, we could try to build our
own little boolean expression language:

물론 syntax 트리를 구성하기 위해 다른 syntax를 우리 자신의 선언에 포함시킬 수도 있습니다. 예를 들어, 우리만의 작은 boolean 식 언어를 만들어 볼 수 있습니다:

```
namespace Playground2

-- The scoped modifier makes sure the syntax declarations remain in this `namespace`
-- because we will keep modifying this along the chapter
scoped syntax "⊥" : term -- ⊥ for false
scoped syntax "⊤" : term -- ⊤ for true
scoped syntax:40 term " OR " term : term
scoped syntax:50 term " AND " term : term
#check_failure ⊥ OR (⊤ AND ⊥) -- elaboration function hasn't been implemented but parsing passes

end Playground2
```

While this does work, it allows arbitrary terms to the left and right of our
`AND` and `OR` operation. If we want to write a mini language that only accepts
our boolean language on a syntax level we will have to declare our own
syntax category on top. This is done using the `declare_syntax_cat` command:

이것이 작동하긴 하지만, `AND`와 `OR` 연산의 좌우에 임의의 term을 허용합니다. syntax 수준에서 우리의 boolean 언어만 허용하는 미니 언어를 작성하려면 별도의 syntax category를 선언해야 합니다. 이는 `declare_syntax_cat` 명령을 사용하여 수행됩니다:

```
declare_syntax_cat boolean_expr
syntax "⊥" : boolean_expr -- ⊥ for false
syntax "⊤" : boolean_expr -- ⊤ for true
syntax:40 boolean_expr " OR " boolean_expr : boolean_expr
syntax:50 boolean_expr " AND " boolean_expr : boolean_expr
```

Now that we are working in our own syntax category, we are completely
disconnected from the rest of the system. And these cannot be used in place of
terms anymore:

이제 우리 자신의 syntax category에서 작업하므로, 나머지 시스템과 완전히 단절됩니다. 그리고 이것들은 더 이상 term 대신 사용할 수 없습니다:

```
#check ⊥ AND ⊤ -- expected term
```

In order to integrate our syntax category into the rest of the system we will
have to extend an already existing one with new syntax, in this case we
will re-embed it into the `term` category:

우리의 syntax category를 나머지 시스템과 통합하려면 이미 존재하는 category를 새 syntax로 확장해야 합니다. 이 경우 `term` category에 재삽입할 것입니다:

```
syntax "[Bool|" boolean_expr "]" : term
#check_failure [Bool| ⊥ AND ⊤] -- elaboration function hasn't been implemented but parsing passes
```


In order to declare more complex syntax, it is often very desirable to have
some basic operations on syntax already built-in, these include:

* helper parsers without syntax categories (i.e. not extendable)
* alternatives
* repetitive parts
* optional parts

While all of these do have an encoding based on syntax categories, this
can make things quite ugly at times, so Lean provides an easier way to do all
of these.

In order to see all of these in action, we will briefly define a simple
binary expression syntax.
First things first, declaring named parsers that don't belong to a syntax
category is quite similar to ordinary `def`s:

더 복잡한 syntax를 선언하기 위해서는 다음과 같은 기본 연산들이 내장되어 있는 것이 매우 바람직합니다:

* syntax category 없는 헬퍼 파서 (즉, 확장 불가능)
* 대안(alternatives)
* 반복 부분
* 선택적 부분

이 모든 것들은 syntax category를 기반으로 인코딩할 수 있지만, 때로는 상당히 복잡해질 수 있으므로 Lean은 이 모든 것들을 더 쉽게 처리하는 방법을 제공합니다.

이것들을 실제로 확인하기 위해 간단한 이진 식 syntax를 간략하게 정의해 보겠습니다. 우선, syntax category에 속하지 않는 이름이 붙은 파서를 선언하는 것은 일반적인 `def`와 꽤 유사합니다:

```
syntax binOne := "O"
syntax binZero := "Z"
```

These named parsers can be used in the same positions as syntax categories
from above, their only difference to them is, that they are not extensible.
That is, they are directly expanded within syntax declarations,
and we cannot define new patterns for them as we would with proper syntax categories.
There does also exist a number of built-in named parsers that are generally useful,
most notably:

* `str` for string literals
* `num` for number literals
* `ident` for identifiers
* ... TODO: better list or link to compiler docs

Next up we want to declare a parser that understands digits, a binary digit is
either 0 or 1 so we can write:

이 이름이 붙은 파서들은 위의 syntax category와 같은 위치에서 사용할 수 있으며, 유일한 차이점은 확장 불가능하다는 것입니다. 즉, 이들은 syntax 선언 내에서 직접 확장되며, 적절한 syntax category처럼 새 패턴을 정의할 수 없습니다. 일반적으로 유용한 다수의 내장 이름 파서도 있습니다. 가장 주목할 만한 것들은:

* `str`: 문자열 리터럴용
* `num`: 숫자 리터럴용
* `ident`: 식별자용
* ... TODO: 더 나은 목록 또는 컴파일러 문서 링크

다음으로 숫자를 이해하는 파서를 선언하려 합니다. 이진 숫자는 0 또는 1이므로 다음과 같이 작성할 수 있습니다:

```
syntax binDigit := binZero <|> binOne
```

Where the `<|>` operator implements the "accept the left or the right" behaviour.
We can also chain them to achieve parsers that accept arbitrarily many, arbitrarily complex
other ones. Now we will define the concept of a binary number, usually this would be written
as digits directly after each other but we will instead use comma separated ones to showcase
the repetition feature:

여기서 `<|>` 연산자는 "왼쪽 또는 오른쪽을 받아들이는" 동작을 구현합니다. 이를 연쇄적으로 사용하여 임의로 많고 복잡한 다른 것들을 받아들이는 파서를 만들 수도 있습니다. 이제 이진수의 개념을 정의할 것입니다. 보통 이것은 숫자들을 바로 연속해서 쓰는 방식이지만, 반복 기능을 보여주기 위해 쉼표로 구분된 것들을 사용하겠습니다:

```
-- the "+" denotes "one or many", in order to achieve "zero or many" use "*" instead
-- the "," denotes the separator between the `binDigit`s, if left out the default separator is a space
syntax binNumber := binDigit,+
```

Since we can just use named parsers in place of syntax categories, we can now easily
add this to the `term` category:

syntax category 대신 이름이 붙은 파서를 사용할 수 있으므로, 이제 쉽게 이것을 `term` category에 추가할 수 있습니다:

```
syntax "bin(" binNumber ")" : term
#check bin(Z, O, Z, Z, O) -- elaboration function hasn't been implemented but parsing passes
#check bin() -- fails to parse because `binNumber` is "one or many": expected 'O' or 'Z'
```

```
syntax binNumber' := binDigit,* -- note the *
syntax "emptyBin(" binNumber' ")" : term
#check_failure emptyBin() -- elaboration function hasn't been implemented but parsing passes
```

Note that nothing is limiting us to only using one syntax combinator per parser,
we could also have written all of this inline:

파서당 하나의 syntax combinator만 사용하도록 제한하는 것은 없으며, 이 모든 것을 인라인으로 작성할 수도 있었습니다:

```
syntax "binCompact(" ("Z" <|> "O"),+ ")" : term
#check_failure binCompact(Z, O, Z, Z, O) -- elaboration function hasn't been implemented but parsing passes
```

As a final feature, let's add an optional string comment that explains the binary
literal being declared:

마지막 기능으로, 선언되는 이진 리터럴을 설명하는 선택적 문자열 주석을 추가해 보겠습니다:

```
-- The (...)? syntax means that the part in parentheses is optional
syntax "binDoc(" (str ";")? binNumber ")" : term
#check_failure binDoc(Z, O, Z, Z, O) -- elaboration function hasn't been implemented but parsing passes
#check_failure binDoc("mycomment"; Z, O, Z, Z, O) -- elaboration function hasn't been implemented but parsing passes
```


As explained above, we will not go into detail in this chapter on how to teach
Lean about the meaning you want to give your syntax. We will, however, take a look
at how to write functions that operate on it. Like all things in Lean, syntax is
represented by the inductive type `Lean.Syntax`, on which we can operate. It does
contain quite some information, but most of what we are interested in, we can
condense in the following simplified view:

위에서 설명한 것처럼, 이 챕터에서는 Lean에게 syntax에 부여하려는 의미를 가르치는 방법에 대해 자세히 다루지 않겠습니다. 그러나 syntax에서 작동하는 함수를 작성하는 방법은 살펴보겠습니다. Lean의 모든 것과 마찬가지로, syntax는 우리가 조작할 수 있는 귀납 타입 `Lean.Syntax`로 표현됩니다. 꽤 많은 정보를 담고 있지만, 우리가 관심 있는 대부분은 다음의 간략화된 뷰로 요약할 수 있습니다:

```
namespace Playground2

inductive Syntax where
  | missing : Syntax
  | node (kind : Lean.SyntaxNodeKind) (args : Array Syntax) : Syntax
  | atom : String -> Syntax
  | ident : Lean.Name -> Syntax

end Playground2
```

Lets go through the definition one constructor at a time:

* `missing` is used when there is something the Lean compiler cannot parse,
  it is what allows Lean to have a syntax error in one part of the file but
  recover from it and try to understand the rest of it. This also means we pretty
  much don't care about this constructor.
* `node` is, as the name suggests, a node in the syntax tree. It has a so called
  `kind : SyntaxNodeKind` where `SyntaxNodeKind` is just a `Lean.Name`. Basically,
  each of our `syntax` declarations receives an automatically generated `SyntaxNodeKind`
  (we can also explicitly specify the name with `syntax (name := foo) ... : cat`) so
  we can tell Lean "this function is responsible for processing this specific syntax construct".
  Furthermore, like all nodes in a tree, it has children, in this case in the form of
  an `Array Syntax`.
* `atom` represents (with the exception of one) every syntax object that is at the bottom of the
  hierarchy. For example, our operators `⊕` and `LXOR` from above will be represented as
  atoms.
* `ident` is the mentioned exception to this rule. The difference between `ident` and `atom`
  is also quite obvious: an identifier has a `Lean.Name` instead of a `String` that represents it.
  Why a `Lean.Name` is not just a `String` is related to a concept called macro hygiene
  that will be discussed in detail in the macro chapter. For now, you can consider them
  basically equivalent.

각 생성자를 하나씩 살펴보겠습니다:

* `missing`은 Lean 컴파일러가 파싱할 수 없는 것이 있을 때 사용됩니다. 이것이 Lean이 파일의 한 부분에서 syntax 오류가 있어도 복구하고 나머지를 이해하려 시도할 수 있게 해주는 것입니다. 이는 또한 우리가 이 생성자에 대해 거의 신경 쓰지 않는다는 것을 의미합니다.
* `node`는 이름에서 알 수 있듯이 syntax 트리의 노드입니다. `SyntaxNodeKind`가 단순히 `Lean.Name`인 소위 `kind : SyntaxNodeKind`를 가집니다. 기본적으로, 우리의 각 `syntax` 선언은 자동으로 생성된 `SyntaxNodeKind`를 받습니다(`syntax (name := foo) ... : cat`으로 이름을 명시적으로 지정할 수도 있습니다). 이를 통해 Lean에게 "이 함수가 이 특정 syntax 구성요소를 처리하는 역할을 합니다"라고 알릴 수 있습니다. 또한 트리의 모든 노드처럼 자식을 가지며, 이 경우 `Array Syntax` 형태입니다.
* `atom`은 (하나의 예외를 제외하고) 계층 구조의 최하위에 있는 모든 syntax 객체를 나타냅니다. 예를 들어, 위의 연산자 `⊕`와 `LXOR`는 atom으로 표현됩니다.
* `ident`는 언급된 이 규칙의 예외입니다. `ident`와 `atom`의 차이점도 매우 명확합니다: 식별자는 이를 나타내는 `String` 대신 `Lean.Name`을 가집니다. `Lean.Name`이 단순한 `String`이 아닌 이유는 macro 챕터에서 자세히 다룰 macro hygiene이라는 개념과 관련이 있습니다. 지금은 이들을 기본적으로 동등하다고 생각하면 됩니다.


Now that we know how syntax is represented in Lean, we could of course write programs that
generate all of these inductive trees by hand, which would be incredibly tedious and is something
we most definitely want to avoid. Luckily for us there is quite an extensive API hidden inside the
`Lean.Syntax` namespace we can explore:

이제 Lean에서 syntax가 어떻게 표현되는지 알게 되었으니, 물론 이 귀납 트리들을 모두 수동으로 생성하는 프로그램을 작성할 수도 있습니다. 하지만 이는 매우 지루한 작업이며 우리가 반드시 피하고 싶은 것입니다. 다행히도 우리가 탐색할 수 있는 상당히 광범위한 API가 `Lean.Syntax` namespace 안에 숨어 있습니다:

```
open Lean
#check Syntax -- Syntax. autocomplete
```

The interesting functions for creating `Syntax` are the `Syntax.mk*` ones that allow us to create
both very basic `Syntax` objects like `ident`s but also more complex ones like `Syntax.mkApp`
which we can use to create the `Syntax` object that would amount to applying the function
from the first argument to the argument list (all given as `Syntax`) in the second one.
Let's see a few examples:

`Syntax`를 생성하는 흥미로운 함수들은 `Syntax.mk*` 계열로, `ident`와 같은 매우 기본적인 `Syntax` 객체뿐만 아니라 `Syntax.mkApp`과 같은 더 복잡한 것들도 만들 수 있습니다. `Syntax.mkApp`은 첫 번째 인수의 함수를 두 번째 인수의 인수 목록(모두 `Syntax`로 주어짐)에 적용하는 `Syntax` 객체를 만드는 데 사용할 수 있습니다. 몇 가지 예를 살펴보겠습니다:

```
-- Name literals are written with this little ` in front of the name
#eval Syntax.mkApp (mkIdent `Nat.add) #[Syntax.mkNumLit "1", Syntax.mkNumLit "1"] -- is the syntax of `Nat.add 1 1`
#eval mkNode `«term_+_» #[Syntax.mkNumLit "1", mkAtom "+", Syntax.mkNumLit "1"] -- is the syntax for `1 + 1`

-- note that the `«term_+_» is the auto-generated SyntaxNodeKind for the + syntax
```

If you don't like this way of creating `Syntax` at all you are not alone.
However, there are a few things involved with the machinery of doing this in
a pretty and correct (the machinery is mostly about the correct part) way
which will be explained in the macro chapter.

이 방식으로 `Syntax`를 생성하는 것이 전혀 마음에 들지 않더라도 그럴 만합니다. 그러나 이것을 예쁘고 올바르게(주로 올바른 부분에 관한 것입니다) 수행하는 기계적 장치와 관련된 몇 가지 사항이 있으며, 이는 macro 챕터에서 설명할 것입니다.


Just like constructing `Syntax` is an important topic, especially
with macros, matching on syntax is equally (or in fact even more) interesting.
Luckily we don't have to match on the inductive type itself either: we can
instead use so-called "syntax patterns". They are quite simple, their syntax is just
`` `(the syntax I want to match on) ``. Let's see one in action:

`Syntax`를 구성하는 것이 중요한 주제인 것처럼, 특히 macro에서는 syntax에 대한 매칭도 동등하게(사실은 더) 흥미롭습니다. 다행히도 귀납 타입 자체에 매칭할 필요도 없습니다. 대신 소위 "syntax 패턴"을 사용할 수 있습니다. 이것들은 매우 간단하며, 그 syntax는 단순히 `` `(매칭하려는 syntax) ``입니다. 실제로 확인해 보겠습니다:

```
def isAdd11 : Syntax → Bool
  | `(Nat.add 1 1) => true
  | _ => false

#eval isAdd11 (Syntax.mkApp (mkIdent `Nat.add) #[Syntax.mkNumLit "1", Syntax.mkNumLit "1"]) -- true
#eval isAdd11 (Syntax.mkApp (mkIdent `Nat.add) #[mkIdent `foo, Syntax.mkNumLit "1"]) -- false
```

The next level with matches is to capture variables from the input instead
of just matching on literals, this is done with a slightly fancier-looking syntax:

매칭의 다음 단계는 리터럴에만 매칭하는 것이 아니라 입력에서 변수를 캡처하는 것입니다. 이것은 약간 더 세련된 syntax로 수행됩니다:

```
def isAdd : Syntax → Option (Syntax × Syntax)
  | `(Nat.add $x $y) => some (x, y)
  | _ => none

#eval isAdd (Syntax.mkApp (mkIdent `Nat.add) #[Syntax.mkNumLit "1", Syntax.mkNumLit "1"]) -- some ...
#eval isAdd (Syntax.mkApp (mkIdent `Nat.add) #[mkIdent `foo, Syntax.mkNumLit "1"]) -- some ...
#eval isAdd (Syntax.mkApp (mkIdent `Nat.add) #[mkIdent `foo]) -- none
```


Note that `x` and `y` in this example are of type `` TSyntax `term ``, not `Syntax`.
Even though we are pattern matching on `Syntax` which, as we can see in the constructors,
is purely composed of types that are not `TSyntax`, so what is going on?
Basically the `` `() `` Syntax is smart enough to figure out the most general
syntax category the syntax we are matching might be coming from (in this case `term`).
It will then use the typed syntax type `TSyntax` which is parameterized
by the `Name` of the syntax category it came from. This is not only more
convenient for the programmer to see what is going on, it also has other
benefits. For example, if we limit the syntax category to just `num`
in the next example Lean will allow us to call `getNat` on the resulting
`` TSyntax `num `` directly without pattern matching or the option to panic:

이 예제에서 `x`와 `y`는 `Syntax`가 아닌 `` TSyntax `term `` 타입임에 주목하세요. 생성자에서 볼 수 있듯이 `Syntax`에 대해 패턴 매칭을 하고 있지만 이는 `TSyntax`가 아닌 타입으로만 구성되어 있습니다. 그렇다면 무슨 일이 벌어지고 있는 걸까요? 기본적으로 `` `() `` syntax는 우리가 매칭하는 syntax가 어느 syntax category에서 올 수 있는지 가장 일반적인 것(이 경우 `term`)을 파악할 만큼 똑똑합니다. 그런 다음 그것이 온 syntax category의 `Name`으로 매개변수화된 타입이 있는 syntax 타입 `TSyntax`를 사용합니다. 이것은 프로그래머가 상황을 파악하는 데 더 편리할 뿐만 아니라 다른 이점들도 있습니다. 예를 들어, 다음 예제에서 syntax category를 `num`으로만 제한하면, Lean은 패턴 매칭이나 panic 옵션 없이 결과로 나온 `` TSyntax `num ``에 직접 `getNat`을 호출할 수 있게 해줍니다:

```
-- Now we are also explicitly marking the function to operate on term syntax
def isLitAdd : TSyntax `term → Option Nat
  | `(Nat.add $x:num $y:num) => some (x.getNat + y.getNat)
  | _ => none

#eval isLitAdd (Syntax.mkApp (mkIdent `Nat.add) #[Syntax.mkNumLit "1", Syntax.mkNumLit "1"]) -- some 2
#eval isLitAdd (Syntax.mkApp (mkIdent `Nat.add) #[mkIdent `foo, Syntax.mkNumLit "1"]) -- none
```

If you want to access the `Syntax` behind a `TSyntax` you can do this using
`TSyntax.raw` although the coercion machinery should just work most of the time.
We will see some further benefits of the `TSyntax` system in the macro chapter.

`TSyntax` 뒤에 있는 `Syntax`에 접근하려면 `TSyntax.raw`를 사용하면 됩니다. 단, 강제 변환 기계가 대부분의 경우에는 그냥 작동합니다. `TSyntax` 시스템의 추가적인 이점들은 macro 챕터에서 확인할 것입니다.

One last important note about the matching on syntax: In this basic
form it only works on syntax from the `term` category. If you want to use
it to match on your own syntax categories you will have to use  `` `(category| ...) ``.

syntax 매칭에 대한 마지막 중요한 참고사항: 이 기본 형태에서는 `term` category의 syntax에만 작동합니다. 자신의 syntax category에 매칭하려면 `` `(category| ...) ``를 사용해야 합니다.


As a final mini project for this chapter we will declare the syntax of a mini
arithmetic expression language and a function of type `Syntax → Nat` to evaluate
it. We will see more about some of the concepts presented below in future
chapters.

이 챕터의 최종 미니 프로젝트로, 미니 산술 식 언어의 syntax와 이를 평가하는 `Syntax → Nat` 타입의 함수를 선언할 것입니다. 아래에서 제시된 개념 중 일부에 대해서는 이후 챕터에서 더 자세히 알아볼 것입니다.

```
declare_syntax_cat arith

syntax num : arith
syntax arith "-" arith : arith
syntax arith "+" arith : arith
syntax "(" arith ")" : arith

partial def denoteArith : TSyntax `arith → Nat
  | `(arith| $x:num) => x.getNat
  | `(arith| $x:arith + $y:arith) => denoteArith x + denoteArith y
  | `(arith| $x:arith - $y:arith) => denoteArith x - denoteArith y
  | `(arith| ($x:arith)) => denoteArith x
  | _ => 0

-- You can ignore Elab.TermElabM, what is important for us is that it allows
-- us to use the ``(arith| (12 + 3) - 4)` notation to construct `Syntax`
-- instead of only being able to match on it like this.
def test : Elab.TermElabM Nat := do
  let stx ← `(arith| (12 + 3) - 4)
  pure (denoteArith stx)

#eval test -- 11
```

Feel free to play around with this example and extend it in whatever way
you want to. The next chapters will mostly be about functions that operate
on `Syntax` in some way.

이 예제를 자유롭게 가지고 놀고 원하는 방식으로 확장해 보세요. 다음 챕터들은 주로 어떤 방식으로든 `Syntax`에서 작동하는 함수들에 관한 것입니다.


We can use type classes in order to add notation that is extensible via
the type instead of the syntax system, this is for example how `+`
using the typeclasses `HAdd` and `Add` and other common operators in
Lean are generically defined.

For example, we might want to have a generic notation for subset notation.
The first thing we have to do is define a type class that captures
the function we want to build notation for.

syntax 시스템 대신 타입을 통해 확장 가능한 표기법을 추가하기 위해 type class를 사용할 수 있습니다. 예를 들어 `HAdd`와 `Add` typeclass를 사용하는 `+`와 Lean의 다른 일반 연산자들이 이런 방식으로 일반적으로 정의됩니다.

예를 들어, 부분집합 표기법에 대한 일반적인 표기법이 필요할 수 있습니다. 먼저 해야 할 것은 표기법을 만들고자 하는 함수를 캡처하는 type class를 정의하는 것입니다.

```
class Subset (α : Type u) where
  subset : α → α → Prop
```

The second step is to define the notation, what we can do here is simply
turn every instance of a `⊆` appearing in the code to a call to `Subset.subset`
because the type class resolution should be able to figure out which `Subset`
instance is referred to. Thus the notation will be a simple:

두 번째 단계는 표기법을 정의하는 것입니다. 여기서 할 수 있는 것은 단순히 코드에 나타나는 `⊆`의 모든 인스턴스를 `Subset.subset` 호출로 변환하는 것입니다. type class resolution이 어떤 `Subset` 인스턴스가 참조되는지 파악할 수 있기 때문입니다. 따라서 표기법은 단순히:

```
-- precedence is arbitrary for this example
infix:50 " ⊆ " => Subset.subset
```

Let's define a simple theory of sets to test it:

이것을 테스트하기 위해 간단한 집합 이론을 정의해 봅시다:

```
-- a `Set` is defined by the elements it contains
-- -> a simple predicate on the type of its elements
def Set (α : Type u) := α → Prop

def Set.mem (X : Set α) (x : α) : Prop := X x

-- Integrate into the already existing typeclass for membership notation
instance : Membership α (Set α) where
  mem := Set.mem

def Set.empty : Set α := λ _ => False

instance : Subset (Set α) where
  subset X Y := ∀ (x : α), x ∈ X → x ∈ Y

example : ∀ (X : Set α), Set.empty ⊆ X := by
  intro X x
  -- ⊢ x ∈ Set.empty → x ∈ X
  intro h
  exact False.elim h -- empty set has no members
```


Because declaring syntax that uses variable binders used to be a rather
unintuitive thing to do in Lean 3, we'll take a brief look at how naturally
this can be done in Lean 4.

For this example we will define the well-known notation for the set
that contains all elements `x` such that some property holds:
`{x ∈ ℕ | x < 10}` for example.

First things first we need to extend the theory of sets from above slightly:

변수 바인더를 사용하는 syntax를 선언하는 것이 Lean 3에서는 다소 직관적이지 않은 일이었기 때문에, Lean 4에서 이것이 얼마나 자연스럽게 이루어질 수 있는지 간략히 살펴보겠습니다.

이 예제에서는 어떤 속성이 성립하는 모든 원소 `x`를 포함하는 집합에 대한 잘 알려진 표기법을 정의할 것입니다: 예를 들어 `{x ∈ ℕ | x < 10}`.

우선 위의 집합 이론을 약간 확장해야 합니다:

```
-- the basic "all elements such that" function for the notation
def setOf {α : Type} (p : α → Prop) : Set α := p
```

Equipped with this function, we can now attempt to intuitively define a
basic version of our notation:

이 함수를 갖추면, 이제 우리의 표기법의 기본 버전을 직관적으로 정의해 볼 수 있습니다:

```
notation "{ " x " | " p " }" => setOf (fun x => p)

#check { (x : Nat) | x ≤ 1 } -- { x | x ≤ 1 } : Set Nat

example : 1 ∈ { (y : Nat) | y ≤ 1 } := by simp[Membership.mem, Set.mem, setOf]
example : 2 ∈ { (y : Nat) | y ≤ 3 ∧ 1 ≤ y } := by simp[Membership.mem, Set.mem, setOf]
```

This intuitive notation will indeed deal with what we could throw at
it in the way we would expect it.

As to how one might extend this notation to allow more set-theoretic
things such as `{x ∈ X | p x}` and leave out the parentheses around
the bound variables, we refer the reader to the macro chapter.

이 직관적인 표기법은 우리가 던질 수 있는 것들을 예상한 대로 처리할 것입니다.

`{x ∈ X | p x}`와 같은 더 많은 집합론적인 것들을 허용하고 한정 변수 주위의 괄호를 생략하도록 이 표기법을 어떻게 확장할 수 있는지에 대해서는 독자를 macro 챕터로 안내합니다.


1. Create an "urgent minus 💀" notation such that `5 * 8 💀 4` returns `20`, and `8 💀 6 💀 1` returns `3`.

   **a)** Using `notation` command.
   **b)** Using `infix` command.
   **c)** Using `syntax` command.

   Hint: multiplication in Lean 4 is defined as `infixl:70 " * " => HMul.hMul`.
2. Consider the following syntax categories: `term`, `command`, `tactic`; and 3 syntax rules given below. Make use of each of these newly defined syntaxes.

   ```
     syntax "good morning" : term
     syntax "hello" : command
     syntax "yellow" : tactic
   ```
3. Create a `syntax` rule that would accept the following commands:

   * `red red red 4`
   * `blue 7`
   * `blue blue blue blue blue 18`

   (So, either all `red`s followed by a number; or all `blue`s followed by a number; `red blue blue 5` - shouldn't work.)

   Use the following code template:

   ```
   syntax (name := colors) ...
   -- our "elaboration function" that infuses syntax with semantics
   @[command_elab colors] def elabColors : CommandElab := λ stx => Lean.logInfo "success!"
   ```
4. Mathlib has a `#help option` command that displays all options available in the current environment, and their descriptions. `#help option pp.r` will display all options starting with a "pp.r" substring.

   Create a `syntax` rule that would accept the following commands:

   * `#better_help option`
   * `#better_help option pp.r`
   * `#better_help option some.other.name`

   Use the following template:

   ```
   syntax (name := help) ...
   -- our "elaboration function" that infuses syntax with semantics
   @[command_elab help] def elabHelp : CommandElab := λ stx => Lean.logInfo "success!"
   ```
5. Mathlib has a ∑ operator. Create a `syntax` rule that would accept the following terms:

   * `∑ x in { 1, 2, 3 }, x^2`
   * `∑ x in { "apple", "banana", "cherry" }, x.length`

   Use the following template:

   ```
   import Batteries.Classes.SetNotation
   import Batteries.Util.ExtendedBinder
   syntax (name := bigsumin) ...
   -- our "elaboration function" that infuses syntax with semantics
   @[term_elab bigsumin] def elabSum : TermElab := λ stx tp => return mkNatLit 666
   ```

   Hint: use the `Batteries.ExtendedBinder.extBinder` parser.
   Hint: you need Batteries installed in your Lean project for these imports to work.