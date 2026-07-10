---
title: "3.2. 평가의 환경 모델 (The Environment Model of Evaluation)"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["sicp", "lean", "lean4", "scheme", "closures", "mutable-state", "evaluation-model"]
categories: ["programming"]
description: "SICP 3장 2절의 아이디어(환경, 프레임, 클로저, 지역 상태, 내부 정의)를 Lean 4의 클로저 표현과 IO.Ref 기반 가변 상태로 다시 짜 봅니다."
---

The substitution model that carried this series through chapter 1 quietly assumed something that stops being true the moment a language admits assignment: that a variable is just a stand-in for the value it happens to equal right now, so you can always replace the name with the value and get an equivalent expression. Once a procedure can mutate a variable it closed over, "the value of `x`" depends on *when* you ask, which means a model of evaluation needs some notion of a place a value lives, not merely the value itself. SICP's answer is the environment model — chains of frames, each a table of bindings, each pointing to an enclosing frame — and this post asks what that model looks like once we're working in a language, Lean, that has closures and references but keeps mutation walled off behind an explicit `IO` or `ST` effect rather than letting it leak into ordinary values.

1장을 관통했던 치환 모델은 조용히 한 가지를 전제하고 있었습니다 — 변수란 그저 지금 우연히 같은 값의 자리표시자일 뿐이라서, 이름을 값으로 바꿔써도 언제나 동등한 표현식을 얻는다는 전제입니다. 이 전제는 언어가 대입(assignment)을 허용하는 순간 더 이상 성립하지 않습니다. 절차가 자신이 포획한 변수를 변경할 수 있게 되면, "`x`의 값"은 *언제* 묻느냐에 따라 달라지고, 그래서 평가 모델에는 값 자체가 아니라 값이 사는 "자리"라는 개념이 필요해집니다. SICP의 답은 환경 모델입니다 — 각각이 바인딩의 표(table)이고 각각이 감싸는 프레임을 가리키는 프레임들의 사슬입니다. 이 글은 그 모델이, 클로저와 참조를 갖고 있으면서도 변경(mutation)을 `IO`나 `ST`라는 명시적 효과 뒤에 가둬두고 보통의 값으로는 새어나가지 못하게 하는 언어인 Lean에서는 어떤 모습일지를 묻습니다.

Every frame in SICP's picture is really two things bolted together: a table of variable-to-value bindings, and a pointer to whatever frame encloses it, with lookup walking outward frame by frame until a binding turns up or the chain runs out. That second part — the enclosing pointer — is exactly what makes a closure a closure rather than just a function pointer: it's the reason two calls to the same `lambda` can each remember a *different* surrounding frame. Lean's own notion of a closure is built the same way underneath the surface, even though the language never shows you a frame object directly; when an anonymous function mentions a variable from its surrounding scope, Lean's elaborator bakes a reference to that variable's value into the function it produces, and calling that function twice from two different enclosing lets produces two independent closures over two independent captured values.

SICP의 그림에서 모든 프레임은 사실 두 가지가 이어붙은 것입니다 — 변수-값 바인딩의 표, 그리고 자신을 감싸는 프레임을 가리키는 포인터. 조회는 바인딩이 나오거나 사슬이 끝날 때까지 바깥쪽으로 프레임을 하나씩 걸어갑니다. 그 두 번째 부분 — 감싸는 프레임 포인터 — 이야말로 클로저를 단순한 함수 포인터가 아니라 클로저로 만들어주는 것입니다. 같은 `lambda`에 대한 두 번의 호출이 각기 *다른* 주변 프레임을 기억할 수 있는 이유가 바로 이것입니다. Lean 자신의 클로저 개념도 표면 아래에서는 같은 방식으로 만들어지는데, 언어가 프레임 객체를 직접 보여주진 않지만, 익명 함수가 주변 스코프의 변수를 언급하면 Lean의 엘라보레이터는 그 변수의 값에 대한 참조를 만들어지는 함수 안에 구워 넣고, 서로 다른 두 개의 감싸는 let에서 그 함수를 각각 두 번 호출하면 서로 독립된 두 개의 포획된 값에 대한 독립적인 두 클로저가 만들어집니다.

```lean
def makeAdder (base : Int) : Int → Int :=
  fun amount => base + amount

def addFive := makeAdder 5
def addTen := makeAdder 10

#eval addFive 3
-- 8

#eval addTen 3
-- 13
```

`addFive` and `addTen` are two distinct closures produced by two separate calls to `makeAdder`, each carrying its own captured `base` — this is precisely SICP's picture of `W1` and `W2` in [Figure 3.10 of the source text], two procedure objects sharing one piece of code but pointing to two different frames. The difference worth sitting with is that `base` here is immutable: once `makeAdder 5` closes over `base = 5`, nothing in ordinary Lean code can ever change what that closure sees, which is exactly why this example alone doesn't yet need anything like an environment *model* — a plain substitution argument (replace `base` with `5` everywhere in the closure's body) already explains `addFive`'s behavior completely.

`addFive`와 `addTen`은 `makeAdder`에 대한 두 번의 별개 호출로 만들어진 서로 다른 두 클로저이고, 각자 자신만의 포획된 `base`를 갖습니다 — 이는 정확히 SICP가 그리는 `W1`과 `W2`의 그림입니다. 하나의 코드를 공유하면서도 서로 다른 프레임을 가리키는 두 개의 절차 객체입니다. 여기서 눈여겨볼 차이는 이 `base`가 불변(immutable)이라는 점입니다 — `makeAdder 5`가 `base = 5`를 포획하고 나면, 평범한 Lean 코드의 그 무엇도 그 클로저가 보는 것을 절대 바꿀 수 없습니다. 그래서 이 예제만으로는 아직 환경 *모델* 같은 것이 전혀 필요하지 않습니다 — 평범한 치환 논증(클로저 본문 전체에서 `base`를 `5`로 바꿔치기)만으로도 `addFive`의 동작을 완전히 설명할 수 있습니다.

---

## 3.2.1. 가변 상태가 있을 때 평가는 어떻게 달라지는가

The moment we want a `make-withdraw`-style object — something that remembers a balance across calls and lets each call change it — Lean's type system insists we say so out loud, because ordinary Lean values have no mutation at all; the tool for a mutable "place" is `IO.Ref α`, a reference cell that lives in the `IO` monad, and a closure over one behaves exactly like SICP's frame containing a mutable binding for `balance`.

`make-withdraw` 스타일의 객체 — 호출들 사이에서 잔액을 기억하고, 각 호출이 그것을 바꿀 수 있게 하는 것 — 을 원하는 순간, Lean의 타입 시스템은 그것을 소리 내어 말하라고 요구합니다. 보통의 Lean 값에는 변경이라는 게 전혀 없기 때문입니다. 가변적인 "자리"를 위한 도구는 `IO.Ref α`인데, `IO` 모나드 안에 사는 참조 셀이고, 그것을 포획한 클로저는 `balance`에 대한 가변 바인딩을 담은 SICP의 프레임과 정확히 똑같이 행동합니다.

```lean
def makeWithdraw (balance : IO.Ref Int) (amount : Int) : IO (Int ⊕ String) := do
  let current ← balance.get
  if current >= amount then
    balance.set (current - amount)
    return .inl (current - amount)
  else
    return .inr "Insufficient funds"

def demo : IO Unit := do
  let w1State ← IO.mkRef 100
  let w2State ← IO.mkRef 100
  let r1 ← makeWithdraw w1State 50
  let r2 ← makeWithdraw w2State 70
  IO.println s!"W1: {r1.getLeft?}, W2: {r2.getLeft?}"

#eval demo
-- W1: some 50, W2: some 30
```

`w1State` and `w2State` are two separate `IO.Ref` cells, playing the role of the two frames E1 and E2 in SICP's diagrams: each closure — really, each partially-applied `makeWithdraw balance` — closes over its own reference, and reading or writing through one never touches the other. The crucial thing the type signature makes visible is that `makeWithdraw` cannot be called except inside `IO` (or something that embeds it): Lean's effect system is, in a sense, a way of making SICP's warning explicit in the types — "an expression's meaning depends on the environment it's evaluated in" becomes, here, "this function's *result* depends on when you run it," and the type `IO (Int ⊕ String)` rather than plain `Int ⊕ String` is the permanent, unavoidable reminder of that fact.

`w1State`와 `w2State`는 서로 다른 두 개의 `IO.Ref` 셀이고, SICP 그림의 두 프레임 E1, E2 역할을 합니다 — 각 클로저(정확히는 부분 적용된 `makeWithdraw balance` 각각)는 자신만의 참조를 포획하고, 하나를 읽거나 쓰는 것이 다른 하나를 절대 건드리지 않습니다. 타입 시그니처가 드러내는 결정적인 것은 `makeWithdraw`가 `IO`(또는 그것을 품은 무언가) 안에서가 아니면 호출될 수 없다는 점입니다 — Lean의 효과 시스템은 어떤 의미에서 SICP의 경고를 타입 안에 명시적으로 새겨넣는 방법입니다. "표현식의 의미는 그것이 평가되는 환경에 달려 있다"는 말이, 여기서는 "이 함수의 *결과*는 당신이 언제 실행하느냐에 달려 있다"가 되고, 평범한 `Int ⊕ String` 대신 `IO (Int ⊕ String)`이라는 타입 자체가 그 사실에 대한 영구적이고 피할 수 없는 상기물입니다.

Contrast this with a closure that captures no reference at all, only an ordinary immutable value — `addFive` from the previous section is such a closure, and it needs no `IO`, because there's no hidden frame anywhere whose contents could ever be mutated later. Reading Lean's type signatures this way turns SICP's environment-diagram exercise into something the compiler settles for you: if a function's type mentions no `IO`, `ST`, or `IO.Ref`, there is no frame in its closure that anyone, anywhere, could ever call `set!` on.

이것을 참조를 전혀 포획하지 않고 오직 평범한 불변 값만 포획하는 클로저와 대조해보세요 — 앞 절의 `addFive`가 그런 클로저이고, `IO`가 전혀 필요 없습니다. 나중에 변경될 수 있는 내용물을 가진 숨은 프레임이 어디에도 없기 때문입니다. Lean의 타입 시그니처를 이런 식으로 읽으면 SICP의 환경 다이어그램 연습이 컴파일러가 대신 해결해주는 것이 됩니다 — 함수의 타입에 `IO`, `ST`, `IO.Ref`가 전혀 언급되지 않는다면, 그 클로저 안에는 그 누구도 어디서도 `set!`을 호출할 수 있는 프레임이 없다는 뜻입니다.

**연습문제 3.10 (Lean 버전):** 원문은 `make-withdraw`를 매개변수로 직접 상태를 받는 버전과, `let`으로 지역 변수를 만드는 버전으로 나눠 비교해 보라고 합니다. 아래는 `let`으로 참조를 만드는 버전입니다 — 두 버전이 만들어내는 클로저 구조가 왜 동일한지, `IO.Ref`가 함수 인자로 오든 `let` 바인딩으로 오든 "포획되는 자리"라는 본질이 달라지지 않는 이유를 생각해 보세요.

```lean
def makeWithdrawLet (initialAmount : Int) : IO (Int → IO (Int ⊕ String)) := do
  let balance ← IO.mkRef initialAmount
  return fun amount => do
    let current ← balance.get
    if current >= amount then
      balance.set (current - amount); return .inl (current - amount)
    else
      return .inr "Insufficient funds"

def demo2 : IO Unit := do
  let w1 ← makeWithdrawLet 100
  let r ← w1 50
  IO.println s!"{r.getLeft?}"

#eval demo2
-- some 50
```

Both versions produce a function value that closes over a *fresh* `IO.Ref` created for that particular call — in `makeWithdraw`, the caller creates the ref and passes it in explicitly; in `makeWithdrawLet`, `makeWithdrawLet` itself creates the ref internally and the caller never sees it. The environment-model point SICP wants made is that these are the same frame either way, just built by different code; Lean's version of that point is that both `balance : IO.Ref Int` bindings denote the exact same kind of "place," regardless of whether the syntax that introduced it was a function parameter or a `let`.

두 버전 모두 그 특정 호출을 위해 만들어진 *새로운* `IO.Ref`를 포획하는 함수 값을 만들어냅니다 — `makeWithdraw`에서는 호출자가 참조를 만들어 명시적으로 넘겨주고, `makeWithdrawLet`에서는 `makeWithdrawLet` 자신이 내부에서 참조를 만들어서 호출자는 그것을 전혀 보지 못합니다. SICP가 짚고 싶어하는 환경 모델의 요점은 이 둘이 어느 쪽이든 같은 프레임이고, 다만 다른 코드로 만들어졌을 뿐이라는 것입니다. Lean 버전의 요점은, 그것을 도입한 구문이 함수 매개변수였든 `let`이었든, 두 `balance : IO.Ref Int` 바인딩이 정확히 같은 종류의 "자리"를 가리킨다는 것입니다.

---

## 3.2.2. 지역 정의는 프레임을 어떻게 나누는가

SICP's other big claim about environments — that internal definitions inside a procedure body get their own frame, subordinate to the frame of the enclosing call, which is why two internally-defined procedures can share a parameter's free variable without colliding with anything at the top level — has a direct Lean analogue in `where` clauses and `let`-bound local functions. A Lean function's `where` block is scoped exactly the way SICP's `good-enough?`, `improve`, and `sqrt-iter` are scoped inside `sqrt`: visible to each other and to the enclosing function's parameters, invisible outside it.

환경에 대한 SICP의 또 다른 큰 주장 — 절차 본문 안의 내부 정의들은 그 호출을 감싸는 프레임에 종속된 자기만의 프레임을 얻고, 그래서 내부에서 정의된 두 절차가 매개변수의 자유 변수를 공유하면서도 최상위의 그 무엇과도 충돌하지 않을 수 있다는 것 — 은 Lean의 `where` 절과 `let`으로 묶인 지역 함수에 직접 대응합니다. Lean 함수의 `where` 블록은 정확히 SICP의 `good-enough?`, `improve`, `sqrt-iter`가 `sqrt` 안에서 스코프되는 방식으로 스코프됩니다 — 서로에게, 그리고 감싸는 함수의 매개변수에게는 보이지만 바깥에서는 보이지 않습니다.

```lean
partial def mySqrt (x : Float) : Float :=
  sqrtIter 1.0
where
  goodEnough (guess : Float) : Bool :=
    Float.abs (guess * guess - x) < 0.001
  improve (guess : Float) : Float :=
    (guess + x / guess) / 2.0
  sqrtIter (guess : Float) : Float :=
    if goodEnough guess then guess else sqrtIter (improve guess)

#eval mySqrt 2.0
-- 1.414214
```

`x`, the parameter of `mySqrt`, is a free variable inside `goodEnough`'s body exactly as SICP describes it: `goodEnough` doesn't take `x` as its own parameter, yet its body refers to it and finds it in the enclosing scope, the same way E3 in SICP's diagram has E1 — the frame binding `x` to 2 — as its enclosing environment. And because `sqrtIter` calls itself with a value produced by `improve`, not with a structurally smaller argument of any type Lean can see through, the whole definition needs `partial`; this is the same `Float`-valued iterative-improvement shape as `sqrtIter` from the very first post in this series, and the same reasoning about "no structurally decreasing measure" applies here as it did there.

`mySqrt`의 매개변수 `x`는 SICP가 기술하는 것과 정확히 같은 방식으로 `goodEnough`의 본문 안에서 자유 변수입니다 — `goodEnough`는 `x`를 자기 매개변수로 받지 않지만 본문이 그것을 참조하고 감싸는 스코프에서 찾아냅니다. 이는 SICP 다이어그램에서 E3가 `x`를 2에 묶는 프레임인 E1을 감싸는 환경으로 갖는 것과 같습니다. 그리고 `sqrtIter`가 `improve`가 만들어낸 값으로 자기 자신을 호출하고, Lean이 꿰뚫어볼 수 있는 어떤 타입의 구조적으로 더 작은 인자로 호출하는 게 아니므로, 정의 전체가 `partial`을 필요로 합니다 — 이는 이 시리즈의 첫 글에 나왔던 `sqrtIter`와 똑같은, `Float` 값에 대한 반복적 개선(iterative improvement) 모양이고, "구조적으로 감소하는 척도가 없다"는 것에 대한 같은 논증이 여기에도 그대로 적용됩니다.

Two calls to `mySqrt` with different `x` produce two entirely independent runs of `sqrtIter`, each closing over its own `x`, in the same sense that two calls to `sqrt` in SICP produce two independent E1 frames — but there's a further Lean-specific fact worth noticing: nothing here is stateful. `where`-bound helpers close over immutable parameters, so unlike the withdrawal example, this whole picture never needs `IO` at all; the "frame" SICP draws for `sqrt`'s local definitions is fully present in Lean's scoping rules, but since nothing in it is ever mutated, it collapses back into something a plain substitution argument could describe, with `where` supplying the modularity SICP is really after — hiding `goodEnough`, `improve`, and `sqrtIter` from every scope outside `mySqrt` — without needing any of the mutable-reference machinery from the previous section.

서로 다른 `x`로 `mySqrt`를 두 번 호출하면 각자 자신만의 `x`를 포획한 완전히 독립적인 두 번의 `sqrtIter` 실행이 만들어집니다. SICP에서 `sqrt`를 두 번 호출하면 독립적인 두 개의 E1 프레임이 만들어지는 것과 같은 의미입니다 — 하지만 여기엔 눈여겨볼 만한 Lean 고유의 사실이 하나 더 있습니다. 여기엔 아무런 상태(state)도 없다는 것입니다. `where`로 묶인 헬퍼들은 불변 매개변수를 포획하므로, 인출 예제와 달리 이 그림 전체는 `IO`를 전혀 필요로 하지 않습니다 — SICP가 `sqrt`의 지역 정의를 위해 그리는 "프레임"은 Lean의 스코프 규칙에 온전히 존재하지만, 그 안의 그 무엇도 절대 변경되지 않으므로 평범한 치환 논증으로 기술할 수 있는 것으로 다시 접혀 들어갑니다. `where`는 SICP가 진짜로 원하는 모듈성 — `goodEnough`, `improve`, `sqrtIter`를 `mySqrt` 바깥의 모든 스코프로부터 숨기는 것 — 을 앞 절의 가변 참조 장치 없이도 제공해줍니다.

**연습문제 3.11 (Lean 버전):** SICP의 메시지 패싱 계좌 객체를 Lean으로 옮겨 봅시다. `dispatch` 역할은 `IO.Ref`를 포획하는 두 개의 클로저(`withdraw`, `deposit`)를 담은 구조체나 함수로 표현할 수 있습니다. 아래 스켈레톤을 채워서 `acc`와 `acc2`가 서로 다른 `IO.Ref`를 포획해 독립된 잔액을 유지하는지 `#eval`로 확인해 보세요 — SICP가 그림으로 보여주는 "E1과 E2는 분리되어 있지만 코드는 공유한다"는 사실이, 여기서는 두 번의 `makeAccount` 호출이 각각 새 `IO.Ref`를 할당한다는 사실로 나타납니다.

```lean
structure Account where
  withdraw : Int → IO (Int ⊕ String)
  deposit : Int → IO Int

def makeAccount (initialBalance : Int) : IO Account := do
  let balance ← IO.mkRef initialBalance
  pure {
    withdraw := fun amount => do
      let current ← balance.get
      if current >= amount then
        balance.set (current - amount); pure (.inl (current - amount))
      else
        pure (.inr "Insufficient funds")
    deposit := fun amount => do
      let current ← balance.get
      balance.set (current + amount)
      pure (current + amount)
  }

def demo3 : IO Unit := do
  let acc ← makeAccount 50
  let d ← acc.deposit 40
  let w ← acc.withdraw 60
  IO.println s!"acc: deposit={d}, withdraw={w.getLeft?}"
  let acc2 ← makeAccount 100
  IO.println s!"acc2 unaffected: {← (do let r ← acc2.withdraw 0; pure r.getLeft?)}"

#eval demo3
-- acc: deposit=90, withdraw=some 30
-- acc2 unaffected: some 100
```

---

Bringing the two threads together: SICP needs the environment model at all because a variable's meaning can now depend on the moment it's read, and every subsequent idea in the section — frames, enclosing pointers, shared code with separate state — is really just the bookkeeping needed to make that moment well defined. Lean doesn't dispense with any of that bookkeeping, but it does relocate the crucial question — "could this expression's value depend on when it's evaluated?" — from something you have to trace through a diagram by hand to something the type signature already answers before you've read a line of the body: `IO` somewhere in the type means yes, its absence means no, and the closures in either case behave exactly as SICP's environment model predicts.

두 갈래를 하나로 모으자면, SICP가 환경 모델을 필요로 하는 이유는 애당초 변수의 의미가 그것을 읽는 순간에 따라 달라질 수 있기 때문이고, 이 절의 이후 아이디어들 — 프레임, 감싸는 포인터, 코드는 공유하되 상태는 분리되는 것 — 은 사실 그 순간을 잘 정의된 것으로 만들기 위한 부기(bookkeeping)일 뿐입니다. Lean이 그 부기를 없애주지는 않지만, 결정적인 질문 — "이 표현식의 값이 평가되는 시점에 따라 달라질 수 있는가?" — 을 다이어그램을 손으로 추적해야 답할 수 있는 것에서, 본문의 한 줄을 읽기도 전에 타입 시그니처가 이미 답해주는 것으로 옮겨놓습니다. 타입 어딘가에 `IO`가 있으면 "그렇다"이고, 없으면 "아니다"이며, 어느 경우든 클로저는 SICP의 환경 모델이 예측하는 그대로 동작합니다.
