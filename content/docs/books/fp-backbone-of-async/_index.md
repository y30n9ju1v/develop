---
title: "함수형 프로그래밍으로 보는 비동기의 근간"
---

`await`는 사실 Monad의 `flatMap`이고, `asyncio.gather`는 Applicative Functor의 철학이라는 것 — 우리가 매일 쓰는 비동기 기술들이 50년 전 함수형 프로그래밍 위에서 탄생했다는 사실을 따라가는 책입니다. 범주론 강의가 아니라, 비동기 코드의 복잡성과 씨름하던 파이썬 개발자의 시선에서 "왜 이 개념이 필요해지는가"를 발견해나가는 방식으로 씁니다.

## 목차

0. **[서문: 비동기 시대의 프로그래머를 위하여](00-preface/)**

**1부: 기초 — 함수형 사고의 토대**

1. **[함수형 사고란 무엇인가: 프로그래밍 패러다임의 전환](01-functional-thinking/)**
2. **[비동기 프로그래밍이 필요한 이유](02-why-async/)**

**2부: 핵심 추상화 — 컨텍스트와 합성**

3. **[Functor: 컨텍스트 안의 값을 다루는 법](03-functor/)**
4. **[Monad: 비동기 작업을 우아하게 연결하는 비밀](04-monad/)**
5. **[에러 처리: 실패를 타입으로 만들기](05-error-handling-as-types/)**
6. **[동시성과 병렬성: 독립적인 작업을 효율적으로](06-concurrency-and-parallelism/)**
7. **[Reactive Programming: 시간에 걸친 값들의 스트림](07-reactive-programming/)**

**3부: 실전 적용 — 아키텍처와 도구**

8. **[실전 패턴: 비동기 시스템의 함수형 아키텍처](08-practical-patterns/)**
9. **[타입 시스템과 함께하는 함수형 비동기](09-type-systems-and-fp/)**
10. **[테스팅: 비동기 코드를 신뢰할 수 있게](10-testing-async-code/)**
11. **[성능과 디버깅: 비동기 코드 최적화하기](11-performance-and-debugging/)**

**4부: 미래를 향하여**

12. **[미래를 향하여: async/await의 비밀과 Effect System](12-toward-the-future/)**
