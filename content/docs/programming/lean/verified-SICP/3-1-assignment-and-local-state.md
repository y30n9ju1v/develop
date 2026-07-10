---
title: "3.1. 배정과 지역 상태 (Assignment and Local State)"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["sicp", "lean", "lean4", "scheme", "mutable-state", "io-monad"]
categories: ["programming"]
description: "SICP 3장 1절의 아이디어(지역 상태 변수, set!, 은행 계좌 객체, 참조 투명성의 붕괴)를 Lean 4의 IO.Ref와 IO 모나드로 다시 짜 봅니다."
---

Everything in the first two chapters could be understood by substitution: replace a name with its value, reduce, repeat. Chapter 3 breaks that model on purpose. We start modeling things — bank accounts, random-number generators — whose behavior depends on their own history, and that means introducing *assignment*: the ability to change what a name refers to. Scheme calls this `set!`; this post is about what happens when the same idea lands in a language where, until now, every function signature has been a promise that nothing hidden could possibly change between two calls with the same arguments.

1장과 2장의 모든 것은 치환으로 이해할 수 있었습니다 — 이름을 값으로 바꾸고, 축약하고, 반복합니다. 3장은 이 모델을 일부러 깨뜨립니다. 이제 자기 자신의 과거 이력에 따라 동작이 달라지는 것들 — 은행 계좌, 난수 생성기 — 을 모델링하기 시작하는데, 이는 *배정(assignment)*, 즉 이름이 가리키는 것을 바꾸는 능력을 도입한다는 뜻입니다. Scheme은 이를 `set!`이라 부릅니다. 이 글은 같은 아이디어가, 지금까지 모든 함수 시그니처가 "같은 인자로 두 번 호출해도 숨겨진 무언가가 달라질 리 없다"는 약속이었던 언어에 떨어지면 무슨 일이 일어나는지에 관한 것입니다.

---

## 3.1.1. 지역 상태 변수

A `withdraw` procedure that models a bank account needs to remember a `balance` across calls, and return a different thing — the new balance, or a complaint — depending on what that balance currently is. Scheme reaches for a global mutable variable and `set!`:

은행 계좌를 모델링하는 `withdraw` 절차는 호출 사이에 `balance`를 기억해야 하고, 그 잔액이 지금 얼마인지에 따라 다른 것 — 새 잔액, 또는 불평 — 을 반환해야 합니다. Scheme은 전역 가변 변수와 `set!`을 씁니다.

Lean has no `set!` for an ordinary `def` — every top-level binding is exactly what SICP's first two chapters assumed all bindings were: a name for one fixed value, forever. To get a genuinely mutable cell, Lean makes us ask for one explicitly, as a value of type `IO.Ref α`, and every operation that reads or writes it has to happen inside `IO`:

Lean에는 평범한 `def`에 대한 `set!`이 없습니다 — 모든 최상위 바인딩은 정확히 SICP의 1, 2장이 모든 바인딩에 대해 가정했던 그대로입니다 — 하나의 고정된 값을 영원히 가리키는 이름입니다. 진짜로 가변적인 셀을 얻으려면, Lean은 우리가 그것을 `IO.Ref α` 타입의 값으로 명시적으로 요청하게 만들고, 그것을 읽거나 쓰는 모든 연산은 `IO` 안에서 일어나야 합니다.

```lean
def withdraw (balance : IO.Ref Int) (amount : Int) : IO (Except String Int) := do
  let bal ← balance.get
  if bal >= amount then
    balance.set (bal - amount)
    return .ok (bal - amount)
  else
    return .error "Insufficient funds"

#eval show IO Unit from do
  let balance ← IO.mkRef (100 : Int)
  IO.println (repr (← withdraw balance 25))
  IO.println (repr (← withdraw balance 25))
  IO.println (repr (← withdraw balance 60))
  IO.println (repr (← withdraw balance 15))
-- Except.ok 75
-- Except.ok 50
-- Except.error "Insufficient funds"
-- Except.ok 35
```

(Scheme의 문자열 메시지와 숫자를 한 함수가 둘 다 반환하는 동적 타입 자유로움 대신, `Except String Int`로 "충분하지 않을 수도 있다"는 것을 타입에 못박았습니다 — [2.1절](../2-1-introduction-to-data-abstraction/)의 `divIntervalSafe`와 같은 결정입니다.)

The problem SICP points out next — `balance` sitting exposed at top level, freely readable and writable by anything — has an even sharper answer in Lean than in Scheme. A `let`-bound `IO.Ref` captured inside a closure isn't just conventionally private; nothing outside that closure's scope even has a name that refers to it:

SICP가 다음으로 짚는 문제 — `balance`가 최상위에 그대로 노출되어 누구든 자유롭게 읽고 쓸 수 있다는 것 — 은 Lean에서 더 날카로운 답을 얻습니다. 클로저 안에 갇힌 `let`으로 묶인 `IO.Ref`는 관례적으로만 사적인 게 아니라, 그 클로저의 스코프 바깥에는 그것을 가리키는 이름 자체가 존재하지 않습니다.

```lean
def makeWithdraw (initialBalance : Int) : IO (Int → IO (Except String Int)) := do
  let balance ← IO.mkRef initialBalance
  pure fun amount => do
    let bal ← balance.get
    if bal >= amount then
      balance.set (bal - amount)
      return .ok (bal - amount)
    else
      return .error "Insufficient funds"

#eval show IO Unit from do
  let w1 ← makeWithdraw 100
  let w2 ← makeWithdraw 100
  IO.println (repr (← w1 50))
  IO.println (repr (← w2 70))
  IO.println (repr (← w2 40))
  IO.println (repr (← w1 40))
-- Except.ok 50
-- Except.ok 30
-- Except.error "Insufficient funds"
-- Except.ok 10
```

`makeWithdraw`'s type is worth staring at: `Int → IO (Int → IO (Except String Int))` — an ordinary function that, when run, produces *another* function, one that itself performs `IO` every time it's called. That double layering of `IO` is the type-level signature of "this returns an object with hidden mutable state," in exactly the sense SICP means it, and it's visible before we've read a single line of the implementation.

`makeWithdraw`의 타입은 뜯어볼 가치가 있습니다 — `Int → IO (Int → IO (Except String Int))`, 즉 실행되면 *또 다른* 함수를 만들어내는 평범한 함수인데, 그 함수 자체가 호출될 때마다 `IO`를 수행합니다. 이 이중으로 겹친 `IO`가 바로 "숨겨진 가변 상태를 가진 객체를 반환한다"는 것의 타입 수준 신호이며, SICP가 의도하는 바로 그 의미이고, 구현을 한 줄도 읽기 전에 이미 눈에 보입니다.

Scheme's `dispatch`-on-a-symbol style for a full bank account (`(acc 'withdraw)`, `(acc 'deposit)`) is really hand-rolled multiple dispatch — a table keyed by symbols that a typo can silently break. Lean gives us a structure of named, typed fields instead, each closing over the same `IO.Ref`:

전체 은행 계좌를 위한 Scheme의 "심볼로 디스패치하기" 스타일(`(acc 'withdraw)`, `(acc 'deposit)`)은 사실 손으로 만든 다중 디스패치입니다 — 오타 하나가 조용히 망가뜨릴 수 있는, 심볼을 키로 하는 테이블입니다. Lean은 대신 이름 붙고 타입이 있는 필드들의 구조체를 주고, 각 필드는 같은 `IO.Ref`를 감쌉니다.

```lean
structure Account where
  withdraw : Int → IO (Except String Int)
  deposit : Int → IO Int

def makeAccount (initialBalance : Int) : IO Account := do
  let balance ← IO.mkRef initialBalance
  pure {
    withdraw := fun amount => do
      let bal ← balance.get
      if bal >= amount then
        balance.set (bal - amount)
        return .ok (bal - amount)
      else
        return .error "Insufficient funds"
    deposit := fun amount => do
      balance.set ((← balance.get) + amount)
      balance.get
  }

#eval show IO Unit from do
  let acc ← makeAccount 100
  IO.println (repr (← acc.withdraw 50))
  IO.println (repr (← acc.withdraw 60))
  IO.println (repr (← acc.deposit 40))
  IO.println (repr (← acc.withdraw 60))
-- Except.ok 50
-- Except.error "Insufficient funds"
-- 90
-- Except.ok 30
```

`acc.withdraw`와 `acc.deposit`은 여전히 [2.4절](../2-4-multiple-representations-for-abstract-data/)의 메시지 패싱과 같은 정신입니다 — 다만 심볼과 `cond`로 손수 라우팅하는 대신, Lean의 필드 접근이 그 라우팅을 대신하고 오타는 컴파일 오류가 됩니다.

**연습문제 3.1 (Lean 버전)**: 반복 호출될 때마다 누적합을 유지하는 어큐뮬레이터입니다.

```lean
def makeAccumulator (initial : Int) : IO (Int → IO Int) := do
  let sum ← IO.mkRef initial
  pure fun amount => do
    sum.set ((← sum.get) + amount)
    sum.get

#eval show IO Unit from do
  let a ← makeAccumulator 5
  IO.println (← a 10)
  IO.println (← a 10)
-- 15
-- 25
```

---

## 3.1.2. 배정을 도입해서 얻는 이득

`set!`을 쓰지 않고도 같은 난수열을 얻을 수는 있습니다 — `rand-update`를 직접 호출하면 됩니다. 문제는 그러면 난수를 쓰는 프로그램의 모든 부분이 현재 시드 값을 명시적으로 기억해서 다음 호출에 넘겨야 한다는 것입니다. SICP는 이를 몬테카를로 시뮬레이션으로 보여줍니다 — 두 정수를 무작위로 골라 최대공약수가 1인 비율로 $\pi$를 근사하는 것입니다.

You could get the same sequence of numbers without `set!` at all, simply by calling `rand-update` directly. The catch is that then every part of the program using random numbers has to explicitly remember the current seed and thread it through to the next call. SICP demonstrates the cost with Monte Carlo simulation — estimating $\pi$ from the fraction of randomly-chosen integer pairs whose GCD is 1.

Lean lets us build both versions side by side, and the type signatures end up telling the whole story. First, the version with hidden state, where `rand` is an `IO` action that returns a new number (and mutates its seed) every time it's run:

Lean에서는 두 버전을 나란히 만들 수 있고, 타입 시그니처가 이야기 전체를 말해줍니다. 먼저, 숨겨진 상태를 가진 버전입니다. `rand`는 실행될 때마다 새 숫자를 반환하며(그리고 시드를 변경하며) `IO` 액션입니다.

```lean
def randUpdate (x : Nat) : Nat := (1103515245 * x + 12345) % 2147483648

def makeRand (seed : Nat) : IO (IO Nat) := do
  let state ← IO.mkRef seed
  pure do
    let x' := randUpdate (← state.get)
    state.set x'
    pure x'

def cesaroTest (rand : IO Nat) : IO Bool := do
  let a ← rand
  let b ← rand
  pure (Nat.gcd a b == 1)

partial def monteCarlo (trials : Nat) (experiment : IO Bool) : IO Float := do
  let rec iter (remaining passed : Nat) : IO Nat := do
    if remaining == 0 then pure passed
    else if ← experiment then iter (remaining - 1) (passed + 1)
    else iter (remaining - 1) passed
  let passed ← iter trials 0
  pure (Float.ofNat passed / Float.ofNat trials)

def estimatePi (trials : Nat) (rand : IO Nat) : IO Float := do
  let frac ← monteCarlo trials (cesaroTest rand)
  pure (Float.sqrt (6.0 / frac))

#eval show IO Float from do
  let rand ← makeRand 1
  estimatePi 10000 rand
```

`estimatePi`, `monteCarlo`, and `cesaroTest` never mention a seed — the whole random-number machinery is encapsulated behind the `IO Nat` action they're handed. Now the version SICP shows as the alternative, threading the seed explicitly through every call instead of hiding it behind `set!`:

`estimatePi`, `monteCarlo`, `cesaroTest` 어디에도 시드가 언급되지 않습니다 — 난수 기계 전체가 이들에게 건네지는 `IO Nat` 액션 뒤에 캡슐화되어 있습니다. 이제 SICP가 대안으로 보여주는 버전, 즉 시드를 `set!` 뒤에 숨기는 대신 매 호출마다 명시적으로 실어 나르는 버전입니다.

```lean
partial def randomGcdTest (trials : Nat) (initialX : Nat) : Float :=
  let rec iter (remaining passed x : Nat) : Float :=
    let x1 := randUpdate x
    let x2 := randUpdate x1
    if remaining == 0 then Float.ofNat passed / Float.ofNat trials
    else if Nat.gcd x1 x2 == 1 then iter (remaining - 1) (passed + 1) x2
    else iter (remaining - 1) passed x2
  iter trials 0 initialX

def estimatePiPure (trials : Nat) (initialX : Nat) : Float :=
  Float.sqrt (6.0 / randomGcdTest trials initialX)

#eval estimatePiPure 10000 1
```

Notice the type of `estimatePiPure`: `Nat → Nat → Float`, with no `IO` anywhere. SICP's prose has to *tell* the reader that threading state explicitly is "a painful breach of modularity" compared to hiding it in `rand`; Lean's type checker enforces the flip side of that trade for free — `randomGcdTest` and `estimatePiPure` are certifiably pure functions, referentially transparent by construction, precisely because they never touch an `IO.Ref`. Encapsulating the seed behind `makeRand` bought back the modularity SICP wants, but it cost exactly this: `estimatePi`'s type now has `IO` in it, an honest admission that calling it twice with the same `trials` can give different answers.

`estimatePiPure`의 타입을 눈여겨보세요 — `Nat → Nat → Float`이고 어디에도 `IO`가 없습니다. SICP의 산문은 독자에게 상태를 명시적으로 실어 나르는 것이 `rand` 뒤에 숨기는 것에 비해 "모듈성의 뼈아픈 훼손"이라고 *말해줘야* 하지만, Lean의 타입 검사기는 그 트레이드오프의 반대쪽 면을 공짜로 강제합니다 — `randomGcdTest`와 `estimatePiPure`는 `IO.Ref`를 전혀 건드리지 않기 때문에 구성상 순수하고 참조 투명함이 보장된 함수입니다. `makeRand` 뒤에 시드를 캡슐화한 것은 SICP가 원하는 모듈성을 되찾아 주었지만, 정확히 이 대가를 치렀습니다 — 이제 `estimatePi`의 타입에는 `IO`가 들어 있고, 이는 같은 `trials`로 두 번 호출해도 다른 답이 나올 수 있다는 것을 정직하게 인정하는 것입니다.

---

## 3.1.3. 배정을 도입하는 대가

SICP's central warning is that `set!` breaks the substitution model outright. `make-decrementer` (no assignment) can be traced by substituting `balance` for its value and reducing; `make-simplified-withdraw` (with `set!`) cannot, because the two occurrences of `balance` — before and after the mutation — need to mean different things, and substitution has no way to tell them apart.

SICP의 핵심 경고는 `set!`이 치환 모델을 완전히 깨뜨린다는 것입니다. `make-decrementer`(배정 없음)는 `balance`를 그 값으로 치환하고 축약해서 추적할 수 있지만, `make-simplified-withdraw`(`set!` 있음)는 그럴 수 없습니다 — `balance`의 두 등장(변이 전과 후)이 서로 다른 것을 의미해야 하는데, 치환은 이를 구분할 방법이 없기 때문입니다.

```lean
def makeDecrementer (balance : Int) : Int → Int :=
  fun amount => balance - amount

def makeSimplifiedWithdraw (initialBalance : Int) : IO (Int → IO Int) := do
  let balance ← IO.mkRef initialBalance
  pure fun amount => do
    balance.set ((← balance.get) - amount)
    balance.get
```

The two signatures already say what SICP spends a page proving: `makeDecrementer : Int → Int → Int` is a plain function of two arguments, fully explained by [1.1.5절](../1-1-elements-of-programming/)의 치환 모델, no caveats needed. `makeSimplifiedWithdraw : Int → IO (Int → IO Int)` cannot be reasoned about that way, and the `IO` in its type is exactly the marker telling us so — Lean doesn't need a page of prose to warn us substitution has stopped working here, because the type already refuses to typecheck as a substitution-friendly `Int → Int → Int` in the first place.

두 시그니처가 이미 SICP가 한 페이지를 들여 증명하는 것을 말해줍니다 — `makeDecrementer : Int → Int → Int`는 두 인자의 평범한 함수이고, [1.1.5절](../1-1-elements-of-programming/)의 치환 모델로 완전히 설명되며, 어떤 단서도 필요 없습니다. `makeSimplifiedWithdraw : Int → IO (Int → IO Int)`는 그런 식으로 추론할 수 없고, 그 타입 안의 `IO`가 정확히 그것을 알려주는 표지입니다 — Lean은 여기서 치환이 더 이상 통하지 않는다고 경고하는 데 산문 한 페이지가 필요 없습니다. 타입 자체가 애초에 치환 친화적인 `Int → Int → Int`로는 타입 검사를 통과하지 못하기 때문입니다.

### 같음과 변화

SICP's Peter-and-Paul example — two accounts with the same initial balance are "the same" only in the weak sense of behaving identically, while an *alias* (`paulAcc := peterAcc`) is the same in the strong sense that a withdrawal through one is visible through the other — translates directly, because `Account` in our Lean encoding really does carry a reference identity via the `IO.Ref` it closes over:

SICP의 피터-폴 예제 — 초기 잔액이 같은 두 계좌는 동일하게 동작한다는 약한 의미에서만 "같고", *별칭(alias)*(`paulAcc := peterAcc`)은 한쪽을 통한 출금이 다른 쪽에서도 보인다는 강한 의미에서 같습니다 — 은 그대로 옮겨집니다. 우리의 Lean 인코딩에서 `Account`가 감싸고 있는 `IO.Ref`를 통해 진짜로 참조 정체성을 지니기 때문입니다.

```lean
#eval show IO Unit from do
  let peterAcc ← makeAccount 100
  let paulAcc := peterAcc  -- 별칭: 내부 IO.Ref를 공유하는 같은 Account
  let _ ← peterAcc.withdraw 40
  IO.println (repr (← paulAcc.withdraw 0))
-- Except.ok 60  (Paul도 Peter의 출금을 그대로 봅니다)
```

Contrast this with `makeAccount 100` called twice: two separate `IO.mkRef` calls produce two genuinely distinct references, and no amount of substitution or renaming can make a withdrawal on one visible through the other. The difference between these two situations was never really about syntax — it's about how many `IO.Ref`s actually got allocated, which is exactly SICP's point that "sameness" here is a question about identity, not about the textual expression used to construct the object.

이를 `makeAccount 100`을 두 번 호출한 것과 대조해보세요 — 두 개의 서로 다른 `IO.mkRef` 호출이 진짜로 구별되는 두 참조를 만들어내고, 어떤 치환이나 이름 바꾸기로도 한쪽의 출금을 다른 쪽에서 보이게 만들 수 없습니다. 이 두 상황의 차이는 애초에 구문에 관한 것이 아니었습니다 — 실제로 몇 개의 `IO.Ref`가 할당됐는지에 관한 것이고, 이는 여기서 "같음"이 객체를 구성하는 데 쓰인 텍스트 표현이 아니라 정체성에 관한 질문이라는 SICP의 핵심과 정확히 일치합니다.

### 명령형 프로그래밍의 함정

Rewriting the iterative factorial from [1.2절](../1-2-procedures-and-processes/) to use explicit mutation instead of passing updated arguments introduces a subtle new way to get the wrong answer — the order of the two `set!`s matters, and nothing about the language stops you from writing them backwards:

[1.2절](../1-2-procedures-and-processes/)의 반복적 팩토리얼을, 갱신된 인자를 넘기는 대신 명시적 변이를 쓰도록 다시 쓰면 미묘하게 새로운 방식으로 틀린 답을 낼 수 있게 됩니다 — 두 `set!`의 순서가 중요하고, 언어의 어떤 것도 그것을 거꾸로 쓰는 걸 막아주지 않습니다.

```lean
partial def imperativeFactorial (n : Nat) : IO Nat := do
  let product ← IO.mkRef 1
  let counter ← IO.mkRef 1
  let rec iter : IO Nat := do
    if (← counter.get) > n then product.get
    else do
      product.set ((← counter.get) * (← product.get))
      counter.set ((← counter.get) + 1)
      iter
  iter

#eval imperativeFactorial 6
-- 720
```

Swap the two `.set` lines and you get a different, wrong answer, exactly as SICP warns — Lean's type checker has no opinion about statement order, because ordering side effects correctly is a semantic property `IO`'s type says nothing about. There's a second, structural price here too: `iter` recurses with no argument that shrinks at all — its only state lives in `counter` and `product`, invisible to the type — so this is `partial` for a stronger reason than [1.2절](../1-2-procedures-and-processes/)의 `factIter` was. `factIter` at least had an explicit `Nat` argument a `termination_by` measure could talk about; here, hiding the loop variables behind `IO.Ref` doesn't just cost referential transparency, it also throws away the termination checker's ability to see the loop at all.

두 `.set` 줄을 바꾸면 SICP가 경고하는 그대로 다르고 틀린 답이 나옵니다 — Lean의 타입 검사기는 문장 순서에 대해 아무 의견이 없습니다. 부수 효과의 순서를 올바르게 맞추는 것은 `IO`의 타입이 아무것도 말해주지 않는 의미론적 속성이기 때문입니다. 여기엔 구조적인 대가도 하나 더 있습니다 — `iter`는 전혀 줄어드는 인자 없이 재귀하는데, 그 유일한 상태는 `counter`와 `product` 안에 살고 있고 타입에는 보이지 않습니다. 그래서 이건 [1.2절](../1-2-procedures-and-processes/)의 `factIter`보다 더 강한 이유로 `partial`입니다. `factIter`는 적어도 `termination_by` 측정값이 이야기할 수 있는 명시적 `Nat` 인자가 있었습니다 — 여기서는 루프 변수를 `IO.Ref` 뒤에 숨기는 것이 참조 투명성뿐 아니라 종료성 검사기가 루프 자체를 볼 수 있는 능력까지 통째로 앗아갑니다.

---

## 정리

| SICP 개념 | Scheme | Lean 4 |
|---|---|---|
| 배정 | `set!` | `IO.Ref`의 `.get`/`.set`, 항상 `IO` 안에서 |
| 지역 상태 은닉 | `let` + `lambda`로 캡슐화 | `do` 블록에서 만든 `IO.Ref`를 클로저가 포획 |
| 메시지 패싱 객체 | 심볼로 분기하는 `dispatch` | 이름 붙은 함수 필드를 가진 `structure` |
| 참조 투명성 | 산문으로 경고("substitution이 더 이상 안 통한다") | 타입에 `IO`가 나타나는지로 판별 가능 |
| 별칭(aliasing) | 같은 객체를 가리키는 두 이름 | 같은 `IO.Ref`를 감싼 같은가 다른가 |
| 순서에 민감한 변이 | `set!` 순서를 잘못 쓰면 틀린 결과 | `IO` do 블록 순서를 잘못 쓰면 틀린 결과, 타입은 순서를 검사 안 함 |

이 절에서 SICP가 산문으로 힘들게 증명해야 했던 것 — 배정이 있는 절차와 없는 절차는 근본적으로 다른 종류라는 것 — 을 Lean은 대체로 타입 시그니처에 `IO`가 있는지 없는지로 미리 알려줍니다. 다만 공짜는 아닙니다 — 상태를 숨기면 참조 투명성과 함께 종료성 검사기의 시야도 잃습니다. 다음 글에서는 3.2절 — `set!`과 지역 변수를 실제로 설명해주는 환경 모델(environment model) — 을 다룹니다.
