---
title: "예제: Monad에서의 산술 연산"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "산술 식 평가기를 여러 Monad(Id, Many, Reader)에 걸쳐 다형적으로 작성하기"
---

# Example: Arithmetic in Monads

Monads are a way of encoding programs with side effects into a language that does not have them.
It would be easy to read this as a sort of admission that pure functional programs are missing something important, requiring programmers to jump through hoops just to write a normal program.
However, while using the `Monad` API does impose a syntactic cost on a program, it brings two important benefits:

One example of a program that can make sense in a variety of monads is an evaluator for arithmetic expressions.

## 4.3.3. Further Effects

Failure and exceptions are not the only kinds of effects that can be interesting when working with an evaluator.
While division's only side effect is failure, adding other primitive operators to the expressions make it possible to express other effects.

실패와 예외는 평가기로 작업할 때 흥미로운 유일한 종류의 효과가 아닙니다. 나눗셈의 유일한 부작용이 실패이지만, 식에 다른 기본 연산자를 추가하면 다른 효과를 표현할 수 있습니다.

The first step is an additional refactoring, extracting division from the datatype of primitives:

첫 번째 단계는 추가 리팩토링으로 기본 datatype에서 나눗셈을 추출하는 것입니다:

```lean
inductive Prim (special : Type) where
  | plus
  | minus
  | times
  | other : special → Prim special
inductive CanFail where
  | div
```

The name `CanFail` suggests that the effect introduced by division is potential failure.

`CanFail`이라는 이름은 나눗셈으로 인해 도입되는 효과가 잠재적 실패임을 암시합니다.

The second step is to broaden the scope of the division handler argument to `evaluateM` so that it can process any special operator:

두 번째 단계는 `evaluateM`의 나눗셈 핸들러 인자의 범위를 확장하여 모든 특수 연산자를 처리할 수 있도록 하는 것입니다:

```lean
def divOption : CanFail → Int → Int → Option Int
  | CanFail.div, x, y => if y == 0 then none else pure (x / y)
def divExcept : CanFail → Int → Int → Except String Int
  | CanFail.div, x, y =>
    if y == 0 then
      Except.error s!"Tried to divide {x} by zero"
    else pure (x / y)
def applyPrim [Monad m]
    (applySpecial : special → Int → Int → m Int) :
    Prim special → Int → Int → m Int
  | Prim.plus, x, y => pure (x + y)
  | Prim.minus, x, y => pure (x - y)
  | Prim.times, x, y => pure (x * y)
  | Prim.other op, x, y => applySpecial op x y
def evaluateM [Monad m]
    (applySpecial : special → Int → Int → m Int) :
    Expr (Prim special) → m Int
  | Expr.const i => pure i
  | Expr.prim p e1 e2 =>
    evaluateM applySpecial e1 >>= fun v1 =>
    evaluateM applySpecial e2 >>= fun v2 =>
    applyPrim applySpecial p v1 v2
```

### 4.3.3.1. No Effects

The type `Empty` has no constructors, and thus no values, like the `Nothing` type in Scala or Kotlin.
In Scala and Kotlin, `Nothing` can represent computations that never return a result, such as functions that crash the program, throw exceptions, or always fall into infinite loops.
An argument to a function or method of type `Nothing` indicates dead code, as there will never be a suitable argument value.
Lean doesn't support infinite loops and exceptions, but `Empty` is still useful as an indication to the type system that a function cannot be called.
Using the syntax `nomatch E` when `E` is an expression whose type has no constructors indicates to Lean that the current expression need not return a result, because it could never have been called.

`Empty` 타입은 Scala나 Kotlin의 `Nothing` 타입처럼 생성자가 없으므로 값이 없습니다. Scala와 Kotlin에서 `Nothing`은 프로그램을 충돌시키는 함수, 예외를 던지는 함수, 또는 항상 무한 루프에 빠지는 함수와 같이 절대 결과를 반환하지 않는 계산을 나타낼 수 있습니다. `Nothing` 타입의 함수나 메소드의 인자는 적절한 인자 값이 절대 없을 것이므로 죽은 코드를 나타냅니다. Lean은 무한 루프와 예외를 지원하지 않지만, `Empty`는 여전히 함수를 호출할 수 없음을 타입 시스템에 표시하는 것으로 유용합니다. 생성자가 없는 타입을 가진 식인 `E`에 대해 `nomatch E`라는 구문을 사용하면, 호출될 수 없었을 것이므로 현재 식이 결과를 반환할 필요가 없음을 Lean에 나타냅니다.

Using `Empty` as the parameter to `Prim` indicates that there are no additional cases beyond `Prim.plus`, `Prim.minus`, and `Prim.times`, because it is impossible to come up with a value of type `Empty` to place in the `Prim.other` constructor.
Because a function to apply an operator of type `Empty` to two integers can never be called, it doesn't need to return a result.
Thus, it can be used in *any* monad:

`Empty`를 `Prim`의 매개변수로 사용하면 `Prim.other` 생성자에 놓을 `Empty` 타입의 값을 만들 수 없기 때문에 `Prim.plus`, `Prim.minus`, `Prim.times` 외에 추가 경우가 없음을 나타냅니다. `Empty` 타입의 연산자를 두 정수에 적용하는 함수는 절대 호출될 수 없으므로 결과를 반환할 필요가 없습니다. 따라서 *어떤* monad에서도 사용할 수 있습니다:

```lean
def applyEmpty [Monad m] (op : Empty) (_ : Int) (_ : Int) : m Int :=
  nomatch op
```

This can be used together with `Id`, the identity monad, to evaluate expressions that have no effects whatsoever:

이는 항등원 monad인 `Id`와 함께 사용하여 효과가 전혀 없는 식을 평가할 수 있습니다:

```lean
open Expr Prim in
#eval evaluateM (m := Id) applyEmpty (prim plus (const 5) (const (-14)))
```

```
-9
```

### 4.3.3.2. Nondeterministic Search

Instead of simply failing when encountering division by zero, it would also be sensible to backtrack and try a different input.
Given the right monad, the very same `evaluateM` can perform a nondeterministic search for a *set* of answers that do not result in failure.
This requires, in addition to division, some means of specifying a choice of results.
One way to do this is to add a function `choose` to the language of expressions that instructs the evaluator to pick either of its arguments while searching for non-failing results.

영으로 나누기를 만났을 때 단순히 실패하는 대신, 역추적하여 다른 입력을 시도하는 것도 합리적입니다. 올바른 monad가 주어지면, 동일한 `evaluateM`은 실패하지 않는 답들의 *집합*에 대한 비결정적 검색을 수행할 수 있습니다. 이는 나눗셈 외에도 결과의 선택을 지정할 수 있는 수단이 필요합니다. 이를 수행하는 한 가지 방법은 실패하지 않는 결과를 검색하는 동안 두 인자 중 하나를 선택하도록 평가기에 지시하는 함수 `choose`를 식의 언어에 추가하는 것입니다.

The result of the evaluator is now a multiset of values, rather than a single value.
The rules for evaluation into a multiset are:

평가기의 결과는 이제 단일 값이 아니라 다중집합 값입니다. 다중집합으로의 평가 규칙은:

* Constants `n` evaluate to singleton sets `\{n\}`.
* Arithmetic operators other than division are called on each pair from the Cartesian product of the operators, so `X + Y` evaluates to `\{ x + y \mid x ∈ X, y ∈ Y \}`.
* Division `X / Y` evaluates to `\{ x / y \mid x ∈ X, y ∈ Y, y ≠ 0\}`. In other words, all `0` values in `Y` are thrown out.
* A choice `\mathrm{choose}(x, y)` evaluates to `\{ x, y \}`.

For example, `1 + \mathrm{choose}(2, 5)` evaluates to `\{ 3, 6 \}`, `1 + 2 / 0` evaluates to `\{\}`, and `90 / (\mathrm{choose}(-5, 5) + 5)` evaluates to `\{ 9 \}`.
Using multisets instead of true sets simplifies the code by removing the need to check for uniqueness of elements.

예를 들어, `1 + \mathrm{choose}(2, 5)`는 `\{ 3, 6 \}`으로 평가되고, `1 + 2 / 0`은 `\{\}`으로 평가되며, `90 / (\mathrm{choose}(-5, 5) + 5)`는 `\{ 9 \}`로 평가됩니다. 참 집합 대신 다중집합을 사용하면 요소의 유일성을 확인할 필요가 없음으로써 코드를 단순화합니다.

A monad that represents this non-deterministic effect must be able to represent a situation in which there are no answers, and a situation in which there is at least one answer together with any remaining answers:

이 비결정적 효과를 나타내는 monad는 답이 없는 상황과 적어도 하나의 답이 있는 상황과 남은 답들을 함께 나타낼 수 있어야 합니다:

```lean
inductive Many (α : Type) where
  | none : Many α
  | more : α → (Unit → Many α) → Many α
```

This datatype looks very much like `List`.
The difference is that where `List.cons` stores the rest of the list, `more` stores a function that should compute the remaining values on demand.
This means that a consumer of `Many` can stop the search when some number of results have been found.

이 datatype은 `List`과 매우 유사합니다. 차이점은 `List.cons`가 리스트의 나머지를 저장하는 반면, `more`은 요청에 따라 남은 값을 계산해야 하는 함수를 저장한다는 것입니다. 즉, `Many`의 소비자가 일정 수의 결과를 찾았을 때 검색을 중지할 수 있음입니다.

A single result is represented by a `more` constructor that returns no further results:

단일 결과는 더 이상의 결과를 반환하지 않는 `more` 생성자로 표현됩니다:

```lean
def Many.one (x : α) : Many α := Many.more x (fun () => Many.none)
```

The union of two multisets of results can be computed by checking whether the first multiset is empty.
If so, the second multiset is the union.
If not, the union consists of the first element of the first multiset followed by the union of the rest of the first multiset with the second multiset:

두 다중집합의 합집합은 첫 번째 다중집합이 비어 있는지 확인하여 계산할 수 있습니다. 그렇다면 두 번째 다중집합이 합집합입니다. 그렇지 않으면 합집합은 첫 번째 다중집합의 첫 번째 요소 다음에 첫 번째 다중집합의 나머지와 두 번째 다중집합의 합집합으로 구성됩니다:

```lean
def Many.union : Many α → Many α → Many α
  | Many.none, ys => ys
  | Many.more x xs, ys => Many.more x (fun () => union (xs ()) ys)
```

It can be convenient to start a search process with a list of values.
`Many.fromList` converts a list into a multiset of results:

검색 프로세스를 값의 리스트로 시작하는 것이 편할 수 있습니다. `Many.fromList`는 리스트를 다중집합 결과로 변환합니다:

```lean
def Many.fromList : List α → Many α
  | [] => Many.none
  | x :: xs => Many.more x (fun () => fromList xs)
```

Similarly, once a search has been specified, it can be convenient to extract either a number of values, or all the values:

마찬가지로, 검색이 명시된 후에는 일정 수의 값들이나 모든 값들을 추출하는 것이 편할 수 있습니다:

```lean
def Many.take : Nat → Many α → List α
  | 0, _ => []
  | _ + 1, Many.none => []
  | n + 1, Many.more x xs => x :: (xs ()).take n
def Many.takeAll : Many α → List α
  | Many.none => []
  | Many.more x xs => x :: (xs ()).takeAll
```

A `Monad Many` instance requires a `bind` operator.
In a nondeterministic search, sequencing two operations consists of taking all possibilities from the first step and running the rest of the program on each of them, taking the union of the results.
In other words, if the first step returns three possible answers, the second step needs to be tried for all three.
Because the second step can return any number of answers for each input, taking their union represents the entire search space.

`Monad Many` 인스턴스는 `bind` 연산자를 필요로 합니다. 비결정적 검색에서 두 작업의 시퀀싱은 첫 번째 단계에서 모든 가능성을 취하고 각각에 대해 프로그램의 나머지를 실행하며 결과의 합집합을 취하는 것으로 구성됩니다. 즉, 첫 번째 단계가 3개의 가능한 답을 반환하면 두 번째 단계를 모두 3개에 대해 시도해야 합니다. 두 번째 단계는 각 입력에 대해 임의의 수의 답을 반환할 수 있으므로, 이들의 합집합을 취하는 것은 전체 검색 공간을 나타냅니다.

```lean
def Many.bind : Many α → (α → Many β) → Many β
  | Many.none, _ =>
    Many.none
  | Many.more x xs, f =>
    (f x).union (bind (xs ()) f)
```

`Many.one` and `Many.bind` obey the monad contract.
To check that `Many.bind (Many.one v) f` is the same as `f v`, start by evaluating the expression as far as possible:

`Many.one`과 `Many.bind`는 monad 계약을 따릅니다. `Many.bind (Many.one v) f`이 `f v`와 같은지 확인하려면 식을 가능한 한 평가하여 시작합니다.

The empty multiset is a right identity of `union`, so the answer is equivalent to `f v`.
To check that `Many.bind v Many.one` is the same as `v`, consider that `Many.bind` takes the union of applying `Many.one` to each element of `v`.
In other words, if `v` has the form `{v₁, v₂, v₃, …, vₙ}`, then `Many.bind v Many.one` is `{v₁} ∪ {v₂} ∪ {v₃} ∪ … ∪ {vₙ}`, which is `{v₁, v₂, v₃, …, vₙ}`.

공 다중집합은 `union`의 우측 항등원이므로, 답은 `f v`와 동등합니다. `Many.bind v Many.one`이 `v`와 같은지 확인하려면 `Many.bind`가 `v`의 각 요소에 `Many.one`을 적용한 합집합을 취한다는 것을 고려합니다. 즉, `v`가 `{v₁, v₂, v₃, …, vₙ}` 형태를 가지면 `Many.bind v Many.one`은 `{v₁} ∪ {v₂} ∪ {v₃} ∪ … ∪ {vₙ}`이고, 이는 `{v₁, v₂, v₃, …, vₙ}`입니다.

Finally, to check that `Many.bind` is associative, check that `Many.bind (Many.bind v f) g` is the same as `Many.bind v (fun x => Many.bind (f x) g)`.
If `v` has the form `{v₁, v₂, v₃, …, vₙ}`, then:

마지막으로 `Many.bind`가 결합적인지 확인하려면 `Many.bind (Many.bind v f) g`이 `Many.bind v (fun x => Many.bind (f x) g)`과 같은지 확인합니다. `v`가 `{v₁, v₂, v₃, …, vₙ}` 형태를 가지면:

```
Many.bind v f
= f v₁ ∪ f v₂ ∪ f v₃ ∪ … ∪ f vₙ
```

which means that

```
Many.bind (Many.bind v f) g
= Many.bind (f v₁) g ∪
  Many.bind (f v₂) g ∪
  Many.bind (f v₃) g ∪
  … ∪
  Many.bind (f vₙ) g
```

Similarly,

```
Many.bind v (fun x => Many.bind (f x) g)
= (fun x => Many.bind (f x) g) v₁ ∪
  (fun x => Many.bind (f x) g) v₂ ∪
  (fun x => Many.bind (f x) g) v₃ ∪
  … ∪
  (fun x => Many.bind (f x) g) vₙ
= Many.bind (f v₁) g ∪
  Many.bind (f v₂) g ∪
  Many.bind (f v₃) g ∪
  … ∪
  Many.bind (f vₙ) g
```

Thus, both sides are equal, so `Many.bind` is associative.

따라서 양쪽이 같으므로 `Many.bind`는 결합적입니다.

The resulting monad instance is:

결과적인 monad 인스턴스는:

```lean
instance : Monad Many where
  pure := Many.one
  bind := Many.bind
```

An example search using this monad finds all the combinations of numbers in a list that add to 15:

이 monad를 사용한 검색 예제는 리스트의 모든 수의 조합이 15를 더하는 것을 찾습니다:

```lean
def addsTo (goal : Nat) : List Nat → Many (List Nat)
  | [] =>
    if goal == 0 then
      pure []
    else
      Many.none
  | x :: xs =>
    if x > goal then
      addsTo goal xs
    else
      (addsTo goal xs).union
        (addsTo (goal - x) xs >>= fun answer =>
          pure (x :: answer))
```

The search process is recursive over the list.
The empty list is a successful search when the goal is `0`; otherwise, it fails.
When the list is non-empty, there are two possibilities: either the head of the list is greater than the goal, in which case it cannot participate in any successful searches, or it is not, in which case it can.
If the head of the list is *not* a candidate, then the search proceeds to the tail of the list.
If the head is a candidate, then there are two possibilities to be combined with `Many.union`: either the solutions found contain the head, or they do not.
The solutions that do not contain the head are found with a recursive call on the tail, while the solutions that do contain it result from subtracting the head from the goal, and then attaching the head to the solutions that result from the recursive call.

검색 프로세스는 리스트에 대해 재귀적입니다. 공 리스트는 목표가 `0`일 때 성공적인 검색이고, 그렇지 않으면 실패합니다. 리스트가 비어있지 않을 때는 두 가지 가능성이 있습니다: 리스트의 헤드가 목표보다 크거나, 그렇지 않거나. 리스트의 헤드가 후보가 *아니면* 검색은 리스트의 테일로 진행됩니다. 헤드가 후보이면 `Many.union`과 결합할 두 가지 가능성이 있습니다: 찾은 해가 헤드를 포함하거나 포함하지 않거나. 헤드를 포함하지 않는 해는 테일에 대한 재귀 호출로 찾아지고, 헤드를 포함하는 해는 목표에서 헤드를 빼고 재귀 호출로부터의 해에 헤드를 붙이기로부터 비롯됩니다.

The helper `printList` ensures that one result is displayed per line:

헬퍼 `printList`는 한 결과가 한 줄에 표시되도록 보장합니다:

```lean
def printList [ToString α] : List α → IO Unit
  | [] => pure ()
  | x :: xs => do
    IO.println x
    printList xs
```

```lean
#eval printList (addsTo 15 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).takeAll
```

```
[7, 8]
[6, 9]
[5, 10]
[4, 5, 6]
[3, 5, 7]
[3, 4, 8]
[2, 6, 7]
[2, 5, 8]
[2, 4, 9]
[2, 3, 10]
[2, 3, 4, 6]
[1, 6, 8]
[1, 5, 9]
[1, 4, 10]
[1, 3, 5, 6]
[1, 3, 4, 7]
[1, 2, 5, 7]
[1, 2, 4, 8]
[1, 2, 3, 9]
[1, 2, 3, 4, 5]
[1, 2, 4, 8]
[1, 2, 3, 9]
[1, 2, 3, 4, 5]
```

Returning to the arithmetic evaluator that produces multisets of results, the `choose` operator can be used to nondeterministically select a value, with division by zero rendering prior selections invalid.

다중집합 결과를 생성하는 산술 평가기로 돌아가면, `choose` 연산자를 사용하여 값을 비결정적으로 선택할 수 있으며, 영으로 나누기는 이전 선택을 무효화합니다.

```lean
inductive NeedsSearch
  | div
  | choose
def applySearch : NeedsSearch → Int → Int → Many Int
  | NeedsSearch.choose, x, y =>
    Many.fromList [x, y]
  | NeedsSearch.div, x, y =>
    if y == 0 then
      Many.none
    else Many.one (x / y)
```

### 4.3.3.3. Custom Environments

The evaluator can be made user-extensible by allowing strings to be used as operators, and then providing a mapping from strings to a function that implements them.
For example, users could extend the evaluator with a remainder operator or with one that returns the maximum of its two arguments.
The mapping from function names to function implementations is called an *environment*.

평가기는 문자열을 연산자로 사용할 수 있도록 하고, 문자열에서 이를 구현하는 함수로의 매핑을 제공함으로써 사용자 확장 가능하게 만들 수 있습니다. 예를 들어, 사용자는 평가기를 나머지 연산자나 두 인자의 최댓값을 반환하는 연산자로 확장할 수 있습니다. 함수 이름에서 함수 구현으로의 매핑을 *환경*이라고 합니다.

The environments needs to be passed in each recursive call.
Initially, it might seem that `evaluateM` needs an extra argument to hold the environment, and that this argument should be passed to each recursive invocation.
However, passing an argument like this is another form of monad, so an appropriate `Monad` instance allows the evaluator to be used unchanged.

환경은 각 재귀 호출에서 전달되어야 합니다. 처음에는 `evaluateM`이 환경을 보유하기 위해 추가 인자가 필요하고, 이 인자가 각 재귀 호출에 전달되어야 하는 것처럼 보일 수 있습니다. 그러나 이와 같은 인자를 전달하는 것은 monad의 또 다른 형태이므로, 적절한 `Monad` 인스턴스는 평가기를 변경되지 않은 채로 사용할 수 있게 해줍니다.

Using functions as a monad is typically called a *reader* monad.
When evaluating expressions in the reader monad, the following rules are used:

함수를 monad로 사용하는 것을 일반적으로 *reader* monad라고 합니다. reader monad에서 식을 평가할 때 다음 규칙들이 사용됩니다:

* Constants `n` evaluate to constant functions `λ e . n`,
* Arithmetic operators evaluate to functions that pass their arguments on, so `f + g` evaluates to `λ e . f(e) + g(e)`, and
* Custom operators evaluate to the result of applying the custom operator to the arguments, so `f \ \mathrm{OP}\ g` evaluates to
  ```
  λ e .
    \begin{cases}
    h(f(e), g(e)) & \mathrm{if}\ e\ \mathrm{contains}\ (\mathrm{OP}, h) \\
    0 & \mathrm{otherwise}
    \end{cases}
  ```
  with `0` serving as a fallback in case an unknown operator is applied.

To define the reader monad in Lean, the first step is to define the `Reader` type and the effect that allows users to get ahold of the environment:

Lean에서 reader monad를 정의하기 위해 첫 번째 단계는 `Reader` 타입과 사용자가 환경을 얻을 수 있게 해주는 효과를 정의하는 것입니다:

```lean
def Reader (ρ : Type) (α : Type) : Type := ρ → α
def read : Reader ρ ρ := fun env => env
```

By convention, the Greek letter `ρ`, which is pronounced “rho”, is used for environments.

관례상 “rho”로 발음되는 그리스 문자 `ρ`가 환경에 사용됩니다.

The fact that constants in arithmetic expressions evaluate to constant functions suggests that the appropriate definition of `pure` for `Reader` is a a constant function:

산술 식의 상수가 상수 함수로 평가된다는 사실은 `Reader`에 대한 `pure`의 적절한 정의가 상수 함수임을 시사합니다:

```lean
def Reader.pure (x : α) : Reader ρ α := fun _ => x
```

On the other hand, `bind` is a bit tricker.
Its type is `Reader ρ α → (α → Reader ρ β) → Reader ρ β`.
This type can be easier to understand by unfolding the definition of `Reader`, which yields `(ρ → α) → (α → ρ → β) → (ρ → β)`.
It should take an environment-accepting function as its first argument, while the second argument should transform the result of the environment-accepting function into yet another environment-accepting function.
The result of combining these is itself a function, waiting for an environment.

한편 `bind`는 조금 더 까다롭습니다. 그 타입은 `Reader ρ α → (α → Reader ρ β) → Reader ρ β`입니다. 이 타입은 `Reader`의 정의를 펼쳐서 `(ρ → α) → (α → ρ → β) → (ρ → β)`를 얻음으로써 더 쉽게 이해할 수 있습니다. 첫 번째 인자로 환경을 받아들이는 함수를 취해야 하고, 두 번째 인자는 환경을 받아들이는 함수의 결과를 또 다른 환경을 받아들이는 함수로 변환해야 합니다. 이들을 결합한 결과는 그 자체로 환경을 기다리는 함수입니다.

It's possible to use Lean interactively to get help writing this function.
The first step is to write down the arguments and return type, being very explicit in order to get as much help as possible, with an underscore for the definition's body:

이 함수를 작성하는 데 도움을 얻기 위해 Lean을 대화형으로 사용할 수 있습니다. 첫 번째 단계는 인자와 반환 타입을 작성하고, 가능한 한 많은 도움을 얻기 위해 매우 명확하게 하며, 정의의 본문에는 언더스코어를 사용하는 것입니다:

```lean
def Reader.bind {ρ : Type} {α : Type} {β : Type}
    (result : ρ → α) (next : α → ρ → β) : ρ → β :=
  _
```

Lean provides a message that describes which variables are available in scope, and the type that's expected for the result.
The `⊢` symbol, called a *turnstile* due to its resemblance to subway entrances, separates the local variables from the desired type, which is `ρ → β` in this message:

Lean은 범위에서 사용 가능한 변수들을 설명하고 결과에 대해 예상되는 타입을 설명하는 메시지를 제공합니다. 지하철 입구와의 유사성 때문에 *turnstile*이라고 불리는 `⊢` 기호는 로컬 변수와 원하는 타입을 분리하며, 이 메시지에서는 `ρ → β`입니다:

```
don't know how to synthesize placeholder
context:
ρ α β : Type
result : ρ → α
next : α → ρ → β
⊢ ρ → β
```

Because the return type is a function, a good first step is to wrap a `fun` around the underscore:

반환 타입이 함수이기 때문에 좋은 첫 번째 단계는 언더스코어 주위에 `fun`을 감싸는 것입니다:

```lean
def Reader.bind {ρ : Type} {α : Type} {β : Type}
    (result : ρ → α) (next : α → ρ → β) : ρ → β :=
  fun env => _
```

The resulting message now shows the function's argument as a local variable:

결과 메시지는 이제 함수의 인자를 로컬 변수로 보여줍니다:

```
don't know how to synthesize placeholder
context:
ρ α β : Type
result : ρ → α
next : α → ρ → β
env : ρ
⊢ β
```

The only thing in the context that can produce a `β` is `next`, and it will require two arguments to do so.
Each argument can itself be an underscore:

맥락에서 `β`를 생성할 수 있는 유일한 것은 `next`이고, 그렇게 하려면 두 인자를 필요로 할 것입니다. 각 인자는 그 자체로 언더스코어일 수 있습니다:

```lean
def Reader.bind {ρ : Type} {α : Type} {β : Type}
    (result : ρ → α) (next : α → ρ → β) : ρ → β :=
  fun env => next _ _
```

The two underscores have the following respective messages associated with them:

두 언더스코어는 다음과 같은 해당 메시지를 가집니다:

```
don't know how to synthesize placeholder
context:
ρ α β : Type
result : ρ → α
next : α → ρ → β
env : ρ
⊢ α
```

```
don't know how to synthesize placeholder
context:
ρ α β : Type
result : ρ → α
next : α → ρ → β
env : ρ
⊢ ρ
```

Attacking the first underscore, only one thing in the context can produce an `α`, namely `result`:

첫 번째 언더스코어를 공격하면, 맥락에서 `α`를 생성할 수 있는 유일한 것은 `result`입니다:

```lean
def Reader.bind {ρ : Type} {α : Type} {β : Type}
    (result : ρ → α) (next : α → ρ → β) : ρ → β :=
  fun env => next (result _) _
```

Now, both underscores have the same error message:

이제 두 언더스코어는 같은 오류 메시지를 가집니다.

Happily, both underscores can be replaced by `env`, yielding:

다행스럽게도, 두 언더스코어는 `env`로 바뀔 수 있으며, 다음을 생성합니다:

```lean
def Reader.bind {ρ : Type} {α : Type} {β : Type}
    (result : ρ → α) (next : α → ρ → β) : ρ → β :=
  fun env => next (result env) env
```

The final version can be obtained by undoing the unfolding of `Reader` and cleaning up the explicit details:

최종 버전은 `Reader`의 펼침을 취소하고 명시적인 세부사항을 정리함으로써 얻을 수 있습니다:

```lean
def Reader.bind
    (result : Reader ρ α)
    (next : α → Reader ρ β) : Reader ρ β :=
  fun env => next (result env) env
```

It's not always possible to write correct functions by simply “following the types”, and it carries the risk of not understanding the resulting program.
However, it can also be easier to understand a program that has been written than one that has not, and the process of filling in the underscores can bring insights.
In this case, `Reader.bind` works just like `bind` for `Id`, except it accepts an additional argument that it then passes down to its arguments, and this intuition can help in understanding how it works.

단순히 “타입을 따르는 것”만으로 항상 올바른 함수를 작성할 수 있는 것은 아니며, 결과 프로그램을 이해하지 못할 위험을 가지고 있습니다. 하지만 작성된 프로그램을 작성되지 않은 프로그램보다 이해하는 것이 더 쉬울 수 있으며, 언더스코어를 채우는 과정은 통찰력을 가져올 수 있습니다. 이 경우 `Reader.bind`는 `Id`의 `bind`와 마찬가지로 작동하지만, 추가 인자를 받아 이를 인자들에게 전달한다는 점을 제외하고, 이러한 직관은 그것이 어떻게 작동하는지 이해하는 데 도움이 될 수 있습니다.

`Reader.pure` (which generates constant functions) and `Reader.bind` obey the monad contract.
To check that `Reader.bind (Reader.pure v) f` is the same as `f v`, it's enough to replace definitions until the last step:

`Reader.pure`(상수 함수를 생성하는)와 `Reader.bind`는 monad 계약을 따릅니다. `Reader.bind (Reader.pure v) f`이 `f v`와 같은지 확인하려면 마지막 단계까지 정의를 바꾸면 충분합니다:

```
Reader.bind (Reader.pure v) f
= fun env => f ((Reader.pure v) env) env
= fun env => f ((fun _ => v) env) env
= fun env => f v env
= f v
```

For every function `f`, `fun x => f x` is the same as `f`, so the first part of the contract is satisfied.
To check that `Reader.bind r Reader.pure` is the same as `r`, a similar technique works:

모든 함수 `f`에 대해 `fun x => f x`는 `f`와 같으므로 계약의 첫 번째 부분이 만족됩니다. `Reader.bind r Reader.pure`이 `r`과 같은지 확인하려면 유사한 기법이 작동합니다:

```
Reader.bind r Reader.pure
= fun env => Reader.pure (r env) env
= fun env => (fun _ => (r env)) env
= fun env => r env
```

Because reader actions `r` are themselves functions, this is the same as `r`.
To check associativity, the same thing can be done for both `Reader.bind (Reader.bind r f) g` and `Reader.bind r (fun x => Reader.bind (f x) g)`:

reader 액션 `r`은 그 자체로 함수이기 때문에, 이는 `r`과 같습니다. 결합성을 확인하려면, `Reader.bind (Reader.bind r f) g`과 `Reader.bind r (fun x => Reader.bind (f x) g)` 모두에 대해 같은 일을 할 수 있습니다:

```
Reader.bind (Reader.bind r f) g
= fun env => g ((Reader.bind r f) env) env
= fun env => g ((fun env' => f (r env') env') env) env
= fun env => g (f (r env) env) env
```

`Reader.bind r (fun x => Reader.bind (f x) g)` reduces to the same expression:

`Reader.bind r (fun x => Reader.bind (f x) g)`은 같은 식으로 감소합니다:

```
Reader.bind r (fun x => Reader.bind (f x) g)
= Reader.bind r (fun x => fun env => g (f x env) env)
= fun env => (fun x => fun env' => g (f x env') env') (r env) env
= fun env => (fun env' => g (f (r env) env') env') env
= fun env => g (f (r env) env) env
```

Thus, a `Monad (Reader ρ)` instance is justified:

따라서 `Monad (Reader ρ)` 인스턴스가 정당화됩니다:

```lean
instance : Monad (Reader ρ) where
  pure x := fun _ => x
  bind x f := fun env => f (x env) env
```

The custom environments that will be passed to the expression evaluator can be represented as lists of pairs:

식 평가기에 전달될 사용자 정의 환경은 쌍의 리스트로 표현될 수 있습니다:

```lean
abbrev Env : Type := List (String × (Int → Int → Int))
```

For instance, `exampleEnv` contains maximum and modulus functions:

예를 들어, `exampleEnv`는 최댓값과 나머지 함수를 포함합니다:

```lean
def exampleEnv : Env := [("max", max), ("mod", (· % ·))]
```

Lean already has a function `List.lookup` that finds the value associated with a key in a list of pairs, so `applyPrimReader` needs only check whether the custom function is present in the environment. It returns `0` if the function is unknown:

Lean은 이미 쌍 리스트에서 키와 관련된 값을 찾는 `List.lookup` 함수를 가지고 있으므로, `applyPrimReader`는 사용자 정의 함수가 환경에 있는지만 확인하면 됩니다. 함수를 알 수 없으면 `0`을 반환합니다:

```lean
def applyPrimReader (op : String) (x : Int) (y : Int) : Reader Env Int :=
  read >>= fun env =>
  match env.lookup op with
  | none => pure 0
  | some f => pure (f x y)
```

Using `evaluateM` with `applyPrimReader` and an expression results in a function that expects an environment.
Luckily, `exampleEnv` is available:

`evaluateM`을 `applyPrimReader`와 식으로 사용하면 환경을 기대하는 함수가 생성됩니다. 다행히 `exampleEnv`를 사용할 수 있습니다:

```lean
open Expr Prim in
#eval
  evaluateM applyPrimReader
    (prim (other "max") (prim plus (const 5) (const 4))
      (prim times (const 3)
        (const 2)))
    exampleEnv
```

```
9
```

Like `Many`, `Reader` is an example of an effect that is difficult to encode in most languages, but type classes and monads make it just as convenient as any other effect.
The dynamic or special variables found in Common Lisp, Clojure, and Emacs Lisp can be used like `Reader`.
Similarly, Scheme and Racket's parameter objects are an effect that exactly correspond to `Reader`.
The Kotlin idiom of context objects can solve a similar problem, but they are fundamentally a means of passing function arguments automatically, so this idiom is more like the encoding as a reader monad than it is an effect in the language.

`Many`와 마찬가지로 `Reader`는 대부분의 언어에서 인코딩하기 어려운 효과의 예이지만, 타입 클래스와 monad는 다른 효과처럼 편리하게 만듭니다. Common Lisp, Clojure, Emacs Lisp에서 발견되는 동적 또는 특수 변수들은 `Reader`처럼 사용될 수 있습니다. 마찬가지로 Scheme과 Racket의 매개변수 객체는 정확히 `Reader`에 대응하는 효과입니다. Kotlin의 맥락 객체 관용구는 유사한 문제를 해결할 수 있지만, 본질적으로는 함수 인자를 자동으로 전달하는 수단이므로, 이 관용구는 언어의 효과이기보다는 reader monad로 인코딩하는 것과 더 유사합니다.

### 4.3.3.4. Exercises

#### 4.3.3.4.1. Checking Contracts

Check the monad contract for `State σ` and `Except ε`.

`State σ`과 `Except ε`에 대한 monad 계약을 확인합니다.

#### 4.3.3.4.2. Readers with Failure

Adapt the reader monad example so that it can also indicate failure when the custom operator is not defined, rather than just returning zero.
In other words, given these definitions:

reader monad 예제를 적응하여 사용자 정의 연산자가 정의되지 않았을 때 단순히 영을 반환하는 대신 실패를 나타낼 수 있도록 합니다. 즉, 이러한 정의들이 주어졌을 때:

```lean
def ReaderOption (ρ : Type) (α : Type) : Type := ρ → Option α
def ReaderExcept (ε : Type) (ρ : Type) (α : Type) : Type := ρ → Except ε α
```

do the following:

다음을 수행합니다:

1. Write suitable `pure` and `bind` functions
2. Check that these functions satisfy the `Monad` contract
3. Write `Monad` instances for `ReaderOption` and `ReaderExcept`
4. Define suitable `applyPrim` operators and test them with `evaluateM` on some example expressions

적절한 `pure`과 `bind` 함수를 작성합니다.
이 함수들이 `Monad` 계약을 만족하는지 확인합니다.
`ReaderOption`과 `ReaderExcept`에 대한 `Monad` 인스턴스를 작성합니다.
적절한 `applyPrim` 연산자를 정의하고 일부 예제 식에 대해 `evaluateM`으로 테스트합니다.

#### 4.3.3.4.3. A Tracing Evaluator

The `WithLog` type can be used with the evaluator to add optional tracing of some operations.
In particular, the type `ToTrace` can serve as a signal to trace a given operator:

`WithLog` 타입을 평가기와 함께 사용하여 일부 작업의 선택적 추적을 추가할 수 있습니다. 특히 `ToTrace` 타입은 주어진 연산자를 추적하는 신호로 작용할 수 있습니다:

```lean
inductive ToTrace (α : Type) : Type where
  | trace : α → ToTrace α
```

For the tracing evaluator, expressions should have type `Expr (Prim (ToTrace (Prim Empty)))`.
This says that the operators in the expression consist of addition, subtraction, and multiplication, augmented with traced versions of each. The innermost argument is `Empty` to signal that there are no further special operators inside of `trace`, only the three basic ones.

추적 평가기에서 식은 `Expr (Prim (ToTrace (Prim Empty)))` 타입을 가져야 합니다. 이는 식의 연산자가 덧셈, 뺄셈, 곱셈으로 구성되며, 각각의 추적된 버전으로 확장됨을 나타냅니다. 가장 안쪽 인자는 `trace` 내부에 추가 특수 연산자가 없고 오직 3개의 기본 연산자만 있음을 신호하기 위해 `Empty`입니다.

Do the following:

다음을 수행합니다:

1. Implement a `Monad (WithLog logged)` instance
2. Write an `applyTraced` function to apply traced operators to their arguments, logging both the operator and the arguments, with type `ToTrace (Prim Empty) → Int → Int → WithLog (Prim Empty × Int × Int) Int`

`Monad (WithLog logged)` 인스턴스를 구현합니다.
추적된 연산자를 인자들에 적용하는 `applyTraced` 함수를 작성하여 연산자와 인자를 모두 로깅합니다. 타입은 `ToTrace (Prim Empty) → Int → Int → WithLog (Prim Empty × Int × Int) Int`입니다.

If the exercise has been completed correctly, then

연습이 올바르게 완료되면,

```lean
open Expr Prim ToTrace in
#eval
  evaluateM applyTraced
    (prim (other (trace times))
      (prim (other (trace plus)) (const 1)
        (const 2))
      (prim (other (trace minus)) (const 3)
        (const 4)))
```

should result in

```
{ log := [(Prim.plus, 1, 2), (Prim.minus, 3, 4), (Prim.times, 3, -1)], val := -3 }
```

다음 결과가 나와야 합니다.

Hint: values of type `Prim Empty` will appear in the resulting log. In order to display them as a result of `#eval`, the following instances are required:

힌트: `Prim Empty` 타입의 값이 결과 로그에 나타납니다. `#eval`의 결과로 표시하려면 다음 인스턴스가 필요합니다:

```lean
deriving instance Repr for WithLog
deriving instance Repr for Empty
deriving instance Repr for Prim
```
