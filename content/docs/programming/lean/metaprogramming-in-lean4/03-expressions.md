---
title: "3. 표현식"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "metaprogramming"]
categories: ["programming"]
description: "Lean 4의 Expr 타입: 추상 구문 트리 구조와 표현식 조작 방법"
---

Expressions (terms of type `Expr`) are an abstract syntax tree for Lean programs.
This means that each term which can be written in Lean has a corresponding `Expr`.
For example, the application `f e` is represented by the expression `Expr.app ⟦f⟧ ⟦e⟧`,
where `⟦f⟧` is a representation of `f` and `⟦e⟧` a representation of `e`.
Similarly, the term `Nat` is represented by the expression `` Expr.const `Nat [] ``.
(The backtick and empty list are discussed below.)

표현식(`Expr` 타입의 항)은 Lean 프로그램의 추상 구문 트리입니다.
즉, Lean에서 작성할 수 있는 모든 항에는 대응하는 `Expr`이 존재합니다.
예를 들어, 적용 `f e`는 표현식 `Expr.app ⟦f⟧ ⟦e⟧`로 표현되며,
여기서 `⟦f⟧`는 `f`의 표현이고 `⟦e⟧`는 `e`의 표현입니다.
마찬가지로, 항 `Nat`은 표현식 `` Expr.const `Nat [] ``으로 표현됩니다.
(백틱과 빈 리스트는 아래에서 설명합니다.)

The ultimate purpose of a Lean tactic block
is to generate a term which serves as a proof of the theorem we want to prove.
Thus, the purpose of a tactic is to produce (part of) an `Expr` of the right type.
Much metaprogramming therefore comes down to manipulating expressions:
constructing new ones and taking apart existing ones.

Lean 택틱 블록의 궁극적인 목적은 증명하고자 하는 정리의 증명으로 사용될 항을 생성하는 것입니다.
따라서 택틱의 목적은 올바른 타입의 `Expr`을 (부분적으로) 생성하는 것입니다.
메타프로그래밍의 상당 부분은 결국 표현식을 조작하는 것으로 귀결됩니다:
새로운 표현식을 구성하거나 기존 표현식을 분해하는 작업입니다.

Once a tactic block is finished, the `Expr` is sent to the kernel,
which checks whether it is well-typed and whether it really has the type claimed by the theorem.
As a result, tactic bugs are not fatal:
if you make a mistake, the kernel will ultimately catch it.
However, many internal Lean functions also assume that expressions are well-typed,
so you may crash Lean before the expression ever reaches the kernel.
To avoid this, Lean provides many functions which help with the manipulation of expressions.
This chapter and the next survey the most important ones.

택틱 블록이 완료되면 `Expr`은 커널로 전달되어 올바른 타입인지, 그리고 정리가 주장하는 타입과 실제로 일치하는지 검사합니다.
따라서 택틱의 버그는 치명적이지 않습니다:
실수를 하더라도 커널이 결국 이를 잡아냅니다.
그러나 많은 Lean 내부 함수들도 표현식이 올바른 타입이라고 가정하기 때문에,
표현식이 커널에 도달하기 전에 Lean이 충돌할 수도 있습니다.
이를 방지하기 위해 Lean은 표현식 조작을 도와주는 많은 함수를 제공합니다.
이 장과 다음 장에서 가장 중요한 것들을 살펴봅니다.

Let's get concrete and look at the
[`Expr`](https://github.com/leanprover/lean4/blob/master/src/Lean/Expr.lean)
type:

```
import Lean

namespace Playground

inductive Expr where
  | bvar    : Nat → Expr                              -- bound variables
  | fvar    : FVarId → Expr                           -- free variables
  | mvar    : MVarId → Expr                           -- meta variables
  | sort    : Level → Expr                            -- Sort
  | const   : Name → List Level → Expr                -- constants
  | app     : Expr → Expr → Expr                      -- application
  | lam     : Name → Expr → Expr → BinderInfo → Expr  -- lambda abstraction
  | forallE : Name → Expr → Expr → BinderInfo → Expr  -- (dependent) arrow
  | letE    : Name → Expr → Expr → Expr → Bool → Expr -- let expressions
  -- less essential constructors:
  | lit     : Literal → Expr                          -- literals
  | mdata   : MData → Expr → Expr                     -- metadata
  | proj    : Name → Nat → Expr → Expr                -- projection

end Playground
```

What is each of these constructors doing?

각 생성자는 무엇을 하는 걸까요?

* `bvar` is a **bound variable**.
  For example, the `x` in `fun x => x + 2` or `∑ x, x²`.
  This is any occurrence of a variable in an expression where there is a binder above it.
  Why is the argument a `Nat`? This is called a de Bruijn index and will be explained later.
  You can figure out the type of a bound variable by looking at its binder,
  since the binder always has the type information for it.
* `fvar` is a **free variable**.
  These are variables which are not bound by a binder.
  An example is `x` in `x + 2`.
  Note that you can't just look at a free variable `x` and tell what its type is,
  there needs to be a context which contains a declaration for `x` and its type.
  A free variable has an ID that tells you where to look for it in a `LocalContext`.
  In Lean 3, free variables were called "local constants" or "locals".
* `mvar` is a **metavariable**.
  There will be much more on these later,
  but you can think of it as a placeholder or a 'hole' in an expression
  that needs to be filled at a later point.
* `sort` is used for `Type u`, `Prop` etc.
* `const` is a constant that has been defined earlier in the Lean document.
* `app` is a function application.
  Multiple arguments are done using *partial application*: `f x y ↝ app (app f x) y`.
* `lam n t b` is a lambda expression (`fun ($n : $t) => $b`).
  The `b` argument is called the **body**.
  Note that you have to give the type of the variable you are binding.
* `forallE n t b` is a dependent arrow expression (`($n : $t) → $b`).
  This is also sometimes called a Π-type or Π-expression
  and is often written `∀ $n : $t, $b`.
  Note that the non-dependent arrow `α → β` is a special case of `(a : α) → β`
  where `β` doesn't depend on `a`.
  The `E` on the end of `forallE` is to distinguish it from the `forall` keyword.
* `letE n t v b` is a **let binder** (`let ($n : $t) := $v in $b`).
* `lit` is a **literal**, this is a number or string literal like `4` or `"hello world"`.
  Literals help with performance:
  we don't want to represent the expression `(10000 : Nat)`
  as `Nat.succ $ ... $ Nat.succ Nat.zero`.
* `mdata` is just a way of storing extra information on expressions that might be useful,
  without changing the nature of the expression.
* `proj` is for projection.
  Suppose you have a structure such as `p : α × β`,
  rather than storing the projection `π₁ p` as `app π₁ p`, it is expressed as `proj Prod 0 p`.
  This is for efficiency reasons ([todo] find link to docstring explaining this).

* `bvar`는 **묶인 변수(bound variable)**입니다.
  예를 들어, `fun x => x + 2`나 `∑ x, x²`에서의 `x`가 해당됩니다.
  이는 표현식에서 위에 바인더(binder)가 존재하는 변수의 모든 출현을 나타냅니다.
  왜 인수가 `Nat`일까요? 이를 de Bruijn 인덱스라고 하며 나중에 설명합니다.
  묶인 변수의 타입은 그 바인더를 보면 알 수 있는데,
  바인더에는 항상 해당 타입 정보가 포함되어 있기 때문입니다.
* `fvar`는 **자유 변수(free variable)**입니다.
  이는 바인더에 묶여 있지 않은 변수입니다.
  예를 들어 `x + 2`에서의 `x`가 해당됩니다.
  자유 변수 `x`만 보고는 그 타입을 알 수 없으며,
  `x`의 선언과 타입을 포함하는 컨텍스트가 필요합니다.
  자유 변수는 `LocalContext`에서 어디에서 찾아야 하는지 알려주는 ID를 가집니다.
  Lean 3에서는 자유 변수를 "지역 상수(local constants)" 또는 "로컬(locals)"이라고 불렀습니다.
* `mvar`는 **메타변수(metavariable)**입니다.
  나중에 더 자세히 다루겠지만,
  나중에 채워져야 할 표현식의 플레이스홀더 또는 '구멍(hole)'으로 생각하면 됩니다.
* `sort`는 `Type u`, `Prop` 등에 사용됩니다.
* `const`는 Lean 문서에서 앞서 정의된 상수입니다.
* `app`는 함수 적용(function application)입니다.
  여러 인수는 *부분 적용(partial application)*을 사용합니다: `f x y ↝ app (app f x) y`.
* `lam n t b`는 람다 표현식(`fun ($n : $t) => $b`)입니다.
  `b` 인수는 **본문(body)**이라고 합니다.
  묶는 변수의 타입을 반드시 제공해야 합니다.
* `forallE n t b`는 의존 화살표 표현식(`($n : $t) → $b`)입니다.
  이를 Π-타입 또는 Π-표현식이라고도 하며,
  흔히 `∀ $n : $t, $b`로 표기합니다.
  비의존 화살표 `α → β`는 `β`가 `a`에 의존하지 않는
  `(a : α) → β`의 특수한 경우입니다.
  끝의 `E`는 `forall` 키워드와 구별하기 위한 것입니다.
* `letE n t v b`는 **let 바인더**(`let ($n : $t) := $v in $b`)입니다.
* `lit`는 **리터럴(literal)**로, `4`나 `"hello world"`와 같은 숫자 또는 문자열 리터럴입니다.
  리터럴은 성능에 도움이 됩니다:
  표현식 `(10000 : Nat)`을
  `Nat.succ $ ... $ Nat.succ Nat.zero`로 표현하고 싶지 않기 때문입니다.
* `mdata`는 표현식의 본질을 변경하지 않으면서 유용할 수 있는 추가 정보를 저장하는 방법입니다.
* `proj`는 프로젝션(projection)을 위한 것입니다.
  `p : α × β`와 같은 구조체가 있을 때,
  프로젝션 `π₁ p`를 `app π₁ p`로 저장하는 대신 `proj Prod 0 p`로 표현합니다.
  이는 효율성을 위한 것입니다([todo] 이를 설명하는 docstring 링크 찾기).

You've probably noticed
that you can write many Lean programs which do not have an obvious corresponding `Expr`.
For example, what about `match` statements, `do` blocks or `by` blocks?
These constructs, and many more, must indeed first be translated into expressions.
The part of Lean which performs this (substantial) task is called the elaborator
and is discussed in its own chapter.
The benefit of this setup is that once the translation to `Expr` is done,
we have a relatively simple structure to work with.
(The downside is that going back from `Expr` to a high-level Lean program can be challenging.)

아마 알아챘겠지만, 명확한 대응하는 `Expr`이 없어 보이는 많은 Lean 프로그램을 작성할 수 있습니다.
예를 들어, `match` 문, `do` 블록, `by` 블록은 어떻게 될까요?
이러한 구성 요소들과 더 많은 것들은 실제로 먼저 표현식으로 변환되어야 합니다.
이 (상당한) 작업을 수행하는 Lean의 부분을 정교화기(elaborator)라고 하며,
별도의 장에서 다룹니다.
이 설계의 장점은 `Expr`로의 변환이 완료되면 비교적 단순한 구조로 작업할 수 있다는 것입니다.
(단점은 `Expr`에서 고수준 Lean 프로그램으로 돌아가는 것이 어려울 수 있다는 점입니다.)

The elaborator also fills in any implicit or typeclass instance arguments
which you may have omitted from your Lean program.
Thus, at the `Expr` level, constants are always applied to all their arguments, implicit or not.
This is both a blessing
(because you get a lot of information which is not obvious from the source code)
and a curse
(because when you build an `Expr`, you must supply any implicit or instance arguments yourself).

정교화기는 또한 Lean 프로그램에서 생략했을 수 있는 암묵적(implicit) 인수나 타입클래스 인스턴스 인수도 채워줍니다.
따라서 `Expr` 수준에서 상수는 암묵적이든 아니든 항상 모든 인수에 적용됩니다.
이는 축복이기도 하고(소스 코드에서 명확하지 않은 많은 정보를 얻을 수 있기 때문에)
저주이기도 합니다(`Expr`를 직접 구성할 때 암묵적 인수나 인스턴스 인수를 직접 제공해야 하기 때문에).

Consider the lambda expression `(λ x : ℕ => λ y : ℕ => x + y) y`.
When we evaluate it naively, by replacing `x` with `y` in the body of the outer lambda, we obtain `λ y : ℕ => y + y`.
But this is incorrect: the lambda is a function with two arguments that adds one argument to the other, yet the evaluated version adds its argument to itself.
The root of the issue is that the name `y` is used for both the variable outside the lambdas and the variable bound by the inner lambda.
Having different variables use the same name means that when we evaluate, or β-reduce, an application, we must be careful not to confuse the different variables.

람다 표현식 `(λ x : ℕ => λ y : ℕ => x + y) y`를 생각해봅시다.
단순하게 평가하면, 외부 람다의 본문에서 `x`를 `y`로 치환하여 `λ y : ℕ => y + y`를 얻습니다.
하지만 이는 잘못된 것입니다: 이 람다는 두 인수를 더하는 함수인데, 평가된 버전은 자신의 인수를 자기 자신에 더합니다.
문제의 근원은 이름 `y`가 람다 외부의 변수와 내부 람다에 묶인 변수 모두에 사용된다는 것입니다.
서로 다른 변수가 같은 이름을 사용한다는 것은, 적용을 평가(β-축약)할 때 서로 다른 변수를 혼동하지 않도록 주의해야 한다는 것을 의미합니다.

To address this issue, Lean does not, in fact, refer to bound variables by name.
Instead, it uses **de Bruijn indexes**.
In de Bruijn indexing,
each variable bound by a `lam` or a `forallE` is converted into a number `#n`.
The number says how many binders up the `Expr` tree we should skip
to find the binder that binds this variable.
So our above example would become
(replacing inessential parts of the expression with `_` for brevity):

이 문제를 해결하기 위해 Lean은 실제로 묶인 변수를 이름으로 참조하지 않습니다.
대신 **de Bruijn 인덱스**를 사용합니다.
de Bruijn 인덱싱에서는
`lam` 또는 `forallE`에 묶인 각 변수가 숫자 `#n`으로 변환됩니다.
이 숫자는 해당 변수를 묶는 바인더를 찾기 위해 `Expr` 트리에서 몇 개의 바인더를 건너뛰어야 하는지를 나타냅니다.
따라서 위의 예제는
(간결성을 위해 불필요한 부분을 `_`로 대체하면) 다음과 같이 됩니다:

```
app (lam `x _ (lam `y _ (app (app `plus #1) #0) _) _) (fvar _)
```

```
app (lam `x _ (lam `y _ (app (app `plus #1) #0) _) _) (fvar _)
```

The `fvar` represents `y` and the lambdas' variables are now represented by `#0` and `#1`.
When we evaluate this application, we replace the bound variable belonging to `` lam `x `` (here `#1`) with the argument `fvar _`, obtaining

`fvar`는 `y`를 나타내고 람다의 변수들은 이제 `#0`과 `#1`로 표현됩니다.
이 적용을 평가할 때, `` lam `x ``에 속하는 묶인 변수(여기서 `#1`)를 인수 `fvar _`로 대체하면 다음을 얻습니다:

```
(lam `y _ (app (app `plus (fvar _)) #0) _)
```

```
(lam `y _ (app (app `plus (fvar _)) #0) _)
```

This is pretty-printed as

이는 다음과 같이 출력됩니다:

```
λ y_1 => y + y_1
```

```
λ y_1 => y + y_1
```

Note that Lean has automatically chosen a name `y_1` for the remaining bound variable that does not clash with the name of the `fvar` `y`.
The chosen name is based on the name suggestion `y` contained in the `lam`.

Lean이 `fvar` `y`의 이름과 충돌하지 않도록 나머지 묶인 변수에 자동으로 이름 `y_1`을 선택했음을 주목하세요.
선택된 이름은 `lam`에 포함된 이름 제안 `y`를 기반으로 합니다.

If a de Bruijn index is too large for the number of binders preceding it,
we say it is a **loose `bvar`**;
otherwise we say it is **bound**.
For example, in the expression `` lam `x _ (app #0 #1) ``
the `bvar` `#0` is bound by the preceding binder and `#1` is loose.
The fact that Lean calls all de Bruijn indexes `bvar`s ("bound variables")
points to an important invariant:
outside of some very low-level functions,
Lean expects that expressions do not contain any loose `bvar`s.
Instead, whenever we would be tempted to introduce a loose `bvar`,
we immediately convert it into an `fvar` ("free variable").
(Hence, Lean's binder representation is "locally nameless".)
Precisely how that works is discussed in the next chapter.

de Bruijn 인덱스가 앞에 있는 바인더의 수보다 너무 크면,
이를 **느슨한 `bvar`(loose `bvar`)**라고 하고,
그렇지 않으면 **묶인(bound)** 것이라고 합니다.
예를 들어, 표현식 `` lam `x _ (app #0 #1) ``에서
`bvar` `#0`은 앞의 바인더에 묶여 있고 `#1`은 느슨합니다.
Lean이 모든 de Bruijn 인덱스를 `bvar`("묶인 변수")라고 부른다는 사실은
중요한 불변 조건을 가리킵니다:
일부 매우 저수준 함수를 제외하고,
Lean은 표현식에 느슨한 `bvar`가 포함되지 않기를 기대합니다.
대신, 느슨한 `bvar`를 도입하고 싶을 때마다
즉시 이를 `fvar`("자유 변수")로 변환합니다.
(따라서 Lean의 바인더 표현은 "locally nameless"입니다.)
정확히 어떻게 작동하는지는 다음 장에서 설명합니다.

If there are no loose `bvar`s in an expression, we say that the expression is **closed**.
The process of replacing all instances of a loose `bvar` with an `Expr`
is called **instantiation**.
Going the other way is called **abstraction**.

표현식에 느슨한 `bvar`가 없으면, 표현식이 **닫혀 있다(closed)**고 합니다.
느슨한 `bvar`의 모든 인스턴스를 `Expr`로 대체하는 과정을
**인스턴스화(instantiation)**라고 합니다.
반대 방향으로 가는 것은 **추상화(abstraction)**라고 합니다.

If you are familiar with the standard terminology around variables,
Lean's terminology may be confusing,
so here's a map:
Lean's "bvars" are usually called just "variables";
Lean's "loose" is usually called "free";
and Lean's "fvars" might be called "local hypotheses".

변수에 관한 표준 용어에 익숙하다면,
Lean의 용어가 혼란스러울 수 있으니 다음과 같이 대응됩니다:
Lean의 "bvars"는 보통 그냥 "변수(variables)"라고 불리며,
Lean의 "loose"는 보통 "자유(free)"라고 불리고,
Lean의 "fvars"는 "지역 가설(local hypotheses)"이라고 불릴 수 있습니다.

Some expressions involve universe levels, represented by the `Lean.Level` type.
A universe level is a natural number,
a universe parameter (introduced with a `universe` declaration),
a universe metavariable or the maximum of two universes.
They are relevant for two kinds of expressions.

일부 표현식은 `Lean.Level` 타입으로 표현되는 유니버스 레벨을 포함합니다.
유니버스 레벨은 자연수,
유니버스 매개변수(`universe` 선언으로 도입됨),
유니버스 메타변수 또는 두 유니버스의 최댓값입니다.
이들은 두 종류의 표현식과 관련이 있습니다.

First, sorts are represented by `Expr.sort u`, where `u` is a `Level`.
`Prop` is `sort Level.zero`; `Type` is `sort (Level.succ Level.zero)`.

첫째, 소트(sort)는 `u`가 `Level`인 `Expr.sort u`로 표현됩니다.
`Prop`은 `sort Level.zero`이고, `Type`은 `sort (Level.succ Level.zero)`입니다.

Second, universe-polymorphic constants have universe arguments.
A universe-polymorphic constant is one whose type contains universe parameters.
For example, the `List.map` function is universe-polymorphic,
as the `pp.universes` pretty-printing option shows:

둘째, 유니버스 다형 상수(universe-polymorphic constant)는 유니버스 인수를 가집니다.
유니버스 다형 상수는 타입에 유니버스 매개변수를 포함하는 상수입니다.
예를 들어, `List.map` 함수는 유니버스 다형적이며,
`pp.universes` 출력 옵션으로 확인할 수 있습니다:

```
set_option pp.universes true in
#check @List.map
```

The `.{u_1,u_2}` suffix after `List.map`
means that `List.map` has two universe arguments, `u_1` and `u_2`.
The `.{u_1}` suffix after `List` (which is itself a universe-polymorphic constant)
means that `List` is applied to the universe argument `u_1`, and similar for `.{u_2}`.

`List.map` 뒤의 `.{u_1,u_2}` 접미사는
`List.map`이 두 개의 유니버스 인수 `u_1`과 `u_2`를 가진다는 것을 의미합니다.
`List` 뒤의 `.{u_1}` 접미사(List 자체도 유니버스 다형 상수임)는
`List`가 유니버스 인수 `u_1`에 적용됨을 의미하며, `.{u_2}`도 마찬가지입니다.

In fact, whenever you use a universe-polymorphic constant,
you must apply it to the correct universe arguments.
This application is represented by the `List Level` argument of `Expr.const`.
When we write regular Lean code, Lean infers the universes automatically,
so we do not need think about them much.
But when we construct `Expr`s,
we must be careful to apply each universe-polymorphic constant to the right universe arguments.

실제로 유니버스 다형 상수를 사용할 때마다 올바른 유니버스 인수를 적용해야 합니다.
이 적용은 `Expr.const`의 `List Level` 인수로 표현됩니다.
일반적인 Lean 코드를 작성할 때는 Lean이 유니버스를 자동으로 추론하므로
크게 신경 쓸 필요가 없습니다.
하지만 `Expr`를 직접 구성할 때는
각 유니버스 다형 상수에 올바른 유니버스 인수를 적용하는 데 주의해야 합니다.

The simplest expressions we can construct are constants.
We use the `const` constructor and give it a name and a list of universe levels.
Most of our examples only involve non-universe-polymorphic constants,
in which case the list is empty.

우리가 구성할 수 있는 가장 단순한 표현식은 상수입니다.
`const` 생성자를 사용하여 이름과 유니버스 레벨 리스트를 제공합니다.
대부분의 예제는 유니버스 비다형 상수만 포함하므로,
이 경우 리스트는 비어 있습니다.

We also show a second form where we write the name with double backticks.
This checks that the name in fact refers to a defined constant,
which is useful to avoid typos.

또한 이름을 이중 백틱으로 작성하는 두 번째 형식도 보여줍니다.
이것은 이름이 실제로 정의된 상수를 참조하는지 확인하여
오타를 방지하는 데 유용합니다.

```
open Lean

def z' := Expr.const `Nat.zero []
#eval z' -- Lean.Expr.const `Nat.zero []

def z := Expr.const ``Nat.zero []
#eval z -- Lean.Expr.const `Nat.zero []
```

The double-backtick variant also resolves the given name, making it fully-qualified.
To illustrate this mechanism, here are two further examples.
The first expression, `z₁`, is unsafe:
if we use it in a context where the `Nat` namespace is not open,
Lean will complain that there is no constant called `zero` in the environment.
In contrast, the second expression, `z₂`,
contains the fully-qualified name `Nat.zero` and does not have this problem.

이중 백틱 형식은 또한 주어진 이름을 완전히 한정된(fully-qualified) 이름으로 해석합니다.
이 메커니즘을 설명하기 위해 두 가지 추가 예제를 보여줍니다.
첫 번째 표현식 `z₁`은 안전하지 않습니다:
`Nat` 네임스페이스가 열려 있지 않은 컨텍스트에서 사용하면,
Lean이 환경에 `zero`라는 상수가 없다고 불평할 것입니다.
반면에, 두 번째 표현식 `z₂`는
완전히 한정된 이름 `Nat.zero`를 포함하므로 이 문제가 없습니다.

```
open Nat

def z₁ := Expr.const `zero []
#eval z₁ -- Lean.Expr.const `zero []

def z₂ := Expr.const ``zero []
#eval z₂ -- Lean.Expr.const `Nat.zero []
```

The next class of expressions we consider are function applications.
These can be built using the `app` constructor,
with the first argument being an expression for the function
and the second being an expression for the argument.

다음으로 살펴볼 표현식 유형은 함수 적용입니다.
이는 `app` 생성자를 사용하여 구성할 수 있으며,
첫 번째 인수는 함수에 대한 표현식이고
두 번째는 인수에 대한 표현식입니다.

Here are two examples.
The first is simply a constant applied to another.
The second is a recursive definition giving an expression as a function of a natural number.

두 가지 예제를 보여줍니다.
첫 번째는 단순히 하나의 상수에 다른 상수를 적용한 것입니다.
두 번째는 자연수의 함수로 표현식을 제공하는 재귀적 정의입니다.

```
def one := Expr.app (.const ``Nat.succ []) z
#eval one
-- Lean.Expr.app (Lean.Expr.const `Nat.succ []) (Lean.Expr.const `Nat.zero [])

def natExpr: Nat → Expr
| 0     => z
| n + 1 => .app (.const ``Nat.succ []) (natExpr n)
```

Next we use the variant `mkAppN` which allows application with multiple arguments.

```
def sumExpr : Nat → Nat → Expr
| n, m => mkAppN (.const ``Nat.add []) #[natExpr n, natExpr m]
```

As you may have noticed, we didn't show `#eval` outputs for the two last functions.
That's because the resulting expressions can grow so large
that it's hard to make sense of them.

다음으로 여러 인수를 사용한 적용을 허용하는 변형인 `mkAppN`을 사용합니다.

마지막 두 함수에 대해 `#eval` 출력을 보여주지 않았다는 것을 알아챘을 것입니다.
결과 표현식이 너무 커서
이해하기 어렵기 때문입니다.

We next use the constructor `lam`
to construct a simple function which takes any natural number `x` and returns `Nat.zero`.
The argument `BinderInfo.default` says that `x` is an explicit argument
(rather than an implicit or typeclass argument).

다음으로 `lam` 생성자를 사용하여
임의의 자연수 `x`를 받아 `Nat.zero`를 반환하는 간단한 함수를 구성합니다.
인수 `BinderInfo.default`는 `x`가 명시적(explicit) 인수임을
(암묵적 또는 타입클래스 인수가 아닌) 나타냅니다.

```
def constZero : Expr :=
  .lam `x (.const ``Nat []) (.const ``Nat.zero []) BinderInfo.default

#eval constZero
-- Lean.Expr.lam `x (Lean.Expr.const `Nat []) (Lean.Expr.const `Nat.zero [])
--   (Lean.BinderInfo.default)
```

As a more elaborate example which also involves universe levels,
here is the `Expr` that represents `List.map (λ x => Nat.add x 1) []`
(broken up into several definitions to make it somewhat readable):

유니버스 레벨도 포함하는 더 정교한 예제로,
`List.map (λ x => Nat.add x 1) []`을 나타내는 `Expr`을 보여줍니다
(어느 정도 읽기 쉽도록 여러 정의로 나누었습니다):

```
def nat : Expr := .const ``Nat []

def addOne : Expr :=
  .lam `x nat
    (mkAppN (.const ``Nat.add []) #[.bvar 0, mkNatLit 1])
    BinderInfo.default

def mapAddOneNil : Expr :=
  mkAppN (.const ``List.map [levelZero, levelZero])
    #[nat, nat, addOne, .app (.const ``List.nil [levelZero]) nat]
```

With a little trick (more about which in the Elaboration chapter),
we can turn our `Expr` into a Lean term, which allows us to inspect it more easily.

약간의 트릭을 사용하면(Elaboration 장에서 더 자세히 설명),
`Expr`을 Lean 항으로 변환할 수 있어 더 쉽게 검사할 수 있습니다.

```
elab "mapAddOneNil" : term => return mapAddOneNil

#check mapAddOneNil
-- List.map (fun x => Nat.add x 1) [] : List Nat

set_option pp.universes true in
set_option pp.explicit true in
#check mapAddOneNil
-- @List.map.{0, 0} Nat Nat (fun x => x.add 1) (@List.nil.{0} Nat) : List.{0} Nat

#reduce mapAddOneNil
-- []
```

In the next chapter we explore the `MetaM` monad,
which, among many other things,
allows us to more conveniently construct and destruct larger expressions.

다음 장에서는 `MetaM` 모나드를 살펴볼 것입니다.
이는 여러 기능 중에서도 더 큰 표현식을 편리하게 구성하고 분해할 수 있게 해줍니다.

1. Create expression `1 + 2` with `Expr.app`.
2. Create expression `1 + 2` with `Lean.mkAppN`.
3. Create expression `fun x => 1 + x`.
4. [**De Bruijn Indexes**] Create expression `fun a, fun b, fun c, (b * a) + c`.
5. Create expression `fun x y => x + y`.
6. Create expression `fun x, String.append "hello, " x`.
7. Create expression `∀ x : Prop, x ∧ x`.
8. Create expression `Nat → String`.
9. Create expression `fun (p : Prop) => (λ hP : p => hP)`.
10. [**Universe levels**] Create expression `Type 6`.

1. `Expr.app`으로 표현식 `1 + 2`를 만드세요.
2. `Lean.mkAppN`으로 표현식 `1 + 2`를 만드세요.
3. 표현식 `fun x => 1 + x`를 만드세요.
4. [**De Bruijn Indexes**] 표현식 `fun a, fun b, fun c, (b * a) + c`를 만드세요.
5. 표현식 `fun x y => x + y`를 만드세요.
6. 표현식 `fun x, String.append "hello, " x`를 만드세요.
7. 표현식 `∀ x : Prop, x ∧ x`를 만드세요.
8. 표현식 `Nat → String`을 만드세요.
9. 표현식 `fun (p : Prop) => (λ hP : p => hP)`를 만드세요.
10. [**Universe levels**] 표현식 `Type 6`을 만드세요.
