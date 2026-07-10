---
title: "9. 구조체와 레코드"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "theorem-proving", "type-theory"]
categories: ["programming"]
description: "구조체(structure)와 레코드, 상속과 확장 가능한 구조 정의 방법을 다룹니다."
---

We have seen that Lean's foundational system includes inductive
types. We have, moreover, noted that it is a remarkable fact that it
is possible to construct a substantial edifice of mathematics based on
nothing more than the type universes, dependent arrow types, and inductive types;
everything else follows from those. The Lean standard library contains
many instances of inductive types (e.g., `Nat`, `Prod`, `List`),
and even the logical connectives are defined using inductive types.

Lean의 기초 시스템에는 귀납적 타입(inductive types)이 포함되어 있습니다. 더 나아가 타입 우주(type universes), 종속 화살표 타입(dependent arrow types), 그리고 귀납적 타입만으로 수학의 상당한 건축물을 구성할 수 있다는 것은 놀라운 사실입니다. 다른 모든 것은 이들로부터 따릅니다. Lean 표준 라이브러리는 귀납적 타입의 많은 사례들(예: `Nat`, `Prod`, `List`)을 포함하고 있으며, 논리 연결자들도 귀납적 타입을 사용하여 정의됩니다.

Recall that a non-recursive inductive type that contains only one
constructor is called a *structure* or *record*. The product type is a
structure, as is the dependent product (Sigma) type.
In general, whenever we define a structure `S`, we usually
define *projection* functions that allow us to “destruct” each
instance of `S` and retrieve the values that are stored in its
fields. The functions `Prod.fst` and `Prod.snd`, which return the
first and second elements of a pair, are examples of such projections.

단 하나의 생성자만을 포함하는 비재귀적 귀납적 타입을 *구조(structure)* 또는 *레코드(record)*라고 합니다. 곱 타입(product type)도 구조이며, 종속 곱(Sigma) 타입도 그렇습니다. 일반적으로 구조 `S`를 정의할 때, 보통 `S`의 각 인스턴스를 “분해”하고 그 필드에 저장된 값을 회수할 수 있게 해주는 *사영(projection)* 함수를 정의합니다. 쌍의 첫 번째와 두 번째 원소를 반환하는 `Prod.fst`와 `Prod.snd` 함수는 이러한 사영의 예입니다.

When writing programs or formalizing mathematics, it is not uncommon
to define structures containing many fields. The `structure`
command, available in Lean, provides infrastructure to support this
process. When we define a structure using this command, Lean
automatically generates all the projection functions. The
`structure` command also allows us to define new structures based on
previously defined ones. Moreover, Lean provides convenient notation
for defining instances of a given structure.

프로그램을 작성하거나 수학을 형식화할 때, 많은 필드를 포함하는 구조를 정의하는 것은 흔한 일입니다. Lean에서 사용 가능한 `structure` 명령은 이 과정을 지원하는 인프라를 제공합니다. 이 명령을 사용하여 구조를 정의하면 Lean이 모든 사영 함수를 자동으로 생성합니다. `structure` 명령은 또한 이전에 정의된 구조를 기반으로 새로운 구조를 정의할 수 있게 합니다. 더욱이, Lean은 주어진 구조의 인스턴스를 정의하기 위한 편리한 표기법을 제공합니다.

## 9.1. Declaring Structures

The structure command is essentially a “front end” for defining
inductive data types. Every `structure` declaration introduces a
namespace with the same name. The general form is as follows:

structure 명령은 본질적으로 귀납적 데이터 타입을 정의하기 위한 “프론트 엔드”입니다. 모든 `structure` 선언은 같은 이름의 네임스페이스를 도입합니다. 일반적인 형식은 다음과 같습니다:

```
    structure <name> <parameters> <parent-structures> where
      <constructor> :: <fields>
```

Most parts are optional. Here is an example:

대부분의 부분은 선택사항입니다. 다음은 예시입니다:

```
structure Point (α : Type u) where
  mk ::
  x : α
  y : α
```

Values of type `Point` are created using `Point.mk a b`, and the
fields of a point `p` are accessed using `Point.x p` and
`Point.y p` (but `p.x` and `p.y` also work, see below).
The structure command also generates useful recursors and
theorems. Here are some of the constructions generated for the
declaration above.

`Point` 타입의 값은 `Point.mk a b`를 사용하여 생성되며, 점 `p`의 필드는 `Point.x p`와 `Point.y p`를 사용하여 접근합니다(하지만 `p.x`와 `p.y`도 작동합니다. 아래를 참조하세요). structure 명령은 유용한 재귀자(recursors)와 정리(theorems)도 생성합니다. 다음은 위의 선언으로부터 생성된 구성 중 일부입니다.

```
structure Point (α : Type u) where
  mk ::
  x : α
  y : α

-- a Type
#check Point
```

```
Point.{u} (α : Type u) : Type u
```

```
-- the eliminator
#check @Point.rec
```

```
@Point.rec : {α : Type u_2} →
  {motive : Point α → Sort u_1} → ((x y : α) → motive { x := x, y := y }) → (t : Point α) → motive t
```

```
-- the constructor
#check @Point.mk
```

```
@Point.mk : {α : Type u_1} → α → α → Point α
```

```
-- a projection
#check @Point.x
```

```
@Point.x : {α : Type u_1} → Point α → α
```

```
-- a projection
#check @Point.y
```

```
@Point.y : {α : Type u_1} → Point α → α
```

If the constructor name is not provided, then a constructor is named
`mk` by default.

생성자 이름이 제공되지 않으면, 생성자는 기본적으로 `mk`라고 명명됩니다.

Here are some simple theorems and expressions that use the generated
constructions. As usual, you can avoid the prefix `Point` by using
the command `open Point`.

다음은 생성된 구성을 사용하는 몇 가지 간단한 정리와 표현식입니다. 평소처럼 `open Point` 명령을 사용하여 `Point` 접두사를 피할 수 있습니다.

```
structure Point (α : Type u) where
  x : α
  y : α

#eval Point.x (Point.mk 10 20)
```

```
10
```

```
#eval Point.y (Point.mk 10 20)
```

```
20
```

```
open Point

example (a b : α) : x (mk a b) = a :=
  rfl

example (a b : α) : y (mk a b) = b :=
  rfl
```

Given `p : Point Nat`, the dot notation `p.x` is shorthand for
`Point.x p`. This provides a convenient way of accessing the fields
of a structure.

`p : Point Nat`가 주어졌을 때, 점 표기법 `p.x`는 `Point.x p`의 약자입니다. 이는 구조의 필드에 접근하는 편리한 방법을 제공합니다.

```
def p := Point.mk 10 20

#check p.x
```

```
p.x : Nat
```

```
#eval p.x
```

```
10
```

```
#eval p.y
```

```
20
```

The dot notation is convenient not just for accessing the projections
of a record, but also for applying functions defined in a namespace
with the same name. Recall from the [Conjunction section](../03-propositions-and-proofs/#conjunction) if `p`
has type `Point`, the expression `p.foo` is interpreted as
`Point.foo p`, assuming that the first non-implicit argument to
`foo` has type `Point`. The expression `p.add q` is therefore
shorthand for `Point.add p q` in the example below.

점 표기법은 레코드의 사영에 접근하기 위해 편리할 뿐만 아니라, 같은 이름의 네임스페이스에 정의된 함수를 적용하기 위해서도 편리합니다. [Conjunction 섹션](../03-propositions-and-proofs/#conjunction)을 상기하면, `p`가 `Point` 타입을 가질 때, 표현식 `p.foo`는 `Point.foo p`로 해석됩니다. 단, `foo`의 첫 번째 비암시적 인자가 `Point` 타입을 가져야 합니다. 따라서 표현식 `p.add q`는 아래 예제에서 `Point.add p q`의 약자입니다.

```
structure Point (α : Type u) where
  x : α
  y : α
deriving Repr

def Point.add (p q : Point Nat) :=
  mk (p.x + q.x) (p.y + q.y)

def p : Point Nat := Point.mk 1 2
def q : Point Nat := Point.mk 3 4

#eval p.add q
```

```
{ x := 4, y := 6 }
```

In the next chapter, you will learn how to define a function like
`add` so that it works generically for elements of `Point α`
rather than just `Point Nat`, assuming `α` has an associated
addition operation.

다음 장에서는 `α`가 연관된 덧셈 연산을 가진다고 가정할 때, `add`와 같은 함수를 정의하여 `Point Nat`뿐만 아니라 `Point α`의 원소에도 일반적으로 작동하도록 하는 방법을 배우게 됩니다.

More generally, given an expression `p.foo x y z` where `p : Point`,
Lean will insert `p` at the first argument to `Point.foo` of type
`Point`. For example, with the definition of scalar multiplication
below, `p.smul 3` is interpreted as `Point.smul 3 p`.

더 일반적으로, `p : Point`인 표현식 `p.foo x y z`가 주어졌을 때, Lean은 `Point` 타입의 `Point.foo`에 대한 첫 번째 인자에 `p`를 삽입합니다. 예를 들어, 아래의 스칼라 곱셈 정의를 사용하면, `p.smul 3`은 `Point.smul 3 p`로 해석됩니다.

```
def Point.smul (n : Nat) (p : Point Nat) :=
  Point.mk (n * p.x) (n * p.y)

def p : Point Nat := Point.mk 1 2

#eval p.smul 3
```

```
{ x := 3, y := 6 }
```

```
example {p : Point Nat} : p.smul 3 = Point.smul 3 p := rfl
```

It is common to use a similar trick with the `List.map` function,
which takes a list as its second non-implicit argument:

`List.map` 함수와 유사한 트릭을 사용하는 것이 일반적입니다. 이 함수는 두 번째 비암시적 인자로 리스트를 취합니다:

```
#check @List.map
```

```
@List.map : {α : Type u_1} → {β : Type u_2} → (α → β) → List α → List β
```

```
def xs : List Nat := [1, 2, 3]
def f : Nat → Nat := fun x => x * x

#eval xs.map f
```

```
[1, 4, 9]
```

```
example {xs : List α} {f : α → β} :
    xs.map f = List.map f xs :=
  rfl
```

Here `xs.map f` is interpreted as `List.map f xs`.

여기서 `xs.map f`는 `List.map f xs`로 해석됩니다.

## 9.2. Objects

We have been using constructors to create elements of a structure
type. For structures containing many fields, this is often
inconvenient, because we have to remember the order in which the
fields were defined. Lean therefore provides the following alternative
notations for defining elements of a structure type.

구조 타입의 원소를 생성하기 위해 생성자를 사용해 왔습니다. 많은 필드를 포함하는 구조의 경우, 필드가 정의된 순서를 기억해야 하기 때문에 이것은 종종 불편합니다. 따라서 Lean은 구조 타입의 원소를 정의하기 위한 다음과 같은 대체 표기법을 제공합니다.

```
    { (<field-name> := <expr>)* : structure-type }
    or
    { (<field-name> := <expr>)* }
```

The suffix `: structure-type` can be omitted whenever the name of
the structure can be inferred from the expected type. For example, we
use this notation to define “points.” The order that the fields are
specified does not matter, so all the expressions below define the
same point.

구조의 이름을 예상되는 타입으로부터 추론할 수 있을 때마다 접미사 `: structure-type`을 생략할 수 있습니다. 예를 들어, 우리는 이 표기법을 사용하여 “점”을 정의합니다. 필드가 지정되는 순서는 중요하지 않으므로, 아래의 모든 표현식은 같은 점을 정의합니다.

```
structure Point (α : Type u) where
  x : α
  y : α

#check { x := 10, y := 20 : Point Nat }
```

```
{ x := 10, y := 20 } : Point Nat
```

```
#check { y := 20, x := 10 : Point _ }
```

```
{ x := 10, y := 20 } : Point Nat
```

```
#check ({ x := 10, y := 20 } : Point Nat)
```

```
{ x := 10, y := 20 } : Point Nat
```

```
example : Point Nat :=
  { y := 20, x := 10 }
```

Fields can be marked as implicit using curly braces.
Implicit fields become implicit parameters to the constructor.

필드를 중괄호를 사용하여 암시적으로 표시할 수 있습니다. 암시적 필드는 생성자의 암시적 매개변수가 됩니다.

If the value of a field is not specified, Lean tries to infer it. If
the unspecified fields cannot be inferred, Lean flags an error
indicating the corresponding placeholder could not be synthesized.

필드의 값이 지정되지 않으면 Lean이 이를 추론하려고 시도합니다. 지정되지 않은 필드를 추론할 수 없으면 Lean은 해당 자리 표시자를 합성할 수 없다는 것을 나타내는 오류를 표시합니다.

```
structure MyStruct where
    {α : Type u}
    {β : Type v}
    a : α
    b : β

#check { a := 10, b := true : MyStruct }
```

```
{ α := Nat, β := Bool, a := 10, b := true } : MyStruct
```

*Record update* is another common operation which amounts to creating
a new record object by modifying the value of one or more fields in an
old one. Lean allows you to specify that unassigned fields in the
specification of a record should be taken from a previously defined
structure object `s` by adding the annotation `s` `with` before the field
assignments. If more than one record object is provided, then they are
visited in order until Lean finds one that contains the unspecified
field. Lean raises an error if any of the field names remain
unspecified after all the objects are visited.

*레코드 업데이트(record update)*는 기존 레코드의 하나 이상의 필드 값을 수정하여 새 레코드 객체를 만드는 또 다른 일반적인 연산입니다. Lean은 레코드 지정에서 할당되지 않은 필드를 필드 할당 전에 `s` `with` 표기를 추가하여 이전에 정의된 구조 객체 `s`에서 가져올 수 있도록 합니다. 하나 이상의 레코드 객체가 제공되면, Lean은 지정되지 않은 필드를 포함하는 객체를 찾을 때까지 순서대로 방문합니다. 모든 객체를 방문한 후에도 필드 이름이 지정되지 않으면 Lean은 오류를 발생시킵니다.

```
structure Point (α : Type u) where
  x : α
  y : α
deriving Repr

def p : Point Nat :=
  { x := 1, y := 2 }

#eval { p with y := 3 }
```

```
{ x := 1, y := 3 }
```

```
#eval { p with x := 4 }
```

```
{ x := 4, y := 2 }
```

```
structure Point3 (α : Type u) where
  x : α
  y : α
  z : α

def q : Point3 Nat :=
  { x := 5, y := 5, z := 5 }

def r : Point3 Nat :=
  { p, q with x := 6 }

example : r.x = 6 := rfl
example : r.y = 2 := rfl
example : r.z = 5 := rfl
```

## 9.3. Inheritance

We can *extend* existing structures by adding new fields. This feature
allows us to simulate a form of *inheritance*.

새로운 필드를 추가하여 기존 구조를 *확장(extend)*할 수 있습니다. 이 기능은 우리가 *상속(inheritance)*의 한 형태를 시뮬레이션할 수 있게 합니다.

```
structure Point (α : Type u) where
  x : α
  y : α

inductive Color where
  | red | green | blue

structure ColorPoint (α : Type u) extends Point α where
  c : Color
```

In the next example, we define a structure using multiple inheritance,
and then define an object using objects of the parent structures.

다음 예제에서는 다중 상속(multiple inheritance)을 사용하여 구조를 정의하고, 부모 구조의 객체를 사용하여 객체를 정의합니다.

```
structure Point (α : Type u) where
  x : α
  y : α
  z : α

structure RGBValue where
  red : Nat
  green : Nat
  blue : Nat

structure RedGreenPoint (α : Type u) extends Point α, RGBValue where
  no_blue : blue = 0

def p : Point Nat :=
  { x := 10, y := 10, z := 20 }

def rgp : RedGreenPoint Nat :=
  { p with red := 200, green := 40, blue := 0, no_blue := rfl }

example : rgp.x   = 10 := rfl
example : rgp.red = 200 := rfl
```
