---
title: "Ch.1: Lean 시작하기"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Ch.1: Lean 시작하기"
---

# 1. Getting to Know Lean

According to tradition, a programming language should be introduced by compiling and running a program that displays `"Hello, world!"` on the console.
This simple program ensures that the language tooling is installed correctly and that the programmer is able to run the compiled code.

프로그래밍 언어를 소개할 때는 관례적으로 콘솔에 `"Hello, world!"`를 출력하는 프로그램을 컴파일하고 실행하는 것으로 시작합니다.
이 간단한 프로그램은 언어 도구가 올바르게 설치되었고, 프로그래머가 컴파일된 코드를 실행할 수 있음을 확인해 줍니다.

Since the 1970s, however, programming has changed.
Today, compilers are typically integrated into text editors, and the programming environment offers feedback as the program is written.
Lean is no exception: it implements an extended version of the Language Server Protocol that allows it to communicate with a text editor and provide feedback as the user types.

하지만 1970년대 이후로 프로그래밍은 변했습니다.
오늘날 컴파일러는 일반적으로 텍스트 편집기에 통합되어 있으며, 프로그래밍 환경은 프로그램을 작성할 때 피드백을 제공합니다.
Lean도 예외가 아닙니다. Lean은 텍스트 편집기와 통신하고 사용자가 입력할 때 피드백을 제공할 수 있는 Language Server Protocol의 확장 버전을 구현합니다.

Languages as varied as Python, Haskell, and JavaScript offer a read-eval-print-loop (REPL), also known as an interactive toplevel or a browser console, in which expressions or statements can be entered.
The language then computes and displays the result of the user's input.
Lean, on the other hand, integrates these features into the interaction with the editor, providing commands that cause the text editor to display feedback integrated into the program text itself.
This chapter provides a short introduction to interacting with Lean in an editor, while [Hello, World!](../ch02/) describes how to use Lean traditionally from the command line in batch mode.

Python, Haskell, JavaScript 같은 언어들은 REPL(read-eval-print-loop) — 인터랙티브 콘솔이라고도 부르는 — 을 제공하며, 여기에 표현식이나 문을 입력하면 결과를 바로 확인할 수 있습니다.
반면 Lean은 이런 기능을 편집기와의 상호작용에 통합합니다. 편집기 명령을 통해 프로그램 코드 안에 직접 피드백이 표시됩니다.
이 챕터는 편집기에서 Lean과 상호작용하는 방법을 간략히 소개합니다. 커맨드라인에서 배치 모드로 Lean을 사용하는 방법은 [Hello, World!](../ch02/)에서 다룹니다.

It is best if you read this book with Lean open in your editor, following along and typing in each example. Please play with the
examples, and see what happens!

편집기에서 Lean을 열어두고 이 책을 읽으면서 각 예제를 직접 입력해 보세요. 예제를 변형해보며 어떤 결과가 나오는지 확인해 보는 것도 좋습니다!

1. [1.1. Evaluating Expressions](1-1-evaluating-expressions/)
2. [1.2. Types](1-2-types/)
3. [1.3. Functions and Definitions](1-3-functions-and-definitions/)
4. [1.4. Structures](1-4-structures/)
5. [1.5. Datatypes and Patterns](1-5-datatypes-and-patterns/)
6. [1.6. Polymorphism](1-6-polymorphism/)
7. [1.7. Additional Conveniences](1-7-additional-conveniences/)
8. [1.8. Summary](1-8-summary/)
