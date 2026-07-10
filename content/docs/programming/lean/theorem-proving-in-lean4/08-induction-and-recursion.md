---
title: "8. 귀납과 재귀"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "theorem-proving", "type-theory"]
categories: ["programming"]
description: "패턴 매칭 컴파일, 구조적/정초 재귀, 종료성 증명 방법을 다룹니다."
---

In the previous chapter, we saw that inductive definitions provide a
powerful means of introducing new types in Lean. Moreover, the
constructors and the recursors provide the only means of defining
functions on these types. By the [propositions-as-types](../03-propositions-and-proofs/#--tech-term-propositions-as-types) correspondence,
this means that induction is the fundamental method of proof.

이전 장에서 우리는 귀납적 정의가 Lean에서 새로운 타입을 도입하는 강력한 수단을 제공한다는 것을 보았습니다. 더욱이, 생성자와 재귀자(recursor)는 이러한 타입에 대한 함수를 정의하는 유일한 수단을 제공합니다. [명제-타입 대응(propositions-as-types)](../03-propositions-and-proofs/#--tech-term-propositions-as-types)에 의해, 이것은 귀납이 증명의 기본 방법이라는 것을 의미합니다.

Lean provides natural ways of defining recursive functions, performing
pattern matching, and writing inductive proofs. It allows you to
define a function by specifying equations that it should satisfy, and
it allows you to prove a theorem by specifying how to handle various
cases that can arise. Behind the scenes, these descriptions are
“compiled” down to primitive recursors, using a procedure that we
refer to as the “equation compiler.” The equation compiler is not part
of the trusted code base; its output consists of terms that are
checked independently by the kernel.

Lean은 재귀 함수를 정의하고, 패턴 매칭을 수행하고, 귀납적 증명을 작성하는 자연스러운 방법을 제공합니다. 함수가 만족해야 할 방정식을 지정하여 함수를 정의할 수 있으며, 발생할 수 있는 다양한 경우를 처리하는 방법을 지정하여 정리를 증명할 수 있습니다. 백그라운드에서, 이러한 설명들은 우리가 “방정식 컴파일러(equation compiler)”라고 부르는 절차를 사용하여 원시 재귀자로 “컴파일”됩니다. 방정식 컴파일러는 신뢰된 코드 기반의 일부가 아니며, 그 출력은 커널에 의해 독립적으로 확인되는 항들로 구성됩니다.

## 8.1. Pattern Matching

The interpretation of schematic patterns is the first step of the
compilation process. We have seen that the `casesOn` recursor can
be used to define functions and prove theorems by cases, according to
the constructors involved in an inductively defined type. But
complicated definitions may use several nested `casesOn`
applications, and may be hard to read and understand. Pattern matching
provides an approach that is more convenient, and familiar to users of
functional programming languages.

도식적 패턴의 해석은 컴파일 과정의 첫 번째 단계입니다. 우리는 `casesOn` 재귀자를 사용하여 귀납적으로 정의된 타입에 포함된 생성자에 따라 경우별로 함수를 정의하고 정리를 증명할 수 있다는 것을 보았습니다. 하지만 복잡한 정의는 여러 개의 중첩된 `casesOn` 적용을 사용할 수 있으며, 읽고 이해하기 어려울 수 있습니다. 패턴 매칭은 더 편리하고 함수형 프로그래밍 언어 사용자들에게 익숙한 접근 방식을 제공합니다.

Consider the inductively defined type of natural numbers. Every
natural number is either `zero` or `succ x`, and so you can define
a function from the natural numbers to an arbitrary type by specifying
a value in each of those cases:

자연수의 귀납적으로 정의된 타입을 생각해봅시다. 모든 자연수는 `zero` 또는 `succ x` 중 하나이므로, 각각의 경우에 값을 지정하여 자연수에서 임의의 타입으로의 함수를 정의할 수 있습니다:

```
open Nat
def sub1 : Nat → Nat
| zero => zero
| succ x => x
def isZero : Nat → Bool
| zero => true
| succ x => false
```

The equations used to define these functions hold definitionally:

이러한 함수를 정의하는 데 사용되는 방정식들은 정의상(definitionally) 성립합니다:

```
example : sub1 0 = 0 := rfl
example (x : Nat) : sub1 (succ x) = x := rfl
example : isZero 0 = true := rfl
example (x : Nat) : isZero (succ x) = false := rfl
example : sub1 7 = 6 := rfl
example (x : Nat) : isZero (x + 3) = false := rfl
```

Instead of `zero` and `succ`, we can use more familiar notation:

`zero`과 `succ` 대신에 우리는 더 친숙한 표기법을 사용할 수 있습니다:

```
def sub1 : Nat → Nat
| 0 => 0
| x + 1 => x
def isZero : Nat → Bool
| 0 => true
| x + 1 => false
```

Because addition and the zero notation have been assigned the
`[match_pattern]` attribute, they can be used in pattern matching. Lean
simply normalizes these expressions until the constructors `zero`
and `succ` are exposed.

덧셈과 영(zero) 표기법이 `[match_pattern]` 속성을 할당받았기 때문에, 패턴 매칭에서 사용될 수 있습니다. Lean은 단순히 생성자 `zero`와 `succ`이 노출될 때까지 이러한 표현들을 정규화합니다.

Pattern matching works with any inductive type, such as products and option types:

패턴 매칭은 곱(product)과 옵션 타입과 같은 모든 귀납적 타입에서 작동합니다:

```
def swap : α × β → β × α
| (a, b) => (b, a)
def foo : Nat × Nat → Nat
| (m, n) => m + n
def bar : Option Nat → Nat
| some n => n + 1
| none => 0
```

Here we use it not only to define a function, but also to carry out a
proof by cases:

여기서 우리는 함수를 정의할 뿐만 아니라 경우별 증명을 수행하기 위해 이를 사용합니다:

```
def not : Bool → Bool
| true => false
| false => true
theorem not_not : ∀ (b : Bool), not (not b) = b
| true => show not (not true) = true from rfl
| false => show not (not false) = false from rfl
```

Pattern matching can also be used to destruct inductively defined propositions:

패턴 매칭은 또한 귀납적으로 정의된 명제를 분해하는 데 사용될 수 있습니다:

```
example (p q : Prop) : p ∧ q → q ∧ p
| And.intro h₁ h₂ => And.intro h₂ h₁
example (p q : Prop) : p ∨ q → q ∨ p
| Or.inl hp => Or.inr hp
| Or.inr hq => Or.inl hq
```

This provides a compact way of unpacking hypotheses that make use of logical connectives.

이것은 논리적 연결자를 사용하는 가설을 풀어내는 간단한 방법을 제공합니다.

In all these examples, pattern matching was used to carry out a single
case distinction. More interestingly, patterns can involve nested
constructors, as in the following examples.

이러한 모든 예제에서 패턴 매칭은 단일 경우 구분을 수행하는 데 사용되었습니다. 더 흥미롭게도, 패턴은 다음 예제와 같이 중첩된 생성자를 포함할 수 있습니다.

```
def sub2 : Nat → Nat
| 0 => 0
| 1 => 0
| x + 2 => x
```

The equation compiler first splits on cases as to whether the input is
`zero` or of the form `succ x`. It then does a case split on
whether `x` is of the form `zero` or `succ x`. It determines
the necessary case splits from the patterns that are presented to it,
and raises an error if the patterns fail to exhaust the cases. Once
again, we can use arithmetic notation, as in the version below. In
either case, the defining equations hold definitionally.

```
example : sub2 0 = 0 := rfl
example : sub2 1 = 0 := rfl
example : sub2 (x+2) = x := rfl
example : sub2 5 = 3 := rfl
```

You can write `#print sub2` to see how the function was compiled to recursors. (Lean will tell you that `sub2` has been defined in terms of an internal auxiliary function, `sub2.match_1`, but you can print that out too.) Lean uses these auxiliary functions to compile `match` expressions. Actually, the definition above is expanded to

방정식 컴파일러는 먼저 입력이 `zero`인지 또는 `succ x` 형태인지에 따라 경우를 분할합니다. 그 다음 `x`가 `zero` 형태인지 또는 `succ x` 형태인지에 따라 경우 분할을 수행합니다. 제시되는 패턴으로부터 필요한 경우 분할을 결정하며, 패턴이 모든 경우를 다루지 않으면 오류를 발생시킵니다. 다시 한 번, 아래 버전처럼 산술 표기법을 사용할 수 있습니다. 어느 경우든, 정의하는 방정식들은 정의상 성립합니다.

| x.succ.succ => x#print sub2`를 작성하여 함수가 재귀자로 어떻게 컴파일되었는지 볼 수 있습니다. (Lean은 `sub2`가 내부 보조 함수 `sub2.match_1`의 관점에서 정의되었다고 알려줄 것이지만, 당신은 그것도 출력할 수 있습니다.) Lean은 이러한 보조 함수들을 사용하여 `match` 식을 컴파일합니다. 실제로, 위의 정의는 다음과 같이 확장됩니다

```
def sub2 : Nat → Nat :=
fun x =>
match x with
| 0 => 0
| 1 => 0
| x + 2 => x
```

Here are some more examples of nested pattern matching:

중첩된 패턴 매칭의 더 많은 예제들이 여기에 있습니다:

```
example (p q : α → Prop) :
(∃ x, p x ∨ q x) →
(∃ x, p x) ∨ (∃ x, q x)
| Exists.intro x (Or.inl px) => Or.inl (Exists.intro x px)
| Exists.intro x (Or.inr qx) => Or.inr (Exists.intro x qx)
def foo : Nat × Nat → Nat
| (0, n) => 0
| (m+1, 0) => 1
| (m+1, n+1) => 2
```

The equation compiler can process multiple arguments sequentially. For
example, it would be more natural to define the previous example as a
function of two arguments:

방정식 컴파일러는 여러 인수를 순차적으로 처리할 수 있습니다. 예를 들어, 이전 예제를 두 개의 인수의 함수로 정의하는 것이 더 자연스러울 것입니다:

```
def foo : Nat → Nat → Nat
| 0, n => 0
| m + 1, 0 => 1
| m + 1, n + 1 => 2
```

Here is another example:

```
def bar : List Nat → List Nat → Nat
| [], [] => 0
| a :: as, [] => a
| [], b :: bs => b
| a :: as, b :: bs => a + b
```

Note that the patterns are separated by commas.

패턴이 쉼표로 분리되어 있음을 주목하세요.

In each of the following examples, splitting occurs on only the first
argument, even though the others are included among the list of
patterns.

다음의 각 예제에서, 다른 것들이 패턴 목록에 포함되어 있음에도 불구하고 분할은 첫 번째 인수에서만 발생합니다.

```
def and : Bool → Bool → Bool
| true, a => a
| false, _ => false
def or : Bool → Bool → Bool
| true, _ => true
| false, a => a
def cond : Bool → α → α → α
| true, x, y => x
| false, x, y => y
```

Notice also that, when the value of an argument is not needed in the
definition, you can use an underscore instead. This underscore is
known as a *wildcard pattern*, or an *anonymous variable*. In contrast
to usage outside the equation compiler, here the underscore does *not*
indicate an implicit argument. The use of underscores for wildcards is
common in functional programming languages, and so Lean adopts that
notation. The section on [wildcards and overlapping patterns](#wildcards-and-overlapping-patterns)
expands on the notion of a wildcard, and the description of [inaccessible patterns](#inaccessible-patterns) explains how
you can use implicit arguments in patterns as well.

As described in [Inductive Types](../07-inductive-types/#inductive-types), inductive data types can depend on parameters. The following example defines the `tail` function using pattern matching. The argument `α : Type u` is a parameter and occurs before the colon to indicate it does not participate in the pattern matching. Lean also allows parameters to occur after the `:`, but pattern matching on them requires an explicit `match`.

또한 인수의 값이 정의에서 필요하지 않을 때, 대신 언더스코어를 사용할 수 있습니다. 이 언더스코어는 *와일드카드 패턴(wildcard pattern)* 또는 *익명 변수(anonymous variable)*로 알려져 있습니다. 방정식 컴파일러 외부의 사용과 달리, 여기서 언더스코어는 암시적 인수를 나타내지 *않습니다*. 와일드카드에 언더스코어를 사용하는 것은 함수형 프로그래밍 언어에서 일반적이므로, Lean도 이 표기법을 채택합니다. [와일드카드와 겹치는 패턴(wildcards and overlapping patterns)](#wildcards-and-overlapping-patterns) 섹션에서 와일드카드의 개념을 확장하며, [접근 불가능한 패턴(inaccessible patterns)](#inaccessible-patterns)의 설명은 패턴에서 암시적 인수를 사용하는 방법을 설명합니다.

[귀납적 타입(Inductive Types)](../07-inductive-types/#inductive-types)에서 설명된 대로, 귀납적 데이터 타입은 매개변수에 의존할 수 있습니다. 다음 예제는 패턴 매칭을 사용하여 `tail` 함수를 정의합니다. 인수 `α : Type u`는 매개변수이며 패턴 매칭에 참여하지 않음을 나타내기 위해 콜론 앞에 나타납니다. Lean은 또한 매개변수가 `:`의 다음에 나타나도록 허용하지만, 이에 대한 패턴 매칭은 명시적인 `match`를 요구합니다.

```
def tail1 {α : Type u} : List α → List α
| [] => []
| a :: as => as
def tail2 : {α : Type u} → List α → List α
| α, [] => []
| α, a :: as => as
```

Despite the different placement of the parameter `α` in these two
examples, in both cases it is treated in the same way, in that it does
not participate in a case split.

이 두 예제에서 매개변수 `α`의 위치가 다르지만, 두 경우 모두 동일한 방식으로 처리되며, 경우 분할에 참여하지 않습니다.

Lean can also handle more complex forms of pattern matching, in which
arguments to dependent types pose additional constraints on the
various cases. Such examples of *dependent pattern matching* are
considered in the section on [dependent pattern matching](#dependent-pattern-matching).

Lean은 또한 더 복잡한 형태의 패턴 매칭을 처리할 수 있으며, 여기서 의존 타입의 인수가 다양한 경우에 추가 제약을 부과합니다. 이러한 *의존 패턴 매칭(dependent pattern matching)*의 예제들은 [의존 패턴 매칭(dependent pattern matching)](#dependent-pattern-matching) 섹션에서 고려됩니다.

## 8.2. Wildcards and Overlapping Patterns

Consider one of the examples from the last section:

마지막 섹션의 예제 중 하나를 생각해봅시다:

```
def foo : Nat → Nat → Nat
| 0, n => 0
| m + 1, 0 => 1
| m + 1, n + 1 => 2
```

An alternative presentation is:

대체 표현은 다음과 같습니다:

```
def foo : Nat → Nat → Nat
| 0, n => 0
| m, 0 => 1
| m, n => 2
```

In the second presentation, the patterns overlap; for example, the
pair of arguments `0, 0` matches all three cases. But Lean handles
the ambiguity by using the first applicable equation, so in this example
the net result is the same. In particular, the following equations hold
definitionally:

두 번째 표현에서, 패턴은 겹칩니다. 예를 들어, 인수 쌍 `0, 0`은 세 경우 모두와 일치합니다. 하지만 Lean은 적용 가능한 첫 번째 방정식을 사용하여 모호성을 처리하므로, 이 예제에서 최종 결과는 동일합니다. 특히, 다음 방정식들이 정의상 성립합니다:

```
example : foo 0 0 = 0 := rfl
example : foo 0 (n + 1) = 0 := rfl
example : foo (m + 1) 0 = 1 := rfl
example : foo (m + 1) (n + 1) = 2 := rfl
```

Since the values of `m` and `n` are not needed, we can just as well use wildcard patterns instead.

`m`과 `n`의 값이 필요하지 않으므로, 대신 와일드카드 패턴을 사용할 수 있습니다.

```
def foo : Nat → Nat → Nat
| 0, _ => 0
| _, 0 => 1
| _, _ => 2
```

You can check that this definition of `foo` satisfies the same
definitional identities as before.

이 `foo` 정의가 이전과 동일한 정의상 항등식을 만족하는지 확인할 수 있습니다.

Some functional programming languages support *incomplete
patterns*. In these languages, the interpreter produces an exception
or returns an arbitrary value for incomplete cases. We can simulate
the arbitrary value approach using the `Inhabited` type
class. Roughly, an element of `Inhabited α` is a witness to the fact
that there is an element of `α`; in [the chapter on type classes](../10-type-classes/#type-classes)
we will see that Lean can be instructed that suitable
base types are inhabited, and can automatically infer that other
constructed types are inhabited. On this basis, the
standard library provides a default element, `default`, of
any inhabited type.

일부 함수형 프로그래밍 언어는 *불완전한 패턴(incomplete patterns)*을 지원합니다. 이러한 언어에서는 인터프리터가 불완전한 경우에 대해 예외를 발생시키거나 임의의 값을 반환합니다. 우리는 `Inhabited` 타입 클래스를 사용하여 임의의 값 접근 방식을 시뮬레이션할 수 있습니다. 대략적으로, `Inhabited α`의 요소는 `α`의 요소가 존재한다는 사실에 대한 증거입니다. [타입 클래스 장](../10-type-classes/#type-classes)에서 우리는 적절한 기본 타입이 inhabited(공집합이 아닌)하다고 Lean에 지시할 수 있으며, 다른 구성된 타입이 inhabited함을 자동으로 추론할 수 있음을 볼 것입니다. 이를 바탕으로, 표준 라이브러리는 임의의 inhabited 타입의 기본 요소인 `default`를 제공합니다.

We can also use the type `Option α` to simulate incomplete patterns.
The idea is to return `some a` for the provided patterns, and use
`none` for the incomplete cases. The following example demonstrates
both approaches.

우리는 또한 `Option α` 타입을 사용하여 불완전한 패턴을 시뮬레이션할 수 있습니다. 제공된 패턴에 대해 `some a`를 반환하고, 불완전한 경우에 `none`을 사용하는 것이 아이디어입니다. 다음 예제는 두 접근 방식을 모두 보여줍니다.

```
def f1 : Nat → Nat → Nat
| 0, _ => 1
| _, 0 => 2
| _, _ => default  -- the "incomplete" case

example : f1 0 0 = 1 := rfl
example : f1 0 (a+1) = 1 := rfl
example : f1 (a+1) 0 = 2 := rfl
example : f1 (a+1) (b+1) = default := rfl
def f2 : Nat → Nat → Option Nat
| 0, _ => some 1
| _, 0 => some 2
| _, _ => none     -- the "incomplete" case

example : f2 0 0 = some 1 := rfl
example : f2 0 (a+1) = some 1 := rfl
example : f2 (a+1) 0 = some 2 := rfl
example : f2 (a+1) (b+1) = none := rfl
```

The equation compiler is clever. If you leave out any of the cases in
the following definition, the error message will let you know what has
not been covered.

```
def bar : Nat → List Nat → Bool → Nat
| 0, _, false => 0
| 0, b :: _, _ => b
| 0, [], true => 7
| a+1, [], false => a
| a+1, [], true => a + 1
| a+1, b :: _, _ => a + b
```

It will also use an `if`` ... ``then`` ... ``else` instead of a `casesOn` in appropriate situations.

방정식 컴파일러는 영리합니다. 다음 정의에서 경우를 생략하면, 오류 메시지가 다루지 않은 것이 무엇인지 알려줄 것입니다.

또한 적절한 상황에서 `casesOn` 대신에 `if` `...` `then` `...` `else`를 사용할 것입니다.

```
def foo : Char → Nat
| 'A' => 1
| 'B' => 2
| _ => 3
#print foo.match_1
```

```
def foo.match_1.{u_1} : (motive : Char → Sort u_1) →
  (x : Char) → (Unit → motive 'A') → (Unit → motive 'B') → ((x : Char) → motive x) → motive x :=
fun motive x h_1 h_2 h_3 =>
  if h_1_1 : x = 'A' then Eq.symm h_1_1 ▸ Eq.symm h_1_1 ▸ h_1 ()
  else
    if h_2_1 : x = 'B' then
      Eq.ndrec (motive := fun x => ¬x = 'A' → motive x) (fun h_1 => Eq.symm h_2_1 ▸ h_2 ()) (Eq.symm h_2_1) h_1_1
    else h_3 x
```

## 8.3. Structural Recursion and Induction

What makes the equation compiler powerful is that it also supports
recursive definitions. In the next three sections, we will describe,
respectively:

* structurally recursive definitions
* well-founded recursive definitions
* mutually recursive definitions

방정식 컴파일러를 강력하게 만드는 것은 또한 재귀 정의를 지원한다는 것입니다. 다음 세 섹션에서 우리는 각각 다음을 설명할 것입니다:

* 구조적으로 재귀적인 정의(structurally recursive definitions)
* 기반이 있는(well-founded) 재귀 정의(well-founded recursive definitions)
* 상호 재귀 정의(mutually recursive definitions)

Generally speaking, the equation compiler processes input of the following form:

Here `(a : α)` is a sequence of parameters, `(b : β)` is the
sequence of arguments on which pattern matching takes place, and `γ`
is any type, which can depend on `a` and `b`. Each line should
contain the same number of patterns, one for each element of `β`. As we
have seen, a pattern is either a variable, a constructor applied to
other patterns, or an expression that normalizes to something of that
form (where the non-constructors are marked with the `[match_pattern]`
attribute). The appearances of constructors prompt case splits, with
the arguments to the constructors represented by the given
variables. In the section on [dependent pattern matching](#dependent-pattern-matching),
we will see that some explicit terms in patterns are forced into a particular form
in order to make an expression type check, though they do not play a
role in pattern matching. These are called “inaccessible patterns” for
that reason. But we will not need to use such inaccessible patterns
before covering [dependent pattern matching](#dependent-pattern-matching).

여기서 `(a : α)`는 매개변수의 수열이고, `(b : β)`는 패턴 매칭이 발생하는 인수의 수열이며, `γ`는 `a`와 `b`에 의존할 수 있는 모든 타입입니다. 각 줄은 `β`의 각 요소에 대해 하나씩 같은 수의 패턴을 포함해야 합니다. 우리가 본 것처럼, 패턴은 변수, 다른 패턴에 적용된 생성자, 또는 그 형태로 정규화되는 표현식입니다 (비생성자는 `[match_pattern]` 속성으로 표시됨). 생성자의 출현은 경우 분할을 유발하며, 생성자의 인수는 주어진 변수로 표현됩니다. [의존 패턴 매칭(dependent pattern matching)](#dependent-pattern-matching) 섹션에서, 우리는 패턴의 일부 명시적 항이 표현식 타입 체크를 하기 위해 특정 형태로 강제되지만 패턴 매칭에서 역할을 하지 않는다는 것을 볼 것입니다. 이것을 “접근 불가능한 패턴(inaccessible patterns)”이라고 부릅니다. 하지만 [의존 패턴 매칭(dependent pattern matching)](#dependent-pattern-matching)을 다루기 전에는 그러한 접근 불가능한 패턴을 사용할 필요가 없습니다.

As we saw in the last section, the terms `t₁, ..., tₙ` can make use
of any of the parameters `a`, as well as any of the variables that
are introduced in the corresponding patterns. What makes recursion and
induction possible is that they can also involve recursive calls to
`foo`. In this section, we will deal with *structural recursion*, in
which the arguments to `foo` occurring on the right-hand side of the
`=>` are subterms of the patterns on the left-hand side. The idea is
that they are structurally smaller, and hence appear in the inductive
type at an earlier stage. Here are some examples of structural
recursion from the last chapter, now defined using the equation
compiler:

우리가 마지막 섹션에서 본 것처럼, 항 `t₁, ..., tₙ`은 매개변수 `a` 중 어느 것이든, 그리고 해당 패턴에서 도입되는 변수들을 사용할 수 있습니다. 재귀와 귀납이 가능하게 하는 것은 또한 `foo`에 대한 재귀 호출을 포함할 수 있다는 것입니다. 이 섹션에서 우리는 *구조적 재귀(structural recursion)*를 다룰 것인데, 여기서 `=>`의 우측에서 나타나는 `foo`의 인수들은 좌측 패턴의 부분항(subterm)입니다. 아이디어는 이들이 구조적으로 더 작으며, 따라서 귀납 타입에서 더 이른 단계에 나타난다는 것입니다. 다음은 마지막 장의 구조적 재귀의 일부 예제이며, 이제 방정식 컴파일러를 사용하여 정의됩니다:

```
open Nat
def add : Nat → Nat → Nat
| m, zero => m
| m, succ n => succ (add m n)
theorem add_zero (m : Nat) : add m zero = m := rfl
theorem add_succ (m n : Nat) : add m (succ n) = succ (add m n) := rfl
theorem zero_add : ∀ n, add zero n = n
| zero => rfl
| succ n => congrArg succ (zero_add n)
def mul : Nat → Nat → Nat
| n, zero => zero
| n, succ m => add (mul n m) n
```

The proof of `zero_add` makes it clear that proof by induction is
really a form of recursion in Lean.

`zero_add`의 증명은 귀납에 의한 증명이 정말로 Lean에서 재귀의 한 형태임을 명확히 합니다.

The example above shows that the defining equations for `add` hold
definitionally, and the same is true of `mul`. The equation compiler
tries to ensure that this holds whenever possible, as is the case with
straightforward structural induction. In other situations, however,
reductions hold only *propositionally*, which is to say, they are
equational theorems that must be applied explicitly. The equation
compiler generates such theorems internally. They are not meant to be
used directly by the user; rather, the `simp` tactic
is configured to use them when necessary. The following
proof of `zero_add` works this way:

위의 예제는 `add`에 대한 정의하는 방정식들이 정의상 성립하며, `mul`도 마찬가지임을 보여줍니다. 방정식 컴파일러는 이것이 가능할 때마다 성립하도록 하려고 노력하며, 직선적인 구조적 귀납의 경우가 그렇습니다. 다른 상황에서는, 그러나, 축약(reductions)은 오직 *명제적으로(propositionally)* 성립하며, 즉, 명시적으로 적용해야 하는 등식 정리입니다. 방정식 컴파일러는 그러한 정리들을 내부적으로 생성합니다. 이들은 사용자가 직접 사용하려는 것이 아닙니다. 오히려 `simp` 전술이 필요할 때 사용하도록 구성됩니다. 다음 `zero_add` 증명은 이런 식으로 작동합니다:

```
theorem zero_add : ∀ n, add zero n = n
| zero => by simp [add]
| succ n => by simp [add, zero_add]
```

As with definition by pattern matching, parameters to a structural
recursion or induction may appear before the colon. Such parameters
are simply added to the local context before the definition is
processed. For example, the definition of addition may also be written
as follows:

패턴 매칭에 의한 정의와 마찬가지로, 구조적 재귀 또는 귀납의 매개변수는 콜론 앞에 나타날 수 있습니다. 그러한 매개변수들은 정의가 처리되기 전에 단순히 지역 컨텍스트에 추가됩니다. 예를 들어, 덧셈의 정의는 다음과 같이 쓸 수도 있습니다:

```
open Nat
def add (m : Nat) : Nat → Nat
| zero => m
| succ n => succ (add m n)
```

You can also write the example above using `match`.

`match`를 사용하여 위의 예제를 쓸 수도 있습니다.

```
open Nat
def add (m n : Nat) : Nat :=
match n with
| zero => m
| succ n => succ (add m n)
```

A more interesting example of structural recursion is given by the Fibonacci function `fib`.

구조적 재귀의 더 흥미로운 예제는 피보나치 함수 `fib`에 의해 주어집니다.

```
def fib : Nat → Nat
| 0 => 1
| 1 => 1
| n+2 => fib (n+1) + fib n
example : fib 0 = 1 := rfl
example : fib 1 = 1 := rfl
example : fib (n + 2) = fib (n + 1) + fib n := rfl
example : fib 7 = 21 := rfl
```

Here, the value of the `fib` function at `n + 2` (which is
definitionally equal to `succ (succ n)`) is defined in terms of the
values at `n + 1` (which is definitionally equivalent to `succ n`)
and the value at `n`. This is a notoriously inefficient way of
computing the Fibonacci function, however, with an execution time that
is exponential in `n`. Here is a better way:

여기서 `fib` 함수의 `n + 2`에서의 값 (이것은 `succ (succ n)`과 정의상 동일함)은 `n + 1`에서의 값들 (이것은 `succ n`과 정의상 동등함) 및 `n`에서의 값에 따라 정의됩니다. 이것은 악명높게 비효율적인 피보나치 함수를 계산하는 방법이지만, 실행 시간이 `n`에서 지수적입니다. 더 좋은 방법이 여기 있습니다:

```
def fibFast (n : Nat) : Nat :=
(loop n).2
where
loop : Nat → Nat × Nat
| 0 => (0, 1)
| n+1 => let p := loop n; (p.2, p.1 + p.2)
#eval fibFast 100
```

```
573147844013817084101
```

Here is the same definition using a `let rec` instead of a `where`.

여기는 `where` 대신에 `let rec`를 사용한 동일한 정의입니다.

```
def fibFast (n : Nat) : Nat :=
let rec loop : Nat → Nat × Nat
| 0 => (0, 1)
| n+1 => let p := loop n; (p.2, p.1 + p.2)
(loop n).2
```

In both cases, Lean generates the auxiliary function `fibFast.loop`.

두 경우 모두에서 Lean은 보조 함수 `fibFast.loop`를 생성합니다.

To handle structural recursion, the equation compiler uses
*course-of-values* recursion, using constants `below` and `brecOn`
that are automatically generated with each inductively defined
type. You can get a sense of how it works by looking at the types of
`Nat.below` and `Nat.brecOn`:

구조적 재귀를 처리하기 위해, 방정식 컴파일러는 각 귀납적으로 정의된 타입과 함께 자동으로 생성되는 상수 `below`와 `brecOn`을 사용하는 *과정의 값(course-of-values)* 재귀를 사용합니다. `Nat.below`와 `Nat.brecOn`의 타입을 보면 어떻게 작동하는지 감을 잡을 수 있습니다:

```
variable (C : Nat → Type u)
#check (@Nat.below C : Nat → Type u)
```

```
Nat.below : Nat → Type u
```

```
#reduce @Nat.below C (3 : Nat)
```

```
Nat.below 3
```

```
#check (@Nat.brecOn C : (n : Nat) → ((n : Nat) → @Nat.below C n → C n) → C n)
```

```
Nat.brecOn : (t : Nat) → ((t : Nat) → Nat.below t → C t) → C t
```

The type `@Nat.below C (3 : Nat)` is a data structure that stores elements of `C 0`, `C 1`, and `C 2`.
The course-of-values recursion is implemented by `Nat.brecOn`. It enables us to define the value of a dependent
function of type `(n : Nat) → C n` at a particular input `n` in terms of all the previous values of the function,
presented as an element of `@Nat.below C n`.

타입 `@Nat.below C (3 : Nat)`는 `C 0`, `C 1`, `C 2`의 요소를 저장하는 데이터 구조입니다. 과정의 값 재귀는 `Nat.brecOn`에 의해 구현됩니다. 이것은 특정 입력 `n`에서 `(n : Nat) → C n` 타입의 의존 함수의 값을 `@Nat.below C n`의 요소로 제시되는 함수의 이전 모든 값에 따라 정의할 수 있게 합니다.

The use of course-of-values recursion is one of the techniques the equation compiler uses to justify to
the Lean kernel that a function terminates. It does not affect the code generator which compiles recursive
functions as other functional programming language compilers. Recall that `#eval` `fib` `<n>` is exponential in `<n>`.
On the other hand, `#reduce fib` `<n>` is efficient because it uses the definition sent to the kernel that
is based on the `brecOn` construction.

과정의 값 재귀의 사용은 방정식 컴파일러가 함수가 종료됨을 Lean 커널에 정당화하기 위해 사용하는 기술 중 하나입니다. 재귀 함수를 다른 함수형 프로그래밍 언어 컴파일러처럼 컴파일하는 코드 생성기에 영향을 주지 않습니다. `#eval` `fib` `<n>`이 `<n>`에서 지수적임을 상기하세요. 한편, `#reduce` `fib` `<n>`은 `brecOn` 구성에 기반한 커널로 전송된 정의를 사용하기 때문에 효율적입니다.

```
def fib : Nat → Nat
| 0 => 1
| 1 => 1
| n+2 => fib (n+1) + fib n
-- Slow:
-- #eval fib 50
-- Fast:
#reduce fib 50
```

```
20365011074
```

```
#print fib
```

```
def fib : Nat → Nat :=
fun x =>
  Nat.brecOn x fun x f =>
    (match (motive := (x : Nat) → Nat.below x → Nat) x with
      | 0 => fun x => 1
      | 1 => fun x => 1
      | n.succ.succ => fun x => x.1 + x.2.1)
      f
```

Another good example of a recursive definition is the list `append` function.

재귀 정의의 또 다른 좋은 예제는 리스트 `append` 함수입니다.

```
def append : List α → List α → List α
| [], bs => bs
| a::as, bs => a :: append as bs
example : append [1, 2, 3] [4, 5] = [1, 2, 3, 4, 5] := rfl
```

Here is another: it adds elements of the first list to elements of the second list, until one of the two lists runs out.

여기 또 다른 것이 있습니다: 두 리스트 중 하나가 끝날 때까지 첫 번째 리스트의 요소를 두 번째 리스트의 요소에 더합니다.

```
def listAdd [Add α] : List α → List α → List α
| [], _ => []
| _, [] => []
| a :: as, b :: bs => (a + b) :: listAdd as bs
#eval listAdd [1, 2, 3] [4, 5, 6, 6, 9, 10]
```

```
[5, 7, 9]
```

You are encouraged to experiment with similar examples in the exercises below.

아래의 연습에서 유사한 예제들로 실험해보도록 권장됩니다.

## 8.4. Local recursive declarations

You can define local recursive declarations using the `let rec` keyword.

`let rec` 키워드를 사용하여 지역 재귀 선언을 정의할 수 있습니다.

```
def replicate (n : Nat) (a : α) : List α :=
let rec loop : Nat → List α → List α
| 0, as => as
| n+1, as => loop n (a::as)
loop n []
#check @replicate.loop
```

```
@replicate.loop : {α : Type u_1} → α → Nat → List α → List α
```

Lean creates an auxiliary declaration for each `let rec`. In the example above,
it created the declaration `replicate.loop` for the `let rec loop` occurring at `replicate`.
Note that, Lean “closes” the declaration by adding any local variable occurring in the
`let rec` declaration as additional parameters. For example, the local variable `a` occurs
at `let rec loop`.

Lean은 각 `let rec`에 대해 보조 선언을 생성합니다. 위의 예제에서, `replicate`에서 발생하는 `let rec loop`에 대해 선언 `replicate.loop`를 생성했습니다. `let rec` 선언에서 발생하는 임의의 지역 변수를 추가 매개변수로 추가하여 선언을 “닫는다”는 점에 유의하세요. 예를 들어, 지역 변수 `a`는 `let rec loop`에서 발생합니다.

You can also use `let rec` in tactic mode and for creating proofs by induction.

전술 모드에서 `let rec`를 사용할 수도 있고, 귀납에 의한 증명을 생성하기 위해 사용할 수도 있습니다.

```
theorem length_replicate (n : Nat) (a : α) :
(replicate n a).length = n := by
let rec aux (n : Nat) (as : List α) :
(replicate.loop a n as).length = n + as.length := by
match n with
| 0 => simp [replicate.loop]
| n+1 => simp +arith [replicate.loop, aux n]
exact aux n []
```

You can also introduce auxiliary recursive declarations using `where` clause after your definition.
Lean converts them into a `let rec`.

정의 후에 `where` 절을 사용하여 보조 재귀 선언을 도입할 수도 있습니다. Lean은 이들을 `let rec`로 변환합니다.

```
def replicate (n : Nat) (a : α) : List α :=
loop n []
where
loop : Nat → List α → List α
| 0, as => as
| n+1, as => loop n (a::as)
theorem length_replicate (n : Nat) (a : α) :
(replicate n a).length = n := by
exact aux n []
where
aux (n : Nat) (as : List α) :
(replicate.loop a n as).length = n + as.length := by
match n with
| 0 => simp [replicate.loop]
| n+1 => simp +arith [replicate.loop, aux n]
```

## 8.5. Well-Founded Recursion and Induction

When structural recursion cannot be used, we can prove termination using well-founded recursion.
We need a well-founded relation and a proof that each recursive application is decreasing with respect to
this relation. Dependent type theory is powerful enough to encode and justify
well-founded recursion. Let us start with the logical background that
is needed to understand how it works.

구조적 재귀를 사용할 수 없을 때, 우리는 기반이 있는(well-founded) 재귀를 사용하여 종료를 증명할 수 있습니다. 우리는 기반이 있는 관계와 각 재귀 적용이 이 관계에 대해 감소한다는 증명이 필요합니다. 의존 타입 이론은 기반이 있는 재귀를 인코딩하고 정당화하기에 충분히 강력합니다. 어떻게 작동하는지 이해하는 데 필요한 논리적 배경부터 시작해봅시다.

Lean's standard library defines two predicates, `Acc r a` and
`WellFounded r`, where `r` is a binary relation on a type `α`,
and `a` is an element of type `α`.

Lean의 표준 라이브러리는 `Acc r a`와 `WellFounded r`이라는 두 개의 술어를 정의합니다. 여기서 `r`은 타입 `α`에 대한 이진 관계이고, `a`는 타입 `α`의 요소입니다.

```
variable (α : Sort u)
variable (r : α → α → Prop)
#check (Acc r : α → Prop)
```

```
Acc r : α → Prop
```

```
#check (WellFounded r : Prop)
```

```
WellFounded r : Prop
```

The first, `Acc`, is an inductively defined predicate. According to
its definition, `Acc r x` is equivalent to
`∀ y, r y x → Acc r y`. If you think of `r y x` as denoting a kind of order relation
`y ≺ x`, then `Acc r x` says that `x` is accessible from below,
in the sense that all its predecessors are accessible. In particular,
if `x` has no predecessors, it is accessible. Given any type `α`,
we should be able to assign a value to each accessible element of
`α`, recursively, by assigning values to all its predecessors first.

첫 번째인 `Acc`는 귀납적으로 정의된 술어입니다. 그 정의에 따르면, `Acc r x`는 `∀ y, r y x → Acc r y`와 동등합니다. `r y x`를 순서 관계 `y ≺ x`의 종류를 나타내는 것으로 생각한다면, `Acc r x`는 모든 전임자(predecessor)가 접근 가능한 의미에서 `x`가 아래에서 접근 가능하다고 말합니다. 특히, `x`가 전임자가 없으면 접근 가능합니다. 주어진 모든 타입 `α`에 대해, 먼저 모든 전임자에 값을 할당하여 `α`의 각 접근 가능한 요소에 재귀적으로 값을 할당할 수 있어야 합니다.

The statement that `r` is well-founded, denoted `WellFounded r`,
is exactly the statement that every element of the type is
accessible. By the above considerations, if `r` is a well-founded
relation on a type `α`, we should have a principle of well-founded
recursion on `α`, with respect to the relation `r`. And, indeed,
we do: the standard library defines `WellFounded.fix`, which serves
exactly that purpose.

`r`이 기반이 있다는 진술, 기호로는 `WellFounded r`, 은 정확히 타입의 모든 요소가 접근 가능하다는 진술입니다. 위의 고려사항에 의해, `r`이 타입 `α`에 대한 기반이 있는 관계라면, 우리는 관계 `r`과 관련하여 `α`에 대한 기반이 있는 재귀의 원리를 가져야 합니다. 그리고 실제로, 우리는 그것을 가집니다: 표준 라이브러리는 정확히 그 목적을 수행하는 `WellFounded.fix`를 정의합니다.

```
noncomputable
def f {α : Sort u}
(r : α → α → Prop)
(h : WellFounded r)
(C : α → Sort v)
(F : (x : α) → ((y : α) → r y x → C y) → C x) :
(x : α) → C x :=
WellFounded.fix h F
```

There is a long cast of characters here, but the first block we have
already seen: the type, `α`, the relation, `r`, and the
assumption, `h`, that `r` is well-founded. The variable `C`
represents the motive of the recursive definition: for each element
`x : α`, we would like to construct an element of `C x`. The
function `F` provides the inductive recipe for doing that: it tells
us how to construct an element `C x`, given elements of `C y` for
each predecessor `y` of `x`.

여기에는 많은 문자가 있지만, 우리가 이미 본 첫 번째 블록이 있습니다: 타입 `α`, 관계 `r`, 그리고 `r`이 기반이 있다는 가정 `h`. 변수 `C`는 재귀 정의의 동기를 나타냅니다: 각 요소 `x : α`에 대해, 우리는 `C x`의 요소를 구성하고 싶습니다. 함수 `F`는 그렇게 하기 위한 귀납적 조리법을 제공합니다: 각 전임자 `y`에 대해 `C y`의 요소가 주어졌을 때, `C x`의 요소를 구성하는 방법을 알려줍니다.

Note that `WellFounded.fix` works equally well as an induction
principle. It says that if `≺` is well-founded and you want to prove
`∀ x, C x`, it suffices to show that for an arbitrary `x`, if we
have `∀ y, r y x → C y`, then we have `C x`.

`WellFounded.fix`는 귀납 원리로도 똑같이 잘 작동한다는 점에 유의하세요. 이것은 `≺`이 기반이 있고 `∀ x, C x`를 증명하고 싶다면, 임의의 `x`에 대해, `∀ y, r y x → C y`를 가지면 `C x`를 가진다는 것을 보이기에 충분하다고 말합니다.

In the example above we use the modifier `noncomputable` because the code
generator currently does not support `WellFounded.fix`. The function
`WellFounded.fix` is another tool Lean uses to justify that a function
terminates.

위의 예제에서 우리는 코드 생성기가 현재 `WellFounded.fix`를 지원하지 않기 때문에 수정자 `noncomputable`을 사용합니다. 함수 `WellFounded.fix`는 Lean이 함수가 종료된다는 것을 정당화하기 위해 사용하는 또 다른 도구입니다.

Lean knows that the usual order `<` on the natural numbers is well
founded. It also knows a number of ways of constructing new well
founded orders from others, for example, using lexicographic order.

Lean은 자연수에 대한 일반적인 순서 `<`이 기반이 있음을 알고 있습니다. 또한 다른 것들로부터 새로운 기반이 있는 순서를 구성하는 여러 방법을 알고 있습니다. 예를 들어, 사전식 순서를 사용하는 것입니다.

Here is essentially the definition of division on the natural numbers that is found in the standard library.

여기는 표준 라이브러리에서 발견되는 자연수에 대한 나눗셈의 정의입니다.

```
open Nat
theorem div_lemma {x y : Nat} : 0 < y ∧ y ≤ x → x - y < x :=
fun h => sub_lt (Nat.lt_of_lt_of_le h.left h.right) h.left
def div.F (x : Nat) (f : (x₁ : Nat) → x₁ < x → Nat → Nat) (y : Nat) : Nat :=
if h : 0 < y ∧ y ≤ x then
f (x - y) (div_lemma h) y + 1
else
zero
noncomputable def div := WellFounded.fix (measure id).wf div.F
#reduce div 8 2
```

```
4
```

The definition is somewhat inscrutable. Here the recursion is on
`x`, and `div.F x f : Nat → Nat` returns the “divide by `y`”
function for that fixed `x`. You have to remember that the second
argument to `div.F`, the recipe for the recursion, is a function
that is supposed to return the divide by `y` function for all values
`x₁` smaller than `x`.

정의는 다소 불투명합니다. 여기서 재귀는 `x`에 있고, `div.F x f : Nat → Nat`은 그 고정된 `x`에 대해 “divide by `y`” 함수를 반환합니다. `div.F`의 두 번째 인수, 재귀의 조리법은 `x`보다 작은 모든 값 `x₁`에 대해 divide by `y` 함수를 반환해야 한다는 함수임을 기억해야 합니다.

The elaborator is designed to make definitions like this more
convenient. It accepts the following:

정교화기(elaborator)는 이러한 정의를 더 편리하게 하기 위해 설계되었습니다. 다음을 허용합니다:

```
def div (x y : Nat) : Nat :=
if h : 0 < y ∧ y ≤ x then
have : x - y < x := Nat.sub_lt (Nat.lt_of_lt_of_le h.1 h.2) h.1
div (x - y) y + 1
else
0
```

When Lean encounters a recursive definition, it first
tries structural recursion, and only when that fails, does it fall
back on well-founded recursion. Lean uses the tactic `decreasing_tactic`
to show that the recursive applications are smaller. The auxiliary
proposition `x - y < x` in the example above should be viewed as a hint
for this tactic.

Lean이 재귀 정의를 만날 때, 먼저 구조적 재귀를 시도하고, 그것이 실패할 때만 기반이 있는 재귀로 폴백합니다. Lean은 재귀 적용이 더 작다는 것을 보여주기 위해 `decreasing_tactic` 전술을 사용합니다. 위의 예제의 보조 명제 `x - y < x`는 이 전술에 대한 힌트로 봐야 합니다.

The defining equation for `div` does *not* hold definitionally, but
we can unfold `div` using the `unfold` tactic. We use [`conv`](../11-the-conversion-tactic-mode/#conv) to select which
`div` application we want to unfold.

`div`의 정의하는 방정식은 정의상 성립하지 *않지만*, `unfold` 전술을 사용하여 `div`를 펼칠 수 있습니다. [`conv`](../11-the-conversion-tactic-mode/#conv)를 사용하여 펼칠 `div` 적용을 선택합니다.

```
example (x y : Nat) :
div x y =
if 0 < y ∧ y ≤ x then
div (x - y) y + 1
else 0 := by
   -- unfold occurrence in the left-hand-side of the equation:
  conv => lhs; unfold div
rfl
example (x y : Nat) (h : 0 < y ∧ y ≤ x) :
div x y = div (x - y) y + 1 := by
conv => lhs; unfold div
simp [h]
```

The following example is similar: it converts any natural number to a
binary expression, represented as a list of 0's and 1's. We have to
provide evidence that the recursive call is
decreasing, which we do here with a `sorry`. The `sorry` does not
prevent the interpreter from evaluating the function successfully,
but `#eval!` must be used instead of `#eval` when a term contains `sorry`.

다음의 예제는 유사합니다: 모든 자연수를 0과 1의 리스트로 표현되는 이진 표현식으로 변환합니다. 우리는 재귀 호출이 감소한다는 증거를 제공해야 하며, 여기서 우리는 `sorry`로 그렇게 합니다. `sorry`는 인터프리터가 함수를 성공적으로 평가하는 것을 방지하지 않지만, 항이 `sorry`를 포함할 때 `#eval` 대신 `#eval!`를 사용해야 합니다.

```
def natToBin : Nat → List Nat
| 0 => [0]
| 1 => [1]
| n + 2 =>
have : (n + 2) / 2 < n + 2 := sorry
natToBin ((n + 2) / 2) ++ [n % 2]
#eval! natToBin 1234567
```

As a final example, we observe that Ackermann's function can be
defined directly, because it is justified by the well-foundedness of
the lexicographic order on the natural numbers. The `termination_by` clause
instructs Lean to use a lexicographic order. This clause is actually mapping
the function arguments to elements of type `Nat × Nat`. Then, Lean uses typeclass
resolution to synthesize an element of type `WellFoundedRelation (Nat × Nat)`.

마지막 예제로, 우리는 Ackermann 함수가 자연수에 대한 사전식 순서의 기반 존재에 의해 정당화되기 때문에 직접 정의될 수 있음을 관찰합니다. `termination_by` 절은 Lean에 사전식 순서를 사용하도록 지시합니다. 이 절은 실제로 함수 인수를 `Nat × Nat` 타입의 요소로 매핑합니다. 그 다음, Lean은 타입클래스 해결을 사용하여 `WellFoundedRelation (Nat × Nat)` 타입의 요소를 합성합니다.

```
def ack : Nat → Nat → Nat
| 0, y => y+1
| x+1, 0 => ack x 1
| x+1, y+1 => ack x (ack (x+1) y)
termination_by x y => (x, y)
```

In many cases, Lean can automatically determine an appropriate lexicographical order.
Ackermann's function is one such case, so the `termination_by` clause is optional:

많은 경우에 Lean은 자동으로 적절한 사전식 순서를 결정할 수 있습니다. Ackermann 함수는 그러한 경우 중 하나이므로 `termination_by` 절은 선택사항입니다:

```
def ack : Nat → Nat → Nat
| 0, y => y+1
| x+1, 0 => ack x 1
| x+1, y+1 => ack x (ack (x+1) y)
```

Note that a lexicographic order is used in the example above because the instance
`WellFoundedRelation (α × β)` uses a lexicographic order. Lean also defines the instance

위의 예제에서 사전식 순서가 사용되는 것에 유의하세요. 왜냐하면 인스턴스 `WellFoundedRelation (α × β)`가 사전식 순서를 사용하기 때문입니다. Lean은 또한 인스턴스를 정의합니다

```
instance (priority := low) [SizeOf α] : WellFoundedRelation α :=
sizeOfWFRel
```

In the following example, we prove termination by showing that `as.size - i` is decreasing
in the recursive application.

다음의 예제에서, 우리는 `as.size - i`가 재귀 적용에서 감소한다는 것을 보여줌으로써 종료를 증명합니다.

```
def takeWhile (p : α → Bool) (as : Array α) : Array α :=
go 0 #[]
where
go (i : Nat) (r : Array α) : Array α :=
if h : i < as.size then
let a := as[i]
if p a then
go (i+1) (r.push a)
else
r
else
r
termination_by as.size - i
```

Note that, auxiliary function `go` is recursive in this example, but `takeWhile` is not.
Once again, Lean can automatically recognize this pattern, so the `termination_by` clause is unnecessary:

이 예제에서 보조 함수 `go`는 재귀적이지만 `takeWhile`은 아님을 주목하세요. 다시 한 번, Lean은 자동으로 이 패턴을 인식할 수 있으므로 `termination_by` 절은 불필요합니다:

```
def takeWhile (p : α → Bool) (as : Array α) : Array α :=
go 0 #[]
where
go (i : Nat) (r : Array α) : Array α :=
if h : i < as.size then
let a := as[i]
if p a then
go (i+1) (r.push a)
else
r
else
r
```

By default, Lean uses the tactic `decreasing_tactic` to prove recursive applications are decreasing. The modifier `decreasing_by` allows us to provide our own tactic. Here is an example.

기본적으로, Lean은 재귀 적용이 감소하는 것을 증명하기 위해 `decreasing_tactic` 전술을 사용합니다. 수정자 `decreasing_by`는 우리의 자신의 전술을 제공할 수 있게 합니다. 여기 예제가 있습니다.

```
theorem div_lemma {x y : Nat} : 0 < y ∧ y ≤ x → x - y < x :=
fun ⟨ypos, ylex⟩ => Nat.sub_lt (Nat.lt_of_lt_of_le ypos ylex) ypos
def div (x y : Nat) : Nat :=
if h : 0 < y ∧ y ≤ x then
div (x - y) y + 1
else
0
decreasing_by apply div_lemma; assumption
```

Note that `decreasing_by` is not replacement for `termination_by`, they complement each other. `termination_by` is used to specify a well-founded relation, and `decreasing_by` for providing our own tactic for showing recursive applications are decreasing. In the following example, we use both of them.

`decreasing_by`는 `termination_by`의 대체물이 아니며, 서로 보완합니다. `termination_by`는 기반이 있는 관계를 지정하는 데 사용되고, `decreasing_by`는 재귀 적용이 감소하는 것을 보여주기 위한 자신의 전술을 제공하는 데 사용됩니다. 다음의 예제에서, 우리는 둘 다 사용합니다.

```
def ack : Nat → Nat → Nat
| 0, y => y+1
| x+1, 0 => ack x 1
| x+1, y+1 => ack x (ack (x+1) y)
termination_by x y => (x, y)
decreasing_by
   -- unfolds well-founded recursion auxiliary definitions:
  all_goals simp_wf
· apply Prod.Lex.left; simp +arith
· apply Prod.Lex.right; simp +arith
· apply Prod.Lex.left; simp +arith
```

We can use `decreasing_by sorry` to instruct Lean to “trust” us that the function terminates.

우리는 `decreasing_by sorry`를 사용하여 함수가 종료된다는 것을 Lean에 “신뢰”하도록 지시할 수 있습니다.

```
def natToBin : Nat → List Nat
| 0 => [0]
| 1 => [1]
| n + 2 => natToBin ((n + 2) / 2) ++ [n % 2]
decreasing_by sorry
#eval! natToBin 1234567
```

Recall that using `sorry` is equivalent to using a new axiom, and should be avoided. In the following example, we used the `sorry` to prove `False`.
The command `#print axioms unsound` shows that `unsound` depends on the unsound axiom `sorryAx` used to implement `sorry`.

`sorry`를 사용하는 것이 새로운 공리를 사용하는 것과 동등하며 피해야 함을 상기하세요. 다음의 예제에서, 우리는 `sorry`를 사용하여 `False`를 증명했습니다. `#print axioms unsound` 명령은 `unsound`가 `sorry`를 구현하는 데 사용되는 건전하지 않은 공리 `sorryAx`에 의존함을 보여줍니다.

```
def unsound (x : Nat) : False :=
unsound (x + 1)
decreasing_by sorry
#check unsound 0
```

```
unsound 0 : False
```

```
-- `unsound 0` is a proof of `False`

#print axioms unsound
```

```
'unsound' depends on axioms: [sorryAx]
```

Summary:

* If there is no `termination_by`, a well-founded relation is derived (if possible) by selecting an argument and then using typeclass resolution to synthesize a well-founded relation for this argument's type.
* If `termination_by` is specified, it maps the arguments of the function to a type `α` and type class resolution is again used. Recall that, the default instance for `β × γ` is a lexicographic order based on the well-founded relations for `β` and `γ`.
* The default well-founded relation instance for `Nat` is `(· < ·)`.
* By default, the tactic `decreasing_tactic` is used to show that recursive applications are smaller with respect to the selected well-founded relation. If `decreasing_tactic` fails, the error message includes the remaining goal `... |- G`. Note that, the `decreasing_tactic` uses `assumption`. So, you can include a `have`-expression to prove goal `G`. You can also provide your own tactic using `decreasing_by`.

If `termination_by` is specified, it maps the arguments of the function to a type `α` and type class resolution is again used. Recall that, the default instance for `β × γ` is a lexicographic order based on the well-founded relations for `β` and `γ`.

The default well-founded relation instance for `Nat` is `(· < ·)`.

By default, the tactic `decreasing_tactic` is used to show that recursive applications are smaller with respect to the selected well-founded relation. If `decreasing_tactic` fails, the error message includes the remaining goal `... |- G`. Note that, the `decreasing_tactic` uses `assumption`. So, you can include a `have`-expression to prove goal `G`. You can also provide your own tactic using `decreasing_by`.

요약:

* `termination_by`가 없으면, 기반이 있는 관계가 인수를 선택한 다음 타입클래스 해결을 사용하여 이 인수의 타입에 대한 기반이 있는 관계를 합성함으로써 도출됩니다 (가능한 경우).

* `termination_by`가 지정되면, 함수의 인수를 타입 `α`로 매핑하고 타입 클래스 해결이 다시 사용됩니다. `β × γ`의 기본 인스턴스가 `β`와 `γ`의 기반이 있는 관계에 기반한 사전식 순서임을 상기하세요.

* `Nat`의 기본 기반이 있는 관계 인스턴스는 `(· < ·)`입니다.

* 기본적으로, `decreasing_tactic` 전술은 선택된 기반이 있는 관계와 관련하여 재귀 적용이 더 작다는 것을 보여주는 데 사용됩니다. `decreasing_tactic`이 실패하면, 오류 메시지는 남은 목표 `... |- G`를 포함합니다. `decreasing_tactic`이 `assumption`을 사용함을 주목하세요. 따라서 목표 `G`를 증명하기 위해 `have` 식을 포함할 수 있습니다. `decreasing_by`를 사용하여 자신의 전술을 제공할 수도 있습니다.

## 8.6. Functional Induction

Lean generates bespoke induction principles for recursive functions. These induction principles follow the recursive structure of the function's definition, rather than the structure of the datatype. Proofs about functions typically follow the recursive structure of the function itself, so these induction principles allow statements about the function to be proved more conveniently.

Lean은 재귀 함수에 대한 맞춤형 귀납 원리를 생성합니다. 이러한 귀납 원리는 데이터 타입의 구조보다는 함수 정의의 재귀 구조를 따릅니다. 함수에 대한 증명은 일반적으로 함수 자체의 재귀 구조를 따르므로, 이러한 귀납 원리는 함수에 대한 진술을 더 편리하게 증명할 수 있게 합니다.

For example, using the functional induction principle for `ack` to prove that the result is always greater than `0` requires one case for each arm of the pattern match in `ack`:

```
def ack : Nat → Nat → Nat
| 0, y => y+1
| x+1, 0 => ack x 1
| x+1, y+1 => ack x (ack (x+1) y)
theorem ack_gt_zero : ack n m > 0 := by
fun_induction ack with
| case1 y =>
simp
| case2 x ih =>
exact ih
| case3 x y ih1 ih2 =>
simp [ack, *]
```

In `case1`, the goal is:

예를 들어, 결과가 항상 `0`보다 크다는 것을 증명하기 위해 `ack`에 대한 함수형 귀납 원리를 사용하려면 `ack`의 패턴 매치의 각 분기에 대해 하나의 경우가 필요합니다:

The `y + 1` in the goal corresponds to the value returned in the first case of `ack`.

In `case2`, the goal is:

`case1case1y:Nat⊢ y + 1 > 0`에서 목표는:

목표의 `y + 1`은 `ack`의 첫 번째 경우에서 반환된 값에 해당합니다.

The `ack x 1` in the goal corresponds to the value of `ack` applied to the pattern variables `x + 1` and `0` returned in the second case of `ack`.
This term is automatically simplified to the right-hand side.
Happily, the inductive hypothesis `ih : ack x 1 > 0` corresponds to the recursive call, which is exactly the answer returned in this case.

In `case3`, the goal is:

`case2case2x:Natih:ack x 1 > 0⊢ ack x 1 > 0`에서 목표는:

목표의 `ack x 1`은 `ack`의 두 번째 경우에서 반환된 패턴 변수 `x + 1`과 `0`에 적용된 `ack`의 값에 해당합니다. 이 항은 자동으로 우측으로 단순화됩니다. 다행히, 귀납 가설 `ih : ack x 1 > 0`은 재귀 호출에 해당하며, 이는 이 경우에 반환된 정확한 답입니다.

The `ack x (ack (x + 1) y)` in the goal corresponds to the value returned in the third case of `ack`, when `ack` applied to `x + 1` and `y + 1` has been reduced.
The inductive hypotheses `ih1 : ack (x + 1) y > 0` and `ih2 : ack x (ack (x + 1) y) > 0` correspond to the recursive calls, with `ih1` matching the nested recursive call.
Once again, the induction hypothesis is suitable.

`case3case3x:Naty:Natih1:ack (x + 1) y > 0ih2:ack x (ack (x + 1) y) > 0⊢ ack x (ack (x + 1) y) > 0`에서 목표는:

목표의 `ack x (ack (x + 1) y)`는 `ack`이 `x + 1`과 `y + 1`에 적용되어 축약되었을 때 `ack`의 세 번째 경우에서 반환된 값에 해당합니다. 귀납 가설 `ih1 : ack (x + 1) y > 0`과 `ih2 : ack x (ack (x + 1) y) > 0`는 재귀 호출에 해당하며, `ih1`은 중첩된 재귀 호출과 일치합니다. 다시 한 번, 귀납 가설이 적절합니다.

Using `fun_induction ack` results in goals and induction hypotheses that match the recursive structure of `ack`. As a result, the proof can be a single line:

`fun_induction ack`를 사용하면 `ack`의 재귀 구조와 일치하는 목표와 귀납 가설이 결과가 됩니다. 결과적으로, 증명은 한 줄일 수 있습니다:

```
theorem ack_gt_zero : ack n m > 0 := by
fun_induction ack <;> simp [*, ack]
```

There is also a `fun_cases` tactic which is analogous to the `cases` tactic.
It generates a case for each branch in a function's control flow.
Both it and `fun_induction` additionally provide assumptions that rule out the paths that were not taken.

또한 `cases` 전술과 유사한 `fun_cases` 전술이 있습니다. 함수의 제어 흐름의 각 분기에 대해 경우를 생성합니다. 그것과 `fun_induction` 모두 추가로 취하지 않은 경로를 배제하는 가정을 제공합니다.

This function `f` represents a five-way Boolean disjunction:

이 함수 `f`는 5-방향 부울 선택(disjunction)을 나타냅니다:

```
def f : Bool → Bool → Bool → Bool → Bool → Bool
| true, _, _, _ , _ => true
| _, true, _, _ , _ => true
| _, _, true, _ , _ => true
| _, _, _, true, _ => true
| _, _, _, _, x => x
```

To prove that it is disjunction, the last case requires knowledge that none of the arguments are `true`.
This knowledge is provided by the tactic:

그것이 선택임을 증명하기 위해, 마지막 경우는 인수 중 어느 것도 `true`가 아니라는 지식이 필요합니다. 이 지식은 전술에 의해 제공됩니다:

```
theorem f_or : f b1 b2 b3 b4 b5 = (b1 || b2 || b3 || b4 || b5) := by
fun_cases f
all_goals sorry
```

Each case includes an assumption that rules out the prior cases:

각 경우는 이전 경우들을 배제하는 가정을 포함합니다:

The `simp_all` tactic, which simplifies all the assumptions and the goal together, can dispatch all cases:

모든 가정과 목표를 함께 단순화하는 `simp_all` 전술은 모든 경우를 처리할 수 있습니다:

```
theorem f_or : f b1 b2 b3 b4 b5 = (b1 || b2 || b3 || b4 || b5) := by
fun_cases f <;> simp_all
```

## 8.7. Mutual Recursion

Lean also supports mutual recursive definitions. The syntax is similar to that for mutual inductive types. Here is an example:

Lean은 또한 상호 재귀 정의를 지원합니다. 구문은 상호 귀납 타입의 구문과 유사합니다. 여기 예제가 있습니다:

```
mutual
def even : Nat → Bool
| 0 => true
| n+1 => odd n
def odd : Nat → Bool
| 0 => false
| n+1 => even n
end
example : even (a + 1) = odd a := by
simp [even]
example : odd (a + 1) = even a := by
simp [odd]
theorem even_eq_not_odd : ∀ a, even a = not (odd a) := by
intro a; induction a
. simp [even, odd]
. simp [even, odd, *]
```

What makes this a mutual definition is that `even` is defined recursively in terms of `odd`, while `odd` is defined recursively in terms of `even`. Under the hood, this is compiled as a single recursive definition. The internally defined function takes, as argument, an element of a sum type, either an input to `even`, or an input to `odd`. It then returns an output appropriate to the input. To define that function, Lean uses a suitable well-founded measure. The internals are meant to be hidden from users; the canonical way to make use of such definitions is to use `simp` (or `unfold`), as we did above.

이것을 상호 정의로 만드는 것은 `even`이 `odd`의 관점에서 재귀적으로 정의되고, `odd`는 `even`의 관점에서 재귀적으로 정의된다는 것입니다. 내부적으로, 이것은 단일 재귀 정의로 컴파일됩니다. 내부적으로 정의된 함수는 인수로 합 타입의 요소를 취하며, `even`의 입력 또는 `odd`의 입력입니다. 그 다음 입력에 적절한 출력을 반환합니다. 그 함수를 정의하기 위해, Lean은 적절한 기반이 있는 측도를 사용합니다. 내부는 사용자로부터 숨겨지도록 의도되었습니다. 그러한 정의를 활용하는 표준적인 방법은 위에서 한 것처럼 `simp` (또는 `unfold`)를 사용하는 것입니다.

Mutual recursive definitions also provide natural ways of working with mutual and nested inductive types. Recall the definition of `Even` and `Odd` as mutual inductive predicates as presented before.

상호 재귀 정의는 또한 상호 및 중첩된 귀납 타입으로 작업하는 자연스러운 방법을 제공합니다. 이전에 제시된 대로 `Even`과 `Odd`의 상호 귀납 술어로서의 정의를 상기하세요.

```
mutual
inductive Even : Nat → Prop where
| even_zero : Even 0
| even_succ : ∀ n, Odd n → Even (n + 1)
inductive Odd : Nat → Prop where
| odd_succ : ∀ n, Even n → Odd (n + 1)
end
```

The constructors, `even_zero`, `even_succ`, and `odd_succ` provide positive means for showing that a number is even or odd. We need to use the fact that the inductive type is generated by these constructors to know that zero is not odd, and that the latter two implications reverse. As usual, the constructors are kept in a namespace that is named after the type being defined, and the command `open Even Odd` allows us to access them more conveniently.

생성자 `even_zero`, `even_succ`, `odd_succ`는 수가 짝수 또는 홀수임을 보여주는 긍정적 수단을 제공합니다. 우리는 귀납 타입이 이러한 생성자들에 의해 생성된다는 사실을 사용하여 0이 홀수가 아니며, 후자의 두 의미(implication)가 역으로 성립함을 알아야 합니다. 항상처럼, 생성자들은 정의되는 타입의 이름을 따서 지어진 네임스페이스에 보관되며, `open Even Odd` 명령은 우리가 이들에 더 편리하게 접근할 수 있게 합니다.

```
open Even Odd
theorem not_odd_zero : ¬ Odd 0 :=
fun h => nomatch h
theorem even_of_odd_succ : ∀ n, Odd (n + 1) → Even n
| _, odd_succ n h => h
theorem odd_of_even_succ : ∀ n, Even (n + 1) → Odd n
| _, even_succ n h => h
```

For another example, suppose we use a nested inductive type to define a set of terms inductively, so that a term is either a constant (with a name given by a string), or the result of applying a constant to a list of constants.

```
inductive Term where
| const : String → Term
| app : String → List Term → Term
```

We can then use a mutual recursive definition to count the number of constants occurring in a term, as well as the number occurring in a list of terms.

```
namespace Term
mutual
def numConsts : Term → Nat
| const _ => 1
| app _ cs => numConstsLst cs
def numConstsLst : List Term → Nat
| [] => 0
| c :: cs => numConsts c + numConstsLst cs
end
def sample := app "f" [app "g" [const "x"], const "y"]
#eval numConsts sample
```

```
2
```

```
end Term
```

As a final example, we define a function `replaceConst a b e` that replaces a constant `a` with `b` in a term `e`, and then prove the number of constants is the same. Note that, our proof uses mutual recursion (aka induction).

또 다른 예제로, 항들의 집합을 귀납적으로 정의하기 위해 중첩된 귀납 타입을 사용한다고 가정합시다. 따라서 항은 상수(이름이 문자열로 주어짐) 또는 상수를 상수 리스트에 적용한 결과입니다.

그 다음 우리는 상호 재귀 정의를 사용하여 항에서 발생하는 상수의 개수, 그리고 상수 리스트에서 발생하는 개수를 셀 수 있습니다.

마지막 예제로, 우리는 항 `e`에서 상수 `a`를 `b`로 바꾸는 함수 `replaceConst a b e`를 정의한 다음, 상수의 개수가 같음을 증명합니다. 우리의 증명은 상호 재귀(aka 귀납)를 사용함을 주목하세요.

```
mutual
def replaceConst (a b : String) : Term → Term
| const c => if a == c then const b else const c
| app f cs => app f (replaceConstLst a b cs)
def replaceConstLst (a b : String) : List Term → List Term
| [] => []
| c :: cs => replaceConst a b c :: replaceConstLst a b cs
end
mutual
theorem numConsts_replaceConst (a b : String) (e : Term) :
numConsts (replaceConst a b e) = numConsts e := by
match e with
| const c =>
simp [replaceConst]; split <;> simp [numConsts]
| app f cs =>
simp [replaceConst, numConsts, numConsts_replaceConstLst a b cs]
theorem numConsts_replaceConstLst (a b : String) (es : List Term) :
numConstsLst (replaceConstLst a b es) = numConstsLst es := by
match es with
| [] => simp [replaceConstLst, numConstsLst]
| c :: cs =>
simp [replaceConstLst, numConstsLst, numConsts_replaceConst a b c,
numConsts_replaceConstLst a b cs]
end
```

## 8.8. Dependent Pattern Matching

All the examples of pattern matching we considered in the section on
[pattern matching](#pattern-matching) can easily be written using `casesOn`
and `recOn`. However, this is often not the case with indexed
inductive families such as `Vect α n`, since case splits impose
constraints on the values of the indices. Without the equation
compiler, we would need a lot of boilerplate code to define very
simple functions such as `map`, `zip`, and `unzip` using
recursors. To understand the difficulty, consider what it would take
to define a function `tail` which takes a vector
`v : Vect α (n + 1)` and deletes the first element.

우리가 [패턴 매칭(pattern matching)](#pattern-matching) 섹션에서 고려한 패턴 매칭의 모든 예제들은 `casesOn`과 `recOn`을 사용하여 쉽게 작성될 수 있습니다. 그러나 이는 종종 `Vect α n`과 같은 색인된 귀납 계열의 경우가 아닙니다. 왜냐하면 경우 분할이 색인 값에 제약을 부과하기 때문입니다. 방정식 컴파일러가 없으면, 우리는 재귀자를 사용하여 `map`, `zip`, `unzip`과 같은 매우 간단한 함수들을 정의하기 위해 많은 보일러플레이트 코드가 필요합니다. 어려움을 이해하려면, 벡터 `v : Vect α (n + 1)`를 취하고 첫 번째 요소를 삭제하는 함수 `tail`을 정의하는 데 필요한 것을 고려하세요.

```
inductive Vect (α : Type u) : Nat → Type u
| nil : Vect α 0
| cons : α → {n : Nat} → Vect α n → Vect α (n + 1)
```

A first thought might be to use the `Vect.casesOn` function:

첫 번째 생각은 `Vect.casesOn` 함수를 사용하는 것일 수 있습니다:

```
Vect.casesOn.{u, v}
{α : Type v} {motive : (a : Nat) → Vect α a → Sort u}
{a : Nat}
(t : Vect α a)
(nil : motive 0 nil)
(cons : (a : α) → {n : Nat} → (a_1 : Vect α n) →
motive (n + 1) (cons a a_1)) :
motive a t
```

But what value should we return in the `nil` case? Something funny
is going on: if `v` has type `Vect α (n + 1)`, it *can't* be
`nil`, but it is not clear how to tell that to `Vect.casesOn`.

하지만 `nil` 경우에 어떤 값을 반환해야 할까요? 뭔가 이상한 일이 일어나고 있습니다: `v`가 타입 `Vect α (n + 1)`를 가지면, 그것은 `nil`일 수 *없습니다*. 하지만 `Vect.casesOn`에 그것을 알리는 방법이 명확하지 않습니다.

One solution is to define an auxiliary function:

한 가지 해결책은 보조 함수를 정의하는 것입니다:

```
def tailAux (v : Vect α m) : m = n + 1 → Vect α n :=
Vect.casesOn (motive := fun x _ => x = n + 1 → Vect α n) v
(fun h : 0 = n + 1 => Nat.noConfusion h)
(fun (a : α) (m : Nat) (as : Vect α m) =>
fun (h : m + 1 = n + 1) =>
Nat.noConfusion h (fun h1 : m = n => h1 ▸ as))
def tail (v : Vect α (n+1)) : Vect α n :=
tailAux v rfl
```

In the `nil` case, `m` is instantiated to `0`, and
`Nat.noConfusion` makes use of the fact that `0 = n + 1` cannot
occur. Otherwise, `v` is of the form `cons a as`, and we can simply
return `as`, after casting it from a vector of length `m` to a
vector of length `n`.

The difficulty in defining `tail` is to maintain the relationships between the indices.
The hypothesis `m = n + 1` in `tailAux` is used to communicate the relationship
between `n` and the index associated with the minor premise.
Moreover, the `0 = n + 1` case is unreachable, and the canonical way to discard such
a case is to use `Nat.noConfusion`.

`nil` 경우에, `m`은 `0`으로 인스턴스화되고, `Nat.noConfusion`은 `0 = n + 1`이 발생할 수 없다는 사실을 활용합니다. 그렇지 않으면 `v`는 `cons` `a` `as` 형태이고, 우리는 단순히 `as`를 반환할 수 있으며, 길이 `m`의 벡터에서 길이 `n`의 벡터로 캐스팅한 후입니다.

`tail`을 정의하는 어려움은 색인들 간의 관계를 유지하는 것입니다. `tailAux`의 가설 `m = n + 1`은 `n`과 소전제(minor premise)와 관련된 색인 사이의 관계를 전달하는 데 사용됩니다. 더욱이, `0 = n + 1` 경우는 도달할 수 없으며, 그러한 경우를 버리는 표준적인 방법은 `Nat.noConfusion`을 사용하는 것입니다.

The `tail` function is, however, easy to define using recursive
equations, and the equation compiler generates all the boilerplate
code automatically for us. Here are a number of similar examples:

`tail` 함수는, 그러나, 재귀 방정식을 사용하여 정의하기 쉽고, 방정식 컴파일러는 우리를 위해 모든 보일러플레이트 코드를 자동으로 생성합니다. 여기 유사한 예제들이 많이 있습니다:

```
def head : {n : Nat} → Vect α (n+1) → α
| n, cons a as => a
def tail : {n : Nat} → Vect α (n+1) → Vect α n
| n, cons a as => as
theorem eta : ∀ {n : Nat} (v : Vect α (n+1)), cons (head v) (tail v) = v
| n, cons a as => rfl
def map (f : α → β → γ) : {n : Nat} → Vect α n → Vect β n → Vect γ n
| 0, nil, nil => nil
| n+1, cons a as, cons b bs => cons (f a b) (map f as bs)
def zip : {n : Nat} → Vect α n → Vect β n → Vect (α × β) n
| 0, nil, nil => nil
| n+1, cons a as, cons b bs => cons (a, b) (zip as bs)
```

Note that we can omit recursive equations for “unreachable” cases such
as `head nil`. The automatically generated definitions for indexed
families are far from straightforward. For example:

`head` `nil`과 같은 “도달할 수 없는” 경우에 대해 재귀 방정식을 생략할 수 있음을 주목하세요. 색인된 계열에 대해 자동으로 생성된 정의는 간단하지 않습니다. 예를 들어:

```
def zipWith (f : α → β → γ) : {n : Nat} → Vect α n → Vect β n → Vect γ n
| 0, nil, nil => nil
| n+1, cons a as, cons b bs => cons (f a b) (zipWith f as bs)
#print zipWith
```

```
def Vect.zipWith.{u_1, u_2, u_3} : {α : Type u_1} →
  {β : Type u_2} → {γ : Type u_3} → (α → β → γ) → {n : Nat} → Vect α n → Vect β n → Vect γ n :=
fun {α} {β} {γ} f x x_1 x_2 =>
  Vect.brecOn (motive := fun x x_3 => Vect β x → Vect γ x) x_1
    (fun x x_3 f_1 x_4 =>
      (match (motive :=
          (x : Nat) →
            (x_5 : Vect α x) → Vect β x → Vect.below (motive := fun x x_7 => Vect β x → Vect γ x) x_5 → Vect γ x)
          x, x_3, x_4 with
        | 0, nil, nil => fun x => nil
        | n.succ, cons a as, cons b bs => fun x => cons (f a b) (x.1 bs))
        f_1)
    x_2
```

```
#print zipWith.match_1
```

```
def Vect.zipWith.match_1.{u_1, u_2, u_3} : {α : Type u_1} →
  {β : Type u_2} →
    (motive : (x : Nat) → Vect α x → Vect β x → Sort u_3) →
      (x : Nat) →
        (x_1 : Vect α x) →
          (x_2 : Vect β x) →
            (Unit → motive 0 nil nil) →
              ((n : Nat) →
                  (a : α) → (as : Vect α n) → (b : β) → (bs : Vect β n) → motive n.succ (cons a as) (cons b bs)) →
                motive x x_1 x_2 :=
fun {α} {β} motive x x_1 x_2 h_1 h_2 =>
  Nat.casesOn (motive := fun x => (x_3 : Vect α x) → (x_4 : Vect β x) → motive x x_3 x_4) x
    (fun x x_3 =>
      casesOn (motive := fun a x_4 => Nat.zero = a → x ≍ x_4 → motive Nat.zero x x_3) x
        (fun h h_3 =>
          ⋯ ▸
            casesOn (motive := fun a x => Nat.zero = a → x_3 ≍ x → motive Nat.zero nil x_3) x_3
              (fun h h_4 => ⋯ ▸ h_1 ()) (fun a {n} a_1 h => False.elim ⋯) ⋯ ⋯)
        (fun a {n} a_1 h => False.elim ⋯) ⋯ ⋯)
    (fun n x x_3 =>
      casesOn (motive := fun a x_4 => n.succ = a → x ≍ x_4 → motive n.succ x x_3) x (fun h => False.elim ⋯)
        (fun a {n_1} a_1 h =>
          n.elimOffset n_1 1 h fun x_4 =>
            Eq.ndrec (motive := fun {n_2} => (a_2 : Vect α n_2) → x ≍ cons a a_2 → motive n.succ x x_3)
              (fun a_2 h =>
                ⋯ ▸
                  casesOn (motive := fun a_3 x => n.succ = a_3 → x_3 ≍ x → motive n.succ (cons a a_2) x_3) x_3
                    (fun h => False.elim ⋯)
                    (fun a_3 {n_2} a_4 h =>
                      n.elimOffset n_2 1 h fun x =>
                        Eq.ndrec (motive := fun {n_3} =>
                          (a_5 : Vect β n_3) → x_3 ≍ cons a_3 a_5 → motive n.succ (cons a a_2) x_3)
                          (fun a_5 h => ⋯ ▸ h_2 n a a_2 a_3 a_5) x a_4)
                    ⋯ ⋯)
              x_4 a_1)
        ⋯ ⋯)
    x_1 x_2
```

The `zipWith` function is even more tedious to define by hand than the
`tail` function. We encourage you to try it, using `Vect.recOn`,
`Vect.casesOn` and `Vect.noConfusion`.

## 8.9. Inaccessible Patterns

Sometimes an argument in a dependent matching pattern is not essential
to the definition, but nonetheless has to be included to specialize
the type of the expression appropriately. Lean allows users to mark
such subterms as *inaccessible* for pattern matching. These
annotations are essential, for example, when a term occurring in the
left-hand side is neither a variable nor a constructor application,
because these are not suitable targets for pattern matching. We can
view such inaccessible patterns as “don't care” components of the
patterns. You can declare a subterm inaccessible by writing
`.(t)`. If the inaccessible pattern can be inferred, you can also write
`_`.

때때로 의존 매칭 패턴의 인수가 정의에 필수적이지는 않지만, 그럼에도 불구하고 표현식의 타입을 적절하게 특수화하기 위해 포함되어야 할 때가 있습니다. Lean은 사용자가 이러한 부분항을 패턴 매칭에서 *접근 불가능(inaccessible)*한 것으로 표시할 수 있게 합니다. 이러한 어노테이션은 예를 들어 좌변에 나타나는 항이 변수도 생성자 적용도 아닐 때 필수적인데, 이는 패턴 매칭의 적절한 대상이 아니기 때문입니다. 우리는 이러한 접근 불가능한 패턴을 패턴의 "상관없는(don't care)" 구성 요소로 볼 수 있습니다. `.(t)`를 써서 부분항을 접근 불가능으로 선언할 수 있습니다. 접근 불가능한 패턴이 유추될 수 있다면 `_`를 쓸 수도 있습니다.

The following example, we declare an inductive type that defines the
property of “being in the image of `f`”. You can view an element of
the type `ImageOf f b` as evidence that `b` is in the image of
`f`, whereby the constructor `imf` is used to build such
evidence. We can then define any function `f` with an “inverse”
which takes anything in the image of `f` to an element that is
mapped to it. The typing rules forces us to write `f a` for the
first argument, but this term is neither a variable nor a constructor
application, and plays no role in the pattern-matching definition. To
define the function `inverse` below, we *have to* mark `f a`
inaccessible.

다음 예제에서 우리는 "`f`의 이미지에 있음"의 성질을 정의하는 귀납적 타입을 선언합니다. `ImageOf f b` 타입의 요소를 `b`가 `f`의 이미지에 있다는 증거로 볼 수 있으며, 여기서 생성자 `imf`는 그러한 증거를 구축하는 데 사용됩니다. 그 다음 우리는 `f`의 이미지에 있는 모든 것을 그것에 매핑되는 요소로 가져가는 "역(inverse)"을 가진 임의의 함수 `f`를 정의할 수 있습니다. 타이핑 규칙은 첫 번째 인수로 `f a`를 쓰도록 강제하지만, 이 항은 변수도 생성자 적용도 아니며 패턴 매칭 정의에서 아무런 역할도 하지 않습니다. 아래에서 `inverse` 함수를 정의하려면 `f a`를 접근 불가능으로 표시*해야 합니다*.

```
inductive ImageOf {α β : Type u} (f : α → β) : β → Type u where
| imf : (a : α) → ImageOf f (f a)
open ImageOf
def inverse {f : α → β} : (b : β) → ImageOf f b → α
| .(f a), imf a => a
def inverse' {f : α → β} : (b : β) → ImageOf f b → α
| _, imf a => a
```

In the example above, the inaccessible annotation makes it clear that
`f` is *not* a pattern matching variable.

위의 예제에서 접근 불가능 어노테이션은 `f`가 패턴 매칭 변수가 *아님*을 명확히 합니다.

Inaccessible patterns can be used to clarify and control definitions that
make use of dependent pattern matching. Consider the following
definition of the function `Vect.add`, which adds two vectors of
elements of a type, assuming that type has an associated addition
function:

접근 불가능한 패턴은 의존 패턴 매칭을 사용하는 정의를 명확히 하고 제어하는 데 사용될 수 있습니다. 타입에 연관된 덧셈 함수가 있다고 가정하고, 해당 타입의 요소들로 이루어진 두 벡터를 더하는 `Vect.add` 함수의 다음 정의를 고려해 보세요.

```
inductive Vect (α : Type u) : Nat → Type u
| nil : Vect α 0
| cons : α → {n : Nat} → Vect α n → Vect α (n+1)
def Vect.add [Add α] : {n : Nat} → Vect α n → Vect α n → Vect α n
| 0, nil, nil => nil
| n+1, cons a as, cons b bs => cons (a + b) (add as bs)
```

The argument `{n : Nat}` appear after the colon, because it cannot
be held fixed throughout the definition. When implementing this
definition, the equation compiler starts with a case distinction as to
whether the first argument is `0` or of the form `n+1`. This is
followed by nested case splits on the next two arguments, and in each
case the equation compiler rules out the cases are not compatible with
the first pattern.

인수 `{n : Nat}`은 정의 전체에서 고정된 상태로 유지될 수 없기 때문에 콜론 뒤에 나타납니다. 이 정의를 구현할 때, 방정식 컴파일러는 첫 번째 인수가 `0`인지 또는 `n+1` 형태인지에 대한 경우 구분으로 시작합니다. 그 다음 나머지 두 인수에 대한 중첩된 경우 분할이 이루어지며, 각 경우에 방정식 컴파일러는 첫 번째 패턴과 호환되지 않는 경우를 배제합니다.

But, in fact, a case split is not required on the first argument; the
`casesOn` eliminator for `Vect` automatically abstracts this
argument and replaces it by `0` and `n + 1` when we do a case
split on the second argument. Using inaccessible patterns, we can prompt
the equation compiler to avoid the case split on `n`.

하지만 사실 첫 번째 인수에 대한 경우 분할은 필요하지 않습니다. `Vect`에 대한 `casesOn` 제거자(eliminator)는 우리가 두 번째 인수에 대한 경우 분할을 수행할 때 이 인수를 자동으로 추상화하고 그것을 `0`과 `n + 1`로 대체합니다. 접근 불가능한 패턴을 사용하여 방정식 컴파일러가 `n`에 대한 경우 분할을 피하도록 유도할 수 있습니다.

```
def add [Add α] : {n : Nat} → Vect α n → Vect α n → Vect α n
| .(_), nil, nil => nil
| .(_), cons a as, cons b bs => cons (a + b) (add as bs)
```

Marking the position as an inaccessible pattern tells the
equation compiler first, that the form of the argument should be
inferred from the constraints posed by the other arguments, and,
second, that the first argument should *not* participate in pattern
matching.

해당 위치를 접근 불가능한 패턴으로 표시하는 것은 방정식 컴파일러에게 첫째, 인수의 형태가 다른 인수들에 의해 제기된 제약 조건으로부터 유추되어야 함을 알려주고, 둘째, 첫 번째 인수가 패턴 매칭에 참여하지 *않아야* 함을 알려줍니다.

The inaccessible pattern `.(_)` can be written as `_` for convenience.

접근 불가능한 패턴 `.(_)`은 편의상 `_`로 쓸 수 있습니다.

```
def add [Add α] : {n : Nat} → Vect α n → Vect α n → Vect α n
| _, nil, nil => nil
| _, cons a as, cons b bs => cons (a + b) (add as bs)
```

As we mentioned above, the argument `{n : Nat}` is part of the
pattern matching, because it cannot be held fixed throughout the
definition. Rather than requiring that these discriminants be provided explicitly, Lean implicitly includes
these extra discriminants automatically for us.

위에서 언급했듯이 `{n : Nat}` 인수는 정의 전체에서 고정될 수 없기 때문에 패턴 매칭의 일부입니다. 이러한 판별식(discriminant)을 명시적으로 요구하는 대신, Lean은 우리를 위해 이러한 추가 판별식을 자동으로 암시적으로 포함합니다.

```
def add [Add α] {n : Nat} : Vect α n → Vect α n → Vect α n
| nil, nil => nil
| cons a as, cons b bs => cons (a + b) (add as bs)
```

When combined with the *auto bound implicits* feature, you can simplify
the declare further and write:

*auto bound implicits* 기능과 결합하면, 선언을 더 단순화하여 다음과 같이 쓸 수 있습니다.

```
def add [Add α] : Vect α n → Vect α n → Vect α n
| nil, nil => nil
| cons a as, cons b bs => cons (a + b) (add as bs)
```

Using these new features, you can write the other vector functions defined
in the previous sections more compactly as follows:

이러한 새로운 기능을 사용하여 이전 섹션에서 정의된 다른 벡터 함수들을 다음과 같이 더 간결하게 쓸 수 있습니다:

## 8.10. 매치 표현식

```
def head : Vect α (n+1) → α
| cons a as => a
def tail : Vect α (n+1) → Vect α n
| cons a as => as
theorem eta : (v : Vect α (n+1)) → cons (head v) (tail v) = v
| cons a as => rfl
def map (f : α → β → γ) : Vect α n → Vect β n → Vect γ n
| nil, nil => nil
| cons a as, cons b bs => cons (f a b) (map f as bs)
def zip : Vect α n → Vect β n → Vect (α × β) n
| nil, nil => nil
| cons a as, cons b bs => cons (a, b) (zip as bs)
```

## 8.10. Match Expressions

Lean also provides a compiler for `match`-`with` expressions found in
many functional languages:

Lean은 또한 많은 함수형 언어에서 발견되는 `match`-`with` 표현식에 대한 컴파일러를 제공합니다.

```
def isNotZero (m : Nat) : Bool :=
match m with
| 0 => false
| n + 1 => true
```

This does not look very different from an ordinary pattern matching
definition, but the point is that a `match` can be used anywhere in
an expression, and with arbitrary arguments.

이것은 일반적인 패턴 매칭 정의와 크게 달라 보이지 않지만, 요점은 `match`가 표현식의 어느 곳에서나 임의의 인수와 함께 사용될 수 있다는 것입니다.

```
def isNotZero (m : Nat) : Bool :=
match m with
| 0 => false
| n + 1 => true
def filter (p : α → Bool) : List α → List α
| [] => []
| a :: as =>
match p a with
| true => a :: filter p as
| false => filter p as
example : filter isNotZero [1, 0, 0, 3, 0] = [1, 3] := rfl
```

Here is another example:

여기에 또 다른 예가 있습니다.

```
def foo (n : Nat) (b c : Bool) :=
5 + match n - 5, b && c with
| 0, true => 0
| m + 1, true => m + 7
| 0, false => 5
| m + 1, false => m + 3
#eval foo 7 true false
```

```
9
```

```
example : foo 7 true false = 9 := rfl
```

Lean uses the `match` construct internally to implement pattern-matching in all parts of the system.
Thus, all four of these definitions have the same net effect:

Lean은 내부적으로 `match` 구문을 사용하여 시스템의 모든 부분에서 패턴 매칭을 구현합니다. 따라서 이 네 가지 정의는 모두 동일한 최종 효과를 가집니다.

```
def bar₁ : Nat × Nat → Nat
| (m, n) => m + n
def bar₂ (p : Nat × Nat) : Nat :=
match p with
| (m, n) => m + n
def bar₃ : Nat × Nat → Nat :=
fun (m, n) => m + n
def bar₄ (p : Nat × Nat) : Nat :=
let (m, n) := p; m + n
```

These variations are equally useful for destructing propositions:

이러한 변형들은 명제를 분해하는 데에도 똑같이 유용합니다.

```
variable (p q : Nat → Prop)
example : (∃ x, p x) → (∃ y, q y) → ∃ x y, p x ∧ q y
| ⟨x, px⟩, ⟨y, qy⟩ => ⟨x, y, px, qy⟩
example (h₀ : ∃ x, p x) (h₁ : ∃ y, q y)
: ∃ x y, p x ∧ q y :=
match h₀, h₁ with
| ⟨x, px⟩, ⟨y, qy⟩ => ⟨x, y, px, qy⟩
example : (∃ x, p x) → (∃ y, q y) → ∃ x y, p x ∧ q y :=
fun ⟨x, px⟩ ⟨y, qy⟩ => ⟨x, y, px, qy⟩
example (h₀ : ∃ x, p x) (h₁ : ∃ y, q y)
: ∃ x y, p x ∧ q y :=
let ⟨x, px⟩ := h₀
let ⟨y, qy⟩ := h₁
⟨x, y, px, qy⟩
```

## 8.11. Exercises

1. Open a namespace `Hidden` to avoid naming conflicts, and use the
   equation compiler to define addition, multiplication, and
   exponentiation on the natural numbers. Then use the equation
   compiler to derive some of their basic properties.

1. 이름 충돌을 피하기 위해 `Hidden` 네임스페이스를 열고, 방정식 컴파일러를 사용하여 자연수에 대한 덧셈, 곱셈, 거듭제곱을 정의하세요. 그 다음 방정식 컴파일러를 사용하여 그들의 기본 성질 중 일부를 유도하세요.

2. Similarly, use the equation compiler to define some basic
   operations on lists (like the `reverse` function) and prove
   theorems about lists by induction (such as the fact that
   `reverse (reverse xs) = xs` for any list `xs`).

2. 유사하게, 리스트에 대한 몇 가지 기본 연산(`reverse` 함수와 같은)을 정의하기 위해 방정식 컴파일러를 사용하고, 귀납법으로 리스트에 대한 정리(임의의 리스트 `xs`에 대해 `reverse (reverse xs) = xs`가 성립한다는 사실 등)를 증명하세요.

3. Define your own function to carry out course-of-value recursion on
   the natural numbers. Similarly, see if you can figure out how to
   define `WellFounded.fix` on your own.

3. 자연수에 대해 과정의 값 재귀(course-of-value recursion)를 수행하는 자신만의 함수를 정의하세요. 유사하게, `WellFounded.fix`를 스스로 어떻게 정의할 수 있는지 알아낼 수 있는지 보세요.

4. Following the examples in the section on [dependent pattern matching](#dependent-pattern-matching),
   define a function that will append two vectors.
   This is tricky; you will have to define an auxiliary function.

4. [의존 패턴 매칭(dependent pattern matching)](#dependent-pattern-matching) 섹션의 예제를 따라 두 벡터를 이어붙이는 함수를 정의하세요. 이것은 까다롭습니다. 보조 함수를 정의해야 할 것입니다.

5. Consider the following type of arithmetic expressions. The idea is
   that `var n` is a variable, `vₙ`, and `const n` is the
   constant whose value is `n`.

```
inductive Expr where
| const : Nat → Expr
| var : Nat → Expr
| plus : Expr → Expr → Expr
| times : Expr → Expr → Expr
deriving Repr
open Expr
def sampleExpr : Expr :=
plus (times (var 0) (const 7)) (times (const 2) (var 1))
```

```
def eval (v : Nat → Nat) : Expr → Nat
| const n => sorry
| var n => v n
| plus e₁ e₂ => sorry
| times e₁ e₂ => sorry
def sampleVal : Nat → Nat
| 0 => 5
| 1 => 6
| _ => 0
-- Try it out. You should get 47 here.
-- #eval eval sampleVal sampleExpr
```

```
def simpConst : Expr → Expr
| plus (const n₁) (const n₂) => const (n₁ + n₂)
| times (const n₁) (const n₂) => const (n₁ * n₂)
| e => e
def fuse : Expr → Expr := sorry
theorem simpConst_eq (v : Nat → Nat)
: ∀ e : Expr, eval v (simpConst e) = eval v e :=
sorry
theorem fuse_eq (v : Nat → Nat)
: ∀ e : Expr, eval v (fuse e) = eval v e :=
sorry
```

5. 다음과 같은 산술 표현식 타입을 고려해 보세요. 아이디어는 `var n`이 변수 `vₙ`이고, `const n`이 값이 `n`인 상수라는 것입니다. 여기서 `sampleExpr`은 `(v₀ * 7) + (2 * v₁)`를 나타냅니다.

각 `var n`을 `v n`으로 평가하여 그러한 표현식을 평가하는 함수를 작성하세요.

`5 + 7`과 같은 부분항을 `12`로 단순화하는 절차인 "상수 융합(constant fusion)"을 구현하세요. 보조 함수 `simpConst`를 사용하여 "fuse" 함수를 정의하세요. 덧셈이나 곱셈을 단순화하려면 먼저 인수를 재귀적으로 단순화한 다음, `simpConst`를 적용하여 결과를 단순화해 보십시오.

마지막 두 정리는 정의가 값을 보존한다는 것을 보여줍니다.
