---
title: "Ordering Monad Transformers"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Ordering Monad Transformers"
---

# 6.3. Ordering Monad Transformers

When composing a monad from a stack of monad transformers, it's important to be aware that the order in which the monad transformers are layered matters.
Different orderings of the same set of transformers result in different monads.

Monad Transformer 스택에서 Monad를 구성할 때 Monad Transformer가 계층화되는 순서가 중요하다는 것을 인식하는 것이 중요합니다. 동일한 Transformer 집합의 다른 순서는 다른 Monad를 생성합니다.

This version of `countLetters` is just like the previous version, except it uses type classes to describe the set of available effects instead of providing a concrete monad:

이 버전의 `countLetters`는 이전 버전과 동일하지만 구체적인 Monad를 제공하는 대신 타입 클래스를 사용하여 사용 가능한 효과의 집합을 설명합니다:

`def countLetters [Monad m] [MonadState LetterCounts m] [MonadExcept Err m]
(str : String) : m Unit :=
let rec loop (chars : List Char) := do
match chars with
| [] => pure ()
| c :: cs =>
if c.isAlpha then
if vowels.contains c then
modify fun st => {st with vowels := st.vowels + 1}
else if consonants.contains c then
modify fun st => {st with consonants := st.consonants + 1}
else -- modified or non-English letter
pure ()
else throw (.notALetter c)
loop cs
loop str.toList`

The state and exception monad transformers can be combined in two different orders, each resulting in a monad that has instances of both type classes:

상태 및 예외 Monad Transformer는 두 가지 다른 순서로 결합될 수 있으며, 각각 두 타입 클래스의 인스턴스를 가지는 Monad를 생성합니다:

`abbrev M1 := StateT LetterCounts (ExceptT Err Id)
abbrev M2 := ExceptT Err (StateT LetterCounts Id)`

When run on input for which the program does not throw an exception, both monads yield similar results:

프로그램이 예외를 발생시키지 않는 입력에서 실행될 때 두 Monad는 유사한 결과를 산출합니다:

`Except.ok ((), { vowels := 2, consonants := 3 })#eval countLetters (m := M1) "hello" ⟨0, 0⟩`

```
Except.ok ((), { vowels := 2, consonants := 3 })
```

`(Except.ok (), { vowels := 2, consonants := 3 })#eval countLetters (m := M2) "hello" ⟨0, 0⟩`

```
(Except.ok (), { vowels := 2, consonants := 3 })
```

However, there is a subtle difference between these return values.
In the case of `M1`, the outermost constructor is `Except.ok`, and it contains a pair of the unit constructor with the final state.
In the case of `M2`, the outermost constructor is the pair, which contains `Except.ok` applied only to the unit constructor.
The final state is outside of `Except.ok`.
In both cases, the program returns the counts of vowels and consonants.

그러나 이들 반환 값 사이에는 미묘한 차이가 있습니다. `M1`의 경우 가장 바깥쪽 생성자는 `Except.ok`이며 최종 상태와 함께 단위 생성자의 쌍을 포함합니다. `M2`의 경우 가장 바깥쪽 생성자는 단위 생성자에만 적용된 `Except.ok`를 포함하는 쌍입니다. 최종 상태는 `Except.ok` 외부에 있습니다. 두 경우 모두 프로그램은 모음과 자음의 수를 반환합니다.

On the other hand, only one monad yields a count of vowels and consonants when the string causes an exception to be thrown.
Using `M1`, only an exception value is returned:

반면에 문자열이 예외를 발생시킬 때 하나의 Monad만 모음과 자음의 수를 생성합니다. `M1`을 사용하면 예외 값만 반환됩니다:

`Except.error (StEx.Err.notALetter '!')#eval countLetters (m := M1) "hello!" ⟨0, 0⟩`

```
Except.error (StEx.Err.notALetter '!')
```

Using `M2`, the exception value is paired with the state as it was at the time that the exception was thrown:

`M2`를 사용하면 예외 값이 예외가 발생한 시점의 상태와 쌍을 이룹니다:

`(Except.error (StEx.Err.notALetter '!'), { vowels := 2, consonants := 3 })#eval countLetters (m := M2) "hello!" ⟨0, 0⟩`

```
(Except.error (StEx.Err.notALetter '!'), { vowels := 2, consonants := 3 })
```

It might be tempting to think that `M2` is superior to `M1` because it provides more information that might be useful when debugging.
The same program might compute *different* answers in `M1` than it does in `M2`, and there's no principled reason to say that one of these answers is necessarily better than the other.
This can be seen by adding a step to the program that handles exceptions:

`M2`가 디버깅할 때 유용할 수 있는 더 많은 정보를 제공하기 때문에 `M1`보다 우수하다고 생각하기가 쉬울 수 있습니다. 동일한 프로그램은 `M1`에서보다 `M2`에서 *다른* 답을 계산할 수 있으며, 이 중 하나가 다른 하나보다 반드시 더 좋다고 말할 원칙적인 이유가 없습니다. 이는 예외를 처리하는 단계를 프로그램에 추가함으로써 볼 수 있습니다:

`def countWithFallback
[Monad m] [MonadState LetterCounts m] [MonadExcept Err m]
(str : String) : m Unit :=
try
countLetters str
catch _ =>
countLetters "Fallback"`

This program always succeeds, but it might succeed with different results.
If no exception is thrown, then the results are the same as `countLetters`:

이 프로그램은 항상 성공하지만 다른 결과로 성공할 수 있습니다. 예외가 발생하지 않으면 결과는 `countLetters`와 동일합니다:

`Except.ok ((), { vowels := 2, consonants := 3 })#eval countWithFallback (m := M1) "hello" ⟨0, 0⟩`

`(Except.ok (), { vowels := 2, consonants := 3 })#eval countWithFallback (m := M2) "hello" ⟨0, 0⟩`

However, if the exception is thrown and caught, then the final states are very different.
With `M1`, the final state contains only the letter counts from `"Fallback"`:

그러나 예외가 발생하여 포착되면 최종 상태는 매우 다릅니다. `M1`을 사용하면 최종 상태는 `"Fallback"`의 문자 수만 포함합니다:

`Except.ok ((), { vowels := 2, consonants := 6 })#eval countWithFallback (m := M1) "hello!" ⟨0, 0⟩`

```
Except.ok ((), { vowels := 2, consonants := 6 })
```

With `M2`, the final state contains letter counts from both `"hello!"` and from `"Fallback"`, as one would expect in an imperative language:

`(Except.ok (), { vowels := 4, consonants := 9 })#eval countWithFallback (m := M2) "hello!" ⟨0, 0⟩`

```
(Except.ok (), { vowels := 4, consonants := 9 })
```

In `M1`, throwing an exception “rolls back” the state to where the exception was caught.
In `M2`, modifications to the state persist across the throwing and catching of exceptions.
This difference can be seen by unfolding the definitions of `M1` and `M2`.
`M1 α` unfolds to `LetterCounts → Except Err (α × LetterCounts)`, and `M2 α` unfolds to `LetterCounts → Except Err α × LetterCounts`.
That is to say, `M1 α` describes functions that take an initial letter count, returning either an error or an `α` paired with updated counts.
When an exception is thrown in `M1`, there is no final state.
`M2 α` describes functions that take an initial letter count and return a new letter count paired with either an error or an `α`.
When an exception is thrown in `M2`, it is accompanied by a state.

## 6.3.1. Commuting Monads

In the jargon of functional programming, two monad transformers are said to *commute* if they can be re-ordered without the meaning of the program changing.
The fact that the result of the program can differ when `StateT` and `ExceptT` are reordered means that state and exceptions do not commute.
In general, monad transformers should not be expected to commute.

Even though not all monad transformers commute, some do.
For example, two uses of `StateT` can be re-ordered.
Expanding the definitions in `StateT σ (StateT σ' Id) α` yields the type `σ → σ' → ((α × σ) × σ')`, and `StateT σ' (StateT σ Id) α` yields `σ' → σ → ((α × σ') × σ)`.
In other words, the differences between them are that they nest the `σ` and `σ'` types in different places in the return type, and they accept their arguments in a different order.
Any client code will still need to provide the same inputs, and it will still receive the same outputs.

Most programming languages that have both mutable state and exceptions work like `M2`.
In those languages, state that *should* be rolled back when an exception is thrown is difficult to express, and it usually needs to be simulated in a manner that looks much like the passing of explicit state values in `M1`.
Monad transformers grant the freedom to choose an interpretation of effect ordering that works for the problem at hand, with both choices being equally easy to program with.
However, they also require care to be taken in the choice of ordering of transformers.
With great expressive power comes the responsibility to check that what's being expressed is what is intended, and the type signature of `countWithFallback` is probably more polymorphic than it should be.

## 6.3.2. Exercises

* Check that `ReaderT` and `StateT` commute by expanding their definitions and reasoning about the resulting types.
* Do `ReaderT` and `ExceptT` commute? Check your answer by expanding their definitions and reasoning about the resulting types.
* Construct a monad transformer `ManyT` based on the definition of `Many`, with a suitable `Alternative` instance. Check that it satisfies the `Monad` contract.
* Does `ManyT` commute with `StateT`? If so, check your answer by expanding definitions and reasoning about the resulting types. If not, write a program in `ManyT (StateT σ Id)` and a program in `StateT σ (ManyT Id)`. Each program should be one that makes more sense for the given ordering of monad transformers.
