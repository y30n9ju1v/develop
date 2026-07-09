---
title: "A Monad Construction Kit"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "A Monad Construction Kit"
---

# 6.2. A Monad Construction Kit

`ReaderT` is far from the only useful monad transformer.
This section describes a number of additional transformers.
Each monad transformer consists of the following:

`ReaderT`는 유일한 유용한 Monad Transformer와는 거리가 멉니다. 이 섹션에서는 여러 추가 Transformer를 설명합니다. 각 Monad Transformer는 다음으로 구성됩니다:

1. A definition or datatype `T` that takes a monad as an argument.
   It should have a type like `(Type u → Type v) → Type u → Type v`, though it may accept additional arguments prior to the monad.
2. A `Monad` instance for `T m` that relies on an instance of `Monad m`. This enables the transformed monad to be used as a monad.
3. A `MonadLift` instance that translates actions of type `m α` into actions of type `T m α`, for arbitrary monads `m`. This enables actions from the underlying monad to be used in the transformed monad.

1. Monad를 인수로 받는 정의 또는 데이터타입 `T`. 이는 `(Type u → Type v) → Type u → Type v` 같은 타입을 가져야 하지만 Monad 이전의 추가 인수를 수락할 수 있습니다.
2. `Monad m` 인스턴스에 의존하는 `T m`의 `Monad` 인스턴스. 이를 통해 변환된 Monad를 Monad로 사용할 수 있습니다.
3. 임의의 Monad `m`에 대해 `m α` 타입의 액션을 `T m α` 타입의 액션으로 변환하는 `MonadLift` 인스턴스. 이를 통해 기본 Monad의 액션을 변환된 Monad에서 사용할 수 있습니다.

Furthermore, the `Monad` instance for the transformer should obey the contract for `Monad`, at least if the underlying `Monad` instance does.
In addition, `monadLift (pure x : m α)` should be equivalent to `pure x` in the transformed monad, and `monadLift` should distribute over `bind` so that `monadLift (x >>= f : m α)` is the same as `(monadLift x : m α) >>= fun y => monadLift (f y)`.

또한 Transformer의 `Monad` 인스턴스는 최소한 기본 `Monad` 인스턴스가 그렇게 하면 `Monad`의 계약을 준수해야 합니다. 또한 `monadLift (pure x : m α)`는 변환된 Monad에서 `pure x`와 동등해야 하며, `monadLift`는 `bind`에 대해 분배되어야 하므로 `monadLift (x >>= f : m α)`는 `(monadLift x : m α) >>= fun y => monadLift (f y)`와 동일합니다.

Many monad transformers additionally define type classes in the style of `MonadReader` that describe the actual effects available in the monad.
This can provide more flexibility: it allows programs to be written that rely only on an interface, and don't constrain the underlying monad to be implemented by a given transformer.
The type classes are a way for programs to express their requirements, and monad transformers are a convenient way to meet these requirements.

많은 Monad Transformer는 `MonadReader` 스타일의 타입 클래스를 추가로 정의하여 Monad에서 사용 가능한 실제 효과를 설명합니다. 이는 더 많은 유연성을 제공할 수 있습니다: 프로그램이 인터페이스에만 의존하도록 하고 기본 Monad가 주어진 Transformer로 구현되도록 제약하지 않습니다. 타입 클래스는 프로그램이 요구사항을 표현하는 방법이며, Monad Transformer는 이러한 요구사항을 충족하는 편리한 방법입니다.

## 6.2.1. Failure with `OptionT`

Failure, represented by the `Option` monad, and exceptions, represented by the `Except` monad, both have corresponding transformers.
In the case of `Option`, failure can be added to a monad by having it contain values of type `Option α` where it would otherwise contain values of type `α`.
For example, `IO (Option α)` represents `IO` actions that don't always return a value of type `α`.
This suggests the definition of the monad transformer `OptionT`:

`Option` Monad로 표현되는 실패와 `Except` Monad로 표현되는 예외 모두 해당하는 Transformer를 가지고 있습니다. `Option`의 경우 실패는 그렇지 않으면 `α` 타입의 값을 포함하는 Monad에 `Option α` 타입의 값을 포함하도록 하여 추가될 수 있습니다. 예를 들어 `IO (Option α)`는 항상 `α` 타입의 값을 반환하지 않는 `IO` 액션을 나타냅니다. 이는 Monad Transformer `OptionT`의 정의를 제안합니다:

`def OptionT (m : Type u → Type v) (α : Type u) : Type v :=
m (Option α)`

As an example of `OptionT` in action, consider a program that asks the user questions.
The function `getSomeInput` asks for a line of input and removes whitespace from both ends.
If the resulting trimmed input is non-empty, then it is returned, but the function fails if there are no non-whitespace characters:

`OptionT`의 실제 작동 예로 사용자에게 질문을 하는 프로그램을 생각해봅시다. `getSomeInput` 함수는 입력 줄을 요청하고 양쪽 끝에서 공백을 제거합니다. 결과 자른 입력이 비어있지 않으면 반환되지만 공백 문자가 없으면 함수는 실패합니다:

`def getSomeInput : OptionT IO String := do
let input ← (← IO.getStdin).getLine
let trimmed := input.trim
if trimmed == "" then
failure
else pure trimmed`

This particular application tracks users with their name and their favorite species of beetle:

`structure UserInfo where
name : String
favoriteBeetle : String`

Asking the user for input is no more verbose than a function that uses only `IO` would be:

이 특정 애플리케이션은 사용자를 이름과 즐겨찾기 甲虫(딱정벌레) 종으로 추적합니다.

사용자에게 입력을 요청하는 것은 `IO`만 사용하는 함수만큼 장황하지 않습니다:

`def getUserInfo : OptionT IO UserInfo := do
IO.println "What is your name?"
let name ← getSomeInput
IO.println "What is your favorite species of beetle?"
let beetle ← getSomeInput
pure ⟨name, beetle⟩`

However, because the function runs in an `OptionT IO` context rather than just in `IO`, failure in the first call to `getSomeInput` causes the whole `getUserInfo` to fail, with control never reaching the question about beetles.
The main function, `interact`, invokes `getUserInfo` in a purely `IO` context, which allows it to check whether the call succeeded or failed by matching on the inner `Option`:

그러나 함수가 단순히 `IO`가 아닌 `OptionT IO` 컨텍스트에서 실행되기 때문에 첫 번째 `getSomeInput` 호출의 실패로 인해 전체 `getUserInfo`가 실패하며 제어가 甲虫에 대한 질문에 도달하지 않습니다. `interact` 메인 함수는 순수 `IO` 컨텍스트에서 `getUserInfo`를 호출하며, 이를 통해 내부 `Option`과 일치시켜 호출이 성공했는지 실패했는지 확인할 수 있습니다:

`def interact : IO Unit := do
match ← getUserInfo with
| none =>
IO.eprintln "Missing info"
| some ⟨name, beetle⟩ =>
IO.println s!"Hello {name}, whose favorite beetle is {beetle}."`

### 6.2.1.1. The Monad Instance

Writing the monad instance reveals a difficulty.
Based on the types, `pure` should use `pure` from the underlying monad `m` together with `some`.
Just as `bind` for `Option` branches on the first argument, propagating `none`, `bind` for `OptionT` should run the monadic action that makes up the first argument, branch on the result, and then propagate `none`.

Monad 인스턴스를 작성하면 어려움이 드러납니다. 타입을 기반으로 `pure`는 `some`과 함께 기본 Monad `m`에서 `pure`를 사용해야 합니다. `Option`에 대한 `bind`가 첫 번째 인수에 대해 분기하고 `none`을 전파하는 것처럼 `OptionT`에 대한 `bind`는 첫 번째 인수를 구성하는 Monadic 액션을 실행하고 결과에 대해 분기한 다음 `none`을 전파해야 합니다.
Following this sketch yields the following definition, which Lean does not accept:

`` instance [Monad m] : Monad (OptionT m) where
pure x := failed to synthesize
Pure (OptionT m)

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.pure Application type mismatch: The argument
some x
has type
Option α✝
but is expected to have type
α✝
in the application
pure (some x)(some x)
bind action next := do
failed to synthesize
Bind (OptionT m)

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.match (← action) with
| Type mismatch
none
has type
Option ?m.24
but is expected to have type
α✝none => pure none
| some v => next v ``

The error message shows a cryptic type mismatch:

```
Application type mismatch: The argument
  some x
has type
  Option α✝
but is expected to have type
  α✝
in the application
  pure (some x)
```

The problem here is that Lean is selecting the wrong `Monad` instance for the surrounding use of `pure`.
Similar errors occur for the definition of `bind`.
One solution is to use type annotations to guide Lean to the correct `Monad` instance:

`instance [Monad m] : Monad (OptionT m) where
pure x := (pure (some x) : m (Option _))
bind action next := (do
match (← action) with
| none => pure none
| some v => next v : m (Option _))`

While this solution works, it is inelegant and the code becomes a bit noisy.

An alternative solution is to define functions whose type signatures guide Lean to the correct instances.
In fact, `OptionT` could have been defined as a structure:

이 해결책이 작동하지만 우아하지 않으며 코드가 약간 시끄러워집니다. 대신 타입 시그니처가 Lean을 올바른 인스턴스로 안내하는 함수를 정의하는 것입니다. 사실 `OptionT`는 구조로 정의될 수 있습니다:

`structure OptionT (m : Type u → Type v) (α : Type u) : Type v where
run : m (Option α)`

This would solve the problem, because the constructor `OptionT.mk` and the field accessor `OptionT.run` would guide type class inference to the correct instances.
The downside to doing this is that the resulting code is more complicated, and these structures can make it more difficult to read proofs.
The best of both worlds can be achieved by defining functions that serve the same role as the constructor `OptionT.mk` and the field `OptionT.run`, but that work with the direct definition:

이는 생성자 `OptionT.mk`와 필드 접근자 `OptionT.run`이 타입 클래스 추론을 올바른 인스턴스로 안내하기 때문에 문제를 해결할 것입니다. 이를 하는 단점은 결과 코드가 더 복잡해지고 이러한 구조는 증명을 읽기 더 어렵게 만들 수 있다는 것입니다. 생성자 `OptionT.mk` 및 필드 `OptionT.run`과 동일한 역할을 하지만 직접 정의에서 작동하는 함수를 정의하여 두 세계의 최고를 달성할 수 있습니다:

`def OptionT.mk (x : m (Option α)) : OptionT m α := x
def OptionT.run (x : OptionT m α) : m (Option α) := x`

Both functions return their inputs unchanged, but they indicate the boundary between code that is intended to present the interface of `OptionT` and code that is intended to present the interface of the underlying monad `m`.
Using these helpers, the `Monad` instance becomes more readable:

두 함수 모두 입력을 변경하지 않고 반환하지만 `OptionT`의 인터페이스를 표현하려는 코드와 기본 Monad `m`의 인터페이스를 표현하려는 코드 사이의 경계를 나타냅니다. 이러한 도우미를 사용하면 `Monad` 인스턴스가 더 읽기 쉬워집니다:

`instance [Monad m] : Monad (OptionT m) where
pure x := OptionT.mk (pure (some x))
bind action next := OptionT.mk do
match ← action with
| none => pure none
| some v => next v`

Here, the use of `OptionT.mk` indicates that its arguments should be considered as code that uses the interface of `m`, which allows Lean to select the correct `Monad` instances.

After defining the monad instance, it's a good idea to check that the monad contract is satisfied.
The first step is to show that `bind (pure v) f` is the same as `f v`.
Here's the steps:

여기서 `OptionT.mk`의 사용은 해당 인수가 `m`의 인터페이스를 사용하는 코드로 간주되어야 함을 나타내며, 이를 통해 Lean이 올바른 `Monad` 인스턴스를 선택할 수 있습니다. Monad 인스턴스를 정의한 후 Monad 계약이 충족되었는지 확인하는 것이 좋습니다. 첫 번째 단계는 `bind (pure v) f`가 `f v`와 동일함을 보이는 것입니다. 다음은 단계입니다.

The second rule states that `bind w pure` is the same as `w`.
To demonstrate this, unfold the definitions of `bind` and `pure`, yielding:

두 번째 규칙은 `bind w pure`가 `w`와 동일함을 명시합니다. 이를 시연하려면 `bind` 및 `pure`의 정의를 펼쳐서:

`OptionT.mk do
match ← w with
| none => pure none
| some v => pure (some v)`

In this pattern match, the result of both cases is the same as the pattern being matched, just with `pure` around it.
In other words, it is equivalent to `w >>= fun y => pure y`, which is an instance of `m`'s second monad rule.

The final rule states that `bind (bind v f) g` is the same as `bind v (fun x => bind (f x) g)`.
It can be checked in the same way, by expanding the definitions of `bind` and `pure` and then delegating to the underlying monad `m`.

이 패턴 매칭에서 두 경우 모두의 결과는 일치하는 패턴과 동일하며, 단지 주변에 `pure`가 있을 뿐입니다. 다시 말해 `w >>= fun y => pure y`와 동등하며, 이는 `m`의 두 번째 Monad 규칙의 인스턴스입니다. 최종 규칙은 `bind (bind v f) g`가 `bind v (fun x => bind (f x) g)`와 동일함을 명시합니다. `bind` 및 `pure`의 정의를 확장한 다음 기본 Monad `m`에 위임하여 동일한 방식으로 확인할 수 있습니다.

### 6.2.1.2. An `Alternative` Instance

One convenient way to use `OptionT` is through the `Alternative` type class.
Successful return is already indicated by `pure`, and the `failure` and `orElse` methods of `Alternative` provide a way to write a program that returns the first successful result from a number of subprograms:

`OptionT`를 사용하는 편리한 방법 중 하나는 `Alternative` 타입 클래스를 통한 것입니다. 성공한 반환은 이미 `pure`로 표시되며, `Alternative`의 `failure` 및 `orElse` 메서드는 여러 하위 프로그램에서 첫 번째 성공한 결과를 반환하는 프로그램을 작성하는 방법을 제공합니다:

`instance [Monad m] : Alternative (OptionT m) where
failure := OptionT.mk (pure none)
orElse x y := OptionT.mk do
match ← x with
| some result => pure (some result)
| none => y ()`

### 6.2.1.3. Lifting

Lifting an action from `m` to `OptionT m` only requires wrapping `some` around the result of the computation:

`m`에서 `OptionT m`으로 액션을 lifting하려면 계산 결과 주변에 `some`을 감싸기만 하면 됩니다:

`instance [Monad m] : MonadLift m (OptionT m) where
monadLift action := OptionT.mk do
pure (some (← action))`

## 6.2.2. Exceptions

The monad transformer version of `Except` is very similar to the monad transformer version of `Option`.
Adding exceptions of type `ε` to some monadic action of type `m``α` can be accomplished by adding exceptions to `α`, yielding type `m (Except ε α)`:

`Except`의 Monad Transformer 버전은 `Option`의 Monad Transformer 버전과 매우 유사합니다. `ε` 타입의 예외를 `m α` 타입의 Monadic 액션에 추가하는 것은 `α`에 예외를 추가하여 `m (Except ε α)` 타입을 생성하여 달성할 수 있습니다:

`def ExceptT (ε : Type u) (m : Type u → Type v) (α : Type u) : Type v :=
m (Except ε α)`

`OptionT` provides `OptionT.mk` and `OptionT.run` functions to guide the type checker towards the correct `Monad` instances.
This trick is also useful for `ExceptT`:

`OptionT`는 타입 체커를 올바른 `Monad` 인스턴스로 안내하는 `OptionT.mk` 및 `OptionT.run` 함수를 제공합니다. 이 트릭은 `ExceptT`에도 유용합니다:

`def ExceptT.mk {ε α : Type u} (x : m (Except ε α)) : ExceptT ε m α := x
def ExceptT.run {ε α : Type u} (x : ExceptT ε m α) : m (Except ε α) := x`

The `Monad` instance for `ExceptT` is also very similar to the instance for `OptionT`.
The only difference is that it propagates a specific error value, rather than `none`:

`ExceptT`의 `Monad` 인스턴스는 `OptionT`의 인스턴스와도 매우 유사합니다. 유일한 차이점은 `none` 대신 특정 오류 값을 전파한다는 것입니다:

`instance {ε : Type u} {m : Type u → Type v} [Monad m] :
Monad (ExceptT ε m) where
pure x := ExceptT.mk (pure (Except.ok x))
bind result next := ExceptT.mk do
match ← result with
| .error e => pure (.error e)
| .ok x => next x`

The type signatures of `ExceptT.mk` and `ExceptT.run` contain a subtle detail: they annotate the universe levels of `α` and `ε` explicitly.
If they are not explicitly annotated, then Lean generates a more general type signature in which they have distinct polymorphic universe variables.
However, the definition of `ExceptT` expects them to be in the same universe, because they can both be provided as arguments to `m`.
This can lead to a problem in the `Monad` instance where the universe level solver fails to find a working solution:

`ExceptT.mk` 및 `ExceptT.run`의 타입 시그니처는 미묘한 세부 사항을 포함합니다: `α` 및 `ε`의 Universe 레벨을 명시적으로 주석합니다. 명시적으로 주석하지 않으면 Lean은 더 일반적인 타입 시그니처를 생성하며 이들은 구별되는 다형 Universe 변수를 가집니다. 그러나 `ExceptT`의 정의는 이들이 동일한 Universe에 있기를 기대합니다. 왜냐하면 둘 다 `m`의 인수로 제공될 수 있기 때문입니다. 이는 Universe 레벨 해결자가 작동하는 해결책을 찾지 못하는 `Monad` 인스턴스에서 문제가 될 수 있습니다:

`def ExceptT.mk (x : m (Except ε α)) : ExceptT ε m α := x``instance {ε : Type u} {m : Type u → Type v} [Monad m] :
Monad (ExceptT ε m) stuck at solving universe constraint
max ?u.19220 ?u.19221 =?= u
while trying to unify
ExceptT ε m α✝ : Type v
with
ExceptT.{max ?u.19221 ?u.19220, v} ε m α✝ : Type vstuck at solving universe constraint
max ?u.19380 ?u.19381 =?= u
while trying to unify
ExceptT ε m β✝ : Type v
with
ExceptT.{max ?u.19381 ?u.19380, v} ε m β✝ : Type vwhere
pure x := ExceptT.mk (pure (Except.ok x))
bind result next := ExceptT.mk do
match (← result) with
| stuck at solving universe constraint
max ?u.19220 ?u.19221 =?= u
while trying to unify
ExceptT ε m α✝ : Type v
with
ExceptT.{max ?u.19221 ?u.19220, v} ε m α✝ : Type v.error e => pure (.error e)
| .ok x => next x`

```
stuck at solving universe constraint
  max ?u.19380 ?u.19381 =?= u
while trying to unify
  ExceptT ε m β✝ : Type v
with
  ExceptT.{max ?u.19381 ?u.19380, v} ε m β✝ : Type v
```

This kind of error message is typically caused by underconstrained universe variables.
Diagnosing it can be tricky, but a good first step is to look for reused universe variables in some definitions that are not reused in others.

Unlike `Option`, the `Except` datatype is typically not used as a data structure.
It is always used as a control structure with its `Monad` instance.
This means that it is reasonable to lift `Except ε` actions into `ExceptT ε m`, as well as actions from the underlying monad `m`.
Lifting `Except` actions into `ExceptT` actions is done by wrapping them in `m`'s `pure`, because an action that only has exception effects cannot have any effects from the monad `m`:

`instance [Monad m] : MonadLift (Except ε) (ExceptT ε m) where
monadLift action := ExceptT.mk (pure action)`

Because actions from `m` do not have any exceptions in them, their value should be wrapped in `Except.ok`.
This can be accomplished using the fact that `Functor` is a superclass of `Monad`, so applying a function to the result of any monadic computation can be accomplished using `Functor.map`:

`instance [Monad m] : MonadLift m (ExceptT ε m) where
monadLift action := ExceptT.mk (.ok <$> action)`

### 6.2.2.1. Type Classes for Exceptions

Exception handling fundamentally consists of two operations: the ability to throw exceptions, and the ability to recover from them.
Thus far, this has been accomplished using the constructors of `Except` and pattern matching, respectively.
However, this ties a program that uses exceptions to one specific encoding of the exception handling effect.
Using a type class to capture these operations allows a program that uses exceptions to be used in *any* monad that supports throwing and catching.

Throwing an exception should take an exception as an argument, and it should be allowed in any context where a monadic action is requested.
The “any context” part of the specification can be written as a type by writing `m α`—because there's no way to produce a value of any arbitrary type, the `throw` operation must be doing something that causes control to leave that part of the program.
Catching an exception should accept any monadic action together with a handler, and the handler should explain how to get back to the action's type from an exception:

`class MonadExcept (ε : outParam (Type u)) (m : Type v → Type w) where
throw : ε → m α
tryCatch : m α → (ε → m α) → m α`

The universe levels on `MonadExcept` differ from those of `ExceptT`.
In `ExceptT`, both `ε` and `α` have the same level, while `MonadExcept` imposes no such limitation.
This is because `MonadExcept` never places an exception value inside of `m`.
The most general universe signature recognizes the fact that `ε` and `α` are completely independent in this definition.
Being more general means that the type class can be instantiated for a wider variety of types.

An example program that uses `MonadExcept` is a simple division service.
The program is divided into two parts: a frontend that supplies a user interface based on strings that handles errors, and a backend that actually does the division.
Both the frontend and the backend can throw exceptions, the former for ill-formed input and the latter for division by zero errors.
The exceptions are an inductive type:

`inductive Err where
| divByZero
| notANumber : String → Err`

The backend checks for zero, and divides if it can:

`def divBackend [Monad m] [MonadExcept Err m] (n k : Int) : m Int :=
if k == 0 then
throw .divByZero
else pure (n / k)`

The frontend's helper `asNumber` throws an exception if the string it is passed is not a number.
The overall frontend converts its inputs to `Int`s and calls the backend, handling exceptions by returning a friendly string error:

`def asNumber [Monad m] [MonadExcept Err m] (s : String) : m Int :=
match s.toInt? with
| none => throw (.notANumber s)
| some i => pure i``def divFrontend [Monad m] [MonadExcept Err m] (n k : String) : m String :=
tryCatch (do pure (toString (← divBackend (← asNumber n) (← asNumber k))))
fun
| .divByZero => pure "Division by zero!"
| .notANumber s => pure s!"Not a number: \"{s}\""`

Throwing and catching exceptions is common enough that Lean provides a special syntax for using `MonadExcept`.
Just as `+` is short for `HAdd.hAdd`, `try` and `catch` can be used as shorthand for the `tryCatch` method:

`def divFrontend [Monad m] [MonadExcept Err m] (n k : String) : m String :=
try
pure (toString (← divBackend (← asNumber n) (← asNumber k)))
catch
| .divByZero => pure "Division by zero!"
| .notANumber s => pure s!"Not a number: \"{s}\""`

In addition to `Except` and `ExceptT`, there are useful `MonadExcept` instances for other types that may not seem like exceptions at first glance.
For example, failure due to `Option` can be seen as throwing an exception that contains no data whatsoever, so there is an instance of `MonadExcept Unit Option` that allows `try``...``catch` `...` syntax to be used with `Option`.

## 6.2.3. State

A simulation of mutable state is added to a monad by having monadic actions accept a starting state as an argument and return a final state together with their result.
The bind operator for a state monad provides the final state of one action as an argument to the next action, threading the state through the program.
This pattern can also be expressed as a monad transformer:

`def StateT (σ : Type u)
(m : Type u → Type v) (α : Type u) : Type (max u v) :=
σ → m (α × σ)`

Once again, the monad instance is very similar to that for `State`.
The only difference is that the input and output states are passed around and returned in the underlying monad, rather than with pure code:

`instance [Monad m] : Monad (StateT σ m) where
pure x := fun s => pure (x, s)
bind result next := fun s => do
let (v, s') ← result s
next v s'`

The corresponding type class has `get` and `set` methods.
One downside of `get` and `set` is that it becomes too easy to `set` the wrong state when updating it.
This is because retrieving the state, updating it, and saving the updated state is a natural way to write some programs.
For example, the following program counts the number of diacritic-free English vowels and consonants in a string of letters:

`structure LetterCounts where
vowels : Nat
consonants : Nat
deriving Repr
inductive Err where
| notALetter : Char → Err
deriving Repr
def vowels :=
let lowerVowels := "aeiuoy"
lowerVowels ++ lowerVowels.map (·.toUpper)
def consonants :=
let lowerConsonants := "bcdfghjklmnpqrstvwxz"
lowerConsonants ++ lowerConsonants.map (·.toUpper )
def countLetters (str : String) : StateT LetterCounts (Except Err) Unit :=
let rec loop (chars : List Char) := do
match chars with
| [] => pure ()
| c :: cs =>
let st ← get
let st' ←
if c.isAlpha then
if vowels.contains c then
pure {st with vowels := st.vowels + 1}
else if consonants.contains c then
pure {st with consonants := st.consonants + 1}
else -- modified or non-English letter
pure st
else throw (.notALetter c)
set st'
loop cs
loop str.toList`

It would be very easy to write `set st` instead of `set st'`.
In a large program, this kind of mistake can lead to difficult-to-diagnose bugs.

While using a nested action for the call to `get` would solve this problem, it can't solve all such problems.
For example, a function might update a field on a structure based on the values of two other fields.
This would require two separate nested-action calls to `get`.
Because the Lean compiler contains optimizations that are only effective when there is a single reference to a value, duplicating the references to the state might lead to code that is significantly slower.
Both the potential performance problem and the potential bug can be worked around by using `modify`, which transforms the state using a function:

`def countLetters (str : String) : StateT LetterCounts (Except Err) Unit :=
let rec loop (chars : List Char) := do
match chars with
| [] => pure ()
| c :: cs =>
if c.isAlpha then
if vowels.contains c then
modify fun st => {st with vowels := st.vowels + 1}
else if consonants.contains c then
modify fun st => {st with consonants := st.consonants + 1}
else -- modified or non-English letter
pure ()
else throw (.notALetter c)
loop cs
loop str.toList`

The type class contains a function akin to `modify` called `modifyGet`, which allows the function to both compute a return value and transform an old state in a single step.
The function returns a pair in which the first element is the return value, and the second element is the new state; `modify` just adds the constructor of `Unit` to the pair used in `modifyGet`:

`def modify [MonadState σ m] (f : σ → σ) : m Unit :=
modifyGet fun s => ((), f s)`

The definition of `MonadState` is as follows:

`class MonadState (σ : outParam (Type u)) (m : Type u → Type v) :
Type (max (u+1) v) where
get : m σ
set : σ → m PUnit
modifyGet : (σ → α × σ) → m α`

`PUnit` is a version of the `Unit` type that is universe-polymorphic to allow it to be in `Type u` instead of `Type`.
While it would be possible to provide a default implementation of `modifyGet` in terms of `get` and `set`, it would not admit the optimizations that make `modifyGet` useful in the first place, rendering the method useless.

## 6.2.4. `Of` Classes and `The` Functions

Thus far, each monad type class that takes extra information, like the type of exceptions for `MonadExcept` or the type of the state for `MonadState`, has this type of extra information as an output parameter.
For simple programs, this is generally convenient, because a monad that combines one use each of `StateT`, `ReaderT`, and `ExceptT` has only a single state type, environment type, and exception type.
As monads grow in complexity, however, they may involve multiple states or errors types.
In this case, the use of an output parameter makes it impossible to target both states in the same `do`-block.

For these cases, there are additional type classes in which the extra information is not an output parameter.
These versions of the type classes use the word `Of` in the name.
For example, `MonadStateOf` is like `MonadState`, but without an `outParam` modifier.

Instead of an `outParam`, these classes use a `semiOutParam` for their respective state, environment, or exception types.
Like an `outParam`, a `semiOutParam` is not required be known before Lean begins the process of searching for an instance.
However, there is an important difference: `outParam`s are ignored during the search for an instance, and as a result they are truly outputs.
If an `outParam` is known prior to the search, then Lean merely checks that the result of the search is the same as what was known.
On the other hand, a `semiOutParam` that is known prior to the start of the search can be used to narrow down candidates, just like an input parameter.

When a state monad's state type is an `outParam`, then each monad can have at most one type of state.
This is convenient, because it improves type inference: the state type can be inferred in more circumstances.
This is also inconvenient, because a monad built from multiple uses of `StateT` cannot provide a useful `MonadState` instance.
Using `MonadStateOf`, however, causes Lean to take the state type into account when it is available to select which instance to use, so one monad may provide multiple types of state.
The downside of this is that the resulting instance may not be the one that was intended when the state type has not been specified explicitly enough, which can lead to confusing error messages.

Similarly, there are versions of the type class methods that accept the type of the extra information as an *explicit*, rather than implicit, argument.
For `MonadStateOf`, there are `getThe` with type

`(σ : Type u) → {m : Type u → Type v} → [MonadStateOf σ m] → m σ`

and `modifyThe` with type

`(σ : Type u) → {m : Type u → Type v} → [MonadStateOf σ m] → (σ → σ) → m PUnit`

There is no `setThe` because the type of the new state is enough to decide which surrounding state monad transformer to use.

In the Lean standard library, there are instances of the non-`Of` versions of the classes defined in terms of the instances of the versions with `Of`.
In other words, implementing the `Of` version yields implementations of both.
It's generally a good idea to implement the `Of` version, and then start writing programs using the non-`Of` versions of the class, transitioning to the `Of` version if the output parameter becomes inconvenient.

## 6.2.5. Transformers and `Id`

The identity monad `Id` is the monad that has no effects whatsoever, to be used in contexts that expect a monad for some reason but where none is actually necessary.
Another use of `Id` is to serve as the bottom of a stack of monad transformers.
For instance, `StateT σ Id` works just like `State σ`.

## 6.2.6. Exercises

### 6.2.6.1. Monad Contract

Using pencil and paper, check that the rules of the monad transformer contract are satisfied for each monad transformer in this section.

### 6.2.6.2. Logging Transformer

Define a monad transformer version of `WithLog`.
Also define the corresponding type class `MonadWithLog`, and write a program that combines logging and exceptions.

### 6.2.6.3. Counting Files

Modify `doug`'s monad with `StateT` such that it counts the number of directories and files seen.
At the end of execution, it should display a report like:

```
  Viewed 38 files in 5 directories.
```
