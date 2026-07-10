---
title: "3. MLIR 텍스트 방출과 커스텀 dialect 설계"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "mlir", "metaprogramming", "compiler", "dialect"]
categories: ["programming"]
description: "우리 예제(안전한 배열 접근)를 실제 MLIR 텍스트로 손으로 짜보면서 operation/region/block/attribute가 무엇을 표현하는지, 왜 기존 dialect 대신 커스텀 dialect를 새로 정의해야 하는지 확인합니다."
---

[2편](../02-safety-encoded-ir/)에서 `Fin n` 타입으로 `arr.get ⟨2, ...⟩`처럼 안전성이 증명된 Lean4 코드를 만들었습니다. 이 글은 그 Lean4 코드가 실제로 어떤 MLIR 텍스트로 옮겨지는지 손으로 직접 짜보면서, MLIR의 표현 단위들이 각각 무엇을 위해 존재하는지 확인합니다.

---

## 1. MLIR이 필요한 이유를 짧게: 도메인마다 다른 어휘가 필요하다

LLVM IR 같은 전통적인 컴파일러 IR은 미리 정해진 명령어 집합(덧셈, 곱셈, 분기 등 몇 가지 고정된 종류)만 씁니다. 우리 예제처럼 "이 배열 접근은 정적으로 범위가 증명됐다"는, 일반적인 컴파일러가 모르는 우리만의 정보를 표현하려면 이 고정된 명령어 집합만으로는 부족합니다.

MLIR은 명령어 집합 자체를 고정하지 않고, 새로운 명령어(오퍼레이션)를 자유롭게 정의할 수 있는 틀을 제공합니다. 이렇게 도메인마다 독립적으로 정의하는 어휘 뭉치를 **dialect**라고 부릅니다. 우리는 우리만의 dialect(이름을 `safec`라고 합시다)를 만들어, "안전이 증명된 배열 접근"이라는 우리 고유의 개념을 있는 그대로 표현할 겁니다.

---

## 2. 우리 예제를 MLIR 텍스트로: 한 줄씩 손으로 써보기

[2편](../02-safety-encoded-ir/)의 `arr.get ⟨2, by decide⟩`(정적으로 안전이 증명된 경우)를 MLIR 텍스트로 옮기면 이렇게 생겼습니다.

```mlir
func.func @get_element(%arr: !safec.array<5xi32>) -> i32 {
  %idx = safec.const_index 2 : index
  %val = safec.array_get %arr[%idx] {bounds_checked = true} : (!safec.array<5xi32>, index) -> i32
  return %val : i32
}
```

한 줄씩 뜯어보면:

- `func.func @get_element(...)`: MLIR이 기본으로 제공하는 `func` dialect의 함수 정의입니다. 함수 이름은 `@get_element`, 매개변수는 우리 dialect가 정의한 배열 타입 `!safec.array<5xi32>`(5칸짜리 32비트 정수 배열)입니다.
- `%arr`, `%idx`, `%val`: MLIR에서 값을 가리키는 이름입니다. `%`로 시작하며, C의 변수 이름과 비슷한 역할을 합니다.
- `safec.array_get`: 우리가 새로 정의한 **오퍼레이션**입니다. `safec.` 접두사가 이게 우리 dialect에 속한다는 걸 나타냅니다. `%arr[%idx]`가 이 오퍼레이션이 받는 피연산자(operand)이고, 결과 타입 `i32`가 화살표 뒤에 명시됩니다.
- `{bounds_checked = true}`: 이게 이 시리즈의 핵심입니다. 중괄호 안의 이건 **attribute**라고 부르는, 오퍼레이션에 붙는 컴파일 타임 메타데이터입니다. [2편](../02-safety-encoded-ir/)에서 Lean4가 `2 < 5`를 정적으로 증명했다는 사실이, 여기서 `bounds_checked = true`라는 표식으로 살아남아 있습니다. Lean4의 증명 자체(타입 이론적 증명 트리)는 MLIR로 그대로 옮겨갈 수 없지만, "증명이 성립했다"는 결론은 이렇게 attribute라는 형태로 다음 단계까지 실어 보낼 수 있습니다.

이제 [2편](../02-safety-encoded-ir/)의 "정적으로 증명 안 되는 경우"(`getUserIndex`, 런타임 검사가 필요한 경우)를 같은 방식으로 옮겨보면 이렇게 됩니다.

```mlir
func.func @get_user_index(%arr: !safec.array<5xi32>, %i: index) -> i32 {
  %val = safec.array_get %arr[%i] {bounds_checked = false} : (!safec.array<5xi32>, index) -> i32
  return %val : i32
}
```

**딱 한 글자, `true`가 `false`로 바뀐 것 말고는 완전히 같은 오퍼레이션입니다.** 이 attribute 하나가 다음 편(4편)에서 "런타임 범위 검사 코드를 생성할지 말지"를 결정하는 전부입니다. 오퍼레이션의 구조 자체는 똑같이 유지하면서, 안전성에 대한 결론만 attribute로 갈아 끼우는 이 설계가 이 파이프라인 전체의 핵심 아이디어입니다.

---

## 3. region과 block: 제어 흐름이 있는 예제로 확장

지금까지는 분기 없는 단순한 함수였습니다. [2편](../02-safety-encoded-ir/)의 `sumAll`(반복문으로 배열을 순회하며 합산)처럼 제어 흐름이 있는 코드는 MLIR에서 **region**과 **block**으로 표현됩니다.

```mlir
func.func @sum_all(%arr: !safec.array<5xi32>) -> i32 {
  %init = arith.constant 0 : i32
  %sum = safec.for_range 0 to 5 iter_args(%acc = %init) -> i32 {
  ^bb0(%i: index, %acc: i32):
    %val = safec.array_get %arr[%i] {bounds_checked = true} : (!safec.array<5xi32>, index) -> i32
    %next = arith.addi %acc, %val : i32
    safec.yield %next : i32
  }
  return %sum : i32
}
```

`safec.for_range { ... }`의 중괄호 안이 **region**입니다 — 오퍼레이션이 자기 내부에 통째로 품고 있는 코드 블록입니다. 그 안의 `^bb0(...)`가 **block**이고, 반복문이 한 바퀴 돌 때마다 실행되는 명령들이 순서대로 나열되어 있습니다. 여기서도 `safec.array_get`에 `bounds_checked = true`가 그대로 붙어 있는데, 이건 [2편](../02-safety-encoded-ir/)에서 반복문 구조 덕분에 `i < 5`가 자동으로 증명됐다는 사실이 여기까지 그대로 전달된 것입니다.

이 예제에서 중요한 점은, Lean4 쪽에서 "반복문 몸체"라는 개념이 이미 트리 형태로 중첩되어 있었기 때문에, MLIR로 옮길 때도 그 구조를 평평하게 풀어헤칠 필요 없이 region 중첩으로 그대로 옮기기만 하면 됐다는 것입니다.

---

## 4. 왜 `arith.addi`를 흉내내지 않고 `safec.array_get`을 새로 만들었나

MLIR에는 이미 정수 덧셈을 위한 `arith.addi` 같은 오퍼레이션이 있습니다. "그럼 배열 접근도 기존 dialect의 오퍼레이션을 흉내내서 표현하면 되지 않나?"라는 질문이 자연스럽게 나옵니다.

한번 시도해봅시다. 배열 접근을 우리 dialect 없이, 기존 오퍼레이션만으로 표현하려면 대략 이렇게 될 겁니다.

```mlir
// 커스텀 dialect 없이 표현하려는 시도
%ptr = memref.extract_aligned_pointer_as_index %arr : memref<5xi32>
%addr = arith.addi %ptr, %idx : index
%val = memref.load %arr[%idx] : memref<5xi32>
```

이렇게 쓰면 **`bounds_checked = true`라는 정보를 붙일 자리가 없습니다.** `memref.load`는 이미 MLIR 프로젝트가 정의해둔 오퍼레이션이라, 우리가 임의로 attribute를 덧붙인다고 해도 그걸 읽고 활용하는 다음 단계 변환 규칙이 저절로 생기지 않습니다. Lean4가 애써 증명한 "이 인덱스는 안전하다"는 사실이 여기서 그냥 사라져버립니다.

`safec.array_get`을 새로 정의하면, 그 오퍼레이션이 어떤 attribute를 가질 수 있는지, 그 attribute가 무엇을 의미하는지를 우리가 온전히 설계할 수 있고, 다음 편에서 이 오퍼레이션을 최종 코드로 바꾸는 규칙도 우리가 그 의미에 맞게 정확히 작성할 수 있습니다. 즉 커스텀 dialect를 만드는 건 "새 문법을 발명하는 수고"가 아니라, **Lean4가 증명한 사실을 다음 단계까지 잃지 않고 운반하기 위한 필수 조건**입니다.

---

## 5. 정리

1. **오퍼레이션은 계산의 기본 단위이고, attribute는 그 오퍼레이션에 붙는 컴파일 타임 메타데이터다.** 우리 예제에서 `bounds_checked = true/false`가 Lean4의 증명 결과를 실어 나르는 attribute다.
2. **region과 block은 제어 흐름(반복문, 분기)을 오퍼레이션 내부의 중첩 구조로 표현한다.** Lean4 IR이 이미 트리 형태였다면 평탄화 없이 그대로 옮길 수 있다.
3. **기존 dialect(`arith`, `memref`)의 오퍼레이션을 흉내내면 우리만의 attribute를 실을 자리가 없어져, Lean4가 증명한 정보가 사라진다.** 커스텀 dialect가 이 정보 손실을 막는다.

다음 편에서는 방금 손으로 짠 `bounds_checked = true`와 `false` 두 버전의 MLIR 텍스트가, 각각 실제로 어떤 C 코드로 번역되는지 — `true`인 경우 검사 코드가 통째로 사라지고, `false`인 경우 `if`문이 자동으로 삽입되는 과정을 직접 확인합니다.
