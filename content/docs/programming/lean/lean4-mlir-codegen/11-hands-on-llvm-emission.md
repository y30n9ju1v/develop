---
title: "11. 실습: 세 번째 타겟으로 LLVM IR 찍어보기"
date: 2026-07-14T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "mlir", "llvm", "compiler", "hands-on"]
categories: ["programming"]
description: "7편(C)·8편(SystemVerilog)과 똑같은 SafecArrayGet 자료구조로, 이번엔 분기와 trap 명령이 있는 LLVM IR 텍스트를 실제로 찍어내고, 독립 검사기로 branch 조건 버그를 잡아내는 세 번째 conversion pattern을 구현합니다."
---

[7편](../07-hands-on-c-emission/)에서 C를, [8편](../08-hands-on-systemverilog-emission/)에서 SystemVerilog를 같은 `SafecArrayGet` 자료구조로 찍어봤습니다. 이 글은 세 번째 타겟으로 **LLVM IR**을 추가합니다 — MLIR의 `llvm` dialect가 실제로 낮아지는 최종 텍스트 형태이자, C나 SystemVerilog와 달리 **고수준 제어 구조(if-else) 없이 기본 블록과 분기 명령만으로** 안전성 검사를 표현해야 하는, 지금까지와는 또 다른 종류의 낮추기를 보여줍니다.

---

## 1. 왜 세 번째 타겟이 흥미로운가: "고수준 제어 구조가 사라진다"

7편의 C 방출과 8편의 SystemVerilog 방출은 둘 다 타겟 언어에 `if`/`case` 같은 **고수준 제어 구조**가 있었습니다. LLVM IR은 다릅니다 — LLVM IR에는 `if`가 없습니다. 대신 프로그램은 **기본 블록(basic block)의 그래프**이고, 각 블록은 반드시 `br`(분기) 또는 `ret`(반환) 같은 **터미네이터 명령**으로 끝나야 합니다. `if h : i < 5 then ... else ...`라는 [2편](../02-safety-encoded-ir/)의 조건부 증명 패턴을, 이번엔 **블록과 조건부 점프의 그래프**로 직접 그려야 합니다.

```
llvm dialect (4편의 dialect conversion 결과물)
   ↓ (타겟에 따라 갈라지는 세 번째 conversion pattern)
C            → if/else 문                    [7편]
SystemVerilog → mux + unique case/default    [8편]
LLVM IR (이 글) → basic block + br + trap    ← 지금 여기
```

---

## 2. 자료구조는 그대로 재사용합니다

7·8편의 `SafecArrayGet`을 그대로 씁니다 — 이 자료구조 하나가 세 가지 서로 다른 타겟 언어로 낮춰질 수 있다는 사실 자체가, [1편](../01-why-lean4-for-mlir/)에서 다룬 "MLIR을 중간에 끼우는 이유"(하나의 안전성 정보를 여러 타겟이 공유)를 가장 직접적으로 보여줍니다.

```lean
structure SafecArrayGet where
  funcName      : String
  arraySize     : Nat
  indexLit      : Option Nat
  boundsChecked : Bool
```

---

## 3. `toLLVM`: 분기와 트랩으로 안전성 검사를 표현하기

정적으로 인덱스가 확정된 경우(`indexLit = some n`, `boundsChecked = true`)는 분기가 아예 필요 없습니다 — `getelementptr`로 주소를 계산하고 바로 `load`하면 끝입니다.

```lean
def emitStaticGet (f : SafecArrayGet) (n : Nat) : String :=
  s!"define i32 @{f.funcName}(ptr %arr) {{\n" ++
  s!"entry:\n" ++
  s!"  %ptr = getelementptr inbounds i32, ptr %arr, i64 {n}\n" ++
  s!"  %val = load i32, ptr %ptr\n" ++
  s!"  ret i32 %val\n" ++
  s!"}}"
```

`inbounds` 키워드가 [2편](../02-safety-encoded-ir/)의 `arr.get ⟨2, by decide⟩`가 이미 정적으로 증명한 사실 — "이 접근은 항상 배열 범위 안"임을 LLVM에게 알려주는 자리입니다. LLVM은 이 키워드를 신뢰해서, 범위를 벗어나지 않는다는 가정 위에 추가 최적화(예: 여러 `inbounds` 접근의 경계 검사를 하나로 합치는 것)를 적용할 수 있습니다 — 이게 바로 [5편](../05-translation-validation/)에서 다룬 "attribute를 신뢰하는 지점"이 LLVM IR 레벨에서 나타나는 형태입니다. 만약 elaboration이 실제로는 범위를 넘는 접근에 `inbounds`를 잘못 붙였다면, LLVM은 그 잘못된 가정 위에서 **정의되지 않은 동작(UB)**을 만들어낼 수 있습니다.

런타임 인덱스(`indexLit = none`)인 경우가 진짜 흥미로운 지점입니다 — 여기서는 **기본 블록 세 개**가 필요합니다.

```lean
def emitRuntimeGet (f : SafecArrayGet) : String :=
  s!"define i32 @{f.funcName}(ptr %arr, i64 %i) {{\n" ++
  s!"entry:\n" ++
  s!"  %cmp = icmp ult i64 %i, {f.arraySize}\n" ++
  s!"  br i1 %cmp, label %safe, label %trap\n" ++
  s!"safe:\n" ++
  s!"  %ptr = getelementptr inbounds i32, ptr %arr, i64 %i\n" ++
  s!"  %val = load i32, ptr %ptr\n" ++
  s!"  ret i32 %val\n" ++
  s!"trap:\n" ++
  s!"  call void @llvm.trap()\n" ++
  s!"  unreachable\n" ++
  s!"}}"
```

이 세 블록(`entry`, `safe`, `trap`)이 정확히 [2편](../02-safety-encoded-ir/)의 `if h : i < 5 then get arr ⟨i, h⟩ else panic`이 낮춰진 형태입니다.

- `icmp ult i64 %i, 5`가 `i < 5`라는 조건을 부호 없는 비교(`ult`, unsigned less than)로 인코딩합니다 — 배열 인덱스는 음수일 수 없으므로 부호 없는 비교를 쓰는 게 맞고, 만약 방출 코드가 실수로 `slt`(signed less than)를 썼다면 이건 5절에서 다룰 독립 검사기가 잡아야 할 버그입니다.
- `br i1 %cmp, label %safe, label %trap`은 `cmp`가 참이면 `safe` 블록으로, 거짓이면 `trap` 블록으로 점프하는 **조건부 분기**입니다.
- `trap` 블록의 `call void @llvm.trap()`은 실행을 즉시 중단시키는 LLVM 내장 함수 호출이고, 그 뒤의 `unreachable`은 "이 지점 이후로는 절대 실행이 이어지지 않는다"는 걸 LLVM 최적화기에게 알려주는 명령입니다 — `trap` 다음에 `unreachable`이 없으면, LLVM은 이 블록이 어떻게든 다음 명령으로 넘어갈 수 있다고 (틀리게) 가정해 잘못된 최적화를 할 위험이 있습니다.

---

## 4. C·SystemVerilog·LLVM IR 세 타겟을 나란히 놓고 비교하기

같은 안전성 정보(`boundsChecked = false`, 런타임 검사 필요)가 세 언어에서 어떻게 다른 형태로 나타나는지 비교하면, [6편](../06-circt-systemverilog/)에서 다룬 "실행 모델이 바뀌면 안전성 증명도 형태를 바꾼다"는 원리가 더 분명해집니다.

| 타겟 | 안전성 검사의 형태 | 실패 시 동작 |
|---|---|---|
| **C** (7편) | `if (i < size) { ... } else { ... }` — 고수준 조건문 | 함수가 에러 값을 반환하거나 `abort()` 호출 |
| **SystemVerilog** (8편) | `unique case`/`default` 분기 — 멀티플렉서 선택 신호 | 회로가 확정된 상수를 출력(래치 추론 회피) |
| **LLVM IR** (이 글) | `icmp` + `br` + 별도 `trap` 블록 — 기본 블록 그래프 | `llvm.trap()` 호출 후 `unreachable`로 실행 중단 |

세 타겟 모두 **"조건을 확인하고, 실패하면 정의된 방식으로 멈춘다"**는 같은 안전성 계약을 지키지만, 그 계약을 표현하는 언어의 실행 모델(명령형 제어 흐름 / 조합 논리 회로 / 기본 블록 그래프)에 따라 완전히 다른 구문으로 나타납니다 — 이게 [4편](../04-mlir-pipeline-integration/)에서 다룬 dialect conversion이 "같은 의미를 보존하면서 표현만 바꾼다"는 게 실제로 무엇을 뜻하는지 가장 잘 보여주는 지점입니다.

---

## 5. 독립 검사기로 재확인하기: `icmp` 조건 자체가 옳은지 확인

[5편](../05-translation-validation/)과 [7편](../07-hands-on-c-emission/)에서처럼, 방출된 텍스트를 신뢰하지 않고 별도 검사기로 재확인합니다. 여기서 확인할 핵심은 **비교 연산자의 종류**입니다 — `%arraySize`, 비교 대상 술어(`ult` vs `slt` vs `ule` 등), 그리고 `trap` 블록이 실제로 `unreachable`로 끝나는지를 텍스트에서 직접 파싱해 확인합니다.

```lean
def contains (haystack needle : String) : Bool :=
  (haystack.splitOn needle).length > 1

def verifyLLVM (f : SafecArrayGet) (emitted : String) : Except String Unit := do
  if f.boundsChecked then
    -- 정적 경로: inbounds가 실제로 붙어 있는지 확인
    if !contains emitted "inbounds" then
      throw "정적으로 안전하다고 표시했는데 inbounds가 없습니다"
  else
    -- 런타임 경로: ult 비교와 trap+unreachable 쌍이 모두 있는지 확인
    if !contains emitted "icmp ult" then
      throw "부호 없는 비교(ult)가 아닙니다 — 음수 인덱스 처리가 잘못될 수 있습니다"
    if !contains emitted "unreachable" then
      throw "trap 블록에 unreachable이 없습니다 — 최적화기가 잘못된 가정을 할 수 있습니다"
  pure ()
```

이 검사기가 잡아내야 할 대표적인 버그 두 가지가 바로 위 3절에서 짚은 지점입니다 — `ult` 대신 `slt`를 잘못 방출하는 것(음수를 인덱스로 받는 경우 결과가 달라짐), 그리고 `trap` 뒤에 `unreachable`을 빠뜨리는 것(정의되지 않은 동작으로 이어짐)입니다. 둘 다 겉보기엔 "그럴듯하게 컴파일되는" 코드를 만들어내기 때문에, [5편](../05-translation-validation/)이 강조한 것처럼 **방출 코드를 그냥 신뢰하지 않고 텍스트 자체를 다시 확인하는 이 계층**이 없으면 조용히 넘어갈 수 있는 버그입니다.

---

## 6. 정리

- LLVM IR은 C나 SystemVerilog와 달리 고수준 제어 구조가 없고, 프로그램이 **기본 블록의 그래프**로 표현됩니다 — [2편](../02-safety-encoded-ir/)의 조건부 안전성 증명은 여기서 `icmp` + `br` + 별도 트랩 블록으로 낮춰집니다.
- `inbounds` 키워드는 정적으로 증명된 안전성 정보를 LLVM 최적화기에게 신뢰하라고 알려주는 자리이고, 잘못 붙이면 [5편](../05-translation-validation/)이 경고한 것과 같은 종류의 신뢰 위반이 정의되지 않은 동작(UB)으로 이어집니다.
- `trap` 다음의 `unreachable`은 "여기 이후로는 실행되지 않는다"를 최적화기에게 알려주는 필수 짝입니다 — 빠뜨리면 조용히 잘못된 최적화의 여지가 생깁니다.
- 같은 `SafecArrayGet` 하나가 C(고수준 조건문)·SystemVerilog(멀티플렉서)·LLVM IR(기본 블록 그래프) 세 가지 완전히 다른 실행 모델로 낮춰질 수 있다는 사실이, 이 시리즈 전체가 다뤄온 "하나의 증명된 안전성 정보를 여러 타겟이 공유한다"는 설계의 가장 직접적인 증거입니다.
