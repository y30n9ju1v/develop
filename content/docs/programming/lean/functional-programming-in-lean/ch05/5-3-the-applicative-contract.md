---
title: "어플리커티브 계약"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "어플리커티브 계약"
---

# 5.3. The Applicative Contract

Just like `Functor`, `Monad`, and types that implement `BEq` and `Hashable`, `Applicative` has a set of rules that all instances should adhere to.

`Functor`, `Monad`, `BEq`, `Hashable`를 구현하는 타입들처럼 `Applicative` 역시 모든 인스턴스가 따라야 하는 규칙 집합을 가지고 있습니다.

There are four rules that an applicative functor should follow:

Applicative functor가 따라야 할 네 가지 규칙이 있습니다:

1. It should respect identity, so `pure id <*> v = v`.

   항등성을 존중해야 하므로 `pure id <*> v = v`입니다.

2. It should respect function composition, so `pure (· ∘ ·) <*> u <*> v <*> w = u <*> (v <*> w)`.

   함수 합성을 존중해야 하므로 `pure (· ∘ ·) <*> u <*> v <*> w = u <*> (v <*> w)`입니다.

3. Sequencing pure operations should be a no-op, so `pure f <*> pure x = pure (f x)`.

   순수 연산의 순서 설정은 no-op이어야 하므로 `pure f <*> pure x = pure (f x)`입니다.

4. The ordering of pure operations doesn't matter, so `u <*> pure x = pure (fun f => f x) <*> u`.

   순수 연산의 순서는 중요하지 않으므로 `u <*> pure x = pure (fun f => f x) <*> u`입니다.

To check these for the `Applicative Option` instance, start by expanding `pure` into `some`.

`Applicative Option` 인스턴스에 대해 이를 확인하려면 `pure`를 `some`으로 확장하는 것부터 시작합니다.

The first rule states that `some id <*> v = v`.
The definition of `seq` for `Option` states that this is the same as `id <$> v = v`, which is one of the `Functor` rules that have already been checked.

첫 번째 규칙은 `some id <*> v = v`를 명시합니다.
`Option`에 대한 `seq`의 정의는 이것이 `id <$> v = v`와 같음을 나타내며, 이는 이미 확인된 `Functor` 규칙 중 하나입니다.

The second rule states that `some (· ∘ ·) <*> u <*> v <*> w = u <*> (v <*> w)`.
If any of `u`, `v`, or `w` is `none`, then both sides are `none`, so the property holds.
Assuming that `u` is `some f`, that `v` is `some g`, and that `w` is `some x`, then this is equivalent to saying that `some (· ∘ ·) <*> some f <*> some g <*> some x = some f <*> (some g <*> some x)`.
Evaluating the two sides yields the same result:

두 번째 규칙은 `some (· ∘ ·) <*> u <*> v <*> w = u <*> (v <*> w)`를 명시합니다.
`u`, `v`, 또는 `w` 중 어느 것이라도 `none`이면 양쪽 모두 `none`이므로 성질이 성립합니다.
`u`가 `some f`이고, `v`가 `some g`이고, `w`가 `some x`라고 가정하면, 이는 `some (· ∘ ·) <*> some f <*> some g <*> some x = some f <*> (some g <*> some x)`라고 말하는 것과 동치입니다.
양쪽을 평가하면 같은 결과를 얻습니다.

The third rule follows directly from the definition of `seq`:

세 번째 규칙은 `seq`의 정의로부터 직접 도출됩니다.

In the fourth case, assume that `u` is `some f`, because if it's `none`, both sides of the equation are `none`.

`some f <*> some x` evaluates directly to `some (f x)`, as does `some (fun g => g x) <*> some f`.

네 번째 경우에는 `u`가 `some f`라고 가정합니다. 왜냐하면 `none`이면 등식의 양쪽이 모두 `none`이기 때문입니다.

`some f <*> some x`는 직접 `some (f x)`로 평가되며, `some (fun g => g x) <*> some f`도 마찬가지입니다.

## 5.3.1. All Applicatives are Functors

The two operators for `Applicative` are enough to define `map`:

`Applicative`의 두 연산자는 `map`을 정의하기에 충분합니다:

```lean
def map [Applicative f] (g : α → β) (x : f α) : f β :=
  pure g <*> x
```

This can only be used to implement `Functor` if the contract for `Applicative` guarantees the contract for `Functor`, however.
The first rule of `Functor` is that `id <$> x = x`, which follows directly from the first rule for `Applicative`.
The second rule of `Functor` is that `map (f ∘ g) x = map f (map g x)`.
Unfolding the definition of `map` here results in `pure (f ∘ g) <*> x = pure f <*> (pure g <*> x)`.
Using the rule that sequencing pure operations is a no-op, the left side can be rewritten to `pure (· ∘ ·) <*> pure f <*> pure g <*> x`.
This is an instance of the rule that states that applicative functors respect function composition.

이는 `Applicative`의 계약이 `Functor`의 계약을 보장할 때에만 `Functor`를 구현하는 데 사용될 수 있습니다.

`Functor`의 첫 번째 규칙은 `id <$> x = x`이며, 이는 `Applicative`의 첫 번째 규칙으로부터 직접 도출됩니다.

`Functor`의 두 번째 규칙은 `map (f ∘ g) x = map f (map g x)`입니다.
여기서 `map`의 정의를 펼치면 `pure (f ∘ g) <*> x = pure f <*> (pure g <*> x)`를 얻습니다.
순수 연산의 순서 설정이 no-op이라는 규칙을 사용하면, 좌변을 `pure (· ∘ ·) <*> pure f <*> pure g <*> x`로 다시 쓸 수 있습니다.
이는 applicative functor가 함수 합성을 존중한다는 규칙의 한 인스턴스입니다.

This justifies a definition of `Applicative` that extends `Functor`, with a default definition of `map` given in terms of `pure` and `seq`:

이는 `Functor`를 확장하는 `Applicative`의 정의를 정당화하며, `pure`와 `seq`의 관점에서 `map`의 기본 정의를 제공합니다:

```lean
class Applicative (f : Type → Type) extends Functor f where
  pure : α → f α
  seq : f (α → β) → (Unit → f α) → f β
  map g x := seq (pure g) (fun () => x)
```

## 5.3.2. All Monads are Applicative Functors

An instance of `Monad` already requires an implementation of `pure`.
Together with `bind`, this is enough to define `seq`:

`Monad`의 인스턴스는 이미 `pure`의 구현을 요구합니다.

`bind`와 함께 이는 `seq`를 정의하기에 충분합니다:

```lean
def seq [Monad m] (f : m (α → β)) (x : Unit → m α) : m β := do
  let g ← f
  let y ← x ()
  pure (g y)
```

Once again, checking that the `Monad` contract implies the `Applicative` contract will allow this to be used as a default definition for `seq` if `Monad` extends `Applicative`.

다시 한 번, `Monad` 계약이 `Applicative` 계약을 함축한다는 것을 확인하면 `Monad`가 `Applicative`를 확장할 때 이를 `seq`의 기본 정의로 사용할 수 있습니다.

The rest of this section consists of an argument that this implementation of `seq` based on `bind` in fact satisfies the `Applicative` contract.
One of the beautiful things about functional programming is that this kind of argument can be worked out on a piece of paper with a pencil, using the kinds of evaluation rules from [the initial section on evaluating expressions](../ch01/).
Thinking about the meanings of the operations while reading these arguments can sometimes help with understanding.

이 섹션의 나머지 부분은 `bind`를 기반으로 한 `seq`의 이 구현이 실제로 `Applicative` 계약을 만족한다는 논증으로 구성됩니다.
함수형 프로그래밍의 아름다운 점 중 하나는 이런 종류의 논증을 종이와 연필로 [초기 표현식 평가 섹션](../ch01/)의 평가 규칙을 사용하여 작성할 수 있다는 것입니다.
이러한 논증을 읽으면서 연산의 의미를 생각하는 것이 이해하는 데 도움이 될 수 있습니다.

Replacing `do`-notation with explicit uses of `>>=` makes it easier to apply the `Monad` rules:

`do`-표기법을 명시적인 `>>=` 사용으로 대체하면 `Monad` 규칙을 적용하기가 더 쉬워집니다:

```lean
def seq [Monad m] (f : m (α → β)) (x : Unit → m α) : m β :=
  f >>= fun g =>
  x () >>= fun y =>
  pure (g y)
```

To check that this definition respects identity, check that `seq (pure id) (fun () => v) = v`.
The left hand side is equivalent to `pure id >>= fun g => (fun () => v) () >>= fun y => pure (g y)`.
The unit function in the middle can be eliminated immediately, yielding `pure id >>= fun g => v >>= fun y => pure (g y)`.
Using the fact that `pure` is a left identity of `>>=`, this is the same as `v >>= fun y => pure (id y)`, which is `v >>= fun y => pure y`.
Because `fun x => f x` is the same as `f`, this is the same as `v >>= pure`, and the fact that `pure` is a right identity of `>>=` can be used to get `v`.

이 정의가 항등성을 존중하는지 확인하려면 `seq (pure id) (fun () => v) = v`를 확인합니다.
좌변은 `pure id >>= fun g => (fun () => v) () >>= fun y => pure (g y)`와 동등합니다.
중간의 unit 함수는 즉시 제거되어 `pure id >>= fun g => v >>= fun y => pure (g y)`를 얻습니다.

`pure`가 `>>=`의 좌항등원이라는 사실을 사용하면, 이는 `v >>= fun y => pure (id y)`와 같으며, 이는 `v >>= fun y => pure y`입니다.

`fun x => f x`가 `f`와 같으므로, 이는 `v >>= pure`와 같으며, `pure`가 `>>=`의 우항등원이라는 사실을 사용하여 `v`를 얻을 수 있습니다.

This kind of informal reasoning can be made easier to read with a bit of reformatting.
In the following chart, read "`EXPR1 ={ REASON }= EXPR2`" as "`EXPR1` is the same as `EXPR2` because `REASON`":

이런 종류의 비형식적 추론은 약간의 재포맷으로 더 쉽게 읽을 수 있습니다.
다음 차트에서 "`EXPR1 ={ REASON }= EXPR2`"를 "`EXPR1`은 `REASON` 때문에 `EXPR2`와 같습니다"로 읽으세요:

```
  seq (pure id) (fun () => v)
={ evaluation }=
  pure id >>= fun g => (fun () => v) () >>= fun y => pure (g y)
={ evaluation }=
  pure id >>= fun g => v >>= fun y => pure (g y)
={ pure is a left identity of >>= }=
  v >>= fun y => pure (id y)
={ evaluation }=
  v >>= fun y => pure y
={ fun x => f x is the same as f }=
  v >>= pure
={ pure is a right identity of >>= }=
  v
```

To check that it respects function composition, check that `pure (· ∘ ·) <*> u <*> v <*> w = u <*> (v <*> w)`.
The first step is to replace `<*>` with this definition of `seq`.
After that, a (somewhat long) series of steps that use the identity and associativity rules from the `Monad` contract is enough to get from one to the other:

함수 합성을 존중하는지 확인하려면 `pure (· ∘ ·) <*> u <*> v <*> w = u <*> (v <*> w)`를 확인합니다.
첫 번째 단계는 `<*>`를 이 `seq`의 정의로 대체하는 것입니다.
그 후 `Monad` 계약의 항등성과 결합 규칙을 사용하는 (다소 긴) 일련의 단계로 한쪽에서 다른 쪽으로 갈 수 있습니다:

```
  seq (seq (seq (pure (· ∘ ·)) (fun _ => u))
          (fun _ => v))
      (fun _ => w)
={ evaluation }=
  ((pure (· ∘ ·) >>= fun f =>
    u >>= fun x =>
    pure (f x)) >>= fun g =>
    v >>= fun y =>
    pure (g y)) >>= fun h =>
    w >>= fun z =>
    pure (h z)
={ pure is a left identity of >>= }=
  ((u >>= fun x =>
    pure (x ∘ ·)) >>= fun g =>
    v >>= fun y =>
    pure (g y)) >>= fun h =>
    w >>= fun z =>
    pure (h z)
={ insertion of parentheses for clarity }=
  ((u >>= fun x =>
    pure (x ∘ ·)) >>= (fun g =>
    v >>= fun y =>
    pure (g y))) >>= fun h =>
    w >>= fun z =>
    pure (h z)
={ associativity of >>= }=
  (u >>= fun x =>
    pure (x ∘ ·) >>= fun g =>
    v >>= fun y => pure (g y)) >>= fun h =>
    w >>= fun z =>
    pure (h z)
={ pure is a left identity of >>= }=
  (u >>= fun x =>
    v >>= fun y =>
    pure (x ∘ y)) >>= fun h =>
    w >>= fun z =>
    pure (h z)
={ associativity of >>= }=
  u >>= fun x =>
    v >>= fun y =>
    pure (x ∘ y) >>= fun h =>
    w >>= fun z =>
    pure (h z)
={ pure is a left identity of >>= }=
  u >>= fun x =>
    v >>= fun y =>
    w >>= fun z =>
    pure ((x ∘ y) z)
={ definition of function composition }=
  u >>= fun x =>
    v >>= fun y =>
    w >>= fun z =>
    pure (x (y z))
```

Time to start moving backwards!

```
  u >>= fun x =>
    v >>= fun y =>
    w >>= fun z =>
    pure (x (y z))
={ pure is a left identity of >>= }=
  u >>= fun x =>
    v >>= fun y =>
    w >>= fun z =>
    pure (y z) >>= fun q =>
    pure (x q)
={ associativity of >>= }=
  u >>= fun x =>
    v >>= fun y =>
    (w >>= fun p =>
    pure (y p)) >>= fun q =>
    pure (x q)
={ associativity of >>= }=
  u >>= fun x =>
    (v >>= fun y =>
    w >>= fun q =>
    pure (y q)) >>= fun z =>
    pure (x z)
={ this includes the definition of seq }=
  u >>= fun x =>
    seq v (fun () => w) >>= fun q =>
    pure (x q)
={ this also includes the definition of seq }=
  seq u (fun () => seq v (fun () => w))
```

To check that sequencing pure operations is a no-op:

순수 연산의 순서 설정이 no-op인지 확인:

```
  seq (pure f) (fun () => pure x)
={ replacing seq with its definition }=
  pure f >>= fun g =>
    pure x >>= fun y =>
    pure (g y)
={ pure is a left identity of >>= }=
  pure f >>= fun g =>
    pure (g x)
={ pure is a left identity of >>= }=
  pure (f x)
```

And finally, to check that the ordering of pure operations doesn't matter:

그리고 마지막으로 순수 연산의 순서가 중요하지 않은지 확인:

```
  seq u (fun () => pure x)
={ replacing seq with its definition }=
  u >>= fun f =>
    pure x >>= fun y =>
    pure (f y)
={ pure is a left identity of >>= }=
  u >>= fun f =>
    pure (f x)
={ clever replacement of one expression by an equivalent one that makes the rule match }=
  u >>= fun f =>
    pure ((fun g => g x) f)
={ pure is a left identity of >>= }=
  pure (fun g => g x) >>= fun h =>
    u >>= fun f =>
    pure (h f)
={ definition of seq }=
  seq (pure (fun f => f x)) (fun () => u)
```

This justifies a definition of `Monad` that extends `Applicative`, with a default definition of `seq`:

이는 `Applicative`를 확장하는 `Monad`의 정의를 정당화하며, `seq`의 기본 정의를 제공합니다.

```lean
class Monad (m : Type → Type) extends Applicative m where
  bind : m α → (α → m β) → m β
  seq f x :=
    bind f fun g =>
    bind (x ()) fun y =>
    pure (g y)
```

`Applicative`'s own default definition of `map` means that every `Monad` instance automatically generates `Applicative` and `Functor` instances as well.

`Applicative`의 자체 기본 `map` 정의는 모든 `Monad` 인스턴스가 자동으로 `Applicative` 및 `Functor` 인스턴스도 생성함을 의미합니다.

## 5.3.3. Additional Stipulations

In addition to adhering to the individual contracts associated with each type class, combined implementations `Functor`, `Applicative` and `Monad` should work equivalently to these default implementations.
In other words, a type that provides both `Applicative` and `Monad` instances should not have an implementation of `seq` that works differently from the version that the `Monad` instance generates as a default implementation.
This is important because polymorphic functions may be refactored to replace a use of `>>=` with an equivalent use of `<*>`, or a use of `<*>` with an equivalent use of `>>=`.
This refactoring should not change the meaning of programs that use this code.

각 타입 클래스와 연관된 개별 계약을 준수하는 것 외에도, `Functor`, `Applicative`, `Monad`의 결합 구현은 이러한 기본 구현과 동등하게 작동해야 합니다.
다시 말해, `Applicative`와 `Monad` 인스턴스를 모두 제공하는 타입은 `Monad` 인스턴스가 기본 구현으로 생성하는 버전과 다르게 작동하는 `seq`의 구현을 가져서는 안 됩니다.
이는 다형 함수가 `>>=`의 사용을 `<*>`의 동등한 사용으로 대체하거나, `<*>`의 사용을 `>>=`의 동등한 사용으로 대체하도록 리팩토링될 수 있기 때문에 중요합니다.
이 리팩토링은 이 코드를 사용하는 프로그램의 의미를 변경해서는 안 됩니다.

This rule explains why `Validate.andThen` should not be used to implement `bind` in a `Monad` instance.
On its own, it obeys the monad contract.
However, when it is used to implement `seq`, the behavior is not equivalent to `seq` itself.
To see where they differ, take the example of two computations, both of which return errors.
Start with an example of a case where two errors should be returned, one from validating a function (which could have just as well resulted from a prior argument to the function), and one from validating an argument:

이 규칙은 `Validate.andThen`이 `Monad` 인스턴스에서 `bind`를 구현하는 데 사용되어서는 안 되는 이유를 설명합니다.
그 자체로는 monad 계약을 따릅니다.
그러나 `seq`를 구현하는 데 사용될 때, 동작이 `seq` 자체와 동등하지 않습니다.
어디서 차이가 나는지 보려면, 둘 다 오류를 반환하는 두 계산의 예를 들어보세요.
두 개의 오류가 반환되어야 하는 경우의 예부터 시작하세요. 하나는 함수를 검증할 때(함수의 이전 인수로부터 야기될 수 있음), 하나는 인수를 검증할 때:

```lean
def notFun : Validate String (Nat → String) :=
  .errors { head := "First error", tail := [] }
def notArg : Validate String Nat :=
  .errors { head := "Second error", tail := [] }
```

Combining them with the version of `<*>` from `Validate`'s `Applicative` instance results in both errors being reported to the user:

`Validate`의 `Applicative` 인스턴스에서 `<*>`의 버전과 결합하면 두 오류가 모두 사용자에게 보고됩니다.

Using the version of `seq` that was implemented with `>>=`, here rewritten to `andThen`, results in only the first error being available:

`>>=`로 구현된 `seq`의 버전을 사용하면, 여기서 `andThen`으로 다시 쓰면, 첫 번째 오류만 사용 가능합니다:
