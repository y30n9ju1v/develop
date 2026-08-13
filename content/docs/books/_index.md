---
title: "Books"
---

이해하고 싶은 책을 직접 번역했거나, AI에게 책으로 써달라고 요청해서 만든 기록입니다.

## Lean4와 형식 증명

- **[Lean4 입문: 함수형 프로그래밍에서 증명, 메타프로그래밍까지](lean4-and-proofs/lean4-getting-started/)** — Functional Programming in Lean, Theorem Proving in Lean 4, Metaprogramming in Lean 4 세 권을 초보자용으로 이어 읽을 수 있게 새로 쓴 책. 왜 배우는지부터 시작해 값·재귀·자료구조·모나드(1부) → 명제-타입 대응·전술·귀납 증명(2부) → 매크로·나만의 tactic(3부) 순서로 쌓아 올린다
- **[Lean4로 증명하는 응용 선형대수](lean4-and-proofs/linalg-in-lean4/)** — 벡터의 덧셈에서 시작해 내적·노름·코시-슈바르츠 부등식·선형독립을 Lean4로 직접 증명하며 쌓는, VMLS류 응용 선형대수 커리큘럼을 새로 쓴 책 (1부: 벡터)
- **[타입으로 설계하기: 모나드, 상태 기계, 시제논리](lean4-and-proofs/type-driven-design/)** — 엘리베이터 하나를 처음부터 끝까지 함께 설계·구현·증명하며, 대수적 데이터 타입·모나드(1부)로 합성을 다지고, 상태 기계를 순수 함수(coalgebra)로 다루는 법(2부)을 거쳐, 그렇게 만든 시스템이 시간에 걸쳐 만족해야 할 성질을 LTL·CTL로 명세·증명하는(3부) Lean4 책
- **[관계, 명제, 그리고 작은 언어: Lean4로 짓는 프로그램 의미론](lean4-and-proofs/lean4-program-semantics/)** — 정리 증명 기초(1부) 위에 관계·귀납적 명제·맵이라는 세 도구를 준비하고(2부), 작은 명령형 언어를 직접 지어 그 실행을 조작적 의미론으로 정의하고 결정성·동치를 증명한 뒤(3부), 증명 항·나만의 귀납 원리·호어 논리로 마무리하는(4부) 독립적인 Lean4 입문서
- **[Mathlib으로 수학하기](lean4-and-proofs/mathlib-mathematics/)** — 증명 기본기(1부) 위에 집합과 함수(2부), 정수론(3부), 군과 순서 구조(4부), 벡터공간과 선형사상(5부), 수열의 극한과 연속함수(6부)를 Mathlib으로 직접 증명하며 다지는 독립적인 Lean4 입문서
- **[확률, 넓이로 재다](lean4-and-proofs/probability-with-mathlib/)** — "확률은 넓이다"라는 그림을 축으로 이산 확률(1부) → 일반 확률공간(2부) → 기댓값과 구조(3부) → 극한정리(4부)를 Mathlib으로 직접 증명하며 다지는 독립적인 확률론 Lean4 입문서
- **[SICP in Lean 4](lean4-and-proofs/sicp-in-lean4/)** — SICP의 아이디어를 챕터·절 순서대로 따라가며, 모든 Scheme 코드를 Lean 4로 다시 작성해보는 책
- **[자원은 한 번만 쓴다: 선형 타입과 세션 타입](lean4-and-proofs/linear-and-session-types/)** — 왜 선형성인가(1부) → 선형 타입 시스템 증명하기(2부) → 세션 타입으로(3부) → 종합과 확장(4부)까지, 컨텍스트를 쪼개는 선형 람다계산법의 Progress 정리와 세션 타입의 교착 없음(session_progress) 정리를 Lean4로 공리 없이 완전히 증명하고, nand2npu-gpu가 조작적 의미론으로 증명했던 배리어 교착을 타입 이론의 눈으로 다시 읽는 독립적인 타입 이론 입문서

## 범주론과 함수형 프로그래밍

- **[Category Theory for Programmers](category-theory-and-fp/category-theory-for-programmers/)** — Bartosz Milewski가 프로그래머를 위해 쓴 범주론 입문서를 장별로 옮긴 한국어 번역
- **[화살표로 생각하기](category-theory-and-fp/category-theory-made-simple/)** — 코드 없이 일상적인 비유와 그림만으로 범주론을 쉽게 푸는 독립적인 입문서. 기초(1부: 범주·함수자·자연변환) → 구조(2부: 곱과 합·보편성질) → 응용(3부: 모나드·프로그래밍이 사실 범주다·범주론이 잇는 세계들) → 심화(4부: 극한과 쌍대극한·요네다 렘마·수반)
- **[함수형 프로그래밍으로 보는 비동기의 근간](category-theory-and-fp/fp-backbone-of-async/)** — Python의 async/await, Monad, Functor, Applicative, Observable이 사실은 함수형 프로그래밍의 오래된 개념 위에 서 있다는 것을 따라가는 책

## nand2npu 시리즈

- **[nand2npu 1권: Lean4로 증명하며 게이트에서 컴퓨터까지](nand2npu-series/nand2npu-cpu/)** — nand2tetris의 상향식 여정(게이트→ALU→CPU→어셈블러→VM→컴파일러→OS)을 Lean4 증명과 MLIR/CIRCT 방출로 쌓는 책
- **[nand2npu 2권: NPU에서 미니 GPU로](nand2npu-series/nand2npu-gpu/)** — 1권의 CPU 위에 프로그램 가능한 병렬 코어(SIMT)를 얹어 레인·발산·워프 스케줄링·공유 메모리·타일링·멀티코어 동기화를 증명하고, 그 유연성의 비용을 직접 측정하는 책
- **[nand2npu 3권: NPU로 이미지 처리하고 마리오 플레이하기](nand2npu-series/nand2npu-vision/)** — 2권의 경험을 바탕으로 행렬 곱셈 하나에 특화된 고정 기능 NPU(MAC 유닛·시스톨릭 어레이·양자화)를 만든 뒤, 이미지 분류 워밍업을 거쳐 마리오를 플레이하는 강화학습 정책망의 추론까지 NPU 위에서 증명·검증하는 책
- **[nand2npu 4권: NPU에서 트랜스포머로](nand2npu-series/nand2npu-transformer/)** — 2권의 GPU 코어와 3권의 NPU를 재사용해 어텐션(Q/K/V, softmax 근사, 멀티헤드, KV 캐시)을 짓고, 깊은 레이어에 걸친 오차 전파를 완성한 뒤 미니 문자 단위 트랜스포머로 실제로 텍스트를 생성하는 책

## 3DGS 기반 자율주행 E2E 검증

- **[사진에서 세계로](3dgs-autonomous-driving-e2e/multiview-geometry-3d-reconstruction/)** — 3DGS 기반 자율주행 E2E 검증 시리즈의 첫 책. 카메라 모델(1부) → 두 장 사진의 기하학(2부) → Structure-from-Motion(3부) → SLAM(4부) → 3DGS를 향하여(5부)까지, 멀티뷰 기하학의 핵심 계산을 NumPy/SciPy로 직접 구현하고 검증하며 배우는 입문서
- **[미분가능 렌더링과 3D Gaussian Splatting](3dgs-autonomous-driving-e2e/differentiable-rendering-3dgs/)** — 3DGS 기반 자율주행 E2E 검증 시리즈의 두 번째 책. 1권이 재구성한 카메라와 점군을 이어받아, 왜 미분해야 하는가(1부) → 볼륨 렌더링/NeRF(2부) → 3DGS 표현(3부) → 최적화로 학습(4부) → 품질과 다음 단계(5부)까지 PyTorch 없이 NumPy만으로 순전파·역전파를 손으로 구현하며 배우는 입문서
- **[센서 퓨전에서 궤적 생성까지: E2E 자율주행 모델 바닥부터 짓기](3dgs-autonomous-driving-e2e/e2e-autonomous-driving-from-scratch/)** — 3DGS 기반 자율주행 E2E 검증 시리즈의 세 번째 책. 센서와 좌표계(1부) → BEV 공간 융합(2부) → Transformer BEV 인코더(3부) → Planning Head와 궤적 생성(4부) → 종합과 평가(5부)까지, 좌표 변환·BEV 융합은 NumPy로, BEVFormer 스타일 인코더와 Planning Head는 PyTorch로 실제 학습시키며 센서에서 궤적까지 E2E 자율주행 모델을 바닥부터 구현하는 입문서
- **[닮았다는 걸 어떻게 잴까: 3DGS와 생성 이미지의 품질 평가 입문](3dgs-autonomous-driving-e2e/image-fidelity-metrics/)** — 픽셀 기반 지표: MSE·PSNR(1부) → 구조를 보는 지표: SSIM(2부) → 사람처럼 보는 지표: 지각적 유사도/LPIPS 아이디어(3부) → 이미지 집합을 비교하는 지표: FID(4부) → 3DGS 렌더링에 적용하기(5부)까지, 이미지가 숫자 배열이라는 사실 하나에서 출발해 모든 지표를 NumPy/SciPy로 직접 구현하고, 같은 PSNR을 가진 흐림과 노이즈를 SSIM은 구별해내지만 색 채널이 뒤바뀌는 렌더링 버그는 PSNR도 SSIM도 전혀 잡지 못한다는 것을 실제 계산으로 확인하며 "어떤 지표도 혼자서는 충분하지 않다"는 것을 체감하는 독립적인 입문서
- **[흔들리는 로그를 선명한 3DGS로: 시간 정렬과 extrinsic 재최적화](3dgs-autonomous-driving-e2e/sensor-sync-extrinsic-refinement/)** — 문제 진단: 왜 3DGS가 무너지는가(1부) → 시간 정렬: 보간·오프셋 추정·검증(2부) → extrinsic 드리프트 보정: 포즈 그래프·리그 제약·루프 클로저(3부) → 통합과 검증: 파이프라인 통합·품질 게이트·종합 실전(4부)까지, 타임싱크가 어긋나고 프레임마다 자세가 흔들리는 자율주행 센서 로그를 NumPy/SciPy로 직접 정제해 재투영 오차를 8.7배 줄이는 실무 지향적 파이프라인을 "회전은 왜 어려운가"·"모르는 곳에서 나를 찾는 법" 책의 SE(3) 최적화 도구로 완성하는 독립적인 입문서

## SLAM과 로보틱스

- **[모르는 곳에서 나를 찾는 법: 필터와 그래프로 배우는 SLAM](slam-and-robotics/slam-filters-and-graphs/)** — 1권 "사진에서 세계로"의 SLAM 개요를 깊게 판 심화편. 확률적 상태 추정 기초(1부) → EKF-SLAM(2부) → 파티클 필터와 FastSLAM(3부) → 그래프 기반 SLAM(4부) → 매핑과 통합(5부)까지, SLAM의 세 가지 주요 패러다임(필터·파티클·그래프)을 NumPy/SciPy로 직접 구현하고 시뮬레이션으로 검증하며 배우는 독립적인 입문서
- **[회전은 왜 어려운가: 리 군과 리 대수로 로봇 자세 다루기](slam-and-robotics/lie-groups-for-robotics/)** — 앞선 SLAM 책이 2D 평면에 한정하며 남겨둔 3D 회전 문제를 정면으로 다루는 심화편. 회전 표현의 문제(1부) → 리 군과 리 대수(2부) → SE(3)와 강체 운동(3부) → 접평면 위의 최적화(4부) → IMU와 3D SLAM 실전(5부)까지, SO(3)·SE(3)를 NumPy/SciPy로 직접 구현하고 검증하며 배우는 독립적인 입문서

## 시스템·병렬 프로그래밍

- **[언어를 처음부터 끝까지: MLIR로 짓는 작은 함수형 언어](systems-and-parallel-programming/building-a-language-from-scratch/)** — 렉싱과 파싱(1부) → 평가와 타입(2부) → 함수·클로저·다형성(3부) → MLIR로 코드 생성하기(4부) → 종합과 확장(5부)까지, 작은 정적 타입 함수형 언어 Twig를 Python으로 구현하고 실제 mlir-opt/mlir-runner로 낮추고 JIT 실행까지 검증하는 독립적인 컴파일러 입문서
- **[이론을 C++23으로 옮기다: 안전한 병렬 프로그래밍](systems-and-parallel-programming/safe-parallel-cpp23/)** — 왜 안전하지 않은가(1부) → 타입 상태로 세션 타입 흉내내기(2부) → 이동 전용 타입으로 선형성 흉내내기와 락 순서로 교착 상태 막기(3부) → 범주론적 인터페이스와 코루틴으로 병렬 파이프라인 짜기(4부) → 동시성 분리 논리(5부) → CRDT(6부)까지, 1장부터 12장까지 하나의 예제 시스템 TaskGrid를 한 조각씩 함께 완성해 나가며 선형 타입·세션 타입·범주론이라는 이론을 타입 상태 패턴·이동 전용 타입·`std::scoped_lock`·코루틴·`std::span` 분할·concepts·join-semilattice로 실제 C++23(Apple Clang 21) 코드로 인코딩해 컴파일 타임/TSan·ASan 검증으로 병렬 버그를 잡고, 맺음말에서 Rust가 이 이론들 중 무엇을 언어 코어로 채용했는지(RustBelt의 형식 증명, 그리고 CRDT는 왜 그 질문 자체가 성립하지 않는지)까지 정리하는 독립적인 실무 입문서
- **[OpenCL로 배우는 헤테로지니어스 컴퓨팅: 3DGS와 디지털 트윈까지](systems-and-parallel-programming/heterogeneous-computing-opencl/)** — 호스트-디바이스 분리(1부) → 워크그룹과 SIMT 실행 모델(2부) → 메모리 계층구조(3부) → 3DGS 점군 래스터라이제이션(4부) → 실시간 시뮬레이션 루프(5부)까지, 어떤 GPU에서나 동작하는 개방 표준 OpenCL로 이 세션의 실제 GPU(Apple M4)에서 커널을 직접 컴파일·실행해 계산 강도·전송 손익분기점·분기 발산·배리어 누락·메모리 대역폭 병목을 전부 실측 수치로 확인하고, 타일링으로 행렬곱을 3.4배, 3DGS 래스터라이제이션을 최대 23.8배 가속하는 독립적인 입문서
- **[학습이 끝난 모델을 하드웨어에 맞게 다시 깎는다: ONNX 하드웨어 최적화](systems-and-parallel-programming/onnx-hardware-optimization/)** — 왜 최적화가 필요한가(1부) → 그래프 레벨 최적화(2부) → 양자화(3부) → MLIR lowering(4부) → 커널 최적화와 이기종 스케줄링(5부)까지, ResNet18 하나를 처음부터 끝까지 예제 삼아 onnxruntime과 IREE(MLIR 기반 컴파일러)로 실제 컴파일·실행해서, 연산자 융합은 5%뿐이고 진짜 이득은 레이아웃 변환에서 온다는 것과 동적 양자화가 17배 느려지는데 정적 양자화는 1.86배 빨라진다는 것, 범용 컴파일(344.7ms)과 NPU 위임(0.67ms) 사이에 515배 격차가 있다는 것을 실측하며 정확도 등 검증 못 한 한계까지 정직하게 밝히는 독립적인 입문서

## 웹 개발

- **[TypeScript + React 입문: react.dev와 Handbook을 왜라는 질문으로 잇기](web-development/ts-react-getting-started/)** — 공식 React 문서와 TypeScript Handbook을 재료로 "왜 이렇게 생겼는가"를 축으로 재구성한 입문서. 값과 타입(1부) → 컴포넌트·State·렌더링·useRef(2부) → API 호출·폼·React Router로 합치기(3부) 순서로 쌓아 올린다
- **[자바스크립트 없이도 상호작용하는 웹: Go, templ, htmx로 만드는 하이퍼미디어 서비스](web-development/go-templ-htmx-web/)** — 기초 다지기: net/http와 templ(1부) → htmx로 상호작용 만들기: 부분 갱신·OOB 스왑·폼 검증(2부) → 실전 패턴: 컴포넌트 설계·SQLite·검색·세션 인증(3부) → 완성과 배포: SSE·httptest·종합 실전 TODO 앱(4부)까지, SPA 프레임워크 없이 서버가 HTML을 직접 내려주는 하이퍼미디어 지향 방식을 실제로 서버를 띄우고 curl로 요청·응답을 확인하며 배우는 독립적인 입문서
- **[AsciiDoc 제대로 배우기](web-development/asciidoc-getting-started/)** — 기초 문법(1부) → 문서 구조화(2부) → 코드와 재사용(3부) → 실전 활용(4부) 순서로, 이 사이트의 모든 책이 실제로 쓰는 태그·include 조립 방식을 직접 뜯어보며 배우는 AsciiDoc 입문서

## 응용수학과 데이터

- **[증명보다 계산이 먼저다: 공업수학을 코드로 다시 배우기](applied-math-and-data/engineering-math-in-code/)** — 미분·지수함수·벡터/행렬·복소수를 화살표나 추상적 정의 없이 계산으로 먼저 짚는 수학 준비운동(0부) → 상미분방정식(1부) → 라플라스 변환(2부) → 선형연립방정식(3부) → 고유값과 대각화(4부) → 벡터 미적분(5부) → 푸리에 해석과 편미분방정식(6부) → 복소해석(7부)까지, 정의-정리-증명 순서 대신 "왜 필요한가 → NumPy/SciPy/SymPy로 계산해서 확인 → 수식 읽기" 순서로 공업수학 표준 커리큘럼을 다시 짓는 독립적인 입문서. 매 장마다 손으로 유도한 해석해와 서로 다른 방법으로 얻은 수치해를 교차 검증하고, 장 끝마다 실제로 검증한 "직접 해보기" 연습문제를 둔다
- **[AICE Associate 실전 대비: 데이터에서 모델까지](applied-math-and-data/aice-associate-deep-learning/)** — Pandas 데이터 다루기(1부) → EDA와 머신러닝 기초(2부) → Keras 딥러닝(3부) → 시험형 문제 실전(4부) 순서로, AICE Associate 자격증 실기 범위를 실제 Pandas·scikit-learn·TensorFlow/Keras를 실행해 검증하며 배우는 독립적인 입문서
