---
title: "7. 귀납적 타입"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "theorem-proving", "type-theory"]
categories: ["programming"]
description: "귀납적 타입의 정의와 재귀자, 그리고 리스트·벡터 같은 예시로 귀납적 타입의 원리를 다룹니다."
---

We have seen that Lean's formal foundation includes basic types,
`Prop`, `Type 0`, `Type 1`, `Type 2`, ..., and allows for the formation of
dependent function types, `(x : α) → β`. In the examples, we have
also made use of additional types like `Bool`, `Nat`, and `Int`,
and type constructors, like `List`, and product, `×`. In fact, in
Lean's library, every concrete type other than the universes and every
type constructor other than dependent arrows is an instance of a general family of
type constructions known as *inductive types*. It is remarkable that
it is possible to construct a substantial edifice of mathematics based
on nothing more than the type universes, dependent arrow types, and inductive
types; everything else follows from those.

Lean의 형식적 기초가 기본 타입인 `Prop`, `Type 0`, `Type 1`, `Type 2`, ... 및 의존함수타입 `(x : α) → β`의 형성을 포함한다는 것을 알았습니다. 예제에서 `Bool`, `Nat`, `Int`와 같은 추가 타입과 `List`, 곱 `×`와 같은 타입 생성자도 사용했습니다. 실제로 Lean의 라이브러리에서 우주(universe)를 제외한 모든 구체적인 타입과 의존화살표 이외의 모든 타입 생성자는 *귀납적 타입(inductive types)*이라고 알려진 타입 구성의 일반적인 계열의 인스턴스입니다. 타입 우주, 의존화살표 타입, 귀납적 타입 이외의 아무것도 없을 수 있는 기초 위에 상당한 수학의 건축물을 구성할 수 있다는 것은 놀랄 일입니다. 다른 모든 것은 이들로부터 따라옵니다.

Intuitively, an inductive type is built up from a specified list of
constructors. In Lean, the syntax for specifying such a type is as
follows:

직관적으로, 귀납적 타입은 지정된 생성자 목록으로부터 구축됩니다. Lean에서 이러한 타입을 지정하는 구문은 다음과 같습니다:

The intuition is that each constructor specifies a way of building new
objects of `Foo`, possibly from previously constructed values. The
type `Foo` consists of nothing more than the objects that are
constructed in this way.

각 생성자는 `Foo`의 새로운 객체를 구축하는 방법을 지정하며, 이전에 구성된 값으로부터 가능합니다. `Foo` 타입은 이러한 방식으로 구성된 객체로만 구성됩니다.

We will see below that the arguments of the constructors can include
objects of type `Foo`, subject to a certain “positivity” constraint,
which guarantees that elements of `Foo` are built from the bottom
up. Roughly speaking, each `...` can be any arrow type constructed from
`Foo` and previously defined types, in which `Foo` appears, if at
all, only as the “target” of the dependent arrow type.

아래에서 생성자의 인자가 일정 "양의성(positivity)" 제약 하에 `Foo` 타입의 객체를 포함할 수 있음을 볼 것입니다. 이는 `Foo`의 요소가 밑바닥부터 구축됨을 보장합니다. 대략적으로 말해서, 각 `...`은 `Foo`와 이전에 정의된 타입들로부터 구성된 모든 화살표 타입일 수 있으며, 여기서 `Foo`는 나타나더라도 오직 의존 화살표 타입의 "목표(target)"로서만 나타납니다.

We will provide a number of examples of inductive types. We will also
consider slight generalizations of the scheme above, to mutually
defined inductive types, and so-called *inductive families*.

우리는 귀납적 타입의 여러 예제를 제공할 것입니다. 또한 위의 스키마를 약간 일반화하여 상호 정의된 귀납적 타입과 소위 *귀납적 계열(inductive families)*을 고려할 것입니다.

As with the logical connectives, every inductive type comes with
introduction rules, which show how to construct an element of the
type, and elimination rules, which show how to “use” an element of the
type in another construction. The analogy to the logical connectives
should not come as a surprise; as we will see below, they, too, are
examples of inductive type constructions. You have already seen the
introduction rules for an inductive type: they are just the
constructors that are specified in the definition of the type. The
elimination rules provide for a principle of recursion on the type,
which includes, as a special case, a principle of induction as well.

In the next chapter, we will describe Lean's function definition
package, which provides even more convenient ways to define functions
on inductive types and carry out inductive proofs. But because the
notion of an inductive type is so fundamental, we feel it is important
to start with a low-level, hands-on understanding. We will start with
some basic examples of inductive types, and work our way up to more
elaborate and complex examples.

다음 장에서는 귀납적 타입에 대한 함수를 정의하고 귀납적 증명을 수행하는 더욱 편리한 방법을 제공하는 Lean의 함수 정의 패키지를 설명할 것입니다. 그러나 귀납적 타입의 개념이 매우 기본적이기 때문에 낮은 수준의 실제적인 이해로 시작하는 것이 중요하다고 생각합니다. 귀납적 타입의 일부 기본 예제로 시작하여 더 정교하고 복잡한 예제로 나아갈 것입니다.

## 7.1. Enumerated Types

The simplest kind of inductive type is a type with a finite, enumerated list of elements.

가장 단순한 종류의 귀납적 타입은 유한하고 열거된 요소 목록을 가진 타입입니다.

```
inductive Weekday where
| sunday : Weekday
| monday : Weekday
| tuesday : Weekday
| wednesday : Weekday
| thursday : Weekday
| friday : Weekday
| saturday : Weekday
```

The `inductive` command creates a new type, `Weekday`. The
constructors all live in the `Weekday` namespace.

`inductive` 명령은 새로운 타입인 `Weekday`를 생성합니다. 모든 생성자는 `Weekday` 네임스페이스에 있습니다.

```
#check Weekday.sunday
```

```
Weekday.sunday : Weekday
```

```
#check Weekday.monday
```

```
Weekday.monday : Weekday
```

```
open Weekday
#check sunday
```

```
Weekday.sunday : Weekday
```

```
#check monday
```

```
Weekday.monday : Weekday
```

You can omit `: Weekday` when declaring the `Weekday` inductive type.

`Weekday` 귀납적 타입을 선언할 때 `: Weekday`를 생략할 수 있습니다.

```
inductive Weekday where
| sunday
| monday
| tuesday
| wednesday
| thursday
| friday
| saturday
```

Think of `sunday`, `monday`, ... , `saturday` as
being distinct elements of `Weekday`, with no other distinguishing
properties. The elimination principle, `Weekday.rec`, is defined
along with the type `Weekday` and its constructors. It is also known
as a *recursor*, and it is what makes the type “inductive”: it allows
us to define a function on `Weekday` by assigning values
corresponding to each constructor. The intuition is that an inductive
type is exhaustively generated by the constructors, and has no
elements beyond those they construct.

```
Weekday.rec.{u} {motive : Weekday → Sort u}
(sunday : motive Weekday.sunday)
(monday : motive Weekday.monday)
(tuesday : motive Weekday.tuesday)
(wednesday : motive Weekday.wednesday)
(thursday : motive Weekday.thursday)
(friday : motive Weekday.friday)
(saturday : motive Weekday.saturday)
(t : Weekday) :
motive t
```

We will use the `match` expression to define a function from `Weekday`
to the natural numbers:

`match` 식을 사용하여 `Weekday`에서 자연수로의 함수를 정의할 것입니다:

```
open Weekday
def numberOfDay (d : Weekday) : Nat :=
match d with
| sunday => 1
| monday => 2
| tuesday => 3
| wednesday => 4
| thursday => 5
| friday => 6
| saturday => 7
#eval numberOfDay Weekday.sunday
```

```
1
```

```
#eval numberOfDay Weekday.monday
```

```
2
```

```
#eval numberOfDay Weekday.tuesday
```

```
3
```

When using Lean's logic, the `match` expression is compiled using the *recursor* `Weekday.rec` generated when
you declare the inductive type. This ensures that the resulting term is well-defined in the type theory. For compiled code,
`match` is compiled as in other functional programming languages.

Lean의 논리를 사용할 때, `match` 식은 귀납적 타입을 선언할 때 생성된 *recursor* `Weekday.rec`를 사용하여 컴파일됩니다. 이는 결과 항이 타입 이론에서 잘 정의되었음을 보장합니다. 컴파일된 코드의 경우, `match`는 다른 함수형 프로그래밍 언어와 같이 컴파일됩니다.

```
open Weekday
def numberOfDay (d : Weekday) : Nat :=
match d with
| sunday => 1
| monday => 2
| tuesday => 3
| wednesday => 4
| thursday => 5
| friday => 6
| saturday => 7
set_option pp.all true
#print numberOfDay
```

```
def numberOfDay : (d : Weekday) → Nat :=
fun (d : Weekday) =>
  numberOfDay.match_1.{1} (fun (d : Weekday) => Nat) d
    (fun (_ : Unit) => @OfNat.ofNat.{0} Nat (nat_lit 1) (instOfNatNat (nat_lit 1)))
    (fun (_ : Unit) => @OfNat.ofNat.{0} Nat (nat_lit 2) (instOfNatNat (nat_lit 2)))
    (fun (_ : Unit) => @OfNat.ofNat.{0} Nat (nat_lit 3) (instOfNatNat (nat_lit 3)))
    (fun (_ : Unit) => @OfNat.ofNat.{0} Nat (nat_lit 4) (instOfNatNat (nat_lit 4)))
    (fun (_ : Unit) => @OfNat.ofNat.{0} Nat (nat_lit 5) (instOfNatNat (nat_lit 5)))
    (fun (_ : Unit) => @OfNat.ofNat.{0} Nat (nat_lit 6) (instOfNatNat (nat_lit 6))) fun (_ : Unit) =>
    @OfNat.ofNat.{0} Nat (nat_lit 7) (instOfNatNat (nat_lit 7))
```

```
#print numberOfDay.match_1
```

```
def numberOfDay.match_1.{u_1} : (motive : Weekday → Sort u_1) →
  (d : Weekday) →
    (h_1 : (a : Unit) → motive Weekday.sunday) →
      (h_2 : (a : Unit) → motive Weekday.monday) →
        (h_3 : (a : Unit) → motive Weekday.tuesday) →
          (h_4 : (a : Unit) → motive Weekday.wednesday) →
            (h_5 : (a : Unit) → motive Weekday.thursday) →
              (h_6 : (a : Unit) → motive Weekday.friday) → (h_7 : (a : Unit) → motive Weekday.saturday) → motive d :=
fun (motive : Weekday → Sort u_1) (d : Weekday) (h_1 : (a : Unit) → motive Weekday.sunday)
    (h_2 : (a : Unit) → motive Weekday.monday) (h_3 : (a : Unit) → motive Weekday.tuesday)
    (h_4 : (a : Unit) → motive Weekday.wednesday) (h_5 : (a : Unit) → motive Weekday.thursday)
    (h_6 : (a : Unit) → motive Weekday.friday) (h_7 : (a : Unit) → motive Weekday.saturday) =>
  @Weekday.casesOn.{u_1} (fun (x : Weekday) => motive x) d (h_1 Unit.unit) (h_2 Unit.unit) (h_3 Unit.unit)
    (h_4 Unit.unit) (h_5 Unit.unit) (h_6 Unit.unit) (h_7 Unit.unit)
```

```
#print Weekday.casesOn
```

```
@[reducible] def Weekday.casesOn.{u} : {motive : (t : Weekday) → Sort u} →
  (t : Weekday) →
    (sunday : motive Weekday.sunday) →
      (monday : motive Weekday.monday) →
        (tuesday : motive Weekday.tuesday) →
          (wednesday : motive Weekday.wednesday) →
            (thursday : motive Weekday.thursday) →
              (friday : motive Weekday.friday) → (saturday : motive Weekday.saturday) → motive t :=
fun {motive : (t : Weekday) → Sort u} (t : Weekday) (sunday : motive Weekday.sunday) (monday : motive Weekday.monday)
    (tuesday : motive Weekday.tuesday) (wednesday : motive Weekday.wednesday) (thursday : motive Weekday.thursday)
    (friday : motive Weekday.friday) (saturday : motive Weekday.saturday) =>
  @Weekday.rec.{u} motive sunday monday tuesday wednesday thursday friday saturday t
```

```
#check @Weekday.rec
```

```
@Weekday.rec.{u_1} : {motive : (t : Weekday) → Sort u_1} →
  (sunday : motive Weekday.sunday) →
    (monday : motive Weekday.monday) →
      (tuesday : motive Weekday.tuesday) →
        (wednesday : motive Weekday.wednesday) →
          (thursday : motive Weekday.thursday) →
            (friday : motive Weekday.friday) → (saturday : motive Weekday.saturday) → (t : Weekday) → motive t
```

When declaring an inductive datatype, you can use `deriving Repr` to instruct
Lean to generate a function that converts `Weekday` objects into text.
This function is used by the `#eval` command to display `Weekday` objects.
If no `Repr` exists, `#eval` attempts to derive one on the spot.

귀납적 데이터타입을 선언할 때 `deriving Repr`을 사용하여 Lean에 `Weekday` 객체를 텍스트로 변환하는 함수를 생성하도록 지시할 수 있습니다. 이 함수는 `#eval` 명령어로 `Weekday` 객체를 표시하는 데 사용됩니다. `Repr`이 없으면 `#eval`은 즉석에서 하나를 파생시키려고 시도합니다.

```
inductive Weekday where
| sunday
| monday
| tuesday
| wednesday
| thursday
| friday
| saturday
deriving Repr
open Weekday
#eval tuesday
```

```
Weekday.tuesday
```

It is often useful to group definitions and theorems related to a
structure in a namespace with the same name. For example, we can put
the `numberOfDay` function in the `Weekday` namespace. We are
then allowed to use the shorter name when we open the namespace.

구조와 관련된 정의와 정리를 같은 이름의 네임스페이스로 그룹화하는 것이 종종 유용합니다. 예를 들어 `numberOfDay` 함수를 `Weekday` 네임스페이스에 넣을 수 있습니다. 그러면 네임스페이스를 열 때 더 짧은 이름을 사용할 수 있습니다.

We can define functions from `Weekday` to `Weekday`:

`Weekday`에서 `Weekday`로의 함수를 정의할 수 있습니다:

```
namespace Weekday
def next (d : Weekday) : Weekday :=
match d with
| sunday => monday
| monday => tuesday
| tuesday => wednesday
| wednesday => thursday
| thursday => friday
| friday => saturday
| saturday => sunday
def previous (d : Weekday) : Weekday :=
match d with
| sunday => saturday
| monday => sunday
| tuesday => monday
| wednesday => tuesday
| thursday => wednesday
| friday => thursday
| saturday => friday
#eval next (next tuesday)
```

```
Weekday.thursday
```

```
#eval next (previous tuesday)
```

```
Weekday.tuesday
```

```
example : next (previous tuesday) = tuesday :=
rfl
end Weekday
```

How can we prove the general theorem that `next (previous d) = d`
for any Weekday `d`? You can use `match` to provide a proof of the claim for each
constructor:

`next (previous d) = d`가 모든 Weekday `d`에 대해 성립한다는 일반적인 정리를 어떻게 증명할 수 있을까요? `match`를 사용하여 각 생성자에 대한 주장의 증명을 제공할 수 있습니다:

```
theorem next_previous (d : Weekday) : next (previous d) = d :=
match d with
| sunday => rfl
| monday => rfl
| tuesday => rfl
| wednesday => rfl
| thursday => rfl
| friday => rfl
| saturday => rfl
```

Using a tactic proof, we can be even more concise:

전술 증명을 사용하면 더욱 간결하게 할 수 있습니다:

```
theorem next_previous (d : Weekday) : next (previous d) = d := by
cases d <;> rfl
```

[Tactics for Inductive Types](#tactics-for-inductive-types) below will introduce additional
tactics that are specifically designed to make use of inductive types.

Notice that, under the [propositions-as-types](../03-propositions-and-proofs/#--tech-term-propositions-as-types) correspondence, we can
use `match` to prove theorems as well as define functions. In other
words, under the [propositions-as-types](../03-propositions-and-proofs/#--tech-term-propositions-as-types) correspondence, the proof by
cases is a kind of definition by cases, where what is being “defined”
is a proof instead of a piece of data.

The `Bool` type in the Lean library is an instance of
enumerated type.

Lean 라이브러리의 `Bool` 타입은 열거된 타입의 인스턴스입니다.

```
inductive Bool where
| false : Bool
| true : Bool
```

(To run these examples, we put them in a namespace called `Hidden`,
so that a name like `Bool` does not conflict with the `Bool` in
the standard library. This is necessary because these types are part
of the Lean “prelude” that is automatically imported when the system
is started.)

As an exercise, you should think about what the introduction and
elimination rules for these types do. As a further exercise, we
suggest defining boolean operations `and`, `or`, `not` on the
`Bool` type, and verifying common identities. Note that you can define a
binary operation like `and` using `match`:

연습 문제로, 이 타입들의 도입 및 제거 규칙이 무엇을 하는지 생각해 보세요. 추가 연습 문제로, `Bool` 타입에 대한 부울 연산 `and`, `or`, `not`을 정의하고 공통 항등식을 검증하는 것을 제안합니다. `match`를 사용하여 `and`와 같은 이항 연산을 정의할 수 있음을 유의하세요:

```
def and (a b : Bool) : Bool :=
match a with
| true => b
| false => false
```

Similarly, most identities can be proved by introducing suitable `match`, and then using `rfl`.

마찬가지로 대부분의 항등식은 적절한 `match`를 도입한 다음 `rfl`을 사용하여 증명할 수 있습니다.

## 7.2. Constructors with Arguments

Enumerated types are a very special case of inductive types, in which
the constructors take no arguments at all. In general, a
“construction” can depend on data, which is then represented in the
constructed argument. Consider the definitions of the product type and
sum type in the library:

```
inductive Prod (α : Type u) (β : Type v)
| mk : α → β → Prod α β
inductive Sum (α : Type u) (β : Type v) where
| inl : α → Sum α β
| inr : β → Sum α β
```

Consider what is going on in these examples.
The product type has one constructor, `Prod.mk`,
which takes two arguments. To define a function on `Prod α β`, we
can assume the input is of the form `Prod.mk a b`, and we have to
specify the output, in terms of `a` and `b`. We can use this to
define the two projections for `Prod`. Remember that the standard
library defines notation `α × β` for `Prod α β` and `(a, b)` for
`Prod.mk a b`.

이 예제에서 무엇이 진행되고 있는지 고려해보세요. 곱 타입은 하나의 생성자인 `Prod.mk`를 가지며, 이는 두 개의 인자를 취합니다. `Prod α β`에 대한 함수를 정의하기 위해 입력이 `Prod.mk a b` 형식이라고 가정할 수 있으며, `a`와 `b` 관점에서 출력을 지정해야 합니다. 이를 사용하여 `Prod`의 두 투영을 정의할 수 있습니다. 표준 라이브러리가 `Prod α β`에 대한 표기법 `α × β`와 `Prod.mk a b`에 대한 `(a, b)`를 정의한다는 것을 기억하세요.

```
def fst {α : Type u} {β : Type v} (p : Prod α β) : α :=
match p with
| Prod.mk a b => a
def snd {α : Type u} {β : Type v} (p : Prod α β) : β :=
match p with
| Prod.mk a b => b
```

The function `fst` takes a pair, `p`. The `match` interprets
`p` as a pair, `Prod.mk a b`. Recall also from [Dependent Type Theory](../02-dependent-type-theory/#dependent-type-theory)
that to give these definitions the greatest generality possible, we allow
the types `α` and `β` to belong to any universe.

함수 `fst`는 쌍 `p`를 취합니다. `match`는 `p`를 쌍 `Prod.mk a b`로 해석합니다. [의존 타입 이론(Dependent Type Theory)](../02-dependent-type-theory/#dependent-type-theory)에서 이 정의들에 최대한 일반성을 주기 위해 타입 `α`와 `β`가 모든 우주에 속하도록 허용한다는 것을 기억하세요.

Here is another example where we use the recursor `Prod.casesOn` instead
of `match`.

여기 `match` 대신 recursor `Prod.casesOn`을 사용하는 또 다른 예가 있습니다.

```
def prod_example (p : Bool × Nat) : Nat :=
Prod.casesOn (motive := fun _ => Nat) p
(fun b n => cond b (2 * n) (2 * n + 1))
#eval prod_example (true, 3)
```

```
6
```

```
#eval prod_example (false, 3)
```

```
7
```

The argument `motive` is used to specify the type of the object you want to
construct, and it is a function because it may depend on the pair.
The `cond` function is a boolean conditional: `cond b t1 t2`
returns `t1` if `b` is true, and `t2` otherwise.
The function `prod_example` takes a pair consisting of a boolean,
`b`, and a number, `n`, and returns either `2 * n` or `2 * n + 1`
according to whether `b` is true or false.

인자 `motive`는 구성하려는 객체의 타입을 지정하는 데 사용되며, 쌍에 의존할 수 있기 때문에 함수입니다. `cond` 함수는 부울 조건문입니다: `cond b t1 t2`는 `b`가 참이면 `t1`을 반환하고, 그렇지 않으면 `t2`를 반환합니다. 함수 `prod_example`은 부울 `b`와 수 `n`으로 이루어진 쌍을 취하고 `b`가 참 또는 거짓인지에 따라 `2 * n` 또는 `2 * n + 1`을 반환합니다.

In contrast, the sum type has *two* constructors, `inl` and `inr`
(for “insert left” and “insert right”), each of which takes *one*
(explicit) argument. To define a function on `Sum α β`, we have to
handle two cases: either the input is of the form `inl a`, in which
case we have to specify an output value in terms of `a`, or the
input is of the form `inr b`, in which case we have to specify an
output value in terms of `b`.

대조적으로, 합 타입(sum type)은 `inl`과 `inr`("왼쪽 삽입" 및 "오른쪽 삽입"을 의미)이라는 두 개의 생성자를 가지며, 각각은 하나의 (명시적) 인자를 취합니다. `Sum α β`에 대한 함수를 정의하려면 두 가지 경우를 처리해야 합니다: 입력이 `inl a` 형식인 경우 `a`에 대한 출력 값을 지정해야 하고, 입력이 `inr b` 형식인 경우 `b`에 대한 출력 값을 지정해야 합니다.

```
def sum_example (s : Sum Nat Nat) : Nat :=
Sum.casesOn (motive := fun _ => Nat) s
(fun n => 2 * n)
(fun n => 2 * n + 1)
#eval sum_example (Sum.inl 3)
```

```
6
```

```
#eval sum_example (Sum.inr 3)
```

```
7
```

This example is similar to the previous one, but now an input to
`sum_example` is implicitly either of the form `inl n` or `inr n`.
In the first case, the function returns `2 * n`, and the second
case, it returns `2 * n + 1`.

이 예제는 이전 예제와 유사하지만, 이제 `sum_example`에 대한 입력은 암시적으로 `inl n` 또는 `inr n` 형식입니다. 첫 번째 경우 함수는 `2 * n`을 반환하고, 두 번째 경우 `2 * n + 1`을 반환합니다.

Notice that the product type depends on parameters `α β : Type`
which are arguments to the constructors as well as `Prod`. Lean
detects when these arguments can be inferred from later arguments to a
constructor or the return type, and makes them implicit in that case.

곱 타입이 `Prod`뿐만 아니라 생성자에 대한 인자인 매개변수 `α β : Type`에 의존한다는 것을 주목하세요. Lean은 이 인자가 생성자에 대한 나중 인자나 반환 타입으로부터 유추될 수 있는 경우를 감지하고 이 경우 암시적으로 만듭니다.

In [Defining the Natural Numbers](#defining-the-natural-numbers)
we will see what happens when the
constructor of an inductive type takes arguments from the inductive
type itself. What characterizes the examples we consider in this
section is that each constructor relies only on previously specified types.

[자연수 정의(Defining the Natural Numbers)](#defining-the-natural-numbers)에서 귀납적 타입의 생성자가 귀납적 타입 자신의 인자를 취하는 경우를 볼 것입니다. 이 섹션에서 고려하는 예제를 특징지우는 것은 각 생성자가 이전에 지정된 타입에만 의존한다는 것입니다.

Notice that a type with multiple constructors is disjunctive: an
element of `Sum α β` is either of the form `inl a` *or* of the
form `inl b`. A constructor with multiple arguments introduces
conjunctive information: from an element `Prod.mk a b` of
`Prod α β` we can extract `a` *and* `b`. An arbitrary inductive type can
include both features, by having any number of constructors, each of
which takes any number of arguments.

여러 생성자를 가진 타입은 분리 연언입니다: `Sum α β`의 요소는 `inl a` 형식 *또는* `inl b` 형식입니다. 여러 인자를 가진 생성자는 연언적 정보를 도입합니다: `Prod α β`의 요소 `Prod.mk a b`로부터 `a` *그리고* `b`를 추출할 수 있습니다. 임의의 귀납적 타입은 모든 개수의 생성자를 가지고 각각이 모든 개수의 인자를 취함으로써 두 기능을 모두 포함할 수 있습니다.

As with function definitions, Lean's inductive definition syntax will
let you put named arguments to the constructors before the colon:

함수 정의와 마찬가지로 Lean의 귀납적 정의 구문을 사용하면 생성자의 명명된 인자를 콜론 앞에 넣을 수 있습니다:

```
inductive Prod (α : Type u) (β : Type v) where
| mk (fst : α) (snd : β) : Prod α β
inductive Sum (α : Type u) (β : Type v) where
| inl (a : α) : Sum α β
| inr (b : β) : Sum α β
```

The results of these definitions are essentially the same as the ones given earlier in this section.

이 정의들의 결과는 이 섹션의 앞부분에서 주어진 것과 본질적으로 동일합니다.

A type, like `Prod`, that has only one constructor is purely
conjunctive: the constructor simply packs the list of arguments into a
single piece of data, essentially a tuple where the type of subsequent
arguments can depend on the type of the initial argument. We can also
think of such a type as a “record” or a “structure”. In Lean, the
keyword `structure` can be used to define such an inductive type as
well as its projections, at the same time.

`Prod`처럼 생성자가 하나뿐인 타입은 순수하게 연언적(conjunctive)입니다: 생성자는 단순히 인자 목록을 하나의 데이터 조각으로 묶으며, 본질적으로 후속 인자의 타입이 초기 인자의 타입에 의존할 수 있는 튜플입니다. 이러한 타입을 "레코드(record)" 또는 "구조(structure)"라고 생각할 수도 있습니다. Lean에서 `structure` 키워드는 이러한 귀납적 타입과 그 투영을 동시에 정의하는 데 사용될 수 있습니다.

```
structure Prod (α : Type u) (β : Type v) where
mk ::
fst : α
snd : β
```

This example simultaneously introduces the inductive type, `Prod`,
its constructor, `mk`, the usual eliminators (`rec` and
`recOn`), as well as the projections, `fst` and `snd`, as
defined above.

이 예제는 동시에 귀납적 타입 `Prod`, 그 생성자 `mk`, 통상적인 제거자들(`rec`과 `recOn`), 그리고 위에 정의된 투영 `fst`와 `snd`를 소개합니다.

If you do not name the constructor, Lean uses `mk` as a default. For
example, the following defines a record to store a color as a triple
of RGB values:

생성자에 이름을 지정하지 않으면 Lean은 `mk`를 기본값으로 사용합니다. 예를 들어 다음은 색상을 RGB 값의 트리플로 저장하기 위한 기록을 정의합니다:

```
structure Color where
red : Nat
green : Nat
blue : Nat
deriving Repr
def yellow := Color.mk 255 255 0
#eval Color.red yellow
```

```
255
```

The definition of `yellow` forms the record with the three values
shown, and the projection `Color.red` returns the red component.

`yellow`의 정의는 표시된 세 값으로 기록을 형성하고, 투영 `Color.red`는 빨강 성분을 반환합니다.

The `structure` command is especially useful for defining algebraic
structures, and Lean provides substantial infrastructure to support
working with them. Here, for example, is the definition of a
semigroup:

`structure` 명령은 대수 구조를 정의하는 데 특히 유용하며, Lean은 그들과 함께 작업하는 것을 지원하기 위한 상당한 인프라를 제공합니다. 예를 들어 여기 반군의 정의가 있습니다:

```
structure Semigroup where
carrier : Type u
mul : carrier → carrier → carrier
mul_assoc : ∀ a b c, mul (mul a b) c = mul a (mul b c)
```

We will see more examples in the chapter on [structures and records](../09-structures-and-records/#structures-and-records).

[구조와 기록(structures and records)](../09-structures-and-records/#structures-and-records)에 관한 장에서 더 많은 예를 볼 것입니다.

We have already discussed the dependent product type `Sigma`:

우리는 이미 의존 곱 타입 `Sigma`를 논의했습니다:

```
inductive Sigma {α : Type u} (β : α → Type v) where
| mk : (a : α) → β a → Sigma β
```

Two more examples of inductive types in the library are the following:

라이브러리의 귀납적 타입의 두 가지 더 많은 예는 다음과 같습니다:

```
inductive Option (α : Type u) where
| none : Option α
| some : α → Option α
inductive Inhabited (α : Type u) where
| mk : α → Inhabited α
```

In the semantics of dependent type theory, there is no built-in notion
of a partial function. Every element of a function type `α → β` or a
dependent function type `(a : α) → β` is assumed to have a value
at every input. The `Option` type provides a way of representing partial functions. An
element of `Option β` is either `none` or of the form `some b`,
for some value `b : β`. Thus we can think of an element `f` of the
type `α → Option β` as being a partial function from `α` to `β`:
for every `a : α`, `f a` either returns `none`, indicating
`f a` is “undefined”, or `some b`.

의존 타입 이론의 의미론에서 부분 함수의 내장된 개념은 없습니다. 함수 타입 `α → β` 또는 의존 함수 타입 `(a : α) → β`인 모든 요소는 모든 입력에서 값을 가진다고 가정됩니다. `Option` 타입은 부분 함수를 표현하는 방법을 제공합니다. `Option β`의 요소는 `none`이거나 어떤 값 `b : β`에 대해 `some b` 형식입니다. 따라서 우리는 타입 `α → Option β`의 요소 `f`를 `α`에서 `β`로의 부분 함수로 생각할 수 있습니다: 모든 `a : α`에 대해 `f a`는 `f a`가 "정의되지 않음"을 나타내는 `none`을 반환하거나 `some b`를 반환합니다.

An element of `Inhabited α` is simply a witness to the fact that
there is an element of `α`. Later, we will see that `Inhabited` is
an example of a *type class* in Lean: Lean can be instructed that
suitable base types are inhabited, and can automatically infer that
other constructed types are inhabited on that basis.

`Inhabited α`의 요소는 단순히 `α`의 요소가 있다는 사실에 대한 증거입니다. 나중에 `Inhabited`은 Lean의 *타입 클래스*의 예임을 볼 것입니다: Lean은 적절한 기본 타입이 inhabited(공집합이 아닌)되어 있다고 지시할 수 있으며, 그 기초 위에 다른 구성된 타입이 inhabited(공집합이 아닌)되어 있다고 자동으로 추론할 수 있습니다.

As exercises, we encourage you to develop a notion of composition for
partial functions from `α` to `β` and `β` to `γ`, and show
that it behaves as expected. We also encourage you to show that
`Bool` and `Nat` are inhabited, that the product of two inhabited
types is inhabited, and that the type of functions to an inhabited
type is inhabited.

연습 문제로, `α`에서 `β`로의 부분 함수와 `β`에서 `γ`로의 부분 함수의 합성 개념을 개발하고 예상대로 동작함을 보이도록 권장합니다. 또한 `Bool`과 `Nat`이 inhabited(공집합이 아닌)되어 있음을 보이고, 두 inhabited(공집합이 아닌)된 타입의 곱이 inhabited(공집합이 아닌)되어 있음을 보이고, inhabited(공집합이 아닌)된 타입으로의 함수 타입이 inhabited(공집합이 아닌)되어 있음을 보이도록 권장합니다.

## 7.3. Inductively Defined Propositions

Inductively defined types can live in any type universe, including the
bottom-most one, `Prop`. In fact, this is exactly how the logical
connectives are defined.

귀납적으로 정의된 타입은 최하위인 `Prop`을 포함한 모든 타입 우주에서 존재할 수 있습니다. 실제로 이것이 논리적 결합자가 정의되는 방식입니다.

```
inductive False : Prop
inductive True : Prop where
| intro : True
inductive And (a b : Prop) : Prop where
| intro : a → b → And a b
inductive Or (a b : Prop) : Prop where
| inl : a → Or a b
| inr : b → Or a b
```

You should think about how these give rise to the introduction and
elimination rules that you have already seen. There are rules that
govern what the eliminator of an inductive type can eliminate *to*,
that is, what kinds of types can be the target of a recursor. Roughly
speaking, what characterizes inductive types in `Prop` is that one
can only eliminate to other types in `Prop`. This is consistent with
the understanding that if `p : Prop`, an element `hp : p` carries
no data. There is a small exception to this rule, however, which we
will discuss below, in [Inductive Families](#inductive-families).

이것이 이미 본 도입 및 제거 규칙을 어떻게 생성하는지 생각해보세요. 귀납적 타입의 제거자가 제거할 수 있는 *대상*, 즉 recursor의 대상이 될 수 있는 타입의 종류를 지배하는 규칙이 있습니다. 대략적으로 `Prop`의 귀납적 타입을 특징짓는 것은 `Prop`의 다른 타입으로만 제거할 수 있다는 것입니다. 이는 `p : Prop`이면 요소 `hp : p`가 데이터를 포함하지 않는다는 이해와 일치합니다. 그러나 이 규칙에는 작은 예외가 있으며, 이는 [귀납적 계열(Inductive Families)](#inductive-families)에서 아래에서 논의할 것입니다.

Even the existential quantifier is inductively defined:

심지어 존재 량화자도 귀납적으로 정의됩니다:

```
inductive Exists {α : Sort u} (p : α → Prop) : Prop where
| intro (w : α) (h : p w) : Exists p
```

Keep in mind that the notation `∃ x : α, p` is syntactic sugar for `Exists (fun x : α => p)`.

`∃ x : α, p` 표기법이 `Exists (fun x : α => p)`의 구문 설탕이라는 것을 기억하세요.

The definitions of `False`, `True`, `And`, and `Or` are
perfectly analogous to the definitions of `Empty`, `Unit`,
`Prod`, and `Sum`. The difference is that the first group yields
elements of `Prop`, and the second yields elements of `Type u` for
some `u`. In a similar way, `∃ x : α, p` is a `Prop`-valued
variant of `Σ x : α, β`.

`False`, `True`, `And`, `Or`의 정의는 `Empty`, `Unit`, `Prod`, `Sum`의 정의와 완벽하게 유사합니다. 차이점은 첫 번째 그룹은 `Prop`의 요소를 생성하고 두 번째는 일부 `u`에 대해 `Type u`의 요소를 생성한다는 것입니다. 유사하게, `∃ x : α, p`는 `Σ x : α, β`의 `Prop`-값 변형입니다.

This is a good place to mention another inductive type, denoted
`{x : α / p}`, which is sort of a hybrid between
`∃ x : α, p` and `Σ x : α, β`.

이것은 `∃ x : α, p`와 `Σ x : α, β` 사이의 일종의 하이브리드인 `{x : α / p}`로 표기되는 또 다른 귀납적 타입을 언급할 좋은 장소입니다.

```
inductive Subtype {α : Type u} (p : α → Prop) where
| mk : (x : α) → p x → Subtype p
```

In fact, in Lean, `Subtype` is defined using the structure command:

```
structure Subtype {α : Sort u} (p : α → Prop) where
val : α
property : p val
```

The notation `{x : α // p x}` is syntactic sugar for `Subtype (fun x : α => p x)`. It is modeled after subset notation in set theory: the idea is that `{x : α // p x}` denotes the collection of elements of `α` that have property `p`.

실제로 Lean에서 `Subtype`은 structure 명령을 사용하여 정의됩니다:

`{x : α / p x}` 표기법은 `Subtype (fun x : α => p x)`의 구문 설탕입니다. 집합 이론의 부분집합 표기법을 모델로 합니다: 아이디어는 `{x : α / p x}`이 속성 `p`를 갖는 `α`의 요소의 모음을 나타낸다는 것입니다.

## 7.4. Defining the Natural Numbers

The inductively defined types we have seen so far are “flat”:
constructors wrap data and insert it into a type, and the
corresponding recursor unpacks the data and acts on it. Things get
much more interesting when the constructors act on elements of the
very type being defined. A canonical example is the type `Nat` of
natural numbers:

```
inductive Nat where
| zero : Nat
| succ : Nat → Nat
```

There are two constructors. We start with `zero : Nat`; it takes
no arguments, so we have it from the start. In contrast, the
constructor `succ` can only be applied to a previously constructed
`Nat`. Applying it to `zero` yields `succ zero : Nat`. Applying
it again yields `succ (succ zero) : Nat`, and so on. Intuitively,
`Nat` is the “smallest” type with these constructors, meaning that
it is exhaustively (and freely) generated by starting with `zero`
and applying `succ` repeatedly.

두 개의 생성자가 있습니다. `zero : Nat`으로 시작합니다. 이는 인자를 취하지 않으므로 처음부터 가지고 있습니다. 대조적으로 생성자 `succ`은 이전에 구성된 `Nat`에만 적용될 수 있습니다. 이를 `zero`에 적용하면 `succ zero : Nat`이 나옵니다. 다시 적용하면 `succ (succ zero) : Nat`이 나옵니다. 직관적으로 `Nat`은 이러한 생성자를 가진 "가장 작은" 타입이며, 이는 `zero`로 시작하여 `succ`을 반복적으로 적용함으로써 남김없이 (그리고 자유롭게) 생성된다는 것을 의미합니다.

As before, the recursor for `Nat` is designed to define a dependent
function `f` from `Nat` to any domain, that is, an element `f`
of `(n : Nat) → motive n` for some `motive : Nat → Sort u`.
It has to handle two cases: the case where the input is `zero`, and the case where
the input is of the form `succ n` for some `n : Nat`. In the first
case, we simply specify a target value with the appropriate type, as
before. In the second case, however, the recursor can assume that a
value of `f` at `n` has already been computed. As a result, the
next argument to the recursor specifies a value for `f (succ n)` in
terms of `n` and `f n`. If we check the type of the recursor,
you find the following:

이전과 같이, `Nat`의 recursor는 의존 함수 `f`를 `Nat`에서 모든 도메인으로 정의하도록 설계되었습니다, 즉, 일부 `motive : Nat → Sort u`에 대해 `(n : Nat) → motive n`의 요소 `f`입니다. 두 경우를 처리해야 합니다: 입력이 `zero`인 경우와 입력이 일부 `n : Nat`에 대해 `succ n` 형식인 경우입니다. 첫 번째 경우 이전과 같이 적절한 타입의 대상 값을 단순히 지정합니다. 그러나 두 번째 경우 recursor는 `n`에서 `f`의 값이 이미 계산되었다고 가정할 수 있습니다. 결과적으로 recursor의 다음 인자는 `n`과 `f n`에 관한 `f (succ n)`의 값을 지정합니다. recursor의 타입을 확인하면 다음을 찾습니다:

```
Nat.rec.{u} :
{motive : Nat → Sort u} →
(zero : motive Nat.zero) →
(succ : (n : Nat) → motive n → motive (Nat.succ n)) →
(t : Nat) → motive t
```

The implicit argument, `motive`, is the codomain of the function being defined.
In type theory it is common to say `motive` is the *motive* for the elimination/recursion,
since it describes the kind of object we wish to construct.
The next two arguments specify how to compute the zero and successor cases, as described above.
They are also known as the *minor premises*.
Finally, the `t : Nat` is the input to the function. It is also known as the *major premise*.

암시적 인자 `motive`는 정의되는 함수의 공역입니다. 타입 이론에서 `motive`이 제거/재귀의 *동기(motive)*라고 말하는 것이 일반적입니다, 우리가 구성하려는 객체의 종류를 설명하기 때문입니다. 다음 두 인자는 위에서 설명한 대로 0과 successor 경우를 계산하는 방법을 지정합니다. 이들은 또한 *부 전제(minor premises)*로 알려져 있습니다. 마지막으로 `t : Nat`은 함수의 입력입니다. 이는 또한 *주 전제(major premise)*로 알려져 있습니다.

The `Nat.recOn` is similar to `Nat.rec` but the major premise occurs before the minor premises.

`Nat.recOn`은 `Nat.rec`와 유사하지만 주 전제가 부 전제 이전에 나타납니다.

```
Nat.recOn.{u} :
{motive : Nat → Sort u} →
(t : Nat) →
(zero : motive Nat.zero) →
(succ : ((n : Nat) → motive n → motive (Nat.succ n))) →
motive t
```

Consider, for example, the addition function `add m n` on the
natural numbers. Fixing `m`, we can define addition by recursion on
`n`. In the base case, we set `add m zero` to `m`. In the
successor step, assuming the value `add m n` is already determined,
we define `add m (succ n)` to be `succ (add m n)`.

예를 들어, 자연수에 대한 더하기 함수 `add m n`을 고려하세요. `m`을 고정하여 `n`에 대한 재귀로 더하기를 정의할 수 있습니다. 기본 경우에 `add m zero`를 `m`으로 설정합니다. successor 단계에서 `add m n` 값이 이미 결정되었다고 가정하고 `add m (succ n)`을 `succ (add m n)`으로 정의합니다.

```
inductive Nat where
| zero : Nat
| succ : Nat → Nat
deriving Repr
def add (m n : Nat) : Nat :=
match n with
| Nat.zero => m
| Nat.succ n => Nat.succ (add m n)
open Nat
#eval add (succ (succ zero)) (succ zero)
```

```
Hidden.Nat.succ (Hidden.Nat.succ (Hidden.Nat.succ (Hidden.Nat.zero)))
```

It is useful to put such definitions into a namespace, `Nat`. We can
then go on to define familiar notation in that namespace. The two
defining equations for addition now hold definitionally:

그러한 정의를 네임스페이스 `Nat`에 넣는 것이 유용합니다. 그러면 그 네임스페이스에서 친숙한 표기법을 정의할 수 있습니다. 더하기에 대한 두 정의 방정식은 이제 정의적으로 유지됩니다:

```
namespace Nat
def add (m n : Nat) : Nat :=
match n with
| Nat.zero => m
| Nat.succ n => Nat.succ (add m n)
instance : Add Nat where
add := add
theorem add_zero (m : Nat) : m + zero = m := rfl
theorem add_succ (m n : Nat) : m + succ n = succ (m + n) := rfl
end Nat
```

We will explain how the `instance` command works in
the [Type Classes](../10-type-classes/#type-classes) chapter. In the examples below, we will use
Lean's version of the natural numbers.

`instance` 명령이 어떻게 작동하는지 [타입 클래스(Type Classes)](../10-type-classes/#type-classes) 장에서 설명할 것입니다. 아래의 예제에서 Lean의 자연수 버전을 사용할 것입니다.

Proving a fact like `0 + n = n`, however, requires a proof by induction.
As observed above, the induction principle is just a special case of the recursion principle,
when the codomain `motive n` is an element of `Prop`. It represents the familiar
pattern of an inductive proof: to prove `∀ n, motive n`, first prove `motive 0`,
and then, for arbitrary `n`, assume `ih : motive n` and prove `motive (n + 1)`.

그러나 `0 + n = n`과 같은 사실을 증명하려면 귀납법에 의한 증명이 필요합니다. 위에서 관찰한 바와 같이, 귀납 원리는 공역 `motive n`이 `Prop`의 요소일 때 재귀 원리의 특수한 경우입니다. 귀납적 증명의 친숙한 패턴을 나타냅니다: `∀ n, motive n`을 증명하려면 먼저 `motive 0`을 증명하고, 그 다음 임의의 `n`에 대해 `ih : motive n`을 가정하고 `motive (n + 1)`을 증명합니다.

```
open Nat
theorem zero_add (n : Nat) : 0 + n = n :=
Nat.recOn (motive := fun x => 0 + x = x)
n
(show 0 + 0 = 0 from rfl)
(fun (n : Nat) (ih : 0 + n = n) =>
show 0 + (n + 1) = n + 1 from
calc 0 + (n + 1)
_ = (0 + n) + 1 := rfl
_ = n + 1 := by rw [ih])
```

Notice that, once again, when `Nat.recOn` is used in the context of
a proof, it is really the induction principle in disguise. The
`rw` and `simp` tactics tend to be very effective in proofs
like these. In this case, each can be used to reduce the proof to:

다시 한 번, `Nat.recOn`이 증명의 맥락에서 사용될 때, 이는 정말로 위장된 귀납 원리입니다. `rw`와 `simp` 전술은 이와 같은 증명에서 매우 효과적입니다. 이 경우 각각은 증명을 다음과 같이 축소하는 데 사용될 수 있습니다:

```
open Nat
theorem zero_add (n : Nat) : 0 + n = n :=
Nat.recOn (motive := fun x => 0 + x = x) n
rfl
(fun n ih => by simp [ih])
```

As another example, let us prove the associativity of addition,
`∀ m n k, m + n + k = m + (n + k)`.
(The notation `+`, as we have defined it, associates to the left, so `m + n + k` is really `(m + n) + k`.)
The hardest part is figuring out which variable to do the induction on. Since addition is defined by recursion on the second argument,
`k` is a good guess, and once we make that choice the proof almost writes itself:

또 다른 예로, 더하기의 연관성, `∀ m n k, m + n + k = m + (n + k)`을 증명해봅시다. (우리가 정의한 표기법 `+`는 왼쪽으로 연관되므로 `m + n + k`는 실제로 `(m + n) + k`입니다.) 가장 어려운 부분은 어느 변수에 대해 귀납법을 수행할지 알아내는 것입니다. 더하기가 두 번째 인자에 대한 재귀로 정의되므로, `k`는 좋은 추측이고 그 선택을 하면 증명이 거의 자동으로 작성됩니다:

```
open Nat
theorem add_assoc (m n k : Nat) : m + n + k = m + (n + k) :=
Nat.recOn (motive := fun k => m + n + k = m + (n + k)) k
(show m + n + 0 = m + (n + 0) from rfl)
(fun k (ih : m + n + k = m + (n + k)) =>
show m + n + (k + 1) = m + (n + (k + 1)) from
calc m + n + (k + 1)
_ = (m + n + k) + 1 := rfl
_ = (m + (n + k)) + 1 := by rw [ih]
_ = m + ((n + k) + 1) := rfl
_ = m + (n + (k + 1)) := rfl)
```

Once again, you can reduce the proof to:

다시 한 번 증명을 다음과 같이 축소할 수 있습니다:

```
open Nat
theorem add_assoc (m n k : Nat) : m + n + k = m + (n + k) :=
Nat.recOn (motive := fun k => m + n + k = m + (n + k)) k
rfl
(fun k ih => by simp [add_succ (m + n) k, ih]; rfl)
```

Suppose we try to prove the commutativity of addition. Choosing induction on the second argument, we might begin as follows:

더하기의 교환성을 증명하려고 시도한다고 가정합시다. 두 번째 인자에 대한 귀납법을 선택하면 다음과 같이 시작할 수 있습니다:

```
open Nat
theorem add_comm (m n : Nat) : m + n = n + m :=
Nat.recOn (motive := fun x => m + x = x + m) n
(show m + 0 = 0 + m by rw [Nat.zero_add, Nat.add_zero])
(fun (n : Nat) (ih : m + n = n + m) =>
show m + succ n = succ n + m from
calc m + succ n
_ = succ (m + n) := rfl
_ = succ (n + m) := by rw [ih]
_ = succ n + m := sorry)
```

At this point, we see that we need another supporting fact, namely, that `succ (n + m)` `=` `succ n + m`.
You can prove this by induction on `m`:

이 시점에서 우리는 또 다른 지원 사실이 필요함을 봅니다, 즉, `succ (n + m)` `=` `succ n + m`입니다. `m`에 대한 귀납법으로 이를 증명할 수 있습니다:

```
open Nat
theorem succ_add (n m : Nat) : succ n + m = succ (n + m) :=
Nat.recOn (motive := fun x => succ n + x = succ (n + x)) m
(show succ n + 0 = succ (n + 0) from rfl)
(fun (m : Nat) (ih : succ n + m = succ (n + m)) =>
show succ n + succ m = succ (n + succ m) from
calc succ n + succ m
_ = succ (succ n + m) := rfl
_ = succ (succ (n + m)) := by rw [ih]
_ = succ (n + succ m) := rfl)
```

You can then replace the `sorry` in the previous proof with `succ_add`. Yet again, the proofs can be compressed:

그러면 이전 증명의 `sorry`를 `succ_add`로 바꿀 수 있습니다. 또 다시, 증명은 압축될 수 있습니다:

```
open Nat
theorem succ_add (n m : Nat) : succ n + m = succ (n + m) :=
Nat.recOn (motive := fun x => succ n + x = succ (n + x)) m
rfl
(fun m ih => by simpa [add_succ (succ n)])
theorem add_comm (m n : Nat) : m + n = n + m :=
Nat.recOn (motive := fun x => m + x = x + m) n
(by simp [add_zero, zero_add])
(fun m ih => by simp_all [succ_add, add_succ])
```

## 7.5. Other Recursive Data Types

Let us consider some more examples of inductively defined types. For
any type, `α`, the type `List α` of lists of elements of `α` is
defined in the library.

귀납적으로 정의된 타입의 더 많은 예를 고려해봅시다. 모든 타입 `α`에 대해, 타입 `α`의 요소 목록의 타입 `List α`는 라이브러리에 정의됩니다.

```
inductive List (α : Type u) where
| nil : List α
| cons (h : α) (t : List α) : List α
namespace List
def append (as bs : List α) : List α :=
match as with
| nil => bs
| cons a as => cons a (append as bs)
theorem nil_append (as : List α) : append nil as = as :=
rfl
theorem cons_append (a : α) (as bs : List α) :
append (cons a as) bs = cons a (append as bs) :=
rfl
end List
```

A list of elements of type `α` is either the empty list, `nil`, or
an element `h : α` followed by a list `t : List α`.
The first element, `h`, is commonly known as the “head” of the list,
and the remainder, `t`, is known as the “tail.”

As an exercise, prove the following:

연습 문제로 다음을 증명하세요:

```
theorem append_nil (as : List α) :
append as nil = as :=
sorry
theorem append_assoc (as bs cs : List α) :
append (append as bs) cs = append as (append bs cs) :=
sorry
```

Try also defining the function `length : {α : Type u} → List α → Nat` that returns the length of a list,
and prove that it behaves as expected (for example, `length (append as bs) = length as + length bs`).

또한 목록의 길이를 반환하는 함수 `length : {α : Type u} → List α → Nat`을 정의하고 예상대로 동작함을 증명해보세요 (예: `length (append as bs) = length as + length bs`).

For another example, we can define the type of binary trees:

다른 예로, 이진 트리의 타입을 정의할 수 있습니다:

```
inductive BinaryTree where
| leaf : BinaryTree
| node : BinaryTree → BinaryTree → BinaryTree
```

In fact, we can even define the type of countably branching trees:

실제로 우리는 가산 분지 트리의 타입을 정의할 수도 있습니다:

```
inductive CBTree where
| leaf : CBTree
| sup : (Nat → CBTree) → CBTree
namespace CBTree
def succ (t : CBTree) : CBTree :=
sup (fun _ => t)
def toCBTree : Nat → CBTree
| 0 => leaf
| n+1 => succ (toCBTree n)
def omega : CBTree :=
sup toCBTree
end CBTree
```

## 7.6. Tactics for Inductive Types

Given the fundamental importance of inductive types in Lean, it should
not be surprising that there are a number of tactics designed to work
with them effectively. We describe some of them here.

Lean에서 귀납적 타입의 기본적인 중요성을 고려하면, 그들과 효과적으로 작동하도록 설계된 여러 전술이 있다는 것은 놀라운 일이 아닙니다. 우리는 여기서 일부를 설명합니다.

The `cases` tactic works on elements of an inductively defined type,
and does what the name suggests: it decomposes the element according
to each of the possible constructors. In its most basic form, it is
applied to an element `x` in the local context. It then reduces the
goal to cases in which `x` is replaced by each of the constructions.

`cases` 전술은 귀납적으로 정의된 타입의 요소에 작동하며 이름이 시사하는 것을 수행합니다: 각 가능한 생성자에 따라 요소를 분해합니다. 가장 기본적인 형식에서, 이는 로컬 컨텍스트의 요소 `x`에 적용됩니다. 그러면 `x`가 각 구성으로 바뀌는 경우로 목표를 축소합니다.

```
example (p : Nat → Prop)
(hz : p 0) (hs : ∀ n, p (Nat.succ n)) :
∀ n, p n := by
intro n
cases n
. exact hz
. apply hs
```

In the first branch, the proof state is:

첫 번째 분기에서 증명 상태는:

In the second branch, it is:

두 번째 분기에서 이는:

There are extra bells and whistles. For one thing, `cases` allows
you to choose the names for each alternative using a
`with` clause. In the next example, for example, we choose the name
`m` for the argument to `succ`, so that the second case refers to
`succ m`. More importantly, the cases tactic will detect any items
in the local context that depend on the target variable. It reverts
these elements, does the split, and reintroduces them. In the example
below, notice that the hypothesis `h : n ≠ 0` becomes `h : 0 ≠ 0`
in the first branch, and `h : m + 1 ≠ 0` in the second.

추가 기능들이 있습니다. 한 가지는 `cases`를 사용하면 `with` 절을 사용하여 각 대안의 이름을 선택할 수 있습니다. 예를 들어, 다음 예제에서는 `succ`의 인자에 대해 이름 `m`을 선택하여 두 번째 경우가 `succ m`을 참조합니다. 더 중요하게는 cases 전술은 대상 변수에 의존하는 로컬 컨텍스트의 모든 항목을 감지합니다. 이 요소들을 되돌리고 분할을 수행한 다음 다시 도입합니다. 아래의 예제에서 가설 `h : n ≠ 0`이 첫 번째 분기에서 `h : 0 ≠ 0`이 되고 두 번째 분기에서 `h : m + 1 ≠ 0`이 됨을 주목하세요.

```
open Nat
example (n : Nat) (h : n ≠ 0) : succ (pred n) = n := by
cases n with
| zero =>
apply absurd rfl h
| succ m =>
rfl
```

Notice that `cases` can be used to produce data as well as prove propositions.

`cases`가 명제를 증명할 뿐만 아니라 데이터를 생성하는 데 사용될 수 있음을 주목하세요.

```
def f (n : Nat) : Nat := by
cases n; exact 3; exact 7
example : f 0 = 3 := rfl
example : f 5 = 7 := rfl
```

Once again, cases will revert, split, and then reintroduce dependencies in the context.

다시 한 번, cases는 컨텍스트의 의존성을 되돌리고 분할한 다음 다시 도입합니다.

```
def Tuple (α : Type) (n : Nat) :=
{ as : List α // as.length = n }
def f {n : Nat} (t : Tuple α n) : Nat := by
cases n; exact 3; exact 7
def myTuple : Tuple Nat 3 :=
⟨[0, 1, 2], rfl⟩
example : f myTuple = 7 :=
rfl
```

Here is an example of multiple constructors with arguments.

여기 여러 생성자가 있는 인자를 가진 예제가 있습니다.

```
inductive Foo where
| bar1 : Nat → Nat → Foo
| bar2 : Nat → Nat → Nat → Foo
def silly (x : Foo) : Nat := by
cases x with
| bar1 a b => exact b
| bar2 c d e => exact e
```

The alternatives for each constructor don't need to be solved
in the order the constructors were declared.

각 생성자의 대안은 생성자가 선언된 순서로 해결될 필요가 없습니다.

```
def silly (x : Foo) : Nat := by
cases x with
| bar2 c d e => exact e
| bar1 a b => exact b
```

The syntax of the `with` is convenient for writing structured proofs.
Lean also provides a complementary `case` tactic, which allows you to focus on goal
assign variable names.

`with`의 구문은 구조화된 증명을 작성하기에 편리합니다. Lean은 또한 목표에 초점을 맞추고 변수 이름을 할당하는 것을 허용하는 보완적인 `case` 전술을 제공합니다.

```
def silly (x : Foo) : Nat := by
cases x
case bar1 a b => exact b
case bar2 c d e => exact e
```

The `case` tactic is clever, in that it will match the constructor to the appropriate goal. For example, we can fill the goals above in the opposite order:

`case` 전술은 생성자를 적절한 목표와 일치시킬 것이기 때문에 영리합니다. 예를 들어 위의 목표를 반대 순서로 채울 수 있습니다:

```
def silly (x : Foo) : Nat := by
cases x
case bar2 c d e => exact e
case bar1 a b => exact b
```

You can also use `cases` with an arbitrary expression. Assuming that
expression occurs in the goal, the cases tactic will generalize over
the expression, introduce the resulting universally quantified
variable, and case on that.

또한 임의의 식으로 `cases`를 사용할 수 있습니다. 그 식이 목표에서 발생한다고 가정하면, cases 전술은 식을 일반화하고 결과적인 전체 한정된 변수를 도입하고 그 위에서 경우를 나눕니다.

```
open Nat
example (p : Nat → Prop) (hz : p 0) (hs : ∀ n, p (succ n)) (m k : Nat)
: p (m + 3 * k) := by
cases m + 3 * k
exact hz   -- goal is p 0
  apply hs   -- goal is a : Nat ⊢ p (succ a)
```

Think of this as saying “split on cases as to whether `m + 3 * k` is
zero or the successor of some number.” The result is functionally
equivalent to the following:

```
open Nat
example (p : Nat → Prop) (hz : p 0) (hs : ∀ n, p (succ n)) (m k : Nat)
: p (m + 3 * k) := by
generalize m + 3 * k = n
cases n
exact hz
apply hs
```

Notice that the expression `m + 3 * k` is erased by `generalize`; all
that matters is whether it is of the form `0` or `n✝ + 1`. This
form of `cases` will *not* revert any hypotheses that also mention
the expression in the equation (in this case, `m + 3 * k`). If such a
term appears in a hypothesis and you want to generalize over that as
well, you need to `revert` it explicitly.

`generalize`로 인해 식 `m + 3 * k`가 제거됩니다; 중요한 것은 `0` 형식인지 또는 `n✝ + 1` 형식인지입니다. 이 형식의 `cases`는 방정식의 식을 언급하는 어떤 가설도 되돌리지 *않습니다* (이 경우 `m + 3 * k`). 그러한 항이 가설에 나타나고 그것도 일반화하려면 명시적으로 `revert`해야 합니다.

If the expression you case on does not appear in the goal, the
`cases` tactic uses `have` to put the type of the expression into
the context. Here is an example:

```
example (p : Prop) (m n : Nat)
(h₁ : m < n → p) (h₂ : m ≥ n → p) : p := by
cases Nat.lt_or_ge m n
case inl hlt => exact h₁ hlt
case inr hge => exact h₂ hge
```

The theorem `Nat.lt_or_ge m n` says `m < n`` ∨ ``m ≥ n`, and it is natural to think of the proof above as splitting on these two cases. In the first branch, we have the hypothesis `hlt : m < n`, and in the second we have the hypothesis `hge : m ≥ n`. The proof above is functionally equivalent to the following:

경우 분석하는 식이 목표에 나타나지 않으면 `cases` 전술은 `have`를 사용하여 식의 타입을 컨텍스트에 넣습니다. 여기 예제가 있습니다:

정리 `Nat.lt_or_ge m n`은 `m < n` `∨` `m ≥ n`를 말하고, 위의 증명을 이 두 경우로 나누는 것으로 생각하는 것이 자연스럽습니다. 첫 번째 분기에서 가설 `hlt : m < n`을 가지고 있고 두 번째에서 가설 `hge : m ≥ n`을 가지고 있습니다. 위의 증명은 기능적으로 다음과 동등합니다:

```
example (p : Prop) (m n : Nat)
(h₁ : m < n → p) (h₂ : m ≥ n → p) : p := by
have h : m < n ∨ m ≥ n := Nat.lt_or_ge m n
cases h
case inl hlt => exact h₁ hlt
case inr hge => exact h₂ hge
```

After the first two lines, we have `h : m < n ∨ m ≥ n` as a
hypothesis, and we simply do cases on that.

처음 두 줄 다음에 가설으로 `h : m < n ∨ m ≥ n`을 가지고 있으며, 단순히 그것에 대한 경우를 나눕니다.

Here is another example, where we use the decidability of equality on
the natural numbers to split on the cases `m = n` and `m ≠ n`.

```
#check Nat.sub_self
```

```
Nat.sub_self (n : Nat) : n - n = 0
```

```
example (m n : Nat) : m - n = 0 ∨ m ≠ n := by
cases Decidable.em (m = n) with
| inl heq => rw [heq]; apply Or.inl; exact Nat.sub_self n
| inr hne => apply Or.inr; exact hne
```

Remember that if you `open ``Classical`, you can use the law of the excluded middle for any proposition at all. But using type class inference (see [Type Classes](../10-type-classes/#type-classes)), Lean can actually find the relevant decision procedure, which means that you can use the case split in a computable function.

여기 자연수에 대한 동등성의 결정 가능성을 사용하여 경우 `m = n`과 `m ≠ n`에 나누는 또 다른 예가 있습니다.

`Classical`을 `open`하면 어떤 명제에 대해서도 배제 중간 법칙을 사용할 수 있음을 기억하세요. 그러나 타입 클래스 추론 (참조: [타입 클래스](../10-type-classes/#type-classes))을 사용하면 Lean은 실제로 관련 결정 절차를 찾을 수 있으며, 이는 계산 가능한 함수에서 경우 분할을 사용할 수 있음을 의미합니다.

Just as the `cases` tactic can be used to carry out proof by cases,
the `induction` tactic can be used to carry out proofs by
induction. The syntax is similar to that of `cases`, except that the
argument can only be a term in the local context. Here is an example:

`cases` 전술이 경우 증명을 수행하는 데 사용될 수 있는 것처럼, `induction` 전술은 귀납법으로 증명을 수행하는 데 사용될 수 있습니다. 구문은 인자가 로컬 컨텍스트의 항일 수만 있다는 것을 제외하고 `cases`의 구문과 유사합니다. 여기 예제가 있습니다:

```
theorem zero_add (n : Nat) : 0 + n = n := by
induction n with
| zero => rfl
| succ n ih => rw [Nat.add_succ, ih]
```

As with `cases`, we can use the `case` tactic instead of `with`.

`cases`와 마찬가지로 `with` 대신 `case` 전술을 사용할 수 있습니다.

```
theorem zero_add (n : Nat) : 0 + n = n := by
induction n
case zero => rfl
case succ n ih => rw [Nat.add_succ, ih]
```

Here are some additional examples:

추가 예제들이 있습니다:

```
open Nat
theorem zero_add (n : Nat) : 0 + n = n := by
induction n <;> simp [*, add_zero, add_succ]
theorem succ_add (m n : Nat) : succ m + n = succ (m + n) := by
induction n <;> simp [*, add_zero, add_succ]
theorem add_comm (m n : Nat) : m + n = n + m := by
induction n <;> simp [*, add_zero, add_succ, succ_add, zero_add]
theorem add_assoc (m n k : Nat) : m + n + k = m + (n + k) := by
induction k <;> simp [*, add_zero, add_succ]
```

The `induction` tactic also supports user-defined induction principles with
multiple targets (aka major premises). This example uses `Nat.mod.inductionOn`, which has the following signature:

`induction` 전술은 또한 여러 대상 (aka 주 전제)을 가진 사용자 정의 귀납 원리를 지원합니다. 이 예제는 다음 서명을 가진 `Nat.mod.inductionOn`을 사용합니다:

```
Nat.mod.inductionOn
{motive : Nat → Nat → Sort u}
(x y : Nat)
(ind : ∀ x y, 0 < y ∧ y ≤ x → motive (x - y) y → motive x y)
(base : ∀ x y, ¬(0 < y ∧ y ≤ x) → motive x y) :
motive x y
```

```
example (x : Nat) {y : Nat} (h : y > 0) : x % y < y := by
induction x, y using Nat.mod.inductionOn with
| ind x y h₁ ih =>
rw [Nat.mod_eq_sub_mod h₁.2]
exact ih h
| base x y h₁ =>
have : ¬ 0 < y ∨ ¬ y ≤ x := Iff.mp (Decidable.not_and_iff_or_not ..) h₁
match this with
| Or.inl h₁ => exact absurd h h₁
| Or.inr h₁ =>
have hgt : y > x := Nat.gt_of_not_le h₁
rw [← Nat.mod_eq_of_lt hgt] at hgt
assumption
```

You can use the `match` notation in tactics too:

전술에서도 `match` 표기법을 사용할 수 있습니다:

```
example : p ∨ q → q ∨ p := by
intro h
match h with
| Or.inl _ => apply Or.inr; assumption
| Or.inr h2 => apply Or.inl; exact h2
```

As a convenience, pattern-matching has been integrated into tactics such as `intro` and `funext`.

편의상 패턴 매칭이 `intro` 및 `funext`와 같은 전술에 통합되었습니다.

```
example : s ∧ q ∧ r → p ∧ r → q ∧ p := by
intro ⟨_, ⟨hq, _⟩⟩ ⟨hp, _⟩
exact ⟨hq, hp⟩
example :
(fun (x : Nat × Nat) (y : Nat × Nat) => x.1 + y.2)
=
(fun (x : Nat × Nat) (z : Nat × Nat) => z.2 + x.1) := by
funext (a, b) (c, d)
show a + d = d + a
rw [Nat.add_comm]
```

We close this section with one last tactic that is designed to
facilitate working with inductive types, namely, the `injection`
tactic. By design, the elements of an inductive type are freely
generated, which is to say, the constructors are injective and have
disjoint ranges. The `injection` tactic is designed to make use of
this fact:

우리는 귀납적 타입과의 작업을 용이하게 하도록 설계된 마지막 전술인 `injection` 전술로 이 섹션을 마무리합니다. 설계상 귀납적 타입의 요소는 자유롭게 생성됩니다, 즉, 생성자는 단사이고 분리된 범위를 가집니다. `injection` 전술은 이 사실을 활용하도록 설계되었습니다:

```
open Nat
example (m n k : Nat) (h : succ (succ m) = succ (succ n))
: n + k = m + k := by
injection h with h'
injection h' with h''
rw [h'']
```

The first instance of the tactic adds `h' : m.succ = n.succ` to the
context, and the second adds `h'' : m = n`.

전술의 첫 번째 인스턴스는 컨텍스트에 `h' : m.succ = n.succ`를 추가하고 두 번째는 `h'' : m = n`을 추가합니다.

The `injection` tactic also detects contradictions that arise when different constructors
are set equal to one another, and uses them to close the goal.

`injection` 전술은 또한 서로 다른 생성자가 동일하게 설정될 때 발생하는 모순을 감지하고 목표를 닫는 데 사용합니다.

```
open Nat
example (m n : Nat) (h : succ m = 0) : n = n + 7 := by
injection h
example (m n : Nat) (h : succ m = 0) : n = n + 7 := by
contradiction
example (h : 7 = 4) : False := by
contradiction
```

As the second example shows, the `contradiction` tactic also detects contradictions of this form.

두 번째 예제가 보여주듯이, `contradiction` 전술도 이 형식의 모순을 감지합니다.

## 7.7. Inductive Families

We are almost done describing the full range of inductive definitions
accepted by Lean. So far, you have seen that Lean allows you to
introduce inductive types with any number of recursive
constructors. In fact, a single inductive definition can introduce an
indexed *family* of inductive types, in a manner we now describe.

Lean이 수용하는 귀납적 정의의 전체 범위를 설명하는 것이 거의 다 됐습니다. 지금까지 Lean은 모든 개수의 재귀 생성자를 가진 귀납적 타입을 도입하도록 허용함을 봤습니다. 실제로, 단일 귀납적 정의는 이제 설명하는 방식으로 귀납적 타입의 색인된 *계열*을 도입할 수 있습니다.

An inductive family is an indexed family of types defined by a
simultaneous induction of the following form:

귀납적 계열은 다음 형식의 동시 귀납으로 정의된 색인된 타입의 계열입니다:

In contrast to an ordinary inductive definition, which constructs an
element of some `Sort u`, the more general version constructs a
function `... →` `Sort u`, where “`...`” denotes a sequence of
argument types, also known as *indices*. Each constructor then
constructs an element of some member of the family. One example is the
definition of `Vect α n`, the type of vectors of elements of `α`
of length `n`:

```
inductive Vect (α : Type u) : Nat → Type u where
| nil : Vect α 0
| cons : α → {n : Nat} → Vect α n → Vect α (n + 1)
```

Notice that the `cons` constructor takes an element of
`Vect α n` and returns an element of `Vect α (n + 1)`, thereby using an
element of one member of the family to build an element of another.

`cons` 생성자는 `Vect α n`의 요소를 취하고 `Vect α (n + 1)`의 요소를 반환하며, 계열의 한 멤버의 요소를 사용하여 다른 멤버의 요소를 구축합니다.

A more exotic example is given by the definition of the equality type in Lean:

더 이국적인 예는 Lean의 동등성 타입의 정의에 의해 주어집니다:

```
inductive Eq {α : Sort u} (a : α) : α → Prop where
| refl : Eq a a
```

For each fixed `α : Sort u` and `a : α`, this definition
constructs a family of types `Eq a x`, indexed by `x : α`.
Notably, however, there is only one constructor, `refl`, which
is an element of `Eq a a`.
Intuitively, the only way to construct a proof of `Eq a x`
is to use reflexivity, in the case where `x` is `a`.
Note that `Eq a a` is the only inhabited type in the family of types
`Eq a x`. The elimination principle generated by Lean is as follows:

각 고정된 `α : Sort u`와 `a : α`에 대해, 이 정의는 `x : α`로 색인된 `Eq a x` 타입의 계열을 구성합니다. 그러나 주목할 점은 `Eq a a`의 요소인 `refl`이라는 단 하나의 생성자가 있다는 것입니다. 직관적으로 `Eq a x`의 증명을 구성하는 유일한 방법은 `x`가 `a`인 경우 반사성을 사용하는 것입니다. `Eq a a`가 타입의 계열 `Eq a x`에서 유일하게 inhabited(공집합이 아닌)된 타입임을 주목합니다. Lean에 의해 생성된 제거 원리는 다음과 같습니다:

```
universe u v
#check (@Eq.rec : {α : Sort u} → {a : α} →
{motive : (x : α) → a = x → Sort v} →
motive a rfl →
{b : α} → (h : a = b) → motive b h)
```

```
@Eq.rec : {α : Sort u} →
  {a : α} → {motive : (a_1 : α) → a = a_1 → Sort v} → motive a (Eq.refl a) → {a_1 : α} → (t : a = a_1) → motive a_1 t
```

It is a remarkable fact that all the basic axioms for equality follow
from the constructor, `refl`, and the eliminator, `Eq.rec`. The
definition of equality is atypical, however; see the discussion in [Axiomatic Details](#axiomatic-details).

동등성의 모든 기본 공리가 생성자 `refl`과 제거자 `Eq.rec`로부터 따라온다는 것은 놀라운 사실입니다. 그러나 동등성의 정의는 비전형적입니다; [공리적 세부 사항(Axiomatic Details)](#axiomatic-details)의 논의를 참조하세요.

The recursor `Eq.rec` is also used to define substitution:

Recursor `Eq.rec`은 또한 치환을 정의하는 데 사용됩니다:

```
theorem subst {α : Type u} {a b : α} {p : α → Prop}
(h₁ : Eq a b) (h₂ : p a) : p b :=
Eq.rec (motive := fun x _ => p x) h₂ h₁
```

You can also define `subst` using `match`.

`match`를 사용하여 `subst`를 정의할 수도 있습니다.

```
theorem subst {α : Type u} {a b : α} {p : α → Prop}
(h₁ : Eq a b) (h₂ : p a) : p b :=
match h₁ with
| rfl => h₂
```

Actually, Lean compiles the `match` expressions using a definition based on generated helpers
such as `Eq.casesOn` and `Eq.ndrec`, which are themselves defined using `Eq.rec`.

실제로 Lean은 `match` 식을 `Eq.rec`를 사용하여 자신들이 정의되는 `Eq.casesOn`과 `Eq.ndrec` 같은 생성된 도우미를 기반으로 한 정의를 사용하여 컴파일합니다.

```
theorem subst {α : Type u} {a b : α} {p : α → Prop}
(h₁ : a = b) (h₂ : p a) : p b :=
match h₁ with
| rfl => h₂
set_option pp.all true
#print subst
```

```
theorem Hidden.subst.{u} : ∀ {α : Type u} {a b : α} {p : α → Prop} (h₁ : @Eq.{u + 1} α a b) (h₂ : p a), p b :=
fun {α : Type u} {a b : α} {p : α → Prop} (h₁ : @Eq.{u + 1} α a b) (h₂ : p a) =>
  @Hidden.subst.match_1.{u} α a (fun (b : α) (h₁ : @Eq.{u + 1} α a b) => p b) b h₁ fun (_ : Unit) => h₂
```

```
#print subst.match_1_1
#print Eq.casesOn
```

```
@[reducible] def Eq.casesOn.{u, u_1} : {α : Sort u_1} →
  {a : α} →
    {motive : (a_1 : α) → (t : @Eq.{u_1} α a a_1) → Sort u} →
      {a_1 : α} → (t : @Eq.{u_1} α a a_1) → (refl : motive a (@Eq.refl.{u_1} α a)) → motive a_1 t :=
fun {α : Sort u_1} {a : α} {motive : (a_1 : α) → (t : @Eq.{u_1} α a a_1) → Sort u} {a_1 : α} (t : @Eq.{u_1} α a a_1)
    (refl : motive a (@Eq.refl.{u_1} α a)) =>
  @Eq.rec.{u, u_1} α a motive refl a_1 t
```

```
#print Eq.ndrec
```

```
@[reducible] def Eq.ndrec.{u1, u2} : {α : Sort u2} →
  {a : α} → {motive : α → Sort u1} → (m : motive a) → {b : α} → (h : @Eq.{u2} α a b) → motive b :=
fun {α : Sort u2} {a : α} {motive : α → Sort u1} (m : motive a) {b : α} (h : @Eq.{u2} α a b) =>
  @Eq.rec.{u1, u2} α a (fun (x : α) (x_1 : @Eq.{u2} α a x) => motive x) m b h
```

Using the recursor or `match` with `h₁ : a = b`, we may assume `a` and `b` are the same,
in which case, `p b` and `p a` are the same.

recursor 또는 `match`를 `h₁ : a = b`와 함께 사용하면 `a`와 `b`가 동일하다고 가정할 수 있으며, 이 경우 `p b`와 `p a`는 동일합니다.

It is not hard to prove that `Eq` is symmetric and transitive.
In the following example, we prove `symm` and leave as exercises the theorems `trans` and `congr` (congruence).

`Eq`가 대칭이고 전이임을 증명하는 것은 어렵지 않습니다. 다음 예제에서 `symm`을 증명하고 정리 `trans`와 `congr` (합동)은 연습 문제로 남깁니다.

```
variable {α β : Type u} {a b c : α}
theorem symm (h : Eq a b) : Eq b a :=
match h with
| rfl => rfl
theorem trans (h₁ : Eq a b) (h₂ : Eq b c) : Eq a c :=
sorry
theorem congr (f : α → β) (h : Eq a b) : Eq (f a) (f b) :=
sorry
```

In the type theory literature, there are further generalizations of
inductive definitions, for example, the principles of
*induction-recursion* and *induction-induction*. These are not
supported by Lean.

타입 이론 문헌에는 귀납적 정의의 추가 일반화가 있으며, 예를 들어 *귀납-재귀*와 *귀납-귀납*의 원리가 있습니다. 이들은 Lean에 의해 지원되지 않습니다.

## 7.8. Axiomatic Details

We have described inductive types and their syntax through
examples. This section provides additional information for those
interested in the axiomatic foundations.

우리는 예제를 통해 귀납적 타입과 그 구문을 설명했습니다. 이 섹션은 공리적 기초에 관심 있는 사람들을 위한 추가 정보를 제공합니다.

We have seen that the constructor to an inductive type takes
*parameters*—intuitively, the arguments that remain fixed
throughout the inductive construction—and *indices*, the arguments
parameterizing the family of types that is simultaneously under
construction. Each constructor should have a type, where the
argument types are built up from previously defined types, the
parameter and index types, and the inductive family currently being
defined. The requirement is that if the latter is present at all, it
occurs only *strictly positively*. This means simply that any argument
to the constructor in which it occurs is a dependent arrow type in which the
inductive type under definition occurs only as the resulting type,
where the indices are given in terms of constants and previous
arguments.

우리는 귀납적 타입의 생성자가 *매개변수* (직관적으로 귀납적 구성 전체에서 고정된 인자)와 *색인* (동시에 구성 중인 타입의 계열을 매개변수화하는 인자)을 취한다는 것을 봤습니다. 각 생성자는 타입을 가져야 하며, 여기서 인자 타입은 이전에 정의된 타입, 매개변수 및 색인 타입, 현재 정의 중인 귀납적 계열로부터 구축됩니다. 요구사항은 후자가 전혀 있다면 *순수하게 양의(strictly positively)* 상황에서만 발생한다는 것입니다. 이는 단순히 발생하는 생성자에 대한 모든 인자가 종속 화살표 타입이며 정의 중인 귀납적 타입이 결과 타입으로만 발생하며 색인은 상수 및 이전 인자 관점에서 주어진다는 의미입니다.

Since an inductive type lives in `Sort u` for some `u`, it is
reasonable to ask *which* universe levels `u` can be instantiated
to. Each constructor `c` in the definition of a family `C` of
inductive types is of the form

귀납적 타입이 일부 `u`에 대해 `Sort u`에 존재하므로 *어떤* 우주 수준 `u`가 인스턴스화될 수 있는지 묻는 것이 합리적입니다. 귀납적 타입의 계열 `C`의 정의에서 각 생성자 `c`는 다음 형식입니다:

where `a` is a sequence of data type parameters, `b` is the
sequence of arguments to the constructors, and `p[a, b]` are the
indices, which determine which element of the inductive family the
construction inhabits. (Note that this description is somewhat
misleading, in that the arguments to the constructor can appear in any
order as long as the dependencies make sense.) The constraints on the
universe level of `C` fall into two cases, depending on whether or
not the inductive type is specified to land in `Prop` (that is,
`Sort 0`).

여기서 `a`는 데이터 타입 매개변수의 시퀀스이고 `b`는 생성자에 대한 인자의 시퀀스이며 `p[a, b]`는 귀납적 계열의 어떤 요소가 구성을 inhabited(공집합이 아닌)하는지 결정하는 색인입니다. (이 설명이 다소 오해의 소지가 있다는 것을 주목하세요. 생성자에 대한 인자는 의존성이 타당한 한 모든 순서로 나타날 수 있기 때문입니다.) `C`의 우주 수준에 대한 제약은 귀납적 타입이 `Prop` (즉, `Sort 0`)으로 지정되는지 여부에 따라 두 경우로 나뉩니다.

Let us first consider the case where the inductive type is *not*
specified to land in `Prop`. Then the universe level `u` is
constrained to satisfy the following:

먼저 귀납적 타입이 `Prop`으로 지정되지 *않은* 경우를 고려해봅시다. 그러면 우주 수준 `u`는 다음을 만족하도록 제약됩니다:

For each constructor `c` as above, and each `βk[a]` in the sequence `β[a]`, if `βk[a] : Sort v`, we have `u` ≥ `v`.

In other words, the universe level `u` is required to be at least as
large as the universe level of each type that represents an argument
to a constructor.

다시 말해, 우주 수준 `u`는 생성자에 대한 인자를 나타내는 각 타입의 우주 수준만큼 크거나 커야 합니다.

When the inductive type is specified to land in `Prop`, there are no
constraints on the universe levels of the constructor arguments. But
these universe levels do have a bearing on the elimination
rule. Generally speaking, for an inductive type in `Prop`, the
motive of the elimination rule is required to be in `Prop`.

귀납적 타입이 `Prop`으로 지정될 때, 생성자 인자의 우주 수준에 제약이 없습니다. 그러나 이 우주 수준은 제거 규칙에 영향을 미칩니다. 일반적으로 `Prop`의 귀납적 타입에 대해 제거 규칙의 동기는 `Prop`에 있어야 합니다.

There is an exception to this last rule: we are allowed to eliminate
from an inductively defined `Prop` to an arbitrary `Sort` when
there is only one constructor and each constructor argument is either
in `Prop` or an index. The intuition is that in this case the
elimination does not make use of any information that is not already
given by the mere fact that the type of argument is inhabited. This
special case is known as *singleton elimination*.

이 마지막 규칙에 대한 예외가 있습니다: 생성자가 하나뿐이고 각 생성자 인자가 `Prop` 또는 색인 중 하나일 때 귀납적으로 정의된 `Prop`에서 임의의 `Sort`로 제거하는 것이 허용됩니다. 직관적으로 이 경우 제거는 인자의 타입이 inhabited(공집합이 아닌)된다는 단순한 사실로 이미 주어진 것 이상의 정보를 사용하지 않습니다. 이 특수한 경우를 *싱글톤 제거(singleton elimination)*라고 합니다.

We have already seen singleton elimination at play in applications of
`Eq.rec`, the eliminator for the inductively defined equality
type. We can use an element `h : Eq a b` to cast an element
`h₂ : p a` to `p b` even when `p a` and `p b` are arbitrary types,
because the cast does not produce new data; it only reinterprets the
data we already have. Singleton elimination is also used with
heterogeneous equality and well-founded recursion, which will be
discussed in a the chapter on [induction and recursion](../08-induction-and-recursion/#well-founded-recursion-and-induction).

우리는 이미 귀납적으로 정의된 동등성 타입의 제거자인 `Eq.rec`의 응용에서 싱글톤 제거가 작용하는 것을 봤습니다. 우리는 요소 `h : Eq a b`를 사용하여 요소 `h₂ : p a`를 `p b`로 캐스트할 수 있습니다. `p a`와 `p b`가 임의의 타입일 때도, 캐스트는 새로운 데이터를 생성하지 않기 때문입니다; 그것은 이미 가진 데이터를 재해석합니다. 싱글톤 제거는 또한 이질적 동등성과 well-founded 재귀에 사용되며, 이는 [귀납과 재귀(induction and recursion)](../08-induction-and-recursion/#well-founded-recursion-and-induction)의 장에서 논의될 것입니다.

## 7.9. Mutual and Nested Inductive Types

We now consider two generalizations of inductive types that are often
useful, which Lean supports by “compiling” them down to the more
primitive kinds of inductive types described above. In other words,
Lean parses the more general definitions, defines auxiliary inductive
types based on them, and then uses the auxiliary types to define the
ones we really want. Lean's equation compiler, described in the next
chapter, is needed to make use of these types
effectively. Nonetheless, it makes sense to describe the declarations
here, because they are straightforward variations on ordinary
inductive definitions.

First, Lean supports *mutually defined* inductive types. The idea is
that we can define two (or more) inductive types at the same time,
where each one refers to the other(s).

첫째, Lean은 *상호 정의된* 귀납적 타입을 지원합니다. 아이디어는 두 개 (또는 그 이상) 귀납적 타입을 동시에 정의할 수 있다는 것이며, 각각은 다른 것(들)을 참조합니다.

```
mutual
inductive Even : Nat → Prop where
| even_zero : Even 0
| even_succ : (n : Nat) → Odd n → Even (n + 1)
inductive Odd : Nat → Prop where
| odd_succ : (n : Nat) → Even n → Odd (n + 1)
end
```

In this example, two types are defined simultaneously: a natural
number `n` is `Even` if it is `0` or one more than an `Odd`
number, and `Odd` if it is one more than an `Even` number.
In the exercises below, you are asked to spell out the details.

이 예제에서 두 타입이 동시에 정의됩니다: 자연수 `n`은 `0`이거나 `Odd` 수보다 하나 많으면 `Even`이고, `Even` 수보다 하나 많으면 `Odd`입니다. 아래의 연습에서 세부 사항을 설명하도록 요청됩니다.

A mutual inductive definition can also be used to define the notation
of a finite tree with nodes labelled by elements of `α`:

상호 귀납적 정의는 또한 `α`의 요소로 레이블이 지정된 노드를 가진 유한 트리의 표기법을 정의하는 데 사용될 수 있습니다:

```
mutual
inductive Tree (α : Type u) where
| node : α → TreeList α → Tree α
inductive TreeList (α : Type u) where
| nil : TreeList α
| cons : Tree α → TreeList α → TreeList α
end
```

With this definition, one can construct an element of `Tree α` by
giving an element of `α` together with a list of subtrees, possibly
empty. The list of subtrees is represented by the type `TreeList α`,
which is defined to be either the empty list, `nil`, or the
`cons` of a tree and an element of `TreeList α`.

이 정의로, `Tree α`의 요소를 구성할 수 있습니다. `α`의 요소를 부분트리의 목록(가능하면 비어 있을 수 있음)과 함께 제공합니다. 부분트리의 목록은 타입 `TreeList α`로 표현되며, 이는 빈 목록 `nil`이거나 트리와 `TreeList α`의 요소의 `cons`로 정의됩니다.

This definition is inconvenient to work with, however. It would be
much nicer if the list of subtrees were given by the type
`List (Tree α)`, especially since Lean's library contains a number of functions
and theorems for working with lists. One can show that the type
`TreeList α` is *isomorphic* to `List (Tree α)`, but translating
results back and forth along this isomorphism is tedious.

그러나 이 정의는 작업하기에 불편합니다. 부분트리의 목록이 타입 `List (Tree α)`로 주어지면 훨씬 더 좋을 것입니다. 특히 Lean의 라이브러리에 목록과 함께 작업하기 위한 많은 함수와 정리가 포함되어 있기 때문입니다. 타입 `TreeList α`가 `List (Tree α)`와 *동형*임을 보일 수 있지만, 이 동형을 따라 결과를 앞뒤로 번역하는 것은 지루합니다.

In fact, Lean allows us to define the inductive type we really want:

실제로 Lean은 우리가 정말로 원하는 귀납적 타입을 정의하도록 허용합니다:

```
inductive Tree (α : Type u) where
| mk : α → List (Tree α) → Tree α
```

This is known as a *nested* inductive type. It falls outside the
strict specification of an inductive type given in the last section
because `Tree` does not occur strictly positively among the
arguments to `mk`, but, rather, nested inside the `List` type
constructor. Lean then automatically builds the
isomorphism between `TreeList α` and `List (Tree α)` in its kernel,
and defines the constructors for `Tree` in terms of the isomorphism.

이를 *중첩된* 귀납적 타입이라고 합니다. 지난 섹션에서 주어진 귀납적 타입의 엄격한 지정을 벗어나갑니다. `Tree`가 `mk`에 대한 인자 중에 순수하게 양의로 발생하지 않기 때문입니다만, 대신 `List` 타입 생성자 내부에 중첩됩니다. Lean은 그러면 자동으로 `TreeList α`와 `List (Tree α)` 사이의 동형을 커널에서 구축하고, 동형 관점에서 `Tree`의 생성자를 정의합니다.

## 7.10. Exercises

1. Try defining other operations on the natural numbers, such as
   multiplication, the predecessor function (with `pred 0 = 0`),
   truncated subtraction (with `n - m = 0` when `m` is greater
   than or equal to `n`), and exponentiation. Then try proving some
   of their basic properties, building on the theorems we have already
   proved.

1. 자연수에 대한 다른 연산들을 정의해보세요, 곱셈, 전임자 함수 (`pred 0 = 0`), 절단 빼기 (`m`이 `n`보다 크거나 같을 때 `n - m = 0`), 그리고 지수 연산. 그 다음 우리가 이미 증명한 정리를 기반으로 이들의 기본 성질을 증명해보세요.

이 중 많은 것이 이미 Lean의 핵심 라이브러리에 정의되어 있으므로 이름 충돌을 피하기 위해 `Hidden`이라는 이름의 네임스페이스 내에서 작업해야 합니다.

2. Define some operations on lists, like a `length` function or the
   `reverse` function. Prove some properties, such as the following:

2. 목록에 대한 연산들을 정의하세요, `length` 함수나 `reverse` 함수와 같은. 다음과 같은 성질들을 증명하세요:

3. Define an inductive data type consisting of terms built up from the following constructors:

3. 다음 생성자로부터 구축된 항으로 이루어진 귀납적 데이터 타입을 정의하세요:

* `const n`, 자연수 `n`을 나타내는 상수

* `var n`, 변수, 번호 `n`

* `plus s t`, `s`와 `t`의 합을 나타냄

* `times s t`, `s`와 `t`의 곱을 나타냄

변수에 대한 값 할당과 관련하여 이러한 항을 평가하는 함수를 재귀적으로 정의하세요.

4. Similarly, define the type of propositional formulas, as well as
   functions on the type of such formulas: an evaluation function,
   functions that measure the complexity of a formula, and a function
   that substitutes another formula for a given variable.

4. 유사하게, 명제 공식의 타입을 정의하세요, 뿐만 아니라 그러한 공식 타입에 대한 함수: 평가 함수, 공식의 복잡성을 측정하는 함수, 그리고 주어진 변수에 대해 다른 공식을 치환하는 함수.
