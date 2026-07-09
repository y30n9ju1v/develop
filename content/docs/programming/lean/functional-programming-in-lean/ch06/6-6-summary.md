---
title: "Summary"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Summary"
---

# 6.6. Summary

## 6.6.1. Combining Monads

When writing a monad from scratch, there are design patterns that tend to describe the ways that each effect is added to the monad.
Reader effects are added by having the monad's type be a function from the reader's environment, state effects are added by including a function from the initial state to the value paired with the final state, failure or exceptions are added by including a sum type in the return type, and logging or other output is added by including a product type in the return type.
Existing monads can be made part of the return type as well, allowing their effects to be included in the new monad.

처음부터 Monad를 작성할 때 각 효과가 Monad에 추가되는 방식을 설명하는 경향이 있는 디자인 패턴이 있습니다. Reader 효과는 Monad의 타입을 Reader의 환경에서의 함수로 만들어 추가되고, 상태 효과는 초기 상태에서 최종 상태와 쌍을 이루는 값으로의 함수를 포함하여 추가되며, 실패 또는 예외는 반환 타입에 합 타입을 포함하여 추가되고, 로깅 또는 기타 출력은 반환 타입에 곱 타입을 포함하여 추가됩니다. 기존 Monad는 반환 타입의 일부로 만들어질 수도 있으며, 이를 통해 그 효과가 새로운 Monad에 포함될 수 있습니다.

These design patterns are made into a library of reusable software components by defining *monad transformers*, which add an effect to some base monad.
Monad transformers take the simpler monad types as arguments, returning the enhanced monad types.
At a minimum, a monad transformer should provide the following instances:

1. A `Monad` instance that assumes the inner type is already a monad
2. A `MonadLift` instance to translate an action from the inner monad to the transformed monad

Monad transformers may be implemented as polymorphic structures or inductive datatypes, but they are most often implemented as functions from the underlying monad type to the enhanced monad type.

이러한 디자인 패턴은 기본 Monad에 효과를 추가하는 *Monad Transformer*를 정의하여 재사용 가능한 소프트웨어 구성 요소의 라이브러리로 만들어집니다. Monad Transformer는 더 단순한 Monad 타입을 인수로 받아 향상된 Monad 타입을 반환합니다. 최소한 Monad Transformer는 다음 인스턴스를 제공해야 합니다:

1. 내부 타입이 이미 Monad라고 가정하는 `Monad` 인스턴스
2. 내부 Monad에서 변환된 Monad로 액션을 변환하는 `MonadLift` 인스턴스

Monad Transformer는 다형 구조 또는 귀납형 데이터타입으로 구현될 수 있지만 가장 종종 기본 Monad 타입에서 향상된 Monad 타입으로의 함수로 구현됩니다.

## 6.6.2. Type Classes for Effects

A common design pattern is to implement a particular effect by defining a monad that has the effect, a monad transformer that adds it to another monad, and a type class that provides a generic interface to the effect.
This allows programs to be written that merely specify which effects they need, so the caller can provide any monad that has the right effects.

일반적인 디자인 패턴은 효과를 가지는 Monad를 정의하고, 다른 Monad에 이를 추가하는 Monad Transformer를 정의하고, 효과에 대한 일반 인터페이스를 제공하는 타입 클래스를 정의하여 특정 효과를 구현하는 것입니다. 이를 통해 필요한 효과만 지정하는 프로그램을 작성할 수 있으므로 호출자는 올바른 효과를 가진 모든 Monad를 제공할 수 있습니다.

Sometimes, auxiliary type information (e.g. the state's type in a monad that provides state, or the exception's type in a monad that provides exceptions) is an output parameter, and sometimes it is not.
The output parameter is most useful for simple programs that use each kind of effect only once, but it risks having the type checker commit to a the wrong type too early when multiple instances of the same effect are used in a given program.
Thus, both versions are typically provided, with the ordinary-parameter version of the type class having a name that ends in `-Of`.

때로는 보조 타입 정보 (예: 상태를 제공하는 Monad의 상태 타입 또는 예외를 제공하는 Monad의 예외 타입)가 출력 매개변수이고 때로는 그렇지 않습니다. 출력 매개변수는 각 효과를 한 번만 사용하는 간단한 프로그램에 가장 유용하지만, 주어진 프로그램에서 동일한 효과의 여러 인스턴스를 사용할 때 타입 체커가 너무 일찍 잘못된 타입에 커밋할 위험이 있습니다. 따라서 일반적으로 두 버전이 제공되며, 타입 클래스의 일반 매개변수 버전의 이름은 `-Of`로 끝납니다.

## 6.6.3. Monad Transformers Don't Commute

It is important to note that changing the order of transformers in a monad can change the meaning of programs that use the monad.
For instance, re-ordering `StateT` and `ExceptT` can result either in programs that lose state modifications when exceptions are thrown or programs that keep changes.
While most imperative languages provide only the latter, the increased flexibility provided by monad transformers demands thought and attention to choose the correct variety for the task at hand.

Monad에서 Transformer의 순서를 변경하면 Monad를 사용하는 프로그램의 의미가 변경될 수 있다는 것을 주목하는 것이 중요합니다. 예를 들어 `StateT`와 `ExceptT`를 재정렬하면 예외가 발생할 때 상태 수정이 손실되는 프로그램 또는 변경 사항을 유지하는 프로그램이 생성될 수 있습니다. 대부분의 명령형 언어는 후자만 제공하는 반면, Monad Transformer가 제공하는 증가된 유연성은 현재 작업에 맞는 올바른 다양성을 선택하기 위해 신중한 생각과 주의를 요구합니다.

## 6.6.4. `do`-Notation for Monad Transformers

Lean's `do`-blocks support early return, in which the block is terminated with some value, locally mutable variables, `for`-loops with `break` and `continue`, and single-branched `if`-statements.
While this may seem to be introducing imperative features that would get in the way of using Lean to write proofs, it is in fact nothing more than a more convenient syntax for certain common uses of monad transformers.
Behind the scenes, whatever monad the `do`-block is written in is transformed by appropriate uses of `ExceptT` and `StateT` to support these additional effects.

Lean의 `do` 블록은 조기 반환을 지원하며, 이를 통해 블록이 어떤 값으로 종료되고, 로컬 변경 가능한 변수, `break` 및 `continue`가 있는 `for` 루프, 그리고 단일 분기 `if` 명령문을 지원합니다. 이는 Lean을 사용하여 증명을 작성하는 것의 방해가 될 명령형 기능을 도입하는 것처럼 보일 수 있지만, 실제로는 Monad Transformer의 특정 일반적인 사용을 위한 더 편리한 문법일 뿐입니다. 뒤에서는 `do` 블록이 작성된 모든 Monad가 이러한 추가 효과를 지원하기 위해 `ExceptT`와 `StateT`의 적절한 사용으로 변환됩니다.
