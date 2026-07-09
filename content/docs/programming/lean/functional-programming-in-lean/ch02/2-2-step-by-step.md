---
title: "단계별로 살펴보기"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Lean 프로그램이 컴파일되고 실행되는 과정을 단계별로 살펴보기"
---

# Step By Step

## 2.2.1. Standard IO

To execute a `let` statement that uses a `←`, start by evaluating the expression to the right of the arrow (in this case, `IO.getStdin`).
Because this expression is just a variable, its value is looked up.
The resulting value is a built-in primitive `IO` action.
The next step is to execute this `IO` action, resulting in a value that represents the standard input stream, which has type `IO.FS.Stream`.
Standard input is then associated with the name to the left of the arrow (here `stdin`) for the remainder of the `do` block.

`←`를 사용하는 `let` 명령문을 실행하려면, 화살표의 오른쪽에 있는 식(이 경우 `IO.getStdin`)을 평가하는 것으로 시작합니다.
이 식이 단지 변수이므로, 그 값을 조회합니다.
결과 값은 내장된 원시 `IO` 액션입니다.
다음 단계는 이 `IO` 액션을 실행하는 것이며, 표준 입력 스트림을 나타내는 값을 생성하며, 이는 `IO.FS.Stream` 타입을 가집니다.
표준 입력은 `do` 블록의 나머지에서 화살표의 왼쪽에 있는 이름(여기서는 `stdin`)과 연결됩니다.

Executing the second line, `let stdout ← IO.getStdout`, proceeds similarly.
First, the expression `IO.getStdout` is evaluated, yielding an `IO` action that will return the standard output.
Next, this action is executed, actually returning the standard output.
Finally, this value is associated with the name `stdout` for the remainder of the `do` block.

두 번째 줄인 `let stdout ← IO.getStdout`을 실행하는 것도 비슷하게 진행됩니다.
먼저 식 `IO.getStdout`이 평가되어 표준 출력을 반환할 `IO` 액션을 생성합니다.
다음으로, 이 액션이 실행되어 실제로 표준 출력을 반환합니다.
마지막으로, 이 값은 `do` 블록의 나머지에서 이름 `stdout`과 연결됩니다.

## 2.2.2. Asking a Question

Now that `stdin` and `stdout` have been found, the remainder of the block consists of a question and an answer:

이제 `stdin`과 `stdout`을 찾았으므로, 블록의 나머지는 질문과 답으로 구성됩니다:

```lean
stdout.putStrLn "How would you like to be addressed?"
let input ← stdin.getLine
let name := input.dropRightWhile Char.isWhitespace
stdout.putStrLn s!"Hello, {name}!"
```

The first statement in the block, `stdout.putStrLn "How would you like to be addressed?"`, consists of an expression.
To execute an expression, it is first evaluated.
In this case, `IO.FS.Stream.putStrLn` has type `IO.FS.Stream → String → IO Unit`.
This means that it is a function that accepts a stream and a string, returning an `IO` action.
The expression uses [accessor notation](../ch01/) for a function call.
This function is applied to two arguments: the standard output stream and a string.
The value of the expression is an `IO` action that will write the string and a newline character to the output stream.
Having found this value, the next step is to execute it, which causes the string and newline to actually be written to `stdout`.
Statements that consist only of expressions do not introduce any new variables.

블록의 첫 번째 명령문인 `stdout.putStrLn "How would you like to be addressed?"`는 식으로 구성됩니다.
식을 실행하려면 먼저 평가합니다.
이 경우 `IO.FS.Stream.putStrLn`은 `IO.FS.Stream → String → IO Unit` 타입을 가집니다.
이는 스트림과 문자열을 받아 `IO` 액션을 반환하는 함수입니다.
식은 함수 호출을 위해 [접근자 표기법](../ch01/)을 사용합니다.
이 함수는 표준 출력 스트림과 문자열이라는 두 개의 인수에 적용됩니다.
식의 값은 문자열과 줄 바꿈 문자를 출력 스트림에 쓸 `IO` 액션입니다.
이 값을 찾은 후 다음 단계는 이를 실행하는 것이며, 이는 문자열과 줄 바꿈이 실제로 `stdout`에 쓰여지게 합니다.
식으로만 구성된 명령문은 새로운 변수를 도입하지 않습니다.

The next statement in the block is `let input ← stdin.getLine`.
`IO.FS.Stream.getLine` has type `IO.FS.Stream → IO String`, which means that it is a function from a stream to an `IO` action that will return a string.
Once again, this is an example of accessor notation.
This `IO` action is executed, and the program waits until the user has typed a complete line of input.
Assume the user writes “`David`”.
The resulting line (`”David\n”`) is associated with `input`, where the escape sequence `\n` denotes the newline character.

블록의 다음 명령문은 `let input ← stdin.getLine`입니다.
`IO.FS.Stream.getLine`은 `IO.FS.Stream → IO String` 타입을 가지며, 이는 스트림에서 문자열을 반환할 `IO` 액션으로의 함수입니다.
다시 한 번, 이는 접근자 표기법의 예입니다.
이 `IO` 액션이 실행되고, 프로그램은 사용자가 완전한 입력 라인을 입력할 때까지 기다립니다.
사용자가 “`David`”를 입력한다고 가정합니다.
결과 라인(`”David\n”`)은 `input`과 연결되며, 여기서 이스케이프 시퀀스 `\n`은 줄 바꿈 문자를 나타냅니다.

```lean
let name := input.dropRightWhile Char.isWhitespace
stdout.putStrLn s!"Hello, {name}!"
```

The next line, `let name := input.dropRightWhile Char.isWhitespace`, is a `let` statement.
Unlike the other `let` statements in this program, it uses `:=` instead of `←`.
This means that the expression will be evaluated, but the resulting value need not be an `IO` action and will not be executed.
In this case, `String.dropRightWhile` takes a string and a predicate over characters and returns a new string from which all the characters at the end of the string that satisfy the predicate have been removed.
For example,

다음 줄인 `let name := input.dropRightWhile Char.isWhitespace`는 `let` 명령문입니다.
이 프로그램의 다른 `let` 명령문과 달리 `←` 대신 `:=`을 사용합니다.
즉, 식이 평가되지만 결과 값이 `IO` 액션일 필요가 없으며 실행되지 않음입니다.
이 경우 `String.dropRightWhile`은 문자열과 문자에 대한 술어를 받아 문자열의 끝에서 술어를 만족하는 모든 문자가 제거된 새 문자열을 반환합니다.
예를 들어,

```lean
#eval "Hello!!!".dropRightWhile (· == '!')
```

yields

```
"Hello"
```

and

```lean
#eval "Hello... ".dropRightWhile (fun c => not (c.isAlphanum))
```

yields

```
"Hello"
```

in which all non-alphanumeric characters have been removed from the right side of the string.
In the current line of the program, whitespace characters (including the newline) are removed from the right side of the input string, resulting in `"David"`, which is associated with `name` for the remainder of the block.

여기서 문자열의 오른쪽에서 모든 영숫자가 아닌 문자가 제거되었습니다.
프로그램의 현재 라인에서 입력 문자열의 오른쪽에서 공백 문자(줄 바꿈 포함)가 제거되어 `"David"`가 되며, 이는 블록의 나머지에서 `name`과 연결됩니다.

## 2.2.3. Greeting the User

All that remains to be executed in the `do` block is a single statement:

```lean
stdout.putStrLn s!"Hello, {name}!"
```

The string argument to `putStrLn` is constructed via string interpolation, yielding the string `"Hello, David!"`.
Because this statement is an expression, it is evaluated to yield an `IO` action that will print this string with a newline to standard output.
Once the expression has been evaluated, the resulting `IO` action is executed, resulting in the greeting.

`do` 블록에서 실행되어야 할 남은 것은 단 하나의 명령문입니다.

`putStrLn`의 문자열 인수는 문자열 보간을 통해 구성되어 문자열 `"Hello, David!"`를 생성합니다.
이 명령문은 식이므로, 이 문자열을 표준 출력으로 줄 바꿈과 함께 인쇄할 `IO` 액션을 생성하도록 평가됩니다.
식이 평가되면, 결과 `IO` 액션이 실행되어 인사말을 생성합니다.

## 2.2.4. `IO` Actions as Values

In the above description, it can be difficult to see why the distinction between evaluating expressions and executing `IO` actions is necessary.
After all, each action is executed immediately after it is produced.
Why not simply carry out the effects during evaluation, as is done in other languages?

The answer is twofold.
First off, separating evaluation from execution means that programs must be explicit about which functions can have side effects.
Because the parts of the program that do not have effects are much more amenable to mathematical reasoning, whether in the heads of programmers or using Lean's facilities for formal proof, this separation can make it easier to avoid bugs.
Secondly, not all `IO` actions need be executed at the time that they come into existence.
The ability to mention an action without carrying it out allows ordinary functions to be used as control structures.

위의 설명에서 식을 평가하는 것과 `IO` 액션을 실행하는 것 사이의 구분이 필요한 이유를 보기가 어려울 수 있습니다.
결국 각 액션은 생성된 직후에 실행됩니다.
다른 언어처럼 평가 중에 효과를 수행하지 않는 이유는 무엇일까요?

답은 두 가지입니다.
먼저 평가를 실행과 분리한다는 것은 프로그램이 어떤 함수가 부작용을 가질 수 있는지에 대해 명시적이어야 함을 의미합니다.
부작용이 없는 프로그램의 부분은 프로그래머의 머릿속이든 Lean의 형식 증명 도구를 사용하든 훨씬 더 수학적 추론에 적합하므로, 이 구분은 버그를 피하기 쉽게 만들 수 있습니다.
둘째, 모든 `IO` 액션이 존재하는 시점에 실행되어야 하는 것은 아닙니다.
액션을 언급하되 수행하지 않을 수 있는 능력은 일반적인 함수가 제어 구조로 사용될 수 있게 합니다.

For example, the function `twice` takes an `IO` action as its argument, returning a new action that will execute the argument action twice.

예를 들어, `twice` 함수는 `IO` 액션을 인수로 받아 인수 액션을 두 번 실행할 새로운 액션을 반환합니다.

```lean
def twice (action : IO Unit) : IO Unit := do
  action
  action
```

Executing

```lean
twice (IO.println "shy")
```

results in

```
shy
shy
```

being printed.
This can be generalized to a version that runs the underlying action any number of times:

이는 기본 액션을 여러 번 실행하는 버전으로 일반화될 수 있습니다:

```lean
def nTimes (action : IO Unit) : Nat → IO Unit
  | 0 => pure ()
  | n + 1 => do
    action
    nTimes action n
```

In the base case for `Nat.zero`, the result is `pure ()`.
The function `pure` creates an `IO` action that has no side effects, but returns `pure`'s argument, which in this case is the constructor for `Unit`.
As an action that does nothing and returns nothing interesting, `pure ()` is at the same time utterly boring and very useful.
In the recursive step, a `do` block is used to create an action that first executes `action` and then executes the result of the recursive call.
Executing `#eval nTimes (IO.println "Hello") 3` causes the following output:

`Nat.zero`의 기본 경우에서 결과는 `pure ()`입니다.
`pure` 함수는 부작용이 없지만 `pure`의 인수(이 경우 `Unit`의 생성자)를 반환하는 `IO` 액션을 생성합니다.
아무것도 하지 않고 의미 있는 것을 반환하지 않는 액션으로서, `pure ()`는 동시에 완전히 지루하면서도 매우 유용합니다.
재귀 단계에서는 `do` 블록을 사용하여 먼저 `action`을 실행하고 재귀 호출의 결과를 실행하는 액션을 만듭니다.
`#eval nTimes (IO.println "Hello") 3`를 실행하면 다음과 같은 출력이 발생합니다:

```
Hello
Hello
Hello
```

In addition to using functions as control structures, the fact that `IO` actions are first-class values means that they can be saved in data structures for later execution.
For instance, the function `countdown` takes a `Nat` and returns a list of unexecuted `IO` actions, one for each `Nat`:

함수를 제어 구조로 사용하는 것 외에도, `IO` 액션이 1급 값이라는 사실은 나중에 실행하기 위해 데이터 구조에 저장될 수 있음을 의미합니다.
예를 들어, `countdown` 함수는 `Nat`을 받아 각 `Nat`마다 하나씩 실행되지 않은 `IO` 액션의 리스트를 반환합니다:

```lean
def countdown : Nat → List (IO Unit)
  | 0 => [IO.println "Blast off!"]
  | n + 1 => IO.println s!"{n + 1}" :: countdown n
```

This function has no side effects, and does not print anything.
For example, it can be applied to an argument, and the length of the resulting list of actions can be checked:

```lean
def from5 : List (IO Unit) := countdown 5
```

This list contains six elements (one for each number, plus a `"Blast off!"` action for zero):

이 함수는 부작용이 없으며 아무것도 인쇄하지 않습니다.
예를 들어, 인수에 적용될 수 있으며, 결과 액션 리스트의 길이를 확인할 수 있습니다.

이 리스트는 여섯 개의 요소(각 숫자마다 하나씩, 그리고 0에 대한 `"Blast off!"` 액션)를 포함합니다:

```lean
#eval from5.length
```

```
6
```

The function `runActions` takes a list of actions and constructs a single action that runs them all in order:

```lean
def runActions : List (IO Unit) → IO Unit
  | [] => pure ()
  | act :: actions => do
    act
    runActions actions
```

Its structure is essentially the same as that of `nTimes`, except instead of having one action that is executed for each `Nat.succ`, the action under each `List.cons` is to be executed.
Similarly, `runActions` does not itself run the actions.
It creates a new action that will run them, and that action must be placed in a position where it will be executed as a part of `main`:

`runActions` 함수는 액션의 리스트를 받아 그 모든 액션을 순서대로 실행하는 단일 액션을 구성합니다.

그 구조는 본질적으로 `nTimes`의 구조와 같습니다. 단, 각 `Nat.succ`에 대해 실행되는 하나의 액션을 가지는 대신 각 `List.cons` 아래의 액션이 실행됩니다.
마찬가지로, `runActions`는 자체적으로 액션을 실행하지 않습니다.
그것들을 실행할 새로운 액션을 만들고, 그 액션은 `main`의 일부로 실행될 위치에 배치되어야 합니다:

```lean
def main : IO Unit := runActions from5
```

Running this program results in the following output:

```
5
4
3
2
1
Blast off!
```

What happens when this program is run?
The first step is to evaluate `main`. That occurs as follows:

The resulting `IO` action is a `do` block.
Each step of the `do` block is then executed, one at a time, yielding the expected output.
The final step, `pure ()`, does not have any effects, and it is only present because the definition of `runActions` needs a base case.

이 프로그램을 실행하면 다음과 같은 출력이 나옵니다.

이 프로그램이 실행되면 어떻게 되나요?
첫 번째 단계는 `main`을 평가하는 것입니다. 그것은 다음과 같이 발생합니다.

결과 `IO` 액션은 `do` 블록입니다.
`do` 블록의 각 단계는 한 번에 하나씩 실행되어 예상된 출력을 생성합니다.
마지막 단계인 `pure ()`는 효과가 없으며, `runActions`의 정의가 기본 경우를 필요로 하기 때문에만 존재합니다.
