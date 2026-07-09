---
title: "More do Features"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "More do Features"
---

# 6.4. More do Features

Lean's `do`-notation provides a syntax for writing programs with monads that resembles imperative programming languages.
In addition to providing a convenient syntax for programs with monads, `do`-notation provides syntax for using certain monad transformers.

Lean의 `do` 표기법은 명령형 프로그래밍 언어와 유사한 Monad를 사용한 프로그램 작성을 위한 문법을 제공합니다. Monad를 사용한 프로그램에 대한 편리한 문법을 제공하는 것 외에도 `do` 표기법은 특정 Monad Transformer를 사용하기 위한 문법을 제공합니다.

## 6.4.1. Single-Branched `if`

When working in a monad, a common pattern is to carry out a side effect only if some condition is true.
For instance, `countLetters` contains a check for vowels or consonants, and letters that are neither have no effect on the state.
This is captured by having the `else` branch evaluate to `pure ()`, which has no effects:

Monad에서 작업할 때 일반적인 패턴은 어떤 조건이 참인 경우에만 부작용을 수행하는 것입니다. 예를 들어 `countLetters`는 모음 또는 자음을 확인하며 둘 다 아닌 문자는 상태에 영향을 주지 않습니다. 이는 `else` 분기가 효과가 없는 `pure ()`로 평가되도록 함으로써 캡처됩니다:

`def countLetters (str : String) : StateT LetterCounts (Except Err) Unit :=
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

When an `if` is a statement in a `do`-block, rather than being an expression, then `else pure ()` can simply be omitted, and Lean inserts it automatically.
The following definition of `countLetters` is completely equivalent:

`if`가 표현이 아닌 `do` 블록의 명령문일 때 `else pure ()`를 단순히 생략할 수 있으며 Lean은 자동으로 삽입합니다. 다음 `countLetters`의 정의는 완전히 동등합니다:

`def countLetters (str : String) : StateT LetterCounts (Except Err) Unit :=
let rec loop (chars : List Char) := do
match chars with
| [] => pure ()
| c :: cs =>
if c.isAlpha then
if vowels.contains c then
modify fun st => {st with vowels := st.vowels + 1}
else if consonants.contains c then
modify fun st => {st with consonants := st.consonants + 1}
else throw (.notALetter c)
loop cs
loop str.toList`

A program that uses a state monad to count the entries in a list that satisfy some monadic check can be written as follows:

상태 Monad를 사용하여 어떤 Monadic 확인을 만족하는 목록의 항목을 세는 프로그램은 다음과 같이 작성할 수 있습니다:

`def count [Monad m] [MonadState Nat m] (p : α → m Bool) : List α → m Unit
| [] => pure ()
| x :: xs => do
if ← p x then
modify (· + 1)
count p xs`

Similarly, `if not E1 then STMT...` can instead be written `unless E1 do STMT...`.
The converse of `count` that counts entries that don't satisfy the monadic check can be written by replacing `if` with `unless`:

유사하게 `if not E1 then STMT...`는 대신 `unless E1 do STMT...`로 작성할 수 있습니다. Monadic 확인을 만족하지 않는 항목을 세는 `count`의 역함수는 `if`를 `unless`로 바꿔서 작성할 수 있습니다:

`def countNot [Monad m] [MonadState Nat m] (p : α → m Bool) : List α → m Unit
| [] => pure ()
| x :: xs => do
unless ← p x do
modify (· + 1)
countNot p xs`

Understanding single-branched `if` and `unless` does not require thinking about monad transformers.
They simply replace the missing branch with `pure ()`.
The remaining extensions in this section, however, require Lean to automatically rewrite the `do`-block to add a local transformer on top of the monad that the `do`-block is written in.

단일 분기 `if` 및 `unless`를 이해하려면 Monad Transformer를 고려할 필요가 없습니다. 단순히 누락된 분기를 `pure ()`로 대체합니다. 그러나 이 섹션의 나머지 확장은 Lean이 `do` 블록이 작성된 Monad의 최상단에 로컬 Transformer를 추가하도록 `do` 블록을 자동으로 다시 작성해야 합니다.

## 6.4.2. Early Return

The standard library contains a function `List.find?` that returns the first entry in a list that satisfies some check.
A simple implementation that doesn't make use of the fact that `Option` is a monad loops over the list using a recursive function, with an `if` to stop the loop when the desired entry is found:

표준 라이브러리는 목록의 확인을 만족하는 첫 번째 항목을 반환하는 `List.find?` 함수를 포함합니다. `Option`이 Monad라는 사실을 사용하지 않는 간단한 구현은 재귀 함수를 사용하여 목록을 반복하며, 원하는 항목을 찾았을 때 루프를 중단하기 위한 `if`를 사용합니다:

`def List.find? (p : α → Bool) : List α → Option α
| [] => none
| x :: xs =>
if p x then
some x
else
find? p xs`

Imperative languages typically sport the `return` keyword that aborts the execution of a function, immediately returning some value to the caller.
In Lean, this is available in `do`-notation, and `return` halts the execution of a `do`-block, with `return`'s argument being the value returned from the monad.
In other words, `List.find?` could have been written like this:

`def List.find? (p : α → Bool) : List α → Option α
| [] => failure
| x :: xs => do
if p x then return x
find? p xs`

Early return in imperative languages is a bit like an exception that can only cause the current stack frame to be unwound.
Both early return and exceptions terminate execution of a block of code, effectively replacing the surrounding code with the thrown value.
Behind the scenes, early return in Lean is implemented using a version of `ExceptT`.
Each `do`-block that uses early return is wrapped in an exception handler (in the sense of the function `tryCatch`).
Early returns are translated to throwing the value as an exception, and the handlers catch the thrown value and return it immediately.
In other words, the `do`-block's original return value type is also used as the exception type.

Making this more concrete, the helper function `runCatch` strips a layer of `ExceptT` from the top of a monad transformer stack when the exception type and return type are the same:

`def runCatch [Monad m] (action : ExceptT α m α) : m α := do
match ← action with
| Except.ok x => pure x
| Except.error x => pure x`

The `do`-block in `List.find?` that uses early return is translated to a `do`-block that does not use early return by wrapping it in a use of `runCatch`, and replacing early returns with `throw`:

`def List.find? (p : α → Bool) : List α → Option α
| [] => failure
| x :: xs =>
runCatch do
if p x then throw x else pure ()
monadLift (find? p xs)`

Another situation in which early return is useful is command-line applications that terminate early if the arguments or input are incorrect.
Many programs begin with a section that validates arguments and inputs before proceeding to the main body of the program.
The following version of [the greeting program `hello-name`](../ch02/) checks that no command-line arguments were provided:

`def main (argv : List String) : IO UInt32 := do
let stdin ← IO.getStdin
let stdout ← IO.getStdout
let stderr ← IO.getStderr
unless argv == [] do
stderr.putStrLn s!"Expected no arguments, but got {argv.length}"
return 1
stdout.putStrLn "How would you like to be addressed?"
stdout.flush
let name := (← stdin.getLine).trim
if name == "" then
stderr.putStrLn s!"No name provided"
return 1
stdout.putStrLn s!"Hello, {name}!"
return 0`

Running it with no arguments and typing the name `David` yields the same result as the previous version:

`lean --run EarlyReturn.lean``How would you like to be addressed?
David
Hello, David!`

Providing the name as a command-line argument instead of an answer causes an error:

`lean --run EarlyReturn.lean David``Expected no arguments, but got 1`

And providing no name causes the other error:

`lean --run EarlyReturn.lean``How would you like to be addressed?
No name provided`

The program that uses early return avoids needing to nest the control flow, as is done in this version that does not use early return:

`def main (argv : List String) : IO UInt32 := do
let stdin ← IO.getStdin
let stdout ← IO.getStdout
let stderr ← IO.getStderr
if argv != [] then
stderr.putStrLn s!"Expected no arguments, but got {argv.length}"
pure 1
else
stdout.putStrLn "How would you like to be addressed?"
stdout.flush
let name := (← stdin.getLine).trim
if name == "" then
stderr.putStrLn s!"No name provided"
pure 1
else
stdout.putStrLn s!"Hello, {name}!"
pure 0`

One important difference between early return in Lean and early return in imperative languages is that Lean's early return applies only to the current `do`-block.
When the entire definition of a function is in the same `do` block, this difference doesn't matter.
But if `do` occurs underneath some other structures, then the difference becomes apparent.
For example, given the following definition of `greet`:

`def greet (name : String) : String :=
"Hello, " ++ Id.run do return name`

the expression `greet "David"` evaluates to `"Hello, David"`, not just `"David"`.

## 6.4.3. Loops

Just as every program with mutable state can be rewritten to a program that passes the state as arguments, every loop can be rewritten as a recursive function.
From one perspective, `List.find?` is most clear as a recursive function.
After all, its definition mirrors the structure of the list: if the head passes the check, then it should be returned; otherwise look in the tail.
When no more entries remain, the answer is `none`.
From another perspective, `List.find?` is most clear as a loop.
After all, the program consults the entries in order until a satisfactory one is found, at which point it terminates.
If the loop terminates without having returned, the answer is `none`.

### 6.4.3.1. Looping with ForM

Lean includes a type class that describes looping over a container type in some monad.
This class is called `ForM`:

`class ForM (m : Type u → Type v) (γ : Type w₁)
(α : outParam (Type w₂)) where
forM [Monad m] : γ → (α → m PUnit) → m PUnit`

This class is quite general.
The parameter `m` is a monad with some desired effects, `γ` is the collection to be looped over, and `α` is the type of elements from the collection.
Typically, `m` is allowed to be any monad, but it is possible to have a data structure that e.g. only supports looping in `IO`.
The method `forM` takes a collection, a monadic action to be run for its effects on each element from the collection, and is then responsible for running the actions.

The instance for `List` allows `m` to be any monad, it sets `γ` to be `List α`, and sets the class's `α` to be the same `α` found in the list:

`def List.forM [Monad m] : List α → (α → m PUnit) → m PUnit
| [], _ => pure ()
| x :: xs, action => do
action x
forM xs action
instance : ForM m (List α) α where
forM := List.forM`

The [function `doList` from `doug`](Monad-Transformers/Combining-IO-and-Reader/#reader-io-implementation) is `forM` for lists.
Because `forM` is intended to be used in `do`-blocks, it uses `Monad` rather than `Applicative`.
`forM` can be used to make `countLetters` much shorter:

`def countLetters (str : String) : StateT LetterCounts (Except Err) Unit :=
forM str.toList fun c => do
if c.isAlpha then
if vowels.contains c then
modify fun st => {st with vowels := st.vowels + 1}
else if consonants.contains c then
modify fun st => {st with consonants := st.consonants + 1}
else throw (.notALetter c)`

The instance for `Many` is very similar:

`def Many.forM [Monad m] : Many α → (α → m PUnit) → m PUnit
| Many.none, _ => pure ()
| Many.more first rest, action => do
action first
forM (rest ()) action
instance : ForM m (Many α) α where
forM := Many.forM`

Because `γ` can be any type at all, `ForM` can support non-polymorphic collections.
A very simple collection is one of the natural numbers less than some given number, in reverse order:

`structure AllLessThan where
num : Nat`

Its `ForM` operator applies the provided action to each smaller `Nat`:

`def AllLessThan.forM [Monad m]
(coll : AllLessThan) (action : Nat → m Unit) :
m Unit :=
let rec countdown : Nat → m Unit
| 0 => pure ()
| n + 1 => do
action n
countdown n
countdown coll.num
instance : ForM m AllLessThan Nat where
forM := AllLessThan.forM`

Running `IO.println` on each number less than five can be accomplished with `ForM`:

`4
3
2
1
0
#eval forM { num := 5 : AllLessThan } IO.println`

```
4
3
2
1
0
```

An example `ForM` instance that works only in a particular monad is one that loops over the lines read from an IO stream, such as standard input:

`structure LinesOf where
stream : IO.FS.Stream
partial def LinesOf.forM
(readFrom : LinesOf) (action : String → IO Unit) :
IO Unit := do
let line ← readFrom.stream.getLine
if line == "" then return ()
action line
forM readFrom action
instance : ForM IO LinesOf String where
forM := LinesOf.forM`

The definition of `ForM` is marked `partial` because there is no guarantee that the stream is finite.
In this case, `IO.FS.Stream.getLine` works only in the `IO` monad, so no other monad can be used for looping.

This example program uses this looping construct to filter out lines that don't contain letters:

`def main (argv : List String) : IO UInt32 := do
if argv != [] then
IO.eprintln "Unexpected arguments"
return 1
forM (LinesOf.mk (← IO.getStdin)) fun line => do
if line.any (·.isAlpha) then
IO.print line
return 0`

The file `test-data` contains:

File: `test-data``Hello!``!!!!!``12345``abc123``Ok`

Invoking this program, which is stored in `ForMIO.lean`, yields the following output:

`lean --run ForMIO.lean < test-data``Hello!
abc123
Ok`

### 6.4.3.2. Stopping Iteration

Terminating a loop early is difficult to do with `ForM`.
Writing a function that iterates over the `Nat`s in an `AllLessThan` only until `3` is reached requires a means of stopping the loop partway through.
One way to achieve this is to use `ForM` with the `OptionT` monad transformer.
The first step is to define `OptionT.exec`, which discards information about both the return value and whether or not the transformed computation succeeded:

`def OptionT.exec [Applicative m] (action : OptionT m α) : m Unit :=
action *> pure ()`

Then, failure in the `OptionT` instance of `Alternative` can be used to terminate looping early:

`def countToThree (n : Nat) : IO Unit :=
let nums : AllLessThan := ⟨n⟩
OptionT.exec (forM nums fun i => do
if i < 3 then failure else IO.println i)`

A quick test demonstrates that this solution works:

`6
5
4
3
#eval countToThree 7`

```
6
5
4
3
```

However, this code is not so easy to read.
Terminating a loop early is a common task, and Lean provides more syntactic sugar to make this easier.
This same function can also be written as follows:

`def countToThree (n : Nat) : IO Unit := do
let nums : AllLessThan := ⟨n⟩
for i in nums do
if i < 3 then break
IO.println i`

Testing it reveals that it works just like the prior version:

The `for``...``in``...``do` `...` syntax desugars to the use of a type class called `ForIn`, which is a somewhat more complicated version of `ForM` that keeps track of state and early termination.
The standard library provides an adapter that converts a `ForM` instance into a `ForIn` instance, called `ForM.forIn`.
To enable `for` loops based on a `ForM` instance, add something like the following, with appropriate replacements for `AllLessThan` and `Nat`:

`instance : ForIn m AllLessThan Nat where
forIn := ForM.forIn`

Note, however, that this adapter only works for `ForM` instances that keep the monad unconstrained, as most of them do.
This is because the adapter uses `StateT` and `ExceptT`, rather than the underlying monad.

Early return is supported in `for` loops.
The translation of `do` blocks with early return into a use of an exception monad transformer applies equally well underneath `ForM` as the earlier use of `OptionT` to halt iteration does.
This version of `List.find?` makes use of both:

`def List.find? (p : α → Bool) (xs : List α) : Option α := do
for x in xs do
if p x then return x
failure`

In addition to `break`, `for` loops support `continue` to skip the rest of the loop body in an iteration.
An alternative (but confusing) formulation of `List.find?` skips elements that don't satisfy the check:

`def List.find? (p : α → Bool) (xs : List α) : Option α := do
for x in xs do
if not (p x) then continue
return x
failure`

A `Std.Range` is a structure that consists of a starting number, an ending number, and a step.
They represent a sequence of natural numbers, from the starting number to the ending number, increasing by the step each time.
Lean has special syntax to construct ranges, consisting of square brackets, numbers, and colons that comes in four varieties.
The stopping point must always be provided, while the start and the step are optional, defaulting to `0` and `1`, respectively:

| Expression | Start | Stop | Step | As List |
| --- | --- | --- | --- | --- |
| `[:10]` | `0` | `10` | `1` | `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]` |
| `[2:10]` | `2` | `10` | `1` | `[2, 3, 4, 5, 6, 7, 8, 9]` |
| `[:10:3]` | `0` | `10` | `3` | `[0, 3, 6, 9]` |
| `[2:10:3]` | `2` | `10` | `3` | `[2, 5, 8]` |

Note that the starting number *is* included in the range, while the stopping numbers is not.
All three arguments are `Nat`s, which means that ranges cannot count down—a range where the starting number is greater than or equal to the stopping number simply contains no numbers.

Ranges can be used with `for` loops to draw numbers from the range.
This program counts even numbers from four to eight:

`def fourToEight : IO Unit := do
for i in [4:9:2] do
IO.println i`

Running it yields:

```
4
6
8
```

Finally, `for` loops support iterating over multiple collections in parallel, by separating the `in` clauses with commas.
Looping halts when the first collection runs out of elements, so the declaration:

`def parallelLoop := do
for x in ["currant", "gooseberry", "rowan"], y in [4:8] do
IO.println (x, y)`

produces three lines of output:

`(currant, 4)
(gooseberry, 5)
(rowan, 6)
#eval parallelLoop`

```
(currant, 4)
(gooseberry, 5)
(rowan, 6)
```

Many data structures implement an enhanced version of the `ForIn` type class that adds evidence that the element was drawn from the collection to the loop body.
These can be used by providing a name for the evidence prior to the name of the element.
This function prints all the elements of an array together with their indices, and the compiler is able to determine that the array lookups are all safe due to the evidence `h`:

`def printArray [ToString α] (xs : Array α) : IO Unit := do
for h : i in [0:xs.size] do
IO.println s!"{i}:\t{xs[i]}"`

In this example, `h` is evidence that `i ∈ [0:xs.size]`, and the tactic that checks whether `xs[i]` is safe is able to transform this into evidence that `i < xs.size`.

## 6.4.4. Mutable Variables

In addition to early `return`, `else`-less `if`, and `for` loops, Lean supports local mutable variables within a `do` block.
Behind the scenes, these mutable variables desugar to code that's equivalent to `StateT`, rather than being implemented by true mutable variables.
Once again, functional programming is used to simulate imperative programming.

A local mutable variable is introduced with `let mut` instead of plain `let`.
The definition `two`, which uses the identity monad `Id` to enable `do`-syntax without introducing any effects, counts to `2`:

`def two : Nat := Id.run do
let mut x := 0
x := x + 1
x := x + 1
return x`

This code is equivalent to a definition that uses `StateT` to add `1` twice:

`def two : Nat :=
let block : StateT Nat Id Nat := do
modify (· + 1)
modify (· + 1)
return (← get)
let (result, _finalState) := block 0
result`

Local mutable variables work well with all the other features of `do`-notation that provide convenient syntax for monad transformers.
The definition `three` counts the number of entries in a three-entry list:

`def three : Nat := Id.run do
let mut x := 0
for _ in [1, 2, 3] do
x := x + 1
return x`

Similarly, `six` adds the entries in a list:

`def six : Nat := Id.run do
let mut x := 0
for y in [1, 2, 3] do
x := x + y
return x`

`List.count` counts the number of entries in a list that satisfy some check:

`def List.count (p : α → Bool) (xs : List α) : Nat := Id.run do
let mut found := 0
for x in xs do
if p x then found := found + 1
return found`

Local mutable variables can be more convenient to use and easier to read than an explicit local use of `StateT`.
However, they don't have the full power of unrestricted mutable variables from imperative languages.
In particular, they can only be modified in the `do`-block in which they are introduced.
This means, for instance, that `for`-loops can't be replaced by otherwise-equivalent recursive helper functions.
This version of `List.count`:

`` def List.count (p : α → Bool) (xs : List α) : Nat := Id.run do
let mut found := 0
let rec go : List α → Id Unit
| [] => pure ()
| y :: ys => do
if p y then `found` cannot be mutated, only variables declared using `let mut` can be mutated. If you did not intend to mutate but define `found`, consider using `let found` insteadfound := found + 1
go ys
return found ``

yields the following error on the attempted mutation of `found`:

```
`found` cannot be mutated, only variables declared using `let mut` can be mutated. If you did not intend to mutate but define `found`, consider using `let found` instead
```

This is because the recursive function is written in the identity monad, and only the monad of the `do`-block in which the variable is introduced is transformed with `StateT`.

## 6.4.5. What counts as a `do` block?

Many features of `do`-notation apply only to a single `do`-block.
Early return terminates the current block, and mutable variables can only be mutated in the block that they are defined in.
To use them effectively, it's important to know what counts as “the same block”.

Generally speaking, the indented block following the `do` keyword counts as a block, and the immediate sequence of statements underneath it are part of that block.
Statements in independent blocks that are nonetheless contained in a block are not considered part of the block.
However, the rules that govern what exactly counts as the same block are slightly subtle, so some examples are in order.
The precise nature of the rules can be tested by setting up a program with a mutable variable and seeing where the mutation is allowed.
This program has a mutation that is clearly in the same block as the mutable variable:

`example : Id Unit := do
let mut x := 0
x := x + 1`

When a mutation occurs in a `do`-block that is part of a `let`-statement that defines a name using `:=`, then it is not considered to be part of the block:

`` example : Id Unit := do
let mut x := 0
let other := do
`x` cannot be mutated, only variables declared using `let mut` can be mutated. If you did not intend to mutate but define `x`, consider using `let x` insteadx := x + 1
other ``

```
`x` cannot be mutated, only variables declared using `let mut` can be mutated. If you did not intend to mutate but define `x`, consider using `let x` instead
```

However, a `do`-block that occurs under a `let`-statement that defines a name using `←` is considered part of the surrounding block.
The following program is accepted:

`example : Id Unit := do
let mut x := 0
let other ← do
x := x + 1
pure other`

Similarly, `do`-blocks that occur as arguments to functions are independent of their surrounding blocks.
The following program is not accepted:

`` example : Id Unit := do
let mut x := 0
let addFour (y : Id Nat) := Id.run y + 4
addFour do
`x` cannot be mutated, only variables declared using `let mut` can be mutated. If you did not intend to mutate but define `x`, consider using `let x` insteadx := 5 ``

If the `do` keyword is completely redundant, then it does not introduce a new block.
This program is accepted, and is equivalent to the first one in this section:

`example : Id Unit := do
let mut x := 0
do x := x + 1`

The contents of branches under a `do` (such as those introduced by `match` or `if`) are considered to be part of the surrounding block, whether or not a redundant `do` is added.
The following programs are all accepted:

`example : Id Unit := do
let mut x := 0
if x > 2 then
x := x + 1``example : Id Unit := do
let mut x := 0
if x > 2 then do
x := x + 1``example : Id Unit := do
let mut x := 0
match true with
| true => x := x + 1
| false => x := 17``example : Id Unit := do
let mut x := 0
match true with
| true => do
x := x + 1
| false => do
x := 17`

Similarly, the `do` that occurs as part of the `for` and `unless` syntax is just part of their syntax, and does not introduce a fresh `do`-block.
These programs are also accepted:

`example : Id Unit := do
let mut x := 0
for y in [1:5] do
x := x + y``example : Id Unit := do
let mut x := 0
unless 1 < 5 do
x := x + 1`

## 6.4.6. Imperative or Functional Programming?

The imperative features provided by Lean's `do`-notation allow many programs to very closely resemble their counterparts in languages like Rust, Java, or C#.
This resemblance is very convenient when translating an imperative algorithm into Lean, and some tasks are just most naturally thought of imperatively.
The introduction of monads and monad transformers enables imperative programs to be written in purely functional languages, and `do`-notation as a specialized syntax for monads (potentially locally transformed) allows functional programmers to have the best of both worlds: the strong reasoning principles afforded by immutability and a tight control over available effects through the type system are combined with syntax and libraries that allow programs that use effects to look familiar and be easy to read.
Monads and monad transformers allow functional versus imperative programming to be a matter of perspective.

## 6.4.7. Exercises

* Rewrite `doug` to use `for` instead of the `doList` function.
* Are there other opportunities to use the features introduced in this section to improve the code? If so, use them!
