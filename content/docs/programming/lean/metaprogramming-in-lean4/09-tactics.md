---
title: "Tactics"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "metaprogramming"]
categories: ["programming"]
description: "Lean 4 Tactic 작성: TacticM 모나드와 proof state 조작을 통한 커스텀 tactic 구현"
---

Tactics are Lean programs that manipulate a custom state. All tactics are, in
the end, of type `TacticM Unit`. This has the type:

```
-- from Lean/Elab/Tactic/Basic.lean
TacticM = ReaderT Context $ StateRefT State TermElabM
```

But before demonstrating how to use `TacticM`, we shall explore macro-based
tactics.

Tactic은 커스텀 상태를 조작하는 Lean 프로그램입니다. 모든 tactic은 결국 `TacticM Unit` 타입을 가집니다. 이 타입은 위와 같이 정의됩니다.

`TacticM` 사용법을 시연하기 전에, 먼저 매크로 기반 tactic을 살펴보겠습니다.


Just like many other parts of the Lean 4 infrastructure, tactics too can be
declared by lightweight macro expansion.

For example, we build an example of a `custom_sorry_macro` that elaborates into
a `sorry`. We write this as a macro expansion, which expands the piece of syntax
`custom_sorry_macro` into the piece of syntax `sorry`:

Lean 4 인프라의 다른 많은 부분과 마찬가지로, tactic도 가벼운 매크로 확장으로 선언할 수 있습니다.

예를 들어, `sorry`로 정교화되는 `custom_sorry_macro`를 만들어 봅니다. 이를 매크로 확장으로 작성하는데, 구문 조각 `custom_sorry_macro`를 구문 조각 `sorry`로 확장합니다:

```
import Lean.Elab.Tactic

macro "custom_sorry_macro" : tactic => `(tactic| sorry)

example : 1 = 42 := by
  custom_sorry_macro
```


As more complex examples, we can write a tactic such as `custom_tactic`, which
is initially completely unimplemented, and can be extended with more tactics.
We start by simply declaring the tactic with no implementation:

더 복잡한 예시로, `custom_tactic`처럼 처음에는 전혀 구현되지 않았다가 더 많은 tactic으로 확장될 수 있는 tactic을 작성할 수 있습니다. 구현 없이 tactic만 선언하는 것부터 시작합니다:

```
syntax "custom_tactic" : tactic

/-- error: tactic 'tacticCustom_tactic' has not been implemented -/
example : 42 = 42 := by
  custom_tactic
  sorry
```

We will now add the `rfl` tactic into `custom_tactic`, which will allow us to
prove the previous theorem

이제 `custom_tactic`에 `rfl` tactic을 추가하면 앞의 정리를 증명할 수 있게 됩니다.

```
macro_rules
| `(tactic| custom_tactic) => `(tactic| rfl)

example : 42 = 42 := by
   custom_tactic
-- Goals accomplished 🎉
```

We can now try a harder problem, that cannot be immediately dispatched by `rfl`:

이제 `rfl`로 바로 해결할 수 없는 더 어려운 문제를 시도해 봅시다:

```
#check_failure (by custom_tactic : 43 = 43 ∧ 42 = 42)
-- type mismatch
--   Iff.rfl
-- has type
--   ?m.1437 ↔ ?m.1437 : Prop
-- but is expected to have type
--   43 = 43 ∧ 42 = 42 : Prop
```

We extend the `custom_tactic` tactic with a tactic that tries to break `And`
down with `apply And.intro`, and then (recursively (!)) applies `custom_tactic`
to the two cases with `(<;> trivial)` to solve the generated subcases `43 = 43`,
`42 = 42`.

`custom_tactic` tactic을 `apply And.intro`로 `And`를 분해하고, 생성된 부분 목표 `43 = 43`, `42 = 42`를 해결하기 위해 (`<;> trivial`)로 두 경우에 `custom_tactic`을 (재귀적으로(!)) 적용하는 tactic으로 확장합니다.

```
macro_rules
| `(tactic| custom_tactic) => `(tactic| apply And.intro <;> custom_tactic)
```

The above declaration uses `<;>` which is a *tactic combinator*. Here, `a <;> b`
means "run tactic `a`, and apply "b" to each goal produced by `a`". Thus,
`And.intro <;> custom_tactic` means "run `And.intro`, and then run
`custom_tactic` on each goal". We test it out on our previous theorem and see
that we dispatch the theorem.

위 선언은 *tactic 결합자*인 `<;>`를 사용합니다. 여기서 `a <;> b`는 "tactic `a`를 실행하고, `a`가 생성한 각 목표에 `b`를 적용한다"는 의미입니다. 따라서 `And.intro <;> custom_tactic`은 "`And.intro`를 실행하고, 각 목표에 `custom_tactic`을 실행한다"는 의미입니다. 이전 정리에서 테스트해보면 정리가 해결되는 것을 확인할 수 있습니다.

```
example : 43 = 43 ∧ 42 = 42 := by
  custom_tactic
-- Goals accomplished 🎉
```

In summary, we declared an extensible tactic called `custom_tactic`. It
initially had no elaboration at all. We added the `rfl` as an elaboration of
`custom_tactic`, which allowed it to solve the goal `42 = 42`. We then tried a
harder theorem, `43 = 43 ∧ 42 = 42` which `custom_tactic` was unable to solve.
We were then able to enrich `custom_tactic` to split "and" with `And.intro`, and
also *recursively* call `custom_tactic` in the two subcases.

요약하면, `custom_tactic`이라는 확장 가능한 tactic을 선언했습니다. 처음에는 정교화가 전혀 없었습니다. `custom_tactic`의 정교화로 `rfl`을 추가해 `42 = 42` 목표를 해결할 수 있었습니다. 그 다음 `custom_tactic`이 해결할 수 없는 더 어려운 정리 `43 = 43 ∧ 42 = 42`를 시도했습니다. 이후 `And.intro`로 "and"를 분리하고 두 부분 목표에서 `custom_tactic`을 *재귀적으로* 호출하도록 `custom_tactic`을 풍부하게 만들 수 있었습니다.


Recall that in the previous section, we said that `a <;> b` meant "run `a`, and
then run `b` for all goals". In fact, `<;>` itself is a tactic macro. In this
section, we will implement the syntax `a and_then b` which will stand for
"run `a`, and then run `b` for all goals".

이전 섹션에서 `a <;> b`가 "`a`를 실행하고, 모든 목표에 대해 `b`를 실행한다"는 의미라고 했습니다. 실제로 `<;>` 자체가 tactic 매크로입니다. 이 섹션에서는 "`a`를 실행하고, 모든 목표에 대해 `b`를 실행한다"는 의미를 가지는 `a and_then b` 구문을 구현해 보겠습니다.

```
-- 1. We declare the syntax `and_then`
syntax tactic " and_then " tactic : tactic

-- 2. We write the expander that expands the tactic
--    into running `a`, and then running `b` on all goals produced by `a`.
macro_rules
| `(tactic| $a:tactic and_then $b:tactic) =>
    `(tactic| $a:tactic; all_goals $b:tactic)

-- 3. We test this tactic.
theorem test_and_then: 1 = 1 ∧ 2 = 2 := by
  apply And.intro and_then rfl

#print test_and_then
-- theorem test_and_then : 1 = 1 ∧ 2 = 2 :=
-- { left := Eq.refl 1, right := Eq.refl 2 }
```


In this section, we wish to write a tactic that fills the proof with sorry:

이 섹션에서는 증명을 sorry로 채우는 tactic을 작성하고자 합니다:

```
example : 1 = 2 := by
  custom_sorry
```

We begin by declaring such a tactic:

```
elab "custom_sorry_0" : tactic => do
  return

example : 1 = 2 := by
  custom_sorry_0
-- unsolved goals: ⊢ 1 = 2
  sorry
```

This defines a syntax extension to Lean, where we are naming the piece of syntax
`custom_sorry_0` as living in `tactic` syntax category. This informs the
elaborator that, in the context of elaborating `tactic`s, the piece of syntax
`custom_sorry_0` must be elaborated as what we write to the right-hand-side of
the `=>` (the actual implementation of the tactic).

Next, we write a term in `TacticM Unit` to fill in the goal with `sorryAx α`,
which can synthesize an artificial term of type `α`. To do this, we first access
the goal with `Lean.Elab.Tactic.getMainGoal : Tactic MVarId`, which returns the
main goal, represented as a metavariable. Recall that under
types-as-propositions, the type of our goal must be the proposition that `1 = 2`.
We check this by printing the type of `goal`.

But first we need to start our tactic with `Lean.Elab.Tactic.withMainContext`,
which computes in `TacticM` with an updated context.

이러한 tactic을 선언하는 것부터 시작합니다:

위 코드는 Lean에 구문 확장을 정의하며, 구문 조각 `custom_sorry_0`를 `tactic` 구문 범주에 속하는 것으로 이름 붙입니다. 이는 정교화기에게 `tactic`을 정교화하는 맥락에서 구문 조각 `custom_sorry_0`는 `=>` 오른쪽에 작성된 것(tactic의 실제 구현)으로 정교화되어야 한다고 알려줍니다.

다음으로, 타입 `α`의 인공적인 항을 합성할 수 있는 `sorryAx α`로 목표를 채우는 `TacticM Unit` 항을 작성합니다. 이를 위해 먼저 메타변수로 표현된 주요 목표를 반환하는 `Lean.Elab.Tactic.getMainGoal : Tactic MVarId`로 목표에 접근합니다. 명제로서의 타입 관점에서 목표의 타입은 `1 = 2`라는 명제여야 합니다. `goal`의 타입을 출력하여 이를 확인합니다.

하지만 먼저 업데이트된 컨텍스트로 `TacticM`에서 계산하는 `Lean.Elab.Tactic.withMainContext`로 tactic을 시작해야 합니다.

```
elab "custom_sorry_1" : tactic =>
  Lean.Elab.Tactic.withMainContext do
    let goal ← Lean.Elab.Tactic.getMainGoal
    let goalDecl ← goal.getDecl
    let goalType := goalDecl.type
    dbg_trace f!"goal type: {goalType}"

example : 1 = 2 := by
  custom_sorry_1
-- goal type: Eq.{1} Nat (OfNat.ofNat.{0} Nat 1 (instOfNatNat 1)) (OfNat.ofNat.{0} Nat 2 (instOfNatNat 2))
-- unsolved goals: ⊢ 1 = 2
  sorry
```

To `sorry` the goal, we can use the helper `Lean.Elab.admitGoal`:

목표를 `sorry` 처리하려면 헬퍼 함수 `Lean.Elab.admitGoal`을 사용할 수 있습니다:

```
elab "custom_sorry_2" : tactic =>
  Lean.Elab.Tactic.withMainContext do
    let goal ← Lean.Elab.Tactic.getMainGoal
    Lean.Elab.admitGoal goal

theorem test_custom_sorry : 1 = 2 := by
  custom_sorry_2

#print test_custom_sorry
-- theorem test_custom_sorry : 1 = 2 :=
-- sorryAx (1 = 2) true
```

And we no longer have the error `unsolved goals: ⊢ 1 = 2`.

이제 `unsolved goals: ⊢ 1 = 2` 오류가 더 이상 발생하지 않습니다.


In this section, we will learn how to access the hypotheses to prove a goal. In
particular, we shall attempt to implement a tactic `custom_assump`, which looks
for an exact match of the goal among the hypotheses, and solves the theorem if
possible.

In the example below, we expect `custom_assump` to use `(H2 : 2 = 2)` to solve
the goal `(2 = 2)`:

이 섹션에서는 목표를 증명하기 위해 가설에 접근하는 방법을 배웁니다. 특히, 가설 중에서 목표와 정확히 일치하는 것을 찾아 가능하면 정리를 해결하는 `custom_assump` tactic을 구현해 보겠습니다.

아래 예시에서 `custom_assump`가 `(H2 : 2 = 2)`를 사용해 목표 `(2 = 2)`를 해결하기를 기대합니다:

```
theorem assump_correct (H1 : 1 = 1) (H2 : 2 = 2) : 2 = 2 := by
  custom_assump

#print assump_correct
-- theorem assump_correct : 1 = 1 → 2 = 2 → 2 = 2 :=
-- fun H1 H2 => H2
```

When we do not have a matching hypothesis to the goal, we expect the tactic
`custom_assump` to throw an error, telling us that we cannot find a hypothesis
of the type we are looking for:

목표와 일치하는 가설이 없을 경우, `custom_assump` tactic이 오류를 발생시켜 찾고 있는 타입의 가설을 찾을 수 없다고 알려주기를 기대합니다:

```
theorem assump_wrong (H1 : 1 = 1) : 2 = 2 := by
  custom_assump

#print assump_wrong
-- tactic 'custom_assump' failed, unable to find matching hypothesis of type (2 = 2)
-- H1 : 1 = 1
-- ⊢ 2 = 2
```

We begin by accessing the goal and the type of the goal so we know what we
are trying to prove. The `goal` variable will soon be used to help us create
error messages.

우리가 무엇을 증명하려는지 알기 위해 목표와 목표의 타입에 접근하는 것부터 시작합니다. `goal` 변수는 곧 오류 메시지 생성에 사용될 것입니다.

```
elab "custom_assump_0" : tactic =>
  Lean.Elab.Tactic.withMainContext do
    let goalType ← Lean.Elab.Tactic.getMainTarget
    dbg_trace f!"goal type: {goalType}"

example (H1 : 1 = 1) (H2 : 2 = 2): 2 = 2 := by
  custom_assump_0
-- goal type: Eq.{1} Nat (OfNat.ofNat.{0} Nat 2 (instOfNatNat 2)) (OfNat.ofNat.{0} Nat 2 (instOfNatNat 2))
-- unsolved goals
-- H1 : 1 = 1
-- H2 : 2 = 2
-- ⊢ 2 = 2
  sorry

example (H1 : 1 = 1): 2 = 2 := by
  custom_assump_0
-- goal type: Eq.{1} Nat (OfNat.ofNat.{0} Nat 2 (instOfNatNat 2)) (OfNat.ofNat.{0} Nat 2 (instOfNatNat 2))
-- unsolved goals
-- H1 : 1 = 1
-- ⊢ 2 = 2
  sorry
```

Next, we access the list of hypotheses, which are stored in a data structure
called `LocalContext`. This is accessed via `Lean.MonadLCtx.getLCtx`. The
`LocalContext` contains `LocalDeclaration`s, from which we can extract
information such as the name that is given to declarations (`.userName`), the
expression of the declaration (`.toExpr`). Let's write a tactic called
`list_local_decls` that prints the local declarations:

다음으로, `LocalContext`라는 데이터 구조에 저장된 가설 목록에 접근합니다. 이는 `Lean.MonadLCtx.getLCtx`를 통해 접근합니다. `LocalContext`는 `LocalDeclaration`들을 포함하며, 여기서 선언에 부여된 이름(`.userName`), 선언의 표현식(`.toExpr`) 등의 정보를 추출할 수 있습니다. 로컬 선언들을 출력하는 `list_local_decls` tactic을 작성해 봅시다:

```
elab "list_local_decls_1" : tactic =>
  Lean.Elab.Tactic.withMainContext do
    let ctx ← Lean.MonadLCtx.getLCtx -- get the local context.
    ctx.forM fun decl: Lean.LocalDecl => do
      let declExpr := decl.toExpr -- Find the expression of the declaration.
      let declName := decl.userName -- Find the name of the declaration.
      dbg_trace f!"+ local decl: name: {declName} | expr: {declExpr}"

example (H1 : 1 = 1) (H2 : 2 = 2): 1 = 1 := by
  list_local_decls_1
-- + local decl: name: test_list_local_decls_1 | expr: _uniq.3339
-- + local decl: name: H1 | expr: _uniq.3340
-- + local decl: name: H2 | expr: _uniq.3341
  rfl
```

Recall that we are looking for a local declaration that has the same type as the
hypothesis. We get the type of `LocalDecl` by calling
`Lean.Meta.inferType` on the local declaration's expression.

가설과 동일한 타입을 가진 로컬 선언을 찾고 있음을 상기하세요. 로컬 선언의 표현식에 `Lean.Meta.inferType`을 호출하여 `LocalDecl`의 타입을 얻습니다.

```
elab "list_local_decls_2" : tactic =>
  Lean.Elab.Tactic.withMainContext do
    let ctx ← Lean.MonadLCtx.getLCtx -- get the local context.
    ctx.forM fun decl: Lean.LocalDecl => do
      let declExpr := decl.toExpr -- Find the expression of the declaration.
      let declName := decl.userName -- Find the name of the declaration.
      let declType ← Lean.Meta.inferType declExpr -- **NEW:** Find the type.
      dbg_trace f!"+ local decl: name: {declName} | expr: {declExpr} | type: {declType}"

example (H1 : 1 = 1) (H2 : 2 = 2): 1 = 1 := by
  list_local_decls_2
  -- + local decl: name: test_list_local_decls_2 | expr: _uniq.4263 | type: (Eq.{1} Nat ...)
  -- + local decl: name: H1 | expr: _uniq.4264 | type: Eq.{1} Nat ...)
  -- + local decl: name: H2 | expr: _uniq.4265 | type: Eq.{1} Nat ...)
  rfl
```

We check if the type of the `LocalDecl` is equal to the goal type with
`Lean.Meta.isExprDefEq`. See that we check if the types are equal at `eq?`, and
we print that `H1` has the same type as the goal
(`local decl[EQUAL? true]: name: H1`), and we print that `H2` does not have the
same type (`local decl[EQUAL? false]: name: H2` ):

`Lean.Meta.isExprDefEq`로 `LocalDecl`의 타입이 목표 타입과 같은지 확인합니다. `eq?`에서 타입이 같은지 확인하고, `H1`이 목표와 같은 타입을 가진다(`local decl[EQUAL? true]: name: H1`)고 출력하며, `H2`는 같은 타입을 가지지 않는다(`local decl[EQUAL? false]: name: H2`)고 출력하는 것을 볼 수 있습니다:

```
elab "list_local_decls_3" : tactic =>
  Lean.Elab.Tactic.withMainContext do
    let goalType ← Lean.Elab.Tactic.getMainTarget
    let ctx ← Lean.MonadLCtx.getLCtx -- get the local context.
    ctx.forM fun decl: Lean.LocalDecl => do
      let declExpr := decl.toExpr -- Find the expression of the declaration.
      let declName := decl.userName -- Find the name of the declaration.
      let declType ← Lean.Meta.inferType declExpr -- Find the type.
      let eq? ← Lean.Meta.isExprDefEq declType goalType -- **NEW** Check if type equals goal type.
      dbg_trace f!"+ local decl[EQUAL? {eq?}]: name: {declName}"

example (H1 : 1 = 1) (H2 : 2 = 2): 1 = 1 := by
  list_local_decls_3
-- + local decl[EQUAL? false]: name: test_list_local_decls_3
-- + local decl[EQUAL? true]: name: H1
-- + local decl[EQUAL? false]: name: H2
  rfl
```

Finally, we put all of these parts together to write a tactic that loops over
all declarations and finds one with the correct type. We loop over declarations
with `lctx.findDeclM?`. We infer the type of declarations with
`Lean.Meta.inferType`. We check that the declaration has the same type as the
goal with `Lean.Meta.isExprDefEq`:

마지막으로, 이 모든 부분을 합쳐 모든 선언을 순회하며 올바른 타입을 가진 것을 찾는 tactic을 작성합니다. `lctx.findDeclM?`로 선언들을 순회합니다. `Lean.Meta.inferType`으로 선언의 타입을 추론합니다. `Lean.Meta.isExprDefEq`로 선언이 목표와 같은 타입을 가지는지 확인합니다:

```
elab "custom_assump_1" : tactic =>
  Lean.Elab.Tactic.withMainContext do
    let goalType ← Lean.Elab.Tactic.getMainTarget
    let lctx ← Lean.MonadLCtx.getLCtx
    -- Iterate over the local declarations...
    let option_matching_expr ← lctx.findDeclM? fun ldecl: Lean.LocalDecl => do
      let declExpr := ldecl.toExpr -- Find the expression of the declaration.
      let declType ← Lean.Meta.inferType declExpr -- Find the type.
      if (← Lean.Meta.isExprDefEq declType goalType) -- Check if type equals goal type.
      then return some declExpr -- If equal, success!
      else return none          -- Not found.
    dbg_trace f!"matching_expr: {option_matching_expr}"

example (H1 : 1 = 1) (H2 : 2 = 2) : 2 = 2 := by
  custom_assump_1
-- matching_expr: some _uniq.6241
  rfl

example (H1 : 1 = 1) : 2 = 2 := by
  custom_assump_1
-- matching_expr: none
  rfl
```

Now that we are able to find the matching expression, we need to close the
theorem by using the match. We do this with `Lean.Elab.Tactic.closeMainGoal`.
When we do not have a matching expression, we throw an error with
`Lean.Meta.throwTacticEx`, which allows us to report an error corresponding to a
given goal. When throwing this error, we format the error using `m!"..."` which
builds a `MessageData`. This provides nicer error messages than using `f!"..."`
which builds a `Format`. This is because `MessageData` also runs *delaboration*,
which allows it to convert raw Lean terms like
`(Eq.{1} Nat (OfNat.ofNat.{0} Nat 2 (instOfNatNat 2)) (OfNat.ofNat.{0} Nat 2 (instOfNatNat 2)))`
into readable strings like`(2 = 2)`. The full code listing given below shows how
to do this:

이제 일치하는 표현식을 찾을 수 있으므로, 일치한 것을 사용해 정리를 닫아야 합니다. 이를 `Lean.Elab.Tactic.closeMainGoal`로 수행합니다. 일치하는 표현식이 없을 경우, `Lean.Meta.throwTacticEx`로 오류를 발생시키는데, 이는 주어진 목표에 해당하는 오류를 보고할 수 있게 해줍니다. 이 오류를 발생시킬 때, `MessageData`를 생성하는 `m!"..."`로 오류를 형식화합니다. 이는 `Format`을 생성하는 `f!"..."`보다 더 나은 오류 메시지를 제공합니다. `MessageData`는 *역정교화(delaboration)*도 실행하여 `(Eq.{1} Nat (OfNat.ofNat.{0} Nat 2 (instOfNatNat 2)) (OfNat.ofNat.{0} Nat 2 (instOfNatNat 2)))`와 같은 raw Lean 항을 `(2 = 2)`처럼 읽기 쉬운 문자열로 변환할 수 있기 때문입니다. 아래의 전체 코드 목록은 이를 수행하는 방법을 보여줍니다:

```
elab "custom_assump_2" : tactic =>
  Lean.Elab.Tactic.withMainContext do
    let goal ← Lean.Elab.Tactic.getMainGoal
    let goalType ← Lean.Elab.Tactic.getMainTarget
    let ctx ← Lean.MonadLCtx.getLCtx
    let option_matching_expr ← ctx.findDeclM? fun decl: Lean.LocalDecl => do
      let declExpr := decl.toExpr
      let declType ← Lean.Meta.inferType declExpr
      if ← Lean.Meta.isExprDefEq declType goalType
        then return Option.some declExpr
        else return Option.none
    match option_matching_expr with
    | some e => Lean.Elab.Tactic.closeMainGoal `custom_assump_2 e
    | none =>
      Lean.Meta.throwTacticEx `custom_assump_2 goal
        (m!"unable to find matching hypothesis of type ({goalType})")

example (H1 : 1 = 1) (H2 : 2 = 2) : 2 = 2 := by
  custom_assump_2

#check_failure (by custom_assump_2 : (H1 : 1 = 1) → 2 = 2)
-- tactic 'custom_assump_2' failed, unable to find matching hypothesis of type (2 = 2)
-- H1 : 1 = 1
-- ⊢ 2 = 2
```


Until now, we've only performed read-like operations with the context. But what
if we want to change it? In this section we will see how to change the order of
goals and how to add content to it (new hypotheses).

Then, after elaborating our terms, we will need to use the helper function
`Lean.Elab.Tactic.liftMetaTactic`, which allows us to run computations in
`MetaM` while also giving us the goal `MVarId` for us to play with. In the end
of our computation, `liftMetaTactic` expects us to return a `List MVarId` as the
resulting list of goals.

The only substantial difference between `custom_let` and `custom_have` is that
the former uses `Lean.MVarId.define` and the later uses `Lean.MVarId.assert`:

지금까지는 컨텍스트에서 읽기 작업만 수행했습니다. 하지만 변경하고 싶다면 어떻게 해야 할까요? 이 섹션에서는 목표의 순서를 변경하는 방법과 새로운 가설을 추가하는 방법을 살펴봅니다.

항들을 정교화한 후, `MetaM`에서 계산을 실행하면서 조작할 수 있도록 목표 `MVarId`도 제공하는 헬퍼 함수 `Lean.Elab.Tactic.liftMetaTactic`을 사용해야 합니다. 계산의 끝에서 `liftMetaTactic`은 결과 목표 목록으로 `List MVarId`를 반환하기를 기대합니다.

`custom_let`과 `custom_have`의 유일한 실질적인 차이는 전자가 `Lean.MVarId.define`을 사용하고 후자가 `Lean.MVarId.assert`를 사용한다는 점입니다:

```
open Lean.Elab.Tactic in
elab "custom_let " n:ident " : " t:term " := " v:term : tactic =>
  withMainContext do
    let t ← elabTerm t none
    let v ← elabTermEnsuringType v t
    liftMetaTactic fun mvarId => do
      let mvarIdNew ← mvarId.define n.getId t v
      let (_, mvarIdNew) ← mvarIdNew.intro1P
      return [mvarIdNew]

open Lean.Elab.Tactic in
elab "custom_have " n:ident " : " t:term " := " v:term : tactic =>
  withMainContext do
    let t ← elabTerm t none
    let v ← elabTermEnsuringType v t
    liftMetaTactic fun mvarId => do
      let mvarIdNew ← mvarId.assert n.getId t v
      let (_, mvarIdNew) ← mvarIdNew.intro1P
      return [mvarIdNew]

theorem test_faq_have : True := by
  custom_let n : Nat := 5
  custom_have h : n = n := rfl
-- n : Nat := 5
-- h : n = n
-- ⊢ True
  trivial
```


To illustrate these, let's build a tactic that can reverse the list of goals.
We can use `Lean.Elab.Tactic.getGoals` and `Lean.Elab.Tactic.setGoals`:

이를 설명하기 위해 목표 목록을 역순으로 만들 수 있는 tactic을 만들어 봅시다. `Lean.Elab.Tactic.getGoals`와 `Lean.Elab.Tactic.setGoals`를 사용할 수 있습니다:

```
elab "reverse_goals" : tactic =>
  Lean.Elab.Tactic.withMainContext do
    let goals : List Lean.MVarId ← Lean.Elab.Tactic.getGoals
    Lean.Elab.Tactic.setGoals goals.reverse

theorem test_reverse_goals : (1 = 2 ∧ 3 = 4) ∧ 5 = 6 := by
  constructor
  constructor
-- case left.left
-- ⊢ 1 = 2
-- case left.right
-- ⊢ 3 = 4
-- case right
-- ⊢ 5 = 6
  reverse_goals
-- case right
-- ⊢ 5 = 6
-- case left.right
-- ⊢ 3 = 4
-- case left.left
-- ⊢ 1 = 2
  all_goals sorry
```


In this section, we collect common patterns that are used during writing tactics,
to make it easy to find common patterns.

이 섹션에서는 tactic 작성 시 사용되는 일반적인 패턴을 수집하여 쉽게 찾을 수 있도록 합니다.

**Q: How do I use goals?**

A: Goals are represented as metavariables. The module `Lean.Elab.Tactic.Basic`
has many functions to add new goals, switch goals, etc.

**Q: 목표를 어떻게 사용하나요?**

**A:** 목표는 메타변수로 표현됩니다. `Lean.Elab.Tactic.Basic` 모듈에는 새 목표 추가, 목표 전환 등의 많은 함수가 있습니다.

**Q: How do I get the main goal?**

A: Use `Lean.Elab.Tactic.getMainGoal`.

**Q: 주요 목표를 어떻게 가져오나요?**

**A:** `Lean.Elab.Tactic.getMainGoal`을 사용하세요.

```
elab "faq_main_goal" : tactic =>
  Lean.Elab.Tactic.withMainContext do
    let goal ← Lean.Elab.Tactic.getMainGoal
    dbg_trace f!"goal: {goal.name}"

example : 1 = 1 := by
  faq_main_goal
-- goal: _uniq.9298
  rfl
```

**Q: How do I get the list of goals?**

A: Use `getGoals`.

**Q: 목표 목록을 어떻게 가져오나요?**

**A:** `getGoals`를 사용하세요.

```
elab "faq_get_goals" : tactic =>
  Lean.Elab.Tactic.withMainContext do
    let goals ← Lean.Elab.Tactic.getGoals
    goals.forM $ fun goal => do
      let goalType ← goal.getType
      dbg_trace f!"goal: {goal.name} | type: {goalType}"

example (b : Bool) : b = true := by
  cases b
  faq_get_goals
-- goal: _uniq.10067 | type: Eq.{1} Bool Bool.false Bool.true
-- goal: _uniq.10078 | type: Eq.{1} Bool Bool.true Bool.true
  sorry
  rfl
```

**Q: How do I get the current hypotheses for a goal?**

A: Use `Lean.MonadLCtx.getLCtx` which provides the local context, and then
iterate on the `LocalDeclaration`s of the `LocalContext` with accessors such as
`foldlM` and `forM`.

**Q: 목표의 현재 가설을 어떻게 가져오나요?**

**A:** 로컬 컨텍스트를 제공하는 `Lean.MonadLCtx.getLCtx`를 사용하고, `foldlM`이나 `forM` 같은 접근자로 `LocalContext`의 `LocalDeclaration`들을 순회하세요.

```
elab "faq_get_hypotheses" : tactic =>
  Lean.Elab.Tactic.withMainContext do
  let ctx ← Lean.MonadLCtx.getLCtx -- get the local context.
  ctx.forM (fun (decl : Lean.LocalDecl) => do
    let declExpr := decl.toExpr -- Find the expression of the declaration.
    let declType := decl.type -- Find the type of the declaration.
    let declName := decl.userName -- Find the name of the declaration.
    dbg_trace f!" local decl: name: {declName} | expr: {declExpr} | type: {declType}"
  )

example (H1 : 1 = 1) (H2 : 2 = 2): 3 = 3 := by
  faq_get_hypotheses
  -- local decl: name: _example | expr: _uniq.10814 | type: ...
  -- local decl: name: H1 | expr: _uniq.10815 | type: ...
  -- local decl: name: H2 | expr: _uniq.10816 | type: ...
  rfl
```

**Q: How do I evaluate a tactic?**

A: Use `Lean.Elab.Tactic.evalTactic: Syntax → TacticM Unit` which evaluates a
given tactic syntax. One can create tactic syntax using the macro
 `` `(tactic| ⋯) ``.

For example, one could call `try rfl` with the piece of code:

**Q: tactic을 어떻게 평가하나요?**

**A:** 주어진 tactic 구문을 평가하는 `Lean.Elab.Tactic.evalTactic: Syntax → TacticM Unit`을 사용하세요. `` `(tactic| ⋯) `` 매크로를 사용해 tactic 구문을 만들 수 있습니다.

예를 들어, 다음 코드로 `try rfl`을 호출할 수 있습니다:

```
Lean.Elab.Tactic.evalTactic (← `(tactic| try rfl))
```

**Q: How do I check if two expressions are equal?**

A: Use `Lean.Meta.isExprDefEq <expr-1> <expr-2>`.

**Q: 두 표현식이 같은지 어떻게 확인하나요?**

**A:** `Lean.Meta.isExprDefEq <expr-1> <expr-2>`를 사용하세요.

```
#check Lean.Meta.isExprDefEq
-- Lean.Meta.isExprDefEq : Lean.Expr → Lean.Expr → Lean.MetaM Bool
```

**Q: How do I throw an error from a tactic?**

A: Use `throwTacticEx <tactic-name> <goal-mvar> <error>`.

**Q: tactic에서 오류를 어떻게 발생시키나요?**

**A:** `throwTacticEx <tactic-name> <goal-mvar> <error>`를 사용하세요.

```
elab "faq_throw_error" : tactic =>
  Lean.Elab.Tactic.withMainContext do
    let goal ← Lean.Elab.Tactic.getMainGoal
    Lean.Meta.throwTacticEx `faq_throw_error goal "throwing an error at the current goal"

#check_failure (by faq_throw_error : (b : Bool) → b = true)
-- tactic 'faq_throw_error' failed, throwing an error at the current goal
-- ⊢ ∀ (b : Bool), b = true
```

**Q: What is the difference between `Lean.Elab.Tactic.*` and `Lean.Meta.Tactic.*`?**

A: `Lean.Meta.Tactic.*` contains low level code that uses the `Meta` monad to
implement basic features such as rewriting. `Lean.Elab.Tactic.*` contains
high-level code that connects the low level development in `Lean.Meta` to the
tactic infrastructure and the parsing front-end.

**Q: `Lean.Elab.Tactic.*`와 `Lean.Meta.Tactic.*`의 차이점은 무엇인가요?**

**A:** `Lean.Meta.Tactic.*`는 재작성(rewriting)과 같은 기본 기능을 구현하기 위해 `Meta` 모나드를 사용하는 저수준 코드를 포함합니다. `Lean.Elab.Tactic.*`는 `Lean.Meta`의 저수준 개발을 tactic 인프라와 파싱 프론트엔드에 연결하는 고수준 코드를 포함합니다.


1. Consider the theorem `p ∧ q ↔ q ∧ p`. We could either write its proof as a proof term, or construct it using the tactics.
   When we are writing the proof of this theorem *as a proof term*, we're gradually filling up `_`s with certain expressions, step by step. Each such step corresponds to a tactic.

   There are many combinations of steps in which we could write this proof term - but consider the sequence of steps we wrote below. Please write each step as a tactic.
   The tactic `step_1` is filled in, please do the same for the remaining tactics (for the sake of the exercise, try to use lower-level apis, such as `mkFreshExprMVar`, `mvarId.assign` and `modify fun _ => { goals := ~)`.

1. 정리 `p ∧ q ↔ q ∧ p`를 고려해 보세요. 증명을 증명 항으로 작성하거나 tactic을 사용해 구성할 수 있습니다.
   이 정리의 증명을 *증명 항으로* 작성할 때, 단계별로 `_`들을 특정 표현식으로 점진적으로 채워나갑니다. 각 단계는 tactic에 대응합니다.

   이 증명 항을 작성할 수 있는 단계 조합은 많지만, 아래에 작성한 단계 순서를 고려하세요. 각 단계를 tactic으로 작성하세요.
   `step_1` tactic은 채워져 있으니, 나머지 tactic도 동일하게 채우세요 (연습을 위해 `mkFreshExprMVar`, `mvarId.assign`, `modify fun _ => { goals := ~)` 같은 저수준 API를 사용해 보세요).

   ```
   -- [this is the initial goal]
   example : p ∧ q ↔ q ∧ p :=
     _

   -- step_1
   example : p ∧ q ↔ q ∧ p :=
     Iff.intro _ _

   -- step_2
   example : p ∧ q ↔ q ∧ p :=
     Iff.intro
       (
         fun hA =>
         _
       )
       (
         fun hB =>
         (And.intro hB.right hB.left)
       )

   -- step_3
   example : p ∧ q ↔ q ∧ p :=
     Iff.intro
       (
         fun hA =>
         (And.intro _ _)
       )
       (
         fun hB =>
         (And.intro hB.right hB.left)
       )

   -- step_4
   example : p ∧ q ↔ q ∧ p :=
     Iff.intro
       (
         fun hA =>
         (And.intro hA.right hA.left)
       )
       (
         fun hB =>
         (And.intro hB.right hB.left)
       )
   ```

   ```
   elab "step_1" : tactic => do
     let mvarId ← getMainGoal
     let goalType ← getMainTarget

     let Expr.app (Expr.app (Expr.const `Iff _) a) b := goalType | throwError "Goal type is not of the form `a ↔ b`"

     -- 1. Create new `_`s with appropriate types.
     let mvarId1 ← mkFreshExprMVar (Expr.forallE `xxx a b .default) (userName := "red")
     let mvarId2 ← mkFreshExprMVar (Expr.forallE `yyy b a .default) (userName := "blue")

     -- 2. Assign the main goal to the expression `Iff.intro _ _`.
     mvarId.assign (mkAppN (Expr.const `Iff.intro []) #[a, b, mvarId1, mvarId2])

     -- 3. Report the new `_`s to Lean as the new goals.
     modify fun _ => { goals := [mvarId1.mvarId!, mvarId2.mvarId!] }
   ```

   ```
   theorem gradual (p q : Prop) : p ∧ q ↔ q ∧ p := by
     step_1
     step_2
     step_3
     step_4
   ```
2. In the first exercise, we used lower-level `modify` api to update our goals.
   `liftMetaTactic`, `setGoals`, `appendGoals`, `replaceMainGoal`, `closeMainGoal`, etc. are all syntax sugars on top of `modify fun s : State => { s with goals := myMvarIds }`.
   Please rewrite the `forker` tactic with:

   **a)** `liftMetaTactic`
   **b)** `setGoals`
   **c)** `replaceMainGoal`

2. 첫 번째 연습에서는 목표를 업데이트하기 위해 저수준 `modify` API를 사용했습니다.
   `liftMetaTactic`, `setGoals`, `appendGoals`, `replaceMainGoal`, `closeMainGoal` 등은 모두 `modify fun s : State => { s with goals := myMvarIds }` 위에 있는 구문 설탕입니다.
   다음을 사용하여 `forker` tactic을 재작성하세요:

   **a)** `liftMetaTactic`
   **b)** `setGoals`
   **c)** `replaceMainGoal`

   ```
   elab "forker" : tactic => do
     let mvarId ← getMainGoal
     let goalType ← getMainTarget

     let (Expr.app (Expr.app (Expr.const `And _) p) q) := goalType | Lean.Meta.throwTacticEx `forker mvarId (m!"Goal is not of the form P ∧ Q")

     mvarId.withContext do
       let mvarIdP ← mkFreshExprMVar p (userName := "red")
       let mvarIdQ ← mkFreshExprMVar q (userName := "blue")

       let proofTerm := mkAppN (Expr.const `And.intro []) #[p, q, mvarIdP, mvarIdQ]
       mvarId.assign proofTerm

       modify fun state => { goals := [mvarIdP.mvarId!, mvarIdQ.mvarId!] ++ state.goals.drop 1 }
   ```

   ```
   example (A B C : Prop) : A → B → C → (A ∧ B) ∧ C := by
     intro hA hB hC
     forker
     forker
     assumption
     assumption
     assumption
   ```
3. In the first exercise, you created your own `intro` in `step_2` (with a hardcoded hypothesis name, but the basics are the same). When writing tactics, we usually want to use functions such as `intro`, `intro1`, `intro1P`, `introN` or `introNP`.

   For each of the points below, create a tactic `introductor` (one per each point), that turns the goal `(ab: a = b) → (bc: b = c) → (a = c)`:

   **a)** into the goal `(a = c)` with hypotheses `(ab✝: a = b)` and `(bc✝: b = c)`.
   **b)** into the goal `(bc: b = c) → (a = c)` with hypothesis `(ab: a = b)`.
   **c)** into the goal `(bc: b = c) → (a = c)` with hypothesis `(hello: a = b)`.

   ```
   example (a b c : Nat) : (ab: a = b) → (bc: b = c) → (a = c) := by
     introductor
     sorry
   ```

   Hint: **"P"** in `intro1P` and `introNP` stands for **"Preserve"**.

3. 첫 번째 연습에서 `step_2`에서 자신만의 `intro`를 만들었습니다 (가설 이름이 하드코딩되었지만 기본은 같습니다). tactic을 작성할 때 보통 `intro`, `intro1`, `intro1P`, `introN` 또는 `introNP` 같은 함수를 사용하고 싶습니다.

   아래 각 항목에 대해, 목표 `(ab: a = b) → (bc: b = c) → (a = c)`를 변환하는 tactic `introductor`를 (각 항목마다 하나씩) 만드세요:

   **a)** 가설 `(ab✝: a = b)`와 `(bc✝: b = c)`를 가진 목표 `(a = c)`로.
   **b)** 가설 `(ab: a = b)`를 가진 목표 `(bc: b = c) → (a = c)`로.
   **c)** 가설 `(hello: a = b)`를 가진 목표 `(bc: b = c) → (a = c)`로.

   힌트: `intro1P`와 `introNP`의 **"P"**는 **"Preserve"**를 의미합니다.