---
title: "Books"
---

AI와 함께 쓴 학습 기록입니다. 폴더 경로와 달리 이 목록은 **책을 끝냈을 때 얻는 역량**으로 묶었습니다. 대부분은 독립적으로 읽을 수 있고, 순서가 중요한 책만 시리즈로 표시합니다.

## 형식화·증명

코드와 수학 명제를 Lean4로 표현하고, 실제로 컴파일되는 증명을 쓰는 법을 배웁니다.

- **[Lean4 입문: 함수형 프로그래밍에서 증명, 메타프로그래밍까지](lean4-and-proofs/lean4-getting-started/)** — 값·재귀·모나드에서 정리 증명과 매크로·전술까지 Lean4의 기본 언어를 한 흐름으로 익히는 입문서
- **[Lean4로 증명하는 응용 선형대수](lean4-and-proofs/linalg-in-lean4/)** — 벡터·내적·노름·선형독립을 Lean4 증명으로 옮기는 응용 선형대수 실습서
- **[타입으로 설계하기: 모나드, 상태 기계, 시제논리](lean4-and-proofs/type-driven-design/)** — 엘리베이터 예제로 타입, 상태 기계, LTL·CTL 명세를 설계와 증명에 연결하는 책
- **[관계, 명제, 그리고 작은 언어: Lean4로 짓는 프로그램 의미론](lean4-and-proofs/lean4-program-semantics/)** — 작은 명령형 언어의 실행 의미와 결정성·동치·호어 논리를 직접 증명하는 입문서
- **[Mathlib으로 수학하기](lean4-and-proofs/mathlib-mathematics/)** — 집합·정수론·대수 구조·해석학의 기초를 Mathlib 정리로 증명하는 법을 익히는 책
- **[확률, 넓이로 재다](lean4-and-proofs/probability-with-mathlib/)** — 이산 확률에서 일반 확률공간과 극한정리까지를 Mathlib으로 형식화하는 입문서
- **[SICP in Lean 4](lean4-and-proofs/sicp-in-lean4/)** — SICP의 계산 모델과 프로그램 설계 아이디어를 Lean4 코드로 다시 구현하는 책
- **[자원은 한 번만 쓴다: 선형 타입과 세션 타입](lean4-and-proofs/linear-and-session-types/)** — 선형 람다계산과 세션 타입의 안전성·교착 없음 성질을 Lean4로 증명하는 타입 이론 입문서

## 계산 이론·함수형 사고·수학

계산의 한계와 구조를 이해하고, 알고리즘·정보·수학을 더 엄밀하게 생각하는 법을 다룹니다.

- **[Category Theory for Programmers](category-theory-and-fp/category-theory-for-programmers/)** — 프로그래밍의 합성과 타입을 범주론의 언어로 연결하는 한국어 번역 자료
- **[함수형 프로그래밍으로 보는 비동기의 근간](category-theory-and-fp/fp-backbone-of-async/)** — Python async/await와 TypeScript Promise를 Functor·Applicative·Monad 관점으로 해석하는 실습서
- **[람다 계산법과 계산 가능성](category-theory-and-fp/lambda-calculus-and-computability/)** — 람다 계산, 튜링 기계, 정지 문제를 통해 계산 가능한 것의 경계를 이해하는 입문서
- **[함수형 사고로 알고리즘 다시 보기](category-theory-and-fp/functional-thinking-for-algorithms/)** — 재귀·귀납·불변식으로 정렬, 자료구조, 동적 계획법, 그래프 알고리즘을 설명하는 책
- **[P vs NP](category-theory-and-fp/p-vs-np/)** — 다항 시간, 환원, NP-완전성과 미해결 문제의 의미를 실험과 함께 다루는 입문서
- **[정보 이론 (섀넌)](category-theory-and-fp/shannon-information-theory/)** — 엔트로피·압축·채널 용량·오류 정정을 실제 계산으로 확인하는 책
- **[괴델의 불완전성 정리](category-theory-and-fp/godels-incompleteness-theorems/)** — 괴델 수, 자기지시, 불완전성과 정지 문제의 연결을 따라가는 입문서
- **[증명보다 계산이 먼저다: 공업수학을 코드로 다시 배우기](applied-math-and-data/engineering-math-in-code/)** — 미분방정식·선형대수·푸리에·복소해석을 계산과 수치 검증으로 먼저 배우는 공업수학 책

## 시스템·언어·하드웨어

언어 구현, 안전한 동시성, 성능 측정, GPU와 추론 런타임을 실제 시스템으로 만듭니다.

- **[언어를 처음부터 끝까지: MLIR로 짓는 작은 함수형 언어](systems-and-parallel-programming/building-a-language-from-scratch/)** — 파서·타입 검사·클로저·MLIR 코드 생성을 거쳐 작은 언어를 완성하는 컴파일러 입문서
- **[이론을 C++23으로 옮기다: 안전한 병렬 프로그래밍](systems-and-parallel-programming/safe-parallel-cpp23/)** — 타입 상태, 락, 코루틴, CRDT로 병렬 프로그램의 안전성을 설계하는 C++23 책
- **[안전을 넘어 성능으로: C++23 최적화 기법](systems-and-parallel-programming/cpp23-performance-engineering/)** — 메모리 배치·할당·뷰·컴파일 타임 계산을 벤치마크로 검증하는 C++23 성능 책
- **[OpenCL로 배우는 헤테로지니어스 컴퓨팅: 3DGS와 디지털 트윈까지](systems-and-parallel-programming/heterogeneous-computing-opencl/)** — GPU 실행 모델·메모리 계층·타일링을 OpenCL 커널과 실측으로 익히는 책
- **[복사 없는 GPU 프로그래밍: MLX로 배우는 Apple Silicon 최적화](systems-and-parallel-programming/mlx-apple-silicon-optimization/)** — Apple Silicon에서 자동미분·지연 평가·통합 메모리의 성능 특성을 MLX로 검증하는 책
- **[학습이 끝난 모델을 하드웨어에 맞게 다시 깎는다: ONNX 하드웨어 최적화](systems-and-parallel-programming/onnx-hardware-optimization/)** — 그래프 최적화·양자화·MLIR·이기종 실행으로 모델 추론을 최적화하는 실습서
- **[TinyRT: 안전하고 빠른 CPU/GPU 추론 런타임](systems-and-parallel-programming/tinyrt-cpu-gpu-inference/)** — CPU/GPU 배치와 안전한 자원 관리를 갖춘 작은 CNN 추론 런타임을 만드는 캡스톤
- **[MarioRL: Apple Silicon 위에서 짓는 병렬 강화학습 프레임워크](systems-and-parallel-programming/mario-rl-framework/)** — 병렬 롤아웃, MLX 학습, CPU/GPU 배치를 조합한 강화학습 실행 프레임워크 캡스톤
- **[RIIR: C의 JSON 파서를 Rust로 다시 쓰고 Python에 배포하기](systems-and-parallel-programming/riir-json-parser/)** — Rust로 JSON 파서를 구현·측정하고 PyO3와 wheel로 Python 패키지까지 배포하는 실무 입문서

## AI·데이터·강화학습

데이터 분석과 학습 알고리즘을 직접 실행해 모델이 학습하고 평가되는 과정을 다룹니다.

- **[AICE Associate 실전 대비: 데이터에서 모델까지](applied-math-and-data/aice-associate-deep-learning/)** — Pandas·EDA·scikit-learn·Keras를 이용해 데이터에서 모델까지 완주하는 시험·실습형 입문서
- **[보상만으로 배운다: 강화학습을 밑바닥부터 마리오까지](machine-learning-and-rl/reward-only-rl-from-scratch/)** — 표 기반 방법부터 DQN·PPO와 마리오 환경 실습까지 강화학습의 전체 흐름을 구현하는 책

## 로보틱스·비전·3D

카메라 관측을 3차원 장면·로봇 상태·자율주행 검증으로 연결합니다.

- **[사진에서 세계로](3dgs-autonomous-driving-e2e/multiview-geometry-3d-reconstruction/)** — 카메라 모델·에피폴라 기하학·SfM·번들 조정으로 사진에서 점군을 복원하는 입문서
- **[미분가능 렌더링과 3D Gaussian Splatting](3dgs-autonomous-driving-e2e/differentiable-rendering-3dgs/)** — 볼륨 렌더링·3DGS 학습·품질 평가·SfM 초기화를 NumPy로 구현하는 책
- **[센서 퓨전에서 궤적 생성까지: E2E 자율주행 모델 바닥부터 짓기](3dgs-autonomous-driving-e2e/e2e-autonomous-driving-from-scratch/)** — 센서 융합, BEV 인코더, 계획 헤드를 조합해 E2E 자율주행 모델을 만드는 입문서
- **[흔들리는 로그를 선명한 3DGS로: 시간 정렬과 extrinsic 재최적화](3dgs-autonomous-driving-e2e/sensor-sync-extrinsic-refinement/)** — 시간 오프셋과 외부 파라미터 드리프트를 진단·보정하는 센서 로그 정제 실습서
- **[모델이 나빠졌는지 사람이 눈으로 보지 않고 아는 법: 3DGS/E2E 회귀 테스트 파이프라인](3dgs-autonomous-driving-e2e/regression-testing-pipeline/)** — 품질 지표, 통계 판정, CI/CD를 묶어 3DGS·E2E 모델 회귀를 자동 감시하는 운영 책
- **[모르는 곳에서 나를 찾는 법: 필터와 그래프로 배우는 SLAM](slam-and-robotics/slam-filters-and-graphs/)** — EKF·파티클 필터·그래프 최적화로 SLAM의 주요 접근을 구현하는 책
- **[회전은 왜 어려운가: 리 군과 리 대수로 로봇 자세 다루기](slam-and-robotics/lie-groups-for-robotics/)** — SO(3)·SE(3), 접평면 최적화, IMU를 통해 3차원 자세 추정을 다루는 입문서
- **[브라우저로 확인하는 3D: Viser로 만드는 로보틱스/비전 뷰어 입문](slam-and-robotics/viser-3d-visualization-for-robotics/)** — 포즈·점군·궤적·Gaussian을 브라우저에서 검사하는 Viser 실습서

## 웹·개발 도구

사용자 인터페이스, 서버 렌더링, 문서화, 테스트 자동화처럼 제품을 완성하는 도구를 다룹니다.

- **[TypeScript + React 입문: react.dev와 Handbook을 왜라는 질문으로 잇기](web-development/ts-react-getting-started/)** — TypeScript의 타입과 React의 렌더링·상태·라우팅을 함께 익히는 입문서
- **[자바스크립트 없이도 상호작용하는 웹: Go, templ, htmx로 만드는 하이퍼미디어 서비스](web-development/go-templ-htmx-web/)** — 서버가 HTML을 직접 제공하는 Go·templ·htmx 서비스와 테스트·배포를 만드는 책
- **[AsciiDoc 제대로 배우기](web-development/asciidoc-getting-started/)** — 문서 구조, include, 코드 조각 재사용으로 실행 가능한 기술 문서를 작성하는 입문서
- **[Playwright와 크로미움 익스텐션으로 배우는 하이브리드 자동화](web-development/playwright-extension-hybrid-automation/)** — 연습용 사이트에서 브라우저 자동화와 확장 프로그램 기반 보조를 설계·검증하는 실습서
- **[미니 정적 사이트 생성기로 배우는 TypeScript](web-development/typescript-mini-ssg/)** — 타입 안전한 Markdown 처리와 빌드를 통해 TypeScript의 실전 타입 설계를 익히는 책

## 순서가 있는 시리즈

아래 책들은 앞 권의 산출물을 이어받으므로 권 번호 순서로 읽는 편이 좋습니다.

- **[nand2npu 1권: Lean4로 증명하며 게이트에서 컴퓨터까지](nand2npu-series/nand2npu-cpu/)** — 게이트에서 CPU·컴파일러·OS까지를 Lean4 증명과 MLIR/CIRCT 출력으로 쌓는 출발점
- **[nand2npu 2권: NPU에서 미니 GPU로](nand2npu-series/nand2npu-gpu/)** — 1권의 CPU 위에 SIMT 코어와 메모리·동기화 모델을 확장하는 책
- **[nand2npu 3권: NPU로 이미지 처리하고 마리오 플레이하기](nand2npu-series/nand2npu-vision/)** — NPU 설계와 강화학습 정책망 추론을 결합해 이미지·게임 작업을 실행하는 책
- **[nand2npu 4권: NPU에서 트랜스포머로](nand2npu-series/nand2npu-transformer/)** — GPU·NPU 구성 요소를 재사용해 어텐션과 미니 트랜스포머 추론을 구현하는 책
