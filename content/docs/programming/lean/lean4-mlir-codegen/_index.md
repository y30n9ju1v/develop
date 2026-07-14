---
title: "Lean4로 MLIR 만들기"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "mlir", "compiler"]
categories: ["programming"]
description: "Lean4의 elaboration으로 안전성이 증명된 IR을 설계하고, 그 IR을 MLIR로 방출해 최종적으로 C 또는 SystemVerilog까지 뽑아내는 파이프라인을 이론적으로 정리하는 시리즈입니다."
---

Lean4의 타입 시스템과 elaboration으로 안전성이 증명된 내부 IR을 설계하고, 이를 MLIR 텍스트로 방출한 뒤 MLIR의 dialect conversion과 EmitC를 거쳐 최종 C 코드까지, 또는 CIRCT를 거쳐 SystemVerilog까지 뽑아내는 파이프라인을 다루는 시리즈입니다. 실전 코드보다 각 단계의 이론적 근거 — 왜 이런 구조가 성립하는지, 무엇을 신뢰하고 무엇을 검증하는지 — 에 집중합니다. MLIR을 처음 접한다면 0편부터, 이미 MLIR의 기본 개념(dialect, operation, attribute)에 익숙하다면 1편부터 읽어도 무방합니다.

## 읽기 순서

0. **[MLIR이란 무엇인가](00-what-is-mlir/)** — 공통 중간 표현(IR)이 왜 필요한지, MLIR이 dialect·operation·region·attribute라는 확장 가능한 단위로 그 문제를 어떻게 푸는지
1. **[왜 Lean4로 MLIR을 만드는가](01-why-lean4-for-mlir/)** — elaboration이 컴파일러 프론트엔드와 구조적으로 닮은 이유, MLIR을 중간 타겟으로 삼는 이론적 이유
2. **[안전성이 타입에 인코딩된 내부 IR 설계](02-safety-encoded-ir/)** — 정제 타입(`Fin n`)으로 위험한 프로그램을 표현 불가능하게 만들고 증명 의무를 자동 생성·해소하는 메커니즘, 그리고 이 전략이 자원 소유권 문제에는 왜 그대로 통하지 않는지
3. **[MLIR 텍스트 방출과 커스텀 dialect 설계](03-emitting-mlir-text/)** — operation/region/block/attribute 모델과, 안전성 증명을 attribute로 실어 보내는 원리
4. **[MLIR 파이프라인과의 접합](04-mlir-pipeline-integration/)** — dialect conversion, EmitC, 그리고 Lean4와 MLIR C++ 인프라 사이의 신뢰 경계
5. **[번역 검증: 방출 코드 자체를 어떻게 믿을 것인가](05-translation-validation/)** — 번역 검증, 증명 운반 코드(PCC), 차등 테스트로 TCB로 지목된 attribute 방출 코드의 신뢰성을 실질적으로 좁히는 방법
6. **[같은 프론트엔드, 다른 타겟: CIRCT로 SystemVerilog 만들기](06-circt-systemverilog/)** — C 대신 하드웨어를 타겟으로 삼을 때 실행 모델이 어떻게 바뀌는지, CIRCT의 hw/comb/seq/sv dialect 스택과 안전성 증명이 멀티플렉서 최적화·래치 추론 회피로 형태를 바꾸는 원리
7. **[실습: 실제로 돌아가는 최소 파이프라인으로 C 찍어보기](07-hands-on-c-emission/)** — MLIR/CIRCT 툴체인 설치 없이 Lean4 코드만으로 MLIR 텍스트와 C 소스를 실제로 찍어내고, 독립 검사기로 방출 코드의 버그를 잡아내는 최소 구현을 직접 돌려봅니다
8. **[실습: 같은 안전 정보로 SystemVerilog 찍어보기](08-hands-on-systemverilog-emission/)** — 7편과 같은 자료구조로, 멀티플렉서와 unique case/default 분기가 있는 SystemVerilog를 실제로 찍어내고 래치 추론 위험을 잡아내는 검사기를 Lean4로 구현합니다

## 더 깊게 파고들기

2편과 5편에서 "훨씬 큰 별도의 프로젝트"·다음 논의로 남겨둔 지점들을 깊게 파고들고, 세 번째 타겟으로 파이프라인을 한 번 더 확장합니다.

9. **[자원 소유권 딥다이브: 선형 타입을 elaboration 확장으로 직접 만들기](09-ownership-linear-types-deep-dive/)** — 변수 사용 횟수를 세는 elaboration 확장을 실제로 설계하고, 이 결과를 attribute로 실어 보내는 방법, 그리고 Rust 대여 검사기와 무엇이 같고 다른지 정리합니다.
10. **[SMT 기반 번역 검증 딥다이브: 검사기를 손으로 짜지 않는 방법](10-smt-translation-validation-deep-dive/)** — 두 프로그램의 의미를 논리식으로 인코딩해 SMT solver로 동등성을 자동 확인하는 접근과, 루프·재귀 앞에서 이 접근이 결국 PCC와 같은 종류의 힌트를 다시 요구하는 지점을 정리합니다.
11. **[실습: 세 번째 타겟으로 LLVM IR 찍어보기](11-hands-on-llvm-emission/)** — 7·8편과 같은 자료구조로, 고수준 제어 구조 없이 기본 블록과 분기·trap 명령만으로 안전성 검사를 표현하는 LLVM IR을 찍어내고, C·SystemVerilog·LLVM IR 세 타겟을 나란히 비교합니다.
