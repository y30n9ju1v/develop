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
