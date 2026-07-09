---
title: "Additional Conveniences"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Additional Conveniences"
---

# Additional Conveniences

## 4.6.2. Leading Dot Notation

The constructors of an inductive type are in a namespace.
This allows multiple related inductive types to use the same constructor names, but it can lead to programs becoming verbose.
In contexts where the inductive type in question is known, the namespace can be omitted by preceding the constructor's name with a dot, and Lean uses the expected type to resolve the constructor names.
For example, a function that mirrors a binary tree can be written:

귀납타입의 생성자들은 네임스페이스 안에 있습니다. 이것은 여러 관련된 귀납타입들이 같은 생성자 이름을 사용할 수 있도록 하지만, 프로그램이 장황해질 수 있습니다. 문제의 귀납타입이 알려진 맥락에서는 생성자의 이름 앞에 점을 붙여 네임스페이스를 생략할 수 있으며, Lean은 예상되는 타입을 사용하여 생성자 이름을 해결합니다. 예를 들어, 이진 트리를 미러링하는 함수를 작성할 수 있습니다:

`def BinTree.mirror : BinTree α → BinTree α
| BinTree.leaf => BinTree.leaf
| BinTree.branch l x r => BinTree.branch (mirror r) x (mirror l)`

Omitting the namespaces makes it significantly shorter, at the cost of making the program harder to read in contexts like code review tools that don't include the Lean compiler:

네임스페이스를 생략하면 코드가 훨씬 짧아지지만, Lean 컴파일러를 포함하지 않는 코드 검토 도구 같은 맥락에서는 프로그램을 읽기 더 어렵게 만듭니다:

`def BinTree.mirror : BinTree α → BinTree α
| .leaf => .leaf
| .branch l x r => .branch (mirror r) x (mirror l)`

Using the expected type of an expression to disambiguate a namespace is also applicable to names other than constructors.
If `BinTree.empty` is defined as an alternative way of creating `BinTree`s, then it can also be used with dot notation:

표현의 예상 타입을 사용하여 네임스페이스를 명확히 하는 것은 생성자 이외의 이름에도 적용 가능합니다. `BinTree.empty`가 `BinTree`s를 만드는 대체 방법으로 정의되면, 점 표기법으로도 사용할 수 있습니다:

`def BinTree.empty : BinTree α := .leaf``BinTree.empty : BinTree Nat#check (.empty : BinTree Nat)`

```
BinTree.empty : BinTree Nat
```

## 4.6.3. Or-Patterns

In contexts that allow multiple patterns, such as `match`-expressions, multiple patterns may share their result expressions.
The datatype `Weekday` that represents days of the week:

`match` 표현식과 같은 여러 패턴을 허용하는 맥락에서 여러 패턴이 결과 표현식을 공유할 수 있습니다. 요일을 나타내는 `Weekday` 데이터타입:

`inductive Weekday where
| monday
| tuesday
| wednesday
| thursday
| friday
| saturday
| sunday
deriving Repr`

Pattern matching can be used to check whether a day is a weekend:

패턴 매칭을 사용하여 어느 날이 주말인지 확인할 수 있습니다:

`def Weekday.isWeekend (day : Weekday) : Bool :=
match day with
| Weekday.saturday => true
| Weekday.sunday => true
| _ => false`

This can already be simplified by using constructor dot notation:

이미 생성자 점 표기법을 사용하여 단순화할 수 있습니다:

`def Weekday.isWeekend (day : Weekday) : Bool :=
match day with
| .saturday => true
| .sunday => true
| _ => false`

Because both weekend patterns have the same result expression (`true`), they can be condensed into one:

두 주말 패턴이 같은 결과 표현식(`true`)을 가지므로 하나로 축약할 수 있습니다:

`def Weekday.isWeekend (day : Weekday) : Bool :=
match day with
| .saturday | .sunday => true
| _ => false`

This can be further simplified into a version in which the argument is not named:

인자가 명명되지 않은 버전으로 더 단순화할 수 있습니다:

`def Weekday.isWeekend : Weekday → Bool
| .saturday | .sunday => true
| _ => false`

Behind the scenes, the result expression is simply duplicated across each pattern.
This means that patterns can bind variables, as in this example that removes the `inl` and `inr` constructors from a sum type in which both contain the same type of value:

숨은 곳에서 결과 표현식은 단순히 각 패턴에 걸쳐 복제됩니다. 이것은 패턴이 변수를 바인딩할 수 있음을 의미하며, 다음 예제에서 두 값이 모두 같은 타입을 포함하는 합타입에서 `inl`과 `inr` 생성자를 제거합니다:

`def condense : α ⊕ α → α
| .inl x | .inr x => x`

Because the result expression is duplicated, the variables bound by the patterns are not required to have the same types.
Overloaded functions that work for multiple types may be used to write a single result expression that works for patterns that bind variables of different types:

결과 표현식이 복제되기 때문에 패턴에 의해 바인딩된 변수들이 같은 타입을 가질 필요가 없습니다. 여러 타입에 대해 작동하는 오버로드된 함수들을 사용하여 다양한 타입의 변수를 바인딩하는 패턴에 대해 작동하는 단일 결과 표현식을 작성할 수 있습니다:

`def stringy : Nat ⊕ Weekday → String
| .inl x | .inr x => s!"It is {repr x}"`

In practice, only variables shared in all patterns can be referred to in the result expression, because the result must make sense for each pattern.
In `getTheNat`, only `n` can be accessed, and attempts to use either `x` or `y` lead to errors.

실제로 결과가 각 패턴에 대해 의미가 있어야 하므로 모든 패턴에서 공유된 변수만 결과 표현식에서 참조될 수 있습니다. `getTheNat`에서는 `n`만 접근할 수 있으며, `x` 또는 `y`를 사용하려는 시도는 오류를 초래합니다.

`def getTheNat : (Nat × α) ⊕ (Nat × β) → Nat
| .inl (n, x) | .inr (n, y) => n`

Attempting to access `x` in a similar definition causes an error because there is no `x` available in the second pattern:

유사한 정의에서 `x`에 접근하려는 시도는 두 번째 패턴에서 사용 가능한 `x`가 없기 때문에 오류를 일으킵니다:

`` def getTheAlpha : (Nat × α) ⊕ (Nat × α) → α
| .inl (n, x) | .inr (n, y) => Unknown identifier `x`x ``

```
Unknown identifier `x`
```

The fact that the result expression is essentially copy-pasted to each branch of the pattern match can lead to some surprising behavior.
For example, the following definitions are acceptable because the `inr` version of the result expression refers to the global definition of `str`:

결과 표현식이 본질적으로 패턴 매치의 각 분기에 복사-붙여넣기되는 사실은 놀라운 동작을 초래할 수 있습니다. 예를 들어, 다음 정의들은 결과 표현식의 `inr` 버전이 `str`의 전역 정의를 참조하기 때문에 수용 가능합니다:

`def str := "Some string"
def getTheString : (Nat × String) ⊕ (Nat × β) → String
| .inl (n, str) | .inr (n, y) => str`

Calling this function on both constructors reveals the confusing behavior.
In the first case, a type annotation is needed to tell Lean which type `β` should be:

두 생성자에서 이 함수를 호출하면 혼란스러운 동작이 나타납니다. 첫 번째 경우, Lean에 어떤 타입 `β`를 사용할지 알려주기 위해 타입 주석이 필요합니다:

`"twenty"#eval getTheString (.inl (20, "twenty") : (Nat × String) ⊕ (Nat × String))`

```
"twenty"
```

In the second case, the global definition is used:

두 번째 경우, 전역 정의가 사용됩니다:

`"Some string"#eval getTheString (.inr (20, "twenty"))`

```
"Some string"
```

Using or-patterns can vastly simplify some definitions and increase their clarity, as in `Weekday.isWeekend`.
Because there is a potential for confusing behavior, it's a good idea to be careful when using them, especially when variables of multiple types or disjoint sets of variables are involved.

또는-패턴을 사용하면 `Weekday.isWeekend`처럼 일부 정의를 크게 단순화하고 명확성을 높일 수 있습니다. 혼란스러운 동작의 가능성이 있기 때문에, 특히 여러 타입의 변수들이나 분리된 변수 집합이 관련되어 있을 때는 신중하게 사용하는 것이 좋습니다.
