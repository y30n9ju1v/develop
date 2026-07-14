---
title: "ONNX 모델을 MLIR로 하드웨어에 맞게 최적화하기"
date: 2026-07-13T00:00:00+09:00
draft: false
tags: ["mlir", "onnx", "deep-learning", "compiler", "hardware-acceleration"]
categories: ["programming"]
description: "PyTorch/TensorFlow에서 export한 ONNX 그래프를 MLIR의 다단계 dialect 스택(onnx → linalg → vector → GPU/NPU)을 거쳐 특정 하드웨어에 맞게 최적화하는 파이프라인을, Conv-BatchNorm-Relu 예제 하나로 끝까지 따라가는 시리즈입니다."
---

ONNX로 export된 딥러닝 모델 그래프는 "무엇을 계산하는지"만 정의할 뿐, 특정 하드웨어에서 얼마나 빠르게 계산할지는 정의하지 않습니다. 이 시리즈는 그 간극을 MLIR이 어떻게 메우는지 — 연산 융합, 상수 접기, 레이아웃 변환, 타일링, 벡터화, 그리고 GPU/커스텀 가속기별 최종 코드 생성까지 — 를 **Conv → BatchNorm → Relu**라는 하나의 예제를 처음부터 끝까지 따라가며 정리합니다. 실전 프로덕션 코드보다 각 최적화가 왜 필요한지, 어떤 정보가 그 판단의 근거가 되는지에 집중합니다.

이 시리즈는 [Lean4로 MLIR 만들기](../lean/lean4-mlir-codegen/) 시리즈와 같은 MLIR 인프라를 다루지만 독립적으로 읽을 수 있습니다. MLIR의 dialect·operation·attribute 같은 기본 개념이 낯설다면 그 시리즈의 [0편: MLIR이란 무엇인가](../lean/lean4-mlir-codegen/00-what-is-mlir/)를 먼저 보는 것도 좋습니다.

## 읽기 순서

1. **[왜 ONNX 모델을 MLIR로 최적화하는가](01-why-onnx-and-mlir/)** — ONNX 그래프가 하드웨어 효율성 정보를 담지 못하는 이유, 최적화마다 필요한 추상화 수준이 달라 MLIR의 다단계 dialect 스택이 필요한 이유
2. **[ONNX를 MLIR로 들여오기: onnx dialect와 shape inference](02-importing-onnx-and-shape-inference/)** — ONNX protobuf가 onnx dialect 오퍼레이션으로 옮겨지는 과정과, 이후 모든 최적화의 전제 조건인 shape inference
3. **[그래프 수준 최적화](03-graph-level-optimization/)** — 연산 융합, 상수 접기, NCHW/NHWC 레이아웃 변환을 실제 패턴으로 확인
4. **[linalg dialect로 낮추기](04-lowering-to-linalg-and-tiling/)** — 반복문 구조가 드러나는 linalg.generic, 캐시 크기에 맞춘 타일링, 텐서에서 메모리로의 버퍼화
5. **[벡터화](05-vectorization/)** — 타일 안쪽 반복문이 하드웨어의 SIMD 폭에 맞춰 vector dialect 명령으로 접히는 과정
6. **[하드웨어별 최종 낮추기: GPU 커널과 커스텀 NPU 명령](06-hardware-backend-lowering/)** — 같은 벡터 표현이 GPU의 스레드 병렬성과 커스텀 가속기의 고정 크기 MAC 배열로 갈라지는 과정, 그리고 양자화가 더하는 새로운 결정
7. **[더 무거운 연산자: 대형 MatMul과 Attention의 최적화](07-heavier-operators-matmul-attention/)** — 다단계 타일링, softmax의 reduction 병렬화, FlashAttention 스타일의 공격적 융합, 동적 shape, 텐서 코어 매핑까지 — 1~6편의 원리가 더 무거운 연산자로 어떻게 확장되는지

## 더 깊게 파고들기

6편과 4편에서 "별도로 다룰 만큼 큰 주제"로 남겨둔 지점들을 깊게 파고들고, 이 시리즈의 축소 모형이 실전 오픈소스 컴파일러에서는 어떻게 구현되어 있는지 대조합니다.

8. **[버퍼화 딥다이브: One-Shot Bufferize와 메모리 재사용 결정](08-bufferization-and-memory-planning/)** — One-Shot Bufferize가 텐서 SSA use-def 체인을 분석해 in-place 재사용을 안전하게 결정하는 원리와, Destination-Passing Style이 이 분석을 값싸게 만드는 이유를 정리합니다.
9. **[양자화 딥다이브: quant dialect과 정수 산술로의 변환](09-quantization-deep-dive/)** — MLIR의 `!quant.uniform` 타입과 per-channel 양자화, `qcast`/`dcast`/`scast`가 만드는 QDQ 표현, 그리고 이 표현이 실제 정수 곱셈-누산 연산으로 재작성되는 과정을 정리합니다.
10. **[실전 비교: IREE·torch-mlir에서는 어떻게 구현되어 있는가](10-iree-torch-mlir-real-world-comparison/)** — 이 시리즈의 onnx→linalg→하드웨어 파이프라인이 torch-mlir의 `torch`/StableHLO dialect, IREE의 flow/stream/hal dialect로 실제 어떻게 대응되는지 정리합니다.
