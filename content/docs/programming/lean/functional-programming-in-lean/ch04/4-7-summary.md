---
title: "4.7. 요약"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "4장 Monad 요약"
---

# 4.7. Summary

## 4.7.1. Encoding Side Effects

Lean is a pure functional language.
This means that it does not include side effects such as mutable variables, logging, or exceptions.
However, most side effects can be *encoded* using a combination of functions and inductive types or structures.
For example, mutable state can be encoded as a function from an initial state to a pair of a final state and a result, and exceptions can be encoded as an inductive type with constructors for successful termination and errors.

Lean은 순수 함수형 언어입니다. 이는 가변 변수, 로깅, 예외와 같은 부작용을 포함하지 않는다는 의미입니다. 그러나 대부분의 부작용은 함수와 귀납적 타입 또는 구조체의 조합을 사용하여 인코딩할 수 있습니다. 예를 들어, 가변 상태는 초기 상태에서 최종 상태와 결과의 쌍으로 가는 함수로 인코딩될 수 있으며, 예외는 성공적인 종료와 오류에 대한 생성자를 가진 귀납적 타입으로 인코딩될 수 있습니다.

Each set of encoded effects is a type.
As a result, if a program uses these encoded effects, then this is apparent in its type.
Functional programming does not mean that programs can't use effects, it simply requires that they be *honest* about which effects they use.
A Lean type signature describes not only the types of arguments that a function expects and the type of result that it returns, but also which effects it may use.

인코딩된 각 부작용 집합은 타입입니다. 결과적으로 프로그램이 이러한 인코딩된 부작용을 사용하면 이는 타입에 명확히 나타납니다. 함수형 프로그래밍은 프로그램이 부작용을 사용할 수 없다는 의미가 아니라, 단순히 사용하는 부작용에 대해 정직해야 한다는 의미입니다. Lean 타입 시그니처는 함수가 기대하는 인수의 타입과 반환하는 결과의 타입뿐만 아니라 어떤 부작용을 사용할 수 있는지도 설명합니다.

## 4.7.2. The Monad Type Class

It's possible to write purely functional programs in languages that allow effects anywhere.
For example, `2 + 3` is a valid Python program that has no effects at all.
Similarly, combining programs that have effects requires a way to state the order in which the effects must occur.
It matters whether an exception is thrown before or after modifying a variable, after all.

부작용을 어디서나 허용하는 언어에서도 순수 함수형 프로그램을 작성할 수 있습니다. 예를 들어, `2 + 3`은 전혀 부작용이 없는 유효한 Python 프로그램입니다. 마찬가지로 부작용이 있는 프로그램을 결합하려면 부작용이 발생해야 하는 순서를 나타내는 방법이 필요합니다. 결국 예외가 변수를 수정하기 전에 발생하는지 후에 발생하는지가 중요합니다.

The type class `Monad` captures these two important properties.
It has two methods: `pure` represents programs that have no effects, and `bind` sequences effectful programs.
The contract for `Monad` instances ensures that `bind` and `pure` actually capture pure computation and sequencing.

`Monad` 타입 클래스는 이 두 가지 중요한 특성을 캡처합니다. 두 가지 메서드가 있습니다: `pure`는 부작용이 없는 프로그램을 나타내고, `bind`는 부작용이 있는 프로그램을 순서대로 연결합니다. `Monad` 인스턴스에 대한 계약은 `bind`와 `pure`가 실제로 순수 계산과 순서대로 연결을 캡처하도록 보장합니다.

## 4.7.3. `do`-Notation for Monads

Rather than being limited to `IO`, `do`-notation works for any monad.
It allows programs that use monads to be written in a style that is reminiscent of statement-oriented languages, with statements sequenced after one another.
Additionally, `do`-notation enables a number of additional convenient shorthands, such as nested actions.
A program written with `do` is translated to applications of `>>=` behind the scenes.

`IO`로 제한되지 않고, `do`-표기법은 모든 Monad에 대해 작동합니다. 이는 Monad를 사용하는 프로그램을 명령문 지향 언어를 연상시키는 스타일로 작성할 수 있게 하며, 명령문은 서로 순서대로 연결됩니다. 추가적으로, `do`-표기법은 중첩된 액션과 같은 여러 편리한 단축어를 활성화합니다. `do`로 작성된 프로그램은 뒤에서 `>>=`의 적용으로 변환됩니다.

## 4.7.4. Custom Monads

Different languages provide different sets of side effects.
While most languages feature mutable variables and file I/O, not all have features like exceptions.
Other languages offer effects that are rare or unique, like Icon's search-based program execution, Scheme and Ruby's continuations, and Common Lisp's resumable exceptions.
An advantage to encoding effects with monads is that programs are not limited to the set of effects that are provided by the language.
Because Lean is designed to make programming with any monad convenient, programmers are free to choose exactly the set of side effects that make sense for any given application.

다양한 언어는 다양한 부작용 집합을 제공합니다. 대부분의 언어는 가변 변수와 파일 I/O 기능을 포함하지만, 모두가 예외와 같은 기능을 가지고 있지는 않습니다. Icon의 검색 기반 프로그램 실행, Scheme과 Ruby의 연속, Common Lisp의 재개 가능한 예외와 같이 드물거나 고유한 부작용을 제공하는 언어도 있습니다. Monad를 사용하여 부작용을 인코딩하는 장점은 프로그램이 언어에서 제공하는 부작용 집합에 제한되지 않는다는 것입니다. Lean은 모든 Monad를 사용한 프로그래밍을 편리하게 하도록 설계되었기 때문에 프로그래머는 주어진 응용 프로그램에 적합한 정확한 부작용 집합을 선택할 수 있습니다.

## 4.7.5. The `IO` Monad

Programs that can affect the real world are written as `IO` actions in Lean.
`IO` is one monad among many.
The `IO` monad encodes state and exceptions, with the state being used to keep track of the state of the world and the exceptions modeling failure and recovery.

실제 세계에 영향을 미칠 수 있는 프로그램은 Lean에서 `IO` 액션으로 작성됩니다. `IO`는 많은 Monad 중 하나입니다. `IO` Monad는 상태와 예외를 인코딩하며, 상태는 세계의 상태를 추적하는 데 사용되고 예외는 실패와 복구를 모델링합니다.
