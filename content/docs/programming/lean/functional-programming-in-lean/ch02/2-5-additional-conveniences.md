---
title: "추가 편의 기능"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "nested action, do 표기법의 유연한 레이아웃, #eval을 이용한 IO action 실행 등 Lean의 추가 편의 기능 소개"
---

# Additional Conveniences

## 2.5.1. Nested Actions

Many of the functions in `feline` exhibit a repetitive pattern in which an `IO` action's result is given a name, and then used immediately and only once.
For instance, in `dump`:

`feline`의 많은 함수들은 `IO` action의 결과에 이름을 부여한 후 즉시 한 번만 사용하는 반복적인 패턴을 보여줍니다.
예를 들어, `dump`에서:

```lean
partial def dump (stream : IO.FS.Stream) : IO Unit := do
  let buf ← stream.read bufsize
  if buf.isEmpty then
    pure ()
  else
    let stdout ← IO.getStdout
    stdout.write buf
    dump stream
```

the pattern occurs for `stdout`:

```lean
let stdout ← IO.getStdout
stdout.write buf
```

이 패턴은 `stdout`에서 나타납니다.

Similarly, `fileStream` contains the following snippet:

```lean
let fileExists ← filename.pathExists
if not fileExists then
```

마찬가지로, `fileStream`은 다음 코드 조각을 포함합니다.

When Lean is compiling a `do` block, expressions that consist of a left arrow immediately under parentheses are lifted to the nearest enclosing `do`, and their results are bound to a unique name.
This unique name replaces the origin of the expression.
This means that `dump` can also be written as follows:

Lean이 `do` 블록을 컴파일할 때, 괄호 바로 아래에 있는 left arrow로 구성된 표현식은 가장 가까운 `do` 블록으로 끌어올려지고, 그 결과는 고유한 이름으로 바인딩됩니다.
이 고유한 이름은 원래 표현식을 대체합니다.
이는 `dump`을 다음과 같이 작성할 수도 있다는 의미입니다:

```lean
partial def dump (stream : IO.FS.Stream) : IO Unit := do
  let buf ← stream.read bufsize
  if buf.isEmpty then
    pure ()
  else
    (← IO.getStdout).write buf
    dump stream
```

This version of `dump` avoids introducing names that are used only once, which can greatly simplify a program.
`IO` actions that Lean lifts from a nested expression context are called *nested actions*.

이 버전의 `dump`은 오직 한 번만 사용되는 이름을 도입하지 않으므로 프로그램을 크게 단순화할 수 있습니다.
Lean이 중첩된 표현식 컨텍스트에서 끌어올린 `IO` action을 *nested action*이라고 부릅니다.

It is important to remember, however, that nested actions are only a shorter notation for `IO` actions that occur in a surrounding `do` block.
The side effects that are involved in executing them still occur in the same order, and execution of side effects is not interspersed with the evaluation of expressions.
Therefore, nested actions cannot be lifted from the branches of an `if`.

그러나 nested action은 주변 `do` 블록에서 발생하는 `IO` action의 짧은 표기법일 뿐이라는 것을 기억하는 것이 중요합니다.
이들을 실행하는 데 관련된 side effect은 여전히 같은 순서로 발생하며, side effect의 실행은 표현식의 평가와 섞여 있지 않습니다.
따라서 nested action은 `if`의 분기에서 끌어올릴 수 없습니다.

For an example of where this might be confusing, consider the following helper definitions that return data after announcing to the world that they have been executed:

이것이 혼동될 수 있는 곳의 예를 들기 위해, 다음 helper 정의들을 고려해보세요. 이 함수들은 실행되었다는 것을 세상에 알린 후 데이터를 반환합니다:

```lean
def getNumA : IO Nat := do
  (← IO.getStdout).putStrLn "A"
  pure 5

def getNumB : IO Nat := do
  (← IO.getStdout).putStrLn "B"
  pure 7
```

These definitions are intended to stand in for more complicated `IO` code that might validate user input, read a database, or open a file.

이러한 정의들은 사용자 입력을 검증하거나, 데이터베이스를 읽거나, 파일을 열 수 있는 더 복잡한 `IO` 코드를 대신하기 위한 것입니다.

A program that prints `0` when number A is five, or number B otherwise, might be written as follows:

숫자 A가 5일 때 `0`을 출력하고, 그렇지 않으면 숫자 B를 출력하는 프로그램은 다음과 같이 작성될 수 있습니다:

```lean
def test : IO Unit := do
  let a : Nat := if (← getNumA) == 5 then 0 else (← getNumB)
  (← IO.getStdout).putStrLn s!"The answer is {a}"
```

This program would be equivalent to:

```lean
def test : IO Unit := do
  let x ← getNumA
  let y ← getNumB
  let a : Nat := if x == 5 then 0 else y
  (← IO.getStdout).putStrLn s!"The answer is {a}"
```

이 프로그램은 다음과 같은 의미를 갖습니다.

which runs `getNumB` regardless of whether the result of `getNumA` is equal to `5`.
To prevent this confusion, nested actions are not allowed in an `if` that is not itself a line in the `do`, and the following error message results:

이는 `getNumA`의 결과가 `5`와 같은지 여부와 관계없이 `getNumB`를 실행합니다.
이러한 혼동을 방지하기 위해, nested action은 `do`의 한 줄이 아닌 `if`에서는 허용되지 않으며, 다음과 같은 오류 메시지가 발생합니다:

```
invalid use of `(<- ...)`, must be nested inside a 'do' expression
```

## 2.5.2. Flexible Layouts for `do`

In Lean, `do` expressions are whitespace-sensitive.
Each `IO` action or local binding in the `do` is expected to start on its own line, and they should all have the same indentation.
Almost all uses of `do` should be written this way.
In some rare contexts, however, manual control over whitespace and indentation may be necessary, or it may be convenient to have multiple small actions on a single line.
In these cases, newlines can be replaced with a semicolon and indentation can be replaced with curly braces.

Lean에서 `do` 표현식은 공백(whitespace)에 민감합니다.
`do` 내의 각 `IO` action 또는 local binding은 고유한 줄에서 시작해야 하며, 모두 동일한 들여쓰기를 가져야 합니다.
거의 모든 `do` 사용은 이런 방식으로 작성되어야 합니다.
그러나 드문 경우에는 공백과 들여쓰기를 수동으로 제어해야 하거나, 여러 개의 작은 action을 한 줄에 배치하는 것이 편리할 수 있습니다.
이러한 경우에는 개행 문자를 세미콜론으로 대체할 수 있고, 들여쓰기를 중괄호로 대체할 수 있습니다.

For instance, all of the following programs are equivalent:

예를 들어, 다음의 모든 프로그램은 동등합니다:

```lean
-- This version uses only whitespace-sensitive layout
def main : IO Unit := do
  let stdin ← IO.getStdin
  let stdout ← IO.getStdout
  stdout.putStrLn "How would you like to be addressed?"
  let name := (← stdin.getLine).trim
  stdout.putStrLn s!"Hello, {name}!"
```

```lean
-- This version is as explicit as possible
def main : IO Unit := do {
  let stdin ← IO.getStdin;
  let stdout ← IO.getStdout;
  stdout.putStrLn "How would you like to be addressed?";
  let name := (← stdin.getLine).trim;
  stdout.putStrLn s!"Hello, {name}!"
}
```

```lean
-- This version uses a semicolon to put two actions on the same line
def main : IO Unit := do
  let stdin ← IO.getStdin; let stdout ← IO.getStdout
  stdout.putStrLn "How would you like to be addressed?"
  let name := (← stdin.getLine).trim
  stdout.putStrLn s!"Hello, {name}!"
```

Idiomatic Lean code uses curly braces with `do` very rarely.

관용적인 Lean 코드는 `do`와 함께 중괄호를 매우 드물게 사용합니다.

## 2.5.3. Running `IO` Actions With `#eval`

Lean's `#eval` command can be used to execute `IO` actions, rather than just evaluating them.
Normally, adding a `#eval` command to a Lean file causes Lean to evaluate the provided expression, convert the resulting value to a string, and provide that string as a tooltip and in the info window.
Rather than failing because `IO` actions can't be converted to strings, `#eval` executes them, carrying out their side effects.
If the result of execution is the `Unit` value `()`, then no result string is shown, but if it is a type that can be converted to a string, then Lean displays the resulting value.

Lean의 `#eval` 명령은 단순히 평가하는 것이 아니라 `IO` action을 실행하는 데 사용할 수 있습니다.
일반적으로 Lean 파일에 `#eval` 명령을 추가하면 Lean은 제공된 표현식을 평가하고, 그 결과 값을 문자열로 변환하여 그 문자열을 tooltip과 info window에 제공합니다.
`IO` action은 문자열로 변환될 수 없기 때문에 실패하는 대신, `#eval`은 이들을 실행하여 그들의 side effect을 수행합니다.
실행 결과가 `Unit` 값 `()`이면 결과 문자열이 표시되지 않지만, 문자열로 변환될 수 있는 타입이면 Lean은 그 결과 값을 표시합니다.

This means that, given the prior definitions of `countdown` and `runActions`,

```lean
#eval runActions (countdown 3)
```

displays

```
3
2
1
Blast off!
```

즉, `countdown`과 `runActions`의 이전 정의가 주어진 경우, 다음은

```lean
#eval runActions (countdown 3)
```

를 실행하면 다음이 표시됩니다.

```
3
2
1
Blast off!
```

This is the output produced by running the `IO` action, rather than some opaque representation of the action itself.
In other words, for `IO` actions, `#eval` both *evaluates* the provided expression and *executes* the resulting action value.

이것은 action 자체의 불투명한 표현보다는 `IO` action을 실행하여 생성된 출력입니다.
다시 말해, `IO` action의 경우, `#eval`은 제공된 표현식을 *평가*하고 그 결과로 나온 action 값을 *실행*합니다.

Quickly testing `IO` actions with `#eval` can be much more convenient that compiling and running whole programs.
However, there are some limitations.
For instance, reading from standard input simply returns empty input.
Additionally, the `IO` action is re-executed whenever Lean needs to update the diagnostic information that it provides to users, and this can happen at unpredictable times.
An action that reads and writes files, for instance, may do so unexpectedly.

`#eval`을 사용하여 `IO` action을 빠르게 테스트할 수 있는 것은 전체 프로그램을 컴파일하고 실행하는 것보다 훨씬 편리할 수 있습니다.
그러나 몇 가지 제한 사항이 있습니다.
예를 들어, 표준 입력에서 읽으면 단순히 빈 입력이 반환됩니다.
또한 Lean이 사용자에게 제공하는 진단 정보를 업데이트해야 할 때마다 `IO` action이 다시 실행되며, 이는 예측할 수 없는 시간에 발생할 수 있습니다.
예를 들어, 파일을 읽고 쓰는 action은 예기치 않게 그렇게 할 수 있습니다.
