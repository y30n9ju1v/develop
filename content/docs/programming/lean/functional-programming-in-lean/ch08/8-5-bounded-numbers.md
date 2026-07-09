---
title: "Bounded Numbers"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Bounded Numbers"
---

# 8.5. Bounded Numbers

The `GetElem` instance for `Array` and `Nat` requires a proof that the provided `Nat` is smaller than the array.
In practice, these proofs often end up being passed to functions along with the indices.
Rather than passing an index and a proof separately, a type called `Fin` can be used to bundle up the index and the proof into a single value.
This can make code easier to read.

`Array`와 `Nat`에 대한 `GetElem` 인스턴스는 제공된 `Nat`이 배열보다 작다는 증명이 필요합니다.
실제로, 이러한 증명은 종종 인덱스와 함께 함수로 전달됩니다.
인덱스와 증명을 따로 전달하는 대신, `Fin`이라는 타입을 사용하여 인덱스와 증명을 하나의 값으로 묶을 수 있습니다.
이렇게 하면 코드를 더 쉽게 읽을 수 있습니다.

The type `Fin n` represents numbers that are strictly less than `n`.
In other words, `Fin 3` describes `0`, `1`, and `2`, while `Fin 0` has no values at all.
The definition of `Fin` resembles `Subtype`, as a `Fin n` is a structure that contains a `Nat` and a proof that it is less than `n`:

`Fin n` 타입은 `n`보다 엄격히 작은 숫자를 나타냅니다.
즉, `Fin 3`은 `0`, `1`, `2`를 나타내고, `Fin 0`은 어떤 값도 가지지 않습니다.
`Fin`의 정의는 `Subtype`과 유사합니다. `Fin n`은 `Nat`과 그것이 `n`보다 작다는 증명을 포함하는 구조체입니다:

`structure Fin (n : Nat) where
val : Nat
isLt : LT.lt val n`

Lean includes instances of `ToString` and `OfNat` that allow `Fin` values to be conveniently used as numbers.
In other words, the output of `#eval (5 : Fin 8)` is `5`, rather than something like `{val := 5, isLt := _}`.

Lean은 `Fin` 값이 편리하게 숫자로 사용될 수 있도록 `ToString`과 `OfNat`의 인스턴스를 포함합니다.
즉, `#eval (5 : Fin 8)`의 출력은 `{val := 5, isLt := _}`와 같은 것이 아니라 `5`입니다.

Instead of failing when the provided number is larger than the bound, the `OfNat` instance for `Fin` returns a value modulo the bound.
This means that `#eval (45 : Fin 10)` results in `5` rather than a compile-time error.

제공된 숫자가 한계보다 클 때 실패하는 대신, `Fin`에 대한 `OfNat` 인스턴스는 한계에 대한 나머지 값을 반환합니다.
이는 `#eval (45 : Fin 10)`이 컴파일 타임 오류가 아니라 `5`를 반환한다는 의미입니다.

In a return type, a `Fin` returned as a found index makes its connection to the data structure in which it was found more clear.
The `Array.find` in the [previous section](Programming___-Proving___-and-Performance/Arrays-and-Termination/#proving-termination) returns an index that the caller cannot immediately use to perform lookups into the array, because the information about its validity has been lost.
A more specific type results in a value that can be used without making the program significantly more complicated:

반환 타입에서, 찾은 인덱스로 반환된 `Fin`은 찾은 데이터 구조와의 연결을 더 명확하게 만듭니다.
[이전 섹션](Programming___-Proving___-and-Performance/Arrays-and-Termination/#proving-termination)의 `Array.find`는 호출자가 배열을 검색하는 데 즉시 사용할 수 없는 인덱스를 반환합니다. 왜냐하면 유효성에 대한 정보가 손실되었기 때문입니다.
더 구체적인 타입은 프로그램을 상당히 복잡하게 하지 않고도 사용할 수 있는 값을 만듭니다:

`def findHelper (arr : Array α) (p : α → Bool) (i : Nat) :
Option (Fin arr.size × α) :=
if h : i < arr.size then
let x := arr[i]
if p x then
some (⟨i, h⟩, x)
else findHelper arr p (i + 1)
else none``def Array.find (arr : Array α) (p : α → Bool) : Option (Fin arr.size × α) :=
findHelper arr p 0`
