---
title: "4. 정량자와 동등성"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "theorem-proving", "type-theory"]
categories: ["programming"]
description: "전칭·존재 정량자, 동등성, calc를 이용한 계산적 증명 스타일을 다룹니다."
---

The last chapter introduced you to methods that construct proofs of
statements involving the propositional connectives. In this chapter,
we extend the repertoire of logical constructions to include the
universal and existential quantifiers, and the equality relation.

지난 장에서는 명제적 연결사를 포함하는 명제의 증명을 구성하는 방법들을 소개했습니다. 이 장에서는 논리적 구성의 범주를 확장하여 전칭 양화사와 존재 양화사, 그리고 동치 관계를 포함합니다.

## 4.1. The Universal Quantifier

Notice that if `α` is any type, we can represent a unary predicate
`p` on `α` as an object of type `α → Prop`. In that case, given
`x : α`, `p x` denotes the assertion that `p` holds of
`x`. Similarly, an object `r : α → α → Prop` denotes a binary
relation on `α`: given `x y : α`, `r x y` denotes the assertion
that `x` is related to `y`.

`α`가 임의의 타입이라면, `α` 위의 단항 술어 `p`를 `α → Prop` 타입의 객체로 나타낼 수 있습니다. 이 경우 `x : α`가 주어지면 `p x`는 `p`가 `x`에 대해 성립한다는 주장을 나타냅니다. 유사하게, 객체 `r : α → α → Prop`은 `α` 위의 이항 관계를 나타냅니다: `x y : α`가 주어지면 `r x y`는 `x`가 `y`와 관련되어 있다는 주장을 나타냅니다.

The universal quantifier, `∀ x : α, p x` is supposed to denote the
assertion that “for every `x : α`, `p x`” holds. As with the
propositional connectives, in systems of natural deduction, “forall”
is governed by an introduction and elimination rule. Informally, the
introduction rule states:

전칭 양화사 `∀ x : α, p x`는 “모든 `x : α`에 대해 `p x`가 성립한다”는 주장을 나타냅니다. 명제적 연결사와 마찬가지로, 자연 연역 체계에서 “forall”은 도입 규칙과 소거 규칙에 의해 지배됩니다. 비공식적으로, 도입 규칙은 다음과 같이 명시됩니다:

Given a proof of `p x`, in a context where `x : α` is arbitrary, we obtain a proof `∀ x : α, p x`.

> 임의의 `x : α`인 문맥에서 `p x`의 증명이 주어지면, 우리는 `∀ x : α, p x`의 증명을 얻습니다.

The elimination rule states:

제거 규칙은 다음과 같이 명시합니다:

제거 규칙은 다음과 같이 명시합니다:

Given a proof `∀ x : α, p x` and any term `t : α`, we obtain a proof of `p t`.

> `∀ x : α, p x`의 증명과 임의의 항 `t : α`가 주어지면, 우리는 `p t`의 증명을 얻습니다.

As was the case for implication, the propositions-as-types
interpretation now comes into play. Remember the introduction and
elimination rules for dependent arrow types:

함의의 경우와 마찬가지로, 명제-유형-으로 해석이 이제 작용합니다. 종속 화살표 타입에 대한 도입 및 소거 규칙을 기억하세요:

Given a term `t` of type `β x`, in a context where `x : α` is arbitrary, we have `(fun x : α => t) : (x : α) → β x`.

> 임의의 `x : α`인 문맥에서 타입이 `β x`인 항 `t`가 주어지면, 우리는 `(fun x : α => t) : (x : α) → β x`를 가집니다.

The elimination rule states:

제거 규칙은 다음과 같이 명시합니다:

제거 규칙은 다음과 같이 명시합니다:

Given a term `s : (x : α) → β x` and any term `t : α`, we have `s t : β t`.

> 항 `s : (x : α) → β x`와 임의의 항 `t : α`가 주어지면, 우리는 `s t : β t`를 가집니다.

In the case where `p x` has type `Prop`, if we replace
`(x : α) → β x` with `∀ x : α, p x`, we can read these as the correct rules
for building proofs involving the universal quantifier.

`p x`가 `Prop` 타입을 갖는 경우, `(x : α) → β x`를 `∀ x : α, p x`로 대체하면, 이를 전칭 양화사를 포함하는 증명을 구축하기 위한 올바른 규칙으로 읽을 수 있습니다.

The Calculus of Constructions therefore identifies dependent arrow
types with forall-expressions in this way. If `p` is any expression,
`∀ x : α, p` is nothing more than alternative notation for
`(x : α) → p`, with the idea that the former is more natural than the latter
in cases where `p` is a proposition. Typically, the expression `p`
will depend on `x : α`. Recall that, in the case of ordinary
function spaces, we could interpret `α → β` as the special case of
`(x : α) → β` in which `β` does not depend on `x`. Similarly, we
can think of an implication `p → q` between propositions as the
special case of `∀ x : p, q` in which the expression `q` does not
depend on `x`.

따라서 구성의 미적분은 이러한 방식으로 종속 화살표 타입을 forall 표현식과 동일시합니다. `p`가 임의의 표현식이라면, `∀ x : α, p`는 `(x : α) → p`의 단순한 대체 표기법일 뿐이며, `p`가 명제인 경우 전자가 후자보다 더 자연스럽다는 생각입니다. 일반적으로 표현식 `p`는 `x : α`에 따라 달라집니다. 일반 함수 공간의 경우 `α → β`를 `β`가 `x`에 의존하지 않는 `(x : α) → β`의 특수한 경우로 해석할 수 있음을 상기하세요. 유사하게, 명제들 사이의 함의 `p → q`를 표현식 `q`가 `x`에 의존하지 않는 `∀ x : p, q`의 특수한 경우로 생각할 수 있습니다.

Here is an example of how the [propositions-as-types](../03-propositions-and-proofs/#--tech-term-propositions-as-types) correspondence gets put into practice.

다음은 [명제-타입-대응](../03-propositions-and-proofs/#--tech-term-propositions-as-types)이 어떻게 실제로 적용되는지에 대한 예시입니다.

```
example (α : Type) (p q : α → Prop) :
(∀ x : α, p x ∧ q x) → ∀ y : α, p y :=
fun h : ∀ x : α, p x ∧ q x =>
fun y : α =>
show p y from (h y).left
```

As a notational convention, we give the universal quantifier the
widest scope possible, so parentheses are needed to limit the
quantifier over `x` to the hypothesis in the example above. The
canonical way to prove `∀ y : α, p y` is to take an arbitrary `y`,
and prove `p y`. This is the introduction rule. Now, given that
`h` has type `∀ x : α, p x ∧ q x`, the expression `h y` has type
`p y` `∧` `q y`. This is the elimination rule. Taking the left conjunct
gives the desired conclusion, `p y`.

표기법 관례로, 우리는 전칭 양화사에 가능한 가장 넓은 범위를 부여하므로, 위의 예시에서 `x` 위의 양화사를 가정에만 제한하기 위해 괄호가 필요합니다. `∀ y : α, p y`를 증명하는 표준적인 방법은 임의의 `y`를 취하고 `p y`를 증명하는 것입니다. 이것이 도입 규칙입니다. 이제 `h`가 `∀ x : α, p x ∧ q x` 타입을 가진다고 할 때, 표현식 `h y`는 `p y ∧ q y` 타입을 갖습니다. 이것이 소거 규칙입니다. 왼쪽 결합을 취하면 원하는 결론인 `p y`를 얻습니다.

Remember that expressions which differ up to renaming of bound
variables are considered to be equivalent. So, for example, we could
have used the same variable, `x`, in both the hypothesis and
conclusion, and instantiated it by a different variable, `z`, in the
proof:

바인딩된 변수의 이름을 바꾸는 것까지 다른 표현식은 동등한 것으로 간주됨을 기억하세요. 예를 들어, 가정과 결론 모두에서 동일한 변수 `x`를 사용할 수 있었고, 증명에서 다른 변수 `z`로 인스턴스화할 수 있습니다:

```
example (α : Type) (p q : α → Prop) :
(∀ x : α, p x ∧ q x) → ∀ x : α, p x :=
fun h : ∀ x : α, p x ∧ q x =>
fun z : α =>
show p z from And.left (h z)
```

As another example, here is how we can express the fact that a relation, `r`, is transitive:

또 다른 예로, 관계 `r`이 추이적이라는 사실을 어떻게 표현할 수 있는지 보여줍니다:

```
variable (α : Type) (r : α → α → Prop)
variable (trans_r : ∀ x y z, r x y → r y z → r x z)
variable (a b c : α)
variable (hab : r a b) (hbc : r b c)
#check trans_r
```

```
trans_r : ∀ (x y z : α), r x y → r y z → r x z
```

```
#check trans_r a b c
```

```
trans_r a b c : r a b → r b c → r a c
```

```
#check trans_r a b c hab
```

```
trans_r a b c hab : r b c → r a c
```

```
#check trans_r a b c hab hbc
```

```
trans_r a b c hab hbc : r a c
```

Think about what is going on here. When we instantiate `trans_r` at
the values `a b c`, we end up with a proof of `r a b` `→` `r b c` `→` `r a c`.
Applying this to the “hypothesis” `hab : r a b`, we get a proof
of the implication `r b c` `→` `r a c`. Finally, applying it to the
hypothesis `hbc` yields a proof of the conclusion `r a c`.

여기서 무슨 일이 일어나고 있는지 생각해보세요. 우리가 값 `a b c`에서 `trans_r`을 인스턴스화하면, 결국 `r a b → r b c → r a c`의 증명을 얻게 됩니다. 이를 “가정” `hab : r a b`에 적용하면, 함의 `r b c → r a c`의 증명을 얻습니다. 마지막으로, 이를 가정 `hbc`에 적용하면 결론 `r a c`의 증명을 얻습니다.

In situations like this, it can be tedious to supply the arguments
`a b c`, when they can be inferred from `hab hbc`. For that reason, it
is common to make these arguments implicit:

이러한 상황에서 `hab hbc`에서 추론할 수 있을 때 인수 `a b c`를 제공하는 것은 지루할 수 있습니다. 그 이유로 이러한 인수를 암묵적으로 만드는 것이 일반적입니다:

```
variable (α : Type) (r : α → α → Prop)
variable (trans_r : ∀ {x y z}, r x y → r y z → r x z)
variable (a b c : α)
variable (hab : r a b) (hbc : r b c)
#check trans_r
```

```
trans_r : r ?m.4 ?m.5 → r ?m.5 ?m.6 → r ?m.4 ?m.6
```

```
#check trans_r hab
```

```
trans_r hab : r b ?m.6 → r a ?m.6
```

```
#check trans_r hab hbc
```

```
trans_r hab hbc : r a c
```

The advantage is that we can simply write `trans_r hab hbc` as a
proof of `r a c`. A disadvantage is that Lean does not have enough
information to infer the types of the arguments in the expressions
`trans_r` and `trans_r hab`. The output of the first `#check`
command is `r ?m.1 ?m.2 → r ?m.2 ?m.3 → r ?m.1 ?m.3`, indicating
that the implicit arguments are unspecified in this case.

장점은 `trans_r hab hbc`를 `r a c`의 증명으로 간단히 쓸 수 있다는 것입니다. 단점은 Lean이 표현식 `trans_r`과 `trans_r hab`의 인수 타입을 추론할 충분한 정보를 갖지 못한다는 것입니다. 첫 번째 `#check` 명령의 출력은 `r ?m.1 ?m.2 → r ?m.2 ?m.3 → r ?m.1 ?m.3`이며, 이 경우 암묵적 인수가 지정되지 않았음을 나타냅니다.

Here is an example of how we can carry out elementary reasoning with an equivalence relation:

동치 관계로 기본적인 추론을 수행하는 방법의 예는 다음과 같습니다:

```
variable (α : Type) (r : α → α → Prop)
variable (refl_r : ∀ x, r x x)
variable (symm_r : ∀ {x y}, r x y → r y x)
variable (trans_r : ∀ {x y z}, r x y → r y z → r x z)
example (a b c d : α) (hab : r a b) (hcb : r c b) (hcd : r c d) : r a d :=
trans_r (trans_r hab (symm_r hcb)) hcd
```

To get used to using universal quantifiers, you should try some of the
exercises at the end of this section.

전칭 양화사를 사용하는 데 익숙해지려면 이 섹션의 끝에 있는 연습문제들을 시도해야 합니다.

It is the typing rule for dependent arrow types, and the universal
quantifier in particular, that distinguishes `Prop` from other
types. Suppose we have `α : Sort i` and `β : Sort j`, where the
expression `β` may depend on a variable `x : α`. Then
`(x : α) → β` is an element of `Sort (imax i j)`, where `imax i j` is the
maximum of `i` and `j` if `j` is not `0`, and `0` otherwise.

종속 화살표 타입, 특히 전칭 양화사의 타입 지정 규칙이 `Prop`을 다른 타입들과 구별합니다. `α : Sort i`와 `β : Sort j`를 가지고 있다고 가정하면, 표현식 `β`는 변수 `x : α`에 따라 달라질 수 있습니다. 그러면 `(x : α) → β`는 `Sort (imax i j)`의 원소입니다. 여기서 `imax i j`는 `j`가 `0`이 아니면 `i`와 `j`의 최댓값이고, 그렇지 않으면 `0`입니다.

The idea is as follows. If `j` is not `0`, then `(x : α) → β` is
an element of `Sort (max i j)`. In other words, the type of
dependent functions from `α` to `β` “lives” in the universe whose
index is the maximum of `i` and `j`. Suppose, however, that `β`
is of `Sort 0`, that is, an element of `Prop`. In that case,
`(x : α) → β` is an element of `Sort 0` as well, no matter which
type universe `α` lives in. In other words, if `β` is a
proposition depending on `α`, then `∀ x : α, β` is again a
proposition. This reflects the interpretation of `Prop` as the type
of propositions rather than data, and it is what makes `Prop`
*impredicative*.

아이디어는 다음과 같습니다. `j`가 `0`이 아니면 `(x : α) → β`는 `Sort (max i j)`의 원소입니다. 즉, `α`에서 `β`로의 종속 함수의 타입은 인덱스가 `i`와 `j`의 최댓값인 우주에 “살고” 있습니다. 그러나 `β`가 `Sort 0`의 것이라고 가정하면, 즉 `Prop`의 원소입니다. 이 경우, `α`가 살고 있는 타입 우주에 관계없이 `(x : α) → β`도 `Sort 0`의 원소입니다. 즉, `β`가 `α`에 따라 달라지는 명제라면, `∀ x : α, β`도 명제입니다. 이는 `Prop`을 데이터보다는 명제의 타입으로 해석하는 것을 반영하며, 이것이 `Prop`을 *함축적*으로 만드는 것입니다.

The term “predicative” stems from foundational developments around the
turn of the twentieth century, when logicians such as Poincaré and
Russell blamed set-theoretic paradoxes on the “vicious circles” that
arise when we define a property by quantifying over a collection that
includes the very property being defined. Notice that if `α` is any
type, we can form the type `α → Prop` of all predicates on `α`
(the “power type of `α`”). The impredicativity of `Prop` means that we
can form propositions that quantify over `α → Prop`. In particular,
we can define predicates on `α` by quantifying over all predicates
on `α`, which is exactly the type of circularity that was once
considered problematic.

“술어적”이라는 용어는 20세기 초반의 기초 발전에서 비롯되었으며, Poincaré와 Russell과 같은 논리학자들은 집합론적 역설을 정의되는 매우 성질을 포함하는 컬렉션에 대해 양화하여 성질을 정의할 때 발생하는 “악순환”에 탓했습니다. `α`가 임의의 타입이라면 `α → Prop`(“`α`의 거듭제곱 타입”)의 `α` 위의 모든 술어의 타입을 형성할 수 있음을 주목하세요. `Prop`의 함축성은 `α → Prop`에 대해 양화하는 명제들을 형성할 수 있다는 것을 의미합니다. 특히, `α` 위의 모든 술어에 대해 양화하여 `α` 위의 술어를 정의할 수 있으며, 이는 한때 문제로 간주되었던 정확한 순환의 유형입니다.

## 4.2. Equality

Let us now turn to one of the most fundamental relations defined in
Lean's library, namely, the equality relation. In the chapter on [inductive types](../07-inductive-types/#inductive-types),
we will explain *how* equality is defined from the primitives of Lean's logical framework.
In the meanwhile, here we explain how to use it.

이제 Lean의 라이브러리에 정의된 가장 기본적인 관계 중 하나인 동치 관계로 눈을 돌립시다. [귀납 타입](../07-inductive-types/#inductive-types) 장에서 Lean의 논리 틀의 원시에서 동치가 어떻게 정의되는지 설명할 것입니다. 그 사이에 여기서 사용 방법을 설명합니다.

Of course, a fundamental property of equality is that it is an equivalence relation:

물론 동치의 기본 성질은 동치 관계라는 것입니다:

```
#check Eq.refl
```

```
Eq.refl.{u_1} {α : Sort u_1} (a : α) : a = a
```

```
#check Eq.symm
```

```
Eq.symm.{u} {α : Sort u} {a b : α} (h : a = b) : b = a
```

```
#check Eq.trans
```

```
Eq.trans.{u} {α : Sort u} {a b c : α} (h₁ : a = b) (h₂ : b = c) : a = c
```

We can make the output easier to read by telling Lean not to insert
the implicit arguments (which are displayed here as metavariables).

우리는 Lean에 암묵적 인수를 삽입하지 않도록 말함으로써 출력을 더 읽기 쉽게 만들 수 있습니다(여기서는 메타변수로 표시됩니다).

```
universe u
#check @Eq.refl.{u}
```

```
@Eq.refl : ∀ {α : Sort u} (a : α), a = a
```

```
#check @Eq.symm.{u}
```

```
@Eq.symm : ∀ {α : Sort u} {a b : α}, a = b → b = a
```

```
#check @Eq.trans.{u}
```

```
@Eq.trans : ∀ {α : Sort u} {a b c : α}, a = b → b = c → a = c
```

The inscription `.{u}` tells Lean to instantiate the constants at the universe `u`.

표기법 `.{u}`는 우주 `u`에서 상수를 인스턴스화하도록 Lean에 지시합니다.

Thus, for example, we can specialize the example from the previous section to the equality relation:

예를 들어, 우리는 이전 섹션의 예를 동치 관계로 특화할 수 있습니다:

```
variable (α : Type) (a b c d : α)
variable (hab : a = b) (hcb : c = b) (hcd : c = d)
example : a = d :=
Eq.trans (Eq.trans hab (Eq.symm hcb)) hcd
```

We can also use the projection notation:

우리는 또한 투영 표기법을 사용할 수 있습니다:

```
example : a = d := (hab.trans hcb.symm).trans hcd
```

Reflexivity is more powerful than it looks. Recall that terms in the
Calculus of Constructions have a computational interpretation, and
that the logical framework treats terms with a common reduct as the
same. As a result, some nontrivial identities can be proved by
reflexivity:

반사성은 보이는 것보다 더 강합니다. 구성의 미적분에서 항들은 계산 해석을 가지고 있으며, 논리 틀은 공통 축약을 가진 항들을 동일한 것으로 취급합니다. 결과적으로, 일부 자명하지 않은 항등식은 반사성으로 증명될 수 있습니다:

```
variable (α β : Type)
example (f : α → β) (a : α) : (fun x => f x) a = f a := Eq.refl _
example (a : α) (b : β) : (a, b).1 = a := Eq.refl _
example : 2 + 3 = 5 := Eq.refl _
```

This feature of the framework is so important that the library defines a notation `rfl` for `Eq.refl _`:

프레임워크의 이 기능은 너무 중요해서 라이브러리가 `Eq.refl _`에 대한 표기법 `rfl`을 정의합니다:

```
example (f : α → β) (a : α) : (fun x => f x) a = f a := rfl
example (a : α) (b : β) : (a, b).1 = a := rfl
example : 2 + 3 = 5 := rfl
```

Equality is much more than an equivalence relation, however. It has
the important property that every assertion respects the equivalence,
in the sense that we can substitute equal expressions without changing
the truth value. That is, given `h1 : a = b` and `h2 : p a`, we
can construct a proof for `p b` using substitution:
`Eq.subst h1 h2`.

하지만 동치는 단순한 동치 관계 이상입니다. 그것은 모든 주장이 동치를 존중한다는 중요한 성질을 가지고 있습니다. 즉, 진리값을 변경하지 않고 같은 표현식들을 대체할 수 있습니다. 즉, `h1 : a = b`와 `h2 : p a`가 주어지면, 대치를 사용하여 `p b`에 대한 증명을 구성할 수 있습니다: `Eq.subst h1 h2`.

```
example (α : Type) (a b : α) (p : α → Prop)
(h1 : a = b) (h2 : p a) : p b :=
Eq.subst h1 h2
example (α : Type) (a b : α) (p : α → Prop)
(h1 : a = b) (h2 : p a) : p b :=
h1 ▸ h2
```

The triangle in the second presentation is a macro built on top of
`Eq.subst` and `Eq.symm`, and you can enter it by typing `\t`.

두 번째 표현의 삼각형은 `Eq.subst`와 `Eq.symm` 위에 구축된 매크로이며, `\t`를 입력하여 입력할 수 있습니다.

The rule `Eq.subst` is used to define the following auxiliary rules,
which carry out more explicit substitutions. They are designed to deal
with applicative terms, that is, terms of form `s t`. Specifically,
`congrArg` can be used to replace the argument, `congrFun` can be
used to replace the term that is being applied, and `congr` can be
used to replace both at once.

규칙 `Eq.subst`는 보다 명시적인 대치를 수행하는 다음 보조 규칙을 정의하는 데 사용됩니다. 이들은 응용적 항, 즉 `s t` 형태의 항을 다루기 위해 설계되었습니다. 특히, `congrArg`는 인수를 대체하는 데 사용될 수 있고, `congrFun`은 적용되는 항을 대체하는 데 사용될 수 있으며, `congr`은 둘 다를 동시에 대체하는 데 사용될 수 있습니다.

```
variable (α : Type)
variable (a b : α)
variable (f g : α → Nat)
variable (h₁ : a = b)
variable (h₂ : f = g)
example : f a = f b := congrArg f h₁
example : f a = g a := congrFun h₂ a
example : f a = g b := congr h₂ h₁
```

Lean's library contains a large number of common identities, such as these:

Lean의 라이브러리는 다음과 같은 많은 수의 공통 항등식을 포함하고 있습니다:

```
variable (a b c : Nat)
example : a + 0 = a := Nat.add_zero a
example : 0 + a = a := Nat.zero_add a
example : a * 1 = a := Nat.mul_one a
example : 1 * a = a := Nat.one_mul a
example : a + b = b + a := Nat.add_comm a b
example : a + b + c = a + (b + c) := Nat.add_assoc a b c
example : a * b = b * a := Nat.mul_comm a b
example : a * b * c = a * (b * c) := Nat.mul_assoc a b c
example : a * (b + c) = a * b + a * c := Nat.mul_add a b c
example : a * (b + c) = a * b + a * c := Nat.left_distrib a b c
example : (a + b) * c = a * c + b * c := Nat.add_mul a b c
example : (a + b) * c = a * c + b * c := Nat.right_distrib a b c
```

Note that `Nat.mul_add` and `Nat.add_mul` are alternative names
for `Nat.left_distrib` and `Nat.right_distrib`, respectively. The
properties above are stated for the natural numbers (type `Nat`).

`Nat.mul_add`와 `Nat.add_mul`은 각각 `Nat.left_distrib`과 `Nat.right_distrib`의 대안적 이름임을 주목하세요. 위의 성질들은 자연수(타입 `Nat`)에 대해 명시됩니다.

Here is an example of a calculation in the natural numbers that uses
substitution combined with associativity and distributivity.

자연수에서 결합 법칙과 분배 법칙과 함께 대치를 사용하는 계산의 예는 다음과 같습니다.

```
example (x y : Nat) :
(x + y) * (x + y) =
x * x + y * x + x * y + y * y :=
have h1 : (x + y) * (x + y) = (x + y) * x + (x + y) * y :=
Nat.mul_add (x + y) x y
have h2 : (x + y) * (x + y) = x * x + y * x + (x * y + y * y) :=
(Nat.add_mul x y x) ▸ (Nat.add_mul x y y) ▸ h1
h2.trans (Nat.add_assoc (x * x + y * x) (x * y) (y * y)).symm
```

Notice that the second implicit parameter to `Eq.subst`, which
provides the context in which the substitution is to occur, has type
`α → Prop`. Inferring this predicate therefore requires an instance
of *higher-order unification*. In full generality, the problem of
determining whether a higher-order unifier exists is undecidable, and
Lean can at best provide imperfect and approximate solutions to the
problem. As a result, `Eq.subst` doesn't always do what you want it
to. The macro `h ▸ e` uses more effective heuristics for computing
this implicit parameter, and often succeeds in situations where
applying `Eq.subst` fails.

대치가 발생할 맥락을 제공하는 `Eq.subst`의 두 번째 암묵적 매개변수가 `α → Prop` 타입을 갖는다는 것을 주목하세요. 따라서 이 술어를 추론하려면 *고차 통일*의 인스턴스가 필요합니다. 완전한 일반성에서, 고차 통일자가 존재하는지 결정하는 문제는 판단 불가능하며, Lean은 최선을 다해 문제에 대한 불완전하고 대략적인 해결책을 제공할 수 있습니다. 결과적으로 `Eq.subst`는 항상 원하는 대로 작동하지 않습니다. 매크로 `h ▸ e`는 이 암묵적 매개변수를 계산하기 위해 더 효과적인 휴리스틱을 사용하며, `Eq.subst`를 적용하는 것이 실패하는 경우에 종종 성공합니다.

Because equational reasoning is so common and important, Lean provides
a number of mechanisms to carry it out more effectively. The next
section offers syntax that allow you to write calculational proofs in
a more natural and perspicuous way. But, more importantly, equational
reasoning is supported by a term rewriter, a simplifier, and other
kinds of automation. The term rewriter and simplifier are described
briefly in the next section, and then in greater detail in the next
chapter.

방정식적 추론이 매우 일반적이고 중요하기 때문에 Lean은 이를 더 효과적으로 수행하기 위한 여러 메커니즘을 제공합니다. 다음 섹션은 계산 증명을 더 자연스럽고 명확한 방식으로 작성할 수 있도록 하는 구문을 제공합니다. 하지만 더 중요하게는, 방정식적 추론은 항 재작성기, 단순화기 및 기타 자동화 형식으로 지원됩니다. 항 재작성기와 단순화기는 다음 섹션에서 간략하게 설명되고 그 다음 장에서 더 자세히 설명됩니다.

## 4.3. Calculational Proofs

A calculational proof is just a chain of intermediate results that are
meant to be composed by basic principles such as the transitivity of
equality. In Lean, a calculational proof starts with the keyword
`calc`, and has the following syntax:

계산 증명은 단순히 동치의 추이성과 같은 기본 원칙으로 합성되도록 의도된 중간 결과들의 체인입니다. Lean에서 계산 증명은 `calc` 키워드로 시작하며 다음과 같은 구문을 가집니다:

Note that the `calc` relations all have the same indentation. Each
`<proof>_i` is a proof for `<expr>_{i-1} op_i <expr>_i`.

`calc` 관계들이 모두 동일한 들여쓰기를 가지고 있음을 주목하세요. 각 `<proof>_i`는 `<expr>_{i-1} op_i <expr>_i`의 증명입니다.

We can also use `_` in the first relation (right after `<expr>_0`)
which is useful to align the sequence of relation/proof pairs:

우리는 또한 첫 번째 관계에서 `_`를 사용할 수 있습니다(`<expr>_0` 직후). 이는 관계/증명 쌍의 순서를 정렬하는 데 유용합니다:

Here is an example:

예는 다음과 같습니다:

```
variable (a b c d e : Nat)
theorem T
(h1 : a = b)
(h2 : b = c + 1)
(h3 : c = d)
(h4 : e = 1 + d) :
a = e :=
calc
a = b := h1
_ = c + 1 := h2
_ = d + 1 := congrArg Nat.succ h3
_ = 1 + d := Nat.add_comm d 1
_ = e := Eq.symm h4
```

This style of writing proofs is most effective when it is used in
conjunction with the `simp` and `rw` tactics, which are
discussed in greater detail in the next chapter. For example, using
`rw` for rewrite, the proof above could be written
as follows:

이 증명 작성 스타일은 다음 장에서 더 자세히 논의되는 `simp`와 `rw` 전술과 함께 사용할 때 가장 효과적입니다. 예를 들어 재작성을 위해 `rw`를 사용하면, 위의 증명을 다음과 같이 작성할 수 있습니다:

```
theorem T
(h1 : a = b)
(h2 : b = c + 1)
(h3 : c = d)
(h4 : e = 1 + d) :
a = e :=
calc
a = b := by rw [h1]
_ = c + 1 := by rw [h2]
_ = d + 1 := by rw [h3]
_ = 1 + d := by rw [Nat.add_comm]
_ = e := by rw [h4]
```

Essentially, the `rw` tactic uses a given equality (which can be a
hypothesis, a theorem name, or a complex term) to “rewrite” the
goal. If doing so reduces the goal to an identity `t = t`, the
tactic applies reflexivity to prove it.

본질적으로 `rw` 전술은 주어진 동치(가정, 정리 이름 또는 복잡한 항일 수 있음)를 사용하여 목표를 “재작성”합니다. 이렇게 하면 목표가 항등식 `t = t`로 축소되면, 전술은 반사성을 적용하여 그것을 증명합니다.

Rewrites can be applied sequentially, so that the proof above can be
shortened to this:

재작성은 순차적으로 적용될 수 있으므로 위의 증명을 다음과 같이 단축할 수 있습니다:

```
theorem T
(h1 : a = b)
(h2 : b = c + 1)
(h3 : c = d)
(h4 : e = 1 + d) :
a = e :=
calc
a = d + 1 := by rw [h1, h2, h3]
_ = 1 + d := by rw [Nat.add_comm]
_ = e := by rw [h4]
```

Or even this:

또는 심지어 이것처럼:

```
theorem T
(h1 : a = b)
(h2 : b = c + 1)
(h3 : c = d)
(h4 : e = 1 + d) :
a = e :=
by rw [h1, h2, h3, Nat.add_comm, h4]
```

The `simp` tactic, instead, rewrites the goal by applying the given
identities repeatedly, in any order, anywhere they are applicable in a
term. It also uses other rules that have been previously declared to
the system, and applies commutativity wisely to avoid looping. As a
result, we can also prove the theorem as follows:

`simp` 전술은 대신 주어진 항등식을 반복적으로, 임의의 순서로, 항에서 적용 가능한 모든 곳에 적용하여 목표를 재작성합니다. 또한 이전에 시스템에 선언된 다른 규칙들을 사용하고, 루핑을 피하기 위해 가환성을 현명하게 적용합니다. 결과적으로, 우리는 또한 정리를 다음과 같이 증명할 수 있습니다:

```
theorem T
(h1 : a = b)
(h2 : b = c + 1)
(h3 : c = d)
(h4 : e = 1 + d) :
a = e :=
by simp [h1, h2, h3, Nat.add_comm, h4]
```

We will discuss variations of `rw` and `simp` in the next chapter.

우리는 다음 장에서 `rw`와 `simp`의 변형을 논의할 것입니다.

The `calc` command can be configured for any relation that supports
some form of transitivity. It can even combine different relations.

`calc` 명령은 어떤 형태의 추이성을 지원하는 모든 관계에 대해 구성될 수 있습니다. 심지어 서로 다른 관계들을 조합할 수도 있습니다.

```
variable (a b c d : Nat)
example (h1 : a = b) (h2 : b ≤ c) (h3 : c + 1 < d) : a < d :=
calc
a = b := h1
_ < b + 1 := Nat.lt_succ_self b
_ ≤ c + 1 := Nat.succ_le_succ h2
_ < d := h3
```

You can “teach” `calc` new transitivity theorems by adding new instances
of the `Trans` type class. Type classes are introduced later, but the following
small example demonstrates how to extend the `calc` notation using new `Trans` instances.

`Trans` 타입 클래스의 새로운 인스턴스를 추가하여 `calc`에 새로운 추이성 정리를 “가르칠” 수 있습니다. 타입 클래스는 나중에 소개되지만, 다음의 작은 예는 새로운 `Trans` 인스턴스를 사용하여 `calc` 표기법을 확장하는 방법을 보여줍니다.

```
def divides (x y : Nat) : Prop :=
∃ k, k*x = y
def divides_trans (h₁ : divides x y) (h₂ : divides y z) : divides x z :=
let ⟨k₁, d₁⟩ := h₁
let ⟨k₂, d₂⟩ := h₂
⟨k₁ * k₂, by rw [Nat.mul_comm k₁ k₂, Nat.mul_assoc, d₁, d₂]⟩
def divides_mul (x : Nat) (k : Nat) : divides x (k*x) :=
⟨k, rfl⟩
instance : Trans divides divides divides where
trans := divides_trans
example (h₁ : divides x y) (h₂ : y = z) : divides x (2*z) :=
calc
divides x y := h₁
_ = z := h₂
divides _ (2*z) := divides_mul ..
infix:50 " | " => divides
example (h₁ : divides x y) (h₂ : y = z) : divides x (2*z) :=
calc
x | y := h₁
_ = z := h₂
_ | 2*z := divides_mul ..
```

The example above also makes it clear that you can use `calc` even if you do not have an infix
notation for your relation. Lean already includes the standard Unicode notation for divisibility
(using `∣`, which can be entered as `\dvd` or `\mid`), so the example above uses the ordinary
vertical bar to avoid a conflict. In practice, this is not a good idea, as it risks confusion with
the ASCII `|` used in the `match` `...` `with` expression.

위의 예는 또한 관계에 대한 중위 표기법이 없더라도 `calc`를 사용할 수 있다는 것을 명확하게 해줍니다. Lean은 이미 나누어떨어짐에 대한 표준 유니코드 표기법을 포함하고 있습니다(`∣` 사용, `\dvd` 또는 `\mid`로 입력 가능). 따라서 위의 예는 충돌을 피하기 위해 일반 수직 막대를 사용합니다. 실제로, 이는 `match` `...` `with` 표현에 사용되는 ASCII `|`와의 혼동 위험이 있으므로 좋은 생각이 아닙니다.

With `calc`, we can write the proof in the last section in a more
natural and perspicuous way.

`calc`를 사용하면, 우리는 마지막 섹션의 증명을 더 자연스럽고 명확한 방식으로 작성할 수 있습니다.

```
variable (x y : Nat)
example : (x + y) * (x + y) = x * x + y * x + x * y + y * y :=
calc
(x + y) * (x + y) = (x + y) * x + (x + y) * y :=
by rw [Nat.mul_add]
_ = x * x + y * x + (x + y) * y :=
by rw [Nat.add_mul]
_ = x * x + y * x + (x * y + y * y) :=
by rw [Nat.add_mul]
_ = x * x + y * x + x * y + y * y :=
by rw [←Nat.add_assoc]
```

The alternative `calc` notation is worth considering here. When the
first expression is taking this much space, using `_` in the first
relation naturally aligns all relations:

여기서 대체 `calc` 표기법을 고려할 가치가 있습니다. 첫 번째 표현이 이렇게 많은 공간을 차지할 때, 첫 번째 관계에서 `_`를 사용하면 모든 관계들이 자연스럽게 정렬됩니다:

```
variable (x y : Nat)
example : (x + y) * (x + y) = x * x + y * x + x * y + y * y :=
calc (x + y) * (x + y)
_ = (x + y) * x + (x + y) * y :=
by rw [Nat.mul_add]
_ = x * x + y * x + (x + y) * y :=
by rw [Nat.add_mul]
_ = x * x + y * x + (x * y + y * y) :=
by rw [Nat.add_mul]
_ = x * x + y * x + x * y + y * y :=
by rw [←Nat.add_assoc]
```

Here the left arrow before `Nat.add_assoc` tells rewrite to use the
identity in the opposite direction. (You can enter it with `\l` or
use the ASCII equivalent, `<-`.) If brevity is what we are after,
both `rw` and `simp` can do the job on their own:

여기서 `Nat.add_assoc` 앞의 왼쪽 화살표는 재작성에게 항등식을 반대 방향으로 사용하도록 지시합니다. (`\l`로 입력하거나 ASCII 동등물 `<-`를 사용할 수 있습니다.) 간결함이 우리가 추구하는 것이라면, `rw`와 `simp` 모두 단독으로 작업을 할 수 있습니다:

```
variable (x y : Nat)
example : (x + y) * (x + y) = x * x + y * x + x * y + y * y := by
rw [Nat.mul_add, Nat.add_mul, Nat.add_mul, ←Nat.add_assoc]
example : (x + y) * (x + y) = x * x + y * x + x * y + y * y := by
simp [Nat.mul_add, Nat.add_mul, Nat.add_assoc]
```

## 4.4. The Existential Quantifier

Finally, consider the existential quantifier, which can be written as
either `exists x : α, p x` or `∃ x : α, p x`. Both versions are
actually notationally convenient abbreviations for a more long-winded
expression, `Exists (fun x : α => p x)`, defined in Lean's library.

마지막으로 존재 양화사를 고려합니다. 이는 `exists x : α, p x` 또는 `∃ x : α, p x`로 작성할 수 있습니다. 두 버전 모두 실제로는 Lean의 라이브러리에 정의된 더 긴 표현식 `Exists (fun x : α => p x)`의 표기상 편리한 약자입니다.

As you should by now expect, the library includes both an introduction
rule and an elimination rule. The introduction rule is
straightforward: to prove `∃ x : α, p x`, it suffices to provide a
suitable term `t` and a proof of `p t`. Here are some examples:

지금쯤 예상했을 것처럼, 라이브러리는 도입 규칙과 소거 규칙을 모두 포함합니다. 도입 규칙은 간단합니다: `∃ x : α, p x`를 증명하려면, 적절한 항 `t`와 `p t`의 증명을 제공하면 충분합니다. 여기 몇 가지 예가 있습니다:

```
example : ∃ x : Nat, x > 0 :=
have h : 1 > 0 := Nat.zero_lt_succ 0
Exists.intro 1 h
example (x : Nat) (h : x > 0) : ∃ y, y < x :=
Exists.intro 0 h
example (x y z : Nat) (hxy : x < y) (hyz : y < z) : ∃ w, x < w ∧ w < z :=
Exists.intro y (And.intro hxy hyz)
#check @Exists.intro
```

```
@Exists.intro : ∀ {α : Sort u_1} {p : α → Prop} (w : α), p w → Exists p
```

We can use the anonymous constructor notation `⟨t, h⟩` for
`Exists.intro t h`, when the type is clear from the context.

타입이 맥락에서 명확할 때, 우리는 `Exists.intro t h`를 위한 익명 생성자 표기법 `⟨t, h⟩`를 사용할 수 있습니다.

```
example : ∃ x : Nat, x > 0 :=
have h : 1 > 0 := Nat.zero_lt_succ 0
⟨1, h⟩
example (x : Nat) (h : x > 0) : ∃ y, y < x :=
⟨0, h⟩
example (x y z : Nat) (hxy : x < y) (hyz : y < z) : ∃ w, x < w ∧ w < z :=
⟨y, hxy, hyz⟩
```

Note that `Exists.intro` has implicit arguments: Lean has to infer
the predicate `p : α → Prop` in the conclusion `∃ x, p x`. This
is not a trivial affair. For example, if we have
`hg : g 0 0 = 0` and write `Exists.intro 0 hg`, there are many possible values
for the predicate `p`, corresponding to the theorems `∃ x, g x x = x`,
`∃ x, g x x = 0`, `∃ x, g x 0 = x`, etc. Lean uses the
context to infer which one is appropriate. This is illustrated in the
following example, in which we set the option `pp.explicit` to true
to ask Lean's pretty-printer to show the implicit arguments.

`Exists.intro`는 암묵적 인수를 가진다는 것을 주목하세요: Lean은 결론 `∃ x, p x`에서 술어 `p : α → Prop`을 추론해야 합니다. 이것은 자명하지 않은 문제입니다. 예를 들어, `hg : g 0 0 = 0`을 가지고 `Exists.intro 0 hg`를 쓰면, 술어 `p`에 대한 많은 가능한 값들이 있습니다. `∃ x, g x x = x`, `∃ x, g x x = 0`, `∃ x, g x 0 = x` 등의 정리에 해당합니다. Lean은 맥락을 사용하여 어느 것이 적절한지 추론합니다. 이는 다음 예에서 설명되며, 여기서 우리는 옵션 `pp.explicit`을 true로 설정하여 Lean의 예쁜 출력기가 암묵적 인수를 표시하도록 요청합니다.

```
variable (g : Nat → Nat → Nat)
theorem gex1 (hg : g 0 0 = 0) : ∃ x, g x x = x := ⟨0, hg⟩
theorem gex2 (hg : g 0 0 = 0) : ∃ x, g x 0 = x := ⟨0, hg⟩
theorem gex3 (hg : g 0 0 = 0) : ∃ x, g 0 0 = x := ⟨0, hg⟩
theorem gex4 (hg : g 0 0 = 0) : ∃ x, g x x = 0 := ⟨0, hg⟩
set_option pp.explicit true  -- display implicit arguments

#print gex1
```

```
theorem gex1 : ∀ (g : Nat → Nat → Nat),
  @Eq Nat
      (g (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0)))
        (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0))))
      (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0))) →
    @Exists Nat fun x => @Eq Nat (g x x) x :=
fun g hg => @Exists.intro Nat (fun x => @Eq Nat (g x x) x) (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0))) hg
```

```
#print gex2
```

```
theorem gex2 : ∀ (g : Nat → Nat → Nat),
  @Eq Nat
      (g (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0)))
        (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0))))
      (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0))) →
    @Exists Nat fun x => @Eq Nat (g x (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0)))) x :=
fun g hg =>
  @Exists.intro Nat (fun x => @Eq Nat (g x (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0)))) x)
    (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0))) hg
```

```
#print gex3
```

```
theorem gex3 : ∀ (g : Nat → Nat → Nat),
  @Eq Nat
      (g (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0)))
        (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0))))
      (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0))) →
    @Exists Nat fun x =>
      @Eq Nat
        (g (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0)))
          (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0))))
        x :=
fun g hg =>
  @Exists.intro Nat
    (fun x =>
      @Eq Nat
        (g (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0)))
          (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0))))
        x)
    (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0))) hg
```

```
#print gex4
```

```
theorem gex4 : ∀ (g : Nat → Nat → Nat),
  @Eq Nat
      (g (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0)))
        (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0))))
      (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0))) →
    @Exists Nat fun x => @Eq Nat (g x x) (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0))) :=
fun g hg =>
  @Exists.intro Nat (fun x => @Eq Nat (g x x) (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0))))
    (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0))) hg
```

We can view `Exists.intro` as an information-hiding operation, since
it hides the witness to the body of the assertion. The existential
elimination rule, `Exists.elim`, performs the opposite operation. It
allows us to prove a proposition `q` from `∃ x : α, p x`, by
showing that `q` follows from `p w` for an arbitrary value
`w`. Roughly speaking, since we know there is an `x` satisfying
`p x`, we can give it a name, say, `w`. If `q` does not mention
`w`, then showing that `q` follows from `p w` is tantamount to
showing that `q` follows from the existence of any such `x`. Here
is an example:

우리는 `Exists.intro`를 정보 숨김 작업으로 볼 수 있습니다. 왜냐하면 그것이 주장의 본체에 대한 증거를 숨기기 때문입니다. 존재 소거 규칙인 `Exists.elim`은 반대 작업을 수행합니다. 이는 `∃ x : α, p x`에서 명제 `q`를 증명할 수 있게 해줍니다. 임의의 값 `w`에 대해 `q`가 `p w`에서 따라옴을 보임으로써. 대략적으로, 우리는 `p x`를 만족하는 `x`가 있다는 것을 알고 있으므로, 그것에 이름을 붙일 수 있습니다. 예를 들어 `w`라고 합시다. `q`가 `w`를 언급하지 않으면, `q`가 `p w`에서 따라옴을 보이는 것은 `q`가 그러한 임의의 `x`의 존재에서 따라옴을 보이는 것과 같습니다. 예는 다음과 같습니다:

```
variable (α : Type) (p q : α → Prop)
example (h : ∃ x, p x ∧ q x) : ∃ x, q x ∧ p x :=
Exists.elim h
(fun w =>
fun hw : p w ∧ q w =>
show ∃ x, q x ∧ p x from ⟨w, hw.right, hw.left⟩)
```

It may be helpful to compare the exists-elimination rule to the
or-elimination rule: the assertion `∃ x : α, p x` can be thought of
as a big disjunction of the propositions `p a`, as `a` ranges over
all the elements of `α`. Note that the anonymous constructor
notation `⟨w, hw.right, hw.left⟩` abbreviates a nested constructor
application; we could equally well have written `⟨w, ⟨hw.right, hw.left⟩⟩`.

존재 소거 규칙을 또는 소거 규칙과 비교하는 것이 도움이 될 수 있습니다: 주장 `∃ x : α, p x`는 `a`가 `α`의 모든 원소들에 걸쳐 범위를 가질 때 명제들 `p a`의 큰 분리로 생각할 수 있습니다. 익명 생성자 표기법 `⟨w, hw.right, hw.left⟩`는 중첩된 생성자 응용을 약자로 나타냅니다; 우리는 동일하게 `⟨w, ⟨hw.right, hw.left⟩⟩`로 작성했을 수도 있습니다.

Notice that an existential proposition is very similar to a sigma
type, as described in dependent types section. The difference is that
existential propositions are *propositions*, while sigma types are *types*.
Otherwise, they are very similar. Given a predicate `p : α → Prop` and a family of types `β : α → Type`,
for a term `a : α` with `h : p a` and `h' : β a`, the term `Exists.intro a h` has
type `(∃ x : α, p x) : Prop`, while `Sigma.mk a h'` has type
`(Σ x : α, β x)`. The similarity between `∃` and `Σ` is another
instance of the [Curry-Howard isomorphism](../03-propositions-and-proofs/#--tech-term-Curry-Howard-isomorphism).

존재 명제가 종속 타입 섹션에 설명된 시그마 타입과 매우 유사함을 주목하세요. 차이점은 존재 명제는 *명제*인 반면 시그마 타입은 *타입*이라는 것입니다. 그 외에는 매우 유사합니다. 술어 `p : α → Prop`과 타입 족 `β : α → Type`이 주어질 때, 항 `a : α`에 대해 `h : p a`와 `h' : β a`를 가진다면, 항 `Exists.intro a h`는 타입 `(∃ x : α, p x) : Prop`을 가지는 반면, `Sigma.mk a h'`는 타입 `(Σ x : α, β x)`을 가집니다. `∃`과 `Σ` 사이의 유사성은 [Curry-Howard 동형](../03-propositions-and-proofs/#--tech-term-Curry-Howard-isomorphism)의 또 다른 인스턴스입니다.

Lean provides a more convenient way to eliminate from an existential
quantifier with the `match` expression:

Lean은 `match` 표현식으로 존재 양화사에서 소거하는 더 편리한 방법을 제공합니다:

```
variable (α : Type) (p q : α → Prop)
example (h : ∃ x, p x ∧ q x) : ∃ x, q x ∧ p x :=
match h with
| ⟨w, hw⟩ => ⟨w, hw.right, hw.left⟩
```

The `match` expression is part of Lean's function definition system,
which provides convenient and expressive ways of defining complex
functions. Once again, it is the [Curry-Howard isomorphism](../03-propositions-and-proofs/#--tech-term-Curry-Howard-isomorphism) that allows
us to co-opt this mechanism for writing proofs as well. The `match`
statement “destructs” the existential assertion into the components
`w` and `hw`, which can then be used in the body of the statement
to prove the proposition. We can annotate the types used in the match
for greater clarity:

`match` 표현식은 Lean의 함수 정의 시스템의 일부이며, 복잡한 함수를 정의하는 편리하고 표현력 있는 방법을 제공합니다. 다시 한 번, [Curry-Howard 동형](../03-propositions-and-proofs/#--tech-term-Curry-Howard-isomorphism)이 증명을 작성하기 위해 이 메커니즘을 채택할 수 있게 해줍니다. `match` 문은 존재 주장을 성분 `w`와 `hw`로 “분해”하며, 이는 명제를 증명하기 위해 문의 본체에서 사용할 수 있습니다. 더 큰 명확성을 위해 일치에 사용된 타입을 주석 처리할 수 있습니다:

```
example (h : ∃ x, p x ∧ q x) : ∃ x, q x ∧ p x :=
match h with
| ⟨(w : α), (hw : p w ∧ q w)⟩ => ⟨w, hw.right, hw.left⟩
```

We can even use the match statement to decompose the conjunction at the same time:

우리는 동시에 결합을 분해하기 위해 일치 문을 사용할 수도 있습니다:

```
example (h : ∃ x, p x ∧ q x) : ∃ x, q x ∧ p x :=
match h with
| ⟨w, hpw, hqw⟩ => ⟨w, hqw, hpw⟩
```

Lean also provides a pattern-matching `let` expression:

Lean은 또한 패턴 매칭 `let` 표현식을 제공합니다:

```
example (h : ∃ x, p x ∧ q x) : ∃ x, q x ∧ p x :=
let ⟨w, hpw, hqw⟩ := h
⟨w, hqw, hpw⟩
```

This is essentially just alternative notation for the `match`
construct above. Lean will even allow us to use an implicit `match`
in the `fun` expression:

이는 본질적으로 위의 `match` 구성에 대한 단순한 대체 표기법입니다. Lean은 심지어 `fun` 표현식에서 암묵적 `match`를 사용하도록 허용합니다:

```
example : (∃ x, p x ∧ q x) → ∃ x, q x ∧ p x :=
fun ⟨w, hpw, hqw⟩ => ⟨w, hqw, hpw⟩
```

We will see in [Induction and Recursion](../08-induction-and-recursion/#induction-and-recursion) that all these variations are
instances of a more general pattern-matching construct.

우리는 [귀납과 재귀](../08-induction-and-recursion/#induction-and-recursion)에서 이러한 모든 변형이 더 일반적인 패턴 매칭 구성의 인스턴스임을 볼 것입니다.

In the following example, we define `IsEven a` as `∃ b, a = 2 * b`,
and then we show that the sum of two even numbers is an even number.

다음 예에서, 우리는 `IsEven a`를 `∃ b, a = 2 * b`로 정의하고, 그 다음 두 짝수의 합이 짝수라는 것을 보여줍니다.

```
def IsEven (a : Nat) := ∃ b, a = 2 * b
theorem even_plus_even (h1 : IsEven a) (h2 : IsEven b) :
IsEven (a + b) :=
Exists.elim h1 (fun w1 (hw1 : a = 2 * w1) =>
Exists.elim h2 (fun w2 (hw2 : b = 2 * w2) =>
Exists.intro (w1 + w2)
(calc a + b
_ = 2 * w1 + 2 * w2 := by rw [hw1, hw2]
_ = 2 * (w1 + w2) := by rw [Nat.mul_add])))
```

Using the various gadgets described in this chapter—the match
statement, anonymous constructors, and the `rewrite` tactic, we can
write this proof concisely as follows:

이 장에서 설명한 다양한 도구들(일치 문, 익명 생성자, `rewrite` 전술)을 사용하면 이 증명을 다음과 같이 간결하게 작성할 수 있습니다:

```
theorem even_plus_even (h1 : IsEven a) (h2 : IsEven b) :
IsEven (a + b) :=
match h1, h2 with
| ⟨w1, hw1⟩, ⟨w2, hw2⟩ =>
⟨w1 + w2, by rw [hw1, hw2, Nat.mul_add]⟩
```

Just as the constructive “or” is stronger than the classical “or,” so,
too, is the constructive “exists” stronger than the classical
“exists”. For example, the following implication requires classical
reasoning because, from a constructive standpoint, knowing that it is
not the case that every `x` satisfies `¬ p` is not the same as
having a particular `x` that satisfies `p`.

구성적 “또는”이 고전적 “또는”보다 더 강한 것처럼, 구성적 “존재”도 고전적 “존재”보다 더 강합니다. 예를 들어, 다음의 함의는 고전적 추론을 필요로 합니다. 왜냐하면 구성적 관점에서, 모든 `x`가 `¬ p`를 만족하는 것은 아니라는 것을 아는 것과 `p`를 만족하는 특정 `x`를 갖는 것은 동일하지 않기 때문입니다.

```
open Classical
variable (p : α → Prop)
example (h : ¬ ∀ x, ¬ p x) : ∃ x, p x :=
byContradiction
(fun h1 : ¬ ∃ x, p x =>
have h2 : ∀ x, ¬ p x :=
fun x =>
fun h3 : p x =>
have h4 : ∃ x, p x := ⟨x, h3⟩
show False from h1 h4
show False from h h2)
```

What follows are some common identities involving the existential
quantifier. In the exercises below, we encourage you to prove as many
as you can. We also leave it to you to determine which are
nonconstructive, and hence require some form of classical reasoning.

다음은 존재 양화사를 포함하는 일반적인 항등식들입니다. 아래의 연습문제에서, 우리는 가능한 한 많은 것을 증명하도록 권장합니다. 또한 어느 것이 구성적이지 않은지 결정하고 따라서 어떤 형태의 고전적 추론이 필요한지 결정하는 것은 여러분에게 맡깁니다.

```
open Classical
variable (α : Type) (p q : α → Prop)
variable (r : Prop)
example : (∃ x : α, r) → r := sorry
example (a : α) : r → (∃ x : α, r) := sorry
example : (∃ x, p x ∧ r) ↔ (∃ x, p x) ∧ r := sorry
example : (∃ x, p x ∨ q x) ↔ (∃ x, p x) ∨ (∃ x, q x) := sorry
example : (∀ x, p x) ↔ ¬ (∃ x, ¬ p x) := sorry
example : (∃ x, p x) ↔ ¬ (∀ x, ¬ p x) := sorry
example : (¬ ∃ x, p x) ↔ (∀ x, ¬ p x) := sorry
example : (¬ ∀ x, p x) ↔ (∃ x, ¬ p x) := sorry
example : (∀ x, p x → r) ↔ (∃ x, p x) → r := sorry
example (a : α) : (∃ x, p x → r) ↔ (∀ x, p x) → r := sorry
example (a : α) : (∃ x, r → p x) ↔ (r → ∃ x, p x) := sorry
```

Notice that the second example and the last two examples require the
assumption that there is at least one element `a` of type `α`.

두 번째 예와 마지막 두 예는 타입 `α`의 적어도 하나의 원소 `a`가 있다는 가정을 필요로 함을 주목하세요.

Here are solutions to two of the more difficult ones:

여기 더 어려운 것들 중 두 개의 해답이 있습니다:

```
open Classical
variable (α : Type) (p q : α → Prop)
variable (a : α)
variable (r : Prop)
example : (∃ x, p x ∨ q x) ↔ (∃ x, p x) ∨ (∃ x, q x) :=
Iff.intro
(fun ⟨a, (h1 : p a ∨ q a)⟩ =>
Or.elim h1
(fun hpa : p a => Or.inl ⟨a, hpa⟩)
(fun hqa : q a => Or.inr ⟨a, hqa⟩))
(fun h : (∃ x, p x) ∨ (∃ x, q x) =>
Or.elim h
(fun ⟨a, hpa⟩ => ⟨a, (Or.inl hpa)⟩)
(fun ⟨a, hqa⟩ => ⟨a, (Or.inr hqa)⟩))
example : (∃ x, p x → r) ↔ (∀ x, p x) → r :=
Iff.intro
(fun ⟨b, (hb : p b → r)⟩ =>
fun h2 : ∀ x, p x =>
show r from hb (h2 b))
(fun h1 : (∀ x, p x) → r =>
show ∃ x, p x → r from
byCases
(fun hap : ∀ x, p x => ⟨a, λ h' => h1 hap⟩)
(fun hnap : ¬ ∀ x, p x =>
byContradiction
(fun hnex : ¬ ∃ x, p x → r =>
have hap : ∀ x, p x :=
fun x =>
byContradiction
(fun hnp : ¬ p x =>
have hex : ∃ x, p x → r := ⟨x, (fun hp => absurd hp hnp)⟩
show False from hnex hex)
show False from hnap hap)))
```

## 4.5. More on the Proof Language

We have seen that keywords like `fun`, `have`, and `show` make
it possible to write formal proof terms that mirror the structure of
informal mathematical proofs. In this section, we discuss some
additional features of the proof language that are often convenient.

우리는 `fun`, `have`, `show`와 같은 키워드들이 비공식적인 수학 증명의 구조를 반영하는 형식적 증명 항을 작성하는 것을 가능하게 하는 것을 보았습니다. 이 섹션에서, 우리는 종종 편리한 증명 언어의 추가 기능들을 논의합니다.

To start with, we can use anonymous `have` expressions to introduce an
auxiliary goal without having to label it. We can refer to the last
expression introduced in this way using the keyword `this`:

시작하기 위해, 우리는 익명 `have` 표현식을 사용하여 보조 목표를 레이블을 붙이지 않고 도입할 수 있습니다. 우리는 키워드 `this`를 사용하여 이러한 방식으로 도입된 마지막 표현식을 참조할 수 있습니다:

```
variable (f : Nat → Nat)
variable (h : ∀ x : Nat, f x ≤ f (x + 1))
example : f 0 ≤ f 3 :=
have : f 0 ≤ f 1 := h 0
have : f 0 ≤ f 2 := Nat.le_trans this (h 1)
show f 0 ≤ f 3 from Nat.le_trans this (h 2)
```

Often proofs move from one fact to the next, so this can be effective
in eliminating the clutter of lots of labels.

증명은 종종 한 사실에서 다음으로 진행되므로, 이는 많은 레이블의 혼잡을 제거하는 데 효과적일 수 있습니다.

When the goal can be inferred, we can also ask Lean instead to fill in
the proof by writing `by assumption`:

목표를 추론할 수 있을 때, 우리는 또한 `by assumption`을 작성하여 Lean에 증명을 채우도록 요청할 수 있습니다:

```
example : f 0 ≤ f 3 :=
have : f 0 ≤ f 1 := h 0
have : f 0 ≤ f 2 := Nat.le_trans (by assumption) (h 1)
show f 0 ≤ f 3 from Nat.le_trans (by assumption) (h 2)
```

This tells Lean to use the `assumption` tactic, which, in turn,
proves the goal by finding a suitable hypothesis in the local
context. We will learn more about the `assumption` tactic in the
next chapter.

이것은 Lean에 `assumption` 전술을 사용하도록 지시하며, 이는 순차적으로 로컬 맥락에서 적절한 가정을 찾음으로써 목표를 증명합니다. 우리는 다음 장에서 `assumption` 전술에 대해 더 배울 것입니다.

We can also ask Lean to fill in the proof by writing `‹p›`, where
`p` is the proposition whose proof we want Lean to find in the
context. You can type these corner quotes using `\f<` and `\f>`,
respectively. The letter “f” is for “French,” since the Unicode
symbols can also be used as French quotation marks. In fact, the
notation is defined in Lean as follows:

우리는 또한 `‹p›`를 작성하여 Lean에 증명을 채우도록 요청할 수 있습니다. 여기서 `p`는 우리가 Lean이 맥락에서 찾기를 원하는 명제입니다. 각각 `\f<`와 `\f>`를 사용하여 이러한 모서리 따옴표를 입력할 수 있습니다. 문자 “f”는 “French”이며, 유니코드 기호들은 프랑스 따옴표로도 사용될 수 있습니다. 실제로, 표기법은 Lean에서 다음과 같이 정의됩니다:

```
notation "‹" p "›" => show p by assumption
```

This approach is more robust than using `by assumption`, because the
type of the assumption that needs to be inferred is given
explicitly. It also makes proofs more readable. Here is a more
elaborate example:

이 접근 방식은 추론되어야 하는 가정의 타입이 명시적으로 주어지므로 `by assumption`을 사용하는 것보다 더 견고합니다. 또한 증명을 더 읽기 쉽게 만듭니다. 다음은 더 정교한 예입니다:

```
variable (f : Nat → Nat)
variable (h : ∀ x : Nat, f x ≤ f (x + 1))
example : f 0 ≥ f 1 → f 1 ≥ f 2 → f 0 = f 2 :=
fun _ : f 0 ≥ f 1 =>
fun _ : f 1 ≥ f 2 =>
have : f 0 ≥ f 2 := Nat.le_trans ‹f 1 ≥ f 2› ‹f 0 ≥ f 1›
have : f 0 ≤ f 2 := Nat.le_trans (h 0) (h 1)
show f 0 = f 2 from Nat.le_antisymm this ‹f 0 ≥ f 2›
```

Keep in mind that you can use the French quotation marks in this way
to refer to *anything* in the context, not just things that were
introduced anonymously. Its use is also not limited to propositions,
though using it for data is somewhat odd:

이 방식으로 프랑스 따옴표를 사용하여 익명으로 도입된 것들뿐만 아니라 맥락에서 *무엇이든* 참조할 수 있다는 점을 기억하세요. 그 사용은 명제들로만 제한되지 않지만, 데이터에 대해 사용하는 것은 다소 이상합니다:

```
example (n : Nat) : Nat := ‹Nat›
```

Later, we show how you can extend the proof language using the Lean macro system.

## 4.6. Exercises

Prove these equivalences:    You should also try to understand why the reverse implication is not derivable in the last example.

나중에, 우리는 Lean 매크로 시스템을 사용하여 증명 언어를 확장하는 방법을 보여줍니다.

1. 다음 동치(equivalences)들을 증명하세요:

```
variable (α : Type) (p q : α → Prop)
example : (∀ x, p x ∧ q x) ↔ (∀ x, p x) ∧ (∀ x, q x) := sorry
example : (∀ x, p x → q x) → (∀ x, p x) → (∀ x, q x) := sorry
example : (∀ x, p x) ∨ (∀ x, q x) → ∀ x, p x ∨ q x := sorry
```

2. It is often possible to bring a component of a formula outside a
   universal quantifier, when it does not depend on the quantified
   variable. Try proving these (one direction of the second of these
   requires classical logic):

마지막 예제에서 역 함의(reverse implication)가 도출될 수 없는 이유를 이해하려고 노력해보아야 합니다.

2. 공식의 구성 요소가 양화(quantified)된 변수에 의존하지 않을 때, 보편 양화사(universal quantifier) 밖으로 그 구성 요소를 가져오는 것이 종종 가능합니다. 다음을 증명해 보세요 (이 중 두 번째의 한 방향은 고전 논리가 필요합니다):

```
variable (α : Type) (p q : α → Prop)
variable (r : Prop)
example : α → ((∀ x : α, r) ↔ r) := sorry
example : (∀ x, p x ∨ r) ↔ (∀ x, p x) ∨ r := sorry
example : (∀ x, r → p x) ↔ (r → ∀ x, p x) := sorry
```

3. Consider the “barber paradox,” that is, the claim that in a certain
   town there is a (male) barber that shaves all and only the men who
   do not shave themselves. Prove that this is a contradiction:

3. “이발사 역설(barber paradox)”을 고려해 보세요. 즉, 어떤 마을에 스스로 면도하지 않는 모든 남자만 면도하는 (남자) 이발사가 있다는 주장입니다. 이것이 모순임을 증명해 보세요:

```
variable (men : Type) (barber : men)
variable (shaves : men → men → Prop)
example (h : ∀ x : men, shaves barber x ↔ ¬ shaves x x) : False :=
sorry
```

4. Remember that, without any parameters, an expression of type
   `Prop` is just an assertion. Fill in the definitions of `prime`
   and `Fermat_prime` below, and construct each of the given
   assertions. For example, you can say that there are infinitely many
   primes by asserting that for every natural number `n`, there is a
   prime number greater than `n`. Goldbach's weak conjecture states
   that every odd number greater than 5 is the sum of three
   primes. Look up the definition of a Fermat prime or any of the
   other statements, if necessary.

4. 매개변수가 없는 `Prop` 타입의 표현식은 단순히 주장에 불과하다는 것을 기억하세요. 아래의 `prime`과 `Fermat_prime`의 정의를 채우고, 주어진 각각의 주장을 구성해 보세요. 예를 들어, 모든 자연수 `n`에 대해 `n`보다 큰 소수가 존재한다고 주장함으로써 소수가 무한히 많다고 말할 수 있습니다. 골드바흐의 약한 추측(Goldbach's weak conjecture)은 5보다 큰 모든 홀수는 세 소수의 합이라고 명시합니다. 필요한 경우 페르마 소수(Fermat prime)의 정의나 기타 다른 명제들을 찾아보세요.

```
def even (n : Nat) : Prop := sorry
def prime (n : Nat) : Prop := sorry
def infinitely_many_primes : Prop := sorry
def Fermat_prime (n : Nat) : Prop := sorry
def infinitely_many_Fermat_primes : Prop := sorry
def goldbach_conjecture : Prop := sorry
def Goldbach's_weak_conjecture : Prop := sorry
def Fermat's_last_theorem : Prop := sorry
```

5. Prove as many of the identities listed in the Existential
   Quantifier section as you can.

5. 존재 양화사(Existential Quantifier) 섹션에 나열된 항등식들을 가능한 한 많이 증명해 보세요.
