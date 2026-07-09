---
title: "Interlude: 명제, 증명, 인덱싱"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "명제, 증명, 인덱싱을 통해 Lean의 타입 검사기가 배열 접근을 안전하게 만드는 방법"
---

# Interlude: Propositions, Proofs, and Indexing

Like many languages, Lean uses square brackets for indexing into arrays and lists.
For instance, if `woodlandCritters` is defined as follows:

많은 언어들과 마찬가지로, Lean은 배열과 리스트를 인덱싱할 때 대괄호를 사용합니다.
예를 들어, `woodlandCritters`가 다음과 같이 정의되어 있다면:

```lean
def woodlandCritters : List String :=
  ["hedgehog", "deer", "snail"]
```

then the individual components can be extracted:

개별 구성 요소를 다음과 같이 추출할 수 있습니다:

```lean
def hedgehog := woodlandCritters[0]
def deer := woodlandCritters[1]
def snail := woodlandCritters[2]
```

However, attempting to extract the fourth element results in a compile-time error, rather than a run-time error:

하지만 네 번째 원소를 추출하려고 하면 실행 시점 오류가 아니라 컴파일 시점 오류가 발생합니다:

```lean
def oops := woodlandCritters[3]
```

```
failed to prove index is valid, possible solutions:
  - Use `have`-expressions to prove the index is valid
  - Use `a[i]!` notation instead, runtime check is performed, and 'Panic' error message is produced if index is not valid
  - Use `a[i]?` notation instead, result is an `Option` type
  - Use `a[i]'h` notation instead, where `h` is a proof that index is valid
⊢ 3 < woodlandCritters.length
```

This error message is saying Lean tried to automatically mathematically prove that `3 < woodlandCritters.length` (i.e. `3 < List.length woodlandCritters`), which would mean that the lookup was safe, but that it could not do so.
Out-of-bounds errors are a common class of bugs, and Lean uses its dual nature as a programming language and a theorem prover to rule out as many as possible.

이 오류 메시지는 Lean이 `3 < woodlandCritters.length`(즉 `3 < List.length woodlandCritters`)를 자동으로 수학적으로 증명하려 했으며, 이것이 성립하면 조회가 안전함을 의미했겠지만, 그것을 증명할 수 없었다는 것을 말해줍니다.
범위를 벗어난 인덱싱 오류는 흔한 종류의 버그이며, Lean은 프로그래밍 언어이자 정리 증명기라는 이중적 성격을 활용해 이런 버그를 최대한 배제합니다.

Understanding how this works requires an understanding of three key ideas: propositions, proofs, and tactics.

이것이 어떻게 작동하는지 이해하려면 명제(proposition), 증명(proof), 전술(tactic)이라는 세 가지 핵심 개념을 이해해야 합니다.

## Propositions and Proofs

A *proposition* is a statement that can be true or false.
All of the following English sentences are propositions:

*명제*는 참이거나 거짓일 수 있는 진술입니다.
다음의 모든 영어 문장은 명제입니다:

* `1 + 1 = 2`
* Addition is commutative.
* There are infinitely many prime numbers.
* `1 + 1 = 15`
* Paris is the capital of France.
* Buenos Aires is the capital of South Korea.
* All birds can fly.

* `1 + 1 = 2`
* 덧셈은 교환 법칙을 만족한다.
* 소수는 무한히 많다.
* `1 + 1 = 15`
* 파리는 프랑스의 수도이다.
* 부에노스아이레스는 대한민국의 수도이다.
* 모든 새는 날 수 있다.

On the other hand, nonsense statements are not propositions.
Despite being grammatical, none of the following are propositions:

반면, 말이 안 되는 진술은 명제가 아닙니다.
문법적으로는 올바르지만, 다음 중 어느 것도 명제가 아닙니다:

Propositions come in two varieties: those that are purely mathematical, relying only on our definitions of concepts, and those that are facts about the world.
Theorem provers like Lean are concerned with the former category, and have nothing to say about the flight capabilities of penguins or the legal status of cities.

명제에는 두 가지 종류가 있습니다: 오직 개념의 정의에만 의존하는 순수하게 수학적인 명제와, 세계에 대한 사실인 명제입니다.
Lean과 같은 정리 증명기는 전자의 범주에 관심이 있으며, 펭귄의 비행 능력이나 도시의 법적 지위에 대해서는 아무것도 말할 수 없습니다.

A *proof* is a convincing argument that a proposition is true.
For mathematical propositions, these arguments make use of the definitions of the concepts that are involved as well as the rules of logical argumentation.
Most proofs are written for people to understand, and leave out many tedious details.
Computer-aided theorem provers like Lean are designed to allow mathematicians to write proofs while omitting many details, and it is the software's responsibility to fill in the missing explicit steps.
These steps can be mechanically checked.
This decreases the likelihood of oversights or mistakes.

*증명*은 어떤 명제가 참임을 설득력 있게 보여주는 논증입니다.
수학적 명제의 경우, 이러한 논증은 관련된 개념의 정의와 논리적 논증의 규칙을 활용합니다.
대부분의 증명은 사람이 이해할 수 있도록 작성되며, 지루한 세부 사항 다수를 생략합니다.
Lean과 같은 컴퓨터 지원 정리 증명기는 수학자들이 많은 세부 사항을 생략한 채 증명을 작성할 수 있도록 설계되어 있으며, 누락된 명시적 단계를 채우는 것은 소프트웨어의 책임입니다.
이 단계들은 기계적으로 검사될 수 있습니다.
이는 실수나 간과가 발생할 가능성을 줄여줍니다.

In Lean, a program's type describes the ways it can be interacted with.
For instance, a program of type `Nat → List String` is a function that takes a `Nat` argument and produces a list of strings.
In other words, each type specifies what counts as a program with that type.

Lean에서 프로그램의 타입은 그 프로그램과 상호작용할 수 있는 방법을 서술합니다.
예를 들어, `Nat → List String` 타입의 프로그램은 `Nat` 인수를 받아 문자열 리스트를 만드는 함수입니다.
다시 말해, 각 타입은 그 타입을 가진 프로그램으로 인정되는 것이 무엇인지를 규정합니다.

In Lean, propositions are in fact types.
They specify what counts as evidence that the statement is true.
The proposition is proved by providing this evidence, which is checked by Lean.
On the other hand, if the proposition is false, then it will be impossible to construct this evidence.

Lean에서 명제는 사실 타입입니다.
명제는 그 진술이 참이라는 증거로 인정되는 것이 무엇인지를 규정합니다.
명제는 이 증거를 제시함으로써 증명되며, Lean이 이를 검사합니다.
반면 명제가 거짓이라면, 이 증거를 구성하는 것은 불가능할 것입니다.

For example, the proposition `1 + 1 = 2` can be written directly in Lean.
The evidence for this proposition is the constructor `rfl`, which is short for *reflexivity*.
In mathematics, a relation is *reflexive* if every element is related to itself; this is a basic requirement in order to have a sensible notion of equality.
Because `1 + 1` computes to `2`, they are really the same thing:

예를 들어, 명제 `1 + 1 = 2`는 Lean에서 직접 작성할 수 있습니다.
이 명제에 대한 증거는 생성자 `rfl`이며, 이는 *반사성(reflexivity)*의 줄임말입니다.
수학에서 관계는 모든 원소가 자기 자신과 관계될 때 *반사적(reflexive)*이라고 하며, 이는 합리적인 동등성 개념을 갖기 위한 기본 요건입니다.
`1 + 1`은 `2`로 계산되므로, 둘은 실제로 같은 것입니다:

```lean
def onePlusOneIsTwo : 1 + 1 = 2 := rfl
```

On the other hand, `rfl` does not prove the false proposition `1 + 1 = 15`:

반면, `rfl`은 거짓 명제인 `1 + 1 = 15`를 증명하지 못합니다:

```lean
def onePlusOneIsFifteen : 1 + 1 = 15 := rfl
```

```
Type mismatch
  rfl
has type
  ?m.16 = ?m.16
but is expected to have type
  1 + 1 = 15
```

This error message indicates that `rfl` can prove that two expressions are equal when both sides of the equality statement are already the same number.
Because `1 + 1` evaluates directly to `2`, they are considered to be the same, which allows `onePlusOneIsTwo` to be accepted.
Just as `Type` describes types such as `Nat`, `String`, and `List (Nat × String × (Int → Float))` that represent data structures and functions, `Prop` describes propositions.

이 오류 메시지는 등식의 양변이 이미 같은 숫자일 때만 `rfl`이 두 식이 같다는 것을 증명할 수 있음을 나타냅니다.
`1 + 1`은 곧바로 `2`로 계산되므로 둘은 같은 것으로 간주되며, 이 덕분에 `onePlusOneIsTwo`가 받아들여집니다.
`Type`이 자료구조와 함수를 나타내는 `Nat`, `String`, `List (Nat × String × (Int → Float))`와 같은 타입들을 서술하는 것처럼, `Prop`은 명제를 서술합니다.

When a proposition has been proven, it is called a *theorem*.
In Lean, it is conventional to declare theorems with the `theorem` keyword instead of `def`.
This helps readers see which declarations are intended to be read as mathematical proofs, and which are definitions.
Generally speaking, with a proof, what matters is that there is evidence that a proposition is true, but it's not particularly important *which* evidence was provided.
With definitions, on the other hand, it matters very much which particular value is selected—after all, a definition of addition that always returns `0` is clearly wrong.
Because the details of a proof don't matter for later proofs, using the `theorem` keyword enables greater parallelism in the Lean compiler.

명제가 증명되면 이를 *정리(theorem)*라고 부릅니다.
Lean에서는 `def` 대신 `theorem` 키워드로 정리를 선언하는 것이 관례입니다.
이는 독자가 어떤 선언이 수학적 증명으로 읽히도록 의도된 것이고 어떤 것이 정의인지 구분하는 데 도움이 됩니다.
일반적으로 증명에서 중요한 것은 명제가 참이라는 증거가 존재한다는 사실이며, *어떤* 증거가 제시되었는지는 그다지 중요하지 않습니다.
반면 정의에서는 어떤 특정 값이 선택되었는지가 매우 중요합니다—결국 항상 `0`을 반환하는 덧셈의 정의는 명백히 잘못된 것입니다.
증명의 세부 사항은 이후의 증명에 영향을 주지 않으므로, `theorem` 키워드를 사용하면 Lean 컴파일러가 더 큰 병렬성을 발휘할 수 있습니다.

The prior example could be rewritten as follows:

앞의 예제는 다음과 같이 다시 작성할 수 있습니다:

```lean
def OnePlusOneIsTwo : Prop := 1 + 1 = 2
theorem onePlusOneIsTwo : OnePlusOneIsTwo := rfl
```

## Tactics

Proofs are normally written using *tactics*, rather than by providing evidence directly.
Tactics are small programs that construct evidence for a proposition.
These programs run in a *proof state* that tracks the statement that is to be proved (called the *goal*) along with the assumptions that are available to prove it.
Running a tactic on a goal results in a new proof state that contains new goals.
The proof is complete when all goals have been proven.

증명은 보통 증거를 직접 제시하기보다는 *전술(tactic)*을 사용해 작성됩니다.
전술은 명제에 대한 증거를 구성하는 작은 프로그램입니다.
이 프로그램들은 증명할 진술(*목표(goal)*라고 함)과 그것을 증명하는 데 사용할 수 있는 가정들을 추적하는 *증명 상태(proof state)*에서 실행됩니다.
목표에 대해 전술을 실행하면 새로운 목표들을 담은 새로운 증명 상태가 생성됩니다.
모든 목표가 증명되면 증명이 완료됩니다.

To write a proof with tactics, begin the definition with `by`.
Writing `by` puts Lean into tactic mode until the end of the next indented block.
While in tactic mode, Lean provides ongoing feedback about the current proof state.
Written with tactics, `onePlusOneIsTwo` is still quite short:

전술로 증명을 작성하려면 정의를 `by`로 시작합니다.
`by`를 작성하면 Lean은 다음 들여쓰기 블록이 끝날 때까지 전술 모드로 들어갑니다.
전술 모드에 있는 동안, Lean은 현재 증명 상태에 대한 피드백을 계속 제공합니다.
전술로 작성하면 `onePlusOneIsTwo`는 여전히 매우 짧습니다:

```lean
theorem onePlusOneIsTwo : 1 + 1 = 2 := by
  decide
```

The `decide` tactic invokes a *decision procedure*, which is a program that can check whether a statement is true or false, returning a suitable proof in either case.
It is primarily used when working with concrete values like `1` and `2`.
The other important tactics in this book are `simp`, short for “simplify,” and `grind`, which can automatically prove many theorems.

`decide` 전술은 *결정 절차(decision procedure)*를 호출하는데, 이는 진술이 참인지 거짓인지 확인하고 어느 쪽이든 적절한 증명을 반환할 수 있는 프로그램입니다.
이 전술은 주로 `1`과 `2`처럼 구체적인 값을 다룰 때 사용됩니다.
이 책에서 중요한 다른 전술로는 “simplify(단순화하다)”의 줄임말인 `simp`와, 많은 정리를 자동으로 증명할 수 있는 `grind`가 있습니다.

Tactics are useful for a number of reasons:

전술은 여러 이유로 유용합니다:

1. Many proofs are complicated and tedious when written out down to the smallest detail, and tactics can automate these uninteresting parts.
2. Proofs written with tactics are easier to maintain over time, because flexible automation can paper over small changes to definitions.
3. Because a single tactic can prove many different theorems, Lean can use tactics behind the scenes to free users from writing proofs by hand. For instance, an array lookup requires a proof that the index is in bounds, and a tactic can typically construct that proof without the user needing to worry about it.

1. 많은 증명은 가장 작은 세부 사항까지 모두 작성하면 복잡하고 지루해지는데, 전술은 이런 흥미롭지 않은 부분들을 자동화할 수 있습니다.
2. 전술로 작성한 증명은 시간이 지나도 유지 보수하기 더 쉬운데, 유연한 자동화가 정의의 작은 변경을 흡수해줄 수 있기 때문입니다.
3. 하나의 전술이 여러 다른 정리를 증명할 수 있으므로, Lean은 배후에서 전술을 사용해 사용자가 손수 증명을 작성하지 않아도 되게 해줄 수 있습니다. 예를 들어, 배열 조회는 인덱스가 범위 내에 있다는 증명을 필요로 하는데, 전술은 대체로 사용자가 신경 쓰지 않아도 그 증명을 구성할 수 있습니다.

Behind the scenes, indexing notation uses a tactic to prove that the user's lookup operation is safe.
This tactic takes many facts about arithmetic into account, combining them with any locally-known facts to attempt to prove that the index is in bounds.

배후에서, 인덱싱 표기법은 사용자의 조회 연산이 안전하다는 것을 증명하기 위해 전술을 사용합니다.
이 전술은 산술에 관한 많은 사실을 고려하고, 지역적으로 알려진 사실들과 결합하여 인덱스가 범위 내에 있음을 증명하려고 시도합니다.

The `simp` tactic is a workhorse of Lean proofs.
It rewrites the goal to as simple a form as possible.
In many cases, this rewriting simplifies the statement so much that it can be automatically proved.
Behind the scenes, a detailed formal proof is constructed, but using `simp` hides this complexity.

`simp` 전술은 Lean 증명의 주력 도구입니다.
이 전술은 목표를 가능한 한 단순한 형태로 재작성합니다.
많은 경우, 이 재작성으로 진술이 크게 단순화되어 자동으로 증명될 수 있게 됩니다.
배후에서는 상세한 형식적 증명이 구성되지만, `simp`를 사용하면 이러한 복잡성이 감춰집니다.

Like `decide`, the `grind` tactic is used to finish proofs.
It uses a collection of techniques from SMT solvers that can prove a wide variety of theorems.
Unlike `simp`, `grind` can never make progress towards a proof without completing it entirely; it either succeeds fully or fails.
The `grind` tactic is very powerful, customizable, and extensible; due to this power and flexibility, its output when it fails to prove a theorem contains a lot of information that can help trained Lean users diagnose the reason for the failure.
This can be overwhelming in the beginning, so this chapter uses only `decide` and `simp`.

`decide`와 마찬가지로, `grind` 전술도 증명을 마무리하는 데 사용됩니다.
이 전술은 다양한 정리를 증명할 수 있는 SMT 솔버의 여러 기법을 사용합니다.
`simp`와 달리, `grind`는 증명을 완전히 끝내지 않고서는 결코 진전을 만들지 않습니다. 즉, 완전히 성공하거나 실패하거나 둘 중 하나입니다.
`grind` 전술은 매우 강력하고, 설정 가능하며, 확장 가능합니다. 이러한 힘과 유연성 때문에, 정리를 증명하지 못했을 때의 출력에는 숙련된 Lean 사용자가 실패 원인을 진단하는 데 도움이 되는 많은 정보가 담겨 있습니다.
초심자에게는 이것이 부담스러울 수 있으므로, 이 장에서는 `decide`와 `simp`만 사용합니다.

## Connectives

The basic building blocks of logic, such as “and”, “or”, “true”, “false”, and “not”, are called *logical connectives*.
Each connective defines what counts as evidence of its truth.
For example, to prove a statement “*A* and *B*”, one must prove both *A* and *B*.
This means that evidence for “*A* and *B*” is a pair that contains both evidence for *A* and evidence for *B*.
Similarly, evidence for “*A* or *B*” consists of either evidence for *A* or evidence for *B*.

“그리고(and)”, “또는(or)”, “참(true)”, “거짓(false)”, “아님(not)”과 같은 논리의 기본 구성 요소를 *논리 연결사(logical connective)*라고 부릅니다.
각 연결사는 그것이 참이라는 증거로 인정되는 것이 무엇인지를 정의합니다.
예를 들어, “*A* 그리고 *B*”라는 진술을 증명하려면 *A*와 *B*를 모두 증명해야 합니다.
즉, “*A* 그리고 *B*”에 대한 증거는 *A*에 대한 증거와 *B*에 대한 증거를 모두 담은 쌍입니다.
마찬가지로, “*A* 또는 *B*”에 대한 증거는 *A*에 대한 증거이거나 *B*에 대한 증거 중 하나로 이루어집니다.

In particular, most of these connectives are defined like datatypes, and they have constructors.
If `A` and `B` are propositions, then “`A` and `B`” (written `A ∧ B`) is a proposition.
Evidence for `A ∧ B` consists of the constructor `And.intro`, which has the type `A → B → A ∧ B`.
Replacing `A` and `B` with concrete propositions, it is possible to prove `1 + 1 = 2 ∧ "Str".append "ing" = "String"` with `And.intro rfl rfl`.
Of course, `decide` is also powerful enough to find this proof:

특히, 이러한 연결사 대부분은 자료형처럼 정의되며 생성자를 가집니다.
`A`와 `B`가 명제라면, “`A` 그리고 `B`”(`A ∧ B`로 표기)는 명제입니다.
`A ∧ B`에 대한 증거는 `A → B → A ∧ B` 타입을 가진 생성자 `And.intro`로 이루어집니다.
`A`와 `B`를 구체적인 명제로 바꾸면, `And.intro rfl rfl`로 `1 + 1 = 2 ∧ "Str".append "ing" = "String"`을 증명할 수 있습니다.
물론, `decide`도 이 증명을 찾아낼 만큼 충분히 강력합니다:

```lean
theorem addAndAppend : 1 + 1 = 2 ∧ "Str".append "ing" = "String" := by
  decide
```

Similarly, “`A` or `B`” (written `A ∨ B`) has two constructors, because a proof of “`A` or `B`” requires only that one of the two underlying propositions be true.
There are two constructors: `Or.inl`, with type `A → A ∨ B`, and `Or.inr`, with type `B → A ∨ B`.

마찬가지로, “`A` 또는 `B`”(`A ∨ B`로 표기)는 두 개의 생성자를 가지는데, “`A` 또는 `B`”의 증명은 근간이 되는 두 명제 중 하나만 참이면 되기 때문입니다.
생성자는 `A → A ∨ B` 타입의 `Or.inl`과 `B → A ∨ B` 타입의 `Or.inr` 두 가지가 있습니다.

Implication (if `A` then `B`) is represented using functions.
In particular, a function that transforms evidence for `A` into evidence for `B` is itself evidence that `A` implies `B`.
This is different from the usual description of implication, in which `A → B` is shorthand for `¬A ∨ B`, but the two formulations are equivalent.

함의(“`A`이면 `B`이다”)는 함수를 이용해 표현됩니다.
구체적으로, `A`에 대한 증거를 `B`에 대한 증거로 변환하는 함수 자체가 “`A`가 `B`를 함의한다”는 증거입니다.
이는 `A → B`를 `¬A ∨ B`의 줄임말로 보는 일반적인 함의 설명과는 다르지만, 두 정식화는 동치입니다.

Because evidence for an “and” is a constructor, it can be used with pattern matching.
For instance, a proof that `A` and `B` implies `A` or `B` is a function that pulls the evidence of `A` (or of `B`) out of the evidence for `A` and `B`, and then uses this evidence to produce evidence of `A` or `B`:

“그리고”에 대한 증거는 생성자이므로, 패턴 매칭과 함께 사용할 수 있습니다.
예를 들어, “`A`와 `B`”가 “`A` 또는 `B`”를 함의한다는 증명은, “`A`와 `B`”에 대한 증거로부터 `A`(또는 `B`)에 대한 증거를 꺼낸 다음, 이 증거를 사용해 “`A` 또는 `B`”에 대한 증거를 만들어내는 함수입니다:

```lean
theorem andImpliesOr : A ∧ B → A ∨ B :=
  fun andEvidence =>
    match andEvidence with
    | And.intro a b => Or.inl a
```

| Connective | Lean Syntax | Evidence |
| --- | --- | --- |
| True | `True` | `True.intro : True` |
| False | `False` | No evidence |
| `A` and `B` | `A ∧ B` | `And.intro : A → B → A ∧ B` |
| `A` or `B` | `A ∨ B` | Either `Or.inl : A → A ∨ B` or `Or.inr : B → A ∨ B` |
| `A` implies `B` | `A → B` | A function that transforms evidence of `A` into evidence of `B` |
| not `A` | `¬A` | A function that would transform evidence of `A` into evidence of `False` |

| 연결사 | Lean 문법 | 증거 |
| --- | --- | --- |
| 참 | `True` | `True.intro : True` |
| 거짓 | `False` | 증거 없음 |
| `A` 그리고 `B` | `A ∧ B` | `And.intro : A → B → A ∧ B` |
| `A` 또는 `B` | `A ∨ B` | `Or.inl : A → A ∨ B` 또는 `Or.inr : B → A ∨ B` |
| `A`는 `B`를 함의한다 | `A → B` | `A`에 대한 증거를 `B`에 대한 증거로 변환하는 함수 |
| `A`가 아니다 | `¬A` | `A`에 대한 증거를 `False`에 대한 증거로 변환하는 함수 |

The `decide` tactic can prove theorems that use these connectives.
For example:

`decide` 전술은 이러한 연결사를 사용하는 정리를 증명할 수 있습니다.
예를 들면:

```lean
theorem onePlusOneOrLessThan : 1 + 1 = 2 ∨ 3 < 5 := by
  decide

theorem notTwoEqualFive : ¬(1 + 1 = 5) := by
  decide

theorem trueIsTrue : True := by
  decide

theorem trueOrFalse : True ∨ False := by
  decide

theorem falseImpliesTrue : False → True := by
  decide
```

## Evidence as Arguments

In some cases, safely indexing into a list requires that the list have some minimum size, but the list itself is a variable rather than a concrete value.
For this lookup to be safe, there must be some evidence that the list is long enough.
One of the easiest ways to make indexing safe is to have the function that performs a lookup into a data structure take the required evidence of safety as an argument.
For instance, a function that returns the third entry in a list is not generally safe because lists might contain zero, one, or two entries:

경우에 따라, 리스트를 안전하게 인덱싱하려면 리스트가 최소한의 크기를 가져야 하지만, 리스트 자체는 구체적인 값이 아니라 변수입니다.
이 조회가 안전하려면 리스트가 충분히 길다는 어떤 증거가 있어야 합니다.
인덱싱을 안전하게 만드는 가장 쉬운 방법 중 하나는, 자료구조를 조회하는 함수가 필요한 안전성 증거를 인수로 받도록 하는 것입니다.
예를 들어, 리스트의 세 번째 항목을 반환하는 함수는 리스트가 0개, 1개, 2개의 항목만 가질 수도 있으므로 일반적으로 안전하지 않습니다:

```lean
def third (xs : List α) : α := xs[2]
```

```
failed to prove index is valid, possible solutions:
  - Use `have`-expressions to prove the index is valid
  - Use `a[i]!` notation instead, runtime check is performed, and 'Panic' error message is produced if index is not valid
  - Use `a[i]?` notation instead, result is an `Option` type
  - Use `a[i]'h` notation instead, where `h` is a proof that index is valid
α:Type ?u.9260xs:List α⊢ 2 < xs.length
```

However, the obligation to show that the list has at least three entries can be imposed on the caller by adding an argument that consists of evidence that the indexing operation is safe:

하지만, 리스트가 최소한 세 개의 항목을 가진다는 것을 보여줄 의무를 인덱싱 연산이 안전하다는 증거로 이루어진 인수를 추가함으로써 호출자에게 부과할 수 있습니다:

```lean
def third (xs : List α) (ok : xs.length > 2) : α := xs[2]
```

In this example, `xs.length > 2` is not a program that checks *whether* `xs` has more than 2 entries.
It is a proposition that could be true or false, and the argument `ok` must be evidence that it is true.

이 예제에서 `xs.length > 2`는 `xs`가 2개보다 많은 항목을 가지고 있는지 *검사하는* 프로그램이 아닙니다.
이는 참이거나 거짓일 수 있는 명제이며, 인수 `ok`는 그것이 참이라는 증거여야 합니다.

When the function is called on a concrete list, its length is known.
In these cases, `by decide` can construct the evidence automatically:

함수가 구체적인 리스트에 대해 호출될 때는 그 길이를 알 수 있습니다.
이 경우, `by decide`가 증거를 자동으로 구성할 수 있습니다:

```lean
#eval third woodlandCritters (by decide)
```

```
"snail"
```

## Indexing Without Evidence

In cases where it's not practical to prove that an indexing operation is in bounds, there are other alternatives.
Adding a question mark results in an `Option`, where the result is `some` if the index is in bounds, and `none` otherwise.
For example:

인덱싱 연산이 범위 내에 있음을 증명하는 것이 실용적이지 않은 경우, 다른 대안들이 있습니다.
물음표를 추가하면 `Option`이 되며, 인덱스가 범위 내에 있으면 결과는 `some`이 되고, 그렇지 않으면 `none`이 됩니다.
예를 들면:

```lean
def thirdOption (xs : List α) : Option α := xs[2]?
```

```lean
#eval thirdOption woodlandCritters
```

```
some "snail"
```

```lean
#eval thirdOption ["only", "two"]
```

```
none
```

There is also a version that crashes the program when the index is out of bounds, rather than returning an `Option`:

`Option`을 반환하는 대신, 인덱스가 범위를 벗어나면 프로그램을 크래시시키는 버전도 있습니다:

```lean
#eval woodlandCritters[1]!
```

```
"deer"
```

## Messages You May Meet

In addition to proving that a statement is true, the `decide` tactic can also prove that it is false.
When asked to prove that a one-element list has more than two elements, it returns an error that indicates that the statement is indeed false:

`decide` 전술은 진술이 참임을 증명하는 것 외에도, 그것이 거짓임을 증명할 수도 있습니다.
원소가 하나뿐인 리스트가 두 개보다 많은 원소를 가진다는 것을 증명하라고 요청받으면, 이 전술은 그 진술이 실제로 거짓임을 나타내는 오류를 반환합니다:

```lean
#eval third ["rabbit"] (by decide)
```

```
Tactic `decide` proved that the proposition
  ["rabbit"].length > 2
is false
```

The `simp` and `decide` tactics do not automatically unfold definitions with `def`.
Attempting to prove `OnePlusOneIsTwo` using `simp` fails:

`simp`와 `decide` 전술은 `def`로 만든 정의를 자동으로 펼치지 않습니다.
`simp`를 사용해 `OnePlusOneIsTwo`를 증명하려는 시도는 실패합니다:

```lean
theorem onePlusOneIsStillTwo : OnePlusOneIsTwo := by
  simp
```

The error messages simply states that it could do nothing, because without unfolding `OnePlusOneIsTwo`, no progress can be made:

이 오류 메시지는 `OnePlusOneIsTwo`를 펼치지 않고서는 아무런 진전도 이룰 수 없기 때문에 아무것도 할 수 없었다고 단순히 말해줍니다:

```
`simp` made no progress
```

Using `decide` also fails:

`decide`를 사용해도 마찬가지로 실패합니다:

```lean
theorem onePlusOneIsStillTwo : OnePlusOneIsTwo := by
  decide
```

This is also due to it not unfolding `OnePlusOneIsTwo`:

이 또한 `OnePlusOneIsTwo`를 펼치지 않기 때문입니다:

```
failed to synthesize
  Decidable OnePlusOneIsTwo

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

Defining `OnePlusOneIsTwo` with [`abbrev` fixes the problem](../ch01/) by marking the definition for unfolding.

`OnePlusOneIsTwo`를 [`abbrev`로 정의하면 이 문제가 해결되는데](../ch01/), 이는 해당 정의를 펼침 대상으로 표시하기 때문입니다.

In addition to the error that occurs when Lean is unable to find compile-time evidence that an indexing operation is safe, polymorphic functions that use unsafe indexing may produce the following message:

Lean이 인덱싱 연산이 안전하다는 컴파일 시점 증거를 찾지 못했을 때 발생하는 오류 외에도, 안전하지 않은 인덱싱을 사용하는 다형 함수는 다음과 같은 메시지를 낼 수 있습니다:

```lean
def unsafeThird (xs : List α) : α := xs[2]!
```

```
failed to synthesize
  Inhabited α

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

This is due to a technical restriction that is part of keeping Lean usable as both a logic for proving theorems and a programming language.
In particular, only programs whose types contain at least one value are allowed to crash.
This is because a proposition in Lean is a kind of type that classifies evidence of its truth.
False propositions have no such evidence.
If a program with an empty type could crash, then that crashing program could be used as a kind of fake evidence for a false proposition.

이는 Lean을 정리 증명 논리이자 프로그래밍 언어로서 함께 사용 가능하게 유지하기 위한 기술적 제약 때문입니다.
구체적으로, 적어도 하나의 값을 포함하는 타입을 가진 프로그램만 크래시할 수 있도록 허용됩니다.
이는 Lean에서 명제가 그 참임의 증거를 분류하는 일종의 타입이기 때문입니다.
거짓 명제에는 그러한 증거가 없습니다.
만약 빈 타입을 가진 프로그램이 크래시할 수 있다면, 그 크래시하는 프로그램이 거짓 명제에 대한 일종의 가짜 증거로 사용될 수 있을 것입니다.

Internally, Lean contains a table of types that are known to have at least one value.
This error is saying that some arbitrary type `α` is not necessarily in that table.
The next chapter describes how to add to this table, and how to successfully write functions like `unsafeThird`.

내부적으로, Lean은 적어도 하나의 값을 가진다고 알려진 타입들의 목록을 가지고 있습니다.
이 오류는 임의의 타입 `α`가 그 목록에 반드시 있는 것은 아니라고 말해주는 것입니다.
다음 장에서는 이 목록에 항목을 추가하는 방법과 `unsafeThird`와 같은 함수를 성공적으로 작성하는 방법을 설명합니다.

Adding whitespace between a list and the brackets used for lookup can cause another message:

리스트와 조회에 사용되는 대괄호 사이에 공백을 추가하면 또 다른 메시지가 발생할 수 있습니다:

```lean
#eval woodlandCritters [1]
```

```
Function expected at
  woodlandCritters
but this term has type
  List String

Note: Expected a function because this term is being applied to the argument
  [1]
```

Adding a space causes Lean to treat the expression as a function application, and the index as a list that contains a single number.
This error message results from having Lean attempt to treat `woodlandCritters` as a function.

공백을 추가하면 Lean은 그 식을 함수 적용으로 취급하고, 인덱스를 하나의 숫자를 담은 리스트로 취급합니다.
이 오류 메시지는 Lean이 `woodlandCritters`를 함수로 취급하려고 시도한 결과 발생합니다.

### Exercises

* Prove the following theorems using `rfl`: `2 + 3 = 5`, `15 - 8 = 7`, `"Hello, ".append "world" = "Hello, world"`. What happens if `rfl` is used to prove `5 < 18`? Why?
* Prove the following theorems using `by decide`: `2 + 3 = 5`, `15 - 8 = 7`, `"Hello, ".append "world" = "Hello, world"`, `5 < 18`.
* Write a function that looks up the fifth entry in a list. Pass the evidence that this lookup is safe as an argument to the function.

* 다음 정리들을 `rfl`을 사용해 증명하세요: `2 + 3 = 5`, `15 - 8 = 7`, `"Hello, ".append "world" = "Hello, world"`. `rfl`로 `5 < 18`을 증명하려고 하면 무슨 일이 일어날까요? 왜 그럴까요?
* 다음 정리들을 `by decide`를 사용해 증명하세요: `2 + 3 = 5`, `15 - 8 = 7`, `"Hello, ".append "world" = "Hello, world"`, `5 < 18`.
* 리스트의 다섯 번째 항목을 조회하는 함수를 작성하세요. 이 조회가 안전하다는 증거를 함수의 인수로 전달하세요.
