---
title: "8. DSL 만들기"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "metaprogramming"]
categories: ["programming"]
description: "Lean 4로 DSL 구현하기: 커스텀 syntax category와 elaboration을 활용한 도메인 특화 언어"
---

In this chapter we will learn how to use elaboration to build a DSL. We will not
explore the full power of `MetaM`, and simply gesture at how to get access to
this low-level machinery.

이 장에서는 elaboration을 사용하여 DSL을 구축하는 방법을 배웁니다. `MetaM`의 전체 기능을 탐구하지는 않고, 이 저수준 기계에 접근하는 방법을 간략히 살펴볼 것입니다.

More precisely, we shall enable Lean to understand the syntax of
[IMP](http://concrete-semantics.org/concrete-semantics.pdf),
which is a simple imperative language, often used for teaching operational and
denotational semantics.

더 정확히는, Lean이 [IMP](http://concrete-semantics.org/concrete-semantics.pdf)의 문법을 이해할 수 있도록 할 것입니다. IMP는 연산 의미론과 표시 의미론을 가르치는 데 자주 사용되는 간단한 명령형 언어입니다.

We are not going to define everything with the same encoding that the book does.
For instance, the book defines arithmetic expressions and boolean expressions.
We, will take a different path and just define generic expressions that take
unary or binary operators.

책과 동일한 인코딩 방식으로 모든 것을 정의하지는 않을 것입니다. 예를 들어, 책에서는 산술 표현식과 불리언 표현식을 별도로 정의합니다. 우리는 다른 방향을 택하여 단항 또는 이항 연산자를 받는 범용 표현식만 정의할 것입니다.

This means that we will allow weirdnesses like `1 + true`! But it will simplify
the encoding, the grammar and consequently the metaprogramming didactic.

이는 `1 + true`와 같은 이상한 표현을 허용하게 됨을 의미합니다! 하지만 이렇게 하면 인코딩, 문법, 그리고 결과적으로 메타프로그래밍 교육이 단순해집니다.

We begin by defining our atomic literal value.

원자 리터럴 값을 정의하는 것부터 시작합니다.

```
import Lean

open Lean Elab Meta

inductive IMPLit
  | nat  : Nat  → IMPLit
  | bool : Bool → IMPLit
```

This is our only unary operator

이것이 우리의 유일한 단항 연산자입니다.

```
inductive IMPUnOp
  | not
```

These are our binary operations.

이것들이 우리의 이항 연산들입니다.

```
inductive IMPBinOp
  | and | add | less
```

Now we define the expressions that we want to handle.

이제 처리하고자 하는 표현식을 정의합니다.

```
inductive IMPExpr
  | lit : IMPLit → IMPExpr
  | var : String → IMPExpr
  | un  : IMPUnOp → IMPExpr → IMPExpr
  | bin : IMPBinOp → IMPExpr → IMPExpr → IMPExpr
```

And finally the commands of our language. Let's follow the book and say that
"each piece of a program is also a program":

그리고 마지막으로 우리 언어의 명령들을 정의합니다. 책을 따라 "프로그램의 각 부분도 프로그램이다"라고 말하겠습니다:

```
inductive IMPProgram
  | Skip   : IMPProgram
  | Assign : String → IMPExpr → IMPProgram
  | Seq    : IMPProgram → IMPProgram → IMPProgram
  | If     : IMPExpr → IMPProgram → IMPProgram → IMPProgram
  | While  : IMPExpr → IMPProgram → IMPProgram
```

Now that we have our data types, let's elaborate terms of `Syntax` into
terms of `Expr`. We begin by defining the syntax and an elaboration function for
literals.

이제 데이터 타입이 준비되었으니, `Syntax` 항을 `Expr` 항으로 정교화(elaborate)해 봅시다. 리터럴에 대한 문법과 정교화 함수를 정의하는 것부터 시작합니다.

```
declare_syntax_cat imp_lit
syntax num       : imp_lit
syntax "true"    : imp_lit
syntax "false"   : imp_lit

def elabIMPLit : Syntax → MetaM Expr
  -- `mkAppM` creates an `Expr.app`, given the function `Name` and the args
  -- `mkNatLit` creates an `Expr` from a `Nat`
  | `(imp_lit| $n:num) => mkAppM ``IMPLit.nat  #[mkNatLit n.getNat]
  | `(imp_lit| true  ) => mkAppM ``IMPLit.bool #[.const ``Bool.true []]
  | `(imp_lit| false ) => mkAppM ``IMPLit.bool #[.const ``Bool.false []]
  | _ => throwUnsupportedSyntax

elab "test_elabIMPLit " l:imp_lit : term => elabIMPLit l

#reduce test_elabIMPLit 4     -- IMPLit.nat 4
#reduce test_elabIMPLit true  -- IMPLit.bool true
#reduce test_elabIMPLit false -- IMPLit.bool true
```

In order to elaborate expressions, we also need a way to elaborate our unary and
binary operators.

표현식을 정교화하기 위해서는 단항 및 이항 연산자를 정교화하는 방법도 필요합니다.

Notice that these could very much be pure functions (`Syntax → Expr`), but we're
staying in `MetaM` because it allows us to easily throw an error for match
completion.

이것들은 순수 함수(`Syntax → Expr`)로 작성할 수도 있지만, 패턴 매칭 완성을 위한 오류를 쉽게 던질 수 있기 때문에 `MetaM` 안에 있습니다.

```
declare_syntax_cat imp_unop
syntax "not"     : imp_unop

def elabIMPUnOp : Syntax → MetaM Expr
  | `(imp_unop| not) => return .const ``IMPUnOp.not []
  | _ => throwUnsupportedSyntax

declare_syntax_cat imp_binop
syntax "+"       : imp_binop
syntax "and"     : imp_binop
syntax "<"       : imp_binop

def elabIMPBinOp : Syntax → MetaM Expr
  | `(imp_binop| +)   => return .const ``IMPBinOp.add []
  | `(imp_binop| and) => return .const ``IMPBinOp.and []
  | `(imp_binop| <)   => return .const ``IMPBinOp.less []
  | _ => throwUnsupportedSyntax
```

Now we define the syntax for expressions:

이제 표현식에 대한 문법을 정의합니다:

```
declare_syntax_cat                   imp_expr
syntax imp_lit                     : imp_expr
syntax ident                       : imp_expr
syntax imp_unop imp_expr           : imp_expr
syntax imp_expr imp_binop imp_expr : imp_expr
```

Let's also allow parentheses so the IMP programmer can denote their parsing
precedence.

IMP 프로그래머가 파싱 우선순위를 명시할 수 있도록 괄호도 허용해 봅시다.

```
syntax "(" imp_expr ")" : imp_expr
```

Now we can elaborate our expressions. Note that expressions can be recursive.
This means that our `elabIMPExpr` function will need to be recursive! We'll need
to use `partial` because Lean can't prove the termination of `Syntax`
consumption alone.

이제 표현식을 정교화할 수 있습니다. 표현식이 재귀적일 수 있다는 점에 주목하세요. 이는 `elabIMPExpr` 함수도 재귀적이어야 함을 의미합니다! Lean이 `Syntax` 소비만으로는 종료를 증명할 수 없기 때문에 `partial`을 사용해야 합니다.

```
partial def elabIMPExpr : Syntax → MetaM Expr
  | `(imp_expr| $l:imp_lit) => do
    let l ← elabIMPLit l
    mkAppM ``IMPExpr.lit #[l]
  -- `mkStrLit` creates an `Expr` from a `String`
  | `(imp_expr| $i:ident) => mkAppM ``IMPExpr.var #[mkStrLit i.getId.toString]
  | `(imp_expr| $b:imp_unop $e:imp_expr) => do
    let b ← elabIMPUnOp b
    let e ← elabIMPExpr e -- recurse!
    mkAppM ``IMPExpr.un #[b, e]
  | `(imp_expr| $l:imp_expr $b:imp_binop $r:imp_expr) => do
    let l ← elabIMPExpr l -- recurse!
    let r ← elabIMPExpr r -- recurse!
    let b ← elabIMPBinOp b
    mkAppM ``IMPExpr.bin #[b, l, r]
  | `(imp_expr| ($e:imp_expr)) => elabIMPExpr e
  | _ => throwUnsupportedSyntax

elab "test_elabIMPExpr " e:imp_expr : term => elabIMPExpr e

#reduce test_elabIMPExpr a
-- IMPExpr.var "a"

#reduce test_elabIMPExpr a + 5
-- IMPExpr.bin IMPBinOp.add (IMPExpr.var "a") (IMPExpr.lit (IMPLit.nat 5))

#reduce test_elabIMPExpr 1 + true
-- IMPExpr.bin IMPBinOp.add (IMPExpr.lit (IMPLit.nat 1)) (IMPExpr.lit (IMPLit.bool true))
```

And now we have everything we need to elaborate our IMP programs!

이제 IMP 프로그램을 정교화하는 데 필요한 모든 것이 준비되었습니다!

```
declare_syntax_cat           imp_program
syntax "skip"              : imp_program
syntax ident ":=" imp_expr : imp_program

syntax imp_program ";;" imp_program : imp_program

syntax "if" imp_expr "then" imp_program "else" imp_program "fi" : imp_program
syntax "while" imp_expr "do" imp_program "od" : imp_program

partial def elabIMPProgram : Syntax → MetaM Expr
  | `(imp_program| skip) => return .const ``IMPProgram.Skip []
  | `(imp_program| $i:ident := $e:imp_expr) => do
    let i : Expr := mkStrLit i.getId.toString
    let e ← elabIMPExpr e
    mkAppM ``IMPProgram.Assign #[i, e]
  | `(imp_program| $p₁:imp_program ;; $p₂:imp_program) => do
    let p₁ ← elabIMPProgram p₁
    let p₂ ← elabIMPProgram p₂
    mkAppM ``IMPProgram.Seq #[p₁, p₂]
  | `(imp_program| if $e:imp_expr then $pT:imp_program else $pF:imp_program fi) => do
    let e ← elabIMPExpr e
    let pT ← elabIMPProgram pT
    let pF ← elabIMPProgram pF
    mkAppM ``IMPProgram.If #[e, pT, pF]
  | `(imp_program| while $e:imp_expr do $pT:imp_program od) => do
    let e ← elabIMPExpr e
    let pT ← elabIMPProgram pT
    mkAppM ``IMPProgram.While #[e, pT]
  | _ => throwUnsupportedSyntax
```

And we can finally test our full elaboration pipeline. Let's use the following
syntax:

이제 드디어 전체 정교화 파이프라인을 테스트할 수 있습니다. 다음 문법을 사용해 봅시다:

```
elab ">>" p:imp_program "<<" : term => elabIMPProgram p

#reduce >>
a := 5;;
if not a and 3 < 4 then
  c := 5
else
  a := a + 1
fi;;
b := 10
<<
-- IMPProgram.Seq (IMPProgram.Assign "a" (IMPExpr.lit (IMPLit.nat 5)))
--   (IMPProgram.Seq
--     (IMPProgram.If
--       (IMPExpr.un IMPUnOp.not
--         (IMPExpr.bin IMPBinOp.and (IMPExpr.var "a")
--           (IMPExpr.bin IMPBinOp.less (IMPExpr.lit (IMPLit.nat 3)) (IMPExpr.lit (IMPLit.nat 4)))))
--       (IMPProgram.Assign "c" (IMPExpr.lit (IMPLit.nat 5)))
--       (IMPProgram.Assign "a" (IMPExpr.bin IMPBinOp.add (IMPExpr.var "a") (IMPExpr.lit (IMPLit.nat 1)))))
--     (IMPProgram.Assign "b" (IMPExpr.lit (IMPLit.nat 10))))
```
