---
title: "More Inequalities"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "More Inequalities"
---

# More Inequalities

## 8.4.1. Merge Sort

One example of a function whose termination proof is non-trivial is merge sort on `List`.

`List`에서 termination 증명이 자명하지 않은 함수의 한 예는 merge sort입니다.
Merge sort consists of two phases: first, a list is split in half.

Merge sort는 두 개의 단계로 구성됩니다: 먼저 리스트를 반으로 나눕니다.
Each half is sorted using merge sort, and then the results are merged using a function that combines two sorted lists into a larger sorted list.

각 절반은 merge sort를 사용하여 정렬되고, 결과는 두 개의 정렬된 리스트를 더 큰 정렬된 리스트로 결합하는 함수를 사용하여 병합됩니다.
The base cases are the empty list and the singleton list, both of which are already considered to be sorted.

기저 사례는 빈 목록과 singleton 리스트이며, 둘 다 이미 정렬된 것으로 간주됩니다.

To merge two sorted lists, there are two basic cases to consider:

두 개의 정렬된 리스트를 병합하려면 고려할 두 가지 기본 사례가 있습니다:

1. If one of the input lists is empty, then the result is the other list.

입력 리스트 중 하나가 비어있으면 결과는 다른 리스트입니다.
2. If both lists are non-empty, then their heads should be compared. The result of the function is the smaller of the two heads, followed by the result of merging the remaining entries of both lists.

함수의 결과는 두 헤드 중 더 작은 것이고, 그 뒤에 두 리스트의 나머지 항목을 병합한 결과가 따릅니다.

This is not structurally recursive on either list.

이는 어느 리스트에 대해서도 구조적으로 재귀적이지 않습니다.
The recursion terminates because an entry is removed from one of the two lists in each recursive call, but it could be either list.

재귀는 각 재귀 호출에서 두 리스트 중 하나에서 항목이 제거되기 때문에 종료되지만, 어느 리스트든 될 수 있습니다.
Behind the scenes, Lean uses this fact to prove that it terminates:

백그라운드에서 Lean은 이 사실을 사용하여 이것이 종료됨을 증명합니다:

`def merge [Ord α] (xs : List α) (ys : List α) : List α :=
match xs, ys with
| [], _ => ys
| _, [] => xs
| x'::xs', y'::ys' =>
match Ord.compare x' y' with
| .lt | .eq => x' :: merge xs' (y' :: ys')
| .gt => y' :: merge (x'::xs') ys'`

A simple way to split a list is to add each entry in the input list to two alternating output lists:

리스트를 나누는 간단한 방법은 입력 리스트의 각 항목을 두 개의 교대로 나타나는 출력 리스트에 추가하는 것입니다:

`def splitList (lst : List α) : (List α × List α) :=
match lst with
| [] => ([], [])
| x :: xs =>
let (a, b) := splitList xs
(x :: b, a)`

This splitting function is structurally recursive.

이 splitting 함수는 구조적으로 재귀적입니다.

Merge sort checks whether a base case has been reached.

Merge sort는 기저 사례에 도달했는지 확인합니다.
If so, it returns the input list.

그렇다면 입력 리스트를 반환합니다.
If not, it splits the input, and merges the result of sorting each half:

그렇지 않으면 입력을 나누고 각 절반의 정렬 결과를 병합합니다:

`` def fail to show termination for
mergeSort
with errors
failed to infer structural recursion:
Not considering parameter α of mergeSort:
it is unchanged in the recursive calls
Not considering parameter #2 of mergeSort:
it is unchanged in the recursive calls
Cannot use parameter xs:
failed to eliminate recursive application
mergeSort halves.fst

Could not find a decreasing measure.
The basic measures relate at each recursive call as follows:
(<, ≤, =: relation proved, ? all proofs failed, _: no proof attempted)
xs #1
1) 70:11-31 ? ?
2) 70:34-54 _ _
#1: xs.length
Please use `termination_by` to specify a decreasing measure.mergeSort [Ord α] (xs : List α) : List α :=
if unused variable `h`

Note: This linter can be disabled with `set_option linter.unusedVariables false`h : xs.length < 2 then
match xs with
| [] => []
| [x] => [x]
else
let halves := splitList xs
merge (mergeSort halves.fst) (mergeSort halves.snd) ``

Lean's pattern match compiler is able to tell that the assumption `h` introduced by the `if` that tests whether `xs.length < 2` rules out lists longer than one entry, so there is no “missing cases” error.
However, even though this program always terminates, it is not structurally recursive, and Lean is unable to automatically discover a decreasing measure:

그러나 이 프로그램이 항상 종료되더라도 구조적으로 재귀적이지 않으며, Lean은 자동으로 감소 척도(decreasing measure)를 발견할 수 없습니다:

```
fail to show termination for
  mergeSort
with errors
failed to infer structural recursion:
Not considering parameter α of mergeSort:
  it is unchanged in the recursive calls
Not considering parameter #2 of mergeSort:
  it is unchanged in the recursive calls
Cannot use parameter xs:
  failed to eliminate recursive application
    mergeSort halves.fst

Could not find a decreasing measure.
The basic measures relate at each recursive call as follows:
(<, ≤, =: relation proved, ? all proofs failed, _: no proof attempted)
            xs #1
1) 70:11-31  ?  ?
2) 70:34-54  _  _

#1: xs.length

Please use `termination_by` to specify a decreasing measure.

`termination_by`를 사용하여 감소 척도를 지정해주세요.
```

The reason it terminates is that `splitList` always returns lists that are shorter than its input, at least when applied to lists that contain at least two elements.
Thus, the length of `halves.fst` and `halves.snd` are less than the length of `xs`.
This can be expressed using a `termination_by` clause:

`` def mergeSort [Ord α] (xs : List α) : List α :=
if unused variable `h`

Note: This linter can be disabled with `set_option linter.unusedVariables false`h : xs.length < 2 then
match xs with
| [] => []
| [x] => [x]
else
let halves := splitList xs
merge (failed to prove termination, possible solutions:
 - Use `have`-expressions to prove the remaining goals
 - Use `termination_by` to specify a different well-founded relation
 - Use `decreasing_by` to specify your own tactic for discharging this kind of goal
α:Type u_1xs:List αh:¬xs.length < 2halves:List α × List α := splitList xs⊢ (splitList xs).fst.length < xs.lengthmergeSort halves.fst) (mergeSort halves.snd)
termination_by xs.length ``

With this clause, the error message changes.
Instead of complaining that the function isn't structurally recursive, Lean instead points out that it was unable to automatically prove that `(splitList xs).fst.length < xs.length`:

```
failed to prove termination, possible solutions:
  - Use `have`-expressions to prove the remaining goals
  - Use `termination_by` to specify a different well-founded relation
  - Use `decreasing_by` to specify your own tactic for discharging this kind of goal
α:Type u_1xs:List αh:¬xs.length < 2halves:List α × List α := splitList xs⊢ (splitList xs).fst.length < xs.length
```

## 8.4.2. Splitting a List Makes it Shorter

It will also be necessary to prove that `(splitList xs).snd.length < xs.length`.
Because `splitList` alternates between adding entries to the two lists, it is easiest to prove both statements at once, so the structure of the proof can follow the algorithm used to implement `splitList`.
In other words, it is easiest to prove that `∀(lst : List α), (splitList lst).fst.length < lst.length ∧ (splitList lst).snd.length < lst.length`.

Unfortunately, the statement is false.
In particular, `splitList []` is `([], [])`. Both output lists have length `0`, which is not less than `0`, the length of the input list.
Similarly, `splitList ["basalt"]` evaluates to `(["basalt"], [])`, and `["basalt"]` is not shorter than `["basalt"]`.
However, `splitList ["basalt", "granite"]` evaluates to `(["basalt"], ["granite"])`, and both of these output lists are shorter than the input list.

It turns out that the lengths of the output lists are always less than or equal to the length of the input list, but they are only strictly shorter when the input list contains at least two entries.
It turns out to be easiest to prove the former statement, then extend it to the latter statement.
Begin with a theorem statement:

`theorem splitList_shorter_le (lst : List α) :
(splitList lst).fst.length ≤ lst.length ∧
(splitList lst).snd.length ≤ lst.length := unsolved goals
α:Type u_1lst:List α⊢ (splitList lst).fst.length ≤ lst.length ∧ (splitList lst).snd.length ≤ lst.lengthbyα:Type u_1lst:List α⊢ (splitList lst).fst.length ≤ lst.length ∧ (splitList lst).snd.length ≤ lst.length
skipα:Type u_1lst:List α⊢ (splitList lst).fst.length ≤ lst.length ∧ (splitList lst).snd.length ≤ lst.length`

```
unsolved goals
α:Type u_1lst:List α⊢ (splitList lst).fst.length ≤ lst.length ∧ (splitList lst).snd.length ≤ lst.length
```

Because `splitList` is structurally recursive on the list, the proof should use induction.
The structural recursion in `splitList` fits a proof by induction perfectly: the base case of the induction matches the base case of the recursion, and the inductive step matches the recursive call.
The `induction` tactic gives two goals:

`theorem splitList_shorter_le (lst : List α) :
(splitList lst).fst.length ≤ lst.length ∧
(splitList lst).snd.length ≤ lst.length := byα:Type u_1lst:List α⊢ (splitList lst).fst.length ≤ lst.length ∧ (splitList lst).snd.length ≤ lst.length
induction lst with
| nil unsolved goals
nilα:Type u_1⊢ (splitList []).fst.length ≤ [].length ∧ (splitList []).snd.length ≤ [].length=> skipnilα:Type u_1⊢ (splitList []).fst.length ≤ [].length ∧ (splitList []).snd.length ≤ [].length
| cons x xs ih unsolved goals
consα:Type u_1x:αxs:List αih:(splitList xs).fst.length ≤ xs.length ∧ (splitList xs).snd.length ≤ xs.length⊢ (splitList (x :: xs)).fst.length ≤ (x :: xs).length ∧ (splitList (x :: xs)).snd.length ≤ (x :: xs).length=> skipconsα:Type u_1x:αxs:List αih:(splitList xs).fst.length ≤ xs.length ∧ (splitList xs).snd.length ≤ xs.length⊢ (splitList (x :: xs)).fst.length ≤ (x :: xs).length ∧ (splitList (x :: xs)).snd.length ≤ (x :: xs).length`

```
unsolved goals
nilα:Type u_1⊢ (splitList []).fst.length ≤ [].length ∧ (splitList []).snd.length ≤ [].length
```

```
unsolved goals
consα:Type u_1x:αxs:List αih:(splitList xs).fst.length ≤ xs.length ∧ (splitList xs).snd.length ≤ xs.length⊢ (splitList (x :: xs)).fst.length ≤ (x :: xs).length ∧ (splitList (x :: xs)).snd.length ≤ (x :: xs).length
```

The goal for the `nil` case can be proved by invoking the simplifier and instructing it to unfold the definition of `splitList`, because the length of the empty list is less than or equal to the length of the empty list.
Similarly, simplifying with `splitList` in the `cons` case places `Nat.succ` around the lengths in the goal:

`theorem splitList_shorter_le (lst : List α) :
(splitList lst).fst.length ≤ lst.length ∧
(splitList lst).snd.length ≤ lst.length := byα:Type u_1lst:List α⊢ (splitList lst).fst.length ≤ lst.length ∧ (splitList lst).snd.length ≤ lst.length
induction lst with
| nil =>nilα:Type u_1⊢ (splitList []).fst.length ≤ [].length ∧ (splitList []).snd.length ≤ [].length simp [splitList]All goals completed! 🐙
| cons x xs ih unsolved goals
consα:Type u_1x:αxs:List αih:(splitList xs).fst.length ≤ xs.length ∧ (splitList xs).snd.length ≤ xs.length⊢ (splitList xs).snd.length ≤ xs.length ∧ (splitList xs).fst.length ≤ xs.length + 1=>
simp [splitList]consα:Type u_1x:αxs:List αih:(splitList xs).fst.length ≤ xs.length ∧ (splitList xs).snd.length ≤ xs.length⊢ (splitList xs).snd.length ≤ xs.length ∧ (splitList xs).fst.length ≤ xs.length + 1consα:Type u_1x:αxs:List αih:(splitList xs).fst.length ≤ xs.length ∧ (splitList xs).snd.length ≤ xs.length⊢ (splitList (x :: xs)).fst.length ≤ (x :: xs).length ∧ (splitList (x :: xs)).snd.length ≤ (x :: xs).length`

```
unsolved goals
consα:Type u_1x:αxs:List αih:(splitList xs).fst.length ≤ xs.length ∧ (splitList xs).snd.length ≤ xs.length⊢ (splitList xs).snd.length ≤ xs.length ∧ (splitList xs).fst.length ≤ xs.length + 1
```

This is because the call to `List.length` consumes the head of the list `x :: xs`, converting it to a `Nat.succ`, in both the length of the input list and the length of the first output list.

Writing `A ∧ B` in Lean is short for `And A B`.
`And` is a structure type in the `Prop` universe:

`structure And (a b : Prop) : Prop where
intro ::
left : a
right : b`

In other words, a proof of `A ∧ B` consists of the `And.intro` constructor applied to a proof of `A` in the `left` field and a proof of `B` in the `right` field.

The `cases` tactic allows a proof to consider each constructor of a datatype or each potential proof of a proposition in turn.
It corresponds to a `match` expression without recursion.
Using `cases` on a structure results in the structure being broken apart, with an assumption added for each field of the structure, just as a pattern match expression extracts the field of a structure for use in a program.
Because structures have only one constructor, using `cases` on a structure does not result in additional goals.

Because `ih` is a proof of `List.length (splitList xs).fst ≤ List.length xs ∧ List.length (splitList xs).snd ≤ List.length xs`, using `cases ih` results in an assumption that `List.length (splitList xs).fst ≤ List.length xs` and an assumption that `List.length (splitList xs).snd ≤ List.length xs`:

`theorem splitList_shorter_le (lst : List α) :
(splitList lst).fst.length ≤ lst.length ∧
(splitList lst).snd.length ≤ lst.length := byα:Type u_1lst:List α⊢ (splitList lst).fst.length ≤ lst.length ∧ (splitList lst).snd.length ≤ lst.length
induction lst with
| nil =>nilα:Type u_1⊢ (splitList []).fst.length ≤ [].length ∧ (splitList []).snd.length ≤ [].length simp [splitList]All goals completed! 🐙
| cons x xs ih unsolved goals
cons.introα:Type u_1x:αxs:List αleft✝:(splitList xs).fst.length ≤ xs.lengthright✝:(splitList xs).snd.length ≤ xs.length⊢ (splitList xs).snd.length ≤ xs.length ∧ (splitList xs).fst.length ≤ xs.length + 1=>
simp [splitList]consα:Type u_1x:αxs:List αih:(splitList xs).fst.length ≤ xs.length ∧ (splitList xs).snd.length ≤ xs.length⊢ (splitList xs).snd.length ≤ xs.length ∧ (splitList xs).fst.length ≤ xs.length + 1
cases ihcons.introα:Type u_1x:αxs:List αleft✝:(splitList xs).fst.length ≤ xs.lengthright✝:(splitList xs).snd.length ≤ xs.length⊢ (splitList xs).snd.length ≤ xs.length ∧ (splitList xs).fst.length ≤ xs.length + 1consα:Type u_1x:αxs:List αih:(splitList xs).fst.length ≤ xs.length ∧ (splitList xs).snd.length ≤ xs.length⊢ (splitList (x :: xs)).fst.length ≤ (x :: xs).length ∧ (splitList (x :: xs)).snd.length ≤ (x :: xs).length`

```
unsolved goals
cons.introα:Type u_1x:αxs:List αleft✝:(splitList xs).fst.length ≤ xs.lengthright✝:(splitList xs).snd.length ≤ xs.length⊢ (splitList xs).snd.length ≤ xs.length ∧ (splitList xs).fst.length ≤ xs.length + 1
```

Because the goal of the proof is also an `And`, the `constructor` tactic can be used to apply `And.intro`, resulting in a goal for each argument:

`theorem splitList_shorter_le (lst : List α) :
(splitList lst).fst.length ≤ lst.length ∧
(splitList lst).snd.length ≤ lst.length := byα:Type u_1lst:List α⊢ (splitList lst).fst.length ≤ lst.length ∧ (splitList lst).snd.length ≤ lst.length
induction lst with
| nil =>nilα:Type u_1⊢ (splitList []).fst.length ≤ [].length ∧ (splitList []).snd.length ≤ [].length simp [splitList]All goals completed! 🐙
| cons x xs ih unsolved goals
cons.intro.leftα:Type u_1x:αxs:List αleft✝:(splitList xs).fst.length ≤ xs.lengthright✝:(splitList xs).snd.length ≤ xs.length⊢ (splitList xs).snd.length ≤ xs.length

cons.intro.rightα:Type u_1x:αxs:List αleft✝:(splitList xs).fst.length ≤ xs.lengthright✝:(splitList xs).snd.length ≤ xs.length⊢ (splitList xs).fst.length ≤ xs.length + 1=>
simp [splitList]consα:Type u_1x:αxs:List αih:(splitList xs).fst.length ≤ xs.length ∧ (splitList xs).snd.length ≤ xs.length⊢ (splitList xs).snd.length ≤ xs.length ∧ (splitList xs).fst.length ≤ xs.length + 1
cases ihcons.introα:Type u_1x:αxs:List αleft✝:(splitList xs).fst.length ≤ xs.lengthright✝:(splitList xs).snd.length ≤ xs.length⊢ (splitList xs).snd.length ≤ xs.length ∧ (splitList xs).fst.length ≤ xs.length + 1
constructorcons.intro.leftα:Type u_1x:αxs:List αleft✝:(splitList xs).fst.length ≤ xs.lengthright✝:(splitList xs).snd.length ≤ xs.length⊢ (splitList xs).snd.length ≤ xs.lengthcons.intro.rightα:Type u_1x:αxs:List αleft✝:(splitList xs).fst.length ≤ xs.lengthright✝:(splitList xs).snd.length ≤ xs.length⊢ (splitList xs).fst.length ≤ xs.length + 1consα:Type u_1x:αxs:List αih:(splitList xs).fst.length ≤ xs.length ∧ (splitList xs).snd.length ≤ xs.length⊢ (splitList (x :: xs)).fst.length ≤ (x :: xs).length ∧ (splitList (x :: xs)).snd.length ≤ (x :: xs).length`

```
unsolved goals
cons.intro.leftα:Type u_1x:αxs:List αleft✝:(splitList xs).fst.length ≤ xs.lengthright✝:(splitList xs).snd.length ≤ xs.length⊢ (splitList xs).snd.length ≤ xs.length

cons.intro.rightα:Type u_1x:αxs:List αleft✝:(splitList xs).fst.length ≤ xs.lengthright✝:(splitList xs).snd.length ≤ xs.length⊢ (splitList xs).fst.length ≤ xs.length + 1
```

The `left` goal is identical to the `left✝` assumption, so the `assumption` tactic dispatches it:

`theorem splitList_shorter_le (lst : List α) :
(splitList lst).fst.length ≤ lst.length ∧
(splitList lst).snd.length ≤ lst.length := byα:Type u_1lst:List α⊢ (splitList lst).fst.length ≤ lst.length ∧ (splitList lst).snd.length ≤ lst.length
induction lst with
| nil =>nilα:Type u_1⊢ (splitList []).fst.length ≤ [].length ∧ (splitList []).snd.length ≤ [].length simp [splitList]All goals completed! 🐙
| cons x xs ih unsolved goals
cons.intro.rightα:Type u_1x:αxs:List αleft✝:(splitList xs).fst.length ≤ xs.lengthright✝:(splitList xs).snd.length ≤ xs.length⊢ (splitList xs).fst.length ≤ xs.length + 1=>
simp [splitList]consα:Type u_1x:αxs:List αih:(splitList xs).fst.length ≤ xs.length ∧ (splitList xs).snd.length ≤ xs.length⊢ (splitList xs).snd.length ≤ xs.length ∧ (splitList xs).fst.length ≤ xs.length + 1
cases ihcons.introα:Type u_1x:αxs:List αleft✝:(splitList xs).fst.length ≤ xs.lengthright✝:(splitList xs).snd.length ≤ xs.length⊢ (splitList xs).snd.length ≤ xs.length ∧ (splitList xs).fst.length ≤ xs.length + 1
constructorcons.intro.leftα:Type u_1x:αxs:List αleft✝:(splitList xs).fst.length ≤ xs.lengthright✝:(splitList xs).snd.length ≤ xs.length⊢ (splitList xs).snd.length ≤ xs.lengthcons.intro.rightα:Type u_1x:αxs:List αleft✝:(splitList xs).fst.length ≤ xs.lengthright✝:(splitList xs).snd.length ≤ xs.length⊢ (splitList xs).fst.length ≤ xs.length + 1
case left =>α:Type u_1x:αxs:List αleft✝:(splitList xs).fst.length ≤ xs.lengthright✝:(splitList xs).snd.length ≤ xs.length⊢ (splitList xs).snd.length ≤ xs.length assumptionAll goals completed! 🐙consα:Type u_1x:αxs:List αih:(splitList xs).fst.length ≤ xs.length ∧ (splitList xs).snd.length ≤ xs.length⊢ (splitList (x :: xs)).fst.length ≤ (x :: xs).length ∧ (splitList (x :: xs)).snd.length ≤ (x :: xs).length`

```
unsolved goals
cons.intro.rightα:Type u_1x:αxs:List αleft✝:(splitList xs).fst.length ≤ xs.lengthright✝:(splitList xs).snd.length ≤ xs.length⊢ (splitList xs).fst.length ≤ xs.length + 1
```

The `right` goal resembles the `right✝` assumption, except the goal adds a `+ 1` only to the length of the input list.
It's time to prove that the inequality holds.

### 8.4.2.1. Adding One to the Greater Side

The inequality needed to prove `splitList_shorter_le` is `∀(n m : Nat), n ≤ m → n ≤ m + 1`.
The incoming assumption that `n ≤ m` essentially tracks the difference between `n` and `m` in the number of `Nat.le.step` constructors.
Thus, the proof should add an extra `Nat.le.step` in the base case.

Starting out, the statement reads:

`theorem Nat.le_succ_of_le : n ≤ m → n ≤ m + 1 := unsolved goals
n m:Nat⊢ n ≤ m → n ≤ m + 1byn:Natm:Nat⊢ n ≤ m → n ≤ m + 1
skipn:Natm:Nat⊢ n ≤ m → n ≤ m + 1`

```
unsolved goals
n m:Nat⊢ n ≤ m → n ≤ m + 1
```

The first step is to introduce a name for the assumption that `n ≤ m`:

`theorem Nat.le_succ_of_le : n ≤ m → n ≤ m + 1 := unsolved goals
n m:Nath:n ≤ m⊢ n ≤ m + 1byn:Natm:Nat⊢ n ≤ m → n ≤ m + 1
intro hn:Natm:Nath:n ≤ m⊢ n ≤ m + 1`

```
unsolved goals
n m:Nath:n ≤ m⊢ n ≤ m + 1
```

The proof is by induction on this assumption:

`theorem Nat.le_succ_of_le : n ≤ m → n ≤ m + 1 := byn:Natm:Nat⊢ n ≤ m → n ≤ m + 1
intro hn:Natm:Nath:n ≤ m⊢ n ≤ m + 1
induction h with
| refl unsolved goals
refln m:Nat⊢ n ≤ n + 1=> skiprefln:Natm:Nat⊢ n ≤ n + 1
| step _ ih unsolved goals
stepn m m✝:Nata✝:n.le m✝ih:n ≤ m✝ + 1⊢ n ≤ m✝.succ + 1=> skipstepn:Natm:Natm✝:Nata✝:n.le m✝ih:n ≤ m✝ + 1⊢ n ≤ m✝.succ + 1`

In the case for `refl`, where `n = m`, the goal is to prove that `n ≤ n + 1`:

```
unsolved goals
refln m:Nat⊢ n ≤ n + 1
```

In the case for `step`, the goal is to prove that `n ≤ m + 1` under the assumption that `n ≤ m`:

```
unsolved goals
stepn m m✝:Nata✝:n.le m✝ih:n ≤ m✝ + 1⊢ n ≤ m✝.succ + 1
```

For the `refl` case, the `step` constructor can be applied:

`theorem Nat.le_succ_of_le : n ≤ m → n ≤ m + 1 := byn:Natm:Nat⊢ n ≤ m → n ≤ m + 1
intro hn:Natm:Nath:n ≤ m⊢ n ≤ m + 1
induction h with
| refl unsolved goals
refl.an m:Nat⊢ n.le n=> constructorrefl.an:Natm:Nat⊢ n.le nrefln:Natm:Nat⊢ n ≤ n + 1
| step _ ih unsolved goals
stepn m m✝:Nata✝:n.le m✝ih:n ≤ m✝ + 1⊢ n ≤ m✝.succ + 1=> skipstepn:Natm:Natm✝:Nata✝:n.le m✝ih:n ≤ m✝ + 1⊢ n ≤ m✝.succ + 1`

```
unsolved goals
refl.an m:Nat⊢ n.le n
```

After `step`, `refl` can be used, which leaves only the goal for `step`:

`theorem Nat.le_succ_of_le : n ≤ m → n ≤ m + 1 := byn:Natm:Nat⊢ n ≤ m → n ≤ m + 1
intro hn:Natm:Nath:n ≤ m⊢ n ≤ m + 1
induction h with
| refl =>refln:Natm:Nat⊢ n ≤ n + 1 constructorrefl.an:Natm:Nat⊢ n.le n; constructorAll goals completed! 🐙
| step _ ih unsolved goals
stepn m m✝:Nata✝:n.le m✝ih:n ≤ m✝ + 1⊢ n ≤ m✝.succ + 1=> skipstepn:Natm:Natm✝:Nata✝:n.le m✝ih:n ≤ m✝ + 1⊢ n ≤ m✝.succ + 1`

For the step, applying the `step` constructor transforms the goal into the induction hypothesis:

`theorem Nat.le_succ_of_le : n ≤ m → n ≤ m + 1 := byn:Natm:Nat⊢ n ≤ m → n ≤ m + 1
intro hn:Natm:Nath:n ≤ m⊢ n ≤ m + 1
induction h with
| refl =>refln:Natm:Nat⊢ n ≤ n + 1 constructorrefl.an:Natm:Nat⊢ n.le n; constructorAll goals completed! 🐙
| step _ ih unsolved goals
step.an m m✝:Nata✝:n.le m✝ih:n ≤ m✝ + 1⊢ n.le (m✝ + 1)=> constructorstep.an:Natm:Natm✝:Nata✝:n.le m✝ih:n ≤ m✝ + 1⊢ n.le (m✝ + 1)stepn:Natm:Natm✝:Nata✝:n.le m✝ih:n ≤ m✝ + 1⊢ n ≤ m✝.succ + 1`

```
unsolved goals
step.an m m✝:Nata✝:n.le m✝ih:n ≤ m✝ + 1⊢ n.le (m✝ + 1)
```

The final proof is as follows:

`theorem  : n ≤ m → n ≤ m + 1 := byn:Natm:Nat⊢ n ≤ m → n ≤ m + 1
intro hn:Natm:Nath:n ≤ m⊢ n ≤ m + 1
induction h with
| refl =>refln:Natm:Nat⊢ n ≤ n + 1 constructorrefl.an:Natm:Nat⊢ n.le n; constructorAll goals completed! 🐙
| step =>stepn:Natm:Natm✝:Nata✝:n.le m✝a_ih✝:n ≤ m✝ + 1⊢ n ≤ m✝.succ + 1 constructorstep.an:Natm:Natm✝:Nata✝:n.le m✝a_ih✝:n ≤ m✝ + 1⊢ n.le (m✝ + 1); assumptionAll goals completed! 🐙`

To reveal what's going on behind the scenes, the `apply` and `exact` tactics can be used to indicate exactly which constructor is being applied.
The `apply` tactic solves the current goal by applying a function or constructor whose return type matches, creating new goals for each argument that was not provided, while `exact` fails if any new goals would be needed:

`theorem  : n ≤ m → n ≤ m + 1 := byn:Natm:Nat⊢ n ≤ m → n ≤ m + 1
intro hn:Natm:Nath:n ≤ m⊢ n ≤ m + 1
induction h with
| refl =>refln:Natm:Nat⊢ n ≤ n + 1 apply Nat.le.steprefl.an:Natm:Nat⊢ n.le n; exact Nat.le.reflAll goals completed! 🐙
| step _ ih =>stepn:Natm:Natm✝:Nata✝:n.le m✝ih:n ≤ m✝ + 1⊢ n ≤ m✝.succ + 1 apply Nat.le.stepstep.an:Natm:Natm✝:Nata✝:n.le m✝ih:n ≤ m✝ + 1⊢ n.le (m✝ + 1); exact ihAll goals completed! 🐙`

The proof can be golfed:

`theorem  (h : n ≤ m) : n ≤ m + 1:= byn:Natm:Nath:n ≤ m⊢ n ≤ m + 1
induction hrefln:Natm:Nat⊢ n ≤ n + 1stepn:Natm:Natm✝:Nata✝:n.le m✝a_ih✝:n ≤ m✝ + 1⊢ n ≤ m✝.succ + 1 <;>refln:Natm:Nat⊢ n ≤ n + 1stepn:Natm:Natm✝:Nata✝:n.le m✝a_ih✝:n ≤ m✝ + 1⊢ n ≤ m✝.succ + 1 repeat (first | constructorstep.a.an:Natm:Natm✝:Nata✝:n.le m✝a_ih✝:n ≤ m✝ + 1⊢ n.le m✝ | assumptionAll goals completed! 🐙)`

In this short tactic script, both goals introduced by `induction` are addressed using `repeat (first | constructor | assumption)`.
The tactic `first | T1 | T2 | ... | Tn` means to use try `T1` through `Tn` in order, using the first tactic that succeeds.
In other words, `repeat (first | constructor | assumption)` applies constructors as long as it can, and then attempts to solve the goal using an assumption.

The proof can be shortened even further by using `grind`, which includes a solver for linear arithmetic:

`theorem  (h : n ≤ m) : n ≤ m + 1:= byn:Natm:Nath:n ≤ m⊢ n ≤ m + 1
grindAll goals completed! 🐙`

Finally, the proof can be written as a recursive function:

`theorem  : n ≤ m → n ≤ m + 1
| .refl => .step .refl
| .step h => .step (Nat.le_succ_of_le h)`

Each style of proof can be appropriate to different circumstances.
The detailed proof script is useful in cases where beginners may be reading the code, or where the steps of the proof provide some kind of insight.
The short, highly-automated proof script is typically easier to maintain, because automation is frequently both flexible and robust in the face of small changes to definitions and datatypes.
The recursive function is typically both harder to understand from the perspective of mathematical proofs and harder to maintain, but it can be a useful bridge for programmers who are beginning to work with interactive theorem proving.

### 8.4.2.3. A Simpler Proof

Instead of using ordinary induction, `splitList_shorter_le` can be proved using functional induction, resulting in one case for each branch of `splitList`:

`theorem splitList_shorter_le (lst : List α) :
(splitList lst).fst.length ≤ lst.length ∧
(splitList lst).snd.length ≤ lst.length := byα:Type u_1lst:List α⊢ (splitList lst).fst.length ≤ lst.length ∧ (splitList lst).snd.length ≤ lst.length
fun_induction splitList with
| case1 unsolved goals
case1α:Type u_1⊢ ([], []).fst.length ≤ [].length ∧ ([], []).snd.length ≤ [].length=> skipcase1α:Type u_1⊢ ([], []).fst.length ≤ [].length ∧ ([], []).snd.length ≤ [].length
| case2 x xs a b splitEq ih unsolved goals
case2α:Type u_1x:αxs a b:List αsplitEq:splitList xs = (a, b)ih:(splitList xs).fst.length ≤ xs.length ∧ (splitList xs).snd.length ≤ xs.length⊢ (x :: b, a).fst.length ≤ (x :: xs).length ∧ (x :: b, a).snd.length ≤ (x :: xs).length=> skipcase2α:Type u_1x:αxs:List αa:List αb:List αsplitEq:splitList xs = (a, b)ih:(splitList xs).fst.length ≤ xs.length ∧ (splitList xs).snd.length ≤ xs.length⊢ (x :: b, a).fst.length ≤ (x :: xs).length ∧ (x :: b, a).snd.length ≤ (x :: xs).length`

The first case matches the base case of `splitList`.
*Both* applications of `splitList` have been replaced by the result of this first branch:

```
unsolved goals
case1α:Type u_1⊢ ([], []).fst.length ≤ [].length ∧ ([], []).snd.length ≤ [].length
```

The second case matches the recursive branch of `splitList`.
In addition to the induction hypothesis, the value of the `let` in `splitList` is tracked in an assumption:

```
unsolved goals
case2α:Type u_1x:αxs a b:List αsplitEq:splitList xs = (a, b)ih:(splitList xs).fst.length ≤ xs.length ∧ (splitList xs).snd.length ≤ xs.length⊢ (x :: b, a).fst.length ≤ (x :: xs).length ∧ (x :: b, a).snd.length ≤ (x :: xs).length
```

While the second case looks a bit complicated, everything needed to complete the proof is present.
Indeed, `grind` can prove both goals immediately:

`theorem splitList_shorter_le (lst : List α) :
(splitList lst).fst.length ≤ lst.length ∧
(splitList lst).snd.length ≤ lst.length := byα:Type u_1lst:List α⊢ (splitList lst).fst.length ≤ lst.length ∧ (splitList lst).snd.length ≤ lst.length
fun_induction splitListcase1α:Type u_1⊢ ([], []).fst.length ≤ [].length ∧ ([], []).snd.length ≤ [].lengthcase2α:Type u_1x✝¹:αxs✝:List αa✝:List αb✝:List αx✝:splitList xs✝ = (a✝, b✝)ih1✝:(splitList xs✝).fst.length ≤ xs✝.length ∧ (splitList xs✝).snd.length ≤ xs✝.length⊢ (x✝¹ :: b✝, a✝).fst.length ≤ (x✝¹ :: xs✝).length ∧ (x✝¹ :: b✝, a✝).snd.length ≤ (x✝¹ :: xs✝).length <;>case1α:Type u_1⊢ ([], []).fst.length ≤ [].length ∧ ([], []).snd.length ≤ [].lengthcase2α:Type u_1x✝¹:αxs✝:List αa✝:List αb✝:List αx✝:splitList xs✝ = (a✝, b✝)ih1✝:(splitList xs✝).fst.length ≤ xs✝.length ∧ (splitList xs✝).snd.length ≤ xs✝.length⊢ (x✝¹ :: b✝, a✝).fst.length ≤ (x✝¹ :: xs✝).length ∧ (x✝¹ :: b✝, a✝).snd.length ≤ (x✝¹ :: xs✝).length grindAll goals completed! 🐙`

## 8.4.3. Merge Sort Terminates

Merge sort has two recursive calls, one for each sub-list returned by `splitList`.
Each recursive call will require a proof that the length of the list being passed to it is shorter than the length of the input list.
It's usually convenient to write a termination proof in two steps: first, write down the propositions that will allow Lean to verify termination, and then prove them.
Otherwise, it's possible to put a lot of effort into proving the propositions, only to find out that they aren't quite what's needed to establish that the recursive calls are on smaller inputs.

The `sorry` tactic can prove any goal, even false ones.
It isn't intended for use in production code or final proofs, but it is a convenient way to “sketch out” a proof or program ahead of time.
Any definitions or theorems that use `sorry` are annotated with a warning.

The initial sketch of `mergeSort`'s termination argument that uses `sorry` can be written by copying the goals that Lean couldn't prove into `have`-expressions.
In Lean, `have` is similar to `let`.
When using `have`, the name is optional.
Typically, `let` is used to define names that refer to interesting values, while `have` is used to locally prove propositions that can be found when Lean is searching for evidence that an array lookup is in-bounds or that a function terminates.

`declaration uses 'sorry'def declaration uses 'sorry'declaration uses 'sorry'declaration uses 'sorry'declaration uses 'sorry'declaration uses 'sorry'declaration uses 'sorry'declaration uses 'sorry'mergeSort [Ord α] (xs : List α) : List α :=
if h : xs.length < 2 then
match xs with
| [] => []
| [x] => [x]
else
let halves := splitList xs
have : halves.fst.length < xs.length := byα:Type ?u.157191inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := splitList xs⊢ halves.fst.length < xs.length
sorryAll goals completed! 🐙
have : halves.snd.length < xs.length := byα:Type ?u.157191inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := splitList xsthis:halves.fst.length < xs.length := sorry⊢ halves.snd.length < xs.length
sorryAll goals completed! 🐙
merge (mergeSort halves.fst) (mergeSort halves.snd)
termination_by xs.length`

The warning is located on the name `mergeSort`:

```
declaration uses 'sorry'
```

Because there are no errors, the proposed propositions are enough to establish termination.

The proofs begin by applying the helper theorems:

`def mergeSort [Ord α] (xs : List α) : List α :=
if h : xs.length < 2 then
match xs with
| [] => []
| [x] => [x]
else
let halves := splitList xs
have : halves.fst.length < xs.length := unsolved goals
hα:Type ?u.189060inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := ⋯⊢ xs.length ≥ 2byα:Type ?u.189060inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := splitList xs⊢ halves.fst.length < xs.length
apply splitList_shorter_fsthα:Type ?u.189060inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := splitList xs⊢ xs.length ≥ 2
have : halves.snd.length < xs.length := unsolved goals
hα:Type ?u.189060inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := ⋯this:halves.fst.length < xs.length⊢ xs.length ≥ 2byα:Type ?u.189060inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := splitList xsthis:halves.fst.length < xs.length := splitList_shorter_fst xs sorry⊢ halves.snd.length < xs.length
apply splitList_shorter_sndhα:Type ?u.189060inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := splitList xsthis:halves.fst.length < xs.length := splitList_shorter_fst xs sorry⊢ xs.length ≥ 2
merge (mergeSort halves.fst) (mergeSort halves.snd)
termination_by xs.length`

Both proofs fail, because `splitList_shorter_fst` and `splitList_shorter_snd` both require a proof that `xs.length ≥ 2`:

```
unsolved goals
hα:Type ?u.189060inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := ⋯⊢ xs.length ≥ 2
```

To check that this will be enough to complete the proof, add it using `sorry` and check for errors:

`declaration uses 'sorry'def declaration uses 'sorry'declaration uses 'sorry'declaration uses 'sorry'declaration uses 'sorry'mergeSort [Ord α] (xs : List α) : List α :=
if h : xs.length < 2 then
match xs with
| [] => []
| [x] => [x]
else
let halves := splitList xs
have : xs.length ≥ 2 := byα:Type ?u.220858inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := splitList xs⊢ xs.length ≥ 2 sorryAll goals completed! 🐙
have : halves.fst.length < xs.length := byα:Type ?u.220858inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := splitList xsthis:xs.length ≥ 2 := sorry⊢ halves.fst.length < xs.length
apply splitList_shorter_fsthα:Type ?u.220858inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := splitList xsthis:xs.length ≥ 2 := sorry⊢ xs.length ≥ 2
assumptionAll goals completed! 🐙
have : halves.snd.length < xs.length := byα:Type ?u.220858inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := splitList xsthis✝:xs.length ≥ 2 := sorrythis:halves.fst.length < xs.length := splitList_shorter_fst xs this✝⊢ halves.snd.length < xs.length
apply splitList_shorter_sndhα:Type ?u.220858inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := splitList xsthis✝:xs.length ≥ 2 := sorrythis:halves.fst.length < xs.length := splitList_shorter_fst xs this✝⊢ xs.length ≥ 2
assumptionAll goals completed! 🐙
merge (mergeSort halves.fst) (mergeSort halves.snd)
termination_by xs.length`

Once again, there is only a warning.

There is one promising assumption available: `h : ¬List.length xs < 2`, which comes from the `if`.
Clearly, if it is not the case that `xs.length < 2`, then `xs.length ≥ 2`.
The `grind` tactic solves this goal, and the program is now complete:

`def mergeSort [Ord α] (xs : List α) : List α :=
if h : xs.length < 2 then
match xs with
| [] => []
| [x] => [x]
else
let halves := splitList xs
have : xs.length ≥ 2 := byα:Type ?u.254832inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := splitList xs⊢ xs.length ≥ 2
grindAll goals completed! 🐙
have : halves.fst.length < xs.length := byα:Type ?u.254832inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := splitList xsthis:xs.length ≥ 2 := mergeSort._proof_1 xs h⊢ halves.fst.length < xs.length
apply splitList_shorter_fsthα:Type ?u.254832inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := splitList xsthis:xs.length ≥ 2 := mergeSort._proof_1 xs h⊢ xs.length ≥ 2
assumptionAll goals completed! 🐙
have : halves.snd.length < xs.length := byα:Type ?u.254832inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := splitList xsthis✝:xs.length ≥ 2 := mergeSort._proof_1 xs hthis:halves.fst.length < xs.length := splitList_shorter_fst xs this✝⊢ halves.snd.length < xs.length
apply splitList_shorter_sndhα:Type ?u.254832inst✝:Ord αxs:List αh:¬xs.length < 2halves:List α × List α := splitList xsthis✝:xs.length ≥ 2 := mergeSort._proof_1 xs hthis:halves.fst.length < xs.length := splitList_shorter_fst xs this✝⊢ xs.length ≥ 2
assumptionAll goals completed! 🐙
merge (mergeSort halves.fst) (mergeSort halves.snd)
termination_by xs.length`

The function can be tested on examples:

`["geode", "limestone", "mica", "soapstone"]#eval mergeSort ["soapstone", "geode", "mica", "limestone"]`

```
["geode", "limestone", "mica", "soapstone"]
```

`[3, 5, 15, 22]#eval mergeSort [5, 3, 22, 15]`

```
[3, 5, 15, 22]
```
