---
title: "Verified SICP"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["sicp", "lean", "lean4"]
categories: ["programming"]
description: "SICP의 아이디어를 Lean 4 코드로 다시 짜 보는 시리즈"
---

*Structure and Interpretation of Computer Programs*(SICP)의 아이디어를 챕터·절 순서대로 따라가며, 모든 Scheme 코드를 Lean 4로 다시 작성하는 시리즈입니다. 정적 타입 시스템과 종료성 증명 요구가 SICP의 원래 논의에 무엇을 더하고, 무엇을 바꾸는지에 초점을 둡니다.

## 시리즈 목록

1. **[1.1. 프로그래밍의 요소](1-1-elements-of-programming/)** — 표현식과 조합, 이름 짓기, 조합의 평가 규칙, 복합 절차, 치환 모델, 조건문, 뉴턴법으로 제곱근 구하기, 블랙박스 추상화를 Lean으로 옮깁니다.
2. **[1.2. 절차와 절차가 만들어내는 프로세스](1-2-procedures-and-processes/)** — 선형 재귀/반복, 트리 재귀, 증가 차수, 거듭제곱, 최대공약수, 소수 판정을 Lean으로 옮기며, Lean의 종료성 검사기가 어떤 재귀는 자동으로 받아들이고 어떤 재귀는 `partial`을 요구하는지를 살펴봅니다.
3. **[1.3. 고차 절차로 추상화 정식화하기](1-3-higher-order-procedures/)** — `sum` 추상화, `lambda`/`let`, 이분법과 고정점 탐색, 절차를 반환하는 절차, 뉴턴법, 일급 절차를 Lean의 `fun`/`let`과 함수 타입으로 옮깁니다.
4. **[2.1. 데이터 추상화 입문](2-1-introduction-to-data-abstraction/)** — 유리수 연산, `Prod` 쌍, 추상화 장벽, 데이터의 행동적 정의, 절차로서의 쌍, 구간 연산을 Lean의 `Prod`와 `structure` 두 가지 방식으로 옮깁니다.
5. **[2.2. 계층적 데이터와 닫힘 성질](2-2-hierarchical-data-and-closure/)** — 쌍의 닫힘 성질, 리스트와 트리, `map`/`filter`/`accumulate`로 조립하는 시퀀스 인터페이스를 Lean의 `List`와 구조적 재귀로 옮깁니다.
6. **[2.3. 기호 데이터](2-3-symbolic-data/)** — 인용, 기호 미분, 집합의 표현, 허프만 부호화 트리를 Lean의 귀납적 타입과 종료성 증명 관점에서 옮깁니다.
7. **[2.4. 추상 데이터의 다중 표현](2-4-multiple-representations-for-abstract-data/)** — 복소수의 직교/극좌표 표현, 타입 태그, 데이터 지향 프로그래밍을 Lean의 귀납 타입과 타입클래스로 옮깁니다.
8. **[2.5. 일반 연산을 가진 시스템](2-5-generic-operations/)** — 일반 산술 연산, 타입 태그와 데이터 지향 디스패치, 강제 변환, 타입의 계층, 다항식 예제를 Lean의 귀납 타입과 타입클래스로 옮기며, Scheme의 런타임 `put`/`get` 테이블이 Lean에서는 컴파일 시점 전수성 검사와 인스턴스 탐색으로 대체되는 지점을 살펴봅니다.
9. **[3.1. 배정과 지역 상태](3-1-assignment-and-local-state/)** — 지역 상태 변수, `set!`, 은행 계좌 객체, 참조 투명성의 붕괴를 Lean의 `IO.Ref`와 `IO` 모나드로 옮기며, 배정이 있는 절차와 없는 절차의 차이가 타입 시그니처에 `IO`가 나타나는지로 미리 드러나는 지점을 살펴봅니다.
10. **[3.2. 평가의 환경 모델](3-2-environment-model-of-evaluation/)** — 환경, 프레임, 클로저, 지역 상태, 내부 정의를 Lean의 클로저 표현과 `IO.Ref` 기반 가변 상태로 옮깁니다.
11. **[3.3. 가변 데이터로 모델링하기](3-3-modeling-with-mutable-data/)** — `set-car!`/`set-cdr!`로 만드는 가변 리스트, 큐, 테이블을 Lean의 `IO.Ref`와 순수 함수형 자료구조 두 갈래로 옮기며, 포인터 정체성을 유지하는 가변 버전과 상각 비용으로 정체성을 포기하는 순수 버전의 트레이드오프를 대조합니다.
12. **[3.4. 동시성: 시간이 중요해지다](3-4-concurrency/)** — 동시성이 낳는 시간 문제, 인터리빙, 시리얼라이저, 뮤텍스, 교착 상태를 Lean의 `IO.Ref`와 `Task`로 옮기며, `IO` 타입이 부수 효과의 존재는 알려주지만 그 내부 단계가 서로 끼어들 수 있는지는 알려주지 않는다는 한계를 짚습니다.
13. **[3.5. 스트림](3-5-streams/)** — 지연 평가, `delay`/`force`, 무한 스트림, 에라토스테네스의 체를 Lean의 `Thunk` 기반 지연 스트림과 `partial` 정의로 옮깁니다.
