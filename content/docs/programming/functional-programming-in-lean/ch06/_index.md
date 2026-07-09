---
title: "Ch.6: 모나드 트랜스포머"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Ch.6: 모나드 트랜스포머"
---

# 6. Monad Transformers

A monad is a way to encode some collection of side effects in a pure language.
Different monads provide different effects, such as state and error handling.
Many monads even provide useful effects that aren't available in most languages, such as nondeterministic searches, readers, and even continuations.

Monad는 순수 언어에서 부작용을 인코딩하는 방법입니다. 다양한 Monad는 상태 및 오류 처리와 같은 다양한 효과를 제공합니다. 많은 Monad는 비결정적 검색, Reader, 그리고 Continuation과 같이 대부분의 언어에서 사용할 수 없는 유용한 효과도 제공합니다.

A typical application has a core set of easily testable functions written without monads paired with an outer wrapper that uses a monad to encode the necessary application logic.
These monads are constructed from well-known components.

일반적인 애플리케이션은 Monad 없이 작성된 쉽게 테스트 가능한 핵심 함수 집합과 필요한 애플리케이션 로직을 인코딩하기 위해 Monad를 사용하는 외부 래퍼로 구성됩니다. 이러한 Monad는 잘 알려진 구성 요소로부터 구성됩니다.
For example:

* Mutable state is encoded with a function parameter and a return value that have the same type
* Error handling is encoded by having a return type that is similar to `Except`, with constructors for success and failure
* Logging is encoded by pairing the return value with the log

* 변경 가능한 상태는 함수 매개변수와 동일한 유형의 반환 값으로 인코딩됩니다
* 오류 처리는 성공과 실패를 위한 생성자가 있는 `Except`와 유사한 반환 유형을 갖음으로써 인코딩됩니다
* 로깅은 반환 값을 로그와 쌍을 이루어 인코딩됩니다

Writing each monad by hand is tedious, however, involving boilerplate definitions of the various type classes.
Each of these components can also be extracted to a definition that modifies some other monad to add an additional effect.
Such a definition is called a *monad transformer*.
A concrete monad can be build from a collection of monad transformers, which enables much more code re-use.

각 Monad를 직접 작성하는 것은 지루하고, 타입 클래스 보일러플레이트가 많이 필요합니다. 각 구성 요소는 다른 Monad를 감싸 추가 효과를 더하는 정의로 추출할 수 있습니다. 이런 정의를 *모나드 트랜스포머(monad transformer)*라고 합니다. 구체적인 Monad를 모나드 트랜스포머 조합으로 구성하면 코드 재사용성이 크게 높아집니다.

1. [6.1. Combining IO and Reader](6-1-combining-io-and-reader/)
2. [6.2. A Monad Construction Kit](6-2-a-monad-construction-kit/)
3. [6.3. Ordering Monad Transformers](6-3-ordering-monad-transformers/)
4. [6.4. More do Features](6-4-more-do-features/)
5. [6.5. Additional Conveniences](6-5-additional-conveniences/)
6. [6.6. Summary](6-6-summary/)
