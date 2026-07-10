---
title: "6. Lean과 상호작용하기"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "theorem-proving", "type-theory"]
categories: ["programming"]
description: "임포트, 섹션, 네임스페이스, 속성(attribute) 등 Lean과 상호작용하는 실전 도구를 다룹니다."
---

You are now familiar with the fundamentals of dependent type theory,
both as a language for defining mathematical objects and a language
for constructing proofs. The one thing you are missing is a mechanism
for defining new data types. We will fill this gap in the next
chapter, which introduces the notion of an *inductive data type*. But
first, in this chapter, we take a break from the mechanics of type
theory to explore some pragmatic aspects of interacting with Lean.

이제 종속 타입 이론의 기초에 대해 잘 알게 되었습니다. 수학 객체를 정의하기 위한 언어이자 증명을 구성하기 위한 언어로서 말입니다. 유일하게 부족한 것은 새로운 데이터 타입을 정의하는 메커니즘입니다. 우리는 다음 장에서 *귀납적 데이터 타입*이라는 개념을 소개하여 이 공백을 채울 것입니다. 하지만 먼저 이 장에서는 타입 이론의 기계적인 면에서 벗어나 Lean과 상호작용하는 실용적인 측면을 탐구해봅시다.

Not all of the information found here will be useful to you right
away. We recommend skimming this section to get a sense of Lean's
features, and then returning to it as necessary.

여기서 찾은 모든 정보가 당신에게 바로 유용할 것은 아닙니다. 우리는 이 섹션을 훑어보면서 Lean의 기능에 대한 감각을 얻고, 필요할 때 다시 돌아오기를 권장합니다.

## 6.1. Messages

Lean produces three kinds of messages:

Lean은 세 가지 종류의 메시지를 생성합니다:

오류

:   오류는 코드의 불일치로 인해 처리할 수 없을 때 생성됩니다. 예시로는 구문 오류(예: 누락된 `)`)와 자연수에 함수를 더하려고 시도하는 것과 같은 타입 오류가 포함됩니다.

경고

:   경고는 `sorry`의 존재와 같은 코드의 잠재적인 문제를 설명합니다. 오류와 달리 코드가 무의미하지는 않지만, 경고는 신중한 주의를 받을 가치가 있습니다.

정보

:   정보는 코드의 문제를 나타내지 않으며, `#check`과 `#eval`과 같은 명령어의 출력을 포함합니다.

Lean can check that a command produces the expected messages. If the messages match,
then any errors are disregarded; this can be used to ensure that the right errors occur.
If they don't, an error is produced. You can use the `#guard_msgs` command to indicate
which messages are expected.

Lean은 명령이 예상된 메시지를 생성하는지 확인할 수 있습니다. 메시지가 일치하면 모든 오류가 무시되며, 이는 올바른 오류가 발생하도록 보장하는 데 사용할 수 있습니다. 일치하지 않으면 오류가 생성됩니다. `#guard_msgs` 명령을 사용하여 어떤 메시지가 예상되는지 나타낼 수 있습니다.

Here is an example:

다음은 예시입니다:

```
/--
error: Type mismatch
  "Not a number"
has type
  String
but is expected to have type
  Nat
-/
#guard_msgs in
def x : Nat := "Not a number"
```

Including a message category in parentheses after `#guard_msgs` causes it to check only
the specified category, letting others through. In this example, `#eval` issues an error
due to the presence of `sorry`, but the warning that is always issued for `sorry` is displayed
as usual:

`#guard_msgs` 뒤의 괄호 안에 메시지 카테고리를 포함하면 지정된 카테고리만 확인하고 다른 카테고리는 통과시킵니다. 이 예시에서 `#eval`은 `sorry`의 존재로 인해 오류를 발생시키지만, `sorry`에 대해 항상 발생하는 경고는 평소대로 표시됩니다:

```
/--
error: aborting evaluation since the expression depends on the
'sorry' axiom, which can lead to runtime instability and crashes.

To attempt to evaluate anyway despite the risks, use the '#eval!'
command.
-/
#guard_msgs(error) in
#eval (sorry : Nat)
```

```
declaration uses 'sorry'
```

Without the configuration, both messages are captured:

설정 없이 두 메시지가 모두 캡처됩니다:

```
/--
error: aborting evaluation since the expression depends on the
'sorry' axiom, which can lead to runtime instability and crashes.

To attempt to evaluate anyway despite the risks, use the '#eval!'
command.
---
warning: declaration uses 'sorry'
-/
#guard_msgs in
#eval (sorry : Nat)
```

```
❌️ Docstring on `#guard_msgs` does not match generated message:

- error: aborting evaluation since the expression depends on the
- 'sorry' axiom, which can lead to runtime instability and crashes.
+ warning: declaration uses 'sorry'
+ ---
+ error: aborting evaluation since the expression depends on the 'sorry' axiom, which can lead to runtime instability and crashes.
 
- To attempt to evaluate anyway despite the risks, use the '#eval!'
- command.
- ---
- warning: declaration uses 'sorry'
+ To attempt to evaluate anyway despite the risks, use the '#eval!' command.
```

Some examples in this book use `#guard_msgs` to indicate expected errors.

이 책의 일부 예시는 예상된 오류를 나타내기 위해 `#guard_msgs`를 사용합니다.

## 6.2. Importing Files

The goal of Lean's front end is to interpret user input, construct
formal expressions, and check that they are well-formed and type-correct.
Lean also supports the use of various editors, which provide
continuous checking and feedback. More information can be found on the
Lean [documentation pages](https://lean-lang.org/documentation/).

Lean의 프론트엔드의 목표는 사용자 입력을 해석하고, 형식적 표현을 구성하며, 그것이 잘 형성되고 타입이 올바른지 확인하는 것입니다. Lean은 또한 지속적인 확인과 피드백을 제공하는 다양한 편집기의 사용을 지원합니다. 더 많은 정보는 Lean [문서 페이지](https://lean-lang.org/documentation/)에서 찾을 수 있습니다.

The definitions and theorems in Lean's standard library are spread
across multiple files. Users may also wish to make use of additional
libraries, or develop their own projects across multiple files. When
Lean starts, it automatically imports the contents of the library
`Init` folder, which includes a number of fundamental definitions
and constructions. As a result, most of the examples we present here
work “out of the box.”

Lean의 표준 라이브러리의 정의와 정리는 여러 파일에 걸쳐 있습니다. 사용자는 또한 추가 라이브러리를 사용하거나 여러 파일에 걸쳐 자신의 프로젝트를 개발하고 싶을 수 있습니다. Lean이 시작될 때, 많은 기본 정의와 구성을 포함하는 라이브러리 `Init` 폴더의 내용을 자동으로 가져옵니다. 그 결과, 여기에서 제시하는 대부분의 예시는 “기본적으로” 작동합니다.

If you want to use additional files, however, they need to be imported
manually, via an `import` statement at the beginning of a file. The
command

`import`` Bar.Baz.Blah`

imports the file `Bar/Baz/Blah.olean`, where the descriptions are
interpreted relative to the Lean *search path*. Information as to how
the search path is determined can be found on the
[documentation pages](https://lean-lang.org/documentation/).
By default, it includes the standard library directory, and (in some contexts)
the root of the user's local project.

그러나 추가 파일을 사용하려면 파일의 시작 부분에서 `import` 문을 통해 수동으로 가져와야 합니다. 명령어는 다음과 같습니다:

파일 `Bar/Baz/Blah.olean`을 가져오며, 여기서 설명은 Lean *검색 경로*에 상대적으로 해석됩니다. 검색 경로가 어떻게 결정되는지에 대한 정보는 [문서 페이지](https://lean-lang.org/documentation/)에서 찾을 수 있습니다. 기본적으로, 표준 라이브러리 디렉토리와 (경우에 따라) 사용자의 로컬 프로젝트의 루트를 포함합니다.

Importing is transitive. In other words, if you import `Foo` and `Foo` imports `Bar`,
then you also have access to the contents of `Bar`, and do not need to import it explicitly.

가져오기는 추이적입니다. 즉, `Foo`를 가져오고 `Foo`가 `Bar`를 가져오면, `Bar`의 내용에도 접근할 수 있으며 명시적으로 가져올 필요가 없습니다.

## 6.3. More on Sections

Lean provides various sectioning mechanisms to help structure a
theory. You saw in [Variables and Sections](../02-dependent-type-theory/#variables-and-sections) that the
`section` command makes it possible not only to group together
elements of a theory that go together, but also to declare variables
that are inserted as arguments to theorems and definitions, as
necessary. Remember that the point of the `variable` command is to
declare variables for use in theorems, as in the following example:

Lean은 이론을 구조화하는 데 도움이 되는 다양한 섹셔닝 메커니즘을 제공합니다. [변수와 섹션](../02-dependent-type-theory/#variables-and-sections)에서 보았듯이, `section` 명령은 함께 속하는 이론의 요소들을 그룹화할 뿐 아니라 필요에 따라 정리와 정의의 인수로 삽입되는 변수를 선언할 수 있게 해줍니다. `variable` 명령의 목적은 다음 예시에서처럼 정리에서 사용할 변수를 선언하는 것임을 기억하세요:

```
section
variable (x y : Nat)
def double := x + x
#check double y
```

```
double y : Nat
```

```
#check double (2 * x)
```

```
double (2 * x) : Nat
```

```
attribute [local simp] Nat.add_assoc Nat.add_comm Nat.add_left_comm
theorem t1 : double (x + y) = double x + double y := by
simp [double]
#check t1 y
```

```
t1 y : ∀ (y_1 : Nat), double (y + y_1) = double y + double y_1
```

```
#check t1 (2 * x)
```

```
t1 (2 * x) : ∀ (y : Nat), double (2 * x + y) = double (2 * x) + double y
```

```
theorem t2 : double (x * y) = double x * y := by
simp [double, Nat.add_mul]
end
```

The definition of `double` does not have to declare `x` as an
argument; Lean detects the dependence and inserts it
automatically. Similarly, Lean detects the occurrence of `x` in
`t1` and `t2`, and inserts it automatically there, too.
Note that `double` does *not* have `y` as argument. Variables are only
included in declarations where they are actually used.

`double`의 정의는 `x`를 인수로 선언할 필요가 없습니다. Lean은 의존성을 감지하고 자동으로 삽입합니다. 마찬가지로 Lean은 `t1`과 `t2`에서 `x`의 발생을 감지하고 거기에도 자동으로 삽입합니다. `double`은 `y`를 인수로 가지지 *않음*을 주목하세요. 변수는 실제로 사용되는 선언에서만 포함됩니다.

## 6.4. More on Namespaces

In Lean, identifiers are given by hierarchical *names* like
`Foo.Bar.baz`. We saw in [Namespaces](../02-dependent-type-theory/#namespaces) that Lean provides
mechanisms for working with hierarchical names. The command
`namespace` `Foo` causes `Foo` to be prepended to the name of each
definition and theorem until `end` `Foo` is encountered. The command
`open` `Foo` then creates temporary *aliases* to definitions and
theorems that begin with prefix `Foo`.

Lean에서 식별자는 `Foo.Bar.baz`와 같은 계층적 *이름*으로 주어집니다. [네임스페이스](../02-dependent-type-theory/#namespaces)에서 보았듯이 Lean은 계층적 이름으로 작업하기 위한 메커니즘을 제공합니다. `namespace` `Foo` 명령은 `end` `Foo`를 만날 때까지 각 정의와 정리의 이름 앞에 `Foo`를 붙입니다. 그런 다음 `open` `Foo` 명령은 `Foo` 접두사로 시작하는 정의와 정리에 대한 임시 *별칭*을 생성합니다.

```
namespace Foo
def bar : Nat := 1
end Foo
open Foo
#check bar
```

```
Foo.bar : Nat
```

```
#check Foo.bar
```

```
Foo.bar : Nat
```

The following definition

```
def Foo.bar : Nat := 1
```

is treated as a macro, and expands to

다음 정의는

매크로로 처리되며 다음과 같이 확장됩니다:

```
namespace Foo
def bar : Nat := 1
end Foo
```

Although the names of theorems and definitions have to be unique, the
aliases that identify them do not. When we open a namespace, an
identifier may be ambiguous. Lean tries to use type information to
disambiguate the meaning in context, but you can always disambiguate
by giving the full name. To that end, the string `_root_` is an
explicit description of the empty prefix.

정리와 정의의 이름은 고유해야 하지만, 그것들을 식별하는 별칭은 그렇지 않습니다. 네임스페이스를 열 때 식별자가 모호할 수 있습니다. Lean은 문맥에서 의미를 명확히 하기 위해 타입 정보를 사용하려고 시도하지만, 전체 이름을 제공하여 항상 명확히 할 수 있습니다. 이를 위해 문자열 `_root_`는 빈 접두사의 명시적 설명입니다.

```
def String.add (a b : String) : String :=
a ++ b
def Bool.add (a b : Bool) : Bool :=
a != b
def add (α β : Type) : Type := Sum α β
open Bool
open String
-- This reference is ambiguous:
-- #check add

#check String.add
```

```
String.add (a b : String) : String
```

```
#check Bool.add
```

```
Bool.add (a b : Bool) : Bool
```

```
#check _root_.add
```

```
_root_.add (α β : Type) : Type
```

```
#check add "hello" "world"
```

```
"hello".add "world" : String
```

```
#check add true false
```

```
true.add false : Bool
```

```
#check add Nat Nat
```

```
_root_.add Nat Nat : Type
```

We can prevent the shorter alias from being created by using the `protected` keyword:

`protected` 키워드를 사용하여 더 짧은 별칭이 생성되는 것을 방지할 수 있습니다:

```
protected def Foo.bar : Nat := 1
open Foo
/-- error: Unknown identifier `bar` -/
#guard_msgs in
#check bar -- error

#check Foo.bar
```

```
Foo.bar : Nat
```

This is often used for names like `Nat.rec` and `Nat.recOn`, to prevent
overloading of common names.

이는 일반적인 이름의 오버로딩을 방지하기 위해 `Nat.rec`과 `Nat.recOn`과 같은 이름에 자주 사용됩니다.

The `open` command admits variations. The command

`open` 명령은 변형을 허용합니다. 명령어는

```
open Nat (succ zero gcd)
#check zero
```

```
Nat.zero : Nat
```

```
#eval gcd 15 6
```

```
3
```

creates aliases for only the identifiers listed. The command

나열된 식별자에 대해서만 별칭을 생성합니다. 명령어는

```
open Nat hiding succ gcd
#check zero
```

```
Nat.zero : Nat
```

```
/-- error: Unknown identifier `gcd` -/
#guard_msgs in
#eval gcd 15 6  -- error

#eval Nat.gcd 15 6
```

```
3
```

creates aliases for everything in the `Nat` namespace *except* the identifiers listed.

나열된 식별자를 *제외한* `Nat` 네임스페이스의 모든 것에 대해 별칭을 생성합니다.

```
open Nat renaming mul → times, add → plus
#eval plus (times 2 2) 3
```

```
7
```

creates aliases renaming `Nat.mul` to `times` and `Nat.add` to `plus`.

`Nat.mul`을 `times`로, `Nat.add`를 `plus`로 이름을 바꾸는 별칭을 생성합니다.

It is sometimes useful to `export` aliases from one namespace to another, or to the top level. The command

때때로 한 네임스페이스에서 다른 네임스페이스로 또는 최상위 수준으로 별칭을 `export`하는 것이 유용합니다. 명령어는

```
export Nat (succ add sub)
```

creates aliases for `succ`, `add`, and `sub` in the current
namespace, so that whenever the namespace is open, these aliases are
available. If this command is used outside a namespace, the aliases
are exported to the top level.

현재 네임스페이스에서 `succ`, `add`, `sub`에 대한 별칭을 생성하므로 네임스페이스가 열릴 때마다 이 별칭을 사용할 수 있습니다. 이 명령을 네임스페이스 외부에서 사용하면 별칭이 최상위 수준으로 내보내집니다.

## 6.5. Attributes

The main function of Lean is to translate user input to formal
expressions that are checked by the kernel for correctness and then
stored in the environment for later use. But some commands have other
effects on the environment, either assigning attributes to objects in
the environment, defining notation, or declaring instances of type
classes, as described in the chapter on [type classes](../10-type-classes/#type-classes). Most of
these commands have global effects, which is to say, they remain
in effect not only in the current file, but also in any file that
imports it. However, such commands often support the `local` modifier,
which indicates that they only have effect until
the current `section` or `namespace` is closed, or until the end
of the current file.

In [Using the Simplifier](../05-tactics/#using-the-simplifier), we saw that theorems can be annotated with the `[simp]` attribute, which makes them available for use by the simplifier. The following example defines the prefix relation on lists, proves that this relation is reflexive, and assigns the `[simp]` attribute to that theorem.

Lean의 주요 기능은 사용자 입력을 형식적 표현으로 번역하고, 커널에서 정확성을 확인한 후 나중에 사용하기 위해 환경에 저장하는 것입니다. 하지만 일부 명령은 [타입 클래스](../10-type-classes/#type-classes) 장에서 설명하듯이 환경에 대한 다른 효과를 가지며, 환경의 객체에 속성을 할당하거나, 표기법을 정의하거나, 타입 클래스의 인스턴스를 선언합니다. 이러한 명령의 대부분은 전역 효과를 가지고 있습니다. 즉, 현재 파일뿐 아니라 그것을 가져오는 모든 파일에서 유효합니다. 그러나 이러한 명령은 종종 `local` 수정자를 지원하며, 이는 현재 `section` 또는 `namespace`가 닫힐 때까지 또는 현재 파일의 끝까지만 유효함을 나타냅니다.

[단순화기 사용](../05-tactics/#using-the-simplifier)에서 정리는 `[simp]` 속성으로 주석을 달 수 있으며, 이는 단순화기에서 사용할 수 있게 해줍니다. 다음 예제는 목록의 접두사 관계를 정의하고, 이 관계가 반사적임을 증명하며, `[simp]` 속성을 그 정리에 할당합니다.

```
def isPrefix (l₁ : List α) (l₂ : List α) : Prop :=
∃ t, l₁ ++ t = l₂
@[simp] theorem List.isPrefix_self (as : List α) : isPrefix as as :=
⟨[], by simp⟩
example : isPrefix [1, 2, 3] [1, 2, 3] := by
simp
```

The simplifier then proves `isPrefix [1, 2, 3] [1, 2, 3]` by rewriting it to `True`.

그러면 단순화기는 `isPrefix [1, 2, 3] [1, 2, 3]`을 `True`로 다시 쓰는 방식으로 증명합니다.

One can also assign the attribute any time after the definition takes place:

정의가 이루어진 후 언제든지 속성을 할당할 수도 있습니다:

```
theorem List.isPrefix_self (as : List α) : isPrefix as as :=
⟨[], by simp⟩
attribute [simp] List.isPrefix_self
```

In all these cases, the attribute remains in effect in any file that
imports the one in which the declaration occurs. Adding the `local`
modifier restricts the scope:

모든 이 경우에 속성은 선언이 발생하는 파일을 가져오는 모든 파일에서 유효합니다. `local` 수정자를 추가하면 범위가 제한됩니다:

```
section
theorem List.isPrefix_self (as : List α) : isPrefix as as :=
⟨[], by simp⟩
attribute [local simp] List.isPrefix_self
example : isPrefix [1, 2, 3] [1, 2, 3] := by
simp
end
/-- error: `simp` made no progress -/
#guard_msgs in
example : isPrefix [1, 2, 3] [1, 2, 3] := by
simp
```

For another example, we can use the `instance` command to assign the
notation `≤` to the `isPrefix` relation. That command, which will
be explained in the chapter on [type classes](../10-type-classes/#type-classes), works by
assigning an `[instance]` attribute to the associated definition.

또 다른 예로, `instance` 명령을 사용하여 `isPrefix` 관계에 표기법 `≤`을 할당할 수 있습니다. [타입 클래스](../10-type-classes/#type-classes) 장에서 설명할 해당 명령은 연관된 정의에 `[instance]` 속성을 할당함으로써 작동합니다.

```
def isPrefix (l₁ : List α) (l₂ : List α) : Prop :=
∃ t, l₁ ++ t = l₂
instance : LE (List α) where
le := isPrefix
theorem List.isPrefix_self (as : List α) : as ≤ as :=
⟨[], by simp⟩
```

That assignment can also be made local:

```
def instLe : LE (List α) :=
{ le := isPrefix }
section
attribute [local instance] instLe
example (as : List α) : as ≤ as :=
⟨[], by simp⟩
end
/--
error: failed to synthesize
  LE (List α)

Hint: Additional diagnostic information may be available using the
`set_option diagnostics true` command.
-/
#guard_msgs in
example (as : List α) : as ≤ as :=
⟨[], by simp⟩
```

In [Notation](#notation) below, we will discuss Lean's mechanisms for defining notation, and see that they also support the `local` modifier. However, in [Setting Options](#setting-options), we will discuss Lean's mechanisms for setting options, which does *not* follow this pattern: options can *only* be set locally, which is to say, their scope is always restricted to the current section or current file.

## 6.6. More on Implicit Arguments

In [Implicit Arguments](../02-dependent-type-theory/#implicit-arguments), we saw that if Lean displays the type of a term `t` as `{x : α} → β x`, then the curly brackets indicate that `x` has been marked as an *implicit argument* to `t`. This means that whenever you write `t`, a placeholder, or “hole,” is inserted, so that `t` is replaced by `@t _`. If you don't want that to happen, you have to write `@t` instead.

그 할당은 또한 로컬로 만들 수 있습니다:

아래의 [표기법](#notation)에서 Lean의 표기법 정의 메커니즘을 논의하고 `local` 수정자도 지원함을 볼 것입니다. 그러나 [설정 옵션](#setting-options)에서 이 패턴을 따르지 *않는* 옵션 설정을 위한 Lean의 메커니즘을 논의할 것입니다: 옵션은 *오직* 로컬로만 설정될 수 있습니다. 즉, 그것의 범위는 항상 현재 섹션 또는 현재 파일로 제한됩니다.

[묵시적 인수](../02-dependent-type-theory/#implicit-arguments)에서 Lean이 항 `t`의 타입을 `{x : α} → β x`로 표시하면, 중괄호는 `x`가 `t`의 *묵시적 인수*로 표시되었음을 나타냅니다. 이는 `t`를 쓸 때마다 자리표시자 또는 “구멍”이 삽입되어 `t`가 `@t _`로 바뀐다는 의미입니다. 이것이 발생하지 않기를 원하면 대신 `@t`를 써야 합니다.

Notice that implicit arguments are inserted eagerly. Suppose we define
a function `f : (x : Nat) → {y : Nat} → (z : Nat) → Nat`.
Then, when we write the expression `f 7` without further
arguments, it is parsed as `@f 7 _`.

묵시적 인수는 신속하게 삽입됨을 주목하세요. 함수 `f : (x : Nat) → {y : Nat} → (z : Nat) → Nat`을 정의한다고 가정합시다. 그러면 추가 인수 없이 표현식 `f 7`을 쓸 때, 그것은 `@f 7 _`로 구문 분석됩니다.

Lean offers a weaker annotation which specifies that a placeholder should only be added
*before* a subsequent explicit argument. It can be written with double braces, so the type of `f` would be
`f : (x : Nat) → {{y : Nat}} → (z : Nat) → Nat`.
With this annotation, the expression `f 7` would be parsed as is, whereas `f 7 3` would be
parsed as `@f 7 _ 3`, just as it would be with the strong annotation.
This annotation can also be written as `⦃y : Nat⦄`, where the Unicode brackets are entered
as `\{{` and `\}}`, respectively.

Lean은 자리표시자가 후속 명시적 인수 *앞에만* 추가되어야 함을 지정하는 약한 주석을 제공합니다. 이것은 이중 중괄호로 작성할 수 있으므로 `f`의 타입은 `f : (x : Nat) → {{y : Nat}} → (z : Nat) → Nat`이 됩니다. 이 주석을 사용하면 표현식 `f 7`은 그대로 구문 분석되는 반면, `f 7 3`은 강한 주석의 경우처럼 `@f 7 _ 3`으로 구문 분석됩니다. 이 주석은 또한 `⦃y : Nat⦄`로 작성할 수 있으며, 여기서 유니코드 괄호는 각각 `\{{`와 `\}}`로 입력됩니다.

To illustrate the difference, consider the following example, which
shows that a reflexive euclidean relation is both symmetric and
transitive.

차이를 설명하기 위해 반사적 유클리드 관계가 대칭이고 추이적임을 보여주는 다음 예를 고려하세요.

```
def reflexive {α : Type u} (r : α → α → Prop) : Prop :=
∀ (a : α), r a a
def symmetric {α : Type u} (r : α → α → Prop) : Prop :=
∀ {a b : α}, r a b → r b a
def transitive {α : Type u} (r : α → α → Prop) : Prop :=
∀ {a b c : α}, r a b → r b c → r a c
def Euclidean {α : Type u} (r : α → α → Prop) : Prop :=
∀ {a b c : α}, r a b → r a c → r b c
theorem th1 {α : Type u} {r : α → α → Prop}
(reflr : reflexive r) (euclr : Euclidean r)
: symmetric r :=
fun {a b : α} =>
fun (h : r a b) =>
show r b a from euclr h (reflr _)
theorem th2 {α : Type u} {r : α → α → Prop}
(symmr : symmetric r) (euclr : Euclidean r)
: transitive r :=
fun {a b c : α} =>
fun (rab : r a b) (rbc : r b c) =>
euclr (symmr rab) rbc
theorem th3 {α : Type u} {r : α → α → Prop}
(reflr : reflexive r) (euclr : Euclidean r)
: transitive r :=
th2 (th1 reflr @euclr) @euclr
variable (r : α → α → Prop)
variable (euclr : Euclidean r)
#check euclr
```

```
euclr : r ?m.3 ?m.4 → r ?m.3 ?m.5 → r ?m.4 ?m.5
```

The results are broken down into small steps: `th1` shows that a
relation that is reflexive and euclidean is symmetric, and `th2`
shows that a relation that is symmetric and euclidean is
transitive. Then `th3` combines the two results. But notice that we
have to manually disable the implicit arguments in `euclr`, because
otherwise too many implicit arguments are inserted. The problem goes
away if we use weak implicit arguments:

```
def reflexive {α : Type u} (r : α → α → Prop) : Prop :=
∀ (a : α), r a a
def symmetric {α : Type u} (r : α → α → Prop) : Prop :=
∀ {{a b : α}}, r a b → r b a
def transitive {α : Type u} (r : α → α → Prop) : Prop :=
∀ {{a b c : α}}, r a b → r b c → r a c
def Euclidean {α : Type u} (r : α → α → Prop) : Prop :=
∀ {{a b c : α}}, r a b → r a c → r b c
theorem th1 {α : Type u} {r : α → α → Prop}
(reflr : reflexive r) (euclr : Euclidean r)
: symmetric r :=
fun {a b : α} =>
fun (h : r a b) =>
show r b a from euclr h (reflr _)
theorem th2 {α : Type u} {r : α → α → Prop}
(symmr : symmetric r) (euclr : Euclidean r)
: transitive r :=
fun {a b c : α} =>
fun (rab : r a b) (rbc : r b c) =>
euclr (symmr rab) rbc
theorem th3 {α : Type u} {r : α → α → Prop}
(reflr : reflexive r) (euclr : Euclidean r)
: transitive r :=
th2 (th1 reflr euclr) euclr
variable (r : α → α → Prop)
variable (euclr : Euclidean r)
#check euclr
```

```
euclr : Euclidean r
```

There is a third kind of implicit argument that is denoted with square
brackets, `[` and `]`. These are used for type classes, as
explained in the chapter on [type classes](../10-type-classes/#type-classes).

네모 괄호 `[`와 `]`로 표시되는 세 번째 종류의 묵시적 인수가 있습니다. 이들은 [타입 클래스](../10-type-classes/#type-classes) 장에서 설명하듯이 타입 클래스에 사용됩니다.

## 6.7. Notation

Identifiers in Lean can include any alphanumeric characters, including
Greek characters (other than ∀ , Σ , and λ , which, as we have seen,
have a special meaning in the dependent type theory). They can also
include subscripts, which can be entered by typing `\_` followed by
the desired subscripted character.

Lean의 식별자는 ∀, Σ, λ(우리가 본 대로 종속 타입 이론에서 특별한 의미를 가지는 것)를 제외한 그리스 문자를 포함한 모든 영숫자를 포함할 수 있습니다. 또한 `\_`를 입력한 후 원하는 아래 첨자를 입력하여 입력할 수 있는 아래 첨자를 포함할 수 있습니다.

Lean's parser is extensible, which is to say, we can define new notation.

Lean의 파서는 확장 가능합니다. 즉, 우리는 새로운 표기법을 정의할 수 있습니다.

Lean's syntax can be extended and customized by users at every level,
ranging from basic “mixfix” notations to custom elaborators. In fact,
all builtin syntax is parsed and processed using the same mechanisms
and APIs open to users. In this section, we will describe and explain
the various extension points.

Lean의 구문은 기본 “mixfix” 표기법에서 사용자 정의 엘래버레이터까지 모든 수준에서 사용자가 확장하고 사용자 정의할 수 있습니다. 실제로 모든 내장 구문은 사용자에게 열린 같은 메커니즘과 API를 사용하여 구문 분석되고 처리됩니다. 이 섹션에서 우리는 다양한 확장 포인트를 설명하고 설명할 것입니다.

While introducing new notations is a relatively rare feature in
programming languages and sometimes even frowned upon because of its
potential to obscure code, it is an invaluable tool in formalization
for expressing established conventions and notations of the respective
field succinctly in code. Going beyond basic notations, Lean's
ability to factor out common boilerplate code into (well-behaved)
macros and to embed entire custom domain specific languages (DSLs) to
textually encode subproblems efficiently and readably can be of great
benefit to both programmers and proof engineers alike.

새로운 표기법을 도입하는 것은 프로그래밍 언어에서 비교적 드문 기능이며 때로는 코드를 모호하게 할 수 있다는 이유로 눈살을 받지만, 형식화에서 확립된 규칙과 각 분야의 표기법을 간결하게 코드로 표현하기 위한 귀중한 도구입니다. 기본 표기법을 넘어, Lean의 공통 보일러플레이트 코드를 (잘 작동하는) 매크로로 분해하고 전체 사용자 정의 도메인 특정 언어(DSL)를 포함하여 효율적이고 읽기 쉬운 방식으로 부분 문제를 텍스트로 인코딩하는 능력은 프로그래머와 증명 엔지니어 모두에게 큰 도움이 될 수 있습니다.

### 6.7.1. Notations and Precedence

The most basic syntax extension commands allow introducing new (or
overloading existing) prefix, infix, and postfix operators.

가장 기본적인 구문 확장 명령어는 새로운 (또는 기존) 접두사, 중위 및 후위 연산자를 도입할 수 있습니다.

```
infixl:65 " + " => HAdd.hAdd  -- left-associative
infix:50 " = " => Eq         -- non-associative
infixr:80 " ^ " => HPow.hPow  -- right-associative
prefix:100 "-" => Neg.neg
postfix:max "⁻¹" => Inv.inv
```

After the initial command name describing the operator kind (its
“fixity”), we give the *parsing precedence* of the operator preceded
by a colon `:`, then a new or existing token surrounded by double
quotes (the whitespace is used for pretty printing), then the function
this operator should be translated to after the arrow `=>`.

연산자의 종류(“fixity”)를 설명하는 초기 명령 이름 뒤에, 콜론 `:`으로 앞에 붙은 연산자의 *구문 분석 우선순위*를 제공한 다음, 이중 따옴표로 둘러싼 새로운 또는 기존 토큰(공백은 멋진 인쇄에 사용됨)을 제공한 다음, 화살표 `=>` 뒤에 이 연산자를 번역해야 하는 함수를 제공합니다.

The precedence is a natural number describing how “tightly” an
operator binds to its arguments, encoding the order of operations. We
can make this more precise by looking at the commands the above unfold to:

우선순위는 연산자가 인수에 “얼마나 강하게” 결합하는지를 설명하는 자연수이며, 연산 순서를 인코딩합니다. 위의 명령어가 어떻게 확장되는지를 보면 이를 더 정확하게 할 수 있습니다:

```
notation:65 lhs:65 " + " rhs:66 => HAdd.hAdd lhs rhs
notation:50 lhs:51 " = " rhs:51 => Eq lhs rhs
notation:80 lhs:81 " ^ " rhs:80 => HPow.hPow lhs rhs
notation:100 "-" arg:100 => Neg.neg arg
 -- `max` is a shorthand for precedence 1024:
notation:1024 arg:1024 "⁻¹" => Inv.inv arg
```

It turns out that all commands from the first code block are in fact
command *macros* translating to the more general `notation` command.
We will learn about writing such macros below. Instead of a single
token, the `notation` command accepts a mixed sequence of tokens and
named term placeholders with precedences, which can be referenced on
the right-hand side of `=>` and will be replaced by the respective
term parsed at that position. A placeholder with precedence `p`
accepts only notations with precedence at least `p` in that place.
Thus the string `a + b + c` cannot be parsed as the equivalent of
`a + (b + c)` because the right-hand side operand of an `infixl` notation
has precedence one greater than the notation itself. In contrast,
`infixr` reuses the notation's precedence for the right-hand side
operand, so `a ^ b ^ c` *can* be parsed as `a ^ (b ^ c)`. Note that
if we used `notation` directly to introduce an infix notation like

```
notation:65 lhs:65 " ~ " rhs:65 => wobble lhs rhs
```

where the precedences do not sufficiently determine associativity,
Lean's parser will default to right associativity. More precisely,
Lean's parser follows a local *longest parse* rule in the presence of
ambiguous grammars: when parsing the right-hand side of `a ~` in
`a ~ b ~ c`, it will continue parsing as long as possible (as the current
precedence allows), not stopping after `b` but parsing `~ c` as well.
Thus the term is equivalent to `a ~ (b ~ c)`.

첫 번째 코드 블록의 모든 명령어는 실제로 더 일반적인 `notation` 명령어로 번역되는 명령어 *매크로*입니다. 우리는 아래에서 그러한 매크로를 작성하는 방법을 배울 것입니다. `notation` 명령어는 단일 토큰 대신, 토큰과 명명된 항 자리표시자의 혼합 시퀀스와 우선순위를 허용하며, 이는 `=>`의 오른쪽에서 참조될 수 있고 그 위치에서 구문 분석된 각각의 항으로 바뀔 것입니다. 우선순위 `p`를 가진 자리표시자는 그 자리에서 최소한 우선순위 `p`를 가진 표기법만을 허용합니다. 따라서 문자열 `a + b + c`는 `infixl` 표기법의 오른쪽 피연산자가 표기법 자체보다 우선순위가 1 더 크기 때문에 `a + (b + c)`의 동등한 것으로 구문 분석될 수 없습니다. 대조적으로, `infixr`은 오른쪽 피연산자에 대해 표기법의 우선순위를 재사용하므로 `a ^ b ^ c`는 *`a ^ (b ^ c)`*로 구문 분석될 수 있습니다. 중위 표기법을 도입하기 위해 `notation`을 직접 사용하는 경우를 주목하세요:

여기서 우선순위가 연산 방향을 충분히 결정하지 않으면, Lean의 파서는 오른쪽 결합으로 기본 설정됩니다. 더 정확하게, Lean의 파서는 모호한 문법이 있을 때 지역 *최장 구문 분석* 규칙을 따릅니다: `a ~ b ~ c`에서 `a ~`의 오른쪽을 구문 분석할 때, 현재 우선순위가 허용하는 한 계속 구문 분석하며, `b` 뒤에 멈추지 않고 `~ c`도 구문 분석합니다. 따라서 항은 `a ~ (b ~ c)`와 동등합니다.

As mentioned above, the `notation` command allows us to define
arbitrary *mixfix* syntax freely mixing tokens and placeholders.

위에서 언급했듯이, `notation` 명령어는 토큰과 자리표시자를 자유롭게 혼합하는 임의의 *mixfix* 구문을 정의할 수 있게 해줍니다.

```
notation:max "(" e ")" => e
notation:10 Γ " ⊢ " e " : " τ => Typing Γ e τ
```

Placeholders without precedence default to `0`, i.e. they accept notations of any precedence in their place.
If two notations overlap, we again apply the longest parse rule:

우선순위 없는 자리표시자는 기본값 `0`입니다. 즉, 그곳에서 모든 우선순위의 표기법을 허용합니다. 두 표기법이 겹치면, 우리는 다시 최장 구문 분석 규칙을 적용합니다:

```
notation:65 a " + " b:66 " + " c:66 => a + b - c
#eval 1 + 2 + 3
```

```
0
```

The new notation is preferred to the binary notation since the latter,
before chaining, would stop parsing after `1 + 2`. If there are
multiple notations accepting the same longest parse, the choice will
be delayed until elaboration, which will fail unless exactly one
overload is type-correct.

새로운 표기법이 이진 표기법보다 선호되는데, 이는 후자가 연쇄 전에 `1 + 2` 뒤에 구문 분석을 멈추기 때문입니다. 동일한 최장 구문 분석을 수락하는 여러 표기법이 있으면, 선택은 정확히 하나의 오버로드가 타입 정확할 때까지 엘래버레이션까지 지연되며, 그렇지 않으면 실패합니다.

## 6.8. Coercions

In Lean, the type of natural numbers, `Nat`, is different from the
type of integers, `Int`. But there is a function `Int.ofNat` that
embeds the natural numbers in the integers, meaning that we can view
any natural number as an integer, when needed. Lean has mechanisms to
detect and insert *coercions* of this sort. Coercions can be explicitly
requested using the overloaded `↑` operator.

Lean에서 자연수의 타입 `Nat`은 정수의 타입 `Int`과 다릅니다. 하지만 자연수를 정수에 내장하는 함수 `Int.ofNat`이 있으며, 이는 필요할 때 모든 자연수를 정수로 볼 수 있음을 의미합니다. Lean은 이러한 종류의 *강제 변환*을 감지하고 삽입하는 메커니즘을 가지고 있습니다. 강제 변환은 오버로드된 `↑` 연산자를 사용하여 명시적으로 요청할 수 있습니다.

```
variable (m n : Nat)
variable (i j : Int)
#check i + m
```

```
i + ↑m : Int
```

```
#check i + m + j
```

```
i + ↑m + j : Int
```

```
#check i + m + n
```

```
i + ↑m + ↑n : Int
```

## 6.9. Displaying Information

There are a number of ways in which you can query Lean for information
about its current state and the objects and theorems that are
available in the current context. You have already seen two of the
most common ones, `#check` and `#eval`. Remember that `#check`
is often used in conjunction with the `@` operator, which makes all
of the arguments to a theorem or definition explicit. In addition, you
can use the `#print` command to get information about any
identifier. If the identifier denotes a definition or theorem, Lean
prints the type of the symbol, and its definition. If it is a constant
or an axiom, Lean indicates that fact, and shows the type.

Lean에 현재 상태와 현재 문맥에서 사용 가능한 객체와 정리에 대한 정보를 요청할 수 있는 여러 방법이 있습니다. 당신은 이미 가장 일반적인 두 가지인 `#check`과 `#eval`을 보았습니다. `#check`은 정리나 정의의 모든 인수를 명시적으로 만드는 `@` 연산자와 함께 자주 사용됨을 기억하세요. 또한, 모든 식별자에 대한 정보를 얻기 위해 `#print` 명령을 사용할 수 있습니다. 식별자가 정의나 정리를 나타내면, Lean은 기호의 타입과 그 정의를 인쇄합니다. 상수나 공리이면, Lean은 그 사실을 나타내고 타입을 표시합니다.

```
-- examples with equality
#check Eq
```

```
Eq.{u_1} {α : Sort u_1} : α → α → Prop
```

```
#check @Eq
```

```
@Eq : {α : Sort u_1} → α → α → Prop
```

```
#check Eq.symm
```

```
Eq.symm.{u} {α : Sort u} {a b : α} (h : a = b) : b = a
```

```
#check @Eq.symm
```

```
@Eq.symm : ∀ {α : Sort u_1} {a b : α}, a = b → b = a
```

```
#print Eq.symm
```

```
theorem Eq.symm.{u} : ∀ {α : Sort u} {a b : α}, a = b → b = a :=
fun {α} {a b} h => h ▸ rfl
```

```
-- examples with And
#check And
```

```
And (a b : Prop) : Prop
```

```
#check And.intro
```

```
And.intro {a b : Prop} (left : a) (right : b) : a ∧ b
```

```
#check @And.intro
```

```
@And.intro : ∀ {a b : Prop}, a → b → a ∧ b
```

```
-- a user-defined function
def foo {α : Type u} (x : α) : α := x
#check foo
```

```
foo.{u} {α : Type u} (x : α) : α
```

```
#check @foo
```

```
@foo : {α : Type u_1} → α → α
```

```
#print foo
```

```
def foo.{u} : {α : Type u} → α → α :=
fun {α} x => x
```

## 6.10. Setting Options

Lean maintains a number of internal variables that can be set by users
to control its behavior. The syntax for doing so is as follows:

`set_option`` <name> <value>`

Lean은 동작을 제어하기 위해 사용자가 설정할 수 있는 여러 내부 변수를 유지합니다. 이를 수행하기 위한 구문은 다음과 같습니다:

One very useful family of options controls the way Lean's *pretty printer* displays terms. The following options take an input of true or false:

매우 유용한 옵션 패밀리 하나는 Lean의 *멋진 인쇄*가 항을 표시하는 방식을 제어합니다. 다음 옵션은 참 또는 거짓 입력을 가집니다:

As an example, the following settings yield much longer output:

예를 들어, 다음 설정은 훨씬 더 긴 출력을 생성합니다:

```
set_option pp.explicit true
set_option pp.universes true
set_option pp.notation false
#check 2 + 2 = 4
```

```
@Eq.{1} Nat
  (@HAdd.hAdd.{0, 0, 0} Nat Nat Nat (@instHAdd.{0} Nat instAddNat)
    (@OfNat.ofNat.{0} Nat (nat_lit 2) (instOfNatNat (nat_lit 2)))
    (@OfNat.ofNat.{0} Nat (nat_lit 2) (instOfNatNat (nat_lit 2))))
  (@OfNat.ofNat.{0} Nat (nat_lit 4) (instOfNatNat (nat_lit 4))) : Prop
```

```
#reduce (fun x => x + 2) = (fun x => x + 3)
```

```
@Eq.{1} (Nat → Nat)
  (fun x =>
    @HAdd.hAdd.{0, 0, 0} Nat Nat Nat (@instHAdd.{0} Nat instAddNat) x
      (@OfNat.ofNat.{0} Nat (nat_lit 2) (instOfNatNat (nat_lit 2))))
  fun x =>
  @HAdd.hAdd.{0, 0, 0} Nat Nat Nat (@instHAdd.{0} Nat instAddNat) x
    (@OfNat.ofNat.{0} Nat (nat_lit 3) (instOfNatNat (nat_lit 3)))
```

```
#check (fun x => x + 1) 1
```

```
(fun x =>
    @HAdd.hAdd.{0, 0, 0} Nat Nat Nat (@instHAdd.{0} Nat instAddNat) x
      (@OfNat.ofNat.{0} Nat (nat_lit 1) (instOfNatNat (nat_lit 1))))
  (@OfNat.ofNat.{0} Nat (nat_lit 1) (instOfNatNat (nat_lit 1))) : Nat
```

The command `set_option pp.all true` carries out these settings all
at once, whereas `set_option pp.all false` reverts to the previous
values. Pretty printing additional information is often very useful
when you are debugging a proof, or trying to understand a cryptic
error message. Too much information can be overwhelming, though, and
Lean's defaults are generally sufficient for ordinary interactions.

`set_option pp.all true` 명령은 이러한 설정을 모두 한 번에 수행하는 반면, `set_option pp.all false`는 이전 값으로 돌아갑니다. 증명을 디버깅하거나 불명확한 오류 메시지를 이해하려고 할 때 멋진 인쇄 추가 정보는 종종 매우 유용합니다. 하지만 너무 많은 정보는 압도적일 수 있으며, Lean의 기본값은 일반적으로 평소 상호작용에 충분합니다.

## 6.11. Using the Library

To use Lean effectively you will inevitably need to make use of
definitions and theorems in the library. Recall that the `import`
command at the beginning of a file imports previously compiled results
from other files, and that importing is transitive; if you import
`Foo` and `Foo` imports `Bar`, then the definitions and theorems
from `Bar` are available to you as well. But the act of opening a
namespace, which provides shorter names, does not carry over. In each
file, you need to open the namespaces you wish to use.

Lean을 효과적으로 사용하려면 라이브러리의 정의와 정리를 불가피하게 사용해야 합니다. 파일의 시작 부분에서 `import` 명령이 다른 파일에서 이전에 컴파일된 결과를 가져오며, 가져오기가 추이적임을 기억하세요. `Foo`를 가져오고 `Foo`가 `Bar`를 가져오면, `Bar`의 정의와 정리도 당신에게 사용 가능합니다. 하지만 더 짧은 이름을 제공하는 네임스페이스를 열기의 행위는 이월되지 않습니다. 각 파일에서 당신이 사용하고 싶은 네임스페이스를 열어야 합니다.

In general, it is important for you to be familiar with the library
and its contents, so you know what theorems, definitions, notations,
and resources are available to you. Below we will see that Lean's
editor modes can also help you find things you need, but studying the
contents of the library directly is often unavoidable. Lean's standard
library can be found online, on GitHub:

[https://github.com/leanprover/lean4/tree/master/src/Init](https://github.com/leanprover/lean4/tree/master/src/Init)

[https://github.com/leanprover/lean4/tree/master/src/Std](https://github.com/leanprover/lean4/tree/master/src/Std)

일반적으로, 사용 가능한 정리, 정의, 표기법 및 리소스가 무엇인지 알 수 있도록 라이브러리와 그 내용에 익숙해지는 것이 중요합니다. 아래에서 Lean의 편집기 모드가 당신이 필요한 것을 찾는 데도 도움이 될 수 있음을 볼 것이지만, 라이브러리의 내용을 직접 연구하는 것이 종종 불가피합니다. Lean의 표준 라이브러리는 GitHub에서 온라인으로 찾을 수 있습니다:

You can see the contents of these directories and files using GitHub's
browser interface. If you have installed Lean on your own computer,
you can find the library in the `lean` folder, and explore it with
your file manager. Comment headers at the top of each file provide
additional information.

GitHub의 브라우저 인터페이스를 사용하여 이러한 디렉토리와 파일의 내용을 볼 수 있습니다. 당신의 컴퓨터에 Lean을 설치했다면, `lean` 폴더에서 라이브러리를 찾을 수 있으며, 파일 매니저로 탐색할 수 있습니다. 각 파일의 상단에 있는 주석 헤더는 추가 정보를 제공합니다.

Lean's library developers follow general naming guidelines to make it
easier to guess the name of a theorem you need, or to find it using
tab completion in editors with a Lean mode that supports this, which
is discussed in the next section. Identifiers are generally
`camelCase`, and types are `CamelCase`. For theorem names,
we rely on descriptive names where the different components are separated
by `_`s. Often the name of theorem simply describes the conclusion:

Lean의 라이브러리 개발자는 필요한 정리의 이름을 추측하거나 다음 섹션에서 논의하는 Lean 모드를 지원하는 편집기에서 탭 완성을 사용하여 찾기를 더 쉽게 하기 위해 일반적인 명명 지침을 따릅니다. 식별자는 일반적으로 `camelCase`이고, 타입은 `CamelCase`입니다. 정리 이름의 경우, 다양한 구성 요소가 `_`로 분리되는 설명적인 이름에 의존합니다. 종종 정리의 이름은 단순히 결론을 설명합니다:

```
#check Nat.succ_ne_zero
```

```
Nat.succ_ne_zero (n : Nat) : n.succ ≠ 0
```

```
#check Nat.zero_add
```

```
Nat.zero_add (n : Nat) : 0 + n = n
```

```
#check Nat.mul_one
```

```
Nat.mul_one (n : Nat) : n * 1 = n
```

```
#check Nat.le_of_succ_le_succ
```

```
Nat.le_of_succ_le_succ {n m : Nat} : n.succ ≤ m.succ → n ≤ m
```

Remember that identifiers in Lean can be organized into hierarchical
namespaces. For example, the theorem named `le_of_succ_le_succ` in the
namespace `Nat` has full name `Nat.le_of_succ_le_succ`, but the shorter
name is made available by the command `open` `Nat` (for names not marked as
`protected`). We will see in the chapters on [inductive types](../07-inductive-types/#inductive-types)
and [structures and records](../09-structures-and-records/#structures-and-records)
that defining structures and inductive data types in Lean generates
associated operations, and these are stored in
a namespace with the same name as the type under definition. For
example, the product type comes with the following operations:

Lean의 식별자는 계층적 네임스페이스로 구조화될 수 있음을 기억하세요. 예를 들어, 네임스페이스 `Nat`의 `le_of_succ_le_succ`라는 정리는 전체 이름 `Nat.le_of_succ_le_succ`를 가지지만, 더 짧은 이름은 `open` `Nat` 명령에 의해 사용 가능하게 됩니다(`protected`로 표시되지 않은 이름의 경우). [귀납적 타입](../07-inductive-types/#inductive-types)과 [구조와 레코드](../09-structures-and-records/#structures-and-records)에 대한 장에서 Lean에서 구조와 귀납적 데이터 타입을 정의하면 연관된 연산을 생성하고, 이들은 정의 중인 타입과 같은 이름의 네임스페이스에 저장됨을 볼 것입니다. 예를 들어, 곱 타입은 다음 연산을 사용합니다:

```
#check @Prod.mk
```

```
@Prod.mk : {α : Type u_1} → {β : Type u_2} → α → β → α × β
```

```
#check @Prod.fst
```

```
@Prod.fst : {α : Type u_1} → {β : Type u_2} → α × β → α
```

```
#check @Prod.snd
```

```
@Prod.snd : {α : Type u_1} → {β : Type u_2} → α × β → β
```

```
#check @Prod.rec
```

```
@Prod.rec : {α : Type u_2} →
  {β : Type u_3} → {motive : α × β → Sort u_1} → ((fst : α) → (snd : β) → motive (fst, snd)) → (t : α × β) → motive t
```

The first is used to construct a pair, whereas the next two,
`Prod.fst` and `Prod.snd`, project the two elements. The last,
`Prod.rec`, provides another mechanism for defining functions on a
product in terms of a function on the two components. Names like
`Prod.rec` are *protected*, which means that one has to use the full
name even when the `Prod` namespace is open.

첫 번째는 쌍을 구성하는 데 사용되는 반면, 다음 두 개인 `Prod.fst`와 `Prod.snd`는 두 요소를 투영합니다. 마지막인 `Prod.rec`은 두 구성 요소의 함수 측면에서 곱에 대한 함수를 정의하기 위한 또 다른 메커니즘을 제공합니다. `Prod.rec`과 같은 이름은 *protected*이며, 이는 `Prod` 네임스페이스가 열려 있어도 전체 이름을 사용해야 함을 의미합니다.

With the propositions as types correspondence, logical connectives are
also instances of inductive types, and so we tend to use dot notation
for them as well:

제안을 타입 대응으로 사용하면, 논리적 연결자도 귀납적 타입의 인스턴스이므로, 그들을 위해 점 표기법을 사용하는 경향이 있습니다:

```
#check @And.intro
```

```
@And.intro : ∀ {a b : Prop}, a → b → a ∧ b
```

```
#check @And.casesOn
```

```
@And.casesOn : {a b : Prop} →
  {motive : a ∧ b → Sort u_1} → (t : a ∧ b) → ((left : a) → (right : b) → motive ⋯) → motive t
```

```
#check @And.left
```

```
@And.left : ∀ {a b : Prop}, a ∧ b → a
```

```
#check @And.right
```

```
@And.right : ∀ {a b : Prop}, a ∧ b → b
```

```
#check @Or.inl
```

```
@Or.inl : ∀ {a b : Prop}, a → a ∨ b
```

```
#check @Or.inr
```

```
@Or.inr : ∀ {a b : Prop}, b → a ∨ b
```

```
#check @Or.elim
```

```
@Or.elim : ∀ {a b c : Prop}, a ∨ b → (a → c) → (b → c) → c
```

```
#check @Exists.intro
```

```
@Exists.intro : ∀ {α : Sort u_1} {p : α → Prop} (w : α), p w → Exists p
```

```
#check @Exists.elim
```

```
@Exists.elim : ∀ {α : Sort u_1} {p : α → Prop} {b : Prop}, (∃ x, p x) → (∀ (a : α), p a → b) → b
```

```
#check @Eq.refl
```

```
@Eq.refl : ∀ {α : Sort u_1} (a : α), a = a
```

```
#check @Eq.subst
```

```
@Eq.subst : ∀ {α : Sort u_1} {motive : α → Prop} {a b : α}, a = b → motive a → motive b
```

## 6.12. Auto Bound Implicit Arguments

In the previous section, we have shown how implicit arguments make functions more convenient to use.
However, functions such as `compose` are still quite verbose to define. Note that the universe
polymorphic `compose` is even more verbose than the one previously defined.

이전 섹션에서 묵시적 인수가 함수를 더 편리하게 사용하게 하는 방법을 보여 주었습니다. 하지만 `compose`와 같은 함수는 여전히 정의하기에 상당히 장황합니다. 우주 다형적 `compose`는 이전에 정의한 것보다 훨씬 더 장황함을 주목하세요.

```
universe u v w
def compose {α : Type u} {β : Type v} {γ : Type w}
(g : β → γ) (f : α → β) (x : α) : γ :=
g (f x)
```

You can avoid the `universe` command by providing the universe parameters when defining `compose`.

`compose`를 정의할 때 우주 매개 변수를 제공하여 `universe` 명령을 피할 수 있습니다.

```
def compose.{u, v, w}
{α : Type u} {β : Type v} {γ : Type w}
(g : β → γ) (f : α → β) (x : α) : γ :=
g (f x)
```

Lean 4 supports a new feature called *auto bound implicit arguments*. It makes functions such as
`compose` much more convenient to write. When Lean processes the header of a declaration,
any unbound identifier is automatically added as an implicit argument. With this feature we can write `compose` as

Lean 4는 *자동 바운드 묵시적 인수*라는 새로운 기능을 지원합니다. `compose`와 같은 함수를 훨씬 더 편리하게 작성할 수 있게 합니다. Lean이 선언의 헤더를 처리할 때, 바운드되지 않은 모든 식별자가 자동으로 묵시적 인수로 추가됩니다. 이 기능을 사용하면 `compose`를 다음과 같이 쓸 수 있습니다:

```
def compose (g : β → γ) (f : α → β) (x : α) : γ :=
g (f x)
#check @compose
```

```
@compose : {β : Sort u_1} → {γ : Sort u_2} → {α : Sort u_3} → (β → γ) → (α → β) → α → γ
```

Note that Lean inferred a more general type using `Sort` instead of `Type`.

Lean이 `Type` 대신 `Sort`를 사용하여 더 일반적인 타입을 추론했음을 주목하세요.

Although we love this feature and use it extensively when implementing Lean,
we realize some users may feel uncomfortable with it. Thus, you can disable it using
the command `set_option autoImplicit false`.

우리는 이 기능을 좋아하고 Lean을 구현할 때 광범위하게 사용하지만, 일부 사용자는 불편함을 느낄 수 있다는 것을 알고 있습니다. 따라서 `set_option autoImplicit false` 명령을 사용하여 비활성화할 수 있습니다.

```
set_option autoImplicit false
/--
error: Unknown identifier `β`
---
error: Unknown identifier `γ`
---
error: Unknown identifier `α`
---
error: Unknown identifier `β`
---
error: Unknown identifier `α`
---
error: Unknown identifier `γ`
-/
#guard_msgs in
def compose (g : β → γ) (f : α → β) (x : α) : γ :=
g (f x)
```

## 6.13. Implicit Lambdas

When the expected type of an expression is a function that is awaiting implicit
arguments, the elaborator automatically introduces the corresponding lambdas.
For example, `pure`'s type states that the first argument is an implicit type
`α`, but `ReaderT.pure`'s first argument is the reader monad's context type `ρ`.
It is automatically surrounded with a `fun` `{α} => ...`, which allows the elaborator to
correctly fill in the implicit arguments in the body.

표현식의 기대되는 타입이 묵시적 인수를 기다리는 함수일 때, 엘래버레이터는 자동으로 상응하는 람다를 도입합니다. 예를 들어, `pure`의 타입은 첫 번째 인수가 묵시적 타입 `α`임을 명시하지만, `ReaderT.pure`의 첫 번째 인수는 리더 모나드의 컨텍스트 타입 `ρ`입니다. 이것은 자동으로 `fun` `{α} => ...`로 둘러싸여 엘래버레이터가 본문의 묵시적 인수를 올바르게 채울 수 있게 합니다.

```
instance : Monad (ReaderT ρ m) where
pure := ReaderT.pure
bind := ReaderT.bind
```

Users can disable the implicit lambda feature by using `@` or writing
a lambda expression with `{}` or `[]` binder annotations. Here are
few examples

사용자는 `@`를 사용하거나 `{}` 또는 `[]` 바인더 주석이 있는 람다 표현식을 작성하여 묵시적 람다 기능을 비활성화할 수 있습니다. 다음은 몇 가지 예시입니다.

```
def id1 : {α : Type} → α → α :=
fun x => x
def listId : List ({α : Type} → α → α) :=
(fun x => x) :: []
-- In this example, implicit lambda introduction has been disabled because
-- we use `@` before {kw}`fun`
def id2 : {α : Type} → α → α :=
@fun α (x : α) => id1 x
def id3 : {α : Type} → α → α :=
@fun α x => id1 x
def id4 : {α : Type} → α → α :=
fun x => id1 x
-- In this example, implicit lambda introduction has been disabled
-- because we used the binder annotation `{...}`
def id5 : {α : Type} → α → α :=
fun {α} x => id1 x
```

## 6.14. Sugar for Simple Functions

Lean includes a notation for describing simple functions using anonymous
placeholders rather than `fun`. When `·` occurs as part of a term,
the nearest enclosing parentheses become a function with the `·` as its argument.
If the parentheses include multiple placeholders without other intervening parentheses,
then they are made into arguments from left to right. Here are a few examples:

Lean은 `fun` 대신 익명 자리표시자를 사용하여 간단한 함수를 설명하는 표기법을 포함합니다. `·`가 항의 일부로 나타나면, 가장 가까이 둘러싸는 괄호가 `·`를 인수로 하는 함수가 됩니다. 괄호에 다른 중간 괄호 없이 여러 자리표시자가 포함되어 있으면 왼쪽에서 오른쪽으로 인수가 됩니다. 다음은 몇 가지 예시입니다:

```
#check (· + 1)
```

```
fun x => x + 1 : Nat → Nat
```

```
#check (2 - ·)
```

```
fun x => 2 - x : Nat → Nat
```

```
#eval [1, 2, 3, 4, 5].foldl (· * ·) 1
```

```
120
```

```
def f (x y z : Nat) :=
x + y + z
#check (f · 1 ·)
```

```
fun x1 x2 => f x1 1 x2 : Nat → Nat → Nat
```

```
#eval [(1, 2), (3, 4), (5, 6)].map (·.1)
```

```
[1, 3, 5]
```

Nested parentheses introduce new functions. In the following example, two different lambda expressions are created:

중첩된 괄호는 새로운 함수를 도입합니다. 다음 예시에서는 두 개의 서로 다른 람다 표현식이 생성됩니다:

```
#check (Prod.mk · (· + 1))
```

```
fun x => (x, fun x => x + 1) : ?m.1 → ?m.1 × (Nat → Nat)
```

## 6.15. Named Arguments

Named arguments enable you to specify an argument for a parameter by
matching the argument with its name rather than with its position in
the parameter list. If you don't remember the order of the parameters
but know their names, you can send the arguments in any order. You may
also provide the value for an implicit parameter when Lean failed to
infer it. Named arguments also improve the readability of your code by
identifying what each argument represents.

명명된 인수를 사용하면 매개변수 목록의 위치가 아니라 이름과 인수를 일치시켜 매개변수에 대한 인수를 지정할 수 있습니다. 매개변수의 순서가 기억나지 않지만 이름을 알고 있다면 어떤 순서로든 인수를 보낼 수 있습니다. 또한 Lean이 추론하는 데 실패했을 때 묵시적 매개변수의 값을 제공할 수도 있습니다. 명명된 인수는 각 인수가 무엇을 나타내는지 식별함으로써 코드의 가독성을 높여줍니다.

```
def sum (xs : List Nat) :=
xs.foldl (init := 0) (·+·)
#eval sum [1, 2, 3, 4]
```

```
10
```

```
-- 10

example {a b : Nat} {p : Nat → Nat → Nat → Prop}
(h₁ : p a b b) (h₂ : b = a) :
p a a b :=
Eq.subst (motive := fun x => p a x b) h₂ h₁
```

In the following examples, we illustrate the interaction between named
and default arguments.

다음 예시에서는 명명된 인수와 기본 인수 사이의 상호 작용을 설명합니다.

```
def f (x : Nat) (y : Nat := 1) (w : Nat := 2) (z : Nat) :=
x + y + w - z
example (x z : Nat) : f (z := z) x = x + 1 + 2 - z := rfl
example (x z : Nat) : f x (z := z) = x + 1 + 2 - z := rfl
example (x y : Nat) : f x y = fun z => x + y + 2 - z := rfl
example : f = (fun x z => x + 1 + 2 - z) := rfl
example (x : Nat) : f x = fun z => x + 1 + 2 - z := rfl
example (y : Nat) : f (y := 5) = fun x z => x + 5 + 2 - z := rfl
def g {α} [Add α] (a : α) (b? : Option α := none) (c : α) : α :=
match b? with
| none => a + c
| some b => a + b + c
variable {α} [Add α]
example : g = fun (a c : α) => a + c := rfl
example (x : α) : g (c := x) = fun (a : α) => a + x := rfl
example (x : α) : g (b? := some x) = fun (a c : α) => a + x + c := rfl
example (x : α) : g x = fun (c : α) => x + c := rfl
example (x y : α) : g x y = fun (c : α) => x + y + c := rfl
```

You can use `..` to provide missing explicit arguments as `_`.
This feature combined with named arguments is useful for writing patterns. Here is an example:

`..`를 사용하여 누락된 명시적 인수를 `_`로 제공할 수 있습니다. 이 기능은 명명된 인수와 결합하여 패턴을 작성할 때 유용합니다. 다음은 예시입니다:

```
inductive Term where
| var (name : String)
| num (val : Nat)
| app (fn : Term) (arg : Term)
| lambda (name : String) (type : Term) (body : Term)
def getBinderName : Term → Option String
| Term.lambda (name := n) .. => some n
| _ => none
def getBinderType : Term → Option Term
| Term.lambda (type := t) .. => some t
| _ => none
```

Ellipses are also useful when explicit arguments can be automatically
inferred by Lean, and we want to avoid a sequence of `_`s.

```
example (f : Nat → Nat) (a b c : Nat) : f (a + b + c) = f (a + (b + c)) :=
congrArg f (Nat.add_assoc ..)
```

생략 기호는 명시적 인수가 Lean에 의해 자동으로 추론될 수 있고, `_`의 나열을 피하고 싶을 때 유용합니다.
