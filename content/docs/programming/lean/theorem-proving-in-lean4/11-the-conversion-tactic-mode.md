---
title: "11. Conversion 전술 모드"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "theorem-proving", "type-theory"]
categories: ["programming"]
description: "conv 모드로 목표와 가정 내부를 탐색하며 부분식을 재작성하는 방법을 다룹니다."
---

Inside a tactic block, one can use the keyword `conv` to enter
*conversion mode*. This mode allows to travel inside assumptions and
goals, even inside function abstractions and dependent arrows, to apply rewriting or
simplifying steps.

전술 블록 내에서 `conv` 키워드를 사용하여 *변환 모드(conversion mode)*에 진입할 수 있습니다. 이 모드를 사용하면 가정과 목표 내부를 이동할 수 있으며, 함수 추상화와 종속 화살표 내부까지 들어가서 다시 쓰기 또는 단순화 단계를 적용할 수 있습니다.

## 11.1. Basic navigation and rewriting

As a first example, let us prove example
`(a b c : Nat) : a * (b * c) = a * (c * b)`
(examples in this file are somewhat artificial since
other tactics could finish them immediately). The naive
first attempt is to enter tactic mode and try `rw [Nat.mul_comm]`. But this
transforms the goal into `b * c * a = a * (c * b)`, after commuting the
very first multiplication appearing in the term. There are several
ways to fix this issue, and one way is to use a more precise tool:
the conversion mode. The following code block shows the current target
after each line.

첫 번째 예로, `(a b c : Nat) : a * (b * c) = a * (c * b)`라는 예제를 증명해봅시다. (이 파일의 예제들은 다른 전술들이 즉시 완료할 수 있기 때문에 다소 인위적입니다). 소박한 첫 번째 시도는 전술 모드에 들어가서 `rw [Nat.mul_comm]`을 시도하는 것입니다. 하지만 이것은 항에서 가장 먼저 나타나는 곱셈을 교환한 후 목표를 `b * c * a = a * (c * b)`로 변환합니다. 이 문제를 해결하는 여러 방법이 있으며, 한 가지 방법은 더 정확한 도구인 변환 모드를 사용하는 것입니다. 다음 코드 블록은 각 줄 이후의 현재 목표를 보여줍니다.

The above snippet shows three navigation commands:

* `lhs` navigates to the left-hand side of a relation (equality, in this case).
  There is also a `rhs` to navigate to the right-hand side.
* `congr` creates as many targets as there are (nondependent and explicit) arguments to the current head function
  (here the head function is multiplication).
* `rfl` closes target using reflexivity.

Once arrived at the relevant target, we can use `rw` as in normal
tactic mode.

위의 코드는 세 가지 네비게이션 명령을 보여줍니다:

* `lhs`는 관계식(이 경우 동치성)의 왼쪽을 네비게이션합니다. 오른쪽으로 이동하는 `rhs`도 있습니다.
* `congr`은 현재 head 함수(여기서는 곱셈)에 대한 (비종속적이고 명시적인) 인수만큼 많은 목표를 생성합니다.
* `rfl`은 반사성을 사용하여 목표를 닫습니다.

관련 목표에 도달하면, 일반적인 전술 모드에서처럼 `rw`를 사용할 수 있습니다.

The second main reason to use conversion mode is to rewrite under
binders. Suppose we want to prove example
`(fun x : Nat => 0 + x) = (fun x => x)`.
The naive first attempt is to enter tactic mode and try
`rw [Nat.zero_add]`. But this fails with a frustrating

```
error: tactic 'rewrite' failed, did not find instance of the pattern
       in the target expression
  0 + ?n
⊢ (fun x => 0 + x) = fun x => x
```

The solution is:

where `intro x` is the navigation command entering inside the `fun` binder.
Note that this example is somewhat artificial, one could also do:

or just

`conv` can also rewrite a hypothesis `h` from the local context, using `conv at` `h`.

변환 모드를 사용하는 두 번째 주요 이유는 바인더 아래에서 다시 쓰기하는 것입니다. `(fun x : Nat => 0 + x) = (fun x => x)`라는 예제를 증명하고 싶다고 가정해봅시다. 소박한 첫 번째 시도는 전술 모드에 들어가서 `rw [Nat.zero_add]`를 시도하는 것입니다. 하지만 이것은 답답한 오류로 실패합니다:

```
error: tactic 'rewrite' failed, did not find instance of the pattern
       in the target expression
  0 + ?n
⊢ (fun x => 0 + x) = fun x => x
```

해결책은:

여기서 `intro x`는 `fun` 바인더 내부로 들어가는 네비게이션 명령입니다. 이 예제는 다소 인위적이며, 다음과 같이 할 수도 있습니다:

또는 단순히:

`conv`는 또한 `conv at h`를 사용하여 로컬 컨텍스트에서 가정 `h`를 다시 쓸 수 있습니다.

## 11.2. Pattern matching

Navigation using the above commands can be tedious. One can shortcut it using pattern matching as follows:

which is just syntax sugar for

Of course, wildcards are allowed:

위의 명령을 사용한 네비게이션은 번거로울 수 있습니다. 다음과 같이 패턴 매칭을 사용하여 단축할 수 있습니다:

이것은 단순히 다음의 문법 설탕입니다:

물론 와일드카드도 허용됩니다:

## 11.3. Structuring conversion tactics

Curly brackets and `.` can also be used in `conv` mode to structure tactics:

중괄호와 `.`는 또한 `conv` 모드에서 전술을 구조화하기 위해 사용될 수 있습니다:

## 11.4. Other tactics inside conversion mode

* `arg` `i` enter the `i`-th nondependent explicit argument of an application.
* `args` is an alternative name for `congr`.
* `simp` applies the simplifier to the current goal. It supports the same options available in regular tactic mode.
* `enter` `[1, x, 2, y]` iterate `arg` and `intro` with the given arguments.
* `done` fail if there are unsolved goals.
* `trace_state` display the current tactic state.
* `whnf` put term in weak head normal form.
* `tactic` `=> <tactic sequence>` go back to regular tactic mode. This
  is useful for discharging goals not supported by `conv` mode, and
  applying custom congruence and extensionality lemmas.
* `apply` `<term>` is syntax sugar for `tactic` `=> apply <term>`.

* `arg` `i`는 응용의 `i`번째 비종속적 명시적 인수를 입력합니다.
* `args`는 `congr`의 대체 이름입니다.
* `simp`는 현재 목표에 단순화 도구를 적용합니다. 일반 전술 모드에서 사용 가능한 동일한 옵션을 지원합니다.
* `enter` `[1, x, 2, y]`는 주어진 인수로 `arg`와 `intro`를 반복합니다.
* `done`은 해결되지 않은 목표가 있으면 실패합니다.
* `trace_state`는 현재 전술 상태를 표시합니다.
* `whnf`는 항을 약한 head 정규형으로 변환합니다.
* `tactic` `=> <tactic sequence>`는 일반 전술 모드로 돌아갑니다. 이것은 `conv` 모드에서 지원하지 않는 목표를 처리하고 사용자 정의 합동 및 확장성 보조정리를 적용할 때 유용합니다.
* `apply` `<term>`은 `tactic` `=> apply <term>`의 문법 설탕입니다.

[←10. Type Classes](../10-type-classes/#type-classes)[12. Axioms and Computation→](../12-axioms-and-computation/#axioms-and-computation)
