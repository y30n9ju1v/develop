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
- **[화살표로 생각하기](category-theory-and-fp/category-theory-made-simple/)** — 본문은 코드 없이 일상적인 비유와 그림만으로 범주론을 쉽게 푸는 독립적인 입문서. 기초(1부: 범주·함수자·자연변환) → 구조(2부: 곱과 합·보편성질) → 응용(3부: 모나드·프로그래밍이 사실 범주다·범주론이 잇는 세계들) → 심화(4부: 극한과 쌍대극한·요네다 렘마·수반), 맺음말 뒤 설문 응답 파이프라인으로 핵심 개념을 파이썬으로 다시 확인하는 짧은 부록까지
- **[함수형 프로그래밍으로 보는 비동기의 근간](category-theory-and-fp/fp-backbone-of-async/)** — Python의 async/await, Monad, Functor, Applicative, Observable이 사실은 함수형 프로그래밍의 오래된 개념 위에 서 있다는 것을 따라가고, 마지막 장에서 그 패턴이 TypeScript의 Promise에서도 그대로 성립하는지(단, 구조적 동시성처럼 언어마다 보장 수준이 다른 지점도 있는지) 실제 컴파일·실행으로 검증하는 책

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
- **[모델이 나빠졌는지 사람이 눈으로 보지 않고 아는 법: 3DGS/E2E 회귀 테스트 파이프라인](3dgs-autonomous-driving-e2e/regression-testing-pipeline/)** — 문제 정의: "회귀"란 무엇인가(1부) → 파이프라인 아키텍처: kind 클러스터·베이스라인 데이터셋·컨테이너화·Argo Workflow DAG(2부) → 자동화·비교·시각화: 지표 계산·통계적 회귀 탐지·CI/CD 연동·Rerun 시각화(3부) → 운영과 실전: 플레이키 테스트·클라우드 스케일링·종합 실전·폐루프 주행 평가 지표(4부)까지, "닮았다는 걸 어떻게 잴까"의 이미지 품질 지표와 "흔들리는 로그를 선명한 3DGS로"의 포즈 오차 지표를 재사용해 새 체크포인트가 나올 때마다 실제로 동작하는 kind/Argo Workflows/Rerun 매니페스트로 회귀를 자동 판정하는 실무 지향적인 후속편

## SLAM과 로보틱스

- **[모르는 곳에서 나를 찾는 법: 필터와 그래프로 배우는 SLAM](slam-and-robotics/slam-filters-and-graphs/)** — 1권 "사진에서 세계로"의 SLAM 개요를 깊게 판 심화편. 확률적 상태 추정 기초(1부) → EKF-SLAM(2부) → 파티클 필터와 FastSLAM(3부) → 그래프 기반 SLAM(4부) → 매핑과 통합(5부)까지, SLAM의 세 가지 주요 패러다임(필터·파티클·그래프)을 NumPy/SciPy로 직접 구현하고 시뮬레이션으로 검증하며 배우는 독립적인 입문서
- **[회전은 왜 어려운가: 리 군과 리 대수로 로봇 자세 다루기](slam-and-robotics/lie-groups-for-robotics/)** — 앞선 SLAM 책이 2D 평면에 한정하며 남겨둔 3D 회전 문제를 정면으로 다루는 심화편. 회전 표현의 문제(1부) → 리 군과 리 대수(2부) → SE(3)와 강체 운동(3부) → 접평면 위의 최적화(4부) → IMU와 3D SLAM 실전(5부)까지, SO(3)·SE(3)를 NumPy/SciPy로 직접 구현하고 검증하며 배우는 독립적인 입문서
- **[브라우저로 확인하는 3D: Viser로 만드는 로보틱스/비전 뷰어 입문](slam-and-robotics/viser-3d-visualization-for-robotics/)** — 컴퓨터 비전과 로보틱스 파이프라인의 중간 결과(카메라 포즈·포인트클라우드·3DGS 결과·로봇 궤적)를 파이썬 몇 줄로 브라우저에 띄워 확인하는 라이브러리 Viser 입문서. 첫 장면 띄우기(1부) → 좌표 프레임·카메라 프러스텀(2부) → 메시·조명·GUI 상호작용(3부) → 대량 데이터와 3D Gaussian Splats(4부) → 시간에 따른 재생(5부) → 재구성 결과 뷰어 앱(6부)까지, 모든 예제가 실제로 `viser.ViserServer()`를 띄우고 씬 트리 배선을 `assert`로 검증하는 독립적인 입문서

## 시스템·병렬 프로그래밍

- **[언어를 처음부터 끝까지: MLIR로 짓는 작은 함수형 언어](systems-and-parallel-programming/building-a-language-from-scratch/)** — 렉싱과 파싱(1부) → 평가와 타입(2부) → 함수·클로저·다형성(3부) → MLIR로 코드 생성하기(4부) → 종합과 확장(5부)까지, 작은 정적 타입 함수형 언어 Twig를 Python으로 구현하고 실제 mlir-opt/mlir-runner로 낮추고 JIT 실행까지 검증하는 독립적인 컴파일러 입문서
- **[이론을 C++23으로 옮기다: 안전한 병렬 프로그래밍](systems-and-parallel-programming/safe-parallel-cpp23/)** — 왜 안전하지 않은가(1부) → 타입 상태로 세션 타입 흉내내기(2부) → 이동 전용 타입으로 선형성 흉내내기와 락 순서로 교착 상태 막기(3부) → 범주론적 인터페이스와 코루틴으로 병렬 파이프라인 짜기(4부) → 동시성 분리 논리(5부) → CRDT(6부)까지, 1장부터 12장까지 하나의 예제 시스템 TaskGrid를 한 조각씩 함께 완성해 나가며 선형 타입·세션 타입·범주론이라는 이론을 타입 상태 패턴·이동 전용 타입·`std::scoped_lock`·코루틴·`std::span` 분할·concepts·join-semilattice로 실제 C++23(Apple Clang 21) 코드로 인코딩해 컴파일 타임/TSan·ASan 검증으로 병렬 버그를 잡고, 맺음말에서 Rust가 이 이론들 중 무엇을 언어 코어로 채용했는지(RustBelt의 형식 증명, 그리고 CRDT는 왜 그 질문 자체가 성립하지 않는지)까지 정리하는 독립적인 실무 입문서
- **[안전을 넘어 성능으로: C++23 최적화 기법](systems-and-parallel-programming/cpp23-performance-engineering/)** — 『이론을 C++23으로 옮기다』의 후속편. `std::mdspan`으로 캐시 친화적인 `BatchBuffer`를 만들고(1부), `deducing this`와 `consteval`로 `TransformWorker`를 완성하고(2부), `atomic_ref`로 진행률을 추적하고(3부), `allocate_at_least`와 PMR 아레나로 할당 병목을 없애고(4부), `flat_map`과 `views::zip`으로 보고 경로를 마무리하는(5부) 것까지, 매 장이 이전 장의 코드를 그대로 확장해 하나의 `PerfGrid` 시스템을 조립하고 순진한 버전과 나란히 벤치마크하는(6부) 독립적인 입문서
- **[OpenCL로 배우는 헤테로지니어스 컴퓨팅: 3DGS와 디지털 트윈까지](systems-and-parallel-programming/heterogeneous-computing-opencl/)** — 호스트-디바이스 분리(1부) → 워크그룹과 SIMT 실행 모델(2부) → 메모리 계층구조(3부) → 3DGS 점군 래스터라이제이션(4부) → 실시간 시뮬레이션 루프(5부)까지, 어떤 GPU에서나 동작하는 개방 표준 OpenCL로 이 세션의 실제 GPU(Apple M4)에서 커널을 직접 컴파일·실행해 계산 강도·전송 손익분기점·분기 발산·배리어 누락·메모리 대역폭 병목을 전부 실측 수치로 확인하고, 타일링으로 행렬곱을 3.4배, 3DGS 래스터라이제이션을 최대 23.8배 가속하는 독립적인 입문서
- **[복사 없는 GPU 프로그래밍: MLX로 배우는 Apple Silicon 최적화](systems-and-parallel-programming/mlx-apple-silicon-optimization/)** — 왜 MLX인가: 통합 메모리와 지연 평가(1부) → 함수 변환: mx.grad와 mx.compile(2부) → 신경망 구성 요소: mlx.nn과 학습 루프(3부) → 성능 최적화: 배치 크기와 양자화(4부) → 종합 실전: NumPy·MLX-CPU·MLX-GPU 비교(5부)까지, 나선형 3클래스 분류기 하나를 이 세션의 실제 Apple GPU(Metal)에서 처음부터 끝까지 함께 만들며, 손 미분과 mx.grad의 결과가 부동소수점 정밀도 수준까지 일치한다는 것과 통합 메모리로 전송 비용이 없는데도 작은 문제에서는 NumPy가 MLX-GPU보다 4.9배 빠르다는 걸 감추지 않고 싣는 독립적인 입문서
- **[학습이 끝난 모델을 하드웨어에 맞게 다시 깎는다: ONNX 하드웨어 최적화](systems-and-parallel-programming/onnx-hardware-optimization/)** — 왜 최적화가 필요한가(1부) → 그래프 레벨 최적화(2부) → 양자화(3부) → MLIR lowering(4부) → 커널 최적화와 이기종 스케줄링(5부) → ONNX 없는 길: MLX로 직접 이식하기(6부)까지, ResNet18 하나를 처음부터 끝까지 예제 삼아 onnxruntime·IREE(MLIR 기반 컴파일러)·MLX 세 도구로 실제 컴파일·실행해서, 연산자 융합은 5%뿐이고 진짜 이득은 레이아웃 변환에서 온다는 것과 동적 양자화가 17배 느려지는데 정적 양자화는 1.86배 빨라진다는 것, ONNX 없이 MLX로 직접 이식한 경로가 onnxruntime CPU보다 빠르지만 범용 컴파일(344.7ms)과 NPU 위임(0.67ms) 사이 515배 격차의 NPU 쪽에는 못 미친다는 것을 실측하며 정확도 등 검증 못 한 한계까지 정직하게 밝히는 독립적인 입문서
- **[TinyRT: 안전하고 빠른 CPU/GPU 추론 런타임](systems-and-parallel-programming/tinyrt-cpu-gpu-inference/)** — 『이론을 C++23으로 옮기다』·『안전을 넘어 성능으로』·『OpenCL로 배우는 헤테로지니어스 컴퓨팅』 세 책의 기법을 한데 모은 캡스톤. 타입 상태로 모델 생명주기를 막고(1부), 텐서를 `mdspan`으로 표현하고(2부), OpenCL RAII로 GPU 컨볼루션을 CPU 기준과 픽셀 단위로 대조 검증하고(3부), 로컬 메모리 타일링과 실측 교차점으로 레이어별 CPU/GPU 배치를 동적으로 정하고(4부), 예외 안전한 GPU 정리와 PMR 아레나 위에서 전체 파이프라인을 조립한 뒤 MobileNet의 depthwise separable convolution까지 확장하고(5부), 여러 추론 요청이 동시에 몰려도 공유된 GPU 커널 오브젝트에 락 없이 접근하면 결과가 조용히 틀어진다는 걸 재현한 뒤 스레드별 커맨드 큐로 정답과 처리량을 함께 지키는(6부) 작은 CNN 추론 런타임을 처음부터 끝까지 같이 만들며, "작은 모델은 CPU가 80배 빠르고 큰 레이어는 GPU가 130배 빠르다"는 실측 교차점을 감추지 않고 그대로 싣는 독립적인 입문서
- **[MarioRL: Apple Silicon 위에서 짓는 병렬 강화학습 프레임워크](systems-and-parallel-programming/mario-rl-framework/)** — 『보상만으로 배운다』가 순수 NumPy로 마리오를 학습시키다 남긴 한계(순전파가 병목의 75%)에서 이어받아, safe-parallel-cpp23·cpp23-performance-engineering·heterogeneous-computing-opencl·tinyrt·mlx-apple-silicon-optimization·onnx-hardware-optimization 여섯 책의 기법을 한데 모은 캡스톤. C++23이 핵심이고 Python은 CPython 임베딩으로 nes-py를 프레임 단위로만 부르는 얇은 다리(1~2부)로, mdspan 프레임 버퍼(2부) 위에서 MLX C++로 정책망과 PPO를 자동미분으로 학습시키고(3부), fork 기반 프로세스로 GIL을 우회해 여러 마리오 인스턴스를 병렬로 굴리며 PMR 아레나로 롤아웃을 안전하게 모으고(4부), 배치 크기와 산술 강도의 실측 교차점으로 어떤 연산을 CPU/GPU 어디에 둘지 정한 뒤(5부) 전체 파이프라인을 조립해 실제 마리오 환경에서 사이클 하나를 1.145ms에 돌리고 TinyRT/CoreML로 배포까지 이어가는(6부), "프레임워크는 빠르고 안전하게 만들었지만 좋은 정책이 실제로 학습됐는지는 확인하지 못했다"는 정직한 한계까지 감추지 않고 싣는 독립적인 입문서
- **[RIIR: C의 JSON 파서를 Rust로 다시 쓰며 배우는 안전한 병렬 프로그래밍](systems-and-parallel-programming/riir-json-parser/)** — "Rust는 병렬처리를 컴파일 타임에 안전하게 체크해서 빠르다"는 오해를 서문에서 바로잡고, C의 cJSON을 기준 삼아 JSON 파서를 처음부터 지으며 소유권·라이프타임(1~2부), Result 에러 전파와 배열/객체 파싱(2부), Display 트레잇과 이터레이터·클로저로 함수형 스타일 트리 변환(3부), cJSON과의 정확성·성능 실측 비교와 빌림 체커가 실제로 잡아준 댕글링 참조 버그(4부), rayon+Arc로 안전한 병렬 파싱과 컴파일되지 않는 데이터 경쟁(5부)까지 Rust 언어 핵심을 실제 컴파일 에러로 익히는 RIIR(Rewrite It In Rust) 입문서. 5만 개짜리 배열 벤치마크에서 C가 16% 더 빨랐던 첫 결과, cpp23-performance-engineering 책 기법을 적용해 역전한 것, 그리고 그 역전의 진짜 원인이 파서가 아니라 C++ 쪽의 느린 파일 읽기 방식이었다는 걸 두 개의 틀린 가설을 거쳐 끝까지 추적해낸 4부 후반의 반전까지 감추지 않고 싣는 게 특징
- **[PyO3로 Rust를 파이썬 패키지로](systems-and-parallel-programming/pyo3-python-extension-packaging/)** — riir-json-parser의 Rust JSON 파서를 PyO3와 maturin으로 파이썬 확장 모듈로 감싸(1부), Result를 파이썬 예외로 매핑하고 표준 json과 정확성을 비교한 뒤(2부), 첫 벤치마크에서 오히려 파이썬 표준 json에게 졌던 결과를 파싱/객체변환 단계로 쪼개 진짜 병목(PyObject 생성 비용)을 찾아내고 GIL을 Python::detach로 실제로 놓아 4스레드 3.14배 병렬성을 실측하고(3부), wheel로 빌드해 Rust 컴파일러가 없는 새 가상환경에 설치해 검증하고 abi3로 파이썬 버전 여러 개를 wheel 하나로 묶기까지(4부) 감추지 않고 싣는 실무 지향적 입문서. "빠른 코어 언어로 짰다는 사실이 전체 파이프라인의 속도를 보장하지 않는다"는 걸 두 번째로 실측 확인하는 riir-json-parser의 직접적인 후속편

## 머신러닝과 강화학습

- **[보상만으로 배운다: 강화학습을 밑바닥부터 마리오까지](machine-learning-and-rl/reward-only-rl-from-scratch/)** — nand2npu 3권이 "이 책은 강화학습 정책을 훈련하는 방법을 다루지 않는다"고 그은 경계선을 채우는 책. 강화학습 문제 정의하기(1부) → 표 기반 방법으로 확실히 검증하기: 정책/가치 반복·몬테카를로·TD(0)·Q-learning(2부) → 함수 근사와 딥 RL: DQN·REINFORCE·Actor-Critic·PPO(3부) → 마리오로 종합하기(4부)까지, NumPy만으로 손으로 짠 표 기반 RL과 신경망을 실제로 실행해 서로 다른 방법이 같은 최적해로 수렴함을 교차 검증하고, 실제로 설치·구동에 성공한 NES 마리오 에뮬레이터 위에서 정책을 학습시켜 그 가중치를 nand2npu 3권이 읽을 수 있는 형식으로 내보내며, 학습이 안정적으로 개선되지 않았다는 사실까지 정직하게 밝히는 독립적인 입문서

## 웹 개발

- **[TypeScript + React 입문: react.dev와 Handbook을 왜라는 질문으로 잇기](web-development/ts-react-getting-started/)** — 공식 React 문서와 TypeScript Handbook을 재료로 "왜 이렇게 생겼는가"를 축으로 재구성한 입문서. 값과 타입(1부) → 컴포넌트·State·렌더링·useRef(2부) → API 호출·폼·React Router로 합치기(3부) 순서로 쌓아 올린다
- **[자바스크립트 없이도 상호작용하는 웹: Go, templ, htmx로 만드는 하이퍼미디어 서비스](web-development/go-templ-htmx-web/)** — 기초 다지기: net/http와 templ(1부) → htmx로 상호작용 만들기: 부분 갱신·OOB 스왑·폼 검증(2부) → 실전 패턴: 컴포넌트 설계·SQLite·검색·세션 인증(3부) → 완성과 배포: SSE·httptest·종합 실전 TODO 앱(4부)까지, SPA 프레임워크 없이 서버가 HTML을 직접 내려주는 하이퍼미디어 지향 방식을 실제로 서버를 띄우고 curl로 요청·응답을 확인하며 배우는 독립적인 입문서
- **[AsciiDoc 제대로 배우기](web-development/asciidoc-getting-started/)** — 기초 문법(1부) → 문서 구조화(2부) → 코드와 재사용(3부) → 실전 활용(4부) 순서로, 이 사이트의 모든 책이 실제로 쓰는 태그·include 조립 방식을 직접 뜯어보며 배우는 AsciiDoc 입문서
- **[Playwright와 크로미움 익스텐션으로 배우는 하이브리드 자동화](web-development/playwright-extension-hybrid-automation/)** — 대기열·캔버스 좌석맵·경쟁 조건을 갖춘 연습용 가짜 예매 사이트를 직접 짓고(1부), 규칙이 명확한 로그인·대기열·재시도는 Python으로 짠 Playwright 자동화 스크립트로(2부), 캔버스 좌석맵처럼 판단이 필요한 부분은 Manifest V3 익스텐션(JS) 안에서 LLM을 호출해(3부) 처리한 뒤, 두 축을 하나의 파이프라인으로 잇고(4부) 재시도 로직 유무로 성공률이 갈린다는 걸 실측하는(5부) 실무 지향적 입문서. 실제 예매 사이트에 이 기술을 적용하면 안 되는 이유(약관 위반과 2024년 공연법 개정)를 서문과 맺음말에서 명확히 밝히는 게 특징
- **[미니 정적 사이트 생성기로 배우는 TypeScript](web-development/typescript-mini-ssg/)** — Markdown을 HTML로 바꾸는 미니 SSG를 TypeScript로 처음부터 지으며, any로 짠 버전이 오타를 조용히 undefined로 흘리는 걸 직접 겪은 뒤(1부), unknown+타입가드로 외부 데이터를 검증하고 판별 유니온·완전성 검사·제네릭 제약·구조적 타이핑으로 콘텐츠를 안전하게 모델링하고(2부), 유틸리티/매핑 타입·비동기 처리·Result 타입·클래스·템플릿 리터럴 타입까지 실전 기능을 확장한 뒤(3부) 실제 Markdown 파일로 진짜 사이트를 빌드하는(4부) 입문서. 모든 컴파일 에러(TS18048, TS2322, TS2353, TS2341)를 실제로 재현해 그대로 싣는 게 특징

## 응용수학과 데이터

- **[증명보다 계산이 먼저다: 공업수학을 코드로 다시 배우기](applied-math-and-data/engineering-math-in-code/)** — 미분·지수함수·벡터/행렬·복소수를 화살표나 추상적 정의 없이 계산으로 먼저 짚는 수학 준비운동(0부) → 상미분방정식(1부) → 라플라스 변환(2부) → 선형연립방정식(3부) → 고유값과 대각화(4부) → 벡터 미적분(5부) → 푸리에 해석과 편미분방정식(6부) → 복소해석(7부)까지, 정의-정리-증명 순서 대신 "왜 필요한가 → NumPy/SciPy/SymPy로 계산해서 확인 → 수식 읽기" 순서로 공업수학 표준 커리큘럼을 다시 짓는 독립적인 입문서. 매 장마다 손으로 유도한 해석해와 서로 다른 방법으로 얻은 수치해를 교차 검증하고, 장 끝마다 실제로 검증한 "직접 해보기" 연습문제를 둔다
- **[AICE Associate 실전 대비: 데이터에서 모델까지](applied-math-and-data/aice-associate-deep-learning/)** — Pandas 데이터 다루기(1부) → EDA와 머신러닝 기초(2부) → Keras 딥러닝(3부) → 시험형 문제 실전(4부) 순서로, AICE Associate 자격증 실기 범위를 실제 Pandas·scikit-learn·TensorFlow/Keras를 실행해 검증하며 배우는 독립적인 입문서
