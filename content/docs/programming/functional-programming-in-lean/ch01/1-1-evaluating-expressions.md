---
title: "Evaluating Expressions"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Evaluating Expressions"
---

# 1.1. Evaluating Expressions

The most important thing to understand as a programmer learning Lean is how evaluation works.
Evaluation is the process of finding the value of an expression, just as one does in arithmetic.
For instance, the value of `15 - 6` is `9` and the value of `2 × (3 + 1)` is `8`.
To find the value of the latter expression, `3 + 1` is first replaced by `4`, yielding `2 × 4`, which itself can be reduced to `8`.
Sometimes, mathematical expressions contain variables: the value of `x + 1` cannot be computed until we know what the value of `x` is.
In Lean, programs are first and foremost expressions, and the primary way to think about computation is as evaluating expressions to find their values.

Lean을 배우는 프로그래머로서 이해해야 할 가장 중요한 것은 평가(evaluation)가 어떻게 작동하는지입니다.
평가는 산술 연산에서와 마찬가지로 표현식의 값을 찾는 과정입니다.
예를 들어, `15 - 6`의 값은 `9`이고 `2 × (3 + 1)`의 값은 `8`입니다.
뒤의 표현식 값을 구하기 위해, `3 + 1`이 먼저 `4`로 대체되어 `2 × 4`를 얻고, 이는 `8`이 됩니다.
때때로 수학식은 변수를 포함합니다: `x + 1`의 값은 `x`의 값이 무엇인지 알 때까지 계산할 수 없습니다.
Lean에서 프로그램은 우선적으로 표현식이며, 계산에 대해 생각하는 주된 방식은 표현식을 평가해 값을 구하는 것입니다.

Most programming languages are *imperative*, where a program consists of a series of statements that should be carried out in order to find the program's result.
Programs have access to mutable memory, so the value referred to by a variable can change over time.
In addition to mutable state, programs may have other side effects, such as deleting files, making outgoing network connections,
throwing or catching exceptions, and reading data from a database.
“Side effects” is essentially a catch-all term for describing things that may happen in a program that don't follow the model of evaluating mathematical expressions.

대부분의 프로그래밍 언어는 *명령형(imperative)*이며, 프로그램은 결과를 얻기 위해 순서대로 실행되는 일련의 문(statement)으로 구성됩니다.
프로그램은 변경 가능한 메모리에 접근할 수 있으므로, 변수가 참조하는 값은 시간이 지남에 따라 변할 수 있습니다.
변경 가능한 상태 외에도, 프로그램은 파일 삭제, 아웃바운드 네트워크 연결, 예외를 던지거나 잡기, 데이터베이스에서 데이터 읽기와 같은 다른 부작용을 가질 수 있습니다.
“부작용”은 본질적으로 수학식 평가 모델을 따르지 않는 프로그램에서 일어날 수 있는 것들을 설명하는 포괄적인 용어입니다.

In Lean, however, programs work the same way as mathematical expressions.
Once given a value, variables cannot be reassigned. Evaluating an expression cannot have side effects.
If two expressions have the same value, then replacing one with the other will not cause the program to compute a different result.
This does not mean that Lean cannot be used to write `Hello, world!` to the console, but performing I/O is not a core part of the experience of using Lean in the same way.
Thus, this chapter focuses on how to evaluate expressions interactively with Lean, while the next chapter describes how to write, compile, and run the `Hello, world!` program.

하지만 Lean에서 프로그램은 수학식과 같은 방식으로 작동합니다.
값이 주어지면, 변수는 재할당될 수 없습니다. 표현식을 평가할 때 부작용이 발생할 수 없습니다.
두 표현식이 같은 값을 가지면, 하나를 다른 것으로 교체해도 프로그램의 결과는 달라지지 않습니다.
이 말이 Lean으로 `Hello, world!`를 콘솔에 출력할 수 없다는 뜻은 아니지만, I/O를 수행하는 것은 Lean에서 I/O는 핵심 관심사가 아닙니다.
따라서 이 챕터는 Lean으로 표현식을 인터랙티브하게 평가하는 방법에 초점을 맞추며, 다음 챕터에서는 `Hello, world!` 프로그램을 작성, 컴파일 및 실행하는 방법을 설명합니다.

To ask Lean to evaluate an expression, write `#eval` before it in your editor, which will then report the result back.
Typically, the result is found by putting the cursor or mouse pointer over `#eval`.
For instance,

`3#eval 1 + 2`

yields the value

```
3
```

Lean obeys the ordinary rules of precedence and associativity for
arithmetic operators. That is,

`11#eval 1 + 2 * 5`

yields the value `11` rather than `15`.

Lean에 표현식을 평가하도록 요청하려면, 편집기에서 그 앞에 `#eval`을 작성하면 Lean이 결과를 보여줍니다.
일반적으로 결과는 커서나 마우스 포인터를 `#eval` 위에 놓으면 확인됩니다.

Lean은 산술 연산자에 대한 표준 연산자 우선순위와 결합 법칙을 따릅니다.
즉, 위 코드는 `15`가 아니라 값 `11`을 산출합니다.

While both ordinary mathematical notation and the majority of programming languages use parentheses (e.g. `f(x)`) to apply a function to its arguments, Lean simply writes the function next to its arguments (e.g. `f x`).
Function application is one of the most common operations, so it pays to keep it concise.
Rather than writing

```
#eval String.append("Hello, ", "Lean!")
```

to compute `"Hello, Lean!"`, one would instead write

`"Hello, Lean!"#eval String.append "Hello, " "Lean!"`

where the function's two arguments are simply written next to it with spaces.

일반적인 수학 표기법과 대부분의 프로그래밍 언어가 함수를 인수에 적용하기 위해 괄호(예: `f(x)`)를 사용하는 반면, Lean은 단순히 함수를 인수 옆에 씁니다(예: `f x`).
함수 적용은 가장 일반적인 연산 중 하나이므로 간결하게 유지하는 것이 좋습니다.
`"Hello, Lean!"`을 계산하기 위해 위 구문 대신 아래처럼 작성할 수 있습니다. 여기서 함수의 두 인수는 단순히 공백을 사이에 두고 옆에 씁니다.

Just as the order-of-operations rules for arithmetic demand parentheses in the expression `(1 + 2) * 5`, parentheses are also necessary when a function's argument is to be computed via another function call.
For instance, parentheses are required in

`"great oak tree"#eval String.append "great " (String.append "oak " "tree")`

because otherwise the second `String.append` would be interpreted as an argument to the first, rather than as a function being passed `"oak "` and `"tree"` as arguments.
The value of the inner `String.append` call must be found first, after which it can be appended to `"great "`, yielding the final value `"great oak tree"`.

산술에 대한 연산 순서 규칙이 표현식 `(1 + 2) * 5`에서 괄호를 요구하는 것처럼, 함수의 인수가 다른 함수 호출을 통해 계산될 때도 괄호가 필요합니다.
예를 들어, 위 코드에서 괄호가 필요한 이유는 그렇지 않으면 두 번째 `String.append`가 `"oak "`과 `"tree"`를 인수로 전달받는 함수가 아니라 첫 번째의 인수로 해석되기 때문입니다.
내부 `String.append` 호출의 값을 먼저 찾아야 하고, 그 후 `"great "`에 추가되어 최종 값 `"great oak tree"`를 산출합니다.

Imperative languages often have two kinds of conditional: a conditional *statement* that determines which instructions to carry out based on a Boolean value, and a conditional *expression* that determines which of two expressions to evaluate based on a Boolean value.
For instance, in C and C++, the conditional statement is written using `if` and `else`, while the conditional expression is written with a ternary operator in which `?` and `:` separate the condition from the branches.
In Python, the conditional statement begins with `if`, while the conditional expression puts `if` in the middle.
Because Lean is an expression-oriented functional language, there are no conditional statements, only conditional expressions.
They are written using `if`, `then`, and `else`.
For example,

`String.append "it is " (if 1 > 2 then "yes" else "no")`

evaluates to

`String.append "it is " (if false then "yes" else "no")`

which evaluates to

`String.append "it is " "no"`

which finally evaluates to `"it is no"`.

명령형 언어는 종종 두 가지 종류의 조건식을 가집니다: Boolean 값에 따라 어떤 지시사항을 수행할지 결정하는 조건 *문장*과 Boolean 값에 따라 두 표현식 중 어느 것을 평가할지 결정하는 조건 *표현식*.
예를 들어, C와 C++에서 조건 문장은 `if`와 `else`를 사용하여 작성되며, 조건 표현식은 `?`와 `:`가 조건과 분기를 구분하는 삼항 연산자로 작성됩니다.
Python에서 조건 문장은 `if`로 시작하고, 조건 표현식은 `if`를 중간에 놓습니다.
Lean은 표현식 지향적 함수형 언어이므로, 조건 문장이 없고 조건 표현식만 있습니다.
이들은 `if`, `then`, `else`를 사용하여 작성됩니다.
위 코드는 단계적으로 평가되어 마지막에 `"it is no"`으로 평가됩니다.

For the sake of brevity, a series of evaluation steps like this will sometimes be written with arrows between them:

간결함을 위해, 이와 같은 일련의 평가 단계는 때때로 그들 사이에 화살표를 사용하여 작성됩니다.

## 1.1.1. Messages You May Meet

Asking Lean to evaluate a function application that is missing an argument will lead to an error message.
In particular, the example

`` could not synthesize a `ToExpr`, `Repr`, or `ToString` instance for type
String → String#eval String.append "it is " ``

yields a quite long error message:

```
could not synthesize a `ToExpr`, `Repr`, or `ToString` instance for type
  String → String
```

This message occurs because Lean functions that are applied to only some of their arguments return new functions that are waiting for the rest of the arguments.
Lean cannot display functions to users, and thus returns an error when asked to do so.

인수가 누락된 함수 적용을 평가하도록 Lean에 요청하면 오류 메시지가 발생합니다.
특히, 위 예제는 상당히 긴 오류 메시지를 산출합니다. 이 메시지는 인수의 일부만 적용된 Lean 함수가 나머지 인수를 기다리는 새로운 함수를 반환하기 때문에 발생합니다.
Lean은 사용자에게 함수를 표시할 수 없으므로, 그렇게 하도록 요청될 때 오류를 반환합니다.

## 1.1.2. Exercises

What are the values of the following expressions? Work them out by hand,
then enter them into Lean to check your work.

다음 표현식의 값은 무엇입니까? 손으로 계산해 본 다음,
Lean에 입력하여 결과를 확인하세요.
