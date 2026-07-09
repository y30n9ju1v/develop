---
title: "Worked Example: cat"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Worked Example: cat"
---

# Worked Example: cat

Now that the basic skeleton of the program has been built, it's time to actually enter the code.
A proper implementation of `cat` can be used with infinite IO streams, such as `/dev/random`, which means that it can't read its input into memory before outputting it.
Furthermore, it should not work one character at a time, as this leads to frustratingly slow performance.
Instead, it's better to read contiguous blocks of data all at once, directing the data to the standard output one block at a time.

이제 프로그램의 기본 구조가 구축되었으므로 실제 코드를 입력할 차례입니다.
`cat`의 적절한 구현은 `/dev/random`과 같은 무한 IO 스트림과 함께 사용될 수 있으므로, 출력하기 전에 입력을 메모리에 읽을 수 없습니다.
또한 한 번에 한 문자씩 작동해서는 안 됩니다. 이는 답답할 정도로 느린 성능을 유도하기 때문입니다.
대신 한 번에 연속된 데이터 블록을 읽은 후 표준 출력으로 한 번에 한 블록씩 데이터를 보내는 것이 더 좋습니다.

The first step is to decide how big of a block to read.
For the sake of simplicity, this implementation uses a conservative 20 kilobyte block.
`USize` is analogous to `size_t` in C—it's an unsigned integer type that is big enough to represent all valid array sizes.

첫 번째 단계는 읽을 블록의 크기를 결정하는 것입니다.
단순함을 위해 이 구현은 보수적인 20 킬로바이트 블록을 사용합니다.
`USize`는 C의 `size_t`와 유사합니다. 모든 유효한 배열 크기를 나타낼 수 있을 정도로 큰 부호 없는 정수 타입입니다.

### 2.4.2.1. Streams

The main work of `feline` is done by `dump`, which reads input one block at a time, dumping the result to standard output, until the end of the input has been reached.
The end of the input is indicated by `read` returning an empty byte array:

`feline`의 주요 작업은 `dump`에 의해 수행되며, 이는 입력의 끝에 도달할 때까지 한 번에 한 블록씩 입력을 읽고 결과를 표준 출력으로 출력합니다.
입력의 끝은 `read`가 빈 바이트 배열을 반환함으로써 표시됩니다:

`partial def dump (stream : IO.FS.Stream) : IO Unit := do
let buf ← stream.read bufsize
if buf.isEmpty then
pure ()
else
let stdout ← IO.getStdout
stdout.write buf
dump stream`

The `dump` function is declared `partial`, because it calls itself recursively on input that is not immediately smaller than an argument.
When a function is declared to be partial, Lean does not require a proof that it terminates.
On the other hand, partial functions are also much less amenable to proofs of correctness, because allowing infinite loops in Lean's logic would make it unsound.
However, there is no way to prove that `dump` terminates, because infinite input (such as from `/dev/random`) would mean that it does not, in fact, terminate.
In cases like this, there is no alternative to declaring the function `partial`.

`dump` 함수는 `partial`로 선언됩니다. 왜냐하면 인수보다 즉시 작지 않은 입력에서 자기 자신을 재귀적으로 호출하기 때문입니다.
함수가 partial로 선언될 때, Lean은 그것이 종료한다는 증명을 요구하지 않습니다.
반면에 partial 함수는 또한 정확성의 증명에 훨씬 덜 적합합니다. 왜냐하면 Lean의 논리에서 무한 루프를 허용하면 건전성이 떨어지기 때문입니다.
그러나 `dump`가 종료한다는 것을 증명할 방법이 없습니다. 무한 입력(예: `/dev/random`에서)이 실제로 종료하지 않음을 의미하기 때문입니다.
이와 같은 경우, 함수를 `partial`로 선언하는 것 외에 다른 방법이 없습니다.

The type `IO.FS.Stream` represents a POSIX stream.
Behind the scenes, it is represented as a structure that has one field for each POSIX stream operation.
Each operation is represented as an IO action that provides the corresponding operation:

`IO.FS.Stream` 타입은 POSIX 스트림을 나타냅니다.
내부적으로 각 POSIX 스트림 작업마다 하나의 필드를 가진 구조로 표현됩니다.
각 작업은 해당 작업을 제공하는 IO 액션으로 표현됩니다:

`structure Stream where
flush : IO Unit
read : USize → IO ByteArray
write : ByteArray → IO Unit
getLine : IO String
putStr : String → IO Unit
isTty : BaseIO Bool`

The type `BaseIO` is a variant of `IO` that rules out run-time errors.
The Lean compiler contains `IO` actions (such as `IO.getStdout`, which is called in `dump`) to get streams that represent standard input, standard output, and standard error.
These are `IO` actions rather than ordinary definitions because Lean allows these standard POSIX streams to be replaced in a process, which makes it easier to do things like capturing the output from a program into a string by writing a custom `IO.FS.Stream`.

`BaseIO` 타입은 실행 시간 오류를 제외하는 `IO`의 변형입니다.
Lean 컴파일러는 표준 입력, 표준 출력, 표준 오류를 나타내는 스트림을 얻기 위한 `IO` 액션(예: `dump`에서 호출되는 `IO.getStdout`)을 포함합니다.
이들은 일반 정의가 아니라 `IO` 액션입니다. Lean이 프로세스에서 이러한 표준 POSIX 스트림을 바꿀 수 있게 하기 때문입니다. 이는 사용자 정의 `IO.FS.Stream`을 작성하여 프로그램의 출력을 문자열로 캡처하는 것과 같은 작업을 더 쉽게 만듭니다.

The control flow in `dump` is essentially a `while` loop.
When `dump` is called, if the stream has reached the end of the file, `pure ()` terminates the function by returning the constructor for `Unit`.
If the stream has not yet reached the end of the file, one block is read, and its contents are written to `stdout`, after which `dump` calls itself directly.
The recursive calls continue until `stream.read` returns an empty byte array, which indicates the end of the file.

`dump`의 제어 흐름은 본질적으로 `while` 루프입니다.
`dump`가 호출되었을 때, 스트림이 파일의 끝에 도달하면 `pure ()`는 `Unit`의 생성자를 반환하여 함수를 종료합니다.
스트림이 아직 파일의 끝에 도달하지 않았다면, 한 블록을 읽고 그 내용을 `stdout`에 기록한 후 `dump`가 자신을 직접 호출합니다.
재귀 호출은 `stream.read`가 파일의 끝을 나타내는 빈 바이트 배열을 반환할 때까지 계속됩니다.

When an `if` expression occurs as a statement in a `do`, as in `dump`, each branch of the `if` is implicitly provided with a `do`.
In other words, the sequence of steps following the `else` are treated as a sequence of `IO` actions to be executed, just as if they had a `do` at the beginning.
Names introduced with `let` in the branches of the `if` are visible only in their own branches, and are not in scope outside of the `if`.

`dump`와 같이 `if` 표현식이 `do`의 명령문으로 나타날 때, `if`의 각 분기는 암시적으로 `do`가 제공됩니다.
즉, `else` 다음의 단계 시퀀스는 시작 부분에 `do`가 있었던 것처럼, 실행할 `IO` 액션의 시퀀스로 취급됩니다.
`if`의 분기에서 `let`으로 도입된 이름은 자신의 분기에서만 보이며, `if` 외부에서는 범위에 없습니다.

There is no danger of running out of stack space while calling `dump` because the recursive call happens as the very last step in the function, and its result is returned directly rather than being manipulated or computed with.
This kind of recursion is called *tail recursion*, and it is described in more detail [later in this book](Programming___-Proving___-and-Performance/Tail-Recursion/#tail-recursion).
Because the compiled code does not need to retain any state, the Lean compiler can compile the recursive call to a jump.

`dump`를 호출하는 동안 스택 공간이 부족할 위험이 없습니다. 왜냐하면 재귀 호출이 함수의 마지막 단계로 발생하고 그 결과가 조작되거나 계산되지 않고 직접 반환되기 때문입니다.
이러한 종류의 재귀를 *꼬리 재귀(tail recursion)*라고 하며, [이 책의 뒷부분](Programming___-Proving___-and-Performance/Tail-Recursion/#tail-recursion)에서 더 자세히 설명됩니다.
컴파일된 코드가 상태를 유지할 필요가 없기 때문에 Lean 컴파일러는 재귀 호출을 점프로 컴파일할 수 있습니다.

If `feline` only redirected standard input to standard output, then `dump` would be sufficient.
However, it also needs to be able to open files that are provided as command-line arguments and emit their contents.
When its argument is the name of a file that exists, `fileStream` returns a stream that reads the file's contents.
When the argument is not a file, `fileStream` emits an error and returns `none`.

`feline`이 표준 입력을 표준 출력으로만 리다이렉트한다면 `dump`로 충분할 것입니다.
그러나 명령줄 인수로 제공되는 파일을 열고 그 내용을 출력할 수도 있어야 합니다.
인수가 존재하는 파일의 이름이면 `fileStream`은 파일의 내용을 읽는 스트림을 반환합니다.
인수가 파일이 아니면 `fileStream`은 오류를 내보내고 `none`을 반환합니다.

`def fileStream (filename : System.FilePath) : IO (Option IO.FS.Stream) := do
let fileExists ← filename.pathExists
if not fileExists then
let stderr ← IO.getStderr
stderr.putStrLn s!"File not found: {filename}"
pure none
else
let handle ← IO.FS.Handle.mk filename IO.FS.Mode.read
pure (some (IO.FS.Stream.ofHandle handle))`

Opening a file as a stream takes two steps.
First, a file handle is created by opening the file in read mode.
A Lean file handle tracks an underlying file descriptor.
When there are no references to the file handle value, a finalizer closes the file descriptor.
Second, the file handle is given the same interface as a POSIX stream using `IO.FS.Stream.ofHandle`, which fills each field of the `Stream` structure with the corresponding `IO` action that works on file handles.

파일을 스트림으로 열기는 두 단계를 거칩니다.
먼저 파일을 읽기 모드로 열어 파일 핸들을 생성합니다.
Lean 파일 핸들은 기본 파일 디스크립터를 추적합니다.
파일 핸들 값에 대한 참조가 없으면 종료자가 파일 디스크립터를 닫습니다.
둘째, `IO.FS.Stream.ofHandle`을 사용하여 파일 핸들에 POSIX 스트림과 동일한 인터페이스를 제공합니다. 이는 `Stream` 구조의 각 필드를 파일 핸들에서 작동하는 해당 `IO` 액션으로 채웁니다.

### 2.4.2.2. Handling Input

The main loop of `feline` is another tail-recursive function, called `process`.
In order to return a non-zero exit code if any of the inputs could not be read, `process` takes an argument `exitCode` that represents the current exit code for the whole program.
Additionally, it takes a list of input files to be processed.

`feline`의 주 루프는 `process`라고 불리는 또 다른 꼬리 재귀 함수입니다.
입력 중 하나라도 읽을 수 없으면 0이 아닌 종료 코드를 반환하기 위해, `process`는 전체 프로그램의 현재 종료 코드를 나타내는 `exitCode` 인수를 받습니다.
또한 처리할 입력 파일의 리스트를 받습니다.

`def process (exitCode : UInt32) (args : List String) : IO UInt32 := do
match args with
| [] => pure exitCode
| "-" :: args =>
let stdin ← IO.getStdin
dump stdin
process exitCode args
| filename :: args =>
let stream ← fileStream ⟨filename⟩
match stream with
| none =>
process 1 args
| some stream =>
dump stream
process exitCode args`

Just as with `if`, each branch of a `match` that is used as a statement in a `do` is implicitly provided with its own `do`.

`if`와 마찬가지로 `do`의 명령문으로 사용되는 `match`의 각 분기는 암시적으로 자신의 `do`가 제공됩니다.

There are three possibilities.
One is that no more files remain to be processed, in which case `process` returns the error code unchanged.
Another is that the specified filename is `"-"`, in which case `process` dumps the contents of the standard input and then processes the remaining filenames.
The final possibility is that an actual filename was specified.
In this case, `fileStream` is used to attempt to open the file as a POSIX stream.
Its argument is encased in `⟨ ... ⟩` because a `FilePath` is a single-field structure that contains a string.
If the file could not be opened, it is skipped, and the recursive call to `process` sets the exit code to `1`.
If it could, then it is dumped, and the recursive call to `process` leaves the exit code unchanged.

세 가지 가능성이 있습니다.
하나는 처리할 파일이 더 이상 없는 경우이며, 이 경우 `process`는 오류 코드를 변경하지 않고 반환합니다.
다른 하나는 지정된 파일명이 `"-"`인 경우이며, 이 경우 `process`는 표준 입력의 내용을 출력한 다음 나머지 파일명을 처리합니다.
마지막 가능성은 실제 파일명이 지정된 경우입니다.
이 경우 `fileStream`을 사용하여 파일을 POSIX 스트림으로 열기를 시도합니다.
`FilePath`는 문자열을 포함하는 단일 필드 구조이므로 인수는 `⟨ ... ⟩`로 감싸집니다.
파일을 열 수 없으면 건너뛰고 `process`에 대한 재귀 호출이 종료 코드를 `1`로 설정합니다.
열 수 있으면 출력되고 `process`에 대한 재귀 호출이 종료 코드를 변경하지 않고 유지합니다.

`process` does not need to be marked `partial` because it is structurally recursive.
Each recursive call is provided with the tail of the input list, and all Lean lists are finite.
Thus, `process` does not introduce any non-termination.

`process`는 구조적으로 재귀적이므로 `partial`로 표시할 필요가 없습니다.
각 재귀 호출은 입력 리스트의 꼬리로 제공되며, 모든 Lean 리스트는 유한합니다.
따라서 `process`는 비종료를 도입하지 않습니다.
