---
title: "2.1. 프로그램 실행하기"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Lean 프로그램을 실행하고 IO 액션의 동작 원리를 이해합니다"
---

# 2.1. Running a Program

The simplest way to run a Lean program is to use the `--run` option to the Lean executable.
Create a file called `Hello.lean` and enter the following contents:

Lean 프로그램을 실행하는 가장 간단한 방법은 Lean 실행 파일에 `--run` 옵션을 사용하는 것입니다.
`Hello.lean`이라는 파일을 만들고 다음 내용을 입력하세요:

```lean
def main : IO Unit := IO.println "Hello, world!"
```

Then, from the command line, run:

그다음, 명령줄에서 다음을 실행하세요:

```bash
$ lean --run Hello.lean
```

The program displays `Hello, world!` and exits.

프로그램은 `Hello, world!`를 표시하고 종료합니다.

## 2.1.1. Anatomy of a Greeting

When Lean is invoked with the `--run` option, it invokes the program's `main` definition.
In programs that do not take command-line arguments, `main` should have type `IO Unit`.
This means that `main` is not a function, because there are no arrows (`→`) in its type.
Instead of being a function that has side effects, `main` consists of a description of effects to be carried out.

Lean이 `--run` 옵션으로 호출되면, 프로그램의 `main` 정의를 호출합니다.
명령줄 인수를 받지 않는 프로그램에서, `main`은 `IO Unit` 타입을 가져야 합니다.
즉, `main`이 함수가 아니라는 것입니다. 왜냐하면 타입에 화살표(`→`)가 없기 때문입니다.
`main`은 부작용을 가진 함수가 아니라, 수행할 효과에 대한 설명으로 구성됩니다.

As discussed in [the preceding chapter](../ch01/), `Unit` is the simplest inductive type.
It has a single constructor called `unit` that takes no arguments.
Languages in the C tradition have a notion of a `void` function that does not return any value at all.
In Lean, all functions take an argument and return a value, and the lack of interesting arguments or return values can be signaled by using the `Unit` type instead.
If `Bool` represents a single bit of information, `Unit` represents zero bits of information.

[이전 장](../ch01/)에서 논의했듯이, `Unit`은 가장 간단한 귀납형(inductive type)입니다.
인수를 받지 않는 `unit`이라는 단일 생성자를 가지고 있습니다.
C 계열의 언어들은 값을 반환하지 않는 `void` 함수의 개념을 가지고 있습니다.
Lean에서는 모든 함수가 인수를 받고 값을 반환하며, 의미 있는 인수나 반환값이 없다는 것을 `Unit` 타입을 사용하여 나타낼 수 있습니다.
`Bool`이 1비트의 정보를 나타낸다면, `Unit`은 0비트의 정보를 나타냅니다.

`IO α` is the type of a program that, when executed, will either throw an exception or return a value of type `α`.
During execution, this program may have side effects.
These programs are referred to as `IO` *actions*.
Lean distinguishes between *evaluation* of expressions, which strictly adheres to the mathematical model of substitution of values for variables and reduction of sub-expressions without side effects, and *execution* of `IO` actions, which rely on an external system to interact with the world.
`IO.println` is a function from strings to `IO` actions that, when executed, write the given string to standard output.
Because this action doesn't read any interesting information from the environment in the process of emitting the string, `IO.println` has type `String → IO Unit`.
If it did return something interesting, then that would be indicated by the `IO` action having a type other than `Unit`.

`IO α`는 실행되었을 때 예외를 발생시키거나 타입 `α`의 값을 반환하는 프로그램의 타입입니다.
실행 중에 이 프로그램은 부작용을 가질 수 있습니다.
이러한 프로그램들은 `IO` *액션(action)*라고 합니다.
Lean은 식의 *평가(evaluation)*와 `IO` 액션의 *실행(execution)* 사이를 구분합니다. 전자는 변수에 값을 대입하고 부작용 없이 부분식을 축약하는 수학적 모델을 엄격히 따르는 반면, 후자는 외부 시스템에 의존하여 세계와 상호작용합니다.
`IO.println`은 문자열에서 `IO` 액션으로의 함수로, 실행되면 주어진 문자열을 표준 출력에 기록합니다.
이 액션은 문자열을 내보내는 과정에서 환경으로부터 의미 있는 정보를 읽지 않기 때문에, `IO.println`은 `String → IO Unit` 타입을 가집니다.
만약 의미 있는 것을 반환했다면, `IO` 액션이 `Unit`이 아닌 다른 타입을 가지고 있을 것입니다.

## 2.1.2. Functional Programming vs Effects

Lean's model of computation is based on the evaluation of mathematical expressions, in which variables are given exactly one value that does not change over time.
The result of evaluating an expression does not change, and evaluating the same expression again will always yield the same result.

Lean의 계산 모델은 수학 식의 평가에 기반하며, 변수에는 시간이 지나도 변하지 않는 정확히 하나의 값이 주어집니다.
식을 평가한 결과는 변하지 않으며, 같은 식을 다시 평가하면 항상 같은 결과를 얻게 됩니다.

On the other hand, useful programs must interact with the world.
A program that performs neither input nor output can't ask a user for data, create files on disk, or open network connections.
Lean is written in itself, and the Lean compiler certainly reads files, creates files, and interacts with text editors.
How can a language in which the same expression always yields the same result support programs that read files from disk, when the contents of these files might change over time?

반면 유용한 프로그램은 세계와 상호작용해야 합니다.
입출력을 수행하지 않는 프로그램은 사용자에게 데이터를 요청하거나, 디스크에 파일을 만들거나, 네트워크 연결을 열 수 없습니다.
Lean은 자기 자신으로 작성되었으며, Lean 컴파일러는 확실히 파일을 읽고, 파일을 만들고, 텍스트 편집기와 상호작용합니다.
같은 식이 항상 같은 결과를 낳는 언어가 어떻게 시간이 지남에 따라 내용이 변할 수 있는 디스크의 파일을 읽는 프로그램을 지원할 수 있을까요?

This apparent contradiction can be resolved by thinking a bit differently about side effects.
Imagine a café that sells coffee and sandwiches.
This café has two employees: a cook who fulfills orders, and a worker at the counter who interacts with customers and places order slips.
The cook is a surly person, who really prefers not to have any contact with the world outside, but who is very good at consistently delivering the food and drinks that the café is known for.
In order to do this, however, the cook needs peace and quiet, and can't be disturbed with conversation.
The counter worker is friendly, but completely incompetent in the kitchen.
Customers interact with the counter worker, who delegates all actual cooking to the cook.
If the cook has a question for a customer, such as clarifying an allergy, they send a little note to the counter worker, who interacts with the customer and passes a note back to the cook with the result.

이 명백한 모순은 부작용에 대해 조금 다르게 생각함으로써 해결할 수 있습니다.
커피와 샌드위치를 파는 카페를 상상해보세요.
이 카페에는 두 명의 직원이 있습니다: 주문을 받아 음식을 만드는 요리사와 고객과 상호작용하며 주문서를 전달하는 카운터 직원입니다.
요리사는 외부 세계와의 접촉을 정말 좋아하지 않는 불평이 많은 사람이지만, 카페가 유명한 음식과 음료를 일관되게 제공하는 데 매우 뛰어납니다.
하지만 이를 위해서는 요리사가 조용한 환경이 필요하며, 대화로 방해받을 수 없습니다.
카운터 직원은 친절하지만 주방에서는 완전히 무능합니다.
고객들은 카운터 직원과 상호작용하며, 카운터 직원은 모든 실제 요리를 요리사에게 위임합니다.
요리사가 고객에게 알레르기를 확인하는 것처럼 질문이 있으면, 요리사는 작은 메모를 카운터 직원에게 보내고, 카운터 직원은 고객과 상호작용한 후 결과를 메모로 다시 요리사에게 전달합니다.

In this analogy, the cook is the Lean language.
When provided with an order, the cook faithfully and consistently delivers what is requested.
The counter worker is the surrounding run-time system that interacts with the world and can accept payments, dispense food, and have conversations with customers.
Working together, the two employees serve all the functions of the restaurant, but their responsibilities are divided, with each performing the tasks that they're best at.
Just as keeping customers away allows the cook to focus on making truly excellent coffee and sandwiches, Lean's lack of side effects allows programs to be used as part of formal mathematical proofs.
It also helps programmers understand the parts of the program in isolation from each other, because there are no hidden state changes that create subtle coupling between components.
The cook's notes represent `IO` actions that are produced by evaluating Lean expressions, and the counter worker's replies are the values that are passed back from effects.

이 비유에서 요리사는 Lean 언어입니다.
주문이 주어지면, 요리사는 요청된 것을 충실하게 그리고 일관되게 제공합니다.
카운터 직원은 세계와 상호작용하며 결제를 받고, 음식을 제공하고, 고객과 대화할 수 있는 주변 실행 시스템(runtime system)입니다.
함께 일함으로써, 두 직원은 레스토랑의 모든 기능을 수행하지만, 책임이 나뉘어져 각각 자신이 잘하는 작업을 수행합니다.
고객을 멀리 유지함으로써 요리사가 정말 훌륭한 커피와 샌드위치를 만드는 데 집중할 수 있도록 하는 것처럼, Lean의 부작용 부재는 프로그램이 형식적인 수학 증명의 일부로 사용될 수 있게 합니다.
또한 프로그래머가 프로그램의 각 부분을 서로 분리하여 이해하는 데 도움이 됩니다. 왜냐하면 컴포넌트 간에 미묘한 결합을 만드는 숨겨진 상태 변화가 없기 때문입니다.
요리사의 메모는 Lean 식을 평가하여 생성되는 `IO` 액션을 나타내며, 카운터 직원의 답장은 효과로부터 다시 전달되는 값입니다.

This model of side effects is quite similar to how the overall aggregate of the Lean language, its compiler, and its run-time system (RTS) work.
Primitives in the run-time system, written in C, implement all the basic effects.
When running a program, the RTS invokes the `main` action, which returns new `IO` actions to the RTS for execution.
The RTS executes these actions, delegating to the user's Lean code to carry out computations.
From the internal perspective of Lean, programs are free of side effects, and `IO` actions are just descriptions of tasks to be carried out.
From the external perspective of the program's user, there is a layer of side effects that create an interface to the program's core logic.

이 부작용 모델은 Lean 언어, 컴파일러, 그리고 실행 시스템(RTS)의 전체적인 작동 방식과 매우 유사합니다.
C로 작성된 실행 시스템의 원시 함수들이 모든 기본 효과를 구현합니다.
프로그램을 실행할 때, RTS는 `main` 액션을 호출하고, 이는 실행할 새로운 `IO` 액션을 RTS에 반환합니다.
RTS는 이 액션들을 실행하며, 계산을 수행하기 위해 사용자의 Lean 코드에 위임합니다.
Lean의 내부 관점에서, 프로그램은 부작용이 없으며, `IO` 액션은 수행할 작업에 대한 설명일 뿐입니다.
프로그램 사용자의 외부 관점에서는, 프로그램의 핵심 논리로의 인터페이스를 만드는 부작용의 계층이 있습니다.

## 2.1.3. Real-World Functional Programming

The other useful way to think about side effects in Lean is by considering `IO` actions to be functions that take the entire world as an argument and return a value paired with a new world.
In this case, reading a line of text from standard input *is* a pure function, because a different world is provided as an argument each time.
Writing a line of text to standard output is a pure function, because the world that the function returns is different from the one that it began with.
Programs do need to be careful to never re-use the world, nor to fail to return a new world—this would amount to time travel or the end of the world, after all.
Careful abstraction boundaries can make this style of programming safe.
If every primitive `IO` action accepts one world and returns a new one, and they can only be combined with tools that preserve this invariant, then the problem cannot occur.

Lean에서 부작용을 생각하는 또 다른 유용한 방법은 `IO` 액션을 전체 세계를 인수로 받아 새로운 세계와 쌍을 이룬 값을 반환하는 함수로 간주하는 것입니다.
이 경우, 표준 입력에서 한 줄의 텍스트를 읽는 것은 *순수 함수*입니다. 왜냐하면 매번 다른 세계가 인수로 제공되기 때문입니다.
표준 출력으로 한 줄의 텍스트를 쓰는 것은 순수 함수입니다. 왜냐하면 함수가 반환하는 세계는 시작한 세계와 다르기 때문입니다.
프로그램은 세계를 다시 사용하거나 새로운 세계를 반환하지 않도록 주의해야 합니다. 결국 이는 시간 여행이나 세계의 종말과 같기 때문입니다.
신중한 추상화 경계는 이 스타일의 프로그래밍을 안전하게 만들 수 있습니다.
모든 원시 `IO` 액션이 하나의 세계를 받아 새로운 하나를 반환하고, 이 불변성을 보존하는 도구로만 결합될 수 있다면, 문제는 발생할 수 없습니다.

This model cannot be implemented.
After all, the entire universe cannot be turned into a Lean value and placed into memory.
However, it is possible to implement a variation of this model with an abstract token that stands for the world.
When the program is started, it is provided with a world token.
This token is then passed on to the IO primitives, and their returned tokens are similarly passed to the next step.
At the end of the program, the token is returned to the operating system.

이 모델은 구현될 수 없습니다.
결국 전체 우주를 Lean 값으로 변환하여 메모리에 넣을 수는 없기 때문입니다.
그러나 세계를 나타내는 추상 토큰으로 이 모델의 변형을 구현할 수 있습니다.
프로그램이 시작되면, 세계 토큰이 제공됩니다.
이 토큰은 IO 원시 함수에 전달되고, 반환된 토큰은 마찬가지로 다음 단계로 전달됩니다.
프로그램이 끝날 때, 토큰은 운영 체제로 반환됩니다.

This model of side effects is a good description of how `IO` actions as descriptions of tasks to be carried out by the RTS are represented internally in Lean.
The actual functions that transform the real world are behind an abstraction barrier.
But real programs typically consist of a sequence of effects, rather than just one.
To enable programs to use multiple effects, there is a sub-language of Lean called `do` notation that allows these primitive `IO` actions to be safely composed into a larger, useful program.

이 부작용 모델은 RTS가 수행할 작업의 설명으로서의 `IO` 액션이 Lean 내부에서 어떻게 표현되는지를 잘 설명합니다.
실제 세계를 변환하는 실제 함수는 추상화 장벽 뒤에 있습니다.
그러나 실제 프로그램은 일반적으로 단일 효과가 아니라 일련의 효과로 구성됩니다.
프로그램이 여러 효과를 사용할 수 있도록 하기 위해, 이 원시 `IO` 액션을 더 크고 유용한 프로그램으로 안전하게 합성할 수 있는 `do` 표기법이라는 Lean의 부언어(sub-language)가 있습니다.

## 2.1.4. Combining `IO` Actions

Most useful programs accept input in addition to producing output.
Furthermore, they may take decisions based on input, using the input data as part of a computation.
The following program, called `HelloName.lean`, asks the user for their name and then greets them:

대부분의 유용한 프로그램은 출력을 생성하는 것 외에도 입력을 받습니다.
나아가, 입력을 기반으로 결정을 내릴 수 있으며, 입력 데이터를 계산의 일부로 사용할 수 있습니다.
`HelloName.lean`이라는 다음 프로그램은 사용자에게 이름을 묻고 인사합니다:

```lean
def main : IO Unit := do
  let stdin ← IO.getStdin
  let stdout ← IO.getStdout
  stdout.putStrLn "How would you like to be addressed?"
  let input ← stdin.getLine
  let name := input.dropRightWhile Char.isWhitespace
  stdout.putStrLn s!"Hello, {name}!"
```

In this program, the `main` action consists of a `do` block.
This block contains a sequence of *statements*, which can be both local variables (introduced using `let`) and actions that are to be executed.
Just as SQL can be thought of as a special-purpose language for interacting with databases, the `do` syntax can be thought of as a special-purpose sub-language within Lean that is dedicated to modeling imperative programs.
`IO` actions that are built with a `do` block are executed by executing the statements in order.

이 프로그램에서 `main` 액션은 `do` 블록으로 구성됩니다.
이 블록은 로컬 변수(let을 사용하여 도입됨)와 실행할 액션이 모두 될 수 있는 *명령문(statements)*의 시퀀스를 포함합니다.
SQL을 데이터베이스와 상호작용하기 위한 특수 목적 언어로 생각할 수 있는 것처럼, `do` 문법을 명령형 프로그램을 모델링하기 위해 헌신하는 Lean 내의 특수 목적 부언어로 생각할 수 있습니다.
`do` 블록으로 빌드된 `IO` 액션은 명령문을 순서대로 실행하여 실행됩니다.

This program can be run in the same manner as the prior program:

```bash
$ lean --run HelloName.lean
```

If the user responds with `David`, a session of interaction with the program reads:

이 프로그램은 이전 프로그램과 같은 방식으로 실행할 수 있습니다.

사용자가 `David`로 응답하면, 프로그램과의 상호작용 세션은 다음과 같이 읽습니다:

```
How would you like to be addressed?
David
Hello, David!
```

The type signature line is just like the one for `Hello.lean`:

```lean
def main : IO Unit := do
```

The only difference is that it ends with the keyword `do`, which initiates a sequence of commands.
Each indented line following the keyword `do` is part of the same sequence of commands.

타입 시그니처 라인은 `Hello.lean`의 것과 같습니다.

유일한 차이점은 명령문의 시퀀스를 시작하는 키워드 `do`로 끝난다는 것입니다.
키워드 `do` 다음의 각 들여쓰기된 라인은 같은 명령문 시퀀스의 일부입니다.

The first two lines, which read:

```lean
let stdin ← IO.getStdin
let stdout ← IO.getStdout
```

retrieve the `stdin` and `stdout` handles by executing the library actions `IO.getStdin` and `IO.getStdout`, respectively.
In a `do` block, `let` has a slightly different meaning than in an ordinary expression.
Ordinarily, the local definition in a `let` can be used in just one expression, which immediately follows the local definition.
In a `do` block, local bindings introduced by `let` are available in all statements in the remainder of the `do` block, rather than just the next one.
Additionally, `let` typically connects the name being defined to its definition using `:=`, while some `let` bindings in `do` use a left arrow (`←` or `<-`) instead.
Using an arrow means that the value of the expression is an `IO` action that should be executed, with the result of the action saved in the local variable.
In other words, if the expression to the right of the arrow has type `IO α`, then the variable has type `α` in the remainder of the `do` block.
`IO.getStdin` and `IO.getStdout` are `IO` actions in order to allow `stdin` and `stdout` to be locally overridden in a program, which can be convenient.
If they were global variables as in C, then there would be no meaningful way to override them, but `IO` actions can return different values each time they are executed.

처음 두 줄은 다음과 같습니다:

```lean
let stdin ← IO.getStdin
let stdout ← IO.getStdout
```

각각 라이브러리 액션 `IO.getStdin`과 `IO.getStdout`을 실행하여 `stdin`과 `stdout` 핸들을 검색합니다.
`do` 블록에서 `let`은 일반 식에서와 약간 다른 의미를 가집니다.
일반적으로, `let`의 로컬 정의는 로컬 정의 바로 다음에 오는 하나의 식에서만 사용할 수 있습니다.
`do` 블록에서, `let`으로 도입된 로컬 바인딩은 다음 명령문이 아니라 `do` 블록의 나머지 모든 명령문에서 사용할 수 있습니다.
또한 `let`은 일반적으로 정의되는 이름을 `:=`을 사용하여 정의에 연결하지만, `do`의 일부 `let` 바인딩은 대신 왼쪽 화살표(`←` 또는 `<-`)를 사용합니다.
화살표를 사용하면 식의 값이 실행해야 할 `IO` 액션이며, 액션의 결과가 로컬 변수에 저장됩니다.
즉, 화살표의 오른쪽 식이 `IO α` 타입을 가지면, 변수는 `do` 블록의 나머지에서 `α` 타입을 가집니다.
`IO.getStdin`과 `IO.getStdout`은 `IO` 액션이므로 프로그램에서 `stdin`과 `stdout`을 로컬로 오버라이드할 수 있으며, 이는 편리할 수 있습니다.
C에서처럼 전역 변수였다면, 이를 오버라이드할 의미 있는 방법이 없을 것입니다. 하지만 `IO` 액션은 실행될 때마다 다른 값을 반환할 수 있습니다.

The next part of the `do` block is responsible for asking the user for their name:

```lean
stdout.putStrLn "How would you like to be addressed?"
let input ← stdin.getLine
let name := input.dropRightWhile Char.isWhitespace
```

The first line writes the question to `stdout`, the second line requests input from `stdin`, and the third line removes the trailing newline (plus any other trailing whitespace) from the input line.
The definition of `name` uses `:=`, rather than `←`, because `String.dropRightWhile` is an ordinary function on strings, rather than an `IO` action.

`do` 블록의 다음 부분은 사용자에게 이름을 묻는 역할을 합니다.

첫 번째 줄은 `stdout`에 질문을 씁니다. 두 번째 줄은 `stdin`에서 입력을 요청합니다. 세 번째 줄은 입력 라인에서 후행 줄 바꿈(및 다른 모든 후행 공백)을 제거합니다.
`name`의 정의는 `←`가 아니라 `:=`을 사용합니다. `String.dropRightWhile`은 `IO` 액션이 아니라 문자열에 대한 일반 함수이기 때문입니다.

Finally, the last line in the program is:

```lean
stdout.putStrLn s!"Hello, {name}!"
```

It uses [string interpolation](../ch01/) to insert the provided name into a greeting string, writing the result to `stdout`.

마지막으로, 프로그램의 마지막 줄은 다음과 같습니다:

```lean
stdout.putStrLn s!"Hello, {name}!"
```

[문자열 보간](../ch01/)을 사용하여 제공된 이름을 인사 문자열에 삽입하고 결과를 `stdout`에 씁니다.
