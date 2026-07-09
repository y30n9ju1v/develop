---
title: "Ch.4: 모나드"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Ch.4: 모나드"
---

# 4. Monads

In C# and Kotlin, the `?.` operator is a way to look up a property or call a method on a potentially-null value.
If the receiver is `null`, the whole expression is null.
Otherwise, the underlying non-`null` value receives the call.
Uses of `?.` can be chained, in which case the first `null` result terminates the chain of lookups.
Chaining null-checks like this is much more convenient than writing and maintaining deeply nested `if`s.

C#과 Kotlin에서 `?.` 연산자는 null일 수 있는 값의 속성을 조회하거나 메서드를 호출하는 방법입니다. 수신자가 `null`이면 전체 식은 null입니다. 그렇지 않으면 기본 null이 아닌 값이 호출을 수신합니다. `?.` 사용은 연쇄될 수 있으며, 이 경우 첫 번째 `null` 결과가 조회 체인을 종료합니다. 이런 식으로 null 체크를 연쇄시키는 것은 깊게 중첩된 `if`를 작성하고 유지하는 것보다 훨씬 더 편리합니다.

Similarly, exceptions are significantly more convenient than manually checking and propagating error codes.
At the same time, logging is easiest to accomplish by having a dedicated logging framework, rather than having each function return both its log results and its return value.
Chained null checks and exceptions typically require language designers to anticipate this use case, while logging frameworks typically make use of side effects to decouple code that logs from the accumulation of the logs.

마찬가지로 예외는 오류 코드를 수동으로 확인하고 전파하는 것보다 훨씬 더 편리합니다. 동시에 로깅은 각 함수가 로그 결과와 반환 값을 모두 반환하는 것보다 전용 로깅 프레임워크를 사용하여 가장 쉽게 수행됩니다. 연쇄된 null 체크와 예외는 일반적으로 언어 설계자가 이 사용 사례를 예상해야 하는 반면, 로깅 프레임워크는 일반적으로 부작용을 사용하여 로깅하는 코드를 로그 축적과 분리합니다.

1. [4.1. The Monad Contract](4-1-one-api-many-applications/)
2. [4.2. The Monad Type Class](4-2-the-monad-type-class/)
3. [4.3. Example: Arithmetic in Monads](4-3-example-arithmetic-in-monads/)
4. [4.4. do-Notation for Monads](4-4-do-notation-for-monads/)
5. [4.5. The IO Monad](4-5-the-io-monad/)
6. [4.6. Additional Conveniences](4-6-additional-conveniences/)
7. [4.7. Summary](4-7-summary/)
