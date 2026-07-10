---
title: "3.4. 배열과 인덱싱"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "GetElem 타입 클래스로 배열, 리스트, 커스텀 컬렉션의 인덱싱 오버로딩하기"
---

# 3.4. Arrays and Indexing

The [Interlude](Interlude___-Propositions___-Proofs___-and-Indexing/#props-proofs-indexing) describes how to use indexing notation in order to look up entries in a list by their position.
This syntax is also governed by a type class, and it can be used for a variety of different types.

[Interlude](Interlude___-Propositions___-Proofs___-and-Indexing/#props-proofs-indexing)는 indexing notation을 사용하여 위치로 리스트의 항목을 조회하는 방법을 설명합니다.
이 문법도 type class에 의해 관리되며, 다양한 타입에 사용될 수 있습니다.

## 3.4.1. Arrays

For instance, Lean arrays are much more efficient than linked lists for most purposes.
In Lean, the type `Array α` is a dynamically-sized array holding values of type `α`, much like a Java `ArrayList`, a C++ `std::vector`, or a Rust `Vec`.
Unlike `List`, which has a pointer indirection on each use of the `cons` constructor, arrays occupy a contiguous region of memory, which is much better for processor caches.
Also, looking up a value in an array takes constant time, while lookup in a linked list takes time proportional to the index being accessed.

예를 들어, Lean array는 대부분의 용도에서 linked list보다 훨씬 더 효율적입니다.
Lean에서 `Array α` 타입은 `α` 타입의 값을 보유하는 동적 크기의 array로, Java의 `ArrayList`, C++의 `std::vector`, Rust의 `Vec`과 유사합니다.
`cons` constructor를 사용할 때마다 pointer indirection을 가지는 `List`와 달리, array는 contiguous region of memory를 차지하므로 processor cache에 훨씬 더 유리합니다.
또한 array에서 값을 조회하는 데는 상수 시간이 걸리는 반면, linked list에서의 조회는 접근하는 index에 비례하는 시간이 걸립니다.

In pure functional languages like Lean, it is not possible to mutate a given position in a data structure.
Instead, a copy is made that has the desired modifications.
However, copying is not always necessary: the Lean compiler and runtime contain an optimization that can allow modifications to be implemented as mutations behind the scenes when there is only a single unique reference to an array.

Lean 같은 pure functional language에서는 data structure의 특정 위치를 변경할 수 없습니다.
대신, 원하는 수정이 포함된 복사본이 만들어집니다.
그러나 복사가 항상 필요한 것은 아닙니다. Lean compiler와 runtime에는 array에 대한 유일한 참조가 있을 때 수정을 백그라운드에서 mutation으로 구현할 수 있게 하는 optimization이 포함되어 있습니다.

Arrays are written similarly to lists, but with a leading `#`:

Array는 list와 유사하게 작성되지만 앞에 `#`이 붙습니다:

```lean
def northernTrees : Array String :=
  #["sloe", "birch", "elm", "oak"]
```

The number of values in an array can be found using `Array.size`.
For instance, `northernTrees.size` evaluates to `4`.
For indices that are smaller than an array's size, indexing notation can be used to find the corresponding value, just as with lists.
That is, `northernTrees[2]` evaluates to `"elm"`.
Similarly, the compiler requires a proof that an index is in bounds, and attempting to look up a value outside the bounds of the array results in a compile-time error, just as with lists.
For instance, `northernTrees[8]` results in:

Array의 값의 개수는 `Array.size`를 사용하여 찾을 수 있습니다.
예를 들어, `northernTrees.size`는 `4`로 평가됩니다.
Array의 크기보다 작은 index의 경우, list와 마찬가지로 indexing notation을 사용하여 해당 값을 찾을 수 있습니다.
즉, `northernTrees[2]`는 `"elm"`으로 평가됩니다.
마찬가지로 compiler는 index가 범위 내에 있다는 증명을 요구하며, array의 범위를 벗어난 값을 조회하려고 하면 list와 마찬가지로 compile-time error가 발생합니다.
예를 들어, `northernTrees[8]`의 결과는 다음과 같습니다:

```
failed to prove index is valid, possible solutions:
  - Use `have`-expressions to prove the index is valid
  - Use `a[i]!` notation instead, runtime check is performed, and 'Panic' error message is produced if index is not valid
  - Use `a[i]?` notation instead, result is an `Option` type
  - Use `a[i]'h` notation instead, where `h` is a proof that index is valid
⊢ 8 < northernTrees.size
```

## 3.4.2. Non-Empty Lists

A datatype that represents non-empty lists can be defined as a structure with a field for the head of the list and a field for the tail, which is an ordinary, potentially empty list:

Non-empty list를 나타내는 datatype은 list의 head를 위한 field와 ordinary하고 잠재적으로 비어 있을 수 있는 list인 tail을 위한 field를 가진 structure로 정의할 수 있습니다:

```lean
structure NonEmptyList (α : Type) : Type where
  head : α
  tail : List α
```

For example, the non-empty list `idahoSpiders` (which contains some spider species native to the US state of Idaho) consists of `"Banded Garden Spider"` followed by four other spiders, for a total of five spiders:

예를 들어, non-empty list인 `idahoSpiders`(미국 아이다호 주에 자생하는 거미 종을 포함함)는 `"Banded Garden Spider"`로 시작하여 네 마리의 다른 거미가 뒤따르며, 총 다섯 마리의 거미로 구성됩니다:

```lean
def idahoSpiders : NonEmptyList String := {
  head := "Banded Garden Spider",
  tail := [
    "Long-legged Sac Spider",
    "Wolf Spider",
    "Hobo Spider",
    "Cat-faced Spider"
  ]
}
```

Looking up the value at a specific index in this list with a recursive function should consider three possibilities:

이 list에서 recursive function을 사용하여 특정 index에서 값을 조회할 때 세 가지 가능성을 고려해야 합니다:

1. The index is `0`, in which case the head of the list should be returned.
2. The index is `n + 1` and the tail is empty, in which case the index is out of bounds.
3. The index is `n + 1` and the tail is non-empty, in which case the function can be called recursively on the tail and `n`.

1. Index가 `0`인 경우, list의 head를 반환해야 합니다.
2. Index가 `n + 1`이고 tail이 비어 있는 경우, index는 범위를 벗어납니다.
3. Index가 `n + 1`이고 tail이 non-empty인 경우, function을 tail과 `n`에 대해 recursively 호출할 수 있습니다.

For example, a lookup function that returns an `Option` can be written as follows:

예를 들어, `Option`을 반환하는 lookup function은 다음과 같이 작성할 수 있습니다:

```lean
def NonEmptyList.get? : NonEmptyList α → Nat → Option α
  | xs, 0 => some xs.head
  | {head := _, tail := []}, _ + 1 => none
  | {head := _, tail := h :: t}, n + 1 => get? {head := h, tail := t} n
```

Each case in the pattern match corresponds to one of the possibilities above.
The recursive call to `get?` does not require a `NonEmptyList` namespace qualifier because the body of the definition is implicitly in the definition's namespace.
Another way to write this function uses a list lookup `xs.tail[n]?` when the index is greater than zero:

Pattern match의 각 경우는 위의 가능성 중 하나에 해당합니다.
definition의 본문이 암묵적으로 definition의 namespace에 있으므로, `get?`에 대한 recursive call은 `NonEmptyList` namespace qualifier가 필요하지 않습니다.
이 function을 작성하는 또 다른 방법은 index가 0보다 클 때 list lookup `xs.tail[n]?`을 사용합니다:

```lean
def NonEmptyList.get? : NonEmptyList α → Nat → Option α
  | xs, 0 => some xs.head
  | xs, n + 1 => xs.tail[n]?
```

If the list contains one entry, then only `0` is a valid index.
If it contains two entries, then both `0` and `1` are valid indices.
If it contains three entries, then `0`, `1`, and `2` are valid indices.
In other words, the valid indices into a non-empty list are natural numbers that are strictly less than the length of the list, which are less than or equal to the length of the tail.

List에 하나의 항목이 포함되어 있으면 `0`만 유효한 index입니다.
두 개의 항목을 포함하면 `0`과 `1` 모두 유효한 index입니다.
세 개의 항목을 포함하면 `0`, `1`, `2`가 유효한 index입니다.
즉, non-empty list에 대한 유효한 index는 list의 길이보다 strictly less than인 자연수이며, 이는 tail의 길이보다 less than or equal입니다.

The definition of what it means for an index to be in bounds should be written as an `abbrev` because the tactics used to find evidence that indices are acceptable are able to solve inequalities of numbers, but they don't know anything about the name `NonEmptyList.inBounds`:

Index가 범위 내에 있다는 것이 무엇을 의미하는지의 정의는 `abbrev`로 작성되어야 합니다. 왜냐하면 index가 허용 가능하다는 증명을 찾기 위해 사용되는 tactic들은 숫자의 부등식을 풀 수 있지만 `NonEmptyList.inBounds`라는 이름에 대해 아무것도 모르기 때문입니다:

```lean
abbrev NonEmptyList.inBounds (xs : NonEmptyList α) (i : Nat) : Prop :=
  i ≤ xs.tail.length
```

This function returns a proposition that might be true or false.
For instance, `2` is in bounds for `idahoSpiders`, while `5` is not:

이 function은 true이거나 false일 수 있는 proposition을 반환합니다.
예를 들어, `2`는 `idahoSpiders`에 대해 범위 내에 있지만, `5`는 그렇지 않습니다:

```lean
theorem atLeastThreeSpiders : idahoSpiders.inBounds 2 := by
  decide
theorem notSixSpiders : ¬idahoSpiders.inBounds 5 := by
  decide
```

```
⊢ idahoSpiders.inBounds 2
All goals completed! 🐙
⊢ ¬idahoSpiders.inBounds 5
All goals completed! 🐙
```

The logical negation operator has a very low precedence, which means that `¬idahoSpiders.inBounds 5` is equivalent to `¬(idahoSpiders.inBounds 5)`.

Logical negation operator는 매우 낮은 precedence를 가지므로, `¬idahoSpiders.inBounds 5`는 `¬(idahoSpiders.inBounds 5)`와 동치입니다.

This fact can be used to write a lookup function that requires evidence that the index is valid, and thus need not return `Option`, by delegating to the version for lists that checks the evidence at compile time:

이 사실은 index가 유효하다는 증명을 요구하고, compile time에 증명을 검사하는 list 버전으로 위임하여 `Option`을 반환할 필요가 없는 lookup function을 작성하는 데 사용될 수 있습니다:

```lean
def NonEmptyList.get (xs : NonEmptyList α)
    (i : Nat) (ok : xs.inBounds i) : α :=
  match i with
  | 0 => xs.head
  | n + 1 => xs.tail[n]
```

It is, of course, possible to write this function to use the evidence directly, rather than delegating to a standard library function that happens to be able to use the same evidence.
This requires techniques for working with proofs and propositions that are described later in this book.

물론 같은 증명을 사용할 수 있는 standard library function으로 위임하는 대신 증명을 직접 사용하도록 이 function을 작성하는 것도 가능합니다.
이는 이 책의 뒷부분에서 설명하는 proof와 proposition을 다루기 위한 기법이 필요합니다.

## 3.4.3. Overloading Indexing

Indexing notation for a collection type can be overloaded by defining an instance of the `GetElem` type class.
For the sake of flexibility, `GetElem` has four parameters:

Collection type의 indexing notation은 `GetElem` type class의 instance를 정의하여 overload할 수 있습니다.
유연성을 위해 `GetElem`은 네 가지 parameter를 가집니다:

* The type of the collection
* The type of the index
* The type of elements that are extracted from the collection
* A function that determines what counts as evidence that the index is in bounds

* Collection의 type
* Index의 type
* Collection에서 추출되는 element의 type
* Index가 범위 내에 있다는 증명으로 간주되는 것을 결정하는 function

The element type and the evidence function are both output parameters.
`GetElem` has a single method, `getElem`, which takes a collection value, an index value, and evidence that the index is in bounds as arguments, and returns an element:

Element type과 evidence function은 모두 output parameter입니다.
`GetElem`은 collection value, index value, index가 범위 내에 있다는 증명을 인자로 받고 element를 반환하는 하나의 method인 `getElem`을 가집니다:

```lean
class GetElem
    (coll : Type)
    (idx : Type)
    (item : outParam Type)
    (inBounds : outParam (coll → idx → Prop)) where
  getElem : (c : coll) → (i : idx) → inBounds c i → item
```

In the case of `NonEmptyList α`, these parameters are:

`NonEmptyList α`의 경우, 이러한 parameter는 다음과 같습니다:

* The collection is `NonEmptyList α`
* Indices have type `Nat`
* The type of elements is `α`
* An index is in bounds if it is less than or equal to the length of the tail

* Collection은 `NonEmptyList α`
* Index는 `Nat` type
* Element의 type은 `α`
* Index가 범위 내에 있으려면 tail의 길이보다 less than or equal해야 합니다

In fact, the `GetElem` instance can delegate directly to `NonEmptyList.get`:

실제로 `GetElem` instance는 `NonEmptyList.get`으로 직접 위임할 수 있습니다:

```lean
instance : GetElem (NonEmptyList α) Nat α NonEmptyList.inBounds where
  getElem := NonEmptyList.get
```

With this instance, `NonEmptyList` becomes just as convenient to use as `List`.
Evaluating `idahoSpiders.head` yields `"Banded Garden Spider"`, while `idahoSpiders[9]` leads to the compile-time error:

이 instance를 사용하면 `NonEmptyList`은 `List`를 사용하는 것만큼 편리해집니다.
`idahoSpiders.head`를 평가하면 `"Banded Garden Spider"`를 얻지만, `idahoSpiders[9]`는 compile-time error를 발생시킵니다:

```
failed to prove index is valid, possible solutions:
  - Use `have`-expressions to prove the index is valid
  - Use `a[i]!` notation instead, runtime check is performed, and 'Panic' error message is produced if index is not valid
  - Use `a[i]?` notation instead, result is an `Option` type
  - Use `a[i]'h` notation instead, where `h` is a proof that index is valid
⊢ idahoSpiders.inBounds 9
```

Because both the collection type and the index type are input parameters to the `GetElem` type class, new types can be used to index into existing collections.
The positive number type `Pos` is a perfectly reasonable index into a `List`, with the caveat that it cannot point at the first entry.
The following instance of `GetElem` allows `Pos` to be used just as conveniently as `Nat` to find a list entry:

Collection type과 index type이 모두 `GetElem` type class의 input parameter이므로, 새로운 type을 사용하여 기존 collection을 index할 수 있습니다.
Positive number type인 `Pos`는 `List`의 완전히 합리적인 index이며, 첫 번째 항목을 가리킬 수 없다는 주의사항이 있습니다.
다음의 `GetElem` instance는 `Pos`를 `Nat`만큼 편리하게 사용하여 list 항목을 찾을 수 있게 합니다:

```lean
instance : GetElem (List α) Pos α
    (fun list n => list.length > n.toNat) where
  getElem (xs : List α) (i : Pos) ok := xs[i.toNat]
```

Indexing can also make sense for non-numeric indices.
For example, `Bool` can be used to select between the fields in a point, with `false` corresponding to `x` and `true` corresponding to `y`:

Indexing은 non-numeric index에 대해서도 의미를 가질 수 있습니다.
예를 들어, `Bool`을 point의 field 사이를 선택하는 데 사용할 수 있으며, `false`는 `x`에, `true`는 `y`에 해당합니다:

```lean
instance : GetElem (PPoint α) Bool α (fun _ _ => True) where
  getElem (p : PPoint α) (i : Bool) _ :=
    if not i then p.x else p.y
```

In this case, both Booleans are valid indices.
Because every possible `Bool` is in bounds, the evidence is simply the true proposition `True`.

이 경우 두 Boolean 모두 유효한 index입니다.
모든 가능한 `Bool`이 범위 내에 있으므로, 증명은 단순히 true proposition인 `True`입니다.
