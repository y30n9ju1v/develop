---
title: "12. 공리와 계산"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "theorem-proving", "type-theory"]
categories: ["programming"]
description: "선택 공리 같은 추가 공리와 그것이 계산 가능성에 미치는 영향을 다룹니다."
---

We have seen that the version of the Calculus of Constructions that
has been implemented in Lean includes dependent function types,
inductive types, and a hierarchy of universes that starts with an
[impredicative](../04-quantifiers-and-equality/#--tech-term-impredicative), [proof-irrelevant](../03-propositions-and-proofs/#--tech-term-proof-irrelevance) `Prop` at the bottom. In this
chapter, we consider ways of extending the CIC with additional axioms
and rules. Extending a foundational system in such a way is often
convenient; it can make it possible to prove more theorems, as well as
make it easier to prove theorems that could have been proved
otherwise. But there can be negative consequences of adding additional
axioms, consequences which may go beyond concerns about their
correctness. In particular, the use of axioms bears on the
computational content of definitions and theorems, in ways we will
explore here.

Lean에 구현된 구성 계산법(Calculus of Constructions)은 종속 함수 타입, 귀납적 타입, 그리고 하단에 [함축적](../04-quantifiers-and-equality/#--tech-term-impredicative)이고 [증명 무관한](../03-propositions-and-proofs/#--tech-term-proof-irrelevance) `Prop`으로 시작하는 우주 계층을 포함합니다. 이 장에서는 추가 공리와 규칙으로 CIC을 확장하는 방법을 고려합니다. 이런 식으로 기초 시스템을 확장하는 것은 종종 편리합니다. 더 많은 정리를 증명하는 것을 가능하게 할 수 있을 뿐만 아니라 다른 방식으로 증명했을 수 있는 정리를 더 쉽게 증명할 수 있게 합니다. 그러나 추가 공리를 더하는 것에는 부정적인 결과가 있을 수 있으며, 이러한 결과는 그 정확성에 대한 우려를 넘어설 수 있습니다. 특히 공리의 사용은 정의와 정리의 계산 내용에 영향을 미치며, 여기서 우리가 탐구할 방식입니다.

Lean is designed to support both computational and classical
reasoning. Users that are so inclined can stick to a “computationally
pure” fragment, which guarantees that closed expressions in the system
evaluate to canonical normal forms. In particular, any closed
computationally pure expression of type `Nat`, for example, will
reduce to a numeral.

Lean은 계산적 추론과 고전적 추론을 모두 지원하도록 설계되었습니다. 경향이 있는 사용자는 “계산적으로 순수한” 조각을 고수할 수 있으며, 이는 시스템의 닫힌 식이 정규 정규 형식으로 평가됨을 보장합니다. 특히, 예를 들어 `Nat` 타입의 닫힌 계산적으로 순수한 식은 숫자로 축약됩니다.

Lean's standard library defines an additional axiom, propositional
extensionality, and a quotient construction which in turn implies the
principle of function extensionality. These extensions are used, for
example, to develop theories of sets and finite sets. We will see
below that using these theorems can block evaluation in Lean's kernel,
so that closed terms of type `Nat` no longer evaluate to numerals. But
Lean erases types and propositional information when compiling
definitions to executable code, and since
these axioms only add new propositions, they are compatible with that
computational interpretation. Even computationally inclined users may
wish to use the classical law of the excluded middle to reason about
computation. This also blocks evaluation in the kernel, but it is
compatible with compiled code.

Lean의 표준 라이브러리는 추가 공리인 명제적 확장성(propositional extensionality)과 함수적 확장성의 원리를 함축하는 몫 구성(quotient construction)을 정의합니다. 이러한 확장은 예를 들어 집합과 유한 집합의 이론을 개발하는 데 사용됩니다. 아래에서 이 정리들을 사용하면 Lean의 커널에서 평가를 차단할 수 있음을 볼 것이며, `Nat` 타입의 닫힌 항이 더 이상 숫자로 평가되지 않습니다. 그러나 Lean은 정의를 실행 가능한 코드로 컴파일할 때 타입과 명제적 정보를 지우므로, 이러한 공리는 새로운 명제만 추가하기 때문에 계산적 해석과 호환됩니다. 계산적 경향이 있는 사용자도 계산에 대해 추론하기 위해 배제된 중간의 고전적 법칙을 사용하기를 원할 수 있습니다. 이것도 커널에서의 평가를 차단하지만, 컴파일된 코드와는 호환됩니다.

The standard library also defines a choice principle that is entirely
antithetical to a computational interpretation, since it magically
produces “data” from a proposition asserting its existence. Its use is
essential to some classical constructions, and users can import it
when needed. But expressions that use this construction to produce
data do not have computational content, and in Lean we are required to
mark such definitions as `noncomputable` to flag that fact.

표준 라이브러리는 또한 선택 원리(choice principle)를 정의하는데, 이는 명제의 존재를 주장하는 것으로부터 “데이터”를 마술처럼 생성하기 때문에 계산적 해석과 완전히 모순됩니다. 그 사용은 일부 고전적 구성에 필수적이며, 사용자는 필요할 때 이를 가져올 수 있습니다. 그러나 이 구성을 사용하여 데이터를 생성하는 식은 계산 내용을 가지지 않으며, Lean에서는 그러한 정의를 `noncomputable`로 표시하여 이 사실을 표시해야 합니다.

Using a clever trick (known as Diaconescu's theorem), one can use
propositional extensionality, function extensionality, and choice to
derive the law of the excluded middle. As noted above, however, use of
the law of the excluded middle is still compatible with
compilation, as are other classical principles, as
long as they are not used to manufacture data.

영리한 트릭(디아코네스쿠 정리로 알려짐)을 사용하면, 명제적 확장성, 함수적 확장성, 그리고 선택을 사용하여 배제된 중간의 법칙을 유도할 수 있습니다. 그러나 위에서 언급했듯이, 배제된 중간의 법칙의 사용은 여전히 컴파일과 호환되며, 다른 고전적 원리들도 데이터를 생성하는 데 사용되지 않는 한 호환됩니다.

To summarize, then, on top of the underlying framework of universes,
dependent function types, and inductive types, the standard library
adds three additional components:

the axiom of propositional extensionality
* a quotient construction, which implies function extensionality
* a choice principle, which produces data from an existential proposition.

a quotient construction, which implies function extensionality

a choice principle, which produces data from an existential proposition.

The first two of these block normalization within Lean, but are
compatible with code generation, whereas the third is not amenable
to computational interpretation. We will spell out the details more
precisely below.

요약하면, 우주, 종속 함수 타입, 그리고 귀납적 타입의 기본 프레임워크 위에, 표준 라이브러리는 세 가지 추가 구성 요소를 추가합니다:

* 명제적 확장성의 공리

* 함수적 확장성을 함축하는 몫 구성

* 존재적 명제로부터 데이터를 생성하는 선택 원리.

이 중 처음 두 개는 Lean 내에서 정규화를 차단하지만 코드 생성과는 호환되는 반면, 세 번째는 계산적 해석에 적합하지 않습니다. 아래에서 세부 사항을 더 정확히 설명하겠습니다.

## 12.1. Historical and Philosophical Context

For most of its history, mathematics was essentially computational:
geometry dealt with constructions of geometric objects, algebra was
concerned with algorithmic solutions to systems of equations, and
analysis provided means to compute the future behavior of systems
evolving over time. From the proof of a theorem to the effect that
“for every `x`, there is a `y` such that ...”, it was generally
straightforward to extract an algorithm to compute such a `y` given
`x`.

대부분의 역사에 걸쳐 수학은 본질적으로 계산적이었습니다: 기하학은 기하학적 객체의 구성을 다루었고, 대수학은 방정식 시스템에 대한 알고리즘적 해를 고려했으며, 분석은 시간에 따라 진화하는 시스템의 미래 행동을 계산하는 수단을 제공했습니다. “모든 `x`에 대해, ... 인 `y`가 존재한다”는 정리의 증명으로부터, 주어진 `x`에 대해 그러한 `y`를 계산하는 알고리즘을 추출하는 것이 일반적으로 직설적이었습니다.

In the nineteenth century, however, increases in the complexity of
mathematical arguments pushed mathematicians to develop new styles of
reasoning that suppress algorithmic information and invoke
descriptions of mathematical objects that abstract away the details of
how those objects are represented. The goal was to obtain a powerful
“conceptual” understanding without getting bogged down in
computational details, but this had the effect of admitting
mathematical theorems that are simply *false* on a direct
computational reading.

그러나 19세기에 수학적 논거의 복잡성이 증가하면서 수학자들은 알고리즘적 정보를 억제하고 그 객체가 어떻게 표현되는지의 세부 사항을 추상화하는 수학적 객체의 설명을 호출하는 새로운 추론 스타일을 개발하도록 강요받았습니다. 목표는 계산 세부 사항에 얽매이지 않고 강력한 “개념적” 이해를 얻는 것이었지만, 이는 직접적인 계산적 해석에서 단순히 *거짓*인 수학적 정리를 인정하는 효과를 가졌습니다.

There is still fairly uniform agreement today that computation is
important to mathematics. But there are different views as to how best
to address computational concerns. From a *constructive* point of
view, it is a mistake to separate mathematics from its computational
roots; every meaningful mathematical theorem should have a direct
computational interpretation. From a *classical* point of view, it is
more fruitful to maintain a separation of concerns: we can use one
language and body of methods to write computer programs, while
maintaining the freedom to use nonconstructive theories and methods
to reason about them. Lean is designed to support both of these

오늘날에도 계산이 수학에 중요하다는 것에 대해 상당히 일관된 합의가 있습니다. 그러나 계산적 우려를 어떻게 가장 잘 해결할 것인지에 대해서는 다양한 견해가 있습니다. *구성주의적* 관점에서, 수학을 계산적 근원으로부터 분리하는 것은 실수입니다. 모든 의미 있는 수학적 정리는 직접적인 계산적 해석을 가져야 합니다. *고전적* 관점에서, 관심사의 분리를 유지하는 것이 더 열매 있습니다: 우리는 컴퓨터 프로그램을 작성하기 위해 하나의 언어와 방법 체계를 사용할 수 있고, 동시에 그것을 추론하기 위해 비구성적 이론과 방법을 사용할 자유를 유지할 수 있습니다. Lean은 이 두 가지를 모두 지원하도록 설계되었습니다

두 가지 접근법을 모두 지원합니다. 라이브러리의 핵심 부분은 구성주의적으로 개발되지만, 시스템은 또한 고전적 수학적 추론을 수행할 수 있도록 지원합니다.

Computationally, the purest part of dependent type theory avoids the
use of `Prop` entirely. Inductive types and dependent function types
can be viewed as data types, and terms of these types can be
“evaluated” by applying reduction rules until no more rules can be
applied. In principle, any closed term (that is, term with no free
variables) of type `Nat` should evaluate to a numeral, `succ (… (succ zero)…)`.

계산적으로, 종속 타입 이론의 가장 순수한 부분은 `Prop`의 사용을 완전히 피합니다. 귀납적 타입과 종속 함수 타입은 데이터 타입으로 볼 수 있으며, 이러한 타입의 항은 더 이상 규칙을 적용할 수 없을 때까지 감소 규칙을 적용하여 “평가”될 수 있습니다. 원칙적으로, `Nat` 타입의 모든 닫힌 항(즉, 자유 변수가 없는 항)은 숫자 `succ (… (succ zero)…)`로 평가되어야 합니다.

Introducing a proof-irrelevant `Prop` and marking theorems
irreducible represents a first step towards separation of
concerns. The intention is that elements of a type `p : Prop` should
play no role in computation, and so the particular construction of a
term `prf : p` is “irrelevant” in that sense. One can still define
computational objects that incorporate elements of type `Prop`; the
point is that these elements can help us reason about the effects of
the computation, but can be ignored when we extract “code” from the
term. Elements of type `Prop` are not entirely innocuous,
however. They include equations `s = t : α` for any type `α`, and
such equations can be used as casts, to type check terms. Below, we
will see examples of how such casts can block computation in the
system. However, computation is still possible under an evaluation
scheme that erases propositional content, ignores intermediate typing
constraints, and reduces terms until they reach a normal form. This is
precisely what Lean's virtual machine does.

증명 무관한 `Prop`을 도입하고 정리를 축약 불가능하게 표시하는 것은 관심사의 분리를 향한 첫 번째 단계를 나타냅니다. 의도는 `p : Prop` 타입의 요소가 계산에서 아무 역할도 하지 않아야 하며, 그래서 항 `prf : p`의 특정 구성이 그 의미에서 “무관하다”는 것입니다. 여전히 `Prop` 타입의 요소를 포함하는 계산 객체를 정의할 수 있습니다. 요점은 이러한 요소가 계산의 효과에 대해 추론하는 데 도움이 될 수 있지만, 항으로부터 “코드”를 추출할 때 무시될 수 있다는 것입니다. 그러나 `Prop` 타입의 요소는 완전히 무해하지는 않습니다. 여기에는 모든 타입 `α`에 대한 방정식 `s = t : α`가 포함되며, 이러한 방정식은 항을 타입 체크하기 위해 캐스트로 사용될 수 있습니다. 아래에서 이러한 캐스트가 시스템에서 계산을 어떻게 차단할 수 있는지의 예를 볼 것입니다. 그러나 명제적 내용을 지우고, 중간 타입 제약을 무시하고, 항이 정규 형식에 도달할 때까지 감소시키는 평가 체계 하에서는 여전히 계산이 가능합니다. 이것이 정확히 Lean의 가상 머신이 하는 것입니다.

Having adopted a proof-irrelevant `Prop`, one might consider it
legitimate to use, for example, the law of the excluded middle,
`p ∨ ¬p`, where `p` is any proposition. Of course, this, too, can block
computation according to the rules of CIC, but it does not prevent the generation
of executable code, as described above. It is only the choice
principles discussed in [the section on choice](#choice) that completely erase the
distinction between the proof-irrelevant and data-relevant parts of
the theory.

증명 무관한 `Prop`을 채택한 후, 예를 들어 배제된 중간의 법칙 `p ∨ ¬p`를 사용하는 것이 합법적이라고 생각할 수 있습니다. 여기서 `p`는 어떤 명제입니다. 물론, 이것도 CIC의 규칙에 따라 계산을 차단할 수 있지만, 위에서 설명한 대로 실행 가능한 코드의 생성을 방지하지는 않습니다. [선택에 관한 섹션](#choice)에서 논의된 선택 원리만이 이론의 증명 무관한 부분과 증명 관련 부분 간의 구별을 완전히 지웁니다.

## 12.2. Propositional Extensionality

Propositional extensionality is the following axiom:

```
axiom propext {a b : Prop} : (a ↔ b) → a = b
```

It asserts that when two propositions imply one another, they are
actually equal. This is consistent with set-theoretic interpretations
in which any element `a : Prop` is either empty or the singleton set
`\{\ast\}`, for some distinguished element `\ast`. The axiom has the
effect that equivalent propositions can be substituted for one another
in any context:

명제적 확장성은 다음 공리입니다:

이것은 두 명제가 서로를 함축할 때 실제로 같다고 주장합니다. 이는 모든 요소 `a : Prop`이 비어있거나 일부 구별된 요소 `\ast`에 대한 싱글톤 집합 `\{\ast\}`인 집합 이론적 해석과 일치합니다. 이 공리의 효과는 동치 명제가 어떤 문맥에서도 서로 대체될 수 있다는 것입니다:

```
variable (a b c d e : Prop)
theorem thm₁ (h : a ↔ b) : (c ∧ a ∧ d → e) ↔ (c ∧ b ∧ d → e) :=
propext h ▸ Iff.refl _
theorem thm₂ (p : Prop → Prop) (h : a ↔ b) (h₁ : p a) : p b :=
propext h ▸ h₁
```

## 12.3. Function Extensionality

Similar to propositional extensionality, function extensionality
asserts that any two functions of type `(x : α) → β x` that agree on
all their inputs are equal:

```
funext.{u, v}
{α : Sort u} {β : α → Sort v}
{f g : (x : α) → β x}
(h : ∀ (x : α), f x = g x) :
f = g
```

From a classical, set-theoretic perspective, this is exactly what it
means for two functions to be equal. This is known as an “extensional”
view of functions. From a constructive perspective, however, it is
sometimes more natural to think of functions as algorithms, or
computer programs, that are presented in some explicit way. It is
certainly the case that two computer programs can compute the same
answer for every input despite the fact that they are syntactically
quite different. In much the same way, you might want to maintain a
view of functions that does not force you to identify two functions
that have the same input / output behavior. This is known as an
“intensional” view of functions.

고전적 집합 이론적 관점에서, 이것은 정확히 두 함수가 같다는 것을 의미하는 것입니다. 이것은 함수의 “외연적” 관점으로 알려져 있습니다. 그러나 구성주의적 관점에서는, 때때로 함수를 어떤 명시적인 방식으로 제시된 알고리즘 또는 컴퓨터 프로그램으로 생각하는 것이 더 자연스럽습니다. 두 컴퓨터 프로그램이 구문적으로 매우 다르다는 사실에도 불구하고 모든 입력에 대해 동일한 답을 계산할 수 있다는 것은 확실히 있는 경우입니다. 마찬가지 방식으로, 같은 입출력 행동을 가진 두 함수를 식별하도록 강요하지 않는 함수의 관점을 유지하기를 원할 수 있습니다. 이것은 함수의 “내연적” 관점으로 알려져 있습니다.

In fact, function extensionality follows from the existence of
quotients, which we describe in the next section. In the Lean standard
library, therefore, `funext` is thus
[proved from the quotient construction](https://github.com/leanprover/lean4/blob/master/src/Init/Core.lean).

Suppose that for `α : Type u` we define the `Set ``α``:= α → Prop` to denote the type of subsets of `α`, essentially identifying subsets with predicates. By combining `funext` and `propext`, we obtain an extensional theory of such sets:

실제로, 함수적 확장성은 다음 섹션에서 설명하는 몫의 존재로부터 따릅니다. 따라서 Lean 표준 라이브러리에서 `funext`는 [몫 구성으로부터 증명됩니다](https://github.com/leanprover/lean4/blob/master/src/Init/Core.lean).

`α : Type u`에 대해 `Set` `α``:= α → Prop`을 정의하여 `α`의 부분집합의 타입을 나타낸다고 가정합시다. 본질적으로 부분집합을 술어로 식별합니다. `funext`와 `propext`를 결합함으로써, 우리는 이러한 집합의 외연적 이론을 얻습니다:

```
def Set (α : Type u) := α → Prop
namespace Set
def mem (x : α) (a : Set α) := a x
infix:50 (priority := high) "∈" => mem
theorem setext {a b : Set α} (h : ∀ x, x ∈ a ↔ x ∈ b) : a = b :=
funext (fun x => propext (h x))
end Set
```

We can then proceed to define the empty set and set intersection, for
example, and prove set identities:

그러면 공집합과 집합 교집합을 정의하고, 예를 들어 집합 항등식을 증명할 수 있습니다:

```
def empty : Set α := fun _ => False
notation (priority := high) "∅" => empty
def inter (a b : Set α) : Set α :=
fun x => x ∈ a ∧ x ∈ b
infix:70 " ∩ " => inter
theorem inter_self (a : Set α) : a ∩ a = a :=
setext fun x => Iff.intro
(fun ⟨h, _⟩ => h)
(fun h => ⟨h, h⟩)
theorem inter_empty (a : Set α) : a ∩ ∅ = ∅ :=
setext fun _ => Iff.intro
(fun ⟨_, h⟩ => h)
(fun h => False.elim h)
theorem empty_inter (a : Set α) : ∅ ∩ a = ∅ :=
setext fun _ => Iff.intro
(fun ⟨h, _⟩ => h)
(fun h => False.elim h)
theorem inter.comm (a b : Set α) : a ∩ b = b ∩ a :=
setext fun _ => Iff.intro
(fun ⟨h₁, h₂⟩ => ⟨h₂, h₁⟩)
(fun ⟨h₁, h₂⟩ => ⟨h₂, h₁⟩)
```

The following is an example of how function extensionality blocks
computation inside the Lean kernel:

```
def f (x : Nat) := x
def g (x : Nat) := 0 + x
theorem f_eq_g : f = g :=
funext fun x => (Nat.zero_add x).symm
def val : Nat :=
Eq.recOn (motive := fun _ _ => Nat) f_eq_g 0
-- does not reduce to 0
#reduce val
```

```
f_eq_g ▸ 0
```

```
-- evaluates to 0
#eval val
```

```
0
```

First, we show that the two functions `f` and `g` are equal using
function extensionality, and then we cast `0` of type `Nat` by
replacing `f` by `g` in the type. Of course, the cast is
vacuous, because `Nat` does not depend on `f`. But that is enough
to do the damage: under the computational rules of the system, we now
have a closed term of `Nat` that does not reduce to a numeral. In this
case, we may be tempted to reduce the expression to `0`. But in
nontrivial examples, eliminating cast changes the type of the term,
which might make an ambient expression type incorrect. The virtual
machine, however, has no trouble evaluating the expression to
`0`. Here is a similarly contrived example that shows how
`propext` can get in the way:

다음은 함수적 확장성이 Lean 커널 내에서 계산을 어떻게 차단하는지의 예입니다:

먼저 함수적 확장성을 사용하여 두 함수 `f`와 `g`가 같음을 보이고, 그 다음 타입에서 `f`를 `g`로 바꾸어 `Nat` 타입의 `0`을 캐스트합니다. 물론, 캐스트는 공허합니다. 왜냐하면 `Nat`은 `f`에 의존하지 않기 때문입니다. 그러나 이것만으로도 충분합니다: 시스템의 계산 규칙에 따르면, 우리는 이제 숫자로 축약되지 않는 `Nat`의 닫힌 항을 가지고 있습니다. 이 경우, 우리는 식을 `0`으로 축약하고 싶을 수 있습니다. 그러나 중요한 예제에서는 캐스트를 제거하면 항의 타입이 변경되어, 주변 식의 타입이 정확하지 않을 수 있습니다. 그러나 가상 머신은 식을 `0`으로 평가하는 데 문제가 없습니다. `propext`가 방해가 될 수 있는 방법을 보여주는 비슷하게 인위적인 예가 있습니다:

```
theorem tteq : (True ∧ True) = True :=
propext (Iff.intro (fun ⟨h, _⟩ => h) (fun h => ⟨h, h⟩))
def val : Nat :=
Eq.recOn (motive := fun _ _ => Nat) tteq 0
-- does not reduce to 0
#reduce val
```

```
tteq ▸ 0
```

```
-- evaluates to 0
#eval val
```

```
0
```

Current research programs, including work on *observational type
theory* and *cubical type theory*, aim to extend type theory in ways
that permit reductions for casts involving function extensionality,
quotients, and more. But the solutions are not so clear-cut, and the
rules of Lean's underlying calculus do not sanction such reductions.

*관찰적 타입 이론*과 *입방형 타입 이론*에 대한 작업을 포함한 현재 연구 프로그램은 함수적 확장성, 몫, 그리고 더 많은 것을 포함하는 캐스트에 대한 축약을 허락하는 방식으로 타입 이론을 확장하는 것을 목표로 합니다. 그러나 해결책이 명확하지 않으며, Lean의 기본 계산법 규칙은 그러한 축약을 허락하지 않습니다.

In a sense, however, a cast does not change the meaning of an
expression. Rather, it is a mechanism to reason about the expression's
type. Given an appropriate semantics, it then makes sense to reduce
terms in ways that preserve their meaning, ignoring the intermediate
bookkeeping needed to make the reductions type-correct. In that case,
adding new axioms in `Prop` does not matter; by [proof irrelevance](../03-propositions-and-proofs/#--tech-term-proof-irrelevance),
an expression in `Prop` carries no information, and can be safely
ignored by the reduction procedures.

그러나 어떤 의미에서, 캐스트는 식의 의미를 변경하지 않습니다. 오히려, 그것은 식의 타입을 추론하기 위한 메커니즘입니다. 적절한 의미론이 주어지면, 축약이 타입 정확하게 하기 위해 필요한 중간 부기를 무시하면서, 그들의 의미를 보존하는 방식으로 항을 축약하는 것이 의미가 있습니다. 그 경우, `Prop`에 새로운 공리를 추가하는 것은 중요하지 않습니다. [증명 무관성](../03-propositions-and-proofs/#--tech-term-proof-irrelevance)에 의해, `Prop`의 식은 어떤 정보도 담지 않으며, 축약 절차에 의해 안전하게 무시될 수 있습니다.

## 12.4. Quotients

Let `α` be any type, and let `r` be an equivalence relation on
`α`. It is mathematically common to form the “quotient” `α / r`,
that is, the type of elements of `α` “modulo” `r`. Set
theoretically, one can view `α / r` as the set of equivalence
classes of `α` modulo `r`. If `f : α → β` is any function that
respects the equivalence relation in the sense that for every
`x y : α`, `r x y` implies `f x = f y`, then `f` “lifts” to a function
`f' : α / r → β` defined on each equivalence class `⟦x⟧` by
`f' ⟦x⟧ = f x`. Lean's standard library extends the Calculus of
Constructions with additional constants that perform exactly these
constructions, and installs this last equation as a definitional
reduction rule.

`α`를 어떤 타입이라고 하고, `r`을 `α` 위의 동치 관계라고 합시다. 수학적으로 “몫” `α / r`을 형성하는 것이 일반적입니다. 즉, `α`의 요소의 타입을 “모듈로” `r`입니다. 집합 이론적으로, 하나는 `α / r`을 모듈로 `r`에서 `α`의 동치 클래스의 집합으로 볼 수 있습니다. 만약 `f : α → β`가 모든 `x y : α`에 대해 `r x y`가 `f x = f y`를 함축하는 의미에서 동치 관계를 존중하는 함수라면, `f`는 각 동치 클래스 `⟦x⟧`에 대해 `f' ⟦x⟧ = f x`로 정의된 함수 `f' : α / r → β`로 “상승”됩니다. Lean의 표준 라이브러리는 정확히 이러한 구성을 수행하는 추가 상수로 구성 계산법을 확장하며, 이 마지막 방정식을 정의적 축약 규칙으로 설치합니다.

In its most basic form, the quotient construction does not even
require `r` to be an equivalence relation. The following constants
are built into Lean:

가장 기본적인 형태에서, 몫 구성은 `r`이 동치 관계일 필요도 없습니다. 다음의 상수들이 Lean에 내장되어 있습니다:

```
universe u v
axiom Quot : {α : Sort u} → (α → α → Prop) → Sort u
axiom Quot.mk : {α : Sort u} → (r : α → α → Prop) → α → Quot r
axiom Quot.ind :
∀ {α : Sort u} {r : α → α → Prop} {β : Quot r → Prop},
(∀ a, β (Quot.mk r a)) → (q : Quot r) → β q
axiom Quot.lift :
{α : Sort u} → {r : α → α → Prop} → {β : Sort u} → (f : α → β)
→ (∀ a b, r a b → f a = f b) → Quot r → β
```

The first one forms a type `Quot r` given a type `α` by any binary
relation `r` on `α`. The second maps `α` to `Quot α`, so that
if `r : α → α → Prop` and `a : α`, then `Quot.mk r a` is an
element of `Quot r`. The third principle, `Quot.ind`, says that
every element of `Quot.mk r a` is of this form. As for
`Quot.lift`, given a function `f : α → β`, if `h` is a proof
that `f` respects the relation `r`, then `Quot.lift f h` is the
corresponding function on `Quot r`. The idea is that for each
element `a` in `α`, the function `Quot.lift f h` maps
`Quot.mk r a` (the `r`-class containing `a`) to `f a`, wherein `h`
shows that this function is well defined. In fact, the computation
principle is declared as a reduction rule, as the proof below makes
clear.

첫 번째는 `α` 위의 어떤 이진 관계 `r`에 의해 주어진 타입 `α`로부터 타입 `Quot r`을 형성합니다. 두 번째는 `α`를 `Quot α`로 매핑하므로, `r : α → α → Prop`이고 `a : α`이면 `Quot.mk r a`는 `Quot r`의 요소입니다. 세 번째 원리인 `Quot.ind`는 `Quot.mk r a`의 모든 요소가 이 형태임을 말합니다. `Quot.lift`에 대해서는, 함수 `f : α → β`가 주어지고, `h`가 `f`가 관계 `r`을 존중한다는 증명이라면, `Quot.lift f h`는 `Quot r` 위의 해당 함수입니다. 아이디어는 `α`의 각 요소 `a`에 대해, 함수 `Quot.lift f h`가 `Quot.mk r a`(`a`를 포함하는 `r`-클래스)를 `f a`로 매핑한다는 것이며, `h`는 이 함수가 잘 정의되어 있음을 보여줍니다. 실제로, 계산 원리는 축약 규칙으로 선언되며, 아래 증명이 명확하게 합니다.

```
def mod7Rel (x y : Nat) : Prop :=
x % 7 = y % 7
-- the quotient type
#check (Quot mod7Rel : Type)
```

```
Quot mod7Rel : Type
```

```
-- the class of numbers equivalent to 4
#check (Quot.mk mod7Rel 4 : Quot mod7Rel)
```

```
Quot.mk mod7Rel 4 : Quot mod7Rel
```

```
def f (x : Nat) : Bool :=
x % 7 = 0
theorem f_respects (a b : Nat) (h : mod7Rel a b) : f a = f b := by
simp [mod7Rel, f] at *
rw [h]
#check (Quot.lift f f_respects : Quot mod7Rel → Bool)
```

```
Quot.lift f f_respects : Quot mod7Rel → Bool
```

```
-- the computation principle
example (a : Nat) : Quot.lift f f_respects (Quot.mk mod7Rel a) = f a :=
rfl
```

The four constants, `Quot`, `Quot.mk`, `Quot.ind`, and
`Quot.lift` in and of themselves are not very strong. You can check
that the `Quot.ind` is satisfied if we take `Quot r` to be simply
`α`, and take `Quot.lift` to be the identity function (ignoring
`h`). For that reason, these four constants are not viewed as
additional axioms.

They are, like inductively defined types and the associated
constructors and recursors, viewed as part of the logical framework.

네 상수 `Quot`, `Quot.mk`, `Quot.ind`, 그리고 `Quot.lift`는 그 자체로는 매우 강력하지 않습니다. `Quot r`을 단순히 `α`로 취하고, `Quot.lift`를 항등 함수(`h`를 무시하고)로 취하면 `Quot.ind`가 만족됨을 확인할 수 있습니다. 그 이유로, 이 네 상수는 추가 공리로 보여지지 않습니다.

그들은 귀납적으로 정의된 타입 및 관련 생성자와 재귀자처럼, 논리적 프레임워크의 일부로 보여집니다.

What makes the `Quot` construction into a bona fide quotient is the
following additional axiom:

```
axiom Quot.sound :
∀ {α : Type u} {r : α → α → Prop} {a b : α},
r a b → Quot.mk r a = Quot.mk r b
```

This is the axiom that asserts that any two elements of `α` that are
related by `r` become identified in the quotient. If a theorem or
definition makes use of `Quot.sound`, it will show up in the
`#print axioms` command.

`Quot` 구성을 정당한 몫으로 만드는 것은 다음 추가 공리입니다:

이것은 `α`의 `r`과 관련된 모든 두 요소가 몫에서 식별된다고 주장하는 공리입니다. 정리나 정의가 `Quot.sound`를 사용하면, `#print axioms` 명령에 나타날 것입니다.

Of course, the quotient construction is most commonly used in
situations when `r` is an equivalence relation. Given `r` as
above, if we define `r'` according to the rule `r' a b` iff
`Quot.mk r a = Quot.mk r b`, then it's clear that `r'` is an
equivalence relation. Indeed, `r'` is the *kernel* of the function
`fun a => Quot.mk r a`. The axiom `Quot.sound` says that `r a b`
implies `r' a b`. Using `Quot.lift` and `Quot.ind`, we can show
that `r'` is the smallest equivalence relation containing `r`, in
the sense that if `r''` is any equivalence relation containing
`r`, then `r' a b` implies `r'' a b`. In particular, if `r`
was an equivalence relation to start with, then for all `a` and
`b` we have `r a b` iff `r' a b`.

물론, 몫 구성은 `r`이 동치 관계인 상황에서 가장 일반적으로 사용됩니다. 위와 같이 `r`이 주어지면, `r' a b` iff `Quot.mk r a = Quot.mk r b`라는 규칙에 따라 `r'`를 정의하면, `r'`이 동치 관계임은 명확합니다. 실제로, `r'`은 함수 `fun a => Quot.mk r a`의 *커널*입니다. 공리 `Quot.sound`는 `r a b`가 `r' a b`를 함축한다고 말합니다. `Quot.lift`와 `Quot.ind`를 사용하여, `r'`이 `r`을 포함하는 가장 작은 동치 관계임을 보일 수 있습니다. 즉, `r''`이 `r`을 포함하는 어떤 동치 관계라면, `r' a b`는 `r'' a b`를 함축한다는 의미에서입니다. 특히, `r`이 처음부터 동치 관계였다면, 모든 `a`와 `b`에 대해 `r a b` iff `r' a b`입니다.

To support this common use case, the standard library defines the
notion of a *setoid*, which is simply a type with an associated
equivalence relation:

이 공통적인 사용 사례를 지원하기 위해, 표준 라이브러리는 *setoid*의 개념을 정의하며, 이는 단순히 연관된 동치 관계가 있는 타입입니다:

```
class Setoid (α : Sort u) where
r : α → α → Prop
iseqv : Equivalence r
instance {α : Sort u} [Setoid α] : HasEquiv α :=
⟨Setoid.r⟩
namespace Setoid
variable {α : Sort u} [Setoid α]
theorem refl (a : α) : a ≈ a :=
iseqv.refl a
theorem symm {a b : α} (hab : a ≈ b) : b ≈ a :=
iseqv.symm hab
theorem trans {a b c : α} (hab : a ≈ b) (hbc : b ≈ c) : a ≈ c :=
iseqv.trans hab hbc
end Setoid
```

Given a type `α`, a relation `r`
on `α`, and a proof `iseqv`
that `r` is an equivalence relation, we can define an
instance of the `Setoid` class.

```
def Quotient {α : Sort u} (s : Setoid α) :=
@Quot α Setoid.r
```

The constants `Quotient.mk`, `Quotient.ind`, `Quotient.lift`,
and `Quotient.sound` are nothing more than the specializations of
the corresponding elements of `Quot`. The fact that type class
inference can find the setoid associated to a type `α` brings a
number of benefits. First, we can use the notation `a ≈ b` (entered
with `\approx`) for `Setoid.r a b`, where the instance of
`Setoid` is implicit in the notation `Setoid.r`. We can use the
generic theorems `Setoid.refl`, `Setoid.symm`, `Setoid.trans` to
reason about the relation. Specifically with quotients we can use the
theorem `Quotient.exact`:

상수 `Quotient.mk`, `Quotient.ind`, `Quotient.lift`, 그리고 `Quotient.sound`는 `Quot`의 해당 요소의 특수화에 지나지 않습니다. 타입 클래스 추론이 타입 `α`와 연결된 setoid를 찾을 수 있다는 사실은 많은 이점을 가져옵니다. 먼저, `Setoid.r a b`에 대한 표기법 `a ≈ b`(`\approx`로 입력됨)를 사용할 수 있으며, 여기서 `Setoid`의 인스턴스는 표기법 `Setoid.r`에서 암묵적입니다. 관계에 대해 추론하기 위해 일반 정리 `Setoid.refl`, `Setoid.symm`, `Setoid.trans`를 사용할 수 있습니다. 특히 몫과 함께, 정리 `Quotient.exact`를 사용할 수 있습니다:

```
Quotient.exact {α : Sort u} {s : Setoid α} {a b : α} :
Quotient.mk s a = Quotient.mk s b →
a ≈ b
```

Together with `Quotient.sound`, this implies that the elements of
the quotient correspond exactly to the equivalence classes of elements
in `α`.

Recall that in the standard library, `α × β` represents the
Cartesian product of the types `α` and `β`. To illustrate the use
of quotients, let us define the type of *unordered* pairs of elements
of a type `α` as a quotient of the type `α × α`. First, we define
the relevant equivalence relation:

`Quotient.sound`과 함께, 이것은 몫의 요소가 정확히 `α`의 요소의 동치 클래스에 대응함을 함축합니다.

표준 라이브러리에서 `α × β`는 타입 `α`와 `β`의 데카르트 곱을 나타냅니다. 몫의 사용을 설명하기 위해, 타입 `α`의 요소의 *순서 없는* 쌍의 타입을 타입 `α × α`의 몫으로 정의해봅시다. 먼저, 관련된 동치 관계를 정의합니다:

```
private def eqv (p₁ p₂ : α × α) : Prop :=
(p₁.1 = p₂.1 ∧ p₁.2 = p₂.2) ∨ (p₁.1 = p₂.2 ∧ p₁.2 = p₂.1)
infix:50 " ~ " => eqv
```

The next step is to prove that `eqv` is in fact an equivalence
relation, which is to say, it is reflexive, symmetric and
transitive. We can prove these three facts in a convenient and
readable way by using dependent pattern matching to perform
case-analysis and break the hypotheses into pieces that are then
reassembled to produce the conclusion.

다음 단계는 `eqv`가 실제로 동치 관계임을 증명하는 것입니다. 즉, 그것은 반사적, 대칭적, 그리고 추이적입니다. 종속 패턴 매칭을 사용하여 사례 분석을 수행하고 가설을 조각으로 분해한 다음 결론을 생성하기 위해 재조립함으로써 이 세 가지 사실을 편리하고 읽기 쉬운 방식으로 증명할 수 있습니다.

```
private theorem eqv.refl (p : α × α) : p ~ p :=
Or.inl ⟨rfl, rfl⟩
private theorem eqv.symm : ∀ {p₁ p₂ : α × α}, p₁ ~ p₂ → p₂ ~ p₁
| (a₁, a₂), (b₁, b₂), (Or.inl ⟨a₁b₁, a₂b₂⟩) =>
Or.inl (by simp_all)
| (a₁, a₂), (b₁, b₂), (Or.inr ⟨a₁b₂, a₂b₁⟩) =>
Or.inr (by simp_all)
private theorem eqv.trans : ∀ {p₁ p₂ p₃ : α × α}, p₁ ~ p₂ → p₂ ~ p₃ → p₁ ~ p₃
| (a₁, a₂), (b₁, b₂), (c₁, c₂), Or.inl ⟨a₁b₁, a₂b₂⟩, Or.inl ⟨b₁c₁, b₂c₂⟩ =>
Or.inl (by simp_all)
| (a₁, a₂), (b₁, b₂), (c₁, c₂), Or.inl ⟨a₁b₁, a₂b₂⟩, Or.inr ⟨b₁c₂, b₂c₁⟩ =>
Or.inr (by simp_all)
| (a₁, a₂), (b₁, b₂), (c₁, c₂), Or.inr ⟨a₁b₂, a₂b₁⟩, Or.inl ⟨b₁c₁, b₂c₂⟩ =>
Or.inr (by simp_all)
| (a₁, a₂), (b₁, b₂), (c₁, c₂), Or.inr ⟨a₁b₂, a₂b₁⟩, Or.inr ⟨b₁c₂, b₂c₁⟩ =>
Or.inl (by simp_all)
private theorem is_equivalence : Equivalence (@eqv α) :=
{ refl := eqv.refl, symm := eqv.symm, trans := eqv.trans }
```

Now that we have proved that `eqv` is an equivalence relation, we
can construct a `Setoid (α × α)`, and use it to define the type
`UProd α` of unordered pairs.

이제 `eqv`가 동치 관계임을 증명했으므로, `Setoid (α × α)`를 구성하고 이를 사용하여 순서 없는 쌍의 타입 `UProd α`를 정의할 수 있습니다.

```
instance uprodSetoid (α : Type u) : Setoid (α × α) where
r := eqv
iseqv := is_equivalence
def UProd (α : Type u) : Type u :=
Quotient (uprodSetoid α)
namespace UProd
def mk {α : Type} (a₁ a₂ : α) : UProd α :=
Quotient.mk' (a₁, a₂)
notation "{ " a₁ ", " a₂ " }" => mk a₁ a₂
end UProd
```

Notice that we locally define the notation `{a₁, a₂}` for unordered
pairs as `Quotient.mk' (a₁, a₂)`. This is useful for illustrative
purposes, but it is not a good idea in general, since the notation
will shadow other uses of curly brackets, such as for records and
sets.

We can easily prove that `{a₁, a₂} = {a₂, a₁}` using `Quot.sound`,
since we have `(a₁, a₂) ~ (a₂, a₁)`.

순서 없는 쌍에 대한 표기법 `{a₁, a₂}`를 `Quotient.mk' (a₁, a₂)`로 지역적으로 정의함을 주목하세요. 이것은 설명 목적에는 유용하지만, 일반적으로는 좋은 아이디어가 아닙니다. 왜냐하면 표기법은 레코드와 집합과 같은 중괄호의 다른 사용을 가립니다.

`(a₁, a₂) ~ (a₂, a₁)`을 가지고 있으므로 `Quot.sound`를 사용하여 `{a₁, a₂} = {a₂, a₁}`을 쉽게 증명할 수 있습니다.

```
theorem mk_eq_mk (a₁ a₂ : α) : {a₁, a₂} = {a₂, a₁} :=
Quot.sound (Or.inr ⟨rfl, rfl⟩)
```

To complete the example, given `a : α` and `u : UProd α`, we
define the proposition `a` `∈` `u` which should hold if `a` is one of
the elements of the unordered pair `u`. First, we define a similar
proposition `mem_fn a u` on (ordered) pairs; then we show that
`mem_fn` respects the equivalence relation `eqv` with the lemma
`mem_respects`. This is an idiom that is used extensively in the
Lean standard library.

예제를 완성하기 위해, `a : α`와 `u : UProd α`가 주어지면, 명제 `a` `∈` `u`를 정의합니다. 이는 `a`가 순서 없는 쌍 `u`의 요소 중 하나인 경우에 성립해야 합니다. 먼저, (순서가 있는) 쌍에 대해 유사한 명제 `mem_fn a u`를 정의합니다. 그 다음 보조정리 `mem_respects`를 사용하여 `mem_fn`이 동치 관계 `eqv`를 존중함을 보입니다. 이것은 Lean 표준 라이브러리에서 광범위하게 사용되는 관용구입니다.

```
private def mem_fn (a : α) : α × α → Prop
| (a₁, a₂) => a = a₁ ∨ a = a₂
-- auxiliary lemma for proving mem_respects
private theorem mem_swap {a : α} :
∀ {p : α × α}, mem_fn a p = mem_fn a (⟨p.2, p.1⟩)
| (a₁, a₂) => by
apply propext
apply Iff.intro
. intro
| Or.inl h => exact Or.inr h
| Or.inr h => exact Or.inl h
. intro
| Or.inl h => exact Or.inr h
| Or.inr h => exact Or.inl h
private theorem mem_respects : {p₁ p₂ : α × α} → (a : α) → p₁ ~ p₂ → mem_fn a p₁ = mem_fn a p₂
| (a₁, a₂), (b₁, b₂), a, Or.inl ⟨a₁b₁, a₂b₂⟩ => by
simp_all
| (a₁, a₂), (b₁, b₂), a, Or.inr ⟨a₁b₂, a₂b₁⟩ => by
simp_all only
apply mem_swap
def mem (a : α) (u : UProd α) : Prop :=
Quot.liftOn u (fun p => mem_fn a p) (fun p₁ p₂ e => mem_respects a e)
infix:50 (priority := high) " ∈ " => mem
theorem mem_mk_left (a b : α) : a ∈ {a, b} :=
Or.inl rfl
theorem mem_mk_right (a b : α) : b ∈ {a, b} :=
Or.inr rfl
theorem mem_or_mem_of_mem_mk {a b c : α} : c ∈ {a, b} → c = a ∨ c = b :=
fun h => h
```

For convenience, the standard library also defines `Quotient.lift₂`
for lifting binary functions, and `Quotient.ind₂` for induction on
two variables.

편의를 위해, 표준 라이브러리는 이진 함수를 상승시키기 위한 `Quotient.lift₂`와 두 변수에 대한 귀납법을 위한 `Quotient.ind₂`도 정의합니다.

We close this section with some hints as to why the quotient
construction implies function extensionality. It is not hard to show
that extensional equality on the `(x : α) → β x` is an equivalence
relation, and so we can consider the type `extfun α β` of functions
“up to equivalence.” Of course, application respects that equivalence
in the sense that if `f₁` is equivalent to `f₂`, then `f₁ a` is
equal to `f₂ a`. Thus application gives rise to a function
`extfun_app : extfun α β → (x : α) → β x`. But for every `f`,
`extfun_app (.mk _ f)` is definitionally equal to `fun x => f x`, which is
in turn definitionally equal to `f`. So, when `f₁` and `f₂` are
extensionally equal, we have the following chain of equalities:

```
example (f₁ f₂ : (x : α) → β x) (h : ∀ x, f₁ x = f₂ x) :=
calc f₁
_ = extfun_app (.mk _ f₁) := rfl
_ = extfun_app (.mk _ f₂) := by rw [Quot.sound]; trivial
_ = f₂ := rfl
```

As a result, `f₁` is equal to `f₂`.

이 섹션을 마치기 위해 몫 구성이 함수적 확장성을 함축하는 이유에 대해 몇 가지 힌트를 제공합니다. `(x : α) → β x`에서 외연적 동치성이 동치 관계임을 보이는 것은 어렵지 않으며, 따라서 함수의 타입 `extfun α β`를 “동치까지” 고려할 수 있습니다. 물론, 응용은 그 동치성을 존중합니다. 즉, `f₁`이 `f₂`와 동치라면, `f₁ a`는 `f₂ a`와 같습니다. 따라서 응용은 함수 `extfun_app : extfun α β → (x : α) → β x`를 일으킵니다. 그러나 모든 `f`에 대해, `extfun_app (.mk _ f)`는 `fun x => f x`와 정의적으로 같으며, 이는 다시 정의적으로 `f`와 같습니다. 따라서 `f₁`과 `f₂`가 외연적으로 같을 때, 우리는 다음의 같음의 연쇄를 가집니다:

결과적으로, `f₁`은 `f₂`와 같습니다.

## 12.5. Choice

To state the final axiom defined in the standard library, we need the
`Nonempty` type, which is defined as follows:

```
class inductive Nonempty (α : Sort u) : Prop where
| intro (val : α) : Nonempty α
```

Because `Nonempty α` has type `Prop` and its constructor contains data, it can only eliminate to `Prop`.
In fact, `Nonempty α` is equivalent to `∃ x : α, True`:

표준 라이브러리에 정의된 최종 공리를 표현하기 위해, `Nonempty` 타입이 필요하며, 다음과 같이 정의됩니다:

`Nonempty α`는 `Prop` 타입을 가지고 있고 그 생성자는 데이터를 포함하므로, `Prop`으로만 제거할 수 있습니다. 실제로, `Nonempty α`는 `∃ x : α, True`와 동치입니다:

```
example (α : Type u) : Nonempty α ↔ ∃ x : α, True :=
Iff.intro (fun ⟨a⟩ => ⟨a, trivial⟩) (fun ⟨a, h⟩ => ⟨a⟩)
```

Our axiom of choice is now expressed simply as follows:

```
axiom choice {α : Sort u} : Nonempty α → α
```

Given only the assertion `h` that `α` is nonempty, `choice h`
magically produces an element of `α`. Of course, this blocks any
meaningful computation: by the interpretation of `Prop`, `h`
contains no information at all as to how to find such an element.

우리의 선택 공리는 이제 다음과 같이 간단하게 표현됩니다:

`α`가 공집합이 아니라는 주장 `h`만 주어지면, `choice h`는 마술처럼 `α`의 요소를 생성합니다. 물론, 이것은 어떤 의미 있는 계산도 차단합니다: `Prop`의 해석에 의해, `h`는 그러한 요소를 찾는 방법에 대한 정보를 전혀 포함하지 않습니다.

This is found in the `Classical` namespace, so the full name of the
theorem is `Classical.choice`. The choice principle is equivalent to
the principle of **indefinite description**, which can be expressed with
subtypes as follows:

이것은 `Classical` 네임스페이스에서 찾을 수 있으므로, 정리의 전체 이름은 `Classical.choice`입니다. 선택 원리는 **부정확한 설명**(indefinite description)의 원리와 동치이며, 다음과 같이 부분 타입으로 표현될 수 있습니다:

```
noncomputable def indefiniteDescription {α : Sort u}
(p : α → Prop) (h : ∃ x, p x) : {x // p x} :=
choice <| let ⟨x, px⟩ := h; ⟨⟨x, px⟩⟩
```

Because it depends on `choice`, Lean cannot generate executable code for
`indefiniteDescription`, and so requires us to mark the definition
as `noncomputable`. Also in the `Classical` namespace, the
function `choose` and the property `choose_spec` decompose the two
parts of the output of `indefiniteDescription`:

`indefiniteDescription`에 의존하기 때문에, Lean은 `indefiniteDescription`에 대해 실행 가능한 코드를 생성할 수 없으며, 따라서 정의를 `noncomputable`로 표시할 것을 요구합니다. 또한 `Classical` 네임스페이스에서, 함수 `choose`와 속성 `choose_spec`은 `indefiniteDescription`의 출력의 두 부분을 분해합니다:

```
variable {α : Sort u} {p : α → Prop}
noncomputable def choose (h : ∃ x, p x) : α :=
(indefiniteDescription p h).val
theorem choose_spec (h : ∃ x, p x) : p (choose h) :=
(indefiniteDescription p h).property
```

The `choice` principle also erases the distinction between the
property of being `Nonempty` and the more constructive property of
being `Inhabited`:

`choice` 원리는 또한 `Nonempty`인 속성과 더 구성주의적인 `Inhabited` 속성 사이의 구별을 지웁니다:

```
noncomputable def inhabited_of_nonempty (h : Nonempty α) : Inhabited α :=
choice (let ⟨a⟩ := h; ⟨⟨a⟩⟩)
```

In the next section, we will see that `propext`, `funext`, and
`choice`, taken together, imply the law of the excluded middle and
the decidability of all propositions. Using those, one can strengthen
the principle of indefinite description as follows:

다음 섹션에서, 우리는 `propext`, `funext`, 그리고 `choice`를 함께 취하면 배제된 중간의 법칙과 모든 명제의 결정가능성을 함축함을 보게 됩니다. 그것들을 사용하여, 부정확한 설명의 원리를 다음과 같이 강화할 수 있습니다:

```
strongIndefiniteDescription {α : Sort u} (p : α → Prop)
(h : Nonempty α) :
{x // (∃ (y : α), p y) → p x}
```

Assuming the ambient type `α` is nonempty,
`strongIndefiniteDescription p` produces an element of `α`
satisfying `p` if there is one. The data component of this
definition is conventionally known as **Hilbert's epsilon function**:

주변 타입 `α`가 공집합이 아니라고 가정하면, `strongIndefiniteDescription p`는 `α`의 요소를 생성합니다. 이 정의의 데이터 구성 요소는 관례적으로 **힐베르트의 엡실론 함수**(Hilbert's epsilon function)로 알려져 있습니다:

```
epsilon {α : Sort u} [h : Nonempty α] (p : α → Prop) : α
```

```
epsilon_spec {α : Sort u} {p : α → Prop}
(hex : ∃ (y : α), p y) :
p (@epsilon _ (nonempty_of_exists hex) p)
```

## 12.6. The Law of the Excluded Middle

The law of the excluded middle is the following:

```
Classical.em : ∀ (p : Prop), p ∨ ¬p
```

[Diaconescu's theorem](https://en.wikipedia.org/wiki/Diaconescu%27s_theorem) states
that the axiom of choice is sufficient to derive the law of excluded
middle. More precisely, it shows that the law of the excluded middle
follows from `Classical.choice`, `propext`, and `funext`. We
sketch the proof that is found in the standard library.

배제된 중간의 법칙은 다음과 같습니다:

[디아코네스쿠 정리](https://en.wikipedia.org/wiki/Diaconescu%27s_theorem)는 선택 공리가 배제된 중간의 법칙을 유도하기에 충분함을 말합니다. 더 정확하게, 배제된 중간의 법칙이 `Classical.choice`, `propext`, 그리고 `funext`로부터 따름을 보입니다. 우리는 표준 라이브러리에서 찾을 수 있는 증명의 개요를 스케치합니다.

First, we import the necessary axioms, and define two predicates `U` and `V`:

```
open Classical
theorem em (p : Prop) : p ∨ ¬p := by
let U (x : Prop) : Prop := x = True ∨ p
let V (x : Prop) : Prop := x = False ∨ p
have exU : ∃ x, U x := ⟨True, Or.inl rfl⟩
have exV : ∃ x, V x := ⟨False, Or.inl rfl⟩
```

If `p` is true, then every element of `Prop` is in both `U` and `V`.
If `p` is false, then `U` is the singleton `True`, and `V` is the singleton `False`.

Next, we use `choose` to choose an element from each of `U` and `V`:

```
let u : Prop := choose exU
let v : Prop := choose exV
have u_def : U u := choose_spec exU
have v_def : V v := choose_spec exV
```

Each of `U` and `V` is a disjunction, so `u_def` and `v_def`
represent four cases. In one of these cases, `u = True` and
`v = False`, and in all the other cases, `p` is true. Thus we have:

먼저, 필요한 공리를 가져오고, 두 술어 `U`와 `V`를 정의합니다:

`p`가 참이면, `Prop`의 모든 요소가 `U`와 `V` 모두에 있습니다.

`p`가 거짓이면, `U`는 싱글톤 `True`이고, `V`는 싱글톤 `False`입니다.

다음으로, 우리는 `choose`를 사용하여 `U`와 `V` 각각에서 요소를 선택합니다:

`U`와 `V` 각각은 분리합이므로, `u_def`와 `v_def`는 네 가지 경우를 나타냅니다. 이 경우 중 하나에서 `u = True`이고 `v = False`이며, 다른 모든 경우에서 `p`는 참입니다. 따라서 우리는 다음을 가집니다:

```
have not_uv_or_p : u ≠ v ∨ p := by
match u_def, v_def with
| Or.inr h, _ => exact Or.inr h
| _, Or.inr h => exact Or.inr h
| Or.inl hut, Or.inl hvf =>
apply Or.inl
simp [hvf, hut, true_ne_false]
```

On the other hand, if `p` is true, then, by function extensionality
and propositional extensionality, `U` and `V` are equal. By the
definition of `u` and `v`, this implies that they are equal as well.

반면에, `p`가 참이면, 함수적 확장성과 명제적 확장성에 의해, `U`와 `V`는 같습니다. `u`와 `v`의 정의에 의해, 이것은 그들도 같음을 함축합니다.

```
have p_implies_uv : p → u = v :=
fun hp =>
have hpred : U = V :=
funext fun x =>
have hl : (x = True ∨ p) → (x = False ∨ p) :=
fun _ => Or.inr hp
have hr : (x = False ∨ p) → (x = True ∨ p) :=
fun _ => Or.inr hp
show (x = True ∨ p) = (x = False ∨ p) from
propext (Iff.intro hl hr)
have h₀ : ∀ exU exV, @choose _ U exU = @choose _ V exV := by
rw [hpred]; intros; rfl
show u = v from h₀ _ _
```

Putting these last two facts together yields the desired conclusion:

이 마지막 두 사실을 함께 놓으면 원하는 결론을 얻습니다:

```
match not_uv_or_p with
| Or.inl hne =>
exact Or.inr (mt p_implies_uv hne)
| Or.inr h =>
exact Or.inl h
```

Consequences of excluded middle include double-negation elimination,
proof by cases, and proof by contradiction, all of which are described
in the section on [classical logic](../03-propositions-and-proofs/#classical-logic).
The law of the excluded middle and propositional extensionality imply propositional completeness:

배제된 중간의 결론은 이중 부정 제거, 경우의 증명, 그리고 귀류법을 포함하며, 이들은 모두 [고전 논리](../03-propositions-and-proofs/#classical-logic)에 관한 섹션에서 설명됩니다. 배제된 중간의 법칙과 명제적 확장성은 명제 완전성을 함축합니다:

```
open Classical
theorem propComplete (a : Prop) : a = True ∨ a = False :=
match em a with
| Or.inl ha =>
Or.inl (propext (Iff.intro (fun _ => True.intro) (fun _ => ha)))
| Or.inr hn =>
Or.inr (propext (Iff.intro (fun h => hn h) (fun h => False.elim h)))
```

Together with choice, we also get the stronger principle that every
proposition is decidable. Recall that the class of `Decidable`
propositions is defined as follows:

선택과 함께, 우리는 또한 모든 명제가 결정가능하다는 더 강력한 원리를 얻습니다. `Decidable` 명제의 클래스가 다음과 같이 정의됨을 회상하세요:

```
class inductive Decidable (p : Prop) where
| isFalse (h : ¬p) : Decidable p
| isTrue (h : p) : Decidable p
```

In contrast to `p ∨ ¬ p`, which can only eliminate to `Prop`, the
type `Decidable p` is equivalent to the sum type `Sum p (¬ p)`, which
can eliminate to any type. It is this data that is needed to write an
if-then-else expression.

`p ∨ ¬ p`와 대조적으로, `Prop`으로만 제거할 수 있는 타입 `Decidable p`는 어떤 타입으로든 제거할 수 있는 합 타입 `Sum p (¬ p)`와 동치입니다. if-then-else 표현식을 쓰기 위해 필요한 데이터는 이것입니다.

As an example of classical reasoning, we use `choose` to show that if
`f : α → β` is injective and `α` is inhabited, then `f` has a
left inverse. To define the left inverse `linv`, we use a dependent
if-then-else expression. Recall that `if h : c then t else e` is
notation for `dite c (fun h : c => t) (fun h : ¬ c => e)`. In the definition
of `linv`, choice is used twice: first, to show that
`(∃ a : α, f a = b)` is “decidable,” and then to choose an `a` such that
`f a = b`. Notice that `propDecidable` is a scoped instance and is activated
by the `open Classical` command. We use this instance to justify
the `if`-`then`-`else` expression. (See also the discussion in
[Decidable Propositions](../10-type-classes/#decidable-propositions)).

고전적 추론의 예로서, 우리는 `choose`를 사용하여 `f : α → β`가 단사 함수이고 `α`가 inhabited 이면 `f`가 좌측 역함수를 가진다는 것을 보입니다. 좌측 역함수 `linv`를 정의하기 위해, 우리는 종속 if-then-else 표현식을 사용합니다. `if h : c then t else e`는 `dite c (fun h : c => t) (fun h : ¬ c => e)`에 대한 표기법임을 회상하세요. `linv`의 정의에서, 선택은 두 번 사용됩니다: 첫째, `(∃ a : α, f a = b)`가 “결정가능함”을 보이고, 둘째 `f a = b`인 `a`를 선택합니다. `propDecidable`이 범위가 지정된 인스턴스이며 `open Classical` 명령으로 활성화됨을 주목하세요. 우리는 이 인스턴스를 사용하여 `if`-`then`-`else` 표현식을 정당화합니다. ([결정가능 명제](../10-type-classes/#decidable-propositions)의 토론도 참조하세요).

```
open Classical
noncomputable def linv [Inhabited α] (f : α → β) : β → α :=
fun b : β => if ex : (∃ a : α, f a = b) then choose ex else default
theorem linv_comp_self {f : α → β} [Inhabited α]
(inj : ∀ {a b}, f a = f b → a = b)
: linv f ∘ f = id :=
funext fun a =>
have ex : ∃ a₁ : α, f a₁ = f a := ⟨a, rfl⟩
have feq : f (choose ex) = f a := choose_spec ex
calc linv f (f a)
_ = choose ex := rfl
_ = a := inj feq
```

From a classical point of view, `linv` is a function. From a
constructive point of view, it is unacceptable; because there is no
way to implement such a function in general, the construction is not
informative.

고전적 관점에서 `linv`는 함수입니다. 구성주의적 관점에서 이는 받아들여질 수 없습니다. 일반적으로 그러한 함수를 구현할 방법이 없기 때문에, 그 구성은 정보를 제공하지 않습니다.
