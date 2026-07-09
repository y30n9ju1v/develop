---
title: "Ch.5: 펑터, 어플리커티브 펑터, 모나드"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Ch.5: 펑터, 어플리커티브 펑터, 모나드"
---

# 5. Functors, Applicative Functors, and Monads

`Functor` and `Monad` both describe operations for types that are still waiting for a type argument.
One way to understand them is that `Functor` describes containers in which the contained data can be transformed, and `Monad` describes an encoding of programs with side effects.
This understanding is incomplete, however.
After all, `Option` has instances for both `Functor` and `Monad`, and simultaneously represents an optional value *and* a computation that might fail to return a value.

`Functor`와 `Monad`는 모두 아직 type 인자를 기다리고 있는 type들을 위한 연산들을 기술합니다.
이들을 이해하는 한 가지 방법은 `Functor`는 포함된 데이터를 변환할 수 있는 컨테이너를 기술하고, `Monad`는 side effect가 있는 프로그램의 인코딩을 기술한다는 것입니다.
그러나 하지만 이 설명은 완전하지 않습니다.
결국, `Option`은 `Functor`와 `Monad` 둘 다에 대한 인스턴스를 가지며, 동시에 선택적 값 *그리고* 값을 반환하지 못할 수 있는 계산을 나타냅니다.

From the perspective of data structures, `Option` is a bit like a nullable type or like a list that can contain at most one entry.
From the perspective of control structures, `Option` represents a computation that might terminate early without a result.
Typically, programs that use the `Functor` instance are easiest to think of as using `Option` as a data structure, while programs that use the `Monad` instance are easiest to think of as using `Option` to allow early failure, but learning to use both of these perspectives fluently is an important part of becoming proficient at functional programming.

데이터 구조의 관점에서, `Option`은 nullable type이나 최대 하나의 항목을 포함할 수 있는 리스트와 유사합니다.
제어 구조의 관점에서, `Option`은 결과를 반환하지 않고 일찍 종료될 수 있는 계산을 나타냅니다.
일반적으로, `Functor` 인스턴스를 사용하는 프로그램은 `Option`을 데이터 구조로 사용하는 것으로 생각하기가 가장 쉽고, `Monad` 인스턴스를 사용하는 프로그램은 `Option`을 조기 실패를 허용하도록 사용하는 것으로 생각하기가 가장 쉽지만, 이 두 관점 모두를 유창하게 사용하는 것을 배우는 것은 함수형 프로그래밍에 능숙해지는 중요한 부분입니다.

There is a deeper relationship between functors and monads.
It turns out that *every monad is a functor*.
Another way to say this is that the monad abstraction is more powerful than the functor abstraction, because not every functor is a monad.
Furthermore, there is an additional intermediate abstraction, called *applicative functors*, that has enough power to write many interesting programs and yet permits libraries that cannot use the `Monad` interface.
The type class `Applicative` provides the overloadable operations of applicative functors.
Every monad is an applicative functor, and every applicative functor is a functor, but the converses do not hold.

Functor와 Monad 사이에는 더 깊은 관계가 있습니다.
*모든 Monad는 Functor입니다*.
이를 다르게 표현하면, Monad 추상화가 Functor 추상화보다 더 강력하다는 것입니다. 왜냐하면 모든 Functor가 Monad인 것은 아니기 때문입니다.
더욱이, *applicative functor*라고 불리는 추가적인 중간 추상화가 있으며, 이는 많은 흥미로운 프로그램을 작성할 수 있을 만큼 충분한 힘을 가지면서도 `Monad` 인터페이스를 사용할 수 없는 라이브러리를 허용합니다.
type class `Applicative`는 applicative functor의 오버로드 가능한 연산들을 제공합니다.
모든 Monad는 applicative functor이고, 모든 applicative functor는 Functor이지만, 역은 성립하지 않습니다.

1. [5.1. Structures and Inheritance](5-1-structures-and-inheritance/)
2. [5.2. Applicative Functors](5-2-applicative-functors/)
3. [5.3. The Applicative Contract](5-3-the-applicative-contract/)
4. [5.4. Alternatives](5-4-alternatives/)
5. [5.5. Universes](5-5-universes/)
6. [5.6. The Complete Definitions](5-6-the-complete-definitions/)
7. [5.7. Summary](5-7-summary/)
