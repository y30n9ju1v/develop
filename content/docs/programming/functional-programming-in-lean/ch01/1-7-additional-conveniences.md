---
title: "Additional Conveniences"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Additional Conveniences"
---

# Additional Conveniences

Lean contains a number of convenience features that make programs much more concise.

# 추가 편의 기능

Lean에는 프로그램을 훨씬 더 간결하게 만들어주는 여러 편의 기능이 포함되어 있습니다.

## 1.7.2. Pattern-Matching Definitions

When defining functions with `def`, it is quite common to name an argument and then immediately use it with pattern matching.
For instance, in `length`, the argument `xs` is used only in `match`.
In these situations, the cases of the `match` expression can be written directly, without naming the argument at all.

`def`로 함수를 정의할 때, 인자에 이름을 붙인 후 즉시 패턴 매칭을 사용하는 것이 일반적입니다.
예를 들어, `length`에서는 인자 `xs`가 `match`에서만 사용됩니다.
이러한 경우들에서는 `match` 표현식의 경우들을 인자에 이름을 붙이지 않고도 바로 작성할 수 있습니다.

The first step is to move the arguments' types to the right of the colon, so the return type is a function type.
For instance, the type of `length` is `List α → Nat`.
Then, replace the `:=` with each case of the pattern match:

첫 번째 단계는 인자들의 타입을 콜론의 오른쪽으로 이동시켜서, 반환 타입이 함수 타입이 되도록 하는 것입니다.
예를 들어, `length`의 타입은 `List α → Nat`입니다.
그 다음 `:=`을 패턴 매치의 각 경우로 대체합니다:

`def length : List α → Nat
| [] => 0
| y :: ys => Nat.succ (length ys)`

This syntax can also be used to define functions that take more than one argument.
In this case, their patterns are separated by commas.
For instance, `drop` takes a number `n` and a list, and returns the list after removing the first `n` entries.

이 문법은 하나 이상의 인자를 받는 함수를 정의할 때도 사용할 수 있습니다.
이 경우, 패턴들은 쉼표로 구분됩니다.
예를 들어, `drop`은 숫자 `n`과 리스트를 받아서 처음 `n`개 항목을 제거한 리스트를 반환합니다.

`def drop : Nat → List α → List α
| Nat.zero, xs => xs
| _, [] => []
| Nat.succ n, x :: xs => drop n xs`

Named arguments and patterns can also be used in the same definition.
For instance, a function that takes a default value and an optional value, and returns the default when the optional value is `none`, can be written:

명명된 인자와 패턴은 같은 정의에서도 함께 사용할 수 있습니다.
예를 들어, 기본값과 선택적 값을 받고, 선택적 값이 `none`일 때 기본값을 반환하는 함수는 다음과 같이 작성할 수 있습니다:

`def fromOption (default : α) : Option α → α
| none => default
| some x => x`

This function is called `Option.getD` in the standard library, and can be called with dot notation:

이 함수는 표준 라이브러리에서 `Option.getD`라고 불리며, 점 표기법으로 호출할 수 있습니다:

`"salmonberry"#eval (some "salmonberry").getD ""`

```
"salmonberry"
```

`""#eval none.getD ""`

```
""
```

## 1.7.3. Local Definitions

It is often useful to name intermediate steps in a computation.
In many cases, intermediate values represent useful concepts all on their own, and naming them explicitly can make the program easier to read.
In other cases, the intermediate value is used more than once.
As in most other languages, writing down the same code twice in Lean causes it to be computed twice, while saving the result in a variable leads to the result of the computation being saved and re-used.

계산의 중간 단계에 이름을 붙이는 것이 유용한 경우가 많습니다.
많은 경우에, 중간 값들은 그 자체로 유용한 개념을 나타내며, 명시적으로 이름을 붙이면 프로그램을 더 쉽게 읽을 수 있습니다.
다른 경우들에서는, 중간 값이 여러 번 사용됩니다.
대부분의 다른 언어와 마찬가지로, Lean에서 같은 코드를 두 번 작성하면 두 번 계산되지만, 변수에 결과를 저장하면 계산 결과가 저장되어 재사용됩니다.

For instance, `unzip` is a function that transforms a list of pairs into a pair of lists.
When the list of pairs is empty, then the result of `unzip` is a pair of empty lists.
When the list of pairs has a pair at its head, then the two fields of the pair are added to the result of unzipping the rest of the list.
This definition of `unzip` follows that description exactly:

예를 들어, `unzip`은 쌍의 리스트를 리스트의 쌍으로 변환하는 함수입니다.
쌍의 리스트가 비어있으면, `unzip`의 결과는 빈 리스트의 쌍입니다.
쌍의 리스트가 헤드에 쌍을 가지고 있으면, 그 쌍의 두 필드가 나머지 리스트를 unzip한 결과에 추가됩니다.
`unzip`의 이 정의는 그 설명을 정확히 따릅니다:

`def unzip : List (α × β) → List α × List β
| [] => ([], [])
| (x, y) :: xys =>
(x :: (unzip xys).fst, y :: (unzip xys).snd)`

Unfortunately, there is a problem: this code is slower than it needs to be.
Each entry in the list of pairs leads to two recursive calls, which makes this function take exponential time.
However, both recursive calls will have the same result, so there is no reason to make the recursive call twice.

안타깝게도, 문제가 있습니다: 이 코드는 필요한 것보다 느립니다.
쌍의 리스트의 각 항목은 두 개의 재귀 호출로 이어지므로, 이 함수는 지수 시간이 걸립니다.
그러나 두 재귀 호출 모두 동일한 결과를 가지므로, 재귀 호출을 두 번 할 이유가 없습니다.

In Lean, the result of the recursive call can be named, and thus saved, using `let`.
Local definitions with `let` resemble top-level definitions with `def`: it takes a name to be locally defined, arguments if desired, a type signature, and then a body following `:=`.
After the local definition, the expression in which the local definition is available (called the *body* of the `let`-expression) must be on a new line, starting at a column in the file that is less than or equal to that of the `let` keyword.
A local definition with `let` in `unzip` looks like this:

Lean에서는 `let`을 사용하여 재귀 호출의 결과에 이름을 붙이고 저장할 수 있습니다.
`let`을 사용한 지역 정의는 `def`을 사용한 최상위 정의와 유사합니다: 지역적으로 정의할 이름, 원하면 인자, 타입 서명, 그리고 `:=` 뒤의 본문을 가집니다.
지역 정의 후, 지역 정의가 사용 가능한 표현식 (`let`-표현식의 *본문*이라고 불림)은 새로운 줄에 있어야 하며, 파일의 `let` 키워드의 열보다 작거나 같은 열에서 시작해야 합니다.
`unzip`에서 `let`을 사용한 지역 정의는 다음과 같습니다:

`def unzip : List (α × β) → List α × List β
| [] => ([], [])
| (x, y) :: xys =>
let unzipped : List α × List β := unzip xys
(x :: unzipped.fst, y :: unzipped.snd)`

To use `let` on a single line, separate the local definition from the body with a semicolon.

`let`을 한 줄에서 사용하려면, 지역 정의와 본문을 세미콜론으로 구분합니다.

Local definitions with `let` may also use pattern matching when one pattern is enough to match all cases of a datatype.
In the case of `unzip`, the result of the recursive call is a pair.
Because pairs have only a single constructor, the name `unzipped` can be replaced with a pair pattern:

`let`을 사용한 지역 정의는 하나의 패턴이 데이터타입의 모든 경우를 매칭하기에 충분할 때 패턴 매칭을 사용할 수 있습니다.
`unzip`의 경우, 재귀 호출의 결과는 쌍입니다.
쌍은 단 하나의 생성자를 가지므로, `unzipped`라는 이름을 쌍 패턴으로 대체할 수 있습니다:

`def unzip : List (α × β) → List α × List β
| [] => ([], [])
| (x, y) :: xys =>
let (xs, ys) : List α × List β := unzip xys
(x :: xs, y :: ys)`

Judicious use of patterns with `let` can make code easier to read, compared to writing the accessor calls by hand.

`let`과 함께 패턴을 신중하게 사용하면 접근자 호출을 직접 작성하는 것보다 코드를 더 쉽게 읽을 수 있습니다.

The biggest difference between `let` and `def` is that recursive `let` definitions must be explicitly indicated by writing `let rec`.
For instance, one way to reverse a list involves a recursive helper function, as in this definition:

`let`과 `def`의 가장 큰 차이점은 재귀적 `let` 정의는 `let rec`을 작성하여 명시적으로 나타내야 한다는 것입니다.
예를 들어, 리스트를 역순으로 하는 한 가지 방법은 이 정의와 같이 재귀 도우미 함수를 사용합니다:

`def reverse (xs : List α) : List α :=
let rec helper : List α → List α → List α
| [], soFar => soFar
| y :: ys, soFar => helper ys (y :: soFar)
helper xs []`

The helper function walks down the input list, moving one entry at a time over to `soFar`.
When it reaches the end of the input list, `soFar` contains a reversed version of the input.

도우미 함수는 입력 리스트를 따라 내려가며, 한 번에 하나의 항목을 `soFar`로 이동합니다.
입력 리스트의 끝에 도달하면, `soFar`는 입력의 역순 버전을 포함합니다.

## 1.7.4. Type Inference

In many situations, Lean can automatically determine an expression's type.
In these cases, explicit types may be omitted from both top-level definitions (with `def`) and local definitions (with `let`).
For example, the recursive call to `unzip` does not need an annotation:

많은 경우에, Lean은 표현식의 타입을 자동으로 결정할 수 있습니다.
이 경우들에서, 명시적 타입은 최상위 정의(`def`) 및 지역 정의(`let`) 모두에서 생략될 수 있습니다.
예를 들어, `unzip`에 대한 재귀 호출은 주석이 필요하지 않습니다:

`def unzip : List (α × β) → List α × List β
| [] => ([], [])
| (x, y) :: xys =>
let unzipped := unzip xys
(x :: unzipped.fst, y :: unzipped.snd)`

As a rule of thumb, omitting the types of literal values (like strings and numbers) usually works, although Lean may pick a type for literal numbers that is more specific than the intended type.
Lean can usually determine a type for a function application, because it already knows the argument types and the return type.
Omitting return types for function definitions will often work, but function parameters typically require annotations.
Definitions that are not functions, like `unzipped` in the example, do not need type annotations if their bodies do not need type annotations, and the body of this definition is a function application.

경험상, 리터럴 값(문자열이나 숫자 같은)의 타입을 생략하는 것은 보통 작동하지만, Lean은 리터럴 숫자에 대해 의도한 타입보다 더 구체적인 타입을 선택할 수 있습니다.
Lean은 이미 인자 타입과 반환 타입을 알고 있으므로 보통 함수 적용에 대한 타입을 결정할 수 있습니다.
함수 정의의 반환 타입을 생략하는 것은 종종 작동하지만, 함수 매개변수는 보통 주석이 필요합니다.
예의 `unzipped`처럼 함수가 아닌 정의는 본문이 타입 주석이 필요 없고 이 정의의 본문이 함수 적용이라면 타입 주석이 필요하지 않습니다.

Omitting the return type for `unzip` is possible when using an explicit `match` expression:

`def unzip (pairs : List (α × β)) :=
match pairs with
| [] => ([], [])
| (x, y) :: xys =>
let unzipped := unzip xys
(x :: unzipped.fst, y :: unzipped.snd)`

`unzip`의 반환 타입을 생략하는 것은 명시적 `match` 표현식을 사용할 때 가능합니다.

일반적으로, 타입 주석이 너무 많은 쪽으로 실수하는 것이 너무 적은 쪽으로 실수하는 것보다 낫습니다.

우선, 명시적 타입은 코드에 대한 가정을 독자들에게 전달합니다.
Lean이 타입을 스스로 결정할 수 있다 해도, Lean에 반복적으로 타입 정보를 묻지 않고도 코드를 읽는 것이 더 쉬울 수 있습니다.
둘째, 명시적 타입은 오류를 지역화하는 데 도움이 됩니다.
프로그램이 타입에 대해 더 명시적일수록, 오류 메시지가 더 유익할 수 있습니다.
이것은 매우 표현력이 풍부한 타입 시스템을 가진 Lean 같은 언어에서 특히 중요합니다.
셋째, 명시적 타입은 처음부터 프로그램을 작성하기가 더 쉽게 합니다.
타입은 명세이며, 컴파일러의 피드백은 명세를 충족하는 프로그램을 작성하는 데 유용한 도구가 될 수 있습니다.
마지막으로, Lean의 타입 추론은 최선의 노력 시스템입니다.
Lean의 타입 시스템이 매우 표현력이 풍부하기 때문에, 모든 표현식에 대해 찾을 “최고” 또는 가장 일반적인 타입은 없습니다.
즉, 타입을 얻는다 해도 주어진 애플리케이션에 대해 *올바른* 타입이라는 보장이 없습니다.
예를 들어, `14`는 `Nat` 또는 `Int`일 수 있습니다:

`14 : Nat#check 14`

```
14 : Nat
```

`14 : Int#check (14 : Int)`

```
14 : Int
```

Missing type annotations can give confusing error messages.
Omitting all types from the definition of `unzip`:

타입 주석이 없으면 혼란스러운 오류 메시지가 나타날 수 있습니다.
`unzip`의 정의에서 모든 타입을 생략합니다:

`def unzip pairs :=
match pairs with
| Invalid match expression: This pattern contains metavariables:
[][] => ([], [])
| (x, y) :: xys =>
let unzipped := unzip xys
(x :: unzipped.fst, y :: unzipped.snd)`

leads to a message about the `match` expression:

```
Invalid match expression: This pattern contains metavariables:
  []
```

This is because `match` needs to know the type of the value being inspected, but that type was not available.
A “metavariable” is an unknown part of a program, written `?m.XYZ` in error messages—they are described in the [section on Polymorphism](../ch01/).
In this program, the type annotation on the argument is required.

Even some very simple programs require type annotations.
For instance, the identity function just returns whatever argument it is passed.
With argument and type annotations, it looks like this:

이것은 `match`가 검사되는 값의 타입을 알아야 하지만, 그 타입을 사용할 수 없었기 때문입니다.
“metavariable”은 프로그램의 미지의 부분이며, 오류 메시지에서 `?m.XYZ`로 쓰여집니다 - 이들은 [Polymorphism 섹션](../ch01/)에서 설명됩니다.
이 프로그램에서, 인자의 타입 주석은 필수입니다.

심지어 아주 간단한 프로그램도 타입 주석이 필요합니다.
예를 들어, 항등 함수는 단지 전달받은 인자를 반환합니다.
인자와 타입 주석과 함께, 다음과 같이 보입니다:

`def id (x : α) : α := x`

Lean is capable of determining the return type on its own:

`def id (x : α) := x`

Lean은 반환 타입을 스스로 결정할 수 있습니다.

Omitting the argument type, however, causes an error:

`` def Failed to infer type of definition `id`id Failed to infer type of binder `x`x := x ``

```
Failed to infer type of binder `x`
```

그러나 인자 타입을 생략하면 오류가 발생합니다.

In general, messages that say something like “failed to infer” or that mention metavariables are often a sign that more type annotations are necessary.
Especially while still learning Lean, it is useful to provide most types explicitly.

일반적으로, “failed to infer”과 같이 말하는 메시지나 metavariable을 언급하는 메시지는 종종 더 많은 타입 주석이 필요하다는 신호입니다.
특히 Lean을 배우는 동안, 대부분의 타입을 명시적으로 제공하는 것이 유용합니다.

## 1.7.5. Simultaneous Matching

Pattern-matching expressions, just like pattern-matching definitions, can match on multiple values at once.
Both the expressions to be inspected and the patterns that they match against are written with commas between them, similarly to the syntax used for definitions.
Here is a version of `drop` that uses simultaneous matching:

패턴 매칭 표현식은 패턴 매칭 정의와 마찬가지로 여러 값에 동시에 매칭할 수 있습니다.
검사할 표현식과 매칭할 패턴 모두 정의에 사용된 문법과 유사하게 쉼표를 사이에 두고 작성됩니다.
동시 매칭을 사용하는 `drop`의 버전은 다음과 같습니다:

`def drop (n : Nat) (xs : List α) : List α :=
match n, xs with
| Nat.zero, ys => ys
| _, [] => []
| Nat.succ n , y :: ys => drop n ys`

Simultaneous matching resembles matching on a pair, but there is an important difference.
Lean tracks the connection between the expression being matched and the patterns, and this information is used for purposes that include checking for termination and propagating static type information.
As a result, the version of `sameLength` that matches a pair is rejected by the termination checker, because the connection between `xs` and `x :: xs'` is obscured by the intervening pair:

동시 매칭은 쌍에 대한 매칭과 유사하지만, 중요한 차이가 있습니다.
Lean은 매칭되는 표현식과 패턴 간의 연결을 추적하며, 이 정보는 종료 확인 및 정적 타입 정보 전파 등의 목적으로 사용됩니다.
결과적으로, 쌍에 매칭하는 `sameLength` 버전은 종료 확인자에 의해 거부되는데, `xs`와 `x :: xs'` 사이의 연결이 중간 쌍에 의해 가려지기 때문입니다:

`` def fail to show termination for
sameLength
with errors
failed to infer structural recursion:
Not considering parameter α of sameLength:
it is unchanged in the recursive calls
Not considering parameter β of sameLength:
it is unchanged in the recursive calls
Cannot use parameter xs:
failed to eliminate recursive application
sameLength xs' ys'
Cannot use parameter ys:
failed to eliminate recursive application
sameLength xs' ys'

Could not find a decreasing measure.
The basic measures relate at each recursive call as follows:
(<, ≤, =: relation proved, ? all proofs failed, _: no proof attempted)
xs ys
1) 1816:28-46 ? ?
Please use `termination_by` to specify a decreasing measure.sameLength (xs : List α) (ys : List β) : Bool :=
match (xs, ys) with
| ([], []) => true
| (x :: xs', y :: ys') => sameLength xs' ys'
| _ => false ``

```
fail to show termination for
  sameLength
with errors
failed to infer structural recursion:
Not considering parameter α of sameLength:
  it is unchanged in the recursive calls
Not considering parameter β of sameLength:
  it is unchanged in the recursive calls
Cannot use parameter xs:
  failed to eliminate recursive application
    sameLength xs' ys'
Cannot use parameter ys:
  failed to eliminate recursive application
    sameLength xs' ys'

Could not find a decreasing measure.
The basic measures relate at each recursive call as follows:
(<, ≤, =: relation proved, ? all proofs failed, _: no proof attempted)
              xs ys
1) 1816:28-46  ?  ?
Please use `termination_by` to specify a decreasing measure.
```

Simultaneously matching both lists is accepted:

감소하는 측정값을 지정하려면 `termination_by`를 사용하세요.

동시에 두 리스트를 모두 매칭하는 것은 허용됩니다:

`def sameLength (xs : List α) (ys : List β) : Bool :=
match xs, ys with
| [], [] => true
| x :: xs', y :: ys' => sameLength xs' ys'
| _, _ => false`

## 1.7.6. Natural Number Patterns

In the section on [datatypes and patterns](../ch01/), `even` was defined like this:

[datatypes and patterns 섹션](../ch01/)에서, `even`은 다음과 같이 정의되었습니다:

`def even (n : Nat) : Bool :=
match n with
| Nat.zero => true
| Nat.succ k => not (even k)`

Just as there is special syntax to make list patterns more readable than using `List.cons` and `List.nil` directly, natural numbers can be matched using literal numbers and `+`.
For example, `even` can also be defined like this:

`List.cons`와 `List.nil`을 직접 사용하는 것보다 리스트 패턴을 더 읽기 좋게 만드는 특별한 문법이 있는 것처럼, 자연수는 리터럴 숫자와 `+`를 사용하여 매칭할 수 있습니다.
예를 들어, `even`은 또한 다음과 같이 정의할 수 있습니다:

`def even : Nat → Bool
| 0 => true
| n + 1 => not (even n)`

In this notation, the arguments to the `+` pattern serve different roles.
Behind the scenes, the left argument (`n` above) becomes an argument to some number of `Nat.succ` patterns, and the right argument (`1` above) determines how many `Nat.succ`s to wrap around the pattern.

이 표기법에서, `+` 패턴에 대한 인자는 서로 다른 역할을 합니다.
내부적으로, 왼쪽 인자(`n`위의)는 어떤 수의 `Nat.succ` 패턴에 대한 인자가 되며, 오른쪽 인자(`1` 위의)는 패턴 주위에 얼마나 많은 `Nat.succ`를 감싸야 하는지 결정합니다.
The explicit patterns in `halve`, which divides a `Nat` by two and drops the remainder:

`Nat`을 2로 나누고 나머지를 버리는 `halve`의 명시적 패턴:

`def halve : Nat → Nat
| Nat.zero => 0
| Nat.succ Nat.zero => 0
| Nat.succ (Nat.succ n) => halve n + 1`

can be replaced by numeric literals and `+`:

숫자 리터럴과 `+`로 대체할 수 있습니다:

`def halve : Nat → Nat
| 0 => 0
| 1 => 0
| n + 2 => halve n + 1`

Behind the scenes, both definitions are completely equivalent.
Remember: `halve n + 1` is equivalent to `(halve n) + 1`, not `halve (n + 1)`.

내부적으로, 두 정의는 완전히 동등합니다.
기억하세요: `halve n + 1`은 `(halve n) + 1`과 동등하고, `halve (n + 1)`이 아닙니다.

When using this syntax, the second argument to `+` should always be a literal `Nat`.
Even though addition is commutative, flipping the arguments in a pattern can result in errors like the following:

이 문법을 사용할 때, `+`의 두 번째 인자는 항상 리터럴 `Nat`이어야 합니다.
덧셈이 교환법칙을 만족하지만, 패턴에서 인자를 뒤집으면 다음과 같은 오류가 발생할 수 있습니다:

`` def halve : Nat → Nat
| 0 => 0
| 1 => 0
Invalid pattern(s): `n` is an explicit pattern variable, but it only occurs in positions that are inaccessible to pattern matching:
.(Nat.add 2 n)| 2 + n => halve n + 1 ``

```
Invalid pattern(s): `n` is an explicit pattern variable, but it only occurs in positions that are inaccessible to pattern matching:
  .(Nat.add 2 n)
```

This restriction enables Lean to transform all uses of the `+` notation in a pattern into uses of the underlying `Nat.succ`, keeping the language simpler behind the scenes.

이 제한은 Lean이 패턴의 모든 `+` 표기법 사용을 기본 `Nat.succ` 사용으로 변환할 수 있게 하므로, 언어를 내부적으로 더 간단하게 유지합니다.

## 1.7.7. Anonymous Functions

Functions in Lean need not be defined at the top level.
As expressions, functions are produced with the `fun` syntax.
Function expressions begin with the keyword `fun`, followed by one or more parameters, which are separated from the return expression using `=>`.
For instance, a function that adds one to a number can be written:

Lean의 함수는 최상위 수준에서 정의될 필요가 없습니다.
표현식으로서, 함수는 `fun` 문법으로 생성됩니다.
함수 표현식은 `fun` 키워드로 시작하고, 반환 표현식과 `=>`로 분리된 하나 이상의 매개변수가 뒤따릅니다.
예를 들어, 숫자에 하나를 더하는 함수는 다음과 같이 작성할 수 있습니다:

`fun x => x + 1 : Nat → Nat#check fun x => x + 1`

```
fun x => x + 1 : Nat → Nat
```

Type annotations are written the same way as on `def`, using parentheses and colons:

타입 주석은 `def`에서와 동일한 방식으로 괄호와 콜론을 사용하여 작성됩니다:

`fun x => x + 1 : Int → Int#check fun (x : Int) => x + 1`

```
fun x => x + 1 : Int → Int
```

Similarly, implicit parameters may be written with curly braces:

유사하게, 암시적 매개변수는 중괄호로 작성할 수 있습니다:

`fun {α} x => x : {α : Type} → α → α#check fun {α : Type} (x : α) => x`

```
fun {α} x => x : {α : Type} → α → α
```

This style of anonymous function expression is often referred to as a *lambda expression*, because the typical notation used in mathematical descriptions of programming languages uses the Greek letter λ (lambda) where Lean has the keyword `fun`.
Even though Lean does permit `λ` to be used instead of `fun`, it is most common to write `fun`.

이 스타일의 무명 함수 표현식은 종종 *lambda 표현식*이라고 불리는데, 프로그래밍 언어의 수학적 설명에서 사용되는 전형적인 표기법이 Lean의 `fun` 키워드 대신 그리스 문자 λ(lambda)를 사용하기 때문입니다.
Lean은 `fun` 대신 `λ`를 사용하도록 허용하지만, `fun`을 작성하는 것이 가장 일반적입니다.

Anonymous functions also support the multiple-pattern style used in `def`.
For instance, a function that returns the predecessor of a natural number if it exists can be written:

무명 함수는 또한 `def`에서 사용되는 다중 패턴 스타일을 지원합니다.
예를 들어, 존재하면 자연수의 전임자를 반환하는 함수는 다음과 같이 작성할 수 있습니다:

`fun x =>
match x with
| 0 => none
| n.succ => some n : Nat → Option Nat#check fun
| 0 => none
| n + 1 => some n`

```
fun x =>
  match x with
  | 0 => none
  | n.succ => some n : Nat → Option Nat
```

Note that Lean's own description of the function has a named argument and a `match` expression.
Many of Lean's convenient syntactic shorthands are expanded to simpler syntax behind the scenes, and the abstraction sometimes leaks.

Lean 자신의 함수 설명이 명명된 인자와 `match` 표현식을 가지고 있다는 것에 유의하세요.
Lean의 많은 편리한 문법 약칭은 내부적으로 더 간단한 문법으로 확장되므로, 때때로 추상화가 누출됩니다.

Definitions using `def` that take arguments may be rewritten as function expressions.
For instance, a function that doubles its argument can be written as follows:

`def`을 사용한 정의는 함수 표현식으로 다시 작성될 수 있습니다.
예를 들어, 인자를 두 배로 하는 함수는 다음과 같이 작성할 수 있습니다:

`def double : Nat → Nat := fun
| 0 => 0
| k + 1 => double k + 2`

When an anonymous function is very simple, like `fun x => x + 1`, the syntax for creating the function can be fairly verbose.
In that particular example, six non-whitespace characters are used to introduce the function, and its body consists of only three non-whitespace characters.
For these simple cases, Lean provides a shorthand.
In an expression surrounded by parentheses, a centered dot character `·` can stand for a parameter, and the expression inside the parentheses becomes the function's body.
That particular function can also be written `(· + 1)`.

무명 함수가 매우 간단할 때, 예를 들어 `fun x => x + 1`처럼, 함수를 생성하는 문법은 매우 장황할 수 있습니다.
그 특정 예에서, 6개의 공백이 아닌 문자는 함수를 도입하는 데 사용되고, 본문은 3개의 공백이 아닌 문자만 포함합니다.
이러한 간단한 경우에 대해, Lean은 약칭을 제공합니다.
괄호로 둘러싼 표현식에서, 중심 점 문자 `·`는 매개변수를 나타낼 수 있으며, 괄호 안의 표현식은 함수의 본문이 됩니다.
그 특정 함수는 또한 `(· + 1)`로 작성될 수 있습니다.

The centered dot always creates a function out of the *closest* surrounding set of parentheses.
For instance, `(· + 5, 3)` is a function that returns a pair of numbers, while `((· + 5), 3)` is a pair of a function and a number.
If multiple dots are used, then they become parameters from left to right:

중심 점은 항상 *가장 가까운* 괄호 집합 밖으로 함수를 만듭니다.
예를 들어, `(· + 5, 3)`은 숫자 쌍을 반환하는 함수이고, `((· + 5), 3)`은 함수와 숫자의 쌍입니다.
여러 개의 점이 사용되면, 왼쪽부터 오른쪽까지 매개변수가 됩니다:

`(· , ·) 1 2``(1, ·) 2``(1, 2)`

Anonymous functions can be applied in precisely the same way as functions defined using `def` or `let`.
The command `10#eval (fun x => x + x) 5` results in:

무명 함수는 `def` 또는 `let`을 사용하여 정의된 함수와 정확히 동일한 방식으로 적용될 수 있습니다.
명령어 `10#eval (fun x => x + x) 5`의 결과:

```
10
```

while `10#eval (· * 2) 5` results in:

한편, `10#eval (· * 2) 5`의 결과.

## 1.7.8. Namespaces

Each name in Lean occurs in a *namespace*, which is a collection of names.
Names are placed in namespaces using `.`, so `List.map` is the name `map` in the `List` namespace.
Names in different namespaces do not conflict with each other, even if they are otherwise identical.
This means that `List.map` and `Array.map` are different names.
Namespaces may be nested, so `Project.Frontend.User.loginTime` is the name `loginTime` in the nested namespace `Project.Frontend.User`.

Lean의 각 이름은 이름들의 모음인 *네임스페이스*에서 발생합니다.
이름은 `.`을 사용하여 네임스페이스에 배치되므로, `List.map`은 `List` 네임스페이스의 `map` 이름입니다.
다른 네임스페이스의 이름은 서로 충돌하지 않습니다. 비록 그들이 동일하더라도.
즉, `List.map`과 `Array.map`은 다른 이름입니다.
네임스페이스는 중첩될 수 있으므로, `Project.Frontend.User.loginTime`은 중첩된 네임스페이스 `Project.Frontend.User`의 `loginTime` 이름입니다.

Names can be directly defined within a namespace.
For instance, the name `double` can be defined in the `Nat` namespace:

이름은 네임스페이스 내에서 직접 정의될 수 있습니다.
예를 들어, `double` 이름은 `Nat` 네임스페이스에서 정의될 수 있습니다:

`def Nat.double (x : Nat) : Nat := x + x`

Because `Nat` is also the name of a type, dot notation is available to call `Nat.double` on expressions with type `Nat`:

`Nat`은 또한 타입의 이름이므로, `Nat` 타입의 표현식에 대해 `Nat.double`을 호출하기 위해 점 표기법을 사용할 수 있습니다:

`8#eval (4 : Nat).double`

```
8
```

In addition to defining names directly in a namespace, a sequence of declarations can be placed in a namespace using the `namespace` and `end` commands.
For instance, this defines `triple` and `quadruple` in the namespace `NewNamespace`:

네임스페이스에서 이름을 직접 정의하는 것 외에도, `namespace`와 `end` 명령을 사용하여 선언 시퀀스를 네임스페이스에 배치할 수 있습니다.
예를 들어, 이것은 `NewNamespace` 네임스페이스에서 `triple`과 `quadruple`을 정의합니다:

`namespace NewNamespace
def triple (x : Nat) : Nat := 3 * x
def quadruple (x : Nat) : Nat := 2 * x + 2 * x
end NewNamespace`

To refer to them, prefix their names with `NewNamespace.`:

이들을 참조하려면, 이름 앞에 `NewNamespace.`를 붙입니다:

`NewNamespace.triple (x : Nat) : Nat#check NewNamespace.triple`

```
NewNamespace.triple (x : Nat) : Nat
```

`NewNamespace.quadruple (x : Nat) : Nat#check NewNamespace.quadruple`

```
NewNamespace.quadruple (x : Nat) : Nat
```

Namespaces may be *opened*, which allows the names in them to be used without explicit qualification.
Writing `open` `MyNamespace``in` before an expression causes the contents of `MyNamespace` to be available in the expression.
For example, `timesTwelve` uses both `quadruple` and `triple` after opening `NewNamespace`:

예를 들어, `timesTwelve`는 `NewNamespace`를 열 때 `quadruple`과 `triple`을 모두 사용합니다:

`def timesTwelve (x : Nat) :=
open NewNamespace in
quadruple (triple x)`

Namespaces can also be opened prior to a command.
This allows all parts of the command to refer to the contents of the namespace, rather than just a single expression.
To do this, place the `open` command prior to the command.

네임스페이스는 명령 전에도 열 수 있습니다.
이렇게 하면 명령의 모든 부분이 단일 표현식이 아닌 네임스페이스의 내용을 참조할 수 있습니다.
이를 수행하려면, 명령 전에 `open` 명령을 배치합니다.

`open NewNamespace in
NewNamespace.quadruple (x : Nat) : Nat#check quadruple`

Function signatures show the name's full namespace.
Namespaces may additionally be opened for *all* following commands for the rest of the file.
To do this, simply omit the `in` from a top-level usage of `open`.

함수 서명은 이름의 전체 네임스페이스를 보여줍니다.
네임스페이스는 파일의 나머지 부분에서 뒤따르는 *모든* 명령을 위해 추가로 열 수 있습니다.
이를 수행하려면, 최상위 수준의 `open` 사용에서 `in`을 생략하면 됩니다.

## 1.7.10. Positional Structure Arguments

The [section on structures](../ch01/) presents two ways of constructing structures:

[section on structures](../ch01/)는 구조를 생성하는 두 가지 방법을 제시합니다:

1. The constructor can be called directly, as in `Point.mk 1 2`.
2. Brace notation can be used, as in `{ x := 1, y := 2 }`.

1. `Point.mk 1 2`에서와 같이 생성자를 직접 호출할 수 있습니다.
2. `{ x := 1, y := 2 }`에서와 같이 중괄호 표기법을 사용할 수 있습니다.

In some contexts, it can be convenient to pass arguments positionally, rather than by name, but without naming the constructor directly.
For instance, defining a variety of similar structure types can help keep domain concepts separate, but the natural way to read the code may treat each of them as being essentially a tuple.
In these contexts, the arguments can be enclosed in angle brackets.
A `Point` can be written in this positional form.
Be careful!
Even though they look like the less-than sign and greater-than sign, these brackets are different.
They can be input using special character codes.

일부 경우에는 이름으로가 아닌 위치로 인자를 전달하는 것이 편할 수 있지만, 생성자를 직접 명명하지 않고 해야 합니다.
예를 들어, 유사한 구조 타입의 다양성을 정의하면 도메인 개념을 분리하는 데 도움이 될 수 있지만, 코드를 읽는 자연스러운 방법은 각각을 본질적으로 튜플로 취급할 수 있습니다.
이러한 경우에는, 인자를 특수 각도 괄호로 묶을 수 있습니다.
`Point`는 이 위치 형식으로 작성될 수 있습니다.
조심하세요!
비록 그들이 부등호 기호처럼 보이지만, 이 괄호는 다릅니다.
특수 문자 코드를 사용하여 입력할 수 있습니다.

Just as with the brace notation for named constructor arguments, this positional syntax can only be used in a context where Lean can determine the structure's type, either from a type annotation or from other type information in the program.
For instance, positional notation without type information yields an error:

중괄호 표기법과 마찬가지로 명명된 생성자 인자의 경우, 이 위치 문법은 Lean이 타입 주석이나 프로그램의 다른 타입 정보에서 구조의 타입을 결정할 수 있는 경우에만 사용될 수 있습니다.
예를 들어, 타입 정보 없이 위치 표기법을 사용하면 오류가 발생합니다:

```
Invalid `⟨...⟩` notation: The expected type of this term could not be determined
```

This error occurs because there is no type information available.
Adding an annotation solves the problem:

타입 정보를 사용할 수 없기 때문에 이 오류가 발생합니다.
주석을 추가하면 문제가 해결됩니다:

```
{ x := 1.000000, y := 2.000000 }
```

## 1.7.11. String Interpolation

In Lean, prefixing a string with `s!` triggers *interpolation*, where expressions contained in curly braces inside the string are replaced with their values.
This is similar to `f`-strings in Python and `$`-prefixed strings in C#.
For instance,

Lean에서, 문자열 앞에 `s!`를 붙이면 *interpolation*이 트리거되므로, 문자열 내의 중괄호에 포함된 표현식이 값으로 대체됩니다.
이것은 Python의 `f`-문자열 및 C#의 `$`-접두어가 붙은 문자열과 유사합니다.
예를 들어,

`"three fives is 15"#eval s!"three fives is {NewNamespace.triple 5}"`

yields the output

```
"three fives is 15"
```

Not all expressions can be interpolated into a string.
For instance, attempting to interpolate a function results in an error.

모든 표현식을 문자열로 interpolate할 수는 없습니다.
예를 들어, 함수를 interpolate하려고 시도하면 오류가 발생합니다.

`` toString "three fives is " ++ sorry : String#check s!"three fives is {failed to synthesize
ToString (Nat → Nat)

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.NewNamespace.triple}" ``

yields the error

```
failed to synthesize
  ToString (Nat → Nat)

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

This is because there is no standard way to convert functions into strings.
Just as the compiler maintains a table that describes how to display the result of evaluating expressions of various types, it maintains a table that describes how to convert values of various types into strings.
The message `failed to synthesize instance` means that the Lean compiler didn't find an entry in this table for the given type.
The chapter on [type classes](../ch03/) describes this mechanism in more detail, including the means of adding new entries to the table.

이것은 함수를 문자열로 변환하는 표준 방법이 없기 때문입니다.
컴파일러가 다양한 타입의 표현식의 평가 결과를 표시하는 방법을 설명하는 테이블을 유지하는 것처럼, 다양한 타입의 값을 문자열로 변환하는 방법을 설명하는 테이블을 유지합니다.
`failed to synthesize instance` 메시지는 Lean 컴파일러가 주어진 타입에 대해 이 테이블에서 항목을 찾지 못했다는 의미입니다.
[type classes](../ch03/) 장은 이 메커니즘을 더 자세히 설명하며, 테이블에 새 항목을 추가하는 방법을 포함합니다.
