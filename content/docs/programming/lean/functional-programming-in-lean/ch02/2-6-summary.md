---
title: "요약"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "평가와 실행, do 표기법, 프로그램 컴파일과 실행, 부분성(partiality)을 정리한 2장 요약"
---

# 2.6. Summary

## 2.6.1. Evaluation vs Execution

Side effects are aspects of program execution that go beyond the evaluation of mathematical expressions, such as reading files, throwing exceptions, or triggering industrial machinery.
While most languages allow side effects to occur during evaluation, Lean does not.
Instead, Lean has a type called `IO` that represents *descriptions* of programs that use side effects.
These descriptions are then executed by the language's run-time system, which invokes the Lean expression evaluator to carry out specific computations.
Values of type `IO α` are called *`IO` actions*.
The simplest is `pure`, which returns its argument and has no actual side effects.

부작용은 파일 읽기, 예외 발생, 또는 산업용 기계 제어와 같이 수학적 표현의 평가를 넘어서는 프로그램 실행의 측면입니다.
대부분의 언어는 평가 중에 부작용이 발생하도록 허용하지만, Lean은 그렇지 않습니다.
대신 Lean은 부작용을 사용하는 프로그램의 *설명*을 나타내는 `IO`라는 타입을 가지고 있습니다.
이러한 설명들은 언어의 런타임 시스템에 의해 실행되며, 이는 Lean 표현식 평가기를 호출하여 특정 계산을 수행합니다.
`IO α` 타입의 값들을 *`IO` 액션*이라고 합니다.
가장 단순한 것은 `pure`로, 인자를 반환하고 실제 부작용이 없습니다.

`IO` actions can also be understood as functions that take the whole world as an argument and return a new world in which the side effect has occurred.
Behind the scenes, the `IO` library ensures that the world is never duplicated, created, or destroyed.
While this model of side effects cannot actually be implemented, as the whole universe is too big to fit in memory, the real world can be represented by a token that is passed around through the program.

`IO` 액션은 또한 전체 세계를 인자로 받아서 부작용이 발생한 새로운 세계를 반환하는 함수로 이해할 수 있습니다.
내부적으로 `IO` 라이브러리는 세계가 절대로 중복되거나 생성되거나 파괴되지 않도록 보장합니다.
이 부작용 모델은 우주 전체가 메모리에 맞기에는 너무 크기 때문에 실제로는 구현될 수 없지만, 실제 세계는 프로그램을 통해 전달되는 토큰으로 표현될 수 있습니다.

An `IO` action `main` is executed when the program starts.
`main` can have one of three types:

* `main : IO Unit` is used for simple programs that cannot read their command-line arguments and always return exit code `0`,
* `main : IO UInt32` is used for programs without arguments that may signal success or failure, and
* `main : List String → IO UInt32` is used for programs that take command-line arguments and signal success or failure.

`IO` 액션 `main`은 프로그램이 시작할 때 실행됩니다.
`main`은 다음 세 가지 타입 중 하나를 가질 수 있습니다:

* `main : IO Unit`은 명령줄 인자를 읽을 수 없고 항상 종료 코드 `0`을 반환하는 단순 프로그램에 사용되며,
* `main : IO UInt32`는 인자가 없으면서 성공 또는 실패를 신호할 수 있는 프로그램에 사용되고,
* `main : List String → IO UInt32`는 명령줄 인자를 받아 성공 또는 실패를 신호하는 프로그램에 사용됩니다.

## 2.6.2. `do` Notation

The Lean standard library provides a number of basic `IO` actions that represent effects such as reading from and writing to files and interacting with standard input and standard output.
These base `IO` actions are composed into larger `IO` actions using `do` notation, which is a built-in domain-specific language for writing descriptions of programs with side effects.
A `do` expression contains a sequence of *statements*, which may be:

* expressions that represent `IO` actions,
* ordinary local definitions with `let` and `:=`, where the defined name refers to the value of the provided expression, or
* local definitions with `let` and `←`, where the defined name refers to the result of executing the value of the provided expression.

Lean 표준 라이브러리는 파일 읽기 및 쓰기, 표준 입력 및 출력과의 상호작용과 같은 효과를 나타내는 여러 기본 `IO` 액션들을 제공합니다.
이러한 기본 `IO` 액션들은 부작용이 있는 프로그램의 설명을 작성하기 위한 내장 도메인별 언어인 `do` 표기법을 사용하여 더 큰 `IO` 액션들로 구성됩니다.
`do` 표현식은 *문장들*의 순서를 포함하며, 이는 다음과 같을 수 있습니다:

* `IO` 액션들을 나타내는 표현식들,
* 정의된 이름이 제공된 표현식의 값을 나타내는 `let`과 `:=`을 사용한 일반적인 지역 정의들, 또는
* 정의된 이름이 제공된 표현식의 값을 실행한 결과를 나타내는 `let`과 `←`을 사용한 지역 정의들.

`IO` actions that are written with `do` are executed one statement at a time.

Furthermore, `if` and `match` expressions that occur immediately under a `do` are implicitly considered to have their own `do` in each branch.
Inside of a `do` expression, *nested actions* are expressions with a left arrow immediately under parentheses.
The Lean compiler implicitly lifts them to the nearest enclosing `do`, which may be implicitly part of a branch of a `match` or `if` expression, and gives them a unique name.
This unique name then replaces the origin site of the nested action.

`do`로 작성된 `IO` 액션들은 한 번에 하나의 문장씩 실행됩니다.

더욱이, `do` 바로 아래에 발생하는 `if`와 `match` 표현식들은 암묵적으로 각 분기에서 자신만의 `do`를 가지도록 간주됩니다.
`do` 표현식 내에서 *중첩 액션들*은 괄호 바로 아래에 왼쪽 화살표를 가진 표현식들입니다.
Lean 컴파일러는 이들을 가장 가까운 바깥쪽 `do`로 암묵적으로 올리며, 이는 `match` 또는 `if` 표현식의 분기의 일부일 수 있으며, 유일한 이름을 부여합니다.
이 유일한 이름은 중첩 액션의 원본 위치를 대체합니다.

## 2.6.3. Compiling and Running Programs

A Lean program that consists of a single file with a `main` definition can be run using `lean --run FILE`.
While this can be a nice way to get started with a simple program, most programs will eventually graduate to a multiple-file project that should be compiled before running.

Lean projects are organized into *packages*, which are collections of libraries and executables together with information about dependencies and a build configuration.
Packages are described using Lake, a Lean build tool.
Use `lake new` to create a Lake package in a new directory, or `lake init` to create one in the current directory.
Lake package configuration is another domain-specific language.
Use `lake build` to build a project.

`main` 정의를 포함하는 단일 파일로 구성된 Lean 프로그램은 `lean --run FILE`을 사용하여 실행할 수 있습니다.
이는 단순한 프로그램으로 시작하는 좋은 방법일 수 있지만, 대부분의 프로그램은 결국 실행 전에 컴파일되어야 하는 다중 파일 프로젝트로 발전합니다.

Lean 프로젝트는 라이브러리와 실행 파일들의 모음으로, 의존성 정보와 빌드 설정을 함께 포함하는 *패키지*로 조직됩니다.
패키지는 Lean 빌드 도구인 Lake를 사용하여 설명됩니다.
`lake new`를 사용하여 새로운 디렉토리에 Lake 패키지를 생성하거나, `lake init`을 사용하여 현재 디렉토리에 생성합니다.
Lake 패키지 설정은 또 다른 도메인별 언어입니다.
프로젝트를 빌드하려면 `lake build`를 사용합니다.

## 2.6.4. Partiality

One consequence of following the mathematical model of expression evaluation is that every expression must have a value.
This rules out both incomplete pattern matches that fail to cover all constructors of a datatype and programs that can fall into an infinite loop.
Lean ensures that all `match` expressions cover all cases, and that all recursive functions are either structurally recursive or have an explicit proof of termination.

However, some real programs require the possibility of looping infinitely, because they handle potentially-infinite data, such as POSIX streams.
Lean provides an escape hatch: functions whose definition is marked `partial` are not required to terminate.
This comes at a cost.
Because types are a first-class part of the Lean language, functions can return types.
Partial functions, however, are not evaluated during type checking, because an infinite loop in a function could cause the type checker to enter an infinite loop.
Furthermore, mathematical proofs are unable to inspect the definitions of partial functions, which means that programs that use them are much less amenable to formal proof.

표현식 평가의 수학적 모델을 따르는 결과로, 모든 표현식은 값을 가져야 합니다.
이는 데이터타입의 모든 생성자를 포함하지 못하는 불완전한 패턴 매칭과 무한 루프에 빠질 수 있는 프로그램 모두를 배제합니다.
Lean은 모든 `match` 표현식이 모든 경우를 포함하도록 보장하며, 모든 재귀 함수는 구조적으로 재귀적이거나 명시적인 종료 증명을 가지도록 합니다.

그러나 일부 실제 프로그램들은 POSIX 스트림과 같이 잠재적으로 무한한 데이터를 처리하기 때문에 무한 루프의 가능성이 필요합니다.
Lean은 빠져나갈 수 있는 방법을 제공합니다: 정의가 `partial`로 표시된 함수들은 종료할 필요가 없습니다.
하지만 이는 비용을 초래합니다.
타입이 Lean 언어의 일급 부분이기 때문에 함수들은 타입을 반환할 수 있습니다.
그러나 부분 함수들은 타입 검사 중에 평가되지 않습니다. 왜냐하면 함수의 무한 루프가 타입 검사기를 무한 루프에 빠지게 할 수 있기 때문입니다.
더욱이, 수학적 증명들은 부분 함수들의 정의를 검사할 수 없으므로, 그들을 사용하는 프로그램들은 형식적 증명에 훨씬 덜 적합합니다.
