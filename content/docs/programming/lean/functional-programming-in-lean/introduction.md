---
title: "소개"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Functional Programming in Lean 소개 — Lean 4의 특징과 이 책의 구성"
---

# Introduction

Lean is an interactive theorem prover based on dependent type theory.
Originally developed at Microsoft Research, development now takes place at the [Lean FRO](https://lean-fro.org).
Dependent type theory unites the worlds of programs and proofs; thus, Lean is also a programming language.
Lean takes its dual nature seriously, and it is designed to be suitable for use as a general-purpose programming language—Lean is even implemented in itself.
This book is about writing programs in Lean.

Lean은 의존 타입 이론(dependent type theory) 기반의 인터랙티브 정리 증명기입니다.
Microsoft Research에서 처음 개발되었으며, 현재는 [Lean FRO](https://lean-fro.org)에서 개발이 이루어지고 있습니다.
의존 타입 이론은 프로그램과 증명의 세계를 하나로 통합합니다. 그래서 Lean은 프로그래밍 언어이기도 합니다.
Lean은 이 두 가지 성질을 모두 진지하게 다루며, 범용 프로그래밍 언어로 사용하기에 적합하도록 설계되었습니다. 심지어 Lean 자체가 Lean으로 구현되어 있습니다.
이 책은 Lean으로 프로그램을 작성하는 방법을 다룹니다.

---

When viewed as a programming language, Lean is a strict pure functional language with dependent types.
A large part of learning to program with Lean consists of learning how each of these attributes affects the way programs are written, and how to think like a functional programmer.
*Strictness* means that function calls in Lean work similarly to the way they do in most languages: the arguments are fully computed before the function's body begins running.
*Purity* means that Lean programs cannot have side effects such as modifying locations in memory, sending emails, or deleting files without the program's type saying so.
Lean is a *functional* language in the sense that functions are first-class values like any other and that the execution model is inspired by the evaluation of mathematical expressions.
*Dependent types*, which are the most unusual feature of Lean, make types into a first-class part of the language, allowing types to contain programs and programs to compute types.

프로그래밍 언어로서 Lean은 의존 타입을 갖춘 엄격한 순수 함수형 언어입니다.
Lean 프로그래밍을 배우는 데 있어 핵심은 이 속성들이 코드 작성 방식에 어떤 영향을 주는지, 그리고 함수형 프로그래머처럼 사고하는 법을 익히는 것입니다.

- ***엄격성(Strictness)***: 함수 호출 시 인수가 함수 본문 실행 전에 모두 계산됩니다. 대부분의 언어와 같은 방식입니다.
- ***순수성(Purity)***: 타입에 명시하지 않는 한, 메모리 수정·이메일 전송·파일 삭제 같은 부작용을 가질 수 없습니다.
- ***함수형(Functional)***: 함수가 다른 값과 동등한 일급 값이며, 실행 모델이 수식 계산의 평가에서 비롯됩니다.
- ***의존 타입(Dependent types)***: Lean의 가장 독특한 특징으로, 타입이 언어의 일급 요소가 됩니다. 타입이 프로그램을 포함할 수 있고, 프로그램이 타입을 계산할 수 있습니다.

---

This book is intended for programmers who want to learn Lean, but who have not necessarily used a functional programming language before.
Familiarity with functional languages such as Haskell, OCaml, or F# is not required.
On the other hand, this book does assume knowledge of concepts like loops, functions, and data structures that are common to most programming languages.
While this book is intended to be a good first book on functional programming, it is not a good first book on programming in general.

이 책은 Lean을 배우고 싶은 프로그래머를 위한 책입니다. 함수형 언어 경험이 없어도 됩니다.
Haskell, OCaml, F# 같은 함수형 언어를 사용해본 적이 없어도 괜찮습니다.
다만 루프, 함수, 자료구조처럼 대부분의 언어에 공통적인 프로그래밍 기초 개념은 알고 있다고 가정합니다.
함수형 프로그래밍 입문서로는 적합하지만, 프로그래밍 자체를 처음 배우는 책은 아닙니다.

---

Mathematicians who are using Lean as a proof assistant will likely need to write custom proof automation tools at some point.
This book is also for them.
As these tools become more sophisticated, they begin to resemble programs in functional languages, but most working mathematicians are trained in languages like Python and Mathematica.
This book can help bridge the gap, empowering more mathematicians to write maintainable and understandable proof automation tools.

증명 보조기로 Lean을 사용하는 수학자들도 이 책의 독자입니다.
정교한 증명 자동화 도구를 만들다 보면 함수형 언어 프로그램과 점점 닮아가는데, 대부분의 수학자는 Python이나 Mathematica로 훈련받습니다.
이 책이 그 간격을 좁혀, 더 많은 수학자들이 유지보수하기 좋고 이해하기 쉬운 증명 자동화 도구를 작성할 수 있도록 돕고자 합니다.

---

This book is intended to be read linearly, from the beginning to the end.
Concepts are introduced one at a time, and later sections assume familiarity with earlier sections.
Sometimes, later chapters will go into depth on a topic that was only briefly addressed earlier on.
Some sections of the book contain exercises.
These are worth doing, in order to cement your understanding of the section.
It is also useful to explore Lean as you read the book, finding creative new ways to use what you have learned.

이 책은 처음부터 끝까지 순서대로 읽도록 설계되었습니다.
개념은 하나씩 소개되며, 뒷부분은 앞 내용을 이해하고 있다고 가정합니다.
앞에서 간략히 다룬 주제를 나중에 더 깊이 파고드는 경우도 있습니다.
일부 섹션에는 연습 문제가 있습니다. 이해를 다지기 위해 직접 풀어보길 권합니다.
책을 읽으면서 Lean을 직접 실행해보고, 배운 내용을 응용하는 방법을 찾아보면 훨씬 효과적입니다.

---

## Getting Lean

Before writing and running programs written in Lean, you'll need to set up Lean on your own computer.
The Lean tooling consists of the following:

* `elan` manages the Lean compiler toolchains, similarly to `rustup` or `ghcup`.
* `lake` builds Lean packages and their dependencies, similarly to `cargo`, `make`, or Gradle.
* `lean` type checks and compiles individual Lean files as well as providing information to programmer tools about files that are currently being written.
  Normally, `lean` is invoked by other tools rather than directly by users.
* Plugins for editors, such as Visual Studio Code or Emacs, that communicate with `lean` and present its information conveniently.

Please refer to the [Lean manual](https://lean-lang.org/lean4/doc/quickstart.html) for up-to-date instructions for installing Lean.

Lean으로 프로그램을 작성하고 실행하려면 먼저 로컬 환경에 Lean을 설치해야 합니다.
Lean 도구 모음은 다음으로 구성됩니다:

* `elan`: `rustup`이나 `ghcup`처럼 Lean 컴파일러 툴체인을 관리합니다.
* `lake`: `cargo`나 `make`처럼 Lean 패키지와 의존성을 빌드합니다.
* `lean`: 개별 Lean 파일의 타입 검사와 컴파일을 수행하고, 현재 편집 중인 파일 정보를 개발 도구에 제공합니다. 보통 사용자가 직접 호출하지 않고 다른 도구가 호출합니다.
* Visual Studio Code, Emacs 등의 편집기 플러그인: `lean`과 통신해 정보를 편리하게 표시합니다.

설치 방법은 [Lean 공식 문서](https://lean-lang.org/lean4/doc/quickstart.html)를 참고하세요.

---

## Typographical Conventions

Code examples that are provided to Lean as *input* are formatted like this:

`def add1 (n : Nat) : Nat := n + 1``#eval add1 7`

The last line above (beginning with `#eval`) is a command that instructs Lean to calculate an answer.
Lean's replies are formatted like this:

```
8
```

Error messages returned by Lean are formatted like this:

```
Application type mismatch: The argument
  "seven"
has type
  String
but is expected to have type
  Nat
in the application
  add1 "seven"
```

Warnings are formatted like this:

```
declaration uses 'sorry'
```

Lean에 *입력*으로 전달되는 코드 예제는 위와 같이 표시됩니다.
마지막 줄(`#eval`로 시작)은 Lean에게 답을 계산하도록 지시하는 명령입니다.
Lean의 응답, 오류 메시지, 경고는 각각 위 형식으로 표시됩니다.

---

## Unicode

Idiomatic Lean code makes use of a variety of Unicode characters that are not part of ASCII.
For instance, Greek letters like `α` and `β` and the arrow `→` both occur in the first chapter of this book.
This allows Lean code to more closely resemble ordinary mathematical notation.

With the default Lean settings, both Visual Studio Code and Emacs allow these characters to be typed with a backslash (`\`) followed by a name.
For example, to enter `α`, type `\alpha`.
To find out how to type a character in Visual Studio Code, point the mouse at it and look at the tooltip.
In Emacs, use `C-c C-k` with point on the character in question.

관용적인 Lean 코드는 ASCII에 없는 다양한 유니코드 문자를 씁니다.
예를 들어 `α`, `β` 같은 그리스 문자와 화살표 `→`가 1장에서부터 등장합니다.
이 덕분에 Lean 코드가 일반적인 수학 표기법과 유사하게 보입니다.

기본 설정에서 Visual Studio Code와 Emacs 모두 역슬래시(`\`) 뒤에 이름을 입력해 이런 문자를 삽입할 수 있습니다.
예를 들어 `α`는 `\alpha`로 입력합니다.
VS Code에서는 문자에 마우스를 올리면 입력 방법이 툴팁으로 표시됩니다.
Emacs에서는 해당 문자에 커서를 두고 `C-c C-k`를 누릅니다.

---

## About the Author

David Thrane Christiansen has been using functional languages for twenty years, and dependent types for ten.
Together with Daniel P. Friedman, he wrote [*The Little Typer*](https://thelittletyper.com/), an introduction to the key ideas of dependent type theory.
He has a Ph.D. from the IT University of Copenhagen.
During his studies, he was a major contributor to the first version of the Idris language.
Since leaving academia, he has worked as a software developer at Galois in Portland, Oregon and Deon Digital in Copenhagen, Denmark, and he was the Executive Director of the Haskell Foundation.
At the time of writing, he is employed at the [Lean Focused Research Organization](https://lean-fro.org) working full-time on Lean.

David Thrane Christiansen은 20년간 함수형 언어를, 10년간 의존 타입을 사용해 왔습니다.
Daniel P. Friedman과 함께 의존 타입 이론의 핵심 개념을 소개하는 [*The Little Typer*](https://thelittletyper.com/)를 저술했습니다.
코펜하겐 IT 대학에서 박사 학위를 받았으며, 재학 중 Idris 언어 초기 버전의 주요 기여자였습니다.
학계를 떠난 뒤 미국 포틀랜드의 Galois, 덴마크 코펜하겐의 Deon Digital에서 소프트웨어 개발자로 일했고, Haskell Foundation 사무국장을 역임했습니다.
현재는 [Lean Focused Research Organization](https://lean-fro.org)에서 Lean 개발에 전념하고 있습니다.

---

## License

이 책의 원문은 Microsoft Corporation과의 계약 아래 David Thrane Christiansen이 작성했으며, Microsoft가 CC BY 4.0 라이선스로 공개했습니다.
현재 버전은 저자가 최신 Lean 버전에 맞게 수정한 것입니다.
변경 이력은 책의 [소스 저장소](https://github.com/leanprover/fp-lean/)에서 확인할 수 있습니다.

[![Creative Commons License](https://i.creativecommons.org/l/by/4.0/88x31.png)](http://creativecommons.org/licenses/by/4.0/)
[Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/)
