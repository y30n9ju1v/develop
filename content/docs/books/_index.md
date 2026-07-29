---
title: "Books"
---

이해하고 싶은 책을 직접 번역했거나, AI에게 책으로 써달라고 요청해서 만든 기록입니다.

- **[Lean4 입문: 함수형 프로그래밍에서 증명, 메타프로그래밍까지](lean4-getting-started/)** — Functional Programming in Lean, Theorem Proving in Lean 4, Metaprogramming in Lean 4 세 권을 초보자용으로 이어 읽을 수 있게 새로 쓴 책. 왜 배우는지부터 시작해 값·재귀·자료구조·모나드(1부) → 명제-타입 대응·전술·귀납 증명(2부) → 매크로·나만의 tactic(3부) 순서로 쌓아 올린다
- **[Lean4로 증명하는 응용 선형대수](linalg-in-lean4/)** — 벡터의 덧셈에서 시작해 내적·노름·코시-슈바르츠 부등식·선형독립을 Lean4로 직접 증명하며 쌓는, VMLS류 응용 선형대수 커리큘럼을 새로 쓴 책 (1부: 벡터)
- **[nand2npu 1권: Lean4로 증명하며 게이트에서 컴퓨터까지](nand2npu/)** — nand2tetris의 상향식 여정(게이트→ALU→CPU→어셈블러→VM→컴파일러→OS)을 Lean4 증명과 MLIR/CIRCT 방출로 쌓는 책
- **[nand2npu 2권: NPU에서 미니 GPU로](nand2npu-gpu/)** — 1권의 CPU 위에 프로그램 가능한 병렬 코어(SIMT)를 얹어 레인·발산·워프 스케줄링·공유 메모리·타일링·멀티코어 동기화를 증명하고, 그 유연성의 비용을 직접 측정하는 책
- **[nand2npu 3권: NPU로 이미지 처리하고 마리오 플레이하기](nand2npu-vision/)** — 2권의 경험을 바탕으로 행렬 곱셈 하나에 특화된 고정 기능 NPU(MAC 유닛·시스톨릭 어레이·양자화)를 만든 뒤, 이미지 분류 워밍업을 거쳐 마리오를 플레이하는 강화학습 정책망의 추론까지 NPU 위에서 증명·검증하는 책
- **[nand2npu 4권: NPU에서 트랜스포머로](nand2npu-transformer/)** — 2권의 GPU 코어와 3권의 NPU를 재사용해 어텐션(Q/K/V, softmax 근사, 멀티헤드, KV 캐시)을 짓고, 깊은 레이어에 걸친 오차 전파를 완성한 뒤 미니 문자 단위 트랜스포머로 실제로 텍스트를 생성하는 책
- **[함수형 프로그래밍으로 보는 비동기의 근간](fp-backbone-of-async/)** — Python의 async/await, Monad, Functor, Applicative, Observable이 사실은 함수형 프로그래밍의 오래된 개념 위에 서 있다는 것을 따라가는 책
- **[SICP in Lean 4](sicp-in-lean4/)** — SICP의 아이디어를 챕터·절 순서대로 따라가며, 모든 Scheme 코드를 Lean 4로 다시 작성해보는 책
- **[Category Theory for Programmers](category-theory-for-programmers/)** — Bartosz Milewski가 프로그래머를 위해 쓴 범주론 입문서를 장별로 옮긴 한국어 번역
- **[Lanelet2를 OpenDRIVE로](lanelet2-to-opendrive/)** — 실차 자율주행 스택의 Lanelet2 HD맵을 3DGS 시뮬레이션 회귀 테스트용 OpenDRIVE로 변환하는 파이프라인을, IR 설계부터 참조선 피팅·중심선·클로소이드·그룹핑·교차로·검증까지 순서대로 설명하는 책
