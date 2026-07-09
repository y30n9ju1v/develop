---
title: "1.2. 타입"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Lean의 타입 시스템 소개"
---

# 1.2. Types

Types classify programs based on the values that they can
compute. Types serve a number of roles in a program:

1. They allow the compiler to make decisions about the in-memory representation of a value.
2. They help programmers to communicate their intent to others, serving as a lightweight specification for the inputs and outputs of a function.
   The compiler ensures that the program adheres to this specification.
3. They prevent various potential mistakes, such as adding a number to a string, and thus reduce the number of tests that are necessary for a program.
4. They help the Lean compiler automate the production of auxiliary code that can save boilerplate.

타입은 프로그램이 계산할 수 있는 값을 기반으로 프로그램을 분류합니다. 타입은 프로그램에서 여러 역할을 수행합니다:

1. 컴파일러가 값의 메모리 내 표현에 대한 결정을 내릴 수 있게 합니다.
2. 프로그래머가 다른 사람에게 자신의 의도를 전달하도록 도와주며, 함수의 입력 및 출력에 대한 경량 사양으로 제공됩니다.
   컴파일러는 프로그램이 이 사양을 준수하는지 확인합니다.
3. 숫자에 문자열을 더하는 것 같은 다양한 잠재적 실수를 방지하므로, 프로그램에 필요한 테스트의 수를 줄입니다.
4. Lean 컴파일러가 보일러플레이트를 절약할 수 있는 보조 코드의 생성을 자동화하도록 도와줍니다.

Lean's type system is unusually expressive.
Types can encode strong specifications like “this sorting function returns a permutation of its input” and flexible specifications like “this function has different return types, depending on the value of its argument”.
The type system can even be used as a full-blown logic for proving mathematical theorems.
This cutting-edge expressive power doesn't make simpler types unnecessary, however, and understanding these simpler types is a prerequisite for using the more advanced features.

Lean의 타입 시스템은 비상적으로 표현력이 풍부합니다.
타입은 “이 정렬 함수는 입력의 순열을 반환한다”와 같은 강한 사양과 “이 함수는 인수의 값에 따라 다른 반환 타입을 가진다”와 같은 유연한 사양을 인코딩할 수 있습니다.
타입 시스템은 심지어 수학 정리를 증명하기 위한 완전한 논리로 사용될 수 있습니다.
이 첨단의 표현력은 더 간단한 타입을 불필요하게 만들지 않으므로, 이러한 더 간단한 타입을 이해하는 것은 더 고급 기능을 사용하기 위한 전제 조건입니다.

Every program in Lean must have a type. In particular, every
expression must have a type before it can be evaluated. In the
examples so far, Lean has been able to discover a type on its own, but
it is sometimes necessary to provide one. This is done using the colon
operator inside parentheses:

```lean
#eval (1 + 2 : Nat)
```

Here, `Nat` is the type of *natural numbers*, which are arbitrary-precision unsigned integers.
In Lean, `Nat` is the default type for non-negative integer literals.
This default type is not always the best choice.
In C, unsigned integers underflow to the largest representable numbers when subtraction would otherwise yield a result less than zero.
`Nat`, however, can represent arbitrarily-large unsigned numbers, so there is no largest number to underflow to.
Thus, subtraction on `Nat` returns `zero` when the answer would have otherwise been negative.
For instance,

```lean
#eval (1 - 2 : Nat)
```

evaluates to `0` rather than `-1`.
To use a type that can represent the negative integers, provide it directly:

```lean
#eval (1 - 2 : Int)
```

With this type, the result is `-1`, as expected.

Lean의 모든 프로그램은 타입을 가져야 합니다. 특히, 모든 표현식은 평가되기 전에 타입을 가져야 합니다. 지금까지의 예제에서, Lean은 자동으로 타입을 발견할 수 있었지만, 때때로 직접 제공해야 합니다. 이는 괄호 안에 콜론 연산자를 사용하여 수행됩니다.

```lean
#eval (1 + 2 : Nat)
```

여기서 `Nat`은 *자연수*의 타입이며, 임의의 정밀도를 가진 부호 없는 정수입니다.
Lean에서 `Nat`은 음이 아닌 정수 리터럴의 기본 타입입니다.
이 기본 타입이 항상 최선의 선택은 아닙니다.
C에서 부호 없는 정수는 뺄셈 결과가 영수보다 작을 때 가장 큰 표현 가능한 수로 언더플로우합니다.
하지만 `Nat`은 임의로 큰 부호 없는 수를 표현할 수 있으므로, 언더플로우할 가장 큰 수가 없습니다.
따라서 `Nat`에서의 뺄셈은 답이 음수일 때 `zero`를 반환합니다.
예를 들어,

```lean
#eval (1 - 2 : Nat)
```

는 `-1`이 아니라 `0`으로 평가됩니다.
음수를 표현할 수 있는 타입을 사용하려면, 직접 제공하세요.

```lean
#eval (1 - 2 : Int)
```

이 타입으로, 결과는 예상대로 `-1`입니다.

To check the type of an expression without evaluating it, use `#check` instead of `#eval`. For instance:

```lean
#check (1 - 2 : Int)
```

reports `1 - 2 : Int` without actually performing the subtraction.

표현식을 평가하지 않고 타입을 확인하려면, `#eval` 대신 `#check`를 사용하세요. 예를 들어,

```lean
#check (1 - 2 : Int)
```

는 실제로 뺄셈을 수행하지 않고 `1 - 2 : Int`를 보고합니다.

When a program can't be given a type, an error is returned from both `#check` and `#eval`. For instance:

```
#check String.append ["hello", " "] "world"
```

outputs

```
Application type mismatch: The argument
  ["hello", " "]
has type
  List String
but is expected to have type
  String
in the application
  String.append ["hello", " "]
```

because the first argument to `String.append` is expected to be a string, but a list of strings was provided instead.

프로그램에 타입을 부여할 수 없으면, `#check`와 `#eval` 모두에서 오류가 반환됩니다. 예를 들어,

```
#check String.append ["hello", " "] "world"
```

는 다음을 출력합니다.

```
Application type mismatch: The argument
  ["hello", " "]
has type
  List String
but is expected to have type
  String
in the application
  String.append ["hello", " "]
```

`String.append`의 첫 번째 인수는 문자열이어야 하지만, 대신 문자열 목록이 제공되었기 때문입니다.
