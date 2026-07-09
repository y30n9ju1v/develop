---
title: "do -Notation for Monads"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "do -Notation for Monads"
---

# 4.4. `do`-Notation for Monads

While APIs based on monads are very powerful, the explicit use of `>>=` with anonymous functions is still somewhat noisy.
Just as infix operators are used instead of explicit calls to `HAdd.hAdd`, Lean provides a syntax for monads called *`do`-notation* that can make programs that use monads easier to read and write.
This is the very same `do`-notation that is used to write programs in `IO`, and `IO` is also a monad.

Monad에 기반한 API는 매우 강력하지만, 익명 함수를 사용한 `>>=`의 명시적 사용은 여전히 다소 복잡합니다. 중위 연산자가 `HAdd.hAdd`에 대한 명시적 호출 대신 사용되는 것처럼, Lean은 Monad를 위한 do-표기법이라는 구문을 제공하여 Monad를 사용하는 프로그램을 더 쉽게 읽고 쓸 수 있게 합니다. 이것은 `IO`에서 프로그램을 작성하는 데 사용되는 동일한 `do`-표기법이며, `IO`도 Monad입니다.

In [Hello, World!](../ch02/), the `do` syntax is used to combine `IO` actions, but the meaning of these programs is explained directly.
Understanding how to program with monads means that `do` can now be explained in terms of how it translates into uses of the underlying monad operators.

[Hello, World!](../ch02/)에서 `do` 구문은 `IO` 액션을 결합하는 데 사용되지만 이러한 프로그램의 의미는 직접 설명됩니다. Monad를 사용하여 프로그래밍하는 방법을 이해하는 것은 이제 `do`가 기본 Monad 연산자의 사용으로 어떻게 변환되는지에 따라 설명될 수 있음을 의미합니다.

The first translation of `do` is used when the only statement in the `do` is a single expression `E`.
In this case, the `do` is removed, so

`do` 번역의 첫 번째는 `do`의 유일한 명령문이 단일 표현식 `E`일 때 사용됩니다. 이 경우 `do`가 제거되므로:

`do E`

translates to

번역.

The second translation is used when the first statement of the `do` is a `let` with an arrow, binding a local variable.
This translates to a use of `>>=` together with a function that binds that very same variable, so

두 번째 번역은 `do`의 첫 번째 명령문이 화살표가 있는 `let`일 때 사용되며, 로컬 변수를 바인딩합니다. 이는 동일한 변수를 바인딩하는 함수와 함께 `>>=`의 사용으로 변환되므로:

`do let x ← E₁
Stmt
…
Eₙ`

translates to

번역:

`E₁ >>= fun x =>
do Stmt
…
Eₙ`

When the first statement of the `do` block is an expression, then it is considered to be a monadic action that returns `Unit`, so the function matches the `Unit` constructor and

`do` 블록의 첫 번째 명령문이 표현식일 때, 이는 `Unit`을 반환하는 Monadic 액션으로 간주되므로 함수는 `Unit` 생성자와 일치합니다:

`do E₁
Stmt
…
Eₙ`

translates to

번역:

`E₁ >>= fun () =>
do Stmt
…
Eₙ`

Finally, when the first statement of the `do` block is a `let` that uses `:=`, the translated form is an ordinary let expression, so

마지막으로 `do` 블록의 첫 번째 명령문이 `:=`를 사용하는 `let`일 때, 변환된 형식은 일반적인 let 표현식이므로:

`do let x := E₁
Stmt
…
Eₙ`

translates to

번역:

`let x := E₁
do Stmt
…
Eₙ`

The definition of `firstThirdFifthSeventh` that uses the `Monad` class looks like this:

`Monad` 클래스를 사용하는 `firstThirdFifthSeventh`의 정의는 다음과 같습니다:

`def firstThirdFifthSeventh [Monad m] (lookup : List α → Nat → m α)
(xs : List α) : m (α × α × α × α) :=
lookup xs 0 >>= fun first =>
lookup xs 2 >>= fun third =>
lookup xs 4 >>= fun fifth =>
lookup xs 6 >>= fun seventh =>
pure (first, third, fifth, seventh)`

Using `do`-notation, it becomes significantly more readable:

`do`-표기법을 사용하면 훨씬 더 읽기 쉬워집니다:

`def firstThirdFifthSeventh [Monad m] (lookup : List α → Nat → m α)
(xs : List α) : m (α × α × α × α) := do
let first ← lookup xs 0
let third ← lookup xs 2
let fifth ← lookup xs 4
let seventh ← lookup xs 6
pure (first, third, fifth, seventh)`

All of the conveniences from `do` with `IO` are also available when using it with other monads.
For example, nested actions also work in any monad.
The original definition of `mapM` was:

`IO`를 사용한 `do`의 모든 편의성은 다른 Monad와 함께 사용할 때도 사용할 수 있습니다. 예를 들어, 중첩된 액션은 모든 Monad에서도 작동합니다. `mapM`의 원래 정의는:

`def mapM [Monad m] (f : α → m β) : List α → m (List β)
| [] => pure []
| x :: xs =>
f x >>= fun hd =>
mapM f xs >>= fun tl =>
pure (hd :: tl)`

With `do`-notation, it can be written:

`do`-표기법으로 다음과 같이 작성할 수 있습니다:

`def mapM [Monad m] (f : α → m β) : List α → m (List β)
| [] => pure []
| x :: xs => do
let hd ← f x
let tl ← mapM f xs
pure (hd :: tl)`

Using nested actions makes it almost as short as the original non-monadic `map`:

중첩된 액션을 사용하면 원래의 non-monadic `map`만큼 짧아집니다:

`def mapM [Monad m] (f : α → m β) : List α → m (List β)
| [] => pure []
| x :: xs => do
pure ((← f x) :: (← mapM f xs))`

Using nested actions, `number` can be made much more concise:

중첩된 액션을 사용하면 `number`를 훨씬 더 간결하게 만들 수 있습니다:

`def increment : State Nat Nat := do
let n ← get
set (n + 1)
pure n
def number (t : BinTree α) : BinTree (Nat × α) :=
let rec helper : BinTree α → State Nat (BinTree (Nat × α))
| BinTree.leaf => pure BinTree.leaf
| BinTree.branch left x right => do
pure
(BinTree.branch
(← helper left)
((← increment), x)
(← helper right))
(helper t 0).snd`

## 4.4.1. Exercises

* Rewrite `evaluateM`, its helpers, and the different specific use cases using `do`-notation instead of explicit calls to `>>=`.
* Rewrite `firstThirdFifthSeventh` using nested actions.

* `evaluateM`, 그 헬퍼 및 여러 특정 사용 사례를 `>>=`의 명시적 호출 대신 `do`-표기법을 사용하여 다시 작성하세요.
* 중첩된 액션을 사용하여 `firstThirdFifthSeventh`를 다시 작성하세요.
