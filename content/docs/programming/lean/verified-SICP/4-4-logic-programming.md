---
title: "4.4. 논리 프로그래밍 (Logic Programming)"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["sicp", "lean", "lean4", "scheme", "unification", "logic-programming", "inductive-relations", "termination"]
categories: ["programming"]
description: "SICP 4장 4절의 아이디어(패턴 매칭, 단일화, 규칙 기반 질의)를 Lean 4의 귀납적 관계와 손으로 짠 단일화기로 다시 짜 봅니다."
---

Every evaluator this series has built so far computes a single answer from a single input — even the nondeterministic `amb` evaluator from the last post ultimately asks "does this branch succeed or fail," one branch at a time. This section asks a different question entirely: instead of "what is the output of this relation," it asks "which assignments to these variables make this relation hold at all," and lets any of the relation's positions be the unknown. `append` stops being a function you call with two known lists and becomes a fact you can query in any direction — forwards, backwards, or asking for every decomposition at once.

지금까지 이 시리즈가 만든 모든 평가기는 하나의 입력에서 하나의 답을 계산했습니다 — 지난 글의 비결정적 `amb` 평가기조차 결국은 "이 가지가 성공하는가 실패하는가"를 한 번에 하나씩 물었을 뿐입니다. 이번 절은 완전히 다른 질문을 던집니다 — "이 관계의 출력이 무엇인가"가 아니라 "이 변수들에 어떤 값을 대입해야 이 관계가 성립하는가"를 묻고, 관계의 어느 자리든 미지수가 될 수 있게 합니다. `append`는 더 이상 두 개의 알려진 리스트로 호출하는 함수가 아니라, 어느 방향으로든 — 정방향, 역방향, 혹은 모든 분해를 한꺼번에 — 질의할 수 있는 사실이 됩니다.

The engine that makes this possible is *unification*: a generalization of pattern matching where both sides of the comparison, not just one, are allowed to contain unknowns. Lean actually runs a unification algorithm constantly, under the hood, every time it elaborates a term with metavariables — that's precisely how `#eval f _ 3` figures out what `_` has to be. This post builds a small, explicit version of that engine by hand, to see the mechanism SICP is describing rather than relying on Lean's built-in one, and asks the same termination question this series always asks: when does a unifier provably finish, and when does it need to be trusted rather than checked?

이를 가능케 하는 엔진이 *단일화(unification)*입니다 — 비교되는 양쪽 중 한쪽뿐 아니라 양쪽 모두에 미지수가 있을 수 있는, 패턴 매칭의 일반화입니다. 사실 Lean은 메타변수가 있는 항을 정교화(elaborate)할 때마다 내부적으로 끊임없이 단일화 알고리즘을 돌립니다 — `#eval f _ 3`에서 `_`가 무엇이어야 하는지 알아내는 방식이 정확히 이것입니다. 이번 글에서는 Lean에 내장된 것에 기대는 대신, SICP가 설명하는 그 메커니즘을 직접 보기 위해 작고 명시적인 버전의 엔진을 손으로 만들어보고, 이 시리즈가 항상 던지는 종료성 질문을 똑같이 던집니다 — 단일화기가 언제 증명 가능하게 끝나고, 언제 신뢰에 맡겨야(`partial`) 하는가.

---

## 4.4.1. 연역적 정보 검색을 `List` 모나드로

Before building a real unifier, it's worth noticing that plain pattern matching against a *fixed* database — no rules, no recursion — is nothing new: it's exactly the finite, all-answers-at-once `List`-monad reading from the [previous post](../4-3-nondeterministic-computing/). A personnel record is just a tuple, a query pattern is a partial tuple with holes, and "find all matches" is a `filterMap` over the database:

진짜 단일화기를 만들기 전에, 규칙도 재귀도 없는 *고정된* 데이터베이스에 대한 순수한 패턴 매칭은 새로운 것이 아니라는 점을 짚어볼 만합니다 — [이전 글](../4-3-nondeterministic-computing/)의 유한하고 "모든 답을 한번에" 읽는 `List` 모나드 그대로입니다. 인사 기록은 그저 튜플이고, 질의 패턴은 구멍이 뚫린 부분 튜플이며, "모든 일치 찾기"는 데이터베이스에 대한 `filterMap`입니다.

```lean
structure Job where
  person : String
  title : List String

def jobs : List Job :=
  [ ⟨"Alyssa", ["computer", "programmer"]⟩
  , ⟨"CyD", ["computer", "programmer"]⟩
  , ⟨"LemE", ["computer", "technician"]⟩ ]

def findByTitlePrefix (prefix : String) : List Job :=
  jobs.filter (fun j => j.title.head? = some prefix)

#eval findByTitlePrefix "computer" |>.map (·.person)
-- ["Alyssa", "CyD", "LemE"]
```

This is fine as far as it goes, but it only handles patterns whose *shape* is nailed down in advance by the `Job` structure's fields — there's no way to ask "find `x` and `y` such that `x ++ y = [a, b, c, d]`" this way, because `filter` can only check a fixed predicate, it can't discover *which* variable positions in a pattern correspond to which parts of the data. That discovery process is exactly what unification adds.

이는 여기까지는 괜찮지만, `Job` 구조체의 필드로 미리 못박힌 *모양*의 패턴만 다룰 수 있습니다 — 이 방식으로는 "`x ++ y = [a, b, c, d]`가 되는 `x`와 `y`를 모두 찾아라" 같은 질의를 할 방법이 없습니다. `filter`는 고정된 술어만 검사할 수 있을 뿐, 패턴의 *어느* 변수 위치가 데이터의 *어느* 부분에 대응하는지를 발견할 수는 없기 때문입니다. 바로 그 발견 과정을 단일화가 더해줍니다.

---

## 4.4.2. 항, 대입, 그리고 단일화기

To talk about patterns with holes, we need a term language: constants, variables, and pairs, which is enough to encode lists as nested pairs the way Scheme does with `cons`:

구멍이 있는 패턴을 이야기하려면 항 언어가 필요합니다 — 상수, 변수, 그리고 쌍이면 충분하고, Scheme이 `cons`로 하듯 리스트를 중첩된 쌍으로 인코딩할 수 있습니다.

```lean
inductive Term where
  | var : String → Term
  | const : String → Term
  | pair : Term → Term → Term
deriving Repr, BEq

def Term.nil : Term := .const "nil"
def Term.cons (x xs : Term) : Term := .pair x xs

abbrev Subst := Std.HashMap String Term
```

A substitution has to be *chased through*: if `?x` is bound to `?y` and `?y` is bound to `(const "a")`, asking what `?x` "really is" means following that chain to the end. This chasing function, `walk`, is the first place termination becomes interesting — as long as every variable's binding is either a non-variable term or a *different* variable that itself terminates, `walk` recurses a bounded number of times, but nothing in the `Subst` type itself prevents someone from building a substitution where `?x ↦ ?x`, which would send `walk` into an infinite loop:

대입은 *따라가며 풀어야* 합니다 — `?x`가 `?y`에 묶여 있고 `?y`가 `(const "a")`에 묶여 있다면, `?x`가 "진짜로 무엇인지" 묻는 것은 그 사슬을 끝까지 따라가는 것을 뜻합니다. 이 추적 함수 `walk`가 종료성이 흥미로워지는 첫 지점입니다 — 모든 변수의 바인딩이 변수가 아닌 항이거나 그 자체로 종료되는 *다른* 변수인 한 `walk`는 유한 번 재귀하지만, `Subst` 타입 자체는 누군가 `?x ↦ ?x`인 대입을 만드는 것을 막지 않으며, 그런 대입이 있으면 `walk`는 무한 루프에 빠집니다.

```lean
partial def walk (s : Subst) : Term → Term
  | .var x => match s.get? x with
    | some t => walk s t
    | none => .var x
  | t => t
```

`walk` has to be `partial` — not because the recursion is hard to see, but because its termination depends on an invariant (the substitution never contains a cycle) that lives outside the type `Subst` entirely. Lean's checker only ever looks at the shape of the *term* being matched, and a `.var x` case can call `walk` again on another `.var`, so structurally nothing has gotten smaller. The responsibility for acyclicity shifts entirely onto whoever builds the substitution — which is exactly the unifier's job, via the *occurs check*.

`walk`는 `partial`이어야 합니다 — 재귀를 알아보기 어려워서가 아니라, 그 종료성이 `Subst` 타입 바깥에 있는 불변식(대입이 순환을 포함하지 않는다는 것)에 달려 있기 때문입니다. Lean의 검사기는 오직 매칭되는 *항*의 모양만 보는데, `.var x` 케이스가 또 다른 `.var`에 대해 `walk`를 다시 호출할 수 있으므로 구조적으로는 아무것도 작아지지 않습니다. 비순환성에 대한 책임은 전적으로 대입을 만드는 쪽으로 넘어가는데, 그것이 바로 *발생 검사(occurs check)*를 통한 단일화기의 역할입니다.

```lean
partial def occursIn (s : Subst) (x : String) (t : Term) : Bool :=
  match walk s t with
  | .var y => y == x
  | .const _ => false
  | .pair a b => occursIn s x a || occursIn s x b

partial def unify (s : Subst) : Term → Term → Option Subst
  | t1, t2 =>
    match walk s t1, walk s t2 with
    | .var x, .var y => if x == y then some s else some (s.insert x (.var y))
    | .var x, t => if occursIn s x t then none else some (s.insert x t)
    | t, .var x => if occursIn s x t then none else some (s.insert x t)
    | .const a, .const b => if a == b then some s else none
    | .pair a1 b1, .pair a2 b2 => do
      let s1 ← unify s a1 a2
      unify s1 b1 b2
    | _, _ => none
```

`unify` also has to be `partial`, for a reason worth separating from `walk`'s: the two structural arguments *do* shrink at every `.pair`/`.pair` case, since `a1`/`b1`/`a2`/`b2` are all strictly smaller than the enclosing pair. What defeats Lean's automatic termination proof here isn't recursive depth, it's that `unify` calls `walk`, and `walk` is already marked `partial` — Lean's termination checker doesn't look inside a `partial` function to see whether it's well-behaved, so any caller that depends on one has to accept `partial` too, by construction rather than by necessity. Give `walk` a `termination_by` argument (say, by threading a fuel parameter or proving the substitution acyclic as a `Subst` invariant) and `unify`'s own case-by-case recursion actually would be structurally provable.

`unify`도 `partial`이어야 하는데, 그 이유는 `walk`와는 구별해볼 만합니다 — 두 구조적 인자는 모든 `.pair`/`.pair` 경우에 *실제로* 줄어듭니다. `a1`/`b1`/`a2`/`b2`는 모두 감싸는 쌍보다 엄격히 작기 때문입니다. 여기서 Lean의 자동 종료성 증명을 무산시키는 것은 재귀 깊이가 아니라, `unify`가 `walk`를 호출하고 그 `walk`가 이미 `partial`로 표시되어 있다는 사실입니다 — Lean의 종료성 검사기는 `partial` 함수 안을 들여다보고 그것이 잘 동작하는지 확인해주지 않으므로, 그것에 의존하는 모든 호출자는 필연이 아니라 그저 그 구성 때문에 `partial`을 받아들여야 합니다. `walk`에 `termination_by`를 달아준다면(예컨대 연료 매개변수를 꿰거나, 대입이 비순환이라는 것을 `Subst`의 불변식으로 증명한다면) `unify` 자신의 케이스별 재귀는 실제로 구조적으로 증명 가능했을 것입니다.

연료 매개변수를 꿰는 쪽을 구체적으로 써보면 이렇습니다 — `fuel`이 세 번째가 아니라 첫 번째 인자여야, 그리고 `Term`과 함께 한 번에 패턴 매칭되어야 구조적 재귀로 받아들여집니다.

Threading a fuel parameter concretely looks like this — `fuel` has to come first and be pattern-matched jointly with the `Term` for Lean to see it as structural recursion:

```lean
def walkFuel : Nat → Subst → Term → Term
  | 0, _, t => t
  | n + 1, s, .var x =>
    match s.get? x with
    | some t => walkFuel n s t
    | none => .var x
  | _ + 1, _, t => t
```

이 버전은 `fuel`이 매 재귀 호출마다 구조적으로 줄어들므로 `partial`이 필요 없습니다. 하지만 이건 `walk`의 종료성을 *증명*한 게 아니라 종료를 *강제*한 것임을 분명히 해야 합니다 — 순환 대입을 만나면 진짜 `walk`는 영원히 멈추지 않지만, `walkFuel`은 `fuel`이 바닥나는 순간 조용히 그 시점의(아직 다 풀리지 않았을 수 있는) 항을 반환합니다. 정상적인 비순환 대입에 대해서는 두 버전이 같은 답을 내지만, 병적인 순환 입력에 대해서는 "영원히 멈추지 않음"이 "잘못된 답을 조용히 반환함"으로 바뀌는 것이니, 자원 한계를 종료성 증명의 대용품으로 쓸 때는 이 차이를 감수하고 있다는 것을 알아야 합니다.

This version needs no `partial`, since `fuel` shrinks structurally at every recursive call. But it's worth being precise that this *forces* termination rather than *proving* `walk` terminates — faced with a cyclic substitution, the real `walk` never returns, while `walkFuel` silently returns whatever (possibly still-unresolved) term it had reached the moment `fuel` ran out. The two agree on any acyclic substitution, but on pathological cyclic input, "never returns" becomes "silently returns a wrong answer" — a trade worth knowing you're making whenever a fuel parameter stands in for an actual termination proof.

```lean
#eval unify {} (.pair (.var "x") (.const "a")) (.pair (.const "b") (.var "y"))
-- some (fromList [("x", const "b"), ("y", const "a")])

#eval unify {} (.pair (.var "x") (.var "y")) (.pair (.var "y") (.const "a"))
-- some (fromList [("x", var "y"), ("y", const "a")])
```

The second example is SICP's own illustration of unification leaving a variable only partially resolved (`?x` bound to `?y`, not to a constant) — `walk`ing `?x` through this substitution correctly produces `const "a"`, exactly as SICP describes.

두 번째 예시는 단일화가 변수를 일부만 해소한 채로 남기는(`?x`가 상수가 아니라 `?y`에 묶임) SICP 자신의 예시입니다 — 이 대입을 통해 `?x`를 `walk`하면 SICP가 설명하는 대로 정확히 `const "a"`가 나옵니다.

---

## 4.4.3. 규칙을 귀납적 관계로 읽기

SICP's two-line characterization of `append` — the empty list appends to `y` to form `y`; a nonempty list appends by recursing on its tail — is not just *like* an inductive definition, it *is* one, almost unchanged. Lean's `inductive` propositions are built exactly this way: a base constructor and a recursive constructor whose premise is the relation applied to smaller arguments. Where SICP's query engine has to *discover* this correspondence by unifying against rule conclusions at run time, Lean lets us write the relation down directly as a type:

`append`에 대한 SICP의 두 줄짜리 서술 — 빈 리스트는 `y`와 붙어 `y`를 이룬다; 빈 리스트가 아니면 꼬리에 대해 재귀하며 붙는다 — 은 귀납적 정의와 그저 *비슷한* 게 아니라, 사실상 그 자체입니다. Lean의 `inductive` 명제는 정확히 이런 식으로 만들어집니다 — 기저 생성자 하나와, 전제가 더 작은 인자에 적용된 관계인 재귀 생성자 하나입니다. SICP의 질의 엔진은 실행 시점에 규칙 결론에 대한 단일화로 이 대응 관계를 *발견*해야 하지만, Lean에서는 이 관계를 타입으로 직접 써 내려갈 수 있습니다.

```lean
inductive AppendsTo : List α → List α → List α → Prop where
  | nil (y : List α) : AppendsTo [] y y
  | cons (u : α) (v y z : List α) :
      AppendsTo v y z → AppendsTo (u :: v) y (u :: z)
```

This buys us proof, not search — `AppendsTo` lets us *prove* that `[a, b]` and `[c, d]` append to `[a, b, c, d]`, but it doesn't, by itself, give us SICP's "ask which `y` appends with `(a b)` to produce `(a b c d)`" behavior, because Lean's `Prop`s aren't executable the way our hand-rolled `unify` is. To recover the query behavior — enumerate all `(x, y)` such that `x ++ y = target` — we go back to the `List`-monad style from the previous section, and the correspondence to `AppendsTo`'s two constructors is visible in the two things the search tries at each step:

이는 검색이 아니라 증명을 가져다줍니다 — `AppendsTo`는 `[a, b]`와 `[c, d]`가 붙어 `[a, b, c, d]`가 됨을 *증명*하게 해주지만, 그 자체로는 SICP의 "`(a b)`에 붙어 `(a b c d)`가 되는 `y`를 찾아라"는 동작을 주지 않습니다. Lean의 `Prop`은 우리가 손으로 만든 `unify`처럼 실행 가능하지 않기 때문입니다. 질의 동작 — `x ++ y = target`인 모든 `(x, y)`를 열거하기 — 을 되살리려면 이전 절의 `List` 모나드 방식으로 돌아가야 하고, 각 단계에서 탐색이 시도하는 두 가지에 `AppendsTo`의 두 생성자가 그대로 대응합니다.

```lean
def appendSplits (target : List α) : List (List α × List α) :=
  (List.range (target.length + 1)).map (fun n => (target.take n, target.drop n))

#eval appendSplits [1, 2, 3, 4]
-- [([], [1, 2, 3, 4]), ([1], [2, 3, 4]), ([1, 2], [3, 4]), ([1, 2, 3], [4]), ([1, 2, 3, 4], [])]
```

`appendSplits` terminates for the same reason every `List`-monad query in the previous post did: `List.range` and `.map` both recurse structurally on a shrinking list, no `partial` in sight. The interesting contrast with SICP isn't in the code at all — it's that SICP gets this enumeration "for free" from a single declarative pair of rules processed by a general-purpose unifying interpreter, while Lean needs either a bespoke enumerator like `appendSplits` (fast, but written by hand for this one relation) or a general resolution engine like the toy `unify` above, generalized to search over `AppendsTo`'s constructors (general, but exactly as much `partial`-laden machinery as SICP's own query evaluator).

`appendSplits`가 종료하는 이유는 이전 글의 모든 `List` 모나드 질의가 종료했던 것과 같습니다 — `List.range`와 `.map` 모두 줄어드는 리스트에 대한 구조적 재귀이고, `partial`이 낄 자리가 없습니다. SICP와의 흥미로운 대조는 코드 자체에 있는 게 아니라, SICP는 선언적인 규칙 한 쌍만으로 범용 단일화 인터프리터가 이 열거를 "공짜로" 해준다는 데 있습니다. 반면 Lean에서는 `appendSplits`처럼 이 관계 하나만을 위해 손으로 짠 전용 열거기(빠르지만 특화됨)를 쓰거나, 위의 장난감 `unify`를 `AppendsTo`의 생성자들에 대한 탐색으로 일반화한 범용 결정 엔진(일반적이지만 SICP의 질의 평가기만큼이나 `partial`이 필요한 장치)을 써야 합니다.

**연습문제 4.63 (Lean 버전).** SICP는 창세기의 족보 데이터베이스로부터 "손자", "아내의 아들은 곧 아들" 같은 규칙을 유도해보라고 합니다. Lean에서 이를 옮기면, 사실 데이터베이스는 그대로 관계로 남고, 유도 규칙은 그 관계들을 전제로 갖는 새 귀납적 관계(또는 `Prop`을 반환하는 함수)가 됩니다 — Prolog의 규칙과 Lean의 귀납 원리 사이의 대응 관계를 가장 직접적으로 보여주는 예시입니다.

```lean
inductive SonOf : String → String → Prop where
  | adam_cain : SonOf "Adam" "Cain"
  | cain_enoch : SonOf "Cain" "Enoch"

inductive WifeOf : String → String → Prop where
  | lamech_ada : WifeOf "Lamech" "Ada"

inductive GrandsonOf : String → String → Prop where
  | mk : SonOf s f → SonOf f g → GrandsonOf s g

theorem enochIsGrandsonOfAdam : GrandsonOf "Enoch" "Adam" :=
  .mk .cain_enoch .adam_cain
```

SICP의 질의 `(grandson ?x Adam)`가 데이터베이스를 훑어 답을 *찾아내는* 것과 달리, `enochIsGrandsonOfAdam`은 답을 이미 알고 있는 사람이 그 답이 왜 성립하는지를 *증명*합니다 — 이것이 이 시리즈 전체를 관통하는 주제이기도 합니다. Prolog류 질의 엔진이 "이 조건을 만족하는 게 있는가"를 실행 시점에 탐색으로 답한다면, Lean의 귀납적 관계는 "이것이 그 조건을 만족한다는 증거"를 컴파일 시점에 검사받는 항으로 답합니다. 둘 다 같은 논리적 구조(SICP의 규칙 = Lean의 생성자)를 공유하지만, 하나는 탐색 기계이고 다른 하나는 증명 검사기입니다.

The next post follows the last major thread SICP opens in Chapter 4 — the metacircular evaluator gains an explicit environment model and register-machine-level implementation in [Chapter 5](../5-1-register-machine-designs/), asking what an evaluator looks like once we stop assuming a host Lisp underneath it and build the machine itself.

다음 글은 SICP가 4장에서 여는 마지막 큰 흐름을 따라갑니다 — [5장](../5-1-register-machine-designs/)에서 메타순환 평가기는 명시적인 환경 모델과 레지스터 머신 수준의 구현을 얻습니다. 밑에 깔린 호스트 Lisp를 더 이상 가정하지 않고 기계 자체를 만들 때, 평가기가 어떤 모습이 되는지를 묻습니다.
