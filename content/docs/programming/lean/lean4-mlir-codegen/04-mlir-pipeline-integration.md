---
title: "4. MLIR 파이프라인과의 접합: conversion, EmitC, 그리고 책임의 경계"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "mlir", "compiler", "emitc"]
categories: ["programming"]
description: "bounds_checked attribute 하나가 최종 C 코드에서 if문의 유무를 어떻게 결정하는지 실제 변환 결과로 확인하고, Lean4와 MLIR 인프라 사이 신뢰 경계를 정리합니다."
---

[3편](../03-emitting-mlir-text/)에서 우리 예제(`safec.array_get`)를 `bounds_checked = true`와 `false` 두 버전의 MLIR 텍스트로 손으로 짰습니다. 이 마지막 편은 그 텍스트 두 개가 실제로 어떤 C 코드로 번역되는지 끝까지 따라가면서, 이 파이프라인에서 가장 신경 써야 할 지점이 어디인지 짚습니다.

---

## 1. Conversion pattern: attribute를 읽고 다른 코드를 고르는 규칙

우리가 정의한 `safec.array_get`은 그 자체로는 실행할 수 없는, 우리만의 어휘일 뿐입니다. 실제로 실행 가능한 코드가 되려면 결국 더 낮은 단계의 표현으로 옮겨져야 합니다. 이 옮기는 규칙 하나하나를 **conversion pattern**이라고 부릅니다.

우리 예제에 대한 conversion pattern을 의사코드로 적어보면 이렇습니다.

```
pattern: safec.array_get(arr, idx) { bounds_checked }
  if bounds_checked == true:
    emit: memref.load %arr[%idx]           // 검사 없이 곧바로 읽기
  else:
    emit:
      %ok = arith.cmpi ult, %idx, <array 길이>
      scf.if %ok {
        %val = memref.load %arr[%idx]
        scf.yield %val
      } else {
        <실패 처리 경로 — 예: 기본값 반환>
      }
```

이 규칙이 하는 일이 이 시리즈 전체의 핵심입니다. **attribute 하나(`bounds_checked`의 값)가 완전히 다른 두 갈래의 코드 생성을 결정합니다.** [2편](../02-safety-encoded-ir/)에서 Lean4가 증명해낸 사실이 [3편](../03-emitting-mlir-text/)에서 attribute로 압축되었고, 이제 여기서 그 압축된 사실이 실제 코드의 모양을 바꾸는 데 쓰입니다.

이 conversion pattern은 우리가 MLIR의 표준 도구(C++ 코드, `PatternRewriter`라는 프레임워크)로 직접 작성해야 하는 유일한 코드입니다. Lean4는 elaboration과 텍스트 방출까지만 책임지고, 그 텍스트를 낮추는 규칙은 MLIR 쪽 인프라로 작성합니다 — Lean4의 강점(타입 이론 기반 증명)과 MLIR의 강점(성숙한 변환 프레임워크)이 각자 잘하는 지점에서만 일하도록 의도적으로 나눈 경계입니다.

---

## 2. 우리 예제의 최종 결과: 두 버전의 C 코드

[3편](../03-emitting-mlir-text/)의 두 MLIR 텍스트에 위 conversion pattern과, C 텍스트로 마지막 번역을 담당하는 **EmitC**(MLIR이 표준으로 제공하는, "C로 표현 가능한 것만 표현하는" dialect)를 차례로 적용하면, 최종적으로 이런 C 코드가 나옵니다.

**`bounds_checked = true`였던 `get_element` 함수:**

```c
int32_t get_element(int32_t arr[5]) {
    return arr[2];  // 검사 코드 없음 — 이미 안전이 증명됐으므로
}
```

**`bounds_checked = false`였던 `get_user_index` 함수:**

```c
int32_t get_user_index(int32_t arr[5], size_t i) {
    if (i < 5) {
        return arr[i];
    } else {
        return -1;  // 실패 시 기본값
    }
}
```

[1편](../01-why-lean4-for-mlir/)에서 처음 봤던 검사 없는 C 코드(`arr[i]`, 버퍼 오버플로우 위험이 있던 그 코드)와 비교해보면, 우리 파이프라인이 정확히 무엇을 해냈는지 드러납니다 — **Lean4가 안전을 증명할 수 있었던 경로는 원래 C처럼 검사 없이 깔끔하게 나오고, 증명할 수 없었던 경로만 자동으로 검사 코드가 붙습니다.** 사람이 어디에 검사를 넣을지 손으로 판단할 필요가 없어졌고, 동시에 검사가 필요 없는 곳에 불필요한 검사가 남지도 않습니다.

---

## 3. EmitC가 하는 마지막 확인

`memref.load`나 `scf.if` 같은 표현이 EmitC를 거쳐 실제 C 문법으로 바뀌는 이 마지막 단계는, 우리가 손댈 필요가 없는 MLIR의 표준 도구(`mlir-translate --mlir-to-cpp`)가 담당합니다. 이 도구가 하는 일은 단순한 번역을 넘어 일종의 **막차 검증**이기도 합니다 — 만약 우리 IR에 C로는 도저히 표현할 수 없는 개념이 섞여 있었다면 이 단계에서 변환이 실패하고, 그건 우리 언어 설계가 애초에 "C 서브셋"이라는 목표를 벗어났다는 신호입니다.

---

## 4. 이 파이프라인에서 가장 조심해야 할 지점

지금까지의 흐름을 신뢰의 관점에서 다시 보면, 각 단계가 서로 다른 종류의 확신을 만들어내고 있습니다.

- **Lean4 elaboration (2편)**: "`2 < 5`" 같은 사실을 수학적 증명으로 확인합니다. 증명이 성립하면 예외가 없는 강한 확신입니다.
- **MLIR 텍스트 방출 (3편)**: 그 증명을 `bounds_checked = true`라는, 증명 자체가 아니라 **증명이 있었다는 압축된 표식**으로 바꿔서 다음 단계로 넘깁니다.
- **Conversion pattern (이 글)**: 그 표식을 읽고 실제로 다른 코드를 생성합니다.
- **EmitC**: 최종적으로 C로 표현 가능한지 확인합니다.

이 사슬에서 가장 조심해야 할 지점은 두 번째 단계 — Lean4의 증명을 attribute로 압축하는 지점입니다. 만약 이 방출 코드에 버그가 있어서, 실제로는 증명되지 않았는데 실수로 `bounds_checked = true`를 붙여버렸다고 해봅시다. 그러면 그 뒤의 모든 단계(conversion pattern, EmitC)는 아무 잘못 없이 "정확하게" 동작하면서도, 결과적으로 검사 없는 위험한 C 코드를 만들어냅니다. 즉 이 파이프라인 전체의 신뢰성은 **Lean4의 증명 결과를 attribute로 옮기는, 우리가 직접 짠 그 방출 코드 한 조각**에 달려 있습니다. 다른 모든 단계는 Lean4의 타입 체커나 MLIR의 검증기가 스스로 지켜주지만, 이 방출 코드만큼은 우리가 직접 쓰고 직접 검토해야 하는 부분입니다. 이렇게 "전체 시스템의 신뢰가 걸려 있는, 사람이 직접 책임져야 하는 최소한의 코드 범위"를 컴파일러 이론에서는 **trusted computing base(TCB)**라고 부르며, 이 부분을 최대한 짧고 읽기 쉽게 유지하는 것이 전체 파이프라인의 신뢰성을 좌우합니다.

---

## 5. 시리즈 정리

네 편에 걸쳐 하나의 예제(`arr[i]`)를 따라가며 확인한 파이프라인을 요약하면:

1. **[왜 Lean4로 MLIR을 만드는가](../01-why-lean4-for-mlir/)**: elaboration은 "확인하고 통과시키는 엄격한 편집자"이고, 이 확인 인프라를 그대로 빌려 쓰면 안전 언어를 처음부터 만들 필요가 없다.
2. **[안전성이 타입에 인코딩된 내부 IR 설계](../02-safety-encoded-ir/)**: `Fin n` 타입으로 범위를 벗어난 인덱스를 표현 불가능하게 만들고, 증명은 가능하면 자동으로, 안 되면 명시적 런타임 검사로 채워진다.
3. **[MLIR 텍스트 방출과 커스텀 dialect 설계](../03-emitting-mlir-text/)**: `bounds_checked` attribute가 Lean4의 증명 결과를 다음 단계로 운반하며, 이걸 실을 자리를 지키려면 커스텀 dialect가 필요하다.
4. **MLIR 파이프라인과의 접합 (이 글)**: attribute 값 하나가 최종 C 코드에서 검사 코드의 유무를 결정하고, 이 전체 신뢰 사슬에서 가장 조심해야 할 지점은 증명을 attribute로 압축하는 방출 코드 자체다.

이 신뢰 문제를 그대로 남겨두지 않고, [5편: 번역 검증](../05-translation-validation/)에서 바로 이어서 다룹니다.
