---
title: "개요"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "metaprogramming"]
categories: ["programming"]
description: "Lean 4 컴파일 과정 개요: 파싱, 정교화, 평가 단계와 Syntax, Expr 타입의 역할"
---

In this chapter, we will provide an overview of the primary steps involved in the Lean compilation process, including parsing, elaboration, and evaluation. As alluded to in the introduction, metaprogramming in Lean involves plunging into the heart of this process. We will explore the fundamental objects involved, `Expr` and `Syntax`, learn what they signify, and discover how one can be turned into another (and back!).

In the next chapters, you will learn the particulars. As you read on, you might want to return to this chapter occasionally to remind yourself of how it all fits together.

이 장에서는 파싱, 정교화(elaboration), 평가(evaluation)를 포함하여 Lean 컴파일 과정에서 수행되는 주요 단계들에 대한 개요를 제공합니다. 서론에서 언급했듯이, Lean에서의 메타프로그래밍은 이 과정의 핵심으로 깊이 파고드는 것을 의미합니다. 우리는 `Expr`과 `Syntax`라는 핵심 객체들을 살펴보고, 이들이 무엇을 의미하는지 알아보며, 어떻게 하나를 다른 하나로 변환할 수 있는지(그리고 역으로도!) 탐구할 것입니다.

다음 장들에서는 세부 사항들을 배우게 됩니다. 읽어나가면서, 전체적인 그림을 상기하기 위해 때때로 이 장으로 돌아오고 싶을 수도 있습니다.


Metaprogramming in Lean is deeply connected to the compilation steps - parsing, syntactic analysis, transformation, and code generation.

Lean에서의 메타프로그래밍은 파싱, 구문 분석, 변환, 코드 생성이라는 컴파일 단계들과 깊이 연결되어 있습니다.

> Lean 4 is a reimplementation of the Lean theorem prover in Lean itself. The new compiler produces C code, and users can now implement efficient proof automation in Lean, compile it into efficient C code, and load it as a plugin. In Lean 4, users can access all internal data structures used to implement Lean by merely importing the Lean package.
>
> Leonardo de Moura, Sebastian Ullrich ([The Lean 4 Theorem Prover and Programming Language](https://pp.ipd.kit.edu/uploads/publikationen/demoura21lean4.pdf))

> Lean 4는 Lean 자체로 Lean 정리 증명기를 재구현한 것입니다. 새 컴파일러는 C 코드를 생성하며, 사용자들은 이제 Lean으로 효율적인 증명 자동화를 구현하고, 이를 효율적인 C 코드로 컴파일하여 플러그인으로 로드할 수 있습니다. Lean 4에서는 Lean 패키지를 임포트하는 것만으로도 Lean 구현에 사용된 모든 내부 데이터 구조에 접근할 수 있습니다.
>
> Leonardo de Moura, Sebastian Ullrich ([The Lean 4 Theorem Prover and Programming Language](https://pp.ipd.kit.edu/uploads/publikationen/demoura21lean4.pdf))

The Lean compilation process can be summed up in the following diagram:

Lean 컴파일 과정은 다음 다이어그램으로 요약할 수 있습니다:

![](https://github.com/arthurpaulino/lean4-metaprogramming-book/assets/7578559/78867009-2624-46a3-a1f4-f488fd25d494)

First, we will start with Lean code as a string. Then we'll see it become a `Syntax` object, and then an `Expr` object. Then finally we can execute it.

먼저 문자열 형태의 Lean 코드로 시작합니다. 그런 다음 `Syntax` 객체가 되고, 이후 `Expr` 객체가 됩니다. 최종적으로 이를 실행할 수 있게 됩니다.

So, the compiler sees a string of Lean code, say `"let a := 2"`, and the following process unfolds:

1. **apply a relevant syntax rule** (`"let a := 2"` ➤ `Syntax`)

   During the parsing step, Lean tries to match a string of Lean code to one of the declared **syntax rules** in order to turn that string into a `Syntax` object. **Syntax rules** are basically glorified regular expressions - when you write a Lean string that matches a certain **syntax rule**'s regex, that rule will be used to handle subsequent steps.
2. **apply all macros in a loop** (`Syntax` ➤ `Syntax`)

   During the elaboration step, each **macro** simply turns the existing `Syntax` object into some new `Syntax` object. Then, the new `Syntax` is processed similarly (repeating steps 1 and 2), until there are no more **macros** to apply.
3. **apply a single elab** (`Syntax` ➤ `Expr`)

   Finally, it's time to infuse your syntax with meaning - Lean finds an **elab** that's matched to the appropriate **syntax rule** by the `name` argument (**syntax rules**, **macros** and **elabs** all have this argument, and they must match). The newfound **elab** returns a particular `Expr` object.
   This completes the elaboration step.

예를 들어, 컴파일러가 `"let a := 2"`라는 Lean 코드 문자열을 보면 다음 과정이 진행됩니다:

1. **관련 syntax rule 적용** (`"let a := 2"` ➤ `Syntax`)

   파싱 단계에서 Lean은 Lean 코드 문자열을 선언된 **syntax rule**들 중 하나와 매칭하여 해당 문자열을 `Syntax` 객체로 변환하려 합니다. **Syntax rule**은 기본적으로 정규 표현식을 발전시킨 것으로, 특정 **syntax rule**의 정규식과 일치하는 Lean 문자열을 작성하면, 해당 규칙이 이후 단계들을 처리하는 데 사용됩니다.
2. **루프 안에서 모든 macro 적용** (`Syntax` ➤ `Syntax`)

   정교화 단계에서 각 **macro**는 단순히 기존 `Syntax` 객체를 새로운 `Syntax` 객체로 변환합니다. 그러면 새로운 `Syntax`가 유사하게 처리되며(1단계와 2단계를 반복), 더 이상 적용할 **macro**가 없을 때까지 계속됩니다.
3. **단일 elab 적용** (`Syntax` ➤ `Expr`)

   마침내 구문에 의미를 부여할 때입니다. Lean은 `name` 인수를 통해 적절한 **syntax rule**과 매칭된 **elab**을 찾습니다(**syntax rule**, **macro**, **elab** 모두 이 인수를 가지며, 서로 일치해야 합니다). 찾아낸 **elab**은 특정 `Expr` 객체를 반환합니다. 이로써 정교화 단계가 완료됩니다.

The expression (`Expr`) is then converted into executable code during the evaluation step - we don't have to specify that in any way, the Lean compiler will handle doing so for us.

표현식(`Expr`)은 평가 단계에서 실행 가능한 코드로 변환됩니다. 우리가 이를 별도로 지정할 필요는 없으며, Lean 컴파일러가 이를 처리해 줍니다.


Elaboration is an overloaded term in Lean. For example, you might encounter the following usage of the word "elaboration", wherein the intention is *"taking a partially-specified expression and inferring what is left implicit"*:

정교화(Elaboration)는 Lean에서 여러 의미로 사용되는 용어입니다. 예를 들어, *"부분적으로 명세된 표현식을 받아 암묵적으로 남겨진 부분을 추론하는 것"*을 의미하는 다음과 같은 용법을 접할 수 있습니다:

> When you enter an expression like `λ x y z, f (x + y) z` for Lean to process, you are leaving information implicit. For example, the types of `x`, `y`, and `z` have to be inferred from the context, the notation `+` may be overloaded, and there may be implicit arguments to `f` that need to be filled in as well.
>
> The process of *taking a partially-specified expression and inferring what is left implicit* is known as **elaboration**. Lean's **elaboration** algorithm is powerful, but at the same time, subtle and complex. Working in a system of dependent type theory requires knowing what sorts of information the **elaborator** can reliably infer, as well as knowing how to respond to error messages that are raised when the elaborator fails. To that end, it is helpful to have a general idea of how Lean's **elaborator** works.
>
> When Lean is parsing an expression, it first enters a preprocessing phase. First, Lean inserts "holes" for implicit arguments. If term t has type `Π {x : A}, P x`, then t is replaced by `@t _` everywhere. Then, the holes — either the ones inserted in the previous step or the ones explicitly written by the user — in a term are instantiated by metavariables `?M1`, `?M2`, `?M3`, .... Each overloaded notation is associated with a list of choices, that is, the possible interpretations. Similarly, Lean tries to detect the points where a coercion may need to be inserted in an application `s t`, to make the inferred type of t match the argument type of `s`. These become choice points too. If one possible outcome of the elaboration procedure is that no coercion is needed, then one of the choices on the list is the identity.
>
> ([Theorem Proving in Lean 2](http://leanprover.github.io/tutorial/08_Building_Theories_and_Proofs.html))

> `λ x y z, f (x + y) z`와 같은 표현식을 Lean이 처리하도록 입력할 때, 여러분은 일부 정보를 암묵적으로 남겨둡니다. 예를 들어, `x`, `y`, `z`의 타입은 문맥으로부터 추론되어야 하고, `+` 표기법은 오버로드될 수 있으며, `f`에는 채워져야 할 암묵적 인수가 있을 수 있습니다.
>
> *부분적으로 명세된 표현식을 받아 암묵적으로 남겨진 부분을 추론하는* 과정을 **정교화(elaboration)**라고 합니다. Lean의 **정교화** 알고리즘은 강력하지만, 동시에 미묘하고 복잡합니다. 종속 타입 이론 시스템에서 작업하려면 **elaborator**가 신뢰할 수 있게 추론할 수 있는 정보의 종류를 알고, elaborator가 실패할 때 발생하는 오류 메시지에 대응하는 방법을 알아야 합니다. 이를 위해 Lean의 **elaborator**가 어떻게 작동하는지 대략적인 아이디어를 갖는 것이 도움이 됩니다.
>
> Lean이 표현식을 파싱할 때, 먼저 전처리 단계로 진입합니다. 먼저 Lean은 암묵적 인수를 위한 "구멍"을 삽입합니다. 항 t가 타입 `Π {x : A}, P x`를 가지면, t는 모든 곳에서 `@t _`로 대체됩니다. 그런 다음, 이전 단계에서 삽입된 구멍이나 사용자가 명시적으로 작성한 구멍들은 메타변수 `?M1`, `?M2`, `?M3`, ...에 의해 인스턴스화됩니다. 각 오버로드된 표기법은 가능한 해석들의 목록, 즉 선택지와 연관됩니다. 마찬가지로, Lean은 추론된 t의 타입이 `s`의 인수 타입과 일치하도록 응용 `s t`에서 강제 변환(coercion)을 삽입해야 할 지점을 감지하려 합니다. 이것들도 선택 지점이 됩니다. 정교화 과정의 가능한 결과 중 하나가 강제 변환이 필요 없는 경우라면, 목록의 선택지 중 하나는 항등 함수(identity)입니다.
>
> ([Theorem Proving in Lean 2](http://leanprover.github.io/tutorial/08_Building_Theories_and_Proofs.html))

We, on the other hand, just defined elaboration as the process of turning `Syntax` objects into `Expr` objects.

반면, 우리는 정교화를 `Syntax` 객체를 `Expr` 객체로 변환하는 과정으로 정의했습니다.

These definitions are not mutually exclusive - elaboration is, indeed, the transformation of `Syntax` into `Expr`s - it's just so that for this transformation to happen we need a lot of trickery - we need to infer implicit arguments, instantiate metavariables, perform unification, resolve identifiers, etc. etc. - and these actions can be referred to as "elaboration" on their own; similarly to how "checking if you turned off the lights in your apartment" (metavariable instantiation) can be referred to as "going to school" (elaboration).

이 두 정의는 상호 배타적이지 않습니다. 정교화는 실제로 `Syntax`를 `Expr`로 변환하는 것입니다. 다만 이 변환이 일어나기 위해서는 많은 기법들이 필요합니다. 암묵적 인수를 추론하고, 메타변수를 인스턴스화하며, 유니피케이션(unification)을 수행하고, 식별자를 해석하는 등의 작업이 필요합니다. 이러한 각 행위들도 "정교화"라고 불릴 수 있습니다. 마치 "아파트의 불을 껐는지 확인하는 것"(메타변수 인스턴스화)이 "학교에 가는 것"(정교화)의 일부로 불릴 수 있는 것처럼 말입니다.

There also exists a process opposite to elaboration in Lean - it's called, appropriately enough, delaboration. During delaboration, an `Expr` is turned into a `Syntax` object; and then the formatter turns it into a `Format` object, which can be displayed in Lean's infoview. Every time you log something to the screen, or see some output upon hovering over `#check`, it's the work of the delaborator.

Lean에는 정교화와 반대되는 과정도 존재합니다. 적절하게도 이를 역정교화(delaboration)라고 부릅니다. 역정교화 중에 `Expr`은 `Syntax` 객체로 변환되고, 포매터(formatter)가 이를 Lean의 infoview에 표시할 수 있는 `Format` 객체로 변환합니다. 화면에 무언가를 로그하거나 `#check`에 커서를 올렸을 때 출력이 보이는 것은 모두 역정교화기(delaborator)의 작업입니다.

Throughout this book you will see references to the elaborator; and in the "Extra: Pretty Printing" chapter you can read about delaborators.

이 책 전반에 걸쳐 elaborator에 대한 참조를 볼 수 있으며, "Extra: Pretty Printing" 장에서 delaborator에 대해 읽을 수 있습니다.


Now, when you're reading Lean source code, you will see 11(+?) commands specifying the **parsing**/**elaboration**/**evaluation** process:

이제 Lean 소스 코드를 읽을 때, **파싱**/**정교화**/**평가** 과정을 명세하는 11개(이상의) 명령들을 보게 될 것입니다:

![](https://github.com/arthurpaulino/lean4-metaprogramming-book/assets/7578559/9b83f06c-49c4-4d93-9d42-72e0499ae6c8)

In the image above, you see `notation`, `prefix`, `infix`, and `postfix` - all of these are combinations of `syntax` and `@[macro xxx] def ourMacro`, just like `macro`. These commands differ from `macro` in that you can only define syntax of a particular form with them.

위 이미지에서 `notation`, `prefix`, `infix`, `postfix`를 볼 수 있는데, 이들은 모두 `macro`처럼 `syntax`와 `@[macro xxx] def ourMacro`의 조합입니다. 이 명령들은 특정 형태의 구문만 정의할 수 있다는 점에서 `macro`와 다릅니다.

All of these commands are used in Lean and Mathlib source code extensively, so it's well worth memorizing them. Most of them are syntax sugars, however, and you can understand their behaviour by studying the behaviour of the following 3 low-level commands: `syntax` (a **syntax rule**), `@[macro xxx] def ourMacro` (a **macro**), and `@[command_elab xxx] def ourElab` (an **elab**).

이 명령들은 모두 Lean과 Mathlib 소스 코드에서 광범위하게 사용되므로, 외워두는 것이 좋습니다. 하지만 대부분은 문법 설탕(syntax sugar)이며, 다음 3개의 저수준 명령의 동작을 이해함으로써 그 동작을 파악할 수 있습니다: `syntax`(**syntax rule**), `@[macro xxx] def ourMacro`(**macro**), `@[command_elab xxx] def ourElab`(**elab**).

To give a more concrete example, imagine we're implementing a `#help` command, that can also be written as `#h`. Then we can write our **syntax rule**, **macro**, and **elab** as follows:

더 구체적인 예를 들어보겠습니다. `#h`로도 작성할 수 있는 `#help` 명령을 구현한다고 가정해 봅시다. 그러면 **syntax rule**, **macro**, **elab**을 다음과 같이 작성할 수 있습니다:

![](https://github.com/lakesare/lean4-metaprogramming-book/assets/7578559/adc1284f-3c0a-441d-91b8-7d87b6035688)

This image is not supposed to be read row by row - it's perfectly fine to use `macro_rules` together with `elab`. Suppose, however, that we used the 3 low-level commands to specify our `#help` command (the first row). After we've done this, we can write `#help "#explode"` or `#h "#explode"`, both of which will output a rather parsimonious documentation for the `#explode` command - *"Displays proof in a Fitch table"*.

이 이미지는 행 단위로 읽어야 하는 것이 아닙니다. `macro_rules`를 `elab`과 함께 사용해도 완전히 괜찮습니다. 그러나 3개의 저수준 명령을 사용하여 `#help` 명령을 명세했다고 가정해봅시다(첫 번째 행). 이렇게 하면 `#help "#explode"` 또는 `#h "#explode"`를 작성할 수 있으며, 둘 다 `#explode` 명령에 대한 간결한 문서를 출력합니다. *"Displays proof in a Fitch table"*.

If we write `#h "#explode"`, Lean will travel the `syntax (name := shortcut_h)` ➤ `@[macro shortcut_h] def helpMacro` ➤ `syntax (name := default_h)` ➤ `@[command_elab default_h] def helpElab` route.  
If we write `#help "#explode"`, Lean will travel the `syntax (name := default_h)` ➤ `@[command_elab default_h] def helpElab` route.

`#h "#explode"`를 작성하면 Lean은 `syntax (name := shortcut_h)` ➤ `@[macro shortcut_h] def helpMacro` ➤ `syntax (name := default_h)` ➤ `@[command_elab default_h] def helpElab` 경로를 따릅니다.  
`#help "#explode"`를 작성하면 Lean은 `syntax (name := default_h)` ➤ `@[command_elab default_h] def helpElab` 경로를 따릅니다.

Note how the matching between **syntax rules**, **macros**, and **elabs** is done via the `name` argument. If we used `macro_rules` or other syntax sugars, Lean would figure out the appropriate `name` arguments on its own.

**syntax rule**, **macro**, **elab** 간의 매칭이 `name` 인수를 통해 이루어지는 방식에 주목하세요. `macro_rules`나 다른 문법 설탕을 사용했다면, Lean이 적절한 `name` 인수를 스스로 파악할 것입니다.

If we were defining something other than a command, instead of `: command` we could write `: term`, or `: tactic`, or any other syntax category.  
The elab function can also be of different types - the `CommandElab` we used to implement `#help` - but also `TermElab` and `Tactic`:

명령이 아닌 다른 것을 정의한다면, `: command` 대신 `: term`, `: tactic` 또는 다른 구문 카테고리를 작성할 수 있습니다.  
elab 함수도 다양한 타입을 가질 수 있습니다. `#help`를 구현하는 데 사용한 `CommandElab`뿐만 아니라 `TermElab`과 `Tactic`도 있습니다:

* `TermElab` stands for **Syntax → Option Expr → TermElabM Expr**, so the elab function is expected to return the **Expr** object.
* `CommandElab` stands for **Syntax → CommandElabM Unit**, so it shouldn't return anything.
* `Tactic` stands for **Syntax → TacticM Unit**, so it shouldn't return anything either.

* `TermElab`은 **Syntax → Option Expr → TermElabM Expr**를 의미하므로, elab 함수는 **Expr** 객체를 반환할 것으로 기대됩니다.
* `CommandElab`은 **Syntax → CommandElabM Unit**를 의미하므로, 아무것도 반환하지 않아야 합니다.
* `Tactic`은 **Syntax → TacticM Unit**를 의미하므로, 마찬가지로 아무것도 반환하지 않아야 합니다.

This corresponds to our intuitive understanding of terms, commands and tactics in Lean - terms return a particular value upon execution, commands modify the environment or print something out, and tactics modify the proof state.

이는 Lean에서 항(term), 명령(command), 전술(tactic)에 대한 우리의 직관적인 이해와 일치합니다. 항은 실행 시 특정 값을 반환하고, 명령은 환경을 수정하거나 무언가를 출력하며, 전술은 증명 상태를 수정합니다.


We have hinted at the flow of execution of these three essential commands here and there, however let's lay it out explicitly. The order of execution follows the following pseudocodey template: `syntax (macro; syntax)* elab`.

여기저기서 이 세 가지 핵심 명령의 실행 흐름을 암시했지만, 이를 명시적으로 정리해 보겠습니다. 실행 순서는 다음과 같은 의사코드 형식을 따릅니다: `syntax (macro; syntax)* elab`.

Consider the following example.

다음 예시를 살펴보겠습니다.

```
import Lean
open Lean Elab Command

syntax (name := xxx) "red" : command
syntax (name := yyy) "green" : command
syntax (name := zzz) "blue" : command

@[macro xxx] def redMacro : Macro := λ stx =>
  match stx with
  | _ => `(green)

@[macro yyy] def greenMacro : Macro := λ stx =>
  match stx with
  | _ => `(blue)

@[command_elab zzz] def blueElab : CommandElab := λ stx =>
  Lean.logInfo "finally, blue!"

red -- finally, blue!
```

The process is as follows:

* match appropriate `syntax` rule (happens to have `name := xxx`) ➤  
  apply `@[macro xxx]` ➤
* match appropriate `syntax` rule (happens to have `name := yyy`) ➤  
  apply `@[macro yyy]` ➤
* match appropriate `syntax` rule (happens to have `name := zzz`) ➤  
  can't find any macros with name `zzz` to apply,  
  so apply `@[command_elab zzz]`. 🎉.

과정은 다음과 같습니다:

* 적절한 `syntax` 규칙 매칭 (`name := xxx`를 가진 것으로 판명) ➤  
  `@[macro xxx]` 적용 ➤
* 적절한 `syntax` 규칙 매칭 (`name := yyy`를 가진 것으로 판명) ➤  
  `@[macro yyy]` 적용 ➤
* 적절한 `syntax` 규칙 매칭 (`name := zzz`를 가진 것으로 판명) ➤  
  이름이 `zzz`인 macro를 찾을 수 없으므로,  
  `@[command_elab zzz]` 적용. 🎉.

The behaviour of syntax sugars (`elab`, `macro`, etc.) can be understood from these first principles.

문법 설탕(`elab`, `macro` 등)의 동작은 이러한 기본 원칙으로부터 이해할 수 있습니다.


Lean will execute the aforementioned **parsing**/**elaboration**/**evaluation** steps for you automatically if you use `syntax`, `macro` and `elab` commands, however, when you're writing your tactics, you will also frequently need to perform these transitions manually. You can use the following functions for that:

`syntax`, `macro`, `elab` 명령을 사용하면 Lean이 앞서 언급한 **파싱**/**정교화**/**평가** 단계를 자동으로 실행해 줍니다. 하지만 전술을 작성할 때는 이러한 변환을 수동으로 수행해야 하는 경우도 많습니다. 이를 위해 다음 함수들을 사용할 수 있습니다:

![](https://github.com/arthurpaulino/lean4-metaprogramming-book/assets/7578559/b403e650-dab4-4843-be8c-8fb812695a3a)

Note how all functions that let us turn `Syntax` into `Expr` start with "elab", short for "elaboration"; and all functions that let us turn `Expr` (or `Syntax`) into `actual code` start with "eval", short for "evaluation".

`Syntax`를 `Expr`로 변환하는 모든 함수는 "elaboration"의 약자인 "elab"으로 시작하고, `Expr`(또는 `Syntax`)를 `실제 코드`로 변환하는 모든 함수는 "evaluation"의 약자인 "eval"로 시작한다는 점에 주목하세요.


In principle, you can do with a `macro` (almost?) anything you can do with the `elab` function. Just write what you would have in the body of your `elab` as a syntax within `macro`. However, the rule of thumb here is to only use `macro`s when the conversion is simple and truly feels elementary to the point of aliasing. As Henrik Böving puts it: "as soon as types or control flow is involved a macro is probably not reasonable anymore" ([Zulip thread](https://leanprover.zulipchat.com/#narrow/stream/270676-lean4/topic/The.20line.20between.20term.20elaboration.20and.20macro/near/280951290)).

원칙적으로 `elab` 함수로 할 수 있는 것은 (거의?) `macro`로도 할 수 있습니다. `elab` 본문에 작성할 내용을 `macro` 내의 구문으로 작성하면 됩니다. 하지만 여기서 경험칙은 변환이 단순하고 별칭(aliasing) 수준에서 진정으로 기본적이라고 느껴질 때만 `macro`를 사용하는 것입니다. Henrik Böving이 말한 것처럼: "타입이나 제어 흐름이 관여되는 순간 macro는 더 이상 적절하지 않을 것입니다" ([Zulip thread](https://leanprover.zulipchat.com/#narrow/stream/270676-lean4/topic/The.20line.20between.20term.20elaboration.20and.20macro/near/280951290)).

So - use `macro`s for creating syntax sugars, notations, and shortcuts, and prefer `elab`s for writing out code with some programming logic, even if it's potentially implementable in a `macro`.

따라서, 문법 설탕, 표기법, 단축키를 만들 때는 `macro`를 사용하고, `macro`로 구현 가능할 수 있더라도 프로그래밍 로직이 있는 코드를 작성할 때는 `elab`을 선호하세요.

Finally - some notes that should clarify a few things as you read the coming chapters.

마지막으로, 다음 장들을 읽을 때 몇 가지를 명확히 해줄 노트들이 있습니다.


In the `#assertType` example, we used `logInfo` to make our command print
something. If, instead, we just want to perform a quick debug, we can use
`dbg_trace`.

They behave a bit differently though, as we can see below:

`#assertType` 예시에서, 명령이 무언가를 출력하도록 `logInfo`를 사용했습니다. 대신 빠른 디버그만 수행하고 싶다면 `dbg_trace`를 사용할 수 있습니다.

하지만 아래에서 볼 수 있듯이 두 함수는 동작이 약간 다릅니다:

```
elab "traces" : tactic => do
  let array := List.replicate 2 (List.range 3)
  Lean.logInfo m!"logInfo: {array}"
  dbg_trace f!"dbg_trace: {array}"

example : True := by -- `example` is underlined in blue, outputting:
                     -- dbg_trace: [[0, 1, 2], [0, 1, 2]]
  traces -- now `traces` is underlined in blue, outputting
         -- logInfo: [[0, 1, 2], [0, 1, 2]]
  trivial
```


Since the objects defined in the meta-level are not the ones we're most
interested in proving theorems about, it can sometimes be overly tedious to
prove that they are type correct. For example, we don't care about proving that
a recursive function to traverse an expression is well-founded. Thus, we can
use the `partial` keyword if we're convinced that our function terminates. In
the worst-case scenario, our function gets stuck in a loop, causing the Lean server to crash
in VSCode, but the soundness of the underlying type theory implemented in the kernel
isn't affected.

메타 수준에서 정의된 객체들은 우리가 정리를 증명하는 데 주로 관심을 두는 대상이 아니기 때문에, 이들이 타입 정확성을 증명하는 것은 때로 지나치게 번거로울 수 있습니다. 예를 들어, 표현식을 순회하는 재귀 함수가 순서 기반(well-founded)임을 증명할 필요는 없습니다. 따라서 함수가 종료된다고 확신한다면 `partial` 키워드를 사용할 수 있습니다. 최악의 경우 함수가 루프에 빠져 VSCode에서 Lean 서버가 충돌할 수 있지만, 커널에서 구현된 기반 타입 이론의 건전성(soundness)은 영향을 받지 않습니다.