---
title: "소개"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "metaprogramming"]
categories: ["programming"]
description: "Lean 4 메타프로그래밍 소개: 메타 수준과 객체 수준, reflection, 커스텀 syntax와 tactic 작성 맛보기"
---

This book aims to build up enough knowledge about metaprogramming in Lean 4 so
you can be comfortable enough to:

* Start building your own meta helpers (defining new Lean notation such as `∑`,
  building new Lean commands such as `#check`, writing tactics such as `use`, etc.)
* Read and discuss metaprogramming APIs like the ones in Lean 4 core and
  Mathlib4

We by no means intend to provide an exhaustive exploration/explanation of the
entire Lean 4 metaprogramming API. We also don't cover the topic of monadic
programming in Lean 4. However, we hope that the examples provided will be
simple enough for the reader to follow and comprehend without a super deep
understanding of monadic programming. The book
[Functional Programming in Lean](https://leanprover.github.io/functional_programming_in_lean/)
is a highly recommended source on that subject.

이 책은 Lean 4의 메타프로그래밍에 대한 충분한 지식을 쌓아, 다음과 같은 작업을 편안하게 수행할 수 있도록 하는 것을 목표로 합니다:

* 자신만의 meta helper 만들기 (`∑`과 같은 새로운 Lean notation 정의, `#check`와 같은 새로운 Lean 커맨드 만들기, `use`와 같은 tactic 작성 등)
* Lean 4 core 및 Mathlib4의 메타프로그래밍 API 읽고 이해하기

이 책이 Lean 4 메타프로그래밍 API 전체를 빠짐없이 다루려는 것은 아닙니다. Lean 4의 모나딕 프로그래밍 주제도 다루지 않습니다. 하지만 제공되는 예제들이 모나딕 프로그래밍에 대한 깊은 이해 없이도 독자가 따라가고 이해할 수 있을 만큼 충분히 간단하기를 바랍니다. [Functional Programming in Lean](https://leanprover.github.io/functional_programming_in_lean/)은 해당 주제에 대해 강력히 추천하는 자료입니다.


The book is organized in a way to build up enough context for the chapters that
cover DSLs and tactics. Backtracking the pre-requisites for each chapter, the
dependency structure is as follows:

* "Tactics" builds on top of "Macros" and "Elaboration"
* "DSLs" builds on top of "Elaboration"
* "Macros" builds on top of "`Syntax`"
* "Elaboration" builds on top of "`Syntax`" and "`MetaM`"
* "`MetaM`" builds on top of "Expressions"

After the chapter on tactics, you find a cheat sheet containing a wrap-up of key
concepts and functions. And after that, there are some chapters with extra
content, showing other applications of metaprogramming in Lean 4. Most chapters contain exercises at the end of the chapter - and at the end of the book you will have full solutions to those exercises.

The rest of this chapter is a gentle introduction to what metaprogramming is,
offering some small examples to serve as appetizers for what the book shall
cover.

Note: the code snippets aren't self-contained. They are supposed to be run/read
incrementally, starting from the beginning of each chapter.

이 책은 DSL과 tactic을 다루는 챕터들에 필요한 충분한 맥락을 쌓아가는 방식으로 구성되어 있습니다. 각 챕터의 전제 조건을 역추적하면 의존 구조는 다음과 같습니다:

* "Tactics"는 "Macros"와 "Elaboration" 위에 구축됩니다
* "DSLs"는 "Elaboration" 위에 구축됩니다
* "Macros"는 "`Syntax`" 위에 구축됩니다
* "Elaboration"은 "`Syntax`"와 "`MetaM`" 위에 구축됩니다
* "`MetaM`"은 "Expressions" 위에 구축됩니다

tactic 챕터가 끝나면 핵심 개념과 함수들을 정리한 cheat sheet가 있습니다. 그 이후에는 Lean 4 메타프로그래밍의 다른 응용을 보여주는 추가 챕터들이 있습니다. 대부분의 챕터에는 끝에 연습 문제가 있으며, 책의 말미에서 해당 연습 문제들의 완전한 풀이를 확인할 수 있습니다.

이 챕터의 나머지 부분은 메타프로그래밍이 무엇인지에 대한 부드러운 소개로, 책에서 다룰 내용의 맛보기가 될 작은 예제들을 제공합니다.

참고: 코드 스니펫은 독립적으로 실행되지 않습니다. 각 챕터의 처음부터 순서대로 실행/읽어야 합니다.

When we write code in most programming languages such as Python, C, Java or
Scala, we usually have to stick to a pre-defined syntax otherwise the compiler
or the interpreter won't be able to figure out what we're trying to say. In
Lean, that would be defining an inductive type, implementing a function, proving
a theorem, etc. The compiler, then, has to parse the code, build an AST (abstract
syntax tree) and elaborate its syntax nodes into terms that can be processed by
the language kernel. We say that such activities performed by the compiler are
done in the **meta-level**, which will be studied throughout the book. And we
also say that the common usage of the language syntax is done in the
**object-level**.

Python, C, Java, Scala 등 대부분의 프로그래밍 언어로 코드를 작성할 때, 우리는 미리 정의된 문법을 따라야 합니다. 그렇지 않으면 컴파일러나 인터프리터가 우리의 의도를 파악할 수 없습니다. Lean에서는 inductive type 정의, 함수 구현, 정리 증명 등이 그에 해당합니다. 컴파일러는 코드를 파싱하고, AST(abstract syntax tree)를 구성한 다음, 그 syntax node들을 언어 커널이 처리할 수 있는 term으로 elaborate합니다. 컴파일러가 수행하는 이러한 활동들을 **meta-level**에서 이루어진다고 하며, 이 책 전반에 걸쳐 이를 학습하게 됩니다. 그리고 언어 문법의 일반적인 사용은 **object-level**에서 이루어진다고 합니다.

In most systems, the meta-level activities are done in a different language to
the one that we use to write code. In Isabelle, the meta-level language is ML
and Scala. In Coq, it's OCaml. In Agda, it's Haskell. In Lean 4, the meta code is
mostly written in Lean itself, with a few components written in C++.

대부분의 시스템에서 meta-level 활동은 코드를 작성하는 언어와 다른 언어로 이루어집니다. Isabelle에서는 meta-level 언어가 ML과 Scala입니다. Coq에서는 OCaml이고, Agda에서는 Haskell입니다. Lean 4에서는 meta 코드가 대부분 Lean 자체로 작성되며, 일부 구성 요소만 C++로 작성됩니다.

One cool thing about Lean, though, is that it allows us to define custom syntax
nodes and implement meta-level routines to elaborate them in the
very same development environment that we use to perform object-level
activities. So for example, one can write notation to instantiate a
term of a certain type and use it right away, in the same file! This concept is
generally called
[**reflection**](https://en.wikipedia.org/wiki/Reflective_programming). We can
say that, in Lean, the meta-level is *reflected* to the object-level.

Lean의 멋진 점은, object-level 활동을 수행하는 것과 동일한 개발 환경에서 커스텀 syntax node를 정의하고 이를 elaborate하는 meta-level 루틴을 구현할 수 있다는 것입니다. 예를 들어, 특정 타입의 term을 인스턴스화하는 notation을 작성하고 같은 파일에서 바로 사용할 수 있습니다! 이 개념은 일반적으로 [**reflection**](https://en.wikipedia.org/wiki/Reflective_programming)이라고 불립니다. Lean에서는 meta-level이 object-level에 *반영(reflected)*된다고 할 수 있습니다.

If you have done some metaprogramming in languages such as Ruby, Python or Javascript,
it probably took the form of making use of predefined metaprogramming methods to define
something on the fly. For example, in Ruby you can use `Class.new` and `define_method`
to define a new class and its new method (with new code inside!) on the fly, as your program is executing.

We don't usually need to define new commands or tactics "on the fly" in Lean, but spiritually
similar feats are possible with Lean metaprogramming and are equally straightforward, e.g. you can define
a new Lean command using a simple one-liner `elab "#help" : command => do ...normal Lean code...`.

In Lean, however, we will frequently want to directly manipulate
Lean's CST (Concrete Syntax Tree, Lean's `Syntax` type) and
Lean's AST (Abstract Syntax Tree, Lean's `Expr` type) instead of using "normal Lean code",
especially when we're writing tactics. So Lean metaprogramming is more challenging to master -
a large chunk of this book is contributed to studying these types and how we can manipulate them.

Next, we introduce several examples of Lean metaprogramming, so that you start getting a taste for
what metaprogramming in Lean is, and what it will enable you to achieve. These examples are meant as
mere illustrations - do not worry if you don't understand the details for now.

Ruby, Python, Javascript와 같은 언어에서 메타프로그래밍을 해본 적 있다면, 아마도 미리 정의된 메타프로그래밍 메서드를 활용해 실행 중에 무언가를 동적으로 정의하는 형태였을 것입니다. 예를 들어 Ruby에서는 `Class.new`와 `define_method`를 사용하여 프로그램이 실행되는 동안 새로운 클래스와 그 메서드를(새로운 코드와 함께!) 동적으로 정의할 수 있습니다.

Lean에서는 새로운 커맨드나 tactic을 "동적으로" 정의할 필요가 거의 없지만, 비슷한 취지의 작업을 Lean 메타프로그래밍으로도 똑같이 간단하게 할 수 있습니다. 예를 들어 `elab "#help" : command => do ...일반 Lean 코드...`와 같은 한 줄짜리 코드로 새로운 Lean 커맨드를 정의할 수 있습니다.

그러나 Lean에서는, 특히 tactic을 작성할 때, "일반 Lean 코드" 대신 Lean의 CST(Concrete Syntax Tree, Lean의 `Syntax` 타입)와 Lean의 AST(Abstract Syntax Tree, Lean의 `Expr` 타입)를 직접 조작해야 하는 경우가 많습니다. 따라서 Lean 메타프로그래밍은 숙달하기가 더 어려우며, 이 책의 상당 부분이 이러한 타입들과 이를 조작하는 방법을 공부하는 데 할애되어 있습니다.

다음으로, Lean 메타프로그래밍이 무엇인지, 그리고 무엇을 가능하게 하는지 맛보기를 위한 몇 가지 예제를 소개합니다. 이 예제들은 단순한 예시로, 지금 당장 세부 사항을 이해하지 못해도 괜찮습니다.


Often one wants to introduce new notation, for example one more suitable for (a branch of) mathematics. For instance, in mathematics one would write the function adding `2` to a natural number as `x : Nat ↦ x + 2` or simply `x ↦ x + 2` if the domain can be inferred to be the natural numbers. The corresponding lean definitions `fun x : Nat => x + 2` and `fun x => x + 2` use `=>` which in mathematics means *implication*, so may be confusing to some.

We can introduce notation using a `macro` which transforms our syntax to Lean's syntax (or syntax we previously defined). Here we introduce the `↦` notation for functions.

새로운 notation을 도입하고 싶을 때가 있는데, 예를 들어 수학(의 특정 분야)에 더 적합한 notation이 그 예입니다. 수학에서는 자연수에 `2`를 더하는 함수를 `x : Nat ↦ x + 2`로 쓰거나, 정의역이 자연수임을 추론할 수 있을 때는 단순히 `x ↦ x + 2`로 씁니다. 이에 해당하는 Lean 정의인 `fun x : Nat => x + 2`와 `fun x => x + 2`는 수학에서 *함의(implication)*를 의미하는 `=>`를 사용하므로 혼란스러울 수 있습니다.

우리의 문법을 Lean의 문법(또는 이전에 정의한 문법)으로 변환하는 `macro`를 사용하여 notation을 도입할 수 있습니다. 여기서는 함수를 위한 `↦` notation을 도입합니다.

```
import Lean

macro x:ident ":" t:term " ↦ " y:term : term => do
  `(fun $x : $t => $y)

#eval (x : Nat ↦ x + 2) 2 -- 4

macro x:ident " ↦ " y:term : term => do
  `(fun $x  => $y)

#eval (x ↦  x + 2) 2 -- 4
```


Suppose we want to build a helper command `#assertType` which tells whether a
given term is of a certain type. The usage will be:

`#assertType <term> : <type>`

Let's see the code:

주어진 term이 특정 타입인지 알려주는 헬퍼 커맨드 `#assertType`을 만들고 싶다고 가정해 봅시다. 사용법은 다음과 같습니다:

`#assertType <term> : <type>`

코드를 살펴봅시다:

```
elab "#assertType " termStx:term " : " typeStx:term : command =>
  open Lean Lean.Elab Command Term in
  liftTermElabM
    try
      let tp ← elabType typeStx
      discard $ elabTermEnsuringType termStx tp
      synthesizeSyntheticMVarsNoPostponing
      logInfo "success"
    catch | _ => throwError "failure"

/-- info: success -/
#assertType 5 : Nat

-- don't display names of metavariables
set_option pp.mvars false in

/--
error: type mismatch
  []
has type
  List ?_ : Type _
but is expected to have type
  Nat : Type
-/
#assertType [] : Nat
```

We started by using `elab` to define a `command` syntax. When parsed
by the compiler, it will trigger the incoming computation.

At this point, the code should be running in the `CommandElabM` monad. We then
use `liftTermElabM` to access the `TermElabM` monad, which allows us to use
`elabType` and `elabTermEnsuringType` to build expressions out of the
syntax nodes `typeStx` and `termStx`.

First, we elaborate the expected type `tp : Expr`, then we use it to elaborate
the term expression. The term should have the type `tp` otherwise an error will be
thrown. We then discard the resulting term expression, since it doesn't matter to us here - we're calling
`elabTermEnsuringType` as a sanity check.

We also add `synthesizeSyntheticMVarsNoPostponing`, which forces Lean to
elaborate metavariables right away. Without that line, `#assertType [] : ?_`
would result in `success`.

If no error is thrown until now then the elaboration succeeded and we can use
`logInfo` to output "success". If, instead, some error is caught, then we use
`throwError` with the appropriate message.

우선 `elab`을 사용하여 `command` 문법을 정의하는 것으로 시작했습니다. 컴파일러에 의해 파싱되면 이후 연산이 트리거됩니다.

이 시점에서 코드는 `CommandElabM` 모나드에서 실행됩니다. 그런 다음 `liftTermElabM`을 사용하여 `TermElabM` 모나드에 접근하고, 이를 통해 `elabType`과 `elabTermEnsuringType`을 사용하여 syntax node인 `typeStx`와 `termStx`로부터 expression을 구성합니다.

먼저 예상 타입 `tp : Expr`를 elaborate하고, 이를 사용하여 term expression을 elaborate합니다. term은 타입 `tp`를 가져야 하며, 그렇지 않으면 오류가 발생합니다. 결과 term expression은 여기서 중요하지 않으므로 버립니다 - `elabTermEnsuringType`을 건전성 검사(sanity check)로 호출하는 것입니다.

또한 `synthesizeSyntheticMVarsNoPostponing`을 추가하여 Lean이 metavariable을 즉시 elaborate하도록 강제합니다. 이 줄이 없으면 `#assertType [] : ?_`는 `success`를 반환합니다.

이 시점까지 오류가 발생하지 않으면 elaboration이 성공한 것이며 `logInfo`를 사용하여 "success"를 출력할 수 있습니다. 반면 오류가 잡히면 적절한 메시지와 함께 `throwError`를 사용합니다.


Let's parse a classic grammar, the grammar of arithmetic expressions with
addition, multiplication, naturals, and variables. We'll define an AST
(Abstract Syntax Tree) to encode the data of our expressions, and use operators
`+` and `*` to denote building an arithmetic AST. Here's the AST that we will be
parsing:

덧셈, 곱셈, 자연수, 변수를 포함하는 산술 표현식의 고전적인 문법을 파싱해 봅시다. 우리의 expression 데이터를 인코딩하는 AST(Abstract Syntax Tree)를 정의하고, 산술 AST를 구성하는 것을 나타내기 위해 연산자 `+`와 `*`를 사용할 것입니다. 파싱할 AST는 다음과 같습니다:

```
inductive Arith : Type where
  | add : Arith → Arith → Arith -- e + f
  | mul : Arith → Arith → Arith -- e * f
  | nat : Nat → Arith           -- constant
  | var : String → Arith        -- variable
```

Now we declare a syntax category to describe the grammar that we will be
parsing. Notice that we control the precedence of `+` and `*` by giving a lower
precedence weight to the `+` syntax than to the `*` syntax indicating that
multiplication binds tighter than addition (the higher the number, the tighter
the binding). This allows us to declare *precedence* when defining new syntax.

이제 파싱할 문법을 설명하는 syntax category를 선언합니다. `+` 문법에 `*` 문법보다 낮은 우선순위 가중치를 부여하여 곱셈이 덧셈보다 강하게 결합함을 나타내는 방식으로 `+`와 `*`의 우선순위를 제어합니다 (숫자가 높을수록 더 강하게 결합). 이를 통해 새로운 문법을 정의할 때 *우선순위(precedence)*를 선언할 수 있습니다.

```
declare_syntax_cat arith
syntax num                        : arith -- nat for Arith.nat
syntax str                        : arith -- strings for Arith.var
syntax:50 arith:50 " + " arith:51 : arith -- Arith.add
syntax:60 arith:60 " * " arith:61 : arith -- Arith.mul
syntax " ( " arith " ) "          : arith -- bracketed expressions

-- Auxiliary notation for translating `arith` into `term`
syntax " ⟪ " arith " ⟫ " : term

-- Our macro rules perform the "obvious" translation:
macro_rules
  | `(⟪ $s:str ⟫)              => `(Arith.var $s)
  | `(⟪ $num:num ⟫)            => `(Arith.nat $num)
  | `(⟪ $x:arith + $y:arith ⟫) => `(Arith.add ⟪ $x ⟫ ⟪ $y ⟫)
  | `(⟪ $x:arith * $y:arith ⟫) => `(Arith.mul ⟪ $x ⟫ ⟪ $y ⟫)
  | `(⟪ ( $x ) ⟫)              => `( ⟪ $x ⟫ )

#check ⟪ "x" * "y" ⟫
-- Arith.mul (Arith.var "x") (Arith.var "y") : Arith

#check ⟪ "x" + "y" ⟫
-- Arith.add (Arith.var "x") (Arith.var "y") : Arith

#check ⟪ "x" + 20 ⟫
-- Arith.add (Arith.var "x") (Arith.nat 20) : Arith

#check ⟪ "x" + "y" * "z" ⟫ -- precedence
-- Arith.add (Arith.var "x") (Arith.mul (Arith.var "y") (Arith.var "z")) : Arith

#check ⟪ "x" * "y" + "z" ⟫ -- precedence
-- Arith.add (Arith.mul (Arith.var "x") (Arith.var "y")) (Arith.var "z") : Arith

#check ⟪ ("x" + "y") * "z" ⟫ -- brackets
-- Arith.mul (Arith.add (Arith.var "x") (Arith.var "y")) (Arith.var "z")
```


Let's create a tactic that adds a new hypothesis to the context with a given
name and postpones the need for its proof to the very end. It's similar to
the `suffices` tactic from Lean 3, except that we want to make sure that the new
goal goes to the bottom of the goal list.

It's going to be called `suppose` and is used like this:

`suppose <name> : <type>`

So let's see the code:

주어진 이름으로 새로운 가설을 컨텍스트에 추가하고 그 증명을 맨 끝으로 미루는 tactic을 만들어 봅시다. Lean 3의 `suffices` tactic과 비슷하지만, 새로운 goal이 goal 목록의 맨 아래로 가도록 보장하고 싶습니다.

이것은 `suppose`라고 불리며 다음과 같이 사용됩니다:

`suppose <name> : <type>`

코드를 살펴봅시다:

```
open Lean Meta Elab Tactic Term in
elab "suppose " n:ident " : " t:term : tactic => do
  let n : Name := n.getId
  let mvarId ← getMainGoal
  mvarId.withContext do
    let t ← elabType t
    let p ← mkFreshExprMVar t MetavarKind.syntheticOpaque n
    let (_, mvarIdNew) ← MVarId.intro1P $ ← mvarId.assert n t p
    replaceMainGoal [p.mvarId!, mvarIdNew]
  evalTactic $ ← `(tactic|rotate_left)

example : 0 + a = a := by
  suppose add_comm : 0 + a = a + 0
  rw [add_comm]; rfl     -- closes the initial main goal
  rw [Nat.zero_add]; rfl -- proves `add_comm`
```

We start by storing the main goal in `mvarId` and using it as a parameter of
`withMVarContext` to make sure that our elaborations will work with types that
depend on other variables in the context.

This time we're using `mkFreshExprMVar` to create a metavariable expression for
the proof of `t`, which we can introduce to the context using `intro1P` and
`assert`.

To require the proof of the new hypothesis as a goal, we call `replaceMainGoal`
passing a list with `p.mvarId!` in the head. And then we can use the
`rotate_left` tactic to move the recently added top goal to the bottom.

main goal을 `mvarId`에 저장하고 이를 `withMVarContext`의 파라미터로 사용하여 elaboration이 컨텍스트의 다른 변수에 의존하는 타입들과 함께 동작하도록 보장하는 것으로 시작합니다.

이번에는 `mkFreshExprMVar`를 사용하여 `t`의 증명에 대한 metavariable expression을 생성하고, `intro1P`와 `assert`를 사용하여 컨텍스트에 도입합니다.

새로운 가설의 증명을 goal로 요구하기 위해, `p.mvarId!`를 맨 앞에 포함한 리스트를 전달하여 `replaceMainGoal`을 호출합니다. 그런 다음 `rotate_left` tactic을 사용하여 방금 추가된 최상단 goal을 맨 아래로 이동시킬 수 있습니다.