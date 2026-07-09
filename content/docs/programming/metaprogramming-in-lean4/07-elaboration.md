---
title: "Elaboration"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "metaprogramming"]
categories: ["programming"]
description: "Lean 4 Elaboration: Syntax를 Expr로 변환하는 과정과 elab 함수 작성"
---

The elaborator is the component in charge of turning the user facing
`Syntax` into something with which the rest of the compiler can work.
Most of the time, this means translating `Syntax` into `Expr`s but
there are also other use cases such as `#check` or `#eval`. Hence the
elaborator is quite a large piece of code, it lives
[here](https://github.com/leanprover/lean4/blob/master/src/Lean/Elab).

Elaborator는 사용자가 작성한 `Syntax`를 컴파일러의 나머지 부분이 처리할 수 있는 형태로 변환하는 컴포넌트입니다. 대부분의 경우 이는 `Syntax`를 `Expr`로 변환하는 것을 의미하지만, `#check`나 `#eval`과 같은 다른 용도도 존재합니다. 따라서 Elaborator는 꽤 방대한 코드로 이루어져 있으며, [여기](https://github.com/leanprover/lean4/blob/master/src/Lean/Elab)에 위치합니다.


A command is the highest level of `Syntax`, a Lean file is made
up of a list of commands. The most commonly used commands are declarations,
for example:

but there are also other ones, most notably `#check`, `#eval` and friends.
All commands live in the `command` syntax category so in order to declare
custom commands, their syntax has to be registered in that category.

커맨드는 `Syntax`의 가장 높은 수준으로, Lean 파일은 커맨드의 목록으로 구성됩니다. 가장 일반적으로 사용되는 커맨드는 선언(declaration)으로, 예를 들어 위와 같은 것들이 있습니다. 그 외에도 `#check`, `#eval` 등의 커맨드가 있습니다. 모든 커맨드는 `command` 구문 카테고리에 속하므로, 커스텀 커맨드를 선언하려면 해당 구문을 이 카테고리에 등록해야 합니다.


The next step is giving some semantics to the syntax. With commands, this
is done by registering a so called command elaborator.

Command elaborators have type `CommandElab` which is an alias for:
`Syntax → CommandElabM Unit`. What they do, is take the `Syntax` that
represents whatever the user wants to call the command and produce some
sort of side effect on the `CommandElabM` monad, after all the return
value is always `Unit`. The `CommandElabM` monad has 4 main kinds of
side effects:

1. Logging messages to the user via the `Monad` extensions
   `MonadLog` and `AddMessageContext`, like `#check`. This is done via
   functions that can be found in `Lean.Elab.Log`, the most notable ones
   being: `logInfo`, `logWarning` and `logError`.
2. Interacting with the `Environment` via the `Monad` extension `MonadEnv`.
   This is the place where all of the relevant information for the compiler
   is stored, all known declarations, their types, doc-strings, values etc.
   The current environment can be obtained via `getEnv` and set via `setEnv`
   once it has been modified. Note that quite often wrappers around `setEnv`
   like `addDecl` are the correct way to add information to the `Environment`.
3. Performing `IO`, `CommandElabM` is capable of running any `IO` operation.
   For example reading from files and based on their contents perform
   declarations.
4. Throwing errors, since it can run any kind of `IO`, it is only natural
   that it can throw errors via `throwError`.

Furthermore there are a bunch of other `Monad` extensions that are supported
by `CommandElabM`:

* `MonadRef` and `MonadQuotation` for `Syntax` quotations like in macros
* `MonadOptions` to interact with the options framework
* `MonadTrace` for debug trace information
* TODO: There are a few others though I'm not sure whether they are relevant,
  see the instance in `Lean.Elab.Command`

다음 단계는 구문에 의미론(semantics)을 부여하는 것입니다. 커맨드의 경우 이는 커맨드 Elaborator를 등록함으로써 이루어집니다.

커맨드 Elaborator의 타입은 `CommandElab`이며, 이는 `Syntax → CommandElabM Unit`의 별칭입니다. 커맨드 Elaborator는 사용자가 호출하려는 커맨드를 나타내는 `Syntax`를 받아 `CommandElabM` 모나드에 어떤 형태의 부수 효과(side effect)를 발생시킵니다. 반환값은 항상 `Unit`입니다. `CommandElabM` 모나드에는 4가지 주요 부수 효과가 있습니다:

1. `MonadLog`와 `AddMessageContext` 모나드 확장을 통해 사용자에게 메시지를 로깅합니다 (`#check`처럼). 이는 `Lean.Elab.Log`에 있는 함수들로 수행되며, 대표적으로 `logInfo`, `logWarning`, `logError`가 있습니다.
2. `MonadEnv` 모나드 확장을 통해 `Environment`와 상호작용합니다. 여기에는 컴파일러가 필요로 하는 모든 관련 정보, 즉 알려진 모든 선언, 그 타입, doc-string, 값 등이 저장됩니다. 현재 환경은 `getEnv`로 얻고, 수정 후 `setEnv`로 설정합니다. `Environment`에 정보를 추가할 때는 `setEnv`의 래퍼인 `addDecl` 등을 사용하는 것이 올바른 방법인 경우가 많습니다.
3. `IO` 수행: `CommandElabM`은 어떤 `IO` 연산도 실행할 수 있습니다. 예를 들어 파일을 읽고 그 내용에 따라 선언을 수행할 수 있습니다.
4. 에러 발생: 어떤 `IO`도 실행할 수 있으므로, `throwError`를 통해 에러를 발생시키는 것도 자연스럽게 가능합니다.

또한 `CommandElabM`이 지원하는 여러 다른 `Monad` 확장들도 있습니다:

* 매크로에서처럼 `Syntax` 인용(quotation)을 위한 `MonadRef`와 `MonadQuotation`
* 옵션 프레임워크와 상호작용하는 `MonadOptions`
* 디버그 트레이스 정보를 위한 `MonadTrace`
* TODO: 몇 가지 다른 것들도 있지만 관련성이 있는지 확실하지 않습니다. `Lean.Elab.Command`의 인스턴스를 참조하세요.


Now that we understand the type of command elaborators let's take a brief
look at how the elaboration process actually works:

1. Check whether any macros can be applied to the current `Syntax`.
   If there is a macro that does apply and does not throw an error
   the resulting `Syntax` is recursively elaborated as a command again.
2. If no macro can be applied, we search for all `CommandElab`s that have been
   registered for the `SyntaxKind` of the `Syntax` we are elaborating,
   using the `command_elab` attribute.
3. All of these `CommandElab` are then tried in order until one of them does not throw an
   `unsupportedSyntaxException`, Lean's way of indicating that the elaborator
   "feels responsible"
   for this specific `Syntax` construct. Note that it can still throw a regular
   error to indicate to the user that something is wrong. If no responsible
   elaborator is found, then the command elaboration is aborted with an `unexpected syntax`
   error message.

As you can see the general idea behind the procedure is quite similar to ordinary macro expansion.

커맨드 Elaborator의 타입을 이해했으니, Elaboration 과정이 실제로 어떻게 동작하는지 간략히 살펴보겠습니다:

1. 현재 `Syntax`에 적용할 수 있는 매크로가 있는지 확인합니다. 적용 가능한 매크로가 있고 에러를 발생시키지 않는다면, 결과로 나온 `Syntax`는 다시 커맨드로서 재귀적으로 Elaborate됩니다.
2. 적용 가능한 매크로가 없으면, `command_elab` 속성을 사용하여 현재 Elaborate하려는 `Syntax`의 `SyntaxKind`에 등록된 모든 `CommandElab`을 검색합니다.
3. 이 `CommandElab`들을 순서대로 시도하여, `unsupportedSyntaxException`을 던지지 않는 것을 찾습니다. `unsupportedSyntaxException`은 Elaborator가 해당 `Syntax` 구조에 대해 "책임감을 느끼지 않는다"는 것을 나타내는 Lean의 방식입니다. 단, 일반적인 에러를 던져 사용자에게 문제가 있음을 알릴 수는 있습니다. 책임지는 Elaborator를 찾지 못하면, 커맨드 Elaboration은 `unexpected syntax` 에러 메시지와 함께 중단됩니다.

보시다시피 이 절차의 기본 아이디어는 일반적인 매크로 확장과 상당히 유사합니다.


Now that we know both what a `CommandElab` is and how they are used, we can
start looking into writing our own. The steps for this, as we learned above, are:

1. Declaring the syntax
2. Declaring the elaborator
3. Registering the elaborator as responsible for the syntax via the `command_elab`
   attribute.

Let's see how this is done:

`CommandElab`이 무엇인지, 그리고 어떻게 사용되는지 알았으니, 이제 직접 작성하는 방법을 살펴볼 수 있습니다. 위에서 배운 것처럼 그 단계는 다음과 같습니다:

1. 구문 선언
2. Elaborator 선언
3. `command_elab` 속성을 통해 Elaborator를 해당 구문의 담당자로 등록

어떻게 이루어지는지 살펴보겠습니다:

```
import Lean

open Lean Elab Command Term Meta

syntax (name := mycommand1) "#mycommand1" : command -- declare the syntax

@[command_elab mycommand1]
def mycommand1Impl : CommandElab := fun stx => do -- declare and register the elaborator
  logInfo "Hello World"

#mycommand1 -- Hello World
```

You might think that this is a little boiler-platey and it turns out the Lean
devs did as well so they added a macro for this!

이것이 다소 상용구(boilerplate)가 많다고 생각할 수 있는데, Lean 개발자들도 그렇게 생각하여 이를 위한 매크로를 추가했습니다!

```
elab "#mycommand2" : command =>
  logInfo "Hello World"

#mycommand2 -- Hello World
```

Note that, due to the fact that command elaboration supports multiple
registered elaborators for the same syntax, we can in fact overload
syntax, if we want to.

커맨드 Elaboration은 동일한 구문에 대해 여러 Elaborator를 등록하는 것을 지원하므로, 원한다면 구문을 오버로드할 수 있습니다.

```
@[command_elab mycommand1]
def myNewImpl : CommandElab := fun stx => do
  logInfo "new!"

#mycommand1 -- new!
```

Furthermore it is also possible to only overload parts of syntax by
throwing an `unsupportedSyntaxException` in the cases we want the default
handler to deal with it or just letting the `elab` command handle it.

In the following example, we are not extending the original `#check` syntax,
but adding a new `SyntaxKind` for this specific syntax construct.
However, from the point of view of the user, the effect is basically the same.

더 나아가, 기본 핸들러가 처리하길 원하는 경우에 `unsupportedSyntaxException`을 던지거나 `elab` 커맨드가 처리하도록 함으로써 구문의 일부만 오버로드하는 것도 가능합니다.

다음 예시에서는 원래의 `#check` 구문을 확장하는 것이 아니라, 이 특정 구문 구조를 위한 새로운 `SyntaxKind`를 추가하고 있습니다. 그러나 사용자의 관점에서는 효과가 기본적으로 동일합니다.

```
elab "#check" "mycheck" : command => do
  logInfo "Got ya!"
```

This is actually extending the original `#check`

이것은 실제로 원래의 `#check`를 확장하는 방법입니다.

```
@[command_elab Lean.Parser.Command.check] def mySpecialCheck : CommandElab := fun stx => do
  if let some str := stx[1].isStrLit? then
    logInfo s!"Specially elaborated string literal!: {str} : String"
  else
    throwUnsupportedSyntax

#check mycheck -- Got ya!
#check "Hello" -- Specially elaborated string literal!: Hello : String
#check Nat.add -- Nat.add : Nat → Nat → Nat
```


As a final mini project for this section let's build a command elaborator
that is actually useful. It will take a command and use the same mechanisms
as `elabCommand` (the entry point for command elaboration) to tell us
which macros or elaborators are relevant to the command we gave it.

We will not go through the effort of actually reimplementing `elabCommand` though

이 섹션의 마지막 미니 프로젝트로, 실제로 유용한 커맨드 Elaborator를 만들어 보겠습니다. 이 Elaborator는 커맨드를 받아 `elabCommand`(커맨드 Elaboration의 진입점)와 동일한 메커니즘을 사용하여, 우리가 준 커맨드와 관련된 매크로나 Elaborator가 무엇인지 알려줄 것입니다.

단, `elabCommand`를 실제로 재구현하는 수고는 하지 않겠습니다.

```
elab "#findCElab " c:command : command => do
  let macroRes ← liftMacroM <| expandMacroImpl? (←getEnv) c
  match macroRes with
  | some (name, _) => logInfo s!"Next step is a macro: {name.toString}"
  | none =>
    let kind := c.raw.getKind
    let elabs := commandElabAttribute.getEntries (←getEnv) kind
    match elabs with
    | [] => logInfo s!"There is no elaborators for your syntax, looks like its bad :("
    | _ => logInfo s!"Your syntax may be elaborated by: {elabs.map (fun el => el.declName.toString)}"

#findCElab def lala := 12 -- Your syntax may be elaborated by: [Lean.Elab.Command.elabDeclaration]
#findCElab abbrev lolo := 12 -- Your syntax may be elaborated by: [Lean.Elab.Command.elabDeclaration]
#findCElab #check foo -- even our own syntax!: Your syntax may be elaborated by: [mySpecialCheck, Lean.Elab.Command.elabCheck]
#findCElab open Hi -- Your syntax may be elaborated by: [Lean.Elab.Command.elabOpen]
#findCElab namespace Foo -- Your syntax may be elaborated by: [Lean.Elab.Command.elabNamespace]
#findCElab #findCElab open Bar -- even itself!: Your syntax may be elaborated by: [«_aux_lean_elaboration___elabRules_command#findCElab__1»]
```

TODO: Maybe we should also add a mini project that demonstrates a
non # style command aka a declaration, although nothing comes to mind right now.
TODO: Define a `conjecture` declaration, similar to `lemma/theorem`, except that
it is automatically sorried. The `sorry` could be a custom one, to reflect that
the "conjecture" might be expected to be true.

TODO: `#` 스타일이 아닌 커맨드, 즉 선언(declaration)을 보여주는 미니 프로젝트도 추가하면 좋을 것 같지만, 지금 당장은 떠오르는 것이 없습니다.
TODO: `lemma/theorem`과 유사하지만 자동으로 sorry 처리되는 `conjecture` 선언을 정의하세요. "추측(conjecture)"이 참으로 예상된다는 것을 반영하기 위해 sorry를 커스텀할 수도 있습니다.


A term is a `Syntax` object that represents some sort of `Expr`.
Term elaborators are the ones that do the work for most of the code we write.
Most notably they elaborate all the values of things like definitions,
types (since these are also just `Expr`) etc.

All terms live in the `term` syntax category (which we have seen in action
in the macro chapter already). So, in order to declare custom terms, their
syntax needs to be registered in that category.

Term은 어떤 형태의 `Expr`을 나타내는 `Syntax` 객체입니다. Term Elaborator는 우리가 작성하는 대부분의 코드에서 실제 작업을 수행하는 것들입니다. 특히 정의(definition)나 타입(이것들도 단지 `Expr`입니다)의 값들을 Elaborate합니다.

모든 term은 `term` 구문 카테고리에 속합니다(매크로 챕터에서 이미 확인했습니다). 따라서 커스텀 term을 선언하려면 해당 구문을 이 카테고리에 등록해야 합니다.


As with command elaboration, the next step is giving some semantics to the syntax.
With terms, this is done by registering a so called term elaborator.

Term elaborators have type `TermElab` which is an alias for:
`Syntax → Option Expr → TermElabM Expr`. This type is already
quite different from command elaboration:

* As with command elaboration the `Syntax` is whatever the user used
  to create this term
* The `Option Expr` is the expected type of the term, since this cannot
  always be known it is only an `Option` argument
* Unlike command elaboration, term elaboration is not only executed
  because of its side effects -- the `TermElabM Expr` return value does
  actually contain something of interest, namely, the `Expr` that represents
  the `Syntax` object.

`TermElabM` is basically an upgrade of `CommandElabM` in every regard:
it supports all the capabilities we mentioned above, plus two more.
The first one is quite simple: On top of running `IO` code it is also
capable of running `MetaM` code, so `Expr`s can be constructed nicely.
The second one is very specific to the term elaboration loop.

커맨드 Elaboration과 마찬가지로, 다음 단계는 구문에 의미론을 부여하는 것입니다. Term의 경우 이는 Term Elaborator를 등록함으로써 이루어집니다.

Term Elaborator의 타입은 `TermElab`이며, 이는 `Syntax → Option Expr → TermElabM Expr`의 별칭입니다. 이 타입은 커맨드 Elaboration과 이미 꽤 다릅니다:

* 커맨드 Elaboration과 마찬가지로 `Syntax`는 사용자가 이 term을 만들기 위해 사용한 것입니다.
* `Option Expr`은 term의 예상 타입입니다. 이것은 항상 알 수 있는 것이 아니므로 `Option` 인자입니다.
* 커맨드 Elaboration과 달리, Term Elaboration은 부수 효과만을 위해 실행되는 것이 아닙니다 — `TermElabM Expr` 반환값은 실제로 흥미로운 내용을 담고 있는데, 바로 `Syntax` 객체를 나타내는 `Expr`입니다.

`TermElabM`은 모든 면에서 `CommandElabM`의 업그레이드 버전입니다: 위에서 언급한 모든 기능을 지원하며, 두 가지가 추가됩니다. 첫 번째는 간단합니다: `IO` 코드 실행에 더해 `MetaM` 코드도 실행할 수 있어, `Expr`을 편리하게 구성할 수 있습니다. 두 번째는 Term Elaboration 루프에 특화된 것입니다.


The basic idea of term elaboration is the same as command elaboration:
expand macros and recurse or run term elaborators that have been registered
for the `Syntax` via the `term_elab` attribute (they might in turn run term elaboration)
until we are done. There is, however, one special action that a term elaborator
can do during its execution.

A term elaborator may throw `Except.postpone`. This indicates that
the term elaborator requires more
information to continue its work. In order to represent this missing information,
Lean uses so called synthetic metavariables. As you know from before, metavariables
are holes in `Expr`s that are waiting to be filled in. Synthetic metavariables are
different in that they have special methods that are used to solve them,
registered in `SyntheticMVarKind`. Right now, there are four of these:

* `typeClass`, the metavariable should be solved with typeclass synthesis
* `coe`, the metavariable should be solved via coercion (a special case of typeclass)
* `tactic`, the metavariable is a tactic term that should be solved by running a tactic
* `postponed`, the ones that are created at `Except.postpone`

Once such a synthetic metavariable is created, the next higher level term elaborator will continue.
At some point, execution of postponed metavariables will be resumed by the term elaborator,
in hopes that it can now complete its execution. We can try to see this in
action with the following example:

Term Elaboration의 기본 아이디어는 커맨드 Elaboration과 동일합니다: 매크로를 확장하고 재귀하거나, `term_elab` 속성을 통해 `Syntax`에 등록된 Term Elaborator를 실행합니다(이것들이 다시 Term Elaboration을 실행할 수 있습니다). 그러나 Term Elaborator가 실행 중에 할 수 있는 특별한 동작이 하나 있습니다.

Term Elaborator는 `Except.postpone`를 던질 수 있습니다. 이는 Term Elaborator가 작업을 계속하기 위해 더 많은 정보가 필요하다는 것을 나타냅니다. 이 누락된 정보를 표현하기 위해, Lean은 소위 합성 메타변수(synthetic metavariable)를 사용합니다. 앞서 알고 있듯이, 메타변수는 `Expr`에서 채워지기를 기다리는 구멍(hole)입니다. 합성 메타변수는 이와 달리, `SyntheticMVarKind`에 등록된 특별한 방법을 통해 해결됩니다. 현재 네 가지 종류가 있습니다:

* `typeClass`: 타입클래스 합성(synthesis)으로 메타변수를 해결합니다.
* `coe`: 강제 변환(coercion)을 통해 메타변수를 해결합니다(타입클래스의 특수한 경우).
* `tactic`: 메타변수가 tactic을 실행하여 해결해야 하는 tactic term입니다.
* `postponed`: `Except.postpone`에서 생성된 것들입니다.

이러한 합성 메타변수가 생성되면, 더 높은 수준의 Term Elaborator가 계속 실행됩니다. 어느 시점에 지연된(postponed) 메타변수의 실행이 Term Elaborator에 의해 재개되며, 이때 실행을 완료할 수 있기를 기대합니다. 다음 예시를 통해 이를 확인할 수 있습니다:

```
#check set_option trace.Elab.postpone true in List.foldr .add 0 [1,2,3] -- [Elab.postpone] .add : ?m.5695 → ?m.5696 → ?m.5696
```

What happened here is that the elaborator for function applications started
at `List.foldr` which is a generic function so it created metavariables
for the implicit type parameters. Then, it attempted to elaborate the first argument `.add`.

In case you don't know how `.name` works, the basic idea is that quite
often (like in this case) Lean should be able to infer the output type (in this case `Nat`)
of a function (in this case `Nat.add`). In such cases, the `.name` feature will then simply
search for a function named `name` in the namespace `Nat`. This is especially
useful when you want to use constructors of a type without referring to its
namespace or opening it, but can also be used like above.

Now back to our example, while Lean does at this point already know that `.add`
needs to have type: `?m1 → ?m2 → ?m2` (where `?x` is notation for a metavariable)
the elaborator for `.add` does need to know the actual value of `?m2` so the
term elaborator postpones execution (by internally creating a synthetic metavariable
in place of `.add`), the elaboration of the other two arguments then yields the fact that
`?m2` has to be `Nat` so once the `.add` elaborator is continued it can work with
this information to complete elaboration.

We can also easily provoke cases where this does not work out. For example:

여기서 일어난 일은, 함수 적용(function application)의 Elaborator가 제네릭 함수인 `List.foldr`에서 시작했기 때문에 암시적 타입 파라미터에 대한 메타변수를 생성한 것입니다. 그런 다음 첫 번째 인자인 `.add`를 Elaborate하려 시도했습니다.

`.name`이 어떻게 동작하는지 모르는 경우를 위해 설명하면, 기본 아이디어는 (이 경우처럼) Lean이 함수(`Nat.add`)의 출력 타입(`Nat`)을 추론할 수 있는 경우가 많다는 것입니다. 이런 경우 `.name` 기능은 단순히 `Nat` 네임스페이스에서 `name`이라는 함수를 검색합니다. 이는 타입의 생성자(constructor)를 네임스페이스를 참조하거나 열지 않고 사용하고 싶을 때 특히 유용하지만, 위와 같이도 사용할 수 있습니다.

다시 예시로 돌아와서, Lean은 이 시점에서 이미 `.add`가 `?m1 → ?m2 → ?m2` 타입을 가져야 한다는 것을 알고 있지만(`?x`는 메타변수 표기법), `.add`의 Elaborator는 `?m2`의 실제 값을 알아야 합니다. 따라서 Term Elaborator는 실행을 지연시키고(`.add` 자리에 합성 메타변수를 내부적으로 생성), 나머지 두 인자의 Elaboration이 `?m2`가 `Nat`이어야 한다는 사실을 밝혀냅니다. 그러면 `.add`의 Elaborator가 재개될 때 이 정보를 가지고 Elaboration을 완료할 수 있습니다.

이것이 잘 되지 않는 경우도 쉽게 유발할 수 있습니다. 예를 들어:

```
#check_failure set_option trace.Elab.postpone true in List.foldr .add
-- [Elab.postpone] .add : ?m.5808 → ?m.5809 → ?m.5809
-- invalid dotted identifier notation, expected type is not of the form (... → C ...) where C is a constant
  -- ?m.5808 → ?m.5809 → ?m.5809
```

In this case `.add` first postponed its execution, then got called again
but didn't have enough information to finish elaboration and thus failed.

이 경우 `.add`는 먼저 실행을 지연시켰다가, 다시 호출되었지만 Elaboration을 완료하기 위한 충분한 정보가 없어 실패했습니다.


Adding new term elaborators works basically the same way as adding new
command elaborators so we'll only take a very brief look:

새로운 Term Elaborator를 추가하는 방법은 새로운 커맨드 Elaborator를 추가하는 방법과 기본적으로 동일하므로, 간략히만 살펴보겠습니다:

```
syntax (name := myterm1) "myterm_1" : term

def mytermValues := [1, 2]

@[term_elab myterm1]
def myTerm1Impl : TermElab := fun stx type? => do
  mkAppM ``List.get! #[.const ``mytermValues [], mkNatLit 0] -- `MetaM` code

#eval myterm_1 -- 1

-- Also works with `elab`
elab "myterm_2" : term => do
  mkAppM ``List.get! #[.const ``mytermValues [], mkNatLit 1] -- `MetaM` code

#eval myterm_2 -- 2
```


As a final mini project for this chapter we will recreate one of the most
commonly used Lean syntax sugars, the `⟨a,b,c⟩` notation as a short hand
for single constructor types:

이 챕터의 마지막 미니 프로젝트로, Lean에서 가장 많이 사용되는 구문 설탕(syntax sugar) 중 하나인 단일 생성자 타입의 약어인 `⟨a,b,c⟩` 표기법을 다시 만들어 보겠습니다:

```
-- slightly different notation so no ambiguity happens
syntax (name := myanon) "⟨⟨" term,* "⟩⟩" : term

def getCtors (typ : Name) : MetaM (List Name) := do
  let env ← getEnv
  match env.find? typ with
  | some (ConstantInfo.inductInfo val) =>
    pure val.ctors
  | _ => pure []

@[term_elab myanon]
def myanonImpl : TermElab := fun stx typ? => do
  -- Attempt to postpone execution if the type is not known or is a metavariable.
  -- Metavariables are used by things like the function elaborator to fill
  -- out the values of implicit parameters when they haven't gained enough
  -- information to figure them out yet.
  -- Term elaborators can only postpone execution once, so the elaborator
  -- doesn't end up in an infinite loop. Hence, we only try to postpone it,
  -- otherwise we may cause an error.
  tryPostponeIfNoneOrMVar typ?
  -- If we haven't found the type after postponing just error
  let some typ := typ? | throwError "expected type must be known"
  if typ.isMVar then
    throwError "expected type must be known"
  let Expr.const base .. := typ.getAppFn | throwError s!"type is not of the expected form: {typ}"
  let [ctor] ← getCtors base | throwError "type doesn't have exactly one constructor"
  let args := TSyntaxArray.mk stx[1].getSepArgs
  let stx ← `($(mkIdent ctor) $args*) -- syntax quotations
  elabTerm stx typ -- call term elaboration recursively

#check (⟨⟨1, sorry⟩⟩ : Fin 12) -- { val := 1, isLt := (_ : 1 < 12) } : Fin 12
#check_failure ⟨⟨1, sorry⟩⟩ -- expected type must be known
#check_failure (⟨⟨0⟩⟩ : Nat) -- type doesn't have exactly one constructor
#check_failure (⟨⟨⟩⟩ : Nat → Nat) -- type is not of the expected form: Nat -> Nat
```

As a final note, we can shorten the postponing act by using an additional
syntax sugar of the `elab` syntax instead:

마지막으로, `elab` 구문의 추가적인 syntax sugar를 사용하여 지연 처리를 더 간단히 할 수 있습니다:

```
-- This `t` syntax will effectively perform the first two lines of `myanonImpl`
elab "⟨⟨" args:term,* "⟩⟩" : term <= t => do
  sorry
```


1. Consider the following code. Rewrite `syntax` + `@[term_elab hi]... : TermElab` combination using just `elab`.

1. 다음 코드를 살펴보세요. `syntax` + `@[term_elab hi]... : TermElab` 조합을 `elab`만 사용하여 재작성하세요.

   ```
   syntax (name := hi) term " ♥ " " ♥ "? " ♥ "? : term

   @[term_elab hi]
   def heartElab : TermElab := fun stx tp =>
     match stx with
       | `($l:term ♥) => do
         let nExpr ← elabTermEnsuringType l (mkConst `Nat)
         return Expr.app (Expr.app (Expr.const `Nat.add []) nExpr) (mkNatLit 1)
       | `($l:term ♥♥) => do
         let nExpr ← elabTermEnsuringType l (mkConst `Nat)
         return Expr.app (Expr.app (Expr.const `Nat.add []) nExpr) (mkNatLit 2)
       | `($l:term ♥♥♥) => do
         let nExpr ← elabTermEnsuringType l (mkConst `Nat)
         return Expr.app (Expr.app (Expr.const `Nat.add []) nExpr) (mkNatLit 3)
       | _ =>
         throwUnsupportedSyntax
   ```
2. Here is some syntax taken from a real mathlib command `alias`.

   ```
   syntax (name := our_alias) (docComment)? "our_alias " ident " ← " ident* : command
   ```

   We want `alias hi ← hello yes` to print out the identifiers after `←` - that is, "hello" and "yes".

   Please add these semantics:

   **a)** using `syntax` + `@[command_elab alias] def elabOurAlias : CommandElab`.
   **b)** using `syntax` + `elab_rules`.
   **c)** using `elab`.

2. 실제 mathlib 커맨드 `alias`에서 가져온 구문입니다.

   

   `alias hi ← hello yes`가 `←` 다음에 오는 식별자들, 즉 "hello"와 "yes"를 출력하도록 하고 싶습니다.

   다음 방법으로 이 의미론을 추가하세요:

   **a)** `syntax` + `@[command_elab alias] def elabOurAlias : CommandElab` 사용.
   **b)** `syntax` + `elab_rules` 사용.
   **c)** `elab` 사용.

3. Here is some syntax taken from a real mathlib tactic `nth_rewrite`.

   ```
   open Parser.Tactic
   syntax (name := nthRewriteSeq) "nth_rewrite " (config)? num rwRuleSeq (ppSpace location)? : tactic
   ```

   We want `nth_rewrite 5 [←add_zero a] at h` to print out `"rewrite location!"` if the user provided location, and `"rewrite target!"` if the user didn't provide location.

   Please add these semantics:

   **a)** using `syntax` + `@[tactic nthRewrite] def elabNthRewrite : Lean.Elab.Tactic.Tactic`.
   **b)** using `syntax` + `elab_rules`.
   **c)** using `elab`.

3. 실제 mathlib tactic `nth_rewrite`에서 가져온 구문입니다.

   

   `nth_rewrite 5 [←add_zero a] at h`가 사용자가 location을 제공했을 때는 `"rewrite location!"`을, 제공하지 않았을 때는 `"rewrite target!"`을 출력하도록 하고 싶습니다.

   다음 방법으로 이 의미론을 추가하세요:

   **a)** `syntax` + `@[tactic nthRewrite] def elabNthRewrite : Lean.Elab.Tactic.Tactic` 사용.
   **b)** `syntax` + `elab_rules` 사용.
   **c)** `elab` 사용.