---
title: "4.5. IO 모나드"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "IO Monad의 내부 구현과 세계 전달(world-passing) 방식 이해하기"
---

# 4.5. The IO Monad

`IO` as a monad can be understood from two perspectives, which were described in the section on [running programs](../ch02/).
Each can help to understand the meanings of `pure` and `bind` for `IO`.

Monad로서의 `IO`는 [프로그램 실행](../ch02/)에 대한 섹션에서 설명한 두 가지 관점에서 이해할 수 있습니다. 각 관점은 `IO`에 대한 `pure`과 `bind`의 의미를 이해하는 데 도움이 될 수 있습니다.

From the first perspective, an `IO` action is an instruction to Lean's run-time system.
For example, the instruction might be “read a string from this file descriptor, then re-invoke the pure Lean code with the string”.
This perspective is an *exterior* one, viewing the program from the perspective of the operating system.
In this case, `pure` is an `IO` action that does not request any effects from the RTS, and `bind` instructs the RTS to first carry out one potentially-effectful operation and then invoke the rest of the program with the resulting value.

첫 번째 관점에서 `IO` 액션은 Lean의 런타임 시스템에 대한 명령어입니다. 예를 들어, 명령어는 “이 파일 디스크립터에서 문자열을 읽고, 그 문자열로 순수 Lean 코드를 다시 호출하세요”일 수 있습니다. 이 관점은 운영 체제의 관점에서 프로그램을 보는 *외부* 관점입니다. 이 경우 `pure`는 RTS에서 효과를 요청하지 않는 `IO` 액션이고, `bind`는 RTS에게 먼저 잠재적으로 부작용이 있을 수 있는 작업을 수행한 다음 결과 값으로 프로그램의 나머지를 호출하도록 지시합니다.

From the second perspective, an `IO` action transforms the whole world.
`IO` actions are actually pure, because they receive a unique world as an argument and then return the changed world.
This perspective is an *interior* one that matches how `IO` is represented inside of Lean.
The world is represented in Lean as a token, and the `IO` monad is structured to make sure that each token is used exactly once.

두 번째 관점에서 `IO` 액션은 전체 세상을 변환합니다. `IO` 액션은 실제로는 순수합니다. 왜냐하면 고유한 세상을 인자로 받아 변환된 세상을 반환하기 때문입니다. 이 관점은 Lean 내부에서 `IO`가 표현되는 방식과 일치하는 *내부* 관점입니다. 세상은 Lean에서 토큰으로 표현되며, `IO` monad는 각 토큰이 정확히 한 번만 사용되도록 구조화되어 있습니다.

To see how this works, it can be helpful to peel back one definition at a time.
The `#print` command reveals the internals of Lean datatypes and definitions.
For example,

이것이 어떻게 작동하는지 보기 위해서는 한 번에 하나씩 정의를 벗겨내는 것이 도움이 될 수 있습니다. `#print` 명령은 Lean 데이터타입과 정의의 내부를 드러냅니다. 예를 들어,

```lean
#print Nat
```

results in

```
inductive Nat : Type
number of parameters: 0
constructors:
Nat.zero : Nat
Nat.succ : Nat → Nat
```

and

때로는 `#print`의 출력에 이 책에서 아직 제시되지 않은 Lean 기능이 포함될 수 있습니다. 예를 들어,

```lean
#print Char.isAlpha
```

```lean
#print List.isEmpty
```

results in

produces

```
def Char.isAlpha : Char → Bool :=
fun c => c.isUpper || c.isLower
```

```
def List.isEmpty.{u} : {α : Type u} → List α → Bool :=
fun {α} x =>
  match x with
  | [] => true
  | head :: tail => false
```

Sometimes, the output of `#print` includes Lean features that have not yet been presented in this book.
For example,

which includes a `.{u}` after the definition's name, and annotates types as `Type u` rather than just `Type`.
This can be safely ignored for now.

정의의 이름 뒤에 `.{u}`를 포함하고, 타입을 단순히 `Type`이 아닌 `Type u`로 주석 처리합니다. 지금은 이를 안전하게 무시할 수 있습니다.

Printing the definition of `IO` shows that it's defined in terms of simpler structures:

`IO`의 정의를 출력하면 더 간단한 구조로 정의되어 있음을 알 수 있습니다:

```lean
#print IO
```

```
@[reducible] def IO : Type → Type :=
EIO IO.Error
```

`IO.Error` represents all the errors that could be thrown by an `IO` action:

`IO.Error`는 `IO` 액션으로 인해 발생할 수 있는 모든 오류를 나타냅니다:

```lean
#print IO.Error
```

```
inductive IO.Error : Type
number of parameters: 0
constructors:
IO.Error.alreadyExists : Option String → UInt32 → String → IO.Error
IO.Error.otherError : UInt32 → String → IO.Error
IO.Error.resourceBusy : UInt32 → String → IO.Error
IO.Error.resourceVanished : UInt32 → String → IO.Error
IO.Error.unsupportedOperation : UInt32 → String → IO.Error
IO.Error.hardwareFault : UInt32 → String → IO.Error
IO.Error.unsatisfiedConstraints : UInt32 → String → IO.Error
IO.Error.illegalOperation : UInt32 → String → IO.Error
IO.Error.protocolError : UInt32 → String → IO.Error
IO.Error.timeExpired : UInt32 → String → IO.Error
IO.Error.interrupted : String → UInt32 → String → IO.Error
IO.Error.noFileOrDirectory : String → UInt32 → String → IO.Error
IO.Error.invalidArgument : Option String → UInt32 → String → IO.Error
IO.Error.permissionDenied : Option String → UInt32 → String → IO.Error
IO.Error.resourceExhausted : Option String → UInt32 → String → IO.Error
IO.Error.inappropriateType : Option String → UInt32 → String → IO.Error
IO.Error.noSuchThing : Option String → UInt32 → String → IO.Error
IO.Error.unexpectedEof : IO.Error
IO.Error.userError : String → IO.Error
```

`EIO ε α` represents `IO` actions that will either terminate with an error of type `ε` or succeed with a value of type `α`.
This means that, like the `Except ε` monad, the `IO` monad includes the ability to define error handling and exceptions.

`EIO ε α`는 `ε` 타입의 오류로 종료되거나 `α` 타입의 값으로 성공할 `IO` 액션을 나타냅니다. 즉, `Except ε` monad처럼 `IO` monad도 오류 처리 및 예외를 정의할 수 있는 기능을 포함합니다.

Peeling back another layer, `EIO` is itself defined in terms of a simpler structure:

더 깊은 레이어를 벗겨내면, `EIO`도 더 간단한 구조로 정의되어 있습니다:

```lean
#print EIO
```

```
def EIO : Type → Type → Type :=
fun ε α => EST ε IO.RealWorld α
```

The `EST` monad includes both errors and state—it's similar to a combination of `Except` and `State`.
It is defined using another type, `EST.Out`:

`EST` monad는 오류와 상태를 모두 포함하며, `Except`와 `State`의 조합과 유사합니다. 다른 타입인 `EST.Out`을 사용하여 정의됩니다:

```lean
#print EST
```

```
def EST : Type → Type → Type → Type :=
fun ε σ α => Void σ → EST.Out ε σ α
```

In other words, a program with type `EST ε σ α` is a function that accepts an initial state of type `σ` and returns an `EST.Out ε σ α`.
The state is wrapped in the type `Void`, which is an internal primitive that causes a value to be erased from compiled code; `Void σ` has the same representation as `Unit`.

다시 말해, `EST ε σ α` 타입의 프로그램은 `σ` 타입의 초기 상태를 받아들이고 `EST.Out ε σ α`를 반환하는 함수입니다. 상태는 `Void` 타입으로 래핑되는데, 이는 컴파일된 코드에서 값이 삭제되도록 하는 내부 primitive입니다. `Void σ`는 `Unit`과 같은 표현을 가집니다.

`EST.Out` is very much like the definition of `Except`, with one constructor that indicates a successful termination and one constructor that indicates an error:

`EST.Out`은 성공적인 종료를 나타내는 하나의 생성자와 오류를 나타내는 하나의 생성자를 가지는 `Except`의 정의와 매우 유사합니다:

```lean
#print EST.Out
```

```
inductive EST.Out : Type → Type → Type → Type
number of parameters: 3
constructors:
EST.Out.ok : {ε σ α : Type} → α → Void σ → EST.Out ε σ α
EST.Out.error : {ε σ α : Type} → ε → Void σ → EST.Out ε σ α
```

Just like `Except ε α`, the `ok` constructor includes a result of type `α`, and the `error` constructor includes an exception of type `ε`.
Unlike `Except`, both constructors have an additional state field that includes the final state of the computation.

`Except ε α`와 마찬가지로 `ok` 생성자는 `α` 타입의 결과를 포함하고, `error` 생성자는 `ε` 타입의 예외를 포함합니다. `Except`와 달리 두 생성자 모두 계산의 최종 상태를 포함하는 추가 상태 필드를 가집니다.

The `Monad` instance for `EST ε σ` requires `pure` and `bind`.
Just as with `State`, the implementation of `pure` for `EST` accepts an initial state and returns it unchanged, and just as with `Except`, it returns its argument in the `ok` constructor:

`EST ε σ`의 `Monad` 인스턴스는 `pure`과 `bind`를 필요로 합니다. `State`와 마찬가지로 `EST`의 `pure` 구현은 초기 상태를 받아들이고 변경되지 않은 상태로 반환하며, `Except`와 마찬가지로 `ok` 생성자에서 인자를 반환합니다:

```lean
#print EST.pure
```

```
protected def EST.pure : {α ε σ : Type} → α → EST ε σ α :=
fun {α ε σ} a s => EST.Out.ok a s
```

`protected` means that the full name `EST.pure` is needed even if the `EST` namespace has been opened.

`protected`는 `EST` 네임스페이스가 열려 있더라도 전체 이름 `EST.pure`이 필요함을 의미합니다.

Similarly, `bind` for `EST` takes an initial state as an argument.
It passes this initial state to its first action.
Like `bind` for `Except`, it then checks whether the result is an error.
If so, the error is returned unchanged and the second argument to `bind` remains unused.
If the result was a success, then the second argument is applied to both the returned value and to the resulting state.

마찬가지로 `EST`의 `bind`는 초기 상태를 인자로 받습니다. 이 초기 상태를 첫 번째 액션에 전달합니다. `Except`의 `bind`처럼 결과가 오류인지 확인합니다. 그렇다면 오류가 변경되지 않은 상태로 반환되고 `bind`의 두 번째 인자는 사용되지 않습니다. 결과가 성공이었다면 두 번째 인자는 반환된 값과 결과 상태 모두에 적용됩니다.

```lean
#print EST.bind
```

```
protected def EST.bind : {ε σ α β : Type} → EST ε σ α → (α → EST ε σ β) → EST ε σ β :=
fun {ε σ α β} x f s =>
  match x s with
  | EST.Out.ok a s => f a s
  | EST.Out.error e s => EST.Out.error e s
```

Putting all of this together, `IO` is a monad that tracks state and errors at the same time.
The collection of available errors is that given by the datatype `IO.Error`, which has constructors that describe many things that can go wrong in a program.
The state is a type that represents the real world, called `IO.RealWorld`.
Each basic `IO` action receives this real world and returns another one, paired either with an error or a result.
In `IO`, `pure` returns the world unchanged, while `bind` passes the modified world from one action into the next action.

이 모든 것을 종합하면 `IO`는 상태와 오류를 동시에 추적하는 monad입니다. 사용 가능한 오류의 모음은 `IO.Error` 데이터타입으로 주어지며, 프로그램에서 잘못될 수 있는 많은 것들을 설명하는 생성자들을 가집니다. 상태는 `IO.RealWorld`라고 불리는 실제 세상을 나타내는 타입입니다. 각 기본 `IO` 액션은 이 실제 세상을 받아 다른 세상을 반환하며, 오류 또는 결과와 쌍을 이룹니다. `IO`에서 `pure`은 세상을 변경하지 않은 상태로 반환하고, `bind`는 한 액션에서 수정된 세상을 다음 액션으로 전달합니다.

Because the entire universe doesn't fit in a computer's memory, the world being passed around is just a representation.
So long as world tokens are not re-used, the representation is safe.
The type `IO.RealWorld` is a trivial primitive type that does not need any representation at all, because it is only used inside of `Void`.

전체 우주가 컴퓨터의 메모리에 맞지 않기 때문에, 전달되는 세상은 단지 표현일 뿐입니다. 세상 토큰이 재사용되지 않는 한, 이 표현은 안전합니다. `IO.RealWorld` 타입은 `Void` 내부에서만 사용되기 때문에 어떤 표현도 필요하지 않은 평범한 primitive 타입입니다.
