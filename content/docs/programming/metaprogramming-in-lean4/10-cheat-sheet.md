---
title: "Cheat Sheet"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "metaprogramming"]
categories: ["programming"]
description: "Lean 4 메타프로그래밍 치트시트: 핵심 함수와 패턴 모음"
---

* Extract the goal: `Lean.Elab.Tactic.getMainGoal`

  Use as `let goal ← Lean.Elab.Tactic.getMainGoal`
* Extract the declaration out of a metavariable: `mvarId.getDecl`
  when `mvarId : Lean.MVarId` is in context.
  For instance, `mvarId` could be the goal extracted using `getMainGoal`
* Extract the type of a metavariable: `mvarId.getType`
  when `mvarId : Lean.MVarId` is in context.
* Extract the type of the main goal: `Lean.Elab.Tactic.getMainTarget`

  Use as `let goal_type ← Lean.Elab.Tactic.getMainTarget`

  Achieves the same as

```
let goal ← Lean.Elab.Tactic.getMainGoal
let goal_type ← goal.getType
```

* Extract local context: `Lean.MonadLCtx.getLCtx`

  Use as `let lctx ← Lean.MonadLCtx.getLCtx`
* Extract the name of a declaration: `Lean.LocalDecl.userName ldecl`
  when `ldecl : Lean.LocalDecl` is in context
* Extract the type of an expression: `Lean.Meta.inferType expr`
  when `expr : Lean.Expr` is an expression in context

  Use as `let expr_type ← Lean.Meta.inferType expr`

* 목표(goal) 추출: `Lean.Elab.Tactic.getMainGoal`

  `let goal ← Lean.Elab.Tactic.getMainGoal` 형태로 사용
* 메타변수에서 선언(declaration) 추출: `mvarId.getDecl`
  `mvarId : Lean.MVarId`가 컨텍스트에 있을 때 사용.
  예를 들어, `mvarId`는 `getMainGoal`로 추출한 목표일 수 있음
* 메타변수의 타입 추출: `mvarId.getType`
  `mvarId : Lean.MVarId`가 컨텍스트에 있을 때 사용.
* 주 목표의 타입 추출: `Lean.Elab.Tactic.getMainTarget`

  `let goal_type ← Lean.Elab.Tactic.getMainTarget` 형태로 사용

  아래와 동일한 결과를 얻음:

```
let goal ← Lean.Elab.Tactic.getMainGoal
let goal_type ← goal.getType
```

* 로컬 컨텍스트 추출: `Lean.MonadLCtx.getLCtx`

  `let lctx ← Lean.MonadLCtx.getLCtx` 형태로 사용
* 선언의 이름 추출: `Lean.LocalDecl.userName ldecl`
  `ldecl : Lean.LocalDecl`이 컨텍스트에 있을 때 사용
* 표현식의 타입 추출: `Lean.Meta.inferType expr`
  `expr : Lean.Expr`가 컨텍스트에 있을 때 사용

  `let expr_type ← Lean.Meta.inferType expr` 형태로 사용


* Convert a declaration into an expression: `Lean.LocalDecl.toExpr`

  Use as `ldecl.toExpr`, when `ldecl : Lean.LocalDecl` is in context

  For instance, `ldecl` could be `let ldecl ← Lean.MonadLCtx.getLCtx`
* Check whether two expressions are definitionally equal: `Lean.Meta.isDefEq ex1 ex2`
  when `ex1 ex2 : Lean.Expr` are in context. Returns a `Lean.MetaM Bool`
* Close a goal: `Lean.Elab.Tactic.closeMainGoal expr`
  when `expr : Lean.Expr` is in context

* 선언을 표현식으로 변환: `Lean.LocalDecl.toExpr`

  `ldecl : Lean.LocalDecl`이 컨텍스트에 있을 때 `ldecl.toExpr` 형태로 사용

  예를 들어, `ldecl`은 `let ldecl ← Lean.MonadLCtx.getLCtx`로 얻은 값일 수 있음
* 두 표현식이 정의적으로 동일한지 확인: `Lean.Meta.isDefEq ex1 ex2`
  `ex1 ex2 : Lean.Expr`가 컨텍스트에 있을 때 사용. `Lean.MetaM Bool`을 반환
* 목표 닫기: `Lean.Elab.Tactic.closeMainGoal expr`
  `expr : Lean.Expr`가 컨텍스트에 있을 때 사용


* meta-sorry: `Lean.Elab.admitGoal goal`, when `goal : Lean.MVarId` is the current goal

* meta-sorry: `Lean.Elab.admitGoal goal`, `goal : Lean.MVarId`가 현재 목표일 때 사용


* Print a "permanent" message in normal usage:

  `Lean.logInfo f!"Hi, I will print\n{Syntax}"`
* Print a message while debugging:

  `dbg_trace f!"1) goal: {Syntax_that_will_be_interpreted}"`.
* Throw an error: `Lean.Meta.throwTacticEx name mvar message_data`
  where `name : Lean.Name` is the name of a tactic and `mvar` contains error data.

  Use as `Lean.Meta.throwTacticEx` tac goal (m!"unable to find matching hypothesis of type ({goal\_type})")`where the`m!`formatting builds a`MessageData` for better printing of terms

* 일반 사용 시 "영구적인" 메시지 출력:

  `Lean.logInfo f!"Hi, I will print\n{Syntax}"`
* 디버깅 중 메시지 출력:

  `dbg_trace f!"1) goal: {Syntax_that_will_be_interpreted}"`.
* 오류 발생시키기: `Lean.Meta.throwTacticEx name mvar message_data`
  `name : Lean.Name`은 tactic의 이름이고 `mvar`은 오류 데이터를 담음.

  `Lean.Meta.throwTacticEx` tac goal (m!"unable to find matching hypothesis of type ({goal\_type})")` 형태로 사용. `m!` 포매팅은 항(term)을 더 잘 출력하기 위한 `MessageData`를 생성함

TODO: Add?

* Lean.LocalContext.forM
* Lean.LocalContext.findDeclM?
