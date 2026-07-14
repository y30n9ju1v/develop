---
title: "8. 버퍼화 딥다이브: One-Shot Bufferize와 메모리 재사용 결정"
date: 2026-07-14T00:00:00+09:00
draft: false
tags: ["mlir", "onnx", "deep-learning", "compiler", "bufferization", "memory-planning"]
categories: ["programming"]
description: "4편에서 한 문단으로 짧게 다뤘던 버퍼화(tensor→memref 변환)를, MLIR의 One-Shot Bufferize가 SSA use-def 체인을 분석해 in-place 재사용을 결정하는 알고리즘 수준까지 깊게 파고듭니다."
---

> [4편](../04-lowering-to-linalg-and-tiling/) 3절에서 "버퍼화가 텐서에서 메모리로의 전환과 in-place 재사용을 결정한다"고 짧게 짚었던 부분을 이 글이 이어서 다룹니다. [MLIR 공식 Bufferization 문서](https://mlir.llvm.org/docs/Bufferization/)를 참고해 작성했습니다.

---

## 1. 4편에서 남겨둔 질문: "재사용 가능한지는 누가, 어떻게 판단하는가"

[4편](../04-lowering-to-linalg-and-tiling/)은 버퍼화를 "텐서를 메모리로 바꾸면서, 어떤 텐서가 다른 텐서의 메모리를 재사용할 수 있는지(in-place bufferization)를 결정하는 pass"라고 소개하고, Relu가 입력 버퍼를 덮어써서 별도 할당을 없앨 수 있다는 예시로 넘어갔습니다. 그런데 "이 연산은 재사용해도 안전하다"는 판단을 컴파일러가 실제로 어떻게 내리는지는 다루지 않았습니다 — 이 글의 주제입니다.

---

## 2. 왜 이게 어려운 문제인가: "안전"과 "빠름"이 충돌한다

텐서 결과값을 메모리에 배치하는 가장 안전한 방법은 **매번 새 버퍼를 할당**하는 것입니다 — 아무것도 덮어쓰지 않으니 잘못될 일이 없습니다. 하지만 이건 고성능 코드 생성 관점에서는 받아들일 수 없습니다 — Conv-BN-Relu처럼 연산이 줄줄이 이어지는 그래프에서 매 단계마다 새 버퍼를 할당하면, 실제 계산보다 메모리 할당·해제 오버헤드가 더 커질 수 있습니다.

반대로 기존 버퍼를 재사용하려면 **"이 버퍼의 원래 값이 프로그램의 뒤쪽에서 더는 필요 없다"**는 걸 확신해야 합니다. 이 판단을 잘못하면 아직 필요한 값을 덮어써서 **조용히 틀린 결과**를 내는, 디버깅하기 매우 어려운 버그가 생깁니다. MLIR의 **One-Shot Bufferize** 패스는 이 안전성 분석을 자동으로 수행합니다.

---

## 3. One-Shot Bufferize: 함수 전체를 한 번에 보는 분석

이름의 "One-Shot"이 가리키는 게 바로 이 지점입니다 — 이전 세대의 버퍼화 방식은 연산 하나하나를 지역적으로(local) 순서대로 버퍼화하면서 필요할 때마다 복사본을 만드는 방식이었는데, One-Shot Bufferize는 **함수 전체를 한 번에 분석**해서 어디서 재사용이 안전한지를 먼저 결정한 다음, 그 결정에 따라 한 번에 IR을 재작성합니다.

핵심 분석 대상은 **텐서 값들의 SSA use-def 체인**입니다 — 어떤 텐서 값이 어디서 만들어지고(def), 어디서 읽히는지(use)를 전부 추적해서, "이 값을 만드는 연산이 입력 버퍼를 그대로 덮어써도, 그 입력 버퍼의 원래 값을 나중에 다시 읽는 다른 use가 프로그램 어디에도 없다"는 게 확인될 때만 in-place 재사용을 허용합니다. 이 조건이 하나라도 깨지면(즉 원래 값을 나중에 또 읽는 지점이 있으면), 컴파일러는 안전한 쪽으로 물러나 **복사본을 만듭니다**.

```mlir
// 안전한 경우: relu_out 이후 conv_out을 다시 읽는 곳이 없다 → in-place 재사용 가능
%conv_out = linalg.generic ... outs(%buf : memref<...>) { ... }  // conv 결과를 buf에 씀
%relu_out = linalg.generic ins(%conv_out) outs(%conv_out) { ... }  // buf를 덮어써서 relu 결과로 재사용

// 안전하지 않은 경우: conv_out이 relu 이후에도 residual 덧셈에 다시 쓰인다 → 복사본 필요
%conv_out = linalg.generic ... outs(%buf : memref<...>) { ... }
%relu_out = linalg.generic ins(%conv_out) outs(%new_buf) { ... }   // 새 버퍼에 써야 함
%residual = linalg.generic ins(%conv_out, %relu_out) outs(%out) { ... }  // conv_out을 다시 읽음
```

이 예시가 보여주는 것처럼, **그래프의 위상(topology)**이 재사용 가능 여부를 결정합니다 — 단순히 이어지는 연산 체인(Conv → BN → Relu처럼 한 줄로 흐르는 경우)은 재사용 여지가 크지만, ResNet의 skip connection처럼 한 텐서가 **두 갈래로 갈라져 나중에 다시 합쳐지는 구조**에서는 그 텐서가 두 번째 사용 지점까지 살아 있어야 하므로 재사용이 제한됩니다.

---

## 4. Destination-Passing Style(DPS): 재사용을 IR 차원에서 명시하기

One-Shot Bufferize가 이 분석을 효율적으로 수행할 수 있는 건, `linalg.generic` 같은 연산이 **Destination-Passing Style(DPS)**로 설계되어 있기 때문입니다. DPS란 연산이 "결과값이 어디에 쓰일지"를 오퍼레이션 자체의 `outs` 피연산자로 미리 받는 스타일입니다 — [4편](../04-lowering-to-linalg-and-tiling/)에서 본 `linalg.generic`의 `ins`/`outs` 구분이 정확히 이겁니다.

```mlir
linalg.generic { ... } ins(%a, %b : ...) outs(%c : ...) { ... }
```

이 구조 덕분에 One-Shot Bufferize는 "이 연산의 결과가 어느 버퍼에 담기는가"를 별도로 추론할 필요 없이, `outs`에 적힌 값을 그대로 후보로 검토하기만 하면 됩니다 — 연산 자체의 시그니처가 이미 "어디에 쓸 것인가"라는 질문에 답을 갖고 있는 셈입니다. `outs`에 입력 텐서 중 하나를 그대로 넘기면 "이 입력을 재사용해도 좋다"는 힌트가 되고, 새로 만든 빈 텐서(`tensor.empty()`)를 넘기면 "새 버퍼가 필요할 수 있다"는 신호가 됩니다. 이 설계가 없었다면, 컴파일러는 매 연산마다 "이 결과가 나중에 어디서 재사용될 수 있는지"를 훨씬 비싼 전역 분석으로 다시 추론해야 했을 것입니다.

---

## 5. 이 결정이 Conv-BN-Relu 예제에 미치는 영향

이 시리즈가 처음부터 따라온 Conv → BatchNorm → Relu 체인은 각 단계가 다음 단계에서만 쓰이는 **단순한 선형 체인**이라서, One-Shot Bufferize 입장에서는 가장 쉬운 경우입니다 — 이론적으로는 Conv의 출력 버퍼 하나를 BN이 덮어쓰고, 그 버퍼를 다시 Relu가 덮어써서, **중간 버퍼를 전혀 새로 할당하지 않고** 체인 전체를 하나의 버퍼로 통과시킬 수 있습니다. 이건 [3편](../03-graph-level-optimization/)에서 다룬 Conv-BN-Relu 연산 융합과는 **다른 층위의 최적화**라는 점이 중요합니다 — 연산 융합은 "세 번의 커널 실행을 한 번으로 줄이는 것"이고, 버퍼화의 in-place 재사용은 "설령 커널 실행이 별개로 남아 있더라도, 그 사이에 오가는 메모리 할당·해제를 없애는 것"입니다. 즉 융합이 실패하거나 부분적으로만 적용된 경우에도, 버퍼 재사용은 독립적으로 여전히 이득을 줍니다.

---

## 6. 정리

- 버퍼화는 "매번 새 버퍼를 할당(항상 안전하지만 느림)"과 "기존 버퍼를 재사용(빠르지만 잘못하면 값이 깨짐)" 사이의 트레이드오프이고, 이 판단을 안전하게 자동화하는 게 **One-Shot Bufferize**입니다.
- One-Shot Bufferize는 함수 전체의 **텐서 SSA use-def 체인**을 한 번에 분석해서, "이 값을 나중에 다시 읽는 지점이 없다"는 게 확인될 때만 in-place 재사용을 허용하고, 그렇지 않으면 복사본을 만듭니다.
- `linalg.generic`의 `ins`/`outs` 구분이 구현하는 **Destination-Passing Style**이 이 분석을 값싸게 만드는 핵심 설계입니다 — 연산 자체가 "결과가 어디에 쓰일지"를 미리 명시하기 때문입니다.
- Conv-BN-Relu 같은 단순 선형 체인은 in-place 재사용의 가장 쉬운 경우이고, 이 재사용은 [3편](../03-graph-level-optimization/)의 연산 융합과는 독립적인 최적화 층위입니다 — 융합이 안 되더라도 버퍼 재사용은 별도로 이득을 줍니다.
