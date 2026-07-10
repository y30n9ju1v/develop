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
