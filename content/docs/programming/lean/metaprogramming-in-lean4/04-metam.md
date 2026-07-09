---
title: "MetaM"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "metaprogramming"]
categories: ["programming"]
description: "MetaM 모나드: Lean 4 메타프로그래밍의 핵심 모나드와 메타변수 조작"
---

The Lean 4 metaprogramming API is organised around a small zoo of monads. The
four main ones are:

* `CoreM` gives access to the *environment*, i.e. the set of things that
  have been declared or imported at the current point in the program.
* `MetaM` gives access to the *metavariable context*, i.e. the set of
  metavariables that are currently declared and the values assigned to them (if
  any).
* `TermElabM` gives access to various information used during elaboration.
* `TacticM` gives access to the list of current goals.

These monads extend each other, so a `MetaM` operation also has access to the
environment and a `TermElabM` computation can use metavariables. There are also
other monads which do not neatly fit into this hierarchy, e.g. `CommandElabM`
extends `MetaM` but neither extends nor is extended by `TermElabM`.

This chapter demonstrates a number of useful operations in the `MetaM` monad.
`MetaM` is of particular importance because it allows us to give meaning to
every expression: the environment (from `CoreM`) gives meaning to constants like
`Nat.zero` or `List.map` and the metavariable context gives meaning to both
metavariables and local hypotheses.

Lean 4 메타프로그래밍 API는 소규모 monad 집합을 중심으로 구성되어 있습니다. 주요 네 가지는 다음과 같습니다:

* `CoreM`은 *환경(environment)*, 즉 프로그램의 현재 지점에서 선언되거나 import된 것들의 집합에 접근합니다.
* `MetaM`은 *메타변수 컨텍스트(metavariable context)*, 즉 현재 선언된 메타변수들과 그에 할당된 값(있는 경우)의 집합에 접근합니다.
* `TermElabM`은 정교화(elaboration) 과정에서 사용되는 다양한 정보에 접근합니다.
* `TacticM`은 현재 목표(goal) 목록에 접근합니다.

이 monad들은 서로를 확장하므로, `MetaM` 연산은 환경에도 접근할 수 있고 `TermElabM` 계산은 메타변수를 사용할 수 있습니다. 이 계층 구조에 깔끔하게 맞지 않는 다른 monad들도 있는데, 예를 들어 `CommandElabM`은 `MetaM`을 확장하지만 `TermElabM`을 확장하지도 않고 `TermElabM`에 의해 확장되지도 않습니다.

이 장에서는 `MetaM` monad의 유용한 여러 연산들을 소개합니다. `MetaM`은 특히 중요한데, 그 이유는 모든 표현식에 의미를 부여할 수 있기 때문입니다: 환경(`CoreM`에서)은 `Nat.zero`나 `List.map` 같은 상수에 의미를 부여하고, 메타변수 컨텍스트는 메타변수와 지역 가설(local hypotheses) 모두에 의미를 부여합니다.

```
import Lean

open Lean Lean.Expr Lean.Meta
```


The 'Meta' in `MetaM` refers to metavariables, so we should talk about these
first. Lean users do not usually interact much with metavariables -- at least
not consciously -- but they are used all over the place in metaprograms. There
are two ways to view them: as holes in an expression or as goals.

Take the goal perspective first. When we prove things in Lean, we always operate
on goals, such as

`MetaM`의 'Meta'는 메타변수(metavariables)를 가리키므로, 먼저 이에 대해 이야기해야 합니다. Lean 사용자들은 메타변수와 직접 상호작용하는 경우가 많지 않습니다 -- 적어도 의식적으로는 -- 하지만 메타프로그램에서는 도처에서 사용됩니다. 메타변수를 바라보는 두 가지 관점이 있습니다: 표현식의 빈 구멍(hole)으로 보는 것과 목표(goal)로 보는 것입니다.

먼저 목표의 관점으로 살펴보겠습니다. Lean에서 무언가를 증명할 때, 우리는 항상 다음과 같은 목표(goal)에 대해 작업합니다:

```
n m : Nat
⊢ n + m = m + n
```

These goals are internally represented by metavariables. Accordingly, each
metavariable has a *local context* containing hypotheses (here `[n : Nat, m : Nat]`) and a *target type* (here `n + m = m + n`). Metavariables also have a
unique name, say `m`, and we usually render them as `?m`.

To close a goal, we must give an expression `e` of the target type. The
expression may contain fvars from the metavariable's local context, but no
others. Internally, closing a goal in this way corresponds to *assigning* the
metavariable; we write `?m := e` for this assignment.

The second, complementary view of metavariables is that they represent holes
in an expression. For instance, an application of `Eq.trans` may generate two
goals which look like this:

이러한 목표들은 내부적으로 메타변수로 표현됩니다. 따라서 각 메타변수는 가설(여기서는 `[n : Nat, m : Nat]`)을 포함하는 *지역 컨텍스트(local context)*와 *목표 타입(target type)*(여기서는 `n + m = m + n`)을 가집니다. 메타변수는 또한 고유한 이름(예: `m`)을 가지며, 우리는 보통 이를 `?m`으로 표기합니다.

목표를 닫으려면, 목표 타입의 표현식 `e`를 제공해야 합니다. 표현식은 메타변수의 지역 컨텍스트에 있는 fvar를 포함할 수 있지만, 그 외의 것은 포함할 수 없습니다. 내부적으로, 이런 방식으로 목표를 닫는 것은 메타변수를 *할당(assigning)*하는 것에 해당합니다; 이 할당을 `?m := e`로 표기합니다.

메타변수를 바라보는 두 번째, 보완적인 관점은 표현식의 빈 구멍을 나타낸다는 것입니다. 예를 들어, `Eq.trans`의 적용은 다음과 같은 두 개의 목표를 생성할 수 있습니다:

```
n m : Nat
⊢ n = ?x

n m : Nat
⊢ ?x = m
```

Here `?x` is another metavariable -- a hole in the target types of both goals,
to be filled in later during the proof. The type of `?x` is `Nat` and its local
context is `[n : Nat, m : Nat]`. Now, if we solve the first goal by reflexivity,
then `?x` must be `n`, so we assign `?x := n`. Crucially, this also affects the
second goal: it is "updated" (not really, as we will see) to have target `n = m`. The metavariable `?x` represents the same expression everywhere it occurs.

Tactics use metavariables to communicate the current goals. To see how, consider
this simple (and slightly artificial) proof:

여기서 `?x`는 또 다른 메타변수입니다 -- 두 목표의 목표 타입에 있는 빈 구멍으로, 나중에 증명 과정에서 채워질 것입니다. `?x`의 타입은 `Nat`이고 그 지역 컨텍스트는 `[n : Nat, m : Nat]`입니다. 이제 첫 번째 목표를 반사성(reflexivity)으로 풀면 `?x`는 반드시 `n`이어야 하므로, `?x := n`을 할당합니다. 중요한 것은, 이것이 두 번째 목표에도 영향을 미친다는 점입니다: 두 번째 목표는 목표 타입이 `n = m`이 되도록 "업데이트"됩니다(실제로는 그렇지 않지만, 나중에 살펴볼 것입니다). 메타변수 `?x`는 그것이 등장하는 모든 곳에서 동일한 표현식을 나타냅니다.

tactic은 메타변수를 사용하여 현재 목표를 전달합니다. 이를 이해하기 위해 다음의 간단한(그리고 약간 인위적인) 증명을 살펴보겠습니다:

```
example {α} (a : α) (f : α → α) (h : ∀ a, f a = a) : f (f a) = a := by
  apply Eq.trans
  apply h
  apply h
```

After we enter tactic mode, our ultimate goal is to generate an expression of
type `f (f a) = a` which may involve the hypotheses `α`, `a`, `f` and `h`. So
Lean generates a metavariable `?m1` with target `f (f a) = a` and a local
context containing these hypotheses. This metavariable is passed to the first
`apply` tactic as the current goal.

The `apply` tactic then tries to apply `Eq.trans` and succeeds, generating three
new metavariables:

tactic 모드로 들어가면, 우리의 최종 목표는 가설 `α`, `a`, `f`, `h`를 포함할 수 있는 타입 `f (f a) = a`의 표현식을 생성하는 것입니다. 따라서 Lean은 목표 타입이 `f (f a) = a`이고 이 가설들을 포함하는 지역 컨텍스트를 가진 메타변수 `?m1`을 생성합니다. 이 메타변수는 현재 목표로서 첫 번째 `apply` tactic에 전달됩니다.

그러면 `apply` tactic은 `Eq.trans`를 적용하려 시도하고 성공하여, 세 개의 새로운 메타변수를 생성합니다:

```
...
⊢ f (f a) = ?b

...
⊢ ?b = a

...
⊢ α
```

Call these metavariables `?m2`, `?m3` and `?b`. The last one, `?b`, stands for
the intermediate element of the transitivity proof and occurs in `?m2` and
`?m3`. The local contexts of all metavariables in this proof are the same, so
we omit them.

Having created these metavariables, `apply` assigns

이 메타변수들을 `?m2`, `?m3`, `?b`라고 부르겠습니다. 마지막 `?b`는 추이성(transitivity) 증명의 중간 원소를 나타내며 `?m2`와 `?m3`에 등장합니다. 이 증명에서 모든 메타변수의 지역 컨텍스트는 동일하므로 생략합니다.

이 메타변수들을 생성한 후, `apply`는 다음을 할당합니다:

```
?m1 := @Eq.trans α (f (f a)) ?b a ?m2 ?m3
```

and reports that `?m2`, `?m3` and `?b` are now the current goals.

At this point the second `apply` tactic takes over. It receives `?m2` as the
current goal and applies `h` to it. This succeeds and the tactic assigns `?m2 := h (f a)`. This assignment implies that `?b` must be `f a`, so the tactic also
assigns `?b := f a`. Assigned metavariables are not considered open goals, so
the only goal that remains is `?m3`.

Now the third `apply` comes in. Since `?b` has been assigned, the target of
`?m3` is now `f a = a`. Again, the application of `h` succeeds and the
tactic assigns `?m3 := h a`.

At this point, all metavariables are assigned as follows:

그리고 `?m2`, `?m3`, `?b`가 이제 현재 목표들이라고 보고합니다.

이 시점에서 두 번째 `apply` tactic이 이어받습니다. `?m2`를 현재 목표로 받아 `h`를 적용합니다. 이것이 성공하고 tactic은 `?m2 := h (f a)`를 할당합니다. 이 할당은 `?b`가 반드시 `f a`여야 함을 의미하므로, tactic은 `?b := f a`도 할당합니다. 할당된 메타변수는 열린 목표로 간주되지 않으므로, 남은 유일한 목표는 `?m3`입니다.

이제 세 번째 `apply`가 들어옵니다. `?b`가 할당되었으므로, `?m3`의 목표 타입은 이제 `f a = a`입니다. 다시, `h`의 적용이 성공하고 tactic은 `?m3 := h a`를 할당합니다.

이 시점에서, 모든 메타변수는 다음과 같이 할당되었습니다:

```
?m1 := @Eq.trans α (f (f a)) ?b a ?m2 ?m3
?m2 := h (f a)
?m3 := h a
?b  := f a
```

Exiting the `by` block, Lean constructs the final proof term by taking the
assignment of `?m1` and replacing each metavariable with its assignment. This
yields

`by` 블록을 빠져나올 때, Lean은 `?m1`의 할당을 취하고 각 메타변수를 그 할당값으로 대체하여 최종 증명 항(proof term)을 구성합니다. 이렇게 하면 다음이 생성됩니다:

```
@Eq.trans α (f (f a)) (f a) a (h (f a)) (h a)
```

The example also shows how the two views of metavariables -- as holes in an
expression or as goals -- are related: the goals we get are holes in the final
proof term.

이 예제는 또한 메타변수를 바라보는 두 가지 관점 -- 표현식의 빈 구멍으로 보는 것과 목표로 보는 것 -- 이 어떻게 연관되어 있는지를 보여줍니다: 우리가 얻는 목표들은 최종 증명 항의 빈 구멍들입니다.


Let us make these concepts concrete. When we operate in the `MetaM` monad, we
have read-write access to a `MetavarContext` structure containing information
about the currently declared metavariables. Each metavariable is identified by
an `MVarId` (a unique `Name`). To create a new metavariable, we use
`Lean.Meta.mkFreshExprMVar` with type

이 개념들을 구체적으로 살펴보겠습니다. `MetaM` monad에서 작업할 때, 우리는 현재 선언된 메타변수에 대한 정보를 포함하는 `MetavarContext` 구조체에 읽기-쓰기 접근권을 가집니다. 각 메타변수는 `MVarId`(고유한 `Name`)로 식별됩니다. 새 메타변수를 생성하려면, 다음 타입의 `Lean.Meta.mkFreshExprMVar`를 사용합니다:

```
mkFreshExprMVar (type? : Option Expr) (kind := MetavarKind.natural)
    (userName := Name.anonymous) : MetaM Expr
```

Its arguments are:

* `type?`: the target type of the new metavariable. If `none`, the target type
  is `Sort ?u`, where `?u` is a universe level metavariable. (This is a special
  class of metavariables for universe levels, distinct from the expression
  metavariables which we have been calling simply "metavariables".)
* `kind`: the metavariable kind. See the [Metavariable Kinds
  section](#metavariable-kinds) (but the default is usually correct).
* `userName`: the new metavariable's user-facing name. This is what gets printed
  when the metavariable appears in a goal. Unlike the `MVarId`, this name does
  not need to be unique.

The returned `Expr` is always a metavariable. We can use `Lean.Expr.mvarId!` to
extract the `MVarId`, which is guaranteed to be unique. (Arguably
`mkFreshExprMVar` should just return the `MVarId`.)

The local context of the new metavariable is inherited from the current local
context, more about which in the next section. If you want to give a different
local context, use `Lean.Meta.mkFreshExprMVarAt`.

Metavariables are initially unassigned. To assign them, use
`Lean.MVarId.assign` with type

인수들은 다음과 같습니다:

* `type?`: 새 메타변수의 목표 타입입니다. `none`이면, 목표 타입은 `Sort ?u`가 되는데, 여기서 `?u`는 우주 레벨(universe level) 메타변수입니다. (이것은 우주 레벨을 위한 특별한 메타변수 클래스로, 우리가 단순히 "메타변수"라고 불러온 표현식 메타변수와는 구별됩니다.)
* `kind`: 메타변수 종류입니다. [메타변수 종류 섹션](#metavariable-kinds)을 참조하세요(기본값이 보통 정확합니다).
* `userName`: 새 메타변수의 사용자 표시 이름입니다. 메타변수가 목표에 나타날 때 출력되는 이름입니다. `MVarId`와 달리, 이 이름은 고유할 필요가 없습니다.

반환된 `Expr`은 항상 메타변수입니다. `Lean.Expr.mvarId!`를 사용하여 `MVarId`를 추출할 수 있으며, 이는 고유성이 보장됩니다. (논란의 여지가 있지만, `mkFreshExprMVar`는 그냥 `MVarId`를 반환해야 할 것입니다.)

새 메타변수의 지역 컨텍스트는 현재 지역 컨텍스트로부터 상속됩니다. 이에 대해서는 다음 섹션에서 더 자세히 설명합니다. 다른 지역 컨텍스트를 지정하려면 `Lean.Meta.mkFreshExprMVarAt`을 사용하세요.

메타변수는 처음에 할당되지 않은 상태입니다. 메타변수를 할당하려면, 다음 타입의 `Lean.MVarId.assign`을 사용합니다:

```
assign (mvarId : MVarId) (val : Expr) : MetaM Unit
```

This updates the `MetavarContext` with the assignment `?mvarId := val`. You must
make sure that `mvarId` is not assigned yet (or that the old assignment is
definitionally equal to the new assignment). You must also make sure that the
assigned value, `val`, has the right type. This means (a) that `val` must have
the target type of `mvarId` and (b) that `val` must only contain fvars from the
local context of `mvarId`.

If you `#check Lean.MVarId.assign`, you will see that its real type is more
general than the one we showed above: it works in any monad that has access to a
`MetavarContext`. But `MetaM` is by far the most important such monad, so in
this chapter, we specialise the types of `assign` and similar functions.

To get information about a declared metavariable, use `Lean.MVarId.getDecl`.
Given an `MVarId`, this returns a `MetavarDecl` structure. (If no metavariable
with the given `MVarId` is declared, the function throws an exception.) The
`MetavarDecl` contains information about the metavariable, e.g. its type, local
context and user-facing name. This function has some convenient variants, such
as `Lean.MVarId.getType`.

To get the current assignment of a metavariable (if any), use
`Lean.getExprMVarAssignment?`. To check whether a metavariable is assigned, use
`Lean.MVarId.isAssigned`. However, these functions are relatively rarely
used in tactic code because we usually prefer a more powerful operation:
`Lean.Meta.instantiateMVars` with type

이것은 `?mvarId := val` 할당으로 `MetavarContext`를 업데이트합니다. `mvarId`가 아직 할당되지 않았는지(또는 이전 할당이 새 할당과 정의적으로 동등한지) 반드시 확인해야 합니다. 또한 할당된 값 `val`이 올바른 타입을 가지고 있는지 확인해야 합니다. 이는 (a) `val`이 `mvarId`의 목표 타입을 가져야 하고, (b) `val`이 `mvarId`의 지역 컨텍스트에 있는 fvar만 포함해야 함을 의미합니다.

`#check Lean.MVarId.assign`을 확인하면, 실제 타입이 위에서 보여준 것보다 더 일반적임을 알 수 있습니다: `MetavarContext`에 접근할 수 있는 임의의 monad에서 작동합니다. 하지만 `MetaM`이 단연 가장 중요한 monad이므로, 이 장에서는 `assign`과 유사한 함수들의 타입을 특수화합니다.

선언된 메타변수에 대한 정보를 얻으려면, `Lean.MVarId.getDecl`을 사용합니다. `MVarId`가 주어지면, 이것은 `MetavarDecl` 구조체를 반환합니다. (주어진 `MVarId`로 선언된 메타변수가 없으면, 함수는 예외를 던집니다.) `MetavarDecl`은 메타변수에 대한 정보, 예를 들어 타입, 지역 컨텍스트, 사용자 표시 이름 등을 포함합니다. 이 함수에는 `Lean.MVarId.getType`과 같은 편리한 변형들이 있습니다.

메타변수의 현재 할당값을 얻으려면(있는 경우), `Lean.getExprMVarAssignment?`를 사용합니다. 메타변수가 할당되었는지 확인하려면, `Lean.MVarId.isAssigned`를 사용합니다. 하지만 이 함수들은 tactic 코드에서 상대적으로 드물게 사용되는데, 우리가 보통 더 강력한 연산을 선호하기 때문입니다: 다음 타입의 `Lean.Meta.instantiateMVars`입니다:

```
instantiateMVars : Expr → MetaM Expr
```

Given an expression `e`, `instantiateMVars` replaces any assigned metavariable
`?m` in `e` with its assigned value. Unassigned metavariables remain as they
are.

This operation should be used liberally. When we assign a metavariable, existing
expressions containing this metavariable are not immediately updated. This is a
problem when, for example, we match on an expression to check whether it is an
equation. Without `instantiateMVars`, we might miss the fact that the expression
`?m`, where `?m` happens to be assigned to `0 = n`, represents an equation. In
other words, `instantiateMVars` brings our expressions up to date with the
current metavariable state.

Instantiating metavariables requires a full traversal of the input expression,
so it can be somewhat expensive. But if the input expression does not contain
any metavariables, `instantiateMVars` is essentially free. Since this is the
common case, liberal use of `instantiateMVars` is fine in most situations.

Before we go on, here is a synthetic example demonstrating how the basic
metavariable operations are used. More natural examples appear in the following
sections.

표현식 `e`가 주어지면, `instantiateMVars`는 `e` 안의 할당된 메타변수 `?m`을 그 할당값으로 대체합니다. 할당되지 않은 메타변수는 그대로 남습니다.

이 연산은 자유롭게 사용해야 합니다. 메타변수를 할당할 때, 해당 메타변수를 포함하는 기존 표현식은 즉시 업데이트되지 않습니다. 이것은 예를 들어, 표현식이 방정식인지 확인하기 위해 패턴 매칭할 때 문제가 됩니다. `instantiateMVars` 없이는, `?m`이 `0 = n`에 할당되어 있는 경우에 표현식 `?m`이 방정식을 나타낸다는 사실을 놓칠 수 있습니다. 다시 말해, `instantiateMVars`는 우리의 표현식들을 현재 메타변수 상태에 맞게 최신화합니다.

메타변수를 인스턴스화하려면 입력 표현식을 완전히 순회해야 하므로 다소 비용이 들 수 있습니다. 하지만 입력 표현식에 메타변수가 없다면, `instantiateMVars`는 사실상 비용이 없습니다. 이것이 일반적인 경우이므로, 대부분의 상황에서 `instantiateMVars`를 자유롭게 사용해도 괜찮습니다.

계속 진행하기 전에, 기본 메타변수 연산이 어떻게 사용되는지를 보여주는 합성 예제를 소개합니다. 더 자연스러운 예제들은 다음 섹션에서 등장합니다.

```
#eval show MetaM Unit from do
  -- Create two fresh metavariables of type `Nat`.
  let mvar1 ← mkFreshExprMVar (Expr.const ``Nat []) (userName := `mvar1)
  let mvar2 ← mkFreshExprMVar (Expr.const ``Nat []) (userName := `mvar2)
  -- Create a fresh metavariable of type `Nat → Nat`. The `mkArrow` function
  -- creates a function type.
  let mvar3 ← mkFreshExprMVar (← mkArrow (.const ``Nat []) (.const ``Nat []))
    (userName := `mvar3)

  -- Define a helper function that prints each metavariable.
  let printMVars : MetaM Unit := do
    IO.println s!"  meta1: {← instantiateMVars mvar1}"
    IO.println s!"  meta2: {← instantiateMVars mvar2}"
    IO.println s!"  meta3: {← instantiateMVars mvar3}"

  IO.println "Initially, all metavariables are unassigned:"
  printMVars

  -- Assign `mvar1 : Nat := ?mvar3 ?mvar2`.
  mvar1.mvarId!.assign (.app mvar3 mvar2)
  IO.println "After assigning mvar1:"
  printMVars

  -- Assign `mvar2 : Nat := 0`.
  mvar2.mvarId!.assign (.const ``Nat.zero [])
  IO.println "After assigning mvar2:"
  printMVars

  -- Assign `mvar3 : Nat → Nat := Nat.succ`.
  mvar3.mvarId!.assign (.const ``Nat.succ [])
  IO.println "After assigning mvar3:"
  printMVars
-- Initially, all metavariables are unassigned:
--   meta1: ?_uniq.1
--   meta2: ?_uniq.2
--   meta3: ?_uniq.3
-- After assigning mvar1:
--   meta1: ?_uniq.3 ?_uniq.2
--   meta2: ?_uniq.2
--   meta3: ?_uniq.3
-- After assigning mvar2:
--   meta1: ?_uniq.3 Nat.zero
--   meta2: Nat.zero
--   meta3: ?_uniq.3
-- After assigning mvar3:
--   meta1: Nat.succ Nat.zero
--   meta2: Nat.zero
--   meta3: Nat.succ
```


Consider the expression `e` which refers to the free variable with unique name
`h`:

```
e := .fvar (FVarId.mk `h)
```

What is the type of this expression? The answer depends on the local context in
which `e` is interpreted. One local context may declare that `h` is a local
hypothesis of type `Nat`; another local context may declare that `h` is a local
definition with value `List.map`.

Thus, expressions are only meaningful if they are interpreted in the local
context for which they were intended. And as we saw, each metavariable has its
own local context. So in principle, functions which manipulate expressions
should have an additional `MVarId` argument specifying the goal in which the
expression should be interpreted.

That would be cumbersome, so Lean goes a slightly different route. In `MetaM`,
we always have access to an ambient `LocalContext`, obtained with `Lean.getLCtx`
of type

고유한 이름 `h`를 가진 자유 변수를 참조하는 표현식 `e`를 생각해 봅시다:


이 표현식의 타입은 무엇일까요? 답은 `e`가 해석되는 지역 컨텍스트에 따라 다릅니다. 한 지역 컨텍스트는 `h`가 `Nat` 타입의 지역 가설이라고 선언할 수도 있고, 다른 지역 컨텍스트는 `h`가 `List.map` 값을 가진 지역 정의라고 선언할 수도 있습니다.

따라서, 표현식은 그것이 의도된 지역 컨텍스트에서 해석될 때만 의미가 있습니다. 그리고 보았듯이, 각 메타변수는 자체 지역 컨텍스트를 가집니다. 원칙적으로, 표현식을 조작하는 함수들은 표현식이 해석될 목표를 지정하는 추가적인 `MVarId` 인수를 가져야 합니다.

이것은 번거로울 것이므로, Lean은 약간 다른 방식을 택합니다. `MetaM`에서, 우리는 항상 다음 타입의 `Lean.getLCtx`로 얻은 주변 `LocalContext`에 접근할 수 있습니다:

```
getLCtx : MetaM LocalContext
```

All operations involving fvars use this ambient local context.

The downside of this setup is that we always need to update the ambient local
context to match the goal we are currently working on. To do this, we use
`Lean.MVarId.withContext` of type

fvar와 관련된 모든 연산은 이 주변 지역 컨텍스트를 사용합니다.

이 설정의 단점은 현재 작업 중인 목표와 일치하도록 주변 지역 컨텍스트를 항상 업데이트해야 한다는 것입니다. 이를 위해, 다음 타입의 `Lean.MVarId.withContext`를 사용합니다:

```
withContext (mvarId : MVarId) (c : MetaM α) : MetaM α
```

This function takes a metavariable `mvarId` and a `MetaM` computation `c` and
executes `c` with the ambient context set to the local context of `mvarId`. A
typical use case looks like this:

이 함수는 메타변수 `mvarId`와 `MetaM` 계산 `c`를 받아, 주변 컨텍스트를 `mvarId`의 지역 컨텍스트로 설정한 상태에서 `c`를 실행합니다. 전형적인 사용 패턴은 다음과 같습니다:

```
def someTactic (mvarId : MVarId) ... : ... :=
  mvarId.withContext do
    ...
```

The tactic receives the current goal as the metavariable `mvarId` and
immediately sets the current local context. Any operations within the `do` block
then use the local context of `mvarId`.

Once we have the local context properly set, we can manipulate fvars. Like
metavariables, fvars are identified by an `FVarId` (a unique `Name`). Basic
operations include:

* `Lean.FVarId.getDecl : FVarId → MetaM LocalDecl` retrieves the declaration
  of a local hypothesis. As with metavariables, a `LocalDecl` contains all
  information pertaining to the local hypothesis, e.g. its type and its
  user-facing name.
* `Lean.Meta.getLocalDeclFromUserName : Name → MetaM LocalDecl` retrieves the
  declaration of the local hypothesis with the given user-facing name. If there
  are multiple such hypotheses, the bottommost one is returned. If there is
  none, an exception is thrown.

We can also iterate over all hypotheses in the local context, using the `ForIn`
instance of `LocalContext`. A typical pattern is this:

tactic은 현재 목표를 메타변수 `mvarId`로 받아 즉시 현재 지역 컨텍스트를 설정합니다. `do` 블록 내의 모든 연산은 그 이후 `mvarId`의 지역 컨텍스트를 사용합니다.

지역 컨텍스트가 올바르게 설정되면, fvar을 조작할 수 있습니다. 메타변수와 마찬가지로, fvar은 `FVarId`(고유한 `Name`)로 식별됩니다. 기본 연산들은 다음과 같습니다:

* `Lean.FVarId.getDecl : FVarId → MetaM LocalDecl`은 지역 가설의 선언을 가져옵니다. 메타변수와 마찬가지로, `LocalDecl`은 지역 가설에 관한 모든 정보(예: 타입과 사용자 표시 이름)를 포함합니다.
* `Lean.Meta.getLocalDeclFromUserName : Name → MetaM LocalDecl`은 주어진 사용자 표시 이름을 가진 지역 가설의 선언을 가져옵니다. 그런 가설이 여러 개 있으면, 가장 아래에 있는 것이 반환됩니다. 없으면, 예외가 던져집니다.

`LocalContext`의 `ForIn` 인스턴스를 사용하여 지역 컨텍스트의 모든 가설을 순회할 수도 있습니다. 전형적인 패턴은 다음과 같습니다:

```
for ldecl in ← getLCtx do
  if ldecl.isImplementationDetail then
    continue
  -- do something with the ldecl
```

The loop iterates over every `LocalDecl` in the context. The
`isImplementationDetail` check skips local hypotheses which are 'implementation
details', meaning they are introduced by Lean or by tactics for bookkeeping
purposes. They are not shown to users and tactics are expected to ignore them.

At this point, we can build the `MetaM` part of an `assumption` tactic:

이 루프는 컨텍스트의 모든 `LocalDecl`을 순회합니다. `isImplementationDetail` 검사는 '구현 세부사항(implementation details)'인 지역 가설들을 건너뜁니다. 이것들은 Lean이나 tactic이 내부 관리 목적으로 도입한 것으로, 사용자에게는 표시되지 않으며 tactic들은 이를 무시해야 합니다.

이 시점에서, `assumption` tactic의 `MetaM` 부분을 구현할 수 있습니다:

```
def myAssumption (mvarId : MVarId) : MetaM Bool := do
  -- Check that `mvarId` is not already assigned.
  mvarId.checkNotAssigned `myAssumption
  -- Use the local context of `mvarId`.
  mvarId.withContext do
    -- The target is the type of `mvarId`.
    let target ← mvarId.getType
    -- For each hypothesis in the local context:
    for ldecl in ← getLCtx do
      -- If the hypothesis is an implementation detail, skip it.
      if ldecl.isImplementationDetail then
        continue
      -- If the type of the hypothesis is definitionally equal to the target
      -- type:
      if ← isDefEq ldecl.type target then
        -- Use the local hypothesis to prove the goal.
        mvarId.assign ldecl.toExpr
        -- Stop and return true.
        return true
    -- If we have not found any suitable local hypothesis, return false.
    return false
```

The `myAssumption` tactic contains three functions we have not seen before:

* `Lean.MVarId.checkNotAssigned` checks that a metavariable is not already
  assigned. The 'myAssumption' argument is the name of the current tactic. It is
  used to generate a nicer error message.
* `Lean.Meta.isDefEq` checks whether two definitions are definitionally equal.
  See the [Definitional Equality section](#definitional-equality).
* `Lean.LocalDecl.toExpr` is a helper function which constructs the `fvar`
  expression corresponding to a local hypothesis.

`myAssumption` tactic은 이전에 보지 못한 세 가지 함수를 포함합니다:

* `Lean.MVarId.checkNotAssigned`는 메타변수가 이미 할당되지 않았는지 확인합니다. 'myAssumption' 인수는 현재 tactic의 이름으로, 더 나은 오류 메시지를 생성하는 데 사용됩니다.
* `Lean.Meta.isDefEq`는 두 정의가 정의적으로 동등한지 확인합니다. [정의적 동등성 섹션](#definitional-equality)을 참조하세요.
* `Lean.LocalDecl.toExpr`는 지역 가설에 해당하는 `fvar` 표현식을 구성하는 도우미 함수입니다.


The above discussion of metavariable assignment contains a lie by omission:
there are actually two ways to assign a metavariable. We have seen the regular
way; the other way is called a *delayed assignment*.

We do not discuss delayed assignments in any detail here since they are rarely
useful for tactic writing. If you want to learn more about them, see the
comments in `MetavarContext.lean` in the Lean standard library. But they create
two complications which you should be aware of.

First, delayed assignments make `Lean.MVarId.isAssigned` and
`getExprMVarAssignment?` medium-calibre footguns. These functions only check for
regular assignments, so you may need to use `Lean.MVarId.isDelayedAssigned`
and `Lean.Meta.getDelayedMVarAssignment?` as well.

Second, delayed assignments break an intuitive invariant. You may have assumed
that any metavariable which remains in the output of `instantiateMVars` is
unassigned, since the assigned metavariables have been substituted. But delayed
metavariables can only be substituted once their assigned value contains no
unassigned metavariables. So delayed-assigned metavariables can appear in an
expression even after `instantiateMVars`.

Metavariable depth is also a niche feature, but one that is occasionally useful.
Any metavariable has a *depth* (a natural number), and a `MetavarContext` has a
corresponding depth as well. Lean only assigns a metavariable if its depth is
equal to the depth of the current `MetavarContext`. Newly created metavariables
inherit the `MetavarContext`'s depth, so by default every metavariable is
assignable.

This setup can be used when a tactic needs some temporary metavariables and also
needs to make sure that other, non-temporary metavariables will not be assigned.
To ensure this, the tactic proceeds as follows:

1. Save the current `MetavarContext`.
2. Increase the depth of the `MetavarContext`.
3. Perform whatever computation is necessary, possibly creating and assigning
   metavariables. Newly created metavariables are at the current depth of the
   `MetavarContext` and so can be assigned. Old metavariables are at a lower
   depth, so cannot be assigned.
4. Restore the saved `MetavarContext`, thereby erasing all the temporary
   metavariables and resetting the `MetavarContext` depth.

This pattern is encapsulated in `Lean.Meta.withNewMCtxDepth`.

위의 메타변수 할당에 대한 논의에는 누락으로 인한 거짓말이 있습니다: 실제로 메타변수를 할당하는 두 가지 방법이 있습니다. 우리는 일반적인 방법을 살펴봤습니다; 다른 방법은 *지연 할당(delayed assignment)*이라고 합니다.

지연 할당은 tactic 작성에서 거의 유용하지 않으므로 여기서 자세히 논의하지 않습니다. 더 알고 싶다면, Lean 표준 라이브러리의 `MetavarContext.lean`에 있는 주석을 참조하세요. 하지만 알아야 할 두 가지 복잡성을 만들어냅니다.

첫째, 지연 할당은 `Lean.MVarId.isAssigned`와 `getExprMVarAssignment?`를 중간 수준의 위험 함수로 만듭니다. 이 함수들은 일반 할당만 확인하므로, `Lean.MVarId.isDelayedAssigned`와 `Lean.Meta.getDelayedMVarAssignment?`도 사용해야 할 수 있습니다.

둘째, 지연 할당은 직관적인 불변성을 깨뜨립니다. 할당된 메타변수들이 대체되었으므로, `instantiateMVars`의 출력에 남아있는 메타변수는 할당되지 않은 것이라고 가정했을 수 있습니다. 하지만 지연 메타변수는 그 할당값에 할당되지 않은 메타변수가 없을 때에만 대체될 수 있습니다. 따라서 지연 할당된 메타변수는 `instantiateMVars` 이후에도 표현식에 나타날 수 있습니다.

메타변수 깊이(metavariable depth)도 틈새 기능이지만 가끔 유용합니다. 모든 메타변수는 *깊이(depth)*(자연수)를 가지며, `MetavarContext`도 대응하는 깊이를 가집니다. Lean은 메타변수의 깊이가 현재 `MetavarContext`의 깊이와 같을 때만 메타변수를 할당합니다. 새로 생성된 메타변수는 `MetavarContext`의 깊이를 상속하므로, 기본적으로 모든 메타변수는 할당 가능합니다.

이 설정은 tactic이 임시 메타변수가 필요하면서도 다른 비임시 메타변수가 할당되지 않도록 보장해야 할 때 사용할 수 있습니다. 이를 보장하기 위해 tactic은 다음과 같이 진행합니다:

1. 현재 `MetavarContext`를 저장합니다.
2. `MetavarContext`의 깊이를 증가시킵니다.
3. 필요한 계산을 수행하고, 메타변수를 생성하고 할당할 수 있습니다. 새로 생성된 메타변수는 `MetavarContext`의 현재 깊이에 있으므로 할당 가능합니다. 이전 메타변수들은 더 낮은 깊이에 있으므로 할당될 수 없습니다.
4. 저장된 `MetavarContext`를 복원하여, 모든 임시 메타변수를 지우고 `MetavarContext` 깊이를 초기화합니다.

이 패턴은 `Lean.Meta.withNewMCtxDepth`에 캡슐화되어 있습니다.


Computation is a core concept of dependent type theory. The terms `2`, `Nat.succ 1` and `1 + 1` are all "the same" in the sense that they compute the same value.
We call them *definitionally equal*. The problem with this, from a
metaprogramming perspective, is that definitionally equal terms may be
represented by entirely different expressions, but our users would usually
expect that a tactic which works for `2` also works for `1 + 1`. So when we
write our tactics, we must do additional work to ensure that definitionally
equal terms are treated similarly.

계산(computation)은 의존 타입 이론(dependent type theory)의 핵심 개념입니다. `2`, `Nat.succ 1`, `1 + 1`이라는 항(term)들은 모두 같은 값을 계산한다는 의미에서 "동일"합니다. 우리는 이를 *정의적으로 동등(definitionally equal)*하다고 합니다. 메타프로그래밍 관점에서의 문제는, 정의적으로 동등한 항들이 완전히 다른 표현식으로 나타날 수 있지만, 사용자들은 보통 `2`에 작동하는 tactic이 `1 + 1`에도 작동하기를 기대한다는 것입니다. 따라서 tactic을 작성할 때, 정의적으로 동등한 항들이 유사하게 처리되도록 추가 작업을 해야 합니다.


The simplest thing we can do with computation is to bring a term into normal
form. With some exceptions for numeric types, the normal form of a term `t` of
type `T` is a sequence of applications of `T`'s constructors. E.g. the normal
form of a list is a sequence of applications of `List.cons` and `List.nil`.

The function that normalises a term (i.e. brings it into normal form) is
`Lean.Meta.reduce` with type signature

계산으로 할 수 있는 가장 간단한 것은 항(term)을 정규형(normal form)으로 만드는 것입니다. 수치 타입에 대한 몇 가지 예외를 제외하고, 타입 `T`의 항 `t`의 정규형은 `T`의 생성자들의 연속적인 적용입니다. 예를 들어, 리스트의 정규형은 `List.cons`와 `List.nil`의 연속적인 적용입니다.

항을 정규화하는(즉, 정규형으로 만드는) 함수는 다음 타입 시그니처를 가진 `Lean.Meta.reduce`입니다:

```
reduce (e : Expr) (explicitOnly skipTypes skipProofs := true) : MetaM Expr
```

We can use it like this:

```
def someNumber : Nat := (· + 2) $ 3

#eval Expr.const ``someNumber []
-- Lean.Expr.const `someNumber []

#eval reduce (Expr.const ``someNumber [])
-- Lean.Expr.lit (Lean.Literal.natVal 5)
```

Incidentally, this shows that the normal form of a term of type `Nat` is not
always an application of the constructors of `Nat`; it can also be a literal.
Also note that `#eval` can be used not only to evaluate a term, but also to
execute a `MetaM` program.

The optional arguments of `reduce` allow us to skip certain parts of an
expression. E.g. `reduce e (explicitOnly := true)` does not normalise any
implicit arguments in the expression `e`. This yields better performance: since
normal forms can be very big, it may be a good idea to skip parts of an
expression that the user is not going to see anyway.

The `#reduce` command is essentially an application of `reduce`:

부수적으로, 이것은 `Nat` 타입 항의 정규형이 항상 `Nat`의 생성자 적용인 것은 아님을 보여줍니다; 리터럴이 될 수도 있습니다. 또한 `#eval`은 항을 평가할 뿐만 아니라 `MetaM` 프로그램을 실행하는 데도 사용할 수 있다는 점을 주목하세요.

`reduce`의 선택적 인수들은 표현식의 특정 부분을 건너뛸 수 있게 해줍니다. 예를 들어 `reduce e (explicitOnly := true)`는 표현식 `e`의 암시적 인수들을 정규화하지 않습니다. 이는 더 나은 성능을 제공합니다: 정규형이 매우 클 수 있으므로, 어차피 사용자가 볼 수 없는 표현식의 일부를 건너뛰는 것이 좋은 방법일 수 있습니다.

`#reduce` 명령은 본질적으로 `reduce`의 적용입니다:

```
#reduce someNumber
-- 5
```


An ugly but important detail of Lean 4 metaprogramming is that any given
expression does not have a single normal form. Rather, it has a normal form up
to a given *transparency*.

A transparency is a value of `Lean.Meta.TransparencyMode`, an enumeration with
four values: `reducible`, `instances`, `default` and `all`. Any `MetaM`
computation has access to an ambient `TransparencyMode` which can be obtained
with `Lean.Meta.getTransparency`.

The current transparency determines which constants get unfolded during
normalisation, e.g. by `reduce`. (To unfold a constant means to replace it with
its definition.) The four settings unfold progressively more constants:

* `reducible`: unfold only constants tagged with the `@[reducible]` attribute.
  Note that `abbrev` is a shorthand for `@[reducible] def`.
* `instances`: unfold reducible constants and constants tagged with the
  `@[instance]` attribute. Again, the `instance` command is a shorthand for
  `@[instance] def`.
* `default`: unfold all constants except those tagged as `@[irreducible]`.
* `all`: unfold all constants, even those tagged as `@[irreducible]`.

The ambient transparency is usually `default`. To execute an operation with a
specific transparency, use `Lean.Meta.withTransparency`. There are also
shorthands for specific transparencies, e.g. `Lean.Meta.withReducible`.

Putting everything together for an example (where we use `Lean.Meta.ppExpr` to
pretty-print an expression):

Lean 4 메타프로그래밍의 번잡하지만 중요한 세부사항은 주어진 표현식이 단일한 정규형을 가지지 않는다는 것입니다. 오히려, 주어진 *투명도(transparency)*에 따른 정규형을 가집니다.

투명도는 `Lean.Meta.TransparencyMode`의 값으로, 네 가지 값: `reducible`, `instances`, `default`, `all`을 가진 열거형입니다. 모든 `MetaM` 계산은 `Lean.Meta.getTransparency`로 얻을 수 있는 주변 `TransparencyMode`에 접근할 수 있습니다.

현재 투명도는 정규화 중 (예: `reduce`에 의해) 어떤 상수들이 펼쳐지는지를 결정합니다. (상수를 펼친다는 것은 그것을 그 정의로 대체하는 것을 의미합니다.) 네 가지 설정은 점진적으로 더 많은 상수를 펼칩니다:

* `reducible`: `@[reducible]` 속성이 태그된 상수들만 펼칩니다. `abbrev`는 `@[reducible] def`의 약어임을 주목하세요.
* `instances`: reducible 상수들과 `@[instance]` 속성이 태그된 상수들을 펼칩니다. 마찬가지로, `instance` 명령은 `@[instance] def`의 약어입니다.
* `default`: `@[irreducible]`로 태그된 것들을 제외한 모든 상수를 펼칩니다.
* `all`: `@[irreducible]`로 태그된 것들도 포함하여 모든 상수를 펼칩니다.

주변 투명도는 보통 `default`입니다. 특정 투명도로 연산을 실행하려면, `Lean.Meta.withTransparency`를 사용합니다. 특정 투명도에 대한 약어들도 있습니다(예: `Lean.Meta.withReducible`).

모든 것을 합쳐서 예제를 살펴보겠습니다(여기서 표현식을 예쁘게 출력하기 위해 `Lean.Meta.ppExpr`를 사용합니다):

```
def traceConstWithTransparency (md : TransparencyMode) (c : Name) :
    MetaM Format := do
  ppExpr (← withTransparency md $ reduce (.const c []))

@[irreducible] def irreducibleDef : Nat      := 1
def                defaultDef     : Nat      := irreducibleDef + 1
abbrev             reducibleDef   : Nat      := defaultDef + 1
```

We start with `reducible` transparency, which only unfolds `reducibleDef`:

`reducibleDef`만 펼치는 `reducible` 투명도로 시작합니다:

```
#eval traceConstWithTransparency .reducible ``reducibleDef
-- defaultDef + 1
```

If we repeat the above command but let Lean print implicit arguments as well,
we can see that the `+` notation amounts to an application of the `hAdd`
function, which is a member of the `HAdd` typeclass:

위 명령을 반복하되 Lean이 암시적 인수도 출력하도록 하면, `+` 표기법이 `HAdd` 타입클래스의 멤버인 `hAdd` 함수의 적용에 해당함을 알 수 있습니다:

```
set_option pp.explicit true in
#eval traceConstWithTransparency .reducible ``reducibleDef
-- @HAdd.hAdd Nat Nat Nat (@instHAdd Nat instAddNat) defaultDef 1
```

When we reduce with `instances` transparency, this applications is unfolded and
replaced by `Nat.add`:

`instances` 투명도로 줄이면, 이 적용이 펼쳐지고 `Nat.add`로 대체됩니다:

```
#eval traceConstWithTransparency .instances ``reducibleDef
-- Nat.add defaultDef 1
```

With `default` transparency, `Nat.add` is unfolded as well:

`default` 투명도에서는 `Nat.add`도 펼쳐집니다:

```
#eval traceConstWithTransparency .default ``reducibleDef
-- Nat.succ (Nat.succ irreducibleDef)
```

And with `TransparencyMode.all`, we're finally able to unfold `irreducibleDef`:

그리고 `TransparencyMode.all`로는 마침내 `irreducibleDef`를 펼칠 수 있습니다:

```
#eval traceConstWithTransparency .all ``reducibleDef
-- 3
```

The `#eval` commands illustrate that the same term, `reducibleDef`, can have a
different normal form for each transparency.

Why all this ceremony? Essentially for performance: if we allowed normalisation
to always unfold every constant, operations such as type class search would
become prohibitively expensive. The tradeoff is that we must choose the
appropriate transparency for each operation that involves normalisation.

`#eval` 명령들은 같은 항 `reducibleDef`가 각 투명도에 대해 다른 정규형을 가질 수 있음을 보여줍니다.

왜 이 모든 의식이 필요할까요? 본질적으로 성능 때문입니다: 정규화가 항상 모든 상수를 펼치도록 허용한다면, 타입 클래스 탐색 같은 연산은 엄청나게 비용이 비싸질 것입니다. 그 대가는 정규화를 포함하는 각 연산에 적절한 투명도를 선택해야 한다는 것입니다.


Transparency addresses some of the performance issues with normalisation. But
even more important is to recognise that for many purposes, we don't need to
fully normalise terms at all. Suppose we are building a tactic that
automatically splits hypotheses of the type `P ∧ Q`. We might want this tactic
to recognise a hypothesis `h : X` if `X` reduces to `P ∧ Q`. But if `P`
additionally reduces to `Y ∨ Z`, the specific `Y` and `Z` do not concern us.
Reducing `P` would be unnecessary work.

This situation is so common that the fully normalising `reduce` is in fact
rarely used. Instead, the normalisation workhorse of Lean is `whnf`, which
reduces an expression to *weak head normal form* (WHNF).

Roughly speaking, an expression `e` is in weak-head normal form when it has the
form

투명도는 정규화에서의 몇 가지 성능 문제를 해결합니다. 하지만 더 중요한 것은, 많은 목적을 위해 항을 완전히 정규화할 필요가 전혀 없다는 것을 인식하는 것입니다. `P ∧ Q` 형태의 가설을 자동으로 분리하는 tactic을 구축한다고 가정해봅시다. `X`가 `P ∧ Q`로 줄어드는 경우, 이 tactic이 가설 `h : X`를 인식하기를 원할 수 있습니다. 하지만 `P`가 추가로 `Y ∨ Z`로 줄어든다면, 구체적인 `Y`와 `Z`는 우리의 관심사가 아닙니다. `P`를 줄이는 것은 불필요한 작업이 될 것입니다.

이 상황은 매우 흔하므로, 완전히 정규화하는 `reduce`는 실제로 거의 사용되지 않습니다. 대신, Lean의 정규화 핵심 도구는 표현식을 *약한 헤드 정규형(weak head normal form, WHNF)*으로 줄이는 `whnf`입니다.

대략적으로 말해서, 표현식 `e`는 다음 형태를 가질 때 약한 헤드 정규형입니다:

```
e = f x₁ ... xₙ   (n ≥ 0)
```

and `f` cannot be reduced (at the current transparency). To conveniently check
the WHNF of an expression, we define a function `whnf'`, using some functions
that will be discussed in the Elaboration chapter.

그리고 `f`는 (현재 투명도에서) 축약될 수 없습니다. 표현식의 WHNF를 편리하게 확인하기 위해, Elaboration 장에서 논의될 함수들을 사용하여 함수 `whnf'`를 정의합니다.

```
open Lean.Elab.Term in
def whnf' (e : TermElabM Syntax) : TermElabM Format := do
  let e ← elabTermAndSynthesize (← e) none
  ppExpr (← whnf e)
```

Now, here are some examples of expressions in WHNF.

Constructor applications are in WHNF (with some exceptions for numeric types):

이제 WHNF인 표현식들의 예를 살펴봅시다.

생성자 적용은 WHNF입니다(수치 타입에 대한 몇 가지 예외 있음):

```
#eval whnf' `(List.cons 1 [])
-- [1]
```

The *arguments* of an application in WHNF may or may not be in WHNF themselves:

WHNF인 적용의 *인수들*은 그 자체로 WHNF일 수도 있고 아닐 수도 있습니다:

```
#eval whnf' `(List.cons (1 + 1) [])
-- [1 + 1]
```

Applications of constants are in WHNF if the current transparency does not
allow us to unfold the constants:

현재 투명도가 상수들을 펼치도록 허용하지 않는 경우, 상수의 적용은 WHNF입니다:

```
#eval withTransparency .reducible $ whnf' `(List.append [1] [2])
-- List.append [1] [2]
```

Lambdas are in WHNF:

람다는 WHNF입니다:

```
#eval whnf' `(λ x : Nat => x)
-- fun x => x
```

Foralls are in WHNF:

전칭 한정(forall)은 WHNF입니다:

```
#eval whnf' `(∀ x, x > 0)
-- ∀ (x : Nat), x > 0
```

Sorts are in WHNF:

Sort는 WHNF입니다:

```
#eval whnf' `(Type 3)
-- Type 3
```

Literals are in WHNF:

리터럴은 WHNF입니다:

```
#eval whnf' `((15 : Nat))
-- 15
```

Here are some more expressions in WHNF which are a bit tricky to test:

다음은 테스트하기 약간 까다로운 WHNF 표현식들의 추가 예입니다:

```
?x 0 1  -- Assuming the metavariable `?x` is unassigned, it is in WHNF.
h 0 1   -- Assuming `h` is a local hypothesis, it is in WHNF.
```

On the flipside, here are some expressions that are not in WHNF.

Applications of constants are not in WHNF if the current transparency allows us
to unfold the constants:

반대로, WHNF가 아닌 표현식들의 예도 있습니다.

현재 투명도가 상수들을 펼치도록 허용한다면, 상수의 적용은 WHNF가 아닙니다:

```
#eval whnf' `(List.append [1])
-- fun x => 1 :: List.append [] x
```

Applications of lambdas are not in WHNF:

람다의 적용은 WHNF가 아닙니다:

```
#eval whnf' `((λ x y : Nat => x + y) 1)
-- `fun y => 1 + y`
```

`let` bindings are not in WHNF:

`let` 바인딩은 WHNF가 아닙니다:

```
#eval whnf' `(let x : Nat := 1; x)
-- 1
```

And again some tricky examples:

그리고 다시 까다로운 예들이 있습니다:

```
?x 0 1 -- Assuming `?x` is assigned (e.g. to `Nat.add`), its application is not
          in WHNF.
h 0 1  -- Assuming `h` is a local definition (e.g. with value `Nat.add`), its
          application is not in WHNF.
```

Returning to the tactic that motivated this section, let us write a function
that matches a type of the form `P ∧ Q`, avoiding extra computation. WHNF
makes it easy:

이 섹션의 동기가 된 tactic으로 돌아가서, 추가 계산을 피하면서 `P ∧ Q` 형태의 타입에 매칭하는 함수를 작성해봅시다. WHNF가 이를 쉽게 만들어줍니다:

```
def matchAndReducing (e : Expr) : MetaM (Option (Expr × Expr)) := do
  match ← whnf e with
  | (.app (.app (.const ``And _) P) Q) => return some (P, Q)
  | _ => return none
```

By using `whnf`, we ensure that if `e` evaluates to something of the form `P ∧ Q`, we'll notice. But at the same time, we don't perform any unnecessary
computation in `P` or `Q`.

However, our 'no unnecessary computation' mantra also means that if we want to
perform deeper matching on an expression, we need to use `whnf` multiple times.
Suppose we want to match a type of the form `P ∧ Q ∧ R`. The correct way to do
this uses `whnf` twice:

`whnf`를 사용함으로써, `e`가 `P ∧ Q` 형태의 것으로 평가된다면 우리가 그것을 알아챌 수 있도록 보장합니다. 동시에, `P`나 `Q`에서 불필요한 계산을 수행하지 않습니다.

하지만 '불필요한 계산 없음'이라는 우리의 원칙은, 표현식에 더 깊은 매칭을 수행하려면 `whnf`를 여러 번 사용해야 함을 의미합니다. `P ∧ Q ∧ R` 형태의 타입에 매칭하고 싶다면, 올바른 방법은 `whnf`를 두 번 사용하는 것입니다:

```
def matchAndReducing₂ (e : Expr) : MetaM (Option (Expr × Expr × Expr)) := do
  match ← whnf e with
  | (.app (.app (.const ``And _) P) e') =>
    match ← whnf e' with
    | (.app (.app (.const ``And _) Q) R) => return some (P, Q, R)
    | _ => return none
  | _ => return none
```

This sort of deep matching up to computation could be automated. But until
someone builds this automation, we have to figure out the necessary `whnf`s
ourselves.

이런 계산까지 고려한 깊은 매칭은 자동화될 수 있습니다. 하지만 누군가 이 자동화를 구축하기 전까지는, 필요한 `whnf`들을 직접 파악해야 합니다.


As mentioned, definitional equality is equality up to computation. Two
expressions `t` and `s` are definitionally equal or *defeq* (at the current
transparency) if their normal forms (at the current transparency) are equal.

To check whether two expressions are defeq, use `Lean.Meta.isDefEq` with type
signature

앞서 언급했듯이, 정의적 동등성은 계산까지 고려한 동등성입니다. 두 표현식 `t`와 `s`는 (현재 투명도에서) 정규형이 같다면 정의적으로 동등하거나 *defeq*합니다.

두 표현식이 defeq인지 확인하려면, 다음 타입 시그니처를 가진 `Lean.Meta.isDefEq`를 사용합니다:

```
isDefEq : Expr → Expr → MetaM Bool
```

Even though definitional equality is defined in terms of normal forms, `isDefEq`
does not actually compute the normal forms of its arguments, which would be very
expensive. Instead, it tries to "match up" `t` and `s` using as few reductions
as possible. This is a necessarily heuristic endeavour and when the heuristics
misfire, `isDefEq` can become very expensive. In the worst case, it may have to
reduce `s` and `t` so often that they end up in normal form anyway. But usually
the heuristics are good and `isDefEq` is reasonably fast.

If expressions `t` and `u` contain assignable metavariables, `isDefEq` may
assign these metavariables to make `t` defeq to `u`. We also say that `isDefEq`
*unifies* `t` and `u`; such unification queries are sometimes written `t =?= u`.
For instance, the unification `List ?m =?= List Nat` succeeds and assigns `?m := Nat`. The unification `Nat.succ ?m =?= n + 1` succeeds and assigns `?m := n`.
The unification `?m₁ + ?m₂ + ?m₃ =?= m + n - k` fails and no metavariables are
assigned (even though there is a 'partial match' between the expressions).

Whether `isDefEq` considers a metavariable assignable is determined by two
factors:

1. The metavariable's depth must be equal to the current `MetavarContext` depth.
   See the [Metavariable Depth section](#metavariable-depth).
2. Each metavariable has a *kind* (a value of type `MetavarKind`) whose sole
   purpose is to modify the behaviour of `isDefEq`. Possible kinds are:
   * Natural: `isDefEq` may freely assign the metavariable. This is the default.
   * Synthetic: `isDefEq` may assign the metavariable, but avoids doing so if
     possible. For example, suppose `?n` is a natural metavariable and `?s` is a
     synthetic metavariable. When faced with the unification problem
     `?s =?= ?n`, `isDefEq` assigns `?n` rather than `?s`.
   * Synthetic opaque: `isDefEq` never assigns the metavariable.

정의적 동등성이 정규형을 기준으로 정의되지만, `isDefEq`는 실제로 인수들의 정규형을 계산하지 않습니다(매우 비용이 비쌀 것이기 때문입니다). 대신, 가능한 한 적은 축약으로 `t`와 `s`를 "맞추려" 시도합니다. 이것은 필연적으로 휴리스틱적인 시도이며, 휴리스틱이 잘못 작동하면 `isDefEq`가 매우 비용이 비쌀 수 있습니다. 최악의 경우, `s`와 `t`를 너무 자주 줄여서 결국 정규형이 될 수도 있습니다. 하지만 보통 휴리스틱이 잘 작동하고 `isDefEq`는 합리적으로 빠릅니다.

표현식 `t`와 `u`가 할당 가능한 메타변수를 포함하면, `isDefEq`는 `t`를 `u`와 defeq하게 만들기 위해 이 메타변수들을 할당할 수 있습니다. 우리는 또한 `isDefEq`가 `t`와 `u`를 *통합(unifies)*한다고 말합니다; 이런 통합 쿼리는 때때로 `t =?= u`로 표기됩니다. 예를 들어, `List ?m =?= List Nat` 통합은 성공하고 `?m := Nat`을 할당합니다. `Nat.succ ?m =?= n + 1` 통합은 성공하고 `?m := n`을 할당합니다. `?m₁ + ?m₂ + ?m₃ =?= m + n - k` 통합은 실패하고 메타변수가 할당되지 않습니다(표현식들 사이에 '부분 매칭'이 있음에도 불구하고).

`isDefEq`가 메타변수를 할당 가능하다고 간주하는지는 두 가지 요소에 의해 결정됩니다:

1. 메타변수의 깊이가 현재 `MetavarContext` 깊이와 같아야 합니다. [메타변수 깊이 섹션](#metavariable-depth)을 참조하세요.
2. 각 메타변수는 `isDefEq`의 동작을 수정하는 것만을 목적으로 하는 *종류(kind)*(타입 `MetavarKind`의 값)를 가집니다. 가능한 종류들은:
   * Natural: `isDefEq`는 메타변수를 자유롭게 할당할 수 있습니다. 이것이 기본값입니다.
   * Synthetic: `isDefEq`는 메타변수를 할당할 수 있지만, 가능하면 피합니다. 예를 들어, `?n`이 natural 메타변수이고 `?s`가 synthetic 메타변수라고 가정합니다. `?s =?= ?n` 통합 문제에 직면했을 때, `isDefEq`는 `?s` 대신 `?n`을 할당합니다.
   * Synthetic opaque: `isDefEq`는 메타변수를 절대 할당하지 않습니다.


In the previous chapter, we saw some primitive functions for building
expressions: `Expr.app`, `Expr.const`, `mkAppN` and so on. There is nothing
wrong with these functions, but the additional facilities of `MetaM` often
provide more convenient ways.

이전 장에서, 우리는 표현식을 구성하는 몇 가지 기본 함수들을 살펴봤습니다: `Expr.app`, `Expr.const`, `mkAppN` 등. 이 함수들에는 문제가 없지만, `MetaM`의 추가 기능들이 더 편리한 방법을 제공하는 경우가 많습니다.


When we write regular Lean code, Lean helpfully infers many implicit arguments
and universe levels. If it did not, our code would look rather ugly:

일반적인 Lean 코드를 작성할 때, Lean은 많은 암시적 인수와 우주 레벨을 유용하게 추론합니다. 그렇지 않으면 코드가 꽤 보기 흉해질 것입니다:

```
def appendAppend (xs ys : List α) := (xs.append ys).append xs

set_option pp.all true in
set_option pp.explicit true in
#print appendAppend
-- def appendAppend.{u_1} : {α : Type u_1} → List.{u_1} α → List.{u_1} α → List.{u_1} α :=
-- fun {α : Type u_1} (xs ys : List.{u_1} α) => @List.append.{u_1} α (@List.append.{u_1} α xs ys) xs
```

The `.{u_1}` suffixes are universe levels, which must be given for every
polymorphic constant. And of course the type `α` is passed around everywhere.

Exactly the same problem occurs during metaprogramming when we construct
expressions. A hand-made expression representing the right-hand side of the
above definition looks like this:

`.{u_1}` 접미사들은 우주 레벨로, 모든 다형 상수에 대해 제공해야 합니다. 그리고 물론 타입 `α`는 어디서나 전달됩니다.

메타프로그래밍에서 표현식을 구성할 때도 정확히 같은 문제가 발생합니다. 위 정의의 오른쪽을 나타내는 직접 만든 표현식은 다음과 같습니다:

```
def appendAppendRHSExpr₁ (u : Level) (α xs ys : Expr) : Expr :=
  mkAppN (.const ``List.append [u])
    #[α, mkAppN (.const ``List.append [u]) #[α, xs, ys], xs]
```

Having to specify the implicit arguments and universe levels is annoying and
error-prone. So `MetaM` provides a helper function which allows us to omit
implicit information: `Lean.Meta.mkAppM` of type

암시적 인수와 우주 레벨을 지정해야 하는 것�� 번거롭고 오류가 발생하기 쉽습니다. 그래서 `MetaM`은 암시적 정보를 생략할 수 있게 해주는 도우미 함수를 제공합니다: 다음 타입의 `Lean.Meta.mkAppM`입니다:

```
mkAppM : Name → Array Expr → MetaM Expr
```

Like `mkAppN`, `mkAppM` constructs an application. But while `mkAppN` requires
us to give all universe levels and implicit arguments ourselves, `mkAppM` infers
them. This means we only need to provide the explicit arguments, which makes for
a much shorter example:

`mkAppN`과 마찬가지로, `mkAppM`은 적용을 구성합니다. 하지만 `mkAppN`이 모든 우주 레벨과 암시적 인수를 직접 제공하도록 요구하는 반면, `mkAppM`은 이를 추론합니다. 이는 명시적 인수만 제공하면 되므로 훨씬 짧은 예제가 됩니다:

```
def appendAppendRHSExpr₂ (xs ys : Expr) : MetaM Expr := do
  mkAppM ``List.append #[← mkAppM ``List.append #[xs, ys], xs]
```

Note the absence of any `α`s and `u`s. There is also a variant of `mkAppM`,
`mkAppM'`, which takes an `Expr` instead of a `Name` as the first argument,
allowing us to construct applications of expressions which are not constants.

However, `mkAppM` is not magic: if you write ``` mkAppM ``List.append #[] ```, you
will get an error at runtime. This is because `mkAppM` tries to determine what
the type `α` is, but with no arguments given to `append`, `α` could be anything,
so `mkAppM` fails.

Another occasionally useful variant of `mkAppM` is `Lean.Meta.mkAppOptM` of type

`α`와 `u`가 없다는 점에 주목하세요. `mkAppM`의 변형인 `mkAppM'`도 있는데, 이는 첫 번째 인수로 `Name` 대신 `Expr`을 받아서 상수가 아닌 표현식의 적용을 구성할 수 있게 합니다.

하지만 `mkAppM`은 마법이 아닙니다: ``` mkAppM ``List.append #[] ```을 작성하면 런타임에 오류가 발생합니다. 이는 `mkAppM`이 타입 `α`가 무엇인지 파악하려 하지만, `append`에 인수가 없으면 `α`가 무엇이든 될 수 있어서 `mkAppM`이 실패하기 때문입니다.

`mkAppM`의 또 다른 가끔 유용한 변형은 다음 타입의 `Lean.Meta.mkAppOptM`입니다:

```
mkAppOptM : Name → Array (Option Expr) → MetaM Expr
```

Whereas `mkAppM` always infers implicit and instance arguments and always
requires us to give explicit arguments, `mkAppOptM` lets us choose freely which
arguments to provide and which to infer. With this, we can, for example, give
instances explicitly, which we use in the following example to give a
non-standard `Ord` instance.

`mkAppM`이 항상 암시적 인수와 인스턴스 인수를 추론하고 항상 명시적 인수를 제공하도록 요구하는 반면, `mkAppOptM`은 어떤 인수를 제공하고 어떤 것을 추론할지 자유롭게 선택할 수 있게 합니다. 이를 통해, 예를 들어 인스턴스를 명시적으로 제공할 수 있는데, 다음 예제에서 비표준 `Ord` 인스턴스를 제공하는 데 사용합니다.

```
def revOrd : Ord Nat where
  compare x y := compare y x

def ordExpr : MetaM Expr := do
  mkAppOptM ``compare #[none, Expr.const ``revOrd [], mkNatLit 0, mkNatLit 1]

#eval format <$> ordExpr
-- Ord.compare.{0} Nat revOrd
--   (OfNat.ofNat.{0} Nat 0 (instOfNatNat 0))
--   (OfNat.ofNat.{0} Nat 1 (instOfNatNat 1))
```

Like `mkAppM`, `mkAppOptM` has a primed variant `Lean.Meta.mkAppOptM'` which
takes an `Expr` instead of a `Name` as the first argument. The file which
contains `mkAppM` also contains various other helper functions, e.g. for making
list literals or `sorry`s.

`mkAppM`과 마찬가지로, `mkAppOptM`에는 첫 번째 인���로 `Name` 대신 `Expr`을 받는 프라임 변형 `Lean.Meta.mkAppOptM'`이 있습니다. `mkAppM`을 포함하는 파일에는 리스트 리터럴이나 `sorry`를 만드는 등의 다른 도우미 함수들도 있습니다.


Another common task is to construct expressions involving `λ` or `∀` binders.
Suppose we want to create the expression `λ (x : Nat), Nat.add x x`. One way is
to write out the lambda directly:

또 다른 일반적인 작업은 `λ` 또는 `∀` 바인더를 포함하는 표현식을 구성하는 것입니다. `λ (x : Nat), Nat.add x x` 표현식을 만들고 싶다고 가정해봅시다. 한 가지 방법은 람다를 직접 작성하는 것입니다:

```
def doubleExpr₁ : Expr :=
  .lam `x (.const ``Nat []) (mkAppN (.const ``Nat.add []) #[.bvar 0, .bvar 0])
    BinderInfo.default

#eval ppExpr doubleExpr₁
-- fun x => Nat.add x x
```

This works, but the use of `bvar` is highly unidiomatic. Lean uses a so-called
*locally closed* variable representation. This means that all but the
lowest-level functions in the Lean API expect expressions not to contain 'loose
`bvar`s', where a `bvar` is loose if it is not bound by a binder in the same
expression. (Outside of Lean, such variables are usually called 'free'. The name
`bvar` -- 'bound variable' -- already indicates that `bvar`s are never supposed
to be free.)

As a result, if in the above example we replace `mkAppN` with the slightly
higher-level `mkAppM`, we get a runtime error. Adhering to the locally closed
convention, `mkAppM` expects any expressions given to it to have no loose bound
variables, and `.bvar 0` is precisely that.

So instead of using `bvar`s directly, the Lean way is to construct expressions
with bound variables in two steps:

1. Construct the body of the expression (in our example: the body of the
   lambda), using temporary local hypotheses (`fvar`s) to stand in for the bound
   variables.
2. Replace these `fvar`s with `bvar`s and, at the same time, add the
   corresponding lambda binders.

This process ensures that we do not need to handle expressions with loose
`bvar`s at any point (except during step 2, which is performed 'atomically' by a
bespoke function). Applying the process to our example:

이것은 작동하지만, `bvar`의 사용은 매우 관용적이지 않습니다. Lean은 소위 *지역적으로 닫힌(locally closed)* 변수 표현을 사용합니다. 이는 Lean API에서 가장 낮은 수준의 함수들을 제외한 모든 함수들이 표현식에 '느슨한(loose) `bvar`'이 없기를 기대한다는 것을 의미합니다. 여기서 `bvar`는 같은 표현식의 바인더에 의해 바인딩되지 않으면 느슨합니다. (Lean 밖에서, 그런 변수들은 보통 '자유(free)'라고 불립니다. `bvar`라는 이름 -- '바인딩된 변수(bound variable)' -- 은 이미 `bvar`가 결코 자유롭지 않아야 함을 나타냅니다.)

결과적으로, 위 예제에서 `mkAppN`을 약간 더 높은 수준의 `mkAppM`으로 대체하면 런타임 오류가 발생합니다. 지역적으로 닫힌 관례를 준수하여, `mkAppM`은 제공된 표현식에 느슨한 바인딩 변수가 없기를 기대하지만, `.bvar 0`이 바로 그것입니다.

따라서 `bvar`을 직접 사용하는 대신, Lean 방식은 바인딩된 변수가 있는 표현식을 두 단계로 구성하는 것입니다:

1. 바인딩된 변수를 대신할 임시 지역 가설(`fvar`)을 사용하여 표현식의 본문(우리 예제에서는: 람다의 본문)을 구성합니다.
2. 이 `fvar`들을 `bvar`들로 대체하고, 동시에 해당 람다 바인더들을 추가합니다.

이 과정은 어느 지점에서도 느슨한 `bvar`가 있는 표현식을 처리할 필요가 없도록 보장합니다(맞춤형 함수에 의해 '원자적으로' 수행되는 2단계 제외). 이 과정을 우리 예제에 적용하면:

```
def doubleExpr₂ : MetaM Expr :=
  withLocalDecl `x BinderInfo.default (.const ``Nat []) λ x => do
    let body ← mkAppM ``Nat.add #[x, x]
    mkLambdaFVars #[x] body

#eval show MetaM _ from do
  ppExpr (← doubleExpr₂)
-- fun x => Nat.add x x
```

There are two new functions. First, `Lean.Meta.withLocalDecl` has type

두 가지 새로운 함수가 있습니다. 첫 번째로, `Lean.Meta.withLocalDecl`의 타입은 다음과 같습니다:

```
withLocalDecl (name : Name) (bi : BinderInfo) (type : Expr) (k : Expr → MetaM α) : MetaM α
```

Given a variable name, binder info and type, `withLocalDecl` constructs a new
`fvar` and passes it to the computation `k`. The `fvar` is available in the local
context during the execution of `k` but is deleted again afterwards.

The second new function is `Lean.Meta.mkLambdaFVars` with type (ignoring some
optional arguments)

변수 이름, 바인더 정보(binder info), 타입이 주어지면, `withLocalDecl`은 새 `fvar`을 구성하고 이를 계산 `k`에 전달합니다. `fvar`은 `k`의 실행 중에 지역 컨텍스트에서 사용 가능하지만 이후에는 다시 삭제됩니다.

두 번째 새로운 함수는 타입(일부 선택적 인수 무시)이 다음과 같은 `Lean.Meta.mkLambdaFVars`입니다:

```
mkLambdaFVars : Array Expr → Expr → MetaM Expr
```

This function takes an array of `fvar`s and an expression `e`. It then adds one
lambda binder for each `fvar` `x` and replaces every occurrence of `x` in `e`
with a bound variable corresponding to the new lambda binder. The returned
expression does not contain the `fvar`s any more, which is good since they
disappear after we leave the `withLocalDecl` context. (Instead of `fvar`s, we
can also give `mvar`s to `mkLambdaFVars`, despite its name.)

Some variants of the above functions may be useful:

* `withLocalDecls` declares multiple temporary `fvar`s.
* `mkForallFVars` creates `∀` binders instead of `λ` binders. `mkLetFVars`
  creates `let` binders.
* `mkArrow` is the non-dependent version of `mkForallFVars` which construcs
  a function type `X → Y`. Since the type is non-dependent, there is no need
  for temporary `fvar`s.

Using all these functions, we can construct larger expressions such as this one:

이 함수는 `fvar` 배열과 표현식 `e`를 받습니다. 그런 다음 각 `fvar` `x`에 대해 하나의 람다 바인더를 추가하고 `e`에서 `x`의 모든 등장을 새 람다 바인더에 해당하는 바인딩된 변수로 대체합니다. 반환된 표현식에는 더 이상 `fvar`들이 없는데, `withLocalDecl` 컨텍스트를 벗어나면 사라지므로 이것이 좋습니다. (`fvar` 대신, 이름에도 불구하고 `mkLambdaFVars`에 `mvar`들을 제공할 수도 있습니다.)

위 함수들의 몇 가지 변형이 유용할 수 있습니다:

* `withLocalDecls`는 여러 임시 `fvar`들을 선언합니다.
* `mkForallFVars`는 `λ` 바인더 대신 `∀` 바인더를 만듭니다. `mkLetFVars`는 `let` 바인더를 만듭니다.
* `mkArrow`는 함수 타입 `X → Y`를 구성하는 `mkForallFVars`의 비의존적(non-dependent) 버전입니다. 타입이 비의존적이므로 임시 `fvar`가 필요하지 않습니다.

이 모든 함수를 사용하여 다음과 같은 더 큰 표현식을 구성할 수 있습니다:

```
λ (f : Nat → Nat), ∀ (n : Nat), f n = f (n + 1)
```

```
def somePropExpr : MetaM Expr := do
  let funcType ← mkArrow (.const ``Nat []) (.const ``Nat [])
  withLocalDecl `f BinderInfo.default funcType fun f => do
    let feqn ← withLocalDecl `n BinderInfo.default (.const ``Nat []) fun n => do
      let lhs := .app f n
      let rhs := .app f (← mkAppM ``Nat.succ #[n])
      let eqn ← mkEq lhs rhs
      mkForallFVars #[n] eqn
    mkLambdaFVars #[f] feqn
```

The next line registers `someProp` as a name for the expression we've just
constructed, allowing us to play with it more easily. The mechanisms behind this
are discussed in the Elaboration chapter.

다음 줄은 방금 구성한 표현식의 이름으로 `someProp`을 등록하여 더 쉽게 다룰 수 있게 합니다. 이 뒤에 있는 메커니즘은 Elaboration 장에서 논의됩니다.

```
elab "someProp" : term => somePropExpr

#check someProp
-- fun f => ∀ (n : Nat), f n = f (Nat.succ n) : (Nat → Nat) → Prop
#reduce someProp Nat.succ
-- ∀ (n : Nat), Nat.succ n = Nat.succ (Nat.succ n)
```


Just like we can construct expressions more easily in `MetaM`, we can also
deconstruct them more easily. Particularly useful is a family of functions for
deconstructing expressions which start with `λ` and `∀` binders.

When we are given a type of the form `∀ (x₁ : T₁) ... (xₙ : Tₙ), U`, we are
often interested in doing something with the conclusion `U`. For instance, the
`apply` tactic, when given an expression `e : ∀ ..., U`, compares `U` with the
current target to determine whether `e` can be applied.

To do this, we could repeatedly match on the type expression, removing `∀`
binders until we get to `U`. But this would leave us with an `U` containing
unbound `bvar`s, which, as we saw, is bad. Instead, we use
`Lean.Meta.forallTelescope` of type

`MetaM`에서 표현식을 더 쉽게 구성할 수 있듯이, 더 쉽게 분해할 수도 있습니다. 특히 유용한 것은 `λ`와 `∀` 바인더로 시작하는 표현식을 분해하는 함수 집합입니다.

`∀ (x₁ : T₁) ... (xₙ : Tₙ), U` 형태의 타입이 주어지면, 우리는 종종 결론 `U`로 무언가를 하는 데 관심이 있습니다. 예를 들어, `apply` tactic은 표현식 `e : ∀ ..., U`가 주어지면 `e`를 적용할 수 있는지 결정하기 위해 `U`를 현재 목표와 비교합니다.

이를 위해 타입 표현식에 반복적으로 패턴 매칭을 하여 `U`에 도달할 때까지 `∀` 바인더들을 제거할 수 있습니다. 하지만 이렇게 하면 바인딩되지 않은 `bvar`들을 포함하는 `U`가 남게 되는데, 앞서 봤듯이 이는 문제입니다. 대신, 다음 타입의 `Lean.Meta.forallTelescope`를 사용합니다:

```
forallTelescope (type : Expr) (k : Array Expr → Expr → MetaM α) : MetaM α
```

Given `type = ∀ (x₁ : T₁) ... (xₙ : Tₙ), U x₁ ... xₙ`, this function creates one
fvar `fᵢ` for each `∀`-bound variable `xᵢ` and replaces each `xᵢ` with `fᵢ` in
the conclusion `U`. It then calls the computation `k`, passing it the `fᵢ` and
the conclusion `U f₁ ... fₙ`. Within this computation, the `fᵢ` are registered
in the local context; afterwards, they are deleted again (similar to
`withLocalDecl`).

There are many useful variants of `forallTelescope`:

* `forallTelescopeReducing`: like `forallTelescope` but matching is performed up
  to computation. This means that if you have an expression `X` which is
  different from but defeq to `∀ x, P x`, `forallTelescopeReducing X` will
  deconstruct `X` into `x` and `P x`. The non-reducing `forallTelescope` would
  not recognise `X` as a quantified expression. The matching is performed by
  essentially calling `whnf` repeatedly, using the ambient transparency.
* `forallBoundedTelescope`: like `forallTelescopeReducing` (even though there is
  no "reducing" in the name) but stops after a specified number of `∀` binders.
* `forallMetaTelescope`, `forallMetaTelescopeReducing`,
  `forallMetaBoundedTelescope`: like the corresponding non-`meta` functions, but
  the bound variables are replaced by new `mvar`s instead of `fvar`s. Unlike the
  non-`meta` functions, the `meta` functions do not delete the new metavariables
  after performing some computation, so the metavariables remain in the
  environment indefinitely.
* `lambdaTelescope`, `lambdaTelescopeReducing`, `lambdaBoundedTelescope`,
  `lambdaMetaTelescope`: like the corresponding `forall` functions, but for
  `λ` binders instead of `∀`.

Using one of the telescope functions, we can implement our own `apply` tactic:

`type = ∀ (x₁ : T₁) ... (xₙ : Tₙ), U x₁ ... xₙ`이 주어지면, 이 함수는 각 `∀`-바인딩 변수 `xᵢ`에 대해 fvar `fᵢ`를 하나씩 만들고 결론 `U`에서 각 `xᵢ`를 `fᵢ`로 대체합니다. 그런 다음 `fᵢ`와 결론 `U f₁ ... fₙ`을 전달하면서 계산 `k`를 호출합니다. 이 계산 내에서, `fᵢ`들은 지역 컨텍스트에 등록됩니다; 이후에는 다시 삭제됩니다(`withLocalDecl`과 유사하게).

`forallTelescope`의 유용한 변형들이 많습니다:

* `forallTelescopeReducing`: `forallTelescope`와 비슷하지만 매칭이 계산까지 수행됩니다. 이는 `∀ x, P x`와 다르지만 defeq한 표현식 `X`가 있으면, `forallTelescopeReducing X`가 `X`를 `x`와 `P x`로 분해한다는 것을 의미합니다. 축약하지 않는 `forallTelescope`는 `X`를 전칭 한정 표현식으로 인식하지 못합니다. 매칭은 주변 투명도를 사용하여 기본적으로 `whnf`를 반복적으로 호출함으로써 수행됩니다.
* `forallBoundedTelescope`: `forallTelescopeReducing`과 비슷하지만(이름에 "reducing"이 없음에도 불구하고) 지정된 수의 `∀` 바인더 이후에 멈춥니다.
* `forallMetaTelescope`, `forallMetaTelescopeReducing`, `forallMetaBoundedTelescope`: 대응하는 비-`meta` 함수들과 비슷하지만, 바인딩된 변수들이 `fvar` 대신 새 `mvar`들로 대체됩니다. 비-`meta` 함수들과 달리, `meta` 함수들은 계산을 수행한 후 새 메타변수들을 삭제하지 않으므로, 메타변수들이 환경에 무기한 남아있습니다.
* `lambdaTelescope`, `lambdaTelescopeReducing`, `lambdaBoundedTelescope`, `lambdaMetaTelescope`: 대응하는 `forall` 함수들과 비슷하지만, `∀` 대신 `λ` 바인더에 대해 작동합니다.

telescope 함수들 중 하나를 사용하여, 우리만의 `apply` tactic을 구현할 수 있습니다:

```
def myApply (goal : MVarId) (e : Expr) : MetaM (List MVarId) := do
  -- Check that the goal is not yet assigned.
  goal.checkNotAssigned `myApply
  -- Operate in the local context of the goal.
  goal.withContext do
    -- Get the goal's target type.
    let target ← goal.getType
    -- Get the type of the given expression.
    let type ← inferType e
    -- If `type` has the form `∀ (x₁ : T₁) ... (xₙ : Tₙ), U`, introduce new
    -- metavariables for the `xᵢ` and obtain the conclusion `U`. (If `type` does
    -- not have this form, `args` is empty and `conclusion = type`.)
    let (args, _, conclusion) ← forallMetaTelescopeReducing type
    -- If the conclusion unifies with the target:
    if ← isDefEq target conclusion then
      -- Assign the goal to `e x₁ ... xₙ`, where the `xᵢ` are the fresh
      -- metavariables in `args`.
      goal.assign (mkAppN e args)
      -- `isDefEq` may have assigned some of the `args`. Report the rest as new
      -- goals.
      let newGoals ← args.filterMapM λ mvar => do
        let mvarId := mvar.mvarId!
        if ! (← mvarId.isAssigned) && ! (← mvarId.isDelayedAssigned) then
          return some mvarId
        else
          return none
      return newGoals.toList
    -- If the conclusion does not unify with the target, throw an error.
    else
      throwTacticEx `myApply goal m!"{e} is not applicable to goal with target {target}"
```

The real `apply` does some additional pre- and postprocessing, but the core
logic is what we show here. To test our tactic, we need an elaboration
incantation, more about which in the Elaboration chapter.

실제 `apply`는 몇 가지 추가적인 전처리 및 후처리를 하지만, 핵심 로직은 여기서 보여주는 것입니다. 우리의 tactic을 테스트하려면, Elaboration 장에서 더 자세히 설명할 정교화 주문이 필요합니다.

```
elab "myApply" e:term : tactic => do
  let e ← Elab.Term.elabTerm e none
  Elab.Tactic.liftMetaTactic (myApply · e)

example (h : α → β) (a : α) : β := by
  myApply h
  myApply a
```


Many tactics naturally require backtracking: the ability to go back to a
previous state, as if the tactic had never been executed. A few examples:

* `first | t | u` first executes `t`. If `t` fails, it backtracks and executes
  `u`.
* `try t` executes `t`. If `t` fails, it backtracks to the initial state,
  erasing any changes made by `t`.
* `trivial` attempts to solve the goal using a number of simple tactics
  (e.g. `rfl` or `contradiction`). After each unsuccessful application of such a
  tactic, `trivial` backtracks.

Good thing, then, that Lean's core data structures are designed to enable easy
and efficient backtracking. The corresponding API is provided by the
`Lean.MonadBacktrack` class. `MetaM`, `TermElabM` and `TacticM` are all
instances of this class. (`CoreM` is not but could be.)

`MonadBacktrack` provides two fundamental operations:

* `Lean.saveState : m s` returns a representation of the current state, where
  `m` is the monad we are in and `s` is the state type. E.g. for `MetaM`,
  `saveState` returns a `Lean.Meta.SavedState` containing the current
  environment, the current `MetavarContext` and various other pieces of
  information.
* `Lean.restoreState : s → m Unit` takes a previously saved state and restores
  it. This effectively resets the compiler state to the previous point.

With this, we can roll our own `MetaM` version of the `try` tactic:

많은 tactic들은 자연스럽게 백트래킹을 필요로 합니다: tactic이 실행된 적이 없었던 것처럼 이전 상태로 돌아가는 능력입니다. 몇 가지 예를 들면:

* `first | t | u`는 먼저 `t`를 실행합니다. `t`가 실패하면, 백트래킹하고 `u`를 실행합니다.
* `try t`는 `t`를 실행합니다. `t`가 실패하면, 초기 상태로 백트래킹하여 `t`가 만든 모든 변경 사항을 지웁니다.
* `trivial`은 여러 간단한 tactic들(예: `rfl` 또는 `contradiction`)을 사용하여 목표를 해결하려 시도합니다. 그런 tactic의 각 실패한 적용 후에, `trivial`은 백트래킹합니다.

다행히도, Lean의 핵심 데이터 구조는 쉽고 효율적인 백트래킹을 가능하게 하도록 설계되었습니다. 해당 API는 `Lean.MonadBacktrack` 클래스에 의해 제공됩니다. `MetaM`, `TermElabM`, `TacticM`은 모두 이 클래스의 인스턴스입니다. (`CoreM`은 아니지만 될 수 있습니다.)

`MonadBacktrack`은 두 가지 기본 연산을 제공합니다:

* `Lean.saveState : m s`는 현재 상태의 표현을 반환합니다. 여기서 `m`은 우리가 있는 monad이고 `s`는 상태 타입입니다. 예를 들어 `MetaM`에서, `saveState`는 현재 환경, 현재 `MetavarContext` 및 기타 다양한 정보를 포함하는 `Lean.Meta.SavedState`를 반환합니다.
* `Lean.restoreState : s → m Unit`은 이전에 저장된 상태를 받아 복원합니다. 이것은 컴파일러 상태를 이전 시점으로 효과적으로 초기화합니다.

이를 통해, `try` tactic의 우리만의 `MetaM` 버전을 만들 수 있습니다:

```
def tryM (x : MetaM Unit) : MetaM Unit := do
  let s ← saveState
  try
    x
  catch _ =>
    restoreState s
```

We first save the state, then execute `x`. If `x` fails, we backtrack the state.

The standard library defines many combinators like `tryM`. Here are the most
useful ones:

Note that the builtin `try ... catch ... finally` does not perform any
backtracking. So code which looks like this is probably wrong:

먼저 상태를 저장한 다음 `x`를 실행합니다. `x`가 실패하면, 상태를 백트래킹합니다.

표준 라이브러리는 `tryM`과 같은 많은 콤비네이터들을 정의합니다. 다음은 가장 유용한 것들입니다:

내장 `try ... catch ... finally`는 백트래킹을 수행하지 않는다는 점에 주목하세요. 따라서 다음과 같은 코드는 아마도 잘못된 것입니다:

```
try
  doSomething
catch e =>
  doSomethingElse
```

The `catch` branch, `doSomethingElse`, is executed in a state containing
whatever modifications `doSomething` made before it failed. Since we probably
want to erase these modifications, we should write instead:

`catch` 분기 `doSomethingElse`는 `doSomething`이 실패하기 전에 만든 모든 수정 사항을 포함하는 상태에서 실행됩니다. 이 수정 사항들을 지우기를 원할 가능성이 높으므로, 대신 다음과 같이 작성해야 합니다:

```
try
  commitIfNoEx doSomething
catch e =>
  doSomethingElse
```

Another `MonadBacktrack` gotcha is that `restoreState` does not backtrack the
*entire* state. Caches, trace messages and the global name generator, among
other things, are not backtracked, so changes made to these parts of the state
are not reset by `restoreState`. This is usually what we want: if a tactic
executed by `observing?` produces some trace messages, we want to see them even
if the tactic fails. See `Lean.Meta.SavedState.restore` and `Lean.Core.restore`
for details on what is and is not backtracked.

In the next chapter, we move towards the topic of elaboration, of which
you've already seen several glimpses in this chapter. We start by discussing
Lean's syntax system, which allows you to add custom syntactic constructs to the
Lean parser.

또 다른 `MonadBacktrack`의 함정은 `restoreState`가 *전체* 상태를 백트래킹하지 않는다는 것입니다. 캐시, 추적 메시지, 전역 이름 생성기 등은 백트래킹되지 않으므로, 상태의 이러한 부분에 대한 변경 사항은 `restoreState`에 의해 초기화되지 않습니다. 이것은 보통 우리가 원하는 것입니다: `observing?`에 의해 실행된 tactic이 추적 메시지를 생성하면, tactic이 실패하더라도 그것들을 보고 싶습니다. 무엇이 백트래킹되고 무엇이 아닌지에 대한 자세한 내용은 `Lean.Meta.SavedState.restore`와 `Lean.Core.restore`를 참조하세요.

다음 장에서는 정교화(elaboration) 주제로 넘어가는데, 이 장에서 이미 여러 번 glimpse를 봤습니다. Lean 파서에 사용자 정의 구문 구조를 추가할 수 있게 해주는 Lean의 구문 시스템 논의부터 시작합니다.


1. [**Metavariables**] Create a metavariable with type `Nat`, and assign to it value `3`.
   Notice that changing the type of the metavariable from `Nat` to, for example, `String`, doesn't raise any errors - that's why, as was mentioned, we must make sure *"(a) that `val` must have the target type of `mvarId` and (b) that `val` must only contain `fvars` from the local context of `mvarId`"*.

   [**메타변수**] `Nat` 타입의 메타변수를 만들고, 여기에 값 `3`을 할당하세요.
   메타변수의 타입을 `Nat`에서 예를 들어 `String`으로 바꿔도 오류가 발생하지 않는다는 점에 주목하세요 - 그래서 앞에서 언급했듯이 *"(a) `val`이 `mvarId`의 목표 타입을 가져야 하고 (b) `val`이 `mvarId`의 지역 컨텍스트에 있는 `fvar`만 포함해야 한다"*는 것을 반드시 확인해야 합니다.

2. [**Metavariables**] What would `instantiateMVars (Lean.mkAppN (Expr.const 'Nat.add []) #[mkNatLit 1, mkNatLit 2])` output?

   [**메타변수**] `instantiateMVars (Lean.mkAppN (Expr.const 'Nat.add []) #[mkNatLit 1, mkNatLit 2])`는 무엇을 출력할까요?

3. [**Metavariables**] Fill in the missing lines in the following code.

   [**메타변수**] 다음 코드에서 빠진 줄들을 채우세요.

   ```
   #eval show MetaM Unit from do
     let oneExpr := Expr.app (Expr.const `Nat.succ []) (Expr.const ``Nat.zero [])
     let twoExpr := Expr.app (Expr.const `Nat.succ []) oneExpr

     -- Create `mvar1` with type `Nat`
     -- let mvar1 ← ...
     -- Create `mvar2` with type `Nat`
     -- let mvar2 ← ...
     -- Create `mvar3` with type `Nat`
     -- let mvar3 ← ...

     -- Assign `mvar1` to `2 + ?mvar2 + ?mvar3`
     -- ...

     -- Assign `mvar3` to `1`
     -- ...

     -- Instantiate `mvar1`, which should result in expression `2 + ?mvar2 + 1`
     ...
   ```
4. [**Metavariables**] Consider the theorem `red`, and tactic `explore` below.
   **a)** What would be the `type` and `userName` of metavariable `mvarId`?
   **b)** What would be the `type`s and `userName`s of all local declarations in this metavariable's local context?
   Print them all out.

   [**메타변수**] 아래의 정리 `red`와 tactic `explore`를 생각해보세요.
   **a)** 메타변수 `mvarId`의 `type`과 `userName`은 무엇일까요?
   **b)** 이 메타변수의 지역 컨텍스트에 있는 모든 지역 선언들의 `type`들과 `userName`들은 무엇일까요?
   모두 출력하세요.

   ```
   elab "explore" : tactic => do
     let mvarId : MVarId ← Lean.Elab.Tactic.getMainGoal
     let metavarDecl : MetavarDecl ← mvarId.getDecl

     IO.println "Our metavariable"
     -- ...

     IO.println "All of its local declarations"
     -- ...

   theorem red (hA : 1 = 1) (hB : 2 = 2) : 2 = 2 := by
     explore
     sorry
   ```
5. [**Metavariables**] Write a tactic `solve` that proves the theorem `red`.

   [**메타변수**] 정리 `red`를 증명하는 tactic `solve`를 작성하세요.

6. [**Computation**] What is the normal form of the following expressions:
   **a)** `fun x => x` of type `Bool → Bool`
   **b)** `(fun x => x) ((true && false) || true)` of type `Bool`
   **c)** `800 + 2` of type `Nat`

   [**계산**] 다음 표현식들의 정규형은 무엇인가요:
   **a)** `Bool → Bool` 타입의 `fun x => x`
   **b)** `Bool` 타입의 `(fun x => x) ((true && false) || true)`
   **c)** `Nat` 타입의 `800 + 2`

7. [**Computation**] Show that `1` created with `Expr.lit (Lean.Literal.natVal 1)` is definitionally equal to an expression created with ``` Expr.app (Expr.const ``Nat.succ []) (Expr.const ``Nat.zero []) ```.

   [**계산**] `Expr.lit (Lean.Literal.natVal 1)`로 만든 `1`이 ``` Expr.app (Expr.const ``Nat.succ []) (Expr.const ``Nat.zero []) ```으로 만든 표현식과 정의적으로 동등함을 보이세요.

8. [**Computation**] Determine whether the following expressions are definitionally equal. If `Lean.Meta.isDefEq` succeeds, and it leads to metavariable assignment, write down the assignments.
   **a)** `5 =?= (fun x => 5) ((fun y : Nat → Nat => y) (fun z : Nat => z))`
   **b)** `2 + 1 =?= 1 + 2`
   **c)** `?a =?= 2`, where `?a` has a type `String`
   **d)** `?a + Int =?= "hi" + ?b`, where `?a` and `?b` don't have a type
   **e)** `2 + ?a =?= 3`
   **f)** `2 + ?a =?= 2 + 1`

   [**계산**] 다음 표현식들이 정의적으로 동등한지 결정하세요. `Lean.Meta.isDefEq`가 성공하고 메타변수 할당으로 이어진다면, 그 할당들을 적으세요.
   **a)** `5 =?= (fun x => 5) ((fun y : Nat → Nat => y) (fun z : Nat => z))`
   **b)** `2 + 1 =?= 1 + 2`
   **c)** `?a =?= 2`, `?a`의 타입이 `String`인 경우
   **d)** `?a + Int =?= "hi" + ?b`, `?a`와 `?b`가 타입이 없는 경우
   **e)** `2 + ?a =?= 3`
   **f)** `2 + ?a =?= 2 + 1`

9. [**Computation**] Write down what you expect the following code to output.

   [**계산**] 다음 코드가 어떤 출력을 낼 것으로 예상하는지 작성하세요.

   ```
   @[reducible] def reducibleDef     : Nat := 1 -- same as `abbrev`
   @[instance] def instanceDef       : Nat := 2 -- same as `instance`
   def defaultDef                    : Nat := 3
   @[irreducible] def irreducibleDef : Nat := 4

   @[reducible] def sum := [reducibleDef, instanceDef, defaultDef, irreducibleDef]

   #eval show MetaM Unit from do
     let constantExpr := Expr.const `sum []

     Meta.withTransparency Meta.TransparencyMode.reducible do
       let reducedExpr ← Meta.reduce constantExpr
       dbg_trace (← ppExpr reducedExpr) -- ...

     Meta.withTransparency Meta.TransparencyMode.instances do
       let reducedExpr ← Meta.reduce constantExpr
       dbg_trace (← ppExpr reducedExpr) -- ...

     Meta.withTransparency Meta.TransparencyMode.default do
       let reducedExpr ← Meta.reduce constantExpr
       dbg_trace (← ppExpr reducedExpr) -- ...

     Meta.withTransparency Meta.TransparencyMode.all do
       let reducedExpr ← Meta.reduce constantExpr
       dbg_trace (← ppExpr reducedExpr) -- ...

     let reducedExpr ← Meta.reduce constantExpr
     dbg_trace (← ppExpr reducedExpr) -- ...
   ```
10. [**Constructing Expressions**] Create expression `fun x => 1 + x` in two ways:
    **a)** not idiomatically, with loose bound variables
    **b)** idiomatically.
    In what version can you use `Lean.mkAppN`? In what version can you use `Lean.Meta.mkAppM`?

    [**표현식 구성**] `fun x => 1 + x` 표현식을 두 가지 방법으로 만드세요:
    **a)** 관용적이지 않게, 느슨한 바인딩 변수를 사용하여
    **b)** 관용적으로.
    어떤 버전에서 `Lean.mkAppN`을 사용할 수 있나요? 어떤 버전에서 `Lean.Meta.mkAppM`을 사용할 수 있나요?

11. [**Constructing Expressions**] Create expression `∀ (yellow: Nat), yellow`.

    [**표현식 구성**] `∀ (yellow: Nat), yellow` 표현식을 만드세요.

12. [**Constructing Expressions**] Create expression `∀ (n : Nat), n = n + 1` in two ways:
    **a)** not idiomatically, with loose bound variables
    **b)** idiomatically.
    In what version can you use `Lean.mkApp3`? In what version can you use `Lean.Meta.mkEq`?

    [**표현식 구성**] `∀ (n : Nat), n = n + 1` 표현식을 두 가지 방법으로 만드세요:
    **a)** 관용적이지 않게, 느슨한 바인딩 변수를 사용하여
    **b)** 관용적으로.
    어떤 버전에서 `Lean.mkApp3`을 사용할 수 있나요? 어떤 버전에서 `Lean.Meta.mkEq`를 사용할 수 있나요?

13. [**Constructing Expressions**] Create expression `fun (f : Nat → Nat), ∀ (n : Nat), f n = f (n + 1)` idiomatically.

    [**표현식 구성**] `fun (f : Nat → Nat), ∀ (n : Nat), f n = f (n + 1)` 표현식을 관용적으로 만드세요.

14. [**Constructing Expressions**] What would you expect the output of the following code to be?

    [**표현식 구성**] 다음 코드의 출력이 어떨 것으로 예상하나요?

    ```
    #eval show Lean.Elab.Term.TermElabM _ from do
      let stx : Syntax ← `(∀ (a : Prop) (b : Prop), a ∨ b → b → a ∧ a)
      let expr ← Elab.Term.elabTermAndSynthesize stx none

      let (_, _, conclusion) ← forallMetaTelescope expr
      dbg_trace conclusion -- ...

      let (_, _, conclusion) ← forallMetaBoundedTelescope expr 2
      dbg_trace conclusion -- ...

      let (_, _, conclusion) ← lambdaMetaTelescope expr
      dbg_trace conclusion -- ...
    ```
15. [**Backtracking**] Check that the expressions `?a + Int` and `"hi" + ?b` are definitionally equal with `isDefEq` (make sure to use the proper types or `Option.none` for the types of your metavariables!).
    Use `saveState` and `restoreState` to revert metavariable assignments.

    [**백트래킹**] `isDefEq`로 표현식 `?a + Int`와 `"hi" + ?b`가 정의적으로 동등한지 확인하세요(메타변수의 타입에 적절한 타입이나 `Option.none`을 사용하세요!).
    `saveState`와 `restoreState`를 사용하여 메타변수 할당을 되돌리세요.