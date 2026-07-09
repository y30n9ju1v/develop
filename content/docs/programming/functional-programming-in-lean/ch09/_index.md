---
title: "Ch.9: 다음 단계"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Ch.9: 다음 단계"
---

# 9. Next Steps

This book introduces the very basics of functional programming in Lean, including a tiny amount of interactive theorem proving.
Using dependently-typed functional languages like Lean is a deep topic, and much can be said.
Depending on your interests, the following resources might be useful for learning Lean 4.

이 책은 Lean으로 배우는 함수형 프로그래밍의 기초를 소개하며, 인터랙티브 정리 증명도 일부 다룹니다.
Lean처럼 의존 타입을 갖춘 함수형 언어를 다루는 것은 깊이 있는 주제이며, 할 말이 많습니다.
관심사에 따라 다음 리소스들이 Lean 4 학습에 도움이 될 것입니다.

## 9.1. Learning Lean

Lean 4 itself is described in the following resources:

Lean 4 자체는 다음 리소스에 설명되어 있습니다.

However, the best way to continue learning Lean is to start reading and writing code, consulting the documentation when you get stuck.
Additionally, the [Lean Zulip](https://leanprover.zulipchat.com/) is an excellent place to meet other Lean users, ask for help, and help others.

그러나 Lean을 계속 배우는 가장 좋은 방법은 직접 코드를 읽고 써보면서, 막히면 문서를 찾아보는 것입니다.
또한, [Lean Zulip](https://leanprover.zulipchat.com/)은 다른 Lean 사용자를 만나고, 도움을 요청하고, 다른 사람을 돕는 좋은 곳입니다.

## 9.2. Mathematics in Lean

A wide selection of learning resources for mathematicians are available at [the community site](https://leanprover-community.github.io/learn.html).

수학자를 위한 광범위한 학습 리소스는 [커뮤니티 사이트](https://leanprover-community.github.io/learn.html)에서 이용할 수 있습니다.

## 9.3. Using Dependent Types in Computer Science

Rocq is a language that has a lot in common with Lean.
For computer scientists, the [Software Foundations](https://softwarefoundations.cis.upenn.edu/) series of interactive textbooks provides an excellent introduction to applications of Rocq in computer science.
The fundamental ideas of Lean and Rocq are very similar, and skills are readily transferable between the systems.

Rocq은 Lean과 공통점이 많은 언어입니다.
컴퓨터 과학자들을 위해, [Software Foundations](https://softwarefoundations.cis.upenn.edu/) 대화형 교과서 시리즈는 컴퓨터 과학에서 Rocq의 응용에 대한 훌륭한 소개를 제공합니다.
Lean과 Rocq의 기본적인 개념은 매우 유사하며, 기술은 시스템 간에 쉽게 이전할 수 있습니다.

## 9.4. Programming with Dependent Types

For programmers who are interested in learning to use indexed families and dependent types to structure programs, Edwin Brady's [*Type Driven Development with Idris*](https://www.manning.com/books/type-driven-development-with-idris) provides an excellent introduction.
Like Rocq, Idris is a close cousin of Lean, though it lacks tactics.

인덱스 패밀리와 종속 타입을 사용하여 프로그램을 구조화하는 방법을 배우는 데 관심이 있는 프로그래머들을 위해, Edwin Brady의 [*Type Driven Development with Idris*](https://www.manning.com/books/type-driven-development-with-idris)는 훌륭한 소개를 제공합니다.
Rocq과 마찬가지로, Idris는 Lean의 가까운 친척이지만, tactic이 부족합니다.

## 9.5. Understanding Dependent Types

[*The Little Typer*](https://thelittletyper.com/) is a book for programmers who haven't formally studied logic or the theory of programming languages, but who want to build an understanding of the core ideas of dependent type theory.
While all of the above resources aim to be as practical as possible, *The Little Typer* presents an approach to dependent type theory where the very basics are built up from scratch, using only concepts from programming.
Disclaimer: the author of *Functional Programming in Lean* is also an author of *The Little Typer*.

[*The Little Typer*](https://thelittletyper.com/)는 논리나 프로그래밍 언어 이론을 정식으로 공부하지는 않았지만 종속 타입 이론의 핵심 개념을 이해하고 싶은 프로그래머들을 위한 책입니다.
위의 모든 리소스들은 가능한 한 실용적이기를 목표로 하지만, *The Little Typer*는 프로그래밍 개념만을 사용하여 기본적인 것부터 차근차근 구축하는 종속 타입 이론의 접근 방식을 제시합니다.
고지: *Functional Programming in Lean*의 저자는 또한 *The Little Typer*의 저자입니다.
