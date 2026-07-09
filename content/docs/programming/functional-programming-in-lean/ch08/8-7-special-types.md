---
title: "Special Types"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Special Types"
---

# 8.7. Special Types

Understanding the representation of data in memory is very important.
Usually, the representation can be understood from the definition of a datatype.
Each constructor corresponds to an object in memory that has a header that includes a tag and a reference count.
The constructor's arguments are each represented by a pointer to some other object.
In other words, `List` really is a linked list and extracting a field from a `structure` really does just chase a pointer.

메모리에서 데이터의 표현을 이해하는 것은 매우 중요합니다.
일반적으로 표현은 데이터타입의 정의에서 이해할 수 있습니다.
각 생성자는 태그와 참조 카운트를 포함하는 헤더를 가진 메모리의 객체에 해당합니다.
생성자의 인수들은 각각 다른 객체를 가리키는 포인터로 표현됩니다.
즉, `List`는 정말로 연결 리스트이고 `structure`에서 필드를 추출하는 것은 정말로 단지 포인터를 따라갑니다.

There are, however, some important exceptions to this rule.
A number of types are treated specially by the compiler.
For example, the type `UInt32` is defined as `Fin (2 ^ 32)`, but it is replaced at run-time with an actual native implementation based on machine words.
Similarly, even though the definition of `Nat` suggests an implementation similar to `List Unit`, the actual run-time representation uses immediate machine words for sufficiently-small numbers and an efficient arbitrary-precision arithmetic library for larger numbers.
The Lean compiler translates from definitions that use pattern matching into the appropriate operations for this representation, and calls to operations like addition and subtraction are mapped to fast operations from the underlying arithmetic library.
After all, addition should not take time linear in the size of the addends.

그러나 이 규칙에는 몇 가지 중요한 예외가 있습니다.
여러 타입이 컴파일러에 의해 특별히 처리됩니다.
예를 들어, `UInt32` 타입은 `Fin (2 ^ 32)`로 정의되지만 런타임에 머신 워드 기반의 실제 네이티브 구현으로 교체됩니다.
마찬가지로, `Nat`의 정의가 `List Unit`과 유사한 구현을 제안하더라도, 실제 런타임 표현은 충분히 작은 숫자의 경우 즉시 머신 워드를 사용하고 더 큰 숫자의 경우 효율적인 임의 정밀도 산술 라이브러리를 사용합니다.
Lean 컴파일러는 패턴 매칭을 사용하는 정의에서 이 표현에 적절한 작업으로 변환하고, 덧셈 및 뺄셈과 같은 작업에 대한 호출은 기본 산술 라이브러리의 빠른 작업으로 매핑됩니다.
결국 덧셈은 피연산자의 크기에 선형 시간을 가져야 하지 않습니다.

The fact that some types have special representations also means that care is needed when working with them.
Most of these types consist of a `structure` that is treated specially by the compiler.
With these structures, using the constructor or the field accessors directly can trigger an expensive conversion from an efficient representation to a slow one that is convenient for proofs.
For example, `String` is defined as a structure that contains a list of characters, but the run-time representation of strings uses UTF-8, not linked lists of pointers to characters.
Applying the constructor to a list of characters creates a byte array that encodes them in UTF-8, and accessing the field of the structure takes time linear in the length of the string to decode the UTF-8 representation and allocate a linked list.
Arrays are represented similarly.
From the logical perspective, arrays are structures that contain a list of array elements, but the run-time representation is a dynamically-sized array.
At run time, the constructor translates the list into an array, and the field accessor allocates a linked list from the array.
The various array operations are replaced with efficient versions by the compiler that mutate the array when possible instead of allocating a new one.

일부 타입이 특별한 표현을 가지고 있다는 사실은 이들을 다룰 때 주의가 필요하다는 의미이기도 합니다.
이러한 타입 대부분은 컴파일러에 의해 특별히 처리되는 `structure`로 구성됩니다.
이러한 구조를 사용하면, 생성자 또는 필드 접근자를 직접 사용하면 효율적인 표현에서 증명에 편리한 느린 표현으로의 비용이 많이 드는 변환을 트리거할 수 있습니다.
예를 들어, `String`은 문자 목록을 포함하는 구조체로 정의되지만, 문자열의 런타임 표현은 문자에 대한 포인터의 연결 리스트가 아닌 UTF-8을 사용합니다.
생성자를 문자 목록에 적용하면 UTF-8로 인코딩된 바이트 배열이 생성되며, 구조체의 필드에 액세스하는 데는 UTF-8 표현을 디코딩하고 연결 리스트를 할당하기 위해 문자열 길이에 선형 시간이 걸립니다.
배열도 유사하게 표현됩니다.
논리적 관점에서 배열은 배열 요소 목록을 포함하는 구조체이지만, 런타임 표현은 동적 크기 배열입니다.
런타임에 생성자는 목록을 배열로 변환하고 필드 접근자는 배열에서 연결 리스트를 할당합니다.
다양한 배열 작업은 컴파일러에 의해 새 배열을 할당하는 대신 가능한 경우 배열을 변경하는 효율적인 버전으로 대체됩니다.

Both types themselves and proofs of propositions are completely erased from compiled code.
In other words, they take up no space, and any computations that might have been performed as part of a proof are similarly erased.
This means that proofs can take advantage of the convenient interface to strings and arrays as inductively-defined lists, including using induction to prove things about them, without imposing slow conversion steps while the program is running.
For these built-in types, a convenient logical representation of the data does not imply that the program must be slow.

타입 자체와 명제의 증명은 모두 컴파일된 코드에서 완전히 삭제됩니다.
즉, 그들은 공간을 차지하지 않으며, 증명의 일부로 수행되었을 수 있는 모든 계산도 마찬가지로 삭제됩니다.
이는 증명이 문자열 및 배열에 대한 편리한 인터페이스를 귀납적으로 정의된 목록으로 활용할 수 있다는 의미입니다. 여기에는 이들에 대한 것을 증명하기 위해 귀납법을 사용하는 것이 포함되며, 프로그램이 실행되는 동안 느린 변환 단계를 부과하지 않습니다.
이러한 내장 타입의 경우, 편리한 논리 데이터 표현은 프로그램이 느려야 한다는 것을 의미하지 않습니다.

If a structure type has only a single non-type non-proof field, then the constructor itself disappears at run time, being replaced with its single argument.
In other words, a subtype is represented identically to its underlying type, rather than with an extra layer of indirection.
Similarly, `Fin` is just `Nat` in memory, and single-field structures can be created to keep track of different uses of `Nat`s or `String`s without paying a performance penalty.
If a constructor has no non-type non-proof arguments, then the constructor also disappears and is replaced with a constant value where the pointer would otherwise be used.
This means that `true`, `false`, and `none` are constant values, rather than pointers to heap-allocated objects.

구조체 타입이 단 하나의 비타입 비증명 필드만 가지고 있으면, 생성자 자체는 런타임에 사라지고 단일 인수로 교체됩니다.
즉, 부분타입은 추가 간접 참조 계층이 아니라 기본 타입과 동일하게 표현됩니다.
마찬가지로, `Fin`은 메모리의 단지 `Nat`이며, 성능 페널티를 지불하지 않고 `Nat` 또는 `String`의 다양한 사용을 추적하기 위해 단일 필드 구조체를 만들 수 있습니다.
생성자가 비타입 비증명 인수가 없으면, 생성자도 사라지고 포인터가 사용될 곳에 상수 값으로 교체됩니다.
이는 `true`, `false`, `none`이 힙 할당 객체에 대한 포인터가 아니라 상수 값이라는 의미입니다.

The following types have special representations:

| Type | Logical representation | Run-time Representation |
| --- | --- | --- |
| `Nat` | Unary, with one pointer from each `Nat.succ` | Efficient arbitrary-precision integers |
| `Int` | A sum type with constructors for positive or negative values, each containing a `Nat` | Efficient arbitrary-precision integers |
| `BitVec w` | A `Fin` with an appropriate bound `2^w` | Efficient arbitrary-precision integers |
| `UInt8`, `UInt16`, `UInt32`, `UInt64`, `USize` | A bitvector of the correct width | Fixed-precision machine integers |
| `Int8`, `Int16`, `Int32`, `Int64`, `ISize` | A wrapped unsigned integer of the same width | Fixed-precision machine integers |
| `Char` | A `UInt32` paired with a proof that it's a valid code point | Ordinary characters |
| `String` | A structure that contains a `List Char` in a field called `data` | UTF-8-encoded string |
| `Array α` | A structure that contains a `List α` in a field called `toList` | Packed arrays of pointers to `α` values |
| `Sort u` | A type | Erased completely |
| Proofs of propositions | Whatever data is suggested by the proposition when considered as a type of evidence | Erased completely |

## 8.7.1. Exercise

[`Pos`의 정의](../ch03/)는 Lean의 `Nat` 컴파일을 효율적인 타입으로 활용하지 않습니다.
런타임에 기본적으로 연결 목록입니다.
또는 [부분타입의 초기 섹션](Functors___-Applicative-Functors___-and-Monads/Applicative-Functors/#subtypes)에서 설명한 대로 Lean의 빠른 `Nat` 타입을 내부적으로 사용할 수 있는 부분타입을 정의할 수 있습니다.
런타임에 증명은 삭제됩니다.
결과 구조에 단일 데이터 필드만 있으므로, 그 필드로 표현되며, 이는 `Pos`의 이 새로운 표현이 `Nat`의 표현과 동일하다는 의미입니다.

정리 `∀ {n k : Nat}, n ≠ 0 → k ≠ 0 → n + k ≠ 0`을 증명한 후, `Pos`의 이 새로운 표현에 대해 `ToString` 및 `Add`의 인스턴스를 정의합니다. 그런 다음, `Mul`의 인스턴스를 정의하고 필요한 모든 정리를 증명하십시오.
