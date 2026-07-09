---
title: "5.4. 대안"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "대안"
---

# Alternatives

## 5.4.1. Recovery from Failure

## 5.4.1. 실패로부터의 회복

`Validate` can also be used in situations where there is more than one way for input to be acceptable.
For the input form `RawInput`, an alternative set of business rules that implement conventions from a legacy system might be the following:

`Validate`는 입력이 수용 가능한 방법이 여러 개인 상황에서도 사용될 수 있습니다. 입력 양식 `RawInput`의 경우, 레거시 시스템의 관례를 구현하는 대체 비즈니스 규칙 집합은 다음과 같을 수 있습니다:

1. All human users must provide a birth year that is four digits.
2. Users born prior to 1970 do not need to provide names, due to incomplete older records.
3. Users born after 1970 must provide names.
4. Companies should enter `"FIRM"` as their year of birth and provide a company name.

1. 모든 인간 사용자는 4자리 생년을 제공해야 합니다.
2. 1970년 이전에 태어난 사용자는 불완전한 오래된 기록으로 인해 이름을 제공할 필요가 없습니다.
3. 1970년 이후에 태어난 사용자는 이름을 제공해야 합니다.
4. 회사는 `"FIRM"`을 생년으로 입력하고 회사명을 제공해야 합니다.

No particular provision is made for users born in 1970.
It is expected that they will either give up, lie about their year of birth, or call.
The company considers this an acceptable cost of doing business.

1970년에 태어난 사용자에 대해서는 특별한 규정이 없습니다. 그들은 포기하거나, 생년을 거짓으로 말하거나, 전화를 할 것으로 예상됩니다. 회사는 이를 비즈니스 운영의 수용 가능한 비용으로 간주합니다.

The following inductive type captures the values that can be produced from these stated rules:

다음 귀납 유형은 이러한 명시된 규칙으로부터 생성될 수 있는 값들을 포착합니다:

```lean
abbrev NonEmptyString := {s : String // s ≠ ""}

inductive LegacyCheckedInput where
  | humanBefore1970 :
    (birthYear : {y : Nat // y > 999 ∧ y < 1970}) →
    String →
    LegacyCheckedInput
  | humanAfter1970 :
    (birthYear : {y : Nat // y > 1970}) →
    NonEmptyString →
    LegacyCheckedInput
  | company :
    NonEmptyString →
    LegacyCheckedInput
deriving Repr
```

A validator for these rules is more complicated, however, as it must address all three cases.
While it can be written as a series of nested `if` expressions, it's easier to design the three cases independently and then combine them.
This requires a means of recovering from failure while preserving error messages:

이러한 규칙에 대한 검증자는 더 복잡하지만, 세 가지 경우를 모두 처리해야 합니다. 중첩된 `if` 표현 시리즈로 작성할 수 있지만, 세 가지 경우를 독립적으로 설계한 다음 결합하는 것이 더 쉽습니다. 이를 위해서는 오류 메시지를 보존하면서 실패로부터 회복하는 수단이 필요합니다:

```lean
def Validate.orElse
    (a : Validate ε α)
    (b : Unit → Validate ε α) :
    Validate ε α :=
  match a with
  | .ok x => .ok x
  | .errors errs1 =>
    match b () with
    | .ok x => .ok x
    | .errors errs2 => .errors (errs1 ++ errs2)
```

This pattern of recovery from failures is common enough that Lean has built-in syntax for it, attached to a type class named `OrElse`:

실패로부터 회복하는 이 패턴은 흔하기 때문에 Lean은 `OrElse`라는 type class에 연결된 내장 구문을 가지고 있습니다:

```lean
class OrElse (α : Type) where
  orElse : α → (Unit → α) → α
```

The expression `E1 <|> E2` is short for `OrElse.orElse E1 (fun () => E2)`.
An instance of `OrElse` for `Validate` allows this syntax to be used for error recovery:

표현식 `E1 <|> E2`는 `OrElse.orElse E1 (fun () => E2)`의 축약입니다. `Validate`에 대한 `OrElse` 인스턴스는 오류 회복에 이 구문을 사용할 수 있게 합니다:

```lean
instance : OrElse (Validate ε α) where
  orElse := Validate.orElse
```

The validator for `LegacyCheckedInput` can be built from a validator for each constructor.
The rules for a company state that the birth year should be the string `"FIRM"` and that the name should be non-empty.
The constructor `LegacyCheckedInput.company`, however, has no representation of the birth year at all, so there's no easy way to carry it out using `<*>`.
The key is to use a function with `<*>` that ignores its argument.

`LegacyCheckedInput`에 대한 검증자는 각 생성자에 대한 검증자로부터 구축될 수 있습니다. 회사에 대한 규칙은 생년이 문자열 `"FIRM"`이어야 하고 이름이 비어있지 않아야 함을 나타냅니다. 그러나 생성자 `LegacyCheckedInput.company`는 생년을 표현하지 않으므로 `<*>`를 사용하여 쉽게 수행할 수 있는 방법이 없습니다. 핵심은 인수를 무시하는 `<*>` 함수를 사용하는 것입니다.

Checking that a Boolean condition holds without recording any evidence of this fact in a type can be accomplished with `checkThat`:

Boolean 조건이 type에 증거를 기록하지 않고도 유지되는지 확인하는 것은 `checkThat`으로 수행할 수 있습니다:

```lean
def checkThat (condition : Bool)
    (field : Field) (msg : String) :
    Validate (Field × String) Unit :=
  if condition then pure () else reportError field msg
```

This definition of `checkCompany` uses `checkThat`, and then throws away the resulting `Unit` value:

이 `checkCompany` 정의는 `checkThat`을 사용한 다음, 결과적인 `Unit` 값을 버립니다:

```lean
def checkCompany (input : RawInput) :
    Validate (Field × String) LegacyCheckedInput :=
  pure (fun () name => .company name) <*>
    checkThat (input.birthYear == "FIRM")
      "birth year" "FIRM if a company" <*>
    checkName input.name
```

However, this definition is quite noisy.
It can be simplified in two ways.
The first is to replace the first use of `<*>` with a specialized version that automatically ignores the value returned by the first argument, called `*>`.
This operator is also controlled by a type class, called `SeqRight`, and `E1 *> E2` is syntactic sugar for `SeqRight.seqRight E1 (fun () => E2)`:

하지만 이 정의는 상당히 복잡합니다. 두 가지 방법으로 단순화될 수 있습니다. 첫 번째는 `<*>`의 첫 번째 사용을 `*>`라고 불리는 첫 번째 인수에 의해 반환된 값을 자동으로 무시하는 특수 버전으로 대체하는 것입니다. 이 연산자는 또한 `SeqRight`라는 type class로 제어되며, `E1 *> E2`는 `SeqRight.seqRight E1 (fun () => E2)`의 syntactic sugar입니다:

```lean
class SeqRight (f : Type → Type) where
  seqRight : f α → (Unit → f β) → f β
```

There is a default implementation of `seqRight` in terms of `seq`: `seqRight (a : f α) (b : Unit → f β) : f β := pure (fun _ x => x) <*> a <*> b ()`.

`seq`의 관점에서 `seqRight`의 기본 구현이 있습니다: `seqRight (a : f α) (b : Unit → f β) : f β := pure (fun _ x => x) <*> a <*> b ()`.

Using `seqRight`, `checkCompany` becomes simpler:

`seqRight`를 사용하면, `checkCompany`는 더 간단해집니다:

```lean
def checkCompany (input : RawInput) :
    Validate (Field × String) LegacyCheckedInput :=
  checkThat (input.birthYear == "FIRM")
    "birth year" "FIRM if a company" *>
  pure .company <*> checkName input.name
```

One more simplification is possible.
For every `Applicative`, `pure f <*> E` is equivalent to `f <$> E`.
In other words, using `seq` to apply a function that was placed into the `Applicative` type using `pure` is overkill, and the function could have just been applied using `Functor.map`.
This simplification yields:

한 가지 더 단순화가 가능합니다. 모든 `Applicative`에 대해 `pure f <*> E`는 `f <$> E`와 동등합니다. 즉, `pure`를 사용하여 `Applicative` type에 배치된 함수를 적용하기 위해 `seq`를 사용하는 것은 과도하며, 함수는 단지 `Functor.map`을 사용하여 적용될 수 있습니다. 이 단순화는 다음을 생성합니다:

```lean
def checkCompany (input : RawInput) :
    Validate (Field × String) LegacyCheckedInput :=
  checkThat (input.birthYear == "FIRM")
    "birth year" "FIRM if a company" *>
  .company <$> checkName input.name
```

The remaining two constructors of `LegacyCheckedInput` use subtypes for their fields.
A general-purpose tool for checking subtypes will make these easier to read:

`LegacyCheckedInput`의 나머지 두 생성자는 해당 필드에 대해 subtype을 사용합니다. subtype을 확인하기 위한 범용 도구는 이들을 더 쉽게 읽을 수 있게 만들 것입니다:

```lean
def checkSubtype {α : Type} (v : α) (p : α → Prop) [Decidable (p v)]
    (err : ε) : Validate ε {x : α // p x} :=
  if h : p v then
    pure ⟨v, h⟩
  else
    .errors { head := err, tail := [] }
```

In the function's argument list, it's important that the type class `[Decidable (p v)]` occur after the specification of the arguments `v` and `p`.
Otherwise, it would refer to an additional set of automatic implicit arguments, rather than to the manually-provided values.
The `Decidable` instance is what allows the proposition `p v` to be checked using `if`.

함수의 인수 목록에서 type class `[Decidable (p v)]`이 인수 `v`와 `p`의 사양 이후에 나타나야 합니다. 그렇지 않으면 수동으로 제공된 값이 아닌 추가 자동 암시적 인수 집합을 참조하게 됩니다. `Decidable` 인스턴스는 명제 `p v`를 `if`를 사용하여 확인할 수 있게 해줍니다.

The two human cases do not need any additional tools:

두 가지 인간 경우는 추가 도구가 필요하지 않습니다:

```lean
def checkHumanBefore1970 (input : RawInput) :
    Validate (Field × String) LegacyCheckedInput :=
  (checkYearIsNat input.birthYear).andThen fun y =>
    .humanBefore1970 <$>
      checkSubtype y (fun x => x > 999 ∧ x < 1970)
        ("birth year", "less than 1970") <*>
      pure input.name

def checkHumanAfter1970 (input : RawInput) :
    Validate (Field × String) LegacyCheckedInput :=
  (checkYearIsNat input.birthYear).andThen fun y =>
    .humanAfter1970 <$>
      checkSubtype y (· > 1970)
        ("birth year", "greater than 1970") <*>
      checkName input.name
```

The validators for the three cases can be combined using `<|>`:

세 가지 경우에 대한 검증자는 `<|>`를 사용하여 결합될 수 있습니다:

```lean
def checkLegacyInput (input : RawInput) :
    Validate (Field × String) LegacyCheckedInput :=
  checkCompany input <|>
  checkHumanBefore1970 input <|>
  checkHumanAfter1970 input
```

The successful cases return constructors of `LegacyCheckedInput`, as expected:

성공한 경우는 예상대로 `LegacyCheckedInput`의 생성자를 반환합니다:

```lean
#eval checkLegacyInput ⟨"Johnny's Troll Groomers", "FIRM"⟩
```

```
Validate.ok (LegacyCheckedInput.company "Johnny's Troll Groomers")
```

```lean
#eval checkLegacyInput ⟨"Johnny", "1963"⟩
```

```
Validate.ok (LegacyCheckedInput.humanBefore1970 1963 "Johnny")
```

```lean
#eval checkLegacyInput ⟨"", "1963"⟩
```

```
Validate.ok (LegacyCheckedInput.humanBefore1970 1963 "")
```

The worst possible input returns all the possible failures:

가장 나쁜 가능한 입력은 모든 가능한 실패를 반환합니다:

```lean
#eval checkLegacyInput ⟨"", "1970"⟩
```

```
Validate.errors
  { head := ("birth year", "FIRM if a company"),
    tail := [("name", "Required"),
             ("birth year", "less than 1970"),
             ("birth year", "greater than 1970"),
             ("name", "Required")] }
```

## 5.4.2. The `Alternative` Class

## 5.4.2. `Alternative` 클래스

Many types support a notion of failure and recovery.
The `Many` monad from the section on [evaluating arithmetic expressions in a variety of monads](../ch04/) is one such type, as is `Option`.
Both support failure without providing a reason (unlike, say, `Except` and `Validate`, which require some indication of what went wrong).

많은 type은 실패와 회복의 개념을 지원합니다. [다양한 monad에서 산술 표현식을 평가하는](../ch04/) 섹션의 `Many` monad는 그러한 type 중 하나이며, `Option`도 마찬가지입니다. 둘 다 이유를 제공하지 않고 실패를 지원합니다 (`Except`와 `Validate`와 달리, 이는 무엇이 잘못되었는지에 대한 표시가 필요합니다).

The `Alternative` class describes applicative functors that have additional operators for failure and recovery:

`Alternative` 클래스는 실패와 회복을 위한 추가 연산자가 있는 applicative functor를 설명합니다:

```lean
class Alternative (f : Type → Type) extends Applicative f where
  failure : f α
  orElse : f α → (Unit → f α) → f α
```

Just as implementors of `Add α` get `HAdd α α α` instances for free, implementors of `Alternative` get `OrElse` instances for free:

`Add α`의 구현자가 `HAdd α α α` 인스턴스를 무료로 얻는 것처럼, `Alternative`의 구현자는 `OrElse` 인스턴스를 무료로 얻습니다:

```lean
instance [Alternative f] : OrElse (f α) where
  orElse := Alternative.orElse
```

The implementation of `Alternative` for `Option` keeps the first non-`none` argument:

`Option`에 대한 `Alternative` 구현은 첫 번째 non-`none` 인수를 유지합니다:

```lean
instance : Alternative Option where
  failure := none
  orElse
    | some x, _ => some x
    | none, y => y ()
```

Similarly, the implementation for `Many` follows the general structure of `Many.union`, with minor differences due to the laziness-inducing `Unit` parameters being placed differently:

마찬가지로, `Many`의 구현은 `Many.union`의 일반 구조를 따릅니다. 지연을 유도하는 `Unit` 매개변수가 다르게 배치되어 있기 때문에 약간의 차이가 있습니다:

```lean
def Many.orElse : Many α → (Unit → Many α) → Many α
  | .none, ys => ys ()
  | .more x xs, ys => .more x (fun () => orElse (xs ()) ys)

instance : Alternative Many where
  failure := .none
  orElse := Many.orElse
```

Like other type classes, `Alternative` enables the definition of a variety of operations that work for *any* applicative functor that implements `Alternative`.
One of the most important is `guard`, which causes `failure` when a decidable proposition is false:

다른 type class와 마찬가지로, `Alternative`는 `Alternative`를 구현하는 *모든* applicative functor에 대해 작동하는 다양한 연산의 정의를 활성화합니다. 가장 중요한 것 중 하나는 decidable 명제가 거짓일 때 `failure`를 발생시키는 `guard`입니다:

```lean
def guard [Alternative f] (p : Prop) [Decidable p] : f Unit :=
  if p then
    pure ()
  else failure
```

It is very useful in monadic programs to terminate execution early.
In `Many`, it can be used to filter out a whole branch of a search, as in the following program that computes all even divisors of a natural number:

monadic 프로그램에서 실행을 조기에 종료하는 것은 매우 유용합니다. `Many`에서, 자연수의 모든 짝수 약수를 계산하는 다음 프로그램과 같이 검색의 전체 분기를 필터링하는 데 사용될 수 있습니다:

```lean
def Many.countdown : Nat → Many Nat
  | 0 => .none
  | n + 1 => .more n (fun () => countdown n)

def evenDivisors (n : Nat) : Many Nat := do
  let k ← Many.countdown (n + 1)
  guard (k % 2 = 0)
  guard (n % k = 0)
  pure k
```

Running it on `20` yields the expected results:

`20`에서 실행하면 예상된 결과를 생성합니다:

```lean
#eval (evenDivisors 20).takeAll
```

```
[20, 10, 4, 2]
```
