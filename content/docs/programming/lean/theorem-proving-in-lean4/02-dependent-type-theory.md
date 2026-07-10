---
title: "2. 종속 타입 이론"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "theorem-proving", "type-theory"]
categories: ["programming"]
description: "단순 타입 이론에서 종속 함수 타입, 전역(universe), 변수와 섹션까지 Lean의 타입 이론 기초를 다룹니다."
---

Dependent type theory is a powerful and expressive language, allowing
you to express complex mathematical assertions, write complex hardware
and software specifications, and reason about both of these in a
natural and uniform way. Lean is based on a version of dependent type
theory known as the *Calculus of Constructions*, with a countable
hierarchy of non-cumulative universes and inductive types. By the end
of this chapter, you will understand much of what this means.

종속 타입 이론은 강력하고 표현력 있는 언어이며, 복잡한 수학적 주장을 표현하고, 복잡한 하드웨어와 소프트웨어 명세를 작성하고, 이 두 가지 모두에 대해 자연스럽고 균일한 방식으로 추론할 수 있게 해줍니다. Lean은 가산 무한 계층의 비누적 우주와 귀납적 타입을 가진 *구성 계산법(Calculus of Constructions)*이라고 알려진 종속 타입 이론의 한 버전을 기반으로 합니다. 이 장의 끝까지, 당신은 이것이 의미하는 바의 많은 부분을 이해하게 될 것입니다.

## 2.1. Simple Type Theory

“Type theory” gets its name from the fact that every expression has an
associated *type*. For example, in a given context, `x + 0` may
denote a natural number and `f` may denote a function on the natural
numbers. For those who like precise definitions, a Lean natural number
is an arbitrary-precision unsigned integer.

“타입 이론”은 모든 표현식이 관련된 *타입*을 가지고 있다는 사실에서 그 이름을 얻었습니다. 예를 들어, 주어진 문맥에서 `x + 0`은 자연수를 나타낼 수 있고, `f`는 자연수에 대한 함수를 나타낼 수 있습니다. 정확한 정의를 좋아하는 사람들을 위해, Lean 자연수는 임의 정밀도 부호 없는 정수입니다.

Here are some examples of how you can declare objects in Lean and
check their types.

여기 Lean에서 객체를 선언하고 타입을 확인하는 방법의 몇 가지 예시가 있습니다.

```
/- Define some constants. -/

def m : Nat := 1       -- m is a natural number
def n : Nat := 0
def b1 : Bool := true  -- b1 is a Boolean
def b2 : Bool := false
/- Check their types. -/

#check m
```

```
m : Nat
```

```
#check n
```

```
n : Nat
```

```
#check n + 0
```

```
n + 0 : Nat
```

```
#check m * (n + 0)
```

```
m * (n + 0) : Nat
```

```
#check b1
```

```
b1 : Bool
```

```
-- "&&" is the Boolean and
#check b1 && b2
```

```
b1 && b2 : Bool
```

```
-- Boolean or
#check b1 || b2
```

```
b1 || b2 : Bool
```

```
-- Boolean "true"
#check true
```

```
Bool.true : Bool
```

```
/- Evaluate -/

#eval 5 * 4
```

```
20
```

```
#eval m + 2
```

```
3
```

```
#eval b1 && b2
```

```
false
```

Any text between `/-` and `-/` constitutes a comment block that is
ignored by Lean. Similarly, two dashes `--` indicate that the rest of
the line contains a comment that is also ignored. Comment blocks can
be nested, making it possible to “comment out” chunks of code, just as
in many programming languages.

`/-`와 `-/` 사이의 텍스트는 Lean에서 무시되는 주석 블록을 구성합니다. 마찬가지로 두 개의 대시 `--`는 해당 줄의 나머지 부분이 주석이며 무시됨을 나타냅니다. 많은 프로그래밍 언어에서와 같이 주석 블록을 중첩하여 코드 덩어리를 "주석 처리"할 수 있습니다.

The `def` keyword declares new constant symbols into the
working environment. In the example above, `def m : Nat := 1`
defines a new constant `m` of type `Nat` whose value is `1`.
The `#check` command asks Lean to report their
types; in Lean, auxiliary commands that query the system for
information typically begin with the hash (#) symbol.
The `#eval` command asks Lean to evaluate the given expression.
You should try
declaring some constants and type checking some expressions on your
own. Declaring new objects in this manner is a good way to experiment
with the system.

`def` 키워드는 작업 환경에 새로운 상수 기호를 선언합니다. 위의 예제에서 `def m : Nat := 1`은 값이 `1`인 `Nat` 타입의 새로운 상수 `m`을 정의합니다. `#check` 명령은 Lean에 타입을 보고하도록 요청합니다. Lean에서 시스템에 정보를 요청하는 보조 명령은 일반적으로 해시(#) 기호로 시작합니다. `#eval` 명령은 Lean에 주어진 표현식을 평가하도록 요청합니다. 직접 일부 상수를 선언하고 일부 표현식에 대해 타입을 확인해보세요. 이러한 방식으로 새로운 객체를 선언하는 것은 시스템을 실험하는 좋은 방법입니다.

What makes simple type theory powerful is that you can build new types
out of others. For example, if `a` and `b` are types, `a -> b`
denotes the type of functions from `a` to `b`, and `a × b`
denotes the type of pairs consisting of an element of `a` paired
with an element of `b`, also known as the *Cartesian product*. Note
that `×` is a Unicode symbol. The judicious use of Unicode improves
legibility, and all modern editors have great support for it. In the
Lean standard library, you often see Greek letters to denote types,
and the Unicode symbol `→` as a more compact version of `->`

단순 타입 이론을 강력하게 만드는 것은 다른 타입에서 새로운 타입을 만들 수 있다는 것입니다. 예를 들어, `a`와 `b`가 타입이면, `a -> b`는 `a`에서 `b`로의 함수의 타입을 나타내고, `a × b`는 `a`의 원소와 `b`의 원소로 구성된 쌍의 타입을 나타내며, 이를 *데카르트 곱(Cartesian product)*이라고도 합니다. `×`는 유니코드 기호입니다. 유니코드를 신중하게 사용하면 가독성이 향상되며, 모든 최신 편집기는 이를 잘 지원합니다. Lean 표준 라이브러리에서는 타입을 나타내기 위해 그리스 문자를 자주 보게 되며, 유니코드 기호 `→`는 `->`의 더 간결한 버전입니다.

```
#check Nat → Nat
```

```
Nat → Nat : Type
```

```
#check Nat -> Nat
```

```
Nat → Nat : Type
```

```
#check Nat × Nat
```

```
Nat × Nat : Type
```

```
#check Prod Nat Nat
```

```
Nat × Nat : Type
```

```
#check Nat → Nat → Nat
```

```
Nat → Nat → Nat : Type
```

```
#check Nat → (Nat → Nat)
```

```
Nat → Nat → Nat : Type
```

```
#check Nat × Nat → Nat
```

```
Nat × Nat → Nat : Type
```

```
#check (Nat → Nat) → Nat
```

```
(Nat → Nat) → Nat : Type
```

```
#check Nat.succ
```

```
Nat.succ (n : Nat) : Nat
```

```
#check (0, 1)
```

```
(0, 1) : Nat × Nat
```

```
#check Nat.add
```

```
Nat.add : Nat → Nat → Nat
```

```
#check Nat.succ 2
```

```
Nat.succ 2 : Nat
```

```
#check Nat.add 3
```

```
Nat.add 3 : Nat → Nat
```

```
#check Nat.add 5 2
```

```
Nat.add 5 2 : Nat
```

```
#check (5, 9).1
```

```
(5, 9).fst : Nat
```

```
#check (5, 9).2
```

```
(5, 9).snd : Nat
```

```
#eval Nat.succ 2
```

```
3
```

```
#eval Nat.add 5 2
```

```
7
```

```
#eval (5, 9).1
```

```
5
```

```
#eval (5, 9).2
```

```
9
```

Once again, you should try some examples on your own.

다시 한번, 여러분 스스로 몇 가지 예제를 시도해 보아야 합니다.

Let's take a look at some basic syntax. You can enter the Unicode
arrow `→` by typing `\to` or `\r` or `\->`. You can also use the
ASCII alternative `->`, so the expressions `Nat -> Nat` and `Nat → Nat`
mean the same thing. Both expressions denote the type of
functions that take a natural number as input and return a natural
number as output. The Unicode symbol `×` for the Cartesian product
is entered as `\times`. You will generally use lower-case Greek
letters like `α`, `β`, and `γ` to range over types. You can
enter these particular ones with `\a`, `\b`, and `\g`.

기본 구문을 살펴보겠습니다. `→` 유니코드 화살표는 `\to`, `\r`, 또는 `\->`를 입력하여 입력할 수 있습니다. ASCII 대체 `->`를 사용할 수도 있으므로, `Nat -> Nat`과 `Nat → Nat` 표현식은 같은 의미입니다. 두 표현식 모두 자연수를 입력받아 자연수를 반환하는 함수의 타입을 나타냅니다. 데카르트 곱의 유니코드 기호 `×`는 `\times`로 입력합니다. 일반적으로 `α`, `β`, `γ`와 같은 소문자 그리스 문자를 사용하여 타입에 대해 나타냅니다. 이들을 `\a`, `\b`, `\g`로 입력할 수 있습니다.

There are a few more things to notice here. First, the application of
a function `f` to a value `x` is denoted `f x` (e.g., `Nat.succ 2`).
Second, when writing type expressions, arrows associate to the *right*; for
example, the type of `Nat.add` is `Nat → Nat → Nat` which is equivalent
to `Nat → (Nat → Nat)`. Thus you can
view `Nat.add` as a function that takes a natural number and returns
another function that takes a natural number and returns a natural
number. In type theory, this is generally more convenient than
writing `Nat.add` as a function that takes a pair of natural numbers as
input and returns a natural number as output. For example, it allows
you to “partially apply” the function `Nat.add`. The example above shows
that `Nat.add 3` has type `Nat → Nat`, that is, `Nat.add 3` returns a
function that “waits” for a second argument, `n`, which is then
equivalent to writing `Nat.add 3 n`.

여기서 주목할 몇 가지 더 있습니다. 첫째, 함수 `f`를 값 `x`에 적용하는 것은 `f x`로 표기됩니다 (예: `Nat.succ 2`). 둘째, 타입 표현식을 작성할 때, 화살표는 *오른쪽*으로 결합합니다. 예를 들어, `Nat.add`의 타입은 `Nat → Nat → Nat`이며, 이는 `Nat → (Nat → Nat)`과 동치입니다. 따라서 `Nat.add`를 자연수를 받아 다른 함수를 반환하는 함수로 볼 수 있으며, 이 다른 함수는 자연수를 받아 자연수를 반환합니다. 타입 이론에서는, `Nat.add`를 자연수 쌍을 입력받아 자연수를 반환하는 함수로 작성하는 것보다 일반적으로 더 편리합니다. 예를 들어, `Nat.add` 함수를 “부분 적용”할 수 있게 해줍니다. 위의 예제는 `Nat.add 3`이 `Nat → Nat` 타입을 가지고 있음을 보여줍니다. 즉, `Nat.add 3`은 두 번째 인수 `n`을 “기다리는” 함수를 반환하며, 이는 `Nat.add 3 n`을 작성하는 것과 동치입니다.

You have seen that if you have `m : Nat` and `n : Nat`, then
`(m, n)` denotes the ordered pair of `m` and `n` which is of
type `Nat × Nat`. This gives you a way of creating pairs of natural
numbers. Conversely, if you have `p : Nat × Nat`, then you can write
`p.1 : Nat` and `p.2 : Nat`. This gives you a way of extracting
its two components.

`m : Nat`과 `n : Nat`을 가지고 있으면, `(m, n)`은 타입이 `Nat × Nat`인 `m`과 `n`의 순서쌍을 나타냅니다. 이는 자연수의 쌍을 만드는 방법을 제공합니다. 반대로, `p : Nat × Nat`을 가지고 있으면, `p.1 : Nat`과 `p.2 : Nat`을 쓸 수 있습니다. 이는 두 구성 요소를 추출하는 방법을 제공합니다.

## 2.2. Types as objects

One way in which Lean's dependent type theory extends simple type
theory is that types themselves—entities like `Nat` and `Bool`—are first-class citizens, which is to say that they themselves are
objects. For that to be the case, each of them also has to have a
type.

Lean의 종속 타입 이론이 단순 타입 이론을 확장하는 한 가지 방법은 타입 자체(`Nat`과 `Bool`과 같은 엔터티들)가 일급 시민이라는 것입니다. 즉, 그들 자체가 객체라는 뜻입니다. 이것이 가능하려면, 각각도 타입을 가져야 합니다.

```
#check Nat
```

```
Nat : Type
```

```
#check Bool
```

```
Bool : Type
```

```
#check Nat → Bool
```

```
Nat → Bool : Type
```

```
#check Nat × Bool
```

```
Nat × Bool : Type
```

```
#check Nat → Nat
```

```
Nat → Nat : Type
```

```
#check Nat × Nat → Nat
```

```
Nat × Nat → Nat : Type
```

```
#check Nat → Nat → Nat
```

```
Nat → Nat → Nat : Type
```

```
#check Nat → (Nat → Nat)
```

```
Nat → Nat → Nat : Type
```

```
#check Nat → Nat → Bool
```

```
Nat → Nat → Bool : Type
```

```
#check (Nat → Nat) → Nat
```

```
(Nat → Nat) → Nat : Type
```

You can see that each one of the expressions above is an object of
type `Type`. You can also declare new constants for types:

위의 각 표현식이 `Type` 타입의 객체임을 볼 수 있습니다. 타입을 위한 새로운 상수를 선언할 수도 있습니다:

```
def α : Type := Nat
def β : Type := Bool
def F : Type → Type := List
def G : Type → Type → Type := Prod
#check α
```

```
α : Type
```

```
#check F α
```

```
F α : Type
```

```
#check F Nat
```

```
F Nat : Type
```

```
#check G α
```

```
G α : Type → Type
```

```
#check G α β
```

```
G α β : Type
```

```
#check G α Nat
```

```
G α Nat : Type
```

As the example above suggests, you have already seen an example of a function of type
`Type → Type → Type`, namely, the Cartesian product `Prod`:

위의 예에서 알 수 있듯이, 여러분은 이미 `Type → Type → Type` 타입의 함수 예시인 데카르트 곱 `Prod`를 보았습니다:

```
def α : Type := Nat
def β : Type := Bool
#check Prod α β
```

```
α × β : Type
```

```
#check α × β
```

```
α × β : Type
```

```
#check Prod Nat Nat
```

```
Nat × Nat : Type
```

```
#check Nat × Nat
```

```
Nat × Nat : Type
```

Here is another example: given any type `α`, the type `List α`
denotes the type of lists of elements of type `α`.

여기 또 다른 예제가 있습니다: 임의의 타입 `α`이 주어지면, 타입 `List α`는 `α` 타입의 원소들의 목록의 타입을 나타냅니다.

```
def α : Type := Nat
#check List α
```

```
List α : Type
```

```
#check List Nat
```

```
List Nat : Type
```

Given that every expression in Lean has a type, it is natural to ask:
what type does `Type` itself have?

Lean의 모든 표현식이 타입을 가지고 있다는 것을 감안할 때, 자연스러운 질문은: `Type` 자체의 타입은 무엇인가? 입니다.

```
#check Type
```

```
Type : Type 1
```

You have actually come up against one of the most subtle aspects of
Lean's typing system. Lean's underlying foundation has an infinite
hierarchy of types:

당신은 실제로 Lean의 타입 체계의 가장 미묘한 측면 중 하나와 마주쳤습니다. Lean의 기초 체계는 타입의 무한 계층을 가지고 있습니다:

```
#check Type
```

```
Type : Type 1
```

```
#check Type 1
```

```
Type 1 : Type 2
```

```
#check Type 2
```

```
Type 2 : Type 3
```

```
#check Type 3
```

```
Type 3 : Type 4
```

```
#check Type 4
```

```
Type 4 : Type 5
```

Think of `Type 0` as a universe of “small” or “ordinary” types.
`Type 1` is then a larger universe of types, which contains `Type 0`
as an element, and `Type 2` is an even larger universe of types,
which contains `Type 1` as an element. The list is infinite:
there is a `Type n` for every natural number `n`. `Type` is
an abbreviation for `Type 0`:

`Type 0`을 “작은” 또는 “일반적인” 타입의 우주로 생각하세요. `Type 1`은 `Type 0`을 원소로 포함하는 더 큰 타입의 우주이고, `Type 2`는 `Type 1`을 원소로 포함하는 훨씬 더 큰 타입의 우주입니다. 목록은 무한합니다: 모든 자연수 `n`에 대해 `Type n`이 있습니다. `Type`은 `Type 0`의 약자입니다:

```
#check Type
```

```
Type : Type 1
```

```
#check Type 0
```

```
Type : Type 1
```

The following table may help concretize the relationships being discussed.
Movement along the x-axis represents a change in the universe, while movement
along the y-axis represents a change in what is sometimes referred to as
“degree”.

다음 표는 논의되는 관계를 구체화하는 데 도움이 될 수 있습니다. x축을 따라 이동하면 우주의 변화를 나타내고, y축을 따라 이동하면 때때로 “차수”라고 불리는 것의 변화를 나타냅니다.

Some operations, however, need to be *polymorphic* over type
universes. For example, `List α` should make sense for any type
`α`, no matter which type universe `α` lives in. This explains the
type signature of the function `List`:

그러나 일부 연산은 타입 우주(type universes)에 대해 *다형성(polymorphic)*을 가져야 합니다. 예를 들어, `List α`는 `α`가 어떤 타입 우주에 속하든 관계없이 모든 타입 `α`에 대해 의미가 있어야 합니다. 이는 `List` 함수의 타입 시그니처를 설명합니다:

```
#check List
```

```
List.{u} (α : Type u) : Type u
```

Here `u` is a variable ranging over type levels. The output of the
`#check` command means that whenever `α` has type `Type u`,
`List α` also has type `Type u`. The function `Prod` is
similarly polymorphic:

여기서 `u`는 타입 레벨에 대한 범위를 가지는 변수입니다. `#check` 명령의 출력은 `α`가 `Type u` 타입을 가질 때마다, `List α`도 `Type u` 타입을 가진다는 의미입니다. 함수 `Prod`는 비슷하게 다형적입니다:

```
#check Prod
```

```
Prod.{u, v} (α : Type u) (β : Type v) : Type (max u v)
```

To define polymorphic constants, Lean allows you to
declare universe variables explicitly using the `universe` command:

다형적 상수를 정의하기 위해, Lean은 `universe` 명령을 사용하여 우주 변수를 명시적으로 선언할 수 있게 해줍니다:

```
universe u
def F (α : Type u) : Type u := Prod α α
#check F
```

```
F.{u} (α : Type u) : Type u
```

You can avoid the `universe` command by providing the universe parameters when defining `F`:

`F`를 정의할 때 우주 매개변수를 제공하여 `universe` 명령을 피할 수 있습니다:

```
def F.{u} (α : Type u) : Type u := Prod α α
#check F
```

```
F.{u} (α : Type u) : Type u
```

## 2.3. Function Abstraction and Evaluation

Lean provides a `fun` (or `λ`) keyword to create a function
from an expression as follows:

Lean은 다음과 같이 표현식에서 함수를 생성하기 위해 `fun` (또는 `λ`) 키워드를 제공합니다:

```
#check fun (x : Nat) => x + 5
```

```
fun x => x + 5 : Nat → Nat
```

```
-- λ and fun mean the same thing
#check λ (x : Nat) => x + 5
```

```
fun x => x + 5 : Nat → Nat
```

The type `Nat` can be inferred in this example:

특정 예제에서는 타입 `Nat`을 유추할 수 있습니다:

```
#check fun x => x + 5
```

```
fun x => x + 5 : Nat → Nat
```

```
#check λ x => x + 5
```

```
fun x => x + 5 : Nat → Nat
```

You can evaluate a lambda function by passing the required parameters:

필요한 매개변수를 전달하여 람다 함수를 평가할 수 있습니다:

```
#eval (λ x : Nat => x + 5) 10
```

```
15
```

Creating a function from another expression is a process known as
*lambda abstraction*. Suppose you have the variable `x : α` and you can
construct an expression `t : β`, then the expression `fun (x : α) => t`,
or, equivalently, `λ (x : α) => t`, is an object of type `α → β`. Think of
this as the function from `α` to `β` which maps
any value `x` to the value `t`.

다른 표현식에서 함수를 만드는 것은 *람다 추상화(lambda abstraction)*라고 알려진 과정입니다. 변수 `x : α`를 가지고 있고 표현식 `t : β`를 구성할 수 있으면, 표현식 `fun (x : α) => t` 또는 동등하게 `λ (x : α) => t`는 `α → β` 타입의 객체입니다. 이를 `α`에서 `β`로의 함수로 생각하세요. 이 함수는 모든 값 `x`를 값 `t`에 매핑합니다.

Here are some more examples

여기에 더 많은 예제가 있습니다.

```
#check fun x : Nat => fun y : Bool => if not y then x + 1 else x + 2
```

```
fun x y => if (!y) = true then x + 1 else x + 2 : Nat → Bool → Nat
```

```
#check fun (x : Nat) (y : Bool) => if not y then x + 1 else x + 2
```

```
fun x y => if (!y) = true then x + 1 else x + 2 : Nat → Bool → Nat
```

```
#check fun x y => if not y then x + 1 else x + 2
```

```
fun x y => if (!y) = true then x + 1 else x + 2 : Nat → Bool → Nat
```

Lean interprets the final three examples as the same expression; in
the last expression, Lean infers the type of `x` and `y` from the
expression `if not y then x + 1 else x + 2`.

Lean은 마지막 세 예제를 같은 표현식으로 해석합니다. 마지막 표현식에서 Lean은 `if not y then x + 1 else x + 2` 표현식에서 `x`와 `y`의 타입을 추론합니다.

Some mathematically common examples of operations of functions can be
described in terms of lambda abstraction:

함수 연산에 대한 수학적으로 일반적인 예시 중 일부는 람다 추상화로 설명할 수 있습니다:

```
def f (n : Nat) : String := toString n
def g (s : String) : Bool := s.length > 0
#check fun x : Nat => x
```

```
fun x => x : Nat → Nat
```

```
#check fun x : Nat => true
```

```
fun x => true : Nat → Bool
```

```
#check fun x : Nat => g (f x)
```

```
fun x => g (f x) : Nat → Bool
```

```
#check fun x => g (f x)
```

```
fun x => g (f x) : Nat → Bool
```

Think about what these expressions mean. The expression
`fun x : Nat => x` denotes the identity function on `Nat`, the
expression `fun x : Nat => true` denotes the constant function that
always returns `true`, and `fun x : Nat => g (f x)` denotes the
composition of `f` and `g`. You can, in general, leave off the
type annotation and let Lean infer it for you. So, for example, you
can write `fun x => g (f x)` instead of `fun x : Nat => g (f x)`.

이 표현식들이 무엇을 의미하는지 생각해보세요. 표현식 `fun x : Nat => x`는 `Nat`에 대한 항등 함수를 나타내고, 표현식 `fun x : Nat => true`는 항상 `true`를 반환하는 상수 함수를 나타내며, `fun x : Nat => g (f x)`는 `f`와 `g`의 합성을 나타냅니다. 일반적으로 타입 주석을 생략하고 Lean이 추론하게 할 수 있습니다. 예를 들어, `fun x : Nat => g (f x)` 대신 `fun x => g (f x)`를 쓸 수 있습니다.

You can pass functions as parameters and by giving them names `f`
and `g` you can then use those functions in the implementation:

함수를 매개변수로 전달할 수 있으며, 여기에 `f`와 `g`라는 이름을 지정하여 구현에서 해당 함수를 사용할 수 있습니다:

```
#check fun (g : String → Bool) (f : Nat → String) (x : Nat) => g (f x)
```

```
fun g f x => g (f x) : (String → Bool) → (Nat → String) → Nat → Bool
```

You can also pass types as parameters:

타입을 매개변수로 전달할 수도 있습니다:

```
#check fun (α β γ : Type) (g : β → γ) (f : α → β) (x : α) => g (f x)
```

```
fun α β γ g f x => g (f x) : (α β γ : Type) → (β → γ) → (α → β) → α → γ
```

The last expression, for example, denotes the function that takes
three types, `α`, `β`, and `γ`, and two functions, `g : β → γ`
and `f : α → β`, and returns the composition of `g` and `f`.
(Making sense of the type of this function requires an understanding
of *dependent products*, which will be explained below.)

예를 들어, 마지막 표현식은 세 가지 타입 `α`, `β`, `γ`와 두 함수 `g : β → γ`와 `f : α → β`를 받아서 `g`와 `f`의 합성을 반환하는 함수를 나타냅니다. (이 함수의 타입을 이해하려면 아래에서 설명할 *종속 곱(dependent products)*을 이해해야 합니다.)

The general form of a lambda expression is `fun (x : α) => t`, where
the variable `x` is a “bound variable”: it is really a placeholder,
whose “scope” does not extend beyond the expression `t`. For
example, the variable `b` in the expression `fun (b : β) (x : α) => b`
has nothing to do with the constant `b` declared earlier. In fact,
the expression denotes the same function as `fun (u : β) (z : α) => u`.

람다 표현식의 일반적인 형태는 `fun (x : α) => t`이며, 여기서 변수 `x`는 "종속 변수(bound variable)"입니다. 이는 사실상 자리 표시자(placeholder)이며, "스코프(scope)"는 표현식 `t`를 넘어서지 않습니다. 예를 들어, `fun (b : β) (x : α) => b` 표현식에서 변수 `b`는 이전에 선언된 상수 `b`와 아무런 관련이 없습니다. 사실 이 표현식은 `fun (u : β) (z : α) => u`와 같은 함수를 나타냅니다.

Formally, expressions that are the same up to a renaming of bound
variables are called *alpha equivalent*, and are considered “the
same.” Lean recognizes this equivalence.

형식적으로, 바운드 변수의 이름 변경까지 같은 표현식들을 *알파 동치(alpha equivalent)*라고 부르며, “같은 것”으로 간주합니다. Lean은 이 동치성을 인식합니다.

Notice that applying a term `t : α → β` to a term `s : α` yields
an expression `t s : β`. Returning to the previous example and
renaming bound variables for clarity, notice the types of the
following expressions:

항 `t : α → β`를 항 `s : α`에 적용하면 표현식 `t s : β`를 생성한다는 점을 주목하세요. 이전 예제로 돌아가서 명확성을 위해 바운드 변수의 이름을 바꾸면, 다음 표현식들의 타입을 주목하세요:

```
#check (fun x : Nat => x) 1
```

```
(fun x => x) 1 : Nat
```

```
#check (fun x : Nat => true) 1
```

```
(fun x => true) 1 : Bool
```

```
def f (n : Nat) : String := toString n
def g (s : String) : Bool := s.length > 0
#check
(fun (α β γ : Type) (u : β → γ) (v : α → β) (x : α) => u (v x)) Nat String Bool g f 0
```

```
(fun α β γ u v x => u (v x)) Nat String Bool g f 0 : Bool
```

As expected, the expression `(fun x : Nat => x) 1` has type `Nat`.
In fact, more should be true: applying the expression `(fun x : Nat => x)` to
`1` should “return” the value `1`. And, indeed, it does:

예상대로, 표현식 `(fun x : Nat => x) 1`은 타입 `Nat`를 가집니다. 사실, 더 많은 것이 참이어야 합니다: 표현식 `(fun x : Nat => x)`를 `1`에 적용하면 값 `1`을 “반환”해야 합니다. 그리고 실제로 그렇습니다:

```
#eval (fun x : Nat => x) 1
```

```
1
```

```
#eval (fun x : Nat => true) 1
```

```
true
```

You will see later how these terms are evaluated. For now, notice that
this is an important feature of dependent type theory: every term has
a computational behavior, and supports a notion of *normalization*. In
principle, two terms that reduce to the same value are called
*definitionally equal*. They are considered “the same” by Lean's type
checker, and Lean does its best to recognize and support these
identifications.

나중에 이러한 항들이 어떻게 평가되는지 볼 것입니다. 지금은 이것이 종속 타입 이론의 중요한 특징임을 주목하세요: 모든 항은 계산적 동작을 가지고 있으며, *정규화(normalization)*의 개념을 지원합니다. 원칙적으로, 같은 값으로 축약되는 두 항을 *정의적으로 동등(definitionally equal)*이라고 부릅니다. Lean의 타입 체커는 이들을 “같은 것”으로 간주하며, Lean은 이러한 동일성을 인식하고 지원하기 위해 최선을 다합니다.

Lean is a complete programming language. It has a compiler that
generates a binary executable and an interactive interpreter. You can
use the command `#eval` to execute expressions, and it is the
preferred way of testing your functions.

Lean은 완전한 프로그래밍 언어입니다. 이진 실행 파일을 생성하는 컴파일러와 대화형 인터프리터를 가지고 있습니다. `#eval` 명령을 사용하여 표현식을 실행할 수 있으며, 이는 함수를 테스트하는 선호되는 방법입니다.

## 2.4. Definitions

Recall that the `def` keyword provides one important way of declaring new named
objects.

`def` 키워드는 이름이 있는 새로운 객체를 선언하는 한 가지 중요한 방법을 제공한다는 것을 기억하세요.

```
def double (x : Nat) : Nat :=
x + x
```

This might look more familiar to you if you know how functions work in
other programming languages. The name `double` is defined as a
function that takes an input parameter `x` of type `Nat`, where the
result of the call is `x + x`, so it is returning type `Nat`. You
can then invoke this function using:

다른 프로그래밍 언어에서 함수가 어떻게 작동하는지 안다면 이것이 더 친숙하게 보일 수 있습니다. `double`이라는 이름은 `Nat` 타입의 입력 매개변수 `x`를 사용하는 함수로 정의되며, 호출 결과는 `x + x`이므로 `Nat` 타입을 반환합니다. 다음과 같이 이 함수를 호출할 수 있습니다:

```
#eval double 3
```

```
6
```

In this case you can think of `def` as a kind of named `fun`.
The following yields the same result:

이 경우, `def`를 일종의 명명된 `fun`으로 생각할 수 있습니다. 다음은 같은 결과를 줍니다:

```
def double : Nat → Nat :=
fun x => x + x
#eval double 3
```

```
6
```

You can omit the type declarations when Lean has enough information to
infer it. Type inference is an important part of Lean:

Lean이 타입을 유추할 수 있는 충분한 정보를 가지고 있을 때는 타입 선언을 생략할 수 있습니다. 타입 추론은 Lean의 중요한 부분입니다:

```
def double :=
fun (x : Nat) => x + x
```

The general form of a definition is `def foo : α := bar` where
`α` is the type returned from the expression `bar`. Lean can
usually infer the type `α`, but it is often a good idea to write it
explicitly. This clarifies your intention, and Lean will flag an
error if the right-hand side of the definition does not have a matching
type.

정의의 일반적인 형태는 `def foo : α := bar`이며, 여기서 `α`는 표현식 `bar`에서 반환되는 타입입니다. Lean은 일반적으로 타입 `α`를 추론할 수 있지만, 명시적으로 작성하는 것이 좋은 경우가 많습니다. 이는 당신의 의도를 명확히 하며, 정의의 오른쪽이 일치하는 타입을 가지지 않으면 Lean이 오류를 표시합니다.

The right hand side `bar` can be any expression, not just a lambda.
So `def` can also be used to simply name a value like this:

우변인 `bar`는 람다뿐만 아니라 모든 표현식이 될 수 있습니다. 따라서 `def`는 다음과 같이 단순히 값에 이름을 지정하는 데 사용될 수도 있습니다:

```
def pi := 3.141592654
```

`def` can take multiple input parameters. Let's create one
that adds two natural numbers:

`def`는 여러 입력 매개변수를 가질 수 있습니다. 두 자연수를 더하는 함수를 만들어봅시다:

```
def add (x y : Nat) :=
x + y
#eval add 3 2
```

```
5
```

The parameter list can be separated like this:

매개변수 목록은 다음과 같이 구분할 수 있습니다:

```
def add (x : Nat) (y : Nat) :=
x + y
#eval add (double 3) (7 + 9)
```

```
22
```

Notice here we called the `double` function to create the first
parameter to `add`.

여기서 우리는 `double` 함수를 호출하여 `add`의 첫 번째 매개변수를 만들었음을 주목하세요.

You can use other more interesting expressions inside a `def`:

`def` 안에 더 흥미로운 다른 표현식을 생략 없이 사용할 수 있습니다:

```
def greater (x y : Nat) :=
if x > y then x
else y
```

You can probably guess what this one will do.

이것이 어떤 일을 할지 아마 짐작할 수 있을 것입니다.

You can also define a function that takes another function as input.
The following calls a given function twice passing the output of the
first invocation to the second:

또한 다른 함수를 입력으로 받는 함수를 정의할 수 있습니다. 다음은 주어진 함수를 두 번 호출하며 첫 번째 호출의 출력을 두 번째 함수에 전달합니다:

```
def doTwice (f : Nat → Nat) (x : Nat) : Nat :=
f (f x)
#eval doTwice double 2
```

```
8
```

Now to get a bit more abstract, you can also specify arguments that
are like type parameters:

이제 조금 더 추상화하여, 타입 매개변수 같은 인자도 지정할 수 있습니다:

```
def compose (α β γ : Type) (g : β → γ) (f : α → β) (x : α) : γ :=
g (f x)
```

This means `compose` is a function that takes any two functions as input
arguments, so long as those functions each take only one input.
The type algebra `β → γ` and `α → β` means it is a requirement
that the type of the output of the second function must match the
type of the input to the first function—which makes sense, otherwise
the two functions would not be composable.

이는 `compose`가 어떤 두 함수를 입력 인수로 받는 함수이며, 그 함수들이 각각 하나의 입력만을 받는 한 그렇다는 의미입니다. 타입 대수 `β → γ`와 `α → β`는 두 번째 함수의 출력 타입이 첫 번째 함수의 입력 타입과 일치해야 한다는 요구사항을 의미합니다. 이는 의미가 있는데, 그렇지 않으면 두 함수는 구성 가능하지 않기 때문입니다.

`compose` also takes a 3rd argument of type `α` which
it uses to invoke the second function (locally named `f`) and it
passes the result of that function (which is type `β`) as input to the
first function (locally named `g`). The first function returns a type
`γ` so that is also the return type of the `compose` function.

`compose`은 또한 `α` 타입의 세 번째 인수를 받으며, 이를 사용하여 두 번째 함수(지역적으로 `f`라고 불림)를 호출하고, 그 함수의 결과(타입 `β`)를 첫 번째 함수(지역적으로 `g`라고 불림)에 입력으로 전달합니다. 첫 번째 함수는 타입 `γ`을 반환하므로, 이것도 `compose` 함수의 반환 타입입니다.

`compose` is also very general in that it works over any type
`α β γ`. This means `compose` can compose just about any 2 functions
so long as they each take one parameter, and so long as the type of
output of the second matches the input of the first. For example:

`compose`는 또한 임의의 타입 `α β γ`에 대해 작동하기 때문에 매우 일반적입니다. 이는 `compose`가 거의 모든 2개 함수를 구성할 수 있다는 의미이며, 그 함수들이 각각 하나의 매개변수를 받는 한, 그리고 두 번째의 출력 타입이 첫 번째의 입력과 일치하는 한 그렇습니다. 예를 들어:

```
def square (x : Nat) : Nat :=
x * x
#eval compose Nat Nat Nat double square 3
```

```
18
```

## 2.5. Local Definitions

Lean also allows you to introduce “local” definitions using the
`let` keyword. The expression `let a := t1; t2` is
definitionally equal to the result of replacing every occurrence of
`a` in `t2` by `t1`.

Lean은 또한 `let` 키워드를 사용하여 "로컬(local)" 정의를 도입할 수 있게 해줍니다. 표현식 `let a := t1; t2`는 `t2` 내에 등장하는 모든 `a`를 `t1`으로 대체한 결과와 정의적으로 동일합니다.

```
#check let y := 2 + 2; y * y
```

```
let y := 2 + 2;
y * y : Nat
```

```
#eval let y := 2 + 2; y * y
```

```
16
```

```
def twice_double (x : Nat) : Nat :=
let y := x + x; y * y
#eval twice_double 2
```

```
16
```

Here, `twice_double x` is definitionally equal to the term `(x + x) * (x + x)`.

여기서 `twice_double x`는 항 `(x + x) * (x + x)`와 정의적으로 동등합니다.

You can combine multiple assignments by chaining `let` statements:

`let` 문을 연결하여 여러 할당을 결합할 수 있습니다:

```
#check let y := 2 + 2; let z := y + y; z * z
```

```
let y := 2 + 2;
let z := y + y;
z * z : Nat
```

```
#eval let y := 2 + 2; let z := y + y; z * z
```

```
64
```

The `;` can be omitted when a line break is used.

줄 바꿈을 사용할 때는 `;`를 생략할 수 있습니다.

```
def t (x : Nat) : Nat :=
let y := x + x
y * y
```

Notice that the meaning of the expression `let a := t1; t2` is very
similar to the meaning of `(fun a => t2) t1`, but the two are not
the same. In the first expression, you should think of every instance
of `a` in `t2` as a syntactic abbreviation for `t1`. In the
second expression, `a` is a variable, and the expression
`fun a => t2` has to make sense independently of the value of `a`.
The `let` construct is a stronger means of abbreviation, and there
are expressions of the form `let a := t1; t2` that cannot be
expressed as `(fun a => t2) t1`. As an exercise, try to understand
why the definition of `foo` below type checks, but the definition of
`bar` does not.

표현식 `let a := t1; t2`의 의미는 `(fun a => t2) t1`의 의미와 매우 유사하지만, 둘은 같지 않습니다. 첫 번째 표현식에서, `t2`의 `a`의 모든 인스턴스를 `t1`에 대한 문법적 약자로 생각해야 합니다. 두 번째 표현식에서, `a`는 변수이며, 표현식 `fun a => t2`는 `a`의 값과 관계없이 독립적으로 의미를 가져야 합니다. `let` 구조는 더 강력한 약자의 수단이며, `let a := t1; t2` 형태의 표현식이 `(fun a => t2) t1`으로 표현될 수 없는 경우가 있습니다. 연습으로, 아래의 `foo` 정의는 타입이 확인되지만, `bar` 정의는 그렇지 않은 이유를 이해해 보세요.

```
def foo := let a := Nat; fun x : a => x + 2
/-
  def bar := (fun a => fun x : a => x + 2) Nat
-/
```

## 2.6. Variables and Sections

Consider the following three function definitions:

다음 세 함수 정의를 고려하세요:

```
def compose (α β γ : Type) (g : β → γ) (f : α → β) (x : α) : γ :=
g (f x)
def doTwice (α : Type) (h : α → α) (x : α) : α :=
h (h x)
def doThrice (α : Type) (h : α → α) (x : α) : α :=
h (h (h x))
```

Lean provides you with the `variable` command to make such
declarations look more compact:

Lean은 그러한 선언들을 더 간결하게 만들기 위해 `variable` 명령을 제공합니다:

```
variable (α β γ : Type)
def compose (g : β → γ) (f : α → β) (x : α) : γ :=
g (f x)
def doTwice (h : α → α) (x : α) : α :=
h (h x)
def doThrice (h : α → α) (x : α) : α :=
h (h (h x))
```

You can declare variables of any type, not just `Type` itself:

`Type` 자체가 아닌 모든 타입의 변수를 선언할 수 있습니다:

```
variable (α β γ : Type)
variable (g : β → γ) (f : α → β) (h : α → α)
variable (x : α)
def compose := g (f x)
def doTwice := h (h x)
def doThrice := h (h (h x))
#print compose
```

```
def compose : (α β γ : Type) → (β → γ) → (α → β) → α → γ :=
fun α β γ g f x => g (f x)
```

```
#print doTwice
```

```
def doTwice : (α : Type) → (α → α) → α → α :=
fun α h x => h (h x)
```

```
#print doThrice
```

```
def doThrice : (α : Type) → (α → α) → α → α :=
fun α h x => h (h (h x))
```

Printing them out shows that all three groups of definitions have
exactly the same effect.

이를 출력해 보면 이 세 그룹의 정의가 완전히 동일한 효과를 가짐을 보여줍니다.

The `variable` command instructs Lean to insert the declared
variables as bound variables in definitions that refer to them by
name. Lean is smart enough to figure out which variables are used
explicitly or implicitly in a definition. You can therefore proceed as
though `α`, `β`, `γ`, `g`, `f`, `h`, and `x` are fixed
objects when you write your definitions, and let Lean abstract the
definitions for you automatically.

`variable` 명령은 선언된 변수를 이름으로 참조하는 정의에서 바운드 변수로 삽입하도록 Lean에 지시합니다. Lean은 어떤 변수가 정의에서 명시적으로 또는 암시적으로 사용되는지 알아낼 만큼 똑똑합니다. 따라서 정의를 작성할 때 `α`, `β`, `γ`, `g`, `f`, `h`, `x`가 고정된 객체인 것처럼 진행할 수 있으며, Lean이 자동으로 정의를 추상화하도록 할 수 있습니다.

When declared in this way, a variable stays in scope until the end of
the file you are working on. Sometimes, however, it is useful to limit
the scope of a variable. For that purpose, Lean provides the notion of
a `section`:

이러한 방식으로 선언되면, 변수는 작업 중인 파일의 끝까지 범위 내에 있습니다. 그러나 때로는 변수의 범위를 제한하는 것이 유용합니다. 이를 위해 Lean은 `section`의 개념을 제공합니다:

```
section useful
 variable (α β γ : Type)
 variable (g : β → γ) (f : α → β) (h : α → α)
 variable (x : α)
 def compose := g (f x)
 def doTwice := h (h x)
 def doThrice := h (h (h x))
end useful
```

When the section is closed, the variables go out of scope, and cannot
be referenced any more.

섹션이 닫히면 변수는 스코프를 벗어나므로 더 이상 참조할 수 없습니다.

You do not have to indent the lines within a section. Nor do you have
to name a section, which is to say, you can use an anonymous
`section` / `end` pair. If you do name a section, however, you
have to close it using the same name. Sections can also be nested,
which allows you to declare new variables incrementally.

섹션 내의 줄들을 들여쓸 필요는 없습니다. 또한 섹션의 이름을 지정할 필요도 없습니다. 즉, 익명의 `section` / `end` 쌍을 사용할 수 있습니다. 그러나 섹션의 이름을 지정하는 경우, 같은 이름을 사용하여 닫아야 합니다. 섹션은 중첩될 수도 있으므로, 새로운 변수를 증분적으로 선언할 수 있습니다.

## 2.7. Namespaces

Lean provides you with the ability to group definitions into nested,
hierarchical *namespaces*:

Lean은 정의를 중첩되고 계층적인 *네임스페이스(namespaces)*로 그룹화할 수 있는 기능을 제공합니다:

```
namespace Foo
 def a : Nat := 5
 def f (x : Nat) : Nat := x + 7
 def fa : Nat := f a
 def ffa : Nat := f (f a)
 #check a
```

```
Foo.a : Nat
```

```
 #check f
```

```
Foo.f (x : Nat) : Nat
```

```
 #check fa
```

```
Foo.fa : Nat
```

```
 #check ffa
```

```
Foo.ffa : Nat
```

```
 #check Foo.fa
```

```
Foo.fa : Nat
```

```
end Foo
-- #check a  -- error
-- #check f  -- error
#check Foo.a
```

```
Foo.a : Nat
```

```
#check Foo.f
```

```
Foo.f (x : Nat) : Nat
```

```
#check Foo.fa
```

```
Foo.fa : Nat
```

```
#check Foo.ffa
```

```
Foo.ffa : Nat
```

```
open Foo
#check a
```

```
Foo.a : Nat
```

```
#check f
```

```
Foo.f (x : Nat) : Nat
```

```
#check fa
```

```
Foo.fa : Nat
```

```
#check Foo.fa
```

```
Foo.fa : Nat
```

When you declare that you are working in the namespace `Foo`, every
identifier you declare has a full name with prefix “`Foo.`”. Within
the namespace, you can refer to identifiers by their shorter names,
but once you end the namespace, you have to use the longer names.
Unlike `section`, namespaces require a name. There is only one
anonymous namespace at the root level.

`Foo` 네임스페이스에서 작업한다고 선언하면, 선언하는 모든 식별자는 "`Foo.`"라는 접두사가 붙은 전체 이름을 갖게 됩니다. 네임스페이스 내에서는 더 짧은 이름으로 식별자를 참조할 수 있지만, 네임스페이스를 종료하면 더 긴 이름을 사용해야 합니다. `section`과 달리 네임스페이스는 이름이 필요합니다. 루트 레벨에는 하나의 익명 네임스페이스만 존재합니다.

The `open` command brings the shorter names into the current
context. Often, when you import a module, you will want to open one or
more of the namespaces it contains, to have access to the short
identifiers. But sometimes you will want to leave this information
protected by a fully qualified name, for example, when they conflict
with identifiers in another namespace you want to use. Thus namespaces
give you a way to manage names in your working environment.

`open` 명령은 짧은 이름들을 현재 문맥으로 가져옵니다. 종종 모듈을 가져올 때, 짧은 식별자에 접근하기 위해 포함된 네임스페이스 중 하나 이상을 열고 싶을 것입니다. 그러나 때때로 이 정보를 정규화된 이름으로 보호하고 싶을 수 있습니다. 예를 들어, 사용하고 싶은 다른 네임스페이스의 식별자와 충돌할 때입니다. 따라서 네임스페이스는 작업 환경에서 이름을 관리하는 방법을 제공합니다.

For example, Lean groups definitions and theorems involving lists into
a namespace `List`.

예를 들어, Lean은 리스트와 관련된 정의 및 정리를 `List` 네임스페이스로 그룹화합니다.

```
#check List.nil
```

```
List.nil.{u} {α : Type u} : List α
```

```
#check List.cons
```

```
List.cons.{u} {α : Type u} (head : α) (tail : List α) : List α
```

```
#check List.map
```

```
List.map.{u_1, u_2} {α : Type u_1} {β : Type u_2} (f : α → β) (l : List α) : List β
```

The command `open List` allows you to use the shorter names:

`open List` 명령을 사용하면 더 짧은 이름을 사용할 수 있습니다:

```
open List
#check nil
```

```
List.nil.{u} {α : Type u} : List α
```

```
#check cons
```

```
List.cons.{u} {α : Type u} (head : α) (tail : List α) : List α
```

```
#check map
```

```
List.map.{u_1, u_2} {α : Type u_1} {β : Type u_2} (f : α → β) (l : List α) : List β
```

Like sections, namespaces can be nested:

섹션과 마찬가지로 네임스페이스도 중첩될 수 있습니다:

```
namespace Foo
 def a : Nat := 5
 def f (x : Nat) : Nat := x + 7
 def fa : Nat := f a
 namespace Bar
 def ffa : Nat := f (f a)
 #check fa
```

```
Foo.fa : Nat
```

```
 #check ffa
```

```
Foo.Bar.ffa : Nat
```

```
 end Bar
 #check fa
```

```
Foo.fa : Nat
```

```
 #check Bar.ffa
```

```
Foo.Bar.ffa : Nat
```

```
end Foo
#check Foo.fa
```

```
Foo.fa : Nat
```

```
#check Foo.Bar.ffa
```

```
Foo.Bar.ffa : Nat
```

```
open Foo
#check fa
```

```
Foo.fa : Nat
```

```
#check Bar.ffa
```

```
Foo.Bar.ffa : Nat
```

Namespaces that have been closed can later be reopened, even in another file:

닫힌 네임스페이스는 나중에 다른 파일에서라도 다시 열 수 있습니다:

```
namespace Foo
 def a : Nat := 5
 def f (x : Nat) : Nat := x + 7
 def fa : Nat := f a
end Foo
#check Foo.a
```

```
Foo.a : Nat
```

```
#check Foo.f
```

```
Foo.f (x : Nat) : Nat
```

```
namespace Foo
 def ffa : Nat := f (f a)
end Foo
```

Like sections, nested namespaces have to be closed in the order they
are opened. Namespaces and sections serve different purposes:
namespaces organize data and sections declare variables for insertion
in definitions. Sections are also useful for delimiting the scope of
commands such as `set_option` and `open`.

In many respects, however, a `namespace` ... `end` block behaves the same as a `section` ... `end` block. In particular, if you use the `variable` command within a namespace, its scope is limited to the namespace. Similarly, if you use an `open` command within a namespace, its effects disappear when the namespace is closed.

섹션과 마찬가지로 중첩된 네임스페이스는 열린 순서에 따라 닫아야 합니다. 네임스페이스와 섹션은 서로 다른 목적을 가지고 있습니다: 네임스페이스는 데이터를 구성하고 섹션은 정의에 삽입할 변수를 선언합니다. 섹션은 `set_option` 및 `open`과 같은 명령어의 스펙(범위)을 구분하는 데도 유용합니다.

그러나 많은 측면에서, `namespace` `...` `end` 블록은 `section` `...` `end` 블록과 같은 방식으로 작동합니다. 특히, 네임스페이스 내에서 `variable` 명령을 사용하면 범위가 네임스페이스로 제한됩니다. 마찬가지로, 네임스페이스 내에서 `open` 명령을 사용하면 네임스페이스가 닫힐 때 그 효과가 사라집니다.

## 2.8. What makes dependent type theory dependent?

The short explanation is that types can depend on parameters. You
have already seen a nice example of this: the type `List α` depends
on the argument `α`, and this dependence is what distinguishes
`List Nat` and `List Bool`. For another example, consider the
type `Vector α n`, the type of vectors of elements of `α` of
length `n`. This type depends on *two* parameters: the type of the
elements in the vector (`α : Type`) and the length of the vector
`n : Nat`.

간단한 설명은 타입이 매개변수에 따라 달라질 수 있다는 것입니다. 당신은 이미 좋은 예제를 보았습니다: 타입 `List α`는 인수 `α`에 따라 달라지며, 이 의존성이 `List Nat`과 `List Bool`을 구별하는 것입니다. 다른 예제로, 타입 `Vector α n`, 길이 `n`의 `α` 원소들의 벡터의 타입을 고려하세요. 이 타입은 *두* 개의 매개변수에 따라 달라집니다: 벡터의 원소들의 타입(`α : Type`)과 벡터의 길이 `n : Nat`입니다.

Suppose you wish to write a function `cons` which inserts a new
element at the head of a list. What type should `cons` have? Such a
function is *polymorphic*: you expect the `cons` function for
`Nat`, `Bool`, or an arbitrary type `α` to behave the same way.
So it makes sense to take the type to be the first argument to
`cons`, so that for any type, `α`, `cons α` is the insertion
function for lists of type `α`. In other words, for every `α`,
`cons α` is the function that takes an element `a : α` and a list
`as : List α`, and returns a new list, so you have `cons α a as : List α`.

리스트의 맨 앞에 새로운 요소를 삽입하는 함수 `cons`를 작성하고 싶다고 가정해 봅시다. `cons`는 어떤 타입을 가져야 할까요? 그러한 함수는 *다형성(polymorphic)*을 띠어야 합니다: 여러분은 `Nat`, `Bool`, 또는 임의의 타입 `α`에 대한 `cons` 함수가 동일한 방식으로 작동하기를 기대할 것입니다. 따라서 타입을 `cons`의 첫 번째 인자로 취하여, 어떤 타입 `α`에 대해서든 `cons α`가 `α` 타입의 리스트를 위한 삽입 함수가 되도록 하는 것이 타당합니다. 다시 말해, 모든 `α`에 대해 `cons α`는 요소 `a : α`와 리스트 `as : List α`를 받아 새로운 리스트를 반환하는 함수이므로, 결과적으로 `cons α a as : List α`를 가지게 됩니다.

It is clear that `cons α` should have type `α → List α → List α`.
But what type should `cons` have? A first guess might be
`Type → α → List α → List α`, but, on reflection, this does not make
sense: the `α` in this expression does not refer to anything,
whereas it should refer to the argument of type `Type`. In other
words, *assuming* `α : Type` is the first argument to the function,
the type of the next two elements are `α` and `List α`. These
types vary depending on the first argument, `α`.

`cons α`가 `α → List α → List α` 타입을 가져야 한다는 것은 명확합니다. 그러나 `cons`의 타입은 무엇이어야 할까요? 첫 번째 추측은 `Type → α → List α → List α`일 수 있지만, 생각해보면 이것은 의미가 없습니다: 이 표현식의 `α`는 아무것도 참조하지 않으며, `Type` 타입의 인수를 참조해야 합니다. 다시 말해, *`α : Type`이 함수의 첫 번째 인수라고 가정할 때*, 다음 두 원소들의 타입은 `α`와 `List α`입니다. 이러한 타입은 첫 번째 인수 `α`에 따라 달라집니다.

```
def cons (α : Type) (a : α) (as : List α) : List α :=
List.cons a as
#check cons Nat
```

```
cons Nat : Nat → List Nat → List Nat
```

```
#check cons Bool
```

```
cons Bool : Bool → List Bool → List Bool
```

```
#check cons
```

```
cons (α : Type) (a : α) (as : List α) : List α
```

This is an instance of a *dependent function type*, or **dependent
arrow type**. Given `α : Type` and `β : α → Type`, think of `β`
as a family of types over `α`, that is, a type `β a` for each
`a : α`. In that case, the type `(a : α) → β a` denotes the type
of functions `f` with the property that, for each `a : α`, `f a`
is an element of `β a`. In other words, the type of the value
returned by `f` depends on its input.

이것이 *종속 함수 타입(dependent function type)*, 혹은 **종속 화살표 타입(dependent arrow type)**의 한 예입니다. `α : Type`과 `β : α → Type`이 주어졌을 때, `β`를 `α`에 대한 타입 족(family of types)으로, 즉 각 `a : α`에 대한 타입 `β a`로 생각해 보십시오. 그런 경우에, 타입 `(a : α) → β a`는 각 `a : α`에 대해 `f a`가 `β a`의 요소가 되는 특성을 가진 함수 `f`의 타입을 나타냅니다. 다른 말로 표현하자면, 함수 `f`에 의해 반환되는 값의 타입이 그 입력에 의존하는 것을 의미합니다.

Notice that `(a : α) → β` makes sense for any expression `β : Type`.
When the value of `β` depends on `a` (as does, for
example, the expression `β a` in the previous paragraph),
`(a : α) → β` denotes a dependent function type. When `β` doesn't
depend on `a`, `(a : α) → β` is no different from the type
`α → β`. Indeed, in dependent type theory (and in Lean), `α → β`
is just notation for `(a : α) → β` when `β` does not depend on `a`.

`(a : α) → β`는 모든 표현식 `β : Type`에 대해 의미가 있습니다. `β`의 값이 `a`에 따라 달라질 때 (예를 들어, 이전 문단의 표현식 `β a`와 같이), `(a : α) → β`는 종속 함수 타입을 나타냅니다. `β`가 `a`에 따라 달라지지 않을 때, `(a : α) → β`는 타입 `α → β`와 다르지 않습니다. 실제로, 종속 타입 이론(그리고 Lean)에서, `α → β`는 `β`가 `a`에 따라 달라지지 않을 때 `(a : α) → β`의 표기법일 뿐입니다.

Returning to the example of lists, you can use the command `#check` to
inspect the type of the following `List` functions. The `@` symbol
and the difference between the round and curly braces will be
explained momentarily.

목록의 예제로 돌아가면, `#check` 명령을 사용하여 다음 `List` 함수들의 타입을 확인할 수 있습니다. `@` 기호와 둥근 괄호와 중괄호 사이의 차이는 잠시 후에 설명할 것입니다.

```
#check @List.cons
```

```
@List.cons : {α : Type u_1} → α → List α → List α
```

```
#check @List.nil
```

```
@List.nil : {α : Type u_1} → List α
```

```
#check @List.length
```

```
@List.length : {α : Type u_1} → List α → Nat
```

```
#check @List.append
```

```
@List.append : {α : Type u_1} → List α → List α → List α
```

Just as dependent function types `(a : α) → β a` generalize the
notion of a function type `α → β` by allowing `β` to depend on
`a`, dependent Cartesian product types `(a : α) × β a` generalize
the Cartesian product `α × β` in the same way. Dependent products
are also called *sigma* types, and you can also write them as
`Σ a : α, β a`. You can use `⟨a, b⟩` or `Sigma.mk a b` to create a
dependent pair. The `⟨` and `⟩` characters may be typed with
`\langle` and `\rangle` or `\<` and `\>`, respectively.

종속 함수 타입 `(a : α) → β a`가 `β`가 `a`에 따라 달라지도록 하여 함수 타입 `α → β`의 개념을 일반화하는 것처럼, 종속 데카르트 곱 타입 `(a : α) × β a`는 같은 방식으로 데카르트 곱 `α × β`를 일반화합니다. 종속 곱은 또한 *시그마(sigma)* 타입이라고 불리며, `Σ a : α, β a`로도 쓸 수 있습니다. `⟨a, b⟩` 또는 `Sigma.mk a b`를 사용하여 종속 쌍을 만들 수 있습니다. `⟨` 및 `⟩` 문자는 각각 `\langle` 및 `\rangle` 또는 `\<` 및 `\>`로 입력할 수 있습니다.

```
universe u v
def f (α : Type u) (β : α → Type v) (a : α) (b : β a) : (a : α) × β a :=
⟨a, b⟩
def g (α : Type u) (β : α → Type v) (a : α) (b : β a) : Σ a : α, β a :=
Sigma.mk a b
def h1 (x : Nat) : Nat :=
(f Type (fun α => α) Nat x).2
#eval h1 5
```

```
5
```

```
def h2 (x : Nat) : Nat :=
(g Type (fun α => α) Nat x).2
#eval h2 5
```

```
5
```

The functions `f` and `g` above denote the same function.

위의 함수 `f`와 `g`는 같은 함수를 나타냅니다.

## 2.9. Implicit Arguments

Suppose we have an implementation of lists as:

우리가 리스트를 다음과 같이 구현했다고 가정해 봅시다:

```
#check Lst
```

```
Lst.{u} (α : Type u) : Type u
```

```
#check Lst.cons
```

```
Lst.cons.{u} (α : Type u) (a : α) (as : Lst α) : Lst α
```

```
#check Lst.nil
```

```
Lst.nil.{u} (α : Type u) : Lst α
```

```
#check Lst.append
```

```
Lst.append.{u} (α : Type u) (as bs : Lst α) : Lst α
```

Then, you can construct lists of `Nat` as follows:

그런 다음 그림과 같이 `Nat` 리스트를 구성할 수 있습니다:

```
#check Lst.cons Nat 0 (Lst.nil Nat)
```

```
Lst.cons Nat 0 (Lst.nil Nat) : Lst Nat
```

```
def as : Lst Nat := Lst.nil Nat
def bs : Lst Nat := Lst.cons Nat 5 (Lst.nil Nat)
#check Lst.append Nat as bs
```

```
Lst.append Nat as bs : Lst Nat
```

Because the constructors are polymorphic over types, we have to insert
the type `Nat` as an argument repeatedly. But this information is
redundant: one can infer the argument `α` in
`Lst.cons Nat 5 (Lst.nil Nat)` from the fact that the second argument, `5`, has
type `Nat`. One can similarly infer the argument in `Lst.nil Nat`, not
from anything else in that expression, but from the fact that it is
sent as an argument to the function `Lst.cons`, which expects an element
of type `Lst α` in that position.

생성자가 타입에 대해 다형적이기 때문에, 타입 `Nat`을 인수로 반복해서 삽입해야 합니다. 그러나 이 정보는 중복됩니다: 두 번째 인수 `5`가 `Nat` 타입을 가진다는 사실에서 `Lst.cons Nat 5 (Lst.nil Nat)`의 인수 `α`를 추론할 수 있습니다. 마찬가지로 `Lst.nil Nat`의 인수를 추론할 수 있으며, 그 표현식의 다른 것에서가 아니라, 그것이 그 위치에서 `Lst α` 타입의 원소를 기대하는 함수 `Lst.cons`에 인수로 전송된다는 사실에서 추론할 수 있습니다.

This is a central feature of dependent type theory: terms carry a lot
of information, and often some of that information can be inferred
from the context. In Lean, one uses an underscore, `_`, to specify
that the system should fill in the information automatically. This is
known as an “implicit argument.”

이는 종속 타입 이론의 핵심 특징 중 하나입니다: 항들은 많은 정보를 가지고 있으며, 종종 문맥에서 그 정보의 일부를 유추할 수 있습니다. Lean에서는 주로 밑줄 `_`을 사용하여 시스템이 해당 정보를 자동으로 추론해 채우도록 지정합니다. 이것은 "암묵적 인자(implicit argument)"라고 알려져 있습니다.

```
#check Lst.cons _ 0 (Lst.nil _)
```

```
Lst.cons Nat 0 (Lst.nil Nat) : Lst Nat
```

```
def as : Lst Nat := Lst.nil _
def bs : Lst Nat := Lst.cons _ 5 (Lst.nil _)
#check Lst.append _ as bs
```

```
Lst.append Nat as bs : Lst Nat
```

It is still tedious, however, to type all these underscores. When a
function takes an argument that can generally be inferred from
context, Lean allows you to specify that this argument should, by
default, be left implicit. This is done by putting the arguments in
curly braces, as follows:

그러나 이 모든 밑줄을 입력하는 것은 여전히 지루합니다. 함수가 일반적으로 문맥에서 추론될 수 있는 인수를 취할 때, Lean은 이 인수가 기본적으로 암시적으로 남겨져야 함을 지정할 수 있게 해줍니다. 이는 다음과 같이 인수를 중괄호로 넣어서 수행됩니다:

```
universe u
def Lst (α : Type u) : Type u := List α
def Lst.cons {α : Type u} (a : α) (as : Lst α) : Lst α := List.cons a as
def Lst.nil {α : Type u} : Lst α := List.nil
def Lst.append {α : Type u} (as bs : Lst α) : Lst α := List.append as bs
#check Lst.cons 0 Lst.nil
```

```
Lst.cons 0 Lst.nil : Lst Nat
```

```
def as : Lst Nat := Lst.nil
def bs : Lst Nat := Lst.cons 5 Lst.nil
#check Lst.append as bs
```

```
as.append bs : Lst Nat
```

All that has changed are the braces around `α : Type u` in the
declaration of the variables. We can also use this device in function
definitions:

변경된 것은 변수 선언에서 `α : Type u` 주위의 중괄호뿐입니다. 함수 정의에서도 이 방법을 사용할 수 있습니다:

```
universe u
def ident {α : Type u} (x : α) := x
```

Checking the type of `ident` requires wrapping it in parentheses to avoid having its signature shown:

`ident`의 타입을 확인할 때 타입 시그니처가 표시되지 않도록 괄호로 감싸야 합니다:

```
#check (ident)
```

```
ident : ?m.1 → ?m.1
```

```
#check ident 1
```

```
ident 1 : Nat
```

```
#check ident "hello"
```

```
ident "hello" : String
```

```
#check @ident
```

```
@ident : {α : Type u_1} → α → α
```

The makes the first argument to `ident` implicit. Notationally,
this hides the specification of the type, making it look as though
`ident` simply takes an argument of any type. In fact, the function
`id` is defined in the standard library in exactly this way. We have
chosen a nontraditional name here only to avoid a clash of names.

이것은 `ident`의 첫 번째 인자를 암묵적으로 만듭니다. 표기상으로 이것은 타입의 명세를 숨겨서, 마치 `ident`가 단순하게 아무 타입의 인자나 하나 취하는 것처럼 보이게 만듭니다. 사실 표준 라이브러리(standard library)에 정의된 함수 `id`도 정확히 이 방식으로 정의되어 있습니다. 여기서 전통적이지 않은 이름을 선택한 것은 오로지 이름 충돌을 피하기 위해서일 뿐입니다.

Variables can also be specified as implicit when they are declared with
the `variable` command:

변수는 `variable` 명령으로 선언될 때에도 암묵적으로 지정될 수 있습니다:

```
universe u
section
 variable {α : Type u}
 variable (x : α)
 def ident := x
end
#check ident
```

```
ident.{u} {α : Type u} (x : α) : α
```

```
#check ident 4
```

```
ident 4 : Nat
```

```
#check ident "hello"
```

```
ident "hello" : String
```

This definition of `ident` here has the same effect as the one
above.

여기서 `ident`의 이 정의는 위의 것과 같은 효과를 가집니다.

Lean has very complex mechanisms for instantiating implicit arguments,
and we will see that they can be used to infer function types,
predicates, and even proofs. The process of instantiating these
“holes,” or “placeholders,” in a term is often known as
*elaboration*. The presence of implicit arguments means that at times
there may be insufficient information to fix the meaning of an
expression precisely. An expression like `id` or `List.nil` is
said to be *polymorphic*, because it can take on different meanings in
different contexts.

Lean은 암시적 인수를 인스턴스화하기 위한 매우 복잡한 메커니즘을 가지고 있으며, 이들을 함수 타입, 술어, 그리고 증명까지도 추론하는 데 사용할 수 있음을 알게 될 것입니다. 항에서 이러한 “구멍(holes)” 또는 “자리 표시자(placeholders)”를 인스턴스화하는 과정을 종종 *정교화(elaboration)*라고 부릅니다. 암시적 인수의 존재는 표현식의 의미를 정확히 고정할 충분한 정보가 없을 수 있다는 것을 의미합니다. `id` 또는 `List.nil`과 같은 표현식은 다양한 문맥에서 다양한 의미를 가질 수 있기 때문에 *다형적(polymorphic)*이라고 합니다.

One can always specify the type `T` of an expression `e` by
writing `(e : T)`. This instructs Lean's elaborator to use the value
`T` as the type of `e` when trying to resolve implicit
arguments. In the second pair of examples below, this mechanism is
used to specify the desired types of the expressions `id` and
`List.nil`:

`e`라는 표현식의 타입 `T`는 항상 `(e : T)`라고 쓰면 명시할 수 있습니다. 이것은 암묵적인 인자 해석을 시도할 때 식 `e`의 타입으로 `T`라는 값을 사용하도록 Lean의 엘래버레이터(elaborator)에 지시합니다. 다음 두 번째 예제 세트에서 이 메커니즘을 적용하여 식 `id`와 `List.nil`의 원하는 타입을 지정하는 데 사용되었습니다:

```
#check (List.nil)
```

```
[] : List ?m.1
```

```
#check (id)
```

```
id : ?m.1 → ?m.1
```

```
#check (List.nil : List Nat)
```

```
[] : List Nat
```

```
#check (id : Nat → Nat)
```

```
id : Nat → Nat
```

Numerals are overloaded in Lean, but when the type of a numeral cannot
be inferred, Lean assumes, by default, that it is a natural number. So
the expressions in the first two `#check` commands below are
elaborated in the same way, whereas the third `#check` command
interprets `2` as an integer.

수치는 Lean에서 오버로드되어 있지만, 수치의 타입을 추론할 수 없을 때, Lean은 기본적으로 그것이 자연수라고 가정합니다. 따라서 아래의 처음 두 `#check` 명령의 표현식은 같은 방식으로 정교화되지만, 세 번째 `#check` 명령은 `2`를 정수로 해석합니다.

```
#check 2
```

```
2 : Nat
```

```
#check (2 : Nat)
```

```
2 : Nat
```

```
#check (2 : Int)
```

```
2 : Int
```

Sometimes, however, we may find ourselves in a situation where we have
declared an argument to a function to be implicit, but now want to
provide the argument explicitly. If `foo` is such a function, the
notation `@foo` denotes the same function with all the arguments
made explicit.

그러나 가끔씩은 함수의 인자를 암묵적인 것으로 선언해 두었지만 실제로는 인자를 명시적으로 제공하고 싶을 때가 있습니다. 이 경우에 `foo`가 그러한 함수라면, 접두어 표기인 `@foo`를 통해 모든 인자를 명시적으로 나타낸 동일한 함수를 지시할 수 있습니다.

```
#check @id
```

```
@id : {α : Sort u_1} → α → α
```

```
#check @id Nat
```

```
id : Nat → Nat
```

```
#check @id Bool
```

```
id : Bool → Bool
```

```
#check @id Nat 1
```

```
id 1 : Nat
```

```
#check @id Bool true
```

```
id true : Bool
```

Notice that now the first `#check` command gives the type of the
identifier, `id`, without inserting any placeholders. Moreover, the
output indicates that the first argument is implicit.

이제 첫 번째 `#check` 명령이 자리 표시자를 삽입하지 않고 식별자 `id`의 타입을 제공함을 주목하세요. 더욱이, 출력은 첫 번째 인수가 암시적임을 나타냅니다.
