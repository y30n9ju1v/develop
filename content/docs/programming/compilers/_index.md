---
title: "컴파일러 (MIT 6.035 기준)"
date: 2026-07-14T00:00:00+09:00
draft: false
tags: ["compilers", "mit-6035", "lexical-analysis", "parsing", "code-generation"]
categories: ["programming"]
description: "MIT 6.035(Computer Language Engineering)의 구성을 따라, 작은 언어 하나를 어휘 분석부터 최적화까지 끝까지 컴파일해보는 시리즈입니다."
---

MIT 6.035(Computer Language Engineering)의 컴파일러 강의가 다루는 순서 — 어휘 분석 → 구문 분석(하향식/상향식) → 의미 분석 → 중간 표현과 코드 생성 → 런타임과 가비지 컬렉션 → 최적화 — 를 따라갑니다. **MiniLang**이라는 정수·불리언·`if`/함수 호출만 있는 아주 작은 언어의 재귀 함수 하나를 시리즈 내내 컴파일해 나가며, 각 단계가 앞 단계의 결과물을 받아 무엇을 새로 결정하는지에 집중합니다.

[계산 이론](../theory-of-computation/) 시리즈가 다룬 MIT 18.404J와 같은 학교의 강의로, 1편(어휘 분석)의 NFA/DFA와 Thompson 구성·부분집합 구성이 정확히 [계산 이론 2편](../theory-of-computation/02-nondeterminism-closure-properties-regular-expressions-to-finite-automata/)에서 증명한 "NFA와 DFA는 계산 능력이 동일하다"는 정리를 실전 도구(렉서 생성기)로 그대로 응용한 것입니다. 이 시리즈는 그 정리를 다시 증명하지 않고, 컴파일러 한 과목 안에서 어디에 어떻게 쓰이는지에 집중합니다.

## 읽기 순서

1. **[어휘 분석: 정규 표현식에서 DFA로](01-lexical-analysis/)** — 정규 표현식으로 토큰을 정의하고, Thompson 구성과 부분집합 구성으로 NFA·DFA를 만들어 실제로 문자열을 스캔하는 원리
2. **[하향식 구문 분석: CFG, 재귀 하강, LL(1)](02-parsing-top-down/)** — 문맥 자유 문법으로 문법을 정의하고, 모호함을 우선순위 계층으로 해소하며, 재귀 하강과 예측 파싱 테이블을 다룹니다
3. **[상향식 구문 분석: Shift-Reduce와 LR 파싱](03-parsing-bottom-up/)** — LL(1)보다 강력한 LR 파싱의 핸들·아이템 개념과, yacc/bison이 파싱 테이블을 자동 생성하는 원리
4. **[의미 분석: 심볼 테이블과 타입 검사](04-semantic-analysis/)** — 스코프별 심볼 테이블, AST를 재귀 순회하는 타입 검사, 재귀 함수를 위한 두 단계 처리
5. **[중간 표현과 스택 머신 코드 생성](05-intermediate-representation-stack-machine/)** — AST를 스택 기반 추상 머신 코드로 낮추는 재귀적 변환 규칙과 제어 흐름의 점프 변환
6. **[레지스터 머신 코드 생성과 런타임 조직](06-code-generation-register-machine/)** — 그래프 컬러링 기반 레지스터 할당, 스필, 활성화 레코드와 호출 규약
7. **[가비지 컬렉션: Mark-Sweep과 Copying](07-garbage-collection/)** — 도달 가능성, mark-sweep과 copying GC의 동작과 트레이드오프, 세대별 GC
8. **[최적화와 데이터플로우 분석](08-optimization-dataflow-analysis/)** — 지역 최적화(상수 접기, 죽은 코드 제거)와 CFG 전체에 걸친 liveness 등 데이터플로우 분석
