---
title: "9. 양자화 딥다이브: quant dialect과 정수 산술로의 변환"
date: 2026-07-14T00:00:00+09:00
draft: false
tags: ["mlir", "onnx", "deep-learning", "compiler", "quantization"]
categories: ["programming"]
description: "6편에서 '별도로 다룰 만큼 큰 주제'로 남겨둔 양자화를, MLIR의 quant dialect(!quant.uniform 타입, qcast/dcast/scast)와 QDQ 표현이 실제 정수 산술로 접히는 과정까지 깊게 파고듭니다."
---

> [6편](../06-hardware-backend-lowering/)에서 "양자화는 그 자체로 다른 논의를 필요로 할 만큼 큰 주제"라며 남겨둔 부분을 이 글이 이어서 다룹니다. [MLIR 공식 quant dialect 문서](https://mlir.llvm.org/docs/Dialects/QuantDialect/)를 참고해 작성했습니다.

---

## 1. 6편에서 남겨둔 질문: "스케일과 제로포인트, 그다음은?"

[6편](../06-hardware-backend-lowering/)에서는 양자화를 "계산 자체의 결과가 미세하게 달라지는 근사"라고 소개하고, `실제값 = scale × (양자화값 - 제로포인트)`라는 관계식과, 이 스케일 값을 정하려면 데이터 분포를 관찰해야 한다는 점까지 짚었습니다. 그런데 그 스케일 값을 IR 안에 어떻게 표현하고, 그 표현이 최종적으로 어떻게 진짜 int8 곱셈-누산 명령으로 바뀌는지는 다루지 않았습니다. 이 글이 그 간극을 채웁니다.

---

## 2. `!quant.uniform`: 스케일과 제로포인트를 타입 안에 붙여넣기

MLIR의 **quant dialect**는 양자화된 값을 별도의 정수 텐서로 흩어놓지 않고, **타입 자체에 양자화 정보를 붙입니다**. 핵심 타입이 `!quant.uniform`입니다.

```mlir
// storage type: i8, expressed type: f32, scale: 0.0078, zero point: 0
%conv_out : tensor<1x64x56x56x!quant.uniform<i8:f32, 0.0078:0>>
```

이 타입 하나가 "이 텐서는 원래 `f32` 값을 표현하려는 것이었지만, 실제로는 `i8`로 저장되어 있고, `실제값 = 0.0078 × (저장값 - 0)`이라는 관계로 복원할 수 있다"는 정보 전체를 담습니다. 이렇게 **타입 시스템에 양자화 파라미터를 얹는 방식**의 장점은, Conv나 MatMul 같은 연산의 오퍼레이션 정의 자체는 그대로 두고 피연산자 타입만 바꿔 끼우면 되기 때문에, 3~5편에서 다룬 융합·타일링·벡터화 패스가 양자화 여부와 무관하게 대부분 그대로 재사용된다는 점입니다.

### 2-1. Per-Channel 양자화: 채널마다 다른 스케일

Conv 레이어의 출력 채널마다 값의 분포 범위가 크게 다른 경우가 흔합니다. 이럴 때 채널 전체에 스케일 하나만 쓰면(per-tensor) 분포가 좁은 채널은 양자화 해상도를 낭비하게 됩니다. `UniformQuantizedPerAxisType`은 **채널마다 별도의 스케일·제로포인트 배열**을 갖도록 확장한 타입입니다 — 어떤 축(quantized dimension)을 기준으로 채널을 나눌지도 함께 지정합니다. [6편](../06-hardware-backend-lowering/)에서 다룬 Conv 예제라면, 출력 채널 축(예: 64개 채널)마다 다른 스케일을 쓰는 것이 정확도 손실을 크게 줄이는 실무 표준 선택입니다.

---

## 3. `qcast`/`dcast`/`scast`: 부동소수점 세계와 정수 세계를 오가는 세 가지 변환

quant dialect는 타입 변환을 위한 세 개의 연산을 정의합니다.

| 연산 | 방향 | 의미 |
|---|---|---|
| `quant.qcast` | `f32` → `!quant.uniform` | "이 부동소수점 값을 지금부터 양자화된 값으로 취급한다"고 선언 (실제 반올림은 아직 없음) |
| `quant.dcast` | `!quant.uniform` → `f32` | 양자화된 값을 다시 부동소수점 근사값으로 복원 |
| `quant.scast` | `!quant.uniform` ↔ 저장 타입(`i8`) | 양자화 타입과 그 밑에 깔린 순수 정수 타입 사이를 오가기(값 자체는 재해석일 뿐 변하지 않음) |

여기서 `qcast`와 `dcast`가 그래프 안에서 **연달아** 나타나는 패턴이 실무에서 아주 흔합니다 — ONNX 익스포터가 양자화 인식 학습(QAT)이나 post-training quantization 툴에서 나온 그래프를 그대로 가져오면, 각 연산 앞뒤에 "양자화했다가 바로 복원하는" `dcast(qcast(x))` 쌍이 잔뜩 붙어 있는 경우가 많습니다. 이걸 흔히 **QDQ(Quantize-DeQuantize) 표현**이라고 부릅니다.

```mlir
// QDQ 표현: Conv 앞뒤로 양자화/역양자화가 명시적으로 붙어 있다
%q_in  = quant.qcast %input  : tensor<1x64x56x56xf32> to tensor<1x64x56x56x!quant.uniform<i8:f32, 0.0078:0>>
%d_in  = quant.dcast %q_in   : tensor<...!quant.uniform<...>> to tensor<1x64x56x56xf32>
%conv  = "onnx.Conv"(%d_in, %weight) : (...) -> tensor<1x64x56x56xf32>
%q_out = quant.qcast %conv   : tensor<1x64x56x56xf32> to tensor<...!quant.uniform<...>>
```

이 표현은 **정확도 시뮬레이션에는 유용**합니다 — `dcast(qcast(x))`를 fp32 그래프에 그대로 끼워 넣고 시뮬레이션하면, "이 지점에서 양자화하면 최종 정확도가 얼마나 떨어지는가"를 실제 정수 연산 없이도 미리 확인할 수 있기 때문입니다. 하지만 **이 상태 그대로는 하드웨어 가속이 전혀 일어나지 않습니다** — Conv 연산 자체는 여전히 `f32` 입력을 받는 `onnx.Conv`이기 때문에, `qcast`/`dcast` 쌍은 그냥 값을 한 번 깎았다가 되돌리는 잉여 연산일 뿐입니다.

---

## 4. QDQ를 정수 산술로 접기: 진짜 최적화는 여기서 시작된다

실제 하드웨어 가속을 얻으려면, 컴파일러가 `dcast(qcast(x))` 패턴을 인식해서 **Conv 자체를 정수 입력을 받는 연산으로 다시 쓰는** 패스가 필요합니다.

```mlir
// 접힌 이후: Conv가 직접 i8 텐서를 받는다
%q_in  = quant.qcast %input : tensor<1x64x56x56xf32> to tensor<...!quant.uniform<i8:f32,0.0078:0>>
%i_in  = quant.scast %q_in  : tensor<...!quant.uniform<...>> to tensor<1x64x56x56xi8>
%i_out = "onnx.Conv"(%i_in, %i_weight) : (tensor<...xi8>, tensor<...xi8>) -> tensor<...xi32>
// int8 x int8 누산은 오버플로를 피하려고 i32로 쌓인다
```

여기서 두 가지가 동시에 일어납니다.

1. **`scast`로 양자화 타입에서 저장 타입(`i8`)으로 재해석**해서, 뒤따르는 Conv가 실제로 정수 연산으로 낮춰질 수 있게 합니다.
2. **누산 결과의 타입이 `i8`이 아니라 `i32`**가 됩니다 — int8 곱 int8은 결과값이 커질 수 있어서, 여러 항을 더하는 누산 과정에서 오버플로를 막으려면 더 넓은 정수 타입에 누적해야 하기 때문입니다. 이 `i32` 누산 결과를 다시 int8로 되돌리려면(다음 레이어 입력으로 쓰기 위해) 별도의 **재양자화(requantization)** 연산이 필요합니다 — 새 스케일에 맞춰 나누고 반올림하는 과정입니다.

이 "QDQ 쌍 인식 → 연산을 정수 버전으로 재작성 → 누산 폭 확장 → 재양자화 삽입"의 흐름이 실제 프로덕션 양자화 컴파일러(TensorRT, TFLite, ONNX Runtime의 양자화 실행기 등)가 공통으로 거치는 패턴입니다. [3편](../03-graph-level-optimization/)에서 다룬 연산 융합과 비슷하게, 이 재작성도 **패턴 매칭 기반**으로 이루어집니다 — 다만 대상이 되는 패턴이 "곱셈 뒤에 오는 덧셈"이 아니라 "dcast 뒤에 오는 연산, 그리고 그 결과를 다시 감싸는 qcast"라는 점이 다릅니다.

---

## 5. 이 재작성이 5~6편의 파이프라인과 만나는 지점

일단 Conv가 `i8` 입력과 `i32` 누산 출력을 갖는 형태로 재작성되고 나면, [4편](../04-lowering-to-linalg-and-tiling/)의 `linalg.generic`으로 낮추기, [5편](../05-vectorization/)의 벡터화는 **타입만 `i8`/`i32`로 바뀌었을 뿐 구조는 그대로** 적용됩니다 — 타일링 크기를 정하는 논리, 벡터 폭에 맞춰 접는 논리 자체는 정수든 부동소수점이든 동일합니다. 다만 하드웨어에 따라 갈리는 지점이 하나 있습니다.

- **GPU**: 최신 GPU의 텐서 코어는 fp16/bf16뿐 아니라 int8 MAC도 네이티브로 지원하는 경우가 많아서, `i8 × i8 → i32` 패턴을 텐서 코어 명령으로 그대로 매핑할 수 있습니다.
- **커스텀 NPU**: [6편](../06-hardware-backend-lowering/)에서 다룬 것처럼 애초에 고정 크기 int8 MAC 배열을 염두에 두고 설계된 경우가 많아서, 오히려 양자화된 형태가 하드웨어의 "네이티브 언어"에 가깝고, fp32 형태가 우회 경로에 가깝습니다.

즉 양자화는 5편까지의 파이프라인을 새로 만드는 게 아니라, **그 파이프라인이 다루는 타입을 바꿔치기하고, 그 바꿔치기를 안전하게 수행하는 재작성 패스 하나를 앞단에 추가하는 것**입니다.

---

## 6. 정리

- MLIR은 스케일·제로포인트를 별도 텐서가 아니라 **`!quant.uniform` 타입 자체**에 붙여서 표현하고, `UniformQuantizedPerAxisType`으로 채널별 스케일(per-channel quantization)까지 표현합니다.
- `qcast`/`dcast`/`scast` 세 연산이 부동소수점·양자화 타입·저장 타입 사이를 오가며, 실무에서 흔한 **QDQ 표현**(정확도 시뮬레이션용 `dcast(qcast(x))` 쌍)을 만듭니다.
- QDQ 표현 자체는 하드웨어 가속을 만들지 않고, 이를 인식해 **연산을 정수 입력/더 넓은 정수 누산 타입으로 재작성**하고 **재양자화를 삽입**하는 패스가 진짜 최적화입니다.
- 이 재작성 이후에는 [4편](../04-lowering-to-linalg-and-tiling/)·[5편](../05-vectorization/)의 타일링·벡터화 구조가 타입만 바뀐 채 그대로 재사용되고, 어떤 하드웨어를 타겟하느냐에 따라 int8 표현이 우회 경로가 될지 네이티브 경로가 될지가 갈립니다.
