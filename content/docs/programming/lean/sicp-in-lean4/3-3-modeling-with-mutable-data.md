---
title: "3.3. 가변 데이터로 모델링하기 (Modeling with Mutable Data)"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["sicp", "lean", "lean4", "scheme", "mutable-state", "ST", "IORef", "sharing"]
categories: ["programming"]
description: "SICP 3장 3절의 아이디어(set-car!/set-cdr!로 만드는 가변 리스트, 큐, 테이블)를 Lean 4의 IORef/ST와 순수 함수형 자료구조로 다시 짜 봅니다."
---

So far every data structure in this series has been something you build once and never touch again — a `List` doesn't get edited, it gets replaced by a new `List` that shares whatever parts didn't change. SICP's Chapter 3 introduces the opposite idea: objects with an *identity* that persists while their *contents* change underneath them, like a bank account whose balance today has nothing to do with the value it printed to at construction time.

지금까지 이 시리즈에 등장한 자료구조는 모두 한 번 만들면 다시 손대지 않는 것들이었습니다 — `List`는 수정되지 않고, 바뀌지 않은 부분을 공유하는 새 `List`로 대체될 뿐입니다. SICP 3장은 정반대의 개념을 도입합니다 — *내용물*이 그 아래에서 바뀌는 동안에도 유지되는 *정체성*을 가진 객체입니다. 마치 은행 계좌의 오늘 잔액이 계좌를 만들 때 찍혔던 값과 아무 상관이 없어지는 것처럼 말이죠.

Scheme reaches this by adding `set-car!` and `set-cdr!` — primitives that reach inside an existing pair and overwrite one of its slots, in place, so that every other piece of code holding a reference to that same pair sees the change. Lean's `List` has no such door: there is no `List.setCar!`, and there couldn't be one without breaking the guarantee that makes `List` safe to share freely in the first place. Where Scheme bolts mutation onto its one universal glue, Lean keeps data immutable and instead makes mutation a distinct, explicitly-typed effect — `IO.Ref` or `ST`— that a function's signature has to admit before it's allowed to use it.

Scheme는 `set-car!`와 `set-cdr!`를 추가해 이를 구현합니다 — 기존 쌍 내부에 직접 접근해 칸 하나를 제자리에서 덮어써서, 그 쌍에 대한 참조를 가진 다른 모든 코드가 변경을 보게 만드는 원시 연산입니다. Lean의 `List`에는 그런 문이 없습니다 — `List.setCar!` 같은 건 없고, 있을 수도 없습니다. 그런 게 있다면 `List`를 자유롭게 공유해도 안전하다는 보장 자체가 깨지기 때문입니다. Scheme이 하나의 보편적 접착제에 변경 기능을 덧붙이는 곳에서, Lean은 데이터를 불변으로 유지하고 대신 변경을 `IO.Ref`나 `ST`라는 별도의, 명시적으로 타입에 드러나는 효과로 만듭니다 — 함수 시그니처가 그 효과를 허락해야만 쓸 수 있습니다.

---

## 3.3.1. 가변 리스트 구조 대신 `IO.Ref`

The clearest way to see what `set-car!`/`set-cdr!` buy Scheme, and what Lean gives up on purpose, is to build the same "identity that persists while contents change" behavior with `IO.Ref` — a reference cell holding a value that can be swapped out without changing the cell's own identity:

`set-car!`/`set-cdr!`가 Scheme에 무엇을 가져다주는지, 그리고 Lean이 의도적으로 무엇을 포기하는지를 가장 분명히 보는 방법은, "내용물이 바뀌어도 유지되는 정체성"이라는 같은 동작을 `IO.Ref`로 직접 만들어보는 것입니다 — 참조 셀 자체의 정체성은 바뀌지 않은 채, 그 안에 담긴 값만 바꿔치기할 수 있는 셀입니다.

```lean
def demoRef : IO Unit := do
  let r ← IO.mkRef (1, 2)
  IO.println s!"before: {(← r.get)}"
  r.set (10, 2)
  IO.println s!"after: {(← r.get)}"

#eval demoRef
-- before: (1, 2)
-- after: (10, 2)
```

Two references bound to the same `IO.Ref` genuinely share state — writing through one is visible through the other, mirroring the way two Scheme variables bound to the same pair share whatever `set-car!` does to it. Two references built independently, even holding equal contents, are distinct cells, exactly the distinction SICP draws between `(cons x x)` and `(cons (list 'a 'b) (list 'a 'b))`:

같은 `IO.Ref`를 가리키는 두 참조는 실제로 상태를 공유합니다 — 한쪽으로 쓴 값이 다른 쪽에서도 보이며, 이는 같은 쌍에 묶인 두 Scheme 변수가 `set-car!`의 효과를 공유하는 것과 같습니다. 반면 내용이 같더라도 독립적으로 만든 참조 두 개는 서로 다른 셀입니다 — 이는 SICP가 `(cons x x)`와 `(cons (list 'a 'b) (list 'a 'b))`를 구분하는 것과 정확히 같은 구분입니다.

```lean
def sharingDemo : IO Unit := do
  let shared ← IO.mkRef 0
  let alias1 := shared
  let alias2 := shared
  alias1.set 99
  IO.println s!"alias2 sees: {(← alias2.get)}"

  let a ← IO.mkRef 0
  let b ← IO.mkRef 0
  a.set 99
  IO.println s!"b still: {(← b.get)}"

#eval sharingDemo
-- alias2 sees: 99
-- b still: 0
```

There's no `eq?` in Lean for comparing `IO.Ref` identity directly from user code — reference identity is deliberately not something ordinary Lean values expose, since exposing it would compromise the reasoning-by-substitution that makes pure Lean code easy to verify. In practice, if you need to ask "are these the same mutable cell," you design that question into your data model explicitly (e.g., by tagging each cell with a unique `Nat` at creation time) rather than relying on a language-level pointer check.

Lean에는 사용자 코드에서 `IO.Ref`의 정체성을 직접 비교하는 `eq?`가 없습니다 — 참조 정체성은 평범한 Lean 값이 노출하도록 의도된 것이 아닙니다. 그것을 노출하면 순수한 Lean 코드를 검증하기 쉽게 만들어주는 "치환에 의한 추론"이 무너지기 때문입니다. 실무에서 "이 둘이 같은 가변 셀인가"를 물어야 한다면, 언어 차원의 포인터 검사에 기대는 대신 생성 시점에 고유한 `Nat`을 태그로 붙이는 식으로 그 질문을 데이터 모델에 명시적으로 설계해 넣습니다.

**연습문제 3.16 (Lean 버전).** SICP는 "쌍이 세 개인 구조인데도 순진한 `count-pairs`가 3, 4, 7을 반환하거나 영영 멈추지 않는" 예시들을 손으로 그려보라고 합니다. Lean에서는 `List`가 공유·순환을 표현할 수 없는 트리 구조이므로 이 문제 자체가 원천 봉쇄됩니다 — `List α`나 위에서 정의한 `Tree α` 값은 항상 유한하고 순환이 없다는 것이 타입의 불변식이기 때문입니다. 순환이 있는 구조를 표현하려면 `IO.Ref`로 직접 셀을 엮어야 하며, 그 순간 "몇 개의 서로 다른 셀이 있는가"라는 질문은 더 이상 구조를 세는 문제가 아니라 어떤 셀들을 이미 방문했는지 추적하는 문제가 됩니다 — 아래처럼 방문한 셀의 고유 ID를 기록하며 순회해야 합니다.

```lean
structure Cell where
  id : Nat
  next : Option (IO.Ref Cell)

partial def countDistinct (visited : IO.Ref (List Nat)) : Option (IO.Ref Cell) → IO Nat
  | none => pure 0
  | some r => do
    let c ← r.get
    if (← visited.get).contains c.id then
      pure 0
    else
      visited.modify (c.id :: ·)
      let restCount ← countDistinct visited c.next
      pure (1 + restCount)
```

`countDistinct`에 `partial`이 붙은 이유를 짚어볼 만합니다 — 순환 구조를 순회하는 함수는 애초에 "인자가 항상 작아진다"는 구조적 재귀의 전제를 만족시킬 수 없습니다(다음 셀이 이전 셀과 같을 수 있으므로). 방문 목록으로 종료를 보장하는 것은 맞지만, 그 보장은 Lean의 termination checker가 자동으로 볼 수 있는 형태가 아니라 프로그래머가 책임지는 불변식입니다 — 그래서 `partial`로 이 재귀가 "믿고 맡기는" 재귀임을 명시합니다.

---

## 3.3.2. 큐를 표현하기

SICP builds an $\Theta(1)$-insertion queue out of a pair of pointers — one to the front of a chain of cells, one to the rear — and gets constant-time insertion by mutating the rear cell's `cdr` in place rather than walking the whole list to find the end. Lean's `List` can't do that trick without mutation, since appending to the end of an immutable singly-linked list is unavoidably $\Theta(n)$: there's no way to "reach" the last cons cell and rewrite it without first walking to it, and once you've walked to it there's nothing to overwrite.

SICP는 셀 사슬의 앞쪽을 가리키는 포인터와 뒤쪽을 가리키는 포인터, 이렇게 포인터 한 쌍으로 $\Theta(1)$ 삽입이 되는 큐를 만듭니다 — 리스트 끝을 찾아 전체를 훑는 대신 마지막 셀의 `cdr`을 제자리에서 바꿔서 상수 시간 삽입을 달성합니다. Lean의 `List`는 변경 없이는 이 트릭을 쓸 수 없습니다 — 불변 단일 연결 리스트의 끝에 원소를 추가하는 것은 어쩔 수 없이 $\Theta(n)$이기 때문입니다. 마지막 `cons` 셀에 "도달"해서 다시 쓸 방법이 없고, 설령 도달했다 해도 덮어쓸 수 있는 것이 없습니다.

Two honest ways to recover the SICP queue's asymptotics exist in Lean, and they represent the two poles of this whole section. The first keeps mutation, using `IO.Ref` exactly the way SICP uses `set-cdr!` — front and rear pointers into a chain of mutable cells, where inserting reaches the current rear cell and overwrites its `next` field in place, reusing the same `IO.Ref`-linked-cell shape as `Cell` from [Exercise 3.16](#) above:

Lean에서 SICP 큐의 점근 성능을 되살리는 정직한 방법은 두 가지이고, 이 둘이 이 절 전체의 두 극단을 보여줍니다. 첫 번째는 변경을 그대로 유지하는 방법으로, SICP가 `set-cdr!`를 쓰는 것과 똑같이 `IO.Ref`를 씁니다 — 가변 셀의 사슬을 가리키는 앞/뒤 포인터이고, 삽입은 현재 뒤쪽 셀에 도달해 그 `next` 필드를 제자리에서 덮어씁니다. 위 연습문제 3.16의 `Cell`과 같은 `IO.Ref`로 엮인 셀 모양을 재사용합니다.

```lean
structure QCell (α : Type) where
  val : α
  next : IO.Ref (Option (QCell α))

structure MutQueuePtr (α : Type) where
  front : IO.Ref (Option (QCell α))
  rear : IO.Ref (Option (QCell α))

def MutQueuePtr.new : IO (MutQueuePtr α) := do
  pure { front := ← IO.mkRef none, rear := ← IO.mkRef none }

def MutQueuePtr.insert (q : MutQueuePtr α) (item : α) : IO Unit := do
  let newCell : QCell α := { val := item, next := ← IO.mkRef none }
  match ← q.rear.get with
  | none =>
    q.front.set (some newCell)
    q.rear.set (some newCell)
  | some oldRear =>
    oldRear.next.set (some newCell)
    q.rear.set (some newCell)

def MutQueuePtr.frontItem (q : MutQueuePtr α) : IO (Option α) := do
  pure ((← q.front.get).map (·.val))

def MutQueuePtr.delete (q : MutQueuePtr α) : IO Unit := do
  match ← q.front.get with
  | none => pure ()
  | some c =>
    let next ← c.next.get
    q.front.set next
    if next.isNone then q.rear.set none

def queueDemoPtr : IO Unit := do
  let q ← MutQueuePtr.new (α := Char)
  q.insert 'a'
  q.insert 'b'
  IO.println s!"front: {← q.frontItem}"
  q.delete
  IO.println s!"front after delete: {← q.frontItem}"

#eval queueDemoPtr
-- front: some 'a'
-- front after delete: some 'b'
```

`insert`가 뒤쪽 셀의 `next`를 직접 덮어쓰므로 리스트를 훑거나 뒤집는 과정이 전혀 없습니다 — SICP의 포인터 변경 그대로, 매 삽입이 진짜 $\Theta(1)$입니다. (이 스니펫은 이 시리즈의 다른 `IO.Ref` 예제들과 같은 패턴을 따르지만, 별도로 컴파일해서 확인하지는 않았습니다.)

The second way gives up pointer identity for the front/rear cells and represents the whole queue as a plain, immutable pair of lists — no `IO.Ref` inside the queue itself at all:

두 번째 방법은 앞/뒤 셀의 포인터 정체성을 포기하고, 큐 전체를 평범하고 불변인 리스트 쌍으로 표현합니다 — 큐 자체 안에는 `IO.Ref`가 전혀 없습니다.

```lean
structure MutQueue (α : Type) where
  front : List α
  rear : List α

def MutQueue.empty : MutQueue α := ⟨[], []⟩

def MutQueue.isEmpty (q : MutQueue α) : Bool := q.front.isEmpty && q.rear.isEmpty

def MutQueue.insert (q : MutQueue α) (item : α) : MutQueue α :=
  { q with rear := item :: q.rear }

def MutQueue.frontItem (q : MutQueue α) : Option α :=
  match q.front with
  | x :: _ => some x
  | [] => q.rear.reverse.head?

def MutQueue.delete (q : MutQueue α) : MutQueue α :=
  match q.front with
  | _ :: xs => { q with front := xs }
  | [] => match q.rear.reverse with
    | [] => q
    | _ :: xs => { front := xs, rear := [] }

def queueDemo : IO Unit := do
  let ref ← IO.mkRef MutQueue.empty
  ref.modify (·.insert 'a')
  ref.modify (·.insert 'b')
  IO.println s!"front: {(← ref.get).frontItem}"
  ref.modify (·.delete)
  IO.println s!"front after delete: {(← ref.get).frontItem}"

#eval queueDemo
-- front: some 'a'
-- front after delete: some 'b'
```

This is the classic *two-list (Banker's) queue*: `insert` conses onto `rear` in $\Theta(1)$, and `delete` pops from `front` in $\Theta(1)$ — except on the rare occasion `front` runs dry, when it pays a one-time $\Theta(n)$ cost to reverse `rear` into the new `front`. That cost is real but *amortized* away over a long sequence of operations, which is the standard trick for getting SICP's pointer-mutation performance out of a purely immutable representation — no `IO.Ref` required at all, *if* you don't need the queue's identity to persist across calls the way `MutQueuePtr` does (which is exactly why `queueDemo` above still has to wrap it in one — the queue's own logic is pure, but sharing one growing queue across multiple call sites still needs a place to hold "the current queue," and that place is a reference).

이것이 바로 고전적인 *투 리스트(Banker's) 큐*입니다 — `insert`는 `rear`에 $\Theta(1)$로 붙이고, `delete`는 `front`에서 $\Theta(1)$로 꺼냅니다. 예외는 `front`가 바닥났을 때뿐인데, 이때는 `rear`를 뒤집어 새 `front`로 만드는 데 한 번 $\Theta(n)$ 비용을 치릅니다. 이 비용은 실재하지만 긴 연산 시퀀스에 걸쳐 *상각(amortize)*됩니다 — 이것이 순수 불변 표현으로도 SICP의 포인터 변경 수준의 성능을 얻는 표준적인 트릭입니다. `MutQueuePtr`처럼 큐의 정체성이 호출 사이에 유지될 필요가 없다*면* `IO.Ref`는 큐 내부에는 아예 필요 없습니다(그런데도 위 `queueDemo`가 여전히 `IO.Ref`로 감싸는 이유는, 큐 자신의 로직은 순수하더라도 여러 호출 지점에 걸쳐 하나의 자라나는 큐를 공유하려면 "지금의 큐"를 담아둘 자리가 필요하고, 그 자리가 곧 참조이기 때문입니다).

The `insert`/`delete` functions above never recurse, so there's no termination question there; the one place recursion shows up is `List.reverse` inside `frontItem`/`delete`, which is ordinary structural recursion over a strictly shrinking list — no `partial`, no `termination_by`.

위의 `insert`/`delete` 함수는 아예 재귀하지 않으므로 종료성 질문이 나올 자리가 없습니다. 재귀가 등장하는 유일한 곳은 `frontItem`/`delete` 안의 `List.reverse`인데, 이는 항상 줄어드는 리스트에 대한 평범한 구조적 재귀입니다 — `partial`도 `termination_by`도 필요 없습니다.

---

## 3.3.3. 테이블을 표현하기와 메모이제이션

SICP builds a table as a headed, mutable association list, so that `insert!` can splice a new record onto the front in $\Theta(1)$ without the caller ever needing a new pointer to "the table" — the header cell's identity is the table's identity. Lean's ecosystem already has the tool this section is building by hand: `Std.HashMap` (mutable-feeling but implemented as a persistent structure under the hood) gives $\Theta(1)$-amortized lookup and insert without any hand-rolled backbone-and-header trick.

SICP는 헤더가 달린 가변 연관 리스트로 테이블을 만듭니다. 그래야 `insert!`가 새 레코드를 $\Theta(1)$로 앞에 이어붙이면서도, 호출자가 "그 테이블"을 가리키는 새 포인터를 받을 필요가 없습니다 — 헤더 셀의 정체성이 곧 테이블의 정체성입니다. Lean 생태계에는 이 절이 손으로 만들고 있는 도구가 이미 있습니다 — `Std.HashMap`은 (겉보기엔 가변적이지만 내부적으로는 영속 구조로 구현된) $\Theta(1)$ 상각 조회·삽입을, 손으로 만든 백본-헤더 트릭 없이 제공합니다.

```lean
def buildTable : Std.HashMap String Nat :=
  (∅ : Std.HashMap String Nat) |>.insert "a" 1 |>.insert "b" 2 |>.insert "c" 3

#eval buildTable.get? "b"
-- some 2

#eval buildTable.get? "z"
-- none
```

The most compelling motivation SICP gives for tables is memoization — caching a function's previously-computed results keyed on its arguments, most vividly with naive exponential Fibonacci. In Lean, an honest memoized function needs `IO.Ref` (or `StateM`), because updating a cache *is* mutation — a `Nat → Nat` function that secretly remembers what it was called with before is a function with hidden side effects, and Lean's type system is built specifically to make that visibility non-optional:

SICP가 테이블에 제시하는 가장 설득력 있는 동기는 메모이제이션입니다 — 인자를 키로 삼아 함수가 이전에 계산한 결과를 캐싱하는 것으로, 순진한 지수 시간 피보나치가 가장 극적인 예입니다. Lean에서 정직한 메모이즈드 함수는 `IO.Ref`(또는 `StateM`)가 필요합니다 — 캐시를 갱신하는 것 자체가 변경이기 때문입니다. 이전에 어떤 인자로 호출됐는지 몰래 기억하는 `Nat → Nat` 함수는 사실 숨겨진 부작용을 가진 함수이고, Lean의 타입 시스템은 바로 그 숨김을 선택 사항이 아니게 만들도록 설계되어 있습니다.

```lean
def mkMemoFib : IO (Nat → IO Nat) := do
  let cache ← IO.mkRef (∅ : Std.HashMap Nat Nat)
  let rec fib (n : Nat) : IO Nat := do
    match (← cache.get).get? n with
    | some v => pure v
    | none => do
      let result ← if n = 0 then pure 0
                   else if n = 1 then pure 1
                   else do
                     let a ← fib (n - 1)
                     let b ← fib (n - 2)
                     pure (a + b)
      cache.modify (·.insert n result)
      pure result
  pure fib

def memoFibDemo : IO Unit := do
  let fib ← mkMemoFib
  IO.println (← fib 30)

#eval memoFibDemo
-- 832040
```

The inner `fib` recurses structurally on `n` and would pass Lean's termination checker as a plain function — the reason it's written inside `do`-notation and threaded through `IO` at all isn't termination, it's that reading and writing `cache` are effects that have to show up in the type of every call. Compare this to the pure, non-memoized `fib` from the very first post in this series: same recursive shape, same termination argument, but no `IO` anywhere in its signature, because it never needed to remember anything between calls.

내부 `fib`은 `n`에 대해 구조적으로 재귀하며, 평범한 함수로 써도 Lean의 종료성 검사기를 그대로 통과했을 것입니다 — 이 함수가 `do` 표기법 안에서 `IO`를 통해 쓰이는 이유는 종료성 때문이 아니라, `cache`를 읽고 쓰는 것이 모든 호출의 타입에 드러나야 하는 효과이기 때문입니다. 이 시리즈 첫 글의 순수하고 메모이제이션 없는 `fib`과 비교해보세요 — 재귀 형태도, 종료성 논증도 같지만 시그니처 어디에도 `IO`가 없습니다. 호출 사이에 아무것도 기억할 필요가 없었기 때문입니다.

**연습문제 3.27 (Lean 버전).** SICP는 `(memoize fib)`처럼 이미 정의된 순수 재귀 `fib`을 감싸는 것과, `memo-fib`이 자기 자신을 재귀 호출하도록 처음부터 다시 쓰는 것의 차이를 물어봅니다. Lean에서 이 차이는 타입에 그대로 드러납니다 — 위 `mkMemoFib`의 내부 `fib`은 재귀 호출 `fib (n - 1)`이 *같은* 캐시를 참조하는 `IO`액션이기 때문에 $\Theta(n)$입니다. 만약 순수 `def fib : Nat → Nat`(이 시리즈 1.2절의 그 함수)을 밖에서 감싸는 `memoize`를 만든다면, 캐시는 최상위 호출 하나만 기억할 뿐 그 함수가 자기 자신을 호출할 때 만드는 재귀 호출들은 여전히 캐시를 모르는 순수 `fib`을 타므로, 여전히 지수 시간이 됩니다 — 메모이제이션의 효과를 보려면 재귀 구조 자체가 캐시를 아는 버전을 참조해야 한다는 것이 핵심입니다.

---

Section 3.3.4 goes on to build a full event-driven digital-circuit simulator out of wires and delayed actions — a genuinely large, self-contained system that deserves its own post rather than a rushed coda here. The throughline to carry forward is the one this post has been building: SICP's `set-car!`/`set-cdr!` do double duty as both "identity that persists" and "the actual mutation," while Lean insists on splitting those two concerns — identity via `IO.Ref`, persistence via the type system tracking exactly where mutation is and isn't allowed to happen.

3.3.4절은 와이어와 지연된 액션으로 완전한 이벤트 기반 디지털 회로 시뮬레이터를 만드는데, 이는 정말로 큰 독립적인 시스템이라 여기서 급하게 요약하기보다 별도의 글로 다룰 가치가 있습니다. 이번 글에서 계속 이어온 핵심은 이것입니다 — SICP의 `set-car!`/`set-cdr!`는 "유지되는 정체성"과 "실제 변경"이라는 두 역할을 동시에 하지만, Lean은 이 둘을 갈라놓습니다 — 정체성은 `IO.Ref`가, 그리고 변경이 허용되는 곳과 허용되지 않는 곳을 정확히 추적하는 일은 타입 시스템이 맡습니다.
