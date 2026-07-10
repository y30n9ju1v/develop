---
title: "7. 실습: 실제로 돌아가는 최소 파이프라인으로 C 찍어보기"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "mlir", "compiler", "hands-on"]
categories: ["programming"]
description: "MLIR/CIRCT 툴체인 설치 없이, Lean4 코드만으로 안전성 정보를 MLIR 텍스트와 C 소스로 실제로 찍어내고 독립 검사기로 재확인하는 최소 파이프라인을 직접 돌려봅니다."
---

[1~4편](../01-why-lean4-for-mlir/)에서는 `arr[i]`라는 예제를 손으로 MLIR 텍스트와 C 코드로 옮기며 원리를 설명했고, [5편](../05-translation-validation/)에서는 그 결과를 재확인하는 verifier를 C++ 의사코드로 보여드렸습니다. 이 글은 "손으로 짠 예시"가 아니라, **실제로 실행하면 그 텍스트를 그대로 찍어내는 Lean4 코드**를 다룹니다. 진짜 MLIR C++ 인프라나 CIRCT 툴체인을 설치할 필요 없이, Lean4 파일 하나만으로 지금까지 다룬 흐름(IR → MLIR 텍스트 → C 소스 → 독립 검증)을 끝까지 돌려볼 수 있습니다.

---

## 1. 이 실습이 보여주는 것과 생략하는 것

정직하게 스코프를 먼저 밝히겠습니다. 이 글은 [2편](../02-safety-encoded-ir/)에서 다룬 `arr.get ⟨2, by decide⟩` 같은 표면 문법을 실제로 파싱하고 elaboration하는 전체 프론트엔드는 구현하지 않습니다. 그건 Lean4 컴파일러 자체의 일이고, 우리가 새로 만들 필요가 없는 부분입니다. 대신 이 글이 실제로 구현하는 건 **[3편](../03-emitting-mlir-text/)과 [4편](../04-mlir-pipeline-integration/)에서 "이렇게 생겼다"고 손으로 보여준 결과물을, 프로그램이 실제로 만들어내는 부분**입니다 — 안전성 정보(배열 크기, 인덱스, `bounds_checked` 여부)를 받아서 MLIR 텍스트를 찍고, 그 정보를 바탕으로 C 코드를 찍고, [5편](../05-translation-validation/)에서 다룬 독립 검사기로 그 정보를 다시 확인하는 부분입니다. 실전 파이프라인에서 이 부분이 정확히 conversion pattern과 verifier가 하는 일이고, 여기서는 그걸 MLIR C++ 대신 순수 Lean4로 구현해 누구나 별도 설치 없이 돌려볼 수 있게 만듭니다.

---

## 2. 안전성 정보를 담는 자료구조

먼저 [3편](../03-emitting-mlir-text/)의 예제 두 개(`get_element`, `get_user_index`)를 표현할 수 있는 최소한의 자료구조를 만듭니다.

```lean
structure SafecArrayGet where
  funcName      : String
  arraySize     : Nat
  indexLit      : Option Nat  -- some n: 컴파일 타임 상수 인덱스, none: 런타임 변수 i
  boundsChecked : Bool
```

`indexLit`이 `some 2`면 [2편](../02-safety-encoded-ir/)의 `arr.get ⟨2, by decide⟩`처럼 인덱스가 이미 알려진 경우이고, `none`이면 `getUserIndex`처럼 런타임에만 알 수 있는 경우입니다. 이 구조체 하나가 elaboration이 끝난 뒤 attribute로 실려 나가는 정보 전체를 압축해서 담고 있다고 보면 됩니다.

우리 두 예제를 이 구조체 값으로 만들어봅니다.

```lean
def getElement : SafecArrayGet :=
  { funcName := "get_element", arraySize := 5, indexLit := some 2, boundsChecked := true }

def getUserIndex : SafecArrayGet :=
  { funcName := "get_user_index", arraySize := 5, indexLit := none, boundsChecked := false }
```

---

## 3. MLIR 텍스트를 실제로 찍어내기

[3편](../03-emitting-mlir-text/)에서 손으로 짰던 텍스트를, 이제 함수로 만들어봅니다.

```lean
def toMlirText (e : SafecArrayGet) : String :=
  let arrTy := s!"!safec.array<{e.arraySize}xi32>"
  let bc := if e.boundsChecked then "true" else "false"
  match e.indexLit with
  | some n =>
    s!"func.func @{e.funcName}(%arr: {arrTy}) -> i32 \{\n" ++
    s!"  %idx = safec.const_index {n} : index\n" ++
    s!"  %val = safec.array_get %arr[%idx] \{bounds_checked = {bc}\} : ({arrTy}, index) -> i32\n" ++
    "  return %val : i32\n}\n"
  | none =>
    s!"func.func @{e.funcName}(%arr: {arrTy}, %i: index) -> i32 \{\n" ++
    s!"  %val = safec.array_get %arr[%i] \{bounds_checked = {bc}\} : ({arrTy}, index) -> i32\n" ++
    "  return %val : i32\n}\n"

#eval IO.println (toMlirText getElement)
```

이걸 실제로 실행하면(에디터에서 `#eval` 위에 커서를 두거나, `lake env lean --run` 명령으로) 정확히 이런 텍스트가 콘솔에 찍힙니다.

```mlir
func.func @get_element(%arr: !safec.array<5xi32>) -> i32 {
  %idx = safec.const_index 2 : index
  %val = safec.array_get %arr[%idx] {bounds_checked = true} : (!safec.array<5xi32>, index) -> i32
  return %val : i32
}
```

[3편](../03-emitting-mlir-text/)에서 손으로 보여드렸던 것과 한 글자도 다르지 않습니다. 차이는 이번엔 이 텍스트가 사람이 아니라 `toMlirText` 함수가 만들어냈다는 것뿐입니다.

---

## 4. 같은 정보로 C 코드도 찍어내기

이제 [4편](../04-mlir-pipeline-integration/)의 conversion pattern을 함수로 옮겨봅니다. `boundsChecked` 값에 따라 완전히 다른 두 형태의 C 함수를 찍는 부분이 핵심입니다.

```lean
def toC (e : SafecArrayGet) : String :=
  match e.boundsChecked, e.indexLit with
  | true, some n =>
    s!"int32_t {e.funcName}(int32_t arr[{e.arraySize}]) \{\n" ++
    s!"    return arr[{n}];  // 검사 없음 — 이미 안전이 증명됨\n}}\n"
  | _, _ =>
    s!"int32_t {e.funcName}(int32_t arr[{e.arraySize}], size_t i) \{\n" ++
    "    if (i < " ++ toString e.arraySize ++ ") {\n" ++
    "        return arr[i];\n" ++
    "    } else {\n" ++
    "        return -1;  // 실패 시 기본값\n" ++
    "    }\n}\n"

#eval IO.println (toC getElement)
#eval IO.println (toC getUserIndex)
```

`getElement`(`boundsChecked = true`, 상수 인덱스)를 넣으면 검사 없는 깔끔한 C 함수가, `getUserIndex`(`boundsChecked = false`)를 넣으면 `if`문이 자동으로 삽입된 C 함수가 나옵니다 — [4편](../04-mlir-pipeline-integration/)에서 봤던 두 결과와 정확히 같습니다.

```c
int32_t get_element(int32_t arr[5]) {
    return arr[2];  // 검사 없음 — 이미 안전이 증명됨
}

int32_t get_user_index(int32_t arr[5], size_t i) {
    if (i < 5) {
        return arr[i];
    } else {
        return -1;  // 실패 시 기본값
    }
}
```

`toC` 함수 하나가 정확히 [4편](../04-mlir-pipeline-integration/)에서 "attribute 하나가 완전히 다른 두 갈래의 코드 생성을 결정한다"고 설명했던 그 분기 로직입니다. `match e.boundsChecked, e.indexLit with` 패턴 매칭이 곧 conversion pattern입니다.

---

## 5. 독립 검사기도 실제로 돌려보기

여기까지는 `toC`가 `boundsChecked`를 무조건 신뢰합니다. [5편](../05-translation-validation/)에서 강조했듯, 이게 이 파이프라인에서 가장 위험한 지점입니다. 이제 [5편](../05-translation-validation/)의 C++ verifier 의사코드를 Lean4로 실제로 구현해, `toC`를 믿기 전에 한 번 더 재확인하게 만듭니다.

```lean
def verifyBounds (e : SafecArrayGet) : Except String Unit :=
  if !e.boundsChecked then
    .ok ()  -- false면 런타임 검사가 대신 처리하므로 재확인할 게 없음
  else
    match e.indexLit with
    | none   => .error "bounds_checked=true인데 인덱스가 상수가 아님 — 재확인 불가"
    | some n =>
      if n < e.arraySize then .ok ()
      else .error s!"PCC 재검증 실패: 인덱스 {n}가 배열 크기 {e.arraySize}를 벗어남"

def reportVerify (e : SafecArrayGet) : IO Unit :=
  match verifyBounds e with
  | .ok ()      => IO.println s!"[OK]   {e.funcName}: 검증 통과"
  | .error msg  => IO.println s!"[FAIL] {e.funcName}: {msg}"

#eval reportVerify getElement     -- [OK]   get_element: 검증 통과
#eval reportVerify getUserIndex   -- [OK]   get_user_index: 검증 통과 (false라 재확인 스킵)
```

이제 [4편](../04-mlir-pipeline-integration/)에서 경고했던 "방출 코드에 버그가 있는 상황"을 직접 만들어봅니다. 실제로는 인덱스가 7이라 위험한데, 방출 코드에 버그가 있어서 `boundsChecked = true`가 잘못 붙었다고 가정해봅시다.

```lean
def buggyGet : SafecArrayGet :=
  { funcName := "buggy_get", arraySize := 5, indexLit := some 7, boundsChecked := true }

#eval IO.println (toC buggyGet)     -- toC는 아무 의심 없이 "return arr[7];"을 찍어버림
#eval reportVerify buggyGet         -- [FAIL] buggy_get: PCC 재검증 실패: 인덱스 7가 배열 크기 5를 벗어남
```

`toC buggyGet`을 그냥 실행하면 `return arr[7];`이라는, 원래 이 시리즈 전체가 막으려던 바로 그 버퍼 오버플로우 코드가 아무 경고 없이 찍혀 나옵니다. 하지만 `reportVerify buggyGet`은 `toC`가 참조한 것과 똑같은 `boundsChecked` attribute를 믿지 않고 `indexLit`과 `arraySize`만으로 스스로 다시 계산해서, 이 코드가 실제로는 안전하지 않다는 걸 잡아냅니다. 실전 파이프라인이라면 `reportVerify`(또는 이에 해당하는 MLIR verifier)가 실패하는 순간 빌드 자체가 멈추고, `toC buggyGet`이 만든 위험한 C 코드는 최종 결과물에 절대 포함되지 않습니다.

---

## 6. `verifyBounds`의 빈틈: false 케이스는 정말 안전한가

`verifyBounds`를 다시 보면 `boundsChecked = false`인 경우를 이렇게 처리합니다.

```lean
if !e.boundsChecked then
  .ok ()  -- false면 런타임 검사가 대신 처리하므로 재확인할 게 없음
```

이 한 줄이 실은 검증되지 않은 가정을 깔고 있습니다. "런타임 검사가 대신 처리한다"는 건 **`toC`가 실제로 `if (i < size)` 가드를 빼먹지 않고 찍었을 것이라는 기대**일 뿐, `verifyBounds`가 직접 확인한 사실이 아닙니다. `verifyBounds`는 오직 `e`(IR/attribute)만 들여다보고, `toC`가 최종적으로 만든 **텍스트 자체**는 한 번도 쳐다보지 않습니다. 만약 `toC` 쪽에 버그가 있어서 `false` 케이스인데도 실수로 가드 없는 코드를 찍어버린다면, `verifyBounds`는 이걸 전혀 잡아내지 못합니다 — `buggyGet` 예제가 attribute 쪽 버그를 잡아낸 것과 대칭적으로, 여기엔 방출 코드 쪽 버그를 잡을 안전망이 없는 것입니다.

이건 [5편](../05-translation-validation/)에서 짚었던 원칙 — 번역 검증은 중간 표현(attribute)만이 아니라 **최종 결과물 자체**를 재확인해야 한다 — 을 우리가 07편에서 절반만 구현했다는 뜻입니다. 이 빈틈을 메우려면, `verifyBounds`가 `toC`가 실제로 만든 문자열까지 인자로 받아서 확인해야 합니다.

```lean
def verifyBoundsAdvanced (e : SafecArrayGet) (generatedC : String) : Except String Unit :=
  match e.boundsChecked, e.indexLit with
  | false, _ =>
    if generatedC.splitOn "if (i <" |>.length > 1 then .ok ()
    else .error "런타임 변수인데 생성된 C 코드에 범위 검사 가드가 없음"
  | _, _ => verifyBounds e

#eval verifyBoundsAdvanced getUserIndex (toC getUserIndex)  -- [ok] — 가드가 실제로 존재함
```

다만 이 구현은 정직하게 그 한계를 밝혀야 합니다. `generatedC.splitOn "if (i <"`는 **생성된 C 텍스트에서 특정 부분 문자열을 찾는 방식**이라, 코드 스타일이 조금만 바뀌어도(공백 하나, 변수명 하나) 깨지는 아주 허술한 검사입니다. 진짜 번역 검증이라면 생성된 C를 다시 파싱해서 그 의미(제어 흐름 그래프 상에서 배열 접근이 실제로 범위 검사 뒤에 위치하는지)를 확인해야 하고, 이건 사실상 작은 C 파서를 하나 더 만드는 일입니다. 여기서는 "텍스트만 봐도 아예 아무것도 확인하지 않는 것보다는 낫다"는 최소한의 안전망을 보여드리는 것으로 그칩니다 — [5편](../05-translation-validation/)에서 다룬 "얕고 국소적인 사실에는 순진한 검증이 통한다"는 원칙이 여기서도 그대로 적용되는데, "가드 문자열이 존재하는가"는 딱 그 정도 수준의 얕은 확인입니다.

---

## 7. 이 실습이 실전과 다른 점

이 최소 구현과 진짜 MLIR/CIRCT 파이프라인 사이에는 몇 가지 의도적인 차이가 있습니다.

- **표면 문법 파싱이 없습니다.** `SafecArrayGet` 값을 우리가 직접 손으로 만들었지만, 실전에서는 [2편](../02-safety-encoded-ir/)에서 다룬 elaboration이 `arr.get ⟨2, by decide⟩` 같은 실제 Lean4 코드를 분석해서 이 값을 자동으로 만들어냅니다.
- **`toMlirText`가 진짜 MLIR 파서를 통과하는지 검증하지 않습니다.** 우리는 문자열을 만들 뿐이고, 이 문자열이 실제 MLIR 문법을 준수하는지는 진짜 `mlir-opt`에 넣어봐야 확인됩니다. [3편](../03-emitting-mlir-text/)에서 다룬 커스텀 dialect를 실제로 등록하려면 TableGen과 MLIR C++ 인프라가 필요합니다.
- **`verifyBounds`가 다루는 경우가 상수 인덱스뿐입니다.** [5편](../05-translation-validation/)에서 다룬 `bounds_proof`/`loop_bound` 같은 PCC 근거나 반복문 케이스는 이 최소 구현에 포함하지 않았습니다. 같은 패턴(다른 필드를 추가하고, `verifyBounds`에 케이스를 하나 더 얹는 것)으로 확장할 수 있습니다.

이 실습의 목적은 진짜 컴파일러를 완성하는 게 아니라, **지금까지 여섯 편에 걸쳐 설명한 "attribute가 정보를 운반하고, conversion pattern이 그 정보로 분기하고, verifier가 그 정보를 재확인한다"는 구조가 손으로 그린 그림이 아니라 실제로 실행 가능한 코드라는 것**을 확인하는 데 있습니다. 여기서 다룬 세 함수(`toMlirText`, `toC`, `verifyBounds`)를 확장해나가는 것이, [4편](../04-mlir-pipeline-integration/) 끝에서 언급한 "가장 현실적인 출발점"의 실제 첫걸음입니다.
