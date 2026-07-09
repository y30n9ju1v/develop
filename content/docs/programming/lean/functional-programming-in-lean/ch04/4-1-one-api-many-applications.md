---
title: "하나의 API, 다양한 응용"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Option, Except, 로깅, 상태 전달을 하나의 andThen 패턴으로 통합하기"
---

# One API, Many Applications

All these features and more can be implemented in library code as instances of a common API called `Monad`.
Lean provides dedicated syntax that makes this API convenient to use, but can also get in the way of understanding what is going on behind the scenes.
This chapter begins with the nitty-gritty presentation of manually nesting null checks, and builds from there to the convenient, general API.
Please suspend your disbelief in the meantime.

이러한 모든 기능과 더 많은 기능을 `Monad`라는 공통 API의 인스턴스로 라이브러리 코드에 구현할 수 있습니다. Lean은 이 API를 편리하게 사용하도록 하는 전용 구문을 제공하지만, 뒤에서 일어나는 일을 이해하는 데 방해가 될 수 있습니다. 이 챕터는 null 체크를 수동으로 중첩하는 세부사항부터 시작하여 편리한 일반 API까지 구축합니다. 그동안 의심을 유보해 주세요.

## 4.1.1. Checking for `none`: Don't Repeat Yourself

In Lean, pattern matching can be used to chain checks for null.
Getting the first entry from a list can just use the optional indexing notation:

Lean에서는 패턴 매칭을 사용하여 null 체크를 연쇄시킬 수 있습니다. 리스트의 첫 번째 항목을 가져오는 것은 선택적 인덱싱 표기법을 사용할 수 있습니다:

```lean
def first (xs : List α) : Option α :=
  xs[0]?
```

The fundamental problem with this code is that it addresses two concerns: extracting the numbers and checking that all of them are present.
The second concern is addressed by copying and pasting the code that handles the `none` case.
It is often good style to lift a repetitive segment into a helper function:

이 코드의 근본적인 문제점은 두 가지 우려사항을 다룬다는 것입니다: 숫자를 추출하고 모두 있는지 확인합니다. 두 번째 우려사항은 `none` 케이스를 처리하는 코드를 복사하여 붙여넣는 방식으로 해결됩니다. 반복적인 세그먼트를 헬퍼 함수로 들어올리는 것이 좋은 스타일인 경우가 많습니다:

```lean
def andThen (opt : Option α) (next : α → Option β) : Option β :=
  match opt with
  | none => none
  | some x => next x
```

This helper, which is used similarly to `?.` in C# and Kotlin, takes care of propagating `none` values.
It takes two arguments: an optional value and a function to apply when the value is not `none`.
If the first argument is `none`, then the helper returns `none`.
If the first argument is not `none`, then the function is applied to the contents of the `some` constructor.

이 헬퍼는 C#과 Kotlin의 `?.`와 유사하게 사용되며, `none` 값 전파를 처리합니다. 두 개의 인수를 받습니다: 선택적 값과 값이 `none`이 아닐 때 적용할 함수입니다. 첫 번째 인수가 `none`이면 헬퍼는 `none`을 반환합니다. 첫 번째 인수가 `none`이 아니면 `some` 생성자의 내용에 함수가 적용됩니다.

Now, `firstThird` can be rewritten to use `andThen` instead of pattern matching:

이제 `firstThird`를 패턴 매칭 대신 `andThen`을 사용하도록 다시 작성할 수 있습니다:

```lean
def firstThird (xs : List α) : Option (α × α) :=
  andThen xs[0]? fun first =>
  andThen xs[2]? fun third =>
  some (first, third)
```

In Lean, functions don't need to be enclosed in parentheses when passed as arguments.
The following equivalent definition uses more parentheses and indents the bodies of functions:

Lean에서는 인수로 전달될 때 함수를 괄호로 감쌀 필요가 없습니다. 다음 동등한 정의는 더 많은 괄호를 사용하고 함수 본문을 들여씁니다:

```lean
def firstThird (xs : List α) : Option (α × α) :=
  andThen xs[0]? (fun first =>
    andThen xs[2]? (fun third =>
      some (first, third)))
```

The `andThen` helper provides a sort of "pipeline" through which values flow, and the version with the somewhat unusual indentation is more suggestive of this fact.
Improving the syntax used to write `andThen` can make these computations even easier to understand.

`andThen` 헬퍼는 값이 흐르는 "파이프라인"의 일종을 제공합니다. 다소 특이한 들여쓰기가 있는 버전이 이 사실을 더 잘 시사합니다. `andThen`을 작성하는 데 사용되는 구문을 개선하면 이러한 계산을 더욱 쉽게 이해할 수 있습니다.

### 4.1.1.1. Infix Operators

In Lean, infix operators can be declared using the `infix`, `infixl`, and `infixr` commands, which create (respectively) non-associative, left-associative, and right-associative operators.
When used multiple times in a row, a *left associative* operator stacks up the opening parentheses on the left side of the expression.
The addition operator `+` is left associative, so `w + x + y + z` is equivalent to `(((w + x) + y) + z)`.
The exponentiation operator `^` is right associative, so `w ^ x ^ y ^ z` is equivalent to `w ^ (x ^ (y ^ z))`.
Comparison operators such as `<` are non-associative, so `x < y < z` is a syntax error and requires manual parentheses.

Lean에서는 `infix`, `infixl`, `infixr` 명령을 사용하여 중위 연산자를 선언할 수 있으며, 이는 각각 비결합적, 좌결합적, 우결합적 연산자를 만듭니다. 한 행에 여러 번 사용될 때, 좌결합적 연산자는 식의 왼쪽에 여는 괄호를 쌓습니다. 덧셈 연산자 `+`는 좌결합적이므로 `w + x + y + z`는 `(((w + x) + y) + z)`와 같습니다. 지수 연산자 `^`는 우결합적이므로 `w ^ x ^ y ^ z`는 `w ^ (x ^ (y ^ z))`와 같습니다. `<`와 같은 비교 연산자는 비결합적이므로 `x < y < z`는 구문 오류이며 수동 괄호가 필요합니다.

The following declaration makes `andThen` into an infix operator:

다음 선언은 `andThen`을 중위 연산자로 만듭니다:

```lean
infixl:55 " ~~> " => andThen
```

The number following the colon declares the *precedence* of the new infix operator.
In ordinary mathematical notation, `x + y * z` is equivalent to `x + (y * z)` even though both `+` and `*` are left associative.
In Lean, `+` has precedence 65 and `*` has precedence 70.
Higher-precedence operators are applied before lower-precedence operators.
According to the declaration of `~~>`, both `+` and `*` have higher precedence, and thus apply first.
Typically, figuring out the most convenient precedences for a group of operators requires some experimentation and a large collection of examples.

콜론 다음의 숫자는 새 중위 연산자의 우선순위를 선언합니다. 일반적인 수학 표기법에서 `x + y * z`는 `+`과 `*`이 모두 좌결합적이더라도 `x + (y * z)`와 같습니다. Lean에서는 `+`의 우선순위가 65이고 `*`의 우선순위가 70입니다. 우선순위가 높은 연산자가 우선순위가 낮은 연산자보다 먼저 적용됩니다. `~~>`의 선언에 따르면 `+`과 `*`은 모두 더 높은 우선순위를 가지며 따라서 먼저 적용됩니다. 일반적으로 연산자 그룹의 가장 편리한 우선순위를 파악하려면 많은 실험과 많은 예제가 필요합니다.

Following the new infix operator is a double arrow `=>`, which specifies the named function to be used for the infix operator.
Lean's standard library uses this feature to define `+` and `*` as infix operators that point at `HAdd.hAdd` and `HMul.hMul`, respectively, allowing type classes to be used to overload the infix operators.
Here, however, `andThen` is just an ordinary function.

새 중위 연산자 다음에는 중위 연산자에 사용할 명명된 함수를 지정하는 이중 화살표 `=>`가 있습니다. Lean의 표준 라이브러리는 이 기능을 사용하여 `+`과 `*`을 각각 `HAdd.hAdd`와 `HMul.hMul`을 가리키는 중위 연산자로 정의하므로 타입 클래스를 사용하여 중위 연산자를 오버로드할 수 있습니다. 그러나 여기서 `andThen`은 단지 일반적인 함수입니다.

Having defined an infix operator for `andThen`, `firstThird` can be rewritten in a way that brings the "pipeline" feeling of `none`-checks front and center:

`andThen`에 대한 중위 연산자를 정의한 후, `firstThird`를 `none` 체크의 "파이프라인" 느낌을 앞에 가져오는 방식으로 다시 작성할 수 있습니다:

```lean
def firstThirdInfix (xs : List α) : Option (α × α) :=
  xs[0]? ~~> fun first =>
  xs[2]? ~~> fun third =>
  some (first, third)
```

This style is much more concise when writing larger functions:

이 스타일은 더 큰 함수를 작성할 때 훨씬 더 간결합니다:

```lean
def firstThirdFifthSeventh (xs : List α) : Option (α × α × α × α) :=
  xs[0]? ~~> fun first =>
  xs[2]? ~~> fun third =>
  xs[4]? ~~> fun fifth =>
  xs[6]? ~~> fun seventh =>
  some (first, third, fifth, seventh)
```

## 4.1.2. Propagating Error Messages

Pure functional languages such as Lean have no built-in exception mechanism for error handling, because throwing or catching an exception is outside of the step-by-step evaluation model for expressions.
However, functional programs certainly need to handle errors.
In the case of `firstThirdFifthSeventh`, it is likely relevant for a user to know just how long the list was and where the lookup failed.

Lean 같은 순수 함수형 언어는 예외를 던지거나 잡는 것이 표현식의 단계별 평가 모델을 벗어나기 때문에 오류 처리를 위한 내장된 예외 메커니즘이 없습니다. 그러나 함수형 프로그램은 확실히 오류를 처리해야 합니다. `firstThirdFifthSeventh`의 경우 사용자가 리스트가 얼마나 길었는지, 조회가 실패한 위치를 알아야 할 가능성이 있습니다.

This is typically accomplished by defining a datatype that can be either an error or a result, and translating functions with exceptions into functions that return this datatype:

이는 일반적으로 오류이거나 결과일 수 있는 데이터 타입을 정의하고 예외가 있는 함수를 이 데이터 타입을 반환하는 함수로 변환하여 달성됩니다:

```lean
inductive Except (ε : Type) (α : Type) where
  | error : ε → Except ε α
  | ok : α → Except ε α
deriving BEq, Hashable, Repr
```

The type variable `ε` stands for the type of errors that can be produced by the function.
Callers are expected to handle both errors and successes, which makes the type variable `ε` play a role that is a bit like that of a list of checked exceptions in Java.

타입 변수 `ε`는 함수에서 생성될 수 있는 오류의 타입을 나타냅니다. 호출자는 오류와 성공 둘 다를 처리해야 하므로 타입 변수 `ε`는 Java의 확인된 예외 목록과 약간 비슷한 역할을 합니다.

Once again, a common pattern can be factored out into a helper.
Each step through the function checks for an error, and only proceeds with the rest of the computation if the result was a success.
A new version of `andThen` can be defined for `Except`:

다시 한 번, 공통 패턴을 헬퍼로 빼낼 수 있습니다. 함수의 각 단계는 오류를 확인하고, 결과가 성공인 경우에만 나머지 계산을 진행합니다. `Except`에 대해 `andThen`의 새 버전을 정의할 수 있습니다:

```lean
def andThen (attempt : Except e α) (next : α → Except e β) : Except e β :=
  match attempt with
  | Except.error msg => Except.error msg
  | Except.ok x => next x
```

Just as with `Option`, this version of `andThen` allows a more concise definition of `firstThird'`:

`Option`의 경우처럼 이 버전의 `andThen`은 `firstThird'`의 더 간결한 정의를 허용합니다:

```lean
def firstThird' (xs : List α) : Except String (α × α) :=
  andThen (get xs 0) fun first =>
  andThen (get xs 2) fun third =>
  Except.ok (first, third)
```

In both the `Option` and `Except` case, there are two repeating patterns: there is the checking of intermediate results at each step, which has been factored out into `andThen`, and there is the final successful result, which is `some` or `Except.ok`, respectively.
For the sake of convenience, success can be factored out into a helper called `ok`:

`Option`과 `Except` 경우 모두에서 두 가지 반복되는 패턴이 있습니다: 각 단계에서 중간 결과를 확인하는 것으로, `andThen`으로 빼낸 것과, 각각 `some` 또는 `Except.ok`인 최종 성공 결과가 있습니다. 편의상 성공을 `ok`라는 헬퍼로 빼낼 수 있습니다:

```lean
def ok (x : α) : Except ε α := Except.ok x
```

Similarly, failure can be factored out into a helper called `fail`:

마찬가지로 실패를 `fail`이라는 헬퍼로 빼낼 수 있습니다:

```lean
def fail (err : ε) : Except ε α := Except.error err
```

Using `ok` and `fail` makes `get` a little more readable:

`ok`와 `fail`을 사용하면 `get`을 조금 더 읽기 쉽게 만듭니다:

```lean
def get (xs : List α) (i : Nat) : Except String α :=
  match xs[i]? with
  | none => fail s!"Index {i} not found (maximum is {xs.length - 1})"
  | some x => ok x
```

After adding the infix declaration for `andThen`, `firstThird` can be just as concise as the version that returns an `Option`:

`andThen`의 중위 선언을 추가한 후 `firstThird`는 `Option`을 반환하는 버전만큼 간결할 수 있습니다:

```lean
infixl:55 " ~~> " => andThen
def firstThird (xs : List α) : Except String (α × α) :=
  get xs 0 ~~> fun first =>
  get xs 2 ~~> fun third =>
  ok (first, third)
```

The technique scales similarly to larger functions:

이 기법은 더 큰 함수에도 유사하게 확장됩니다:

```lean
def firstThirdFifthSeventh (xs : List α) : Except String (α × α × α × α) :=
  get xs 0 ~~> fun first =>
  get xs 2 ~~> fun third =>
  get xs 4 ~~> fun fifth =>
  get xs 6 ~~> fun seventh =>
  ok (first, third, fifth, seventh)
```

## 4.1.3. Logging

A number is even if dividing it by 2 leaves no remainder:

숫자는 2로 나누면 나머지가 없을 때 짝수입니다:

```lean
def isEven (i : Int) : Bool :=
  i % 2 == 0
```

The function `sumAndFindEvens` computes the sum of a list while remembering the even numbers encountered along the way:

함수 `sumAndFindEvens`는 리스트의 합을 계산하면서 도중에 마주친 짝수를 기억합니다:

```lean
def sumAndFindEvens : List Int → List Int × Int
  | [] => ([], 0)
  | i :: is =>
    let (moreEven, sum) := sumAndFindEvens is
    (if isEven i then i :: moreEven else moreEven, sum + i)
```

This function is a simplified example of a common pattern.
Many programs need to traverse a data structure once, while both computing a main result and accumulating some kind of tertiary extra result.
One example of this is logging: a program that is an `IO` action can always log to a file on disk, but because the disk is outside of the mathematical world of Lean functions, it becomes much more difficult to prove things about logs based on `IO`.
Another example is a function that computes the sum of all the nodes in a tree with an inorder traversal, while simultaneously recording each nodes visited:

이 함수는 공통 패턴의 단순화된 예입니다. 많은 프로그램은 데이터 구조를 한 번 순회하면서 주요 결과를 계산하고 어떤 종류의 삼차 추가 결과를 축적해야 합니다. 이의 한 예가 로깅입니다: `IO` 액션인 프로그램은 항상 디스크의 파일에 로깅할 수 있지만, 디스크는 Lean 함수의 수학적 세계 밖에 있기 때문에 `IO`를 기반으로 한 로그에 대해 증명하기가 훨씬 더 어려워집니다. 또 다른 예는 중위 순회로 트리의 모든 노드의 합을 계산하면서 동시에 방문한 각 노드를 기록하는 함수입니다:

```lean
def inorderSum : BinTree Int → List Int × Int
  | BinTree.leaf => ([], 0)
  | BinTree.branch l x r =>
    let (leftVisited, leftSum) := inorderSum l
    let (hereVisited, hereSum) := ([x], x)
    let (rightVisited, rightSum) := inorderSum r
    (leftVisited ++ hereVisited ++ rightVisited,
     leftSum + hereSum + rightSum)
```

Both `sumAndFindEvens` and `inorderSum` have a common repetitive structure.
Each step of computation returns a pair that consists of a list of data that have been saved along with the primary result.
The lists are then appended, and the primary result is computed and paired with the appended lists.
The common structure becomes more apparent with a small rewrite of `sumAndFindEvens` that more cleanly separates the concerns of saving even numbers and computing the sum:

`sumAndFindEvens`과 `inorderSum`은 공통된 반복적인 구조를 가지고 있습니다. 계산의 각 단계는 저장된 데이터 목록과 주요 결과로 구성된 쌍을 반환합니다. 그런 다음 목록이 추가되고 주요 결과가 계산되고 추가된 목록과 쌍을 이룹니다. 짝수 저장과 합 계산의 우려사항을 더 명확하게 분리하는 `sumAndFindEvens`의 작은 재작성으로 공통 구조가 더 분명해집니다:

```lean
def sumAndFindEvens : List Int → List Int × Int
  | [] => ([], 0)
  | i :: is =>
    let (moreEven, sum) := sumAndFindEvens is
    let (evenHere, ()) := (if isEven i then [i] else [], ())
    (evenHere ++ moreEven, sum + i)
```

For the sake of clarity, a pair that consists of an accumulated result together with a value can be given its own name:

명확함을 위해 축적된 결과와 값으로 구성된 쌍에 자신의 이름을 지정할 수 있습니다:

```lean
structure WithLog (logged : Type) (α : Type) where
  log : List logged
  val : α
```

Similarly, the process of saving a list of accumulated results while passing a value on to the next step of a computation can be factored out into a helper, once again named `andThen`:

마찬가지로 축적된 결과 목록을 저장하면서 값을 계산의 다음 단계로 전달하는 프로세스를 헬퍼로 빼낼 수 있습니다. 이번에도 `andThen`이라고 이름을 지었습니다:

```lean
def andThen (result : WithLog α β) (next : β → WithLog α γ) : WithLog α γ :=
  let {log := thisOut, val := thisRes} := result
  let {log := nextOut, val := nextRes} := next thisRes
  {log := thisOut ++ nextOut, val := nextRes}
```

In the case of errors, `ok` represents an operation that always succeeds.
Here, however, it is an operation that simply returns a value without logging anything:

오류의 경우 `ok`는 항상 성공하는 연산을 나타냅니다. 그러나 여기서는 아무것도 로깅하지 않고 값을 단순히 반환하는 연산입니다:

```lean
def ok (x : β) : WithLog α β := {log := [], val := x}
```

Just as `Except` provides `fail` as a possibility, `WithLog` should allow items to be added to a log.
This has no interesting return value associated with it, so it returns `Unit`:

`Except`가 `fail`을 가능성으로 제공하는 것처럼, `WithLog`는 항목을 로그에 추가할 수 있어야 합니다. 이와 관련된 흥미로운 반환 값이 없으므로 `Unit`을 반환합니다:

```lean
def save (data : α) : WithLog α Unit :=
  {log := [data], val := ()}
```

`WithLog`, `andThen`, `ok`, and `save` can be used to separate the logging concern from the summing concern in both programs:

`WithLog`, `andThen`, `ok`, `save`는 두 프로그램 모두에서 로깅 우려사항을 합산 우려사항과 분리하는 데 사용할 수 있습니다:

```lean
def sumAndFindEvens : List Int → WithLog Int Int
  | [] => ok 0
  | i :: is =>
    andThen (if isEven i then save i else ok ()) fun () =>
    andThen (sumAndFindEvens is) fun sum =>
    ok (i + sum)
def inorderSum : BinTree Int → WithLog Int Int
  | BinTree.leaf => ok 0
  | BinTree.branch l x r =>
    andThen (inorderSum l) fun leftSum =>
    andThen (save x) fun () =>
    andThen (inorderSum r) fun rightSum =>
    ok (leftSum + x + rightSum)
```

And, once again, the infix operator helps put focus on the correct steps:

그리고 다시 한 번, 중위 연산자는 올바른 단계에 초점을 맞추는 데 도움이 됩니다:

```lean
infixl:55 " ~~> " => andThen
def sumAndFindEvens : List Int → WithLog Int Int
  | [] => ok 0
  | i :: is =>
    (if isEven i then save i else ok ()) ~~> fun () =>
    sumAndFindEvens is ~~> fun sum =>
    ok (i + sum)
def inorderSum : BinTree Int → WithLog Int Int
  | BinTree.leaf => ok 0
  | BinTree.branch l x r =>
    inorderSum l ~~> fun leftSum =>
    save x ~~> fun () =>
    inorderSum r ~~> fun rightSum =>
    ok (leftSum + x + rightSum)
```

## 4.1.4. Numbering Tree Nodes

An *inorder numbering* of a tree associates each data point in the tree with the step it would be visited at in an inorder traversal of the tree.
For example, consider `aTree`:

트리의 중위 번호 매기기는 트리의 각 데이터 포인트를 트리의 중위 순회에서 방문할 단계와 연결합니다. 예를 들어, `aTree`를 고려하세요:

```lean
open BinTree in
def aTree :=
  branch
    (branch
      (branch leaf "a" (branch leaf "b" leaf))
      "c"
      leaf)
    "d"
    (branch leaf "e" leaf)
```

Its inorder numbering is:

중위 번호 매기기는:

```
BinTree.branch
  (BinTree.branch
    (BinTree.branch (BinTree.leaf) (0, "a") (BinTree.branch (BinTree.leaf) (1, "b") (BinTree.leaf)))
    (2, "c")
    (BinTree.leaf))
  (3, "d")
  (BinTree.branch (BinTree.leaf) (4, "e") (BinTree.leaf))
```

Trees are most naturally processed with recursive functions, but the usual pattern of recursion on trees makes it difficult to compute an inorder numbering.
This is because the highest number assigned anywhere in the left subtree is used to determine the numbering of a node's data value, and then again to determine the starting point for numbering the right subtree.
In an imperative language, this issue can be worked around by using a mutable variable that contains the next number to be assigned.
The following Python program computes an inorder numbering using a mutable variable:

트리는 재귀 함수로 가장 자연스럽게 처리되지만, 트리에 대한 일반적인 재귀 패턴은 중위 번호 매기기를 계산하기 어렵게 만듭니다. 이는 왼쪽 부트리의 어디에 할당된 가장 높은 숫자가 노드의 데이터 값 번호 매기기를 결정하는 데 사용되고, 그런 다음 오른쪽 부트리 번호 매기기의 시작점을 결정하는 데 다시 사용되기 때문입니다. 명령형 언어에서는 이 문제를 할당할 다음 숫자를 포함하는 가변 변수를 사용하여 해결할 수 있습니다. 다음 Python 프로그램은 가변 변수를 사용하여 중위 번호 매기기를 계산합니다:

```
class Branch:
    def __init__(self, value, left=None, right=None):
        self.left = left
        self.value = value
        self.right = right
    def __repr__(self):
        return f'Branch({self.value!r}, left={self.left!r}, right={self.right!r})'

def number(tree):
    num = 0
    def helper(t):
        nonlocal num
        if t is None:
            return None
        else:
            new_left = helper(t.left)
            new_value = (num, t.value)
            num += 1
            new_right = helper(t.right)
            return Branch(left=new_left, value=new_value, right=new_right)

    return helper(tree)
```

The numbering of the Python equivalent of `aTree` is:

`aTree`의 Python 동등물의 번호 매기기는:

```
a_tree = Branch("d",
                left=Branch("c",
                            left=Branch("a", left=None, right=Branch("b")),
                            right=None),
                right=Branch("e"))
```

and its numbering is:

그리고 번호 매기기는:

```python
>>> number(a_tree)
```

```
Branch((3, 'd'), left=Branch((2, 'c'), left=Branch((0, 'a'), left=None, right=Branch((1, 'b'), left=None, right=None)), right=None), right=Branch((4, 'e'), left=None, right=None))
```

Even though Lean does not have mutable variables, a workaround exists.
From the point of view of the rest of the world, the mutable variable can be thought of as having two relevant aspects: its value when the function is called, and its value when the function returns.
In other words, a function that uses a mutable variable can be seen as a function that takes the mutable variable's starting value as an argument, returning a pair of the variable's final value and the function's result.
This final value can then be passed as an argument to the next step.

Lean에는 가변 변수가 없지만 해결 방법이 있습니다. 나머지 세계의 관점에서 가변 변수는 두 가지 관련 측면을 가진 것으로 생각할 수 있습니다: 함수가 호출될 때의 값과 함수가 반환될 때의 값입니다. 즉, 가변 변수를 사용하는 함수는 가변 변수의 시작 값을 인수로 받아 변수의 최종 값과 함수의 결과의 쌍을 반환하는 함수로 볼 수 있습니다. 이 최종 값은 그런 다음 다음 단계에 대한 인수로 전달될 수 있습니다.

Just as the Python example uses an outer function that establishes a mutable variable and an inner helper function that changes the variable, a Lean version of the function uses an outer function that provides the variable's starting value and explicitly returns the function's result along with an inner helper function that threads the variable's value while computing the numbered tree:

Python 예제가 가변 변수를 설정하는 외부 함수와 변수를 변경하는 내부 헬퍼 함수를 사용하는 것처럼, 함수의 Lean 버전은 변수의 시작 값을 제공하고 명시적으로 함수의 결과를 반환하는 외부 함수와 번호가 매겨진 트리를 계산하는 동안 변수의 값을 전달하는 내부 헬퍼 함수를 사용합니다:

```lean
def number (t : BinTree α) : BinTree (Nat × α) :=
  let rec helper (n : Nat) : BinTree α → (Nat × BinTree (Nat × α))
    | BinTree.leaf => (n, BinTree.leaf)
    | BinTree.branch left x right =>
      let (k, numberedLeft) := helper n left
      let (i, numberedRight) := helper (k + 1) right
      (i, BinTree.branch numberedLeft (k, x) numberedRight)
  (helper 0 t).snd
```

This code, like the `none`-propagating `Option` code, the `error`-propagating `Except` code, and the log-accumulating `WithLog` code, commingles two concerns: propagating the value of the counter, and actually traversing the tree to find the result.
Just as in those cases, an `andThen` helper can be defined to propagate state from one step of a computation to another.
The first step is to give a name to the pattern of taking an input state as an argument and returning an output state together with a value:

이 코드는 `none`-전파하는 `Option` 코드, `error`-전파하는 `Except` 코드, 로그-축적하는 `WithLog` 코드처럼 두 가지 우려사항을 섞습니다: 카운터의 값 전파 및 실제로 트리를 순회하여 결과를 찾기. 이러한 경우들처럼 `andThen` 헬퍼를 정의하여 계산의 한 단계에서 다른 단계로 상태를 전파할 수 있습니다. 첫 번째 단계는 입력 상태를 인수로 받아 출력 상태와 값을 함께 반환하는 패턴에 이름을 지정하는 것입니다:

```lean
def State (σ : Type) (α : Type) : Type :=
  σ → (σ × α)
```

In the case of `State`, `ok` is a function that returns the input state unchanged, along with the provided value:

`State`의 경우 `ok`는 입력 상태를 변경되지 않은 상태로 제공된 값과 함께 반환하는 함수입니다:

```lean
def ok (x : α) : State σ α :=
  fun s => (s, x)
```

When working with a mutable variable, there are two fundamental operations: reading the value and replacing it with a new one.
Reading the current value is accomplished with a function that places the input state unmodified into the output state, and also places it into the value field:

가변 변수를 사용할 때 두 가지 기본 연산이 있습니다: 값 읽기와 새 값으로 교체. 현재 값 읽기는 입력 상태를 변경되지 않은 상태로 출력 상태에 배치하고 값 필드에도 배치하는 함수로 달성됩니다:

```lean
def get : State σ σ :=
  fun s => (s, s)
```

Writing a new value consists of ignoring the input state, and placing the provided new value into the output state:

새 값을 작성하는 것은 입력 상태를 무시하고 제공된 새 값을 출력 상태에 배치하는 것으로 구성됩니다:

```lean
def set (s : σ) : State σ Unit :=
  fun _ => (s, ())
```

Finally, two computations that use state can be sequenced by finding both the output state and return value of the first function, then passing them both into the next function:

마지막으로 상태를 사용하는 두 계산은 첫 번째 함수의 출력 상태와 반환 값을 찾은 다음 둘 다를 다음 함수에 전달하여 순서대로 나열할 수 있습니다:

```lean
def andThen (first : State σ α) (next : α → State σ β) : State σ β :=
  fun s =>
    let (s', x) := first s
    next x s'
infixl:55 " ~~> " => andThen
```

Using `State` and its helpers, local mutable state can be simulated:

`State`와 그 헬퍼를 사용하여 로컬 가변 상태를 시뮬레이션할 수 있습니다:

```lean
def number (t : BinTree α) : BinTree (Nat × α) :=
  let rec helper : BinTree α → State Nat (BinTree (Nat × α))
    | BinTree.leaf => ok BinTree.leaf
    | BinTree.branch left x right =>
      helper left ~~> fun numberedLeft =>
      get ~~> fun n =>
      set (n + 1) ~~> fun () =>
      helper right ~~> fun numberedRight =>
      ok (BinTree.branch numberedLeft (n, x) numberedRight)
  (helper t 0).snd
```

Because `State` simulates only a single local variable, `get` and `set` don't need to refer to any particular variable name.

`State`는 단일 로컬 변수만 시뮬레이션하므로 `get`과 `set`은 특정 변수 이름을 참조할 필요가 없습니다.
