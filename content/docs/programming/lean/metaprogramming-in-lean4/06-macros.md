---
title: "6. 매크로"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "metaprogramming"]
categories: ["programming"]
description: "Lean 4 매크로: syntax 변환을 통한 새로운 notation과 shortcut 정의"
---

Macros in Lean are `Syntax → MacroM Syntax` functions. `MacroM` is the macro
monad which allows macros to have some static guarantees we will discuss in the
next section, you can mostly ignore it for now.

Lean에서 매크로는 `Syntax → MacroM Syntax` 함수입니다. `MacroM`은 매크로 모나드로, 다음 섹션에서 다룰 일부 정적 보장을 매크로에 제공합니다. 지금은 무시해도 됩니다.

Macros are registered as handlers for a specific syntax declaration using the
`macro` attribute. The compiler will take care of applying these function
to the syntax for us before performing actual analysis of the input. This
means that the only thing we have to do is declare our syntax with a specific
name and bind a function of type `Lean.Macro` to it. Let's try to reproduce
the `LXOR` notation from the `Syntax` chapter:

매크로는 `macro` 속성을 사용하여 특정 syntax 선언의 핸들러로 등록됩니다. 컴파일러는 실제 입력 분석을 수행하기 전에 이 함수들을 syntax에 적용하는 일을 처리합니다. 따라서 우리가 해야 할 일은 특정 이름으로 syntax를 선언하고 `Lean.Macro` 타입의 함수를 바인딩하는 것뿐입니다. `Syntax` 챕터의 `LXOR` 표기법을 재현해 봅시다:

```
import Lean

open Lean

syntax:10 (name := lxor) term:10 " LXOR " term:11 : term

@[macro lxor] def lxorImpl : Macro
  | `($l:term LXOR $r:term) => `(!$l && $r) -- we can use the quotation mechanism to create `Syntax` in macros
  | _ => Macro.throwUnsupported

#eval true LXOR true -- false
#eval true LXOR false -- false
#eval false LXOR true -- true
#eval false LXOR false -- false
```

That was quite easy! The `Macro.throwUnsupported` function can be used by a macro
to indicate that "it doesn't feel responsible for this syntax". In this case
it's merely used to fill a wildcard pattern that should never be reached anyways.

꽤 쉬웠죠! `Macro.throwUnsupported` 함수는 매크로가 "이 syntax에 대한 책임이 없다"고 나타낼 때 사용할 수 있습니다. 이 경우에는 어차피 도달하지 않아야 할 와일드카드 패턴을 채우기 위해 사용되었을 뿐입니다.

However we can in fact register multiple macros for the same syntax this way
if we desire, they will be tried one after another (the later registered ones have
higher priority) -- is "higher" correct?
until one throws either a real error using `Macro.throwError` or succeeds, that
is it does not `Macro.throwUnsupported`. Let's see this in action:

그러나 원한다면 같은 syntax에 여러 매크로를 등록할 수 있습니다. 이 경우 나중에 등록된 것이 더 높은 우선순위를 가지며, 하나가 `Macro.throwError`로 실제 오류를 던지거나 성공할 때까지(즉, `Macro.throwUnsupported`를 던지지 않을 때까지) 하나씩 시도됩니다. 이를 실제로 확인해 봅시다:

```
@[macro lxor] def lxorImpl2 : Macro
  -- special case that changes behaviour of the case where the left and
  -- right hand side are these specific identifiers
  | `(true LXOR true) => `(true)
  | _ => Macro.throwUnsupported

#eval true LXOR true -- true, handled by new macro
#eval true LXOR false -- false, still handled by the old
```

This capability is obviously *very* powerful! It should not be used
lightly and without careful thinking since it can introduce weird
behaviour while writing code later on. The following example illustrates
this weird behaviour:

이 기능은 분명히 *매우* 강력합니다! 나중에 코드를 작성할 때 이상한 동작을 유발할 수 있으므로 신중한 고려 없이 가볍게 사용해서는 안 됩니다. 다음 예제는 이런 이상한 동작을 보여줍니다:

```
#eval true LXOR true -- true, handled by new macro

def foo := true
#eval foo LXOR foo -- false, handled by old macro, after all the identifiers have a different name
```

Without knowing exactly how this macro is implemented this behaviour
will be very confusing to whoever might be debugging an issue based on this.
The rule of thumb for when to use a macro vs. other mechanisms like
elaboration is that as soon as you are building real logic like in the 2nd
macro above, it should most likely not be a macro but an elaborator
(explained in the elaboration chapter). This means ideally we want to
use macros for simple syntax to syntax translations, that a human could
easily write out themselves as well but is too lazy to.

이 매크로가 정확히 어떻게 구현되었는지 모른다면, 이를 기반으로 문제를 디버깅하는 사람에게 이 동작은 매우 혼란스러울 것입니다. 매크로를 사용할지 elaboration 같은 다른 메커니즘을 사용할지에 대한 경험칙은, 위의 두 번째 매크로처럼 실제 로직을 구축하기 시작하면 매크로보다는 elaborator(elaboration 챕터에서 설명)를 사용해야 한다는 것입니다. 이상적으로 매크로는 사람이 직접 작성할 수 있지만 귀찮아서 하지 않는 간단한 syntax-to-syntax 변환에 사용해야 합니다.

Now that we know the basics of what a macro is and how to register it
we can take a look at slightly more automated ways to do this (in fact
all of the ways about to be presented are implemented as macros themselves).

이제 매크로가 무엇인지, 어떻게 등록하는지 기본을 알았으니 이를 더 자동화된 방법으로 할 수 있는 방법을 살펴보겠습니다(사실 앞으로 소개할 모든 방법은 자체적으로 매크로로 구현되어 있습니다).

First things first there is `macro_rules` which basically desugars to
functions like the ones we wrote above, for example:

먼저 `macro_rules`가 있는데, 이는 기본적으로 위에서 작성한 것과 같은 함수로 desugar됩니다. 예를 들면:

```
syntax:10 term:10 " RXOR " term:11 : term

macro_rules
  | `($l:term RXOR $r:term) => `($l && !$r)
```

As you can see, it figures out lot's of things on its own for us:

보시다시피, 많은 것들을 자동으로 처리해 줍니다:

* the name of the syntax declaration
* the `macro` attribute registration
* the `throwUnsupported` wildcard

* syntax 선언의 이름
* `macro` 속성 등록
* `throwUnsupported` 와일드카드

apart from this it just works like a function that is using pattern
matching syntax, we can in theory encode arbitrarily complex macro
functions on the right hand side.

이 외에는 패턴 매칭 syntax를 사용하는 함수처럼 작동하며, 이론적으로 오른쪽에 임의로 복잡한 매크로 함수를 인코딩할 수 있습니다.

If this is still not short enough for you, there is a next step using the
`macro` macro:

아직도 충분히 짧지 않다면, `macro` 매크로를 사용하는 다음 단계가 있습니다:

```
macro l:term:10 " ⊕ " r:term:11 : term => `((!$l && $r) || ($l && !$r))

#eval true ⊕ true -- false
#eval true ⊕ false -- true
#eval false ⊕ true -- true
#eval false ⊕ false -- false
```

As you can see, `macro` is quite close to `notation` already:

보시다시피, `macro`는 이미 `notation`에 꽤 가깝습니다:

* it performed syntax declaration for us
* it automatically wrote a `macro_rules` style function to match on it

* syntax 선언을 자동으로 처리해 줍니다
* 매칭을 위한 `macro_rules` 스타일 함수를 자동으로 작성합니다

The are of course differences as well:

물론 차이점도 있습니다:

* `notation` is limited to the `term` syntax category
* `notation` cannot have arbitrary macro code on the right hand side

* `notation`은 `term` syntax 카테고리로 제한됩니다
* `notation`은 오른쪽에 임의의 매크로 코드를 가질 수 없습니다

So far we've handwaved the `` `(foo $bar) `` syntax to both create and
match on `Syntax` objects but it's time for a full explanation since
it will be essential to all non trivial things that are syntax related.

지금까지 `` `(foo $bar) `` syntax를 `Syntax` 객체를 생성하고 매칭하는 데 모두 사용한다고 대략적으로 설명했지만, 이제 syntax와 관련된 모든 비자명한 것들에 필수적이므로 완전한 설명을 할 때가 되었습니다.

First things first we call the `` `() `` syntax a `Syntax` quotation.
When we plug variables into a syntax quotation like this: `` `($x) ``
we call the `$x` part an anti-quotation. When we insert `x` like this
it is required that `x` is of type `TSyntax y` where `y` is some `Name`
of a syntax category. The Lean compiler is actually smart enough to figure
the syntax categories that are allowed in this place out. Hence you might
sometimes see errors of the form:

먼저 `` `() `` syntax를 `Syntax` 인용(quotation)이라고 부릅니다. `` `($x) ``처럼 syntax 인용에 변수를 삽입할 때, `$x` 부분을 역인용(anti-quotation)이라고 부릅니다. 이런 식으로 `x`를 삽입할 때, `x`는 `TSyntax y` 타입이어야 하며, 여기서 `y`는 어떤 syntax 카테고리의 `Name`입니다. Lean 컴파일러는 이 위치에서 허용되는 syntax 카테고리를 자동으로 파악할 만큼 충분히 똑똑합니다. 따라서 때때로 다음과 같은 형식의 오류를 볼 수 있습니다:

```
application type mismatch
  x.raw
argument
  x
has type
  TSyntax `a : Type
but is expected to have type
  TSyntax `b : Type
```

If you are sure that your thing from the `a` syntax category can be
used as a `b` here you can declare a coercion of the form:

`a` syntax 카테고리의 것이 여기서 `b`로 사용될 수 있다고 확신한다면 다음과 같은 형식의 강제 변환(coercion)을 선언할 수 있습니다:

```
instance : Coe (TSyntax `a) (TSyntax `b) where
  coe s := ⟨s.raw⟩
```

Which will allow Lean to perform the type cast automatically. If you
notice that your `a` can not be used in place of the `b` here congrats,
you just discovered a bug in your `Syntax` function. Similar to the Lean
compiler, you could also declare functions that are specific to certain
`TSyntax` variants. For example as we have seen in the syntax chapter
there exists the function:

이렇게 하면 Lean이 자동으로 타입 캐스트를 수행할 수 있습니다. `a`가 여기서 `b` 대신 사용될 수 없다는 것을 발견하면, 축하합니다, `Syntax` 함수의 버그를 발견한 것입니다. Lean 컴파일러와 유사하게, 특정 `TSyntax` 변형에 특화된 함수를 선언할 수도 있습니다. 예를 들어 syntax 챕터에서 보았듯이 다음과 같은 함수가 존재합니다:

```
#check TSyntax.getNat -- TSyntax.getNat : TSyntax numLitKind → Nat
```

Which is guaranteed to not panic because we know that the `Syntax` that
the function is receiving is a numeric literal and can thus naturally
be converted to a `Nat`.

함수가 받는 `Syntax`가 숫자 리터럴임을 알기 때문에 패닉이 발생하지 않으며, 자연스럽게 `Nat`으로 변환될 수 있습니다.

If we use the antiquotation syntax in pattern matching it will, as discussed
in the syntax chapter, give us a variable `x` of type `TSyntax y` where
`y` is the `Name` of the syntax category that fits in the spot where we pattern matched.
If we wish to insert a literal `$x` into the `Syntax` for some reason,
for example macro creating macros, we can escape the anti quotation using: `` `($$x) ``.

패턴 매칭에서 역인용 syntax를 사용하면, syntax 챕터에서 논의한 것처럼, 패턴 매칭한 위치에 맞는 syntax 카테고리의 `Name`인 `y`를 가진 `TSyntax y` 타입의 변수 `x`를 제공합니다. 어떤 이유로 `Syntax`에 리터럴 `$x`를 삽입하고 싶다면(예: 매크로를 생성하는 매크로), `` `($$x) ``를 사용하여 역인용을 이스케이프할 수 있습니다.

If we want to specify the syntax kind we wish `x` to be interpreted as
we can make this explicit using: `` `($x:term) `` where `term` can be
replaced with any other valid syntax category (e.g. `command`) or parser
(e.g. `ident`).

`x`를 해석할 syntax 종류를 명시하려면 `` `($x:term) ``을 사용하여 이를 명시적으로 지정할 수 있으며, 여기서 `term`은 다른 유효한 syntax 카테고리(예: `command`)나 파서(예: `ident`)로 대체될 수 있습니다.

So far this is only a more formal explanation of the intuitive things
we've already seen in the syntax chapter and up to now in this chapter,
next we'll discuss some more advanced anti-quotations.

지금까지는 syntax 챕터와 이 챕터에서 이미 본 직관적인 내용들에 대한 더 공식적인 설명이었고, 다음에는 더 고급 역인용을 다룰 것입니다.

For convenience we can also use anti-quotations in a way similar to
format strings: `` `($(mkIdent `c)) `` is the same as: `` let x := mkIdent `c; `($x) ``.

편의를 위해 역인용을 형식 문자열처럼 사용할 수도 있습니다: `` `($(mkIdent `c)) ``는 `` let x := mkIdent `c; `($x) ``와 동일합니다.

Furthermore there are sometimes situations in which we are not working
with basic `Syntax` but `Syntax` wrapped in more complex datastructures,
most notably `Array (TSyntax c)` or `TSepArray c s`. Where `TSepArray c s`, is a
`Syntax` specific type, it is what we get if we pattern match on some
`Syntax` that uses a separator `s` to separate things from the category `c`.
For example if we match using: `$xs,*`, `xs` will have type `TSepArray c ","`,.
With the special case of matching on no specific separator (i.e. whitespace):
`$xs*` in which we will receive an `Array (TSyntax c)`.

또한 기본 `Syntax`가 아닌 더 복잡한 데이터 구조로 감싸진 `Syntax`, 특히 `Array (TSyntax c)` 또는 `TSepArray c s`를 다루는 경우가 있습니다. `TSepArray c s`는 `Syntax` 전용 타입으로, 카테고리 `c`의 것들을 구분자 `s`로 구분하는 `Syntax`를 패턴 매칭할 때 얻는 값입니다. 예를 들어 `$xs,*`으로 매칭하면 `xs`는 `TSepArray c ","` 타입을 가집니다. 특정 구분자 없이 매칭하는 특수한 경우(즉, 공백): `$xs*`에서는 `Array (TSyntax c)`를 받게 됩니다.

If we are dealing with `xs : Array (TSyntax c)` and want to insert it into
a quotation we have two main ways to achieve this:

`xs : Array (TSyntax c)`를 다루면서 이를 인용에 삽입하려면 두 가지 주요 방법이 있습니다:

1. Insert it using a separator, most commonly `,`: `` `($xs,*) ``.
   This is also the way to insert a `TSepArray c ",""`
2. Insert it point blank without a separator (TODO): `` `() ``

1. 구분자를 사용하여 삽입, 가장 일반적으로 `,`: `` `($xs,*) ``. 이는 `TSepArray c ",""`를 삽입하는 방법이기도 합니다.
2. 구분자 없이 그대로 삽입(TODO): `` `() ``

For example:

```
-- syntactically cut away the first element of a tuple if possible
syntax "cut_tuple " "(" term ", " term,+ ")" : term

macro_rules
  -- cutting away one element of a pair isn't possible, it would not result in a tuple
  | `(cut_tuple ($x, $y)) => `(($x, $y))
  | `(cut_tuple ($x, $y, $xs,*)) => `(($y, $xs,*))

#check cut_tuple (1, 2) -- (1, 2) : Nat × Nat
#check cut_tuple (1, 2, 3) -- (2, 3) : Nat × Nat
```

The last thing for this section will be so called "anti-quotation splices".
There are two kinds of anti quotation splices, first the so called optional
ones. For example we might declare a syntax with an optional argument,
say our own `let` (in real projects this would most likely be a `let`
in some functional language we are writing a theory about):

```
syntax "mylet " ident (" : " term)? " := " term " in " term : term
```

There is this optional `(" : " term)?` argument involved which can let
the user define the type of the term to the left of it. With the methods
we know so far we'd have to write two `macro_rules` now, one for the case
with, one for the case without the optional argument. However the rest
of the syntactic translation works exactly the same with and without
the optional argument so what we can do using a splice here is to essentially
define both cases at once:

이 섹션의 마지막 내용은 소위 "역인용 스플라이스(anti-quotation splices)"입니다. 역인용 스플라이스에는 두 가지 종류가 있는데, 첫 번째는 소위 선택적(optional) 스플라이스입니다. 예를 들어 선택적 인수가 있는 syntax를 선언할 수 있습니다. 우리만의 `let`을 예로 들겠습니다(실제 프로젝트에서는 이론을 작성하는 어떤 함수형 언어의 `let`이 될 가능성이 높습니다):

사용자가 왼쪽 항의 타입을 정의할 수 있게 하는 선택적 `(" : " term)?` 인수가 포함되어 있습니다. 지금까지 아는 방법으로는 두 개의 `macro_rules`를 작성해야 합니다: 선택적 인수가 있는 경우와 없는 경우 각각. 그러나 나머지 구문 변환은 선택적 인수의 유무와 관계없이 완전히 동일하게 작동하므로, 여기서 스플라이스를 사용하면 두 경우를 한 번에 정의할 수 있습니다:

```
macro_rules
  | `(mylet $x $[: $ty]? := $val in $body) => `(let $x $[: $ty]? := $val; $body)
```

The `$[...]?` part is the splice here, it basically says "if this part of
the syntax isn't there, just ignore the parts on the right hand side that
involve anti quotation variables involved here". So now we can run
this syntax both with and without type ascription:

`$[...]?` 부분이 여기서 스플라이스입니다. 이는 기본적으로 "이 부분의 syntax가 없으면, 오른쪽에서 여기에 관련된 역인용 변수를 포함하는 부분을 무시하라"는 의미입니다. 이제 이 syntax를 타입 명시(type ascription) 유무에 관계없이 실행할 수 있습니다:

```
#eval mylet x := 5 in x - 10 -- 0, due to subtraction behaviour of `Nat`
#eval mylet x : Int := 5 in x - 10 -- -5, after all it is an `Int` now
```

The second and last splice might remind readers of list comprehension
as seen for example in Python. We will demonstrate it using an implementation
of `map` as a macro:

두 번째이자 마지막 스플라이스는 독자들에게 Python에서 볼 수 있는 리스트 컴프리헨션을 떠올리게 할 것입니다. 매크로로 `map`을 구현하는 것으로 이를 시연하겠습니다:

```
-- run the function given at the end for each element of the list
syntax "foreach " "[" term,* "]" term : term

macro_rules
  | `(foreach [ $[$x:term],* ] $func:term) => `(let f := $func; [ $[f $x],* ])

#eval foreach [1,2,3,4] (Nat.add 2) -- [3, 4, 5, 6]
```

In this case the `$[...],*` part is the splice. On the match side it tries
to match the pattern we define inside of it repetitively (given the separator
we tell it to). However unlike regular separator matching it does not
give us an `Array` or `SepArray`, instead it allows us to write another
splice on the right hand side that gets evaluated for each time the
pattern we specified matched, with the specific values from the match
per iteration.

이 경우 `$[...],*` 부분이 스플라이스입니다. 매칭 측에서는 지정한 구분자를 기준으로 내부에 정의한 패턴을 반복적으로 매칭하려고 시도합니다. 그러나 일반적인 구분자 매칭과 달리 `Array`나 `SepArray`를 제공하지 않고, 대신 오른쪽에 또 다른 스플라이스를 작성할 수 있게 하여 지정한 패턴이 매칭될 때마다, 각 반복에서 매칭된 특정 값들로 평가됩니다.

If you are familiar with macro systems in other languages like C you
probably know about so called macro hygiene issues already.
A hygiene issue is when a macro introduces an identifier that collides with an
identifier from some syntax that it is including. For example:

C와 같은 다른 언어의 매크로 시스템에 익숙하다면 소위 매크로 위생(hygiene) 문제에 대해 이미 알고 있을 것입니다. 위생 문제는 매크로가 포함하는 어떤 syntax의 식별자와 충돌하는 식별자를 도입할 때 발생합니다. 예를 들어:

```
-- Applying this macro produces a function that binds a new identifier `x`.
macro "const" e:term : term => `(fun x => $e)

-- But `x` can also be defined by a user
def x : Nat := 42

-- Which `x` should be used by the compiler in place of `$e`?
#eval (const x) 10 -- 42
```

Given the fact that macros perform only syntactic translations one might
expect the above `eval` to return 10 instead of 42: after all, the resulting
syntax should be `(fun x => x) 10`. While this was of course not the intention
of the author, this is what would happen in more primitive macro systems like
the one of C. So how does Lean avoid these hygiene issues? You can read
about this in detail in the excellent [Beyond Notations](https://lmcs.episciences.org/9362/pdf)
paper which discusses the idea and implementation in Lean in detail.
We will merely give an overview of the topic, since the details are not
that interesting for practical uses. The idea described in Beyond Notations
comes down to a concept called "macro scopes". Whenever a new macro
is invoked, a new macro scope (basically a unique number) is added to
a list of all the macro scopes that are active right now. When the current
macro introduces a new identifier what is actually getting added is an
identifier of the form:

매크로가 구문 변환만 수행한다는 사실을 감안하면, 위의 `eval`이 42 대신 10을 반환할 것이라고 예상할 수 있습니다: 결국 결과 syntax는 `(fun x => x) 10`이어야 합니다. 물론 이것은 작성자의 의도가 아니었지만, C와 같은 더 원시적인 매크로 시스템에서는 이런 일이 발생합니다. 그렇다면 Lean은 이러한 위생 문제를 어떻게 피할까요? 이에 대한 자세한 내용은 아이디어와 Lean에서의 구현을 상세히 논의하는 훌륭한 [Beyond Notations](https://lmcs.episciences.org/9362/pdf) 논문에서 읽을 수 있습니다. 세부 사항은 실용적인 사용에서 그다지 흥미롭지 않으므로 주제에 대한 개요만 제공하겠습니다. Beyond Notations에서 설명된 아이디어는 "매크로 스코프(macro scopes)"라는 개념으로 귀결됩니다. 새 매크로가 호출될 때마다, 새 매크로 스코프(기본적으로 고유한 숫자)가 현재 활성화된 모든 매크로 스코프 목록에 추가됩니다. 현재 매크로가 새 식별자를 도입할 때 실제로 추가되는 것은 다음 형식의 식별자입니다:

```
<actual name>._@.(<module_name>.<scopes>)*.<module_name>._hyg.<scopes>
```

For example, if the module name is `Init.Data.List.Basic`, the name is
`foo.bla`, and macros scopes are [2, 5] we get:

예를 들어, 모듈 이름이 `Init.Data.List.Basic`이고, 이름이 `foo.bla`이며, 매크로 스코프가 [2, 5]라면 다음을 얻습니다:

```
foo.bla._@.Init.Data.List.Basic._hyg.2.5
```

Since macro scopes are unique numbers the list of macro scopes appended in the end
of the name will always be unique across all macro invocations, hence macro hygiene
issues like the ones above are not possible.

If you are wondering why there is more than just the macro scopes to this
name generation, that is because we may have to combine scopes from different files/modules.
The main module being processed is always the right most one.
This situation may happen when we execute a macro generated in a file
imported in the current file.

매크로 스코프는 고유한 숫자이므로, 이름 끝에 추가된 매크로 스코프 목록은 모든 매크로 호출에 걸쳐 항상 고유하며, 따라서 위와 같은 매크로 위생 문제는 발생하지 않습니다.

이 이름 생성에 매크로 스코프 이상의 것이 있는 이유가 궁금하다면, 그것은 다른 파일/모듈의 스코프를 결합해야 할 수 있기 때문입니다. 처리되는 메인 모듈은 항상 가장 오른쪽에 있습니다. 이 상황은 현재 파일에서 가져온(import된) 파일에서 생성된 매크로를 실행할 때 발생할 수 있습니다.

```
foo.bla._@.Init.Data.List.Basic.2.1.Init.Lean.Expr_hyg.4
```

The delimiter `_hyg` at the end is used just to improve performance of
the function `Lean.Name.hasMacroScopes` -- the format could also work without it.

This was a lot of technical details. You do not have to understand them
in order to use macros, if you want you can just keep in mind that Lean
will not allow name clashes like the one in the `const` example.

Note that this extends to *all* names that are introduced using syntax
quotations, that is if you write a macro that produces:
`` `(def foo := 1) ``, the user will not be able to access `foo`
because the name will subject to hygiene. Luckily there is a way to
circumvent this. You can use `mkIdent` to generate a raw identifier,
for example: `` `(def $(mkIdent `foo) := 1) ``. In this case it won't
be subject to hygiene and accessible to the user.

끝의 `_hyg` 구분자는 `Lean.Name.hasMacroScopes` 함수의 성능을 개선하기 위해 사용됩니다. 이 형식은 이것 없이도 작동할 수 있습니다.

이것은 많은 기술적 세부 사항이었습니다. 매크로를 사용하기 위해 이것들을 이해할 필요는 없습니다. 원한다면 Lean이 `const` 예제에서와 같은 이름 충돌을 허용하지 않는다는 것만 기억하면 됩니다.

이것은 syntax 인용을 사용하여 도입된 *모든* 이름에 적용됩니다. 즉, `` `(def foo := 1) ``을 생성하는 매크로를 작성하면, 이름이 위생(hygiene)의 적용을 받기 때문에 사용자가 `foo`에 접근할 수 없게 됩니다. 다행히 이를 우회하는 방법이 있습니다. `mkIdent`를 사용하여 원시 식별자를 생성할 수 있습니다. 예를 들어: `` `(def $(mkIdent `foo) := 1) ``. 이 경우에는 위생의 적용을 받지 않으며 사용자가 접근할 수 있습니다.

Based on this description of the hygiene mechanism one interesting
question pops up, how do we know what the current list of macro scopes
actually is? After all in the macro functions that were defined above
there is never any explicit passing around of the scopes happening.
As is quite common in functional programming, as soon as we start
having some additional state that we need to bookkeep (like the macro scopes)
this is done with a monad, this is the case here as well with a slight twist.

Instead of implementing this for only a single monad `MacroM` the general
concept of keeping track of macro scopes in monadic way is abstracted
away using a type class called `MonadQuotation`. This allows any other
monad to also easily provide this hygienic `Syntax` creation mechanism
by simply implementing this type class.

This is also the reason that while we are able to use pattern matching on syntax
with `` `(syntax) `` we cannot just create `Syntax` with the same
syntax in pure functions: there is no `Monad` implementing `MonadQuotation`
involved in order to keep track of the macro scopes.

Now let's take a brief look at the `MonadQuotation` type class:

위생 메커니즘에 대한 이 설명을 바탕으로 흥미로운 질문이 생깁니다: 현재 매크로 스코프 목록이 실제로 무엇인지 어떻게 알 수 있을까요? 결국 위에서 정의된 매크로 함수들에서는 스코프를 명시적으로 전달하는 일이 전혀 없습니다. 함수형 프로그래밍에서 흔히 볼 수 있듯이, 기록해야 할 추가 상태(매크로 스코프 같은)가 생기기 시작하면 모나드로 처리합니다. 여기서도 약간의 변형과 함께 마찬가지입니다.

단일 모나드 `MacroM`에만 구현하는 대신, 모나드 방식으로 매크로 스코프를 추적하는 일반적인 개념은 `MonadQuotation`이라는 타입 클래스를 사용하여 추상화됩니다. 이를 통해 다른 모나드도 이 타입 클래스를 구현하기만 하면 위생적인 `Syntax` 생성 메커니즘을 쉽게 제공할 수 있습니다.

이것은 또한 `` `(syntax) ``로 syntax에 패턴 매칭은 할 수 있지만, 순수 함수에서는 동일한 syntax로 `Syntax`를 생성할 수 없는 이유이기도 합니다: 매크로 스코프를 추적하기 위한 `MonadQuotation`을 구현하는 `Monad`가 없기 때문입니다.

이제 `MonadQuotation` 타입 클래스를 간략히 살펴보겠습니다:

```
namespace Playground

class MonadRef (m : Type → Type) where
  getRef      : m Syntax
  withRef {α} : Syntax → m α → m α

class MonadQuotation (m : Type → Type) extends MonadRef m where
  getCurrMacroScope : m MacroScope
  getMainModule     : m Name
  withFreshMacroScope {α : Type} : m α → m α

end Playground
```

Since `MonadQuotation` is based on `MonadRef`, let's take a look at `MonadRef`
first. The idea here is quite simple: `MonadRef` is meant to be seen as an extension
to the `Monad` typeclass which

* gives us a reference to a `Syntax` value with `getRef`
* can evaluate a certain monadic action `m α` with a new reference to a `Syntax`
  using `withRef`

On it's own `MonadRef` isn't exactly interesting, but once it is combined with
`MonadQuotation` it makes sense.

As you can see `MonadQuotation` extends `MonadRef` and adds 3 new functions:

* `getCurrMacroScope` which obtains the latest `MacroScope` that was created
* `getMainModule` which (obviously) obtains the name of the main module,
  both of these are used to create these hygienic identifiers explained above
* `withFreshMacroScope` which will compute the next macro scope and run
  some computation `m α` that performs syntax quotation with this new
  macro scope in order to avoid name clashes. While this is mostly meant
  to be used internally whenever a new macro invocation happens, it can sometimes
  make sense to use this in our own macros, for example when we are generating
  some syntax block repeatedly and want to avoid name clashes.

How `MonadRef` comes into play here is that Lean requires a way to indicate
errors at certain positions to the user. One thing that wasn't introduced
in the `Syntax` chapter is that values of type `Syntax` actually carry their
position in the file around as well. When an error is detected, it is usually
bound to a `Syntax` value which tells Lean where to indicate the error in the file.
What Lean will do when using `withFreshMacroScope` is to apply the position of
the result of `getRef` to each introduced symbol, which then results in better
error positions than not applying any position.

To see error positioning in action, we can write a little macro that makes use of it:

`MonadQuotation`은 `MonadRef`를 기반으로 하므로, 먼저 `MonadRef`를 살펴보겠습니다. 아이디어는 꽤 단순합니다: `MonadRef`는 `Monad` 타입 클래스의 확장으로 볼 수 있으며

* `getRef`로 `Syntax` 값에 대한 참조를 제공합니다
* `withRef`를 사용하여 새 `Syntax` 참조로 특정 모나드 액션 `m α`를 평가할 수 있습니다

`MonadRef` 자체만으로는 특별히 흥미롭지 않지만, `MonadQuotation`과 결합되면 의미가 생깁니다.

보시다시피 `MonadQuotation`은 `MonadRef`를 확장하고 3개의 새로운 함수를 추가합니다:

* `getCurrMacroScope`: 생성된 최신 `MacroScope`를 얻습니다
* `getMainModule`: (당연히) 메인 모듈의 이름을 얻습니다. 이 두 가지 모두 위에서 설명한 위생적인 식별자를 생성하는 데 사용됩니다
* `withFreshMacroScope`: 다음 매크로 스코프를 계산하고, 이름 충돌을 피하기 위해 이 새로운 매크로 스코프로 syntax 인용을 수행하는 계산 `m α`를 실행합니다. 이는 주로 새 매크로 호출이 발생할 때 내부적으로 사용되도록 의도되었지만, 예를 들어 syntax 블록을 반복적으로 생성하면서 이름 충돌을 피하고 싶을 때처럼 자체 매크로에서 사용하는 것이 합리적인 경우도 있습니다.

`MonadRef`가 여기에 관여하는 이유는 Lean이 사용자에게 특정 위치에서 오류를 나타내는 방법이 필요하기 때문입니다. `Syntax` 챕터에서 소개하지 않은 한 가지는 `Syntax` 타입의 값들이 실제로 파일에서의 위치 정보도 함께 가지고 있다는 것입니다. 오류가 감지되면 보통 파일에서 어디에 오류를 나타낼지 Lean에게 알려주는 `Syntax` 값에 바인딩됩니다. `withFreshMacroScope`를 사용할 때 Lean이 하는 일은 `getRef` 결과의 위치를 각 도입된 기호에 적용하는 것입니다. 이렇게 하면 위치를 전혀 적용하지 않는 것보다 더 나은 오류 위치가 됩니다.

오류 위치 지정이 실제로 작동하는 것을 보려면, 이를 활용하는 작은 매크로를 작성할 수 있습니다:

```
syntax "error_position" ident : term

macro_rules
  | `(error_position all) => Macro.throwError "Ahhh"
  -- the `%$tk` syntax gives us the Syntax of the thing before the %,
  -- in this case `error_position`, giving it the name `tk`
  | `(error_position%$tk first) => withRef tk (Macro.throwError "Ahhh")

#check_failure error_position all -- the error is indicated at `error_position all`
#check_failure error_position first -- the error is only indicated at `error_position`
```

Obviously controlling the positions of errors in this way is quite important
for a good user experience.

분명히 이런 방식으로 오류 위치를 제어하는 것은 좋은 사용자 경험을 위해 매우 중요합니다.

As a final mini project for this section we will re-build the arithmetic
DSL from the syntax chapter in a slightly more advanced way, using a macro
this time so we can actually fully integrate it into the Lean syntax.

이 섹션의 마지막 미니 프로젝트로, syntax 챕터의 산술 DSL을 매크로를 사용하여 Lean syntax에 완전히 통합할 수 있도록 약간 더 발전된 방식으로 다시 구축하겠습니다.

```
declare_syntax_cat arith

syntax num : arith
syntax arith "-" arith : arith
syntax arith "+" arith : arith
syntax "(" arith ")" : arith
syntax "[Arith|" arith "]" : term

macro_rules
  | `([Arith| $x:num]) => `($x)
  | `([Arith| $x:arith + $y:arith]) => `([Arith| $x] + [Arith| $y]) -- recursive macros are possible
  | `([Arith| $x:arith - $y:arith]) => `([Arith| $x] - [Arith| $y])
  | `([Arith| ($x:arith)]) => `([Arith| $x])

#eval [Arith| (12 + 3) - 4] -- 11
```

Again feel free to play around with it. If you want to build more complex
things, like expressions with variables, maybe consider building an inductive type
using macros instead. Once you got your arithmetic expression term
as an inductive, you could then write a function that takes some form of
variable assignment and evaluates the given expression for this
assignment. You could also try to embed arbitrary `term`s into your
arith language using some special syntax or whatever else comes to your mind.

다시 한번 자유롭게 실험해 보세요. 변수가 있는 식처럼 더 복잡한 것을 만들고 싶다면 대신 매크로를 사용하여 귀납 타입을 구축하는 것을 고려해 보세요. 귀납 타입으로 산술 식 항을 만들면, 어떤 형식의 변수 할당을 받아 해당 할당에 대해 주어진 식을 평가하는 함수를 작성할 수 있습니다. 또한 특별한 syntax를 사용하여 임의의 `term`을 arith 언어에 임베딩하거나 그 외에 떠오르는 것들을 시도해 볼 수도 있습니다.

As promised in the syntax chapter here is Binders 2.0. We'll start by
reintroducing our theory of sets:

syntax 챕터에서 약속한 대로 Binders 2.0을 소개합니다. 집합 이론을 다시 소개하는 것부터 시작하겠습니다:

```
def Set (α : Type u) := α → Prop
def Set.mem (X : Set α) (x : α) : Prop := X x

-- Integrate into the already existing typeclass for membership notation
instance : Membership α (Set α) where
  mem := Set.mem

def Set.empty : Set α := λ _ => False

-- the basic "all elements such that" function for the notation
def setOf {α : Type} (p : α → Prop) : Set α := p
```

The goal for this section will be to allow for both `{x : X | p x}`
and `{x ∈ X, p x}` notations. In principle there are two ways to do this:

1. Define a syntax and macro for each way to bind a variable we might think of
2. Define a syntax category of binders that we could reuse across other
   binder constructs such as `Σ` or `Π` as well and implement macros for
   the `{ | }` case

In this section we will use approach 2 because it is more easily reusable.

이 섹션의 목표는 `{x : X | p x}`와 `{x ∈ X, p x}` 표기법 모두를 허용하는 것입니다. 원칙적으로 이를 수행하는 두 가지 방법이 있습니다:

1. 생각할 수 있는 변수를 바인딩하는 각 방법에 대해 syntax와 매크로를 정의하기
2. `Σ`나 `Π`와 같은 다른 바인더 구성에서도 재사용할 수 있는 바인더의 syntax 카테고리를 정의하고 `{ | }` 경우에 대한 매크로를 구현하기

이 섹션에서는 더 쉽게 재사용 가능하기 때문에 접근 방법 2를 사용하겠습니다.

```
declare_syntax_cat binder_construct
syntax "{" binder_construct "|" term "}" : term
```

Now let's define the two binders constructs we are interested in:

이제 관심 있는 두 가지 바인더 구성을 정의해 봅시다:

```
syntax ident " : " term : binder_construct
syntax ident " ∈ " term : binder_construct
```

And finally the macros to expand our syntax:

그리고 마지막으로 syntax를 확장하는 매크로를 만들겠습니다:

```
macro_rules
  | `({ $var:ident : $ty:term | $body:term }) => `(setOf (fun ($var : $ty) => $body))
  | `({ $var:ident ∈ $s:term | $body:term }) => `(setOf (fun $var => $var ∈ $s ∧ $body))

-- Old examples with better syntax:
#check { x : Nat | x ≤ 1 } -- setOf fun x => x ≤ 1 : Set Nat

example : 1 ∈ { y : Nat | y ≤ 1 } := by simp[Membership.mem, Set.mem, setOf]
example : 2 ∈ { y : Nat | y ≤ 3 ∧ 1 ≤ y } := by simp[Membership.mem, Set.mem, setOf]

-- New examples:
def oneSet : Set Nat := λ x => x = 1
#check { x ∈ oneSet | 10 ≤ x } -- setOf fun x => x ∈ oneSet ∧ 10 ≤ x : Set Nat

example : ∀ x, ¬(x ∈ { y ∈ oneSet | y ≠ 1 }) := by
  intro x h
  -- h : x ∈ setOf fun y => y ∈ oneSet ∧ y ≠ 1
  -- ⊢ False
  cases h
  -- : x ∈ oneSet
  -- : x ≠ 1
  contradiction
```

If you want to know more about macros you can read:

* the API docs: TODO link
* the source code: the lower parts of [Init.Prelude](https://github.com/leanprover/lean4/blob/master/src/Init/Prelude.lean)
  as you can see they are declared quite early in Lean because of their importance
  to building up syntax
* the aforementioned [Beyond Notations](https://lmcs.episciences.org/9362/pdf) paper

매크로에 대해 더 알고 싶다면 다음을 읽어보세요:

* API 문서: TODO 링크
* 소스 코드: [Init.Prelude](https://github.com/leanprover/lean4/blob/master/src/Init/Prelude.lean)의 하단 부분. 보시다시피 syntax 구축에 중요하기 때문에 Lean에서 꽤 초기에 선언됩니다
* 앞서 언급한 [Beyond Notations](https://lmcs.episciences.org/9362/pdf) 논문
