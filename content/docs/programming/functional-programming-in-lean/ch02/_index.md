---
title: "Ch.2: Hello, World!"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Ch.2: Hello, World!"
---

# 2. Hello, World!

While Lean has been designed to have a rich interactive environment in which programmers can get quite a lot of feedback from the language without leaving the confines of their favorite text editor, it is also a language in which real programs can be written.
This means that it also has a batch-mode compiler, a build system, a package manager, and all the other tools that are necessary for writing programs.

Lean은 풍부한 인터랙티브 환경을 갖추어 편집기 안에서 언어로부터 풍부한 피드백을 받을 수 있을 뿐만 아니라, 실제 프로그램을 작성하기에도 충분한 언어입니다.
따라서 Lean은 배치 모드 컴파일러, 빌드 시스템, 패키지 관리자 등 프로그램 작성에 필요한 도구들을 모두 갖추고 있습니다.

While the [previous chapter](../ch01/) presented the basics of functional programming in Lean, this chapter explains how to start a programming project, compile it, and run the result.
Programs that run and interact with their environment (e.g. by reading input from standard input or creating files) are difficult to reconcile with the understanding of computation as the evaluation of mathematical expressions.
In addition to a description of the Lean build tools, this chapter also provides a way to think about functional programs that interact with the world.

[앞 챕터](../ch01/)에서 Lean 함수형 프로그래밍의 기초를 다뤘다면, 이 챕터는 프로젝트를 시작하고, 컴파일하고, 실행하는 방법을 설명합니다.
환경과 상호작용하는 프로그램(예: 표준 입력 읽기, 파일 생성)은 '계산 = 수식 평가'라는 개념과 쉽게 맞지 않습니다.
Lean 빌드 도구 소개와 함께, 외부와 상호작용하는 함수형 프로그램을 어떻게 이해할지도 다룹니다.

1. [2.1. Running a Program](2-1-running-a-program/)
2. [2.2. Step By Step](2-2-step-by-step/)
3. [2.3. Starting a Project](2-3-starting-a-project/)
4. [2.4. Worked Example: `cat`](2-4-worked-example-cat/)
5. [2.5. Additional Conveniences](2-5-additional-conveniences/)
6. [2.6. Summary](2-6-summary/)
7. [Interlude: Propositions, Proofs, and Indexing](interlude-propositions-proofs-and-indexing/)
