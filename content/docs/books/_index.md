---
title: "Books"
---

이해하고 싶은 책을 직접 번역했거나, AI에게 책으로 써달라고 요청해서 만든 기록입니다.

- **[Lean4 입문: 함수형 프로그래밍에서 증명, 메타프로그래밍까지](lean4-getting-started/)** — Functional Programming in Lean, Theorem Proving in Lean 4, Metaprogramming in Lean 4 세 권을 초보자용으로 이어 읽을 수 있게 새로 쓴 책. 왜 배우는지부터 시작해 값·재귀·자료구조·모나드(1부) → 명제-타입 대응·전술·귀납 증명(2부) → 매크로·나만의 tactic(3부) 순서로 쌓아 올린다
- **[Lean4로 증명하는 응용 선형대수](linalg-in-lean4/)** — 벡터의 덧셈에서 시작해 내적·노름·코시-슈바르츠 부등식·선형독립을 Lean4로 직접 증명하며 쌓는, VMLS류 응용 선형대수 커리큘럼을 새로 쓴 책 (1부: 벡터)
- **[nand2npu 1권: Lean4로 증명하며 게이트에서 컴퓨터까지](nand2npu-cpu/)** — nand2tetris의 상향식 여정(게이트→ALU→CPU→어셈블러→VM→컴파일러→OS)을 Lean4 증명과 MLIR/CIRCT 방출로 쌓는 책
- **[nand2npu 2권: NPU에서 미니 GPU로](nand2npu-gpu/)** — 1권의 CPU 위에 프로그램 가능한 병렬 코어(SIMT)를 얹어 레인·발산·워프 스케줄링·공유 메모리·타일링·멀티코어 동기화를 증명하고, 그 유연성의 비용을 직접 측정하는 책
- **[nand2npu 3권: NPU로 이미지 처리하고 마리오 플레이하기](nand2npu-vision/)** — 2권의 경험을 바탕으로 행렬 곱셈 하나에 특화된 고정 기능 NPU(MAC 유닛·시스톨릭 어레이·양자화)를 만든 뒤, 이미지 분류 워밍업을 거쳐 마리오를 플레이하는 강화학습 정책망의 추론까지 NPU 위에서 증명·검증하는 책
- **[nand2npu 4권: NPU에서 트랜스포머로](nand2npu-transformer/)** — 2권의 GPU 코어와 3권의 NPU를 재사용해 어텐션(Q/K/V, softmax 근사, 멀티헤드, KV 캐시)을 짓고, 깊은 레이어에 걸친 오차 전파를 완성한 뒤 미니 문자 단위 트랜스포머로 실제로 텍스트를 생성하는 책
- **[함수형 프로그래밍으로 보는 비동기의 근간](fp-backbone-of-async/)** — Python의 async/await, Monad, Functor, Applicative, Observable이 사실은 함수형 프로그래밍의 오래된 개념 위에 서 있다는 것을 따라가는 책
- **[SICP in Lean 4](sicp-in-lean4/)** — SICP의 아이디어를 챕터·절 순서대로 따라가며, 모든 Scheme 코드를 Lean 4로 다시 작성해보는 책
- **[Category Theory for Programmers](category-theory-for-programmers/)** — Bartosz Milewski가 프로그래머를 위해 쓴 범주론 입문서를 장별로 옮긴 한국어 번역
- **[TypeScript + React 입문: react.dev와 Handbook을 왜라는 질문으로 잇기](ts-react-getting-started/)** — 공식 React 문서와 TypeScript Handbook을 재료로 "왜 이렇게 생겼는가"를 축으로 재구성한 입문서. 값과 타입(1부) → 컴포넌트·State·렌더링·useRef(2부) → API 호출·폼·React Router로 합치기(3부) 순서로 쌓아 올린다
- **[타입으로 설계하기: 모나드, 상태 기계, 시제논리](type-driven-design/)** — 엘리베이터 하나를 처음부터 끝까지 함께 설계·구현·증명하며, 대수적 데이터 타입·모나드(1부)로 합성을 다지고, 상태 기계를 순수 함수(coalgebra)로 다루는 법(2부)을 거쳐, 그렇게 만든 시스템이 시간에 걸쳐 만족해야 할 성질을 LTL·CTL로 명세·증명하는(3부) Lean4 책
- **[관계, 명제, 그리고 작은 언어: Lean4로 짓는 프로그램 의미론](lean4-program-semantics/)** — 정리 증명 기초(1부) 위에 관계·귀납적 명제·맵이라는 세 도구를 준비하고(2부), 작은 명령형 언어를 직접 지어 그 실행을 조작적 의미론으로 정의하고 결정성·동치를 증명한 뒤(3부), 증명 항·나만의 귀납 원리·호어 논리로 마무리하는(4부) 독립적인 Lean4 입문서
- **[Mathlib으로 수학하기](mathlib-mathematics/)** — 증명 기본기(1부) 위에 집합과 함수(2부), 정수론(3부), 군과 순서 구조(4부), 벡터공간과 선형사상(5부), 수열의 극한과 연속함수(6부)를 Mathlib으로 직접 증명하며 다지는 독립적인 Lean4 입문서
- **[AsciiDoc 제대로 배우기](asciidoc-getting-started/)** — 기초 문법(1부) → 문서 구조화(2부) → 코드와 재사용(3부) → 실전 활용(4부) 순서로, 이 사이트의 모든 책이 실제로 쓰는 태그·include 조립 방식을 직접 뜯어보며 배우는 AsciiDoc 입문서
- **[확률, 넓이로 재다](probability-with-mathlib/)** — "확률은 넓이다"라는 그림을 축으로 이산 확률(1부) → 일반 확률공간(2부) → 기댓값과 구조(3부) → 극한정리(4부)를 Mathlib으로 직접 증명하며 다지는 독립적인 확률론 Lean4 입문서
- **[화살표로 생각하기](category-theory-made-simple/)** — 코드 없이 일상적인 비유와 그림만으로 범주론을 쉽게 푸는 독립적인 입문서. 기초(1부: 범주·함수자·자연변환) → 구조(2부: 곱과 합·보편성질) → 응용(3부: 모나드·프로그래밍이 사실 범주다·범주론이 잇는 세계들) → 심화(4부: 극한과 쌍대극한·요네다 렘마·수반)
