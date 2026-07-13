---
title: "2. ONNX를 MLIR로 들여오기: onnx dialect와 shape inference"
date: 2026-07-13T00:00:00+09:00
draft: false
tags: ["mlir", "onnx", "deep-learning", "compiler", "shape-inference"]
categories: ["programming"]
description: "ONNX 프로토콜 버퍼가 onnx dialect의 오퍼레이션으로 어떻게 옮겨지는지, 그리고 정적 shape가 왜 이후 모든 최적화의 전제 조건이 되는지를 Conv-BatchNorm-Relu 예제로 확인합니다."
---

[1편](../01-why-onnx-and-mlir/)에서 ONNX 그래프를 하드웨어에 맞게 최적화하려면 여러 추상화 수준의 dialect를 거쳐야 한다고 봤습니다. 이 글은 그 첫 단계 — ONNX 파일이 실제로 어떤 MLIR 텍스트로 들어오는지, 그리고 이 시리즈 전체를 통틀어 가장 조용하지만 가장 중요한 전제 조건인 **shape inference**를 다룹니다.

---

## 1. ONNX 파일의 실체: 프로토콜 버퍼로 직렬화된 그래프

`.onnx` 파일은 사람이 읽는 텍스트가 아니라 프로토콜 버퍼(protobuf)로 직렬화된 바이너리입니다. 이 안에는 대략 이런 정보가 들어 있습니다.

- **노드(node) 목록**: 오퍼레이터 이름(`Conv`, `BatchNormalization`, `Relu`), 입력/출력 텐서 이름, 오퍼레이터별 속성(attribute — 예: Conv의 `stride`, `pads`)
- **초기값(initializer)**: 가중치, bias처럼 학습이 끝난 뒤 고정된 상수 텐서
- **입출력 명세**: 모델 전체의 입력/출력 텐서 이름과 (선언은 되어 있지만 종종 불완전한) shape

이 protobuf를 MLIR로 들여오는 역할은 [onnx-mlir](https://onnx.ai/onnx-mlir/) 같은 프로젝트가 제공하는 **importer**가 담당합니다. 이 importer는 protobuf를 순회하며 각 ONNX 노드를 `onnx` dialect의 오퍼레이션 하나로 그대로 매핑합니다 — 아직 아무 최적화도 하지 않고, ONNX가 말한 그래프 구조를 MLIR의 어휘로 옮겨 적기만 합니다.

---

## 2. 우리 예제가 `onnx` dialect 텍스트로 옮겨진 모습

1편의 Conv → BatchNorm → Relu 그래프를 `onnx` dialect로 옮기면 이렇게 생겼습니다.

```mlir
func.func @block(%x: tensor<1x3x224x224xf32>) -> tensor<1x64x224x224xf32> {
  %w = "onnx.Constant"() {value = dense<...> : tensor<64x3x3x3xf32>} : () -> tensor<64x3x3x3xf32>
  %conv = "onnx.Conv"(%x, %w) {
    strides = [1, 1], pads = [1, 1, 1, 1], group = 1
  } : (tensor<1x3x224x224xf32>, tensor<64x3x3x3xf32>) -> tensor<1x64x224x224xf32>

  %scale = "onnx.Constant"() {value = dense<...> : tensor<64xf32>} : () -> tensor<64xf32>
  %bias  = "onnx.Constant"() {value = dense<...> : tensor<64xf32>} : () -> tensor<64xf32>
  %mean  = "onnx.Constant"() {value = dense<...> : tensor<64xf32>} : () -> tensor<64xf32>
  %var   = "onnx.Constant"() {value = dense<...> : tensor<64xf32>} : () -> tensor<64xf32>
  %bn = "onnx.BatchNormalization"(%conv, %scale, %bias, %mean, %var) {epsilon = 1.0e-5}
    : (tensor<1x64x224x224xf32>, tensor<64xf32>, tensor<64xf32>, tensor<64xf32>, tensor<64xf32>)
    -> tensor<1x64x224x224xf32>

  %relu = "onnx.Relu"(%bn) : (tensor<1x64x224x224xf32>) -> tensor<1x64x224x224xf32>
  return %relu : tensor<1x64x224x224xf32>
}
```

이 텍스트를 보면 ONNX 그래프와 거의 1:1로 대응한다는 걸 알 수 있습니다 — 노드 하나가 오퍼레이션 하나(`onnx.Conv`, `onnx.BatchNormalization`, `onnx.Relu`)로, 초기값(가중치)이 `onnx.Constant`로, ONNX의 attribute(`strides`, `pads`)가 MLIR의 attribute로 그대로 옮겨졌습니다. 아직 아무것도 합쳐지지 않았고, 아무 반복문도 드러나지 않았습니다 — 이건 의도된 것입니다. `onnx` dialect는 "ONNX가 말한 그래프 구조를 최대한 그대로 보존하는 첫 번째 정거장" 역할만 합니다.

---

## 3. 왜 shape가 전부 확정되어 있어야만 하는가

위 텍스트에서 모든 텐서 타입에 `1x64x224x224` 같은 **구체적인 숫자**가 박혀 있다는 점을 주목해야 합니다. 실제 ONNX 파일에는 이 shape 정보가 없거나(동적 배치 크기를 지원하기 위해 `batch` 축이 `?`로 남아 있는 경우가 흔합니다) 일부만 있는 경우가 많습니다.

문제는 3편에서 다룰 그래프 최적화도, 4편에서 다룰 타일링도 전부 **구체적인 숫자로서의 shape**를 요구한다는 것입니다.

- 연산 융합을 판단하려면 "Conv의 출력 shape와 BatchNorm이 기대하는 입력 shape가 정확히 맞아떨어지는가"를 확인해야 합니다.
- 타일링을 하려면 "이 축의 전체 크기가 224인데, 이걸 32씩 나눠서 처리한다"처럼 나눗셈 자체가 구체적인 숫자를 전제로 합니다.
- 레이아웃 변환(`NCHW` → `NHWC`)은 어느 축이 채널 축인지, 그 축의 크기가 몇인지 알아야 트랜스포즈 연산을 올바르게 삽입할 수 있습니다.

이 확정 작업을 **shape inference**라고 부릅니다. `onnx` dialect는 각 오퍼레이션이 "입력 shape가 주어지면 출력 shape를 계산하는 규칙"을 오퍼레이션 정의에 함께 등록해 둡니다 — 예를 들어 `onnx.Conv`는 "출력 크기 = (입력 크기 + 2×pad − 커널 크기) / stride + 1"이라는 규칙을 압니다. shape inference pass는 이 규칙을 그래프 전체에 앞에서부터 반복 적용하며, `tensor<?x?x?x?xf32>`처럼 물음표로 남아 있던 타입을 하나씩 구체적인 숫자로 채워 나갑니다.

```
입력: tensor<1x3x224x224xf32>  (구체적으로 알려짐)
   ↓ onnx.Conv의 shape 추론 규칙 적용
Conv 출력: tensor<1x64x224x224xf32>  (stride=1, pad=1 이므로 크기가 그대로 유지됨을 계산)
   ↓ onnx.BatchNormalization의 shape 추론 규칙 적용 (입력과 출력 shape가 항상 같음)
BatchNorm 출력: tensor<1x64x224x224xf32>
   ↓ onnx.Relu의 shape 추론 규칙 적용 (입력과 출력 shape가 항상 같음)
Relu 출력: tensor<1x64x224x224xf32>
```

이 과정이 실패하는 경우도 있습니다 — 배치 크기가 진짜로 실행 시점에만 정해지는 모델이라면, `1` 대신 `?`가 끝까지 남습니다. 이런 동적 축은 4~5편에서 다룰 타일링·벡터화가 "이 축은 컴파일 타임에 크기를 모른다"는 전제 위에서 좀 더 보수적인 코드(런타임에 크기를 읽어 반복 횟수를 결정하는 코드)를 만들어야 한다는 뜻이 됩니다. 이 시리즈는 예제를 단순하게 유지하기 위해 배치 크기 1로 고정된, shape가 전부 정적으로 확정되는 경우만 따라갑니다.

---

## 4. shape inference가 이 시리즈에서 갖는 위치

`onnx` dialect로 들여오는 것과 shape inference를 마치는 것 사이에는 미묘하지만 중요한 차이가 있습니다 — 전자는 단순한 형식 변환(protobuf → MLIR 오퍼레이션)이고, 후자는 **그래프 전체를 순회하며 타입 정보를 계산해 채우는 실제 컴파일러 pass**입니다. 이후 모든 편(3편의 연산 융합부터 6편의 하드웨어별 코드 생성까지)은 이 pass가 이미 끝나 모든 텐서 타입에 구체적인 숫자가 박혀 있다는 것을 전제로 진행됩니다.

다음 편에서는 이렇게 shape가 확정된 `onnx` dialect 그래프에, 실제로 어떤 그래프 수준 최적화(Conv-BatchNorm-Relu 융합, 상수 접기, 레이아웃 변환)가 적용되는지 — 그리고 그 최적화들이 왜 하나같이 "이 축의 크기가 정확히 얼마인지 안다"는 이번 편의 전제에 의존하는지를 확인합니다.
