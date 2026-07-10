---
title: "1. 소개"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "theorem-proving", "type-theory"]
categories: ["programming"]
description: "Lean이 무엇인지, 정리 증명이란 무엇인지, 이 책의 구성과 사용법을 소개합니다."
---

## 1.1. Computers and Theorem Proving

*Formal verification* involves the use of logical and computational methods to establish claims that are expressed in
precise mathematical terms. These can include ordinary mathematical theorems, as well as claims that pieces of hardware
or software, network protocols, and mechanical and hybrid systems meet their specifications. In practice, there is not a
sharp distinction between verifying a piece of mathematics and verifying the correctness of a system: formal
verification requires describing hardware and software systems in mathematical terms, at which point establishing claims
as to their correctness becomes a form of theorem proving. Conversely, the proof of a mathematical theorem may require a
lengthy computation, in which case verifying the truth of the theorem requires verifying that the computation does what
it is supposed to do.

*형식 검증(Formal Verification)*은 정확한 수학적 용어로 표현된 주장을 확립하기 위해 논리적, 계산적 방법을 사용하는 것을 포함합니다. 여기에는 일반적인 수학 정리뿐만 아니라 하드웨어 또는 소프트웨어, 네트워크 프로토콜, 기계 및 하이브리드 시스템이 사양을 충족하는지에 대한 주장도 포함될 수 있습니다. 실제로 수학을 검증하는 것과 시스템의 정확성을 검증하는 것 사이에는 명확한 구분이 없습니다: 형식 검증은 하드웨어와 소프트웨어 시스템을 수학적 용어로 설명해야 하며, 이 시점에서 정확성에 대한 주장을 확립하는 것은 정리 증명의 한 형태가 됩니다. 반대로, 수학 정리의 증명에는 길고 복잡한 계산이 필요할 수 있으며, 이 경우 정리의 진실성을 검증하려면 그 계산이 의도한 대로 작동하는지 확인해야 합니다.

The gold standard for supporting a mathematical claim is to provide a proof, and twentieth-century developments in logic
show most if not all conventional proof methods can be reduced to a small set of axioms and rules in any of a number of
foundational systems. With this reduction, there are two ways that a computer can help establish a claim: it can help
find a proof in the first place, and it can help verify that a purported proof is correct.

수학적 주장을 뒷받침하기 위한 최고의 표준은 증명을 제공하는 것입니다. 20세기의 논리학 발전은 대부분의 기존 증명 방법이 여러 기초 시스템 중 하나에서 소수의 공리와 규칙으로 축소될 수 있음을 보여줍니다. 이러한 축소를 통해 컴퓨터가 주장을 확립하는 데 도움을 줄 수 있는 두 가지 방법이 있습니다: 첫째, 증명을 찾는 데 도움을 줄 수 있고, 둘째, 주장된 증명이 정확한지 확인하는 데 도움을 줄 수 있습니다.

*Automated theorem proving* focuses on the “finding” aspect. Resolution theorem provers, tableau theorem provers, fast
satisfiability solvers, and so on provide means of establishing the validity of formulas in propositional and
first-order logic. Other systems provide search procedures and decision procedures for specific languages and domains,
such as linear or nonlinear expressions over the integers or the real numbers. Architectures like SMT (“satisfiability
modulo theories”) combine domain-general search methods with domain-specific procedures. Computer algebra systems and
specialized mathematical software packages provide means of carrying out mathematical computations, establishing
mathematical bounds, or finding mathematical objects. A calculation can be viewed as a proof as well, and these systems,
too, help establish mathematical claims.

*자동 정리 증명(Automated Theorem Proving)*은 “찾기” 측면에 초점을 맞춥니다. 해석 정리 증명기, 표(tableau) 정리 증명기, 빠른 만족성 해결기 등은 명제논리와 1차 논리의 공식의 타당성을 확립하는 수단을 제공합니다. 다른 시스템들은 정수나 실수에 대한 선형 또는 비선형 표현과 같은 특정 언어와 도메인을 위한 검색 절차와 결정 절차를 제공합니다. SMT(“만족성 모듈로 이론”)와 같은 아키텍처는 도메인 일반적 검색 방법과 도메인 특정 절차를 결합합니다. 컴퓨터 대수 시스템과 전문화된 수학 소프트웨어 패키지는 수학 계산을 수행하거나, 수학적 경계를 설정하거나, 수학적 객체를 찾는 수단을 제공합니다. 계산은 증명으로도 볼 수 있으므로, 이러한 시스템들도 수학적 주장을 확립하는 데 도움을 줍니다.

Automated reasoning systems strive for power and efficiency, often at the expense of guaranteed soundness. Such systems
can have bugs, and it can be difficult to ensure that the results they deliver are correct. In contrast, *interactive
theorem proving* focuses on the “verification” aspect of theorem proving, requiring that every claim is supported by a
proof in a suitable axiomatic foundation. This sets a very high standard: every rule of inference and every step of a
calculation has to be justified by appealing to prior definitions and theorems, all the way down to basic axioms and
rules. In fact, most such systems provide fully elaborated “proof objects” that can be communicated to other systems and
checked independently. Constructing such proofs typically requires much more input and interaction from users, but it
allows you to obtain deeper and more complex proofs.

자동 추론 시스템은 흔히 보장된 건전성(soundness)을 희생하면서 성능과 효율성을 추구합니다. 이러한 시스템은 버그를 가질 수 있으며, 결과가 정확한지 확인하기 어려울 수 있습니다. 대조적으로, *대화형 정리 증명(Interactive Theorem Proving)*은 정리 증명의 “검증” 측면에 초점을 맞추며, 모든 주장이 적절한 공리적 기초에서 증명으로 뒷받침되어야 함을 요구합니다. 이는 매우 높은 표준을 설정합니다: 모든 추론 규칙과 계산의 각 단계는 기본 공리와 규칙까지 거슬러 올라가며 이전의 정의와 정리에 호소해서 정당화되어야 합니다. 실제로, 대부분의 그러한 시스템은 완전히 구성된 “증명 객체(proof objects)”를 제공하며, 이는 다른 시스템에 전달되고 독립적으로 확인될 수 있습니다. 이러한 증명을 구성하려면 일반적으로 사용자의 훨씬 더 많은 입력과 상호작용이 필요하지만, 더 깊고 더 복잡한 증명을 얻을 수 있게 해줍니다.

The *Lean Theorem Prover* aims to bridge the gap between interactive and automated theorem proving, by situating
automated tools and methods in a framework that supports user interaction and the construction of fully specified
axiomatic proofs. The goal is to support both mathematical reasoning and reasoning about complex systems, and to verify
claims in both domains.

*Lean 정리 증명기(Lean Theorem Prover)*는 자동화된 도구와 방법을 사용자 상호작용과 완전히 명시된 공리적 증명 구성을 지원하는 프레임워크에 배치함으로써 대화형과 자동화된 정리 증명 사이의 간격을 메우는 것을 목표로 합니다. 목표는 수학적 추론과 복잡한 시스템에 대한 추론을 모두 지원하고, 두 영역 모두에서 주장을 검증하는 것입니다.

Lean's underlying logic has a computational interpretation, and Lean can be viewed equally well as a programming
language. More to the point, it can be viewed as a system for writing programs with a precise semantics, as well as
reasoning about the functions that the programs compute. Lean also has mechanisms to serve as its own *metaprogramming
language*, which means that you can implement automation and extend the functionality of Lean using Lean itself. These
aspects of Lean are described in the free online book, [Functional Programming in Lean](https://lean-lang.org/functional_programming_in_lean/), though computational
aspects of the system will make an appearance here.

Lean의 기초 논리는 계산적 해석을 가지고 있으며, Lean은 프로그래밍 언어로도 똑같이 잘 볼 수 있습니다. 더 정확히 말하면, 정확한 의미론을 가진 프로그램을 작성하기 위한 시스템으로, 그리고 프로그램이 계산하는 함수에 대해 추론하는 시스템으로 볼 수 있습니다. Lean은 또한 자체 *메타프로그래밍 언어*로 작동하는 메커니즘을 가지고 있으므로, Lean을 사용하여 Lean의 기능을 자동화하고 확장할 수 있습니다. Lean의 이러한 측면들은 무료 온라인 책인 [Functional Programming in Lean](https://lean-lang.org/functional_programming_in_lean/)에서 설명되어 있지만, 시스템의 계산적 측면도 여기에서 나타날 것입니다.

## 1.2. About Lean

The *Lean* project was launched by Leonardo de Moura at Microsoft Research Redmond in 2013. It is an ongoing, long-term
effort, and much of the potential for automation will be realized only gradually over time. Lean is released under the
[Apache 2.0 license](https://github.com/leanprover/lean4/blob/master/LICENSE), a permissive open source license that permits others to use and extend the code and
mathematical libraries freely.

*Lean* 프로젝트는 2013년 Microsoft Research Redmond의 Leonardo de Moura에 의해 시작되었습니다. 이는 지속적이고 장기적인 노력이며, 자동화의 많은 잠재력은 시간이 지나면서 점진적으로만 실현될 것입니다. Lean은 [Apache 2.0 라이선스](https://github.com/leanprover/lean4/blob/master/LICENSE)로 출시되며, 이는 다른 사람들이 코드와 수학 라이브러리를 자유롭게 사용하고 확장할 수 있게 하는 허용적인 오픈소스 라이선스입니다.

To install Lean in your computer consider using the [Quickstart](https://lean-lang.org/install/) instructions. The Lean source code, and instructions for building Lean, are available at
<https://github.com/leanprover/lean4/>.

컴퓨터에 Lean을 설치하려면 [빠른 시작](https://lean-lang.org/install/) 지침을 사용하는 것을 고려해보세요. Lean 소스 코드와 Lean을 구축하기 위한 지침은 <https://github.com/leanprover/lean4/>에서 이용할 수 있습니다.

This tutorial describes the current version of Lean, known as Lean 4.

이 튜토리얼은 Lean 4로 알려진 Lean의 현재 버전을 설명합니다.

## 1.3. About this Book

This book is designed to teach you to develop and verify proofs in Lean. Much of the background information you will
need in order to do this is not specific to Lean at all. To start with, you will learn the logical system that Lean is
based on, a version of *dependent type theory* that is powerful enough to prove almost any conventional mathematical
theorem, and expressive enough to do it in a natural way. More specifically, Lean is based on a version of a system
known as the Calculus of Constructions with inductive types. Lean can not only define mathematical objects and express
mathematical assertions in dependent type theory, but it also can be used as a language for writing proofs.

이 책은 Lean에서 증명을 개발하고 검증하는 방법을 가르치도록 설계되었습니다. 이를 위해 필요한 배경 정보의 많은 부분은 Lean에 국한되지 않습니다. 우선, Lean이 기반한 논리 체계인 거의 모든 기존 수학 정리를 증명할 수 있을 만큼 강력하고, 자연스러운 방식으로 표현할 수 있을 만큼 표현적인 *종속 타입 이론(dependent type theory)*의 한 버전을 배우게 될 것입니다. 더 구체적으로, Lean은 귀납적 타입을 가진 구성 계산법(Calculus of Constructions)으로 알려진 시스템의 한 버전을 기반으로 합니다. Lean은 종속 타입 이론에서 수학적 객체를 정의하고 수학적 주장을 표현할 수 있을 뿐만 아니라, 증명을 작성하기 위한 언어로도 사용될 수 있습니다.

Because fully detailed axiomatic proofs are so complicated, the challenge of theorem proving is to have the computer
fill in as many of the details as possible. You will learn various methods to support this in [dependent type
theory](../02-dependent-type-theory/#dependent-type-theory). For example, term rewriting, and Lean's automated methods for simplifying terms and
expressions automatically. Similarly, methods of *elaboration* and *type inference*, which can be used to support
flexible forms of algebraic reasoning.

완전히 상세한 공리적 증명이 매우 복잡하기 때문에, 정리 증명의 과제는 컴퓨터가 가능한 많은 세부 사항을 채우는 것입니다. [종속 타입 이론](../02-dependent-type-theory/#dependent-type-theory)에서 이를 지원하는 다양한 방법을 배우게 될 것입니다. 예를 들어, 항 재작성(term rewriting)과 Lean의 항과 식을 자동으로 단순화하는 자동화된 방법이 있습니다. 마찬가지로, *정교화(elaboration)*와 *타입 추론(type inference)* 방법이 있으며, 이는 유연한 형태의 대수적 추론을 지원하는 데 사용될 수 있습니다.

Finally, you will learn about features that are specific to Lean, including the language you use to communicate
with the system, and the mechanisms Lean offers for managing complex theories and data.

마지막으로, 시스템과 통신하는 데 사용하는 언어와 Lean이 복잡한 이론과 데이터를 관리하기 위해 제공하는 메커니즘을 포함하여 Lean에 특정한 기능에 대해 배우게 될 것입니다.

Throughout the text you will find examples of Lean code like the one below:

전체 텍스트에서 다음과 같은 Lean 코드 예제를 찾을 수 있습니다:

```
theorem and_commutative (p q : Prop) : p ∧ q → q ∧ p :=
  fun hpq : p ∧ q =>
  have hp : p := And.left hpq
  have hq : q := And.right hpq
  show q ∧ p from And.intro hq hp
```

Next to every code example in this book, you will see a button that reads “Copy to clipboard”.
Pressing the button copies the example with enough surrounding context to make the code compile correctly.
You can paste the example code into [VS Code](https://code.visualstudio.com/) and modify the examples, and Lean will check the results and provide feedback continuously as you type.
We recommend running the examples and experimenting with the code on your own as you work through the chapters that follow.
You can open this book in VS Code by using the command “Lean 4: Docs: Show Documentation Resources” and selecting “Theorem Proving in Lean 4” in the tab that opens.

이 책의 모든 코드 예제 옆에는 “클립보드에 복사”라고 표시된 버튼이 있습니다. 버튼을 누르면 코드가 올바르게 컴파일될 수 있도록 충분한 주변 컨텍스트와 함께 예제가 복사됩니다. 예제 코드를 [VS Code](https://code.visualstudio.com/)에 붙여넣고 예제를 수정할 수 있으며, Lean은 입력할 때 연속적으로 결과를 확인하고 피드백을 제공합니다. 우리는 다음 장들을 진행하면서 예제를 직접 실행하고 코드로 실험해보기를 권장합니다. “Lean 4: Docs: Show Documentation Resources” 명령을 사용하여 VS Code에서 이 책을 열고 열리는 탭에서 “Theorem Proving in Lean 4”를 선택할 수 있습니다.

## 1.4. Acknowledgments

This tutorial is an open access project maintained on Github. Many people have contributed to the effort, providing
corrections, suggestions, examples, and text. We are grateful to Ulrik Buchholz, Kevin Buzzard, Mario Carneiro, Nathan
Carter, Eduardo Cavazos, Amine Chaieb, Joe Corneli, William DeMeo, Marcus Klaas de Vries, Ben Dyer, Gabriel Ebner,
Anthony Hart, Simon Hudon, Sean Leather, Assia Mahboubi, Gihan Marasingha, Patrick Massot, Christopher John Mazey,
Sebastian Ullrich, Floris van Doorn, Daniel Velleman, Théo Zimmerman, Paul Chisholm, Chris Lovett, and Siddhartha Gadgil for their contributions. Please see [lean prover](https://github.com/leanprover/) and [lean community](https://github.com/leanprover-community/) for an up to date list
of our amazing contributors.

이 튜토리얼은 Github에서 유지 관리되는 공개 접근 프로젝트입니다. 많은 사람들이 수정 사항, 제안, 예제, 텍스트를 제공하여 노력에 기여했습니다. Ulrik Buchholz, Kevin Buzzard, Mario Carneiro, Nathan Carter, Eduardo Cavazos, Amine Chaieb, Joe Corneli, William DeMeo, Marcus Klaas de Vries, Ben Dyer, Gabriel Ebner, Anthony Hart, Simon Hudon, Sean Leather, Assia Mahboubi, Gihan Marasingha, Patrick Massot, Christopher John Mazey, Sebastian Ullrich, Floris van Doorn, Daniel Velleman, Théo Zimmerman, Paul Chisholm, Chris Lovett, 그리고 Siddhartha Gadgil의 기여에 감사드립니다. [lean prover](https://github.com/leanprover/)와 [lean community](https://github.com/leanprover-community/)에서 우리의 놀라운 기여자들의 최신 목록을 확인하세요.
