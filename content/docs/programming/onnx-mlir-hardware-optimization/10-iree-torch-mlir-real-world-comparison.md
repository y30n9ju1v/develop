---
title: "10. 실전 비교: 이 시리즈의 파이프라인이 IREE·torch-mlir에서는 어떻게 구현되어 있는가"
date: 2026-07-14T00:00:00+09:00
draft: false
tags: ["mlir", "onnx", "deep-learning", "compiler", "iree", "torch-mlir"]
categories: ["programming"]
description: "1~7편에서 Conv-BN-Relu 예제로 따라간 onnx → linalg → vector → 하드웨어 파이프라인이, 실제 오픈소스 컴파일러인 IREE와 torch-mlir에서는 어떤 이름의 dialect와 pass로 구현되어 있는지 대조합니다."
---

> [IREE 공식 문서](https://iree.dev/reference/mlir-dialects/Flow/)의 flow/stream/hal dialect 설명과 [IREE MLIR/Linalg 튜토리얼](https://iree.dev/community/blog/2024-01-29-iree-mlir-linalg-tutorial/)을 참고해 작성했습니다.

---

## 1. 이 글의 목적: "우리가 만든 장난감 파이프라인"과 "진짜 컴파일러"의 대응 관계

1편부터 7편까지 이 시리즈는 **onnx → linalg → vector → GPU/NPU**라는 다단계 dialect 스택을, Conv-BatchNorm-Relu라는 단순한 예제 하나로 처음부터 끝까지 따라갔습니다. 이건 실전 컴파일러의 축소 모형입니다. 이 글은 그 축소 모형이 실제 오픈소스 프로젝트인 **torch-mlir**(PyTorch 프론트엔드)과 **IREE**(엔드투엔드 컴파일러/런타임)에서 어떤 이름의 dialect와 pass로 실제 구현되어 있는지 대조표를 만듭니다. 목적은 코드를 그대로 베끼는 게 아니라, **이 시리즈에서 배운 개념이 실전 코드베이스를 읽을 때 어디를 봐야 하는지 알려주는 지도**를 만드는 것입니다.

---

## 2. torch-mlir: "onnx dialect" 자리에 오는 것

이 시리즈의 [2편](../02-importing-onnx-and-shape-inference/)은 ONNX protobuf를 `onnx` dialect 오퍼레이션으로 들여오는 과정을 다뤘습니다. PyTorch에서 직접 모델을 가져오고 싶다면 이 자리에 오는 게 **torch-mlir**입니다.

- PyTorch 모델은 먼저 **`torch` dialect**로 들어옵니다 — `torch.aten.conv2d`처럼, PyTorch의 ATen 연산자 하나하나가 거의 그대로 대응하는 오퍼레이션이 됩니다. 이건 이 시리즈의 `onnx` dialect와 같은 역할(원본 프레임워크의 연산자를 최대한 그대로 옮겨오는 "입구" dialect)입니다.
- 이후 torch-mlir은 이걸 **StableHLO** 또는 **`linalg`** dialect로 낮춥니다. StableHLO는 XLA 계열 컴파일러들이 공유하는 중간 표현이고, 이 시리즈의 [3편](../03-graph-level-optimization/)이 다룬 그래프 수준 최적화(연산 융합, 상수 접기)의 상당 부분이 StableHLO 단계 또는 `linalg`로 낮추는 과정에서 일어납니다.

즉 이 시리즈의 `onnx → linalg` 흐름은 torch-mlir에서는 `torch → (StableHLO) → linalg` 흐름으로 대응됩니다 — 입구가 되는 프레임워크별 dialect만 다를 뿐, "프레임워크 고유 표현을 최대한 빨리 공통 중간 표현(`linalg`)으로 정규화한다"는 설계 목표는 동일합니다.

---

## 3. IREE: [4~6편]의 자리에 오는 flow/stream/hal 세 단계

IREE는 `linalg`를 받아들인 **이후의 파이프라인**이 이 시리즈보다 훨씬 세분화되어 있습니다. 이 시리즈의 [4편](../04-lowering-to-linalg-and-tiling/)~[6편](../06-hardware-backend-lowering/)이 뭉뚱그려 다룬 "타일링 → 벡터화 → 하드웨어별 코드 생성"을, IREE는 **flow → stream → hal** 세 개의 독립된 dialect로 명시적으로 분리합니다.

| IREE dialect | 이 시리즈에서 가장 가까운 개념 | 실제로 하는 일 |
|---|---|---|
| **flow** | [3편](../03-graph-level-optimization/)의 연산 융합과 비슷하지만 스케줄링 단위가 다름 | 함께 실행해도 안전하고 효율적인 연산들을 묶어 **dispatch region**(하나의 커널로 실행될 단위)으로 만든다. "가능한 한 많이 묶으려 시도"하지만, 타겟 백엔드에 따라 하나의 dispatch로 묶지 못하는 경우도 있다. |
| **stream** | [4편](../04-lowering-to-linalg-and-tiling/)의 버퍼화, [8편](../08-bufferization-and-memory-planning/)의 메모리 재사용 결정과 같은 층위 | dispatch region들을 **비동기 스케줄링 단위**로 명시화한다 — 어떤 작업을 어느 디바이스(affinity)에서 실행할지 정하고, 텐서를 타겟 특화 형태로 인코딩하며, `!stream.resource` 타입으로 버퍼 크기를 심볼릭하게 추적하면서 동시 실행 가능한 작업을 스케줄링한다. |
| **hal** | [6편](../06-hardware-backend-lowering/)의 GPU/NPU별 최종 코드 생성 | Hardware Abstraction Layer — `!hal.device` 큐와 `!hal.buffer` 같은 실제 버퍼·디바이스 자원을 다루는 단계로 낮춘다. 이 단계 이후에야 비로소 "이 작업을 CPU 스레드 풀에서 돌릴지, Vulkan/SPIR-V GPU 커널로 돌릴지"가 실제 코드로 확정된다. |

이 세 단계 분리가 이 시리즈의 단순화된 설명과 다른 점은, **"무엇을 계산하는가"(linalg)**, **"언제·어디서 실행하는가"(flow/stream)**, **"실제 하드웨어 자원을 어떻게 다루는가"(hal)**를 서로 다른 dialect로 명시적으로 갈라놓았다는 것입니다. 이 시리즈의 6편은 이 세 관심사를 한 편 안에서 뭉뚱그려 다뤘지만, 실전 컴파일러는 이걸 각각 별도로 최적화할 수 있도록 IR 레벨에서부터 분리해둔 것입니다 — 예를 들어 "어느 dispatch region을 어느 디바이스에 배정할지"(stream의 문제)는 "그 디바이스에서 실제 커널 코드를 어떻게 생성할지"(hal 이후의 문제)와 완전히 독립적으로 바꿀 수 있습니다.

---

## 4. 왜 이렇게 나뉘어 있는가: 멀티 디바이스가 진짜 이유다

이 시리즈는 예제 하나가 **하나의 디바이스**(GPU 또는 하나의 NPU)에서 실행된다고 가정했습니다. 하지만 실전 배포 환경은 종종 **CPU + GPU**, 또는 **여러 개의 가속기**를 동시에 쓰는 이기종 구성입니다. IREE가 flow/stream/hal을 분리한 근본적인 이유가 여기 있습니다 — "이 dispatch region을 어느 디바이스에 배정하고 어떻게 스케줄링할지"라는 결정을, 특정 디바이스의 코드 생성 세부사항과 독립적으로 내릴 수 있어야 여러 디바이스를 함께 쓰는 구성을 표현할 수 있기 때문입니다.

이 시리즈의 6편에서 다룬 "GPU 경로 vs 커스텀 NPU 경로"라는 이분법은, 이 이기종 스케줄링 문제의 가장 단순한 형태(디바이스가 하나뿐이라 스케줄링 결정이 거의 자명한 경우)라고 볼 수 있습니다.

---

## 5. 정리

- **torch-mlir**은 이 시리즈의 `onnx` dialect(2편) 자리에 `torch` dialect를 놓고, StableHLO를 거쳐 `linalg`로 정규화한다는 점에서 이 시리즈의 "onnx → linalg" 흐름과 같은 역할을 합니다.
- **IREE**는 이 시리즈의 4~6편이 뭉뚱그린 "타일링 → 벡터화 → 하드웨어별 코드 생성"을 **flow(무엇을 묶어 실행할지) → stream(언제·어느 디바이스에서 스케줄링할지) → hal(실제 버퍼·디바이스 자원을 어떻게 다룰지)** 세 dialect로 명시적으로 분리합니다.
- 이 분리의 근본 동기는 **멀티 디바이스 스케줄링**입니다 — 6편이 다룬 "GPU 또는 NPU 중 하나"라는 단순한 상황은, 여러 디바이스를 함께 쓰는 실전 배포 환경의 가장 쉬운 특수 케이스에 해당합니다.
- 이 시리즈의 개념(연산 융합, 타일링, 버퍼 재사용, 하드웨어별 최종 코드 생성)은 이름과 분리 방식만 다를 뿐, 실전 컴파일러 어디에나 형태를 바꿔 존재합니다 — 이 대응표가 그 실제 코드베이스를 읽기 시작할 때의 지도가 되길 바랍니다.
