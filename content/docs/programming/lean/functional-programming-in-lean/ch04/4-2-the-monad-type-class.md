---
title: "4.2. Monad 타입 클래스"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "모든 Monad에 대해 다형적으로 동작하는 연산자와 API를 다룹니다"
---

# 4.2. The Monad Type Class

Rather than having to import an operator like `ok` or `andThen` for each type that is a monad, the Lean standard library contains a type class that allow them to be overloaded, so that the same operators can be used for *any* monad.
Monads have two operations, which are the equivalent of `ok` and `andThen`:

각 타입이 Monad일 때 `ok` 또는 `andThen`과 같은 연산자를 가져올 필요가 없도록, Lean 표준 라이브러리는 이러한 연산자들이 오버로드될 수 있도록 하는 타입 클래스를 포함하고 있어서 모든 Monad에 대해 동일한 연산자를 사용할 수 있습니다. Monad는 `ok`와 `andThen`의 동등한 두 가지 연산을 가집니다:

```lean
class Monad (m : Type → Type) where
  pure : α → m α
  bind : m α → (α → m β) → m β
```

This definition is slightly simplified.
The actual definition in the Lean library is somewhat more involved, and will be presented later.

이 정의는 약간 단순화되어 있습니다. Lean 라이브러리의 실제 정의는 훨씬 더 복잡하며 나중에 제시될 것입니다.

As an example, `firstThirdFifthSeventh` was defined separately for `Option α` and `Except String α` return types.
Now, it can be defined polymorphically for *any* monad.
It does, however, require a lookup function as an argument, because different monads might fail to find a result in different ways.
The infix version of `bind` is `>>=`, which plays the same role as `~~>` in the examples.

예를 들어, `firstThirdFifthSeventh`는 `Option α`와 `Except String α` 반환 타입에 대해 별도로 정의되었습니다. 이제 모든 Monad에 대해 다형적으로 정의할 수 있습니다. 그러나 다양한 Monad가 다양한 방식으로 결과를 찾지 못할 수 있으므로 조회 함수를 인수로 요구합니다. `bind`의 중위 버전은 `>>=`이며, 이는 예제에서 `~~>`와 동일한 역할을 합니다.

```lean
def firstThirdFifthSeventh [Monad m] (lookup : List α → Nat → m α)
    (xs : List α) : m (α × α × α × α) :=
  lookup xs 0 >>= fun first =>
  lookup xs 2 >>= fun third =>
  lookup xs 4 >>= fun fifth =>
  lookup xs 6 >>= fun seventh =>
  pure (first, third, fifth, seventh)
```

Given example lists of slow mammals and fast birds, this implementation of `firstThirdFifthSeventh` can be used with `Option`:

느린 포유류와 빠른 새들의 예시 리스트가 주어진 경우, `firstThirdFifthSeventh`의 이 구현은 `Option`과 함께 사용될 수 있습니다:

```lean
def slowMammals : List String :=
  ["Three-toed sloth", "Slow loris"]
def fastBirds : List String := [
  "Peregrine falcon",
  "Saker falcon",
  "Golden eagle",
  "Gray-headed albatross",
  "Spur-winged goose",
  "Swift",
  "Anna's hummingbird"
]
```

```lean
#eval firstThirdFifthSeventh (fun xs i => xs[i]?) slowMammals
```

```
none
```

```lean
#eval firstThirdFifthSeventh (fun xs i => xs[i]?) fastBirds
```

```
some ("Peregrine falcon", "Golden eagle", "Spur-winged goose", "Anna's hummingbird")
```

After renaming `Except`'s lookup function `get` to something more specific, the very same implementation of `firstThirdFifthSeventh` can be used with `Except` as well:

`Except`의 조회 함수 `get`을 더 구체적인 것으로 이름을 바꾼 후, `firstThirdFifthSeventh`의 동일한 구현을 `Except`와 함께도 사용할 수 있습니다:

```lean
def getOrExcept (xs : List α) (i : Nat) : Except String α :=
  match xs[i]? with
  | none =>
    Except.error s!"Index {i} not found (maximum is {xs.length - 1})"
  | some x =>
    Except.ok x
```

```lean
#eval firstThirdFifthSeventh getOrExcept slowMammals
```

```
Except.error "Index 2 not found (maximum is 1)"
```

```lean
#eval firstThirdFifthSeventh getOrExcept fastBirds
```

```
Except.ok ("Peregrine falcon", "Golden eagle", "Spur-winged goose", "Anna's hummingbird")
```

The fact that `m` must have a `Monad` instance means that the `>>=` and `pure` operations are available.

`m`이 `Monad` 인스턴스를 가져야 한다는 사실은 `>>=`과 `pure` 연산을 사용할 수 있다는 의미입니다.

## 4.2.1. General Monad Operations

Because many different types are monads, functions that are polymorphic over *any* monad are very powerful.
For example, the function `mapM` is a version of `map` that uses a `Monad` to sequence and combine the results of applying a function:

많은 서로 다른 타입이 Monad이므로, 모든 Monad에 대해 다형적인 함수는 매우 강력합니다. 예를 들어, 함수 `mapM`은 함수 적용 결과를 순서대로 나열하고 결합하기 위해 `Monad`를 사용하는 `map`의 버전입니다:

```lean
def mapM [Monad m] (f : α → m β) : List α → m (List β)
  | [] => pure []
  | x :: xs =>
    f x >>= fun hd =>
    mapM f xs >>= fun tl =>
    pure (hd :: tl)
```

The return type of the function argument `f` determines which `Monad` instance will be used.
In other words, `mapM` can be used for functions that produce logs, for functions that can fail, or for functions that use mutable state.
Because `f`'s type determines the available effects, they can be tightly controlled by API designers.

함수 인수 `f`의 반환 타입은 어떤 `Monad` 인스턴스를 사용할지 결정합니다. 즉, `mapM`은 로그를 생성하는 함수, 실패할 수 있는 함수, 또는 가변 상태를 사용하는 함수에 사용될 수 있습니다. `f`의 타입이 사용 가능한 부작용을 결정하므로, API 설계자들은 이들을 엄격하게 제어할 수 있습니다.

As described in [this chapter's introduction](../ch04/), `State σ α` represents programs that make use of a mutable variable of type `σ` and return a value of type `α`.
These programs are actually functions from a starting state to a pair of a value and a final state.
The `Monad` class requires that its parameter expect a single type argument—that is, it should be a `Type → Type`.
This means that the instance for `State` should mention the state type `σ`, which becomes a parameter to the instance:

[이 장의 소개](../ch04/)에서 설명한 대로, `State σ α`는 `σ` 타입의 가변 변수를 사용하고 `α` 타입의 값을 반환하는 프로그램을 나타냅니다. 이러한 프로그램은 실제로 시작 상태에서 값과 최종 상태의 쌍으로 가는 함수입니다. `Monad` 클래스는 단일 타입 인수를 기대하는 매개변수를 요구합니다(즉, `Type → Type`이어야 합니다). 이는 `State`에 대한 인스턴스가 상태 타입 `σ`를 언급해야 하며, 이는 인스턴스의 매개변수가 됩니다:

```lean
instance : Monad (State σ) where
  pure x := fun s => (s, x)
  bind first next :=
    fun s =>
      let (s', x) := first s
      next x s'
```

This means that the type of the state cannot change between calls to `get` and `set` that are sequenced using `bind`, which is a reasonable rule for stateful computations.
The operator `increment` increases a saved state by a given amount, returning the old value:

이는 `bind`를 사용하여 순서대로 연결된 `get`과 `set` 호출 사이에 상태의 타입이 변경될 수 없다는 의미이며, 이는 상태 저장 계산에 대한 합리적인 규칙입니다. 연산자 `increment`는 저장된 상태를 주어진 양만큼 증가시키고 이전 값을 반환합니다:

```lean
def increment (howMuch : Int) : State Int Int :=
  get >>= fun i =>
  set (i + howMuch) >>= fun () =>
  pure i
```

Using `mapM` with `increment` results in a program that computes the sum of the entries in a list.
More specifically, the mutable variable contains the sum so far, while the resulting list contains a running sum.
In other words, `mapM increment` has type `List Int → State Int (List Int)`, and expanding the definition of `State` yields `List Int → Int → (Int × List Int)`.
It takes an initial sum as an argument, which should be `0`:

`mapM`을 `increment`와 함께 사용하면 리스트의 항목 합을 계산하는 프로그램이 생성됩니다. 더 구체적으로, 가변 변수는 지금까지의 합을 포함하고, 결과 리스트는 누계 합을 포함합니다. 즉, `mapM increment`는 `List Int → State Int (List Int)` 타입을 가지며, `State`의 정의를 확장하면 `List Int → Int → (Int × List Int)`를 얻습니다. 초기 합을 인수로 받으며, 이는 `0`이어야 합니다:

```lean
#eval mapM increment [1, 2, 3, 4, 5] 0
```

```
(15, [0, 1, 3, 6, 10])
```

A [logging effect](../ch04/) can be represented using `WithLog`.
Just like `State`, its `Monad` instance is polymorphic with respect to the type of the logged data:

[로깅 부작용](../ch04/)은 `WithLog`를 사용하여 나타낼 수 있습니다. `State`와 마찬가지로, 그 `Monad` 인스턴스는 로깅된 데이터의 타입에 대해 다형적입니다:

```lean
instance : Monad (WithLog logged) where
  pure x := {log := [], val := x}
  bind result next :=
    let {log := thisOut, val := thisRes} := result
    let {log := nextOut, val := nextRes} := next thisRes
    {log := thisOut ++ nextOut, val := nextRes}
```

`saveIfEven` is a function that logs even numbers but returns its argument unchanged:

`saveIfEven`은 짝수를 로깅하지만 인수를 변경되지 않은 상태로 반환하는 함수입니다:

```lean
def saveIfEven (i : Int) : WithLog Int Int :=
  (if isEven i then
     save i
   else pure ()) >>= fun () =>
  pure i
```

Using this function with `mapM` results in a log containing even numbers paired with an unchanged input list:

이 함수를 `mapM`과 함께 사용하면 짝수를 포함하는 로그가 변경되지 않은 입력 리스트와 쌍을 이루어 생성됩니다:

```lean
#eval mapM saveIfEven [1, 2, 3, 4, 5]
```

```
{ log := [2, 4], val := [1, 2, 3, 4, 5] }
```

## 4.2.2. The Identity Monad

Monads encode programs with effects, such as failure, exceptions, or logging, into explicit representations as data and functions.
Sometimes, however, an API will be written to use a monad for flexibility, but the API's client may not require any encoded effects.
The *identity monad* is a monad that has no effects.
It allows pure code to be used with monadic APIs:

Monad는 실패, 예외, 또는 로깅과 같은 부작용이 있는 프로그램을 데이터 및 함수로 명시적 표현으로 인코딩합니다. 그러나 때로는 API가 유연성을 위해 Monad를 사용하도록 작성되지만, API의 클라이언트는 인코딩된 부작용을 요구하지 않을 수 있습니다. 항등 Monad는 부작용이 없는 Monad입니다. 이는 순수 코드가 Monadic API와 함께 사용될 수 있도록 합니다:

```lean
def Id (t : Type) : Type := t
instance : Monad Id where
  pure x := x
  bind x f := f x
```

The type of `pure` should be `α → Id α`, but `Id α` reduces to just `α`.
Similarly, the type of `bind` should be `α → (α → Id β) → Id β`.
Because this reduces to `α → (α → β) → β`, the second argument can be applied to the first to find the result.

`pure`의 타입은 `α → Id α`이어야 하지만, `Id α`는 단순히 `α`로 축약됩니다. 마찬가지로, `bind`의 타입은 `α → (α → Id β) → Id β`이어야 합니다. 이는 `α → (α → β) → β`로 축약되므로, 두 번째 인수는 결과를 찾기 위해 첫 번째 인수에 적용될 수 있습니다.

With the identity monad, `mapM` becomes equivalent to `map`
To call it this way, however, Lean requires a hint that the intended monad is `Id`:

항등 Monad를 사용하면 `mapM`은 `map`과 동등해집니다. 그러나 이런 방식으로 호출하려면 Lean은 의도한 Monad가 `Id`임을 나타내는 힌트가 필요합니다:

```lean
def numbers := mapM (m := Id) (do return · + 1) [1, 2, 3, 4, 5]
```

Using `mapM` in a context in which the type doesn't provide any specific hints about which monad is to be used results in an "instance problem is stuck" message:

타입이 어떤 Monad를 사용할지에 대한 구체적인 힌트를 제공하지 않는 컨텍스트에서 `mapM`을 사용하면 "instance problem is stuck" 메시지가 나타납니다:

```lean
def numbers := mapM (do return · + 1) [1, 2, 3, 4, 5]
```

```
typeclass instance problem is stuck
  Pure ?m.6

Note: Lean will not try to resolve this typeclass instance problem because the type argument to `Pure` is a metavariable. This argument must be fully determined before Lean will try to resolve the typeclass.

Hint: Adding type annotations and supplying implicit arguments to functions can give Lean more information for typeclass resolution. For example, if you have a variable `x` that you intend to be a `Nat`, but Lean reports it as having an unresolved type like `?m`, replacing `x` with `(x : Nat)` can get typeclass resolution un-stuck.
```

## 4.2.3. The Monad Contract

Just as every pair of instances of `BEq` and `Hashable` should ensure that any two equal values have the same hash, there is a contract that each instance of `Monad` should obey.
First, `pure` should be a left identity of `bind`.
That is, `bind (pure v) f` should be the same as `f v`.
Secondly, `pure` should be a right identity of `bind`, so `bind v pure` is the same as `v`.
Finally, `bind` should be associative, so `bind (bind v f) g` is the same as `bind v (fun x => bind (f x) g)`.

`BEq`과 `Hashable`의 모든 인스턴스 쌍이 두 개의 동일한 값이 동일한 해시를 가지도록 보장해야 하는 것처럼, `Monad`의 각 인스턴스가 준수해야 할 계약이 있습니다. 먼저, `pure`는 `bind`의 좌측 항등원이어야 합니다. 즉, `bind (pure v) f`는 `f v`와 동일해야 합니다. 둘째, `pure`는 `bind`의 우측 항등원이어야 하므로, `bind v pure`는 `v`와 동일합니다. 마지막으로, `bind`는 결합적이어야 하므로, `bind (bind v f) g`는 `bind v (fun x => bind (f x) g)`와 동일합니다.

This contract specifies the expected properties of programs with effects more generally.
Because `pure` has no effects, sequencing its effects with `bind` shouldn't change the result.
The associative property of `bind` basically says that the sequencing bookkeeping itself doesn't matter, so long as the order in which things are happening is preserved.

이 계약은 부작용이 있는 프로그램의 예상 속성을 더 일반적으로 지정합니다. `pure`는 부작용이 없으므로, `bind`로 그 부작용을 순서대로 연결해도 결과는 변하지 않아야 합니다. `bind`의 결합적 속성은 기본적으로 순서대로 연결하는 기록 자체는 중요하지 않으며, 일이 일어나는 순서가 보존되는 한 상관없다는 의미입니다.

## 4.2.4. Exercises

### 4.2.4.1. Mapping on a Tree

Define a function `BinTree.mapM`.
By analogy to `mapM` for lists, this function should apply a monadic function to each data entry in a tree, as a preorder traversal.
The type signature should be:

`BinTree.mapM` 함수를 정의하세요. 리스트에 대한 `mapM`과의 유추에 의해, 이 함수는 트리의 각 데이터 항목에 Monadic 함수를 사전 순서 순회로 적용해야 합니다. 타입 시그니처는 다음과 같아야 합니다:

```lean
def BinTree.mapM [Monad m] (f : α → m β) : BinTree α → m (BinTree β)
```

### 4.2.4.2. The Option Monad Contract

First, write a convincing argument that the `Monad` instance for `Option` satisfies the monad contract.
Then, consider the following instance:

먼저 `Option`에 대한 `Monad` 인스턴스가 Monad 계약을 만족한다는 설득력 있는 논거를 작성하세요. 그 다음 다음 인스턴스를 고려하세요:

```lean
instance : Monad Option where
  pure x := some x
  bind opt next := none
```

Both methods have the correct type.
Why does this instance violate the monad contract?

두 메서드 모두 올바른 타입을 가지고 있습니다. 이 인스턴스가 Monad 계약을 위반하는 이유는 무엇입니까?
