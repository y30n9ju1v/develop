---
title: "8.6. 삽입 정렬과 배열 변경 (Insertion Sort and Array Mutation)"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "삽입 정렬과 배열 변경 (Insertion Sort and Array Mutation)"
---

# 8.6. Insertion Sort and Array Mutation

While insertion sort does not have the optimal worst-case time complexity for a sorting algorithm, it still has a number of useful properties:

삽입 정렬은 정렬 알고리즘의 최적 최악의 경우 시간 복잡도를 가지지는 않지만, 여전히 많은 유용한 특성을 가지고 있습니다:

* It is simple and straightforward to implement and understand
* It is an in-place algorithm, requiring no additional space to run
* It is a stable sort
* It is fast when the input is already almost sorted

* 구현하고 이해하기가 간단하고 명확합니다
* In-place 알고리즘으로, 실행하는 데 추가 공간이 필요하지 않습니다
* 안정 정렬입니다
* 입력이 이미 거의 정렬되어 있을 때 빠릅니다

In-place algorithms are particularly useful in Lean due to the way it manages memory.
In some cases, operations that would normally copy an array can be optimized into mutation.
This includes swapping elements in an array.

In-place 알고리즘은 Lean의 메모리 관리 방식 때문에 특히 유용합니다.
어떤 경우에는 일반적으로 배열을 복사하는 작업을 변경 최적화로 변환할 수 있습니다.
여기에는 배열의 요소 교환도 포함됩니다.

Most languages and run-time systems with automatic memory management, including JavaScript, the JVM, and .NET, use tracing garbage collection.
When memory needs to be reclaimed, the system starts at a number of *roots* (such as the call stack and global values) and then determines which values can be reached by recursively chasing pointers.
Any values that can't be reached are deallocated, freeing memory.

JavaScript, JVM, .NET를 포함한 자동 메모리 관리가 있는 대부분의 언어 및 런타임 시스템은 추적 garbage collection을 사용합니다.
메모리를 회수해야 할 때, 시스템은 여러 *root*(예: 호출 스택 및 전역 값)에서 시작하여 포인터를 재귀적으로 따라 어떤 값에 도달할 수 있는지 결정합니다.
도달할 수 없는 값들은 할당이 해제되어 메모리가 해제됩니다.

Reference counting is an alternative to tracing garbage collection that is used by a number of languages, including Python, Swift, and Lean.
In a system with reference counting, each object in memory has a field that tracks how many references there are to it.
When a new reference is established, the counter is incremented.
When a reference ceases to exist, the counter is decremented.
When the counter reaches zero, the object is immediately deallocated.

Reference counting은 Python, Swift, Lean을 포함한 여러 언어에서 사용하는 추적 garbage collection의 대안입니다.
Reference counting 시스템에서, 메모리의 각 객체는 그에 대한 참조가 몇 개인지를 추적하는 필드를 가집니다.
새로운 참조가 생성되면, 카운터가 증가합니다.
참조가 사라지면, 카운터가 감소합니다.
카운터가 0에 도달하면, 객체는 즉시 할당이 해제됩니다.

Reference counting has one major disadvantage compared to a tracing garbage collector: circular references can lead to memory leaks.
If object `A` references object `B` , and object `B` references object `A`, they will never be deallocated, even if nothing else in the program references either `A` or `B`.
Circular references result either from uncontrolled recursion or from mutable references.
Because Lean supports neither, it is impossible to construct circular references.

Reference counting은 추적 garbage collector와 비교할 때 한 가지 주요 단점이 있습니다: 순환 참조는 메모리 누수를 초래할 수 있습니다.
객체 `A`가 객체 `B`를 참조하고 객체 `B`가 객체 `A`를 참조하면, 프로그램의 다른 부분이 `A`나 `B`를 참조하지 않아도 절대 할당이 해제되지 않습니다.
순환 참조는 제어되지 않는 재귀 또는 가변 참조에서 발생합니다.
Lean은 둘 다 지원하지 않으므로, 순환 참조를 구성하는 것은 불가능합니다.

Reference counting means that the Lean runtime system's primitives for allocating and deallocating data structures can check whether a reference count is about to fall to zero, and re-use an existing object instead of allocating a new one.
This is particularly important when working with large arrays.

Reference counting은 Lean 런타임 시스템의 데이터 구조 할당/해제 원시 연산이 reference count가 0에 떨어지려고 하는지 확인하고, 새 객체를 할당하는 대신 기존 객체를 재사용할 수 있다는 의미입니다.
이는 특히 큰 배열로 작업할 때 중요합니다.

An implementation of insertion sort for Lean arrays should satisfy the following criteria:

Lean 배열에 대한 삽입 정렬 구현은 다음 기준을 만족해야 합니다:

1. Lean should accept the function without a `partial` annotation
2. If passed an array to which there are no other references, it should modify the array in-place rather than allocating a new one

1. Lean은 `partial` 주석 없이 함수를 수용해야 합니다
2. 다른 참조가 없는 배열이 전달되면, 새 배열을 할당하지 않고 배열을 in-place로 수정해야 합니다

The first criterion is easy to check: if Lean accepts the definition, then it is satisfied.
The second, however, requires a means of testing it.
Lean provides a built-in function called `dbgTraceIfShared` with the following signature:

첫 번째 기준은 확인하기 쉽습니다: Lean이 정의를 수용하면, 그것이 만족됩니다.
그러나 두 번째는 이를 테스트할 수단이 필요합니다.
Lean은 다음 서명을 가진 `dbgTraceIfShared`라는 내장 함수를 제공합니다:

```lean
#check dbgTraceIfShared
```

```
dbgTraceIfShared.{u} {α : Type u} (s : String) (a : α) : α
```

It takes a string and a value as arguments, and prints a message that uses the string to standard error if the value has more than one reference, returning the value.
This is not, strictly speaking, a pure function.
However, it is intended to be used only during development to check that a function is in fact able to re-use memory rather than allocating and copying.

문자열과 값을 인수로 받고, 값이 하나 이상의 참조를 가지면 표준 오류에 문자열을 사용하는 메시지를 출력하고 값을 반환합니다.
엄격히 말하면, 이것은 순수 함수가 아닙니다.
그러나 이는 개발 중에만 함수가 실제로 메모리를 재사용할 수 있는지 할당 및 복사 대신 확인하기 위해 사용하려고 합니다.

When learning to use `dbgTraceIfShared`, it's important to know that `#eval` will report that many more values are shared than in compiled code.
This can be confusing.
It's important to build an executable with `lake` rather than experimenting in an editor.

`dbgTraceIfShared`를 사용하는 방법을 배울 때, `#eval`이 컴파일된 코드보다 훨씬 더 많은 값이 공유된다고 보고할 것이라는 점을 아는 것이 중요합니다.
이것은 혼동을 줄 수 있습니다.
편집기에서 실험하는 것이 아니라 `lake`를 사용하여 실행 파일을 구성하는 것이 중요합니다.

Insertion sort consists of two loops.
The outer loop moves a pointer from left to right across the array to be sorted.
After each iteration, the region of the array to the left of the pointer is sorted, while the region to the right may not yet be sorted.
The inner loop takes the element pointed to by the pointer and moves it to the left until the appropriate location has been found and the loop invariant has been restored.
In other words, each iteration inserts the next element of the array into the appropriate location in the sorted region.

삽입 정렬은 두 개의 루프로 구성됩니다.
외부 루프는 정렬할 배열 전체에서 포인터를 왼쪽에서 오른쪽으로 이동합니다.
각 반복 후, 포인터의 왼쪽 영역은 정렬되지만, 오른쪽 영역은 아직 정렬되지 않을 수 있습니다.
내부 루프는 포인터가 가리키는 요소를 가져와서 적절한 위치를 찾고 루프 불변식이 복원될 때까지 왼쪽으로 이동합니다.
다시 말해, 각 반복은 배열의 다음 요소를 정렬된 영역의 적절한 위치에 삽입합니다.

## 8.6.1. The Inner Loop

The inner loop of insertion sort can be implemented as a tail-recursive function that takes the array and the index of the element being inserted as arguments.
The element being inserted is repeatedly swapped with the element to its left until either the element to the left is smaller or the beginning of the array is reached.
The inner loop is structurally recursive on the `Nat` that is inside the `Fin` used to index into the array:

```lean
def insertSorted [Ord α] (arr : Array α) (i : Fin arr.size) : Array α :=
  match i with
  | ⟨0, _⟩ => arr
  | ⟨i' + 1, _⟩ =>
    have : i' < arr.size := by
      grind
    match Ord.compare arr[i'] arr[i] with
    | .lt | .eq => arr
    | .gt =>
      insertSorted (arr.swap i' i) ⟨i', by simp [*]⟩
```

If the index `i` is `0`, then the element being inserted into the sorted region has reached the beginning of the region and is the smallest.
If the index is `i' + 1`, then the element at `i'` should be compared to the element at `i`.
Note that while `i` is a `Fin arr.size`, `i'` is just a `Nat` because it results from the `val` field of `i`.
Nonetheless, the proof automation used for checking array index notation includes a solver for linear integer arithmetic, so `i'` is automatically usable as an index.

The two elements are looked up and compared.
If the element to the left is less than or equal to the element being inserted, then the loop is finished and the invariant has been restored.
If the element to the left is greater than the element being inserted, then the elements are swapped and the inner loop begins again.
`Array.swap` takes both of its indices as `Nat`s, using the same tactics as array indexing behind the scenes to ensure that they are in bounds.

Nonetheless, the `Fin` used for the recursive call needs a proof that `i'` is in bounds for the result of swapping two elements.
The `simp` tactic's database contains the fact that swapping two elements of an array doesn't change its size, and the `[*]` argument instructs it to additionally use the assumption introduced by `have`.
Omitting the `have`-expression with the proof that `i' < arr.size` reveals the following goal:

```
unsolved goals
α:Type ?u.7inst✝:Ord αarr:Array αi:Fin arr.sizei':NatisLt✝:i' + 1 < arr.size⊢ i' < arr.size
```

## 8.6.2. The Outer Loop

The outer loop of insertion sort moves the pointer from left to right, invoking `insertSorted` at each iteration to insert the element at the pointer into the correct position in the array.
The basic form of the loop resembles the implementation of `Array.map`:

```lean
def insertionSortLoop [Ord α] (arr : Array α) (i : Nat) : Array α :=
  if h : i < arr.size then
    insertionSortLoop (insertSorted arr ⟨i, h⟩) (i + 1)
  else
    arr
```

An error occurs because there is no argument that decreases at every recursive call:

모든 재귀 호출에서 감소하는 인수가 없기 때문에 오류가 발생합니다:

```
fail to show termination for
  insertionSortLoop
with errors
failed to infer structural recursion:
Not considering parameter α of insertionSortLoop:
  it is unchanged in the recursive calls
Not considering parameter #2 of insertionSortLoop:
  it is unchanged in the recursive calls
Cannot use parameter arr:
  the type Array α does not have a `.brecOn` recursor
Cannot use parameter i:
  failed to eliminate recursive application
    insertionSortLoop (insertSorted arr ⟨i, h⟩) (i + 1)

Could not find a decreasing measure.
The basic measures relate at each recursive call as follows:
(<, ≤, =: relation proved, ? all proofs failed, _: no proof attempted)
            arr i #1
1) 324:4-55   ? ?  ?

#1: arr.size - i

Please use `termination_by` to specify a decreasing measure.
```

While Lean can prove that a `Nat` that increases towards a constant bound at each iteration leads to a terminating function, this function has no constant bound because the array is replaced with the result of calling `insertSorted` at each iteration.

Before constructing the termination proof, it can be convenient to test the definition with a `partial` modifier to make sure that it returns the expected answers:

Lean은 각 반복에서 상수 한계로 증가하는 `Nat`이 종료하는 함수로 이어진다는 것을 증명할 수 있지만, 이 함수는 각 반복에서 `insertSorted` 호출의 결과로 배열이 교체되기 때문에 상수 한계가 없습니다.

종료 증명을 구성하기 전에, `partial` 수정자를 사용하여 정의를 테스트하여 예상된 답을 반환하는지 확인하는 것이 편리합니다:

```lean
partial def insertionSortLoop [Ord α] (arr : Array α) (i : Nat) : Array α :=
  if h : i < arr.size then
    insertionSortLoop (insertSorted arr ⟨i, h⟩) (i + 1)
  else
    arr
```

```lean
#eval insertionSortLoop #[5, 17, 3, 8] 0
```

```
#[3, 5, 8, 17]
```

```lean
#eval insertionSortLoop #["metamorphic", "igneous", "sedimentary"] 0
```

```
#["igneous", "metamorphic", "sedimentary"]
```

### 8.6.2.1. Termination

Once again, the function terminates because the difference between the index and the size of the array being processed decreases on each recursive call.
This time, however, Lean does not accept the `termination_by`:

다시 말해, 함수는 처리되는 배열의 크기와 인덱스 간의 차이가 각 재귀 호출에서 감소하기 때문에 종료됩니다.
하지만 이번에는 Lean이 `termination_by`를 수용하지 않습니다:

```lean
def insertionSortLoop [Ord α] (arr : Array α) (i : Nat) : Array α :=
  if h : i < arr.size then
    insertionSortLoop (insertSorted arr ⟨i, h⟩) (i + 1)
  else
    arr
termination_by arr.size - i
```

```
failed to prove termination, possible solutions:
  - Use `have`-expressions to prove the remaining goals
  - Use `termination_by` to specify a different well-founded relation
  - Use `decreasing_by` to specify your own tactic for discharging this kind of goal
α:Type u_1inst✝:Ord αarr:Array αi:Nath:i < arr.size⊢ (insertSorted arr ⟨i, h⟩).size - (i + 1) < arr.size - i
```

The problem is that Lean has no way to know that `insertSorted` returns an array that's the same size as the one it is passed.
In order to prove that `insertionSortLoop` terminates, it is necessary to first prove that `insertSorted` doesn't change the size of the array.
Copying the unproved termination condition from the error message to the function and “proving” it with `sorry` allows the function to be temporarily accepted:

문제는 Lean이 `insertSorted`가 전달된 배열과 같은 크기의 배열을 반환한다는 것을 알 수 없다는 것입니다.
`insertionSortLoop`가 종료된다는 것을 증명하기 위해, 먼저 `insertSorted`가 배열의 크기를 변경하지 않는다는 것을 증명해야 합니다.
오류 메시지에서 증명되지 않은 종료 조건을 함수에 복사하고 `sorry`로 “증명”하면 함수를 임시로 수용할 수 있습니다:

```lean
def insertionSortLoop [Ord α] (arr : Array α) (i : Nat) : Array α :=
  if h : i < arr.size then
    have : (insertSorted arr ⟨i, h⟩).size - (i + 1) < arr.size - i := by
      sorry
    insertionSortLoop (insertSorted arr ⟨i, h⟩) (i + 1)
  else
    arr
termination_by arr.size - i
```

```
declaration uses 'sorry'
```

Because `insertSorted` is structurally recursive on the index of the element being inserted, the proof should be by induction on the index.
In the base case, the array is returned unchanged, so its length certainly does not change.
For the inductive step, the induction hypothesis is that a recursive call on the next smaller index will not change the length of the array.
There are two cases two consider: either the element has been fully inserted into the sorted region and the array is returned unchanged, in which case the length is also unchanged, or the element is swapped with the next one before the recursive call.
However, swapping two elements in an array doesn't change the size of it, and the induction hypothesis states that the recursive call with the next index returns an array that's the same size as its argument.
Thus, the size remains unchanged.

`insertSorted`가 삽입되는 요소의 인덱스에서 구조적으로 재귀하기 때문에, 증명은 인덱스에 대한 귀납법이어야 합니다.
기본 경우에서, 배열은 변경되지 않은 상태로 반환되므로, 그 길이는 확실히 변하지 않습니다.
귀납적 단계의 경우, 귀납 가설은 다음 더 작은 인덱스에 대한 재귀 호출이 배열의 길이를 변경하지 않는다는 것입니다.
두 가지 경우를 고려해야 합니다: 요소가 정렬된 영역에 완전히 삽입되고 배열이 변경되지 않은 상태로 반환되는 경우(이 경우 길이도 변경되지 않음) 또는 요소가 재귀 호출 전에 다음 요소와 교환되는 경우입니다.
그러나 배열의 두 요소를 교환해도 크기는 변경되지 않으며, 귀납 가설은 다음 인덱스를 사용하는 재귀 호출이 인수와 같은 크기의 배열을 반환한다고 명시합니다.
따라서 크기는 변경되지 않습니다.

Translating this English-language theorem statement to Lean and proceeding using the techniques from this chapter is enough to prove the base case and make progress in the inductive step:

이 영어 정리문을 Lean으로 변환하고 이 장의 기법을 사용하여 진행하는 것만으로도 기본 경우를 증명하고 귀납적 단계에서 진행할 수 있습니다:

```lean
theorem insert_sorted_size_eq [Ord α] (arr : Array α) (i : Fin arr.size) :
    (insertSorted arr i).size = arr.size := by
  match i with
  | ⟨j, isLt⟩ =>
    induction j with
    | zero => simp [insertSorted]
    | succ j' ih =>
      simp [insertSorted]
```

The simplification using `insertSorted` in the inductive step revealed the pattern match in `insertSorted`:

귀납적 단계에서 `insertSorted`를 사용한 단순화는 `insertSorted`의 패턴 매칭을 드러냈습니다:

```
unsolved goals
succα:Type u_1inst✝:Ord αarr:Array αi:Fin arr.sizej':Natih:∀ (isLt : j' < arr.size), (insertSorted arr ⟨j', isLt⟩).size = arr.sizeisLt:j' + 1 < arr.size⊢ (match compare arr[j'] arr[j' + 1] with
    | Ordering.lt => arr
    | Ordering.eq => arr
    | Ordering.gt => insertSorted (arr.swap j' (j' + 1) ⋯ ⋯) ⟨j', ⋯⟩).size =
  arr.size
```

When faced with a goal that includes `if` or `match`, the `split` tactic (not to be confused with the `splitList` function used in the definition of merge sort) replaces the goal with one new goal for each path of control flow:

`if` 또는 `match`를 포함하는 목표에 직면했을 때, `split` 전술(병합 정렬 정의에 사용되는 `splitList` 함수와 혼동하지 않음)은 목표를 제어 흐름의 각 경로에 대한 하나의 새로운 목표로 바꿉니다:

```lean
theorem insert_sorted_size_eq [Ord α] (arr : Array α) (i : Fin arr.size) :
    (insertSorted arr i).size = arr.size := by
  match i with
  | ⟨j, isLt⟩ =>
    induction j with
    | zero => simp [insertSorted]
    | succ j' ih =>
      simp [insertSorted]
      split
```

Because it typically doesn't matter *how* a statement was proved, but only *that* it was proved, proofs in Lean's output are typically replaced by `⋯`.
Additionally, each new goal has an assumption that indicates which branch led to that goal, named `heq✝` in this case:

일반적으로 진술이 *어떻게* 증명되었는지는 중요하지 않지만, *그것이* 증명되었다는 것만 중요하기 때문에, Lean의 출력에서 증명은 일반적으로 `⋯`로 교체됩니다.
또한, 각 새로운 목표는 그 목표로 이끈 분기를 나타내는 가정이 있으며, 이 경우 `heq✝`라고 이름이 지어집니다:

```
unsolved goals
h_1α:Type u_1inst✝:Ord αarr:Array αi:Fin arr.sizej':Natih:∀ (isLt : j' < arr.size), (insertSorted arr ⟨j', isLt⟩).size = arr.sizeisLt:j' + 1 < arr.sizex✝:Orderingheq✝:compare arr[j'] arr[j' + 1] = Ordering.lt⊢ arr.size = arr.size

h_2α:Type u_1inst✝:Ord αarr:Array αi:Fin arr.sizej':Natih:∀ (isLt : j' < arr.size), (insertSorted arr ⟨j', isLt⟩).size = arr.sizeisLt:j' + 1 < arr.sizex✝:Orderingheq✝:compare arr[j'] arr[j' + 1] = Ordering.eq⊢ arr.size = arr.size

h_3α:Type u_1inst✝:Ord αarr:Array αi:Fin arr.sizej':Natih:∀ (isLt : j' < arr.size), (insertSorted arr ⟨j', isLt⟩).size = arr.sizeisLt:j' + 1 < arr.sizex✝:Orderingheq✝:compare arr[j'] arr[j' + 1] = Ordering.gt⊢ (insertSorted (arr.swap j' (j' + 1) ⋯ ⋯) ⟨j', ⋯⟩).size = arr.size
```

Rather than write proofs for both simple cases, adding `<;> try rfl` after `split` causes the two straightforward cases to disappear immediately, leaving only a single goal:

두 단순한 경우 모두에 대한 증명을 작성하는 대신, `split` 후에 `<;> try rfl`을 추가하면 두 직선적 경우가 즉시 사라지고 하나의 목표만 남습니다:

```lean
theorem insert_sorted_size_eq [Ord α] (arr : Array α) (i : Fin arr.size) :
    (insertSorted arr i).size = arr.size := by
  match i with
  | ⟨j, isLt⟩ =>
    induction j with
    | zero => simp [insertSorted]
    | succ j' ih =>
      simp [insertSorted]
      split <;> try rfl
```

```
unsolved goals
h_3α:Type u_1inst✝:Ord αarr:Array αi:Fin arr.sizej':Natih:∀ (isLt : j' < arr.size), (insertSorted arr ⟨j', isLt⟩).size = arr.sizeisLt:j' + 1 < arr.sizex✝:Orderingheq✝:compare arr[j'] arr[j' + 1] = Ordering.gt⊢ (insertSorted (arr.swap j' (j' + 1) ⋯ ⋯) ⟨j', ⋯⟩).size = arr.size
```

Unfortunately, the induction hypothesis is not strong enough to prove this goal.
The induction hypothesis states that calling `insertSorted` on `arr` leaves the size unchanged, but the proof goal is to show that the result of the recursive call with the result of swapping leaves the size unchanged.
Successfully completing the proof requires an induction hypothesis that works for *any* array that is passed to `insertSorted` together with the smaller index as an argument

It is possible to get a strong induction hypothesis by using the `generalizing` option to the `induction` tactic.
This option brings additional assumptions from the context into the statement that's used to generate the base case, the induction hypothesis, and the goal to be shown in the inductive step.
Generalizing over `arr` leads to a stronger hypothesis:

```lean
theorem insert_sorted_size_eq [Ord α] (arr : Array α) (i : Fin arr.size) :
    (insertSorted arr i).size = arr.size := by
  match i with
  | ⟨j, isLt⟩ =>
    induction j generalizing arr with
    | zero => simp [insertSorted]
    | succ j' ih =>
      simp [insertSorted]
      split <;> try rfl
```

In the resulting goal, `arr` is now part of a “for all” statement in the inductive hypothesis:

```
unsolved goals
h_3α:Type u_1inst✝:Ord αj':Natih:∀ (arr : Array α) (i : Fin arr.size) (isLt : j' < arr.size), (insertSorted arr ⟨j', isLt⟩).size = arr.sizearr:Array αi:Fin arr.sizeisLt:j' + 1 < arr.sizex✝:Orderingheq✝:compare arr[j'] arr[j' + 1] = Ordering.gt⊢ (insertSorted (arr.swap j' (j' + 1) ⋯ ⋯) ⟨j', ⋯⟩).size = arr.size
```

However, this whole proof is beginning to get unmanageable.
The next step would be to introduce a variable standing for the length of the result of swapping, show that it is equal to `arr.size`, and then show that this variable is also equal to the length of the array that results from the recursive call.
These equality statements can then be chained together to prove the goal.
It's much easier, however, to use functional induction:

```lean
theorem insert_sorted_size_eq [Ord α]
    (arr : Array α) (i : Fin arr.size) :
    (insertSorted arr i).size = arr.size := by
  fun_induction insertSorted with
  | case1 arr isLt => skip
  | case2 arr i isLt this isLt => skip
  | case3 arr i isLt this isEq => skip
  | case4 arr i isLt this isGt ih => skip
```

The first goal is the case for index `0`.
Here, the array is not modified, so proving that its size is unmodified will not require any complicated steps:

```
unsolved goals
case1α:Type u_1inst✝:Ord αarr✝ arr:Array αisLt:0 < arr.size⊢ arr.size = arr.size
```

The next two goals are the same, and cover the `.lt` and `.eq` cases for the element comparison.
The local assumptions `isLt` and `isEq` will allow the correct branch of the `match` to be selected:

```
unsolved goals
case2α:Type u_1inst✝:Ord αarr✝ arr:Array αi:NatisLt✝:i + 1 < arr.sizethis:i < arr.sizeisLt:compare arr[i] arr[⟨i.succ, isLt✝⟩] = Ordering.lt⊢ (match compare arr[i] arr[⟨i.succ, isLt✝⟩] with
    | Ordering.lt => arr
    | Ordering.eq => arr
    | Ordering.gt => insertSorted (arr.swap i (↑⟨i.succ, isLt✝⟩) this ⋯) ⟨i, ⋯⟩).size =
  arr.size
```

```
unsolved goals
case3α:Type u_1inst✝:Ord αarr✝ arr:Array αi:NatisLt:i + 1 < arr.sizethis:i < arr.sizeisEq:compare arr[i] arr[⟨i.succ, isLt⟩] = Ordering.eq⊢ (match compare arr[i] arr[⟨i.succ, isLt⟩] with
    | Ordering.lt => arr
    | Ordering.eq => arr
    | Ordering.gt => insertSorted (arr.swap i (↑⟨i.succ, isLt⟩) this ⋯) ⟨i, ⋯⟩).size =
  arr.size
```

In the final case, once the `match` is reduced, there will be some work left to do to prove that the next step of the insertion preserves the size of the array.
In particular, the induction hypothesis states that the size of the next step is equal to the size of the result of the swap, but the desired conclusion is that it's equal to the size of the original array:

```
unsolved goals
case4α:Type u_1inst✝:Ord αarr✝ arr:Array αi:NatisLt:i + 1 < arr.sizethis:i < arr.sizeisGt:compare arr[i] arr[⟨i.succ, isLt⟩] = Ordering.gtih:(insertSorted (arr.swap i (↑⟨i.succ, isLt⟩) this ⋯) ⟨i, ⋯⟩).size = (arr.swap i (↑⟨i.succ, isLt⟩) this ⋯).size⊢ (match compare arr[i] arr[⟨i.succ, isLt⟩] with
    | Ordering.lt => arr
    | Ordering.eq => arr
    | Ordering.gt => insertSorted (arr.swap i (↑⟨i.succ, isLt⟩) this ⋯) ⟨i, ⋯⟩).size =
  arr.size
```

The Lean library includes the theorem `Array.size_swap`, which states that swapping two elements of an array doesn't change its size.
By default, `grind` doesn't use this fact, but once instructed to do so, it can take care of all four cases:

```lean
theorem insert_sorted_size_eq [Ord α]
    (arr : Array α) (i : Fin arr.size) :
    (insertSorted arr i).size = arr.size := by
  fun_induction insertSorted <;> grind [Array.size_swap]
```

## 8.6.3. The Driver Function

Insertion sort itself calls `insertionSortLoop`, initializing the index that demarcates the sorted region of the array from the unsorted region to `0`:

```lean
def insertionSort [Ord α] (arr : Array α) : Array α :=
  insertionSortLoop arr 0
```

A few quick tests show the function is at least not blatantly wrong:

```lean
#eval insertionSort #[3, 1, 7, 4]
```

```
#[1, 3, 4, 7]
```

```lean
#eval insertionSort #["quartz", "marble", "granite", "hematite"]
```

```
#["granite", "hematite", "marble", "quartz"]
```

## 8.6.4. Is This Really Insertion Sort?

Insertion sort is *defined* to be an in-place sorting algorithm.
What makes it useful, despite its quadratic worst-case run time, is that it is a stable sorting algorithm that doesn't allocate extra space and that handles almost-sorted data efficiently.
If each iteration of the inner loop allocated a new array, then the algorithm wouldn't *really* be insertion sort.

Lean's array operations, such as `Array.set` and `Array.swap`, check whether the array in question has a reference count that is greater than one.
If so, then the array is visible to multiple parts of the code, which means that it must be copied.
Otherwise, Lean would no longer be a pure functional language.
However, when the reference count is exactly one, there are no other potential observers of the value.
In these cases, the array primitives mutate the array in place.
What other parts of the program don't know can't hurt them.

Lean's proof logic works at the level of pure functional programs, not the underlying implementation.
This means that the best way to discover whether a program unnecessarily copies data is to test it.
Adding calls to `dbgTraceIfShared` at each point where mutation is desired causes the provided message to be printed to `stderr` when the value in question has more than one reference.

Insertion sort has precisely one place that is at risk of copying rather than mutating: the call to `Array.swap`.
Replacing `arr.swap i' i` with `(dbgTraceIfShared "array to swap" arr).swap i' i` causes the program to emit `shared RC array to swap` whenever it is unable to mutate the array.
However, this change to the program changes the proofs as well, because now there's a call to an additional function.
Adding a local assumption that `dbgTraceIfShared` preserves the length of its argument and adding it to some calls to `simp` is enough to fix the program and proofs.

The complete instrumented code for insertion sort is:

```lean
def insertSorted [Ord α] (arr : Array α) (i : Fin arr.size) : Array α :=
  match i with
  | ⟨0, _⟩ => arr
  | ⟨i' + 1, _⟩ =>
    have : i' < arr.size := by
      omega
    match Ord.compare arr[i'] arr[i] with
    | .lt | .eq => arr
    | .gt =>
      have : (dbgTraceIfShared "array to swap" arr).size = arr.size := by
        simp [dbgTraceIfShared]
      insertSorted
        ((dbgTraceIfShared "array to swap" arr).swap i' i)
        ⟨i', by simp [*]⟩

theorem insert_sorted_size_eq [Ord α] (len : Nat) (i : Nat) :
    (arr : Array α) → (isLt : i < arr.size) → (arr.size = len) →
    (insertSorted arr ⟨i, isLt⟩).size = len := by
  induction i with
  | zero =>
    intro arr isLt hLen
    simp [insertSorted, *]
  | succ i' ih =>
    intro arr isLt hLen
    simp [insertSorted, dbgTraceIfShared]
    split <;> simp [*]

def insertionSortLoop [Ord α] (arr : Array α) (i : Nat) : Array α :=
  if h : i < arr.size then
    have : (insertSorted arr ⟨i, h⟩).size - (i + 1) < arr.size - i := by
      rw [insert_sorted_size_eq arr.size i arr h rfl]
      omega
    insertionSortLoop (insertSorted arr ⟨i, h⟩) (i + 1)
  else
    arr
termination_by arr.size - i

def insertionSort [Ord α] (arr : Array α) : Array α :=
  insertionSortLoop arr 0
```

A bit of cleverness is required to check whether the instrumentation actually works.
First off, the Lean compiler aggressively optimizes function calls away when all their arguments are known at compile time.
Simply writing a program that applies `insertionSort` to a large array is not sufficient, because the resulting compiled code may contain only the sorted array as a constant.
The easiest way to ensure that the compiler doesn't optimize away the sorting routine is to read the array from `stdin`.
Secondly, the compiler performs dead code elimination.
Adding extra `let`s to the program won't necessarily result in more references in running code if the `let`-bound variables are never used.
To ensure that the extra reference is not eliminated entirely, it's important to ensure that the extra reference is somehow used.

The first step in testing the instrumentation is to write `getLines`, which reads an array of lines from standard input:

```lean
def getLines : IO (Array String) := do
  let stdin ← IO.getStdin
  let mut lines : Array String := #[]
  let mut currLine ← stdin.getLine
  while !currLine.isEmpty do
    -- Drop trailing newline:
    lines := lines.push (currLine.dropRight 1)
    currLine ← stdin.getLine
  pure lines
```

`IO.FS.Stream.getLine` returns a complete line of text, including the trailing newline.
It returns `""` when the end-of-file marker has been reached.

Next, two separate `main` routines are needed.
Both read the array to be sorted from standard input, ensuring that the calls to `insertionSort` won't be replaced by their return values at compile time.
Both then print to the console, ensuring that the calls to `insertionSort` won't be optimized away entirely.
One of them prints only the sorted array, while the other prints both the sorted array and the original array.
The second function should trigger a warning that `Array.swap` had to allocate a new array:

```lean
def mainUnique : IO Unit := do
  let lines ← getLines
  for line in insertionSort lines do
    IO.println line

def mainShared : IO Unit := do
  let lines ← getLines
  IO.println "--- Sorted lines: ---"
  for line in insertionSort lines do
    IO.println line
  IO.println ""
  IO.println "--- Original data: ---"
  for line in lines do
    IO.println line
```

The actual `main` simply selects one of the two main actions based on the provided command-line arguments:

```lean
def main (args : List String) : IO UInt32 := do
  match args with
  | ["--shared"] => mainShared; pure 0
  | ["--unique"] => mainUnique; pure 0
  | _ =>
    IO.println "Expected single argument, either \"--shared\" or \"--unique\""
    pure 1
```

Running it with no arguments produces the expected usage information:

```bash
$ sort
Expected single argument, either "--shared" or "--unique"
```

The file `test-data` contains the following rocks:

File: `test-data`

```
schist
feldspar
diorite
pumice
obsidian
shale
gneiss
marble
flint
```

Using the instrumented insertion sort on these rocks results them being printed in alphabetical order:

```bash
$ sort --unique < test-data
diorite
feldspar
flint
gneiss
marble
obsidian
pumice
schist
shale
```

However, the version in which a reference is retained to the original array results in a notification on `stderr` (namely, `shared RC array to swap`) from the first call to `Array.swap`:

```bash
$ sort --shared < test-data
--- Sorted lines: ---
diorite
feldspar
flint
gneiss
marble
obsidian
pumice
schist
shale

--- Original data: ---
schist
feldspar
diorite
pumice
obsidian
shale
gneiss
marble
flint
shared RC array to swap
```

The fact that only a single `shared RC` notification appears means that the array is copied only once.
This is because the copy that results from the call to `Array.swap` is itself unique, so no further copies need to be made.
In an imperative language, subtle bugs can result from forgetting to explicitly copy an array before passing it by reference.
When running `sort --shared`, the array is copied as needed to preserve the pure functional meaning of Lean programs, but no more.

## 8.6.5. Other Opportunities for Mutation

The use of mutation instead of copying when references are unique is not limited to array update operators.
Lean also attempts to “recycle” constructors whose reference counts are about to fall to zero, reusing them instead of allocating new data.
This means, for instance, that `List.map` will mutate a linked list in place, at least in cases when nobody could possibly notice.
One of the most important steps in optimizing hot loops in Lean code is making sure that the data being modified is not referred to from multiple locations.

## 8.6.6. Exercises

* Write a function that reverses arrays. Test that if the input array has a reference count of one, then your function does not allocate a new array.
* Implement either merge sort or quicksort for arrays. Prove that your implementation terminates, and test that it doesn't allocate more arrays than expected. This is a challenging exercise!
