---
title: "3. 명제와 증명"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "theorem-proving", "type-theory"]
categories: ["programming"]
description: "명제를 타입으로 다루는 Curry-Howard 대응과 논리 연결사, 고전 논리를 이용한 증명 작성법을 다룹니다."
---

By now, you have seen some ways of defining objects and functions in
Lean. In this chapter, we will begin to explain how to write
mathematical assertions and proofs in the language of dependent type
theory as well.

지금까지 Lean에서 객체와 함수를 정의하는 방법들을 보았습니다. 이 장에서는 종속 타입 이론의 언어로 수학적 주장과 증명을 작성하는 방법을 설명하기 시작할 것입니다.

## 3.1. Propositions as Types

One strategy for proving assertions about objects defined in the
language of dependent type theory is to layer an assertion language
and a proof language on top of the definition language. But there is
no reason to multiply languages in this way: dependent type theory is
flexible and expressive, and there is no reason we cannot represent
assertions and proofs in the same general framework.

종속 타입 이론의 언어로 정의된 객체에 대한 주장을 증명하는 한 가지 전략은 정의 언어 위에 주장 언어와 증명 언어를 계층화하는 것입니다. 하지만 이러한 방식으로 언어를 복수화할 이유가 없습니다. 종속 타입 이론은 유연하고 표현력이 풍부하므로 주장과 증명을 동일한 일반적인 틀에서 표현할 수 없을 이유가 없습니다.

For example, we could introduce a new type, `Prop`, to represent
propositions, and introduce constructors to build new propositions
from others.

예를 들어, 명제를 나타내기 위해 새로운 타입 `Prop`을 도입하고, 다른 명제로부터 새로운 명제를 만들기 위한 생성자를 도입할 수 있습니다.

```
#check And
```

```
And (a b : Prop) : Prop
```

```
#check Or
```

```
Or (a b : Prop) : Prop
```

```
#check Not
```

```
Not (a : Prop) : Prop
```

```
#check Implies
```

```
Implies (p q : Prop) : Prop
```

```
variable (p q r : Prop)
#check And p q
```

```
p ∧ q : Prop
```

```
#check Or (And p q) r
```

```
p ∧ q ∨ r : Prop
```

```
#check Implies (And p q) (And q p)
```

```
Implies (p ∧ q) (q ∧ p) : Prop
```

We could then introduce, for each element `p : Prop`, another type
`Proof p`, for the type of proofs of `p`. An “axiom” would be a
constant of such a type.

그런 다음 각 원소 `p : Prop`에 대해, `p`의 증명의 타입인 다른 타입 `Proof p`를 도입할 수 있습니다. “공리”는 이러한 타입의 상수가 됩니다.

```
#check Proof
```

```
Proof (p : Prop) : Type
```

```
axiom and_commut (p q : Prop) : Proof (Implies (And p q) (And q p))
variable (p q : Prop)
#check and_commut p q
```

```
and_commut p q : Proof (Implies (p ∧ q) (q ∧ p))
```

In addition to axioms, however, we would also need rules to build new
proofs from old ones. For example, in many proof systems for
propositional logic, we have the rule of *modus ponens*:

하지만 공리 외에도, 우리는 기존 증명으로부터 새로운 증명을 만들기 위한 규칙이 필요할 것입니다. 예를 들어, 많은 명제 논리 증명 체계에서 우리는 *modus ponens* (양태 긍정법) 규칙을 가지고 있습니다:

From a proof of `Implies p q` and a proof of `p`, we obtain a proof of `q`.

> `Implies p q`의 증명과 `p`의 증명으로부터, 우리는 `q`의 증명을 얻습니다.

We could represent this as follows:

이를 다음과 같이 표현할 수 있습니다:

```
axiom modus_ponens (p q : Prop) :
Proof (Implies p q) → Proof p →
Proof q
```

Systems of natural deduction for propositional logic also typically rely on the following rule:

명제 논리를 위한 자연 연역 체계도 일반적으로 다음 규칙에 의존합니다:

Suppose that, assuming `p` as a hypothesis, we have a proof of `q`. Then we can “cancel” the hypothesis and obtain a proof of `Implies p q`.

> `p`를 가정으로 가정하면 `q`의 증명을 가진다고 가정합니다. 그러면 우리는 가정을 “취소”하고 `Implies p q`의 증명을 얻을 수 있습니다.

We could render this as follows:

이를 다음과 같이 표현할 수 있습니다:

```
axiom implies_intro (p q : Prop) :
(Proof p → Proof q) → Proof (Implies p q)
```

This approach would provide us with a reasonable way of building assertions and proofs.
Determining that an expression `t` is a correct proof of assertion `p` would then
simply be a matter of checking that `t` has type `Proof p`.

이러한 접근 방식은 주장과 증명을 만드는 합리적인 방법을 제공할 것입니다. 표현식 `t`가 주장 `p`의 올바른 증명인지 판단하는 것은 단순히 `t`가 `Proof p` 타입을 가지는지 확인하는 문제가 됩니다.

Some simplifications are possible, however. To start with, we can
avoid writing the term `Proof` repeatedly by conflating `Proof p`
with `p` itself. In other words, whenever we have `p : Prop`, we
can interpret `p` as a type, namely, the type of its proofs. We can
then read `t : p` as the assertion that `t` is a proof of `p`.

그러나 일부 단순화는 가능합니다. 시작하려면, `Proof p`와 `p` 자체를 동일시함으로써 `Proof` 항을 반복해서 쓰는 것을 피할 수 있습니다. 즉, `p : Prop`을 가질 때마다, `p`를 타입으로 해석할 수 있으며, 이는 그 증명들의 타입입니다. 그러면 `t : p`를 `t`가 `p`의 증명이라는 주장으로 읽을 수 있습니다.

Moreover, once we make this identification, the rules for implication
show that we can pass back and forth between `Implies p q` and
`p → q`. In other words, implication between propositions `p` and `q`
corresponds to having a function that takes any element of `p` to an
element of `q`. As a result, the introduction of the connective
`Implies` is entirely redundant: we can use the usual function space
constructor `p → q` from dependent type theory as our notion of
implication.

더욱이, 이 동일시를 하면, 함축에 대한 규칙들은 `Implies p q`와 `p → q` 사이를 왕복할 수 있음을 보여줍니다. 즉, 명제 `p`와 `q` 사이의 함축은 `p`의 임의의 원소를 `q`의 원소로 취하는 함수를 가지는 것에 대응됩니다. 결과적으로, 결합자 `Implies`의 도입은 완전히 중복입니다. 우리는 종속 타입 이론으로부터 일반적인 함수 공간 생성자 `p → q`를 함축의 개념으로 사용할 수 있습니다.

This is the approach followed in the Calculus of Constructions, and
hence in Lean as well. The fact that the rules for implication in a
proof system for natural deduction correspond exactly to the rules
governing abstraction and application for functions is an instance of
the *Curry-Howard isomorphism*, sometimes known as the
*propositions-as-types* paradigm. In fact, the type `Prop` is
syntactic sugar for `Sort 0`, the very bottom of the type hierarchy
described in the last chapter. Moreover, `Type u` is also just
syntactic sugar for `Sort (u+1)`. `Prop` has some special
features, but like the other type universes, it is closed under the
arrow constructor: if we have `p q : Prop`, then `p → q : Prop`.

이것은 Calculus of Constructions에서 따르는 접근 방식이며, 따라서 Lean에서도 마찬가지입니다. 자연 연역을 위한 증명 체계의 함축 규칙이 함수의 추상화와 적용을 지배하는 규칙과 정확히 대응된다는 사실은 *Curry-Howard isomorphism*의 인스턴스이며, 때로는 *명제-타입-패러다임*으로도 알려져 있습니다. 실제로, 타입 `Prop`은 지난 장에서 설명한 타입 계층의 매우 하단인 `Sort 0`의 신택스 슈거입니다. 더욱이, `Type u`도 그냥 `Sort (u+1)`의 신택스 슈거입니다. `Prop`은 일부 특수한 특징을 가지고 있지만, 다른 타입 우주처럼, 화살표 생성자에 대해 닫혀 있습니다. `p q : Prop`을 가지면, `p → q : Prop`입니다.

There are at least two ways of thinking about propositions as
types. To some who take a constructive view of logic and mathematics,
this is a faithful rendering of what it means to be a proposition: a
proposition `p` represents a sort of data type, namely, a
specification of the type of data that constitutes a proof. A proof of
`p` is then simply an object `t : p` of the right type.

명제를 타입으로 생각하는 최소한 두 가지 방법이 있습니다. 논리와 수학의 구성적 견해를 취하는 사람들에게는, 이것이 명제가 무엇을 의미하는지에 대한 충실한 표현입니다. 즉, 명제 `p`는 일종의 데이터 타입을 나타내며, 증명을 구성하는 데이터의 타입을 명시합니다. 그러면 `p`의 증명은 단순히 올바른 타입의 객체 `t : p`입니다.

Those not inclined to this ideology can view it, rather, as a simple
coding trick. To each proposition `p` we associate a type that is
empty if `p` is false and has a single element, say `*`, if `p`
is true. In the latter case, let us say that (the type associated
with) `p` is *inhabited*. It just so happens that the rules for
function application and abstraction can conveniently help us keep
track of which elements of `Prop` are inhabited. So constructing an
element `t : p` tells us that `p` is indeed true. You can think of
the inhabitant of `p` as being the “fact that `p` is true.” A
proof of `p → q` uses “the fact that `p` is true” to obtain “the
fact that `q` is true.”

이 이념에 기울지 않는 사람들은 이를 단순한 코딩 기법으로 볼 수 있습니다. 각 명제 `p`에 대해, `p`가 거짓이면 비어 있고 `p`가 참이면 `*`라는 단일 원소를 가지는 타입을 연결합니다. 후자의 경우, `p`가 *거주된*(inhabited) 것이라고 합시다. 함수 적용과 추상화의 규칙이 `Prop`의 어떤 원소들이 거주되는지를 추적하는 데 편리하게 도움이 될 수 있다는 사실입니다. 따라서 원소 `t : p`를 구성하는 것은 `p`가 실제로 참이라는 것을 알려줍니다. `p`의 거주자를 “`p`가 참이라는 사실”로 생각할 수 있습니다. `p → q`의 증명은 “`p`가 참이라는 사실”을 사용하여 “`q`가 참이라는 사실”을 얻습니다.

Indeed, if `p : Prop` is any proposition, Lean's kernel treats any
two elements `t1 t2 : p` as being definitionally equal, much the
same way as it treats `(fun x => t) s` and `t[s/x]` as
definitionally equal. This is known as *proof irrelevance*, and is
consistent with the interpretation in the last paragraph. It means
that even though we can treat proofs `t : p` as ordinary objects in
the language of dependent type theory, they carry no information
beyond the fact that `p` is true.

실제로, `p : Prop`이 어떤 명제든, Lean의 커널은 `(fun x => t) s`와 `t[s/x]`를 정의적으로 동일하게 취급하는 것과 마찬가지로, `t1 t2 : p`인 임의의 두 원소를 정의적으로 동일한 것으로 취급합니다. 이는 *증명 무관성*으로 알려져 있으며, 이전 단락의 해석과 일치합니다. 이는 종속 타입 이론의 언어에서 증명 `t : p`를 일반 객체로 취급할 수 있지만, `p`가 참이라는 사실을 넘어서 어떤 정보도 전달하지 않는다는 것을 의미합니다.

The two ways we have suggested thinking about the
[propositions-as-types](#--tech-term-propositions-as-types) paradigm differ in a fundamental way. From the
constructive point of view, proofs are abstract mathematical objects
that are *denoted* by suitable expressions in dependent type
theory. In contrast, if we think in terms of the coding trick
described above, then the expressions themselves do not denote
anything interesting. Rather, it is the fact that we can write them
down and check that they are well-typed that ensures that the
proposition in question is true. In other words, the expressions
*themselves* are the proofs.

우리가 제시한 [명제-타입-패러다임](#--tech-term-propositions-as-types)에 대해 생각하는 두 가지 방법은 근본적인 방식으로 다릅니다. 구성적 관점에서, 증명은 종속 타입 이론의 적절한 표현식으로 *표현되는* 추상적인 수학적 객체입니다. 대조적으로, 위에서 설명한 코딩 기법 관점에서 생각하면, 표현식 자체는 특별히 흥미로운 것을 나타내지 않습니다. 오히려, 우리가 이들을 쓸 수 있고 그것들이 잘 입력되는지 확인할 수 있다는 사실이 해당 명제가 참이라는 것을 보장합니다. 즉, 표현식 *자체*가 증명입니다.

In the exposition below, we will slip back and forth between these two
ways of talking, at times saying that an expression “constructs” or
“produces” or “returns” a proof of a proposition, and at other times
simply saying that it “is” such a proof. This is similar to the way
that computer scientists occasionally blur the distinction between
syntax and semantics by saying, at times, that a program “computes” a
certain function, and at other times speaking as though the program
“is” the function in question.

아래의 설명에서, 우리는 이 두 가지 말하기 방식 사이를 왕복할 것입니다. 때로는 표현식이 명제의 증명을 “구성한다” 또는 “생성한다” 또는 “반환한다”고 말하고, 다른 때는 단순히 그것이 “그러한 증명이다”라고 말합니다. 이는 컴퓨터 과학자들이 때로는 프로그램이 특정 함수를 “계산한다”고 말하면서 구문과 의미 간의 구분을 흐릿하게 하는 방식과 유사하며, 다른 때는 프로그램이 해당 함수”이다”인 것처럼 이야기합니다.

In any case, all that really matters is the bottom line. To formally
express a mathematical assertion in the language of dependent type
theory, we need to exhibit a term `p : Prop`. To *prove* that
assertion, we need to exhibit a term `t : p`. Lean's task, as a
proof assistant, is to help us to construct such a term, `t`, and to
verify that it is well-formed and has the correct type.

어쨌든, 정말 중요한 것은 핵심입니다. 종속 타입 이론의 언어로 수학적 주장을 형식적으로 표현하려면, 항 `p : Prop`을 제시해야 합니다. 그 주장을 *증명*하려면, 항 `t : p`를 제시해야 합니다. 증명 보조자로서 Lean의 작업은 우리가 그러한 항 `t`를 구성하는 것을 돕고, 그것이 잘 형성되고 올바른 타입을 가지는지 검증하는 것입니다.

## 3.2. Working with Propositions as Types

In the [propositions-as-types](#--tech-term-propositions-as-types) paradigm, theorems involving only `→`
can be proved using lambda abstraction and application. In Lean, the
`theorem` command introduces a new theorem:

[명제-타입-패러다임](#--tech-term-propositions-as-types)에서, `→`만 포함하는 정리들은 람다 추상화와 적용을 사용하여 증명할 수 있습니다. Lean에서, `theorem` 명령은 새로운 정리를 도입합니다:

```
set_option linter.unusedVariables false
---
variable {p : Prop}
variable {q : Prop}
theorem t1 : p → q → p := fun hp : p => fun hq : q => hp
```

Compare this proof to the expression `fun x : α => fun y : β => x`
of type `α → β → α`, where `α` and `β` are data types.
This describes the function that takes arguments `x` and `y`
of type `α` and `β`, respectively, and returns `x`.
The proof of `t1` has the same form, the only difference being that
`p` and `q` are elements of `Prop` rather than `Type`.
Intuitively, our proof of
`p → q → p` assumes `p` and `q` are true, and uses the first
hypothesis (trivially) to establish that the conclusion, `p`, is
true.

이 증명을 `α → β → α` 타입의 표현식 `fun x : α => fun y : β => x`와 비교하세요. 여기서 `α`와 `β`는 데이터 타입입니다. 이는 `α`와 `β` 타입의 인자 `x`와 `y`를 취하고 `x`를 반환하는 함수를 설명합니다. `t1`의 증명은 같은 형식이며, 유일한 차이는 `p`와 `q`가 `Type`이 아닌 `Prop`의 원소라는 것입니다. 직관적으로, `p → q → p`의 우리의 증명은 `p`와 `q`가 참이라고 가정하고, 첫 번째 가정(자명하게)을 사용하여 결론 `p`가 참이라는 것을 확립합니다.

Note that the `theorem` command is really a version of the
`def` command: under the propositions and types
correspondence, proving the theorem `p → q → p` is really the same
as defining an element of the associated type. To the kernel type
checker, there is no difference between the two.

`theorem` 명령은 실제로 `def` 명령의 버전입니다. 명제와 타입의 대응 하에, `p → q → p` 정리를 증명하는 것은 실제로 관련 타입의 원소를 정의하는 것과 같습니다. 커널 타입 체커에게는 둘 사이에 차이가 없습니다.

There are a few pragmatic differences between definitions and
theorems, however. In normal circumstances, it is never necessary to
unfold the “definition” of a theorem; by [proof irrelevance](#--tech-term-proof-irrelevance), any two
proofs of that theorem are definitionally equal. Once the proof of a
theorem is complete, typically we only need to know that the proof
exists; it doesn't matter what the proof is. In light of that fact,
Lean tags proofs as *irreducible*, which serves as a hint to the
parser (more precisely, the *elaborator*) that there is generally no
need to unfold them when processing a file. In fact, Lean is generally
able to process and check proofs in parallel, since assessing the
correctness of one proof does not require knowing the details of
another. Additionally, [section variables](../02-dependent-type-theory/#variables-and-sections)
that are referred to in the body of a definition are automatically added as
parameters, but only the variables referred to in a theorem's type are added.
This is because the way in which a statement is proved should not influence
the statement that is being proved.

그러나 정의와 정리 사이에는 몇 가지 실용적인 차이가 있습니다. 정상적인 상황에서는 정리의 “정의”를 펼칠 필요가 절대 없습니다. [증명 무관성](#--tech-term-proof-irrelevance)에 의해, 그 정리의 임의의 두 증명은 정의적으로 동일합니다. 정리의 증명이 완료되면, 일반적으로 우리는 증명이 존재한다는 것을 알아야 합니다. 증명이 무엇인지는 중요하지 않습니다. 그 사실에 비추어, Lean은 증명에 *기약적(irreducible)*인 태그를 붙이며, 이는 파일을 처리할 때 일반적으로 펼칠 필요가 없다는 것을 파서(더 정확히는, *엘래버레이터*)에 암시합니다. 실제로, Lean은 일반적으로 증명을 병렬로 처리하고 확인할 수 있으며, 한 증명의 정확성을 평가하는 것이 다른 증명의 세부 사항을 알 필요가 없기 때문입니다. 추가적으로, [섹션 변수](../02-dependent-type-theory/#variables-and-sections)는 정의의 본체에서 참조되면 자동으로 매개변수로 추가되지만, 정리의 타입에서 참조된 변수만 추가됩니다. 이는 명제가 증명되는 방식이 증명되는 명제에 영향을 미쳐서는 안 되기 때문입니다.

As with definitions, the `#print` command will show you the proof of
a theorem:

정의와 마찬가지로, `#print` 명령은 정리의 증명을 보여줍니다:

```
theorem t1 : p → q → p := fun hp : p => fun hq : q => hp
#print t1
```

```
theorem t1 : ∀ {p q : Prop}, p → q → p :=
fun {p q} hp hq => hp
```

Notice that the lambda abstractions `hp : p` and `hq : q` can be
viewed as temporary assumptions in the proof of `t1`. Lean also
allows us to specify the type of the final term `hp`, explicitly,
with a `show` statement:

람다 추상화 `hp : p`와 `hq : q`가 `t1`의 증명에서 임시 가정으로 볼 수 있음을 주목하세요. Lean은 또한 `show` 명령으로 최종 항 `hp`의 타입을 명시적으로 지정할 수 있게 합니다:

```
theorem t1 : p → q → p :=
fun hp : p =>
fun hq : q =>
show p from hp
```

Adding such extra information can improve the clarity of a proof and
help detect errors when writing a proof. The `show` command does
nothing more than annotate the type, and, internally, all the
presentations of `t1` that we have seen produce the same term.

이러한 추가 정보를 추가하면 증명의 명확성을 개선하고 증명을 작성할 때 오류를 감지하는 데 도움이 될 수 있습니다. `show` 명령은 단순히 타입을 주석 처리하고, 내부적으로 우리가 본 `t1`의 모든 표현은 같은 항을 생성합니다.

As with ordinary definitions, we can move the lambda-abstracted
variables to the left of the colon:

일반 정의와 마찬가지로, 람다-추상화된 변수를 콜론의 왼쪽으로 이동할 수 있습니다:

```
theorem t1 (hp : p) (hq : q) : p := hp
#print t1
```

```
theorem t1 : ∀ {p q : Prop}, p → q → p :=
fun {p q} hp hq => hp
```

We can use the theorem `t1` just as a function application:

우리는 정리 `t1`을 함수 적용처럼 사용할 수 있습니다:

```
theorem t1 (hp : p) (hq : q) : p := hp
axiom hp : p
theorem t2 : q → p := t1 hp
```

The `axiom` declaration postulates the existence of an
element of the given type and may compromise logical consistency. For
example, we can use it to postulate that the empty type `False` has an
element:

`axiom` 선언은 주어진 타입의 원소의 존재를 공준으로 설정하며 논리적 일관성을 손상시킬 수 있습니다. 예를 들어, 우리는 이를 사용하여 빈 타입 `False`가 원소를 가진다고 공준으로 설정할 수 있습니다:

```
axiom unsound : False
-- Everything follows from false
theorem ex : 1 = 0 :=
False.elim unsound
```

Declaring an “axiom” `hp : p` is tantamount to declaring that `p`
is true, as witnessed by `hp`. Applying the theorem
`t1 : p → q → p` to the fact `hp : p` that `p` is true yields the theorem
`t1 hp : q → p`.

“공리” `hp : p`를 선언하는 것은 `hp`에 의해 증거된 `p`가 참이라고 선언하는 것과 동등합니다. 정리 `t1 : p → q → p`를 `p`가 참이라는 사실 `hp : p`에 적용하면 정리 `t1 hp : q → p`를 생성합니다.

Recall that we can also write theorem `t1` as follows:

정리 `t1`을 다음과 같이 작성할 수도 있음을 기억하세요:

```
theorem t1 {p q : Prop} (hp : p) (hq : q) : p := hp
#print t1
```

```
theorem t1 : ∀ {p q : Prop}, p → q → p :=
fun {p q} hp hq => hp
```

The type of `t1` is now `∀ {p q : Prop}, p → q → p`. We can read
this as the assertion “for every pair of propositions `p q`, we have
`p → q → p`.” For example, we can move all parameters to the right
of the colon:

이제 `t1`의 타입은 `∀ {p q : Prop}, p → q → p`입니다. 이를 “모든 명제 쌍 `p q`에 대해, 우리는 `p → q → p`를 가진다”는 주장으로 읽을 수 있습니다. 예를 들어, 우리는 모든 매개변수를 콜론의 오른쪽으로 이동할 수 있습니다:

```
theorem t1 : ∀ {p q : Prop}, p → q → p :=
fun {p q : Prop} (hp : p) (hq : q) => hp
```

If `p` and `q` have been declared as [variables](../02-dependent-type-theory/#variables-and-sections), Lean will
generalize them for us automatically:

`p`와 `q`가 [변수](../02-dependent-type-theory/#variables-and-sections)로 선언되었다면, Lean은 자동으로 우리를 위해 일반화합니다:

```
variable {p q : Prop}
theorem t1 : p → q → p := fun (hp : p) (hq : q) => hp
```

When we generalize `t1` in such a way, we can then apply it to
different pairs of propositions, to obtain different instances of the
general theorem.

이러한 방식으로 `t1`을 일반화하면, 우리는 일반 정리의 다른 인스턴스를 얻기 위해 명제의 다른 쌍에 적용할 수 있습니다.

```
theorem t1 (p q : Prop) (hp : p) (hq : q) : p := hp
variable (p q r s : Prop)
#check t1 p q
```

```
t1 p q : p → q → p
```

```
#check t1 r s
```

```
t1 r s : r → s → r
```

```
#check t1 (r → s) (s → r)
```

```
t1 (r → s) (s → r) : (r → s) → (s → r) → r → s
```

```
variable (h : r → s)
#check t1 (r → s) (s → r) h
```

```
t1 (r → s) (s → r) h : (s → r) → r → s
```

Once again, using the [propositions-as-types](#--tech-term-propositions-as-types) correspondence, the
variable `h` of type `r → s` can be viewed as the hypothesis, or
premise, that `r → s` holds.

다시 한 번, [명제-타입-대응](#--tech-term-propositions-as-types)을 사용하면, `r → s` 타입의 변수 `h`는 `r → s`가 성립한다는 가정 또는 전제로 볼 수 있습니다.

As another example, let us consider the composition function discussed
in the last chapter, now with propositions instead of types.

또 다른 예로, 이전 장에서 논의한 구성 함수를 고려해봅시다. 이제 타입 대신 명제를 사용합니다.

```
variable (p q r s : Prop)
theorem t2 (h₁ : q → r) (h₂ : p → q) : p → r :=
fun h₃ : p =>
show r from h₁ (h₂ h₃)
```

As a theorem of propositional logic, what does `t2` say?

명제 논리의 정리로서, `t2`는 무엇을 말합니까?

Note that it is often useful to use numeric Unicode subscripts,
entered as `\0`, `\1`, `\2`, ..., for hypotheses, as we did in
this example.

이 예에서 우리가 한 것처럼 가정에 대해 `\0`, `\1`, `\2`, ... 로 입력되는 숫자 유니코드 첨자를 사용하는 것이 종종 유용하다는 점을 주목하세요.

## 3.3. Propositional Logic

Lean defines all the standard logical connectives and notation. The propositional connectives come with the following notation:

Lean은 모든 표준 논리 연결자와 표기법을 정의합니다. 명제 연결자들은 다음의 표기법과 함께 나옵니다:

They all take values in `Prop`.

이들은 모두 `Prop`의 값을 가집니다.

```
variable (p q : Prop)
#check p → q → p ∧ q
```

```
p → q → p ∧ q : Prop
```

```
#check ¬p → p ↔ False
```

```
¬p → p ↔ False : Prop
```

```
#check p ∨ q → q ∨ p
```

```
p ∨ q → q ∨ p : Prop
```

The order of operations is as follows: unary negation `¬` binds most
strongly, then `∧`, then `∨`, then `→`, and finally `↔`. For
example, `a ∧ b → c ∨ d ∧ e` means `(a ∧ b) → (c ∨ (d ∧ e))`.
Remember that `→` associates to the right (nothing changes
now that the arguments are elements of `Prop`, instead of some other
`Type`), as do the other binary connectives. So if we have
`p q r : Prop`, the expression `p → q → r` reads “if `p`, then if `q`,
then `r`.” This is just the “curried” form of `p ∧ q → r`.

연산 순서는 다음과 같습니다. 단항 부정 `¬`이 가장 강하게 결합하고, 그 다음 `∧`, 그 다음 `∨`, 그 다음 `→`, 그리고 마지막으로 `↔`입니다. 예를 들어, `a ∧ b → c ∨ d ∧ e`는 `(a ∧ b) → (c ∨ (d ∧ e))`를 의미합니다. `→`은 오른쪽으로 결합한다는 것을 기억하세요 (인자가 다른 `Type` 대신 `Prop`의 원소라는 사실이 바뀌지 않습니다), 다른 이항 연결자들도 마찬가지입니다. 따라서 `p q r : Prop`을 가지면, 표현식 `p → q → r`은 “만약 `p`, 그러면 만약 `q`, 그러면 `r`”로 읽습니다. 이는 `p ∧ q → r`의 “curried” 형식일 뿐입니다.

In the last chapter we observed that lambda abstraction can be viewed
as an “introduction rule” for `→`. In the current setting, it shows
how to “introduce” or establish an implication. Application can be
viewed as an “elimination rule,” showing how to “eliminate” or use an
implication in a proof. The other propositional connectives are
defined in Lean's library, and are automatically imported. Each connective
comes with its canonical introduction and elimination rules.

이전 장에서 우리는 람다 추상화를 `→`의 “도입 규칙”으로 볼 수 있음을 관찰했습니다. 현재 설정에서, 이는 함축을 “도입하거나” 확립하는 방법을 보여줍니다. 적용은 “제거 규칙”으로 볼 수 있으며, 증명에서 함축을 “제거하거나” 사용하는 방법을 보여줍니다. 다른 명제 연결자들은 Lean의 라이브러리에서 정의되며, 자동으로 가져옵니다. 각 연결자는 그 정규적인 도입 및 제거 규칙과 함께 옵니다.

### 3.3.1. Conjunction

The expression `And.intro h1 h2` builds a proof of `p ∧ q` using
proofs `h1 : p` and `h2 : q`. It is common to describe
`And.intro` as the *and-introduction* rule. In the next example we
use `And.intro` to create a proof of `p → q → p ∧ q`.

표현식 `And.intro h1 h2`는 증명 `h1 : p`와 `h2 : q`를 사용하여 `p ∧ q`의 증명을 만듭니다. `And.intro`을 *and-도입-규칙*으로 설명하는 것이 일반적입니다. 다음 예에서 우리는 `And.intro`을 사용하여 `p → q → p ∧ q`의 증명을 만듭니다.

```
variable (p q : Prop)
example (hp : p) (hq : q) : p ∧ q := And.intro hp hq
#check fun (hp : p) (hq : q) => And.intro hp hq
```

```
fun hp hq => ⟨hp, hq⟩ : p → q → p ∧ q
```

The `example` command states a theorem without naming it or storing
it in the permanent context. Essentially, it just checks that the
given term has the indicated type. It is convenient for illustration,
and we will use it often.

`example` 명령은 정리를 명명하거나 영구 컨텍스트에 저장하지 않고 선언합니다. 본질적으로, 주어진 항이 표시된 타입을 가지는지만 확인합니다. 이는 설명에 편리하며, 우리는 자주 사용할 것입니다.

The expression `And.left h` creates a proof of `p` from a proof
`h : p ∧ q`. Similarly, `And.right h` is a proof of `q`. They
are commonly known as the left and right *and-elimination* rules.

표현식 `And.left h`는 증명 `h : p ∧ q`로부터 `p`의 증명을 만듭니다. 마찬가지로, `And.right h`는 `q`의 증명입니다. 이들은 일반적으로 왼쪽과 오른쪽 *and-제거-규칙*으로 알려져 있습니다.

```
variable (p q : Prop)
example (h : p ∧ q) : p := And.left h
example (h : p ∧ q) : q := And.right h
```

We can now prove `p ∧ q → q ∧ p` with the following proof term.

우리는 이제 다음 증명 항으로 `p ∧ q → q ∧ p`를 증명할 수 있습니다.

```
variable (p q : Prop)
example (h : p ∧ q) : q ∧ p :=
And.intro (And.right h) (And.left h)
```

Notice that and-introduction and and-elimination are similar to the
pairing and projection operations for the Cartesian product. The
difference is that given `hp : p` and `hq : q`, `And.intro hp hq` has type
`p ∧ q : Prop`, while given `a : α` and `b : β`, `Prod.mk a b` has type
`α × β : Type`. `Prod` cannot be used with `Prop`s, and `And` cannot be used with `Type`s.
The similarity between `∧` and `×` is another instance
of the [Curry-Howard isomorphism](#--tech-term-Curry-Howard-isomorphism), but in contrast to implication and
the function space constructor, `∧` and `×` are treated separately
in Lean. With the analogy, however, the proof we have just constructed
is similar to a function that swaps the elements of a pair.

and-도입과 and-제거는 데카르트 곱에 대한 페어링 및 투영 연산과 유사합니다. 차이점은 `hp : p`와 `hq : q`가 주어졌을 때, `And.intro hp hq`는 `p ∧ q : Prop` 타입을 가지는 반면, `a : α`와 `b : β`가 주어졌을 때, `Prod.mk a b`는 `α × β : Type` 타입을 가진다는 것입니다. `Prod`는 `Prop`과 함께 사용될 수 없고, `And`는 `Type`과 함께 사용될 수 없습니다. `∧`와 `×` 사이의 유사성은 [Curry-Howard isomorphism](#--tech-term-Curry-Howard-isomorphism)의 또 다른 인스턴스이지만, 함축 및 함수 공간 생성자와 달리, `∧`과 `×`는 Lean에서 별도로 취급됩니다. 그러나 유추로, 우리가 방금 구성한 증명은 쌍의 원소를 교환하는 함수와 유사합니다.

We will see in [Structures and Records](../09-structures-and-records/#structures-and-records) that certain
types in Lean are *structures*, which is to say, the type is defined
with a single canonical *constructor* which builds an element of the
type from a sequence of suitable arguments. For every `p q : Prop`,
`p ∧ q` is an example: the canonical way to construct an element is
to apply `And.intro` to suitable arguments `hp : p` and
`hq : q`. Lean allows us to use *anonymous constructor* notation
`⟨arg1, arg2, ...⟩` in situations like these, when the relevant type is an
inductive type and can be inferred from the context. In particular, we
can often write `⟨hp, hq⟩` instead of `And.intro hp hq`:

[Structures and Records](../09-structures-and-records/#structures-and-records)에서 Lean의 특정 타입들이 *structures*임을 알 수 있을 것입니다. 즉, 타입은 적절한 인자의 시퀀스로부터 타입의 원소를 만드는 단일 정규 *생성자*로 정의됩니다. 모든 `p q : Prop`에 대해, `p ∧ q`는 예입니다. 원소를 구성하는 정규적인 방법은 적절한 인자 `hp : p`와 `hq : q`에 `And.intro`를 적용하는 것입니다. Lean은 우리가 이러한 상황에서 *익명 생성자* 표기법 `⟨arg1, arg2, ...⟩`를 사용할 수 있도록 합니다. 관련 타입이 귀납적 타입이고 컨텍스트에서 추론될 수 있을 때. 특히, 우리는 종종 `And.intro hp hq` 대신 `⟨hp, hq⟩`을 작성할 수 있습니다:

```
variable (p q : Prop)
variable (hp : p) (hq : q)
#check (⟨hp, hq⟩ : p ∧ q)
```

```
⟨hp, hq⟩ : p ∧ q
```

These angle brackets are obtained by typing `\<` and `\>`, respectively.

이 꺾쇠 괄호는 각각 `\<`와 `\>`를 입력하여 얻을 수 있습니다.

Lean provides another useful syntactic gadget. Given an expression
`e` of an inductive type `Foo` (possibly applied to some
arguments), the notation `e.bar` is shorthand for `Foo.bar e`.
This provides a convenient way of accessing functions without opening
a namespace. For example, the following two expressions mean the same
thing:

Lean은 또 다른 유용한 신택스 가젯을 제공합니다. 귀납적 타입 `Foo`의 표현식 `e`(어쩌면 일부 인자와 함께 적용됨)가 주어졌을 때, 표기법 `e.bar`은 `Foo.bar e`의 약자입니다. 이는 네임스페이스를 열지 않고 함수에 접근하는 편리한 방법을 제공합니다. 예를 들어, 다음의 두 표현식은 같은 의미입니다:

```
variable (xs : List Nat)
#check List.length xs
```

```
xs.length : Nat
```

```
#check xs.length
```

```
xs.length : Nat
```

As a result, given `h : p ∧ q`, we can write `h.left` for
`And.left h` and `h.right` for `And.right h`. We can therefore
rewrite the sample proof above conveniently as follows:

결과적으로, `h : p ∧ q`가 주어졌을 때, 우리는 `And.left h`에 대해 `h.left`을 쓸 수 있고 `And.right h`에 대해 `h.right`를 쓸 수 있습니다. 따라서 위의 샘플 증명을 편리하게 다음과 같이 다시 쓸 수 있습니다:

```
variable (p q : Prop)
example (h : p ∧ q) : q ∧ p :=
⟨h.right, h.left⟩
```

There is a fine line between brevity and obfuscation, and omitting
information in this way can sometimes make a proof harder to read. But
for straightforward constructions like the one above, when the type of
`h` and the goal of the construction are salient, the notation is
clean and effective.

간결함과 모호함 사이에는 미묘한 선이 있으며, 이러한 방식으로 정보를 생략하면 증명을 더 어렵게 읽을 수 있습니다. 하지만 위와 같은 간단한 구성의 경우, `h`의 타입과 구성의 목표가 두드러질 때, 표기법은 깔끔하고 효과적입니다.

It is common to iterate constructions like “And.” Lean also allows you
to flatten nested constructors that associate to the right, so that
these two proofs are equivalent:

“And”와 같은 구성을 반복하는 것이 일반적입니다. Lean은 또한 오른쪽으로 결합하는 중첩된 생성자를 평탄화할 수 있으므로, 이 두 증명은 동등합니다:

```
variable (p q : Prop)
example (h : p ∧ q) : q ∧ p ∧ q :=
⟨h.right, ⟨h.left, h.right⟩⟩
example (h : p ∧ q) : q ∧ p ∧ q :=
⟨h.right, h.left, h.right⟩
```

This is often useful as well.

이것도 종종 유용합니다.

### 3.3.2. Disjunction

The expression `Or.intro_left q hp` creates a proof of `p ∨ q`
from a proof `hp : p`. Similarly, `Or.intro_right p hq` creates a
proof for `p ∨ q` using a proof `hq : q`. These are the left and
right *or-introduction* rules.

표현식 `Or.intro_left q hp`는 증명 `hp : p`로부터 `p ∨ q`의 증명을 만듭니다. 마찬가지로, `Or.intro_right p hq`는 증명 `hq : q`를 사용하여 `p ∨ q`의 증명을 만듭니다. 이들은 왼쪽과 오른쪽 *or-도입-규칙*입니다.

```
variable (p q : Prop)
example (hp : p) : p ∨ q := Or.intro_left q hp
example (hq : q) : p ∨ q := Or.intro_right p hq
```

The *or-elimination* rule is slightly more complicated. The idea is
that we can prove `r` from `p ∨ q`, by showing that `r` follows
from `p` and that `r` follows from `q`. In other words, it is a
proof by cases. In the expression `Or.elim hpq hpr hqr`, `Or.elim`
takes three arguments, `hpq : p ∨ q`, `hpr : p → r` and
`hqr : q → r`, and produces a proof of `r`. In the following example, we use
`Or.elim` to prove `p ∨ q → q ∨ p`.

*or-제거-규칙*은 약간 더 복잡합니다. 아이디어는 `r`이 `p`로부터 따라오고 `r`이 `q`로부터 따라온다는 것을 보임으로써 `p ∨ q`로부터 `r`을 증명할 수 있다는 것입니다. 즉, 경우별 증명입니다. 표현식 `Or.elim hpq hpr hqr`에서, `Or.elim`은 세 개의 인자 `hpq : p ∨ q`, `hpr : p → r`과 `hqr : q → r`을 취하고 `r`의 증명을 생성합니다. 다음 예에서, 우리는 `Or.elim`을 사용하여 `p ∨ q → q ∨ p`를 증명합니다.

```
variable (p q r : Prop)
example (h : p ∨ q) : q ∨ p :=
Or.elim h
(fun hp : p =>
show q ∨ p from Or.intro_right q hp)
(fun hq : q =>
show q ∨ p from Or.intro_left p hq)
```

In most cases, the first argument of `Or.intro_right` and
`Or.intro_left` can be inferred automatically by Lean. Lean
therefore provides `Or.inr` and `Or.inl` which can be viewed as
shorthand for `Or.intro_right _` and `Or.intro_left _`. Thus the
proof term above could be written more concisely:

대부분의 경우, `Or.intro_right`와 `Or.intro_left`의 첫 번째 인자는 Lean에 의해 자동으로 추론될 수 있습니다. Lean은 따라서 `Or.intro_right _`와 `Or.intro_left _`의 약자로 볼 수 있는 `Or.inr`과 `Or.inl`을 제공합니다. 따라서 위의 증명 항은 더 간결하게 작성될 수 있습니다:

```
variable (p q r : Prop)
example (h : p ∨ q) : q ∨ p :=
Or.elim h (fun hp => Or.inr hp) (fun hq => Or.inl hq)
```

Notice that there is enough information in the full expression for
Lean to infer the types of `hp` and `hq` as well. But using the
type annotations in the longer version makes the proof more readable,
and can help catch and debug errors.

전체 표현식에 `hp`과 `hq`의 타입을 추론하기 위한 충분한 정보가 있음을 주목하세요. 하지만 더 긴 버전에서 타입 주석을 사용하면 증명을 더 읽기 쉽게 만들 수 있고, 오류를 잡고 디버깅하는 데 도움이 될 수 있습니다.

Because `Or` has two constructors, we cannot use anonymous
constructor notation. But we can still write `h.elim` instead of
`Or.elim h`:

`Or`은 두 개의 생성자를 가지고 있으므로, 우리는 익명 생성자 표기법을 사용할 수 없습니다. 하지만 우리는 여전히 `Or.elim h` 대신 `h.elim`을 쓸 수 있습니다:

```
variable (p q r : Prop)
example (h : p ∨ q) : q ∨ p :=
h.elim (fun hp => Or.inr hp) (fun hq => Or.inl hq)
```

Once again, you should exercise judgment as to whether such
abbreviations enhance or diminish readability.

다시 한 번, 이러한 약어가 가독성을 향상시키는지 감소시키는지 판단해야 합니다.

### 3.3.3. Negation and Falsity

Negation, `¬p`, is actually defined to be `p → False`, so we
obtain `¬p` by deriving a contradiction from `p`. Similarly, the
expression `hnp hp` produces a proof of `False` from `hp : p`
and `hnp : ¬p`. The next example uses both these rules to produce a
proof of `(p → q) → ¬q → ¬p`. (The symbol `¬` is produced by
typing `\not` or `\neg`.)

부정 `¬p`는 실제로 `p → False`로 정의되므로, 우리는 `p`로부터 모순을 도출함으로써 `¬p`를 얻습니다. 마찬가지로, 표현식 `hnp hp`는 `hp : p`와 `hnp : ¬p`로부터 `False`의 증명을 생성합니다. 다음 예는 이 두 규칙을 모두 사용하여 `(p → q) → ¬q → ¬p`의 증명을 생성합니다. (기호 `¬`은 `\not` 또는 `\neg`를 입력하여 생성됩니다.)

```
variable (p q : Prop)
example (hpq : p → q) (hnq : ¬q) : ¬p :=
fun hp : p =>
show False from hnq (hpq hp)
```

The connective `False` has a single elimination rule,
`False.elim`, which expresses the fact that anything follows from a
contradiction. This rule is sometimes called *ex falso* (short for *ex
falso sequitur quodlibet*), or the *principle of explosion*.

연결자 `False`는 단일 제거 규칙 `False.elim`을 가지며, 이는 모순으로부터 무엇이든 따라온다는 사실을 표현합니다. 이 규칙은 때때로 *ex falso* (*ex falso sequitur quodlibet*의 약자) 또는 *폭발의 원칙*이라고 불립니다.

```
variable (p q : Prop)
example (hp : p) (hnp : ¬p) : q := False.elim (hnp hp)
```

The arbitrary fact, `q`, that follows from falsity is an implicit
argument in `False.elim` and is inferred automatically. This
pattern, deriving an arbitrary fact from contradictory hypotheses, is
quite common, and is represented by `absurd`.

거짓으로부터 따라오는 임의의 사실 `q`는 `False.elim`의 암묵적 인자이며 자동으로 추론됩니다. 모순적인 가정으로부터 임의의 사실을 도출하는 이 패턴은 매우 일반적이며, `absurd`로 표현됩니다.

```
variable (p q : Prop)
example (hp : p) (hnp : ¬p) : q := absurd hp hnp
```

Here, for example, is a proof of `¬p → q → (q → p) → r`:

여기, 예를 들어 `¬p → q → (q → p) → r`의 증명이 있습니다:

```
variable (p q r : Prop)
example (hnp : ¬p) (hq : q) (hqp : q → p) : r :=
absurd (hqp hq) hnp
```

Incidentally, just as `False` has only an elimination rule, `True`
has only an introduction rule, `True.intro : True`. In other words,
`True` is simply true, and has a canonical proof, `True.intro`.

그런데 `False`가 제거 규칙만 가지는 것처럼, `True`는 도입 규칙만 가지며, `True.intro : True`입니다. 즉, `True`는 단순히 참이며, 정규적인 증명 `True.intro`를 가집니다.

### 3.3.4. Logical Equivalence

The expression `Iff.intro h1 h2` produces a proof of `p ↔ q` from
`h1 : p → q` and `h2 : q → p`. The expression `Iff.mp h`
produces a proof of `p → q` from `h : p ↔ q`. Similarly,
`Iff.mpr h` produces a proof of `q → p` from `h : p ↔ q`. Here is a proof
of `p ∧ q ↔ q ∧ p`:

표현식 `Iff.intro h1 h2`는 `h1 : p → q`와 `h2 : q → p`로부터 `p ↔ q`의 증명을 생성합니다. 표현식 `Iff.mp h`는 `h : p ↔ q`로부터 `p → q`의 증명을 생성합니다. 마찬가지로, `Iff.mpr h`는 `h : p ↔ q`로부터 `q → p`의 증명을 생성합니다. 다음은 `p ∧ q ↔ q ∧ p`의 증명입니다:

```
variable (p q : Prop)
theorem and_swap : p ∧ q ↔ q ∧ p :=
Iff.intro
(fun h : p ∧ q =>
show q ∧ p from And.intro (And.right h) (And.left h))
(fun h : q ∧ p =>
show p ∧ q from And.intro (And.right h) (And.left h))
#check and_swap p q
```

```
and_swap p q : p ∧ q ↔ q ∧ p
```

```
variable (h : p ∧ q)
example : q ∧ p := Iff.mp (and_swap p q) h
```

We can use the anonymous constructor notation to construct a proof of
`p ↔ q` from proofs of the forward and backward directions, and we
can also use `.` notation with `mp` and `mpr`. The previous
examples can therefore be written concisely as follows:

우리는 익명 생성자 표기법을 사용하여 앞의 방향과 역의 방향의 증명으로부터 `p ↔ q`의 증명을 구성할 수 있으며, `mp`와 `mpr`과 함께 `.` 표기법을 사용할 수도 있습니다. 이전 예는 따라서 간결하게 다음과 같이 작성될 수 있습니다:

```
variable (p q : Prop)
theorem and_swap : p ∧ q ↔ q ∧ p :=
⟨ fun h => ⟨h.right, h.left⟩, fun h => ⟨h.right, h.left⟩ ⟩
example (h : p ∧ q) : q ∧ p := (and_swap p q).mp h
```

## 3.4. Introducing Auxiliary Subgoals

This is a good place to introduce another device Lean offers to help
structure long proofs, namely, the `have` construct, which
introduces an auxiliary subgoal in a proof. Here is a small example,
adapted from the last section:

이것은 Lean이 제공하는 또 다른 장치를 소개하기에 좋은 장소입니다. 즉, 증명에서 보조 부분 목표를 도입하는 `have` 구성입니다. 다음은 이전 섹션으로부터 조정된 작은 예입니다:

```
variable (p q : Prop)
example (h : p ∧ q) : q ∧ p :=
have hp : p := h.left
have hq : q := h.right
show q ∧ p from And.intro hq hp
```

Internally, the expression `have h : p := s; t` produces the term
`(fun (h : p) => t) s`. In other words, `s` is a proof of `p`,
`t` is a proof of the desired conclusion assuming `h : p`, and the
two are combined by a lambda abstraction and application. This simple
device is extremely useful when it comes to structuring long proofs,
since we can use intermediate `have`'s as stepping stones leading to
the final goal.

내부적으로, 표현식 `have h : p := s; t`는 항 `(fun (h : p) => t) s`를 생성합니다. 즉, `s`는 `p`의 증명이고, `t`는 `h : p`를 가정하는 원하는 결론의 증명이며, 둘은 람다 추상화와 적용으로 결합됩니다. 이 간단한 장치는 긴 증명을 구조화할 때 매우 유용하며, 최종 목표로 이어지는 중간 `have`를 디딤돌로 사용할 수 있기 때문입니다.

Lean also supports a structured way of reasoning backwards from a
goal, which models the “suffices to show” construction in ordinary
mathematics. The next example simply permutes the last two lines in
the previous proof.

Lean은 또한 목표로부터 역으로 추론하는 구조화된 방법을 지원하며, 이는 일반 수학에서 “충분히 보이다” 구성을 모델링합니다. 다음 예는 단순히 이전 증명에서 마지막 두 줄을 바꿉니다.

```
variable (p q : Prop)
example (h : p ∧ q) : q ∧ p :=
have hp : p := h.left
suffices hq : q from And.intro hq hp
show q from And.right h
```

Writing `suffices hq : q` leaves us with two goals. First, we have
to show that it indeed suffices to show `q`, by proving the original
goal of `q ∧ p` with the additional hypothesis `hq : q`. Finally,
we have to show `q`.

`suffices hq : q`를 작성하면 우리는 두 개의 목표를 남깁니다. 먼저, 추가 가정 `hq : q`로 원래의 목표 `q ∧ p`를 증명함으로써 `q`를 보이는 것이 실제로 충분함을 보여야 합니다. 마지막으로, `q`를 보여야 합니다.

## 3.5. Classical Logic

The introduction and elimination rules we have seen so far are all
constructive, which is to say, they reflect a computational
understanding of the logical connectives based on the
[propositions-as-types](#--tech-term-propositions-as-types) correspondence. Ordinary classical logic adds to
this the law of the excluded middle, `p ∨ ¬p`. To use this
principle, you have to open the classical namespace.

지금까지 본 도입 및 제거 규칙은 모두 구성적이며, 즉 [명제-타입-대응](#--tech-term-propositions-as-types)에 기반한 논리 연결자의 계산적 이해를 반영합니다. 일반적인 고전 논리는 여기에 제외의 법칙 `p ∨ ¬p`를 추가합니다. 이 원칙을 사용하려면, 고전 네임스페이스를 열어야 합니다.

```
open Classical
variable (p : Prop)
#check em p
```

```
em p : p ∨ ¬p
```

Intuitively, the constructive “Or” is very strong: asserting `p ∨ q`
amounts to knowing which is the case. If `RH` represents the Riemann
hypothesis, a classical mathematician is willing to assert
`RH ∨ ¬RH`, even though we cannot yet assert either disjunct.

직관적으로, 구성적인 “Or”은 매우 강합니다. `p ∨ q`를 주장하는 것은 어느 것이 그 경우인지를 아는 것에 해당합니다. `RH`가 리만 가설을 나타내면, 고전 수학자는 아직 어느 한 선택지도 주장할 수 없지만 `RH ∨ ¬RH`를 주장할 의향이 있습니다.

One consequence of the law of the excluded middle is the principle of
double-negation elimination:

제외의 법칙의 하나의 결과는 이중-부정-제거의 원칙입니다:

```
open Classical
theorem dne {p : Prop} (h : ¬¬p) : p :=
Or.elim (em p)
(fun hp : p => hp)
(fun hnp : ¬p => absurd hnp h)
```

Double-negation elimination allows one to prove any proposition,
`p`, by assuming `¬p` and deriving `False`, because that amounts
to proving `¬¬p`. In other words, double-negation elimination allows
one to carry out a proof by contradiction, something which is not
generally possible in constructive logic. As an exercise, you might
try proving the converse, that is, showing that `em` can be proved
from `dne`.

이중-부정-제거는 `¬p`를 가정하고 `False`를 도출함으로써 임의의 명제 `p`를 증명할 수 있게 하며, 그 이유는 `¬¬p`를 증명하는 것과 같기 때문입니다. 즉, 이중-부정-제거는 구성적 논리에서 일반적으로 불가능한 모순으로 증명을 수행할 수 있게 합니다. 연습으로, `dne`로부터 `em`을 증명할 수 있음을 보이는 역을 증명해 보시기 바랍니다.

The classical axioms also give you access to additional patterns of
proof that can be justified by appeal to `em`. For example, one can
carry out a proof by cases:

고전 공리도 `em`에 호소함으로써 정당화될 수 있는 증명의 추가 패턴에 접근할 수 있게 합니다. 예를 들어, 경우별 증명을 수행할 수 있습니다:

```
open Classical
variable (p : Prop)
example (h : ¬¬p) : p :=
byCases
(fun h1 : p => h1)
(fun h1 : ¬p => absurd h1 h)
```

Or you can carry out a proof by contradiction:

또는 모순으로 증명을 수행할 수 있습니다:

```
open Classical
variable (p : Prop)
example (h : ¬¬p) : p :=
byContradiction
(fun h1 : ¬p =>
show False from h h1)
```

If you are not used to thinking constructively, it may take some time
for you to get a sense of where classical reasoning is used. It is
needed in the following example because, from a constructive
standpoint, knowing that `p` and `q` are not both true does not
necessarily tell you which one is false:

구성적으로 생각하는 데 익숙하지 않다면, 고전 추론이 어디에 사용되는지에 대한 감각을 얻는 데 시간이 걸릴 수 있습니다. 다음 예에서 필요하며, 구성적 관점에서 `p`와 `q`가 모두 참이 아니라는 것을 아는 것이 반드시 어느 것이 거짓인지를 알려주지는 않기 때문입니다:

```
example (h : ¬(p ∧ q)) : ¬p ∨ ¬q :=
Or.elim (em p)
(fun hp : p =>
Or.inr
(show ¬q from
fun hq : q =>
h ⟨hp, hq⟩))
(fun hp : ¬p =>
Or.inl hp)
```

We will see later that there *are* situations in constructive logic
where principles like excluded middle and double-negation elimination
are permissible, and Lean supports the use of classical reasoning in
such contexts without relying on excluded middle.

우리는 나중에 제외의 법칙과 이중-부정-제거와 같은 원칙이 허락되는 구성적 논리의 상황이 *있다*는 것을 알 것이며, Lean은 제외의 법칙에 의존하지 않고 이러한 맥락에서 고전 추론의 사용을 지원합니다.

The full list of axioms that are used in Lean to support classical
reasoning are discussed in [Axioms and Computation](../12-axioms-and-computation/#axioms-and-computation).

고전 추론을 지원하기 위해 Lean에서 사용되는 공리의 전체 목록은 [공리 및 계산](../12-axioms-and-computation/#axioms-and-computation)에서 논의됩니다.

## 3.6. Examples of Propositional Validities

Lean's standard library contains proofs of many valid statements of
propositional logic, all of which you are free to use in proofs of
your own. The following list includes a number of common identities.

Lean의 표준 라이브러리는 명제 논리의 많은 유효한 명제들의 증명을 포함하며, 이들은 모두 자신의 증명에서 자유롭게 사용할 수 있습니다. 다음 목록은 많은 공통 항등식들을 포함합니다.

Commutativity:

교환법칙 (Commutativity):

1. `p ∧ q ↔ q ∧ p`
2. `p ∨ q ↔ q ∨ p`

`p ∨ q ↔ q ∨ p`

Associativity:

결합법칙 (Associativity):

3. `(p ∧ q) ∧ r ↔ p ∧ (q ∧ r)`
4. `(p ∨ q) ∨ r ↔ p ∨ (q ∨ r)`

`(p ∨ q) ∨ r ↔ p ∨ (q ∨ r)`

Distributivity:

분배법칙 (Distributivity):

5. `p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r)`
6. `p ∨ (q ∧ r) ↔ (p ∨ q) ∧ (p ∨ r)`

`p ∨ (q ∧ r) ↔ (p ∨ q) ∧ (p ∨ r)`

Other properties:

기타 속성 (Other properties):

7. `(p → (q → r)) ↔ (p ∧ q → r)`
8. `((p ∨ q) → r) ↔ (p → r) ∧ (q → r)`
9. `¬(p ∨ q) ↔ ¬p ∧ ¬q`
10. `¬p ∨ ¬q → ¬(p ∧ q)`
11. `¬(p ∧ ¬p)`
12. `p ∧ ¬q → ¬(p → q)`
13. `¬p → (p → q)`
14. `(¬p ∨ q) → (p → q)`
15. `p ∨ False ↔ p`
16. `p ∧ False ↔ False`
17. `¬(p ↔ ¬p)`
18. `(p → q) → (¬q → ¬p)`

`((p ∨ q) → r) ↔ (p → r) ∧ (q → r)`

`¬(p ∨ q) ↔ ¬p ∧ ¬q`

`¬p ∨ ¬q → ¬(p ∧ q)`

`¬(p ∧ ¬p)`

`p ∧ ¬q → ¬(p → q)`

`¬p → (p → q)`

`(¬p ∨ q) → (p → q)`

`p ∨ False ↔ p`

`p ∧ False ↔ False`

이들은 고전 추론이 필요합니다:

`sorry` 식별자는 마법처럼 무엇이든 증명을 생성하거나, 어떤 데이터 타입의 객체든 제공합니다. 물론, 이는 증명 방법으로는 건전하지 않습니다. 예를 들어, `False`를 증명하는 데 사용할 수 있습니다. Lean은 파일이 이에 의존하는 정리를 사용하거나 가져올 때 심한 경고를 생성합니다. 하지만 긴 증명을 점진적으로 만드는 데 매우 유용합니다. 증명을 하향식으로 작성하기 시작하고, `sorry`를 사용하여 부분 증명을 채웁니다. 모든 `sorry`와 함께 Lean이 항을 수용하는지 확인하세요. 그렇지 않으면 수정해야 할 오류가 있습니다. 그 다음 돌아가서 각 `sorry`를 실제 증명으로 대체하고, 더 이상 남아 있지 않을 때까지 반복합니다.

또 다른 유용한 트릭이 있습니다. `sorry`를 사용하는 대신, 밑줄 `_`을 자리 표시자로 사용할 수 있습니다. 이는 인자가 암묵적이며 자동으로 채워져야 함을 Lean에 알려주는 것을 상기하세요. Lean이 그렇게 하려고 시도했다가 실패하면, “자리 표시자를 합성하는 방법을 모릅니다”는 오류 메시지와 함께 반환되며, 기대하는 항의 타입 및 컨텍스트에서 사용 가능한 모든 객체와 가정이 뒤따릅니다. 즉, 각 미해결 자리 표시자에 대해, Lean은 그 지점에서 채워져야 할 부분 목표를 보고합니다. 그런 다음 이러한 자리 표시자를 점진적으로 채움으로써 증명을 구성할 수 있습니다.

참고로, 위의 목록에서 가져온 유효성의 두 샘플 증명이 있습니다.

다음 항등식들을 증명하세요. `sorry` 자리 표시자를 실제 증명으로 대체하여.

다음 항등식들을 증명하세요. `sorry` 자리 표시자를 실제 증명으로 대체하여. 이들은 고전 추론이 필요합니다.

`¬(p ↔ ¬p)` without using classical logic.

`(p → q) → (¬q → ¬p)`

These require classical reasoning:

`(p → r ∨ s) → ((p → r) ∨ (p → s))`

`¬(p ∧ q) → ¬p ∨ ¬q`

`¬(p → q) → p ∧ ¬q`

`(p → q) → (¬p ∨ q)`

`(¬q → ¬p) → (p → q)`

`p ∨ ¬p`

`(((p → q) → p) → p)`

The `sorry` identifier magically produces a proof of anything, or provides an object of any data type at all. Of course, it is unsound as a proof method—for example, you can use it to prove `False`—and Lean produces severe warnings when files use or import theorems which depend on it. But it is very useful for building long proofs incrementally. Start writing the proof from the top down, using `sorry` to fill in subproofs. Make sure Lean accepts the term with all the `sorry`'s; if not, there are errors that you need to correct. Then go back and replace each `sorry` with an actual proof, until no more remain.

Here is another useful trick. Instead of using `sorry`, you can use an underscore `_` as a placeholder. Recall this tells Lean that the argument is implicit, and should be filled in automatically. If Lean tries to do so and fails, it returns with an error message “don't know how to synthesize placeholder,” followed by the type of the term it is expecting, and all the objects and hypotheses available in the context. In other words, for each unresolved placeholder, Lean reports the subgoal that needs to be filled at that point. You can then construct a proof by incrementally filling in these placeholders.

For reference, here are two sample proofs of validities taken from the list above.

```
open Classical
-- distributivity
example (p q r : Prop) : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) :=
Iff.intro
(fun h : p ∧ (q ∨ r) =>
have hp : p := h.left
Or.elim (h.right)
(fun hq : q =>
show (p ∧ q) ∨ (p ∧ r) from Or.inl ⟨hp, hq⟩)
(fun hr : r =>
show (p ∧ q) ∨ (p ∧ r) from Or.inr ⟨hp, hr⟩))
(fun h : (p ∧ q) ∨ (p ∧ r) =>
Or.elim h
(fun hpq : p ∧ q =>
have hp : p := hpq.left
have hq : q := hpq.right
show p ∧ (q ∨ r) from ⟨hp, Or.inl hq⟩)
(fun hpr : p ∧ r =>
have hp : p := hpr.left
have hr : r := hpr.right
show p ∧ (q ∨ r) from ⟨hp, Or.inr hr⟩))
-- an example that requires classical reasoning
example (p q : Prop) : ¬(p ∧ ¬q) → (p → q) :=
fun h : ¬(p ∧ ¬q) =>
fun hp : p =>
show q from
Or.elim (em q)
(fun hq : q => hq)
(fun hnq : ¬q => absurd (And.intro hp hnq) h)
```

## 3.7. Exercises

Prove the following identities, replacing the `sorry` placeholders with actual proofs.

```
variable (p q r : Prop)
-- commutativity of ∧ and ∨
example : p ∧ q ↔ q ∧ p := sorry
example : p ∨ q ↔ q ∨ p := sorry
-- associativity of ∧ and ∨
example : (p ∧ q) ∧ r ↔ p ∧ (q ∧ r) := sorry
example : (p ∨ q) ∨ r ↔ p ∨ (q ∨ r) := sorry
-- distributivity
example : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) := sorry
example : p ∨ (q ∧ r) ↔ (p ∨ q) ∧ (p ∨ r) := sorry
-- other properties
example : (p → (q → r)) ↔ (p ∧ q → r) := sorry
example : ((p ∨ q) → r) ↔ (p → r) ∧ (q → r) := sorry
example : ¬(p ∨ q) ↔ ¬p ∧ ¬q := sorry
example : ¬p ∨ ¬q → ¬(p ∧ q) := sorry
example : ¬(p ∧ ¬p) := sorry
example : p ∧ ¬q → ¬(p → q) := sorry
example : ¬p → (p → q) := sorry
example : (¬p ∨ q) → (p → q) := sorry
example : p ∨ False ↔ p := sorry
example : p ∧ False ↔ False := sorry
example : (p → q) → (¬q → ¬p) := sorry
```

Prove the following identities, replacing the `sorry` placeholders with actual proofs. These require classical reasoning.

```
open Classical
variable (p q r : Prop)
example : (p → q ∨ r) → ((p → q) ∨ (p → r)) := sorry
example : ¬(p ∧ q) → ¬p ∨ ¬q := sorry
example : ¬(p → q) → p ∧ ¬q := sorry
example : (p → q) → (¬p ∨ q) := sorry
example : (¬q → ¬p) → (p → q) := sorry
example : p ∨ ¬p := sorry
example : (((p → q) → p) → p) := sorry
```

Prove `¬(p ↔ ¬p)` without using classical logic.

고전 논리를 사용하지 않고 `¬(p ↔ ¬p)`를 증명하세요.
