---
title: "Tail Recursion"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Tail Recursion"
---

# 8.1. Tail Recursion

While Lean's `do`-notation makes it possible to use traditional loop syntax such as `for` and `while`, these constructs are translated behind the scenes to invocations of recursive functions.
In most programming languages, recursive functions have a key disadvantage with respect to loops: loops consume no space on the stack, while recursive functions consume stack space proportional to the number of recursive calls.
Stack space is typically limited, and it is often necessary to take algorithms that are naturally expressed as recursive functions and rewrite them as loops paired with an explicit mutable heap-allocated stack.

Lean의 `do`-notation을 사용하면 `for`와 `while` 같은 전통적인 루프 문법을 사용할 수 있지만, 이러한 구조들은 내부적으로 재귀 함수의 호출로 변환됩니다.
대부분의 프로그래밍 언어에서 재귀 함수는 루프에 비해 중요한 단점이 있습니다: 루프는 스택에 공간을 소비하지 않지만, 재귀 함수는 재귀 호출 수에 비례하는 스택 공간을 소비합니다.
스택 공간은 일반적으로 제한되어 있으므로, 재귀 함수로 자연스럽게 표현되는 알고리즘을 루프와 명시적인 가변 힙 할당 스택으로 다시 작성해야 하는 경우가 많습니다.

In functional programming, the opposite is typically true.
Programs that are naturally expressed as mutable loops may consume stack space, while rewriting them to recursive functions can cause them to run quickly.
This is due to a key aspect of functional programming languages: *tail-call elimination*.
A tail call is a call from one function to another that can be compiled to an ordinary jump, replacing the current stack frame rather than pushing a new one, and tail-call elimination is the process of implementing this transformation.

함수형 프로그래밍에서는 일반적으로 반대가 참입니다.
가변 루프로 자연스럽게 표현되는 프로그램은 스택 공간을 소비할 수 있지만, 이를 재귀 함수로 다시 작성하면 빠르게 실행될 수 있습니다.
이는 함수형 프로그래밍 언어의 핵심 측면 때문입니다: *tail-call elimination* (꼬리 호출 제거).
꼬리 호출은 한 함수에서 다른 함수로의 호출로, 새로운 스택 프레임을 푸시하는 대신 현재 스택 프레임을 대체하는 일반적인 점프로 컴파일될 수 있으며, 꼬리 호출 제거는 이 변환을 구현하는 프로세스입니다.

Tail-call elimination is not just merely an optional optimization.
Its presence is a fundamental part of being able to write efficient functional code.
For it to be useful, it must be reliable.
Programmers must be able to reliably identify tail calls, and they must be able to trust that the compiler will eliminate them.

꼬리 호출 제거는 단순한 선택적 최적화가 아닙니다.
그것의 존재는 효율적인 함수형 코드를 작성할 수 있는 기본적인 부분입니다.
유용하려면 신뢰할 수 있어야 합니다.
프로그래머는 꼬리 호출을 확실하게 식별할 수 있어야 하며, 컴파일러가 이를 제거할 것이라고 믿을 수 있어야 합니다.

The function `NonTail.sum` adds the contents of a list of `Nat`s:

`def NonTail.sum : List Nat → Nat
| [] => 0
| x :: xs => x + sum xs`

`NonTail.sum` 함수는 `Nat` 리스트의 내용을 더합니다.

Applying this function to the list `[1, 2, 3]` results in the following sequence of evaluation steps:

`NonTail.sum [1, 2, 3]``1 + (NonTail.sum [2, 3])``1 + (2 + (NonTail.sum [3]))``1 + (2 + (3 + (NonTail.sum [])))``1 + (2 + (3 + 0))``1 + (2 + 3)``1 + 5``6`

이 함수를 리스트 `[1, 2, 3]`에 적용하면 다음의 평가 단계 순서가 생깁니다.

In the evaluation steps, parentheses indicate recursive calls to `NonTail.sum`.
In other words, to add the three numbers, the program must first check that the list is non-empty.
To add the head of the list (`1`) to the sum of the tail of the list, it is first necessary to compute the sum of the tail of the list:

But to compute the sum of the tail of the list, the program must check whether it is empty.
It is not—the tail is itself a list with `2` at its head.
The resulting step is waiting for the return of `NonTail.sum [3]`:

The whole point of the run-time call stack is to keep track of the values `1`, `2`, and `3` along with the instruction to add them to the result of the recursive call.
As recursive calls are completed, control returns to the stack frame that made the call, so each step of addition is performed.
Storing the heads of the list and the instructions to add them is not free; it takes space proportional to the length of the list.

평가 단계에서 괄호는 `NonTail.sum`에 대한 재귀 호출을 나타냅니다.
다시 말해, 세 숫자를 더하기 위해 프로그램은 먼저 리스트가 비어있지 않은지 확인해야 합니다.
리스트의 헤드(`1`)를 리스트의 꼬리의 합에 더하기 위해, 먼저 리스트의 꼬리의 합을 계산해야 합니다.

하지만 리스트의 꼬리의 합을 계산하기 위해, 프로그램은 그것이 비어있는지 확인해야 합니다.
그렇지 않습니다. 꼬리는 그 자체로 헤드에 `2`가 있는 리스트입니다.
결과적인 단계는 `NonTail.sum [3]`의 반환을 기다리고 있습니다.

런타임 호출 스택의 전체 목적은 값 `1`, `2`, 그리고 `3`을 재귀 호출의 결과에 더하는 지시사항과 함께 추적하는 것입니다.
재귀 호출이 완료되면, 제어는 호출을 한 스택 프레임으로 반환되므로, 더하기의 각 단계가 수행됩니다.
리스트의 헤드와 이들을 더하는 지시사항을 저장하는 것은 무료가 아닙니다. 리스트의 길이에 비례하는 공간이 소요됩니다.

The function `Tail.sum` also adds the contents of a list of `Nat`s:

`def Tail.sumHelper (soFar : Nat) : List Nat → Nat
| [] => soFar
| x :: xs => sumHelper (x + soFar) xs
def Tail.sum (xs : List Nat) : Nat :=
Tail.sumHelper 0 xs`

`Tail.sum` 함수도 `Nat` 리스트의 내용을 더합니다.

Applying it to the list `[1, 2, 3]` results in the following sequence of evaluation steps:

`Tail.sum [1, 2, 3]``Tail.sumHelper 0 [1, 2, 3]``Tail.sumHelper (0 + 1) [2, 3]``Tail.sumHelper 1 [2, 3]``Tail.sumHelper (1 + 2) [3]``Tail.sumHelper 3 [3]``Tail.sumHelper (3 + 3) []``Tail.sumHelper 6 []``6`

이를 리스트 `[1, 2, 3]`에 적용하면 다음의 평가 단계 순서가 생깁니다.

The internal helper function calls itself recursively, but it does so in a way where nothing needs to be remembered in order to compute the final result.
When `Tail.sumHelper` reaches its base case, control can be returned directly to `Tail.sum`, because the intermediate invocations of `Tail.sumHelper` simply return the results of their recursive calls unmodified.
In other words, a single stack frame can be re-used for each recursive invocation of `Tail.sumHelper`.
Tail-call elimination is exactly this re-use of the stack frame, and `Tail.sumHelper` is referred to as a *tail-recursive function*.

The first argument to `Tail.sumHelper` contains all of the information that would otherwise need to be tracked in the call stack—namely, the sum of the numbers encountered so far.
In each recursive call, this argument is updated with new information, rather than adding new information to the call stack.
Arguments like `soFar` that replace the information from the call stack are called *accumulators*.

내부 헬퍼 함수는 자신을 재귀적으로 호출하지만, 최종 결과를 계산하기 위해 아무것도 기억할 필요가 없는 방식으로 그렇게 합니다.
`Tail.sumHelper`가 기본 경우에 도달하면, `Tail.sumHelper`의 중간 호출들이 단순히 재귀 호출의 결과를 수정 없이 반환하기 때문에, 제어를 `Tail.sum`으로 직접 반환할 수 있습니다.
다시 말해, 단일 스택 프레임은 `Tail.sumHelper`의 각 재귀 호출에 대해 재사용될 수 있습니다.
꼬리 호출 제거는 정확히 이 스택 프레임의 재사용이며, `Tail.sumHelper`는 *tail-recursive function* (꼬리 재귀 함수)라고 불립니다.

`Tail.sumHelper`에 대한 첫 번째 인자는 호출 스택에서 추적해야 할 모든 정보를 포함합니다. 즉, 지금까지 만난 숫자들의 합입니다.
각 재귀 호출에서, 이 인자는 새로운 정보로 업데이트되며, 호출 스택에 새로운 정보를 추가하지 않습니다.
`soFar`와 같이 호출 스택의 정보를 대체하는 인자들을 *accumulators* (누적자)라고 부릅니다.

At the time of writing and on the author's computer, `NonTail.sum` crashes with a stack overflow when passed a list with 216,856 or more entries.
`Tail.sum`, on the other hand, can sum a list of 100,000,000 elements without a stack overflow.
Because no new stack frames need to be pushed while running `Tail.sum`, it is completely equivalent to a `while` loop with a mutable variable that holds the current list.
At each recursive call, the function argument on the stack is simply replaced with the next node of the list.

저작 시점의 저자의 컴퓨터에서 `NonTail.sum`은 216,856개 이상의 항목을 가진 리스트가 전달될 때 스택 오버플로우로 충돌합니다.
반면 `Tail.sum`은 스택 오버플로우 없이 100,000,000개 요소의 리스트를 합산할 수 있습니다.
`Tail.sum` 실행 중 새로운 스택 프레임을 푸시할 필요가 없기 때문에, 현재 리스트를 보유하는 가변 변수를 가진 `while` 루프와 완전히 동등합니다.
각 재귀 호출에서, 스택의 함수 인자는 단순히 리스트의 다음 노드로 대체됩니다.

## 8.1.1. Tail and Non-Tail Positions

The reason why `Tail.sumHelper` is tail recursive is that the recursive call is in *tail position*.
Informally speaking, a function call is in tail position when the caller does not need to modify the returned value in any way, but will just return it directly.
More formally, tail position can be defined explicitly for expressions.

If a `match`-expression is in tail position, then each of its branches is also in tail position.
Once a `match` has selected a branch, control proceeds immediately to it.
Similarly, both branches of an `if`-expression are in tail position if the `if`-expression itself is in tail position.
Finally, if a `let`-expression is in tail position, then its body is as well.

All other positions are not in tail position.
The arguments to a function or a constructor are not in tail position because evaluation must track the function or constructor that will be applied to the argument's value.
The body of an inner function is not in tail position because control may not even pass to it: function bodies are not evaluated until the function is called.
Similarly, the body of a function type is not in tail position.
To evaluate `E` in `(x : α) → E`, it is necessary to track that the resulting type must have `(x : α) → ...` wrapped around it.

`Tail.sumHelper`가 꼬리 재귀인 이유는 재귀 호출이 *tail position* (꼬리 위치)에 있기 때문입니다.
비공식적으로 말하면, 함수 호출이 꼬리 위치에 있을 때 호출자가 반환된 값을 어떤 방식으로든 수정할 필요가 없고, 단지 그것을 직접 반환하려고 합니다.
더 공식적으로는, 꼬리 위치를 표현식에 대해 명시적으로 정의할 수 있습니다.

`match`-expression이 꼬리 위치에 있으면, 그것의 각 분기도 꼬리 위치에 있습니다.
`match`가 분기를 선택한 후, 제어는 즉시 그것으로 진행됩니다.
마찬가지로, `if`-expression의 두 분기는 `if`-expression 자체가 꼬리 위치에 있을 때 꼬리 위치에 있습니다.
마지막으로, `let`-expression이 꼬리 위치에 있으면, 그것의 본문도 그렇습니다.

다른 모든 위치는 꼬리 위치에 있지 않습니다.
함수 또는 생성자에 대한 인자는 꼬리 위치에 있지 않습니다. 왜냐하면 평가는 인자의 값에 적용될 함수 또는 생성자를 추적해야 하기 때문입니다.
내부 함수의 본문은 꼬리 위치에 있지 않습니다. 왜냐하면 제어가 그것으로 통과하지 않을 수도 있기 때문입니다: 함수 본문은 함수가 호출될 때까지 평가되지 않습니다.
마찬가지로, 함수 타입의 본문은 꼬리 위치에 있지 않습니다.
`(x : α) → E`에서 `E`를 평가하기 위해, 결과 타입이 `(x : α) → ...`로 감싸져 있어야 한다는 것을 추적해야 합니다.

In `NonTail.sum`, the recursive call is not in tail position because it is an argument to `+`.
In `Tail.sumHelper`, the recursive call is in tail position because it is immediately underneath a pattern match, which itself is the body of the function.

At the time of writing, Lean only eliminates direct tail calls in recursive functions.
This means that tail calls to `f` in `f`'s definition will be eliminated, but not tail calls to some other function `g`.
While it is certainly possible to eliminate a tail call to some other function, saving a stack frame, this is not yet implemented in Lean.

`NonTail.sum`에서 재귀 호출은 `+`의 인자이기 때문에 꼬리 위치에 있지 않습니다.
`Tail.sumHelper`에서 재귀 호출은 패턴 매치 바로 아래에 있기 때문에 꼬리 위치에 있으며, 패턴 매치는 그 자체로 함수의 본문입니다.

저작 시점에서 Lean은 재귀 함수에서 직접 꼬리 호출만 제거합니다.
즉, `f`의 정의에서 `f`로의 꼬리 호출은 제거되지만, 다른 함수 `g`로의 꼬리 호출은 제거되지 않음입니다.
다른 함수로의 꼬리 호출을 제거하는 것이 스택 프레임을 절약할 수 있지만, 이는 아직 Lean에 구현되지 않았습니다.

## 8.1.2. Reversing Lists

The function `NonTail.reverse` reverses lists by appending the head of each sub-list to the end of the result:

`def NonTail.reverse : List α → List α
| [] => []
| x :: xs => reverse xs ++ [x]`

`NonTail.reverse` 함수는 각 부분 리스트의 헤드를 결과의 끝에 추가하여 리스트를 역순으로 합니다.

Using it to reverse `[1, 2, 3]` yields the following sequence of steps:

`NonTail.reverse [1, 2, 3]``(NonTail.reverse [2, 3]) ++ [1]``((NonTail.reverse [3]) ++ [2]) ++ [1]``(((NonTail.reverse []) ++ [3]) ++ [2]) ++ [1]``(([] ++ [3]) ++ [2]) ++ [1]``([3] ++ [2]) ++ [1]``[3, 2] ++ [1]``[3, 2, 1]`

이를 사용하여 `[1, 2, 3]`을 역순으로 하면 다음의 단계 순서가 생깁니다.

The tail-recursive version uses `x :: ·` instead of `· ++ [x]` on the accumulator at each step:

`def Tail.reverseHelper (soFar : List α) : List α → List α
| [] => soFar
| x :: xs => reverseHelper (x :: soFar) xs
def Tail.reverse (xs : List α) : List α :=
Tail.reverseHelper [] xs`

꼬리 재귀 버전은 각 단계에서 누적자에 `· ++ [x]` 대신 `x :: ·`를 사용합니다.

This is because the context saved in each stack frame while computing with `NonTail.reverse` is applied beginning at the base case.
Each “remembered” piece of context is executed in last-in, first-out order.
On the other hand, the accumulator-passing version modifies the accumulator beginning from the first entry in the list, rather than the original base case, as can be seen in the series of reduction steps:

`Tail.reverse [1, 2, 3]``Tail.reverseHelper [] [1, 2, 3]``Tail.reverseHelper [1] [2, 3]``Tail.reverseHelper [2, 1] [3]``Tail.reverseHelper [3, 2, 1] []``[3, 2, 1]`

이는 `NonTail.reverse`로 계산할 때 각 스택 프레임에 저장된 컨텍스트가 기본 경우부터 시작하여 적용되기 때문입니다.
각 “기억된” 컨텍스트 조각은 후입선출(LIFO) 순서로 실행됩니다.
반면 누적자 전달 버전은 원래 기본 경우가 아닌 리스트의 첫 번째 항목부터 시작하여 누적자를 수정합니다.

In other words, the non-tail-recursive version starts at the base case, modifying the result of recursion from right to left through the list.
The entries in the list affect the accumulator in a first-in, first-out order.
The tail-recursive version with the accumulator starts at the head of the list, modifying an initial accumulator value from left to right through the list.

다시 말해, non-tail-recursive 버전은 기본 경우부터 시작하여 리스트를 통해 오른쪽에서 왼쪽으로 재귀의 결과를 수정합니다.
리스트의 항목들은 선입선출(FIFO) 순서로 누적자에 영향을 미칩니다.
누적자가 있는 꼬리 재귀 버전은 리스트의 헤드에서 시작하여, 초기 누적자 값을 리스트를 통해 왼쪽에서 오른쪽으로 수정합니다.

Because addition is commutative, nothing needed to be done to account for this in `Tail.sum`.
Appending lists is not commutative, so care must be taken to find an operation that has the same effect when run in the opposite direction.
Appending `[x]` after the result of the recursion in `NonTail.reverse` is analogous to adding `x` to the beginning of the list when the result is built in the opposite order.

더하기는 교환법칙이 성립하므로, `Tail.sum`에서 이것을 고려하기 위해 아무것도 할 필요가 없습니다.
리스트를 추가하는 것은 교환법칙이 성립하지 않으므로, 반대 방향으로 실행할 때 동일한 효과를 갖는 연산을 찾기 위해 주의해야 합니다.
`NonTail.reverse`의 재귀 결과 후에 `[x]`를 추가하는 것은 결과가 반대 순서로 구성될 때 리스트의 시작에 `x`를 추가하는 것과 유사합니다.

## 8.1.3. Multiple Recursive Calls

In the definition of `BinTree.mirror`, there are two recursive calls:

`def BinTree.mirror : BinTree α → BinTree α
| .leaf => .leaf
| .branch l x r => .branch (mirror r) x (mirror l)`

`BinTree.mirror`의 정의에서 두 개의 재귀 호출이 있습니다.

Just as imperative languages would typically use a while loop for functions like `reverse` and `sum`, they would typically use recursive functions for this kind of traversal.
This function cannot be straightforwardly rewritten to be tail recursive using accumulator-passing style, at least not using the techniques presented in this book.

Typically, if more than one recursive call is required for each recursive step, then it will be difficult to use accumulator-passing style.
This difficulty is similar to the difficulty of rewriting a recursive function to use a loop and an explicit data structure, with the added complication of convincing Lean that the function terminates.
However, as in `BinTree.mirror`, multiple recursive calls often indicate a data structure that has a constructor with multiple recursive occurrences of itself.
In these cases, the depth of the structure is often logarithmic with respect to its overall size, which makes the tradeoff between stack and heap less stark.
There are systematic techniques for making these functions tail-recursive, such as using *continuation-passing style* and *defunctionalization*, but they are outside the scope of this book.

명령형 언어가 `reverse`와 `sum` 같은 함수에 일반적으로 while 루프를 사용하는 것처럼, 이런 종류의 순회에는 일반적으로 재귀 함수를 사용합니다.
이 함수는 누적자 전달 스타일을 사용하여 직접적으로 꼬리 재귀로 다시 작성될 수 없으며, 적어도 이 책에서 제시한 기술을 사용하여는 그렇습니다.

일반적으로, 각 재귀 단계에서 둘 이상의 재귀 호출이 필요하면 누적자 전달 스타일을 사용하기 어려울 것입니다.
이 어려움은 재귀 함수를 루프와 명시적 데이터 구조를 사용하도록 다시 작성하는 어려움과 유사하며, 함수가 종료된다는 것을 Lean에 확신시켜야 한다는 추가적인 복잡성이 있습니다.
하지만 `BinTree.mirror`에서와 같이, 여러 개의 재귀 호출은 종종 자신을 여러 번 재귀적으로 포함하는 생성자를 가진 데이터 구조를 나타냅니다.
이러한 경우에, 구조의 깊이는 전체 크기에 대해 종종 로그적이며, 이는 스택과 힙 간의 트레이드오프를 덜 극단적으로 만듭니다.
*continuation-passing style*과 *defunctionalization*을 사용하는 것과 같은 이러한 함수들을 꼬리 재귀로 만드는 체계적인 기술들이 있지만, 이는 이 책의 범위를 벗어납니다.

## 8.1.4. Exercises

Translate each of the following non-tail-recursive functions into accumulator-passing tail-recursive functions:

`def NonTail.length : List α → Nat
| [] => 0
| _ :: xs => NonTail.length xs + 1``def NonTail.factorial : Nat → Nat
| 0 => 1
| n + 1 => factorial n * (n + 1)`

다음의 각 non-tail-recursive 함수를 누적자 전달 꼬리 재귀 함수로 변환합니다.

The translation of `NonTail.filter` should result in a program that takes constant stack space through tail recursion, and time linear in the length of the input list.
A constant factor overhead is acceptable relative to the original:

`def NonTail.filter (p : α → Bool) : List α → List α
| [] => []
| x :: xs =>
if p x then
x :: filter p xs
else
filter p xs`

`NonTail.filter`의 변환은 꼬리 재귀를 통해 상수 스택 공간을 취하는 프로그램과 입력 리스트의 길이에 대해 선형 시간을 생성해야 합니다.
상수 계수 오버헤드는 원본에 상대적으로 허용됩니다:

