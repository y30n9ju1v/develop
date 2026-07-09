---
title: "8.8. 요약 (Summary)"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "요약 (Summary)"
---

# 8.8. Summary

## 8.8.1. Tail Recursion

Tail recursion is recursion in which the results of recursive calls are returned immediately, rather than being used in some other way.
These recursive calls are called *tail calls*.
Tail calls are interesting because they can be compiled to a jump instruction rather than a call instruction, and the current stack frame can be re-used instead of pushing a new frame.
In other words, tail-recursive functions are actually loops.

Tail recursion은 재귀 호출의 결과가 즉시 반환되는 재귀입니다. 다른 방식으로 사용되지는 않습니다.
이러한 재귀 호출을 *tail calls*이라고 합니다.
Tail calls는 호출 명령어가 아닌 점프 명령어로 컴파일될 수 있고, 새 프레임을 푸시하는 대신 현재 스택 프레임을 재사용할 수 있기 때문에 흥미롭습니다.
즉, tail-recursive 함수는 실제로 루프입니다.

A common way to make a recursive function faster is to rewrite it in accumulator-passing style.
Instead of using the call stack to remember what is to be done with the result of a recursive call, an additional argument called an *accumulator* is used to collect this information.
For example, an accumulator for a tail-recursive function that reverses a list contains the already-seen list entries, in reverse order.

재귀 함수를 더 빠르게 하는 일반적인 방법은 accumulator-passing 스타일로 다시 작성하는 것입니다.
재귀 호출의 결과로 수행할 작업을 기억하기 위해 호출 스택을 사용하는 대신, *accumulator*라는 추가 인수를 사용하여 이 정보를 수집합니다.
예를 들어, 목록을 역순으로 하는 tail-recursive 함수의 accumulator는 이미 본 목록 항목을 역순으로 포함합니다.

In Lean, only self-tail-calls are optimized into loops.
In other words, two functions that each end with a tail call to the other will not be optimized.

Lean에서는 self-tail-calls만 루프로 최적화됩니다.
즉, 서로에게 tail call로 끝나는 두 함수는 최적화되지 않습니다.

## 8.8.2. Reference Counting and In-Place Updates

Rather than using a tracing garbage collector, as is done in Java, C#, and most JavaScript implementations, Lean uses reference counting for memory management.
This means that each value in memory contains a field that tracks how many other values refer to it, and the run-time system maintains these counts as references appear or disappear.
Reference counting is also used in Python, PHP, and Swift.

Java, C#, 대부분의 JavaScript 구현과 달리 추적 garbage collector를 사용하는 대신, Lean은 메모리 관리를 위해 reference counting을 사용합니다.
이는 메모리의 각 값이 그것을 참조하는 다른 값의 개수를 추적하는 필드를 포함한다는 의미이며, 런타임 시스템은 참조가 나타나거나 사라지면서 이러한 카운트를 유지합니다.
Reference counting은 Python, PHP, Swift에서도 사용됩니다.

When asked to allocate a fresh object, Lean's run-time system is able to recycle existing objects whose reference counts are falling to zero.
Additionally, array operations such as `Array.set` and `Array.swap` will mutate an array if its reference count is one, rather than allocating a modified copy.
If `Array.swap` holds the only reference to an array, then no other part of the program can tell that it was mutated rather than copied.

새 객체를 할당하도록 요청받으면, Lean의 런타임 시스템은 reference count가 0으로 떨어지는 기존 객체를 재활용할 수 있습니다.
또한, `Array.set` 및 `Array.swap`과 같은 배열 작업은 수정된 복사본을 할당하는 대신 reference count가 1이면 배열을 변경합니다.
`Array.swap`이 배열에 대한 유일한 참조를 가지고 있으면, 프로그램의 다른 부분은 그것이 복사되기보다는 변경되었다는 것을 알 수 없습니다.

Writing efficient code in Lean requires the use of tail recursion and being careful to ensure that large arrays are used uniquely.
While tail calls can be identified by inspecting the function's definition, understanding whether a value is referred to uniquely may require reading the whole program.
The debugging helper `dbgTraceIfShared` can be used at key locations in the program to check that a value is not shared.

Lean에서 효율적인 코드를 작성하려면 tail recursion을 사용하고 큰 배열이 고유하게 사용되는지 확인하는 데 주의해야 합니다.
tail calls는 함수의 정의를 검사하여 식별할 수 있지만, 값이 고유하게 참조되는지 여부를 이해하려면 전체 프로그램을 읽어야 할 수 있습니다.
디버깅 도우미 `dbgTraceIfShared`를 프로그램의 주요 위치에서 사용하여 값이 공유되지 않는지 확인할 수 있습니다.

## 8.8.3. Proving Programs Correct

Rewriting a program in accumulator-passing style, or making other transformations that make it run faster, can also make it more difficult to understand.
It can be useful to keep the original version of the program that is more clearly correct, and then use it as an executable specification for the optimized version.
While techniques such as unit testing work just as well in Lean as in any other language, Lean also enables the use of mathematical proofs that completely ensure that both versions of the function return the same result for *all possible* inputs.

프로그램을 accumulator-passing 스타일로 다시 작성하거나 더 빠르게 실행되게 하는 다른 변환을 만들면 이해하기가 더 어려워질 수도 있습니다.
더 명확하게 정확한 프로그램의 원본 버전을 유지하고 이를 최적화된 버전에 대한 실행 가능한 사양으로 사용하는 것이 유용할 수 있습니다.
단위 테스트와 같은 기술이 Lean에서도 다른 언어와 마찬가지로 잘 작동하지만, Lean은 두 버전의 함수가 *모든 가능한* 입력에 대해 동일한 결과를 반환하는지 완전히 보장하는 수학 증명의 사용도 가능하게 합니다.

Typically, proving that two functions are equal is done using function extensionality (the `funext` tactic), which is the principle that two functions are equal if they return the same values for every input.
If the functions are recursive, then induction is usually a good way to prove that their outputs are the same.
Usually, the recursive definition of the function will make recursive calls on one particular argument; this argument is a good choice for induction.
In some cases, the induction hypothesis is not strong enough.
Fixing this problem usually requires thought about how to construct a more general version of the theorem statement that provides induction hypotheses that are strong enough.
In particular, to prove that a function is equivalent to an accumulator-passing version, a theorem statement that relates arbitrary initial accumulator values to the final result of the original function is needed.

일반적으로 두 함수가 같다는 것을 증명하는 것은 function extensionality(`funext` 전술)를 사용하여 수행됩니다. 이는 두 함수가 모든 입력에 대해 동일한 값을 반환하면 같다는 원칙입니다.
함수가 재귀적이면, 귀납법이 일반적으로 출력이 같다는 것을 증명하는 좋은 방법입니다.
일반적으로 함수의 재귀 정의는 특정 인수에 대한 재귀 호출을 수행합니다. 이 인수는 귀납법의 좋은 선택입니다.
경우에 따라 귀납 가설이 충분하지 않습니다.
이 문제를 해결하려면 일반적으로 충분히 강한 귀납 가설을 제공하는 더 일반적인 버전의 정리 문을 구성하는 방법에 대해 생각이 필요합니다.
특히, 함수가 accumulator-passing 버전과 동등하다는 것을 증명하려면, 임의의 초기 accumulator 값을 원래 함수의 최종 결과와 연결하는 정리 문이 필요합니다.

## 8.8.4. Safe Array Indices

The type `Fin n` represents natural numbers that are strictly less than `n`.
`Fin` is short for “finite”.
As with subtypes, a `Fin n` is a structure that contains a `Nat` and a proof that this `Nat` is less than `n`.
There are no values of type `Fin 0`.

`Fin n` 타입은 `n`보다 엄격히 작은 자연수를 나타냅니다.
`Fin`은 “유한”의 약자입니다.
부분타입과 마찬가지로, `Fin n`은 `Nat`과 이 `Nat`이 `n`보다 작다는 증명을 포함하는 구조체입니다.
`Fin 0` 타입의 값은 없습니다.

If `arr` is an `Array α`, then `Fin arr.size` always contains a number that is a suitable index into `arr`.

Lean provides instances of most of the useful numeric type classes for `Fin`.
The `OfNat` instances for `Fin` perform modular arithmetic rather than failing at compile time if the number provided is larger than the `Fin` can accept.

`arr`이 `Array α`이면, `Fin arr.size`는 항상 `arr`에 대한 적절한 인덱스인 숫자를 포함합니다.

Lean은 `Fin`에 대해 대부분의 유용한 숫자 타입 클래스의 인스턴스를 제공합니다.
`Fin`에 대한 `OfNat` 인스턴스는 제공된 숫자가 `Fin`이 수용할 수 있는 것보다 크면 컴파일 타임에 실패하는 대신 모듈로 산술을 수행합니다.

## 8.8.5. Provisional Proofs

Sometimes, it can be useful to pretend that a statement is proved without actually doing the work of proving it.
This can be useful when making sure that a proof of a statement would be suitable for some task, such as a rewrite in another proof, determining that an array access is safe, or showing that a recursive call is made on a smaller value than the original argument.
It's very frustrating to spend time proving something, only to discover that some other proof would have been more useful.

때로는 실제로 증명하는 작업을 하지 않고 진술이 증명되었다고 가장하는 것이 유용할 수 있습니다.
이는 진술의 증명이 다른 증명에서의 재작성, 배열 액세스가 안전한지 결정, 또는 재귀 호출이 원래 인수보다 작은 값에 대해 이루어지는지 보여주는 등의 일부 작업에 적합한지 확인할 때 유용할 수 있습니다.
뭔가를 증명하는 데 시간을 소비한 후 다른 증명이 더 유용했을 것을 발견하는 것은 매우 답답합니다.

The `sorry` tactic causes Lean to provisionally accept a statement as if it were a real proof.
It can be seen as analogous to a stub method that throws a `NotImplementedException` in C#.
Any proof that relies on `sorry` includes a warning in Lean.

`sorry` 전술은 Lean이 진술을 실제 증명인 것처럼 임시로 수용하도록 합니다.
C#에서 `NotImplementedException`을 던지는 스텁 메서드와 유사한 것으로 볼 수 있습니다.
`sorry`에 의존하는 모든 증명은 Lean에서 경고를 포함합니다.

Be careful!
The `sorry` tactic can prove *any* statement, even false statements.
Proving that `3 < 2` can cause an out-of-bounds array access to persist to runtime, unexpectedly crashing a program.
Using `sorry` is convenient during development, but keeping it in the code is dangerous.

주의하세요!
`sorry` 전술은 거짓 진술을 포함하여 *모든* 진술을 증명할 수 있습니다.
`3 < 2`를 증명하면 범위를 벗어난 배열 액세스가 런타임에 유지되어 프로그램이 예기치 않게 충돌할 수 있습니다.
`sorry`를 사용하는 것은 개발 중에는 편리하지만, 코드에 유지하는 것은 위험합니다.

## 8.8.6. Proving Termination

When a recursive function does not use structural recursion, Lean cannot automatically determine that it terminates.
In these situations, the function could just be marked `partial`.
However, it is also possible to provide a proof that the function terminates.

재귀 함수가 구조적 재귀를 사용하지 않을 때, Lean은 자동으로 종료되는지 결정할 수 없습니다.
이러한 상황에서 함수는 단지 `partial`로 표시될 수 있습니다.
그러나 함수가 종료된다는 증명을 제공하는 것도 가능합니다.

Partial functions have a key downside: they can't be unfolded during type checking or in proofs.
This means that Lean's value as an interactive theorem prover can't be applied to them.
Additionally, showing that a function that is expected to terminate actually always does terminate removes one more potential source of bugs.

Partial 함수에는 한 가지 주요 단점이 있습니다: 타입 체크 중이나 증명에서 펼쳐질 수 없습니다.
이는 Lean의 대화형 정리 증명자로서의 가치를 적용할 수 없다는 의미입니다.
또한, 종료될 것으로 예상되는 함수가 실제로 항상 종료된다는 것을 보여주면 버그의 잠재적 원인을 하나 더 제거합니다.

The `termination_by` clause that's allowed at the end of a function can be used to specify the reason why a recursive function terminates.
The clause maps the function's arguments to an expression that is expected to be smaller for each recursive call.
Some examples of expressions that might decrease are the difference between a growing index into an array and the array's size, the length of a list that's cut in half at each recursive call, or a pair of lists, exactly one of which shrinks on each recursive call.

함수 끝에서 허용되는 `termination_by` 절을 사용하여 재귀 함수가 종료되는 이유를 지정할 수 있습니다.
절은 함수의 인수를 각 재귀 호출에서 더 작을 것으로 예상되는 식에 매핑합니다.
감소할 수 있는 식의 몇 가지 예는 배열로 증가하는 인덱스와 배열의 크기 간의 차이, 각 재귀 호출에서 반으로 잘린 목록의 길이, 또는 정확히 하나가 각 재귀 호출에서 축소되는 목록 쌍입니다.

Lean contains proof automation that can automatically determine that some expressions shrink with each call, but many interesting programs will require manual proofs.
These proofs can be provided with `have`, a version of `let` that's intended for locally providing proofs rather than values.

Lean에는 일부 식이 각 호출에서 축소되는지 자동으로 결정할 수 있는 증명 자동화가 포함되어 있지만, 많은 흥미로운 프로그램은 수동 증명이 필요합니다.
이 증명은 `have`를 사용하여 제공할 수 있습니다. 이는 값이 아닌 증명을 로컬로 제공하기 위한 `let`의 버전입니다.

A good way to write recursive functions is to begin by declaring them `partial` and debugging them with testing until they return the right answers.
Then, `partial` can be removed and replaced with a `termination_by` clause.
Lean will place error highlights on each recursive call for which a proof is needed that contains the statement that needs to be proved.
Each of these statements can be placed in a `have`, with the proof being `sorry`.
If Lean accepts the program and it still passes its tests, the final step is to actually prove the theorems that enable Lean to accept it.
This approach can prevent wasting time on proving that a buggy program terminates.

재귀 함수를 작성하는 좋은 방법은 `partial`을 선언하고 올바른 답을 반환할 때까지 테스트로 디버깅하는 것으로 시작하는 것입니다.
그런 다음 `partial`을 제거하고 `termination_by` 절로 대체할 수 있습니다.
Lean은 증명이 필요한 각 재귀 호출 위에 오류 강조를 배치하고 증명해야 할 진술을 포함합니다.
이러한 각 진술은 `have`에 배치될 수 있으며, 증명은 `sorry`입니다.
Lean이 프로그램을 수용하고 여전히 테스트를 통과하면, 마지막 단계는 Lean이 수용할 수 있게 하는 정리를 실제로 증명하는 것입니다.
이 접근 방식은 버그 있는 프로그램이 종료된다는 것을 증명하는 데 시간을 낭비하는 것을 방지할 수 있습니다.
