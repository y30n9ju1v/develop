---
title: "5. 전술"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "theorem-proving", "type-theory"]
categories: ["programming"]
description: "rewrite, simp, induction 등 주요 전술과 구조화된 증명 작성 방법을 다룹니다."
---

In this chapter, we describe an alternative approach to constructing
proofs, using *tactics*. A proof term is a representation of a
mathematical proof; tactics are commands, or instructions, that
describe how to build such a proof. Informally, you might begin a
mathematical proof by saying “to prove the forward direction, unfold
the definition, apply the previous lemma, and simplify.” Just as these
are instructions that tell the reader how to find the relevant proof,
tactics are instructions that tell Lean how to construct a proof
term. They naturally support an incremental style of writing proofs,
in which you decompose a proof and work on goals one step at a time.

이 장에서는 *택틱*을 사용하여 증명을 구성하는 대안적 접근 방식을 설명합니다. 증명 항은 수학적 증명의 표현이고, 택틱은 그러한 증명을 구성하는 방법을 설명하는 명령 또는 지침입니다. 비공식적으로, 당신은 수학적 증명을 “순방향을 증명하기 위해 정의를 펼치고, 이전 보조정리를 적용하고, 단순화한다”고 말하기 시작할 수 있습니다. 마찬가지로 독자에게 관련 증명을 찾는 방법을 알려주는 지침이 있듯이, 택틱은 Lean에 증명 항을 구성하는 방법을 알려주는 지침입니다. 이들은 증명을 분해하고 한 번에 한 단계씩 목표에 대해 작업하는 증분식 증명 작성 스타일을 자연스럽게 지원합니다.

We will describe proofs that consist of sequences of tactics as
“tactic-style” proofs, to contrast with the ways of writing proof
terms we have seen so far, which we will call “term-style”
proofs. Each style has its own advantages and disadvantages. For
example, tactic-style proofs can be harder to read, because they
require the reader to predict or guess the results of each
instruction. But they can also be shorter and easier to
write. Moreover, tactics offer a gateway to using Lean's automation,
since automated procedures are themselves tactics.

우리는 일련의 전술(tactics)로 구성된 증명을 “전술 스타일(tactic-style)” 증명이라고 부를 것이며, 이를 지금까지 우리가 살펴본 증명 항을 작성하는 방식인 “항 스타일(term-style)” 증명과 대조할 것입니다. 각각의 스타일은 장단점이 있습니다. 예를 들어, 전술 스타일 증명은 독자가 각 명령의 결과를 예측하거나 추측해야 하기 때문에 읽기 어려울 수 있습니다. 그러나 더 짧고 쓰기 쉬울 수도 있습니다. 더욱이, 자동화된 절차 자체가 전술이기 때문에, 전술은 Lean의 자동화를 사용하는 관문을 제공합니다.

## 5.1. Entering Tactic Mode

Conceptually, stating a theorem or introducing a `have` statement
creates a goal, namely, the goal of constructing a term with the
expected type. For example, the following creates the goal of
constructing a term of type `p ∧ q ∧ p`, in a context with constants
`p q : Prop`, `hp : p` and `hq : q`:

개념적으로 정리나 `have` 문을 진술하는 것은 목표, 즉 예상 타입의 항을 구성하는 목표를 생성합니다. 예를 들어, 다음은 `p ∧ q ∧ p` 타입의 항을 구성하는 목표를 생성하며, 상수 `p q : Prop`, `hp : p` 및 `hq : q`의 컨텍스트에서 실행됩니다.

```
theorem test (p q : Prop) (hp : p) (hq : q) : p ∧ q ∧ p := by
sorry
```

You can write this goal as follows:

이 목표를 다음과 같이 작성할 수 있습니다:

Indeed, if you replace the “sorry” by an underscore in the example
above, Lean will report that it is exactly this goal that has been
left unsolved.

실제로, 위 예제에서 “sorry”를 밑줄로 바꾸면 Lean은 정확히 이 목표가 해결되지 않은 채로 남아 있다고 보고할 것입니다.

Ordinarily, you meet such a goal by writing an explicit term. But
wherever a term is expected, Lean allows us to insert instead a
`by <tactics>` block, where `<tactics>` is a sequence of commands,
separated by semicolons or line breaks. You can prove the theorem above
in that way:

일반적으로 그러한 목표를 만나려면 명시적인 항을 작성합니다. 하지만 항이 예상되는 곳 어디든, Lean은 대신 `by <tactics>` 블록을 삽입하도록 허락합니다. 여기서 `<tactics>`는 세미콜론이나 줄 바꿈으로 구분된 명령 시퀀스입니다. 위의 정리를 그렇게 증명할 수 있습니다.

```
theorem test (p q : Prop) (hp : p) (hq : q) : p ∧ q ∧ p :=
by apply And.intro
exact hp
apply And.intro
exact hq
exact hp
```

We often put the `by` keyword on the preceding line, and write the
example above as:

우리는 종종 `by` 키워드를 앞의 줄에 놓고 위의 예제를 다음과 같이 작성합니다.

```
theorem test (p q : Prop) (hp : p) (hq : q) : p ∧ q ∧ p := by
apply And.intro
exact hp
apply And.intro
exact hq
exact hp
```

The `apply` tactic applies an expression, viewed as denoting a
function with zero or more arguments. It unifies the conclusion with
the expression in the current goal, and creates new goals for the
remaining arguments, provided that no later arguments depend on
them. In the example above, the command `apply And.intro` yields two
subgoals:

`apply` 택틱은 0개 이상의 인수를 가지는 함수로 본 표현식을 적용합니다. 결론을 현재 목표의 표현식과 통일하고, 나머지 인수에 대한 새 목표를 생성하며, 이후 인수가 이들에 의존하지 않는 한 생성합니다. 위의 예제에서 `apply And.intro` 명령은 두 개의 부분 목표를 생성합니다.

The first goal is met with the command `exact hp`. The `exact`
command is just a variant of `apply` which signals that the
expression given should fill the goal exactly. It is good form to use
it in a tactic proof, since its failure signals that something has
gone wrong. It is also more robust than `apply`, since the
elaborator takes the expected type, given by the target of the goal,
into account when processing the expression that is being applied. In
this case, however, `apply` would work just as well.

첫 번째 목표는 `exact hp` 명령으로 만족됩니다. `exact` 명령은 단순히 주어진 표현식이 목표를 정확히 채워야 함을 신호하는 `apply`의 변형입니다. 택틱 증명에서 좋은 형태입니다. 왜냐하면 실패는 뭔가 잘못되었음을 나타내기 때문입니다. `apply`보다 더 견고합니다. 왜냐하면 엘래버레이터가 적용되는 표현식을 처리할 때 목표의 대상으로 주어진 예상 타입을 고려하기 때문입니다. 하지만 이 경우에는 `apply`도 마찬가지로 작동할 것입니다.

You can see the resulting proof term with the `#print` command:

결과 증명 항을 `#print` 명령으로 볼 수 있습니다.

```
#print test
```

```
theorem test : ∀ (p q : Prop), p → q → p ∧ q ∧ p :=
fun p q hp hq => ⟨hp, ⟨hq, hp⟩⟩
```

You can write a tactic script incrementally. In VS Code, you can open
a window to display messages by pressing `CtrlShiftEnter`, and
that window will then show you the current goal whenever the cursor is
in a tactic block. If the proof is incomplete, the token `by` is
decorated with a red squiggly line, and the error message contains the
remaining goals.

택틱 스크립트를 증분식으로 작성할 수 있습니다. VS Code에서 `CtrlShiftEnter`를 눌러 메시지를 표시하는 창을 열 수 있으며, 커서가 택틱 블록에 있을 때마다 현재 목표를 표시합니다. 증명이 불완전하면 `by` 토큰은 빨간색 물결선으로 장식되고, 오류 메시지에는 남은 목표가 포함됩니다.

Tactic commands can take compound expressions, not just single
identifiers. The following is a shorter version of the preceding
proof:

택틱 명령은 단일 식별자뿐만 아니라 복합 표현식을 사용할 수 있습니다. 다음은 이전 증명의 더 짧은 버전입니다.

```
theorem test (p q : Prop) (hp : p) (hq : q) : p ∧ q ∧ p := by
apply And.intro hp
exact And.intro hq hp
```

Unsurprisingly, it produces exactly the same proof term:

당연하게도, 그것은 정확히 같은 증명 항을 생성합니다.

```
#print test
```

```
theorem test : ∀ (p q : Prop), p → q → p ∧ q ∧ p :=
fun p q hp hq => ⟨hp, ⟨hq, hp⟩⟩
```

Multiple tactic applications can be written in a single line by concatenating with a semicolon.

여러 택틱 적용은 세미콜론과 연결하여 한 줄로 작성할 수 있습니다.

```
theorem test (p q : Prop) (hp : p) (hq : q) : p ∧ q ∧ p := by
apply And.intro hp; exact And.intro hq hp
```

Tactics that may produce multiple subgoals often tag them. For
example, the tactic `apply And.intro` tagged the first subgoal as
`leftleftp:Propq:Prophp:phq:q⊢ p`, and the second as `rightrightp:Propq:Prophp:phq:q⊢ q ∧ p`. In the case of the `apply`
tactic, the tags are inferred from the parameters' names used in the
`And.intro` declaration. You can structure your tactics using the
notation `case` `<tag> => <tactics>`. The following is a structured
version of our first tactic proof in this chapter.

```
theorem test (p q : Prop) (hp : p) (hq : q) : p ∧ q ∧ p := by
apply And.intro
case left => exact hp
case right =>
apply And.intro
case left => exact hq
case right => exact hp
```

You can solve the subgoal `right` before `left` using the `case` notation:

여러 부분 목표를 생성할 수 있는 택틱은 종종 이들에 태그를 지정합니다. 예를 들어, `apply And.intro` 택틱은 첫 번째 부분 목표에 `left` 태그를 지정하고, 두 번째에 `right` 태그를 지정합니다. `apply` 택틱의 경우, 태그는 `And.intro` 선언에서 사용된 매개변수의 이름에서 유추됩니다. `case` `<tag> => <tactics>` 표기법을 사용하여 택틱을 구조화할 수 있습니다. 다음은 이 장의 첫 번째 택틱 증명의 구조화된 버전입니다.

`case` 표기법을 사용하여 `right` 부분 목표를 `left` 부분 목표 이전에 해결할 수 있습니다.

```
theorem test (p q : Prop) (hp : p) (hq : q) : p ∧ q ∧ p := by
apply And.intro
case right =>
apply And.intro
case left => exact hq
case right => exact hp
case left => exact hp
```

Note that Lean hides the other goals inside the `case` block. After `case left =>`,
the proof state is:

Lean은 `case` 블록 내부의 다른 목표를 숨깁니다. `case left =>`를 따른 후 증명 상태는 다음과 같습니다.

We say that `case` is “focusing” on the selected goal. Moreover, Lean flags an error
if the selected goal is not fully solved at the end of the `case`
block.

우리는 `case`가 선택된 목표에 “초점(focusing)”을 맞추고 있다고 말합니다. 게다가 Lean은 선택된 목표가 `case` 블록의 끝에서 완전히 해결되지 않으면 오류를 표시합니다.

For simple subgoals, it may not be worth selecting a subgoal using its
tag, but you may still want to structure the proof. Lean also provides
the “bullet” notation `. <tactics>` (or `· <tactics>`) for
structuring proofs:

간단한 부목표의 경우, 태그를 사용하여 부목표를 선택할 가치가 없을 수 있지만 여전히 증명을 구조화하고 싶을 것입니다. Lean은 증명을 구조화하기 위해 “불릿(bullet)” 표기법 `. <tactics>` (또는 `· <tactics>`)도 제공합니다:

```
theorem test (p q : Prop) (hp : p) (hq : q) : p ∧ q ∧ p := by
apply And.intro
. exact hp
. apply And.intro
. exact hq
. exact hp
```

## 5.2. Basic Tactics

In addition to `apply` and `exact`, another useful tactic is
`intro`, which introduces a hypothesis. What follows is an example
of an identity from propositional logic that we proved in a previous
chapter, now proved using tactics.

`apply`와 `exact` 외에도 다른 유용한 택틱은 가설을 도입하는 `intro`입니다. 다음은 이전 장에서 증명한 명제 논리의 항등식의 예로, 이제 택틱을 사용하여 증명됩니다.

```
example (p q r : Prop) : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) := by
apply Iff.intro
. intro h
apply Or.elim (And.right h)
. intro hq
apply Or.inl
apply And.intro
. exact And.left h
. exact hq
. intro hr
apply Or.inr
apply And.intro
. exact And.left h
. exact hr
. intro h
apply Or.elim h
. intro hpq
apply And.intro
. exact And.left hpq
. apply Or.inl
exact And.right hpq
. intro hpr
apply And.intro
. exact And.left hpr
. apply Or.inr
exact And.right hpr
```

The `intro` command can more generally be used to introduce a variable of any type:

`intro` 명령은 더 일반적으로 모든 타입의 변수를 도입하는 데 사용할 수 있습니다.

```
example (α : Type) : α → α := by
intro a
exact a
example (α : Type) : ∀ x : α, x = x := by
intro x
exact Eq.refl x
```

You can use it to introduce several variables:

이를 사용하여 여러 변수를 도입할 수 있습니다.

```
example : ∀ a b c : Nat, a = b → a = c → c = b := by
intro a b c h₁ h₂
exact Eq.trans (Eq.symm h₂) h₁
```

As the `apply` tactic is a command for constructing function
applications interactively, the `intro` tactic is a command for
constructing function abstractions interactively (i.e., terms of the
form `fun x => e`). As with lambda abstraction notation, the
`intro` tactic allows us to use an implicit `match`.

`apply` 택틱이 함수 적용을 대화형으로 구성하는 명령이므로, `intro` 택틱은 함수 추상화를 대화형으로 구성하는 명령입니다 (즉, `fun x => e` 형식의 항). 람다 추상화 표기법과 마찬가지로, `intro` 택틱은 암시적 `match`를 사용하도록 허락합니다.

```
example (p q : α → Prop) : (∃ x, p x ∧ q x) → ∃ x, q x ∧ p x := by
intro ⟨w, hpw, hqw⟩
exact ⟨w, hqw, hpw⟩
```

You can also provide multiple alternatives like in the `match` expression.

`match` 표현식처럼 여러 대안을 제공할 수도 있습니다.

```
example (p q : α → Prop) : (∃ x, p x ∨ q x) → ∃ x, q x ∨ p x := by
intro
| ⟨w, Or.inl h⟩ => exact ⟨w, Or.inr h⟩
| ⟨w, Or.inr h⟩ => exact ⟨w, Or.inl h⟩
```

The `intros` tactic can be used without any arguments, in which
case, it chooses names and introduces as many variables as it can. You
will see an example of this in a moment.

`intros` 택틱은 인수 없이 사용할 수 있으며, 이 경우 이름을 선택하고 가능한 한 많은 변수를 도입합니다. 당신은 곧 이것의 예를 볼 것입니다.

The `assumption` tactic looks through the assumptions in context of
the current goal, and if there is one matching the conclusion, it
applies it.

`assumption` 택틱은 현재 목표의 컨텍스트에서 가정을 찾아보고, 결론과 일치하는 것이 있으면 이를 적용합니다.

```
variable (x y z w : Nat)
example (h₁ : x = y) (h₂ : y = z) (h₃ : z = w) : x = w := by
apply Eq.trans h₁
apply Eq.trans h₂
assumption   -- applied h₃
```

It will unify metavariables in the conclusion if necessary:

필요하면 결론의 메타변수를 통일합니다.

```
variable (x y z w : Nat)
example (h₁ : x = y) (h₂ : y = z) (h₃ : z = w) : x = w := by
apply Eq.trans
assumption      -- solves x = ?b with h₁
  apply Eq.trans
assumption      -- solves y = ?h₂.b with h₂
  assumption      -- solves z = w with h₃
```

The following example uses the `intros` command to introduce the three variables and two hypotheses automatically:

다음 예제는 `intros` 명령을 사용하여 자동으로 3개의 변수와 2개의 가정을 도입합니다.

```
example : ∀ a b c : Nat, a = b → a = c → c = b := by
intros
apply Eq.trans
apply Eq.symm
assumption
assumption
```

Note that names automatically generated by Lean are inaccessible by default. The motivation is to
ensure your tactic proofs do not rely on automatically generated names, and are consequently more robust.
However, you can use the combinator `unhygienic` to disable this restriction.

Lean이 자동으로 생성한 이름은 기본적으로 접근할 수 없습니다. 동기는 택틱 증명이 자동으로 생성된 이름에 의존하지 않도록 보장하여 결과적으로 더 견고하게 하는 것입니다. 그러나 `unhygienic` 조합자를 사용하여 이 제한을 비활성화할 수 있습니다.

```
example : ∀ a b c : Nat, a = b → a = c → c = b := by unhygienic
intros
apply Eq.trans
apply Eq.symm
exact a_2
exact a_1
```

You can also use the `rename_i` tactic to rename the most recent inaccessible names in your context.
In the following example, the tactic `rename_i h1 _ h2` renames two of the last three hypotheses in
your context.

또한 `rename_i` 택틱을 사용하여 컨텍스트의 가장 최근 접근할 수 없는 이름을 변경할 수 있습니다. 다음 예제에서 `rename_i h1 _ h2` 택틱은 컨텍스트의 마지막 3개 가정 중 2개를 변경합니다.

```
example : ∀ a b c d : Nat, a = b → a = d → a = c → c = b := by
intros
rename_i h1 _ h2
apply Eq.trans
apply Eq.symm
exact h2
exact h1
```

The `rfl` tactic solves goals that are reflexive relations applied to definitionally equal arguments.
Equality is reflexive:

`rfl` 택틱은 정의상 동일한 인수에 적용된 반사 관계인 목표를 해결합니다. 동등은 반사적입니다.

```
example (y : Nat) : (fun x : Nat => 0) y = 0 := by
rfl
```

The `repeat` combinator can be used to apply a tactic several times:

`repeat` 조합자는 택틱을 여러 번 적용하는 데 사용할 수 있습니다.

```
example : ∀ a b c : Nat, a = b → a = c → c = b := by
intros
apply Eq.trans
apply Eq.symm
repeat assumption
```

Another tactic that is sometimes useful is the `revert` tactic,
which is, in a sense, an inverse to `intro`:

때때로 유용한 또 다른 택틱은 `revert` 택틱이며, 이는 어떤 의미에서 `intro`의 역입니다.

```
example (x : Nat) : x = x := by
revert x
intro y
rfl
```

After `revert x`, the proof state is:

`revert x`를 따른 후 증명 상태는 다음과 같습니다.

After `intro y`, it is:

`intro y`를 따른 후 다음과 같습니다.

Moving a hypothesis into the goal yields an implication:

가정을 목표로 이동하면 함축을 생성합니다.

```
example (x y : Nat) (h : x = y) : y = x := by
revert h
intro h₁
  -- goal is x y : Nat, h₁ : x = y ⊢ y = x
  apply Eq.symm
assumption
```

After `revert h`, the proof state is:

`revert h`를 따른 후 증명 상태는 다음과 같습니다.

After `intro h₁`, it is:

`intro h₁`를 따른 후 다음과 같습니다.

But `revert` is even more clever, in that it will revert not only an
element of the context but also all the subsequent elements of the
context that depend on it. For example, reverting `x` in the example
above brings `h` along with it:

하지만 `revert`는 더욱 영리하여 컨텍스트의 요소뿐만 아니라 이에 의존하는 컨텍스트의 모든 후속 요소도 되돌립니다. 예를 들어, 위의 예제에서 `x`를 되돌리면 `h`도 함께 가져옵니다.

```
example (x y : Nat) (h : x = y) : y = x := by
revert x
intros
apply Eq.symm
assumption
```

After `revert x`, the goal is:

`revert x` 이후에 목표는 다음과 같습니다:

You can also revert multiple elements of the context at once:

동시에 컨텍스트의 여러 요소를 되돌릴(revert) 수도 있습니다:

```
example (x y : Nat) (h : x = y) : y = x := by
revert x y
intros
apply Eq.symm
assumption
```

After `revert x y`, the goal is:

`revert x y` 이후에 목표는 다음과 같습니다:

You can only `revert` an element of the local context, that is, a
local variable or hypothesis. But you can replace an arbitrary
expression in the goal by a fresh variable using the `generalize`
tactic:

로컬 컨텍스트의 요소, 즉 로컬 변수 또는 가정만 `revert`할 수 있습니다. 하지만 `generalize` 택틱을 사용하여 목표의 임의의 표현식을 새 변수로 바꿀 수 있습니다.

```
example : 3 = 3 := by
generalize 3 = x
revert x
intro y
rfl
```

In particular, after `generalize`, the goal is

특히, `generalize` 이후에 목표는 다음과 같습니다:

The mnemonic in the notation above is that you are generalizing the
goal by setting `3` to an arbitrary variable `x`. Be careful: not
every generalization preserves the validity of the goal. Here,
`generalize` replaces a goal that could be proved using
`rfl` with one that is not provable:

위의 표기법의 니모닉은 `3`을 임의의 변수 `x`로 설정하여 목표를 일반화한다는 것입니다. 주의하십시오: 모든 일반화가 목표의 유효성을 보존하는 것은 아닙니다. 여기서 `generalize`는 `rfl`을 사용하여 증명할 수 있는 목표를 증명할 수 없는 것으로 바꿉니다.

```
example : 2 + 3 = 5 := by
generalize 3 = x
sorry
```

In this example, the `sorry` tactic is the analogue of the `sorry`
proof term. It closes the current goal, producing the usual warning
that `sorry` has been used. To preserve the validity of the previous
goal, the `generalize` tactic allows us to record the fact that
`3` has been replaced by `x`. All you need to do is to provide a
label, and `generalize` uses it to store the assignment in the local
context:

이 예제에서 `sorry` 택틱은 `sorry` 증명 항의 유사체입니다. 현재 목표를 닫아 `sorry`가 사용되었다는 일반적인 경고를 생성합니다. 이전 목표의 유효성을 보존하려면, `generalize` 택틱은 `3`이 `x`로 대체되었다는 사실을 기록하도록 허락합니다. 필요한 것은 레이블을 제공하는 것뿐이며, `generalize`는 이를 사용하여 할당을 로컬 컨텍스트에 저장합니다.

```
example : 2 + 3 = 5 := by
generalize h : 3 = x
rw [← h]
```

Following `generalize h : 3 = x`, `h` is a proof that `3 = x`:

`generalize h : 3 = x`를 따른 후, `h`는 `3 = x`의 증명입니다.

Here the rewriting tactic `rw` uses `h` to replace
`x` by `3` again. The `rw` tactic will be discussed below.

여기서 다시 쓰기 택틱 `rw`는 `h`를 사용하여 `x`를 다시 `3`으로 바꿉니다. `rw` 택틱은 아래에서 논의될 것입니다.

## 5.3. More Tactics

Some additional tactics are useful for constructing and destructing
propositions and data. For example, when applied to a goal of the form
`p ∨ q`, you use tactics such as `apply Or.inl` and
`apply Or.inr`. Conversely, the `cases` tactic can be used to decompose a
disjunction:

일부 추가 택틱은 명제와 데이터를 구성하고 분해하는 데 유용합니다. 예를 들어, `p ∨ q` 형식의 목표에 적용할 때, `apply Or.inl` 및 `apply Or.inr`과 같은 택틱을 사용합니다. 반대로, `cases` 택틱은 분리를 분해하는 데 사용할 수 있습니다.

```
example (p q : Prop) : p ∨ q → q ∨ p := by
intro h
cases h with
| inl hp => apply Or.inr; exact hp
| inr hq => apply Or.inl; exact hq
```

Note that the syntax is similar to the one used in `match` expressions.
The new subgoals can be solved in any order:

문법이 `match` 표현식에서 사용되는 것과 유사함을 유의하십시오. 새 부분 목표는 임의의 순서로 해결할 수 있습니다.

```
example (p q : Prop) : p ∨ q → q ∨ p := by
intro h
cases h with
| inr hq => apply Or.inl; exact hq
| inl hp => apply Or.inr; exact hp
```

You can also use a (unstructured) `cases` without the `with` and a tactic
for each alternative:

또한 각 대안에 `with` 없이 (비구조적) `cases`와 택틱을 사용할 수 있습니다.

```
example (p q : Prop) : p ∨ q → q ∨ p := by
intro h
cases h
apply Or.inr
assumption
apply Or.inl
assumption
```

The (unstructured) `cases` is particularly useful when you can close several
subgoals using the same tactic:

```
example (p : Prop) : p ∨ p → p := by
intro h
cases h
repeat assumption
```

You can also use the combinator `tac1 ``<;>`` tac2` to apply `tac2` to each subgoal produced by tactic `tac1`:

(비구조적) `cases`는 같은 택틱을 사용하여 여러 부분 목표를 닫을 수 있을 때 특히 유용합니다.

`tac1` `<;>` `tac2` 조합자를 사용하여 `tac1`이 생성한 각 부분 목표에 `tac2`를 적용할 수 있습니다.

```
example (p : Prop) : p ∨ p → p := by
intro h
cases h <;> assumption
```

You can combine the unstructured `cases` tactic with the `case` and `.` notation:

비구조적 `cases` 택틱을 `case` 및 `.` 표기법과 결합할 수 있습니다.

```
example (p q : Prop) : p ∨ q → q ∨ p := by
intro h
cases h
. apply Or.inr
assumption
. apply Or.inl
assumption
example (p q : Prop) : p ∨ q → q ∨ p := by
intro h
cases h
case inr h =>
apply Or.inl
assumption
case inl h =>
apply Or.inr
assumption
example (p q : Prop) : p ∨ q → q ∨ p := by
intro h
cases h
case inr h =>
apply Or.inl
assumption
. apply Or.inr
assumption
```

The `cases` tactic can also be used to
decompose a conjunction:

`cases` 전술은 논리곱(conjunction)을 분해하는 데 사용될 수도 있습니다:

```
example (p q : Prop) : p ∧ q → q ∧ p := by
intro h
cases h with
| intro hp hq => constructor; exact hq; exact hp
```

In this example, there is only one goal after the `cases` tactic is
applied, with `h` `:` `p ∧ q` replaced by a pair of assumptions,
`hp` `:` `p` and `hq` `:` `q`:

이 예제에서 `cases` 택틱이 적용된 후에는 하나의 목표만 있으며, `h` `:` `p ∧ q`는 한 쌍의 가정으로 대체됩니다.

The `constructor` tactic applies the unique
constructor for conjunction, `And.intro`.

`constructor` 택틱은 결합의 고유한 생성자인 `And.intro`를 적용합니다.

With these tactics, an
example from the previous section can be rewritten as follows:

```
example (p q r : Prop) : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) := by
apply Iff.intro
. intro h
cases h with
| intro hp hqr =>
cases hqr
. apply Or.inl; constructor <;> assumption
. apply Or.inr; constructor <;> assumption
. intro h
cases h with
| inl hpq =>
cases hpq with
| intro hp hq =>
constructor; exact hp; apply Or.inl; exact hq
| inr hpr =>
cases hpr with
| intro hp hr =>
constructor; exact hp; apply Or.inr; exact hr
```

You will see in [Inductive Types](../07-inductive-types/#inductive-types) that these tactics are quite general. The `cases` tactic can be used to decompose any element of an inductively defined type; `constructor` always applies the first applicable constructor of an inductively defined type. For example, you can use `cases` and `constructor` with an existential quantifier:

이 택틱들과 함께, 이전 섹션의 예제는 다음과 같이 다시 쓸 수 있습니다.

[귀납적 타입]에서 이 택틱들은 상당히 일반적임을 알 수 있습니다. `cases` 택틱은 귀납적으로 정의된 타입의 임의의 요소를 분해하는 데 사용할 수 있으며; `constructor`는 항상 귀납적으로 정의된 타입의 첫 번째 적용 가능한 생성자를 적용합니다. 예를 들어, 존재 한정자를 사용하여 `cases`와 `constructor`를 사용할 수 있습니다.

```
example (p q : Nat → Prop) : (∃ x, p x) → ∃ x, p x ∨ q x := by
intro h
cases h with
| intro x px => constructor; apply Or.inl; exact px
```

Here, the `constructor` tactic leaves the first component of the
existential assertion, the value of `x`, implicit. It is represented
by a metavariable, which should be instantiated later on. In the
previous example, the proper value of the metavariable is determined
by the tactic `exact px`, since `px` has type `p x`. If you want
to specify a witness to the existential quantifier explicitly, you can
use the `exists` tactic instead:

여기서 `constructor` 택틱은 존재 단언의 첫 번째 구성 요소인 `x`의 값을 암시적으로 남깁니다. 이는 나중에 인스턴스화되어야 하는 메타변수로 표현됩니다. 이전 예제에서, 메타변수의 적절한 값은 `px`가 `p x` 타입을 가지므로 `exact px` 택틱에 의해 결정됩니다. 존재 한정자의 증인을 명시적으로 지정하려면 `exists` 택틱을 대신 사용할 수 있습니다.

```
example (p q : Nat → Prop) : (∃ x, p x) → ∃ x, p x ∨ q x := by
intro h
cases h with
| intro x px => exists x; apply Or.inl; exact px
```

Here is another example:

다음은 다른 예제입니다:

여기 또 다른 예제입니다.

```
example (p q : Nat → Prop) : (∃ x, p x ∧ q x) → ∃ x, q x ∧ p x := by
intro h
cases h with
| intro x hpq =>
cases hpq with
| intro hp hq =>
exists x
```

These tactics can be used on data just as well as propositions. In the
next example, they are used to define functions which swap the
components of the product and sum types:

이 택틱들은 명제뿐만 아니라 데이터에서도 사용할 수 있습니다. 다음 예제에서 이들은 곱과 합 타입의 구성 요소를 교환하는 함수를 정의하는 데 사용됩니다.

```
def swap_pair : α × β → β × α := by
intro p
cases p
constructor <;> assumption
def swap_sum : Sum α β → Sum β α := by
intro p
cases p
. apply Sum.inr; assumption
. apply Sum.inl; assumption
```

Note that up to the names we have chosen for the variables, the
definitions are identical to the proofs of the analogous propositions
for conjunction and disjunction. The `cases` tactic will also do a
case distinction on a natural number:

우리가 변수에 대해 선택한 이름을 제외하고, 정의는 결합과 분리에 대한 유사한 명제의 증명과 동일합니다. `cases` 택틱은 또한 자연수에 대한 경우 구분을 수행합니다.

```
open Nat
example (P : Nat → Prop)
(h₀ : P 0) (h₁ : ∀ n, P (succ n))
(m : Nat) : P m := by
cases m with
| zero => exact h₀
| succ m' => exact h₁ m'
```

The `cases` tactic, and its companion, the `induction` tactic, are discussed in greater detail in
the [Tactics for Inductive Types](../07-inductive-types/#tactics-for-inductive-types) section.

`cases` 택틱과 그 동반자인 `induction` 택틱은 [귀납적 타입에 대한 택틱] 섹션에서 더 자세히 논의됩니다.

The `contradiction` tactic searches for a contradiction among the hypotheses of the current goal:

`contradiction` 택틱은 현재 목표의 가정 중에서 모순을 찾습니다.

```
example (p q : Prop) : p ∧ ¬ p → q := by
intro h
cases h
contradiction
```

You can also use `match` in tactic blocks.

택틱 블록에서 `match`를 사용할 수도 있습니다.

```
example (p q r : Prop) : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) := by
apply Iff.intro
. intro h
match h with
| ⟨_, Or.inl _⟩ =>
apply Or.inl; constructor <;> assumption
| ⟨_, Or.inr _⟩ =>
apply Or.inr; constructor <;> assumption
. intro h
match h with
| Or.inl ⟨hp, hq⟩ =>
constructor; exact hp; apply Or.inl; exact hq
| Or.inr ⟨hp, hr⟩ =>
constructor; exact hp; apply Or.inr; exact hr
```

You can “combine” `intro` with `match` and write the previous examples as follows:

`intro`를 `match`와 “결합”하여 이전 예제들을 다음과 같이 작성할 수 있습니다:

```
example (p q r : Prop) : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) := by
apply Iff.intro
. intro
| ⟨hp, Or.inl hq⟩ =>
apply Or.inl; constructor <;> assumption
| ⟨hp, Or.inr hr⟩ =>
apply Or.inr; constructor <;> assumption
. intro
| Or.inl ⟨hp, hq⟩ =>
constructor; assumption; apply Or.inl; assumption
| Or.inr ⟨hp, hr⟩ =>
constructor; assumption; apply Or.inr; assumption
```

## 5.4. Structuring Tactic Proofs

Tactics often provide an efficient way of building a proof, but long
sequences of instructions can obscure the structure of the
택틱은 종종 증명을 구성하는 효율적인 방법을 제공하지만, 긴 지침 시퀀스는 증명의 구조를 모호하게 할 수 있습니다.

인자(argument)입니다. 이 섹션에서는 전술 스타일 증명에 구조를 제공하여 이러한 증명을 더 읽기 쉽고 견고하게 만드는 데 도움이 되는 몇 가지 방법을 설명합니다.

One thing that is nice about Lean's proof-writing syntax is that it is
possible to mix term-style and tactic-style proofs, and pass between
the two freely. For example, the tactics `apply` and `exact`
expect arbitrary terms, which you can write using `have`, `show`,
and so on. Conversely, when writing an arbitrary Lean term, you can
always invoke the tactic mode by inserting a `by`
block. The following is a somewhat toy example:

Lean의 증명 작성 구문의 좋은 점 중 하나는 항 스타일과 전술 스타일 증명을 혼합하고 둘 사이를 자유롭게 오갈 수 있다는 것입니다. 예를 들어, `apply`와 `exact` 전술은 임의의 항을 기대하며, `have`, `show` 등을 사용하여 이를 작성할 수 있습니다. 반대로 임의의 Lean 항을 작성할 때 `by` 블록을 삽입하여 항상 전술 모드를 호출할 수 있습니다. 다음은 다소 장난감 같은 예시입니다:

```
example (p q r : Prop) : p ∧ (q ∨ r) → (p ∧ q) ∨ (p ∧ r) := by
intro h
exact
have hp : p := h.left
have hqr : q ∨ r := h.right
show (p ∧ q) ∨ (p ∧ r) by
cases hqr with
| inl hq => exact Or.inl ⟨hp, hq⟩
| inr hr => exact Or.inr ⟨hp, hr⟩
```

The following is a more natural example:

다음은 더 자연스러운 예시입니다:

```
example (p q r : Prop) : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) := by
apply Iff.intro
. intro h
cases h.right with
| inl hq => exact Or.inl ⟨h.left, hq⟩
| inr hr => exact Or.inr ⟨h.left, hr⟩
. intro h
cases h with
| inl hpq => exact ⟨hpq.left, Or.inl hpq.right⟩
| inr hpr => exact ⟨hpr.left, Or.inr hpr.right⟩
```

In fact, there is a `show` tactic, which is similar to the
`show` expression in a proof term. It simply declares the type of the
goal that is about to be solved, while remaining in tactic
mode.

사실, 증명 항의 `show` 표현식과 유사한 `show` 전술이 있습니다. 전술 모드를 유지하면서 해결하려는 목표의 타입을 단순히 선언합니다.

```
example (p q r : Prop) : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) := by
apply Iff.intro
. intro h
cases h.right with
| inl hq =>
show (p ∧ q) ∨ (p ∧ r)
exact Or.inl ⟨h.left, hq⟩
| inr hr =>
show (p ∧ q) ∨ (p ∧ r)
exact Or.inr ⟨h.left, hr⟩
. intro h
cases h with
| inl hpq =>
show p ∧ (q ∨ r)
exact ⟨hpq.left, Or.inl hpq.right⟩
| inr hpr =>
show p ∧ (q ∨ r)
exact ⟨hpr.left, Or.inr hpr.right⟩
```

The `show` tactic can actually be used to rewrite a goal to something definitionally equivalent:

`show` 전술은 목표를 정의적으로 동등한 것으로 재작성하는 데 실제로 사용될 수 있습니다:

```
example (n : Nat) : n + 1 = Nat.succ n := by
show Nat.succ n = Nat.succ n
rfl
```

There is also a `have` tactic, which introduces a new subgoal, just as when writing proof terms:

증명 항을 작성할 때와 마찬가지로 새로운 부목표를 도입하는 `have` 전술도 있습니다:

```
example (p q r : Prop) : p ∧ (q ∨ r) → (p ∧ q) ∨ (p ∧ r) := by
intro ⟨hp, hqr⟩
show (p ∧ q) ∨ (p ∧ r)
cases hqr with
| inl hq =>
have hpq : p ∧ q := And.intro hp hq
apply Or.inl
exact hpq
| inr hr =>
have hpr : p ∧ r := And.intro hp hr
apply Or.inr
exact hpr
```

As with proof terms, you can omit the label in the `have` tactic, in
which case, the default label `this` is used:

증명 항과 마찬가지로 `have` 전술에서 레이블을 생략할 수 있으며, 이 경우 기본 레이블인 `this`가 사용됩니다:

```
example (p q r : Prop) : p ∧ (q ∨ r) → (p ∧ q) ∨ (p ∧ r) := by
intro ⟨hp, hqr⟩
show (p ∧ q) ∨ (p ∧ r)
cases hqr with
| inl hq =>
have : p ∧ q := And.intro hp hq
apply Or.inl
exact this
| inr hr =>
have : p ∧ r := And.intro hp hr
apply Or.inr
exact this
```

The types in a `have` tactic can be omitted, so you can write
`have hp := h.left` and `have hqr := h.right`. In fact, with this
notation, you can even omit both the type and the label, in which case
the new fact is introduced with the label `this`:

`have` 전술에서 타입은 생략될 수 있으므로 `have hp := h.left`와 `have hqr := h.right`를 작성할 수 있습니다. 사실 이 표기법을 사용하면 타입과 레이블을 모두 생략할 수 있으며, 이 경우 새로운 사실이 `this`라는 레이블로 도입됩니다:

```
example (p q r : Prop) : p ∧ (q ∨ r) → (p ∧ q) ∨ (p ∧ r) := by
intro ⟨hp, hqr⟩
cases hqr with
| inl hq =>
have := And.intro hp hq
apply Or.inl; exact this
| inr hr =>
have := And.intro hp hr
apply Or.inr; exact this
```

Lean also has a `let` tactic, which is similar to the `have`
tactic, but is used to introduce local definitions instead of
auxiliary facts. It is the tactic analogue of a `let` in a proof
term:

Lean에는 `have` 전술과 유사하지만 보조 사실 대신 로컬 정의를 도입하는 데 사용되는 `let` 전술도 있습니다. 이는 증명 항에서 `let`의 전술 스타일(analogue)입니다:

```
example : ∃ x, x + 2 = 8 := by
let a : Nat := 3 * 2
exists a
```

As with `have`, you can leave the type implicit by writing
`let a := 3 * 2`. The difference between `let` and `have` is that
`let` introduces a local definition in the context, so that the
definition of the local declaration can be unfolded in the proof.

`have`와 마찬가지로 `let a := 3 * 2`라고 적어 타입을 암묵적으로 남겨둘 수 있습니다. `let`과 `have`의 차이점은 `let`이 컨텍스트에 로컬 정의를 도입하여 증명에서 로컬 선언의 정의를 풀(unfold) 수 있다는 것입니다.

We have used `.` to create nested tactic blocks. In a nested block,
Lean focuses on the first goal, and generates an error if it has not
been fully solved at the end of the block. This can be helpful in
indicating the separate proofs of multiple subgoals introduced by a
tactic. The notation `.` is whitespace sensitive and relies on the indentation
to detect whether the tactic block ends. Alternatively, you can
define tactic blocks using curly braces and semicolons:

우리는 중첩된 전술 블록을 생성하기 위해 `.`을 사용했습니다. 중첩된 블록에서 Lean은 첫 번째 목표에 초점을 맞추며, 블록 끝에서 완전히 해결되지 않으면 오류를 생성합니다. 이는 전술에 의해 도입된 여러 부목표의 개별 증명을 나타내는 데 유용할 수 있습니다. 표기법 `.`는 공백에 민감하며 들여쓰기에 의존하여 전술 블록이 끝나는지 여부를 감지합니다. 또는 중괄호와 세미콜론을 사용하여 전술 블록을 정의할 수 있습니다:

```
example (p q r : Prop) : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) := by
apply Iff.intro
{ intro h;
cases h.right;
{ show (p ∧ q) ∨ (p ∧ r);
exact Or.inl ⟨h.left, ‹q›⟩ }
{ show (p ∧ q) ∨ (p ∧ r);
exact Or.inr ⟨h.left, ‹r›⟩ } }
{ intro h;
cases h;
{ show p ∧ (q ∨ r);
rename_i hpq;
exact ⟨hpq.left, Or.inl hpq.right⟩ }
{ show p ∧ (q ∨ r);
rename_i hpr;
exact ⟨hpr.left, Or.inr hpr.right⟩ } }
```

It is useful to use indentation to structure proof: every time a tactic
leaves more than one subgoal, we separate the remaining subgoals by
enclosing them in blocks and indenting. Thus if the application of
theorem `foo` to a single goal produces four subgoals, one would
expect the proof to look like this:

증명을 구조화하기 위해 들여쓰기를 사용하는 것이 유용합니다: 전술이 둘 이상의 부목표를 남길 때마다, 우리는 남은 부목표를 블록으로 묶고 들여쓰기하여 구분합니다. 따라서 단일 목표에 정리 `foo`를 적용하여 4개의 부목표가 생성된다면 증명이 다음과 같을 것으로 예상할 수 있습니다:

or

or

## 5.5. Tactic Combinators

*Tactic combinators* are operations that form new tactics from old
ones. A sequencing combinator is already implicit in the `by` block:

*전술 결합자(tactic combinators)*는 기존 전술에서 새로운 전술을 형성하는 연산입니다. 시퀀싱 결합자는 `by` 블록에 이미 암시되어 있습니다:

```
example (p q : Prop) (hp : p) : p ∨ q :=
by apply Or.inl; assumption
```

Here, `apply Or.inl; assumption` is functionally equivalent to a
single tactic which first applies `apply Or.inl` and then applies
`assumption`.

In `t₁ ``<;>`` t₂`, the `<;>` operator provides a *parallel* version of the sequencing operation: `t₁` is applied to the current goal, and then `t₂` is applied to *all* the resulting subgoals:

여기서 `apply Or.inl; assumption`은 먼저 `apply Or.inl`을 적용한 다음 `assumption`을 적용하는 단일 전술과 기능적으로 동등합니다.

`t₁` `<;>` `t₂`에서 `<;>` 연산자는 시퀀싱 연산의 *병렬* 버전을 제공합니다. `t₁`이 현재 목표에 적용되고, 그런 다음 `t₂`가 결과로 나오는 *모든* 부목표에 적용됩니다:

```
example (p q : Prop) (hp : p) (hq : q) : p ∧ q :=
by constructor <;> assumption
```

This is especially useful when the resulting goals can be finished off
in a uniform way, or, at least, when it is possible to make progress
on all of them uniformly.

The `first`` | t₁ | t₂ | ... | tₙ` applies each `tᵢ` until one succeeds, or else fails:

이것은 결과 목표를 일관된 방식으로 끝낼 수 있거나, 적어도 일관되게 모두에서 진행할 수 있을 때 특히 유용합니다.

`first` `| t₁ | t₂ | ... | tₙ`는 성공할 때까지 각 `tᵢ`를 적용하거나 모두 실패합니다:

```
example (p q : Prop) (hp : p) : p ∨ q := by
first | apply Or.inl; assumption | apply Or.inr; assumption
example (p q : Prop) (hq : q) : p ∨ q := by
first | apply Or.inl; assumption | apply Or.inr; assumption
```

In the first example, the left branch succeeds, whereas in the second one, it is the right one that succeeds.
In the next three examples, the same compound tactic succeeds in each case:

첫 번째 예에서는 왼쪽 분기가 성공하는 반면, 두 번째 예에서는 오른쪽 분기가 성공합니다. 다음 세 가지 예에서는 동일한 복합 전술이 각 경우에 성공합니다:

```
example (p q r : Prop) (hp : p) : p ∨ q ∨ r := by
repeat (first | apply Or.inl; assumption | apply Or.inr | assumption)
example (p q r : Prop) (hq : q) : p ∨ q ∨ r := by
repeat (first | apply Or.inl; assumption | apply Or.inr | assumption)
example (p q r : Prop) (hr : r) : p ∨ q ∨ r := by
repeat (first | apply Or.inl; assumption | apply Or.inr | assumption)
```

The tactic tries to solve the left disjunct immediately by assumption;
if that fails, it tries to focus on the right disjunct; and if that
doesn't work, it invokes the assumption tactic.

이 전술은 `assumption` 전술을 사용하여 왼쪽의 선택지를 즉시 해결하려고 시도합니다. 실패하면 오른쪽 선택지에 초점을 맞추려고 시도하며, 작동하지 않으면 다시 `assumption` 전술을 호출합니다.

You will have no doubt noticed by now that tactics can fail. Indeed, it is the “failure” state that causes the *first* combinator to backtrack and try the next tactic. The `try` combinator builds a tactic that always succeeds, though possibly in a trivial way: `try`` t` executes `t` and reports success, even if `t` fails. It is equivalent to `first``| t |``skip`, where `skip` is a tactic that does nothing (and succeeds in doing so). In the next example, the second `constructor` succeeds on the right conjunct `q ∧ r` (remember that disjunction and conjunction associate to the right) but fails on the first. The `try` tactic ensures that the sequential composition succeeds:

```
example (p q r : Prop) (hp : p) (hq : q) (hr : r) : p ∧ q ∧ r := by
constructor <;> (try constructor) <;> assumption
```

Be careful: `repeat`` (``try`` t)` will loop forever, because the inner tactic never fails.

이제 전술이 실패할 수 있다는 것을 무의식중에 알게 되었을 것입니다. 실제로, *first* 결합자가 역추적(backtrack)하여 다음 전술을 시도하게 만드는 것은 "실패" 상태입니다. `try` 결합자는 항상 성공하는 전술을 구성합니다(사소한 방식일지라도). `try` `t`는 `t`가 실패하더라도 `t`를 실행하고 성공을 보고합니다. 이는 `first``| t |``skip`과 동일하며, 여기서 `skip`은 아무 작업도 수행하지 않는(그리고 그로 인해 성공하는) 전술입니다. 다음 예에서 두 번째 `constructor`는 오른쪽 논리곱 `q ∧ r` (논리합과 논리곱이 오른쪽으로 결합함을 기억하세요)에서는 성공하지만 첫 번째에서는 실패합니다. `try` 전술은 순차적 구성이 성공하도록 보장합니다:

주의하십시오: 내부 전술이 절대로 실패하지 않기 때문에 `repeat` `(``try` `t)`은 영원히 루프를 돌게 됩니다.

In a proof, there are often multiple goals outstanding. Parallel
sequencing is one way to arrange it so that a single tactic is applied
to multiple goals, but there are other ways to do this. For example,
`all_goals` `t` applies `t` to all open goals:

증명에서는 자주 여러 목표가 남아 있습니다. 병렬 시퀀싱은 단일 전술을 여러 목표에 적용하도록 배치하는 하나의 방법이지만, 이를 수행하는 다른 방법도 있습니다. 예를 들어, `all_goals` `t`는 열려 있는 모든 목표에 `t`를 적용합니다:

```
example (p q r : Prop) (hp : p) (hq : q) (hr : r) : p ∧ q ∧ r := by
constructor
all_goals (try constructor)
all_goals assumption
```

In this case, the `any_goals` tactic provides a more robust solution.
It is similar to `all_goals`, except it succeeds if its argument
succeeds on at least one goal:

이 경우 `any_goals` 전술은 더 강력한 솔루션을 제공합니다. 인자가 최소한 하나의 목표에서 성공하면 성공한다는 점을 제외하면 `all_goals`와 유사합니다:

```
example (p q r : Prop) (hp : p) (hq : q) (hr : r) : p ∧ q ∧ r := by
constructor
any_goals constructor
any_goals assumption
```

The first tactic in the `by` block below repeatedly splits
conjunctions:

아래 `by` 블록의 첫 번째 전술은 논리곱을 반복적으로 분할합니다:

```
example (p q r : Prop) (hp : p) (hq : q) (hr : r) :
p ∧ ((p ∧ q) ∧ r) ∧ (q ∧ r ∧ p) := by
repeat (any_goals constructor)
all_goals assumption
```

In fact, we can compress the full tactic down to one line:

```
example (p q r : Prop) (hp : p) (hq : q) (hr : r) :
p ∧ ((p ∧ q) ∧ r) ∧ (q ∧ r ∧ p) := by
repeat (any_goals (first | constructor | assumption))
```

The combinator `focus`` t` ensures that `t` only effects the current goal, temporarily hiding the others from the scope. So, if `t` ordinarily only effects the current goal, `focus`` (``all_goals`` t)` has the same effect as `t`.

사실, 전체 전술을 한 줄로 압축할 수 있습니다:

결합자 `focus` `t`는 `t`가 현재 목표에만 영향을 미치도록 보장하여, 다른 것들을 일시적으로 스코프(범위)에서 숨깁니다. 따라서 `t`가 원래 현재 목표에만 영향을 미친다면, `focus` `(``all_goals` `t)`는 `t`와 같은 효과를 갖습니다.

## 5.6. Rewriting

The `rw` tactic and the `simp` tactic
were introduced briefly in [Calculational Proofs](../04-quantifiers-and-equality/#calculational-proofs). In this
section and the next, we discuss them in greater detail.

`rw` 전술과 `simp` 전술은 [계산적 증명](../04-quantifiers-and-equality/#calculational-proofs)에서 간략히 소개되었습니다. 이 섹션과 다음 섹션에서 이들에 대해 자세히 논의합니다.

The `rw` tactic provides a basic mechanism for applying
substitutions to goals and hypotheses, providing a convenient and
efficient way of working with equality. The most basic form of the
tactic is `rw` `[t]`, where `t` is a term whose type asserts an
equality. For example, `t` can be a hypothesis `h : x = y` in the
context; it can be a general lemma, like
`add_comm : ∀ x y, x + y = y + x`, in which the rewrite tactic tries to find suitable
instantiations of `x` and `y`; or it can be any compound term
asserting a concrete or general equation. In the following example, we
use this basic form to rewrite the goal using a hypothesis.

`rw` 전술은 목표와 가정에 대체를 적용하는 기본 메커니즘을 제공하여 동등성(equality)을 다루는 편리하고 효율적인 방법을 제공합니다. 전술의 가장 기본적인 형태는 `rw` `[t]`이며, 여기서 `t`는 타입이 동등성을 주장하는 항입니다. 예를 들어, `t`는 컨텍스트 내의 가정 `h : x = y`일 수 있습니다. 또는 재작성(rewrite) 전술이 `x`와 `y`의 적절한 인스턴스화를 찾으려고 시도하는 `add_comm : ∀ x y, x + y = y + x`와 같은 일반적인 보조정리(lemma)일 수 있습니다. 또는 구체적이거나 일반적인 방정식을 주장하는 모든 복합 항일 수 있습니다. 다음 예에서는 가정을 사용하여 목표를 재작성하는 데 이 기본 양식을 사용합니다.

```
variable (k : Nat) (f : Nat → Nat)
example (h₁ : f 0 = 0) (h₂ : k = 0) : f k = 0 := by
rw [h₂] -- replace k with 0
  rw [h₁] -- replace f 0 with 0
```

In the example above, the first use of `rw` replaces `k` with
`0` in the goal `f k = 0`. Then, the second one replaces `f 0`
with `0`. The tactic automatically closes any goal of the form
`t = t`. Here is an example of rewriting using a compound expression:

위의 예에서 첫 번째 `rw`의 사용은 목표 `f k = 0`에서 `k`를 `0`으로 바꿉니다. 그런 다음 두 번째 것은 `f 0`을 `0`으로 바꿉니다. 이 전술은 `t = t` 형식의 모든 목표를 자동으로 닫습니다. 다음은 복합 표현식을 사용한 재작성의 예입니다:

```
example (x y : Nat) (p : Nat → Prop) (q : Prop) (h : q → x = y)
(h' : p y) (hq : q) : p x := by
rw [h hq]; assumption
```

Here, `h hq` establishes the equation `x = y`.

Multiple rewrites can be combined using the notation `rw`` [t_1, ..., t_n]`, which is just shorthand for `rw``[t_1]; ...;``rw`` [t_n]`. The previous example can be written as follows:

여기서 `h hq`는 방정식 `x = y`를 설정합니다.

다중 재작성은 `rw` `[t_1, ..., t_n]` 표기법을 사용하여 결합할 수 있으며, 이는 단순히 `rw``[t_1]; ...;``rw` `[t_n]`의 줄임말입니다. 이전 예제를 다음과 같이 작성할 수 있습니다:

```
variable (k : Nat) (f : Nat → Nat)
example (h₁ : f 0 = 0) (h₂ : k = 0) : f k = 0 := by
rw [h₂, h₁]
```

By default, `rw` uses an equation in the forward direction, matching
the left-hand side with an expression, and replacing it with the
right-hand side. The notation `←t` can be used to instruct the
tactic to use the equality `t` in the reverse direction.

기본적으로 `rw`는 방정식을 정방향으로 사용하여 왼쪽 변을 표현식과 일치시키고 오른쪽 변으로 바꿉니다. 표기법 `←t`를 사용하면 전술에 역방향으로 동등성 `t`를 사용하도록 지시할 수 있습니다.

```
variable (a b : Nat) (f : Nat → Nat)
example (h₁ : a = b) (h₂ : f a = 0) : f b = 0 := by
rw [←h₁, h₂]
```

In this example, the term `←h₁` instructs the rewriter to replace
`b` with `a`. In the editors, you can type the backwards arrow as
`\l`. You can also use the ASCII equivalent, `<-`.

이 예에서 `←h₁` 항은 재작성기(rewriter)에게 `b`를 `a`로 바꾸도록 지시합니다. 편집기에서 역방향 화살표를 `\l`로 입력할 수 있습니다. ASCII 동등 표현인 `<-`를 사용할 수도 있습니다.

Sometimes the left-hand side of an identity can match more than one
subterm in the pattern, in which case the `rw` tactic chooses the
first match it finds when traversing the term. If that is not the one
you want, you can use additional arguments to specify the appropriate
subterm.

때때로 항등식의 왼쪽 변이 패턴의 하나 이상의 하위 항(subterm)과 일치할 수 있으며, 이 경우 `rw` 전술은 항을 탐색할 때 찾는 첫 번째 일치를 선택합니다. 그것이 원하지 않는 것이라면 추가 인자를 사용하여 적절한 하위 항을 지정할 수 있습니다.

```
example (a b c : Nat) : a + b + c = a + c + b := by
rw [Nat.add_assoc, Nat.add_comm b, ← Nat.add_assoc]
example (a b c : Nat) : a + b + c = a + c + b := by
rw [Nat.add_assoc, Nat.add_assoc, Nat.add_comm b]
example (a b c : Nat) : a + b + c = a + c + b := by
rw [Nat.add_assoc, Nat.add_assoc, Nat.add_comm _ b]
```

In the first example above, the first step rewrites `a + b + c` to `a`` + (``b + c``)`. The next step applies commutativity to the term `b + c`; without specifying the argument, the tactic would instead rewrite `a`` + (``b + c``)` to `(``b + c``) + ``a`. Finally, the last step applies associativity in the reverse direction, rewriting `a`` + (``c`` + ``b``)` to `a + c + b`. The next two examples instead apply associativity to move the parenthesis to the right on both sides, and then switch `b` and `c`. Notice that the last example specifies that the rewrite should take place on the right-hand side by specifying the second argument to `Nat.add_comm`.

By default, the `rw` tactic affects only the goal. The notation `rw`` [t] ``at`` h` applies the rewrite

위의 첫 번째 예에서, 첫 번째 단계는 `a + b + c`를 `a` `+ (``b + c``)`로 재작성합니다. 다음 단계는 하위 항 `b + c`에 교환법칙을 적용합니다. 인자를 지정하지 않았다면 전술은 대신 `a` `+ (``b + c``)`를 `(``b + c``) +` `a`로 썼을 것입니다. 마지막 단계는 역방향으로 결합법칙을 적용하여 `a` `+ (``c` `+` `b``)`를 `a + c + b`로 씁니다. 다음 두 예는 양쪽의 오른쪽으로 괄호를 옮기기 위해 결합법칙을 적용한 다음 `b`와 `c`를 바꿉니다. 마지막 예제는 `Nat.add_comm`의 두 번째 인자를 지정함으로써 우변에서 재작성이 일어나야 함을 지정한다는 점을 주의하세요.

기본적으로 `rw` 전술은 목표에만 영향을 미칩니다. 표기법 `rw` `[t]` `at` `h`는 재작성을 적용합니다:

```
example (f : Nat → Nat) (a : Nat) (h : a + 0 = 0) : f a = f 0 := by
rw [Nat.add_zero] at h
rw [h]
```

The first step, `rw [Nat.add_zero] at h`, rewrites the hypothesis `a + 0 = 0` to `a = 0`.
Then the new hypothesis `a = 0` is used to rewrite the goal to `f 0` `=` `f 0`.

첫 번째 단계인 `rw [Nat.add_zero] at h`는 가정 `a + 0 = 0`을 `a = 0`으로 재작성합니다. 그런 다음 새로운 가정 `a = 0`이 목표를 `f 0` `=` `f 0`으로 재작성하는 데 사용됩니다.

The `rw` tactic is not restricted to propositions.
In the following example, we use `rw` `[h]` `at` `t` to rewrite the hypothesis `t : Tuple α n` to `t : Tuple α` `0`.

`rw` 전술은 명제에만 국한되지 않습니다. 다음 예에서는 `rw` `[h]` `at` `t`를 사용하여 가정 `t : Tuple α n`을 `t : Tuple α` `0`으로 재작성합니다.

```
def Tuple (α : Type) (n : Nat) :=
{ as : List α // as.length = n }
example (n : Nat) (h : n = 0) (t : Tuple α n) : Tuple α 0 := by
rw [h] at t
exact t
```

## 5.7. Using the Simplifier

Whereas `rw` is designed as a surgical tool for manipulating a
goal, the simplifier offers a more powerful form of automation. A
number of identities in Lean's library have been tagged with the
`[simp]` attribute, and the `simp` tactic uses them to iteratively
rewrite subterms in an expression.

`rw`가 목표를 조작하기 위한 외과적 도구로 설계된 반면, simplifier는 더 강력한 자동화 형태를 제공합니다. Lean의 라이브러리의 많은 항등식들이 `[simp]` 속성으로 태그되어 있으며, `simp` 택틱은 이들을 사용하여 표현식의 부분항을 반복적으로 다시 씁니다.

```
example (x y z : Nat) : (x + 0) * (0 + y * 1 + z * 0) = x * y := by
simp
example (x y z : Nat) (p : Nat → Prop) (h : p (x * y))
: p ((x + 0) * (0 + y * 1 + z * 0)) := by
simp; assumption
```

In the first example, the left-hand side of the equality in the goal
is simplified using the usual identities involving 0 and 1, reducing
the goal to `x * y` `=` `x * y`. At that point, `simp` applies
reflexivity to finish it off. In the second example, `simp` reduces
the goal to `p (x * y)`, at which point the assumption `h`
finishes it off. Here are some more examples
with lists:

첫 번째 예제에서, 목표의 등식의 왼쪽은 0과 1을 포함하는 일반적인 항등식을 사용하여 단순화되어 목표를 `x * y` `=` `x * y`로 줄입니다. 그 시점에서 `simp`는 반사성을 적용하여 완료합니다. 두 번째 예제에서, `simp`는 목표를 `p (x * y)`로 줄이고, 그 시점에서 가정 `h`가 이를 완료합니다. 목록이 있는 더 많은 예제가 있습니다.

```
open List
example (xs : List Nat)
: reverse (xs ++ [1, 2, 3]) = [3, 2, 1] ++ reverse xs := by
simp
example (xs ys : List α)
: length (reverse (xs ++ ys)) = length xs + length ys := by
simp [Nat.add_comm]
```

As with `rw`, you can use the keyword `at` to simplify a hypothesis:

`rw`과 마찬가지로, 가설을 단순화하기 위해 `at` 키워드를 사용할 수 있습니다.

```
example (x y z : Nat) (p : Nat → Prop)
(h : p ((x + 0) * (0 + y * 1 + z * 0))) : p (x * y) := by
simp at h; assumption
```

Moreover, you can use a “wildcard” asterisk to simplify all the hypotheses and the goal:

```
attribute [local simp] Nat.mul_comm Nat.mul_assoc Nat.mul_left_comm
attribute [local simp] Nat.add_assoc Nat.add_comm Nat.add_left_comm
example (w x y z : Nat) (p : Nat → Prop)
(h : p (x * y + z * w * x)) : p (x * w * z + y * x) := by
simp at *; assumption
example (x y z : Nat) (p : Nat → Prop)
(h₁ : p (1 * x + y)) (h₂ : p (x * z * 1))
: p (y + 0 + x) ∧ p (z * x) := by
simp at * <;> constructor <;> assumption
```

For operations that are commutative and associative, like
multiplication on the natural numbers, the simplifier uses these two
facts to rewrite an expression, as well as *left commutativity*. In
the case of multiplication the latter is expressed as follows:
`x * (y * z) = y * (x * z)`. The `local` modifier tells the simplifier
to use these rules in the current file (or section or namespace, as
the case may be). It may seem that commutativity and
left-commutativity are problematic, in that repeated application of
either causes looping. But the simplifier detects identities that
permute their arguments, and uses a technique known as *ordered
rewriting*. This means that the system maintains an internal ordering
of terms, and only applies the identity if doing so decreases the
자연수의 곱셈과 같은 가환이고 결합 가능한 연산의 경우, simplifier는 이 두 사실을 사용하여 표현식을 다시 쓸 뿐만 아니라 *좌 가환성*을 사용합니다. 곱셈의 경우 후자는 다음과 같이 표현됩니다. `x * (y * z) = y * (x * z)`. `local` 수정자는 simplifier에 현재 파일 (또는 섹션 또는 네임스페이스)에서 이 규칙들을 사용하도록 지시합니다. 가환성과 좌 가환성이 문제가 될 수 있어 보일 수 있습니다. 반복된 적용이 루핑을 야기하기 때문입니다. 하지만 simplifier는 인수를 치환하는 항등식을 감지하고, *정렬된 다시 쓰기*로 알려진 기법을 사용합니다. 이는 시스템이 항의 내부 순서를 유지하고, 그렇게 함으로써 감소하는 경우에만 항등식을 적용한다는 의미입니다.

순서입니다. 위의 세 항등식으로, 이는 표현식의 모든 괄호가 오른쪽으로 연결되고, 표현식이 정규적 (다소 자의적)인 방식으로 순서를 매긴다는 효과를 갖습니다. 결합성과 가환성까지 동등한 두 표현식은 동일한 정규 형식으로 다시 씌워집니다.

```
example (w x y z : Nat) (p : Nat → Prop)
: x * y + z * w * x = x * w * z + y * x := by
simp
example (w x y z : Nat) (p : Nat → Prop)
(h : p (x * y + z * w * x)) : p (x * w * z + y * x) := by
simp; simp at h; assumption
```

As with `rw`, you can send `simp` a list of facts to use,
including general lemmas, local hypotheses, definitions to unfold, and
compound expressions. The `simp` tactic also recognizes the `←t`
syntax that `rewrite` does. In any case, the additional rules are
added to the collection of identities that are used to simplify a
term.

`rw`과 마찬가지로, 일반 보조정리, 로컬 가설, 펼칠 정의 및 복합 표현식을 포함하여 `simp`에 사용할 사실 목록을 보낼 수 있습니다. `simp` 택틱은 또한 `rewrite`가 하는 `←t` 구문을 인식합니다. 어쨌든, 추가 규칙은 항을 단순화하는 데 사용되는 항등식 컬렉션에 추가됩니다.

```
def f (m n : Nat) : Nat :=
m + n + m
example {m n : Nat} (h : n = 1) (h' : 0 = m) : (f m n) = n := by
simp [h, ←h', f]
```

A common idiom is to simplify a goal using local hypotheses:

일반적인 관용구는 로컬 가설을 사용하여 목표를 단순화하는 것입니다.

```
variable (k : Nat) (f : Nat → Nat)
example (h₁ : f 0 = 0) (h₂ : k = 0) : f k = 0 := by
simp [h₁, h₂]
```

To use all the hypotheses present in the local context when
simplifying, we can use the wildcard symbol, `*`:

단순화할 때 로컬 컨텍스트에 있는 모든 가설을 사용하려면 와일드카드 기호 `*`를 사용할 수 있습니다.

```
variable (k : Nat) (f : Nat → Nat)
example (h₁ : f 0 = 0) (h₂ : k = 0) : f k = 0 := by
simp [*]
```

Here is another example:

다음은 다른 예제입니다:

```
example (u w x y z : Nat) (h₁ : x = y + z) (h₂ : w = u + x)
: w = z + y + u := by
simp [*, Nat.add_comm]
```

The simplifier will also do propositional rewriting. For example,
using the hypothesis `p`, it rewrites `p ∧ q` to `q` and `p ∨ q` to `True`,
which it then proves trivially. Iterating such
rewrites produces nontrivial propositional reasoning.

Simplifier는 또한 명제 다시 쓰기를 수행합니다. 예를 들어, 가설 `p`를 사용하면, `p ∧ q`를 `q`로 다시 쓰고 `p ∨ q`를 `True`로 다시 쓰며, 이를 자명하게 증명합니다. 이러한 다시 쓰기를 반복하면 자명하지 않은 명제 추론이 생성됩니다.

```
example (p q : Prop) (hp : p) : p ∧ q ↔ q := by
simp [*]
example (p q : Prop) (hp : p) : p ∨ q := by
simp [*]
example (p q r : Prop) (hp : p) (hq : q) : p ∧ (q ∨ r) := by
simp [*]
```

The next example simplifies all the hypotheses, and then uses them to prove the goal.

다음 예제는 모든 가설을 단순화한 다음 이를 사용하여 목표를 증명합니다.

```
example (u w x x' y y' z : Nat) (p : Nat → Prop)
(h₁ : x + 0 = x') (h₂ : y + 0 = y')
: x + y + 0 = x' + y' := by
simp at *
simp [*]
```

One thing that makes the simplifier especially useful is that its
capabilities can grow as a library develops. For example, suppose we
define a list operation that symmetrizes its input by appending its
reversal:

simplifier를 특히 유용하게 만드는 것은 라이브러리가 발전함에 따라 그 기능이 성장할 수 있다는 것입니다. 예를 들어, 입력의 역을 추가하여 대칭화하는 목록 연산을 정의한다고 가정합시다.

```
def mk_symm (xs : List α) :=
xs ++ xs.reverse
```

Then for any list `xs`, `(mk_symm xs).reverse` is equal to `mk_symm xs`,
which can easily be proved by unfolding the definition:

그러면 모든 목록 `xs`에 대해 `(mk_symm xs).reverse`는 `mk_symm xs`와 같으며, 정의를 펼침으로써 쉽게 증명될 수 있습니다.

```
theorem reverse_mk_symm (xs : List α)
: (mk_symm xs).reverse = mk_symm xs := by
simp [mk_symm]
```

We can now use this theorem to prove new results:

이제 이 정리를 사용하여 새로운 결과를 증명할 수 있습니다.

```
example (xs ys : List Nat)
: (xs ++ mk_symm ys).reverse = mk_symm ys ++ xs.reverse := by
simp [reverse_mk_symm]
example (xs ys : List Nat) (p : List Nat → Prop)
(h : p (xs ++ mk_symm ys).reverse)
: p (mk_symm ys ++ xs.reverse) := by
simp [reverse_mk_symm] at h; assumption
```

But using `reverse_mk_symm` is generally the right thing to do, and
it would be nice if users did not have to invoke it explicitly. You can
achieve that by marking it as a simplification rule when the theorem
is defined:

하지만 `reverse_mk_symm`을 사용하는 것은 일반적으로 올바른 일이며, 사용자가 이를 명시적으로 호출할 필요가 없다면 좋을 것입니다. 정리가 정의될 때 이를 단순화 규칙으로 표시하여 달성할 수 있습니다.

```
@[simp] theorem reverse_mk_symm (xs : List α)
: (mk_symm xs).reverse = mk_symm xs := by
simp [mk_symm]
example (xs ys : List Nat)
: (xs ++ mk_symm ys).reverse = mk_symm ys ++ xs.reverse := by
simp
example (xs ys : List Nat) (p : List Nat → Prop)
(h : p (xs ++ mk_symm ys).reverse)
: p (mk_symm ys ++ xs.reverse) := by
simp at h; assumption
```

The notation `@[simp]` declares `reverse_mk_symm` to have the
`[simp]` attribute, and can be spelled out more explicitly:

표기법 `@[simp]`는 `reverse_mk_symm`이 `[simp]` 속성을 가지도록 선언하며, 더 명시적으로 작성할 수 있습니다.

```
theorem reverse_mk_symm (xs : List α)
: (mk_symm xs).reverse = mk_symm xs := by
simp [mk_symm]
attribute [simp] reverse_mk_symm
example (xs ys : List Nat)
: (xs ++ mk_symm ys).reverse = mk_symm ys ++ xs.reverse := by
simp
example (xs ys : List Nat) (p : List Nat → Prop)
(h : p (xs ++ mk_symm ys).reverse)
: p (mk_symm ys ++ xs.reverse) := by
simp at h; assumption
```

The attribute can also be applied any time after the theorem is declared:

속성은 정리가 선언된 후 언제든지 적용할 수 있습니다.

```
theorem reverse_mk_symm (xs : List α)
: (mk_symm xs).reverse = mk_symm xs := by
simp [mk_symm]
example (xs ys : List Nat)
: (xs ++ mk_symm ys).reverse = mk_symm ys ++ xs.reverse := by
simp [reverse_mk_symm]
attribute [simp] reverse_mk_symm
example (xs ys : List Nat) (p : List Nat → Prop)
(h : p (xs ++ mk_symm ys).reverse)
: p (mk_symm ys ++ xs.reverse) := by
simp at h; assumption
```

Once the attribute is applied, however, there is no way to permanently
remove it; it persists in any file that imports the one where the
attribute is assigned. As we will discuss further in
[Attributes](../06-interacting-with-lean/#attributes), one can limit the scope of an attribute to the
current file or section using the `local` modifier:

그러나 속성이 적용되면, 이를 영구적으로 제거할 수 있는 방법이 없습니다. 속성이 할당된 파일을 가져오는 모든 파일에 유지됩니다. [속성](../06-interacting-with-lean/#attributes)에서 더 논의할 것처럼, `local` 수정자를 사용하여 속성의 범위를 현재 파일이나 섹션으로 제한할 수 있습니다.

```
theorem reverse_mk_symm (xs : List α)
: (mk_symm xs).reverse = mk_symm xs := by
simp [mk_symm]
section
attribute [local simp] reverse_mk_symm
example (xs ys : List Nat)
: (xs ++ mk_symm ys).reverse = mk_symm ys ++ xs.reverse := by
simp
example (xs ys : List Nat) (p : List Nat → Prop)
(h : p (xs ++ mk_symm ys).reverse)
: p (mk_symm ys ++ xs.reverse) := by
simp at h; assumption
end
```

Outside the section, the simplifier will no longer use
`reverse_mk_symm` by default.

섹션 외부에서 simplifier는 더 이상 기본적으로 `reverse_mk_symm`을 사용하지 않습니다.

Note that the various `simp` options we have discussed—giving an
explicit list of rules, and using `at` to specify the location—can be combined,
but the order they are listed is rigid. You can see the correct order
in an editor by placing the cursor on the `simp` identifier to see
the documentation string that is associated with it.

우리가 논의한 다양한 `simp` 옵션 - 명시적 규칙 목록을 제공하고, `at`를 사용하여 위치를 지정 - 은 결합될 수 있지만, 나열된 순서는 엄격합니다. 편집기에서 커서를 `simp` 식별자에 놓으면 관련된 문서 문자열을 보아 올바른 순서를 볼 수 있습니다.

There are two additional modifiers that are useful. By default,
`simp` includes all theorems that have been marked with the
attribute `[simp]`. Writing `simp only` excludes these defaults,
allowing you to use a more explicitly crafted list of
rules. In the examples below, the minus sign and
`only` are used to block the application of `reverse_mk_symm`.

유용한 두 가지 추가 수정자가 있습니다. 기본적으로 `simp`는 `[simp]` 속성으로 표시된 모든 정리를 포함합니다. `simp only`를 작성하면 이러한 기본값을 제외하여 더 명시적으로 작성된 규칙 목록을 사용할 수 있습니다. 아래의 예제에서, 마이너스 기호와 `only`는 `reverse_mk_symm`의 적용을 차단하는 데 사용됩니다.

```
def mk_symm (xs : List α) :=
xs ++ xs.reverse
@[simp] theorem reverse_mk_symm (xs : List α)
: (mk_symm xs).reverse = mk_symm xs := by
simp [mk_symm]
example (xs ys : List Nat) (p : List Nat → Prop)
(h : p (xs ++ mk_symm ys).reverse)
: p (mk_symm ys ++ xs.reverse) := by
simp at h; assumption
example (xs ys : List Nat) (p : List Nat → Prop)
(h : p (xs ++ mk_symm ys).reverse)
: p ((mk_symm ys).reverse ++ xs.reverse) := by
simp [-reverse_mk_symm] at h; assumption
example (xs ys : List Nat) (p : List Nat → Prop)
(h : p (xs ++ mk_symm ys).reverse)
: p ((mk_symm ys).reverse ++ xs.reverse) := by
simp only [List.reverse_append] at h; assumption
```

The `simp` tactic has many configuration options. For example, we can enable contextual simplifications as follows:

`simp` 택틱은 많은 구성 옵션을 가지고 있습니다. 예를 들어, 다음과 같이 문맥적 단순화를 활성화할 수 있습니다.

```
example : if x = 0 then y + x = y else x ≠ 0 := by
simp +contextual
```

With `+contextual`, the `simp` tactic uses the fact that `x = 0` when simplifying `y + x = y`, and
`x ≠ 0` when simplifying the other branch. Here is another example:

다음은 다른 예제입니다:

`+contextual`을 사용하면, `simp` 택틱은 `y + x = y`를 단순화할 때 `x = 0`이라는 사실을 사용하고, 다른 분기를 단순화할 때 `x ≠ 0`을 사용합니다. 여기 또 다른 예제입니다.

```
example : ∀ (x : Nat) (h : x = 0), y + x = y := by
simp +contextual
```

Another useful configuration option is `+arith` which enables arithmetical simplifications.

또 다른 유용한 구성 옵션은 산술 단순화를 활성화하는 `+arith`입니다.

```
example : 0 < 1 + x ∧ x + y + 2 ≥ y + 1 := by
simp +arith
```

## 5.8. Split Tactic

The `split` tactic is useful for breaking nested `if`-`then`-`else` and `match` expressions in cases.
For a `match` expression with `n` cases, the `split` tactic generates at most `n` subgoals. Here is an example:

`split` 택틱은 중첩된 `if`-`then`-`else` 및 `match` 표현식을 경우로 나누는 데 유용합니다. `n`개의 경우가 있는 `match` 표현식의 경우, `split` 택틱은 최대 `n`개의 부분 목표를 생성합니다. 여기 예제입니다.

```
def f (x y z : Nat) : Nat :=
match x, y, z with
| 5, _, _ => y
| _, 5, _ => y
| _, _, 5 => y
| _, _, _ => 1
example (x y z : Nat) : x ≠ 5 → y ≠ 5 → z ≠ 5 → z = w → f x y w = 1 := by
intros
simp [f]
split
. contradiction
. contradiction
. contradiction
. rfl
```

We can compress the tactic proof above as follows.

위의 택틱 증명을 다음과 같이 압축할 수 있습니다.

```
example (x y z : Nat) :
x ≠ 5 → y ≠ 5 → z ≠ 5 → z = w →
f x y w = 1 := by
intros; simp [f]; split <;> first | contradiction | rfl
```

The tactic `split <;> first | contradiction | rfl` first applies the `split` tactic,
and then for each generated goal it tries `contradiction`, and then `rfl` if `contradiction` fails.
Like `simp`, we can apply `split` to a particular hypothesis:

택틱 `split <;> first | contradiction | rfl`은 먼저 `split` 택틱을 적용한 다음, 생성된 각 목표에 대해 `contradiction`을 시도하고, `contradiction`이 실패하면 `rfl`을 시도합니다. `simp`처럼, 특정 가설에 `split`를 적용할 수 있습니다.

```
def g (xs ys : List Nat) : Nat :=
match xs, ys with
| [a, b], _ => a+b+1
| _, [b, _] => b+1
| _, _ => 1
example (xs ys : List Nat) (h : g xs ys = 0) : False := by
simp [g] at h; split at h <;> simp +arith at h
```

## 5.9. Extensible Tactics

In the following example, we define the notation `triv` using the command `syntax`.
Then, we use the command `macro_rules` to specify what should
be done when `triv` is used. You can provide different expansions, and the tactic
interpreter will try all of them until one succeeds:

다음 예제에서는 `syntax` 명령을 사용하여 표기법 `triv`를 정의합니다. 그 다음, `macro_rules` 명령을 사용하여 `triv`가 사용될 때 수행해야 할 작업을 지정합니다. 다양한 확장을 제공할 수 있으며, 택틱 해석기는 하나가 성공할 때까지 모두 시도합니다.

```
-- Define a new tactic notation
syntax "triv" : tactic
macro_rules
| `(tactic| triv) => `(tactic| assumption)
example (h : p) : p := by
triv
-- You cannot prove the following theorem using `triv`
-- example (x : α) : x = x := by
--  triv

-- Let's extend `triv`. The tactic interpreter
-- tries all possible macro extensions for `triv` until one succeeds
macro_rules
| `(tactic| triv) => `(tactic| rfl)
example (x : α) : x = x := by
triv
example (x : α) (h : p) : x = x ∧ p := by
apply And.intro <;> triv
-- We now add a (recursive) extension
macro_rules | `(tactic| triv) => `(tactic| apply And.intro <;> triv)
example (x : α) (h : p) : x = x ∧ p := by
triv
```

## 5.10. Exercises

1. Go back to the exercises in [Propositions and Proofs](../03-propositions-and-proofs/#propositions-and-proofs) and
   [Quantifiers and Equality](../04-quantifiers-and-equality/#quantifiers-and-equality) and
   redo as many as you can now with tactic proofs, using also `rw`
   and `simp` as appropriate.

1. [명제 및 증명](../03-propositions-and-proofs/#propositions-and-proofs) 및 [한정자 및 동등성](../04-quantifiers-and-equality/#quantifiers-and-equality)의 연습으로 돌아가서, 이제 택틱 증명으로 할 수 있는 많은 것들을 다시 수행하고, 필요에 따라 `rw` 및 `simp`도 사용하십시오.

2. Use tactic combinators to obtain a one-line proof of the following:

```
example (p q r : Prop) (hp : p)
: (p ∨ q ∨ r) ∧ (q ∨ p ∨ r) ∧ (q ∨ r ∨ p) := by
sorry
```
