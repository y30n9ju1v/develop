---
title: "Ch.8: 프로그래밍, 증명, 성능"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Ch.8: 프로그래밍, 증명, 성능"
---

# 8. Programming, Proving, and Performance

This chapter is about programming.
Programs need to compute the correct result, but they also need to do so efficiently.
To write efficient functional programs, it's important to know both how to use data structures appropriately and how to think about the time and space needed to run a program.

이 챕터는 프로그래밍에 관한 것입니다.
프로그램은 올바른 결과를 계산해야 하지만, 효율적으로 수행해야 합니다.
효율적인 함수형 프로그램을 작성하려면, 데이터 구조를 적절하게 사용하는 방법과 프로그램을 실행하는 데 필요한 시간 및 공간을 생각하는 방법을 모두 알아야 합니다.

This chapter is also about proofs.
One of the most important data structures for efficient programming in Lean is the array, but safe use of arrays requires proving that array indices are in bounds.
Furthermore, most interesting algorithms on arrays do not follow the pattern of structural recursion—instead, they iterate over the array.
While these algorithms terminate, Lean will not necessarily be able to automatically check this.
Proofs can be used to demonstrate why a program terminates.

이 챕터는 증명도 다룹니다.
Lean의 효율적인 프로그래밍을 위한 가장 중요한 데이터 구조 중 하나는 배열이지만, 배열을 안전하게 사용하려면 배열 인덱스가 범위 내에 있다는 것을 증명해야 합니다.
더욱이, 배열에 대한 대부분의 흥미로운 알고리즘은 구조적 재귀의 패턴을 따르지 않습니다. 대신 배열을 반복합니다.
이런 알고리즘은 언젠가 종료되지만, Lean이 자동으로 이를 확인하지 못할 수 있습니다.
증명을 통해 프로그램이 종료됨을 보일 수 있습니다.

Rewriting programs to make them faster often results in code that is more difficult to understand.
Proofs can also show that two programs always compute the same answers, even if they do so with different algorithms or implementation techniques.
In this way, the slow, straightforward program can serve as a specification for the fast, complicated version.

프로그램을 더 빠르게 최적화하면 코드가 복잡해지는 경우가 많습니다.
증명을 통해, 두 프로그램이 서로 다른 알고리즘을 쓰더라도 항상 같은 답을 낸다는 것을 보일 수 있습니다.
이렇게 하면 느리고 단순한 프로그램이 빠르고 복잡한 버전의 명세 역할을 할 수 있습니다.

Combining proofs and programming allows programs to be both safe and efficient.
Proofs allow elision of run-time bounds checks, they render many tests unnecessary, and they provide an extremely high level of confidence in a program without introducing any runtime performance overhead.
However, proving theorems about programs can be time consuming and expensive, so other tools are often more economical.

증명과 프로그래밍을 결합하면 프로그램이 안전하고 효율적일 수 있습니다.
증명은 런타임 범위 확인의 생략을 허용하고, 많은 테스트를 불필요하게 하고, 런타임 성능 오버헤드를 도입하지 않고 프로그램에 극도로 높은 수준의 신뢰를 제공합니다.
그러나 프로그램에 대한 정리를 증명하는 것은 시간이 많이 걸리고 비용이 많이 들 수 있으므로, 다른 도구가 종종 더 경제적입니다.

Interactive theorem proving is a deep topic.
This chapter provides only a taste, oriented towards the proofs that come up in practice while programming in Lean.
Most interesting theorems are not closely related to programming.
Please refer to [Next Steps](Next-Steps/#next-steps) for a list of resources for learning more.
Just as when learning programming, however, there's no substitute for hands-on experience when learning to write proofs—it's time to get started!

대화형 정리 증명은 깊은 주제입니다.
이 챕터는 Lean으로 프로그래밍할 때 실제로 나오는 증명을 지향하는 맛만 제공합니다.
대부분의 흥미로운 정리는 프로그래밍과 밀접한 관련이 없습니다.
더 자세히 알아보기 위한 리소스 목록은 [다음 단계](Next-Steps/#next-steps)를 참조하세요.
프로그래밍을 배울 때와 마찬가지로, 증명을 작성하는 방법을 배울 때 직접 경험을 대신할 수 없습니다. 시작할 때입니다!

1. [8.1. Tail Recursion](8-1-tail-recursion/)
2. [8.2. Proving Equivalence](8-2-proving-equivalence/)
3. [8.3. Arrays and Termination](8-3-arrays-and-termination/)
4. [8.4. More Inequalities](8-4-more-inequalities/)
5. [8.5. Bounded Numbers](8-5-bounded-numbers/)
6. [8.6. Insertion Sort and Array Mutation](8-6-insertion-sort-and-array-mutation/)
7. [8.7. Special Types](8-7-special-types/)
8. [8.8. Summary](8-8-summary/)
