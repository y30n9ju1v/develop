---
title: "의존 타입 프로그래밍의 함정 (Pitfalls of Programming with Dependent Types)"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "의존 타입 프로그래밍의 함정 (Pitfalls of Programming with Dependent Types)"
---

# 7.5. Pitfalls of Programming with Dependent Types

The flexibility of dependent types allows more useful programs to be accepted by a type checker, because the language of types is expressive enough to describe variations that less-expressive type systems cannot.
At the same time, the ability of dependent types to express very fine-grained specifications allows more buggy programs to be rejected by a type checker.
This power comes at a cost.

의존 타입의 유연성은 타입 체커가 더 유용한 프로그램을 수용할 수 있게 해줍니다. 왜냐하면 타입의 언어가 덜 표현력있는 타입 시스템이 표현할 수 없는 변형들을 설명할 수 있을 정도로 충분히 표현력있기 때문입니다. 동시에, 의존 타입이 매우 세밀한 사양을 표현할 수 있는 능력은 타입 체커가 더 많은 버그가 있는 프로그램을 거절할 수 있게 해줍니다. 이러한 힘에는 대가가 따릅니다.

The close coupling between the internals of type-returning functions such as `Row` and the types that they produce is an instance of a bigger difficulty: the distinction between the interface and the implementation of functions begins to break down when functions are used in types.
Normally, all refactorings are valid as long as they don't change the type signature or input-output behavior of a function.
Functions can be rewritten to use more efficient algorithms and data structures, bugs can be fixed, and code clarity can be improved without breaking client code.
When the function is used in a type, however, the internals of the function's implementation become part of the type, and thus part of the *interface* to another program.

`Row` 같은 타입 반환 함수의 내부와 그것이 생산하는 타입 간의 밀접한 결합은 더 큰 어려움의 한 예입니다: 함수가 타입에 사용될 때 함수의 인터페이스와 구현 간의 구분이 무너지기 시작합니다. 보통 리팩토링은 함수의 타입 서명이나 입출력 동작을 변경하지 않는 한 모두 유효합니다. 함수는 더 효율적인 알고리즘과 자료 구조를 사용하도록 재작성될 수 있고, 버그를 수정할 수 있으며, 클라이언트 코드를 깨뜨리지 않으면서 코드 명확성을 개선할 수 있습니다. 하지만 함수가 타입에 사용될 때, 함수 구현의 내부가 타입의 일부가 되고, 따라서 다른 프로그램으로의 *인터페이스*의 일부가 됩니다.

As an example, take the following two implementations of addition on `Nat`.
`Nat.plusL` is recursive on its first argument:

예를 들어, `Nat`에 대한 다음 두 덧셈 구현을 생각해봅시다. `Nat.plusL`은 첫 번째 인자에 대해 재귀적입니다:

```lean
def Nat.plusL : Nat → Nat → Nat
  | 0, k => k
  | n + 1, k => plusL n k + 1
```

`Nat.plusR`, on the other hand, is recursive on its second argument:

반면 `Nat.plusR`은 두 번째 인자에 대해 재귀적입니다:

```lean
def Nat.plusR : Nat → Nat → Nat
  | n, 0 => n
  | n, k + 1 => plusR n k + 1
```

Both implementations of addition are faithful to the underlying mathematical concept, and they thus return the same result when given the same arguments.

덧셈의 두 구현 모두 기초적인 수학적 개념에 충실하며, 따라서 같은 인자가 주어질 때 같은 결과를 반환합니다.

However, these two implementations present quite different interfaces when they are used in types.

하지만 이 두 구현은 타입에 사용될 때 상당히 다른 인터페이스를 제시합니다.
As an example, take a function that appends two `Vect`s.
This function should return a `Vect` whose length is the sum of the length of the arguments.
Because `Vect` is essentially a `List` with a more informative type, it makes sense to write the function just as one would for `List.append`, with pattern matching and recursion on the first argument.
Starting with a type signature and initial pattern match pointing at placeholders yields two messages:

예를 들어, 두 개의 `Vect`을 연결하는 함수를 생각해봅시다. 이 함수는 길이가 인자들의 길이의 합인 `Vect`을 반환해야 합니다. `Vect`는 기본적으로 더 유익한 타입을 가진 `List`이므로, `List.append`처럼 함수를 작성하는 것이 합리적입니다. 즉, 첫 번째 인자에 대한 패턴 매칭과 재귀를 사용합니다. 타입 서명과 초기 패턴 매치를 플레이스홀더를 가리키도록 시작하면 두 개의 메시지가 나옵니다:

```lean
def appendL : Vect α n → Vect α k → Vect α (n.plusL k)
  | .nil, ys => _
  | .cons x xs, ys => _
```

The first message, in the `nil` case, states that the placeholder should be replaced by a `Vect` with length `plusL 0 k`:

`nil` 경우의 첫 번째 메시지는 플레이스홀더를 길이가 `plusL 0 k`인 `Vect`으로 바꿔야 한다고 말합니다:

```
don't know how to synthesize placeholder
context:
α:Type u_1n k:Natys:Vect α k⊢ Vect α (Nat.plusL 0 k)
```

The second message, in the `cons` case, states that the placeholder should be replaced by a `Vect` with length `plusL (n✝ + 1) k`:

`cons` 경우의 두 번째 메시지는 플레이스홀더를 길이가 `plusL (n✝ + 1) k`인 `Vect`으로 바꿔야 한다고 말합니다:

```
don't know how to synthesize placeholder
context:
α:Type u_1n k n✝:Natx:αxs:Vect α n✝ys:Vect α k⊢ Vect α ((n✝ + 1).plusL k)
```

The symbol after `n`, called a *dagger*, is used to indicate names that Lean has internally invented.
Behind the scenes, pattern matching on the first `Vect` implicitly caused the value of the first `Nat` to be refined as well, because the index on the constructor `cons` is `n + 1`, with the tail of the `Vect` having length `n`.
Here, `n✝` represents the `Nat` that is one less than the argument `n`.

`n` 뒤의 기호는 *dagger*라 불리며, Lean이 내부적으로 생성한 이름들을 나타내는 데 사용됩니다. 뒤에서 일어나는 일은, 첫 번째 `Vect`에 대한 패턴 매칭이 첫 번째 `Nat`의 값도 암묵적으로 정제시킨다는 것입니다. 왜냐하면 `cons` 생성자의 인덱스가 `n + 1`이고, `Vect`의 꼬리 부분의 길이가 `n`이기 때문입니다. 여기서 `n✝`는 인자 `n`보다 하나 작은 `Nat`을 나타냅니다.

## 7.5.1. Definitional Equality

In the definition of `plusL`, there is a pattern case `0, k => k`.
This applies in the length used in the first placeholder, so another way to write the underscore's type `Vect α (Nat.plusL 0 k)` is `Vect α k`.
Similarly, `plusL` contains a pattern case `n + 1, k => plusL n k + 1`.
This means that the type of the second underscore can be equivalently written `Vect α (plusL n✝ k + 1)`.

`plusL`의 정의에서 패턴 경우 `0, k => k`가 있습니다. 이것은 첫 번째 플레이스홀더에서 사용된 길이에 적용되므로, 언더스코어의 타입 `Vect α (Nat.plusL 0 k)`를 쓰는 또 다른 방법은 `Vect α k`입니다. 마찬가지로, `plusL`은 패턴 경우 `n + 1, k => plusL n k + 1`을 포함합니다. 이는 두 번째 언더스코어의 타입을 동등하게 `Vect α (plusL n✝ k + 1)`으로 쓸 수 있다는 의미입니다.

To expose what is going on behind the scenes, the first step is to write the `Nat` arguments explicitly, which also results in daggerless error messages because the names are now written explicitly in the program:

뒤에서 일어나는 일을 드러내기 위해 첫 번째 단계는 `Nat` 인자들을 명시적으로 작성하는 것입니다. 이렇게 하면 이름들이 이제 프로그램에서 명시적으로 작성되기 때문에 dagger 없는 에러 메시지도 생깁니다:

```lean
def appendL : (n k : Nat) → Vect α n → Vect α k → Vect α (n.plusL k)
  | 0, k, .nil, ys => _
  | n + 1, k, .cons x xs, ys => _
```

```
don't know how to synthesize placeholder
context:
α:Type u_1k:Natys:Vect α k⊢ Vect α (Nat.plusL 0 k)
```

```
don't know how to synthesize placeholder
context:
α:Type u_1n k:Natx:αxs:Vect α nys:Vect α k⊢ Vect α ((n + 1).plusL k)
```

Annotating the underscores with the simplified versions of the types does not introduce a type error, which means that the types as written in the program are equivalent to the ones that Lean found on its own:

언더스코어에 단순화된 버전의 타입으로 주석을 달면 타입 에러가 발생하지 않습니다. 이는 프로그램에서 작성된 타입들이 Lean이 자체적으로 찾은 타입들과 동등하다는 의미입니다:

```lean
def appendL : (n k : Nat) → Vect α n → Vect α k → Vect α (n.plusL k)
  | 0, k, .nil, ys => (_ : Vect α k)
  | n + 1, k, .cons x xs, ys => (_ : Vect α (n.plusL k + 1))
```

```
don't know how to synthesize placeholder
context:
α:Type u_1k:Natys:Vect α k⊢ Vect α k
```

```
don't know how to synthesize placeholder
context:
α:Type u_1n k:Natx:αxs:Vect α nys:Vect α k⊢ Vect α (n.plusL k + 1)
```

The first case demands a `Vect α k`, and `ys` has that type.
This is parallel to the way that appending the empty list to any other list returns that other list.
Refining the definition with `ys` instead of the first underscore yields a program with only one remaining underscore to be filled out:

첫 번째 경우는 `Vect α k`를 요구하며, `ys`가 그 타입을 가집니다. 이는 빈 리스트를 다른 리스트에 추가하면 그 다른 리스트를 반환하는 방식과 유사합니다. 첫 번째 언더스코어 대신 `ys`로 정의를 정제하면 채워야 할 언더스코어가 하나만 남는 프로그램이 나옵니다:

```lean
def appendL : (n k : Nat) → Vect α n → Vect α k → Vect α (n.plusL k)
  | 0, k, .nil, ys => ys
  | n + 1, k, .cons x xs, ys => (_ : Vect α (n.plusL k + 1))
```

Something very important has happened here.
In a context where Lean expected a `Vect α (Nat.plusL 0 k)`, it received a `Vect α k`.
However, `Nat.plusL` is not an `abbrev`, so it may seem like it shouldn't be running during type checking.
Something else is happening.

매우 중요한 일이 여기서 일어났습니다. Lean이 `Vect α (Nat.plusL 0 k)`를 기대하는 문맥에서 `Vect α k`를 받았습니다. 하지만 `Nat.plusL`은 `abbrev`가 아니므로, 타입 체킹 중에 실행되지 않아야 할 것 같습니다. 다른 일이 일어나고 있습니다.

The key to understanding what's going on is that Lean doesn't just expand `abbrev`s while type checking.
It can also perform computation while checking whether two types are equivalent to one another, such that any expression of one type can be used in a context that expects the other type.
This property is called *definitional equality*, and it is subtle.

무슨 일이 일어나는지 이해하는 열쇠는 Lean이 타입 체킹 중에 단지 `abbrev`들을 확장하는 것이 아니라는 것입니다. 또한 두 타입이 서로 동등한지 확인하는 동안 계산을 수행할 수 있으므로, 한 타입의 표현이 다른 타입을 기대하는 문맥에서 사용될 수 있습니다. 이 성질을 *정의적 동등성(definitional equality)*이라고 부르며, 이는 미묘합니다.

Certainly, two types that are written identically are considered to be definitionally equal—`Nat` and `Nat` or `List String` and `List String` should be considered equal.
Any two concrete types built from different datatypes are not equal, so `List Nat` is not equal to `Int`.
Additionally, types that differ only by renaming internal names are equal, so `(n : Nat) → Vect String n` is the same as `(k : Nat) → Vect String k`.
Because types can contain ordinary data, definitional equality must also describe when data are equal.
Uses of the same constructors are equal, so `0` equals `0` and `[5, 3, 1]` equals `[5, 3, 1]`.

확실히, 동일하게 작성된 두 타입은 정의적으로 동등한 것으로 간주됩니다. 즉, `Nat`과 `Nat` 또는 `List String`과 `List String`은 동등한 것으로 간주되어야 합니다. 다른 데이터타입으로부터 구축된 두 구체적 타입은 동등하지 않으므로, `List Nat`은 `Int`와 동등하지 않습니다. 게다가, 내부 이름의 이름 바꾸기만으로 다른 타입들은 동등하므로, `(n : Nat) → Vect String n`은 `(k : Nat) → Vect String k`와 같습니다. 타입들이 일반적인 데이터를 포함할 수 있기 때문에, 정의적 동등성은 또한 데이터가 언제 동등한지를 설명해야 합니다. 같은 생성자의 사용들은 동등하므로, `0`은 `0`과 같고 `[5, 3, 1]`은 `[5, 3, 1]`과 같습니다.

Types contain more than just function arrows, datatypes, and constructors, however.
They also contain *variables* and *functions*.
Definitional equality of variables is relatively simple: each variable is equal only to itself, so `(n k : Nat) → Vect Int n` is not definitionally equal to `(n k : Nat) → Vect Int k`.
Functions, on the other hand, are more complicated.
While mathematics considers two functions to be equal if they have identical input-output behavior, there is no efficient algorithm to check that, and the whole point of definitional equality is for Lean to check whether two types are interchangeable.
Instead, Lean considers functions to be definitionally equal either when they are both `fun`-expressions with definitionally equal bodies.
In other words, two functions must use *the same algorithm* that calls *the same helpers* to be considered definitionally equal.
This is not typically very helpful, so definitional equality of functions is mostly used when the exact same defined function occurs in two types.

하지만 타입들은 함수 화살표, 데이터타입, 생성자보다 더 많은 것을 포함합니다. 또한 *변수들*과 *함수들*도 포함합니다. 변수들의 정의적 동등성은 상대적으로 간단합니다. 각 변수는 자기 자신하고만 동등하므로, `(n k : Nat) → Vect Int n`은 `(n k : Nat) → Vect Int k`와 정의적으로 동등하지 않습니다. 반면 함수들은 더 복잡합니다. 수학에서는 동일한 입출력 동작을 가지면 두 함수를 동등한 것으로 간주하지만, 이를 확인하는 효율적인 알고리즘이 없으며, 정의적 동등성의 전체 요점은 Lean이 두 타입이 상호 교환 가능한지 확인하는 것입니다. 대신, Lean은 함수들이 정의적으로 동등한 본체를 가진 `fun` 표현식일 때 함수들을 정의적으로 동등한 것으로 간주합니다. 즉, 두 함수가 정의적으로 동등한 것으로 간주되려면 *동일한 알고리즘*을 사용하고 *동일한 도우미*들을 호출해야 합니다. 이는 전형적으로 매우 도움이 되지 않으므로, 함수들의 정의적 동등성은 대부분 정확히 같은 정의된 함수가 두 타입에서 나타날 때 사용됩니다.

When functions are *called* in a type, checking definitional equality may involve reducing the function call.
The type `Vect String (1 + 4)` is definitionally equal to the type `Vect String (3 + 2)` because `1 + 4` is definitionally equal to `3 + 2`.
To check their equality, both are reduced to `5`, and then the constructor rule can be used five times.
Definitional equality of functions applied to data can be checked first by seeing if they're already the same—there's no need to reduce `["a", "b"] ++ ["c"]` to check that it's equal to `["a", "b"] ++ ["c"]`, after all.
If not, the function is called and replaced with its value, and the value can then be checked.

타입에서 함수가 *호출될* 때, 정의적 동등성을 확인하는 것은 함수 호출을 축약하는 것을 포함할 수 있습니다. 타입 `Vect String (1 + 4)`은 타입 `Vect String (3 + 2)`과 정의적으로 동등합니다. 왜냐하면 `1 + 4`가 `3 + 2`와 정의적으로 동등하기 때문입니다. 그들의 동등성을 확인하기 위해, 둘 다 `5`로 축약되고, 그 다음 생성자 규칙을 다섯 번 사용할 수 있습니다. 데이터에 적용된 함수들의 정의적 동등성은 먼저 이미 같은지 확인하여 확인할 수 있습니다. 결국 `["a", "b"] ++ ["c"]`를 `["a", "b"] ++ ["c"]`와 동등한지 확인하기 위해 축약할 필요는 없습니다. 만약 아니라면, 함수가 호출되어 그 값으로 대체되고, 그 값은 그 다음에 확인될 수 있습니다.

Not all function arguments are concrete data.
For example, types may contain `Nat`s that are not built from the `zero` and `succ` constructors.
In the type `(n : Nat) → Vect String n`, the variable `n` is a `Nat`, but it is impossible to know *which* `Nat` it is before the function is called.
Indeed, the function may be called first with `0`, and then later with `17`, and then again with `33`.
As seen in the definition of `appendL`, variables with type `Nat` may also be passed to functions such as `plusL`.
Indeed, the type `(n : Nat) → Vect String n` is definitionally equal to the type `(n : Nat) → Vect String (Nat.plusL 0 n)`.

모든 함수 인자가 구체적 데이터는 아닙니다. 예를 들어, 타입들은 `zero`와 `succ` 생성자로부터 구축되지 않은 `Nat`들을 포함할 수 있습니다. 타입 `(n : Nat) → Vect String n`에서, 변수 `n`은 `Nat`이지만, 함수가 호출되기 전에 *어느* `Nat`인지 알 수 없습니다. 실제로, 함수는 먼저 `0`으로 호출되고, 나중에 `17`로 호출되고, 다시 `33`으로 호출될 수 있습니다. `appendL`의 정의에서 본 것처럼, `Nat` 타입의 변수들도 `plusL`과 같은 함수에 전달될 수 있습니다. 실제로, 타입 `(n : Nat) → Vect String n`은 타입 `(n : Nat) → Vect String (Nat.plusL 0 n)`과 정의적으로 동등합니다.

The reason that `n` and `Nat.plusL 0 n` are definitionally equal is that `plusL`'s pattern match examines its *first* argument.
This is problematic: `(n : Nat) → Vect String n` is *not* definitionally equal to `(n : Nat) → Vect String (Nat.plusL n 0)`, even though zero should be both a left and a right identity of addition.
This happens because pattern matching gets stuck when it encounters variables.
Until the actual value of `n` becomes known, there is no way to know which case of `Nat.plusL n 0` should be selected.

`n`과 `Nat.plusL 0 n`이 정의적으로 동등한 이유는 `plusL`의 패턴 매칭이 그 *첫 번째* 인자를 검토하기 때문입니다. 이것은 문제가 됩니다: `(n : Nat) → Vect String n`은 `(n : Nat) → Vect String (Nat.plusL n 0)`과 정의적으로 동등하지 *않습니다*. 0이 덧셈의 왼쪽과 오른쪽 항등원소여야 함에도 불구하고 말입니다. 이는 패턴 매칭이 변수를 만날 때 멈추기 때문에 일어납니다. `n`의 실제 값이 알려질 때까지, `Nat.plusL n 0`의 어느 경우를 선택해야 할지 알 수 있는 방법이 없습니다.

The same issue appears with the `Row` function in the query example.
The type `Row (c :: cs)` does not reduce to any datatype because the definition of `Row` has separate cases for singleton lists and lists with at least two entries.
In other words, it gets stuck when trying to match the variable `cs` against concrete `List` constructors.
This is why almost every function that takes apart or constructs a `Row` needs to match the same three cases as `Row` itself: getting it unstuck reveals concrete types that can be used for either pattern matching or constructors.

같은 문제가 쿼리 예제의 `Row` 함수에 나타납니다. 타입 `Row (c :: cs)`는 어떤 데이터타입으로도 축약되지 않습니다. 왜냐하면 `Row`의 정의는 싱글톤 리스트와 최소 두 개 항목이 있는 리스트에 대한 별도의 경우들을 가지기 때문입니다. 즉, 변수 `cs`를 구체적 `List` 생성자들과 매칭하려고 할 때 멈춥니다. 이것이 왜 거의 모든 `Row`를 분해하거나 구성하는 함수가 `Row` 자체와 같은 세 가지 경우들을 매칭해야 하는 이유입니다: 그것을 해제하면 패턴 매칭이나 생성자 중 하나에 사용할 수 있는 구체적 타입들이 드러납니다.

The missing case in `appendL` requires a `Vect α (Nat.plusL n k + 1)`.
The `+ 1` in the index suggests that the next step is to use `Vect.cons`:

`appendL`의 누락된 경우는 `Vect α (Nat.plusL n k + 1)`을 요구합니다. 인덱스의 `+ 1`은 다음 단계가 `Vect.cons`를 사용하는 것임을 시사합니다:

```lean
def appendL : (n k : Nat) → Vect α n → Vect α k → Vect α (n.plusL k)
  | 0, k, .nil, ys => ys
  | n + 1, k, .cons x xs, ys => .cons x (_ : Vect α (n.plusL k))
```

```
don't know how to synthesize placeholder
context:
α:Type u_1n k:Natx:αxs:Vect α nys:Vect α k⊢ Vect α (n.plusL k)
```

A recursive call to `appendL` can construct a `Vect` with the desired length:

`appendL`에 대한 재귀 호출은 원하는 길이를 가진 `Vect`을 구성할 수 있습니다:

```lean
def appendL : (n k : Nat) → Vect α n → Vect α k → Vect α (n.plusL k)
  | 0, k, .nil, ys => ys
  | n + 1, k, .cons x xs, ys => .cons x (appendL n k xs ys)
```

Now that the program is finished, removing the explicit matching on `n` and `k` makes it easier to read and easier to call the function:

프로그램이 완료되었으므로, `n`과 `k`에 대한 명시적 매칭을 제거하면 읽기 쉽고 함수를 호출하기 쉬워집니다:

```lean
def appendL : Vect α n → Vect α k → Vect α (n.plusL k)
  | .nil, ys => ys
  | .cons x xs, ys => .cons x (appendL xs ys)
```

Comparing types using definitional equality means that everything involved in definitional equality, including the internals of function definitions, becomes part of the *interface* of programs that use dependent types and indexed families.
Exposing the internals of a function in a type means that refactoring the exposed program may cause programs that use it to no longer type check.
In particular, the fact that `plusL` is used in the type of `appendL` means that the definition of `plusL` cannot be replaced by the otherwise-equivalent `plusR`.

정의적 동등성을 사용하여 타입들을 비교하는 것은 함수 정의의 내부를 포함하여 정의적 동등성에 관련된 모든 것이 의존 타입과 인덱스된 패밀리를 사용하는 프로그램의 *인터페이스*의 일부가 된다는 의미입니다. 함수의 내부를 타입에서 드러내는 것은 노출된 프로그램을 리팩토링하면 그것을 사용하는 프로그램이 더 이상 타입 체크되지 않을 수 있다는 의미입니다. 특히, `plusL`이 `appendL`의 타입에 사용된다는 사실은 `plusL`의 정의가 다른 경우 동등한 `plusR`으로 대체될 수 없다는 의미입니다.

## 7.5.2. Getting Stuck on Addition

What happens if append is defined with `plusR` instead?
Beginning in the same way, with explicit lengths and placeholder underscores in each case, reveals the following useful error messages:

만약 append가 대신 `plusR`로 정의된다면 어떤 일이 일어날까요? 같은 방식으로 시작하여, 각 경우에 명시적 길이와 플레이스홀더 언더스코어를 사용하면 다음의 유용한 에러 메시지들이 드러납니다:

```lean
def appendR : (n k : Nat) → Vect α n → Vect α k → Vect α (n.plusR k)
  | 0, k, .nil, ys => _
  | n + 1, k, .cons x xs, ys => _
```

```
don't know how to synthesize placeholder
context:
α:Type u_1k:Natys:Vect α k⊢ Vect α (Nat.plusR 0 k)
```

```
don't know how to synthesize placeholder
context:
α:Type u_1n k:Natx:αxs:Vect α nys:Vect α k⊢ Vect α ((n + 1).plusR k)
```

However, attempting to place a `Vect α k` type annotation around the first placeholder results in an type mismatch error:

그러나 첫 번째 플레이스홀더 주위에 `Vect α k` 타입 주석을 배치하려고 시도하면 타입 불일치 에러가 발생합니다:

```lean
def appendR : (n k : Nat) → Vect α n → Vect α k → Vect α (n.plusR k)
  | 0, k, .nil, ys => (_ : Vect α k)
  | n + 1, k, .cons x xs, ys => _
```

```
Type mismatch
  ?m.11
has type
  Vect α k
but is expected to have type
  Vect α (Nat.plusR 0 k)
```

This error is pointing out that `Nat.plusR 0 k` and `k` are *not* definitionally equal.

이 에러는 `Nat.plusR 0 k`와 `k`가 정의적으로 동등하지 *않다*는 것을 지적하고 있습니다.

This is because `plusR` has the following definition:

이것은 `plusR`이 다음 정의를 가지기 때문입니다:

```lean
def Nat.plusR : Nat → Nat → Nat
  | n, 0 => n
  | n, k + 1 => plusR n k + 1
```

Its pattern matching occurs on the *second* argument, not the first argument, which means that the presence of the variable `k` in that position prevents it from reducing.
`Nat.add` in Lean's standard library is equivalent to `plusR`, not `plusL`, so attempting to use it in this definition results in precisely the same difficulties:

그것의 패턴 매칭은 첫 번째 인자가 아닌 *두 번째* 인자에 대해 발생합니다. 즉, 그 위치에 변수 `k`가 있으면 축약되는 것을 막습니다. Lean의 표준 라이브러리의 `Nat.add`는 `plusL`이 아닌 `plusR`과 동등하므로, 이 정의에서 사용하려고 시도하면 정확히 동일한 어려움이 발생합니다:

```lean
def appendR : (n k : Nat) → Vect α n → Vect α k → Vect α (n + k)
  | 0, k, .nil, ys => (_ : Vect α k)
  | n + 1, k, .cons x xs, ys => _
```

```
Type mismatch
  ?m.15
has type
  Vect α k
but is expected to have type
  Vect α (0 + k)
```

Addition is getting *stuck* on the variables.
Getting it unstuck requires [propositional equality](../ch03/).

덧셈이 변수들에 대해 *멈추고* 있습니다. 그것을 해제하려면 [명제적 동등성(propositional equality)](../ch03/)이 필요합니다.

## 7.5.3. Propositional Equality

Propositional equality is the mathematical statement that two expressions are equal.
While definitional equality is a kind of ambient fact that Lean automatically checks when required, statements of propositional equality require explicit proofs.
Once an equality proposition has been proved, it can be used in a program to modify a type, replacing one side of the equality with the other, which can unstick the type checker.

명제적 동등성은 두 표현식이 동등하다는 수학적 진술입니다. 정의적 동등성이 필요할 때 Lean이 자동으로 확인하는 일종의 환경적 사실인 반면, 명제적 동등성의 진술들은 명시적 증명이 필요합니다. 동등성 명제가 증명되면, 그것을 프로그램에서 사용하여 타입을 수정하고, 동등성의 한쪽을 다른 쪽으로 바꿀 수 있습니다. 이는 타입 체커를 해제할 수 있습니다.

The reason why definitional equality is so limited is to enable it to be checked by an algorithm.
Propositional equality is much richer, but the computer cannot in general check whether two expressions are propositionally equal, though it can verify that a purported proof is in fact a proof.
The split between definitional and propositional equality represents a division of labor between humans and machines: the most boring equalities are checked automatically as part of definitional equality, freeing the human mind to work on the interesting problems available in propositional equality.
Similarly, definitional equality is invoked automatically by the type checker, while propositional equality must be specifically appealed to.

정의적 동등성이 그렇게 제한적인 이유는 알고리즘으로 확인될 수 있게 하기 위함입니다. 명제적 동등성은 훨씬 더 풍부하지만, 컴퓨터는 일반적으로 두 표현식이 명제적으로 동등한지 확인할 수 없습니다. 하지만 주장된 증명이 실제로 증명인지 확인할 수 있습니다. 정의적 동등성과 명제적 동등성 간의 분할은 인간과 기계 간의 분업을 나타냅니다. 가장 지루한 동등성들은 정의적 동등성의 일부로 자동으로 확인되어, 인간의 마음이 명제적 동등성에서 사용 가능한 흥미로운 문제들에 작동할 수 있도록 해줍니다. 마찬가지로, 정의적 동등성은 타입 체커에 의해 자동으로 호출되는 반면, 명제적 동등성은 구체적으로 호소되어야 합니다.

In [Propositions, Proofs, and Indexing](Interlude___-Propositions___-Proofs___-and-Indexing/#props-proofs-indexing), some equality statements are proved using `decide`.
All of these equality statements are ones in which the propositional equality is in fact already a definitional equality.
Typically, statements of propositional equality are proved by first getting them into a form where they are either definitional or close enough to existing proved equalities, and then using tools like `decide` or `simp` to take care of the simplified cases.
The `simp` tactic is quite powerful: behind the scenes, it uses a number of fast, automated tools to construct a proof.
A simpler tactic called `rfl` specifically uses definitional equality to prove propositional equality.
The name `rfl` is short for *reflexivity*, which is the property of equality that states that everything equals itself.

[명제들, 증명들, 그리고 인덱싱](Interlude___-Propositions___-Proofs___-and-Indexing/#props-proofs-indexing)에서, 일부 동등성 진술들은 `decide`를 사용하여 증명됩니다. 이 모든 동등성 진술들은 명제적 동등성이 실제로 이미 정의적 동등성인 것들입니다. 일반적으로, 명제적 동등성의 진술들은 먼저 그들을 정의적이거나 기존 증명된 동등성에 충분히 가까운 형태로 변환한 후, `decide` 또는 `simp`와 같은 도구를 사용하여 단순화된 경우들을 처리함으로써 증명됩니다. `simp` tactic은 상당히 강력합니다: 뒤에서는, 증명을 구성하기 위해 많은 빠르고 자동화된 도구들을 사용합니다. `rfl`이라는 더 간단한 tactic은 정의적 동등성을 사용하여 명제적 동등성을 증명합니다. `rfl`이라는 이름은 *반사성(reflexivity)*의 약자이며, 이는 모든 것이 자기 자신과 같다는 동등성의 성질입니다.

Unsticking `appendR` requires a proof that `k = Nat.plusR 0 k`, which is not a definitional equality because `plusR` is stuck on the variable in its second argument.
To get it to compute, the `k` must become a concrete constructor.
This is a job for pattern matching.

`appendR`를 해제하려면 `k = Nat.plusR 0 k`의 증명이 필요합니다. 이것은 `plusR`이 두 번째 인자의 변수에 멈춰있기 때문에 정의적 동등성이 아닙니다. 계산하게 하려면, `k`가 구체적 생성자가 되어야 합니다. 이는 패턴 매칭의 일입니다.

The second placeholder is a bit trickier.
The expression `Nat.plusR 0 k + 1` is definitionally equal to `Nat.plusR 0 (k + 1)`.
This means that the goal could also be written `k + 1 = Nat.plusR 0 k + 1`:

두 번째 플레이스홀더는 조금 더 까다롭습니다. 표현식 `Nat.plusR 0 k + 1`은 `Nat.plusR 0 (k + 1)`과 정의적으로 동등합니다. 이는 목표를 `k + 1 = Nat.plusR 0 k + 1`로도 작성할 수 있다는 의미입니다:

```lean
def plusR_zero_left : (k : Nat) → k = Nat.plusR 0 k
  | 0 => by rfl
  | k + 1 => (_ : k + 1 = Nat.plusR 0 k + 1)
```

```
don't know how to synthesize placeholder
context:
k:Nat⊢ k + 1 = Nat.plusR 0 k + 1
```

Propositional equalities can be deployed in a program using the rightward triangle operator `▸`.
Given an equality proof as its first argument and some other expression as its second, this operator replaces instances of one side of the equality with the other side of the equality in the second argument's type.
In other words, the following definition contains no type errors:

명제적 동등성들은 오른쪽 삼각형 연산자 `▸`를 사용하여 프로그램에 배포될 수 있습니다. 첫 번째 인자로 동등성 증명과 두 번째로 다른 표현식이 주어지면, 이 연산자는 두 번째 인자의 타입에서 동등성의 한쪽 인스턴스를 다른 쪽으로 바꿉니다. 다시 말해, 다음 정의는 타입 에러를 포함하지 않습니다:

```lean
def appendR : (n k : Nat) → Vect α n → Vect α k → Vect α (n.plusR k)
  | 0, k, .nil, ys => plusR_zero_left k ▸ (_ : Vect α k)
  | n + 1, k, .cons x xs, ys => _
```

The first placeholder has the expected type:

첫 번째 플레이스홀더는 예상된 타입을 가집니다.

It can now be filled in with `ys`:

이제 `ys`로 채울 수 있습니다:

```lean
def appendR : (n k : Nat) → Vect α n → Vect α k → Vect α (n.plusR k)
  | 0, k, .nil, ys => plusR_zero_left k ▸ ys
  | n + 1, k, .cons x xs, ys => _
```

남은 플레이스홀더를 채우는 것은 덧셈의 다른 인스턴스를 해제해야 합니다.

Here, the statement to be proved is that `Nat.plusR (n + 1) k = Nat.plusR n k + 1`, which can be used with `▸` to draw the `+ 1` out to the top of the expression so that it matches the index of `cons`.

여기서, 증명할 진술은 `Nat.plusR (n + 1) k = Nat.plusR n k + 1`입니다. 이것은 `▸`와 함께 사용하여 `+ 1`을 표현식의 최상단으로 끌어낼 수 있으므로 `cons`의 인덱스와 일치합니다.

The proof is a recursive function that pattern matches on the second argument to `plusR`, namely `k`.
This is because `plusR` itself pattern matches on its second argument, so the proof can “unstick” it through pattern matching, exposing the computational behavior.
The skeleton of the proof is very similar to that of `plusR_zero_left`:

증명은 `plusR`의 두 번째 인자인 `k`에 대해 패턴 매칭하는 재귀 함수입니다. 이것은 `plusR` 자체가 그 두 번째 인자에 대해 패턴 매칭하기 때문입니다. 따라서 증명은 패턴 매칭을 통해 그것을 “해제”할 수 있으므로, 계산 동작을 드러냅니다. 증명의 골격은 `plusR_zero_left`의 것과 매우 유사합니다:

```lean
theorem plusR_succ_left (n : Nat) :
    (k : Nat) → Nat.plusR (n + 1) k = Nat.plusR n k + 1
  | 0 => by rfl
  | k + 1 => _
```

The remaining case's type is definitionally equal to `Nat.plusR (n + 1) k + 1 = Nat.plusR n (k + 1) + 1`, so it can be solved with `congrArg`, just as in `plusR_zero_left`:

남은 경우의 타입은 `Nat.plusR (n + 1) k + 1 = Nat.plusR n (k + 1) + 1`과 정의적으로 동등하므로, `plusR_zero_left`에서처럼 `congrArg`로 해결할 수 있습니다:

```
don't know how to synthesize placeholder
context:
n k:Nat⊢ (n + 1).plusR (k + 1) = n.plusR (k + 1) + 1
```

This results in a finished proof:

이는 완료된 증명이 됩니다:

```lean
theorem plusR_succ_left (n : Nat) :
    (k : Nat) → Nat.plusR (n + 1) k = Nat.plusR n k + 1
  | 0 => by rfl
  | k + 1 => congrArg (· + 1) (plusR_succ_left n k)
```

The finished proof can be used to unstick the second case in `appendR`:

완료된 증명은 `appendR`의 두 번째 경우를 해제하는 데 사용될 수 있습니다:

```lean
def appendR : (n k : Nat) → Vect α n → Vect α k → Vect α (n.plusR k)
  | 0, k, .nil, ys =>
    plusR_zero_left k ▸ ys
  | n + 1, k, .cons x xs, ys =>
    plusR_succ_left n k ▸ .cons x (appendR n k xs ys)
```

When making the length arguments to `appendR` implicit again, they are no longer explicitly named to be appealed to in the proofs.
However, Lean's type checker has enough information to fill them in automatically behind the scenes, because no other values would allow the types to match:

`appendR`의 길이 인자들을 다시 암묵적으로 만들 때, 그들은 더 이상 증명에서 호소되기 위해 명시적으로 명명되지 않습니다. 하지만 Lean의 타입 체커는 뒤에서 자동으로 그들을 채우기에 충분한 정보를 가지고 있습니다. 왜냐하면 다른 값들은 타입들이 일치하도록 하지 않을 것이기 때문입니다:

```lean
def appendR : Vect α n → Vect α k → Vect α (n.plusR k)
  | .nil, ys => plusR_zero_left _ ▸ ys
  | .cons x xs, ys => plusR_succ_left _ _ ▸ .cons x (appendR xs ys)
```

## 7.5.4. Pros and Cons

Indexed families have an important property: pattern matching on them affects definitional equality.
For example, in the `nil` case in a `match` expression on a `Vect`, the length simply *becomes* `0`.
Definitional equality can be very convenient, because it is always active and does not need to be invoked explicitly.

인덱스된 패밀리는 중요한 성질을 가집니다: 그들에 대한 패턴 매칭이 정의적 동등성에 영향을 미칩니다. 예를 들어, `Vect`에 대한 `match` 표현식의 `nil` 경우에서, 길이는 단순히 *0이 됩니다*. 정의적 동등성은 매우 편리할 수 있습니다. 왜냐하면 그것은 항상 활성이며 명시적으로 호출될 필요가 없기 때문입니다.

However, the use of definitional equality with dependent types and pattern matching has serious software engineering drawbacks.
First off, functions must be written especially to be used in types, and functions that are convenient to use in types may not use the most efficient algorithms.
Once a function has been exposed through using it in a type, its implementation has become part of the interface, leading to difficulties in future refactoring.
Secondly, definitional equality can be slow.
When asked to check whether two expressions are definitionally equal, Lean may need to run large amounts of code if the functions in question are complicated and have many layers of abstraction.
Third, error messages that result from failures of definitional equality are not always very easy to understand, because they may be phrased in terms of the internals of functions.
It is not always easy to understand the provenance of the expressions in the error messages.
Finally, encoding non-trivial invariants in a collection of indexed families and dependently-typed functions can often be brittle.
It is often necessary to change early definitions in a system when the exposed reduction behavior of functions proves to not provide convenient definitional equalities.
The alternative is to litter the program with appeals to equality proofs, but these can become quite unwieldy.

그러나 의존 타입과 패턴 매칭을 가진 정의적 동등성의 사용은 심각한 소프트웨어 공학적 단점을 가집니다. 먼저, 함수들은 타입에 사용되도록 특별히 작성되어야 하며, 타입에서 사용하기 편한 함수들은 가장 효율적인 알고리즘을 사용하지 않을 수 있습니다. 함수가 타입에서 사용함으로써 드러나면, 그 구현은 인터페이스의 일부가 되어, 향후 리팩토링에서 어려움이 생깁니다. 둘째, 정의적 동등성은 느릴 수 있습니다. Lean이 두 표현식이 정의적으로 동등한지 확인하도록 요청받으면, 문제의 함수가 복잡하고 많은 추상화 계층을 가질 경우 많은 양의 코드를 실행해야 할 수 있습니다. 셋째, 정의적 동등성의 실패로 인한 에러 메시지는 항상 매우 이해하기 쉽지는 않습니다. 왜냐하면 함수의 내부 측면으로 표현될 수 있기 때문입니다. 에러 메시지의 표현식의 출처를 항상 쉽게 이해할 수 있는 것은 아닙니다. 마지막으로, 인덱스된 패밀리와 의존적으로 타입된 함수의 모음에서 자명하지 않은 불변성을 인코딩하는 것은 종종 취약할 수 있습니다. 함수의 노출된 축약 동작이 편리한 정의적 동등성을 제공하지 않는 것으로 증명될 때 시스템의 초기 정의를 변경해야 하는 경우가 많습니다. 대안은 프로그램에 동등성 증명에 대한 호소를 흩뿌리는 것이지만, 이것들은 상당히 다루기 어려워질 수 있습니다.

In idiomatic Lean code, indexed datatypes are not used very often.
Instead, subtypes and explicit propositions are typically used to enforce important invariants.
This approach involves many explicit proofs, and very few appeals to definitional equality.
As befits an interactive theorem prover, Lean has been designed to make explicit proofs convenient.
Generally speaking, this approach should be preferred in most cases.

관례적인 Lean 코드에서, 인덱스된 데이터타입들은 매우 자주 사용되지 않습니다. 대신, 부분타입(subtype)과 명시적 명제(explicit proposition)들이 일반적으로 중요한 불변성을 적용하는 데 사용됩니다. 이 접근 방식은 많은 명시적 증명들을 포함하고, 정의적 동등성에 대한 호소는 매우 적습니다. 상호 작용적 정리 증명기(interactive theorem prover)에 걸맞게, Lean은 명시적 증명들을 편리하게 만들도록 설계되었습니다. 일반적으로 말해서, 이 접근 방식이 대부분의 경우에 선호되어야 합니다.

However, understanding indexed families of datatypes is important.
Recursive functions such as `plusR_zero_left` and `plusR_succ_left` are in fact *proofs by mathematical induction*.
The base case of the recursion corresponds to the base case in induction, and the recursive call represents an appeal to the induction hypothesis.
More generally, new propositions in Lean are often defined as inductive types of evidence, and these inductive types usually have indices.
The process of proving theorems is in fact constructing expressions with these types behind the scenes, in a process not unlike the proofs in this section.
Also, indexed datatypes are sometimes exactly the right tool for the job.
Fluency in their use is an important part of knowing when to use them.

그러나 데이터타입의 인덱스된 패밀리를 이해하는 것은 중요합니다. `plusR_zero_left`와 `plusR_succ_left`와 같은 재귀 함수들은 실제로 *수학적 귀납법에 의한 증명*입니다. 재귀의 베이스 경우는 귀납법의 베이스 경우에 해당하고, 재귀 호출은 귀납 가정에 대한 호소를 나타냅니다. 더 일반적으로, Lean의 새로운 명제들은 종종 증거의 귀납적 타입으로 정의되며, 이 귀납적 타입들은 보통 인덱스를 가집니다. 정리를 증명하는 과정은 실제로 이 섹션의 증명들과 비슷하지 않은 과정에서, 뒤에서 이 타입들의 표현식을 구성하는 것입니다. 또한, 인덱스된 데이터타입들은 때때로 정확히 올바른 도구입니다. 그들의 사용에 대한 능숙함은 그들을 사용할 때를 알기 위한 중요한 부분입니다.

## 7.5.5. Exercises

* Using a recursive function in the style of `plusR_succ_left`, prove that for all `Nat`s `n` and `k`, `n.plusR k = n + k`.
* Write a function on `Vect` for which `plusR` is more natural than `plusL`, where `plusL` would require proofs to be used in the definition.

* `plusR_succ_left` 스타일의 재귀 함수를 사용하여, 모든 `Nat` `n`과 `k`에 대해 `n.plusR k = n + k`임을 증명합니다.
* `plusL`이 정의에서 증명을 사용해야 하는 `Vect`에 대한 함수를 작성합니다. `plusR`이 더 자연스러운 경우입니다.
