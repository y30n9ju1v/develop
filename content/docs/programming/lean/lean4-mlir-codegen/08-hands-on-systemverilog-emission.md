---
title: "8. 실습: 같은 안전 정보로 SystemVerilog 찍어보기"
date: 2026-07-14T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "mlir", "circt", "systemverilog", "hands-on"]
categories: ["programming"]
description: "7편의 C 방출 실습과 똑같은 안전성 정보(SafecArrayGet)로, 이번엔 멀티플렉서와 unique case/default 분기가 있는 SystemVerilog를 실제로 찍어내고 래치 추론 위험을 잡아내는 검사기를 Lean4로 구현합니다."
---

[7편](../07-hands-on-c-emission/)에서는 `SafecArrayGet`이라는 최소 자료구조 하나로 MLIR 텍스트와 C 코드를 실제로 찍어내고, 방출 코드의 버그를 독립 검사기로 잡아내는 것까지 Lean4 코드로 직접 돌려봤습니다. [6편](../06-circt-systemverilog/)에서는 같은 안전성 정보가 C 대신 SystemVerilog를 타겟으로 할 때 **멀티플렉서 크기**와 **`unique case`/일반 `case` 선택**을 결정한다고 손으로 보여드렸습니다. 이 글은 그 손으로 그린 예시를 7편과 똑같은 방식 — 실제로 실행하면 텍스트를 그대로 찍어내는 Lean4 코드 — 로 다시 구현합니다.

---

## 1. 이 실습이 보여주는 것

7편과 마찬가지로 진짜 CIRCT 툴체인이나 `circt-translate`를 설치하지 않습니다. 대신 [6편](../06-circt-systemverilog/)에서 손으로 보여드렸던 두 결과물 — `bounds_checked = true`일 때의 `unique case`와, `false`일 때의 `default` 분기가 붙은 일반 `case` — 을 **같은 `SafecArrayGet` 값**으로부터 함수가 실제로 만들어내는 과정을 다룹니다. 7편의 `toC`가 conversion pattern 하나였다면, 이 글의 `toSystemVerilog`는 **같은 IR에서 갈라지는 또 하나의 conversion pattern**입니다 — [6편](../06-circt-systemverilog/#2-circt의-dialect-스택-emitc의-자리에-sv가-들어온다)에서 그렸던 "같은 `safec` dialect에서 두 경로로 갈라진다"는 그림이, 여기서는 "같은 `SafecArrayGet` 값에서 `toC`와 `toSystemVerilog` 두 함수로 갈라진다"는 형태로 재현됩니다.

---

## 2. 자료구조는 그대로, 값 하나만 다시 씁니다

7편의 `SafecArrayGet` 구조체를 그대로 재사용합니다.

```lean
structure SafecArrayGet where
  funcName      : String
  arraySize     : Nat
  indexLit      : Option Nat
  boundsChecked : Bool
```

다만 이번엔 [6편](../06-circt-systemverilog/#3-배열-접근이-멀티플렉서가-될-때-안전성-증명은-형태를-바꾼다)의 예제에 맞춰, `indexLit`을 쓰지 않는(런타임 인덱스 `idx`로 원소를 고르는) 경우를 기본으로 둡니다 — 멀티플렉서는 애초에 "인덱스로 여러 원소 중 하나를 고른다"는 연산이라, 상수 인덱스보다 런타임 인덱스 케이스가 하드웨어 타겟에서 더 대표적입니다.

```lean
def hwGetChecked : SafecArrayGet :=
  { funcName := "get_element", arraySize := 5, indexLit := none, boundsChecked := true }

def hwGetUnchecked : SafecArrayGet :=
  { funcName := "get_user_index", arraySize := 5, indexLit := none, boundsChecked := false }
```

`boundsChecked = true`인데 `indexLit`이 `none`인 조합이 이상해 보일 수 있는데, [6편](../06-circt-systemverilog/#3-배열-접근이-멀티플렉서가-될-때-안전성-증명은-형태를-바꾼다)에서 다룬 것과 같은 상황입니다 — `idx`가 상수는 아니지만 `Fin 5` 타입으로 "0~4 사이의 값"이라는 게 정적으로 증명되어 있는 경우입니다. 즉 여기서 `boundsChecked`가 뜻하는 건 "인덱스가 상수다"가 아니라 "인덱스의 범위가 증명되어 있다"입니다.

---

## 3. SystemVerilog 텍스트를 실제로 찍어내기

[6편](../06-circt-systemverilog/#3-배열-접근이-멀티플렉서가-될-때-안전성-증명은-형태를-바꾼다)에서 손으로 짰던 두 버전을, 이제 함수 하나로 만듭니다.

```lean
def toSystemVerilog (e : SafecArrayGet) : String :=
  let cases := String.join
    ((List.range e.arraySize).map (fun i =>
      s!"    3'd{i}: val = arr_{i};\n"))
  if e.boundsChecked then
    s!"// bounds_checked = true — \"그 외의 경우\"가 애초에 없다\n" ++
    s!"always_comb begin\n" ++
    s!"  unique case (idx)\n" ++
    cases ++
    s!"  endcase\n" ++
    s!"end\n"
  else
    s!"// bounds_checked = false — 정의되지 않은 idx 값에 대비해야 한다\n" ++
    s!"always_comb begin\n" ++
    s!"  case (idx)\n" ++
    cases ++
    s!"    default: val = 32'd0;  // 이 분기가 없으면 래치가 추론될 수 있다\n" ++
    s!"  endcase\n" ++
    s!"end\n"

#eval IO.println (toSystemVerilog hwGetChecked)
#eval IO.println (toSystemVerilog hwGetUnchecked)
```

`List.range e.arraySize`로 `arraySize`(여기서는 5)만큼의 case 절을 자동으로 만들어낸다는 점이 7편의 `toC`와 다릅니다 — C 방출은 배열 크기와 무관하게 `arr[idx]`라는 한 줄이면 충분했지만, 멀티플렉서는 **원소 개수만큼 case 절을 전부 나열해야** 하므로 방출 코드가 배열 크기에 따라 반복 구조를 생성해야 합니다. 이 `cases` 문자열이 두 분기(`true`/`false`)에서 똑같이 재사용된다는 것도 눈여겨볼 부분입니다 — [6편](../06-circt-systemverilog/#3-배열-접근이-멀티플렉서가-될-때-안전성-증명은-형태를-바꾼다)에서 강조했듯, `bounds_checked`가 바꾸는 건 각 원소를 고르는 case 절 자체가 아니라 그 케이스들이 **전부인지 아닌지를 선언하는 방식**(`unique` 유무, `default` 유무)뿐입니다.

실행하면 정확히 6편에서 손으로 보여드렸던 두 텍스트가 그대로 나옵니다.

```systemverilog
// bounds_checked = true — "그 외의 경우"가 애초에 없다
always_comb begin
  unique case (idx)
    3'd0: val = arr_0;
    3'd1: val = arr_1;
    3'd2: val = arr_2;
    3'd3: val = arr_3;
    3'd4: val = arr_4;
  endcase
end
```

```systemverilog
// bounds_checked = false — 정의되지 않은 idx 값에 대비해야 한다
always_comb begin
  case (idx)
    3'd0: val = arr_0;
    3'd1: val = arr_1;
    3'd2: val = arr_2;
    3'd3: val = arr_3;
    3'd4: val = arr_4;
    default: val = 32'd0;  // 이 분기가 없으면 래치가 추론될 수 있다
  endcase
end
```

---

## 4. 래치 위험을 잡는 독립 검사기

7편의 `verifyBounds`가 "attribute가 실제로 안전한가"를 재확인했다면, 이번엔 "**방출된 SystemVerilog가 실제로 모든 `idx` 값에 대해 완전한가**"를 재확인하는 검사기를 만듭니다. [6편](../06-circt-systemverilog/#5-exportverilog-emitc와-같은-역할-다른-완전성-기준)에서 다룬 것처럼, 이 완전성 조건은 C 타겟에는 없던 하드웨어 고유의 요구사항입니다.

```lean
def verifyCompleteness (e : SafecArrayGet) (generatedSv : String) : Except String Unit :=
  if e.boundsChecked then
    if generatedSv.splitOn "unique case" |>.length > 1 then .ok ()
    else .error "bounds_checked=true인데 unique case가 아님 — 완전성 선언 누락"
  else
    if generatedSv.splitOn "default:" |>.length > 1 then .ok ()
    else .error "bounds_checked=false인데 default 분기가 없음 — 래치 추론 위험"

#eval verifyCompleteness hwGetChecked   (toSystemVerilog hwGetChecked)    -- [ok]
#eval verifyCompleteness hwGetUnchecked (toSystemVerilog hwGetUnchecked)  -- [ok]
```

이제 [7편](../07-hands-on-c-emission/#5-독립-검사기도-실제로-돌려보기)에서 만들었던 것과 같은 종류의 결함을 하드웨어 타겟에 주입해봅니다 — `toSystemVerilog` 자체에 버그가 있어서, `false` 케이스인데도 실수로 `default` 분기를 빼먹은 상황을 가정합니다.

```lean
def buggyToSystemVerilog (e : SafecArrayGet) : String :=
  let cases := String.join
    ((List.range e.arraySize).map (fun i => s!"    3'd{i}: val = arr_{i};\n"))
  -- 버그: bounds_checked = false인데도 default 분기를 빼먹음
  s!"always_comb begin\n  case (idx)\n" ++ cases ++ s!"  endcase\nend\n"

#eval IO.println (buggyToSystemVerilog hwGetUnchecked)
#eval verifyCompleteness hwGetUnchecked (buggyToSystemVerilog hwGetUnchecked)
-- [error] bounds_checked=false인데 default 분기가 없음 — 래치 추론 위험
```

`buggyToSystemVerilog hwGetUnchecked`를 그냥 실행하면, `idx`가 5 이상인 입력이 들어왔을 때 `val`이 이전 값을 그대로 유지하는 **래치**가 합성 도구에 의해 조용히 추론됩니다 — 시뮬레이션에서는 한동안 멀쩡히 동작하다가, [6편](../06-circt-systemverilog/#6-신뢰-사슬의-마지막-고리가-하드웨어에서는-더-무겁다)에서 경고했듯 칩이 제작된 뒤에야 타이밍 문제로 드러날 수 있는 종류의 결함입니다. `verifyCompleteness`가 이 결함을 `toSystemVerilog`가 참조한 것과 같은 attribute(`boundsChecked`)를 다시 믿는 대신, **방출된 텍스트 자체에 `default:`라는 문자열이 있는지**를 직접 확인해서 잡아냅니다.

---

## 5. 이 검사기의 빈틈: 문자열 검사는 의미를 보지 않는다

`verifyCompleteness`가 `default:`라는 부분 문자열의 존재만 확인한다는 점은, [7편](../07-hands-on-c-emission/#6-verifybounds의-빈틈-false-케이스는-정말-안전한가)에서 지적한 것과 똑같은 종류의 한계를 갖습니다. 예를 들어 이런 코드는 검사를 통과하지만 실제로는 잘못되었습니다.

```systemverilog
always_comb begin
  case (idx)
    3'd0: val = arr_0;
    // default: val = 32'd0;  <- 주석 처리된 코드
  endcase
end
```

`splitOn "default:"`는 이게 실제 SystemVerilog 코드인지 주석인지 구분하지 못하므로, 이 텍스트에도 `.ok ()`를 반환해버립니다. 진짜 완전성 검증이라면 SystemVerilog 파서로 텍스트를 다시 구문 분석해서 `default` 분기가 실제 `case` 블록 안에 살아있는 코드로 존재하는지 확인해야 합니다 — 이건 [5편](../05-translation-validation/#2-mlir-텍스트-자체를-재확인하기)에서 다룬 "얕고 국소적인 사실에는 순진한 검증이 통하지만, 진짜 견고한 검증에는 파서가 필요하다"는 원칙이 소프트웨어 타겟(7편)에 이어 하드웨어 타겟에서도 똑같이 반복되는 지점입니다.

---

## 6. 7편과 나란히 놓고 보는 대칭

7편의 `toC`/`verifyBounds`와 이 글의 `toSystemVerilog`/`verifyCompleteness`를 나란히 놓으면, [6편](../06-circt-systemverilog/#7-이-글의-정리)에서 정리했던 "신뢰 사슬의 구조는 동일하지만 무엇을 재확인하는지는 타겟마다 다르다"는 결론이 코드 레벨에서 그대로 드러납니다.

| | 7편: C 타겟 | 8편(이 글): SystemVerilog 타겟 |
|---|---|---|
| 방출 함수 | `toC` | `toSystemVerilog` |
| `bounds_checked=true`일 때 | 검사 없는 `arr[idx]` | `unique case` (그 외의 경우 없음 선언) |
| `bounds_checked=false`일 때 | `if (i<size)` 가드 삽입 | `default` 분기 삽입 |
| 검사기 | `verifyBounds`/`verifyBoundsAdvanced` | `verifyCompleteness` |
| 검사기가 막는 결함 | 버퍼 오버플로우 | 래치 추론 |
| 검사기의 공통 한계 | 텍스트 부분 문자열 검사, 의미(파싱) 확인 아님 | 동일 |

두 타겟 모두 같은 `SafecArrayGet` 값에서 출발하고, 같은 구조(방출 함수가 attribute로 분기 → 독립 검사기가 방출 결과를 재확인)를 갖지만, **무엇이 위험한 결함인지**(오버플로우 vs 래치)와 **무엇으로 그 결함을 확인하는지**(가드문 존재 vs 완전성 선언 존재)는 타겟의 실행 모델에 따라 완전히 달라집니다.

---

## 7. 정리

- [7편](../07-hands-on-c-emission/)과 똑같은 `SafecArrayGet` 자료구조 하나로, C 대신 SystemVerilog를 찍어내는 `toSystemVerilog` 함수를 실제로 실행 가능한 Lean4 코드로 구현했습니다.
- `bounds_checked` attribute는 하드웨어 타겟에서 "런타임 분기의 유무"가 아니라 "`unique case`로 완전성을 선언할지, `default` 분기로 안전망을 깔지"를 결정합니다 — [6편](../06-circt-systemverilog/)에서 손으로 보여드린 원리가 실제 코드로 재현됩니다.
- `verifyCompleteness`는 `toSystemVerilog`가 참조한 것과 같은 attribute를 다시 믿는 대신, 방출된 텍스트에서 `unique case`/`default` 분기의 존재를 직접 확인해 래치 추론 위험을 잡아냅니다.
- 이 검사기도 7편의 `verifyBoundsAdvanced`와 마찬가지로 텍스트 수준의 얕은 확인이라는 한계를 갖고 있으며, 진짜 완전성 검증은 SystemVerilog를 다시 파싱해야 합니다.

7편과 8편을 합치면, [4편](../04-mlir-pipeline-integration/)과 [6편](../06-circt-systemverilog/)에서 각각 손으로 그렸던 두 타겟(C, SystemVerilog)의 전체 파이프라인 — "같은 안전 정보 → 타겟별 방출 함수 → 타겟별 독립 검사기" — 이 전부 실제로 실행 가능한 코드로 확인된 셈입니다.
