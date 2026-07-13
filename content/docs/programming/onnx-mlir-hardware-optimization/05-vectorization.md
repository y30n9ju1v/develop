---
title: "5. 벡터화: 타일 안쪽 반복문을 SIMD 명령으로 접기"
date: 2026-07-13T00:00:00+09:00
draft: false
tags: ["mlir", "onnx", "deep-learning", "compiler", "vectorization", "simd"]
categories: ["programming"]
description: "타일 안쪽의 순차 반복문이 vector dialect를 거쳐 실제 SIMD 명령 하나로 접히는 과정과, iterator_types의 parallel/reduction 구분이 왜 이 변환의 안전성을 결정하는지 확인합니다."
---

[4편](../04-lowering-to-linalg-and-tiling/)에서 우리 예제는 캐시에 맞춰 32×32 타일로 쪼개진 `linalg.generic` + `memref`까지 내려왔습니다. 이 글은 타일 안쪽 반복문이 **한 번에 여러 원소를 처리하는 SIMD 명령**으로 접히는 벡터화 과정을 다룹니다.

---

## 1. 스칼라 반복문 vs 벡터 명령: 무엇이 정말 달라지는가

타일 하나를 가장 단순하게(아무 벡터화 없이) 실행하면, 입력 채널(`ci`)을 도는 안쪽 반복문은 원소 하나씩 곱하고 더하는 명령을 3번(우리 예제는 `ci`가 3) 반복합니다.

```
// 스칼라: ci = 0, 1, 2를 한 원소씩 처리
load  in[0]; load k[0]; mul; add;
load  in[1]; load k[1]; mul; add;
load  in[2]; load k[2]; mul; add;
```

현대 CPU/GPU는 이렇게 하나씩 처리하는 대신, 레지스터 하나에 여러 개의 float 값을 나란히 채워 넣고 **그 레지스터 전체에 대해 곱셈과 덧셈을 한 번의 명령으로 수행**하는 벡터 유닛을 가지고 있습니다(예: x86의 AVX는 256비트 레지스터에 float 8개를 채워 한 번에 처리, ARM NEON은 128비트에 4개). 같은 계산을 벡터 명령으로 표현하면:

```
// 벡터: ci 축 전체(3개, 벡터 레지스터가 더 넓다면 남는 자리는 0으로 채움)를 한 명령으로
vload in_vec  = [in[0], in[1], in[2], 0]
vload k_vec   = [k[0], k[1], k[2], 0]
vfma  acc = acc + in_vec * k_vec   // 곱하고 누적을 한 명령으로 (fused multiply-add)
```

명령 개수가 3배 넘게 줄어드는 게 아니라, **애초에 "여러 원소를 동시에 처리한다"는 하드웨어 능력을 실제로 쓰기 시작하는 것**입니다. 이 변환을 IR 수준에서 표현하는 게 `vector` dialect입니다.

---

## 2. `iterator_types`가 벡터화의 안전성을 결정한다

4편에서 `linalg.generic`에 붙어 있던 `iterator_types = ["parallel", ..., "reduction", "reduction", "reduction"]`을 기억해봅시다. 벡터화 pass가 "이 축을 벡터 레지스터에 나란히 태워도 되는가"를 판단할 때 정확히 이 정보를 씁니다.

- **`"parallel"` 축(`n, h, w, co`)**: 이 축 위의 계산들은 서로 독립적입니다. 출력 채널 `co=0`과 `co=1`의 계산 결과는 서로 영향을 주지 않으므로, 이 축을 벡터 레지스터에 나란히 태워 "출력 채널 여러 개를 동시에 계산"해도 결과가 달라지지 않습니다.
- **`"reduction"` 축(`kh, kw, ci`)**: 이 축은 누적(덧셈)이 일어나는 축입니다. 벡터화 자체는 여전히 가능하지만(위 예제가 정확히 `ci` 축을 벡터로 태운 경우입니다), **부동소수점 덧셈은 결합법칙이 정확히 성립하지 않기 때문에** 누적 순서를 바꾸면 마지막 자리의 반올림 오차가 미세하게 달라질 수 있습니다. 대부분의 딥러닝 추론에서는 이 오차가 무시할 만한 수준이라 허용되지만, 이건 컴파일러가 자동으로 판단할 문제가 아니라 "이 정도 오차는 감수한다"는 명시적인 선택(fast-math 같은 컴파일 옵션)으로 다뤄야 하는 지점입니다.

즉 벡터화 pass가 4편의 `iterator_types`를 다시 읽는 이유는, 그래프 수준([3편](../03-graph-level-optimization/))에서 융합 가능성을 판단할 때 "출력을 쓰는 곳이 하나뿐인가"를 확인했던 것과 똑같은 종류의 안전성 확인을 반복문 수준에서 다시 하는 것입니다 — 최적화의 종류는 다르지만, "이 축을 재배치해도 결과가 같은가"라는 질문 자체는 파이프라인 전체에서 반복됩니다.

---

## 3. 어느 축을 벡터화할지는 하드웨어의 벡터 폭이 정한다

우리 예제에서 벡터화 후보가 될 수 있는 축은 `ci`(3), `co`(64), 그리고 타일 안의 공간 축(`h, w`, 각 32)이 있습니다. 어느 축을 고를지는 대상 하드웨어의 벡터 레지스터 폭과, 그 축의 크기가 얼마나 그 폭에 잘 맞아떨어지는지로 결정됩니다.

- `ci = 3`을 벡터화하면 8-wide 벡터 레지스터의 5칸이 낭비됩니다(패딩 후 계산해도 결과엔 지장 없지만 유닛을 절반도 못 씁니다).
- `co = 64`를 벡터화하면 8-wide 레지스터를 정확히 8번 채워 낭비 없이 쓸 수 있습니다.

그래서 실전에서는 `co` 축을 벡터화 대상으로 재배치하는 경우가 많습니다 — 이는 4편에서 결정한 반복문의 축 순서를 벡터화 단계에서 다시 조정(loop interchange)해야 할 수 있다는 뜻이기도 합니다. `vector` dialect로 옮기면 이렇게 됩니다.

```mlir
%acc_vec = vector.broadcast %zero : vector<8xf32>
%acc_vec = scf.for %ci = 0 to 3 step 1 iter_args(%acc = %acc_vec) -> vector<8xf32> {
  %in_scalar = memref.load %input[%n, %h, %w, %ci] : memref<...xf32>
  %in_vec    = vector.broadcast %in_scalar : vector<8xf32>
  %k_vec     = vector.load %kernel[%co_base, %kh, %kw, %ci] : memref<...xf32>, vector<8xf32>
  %acc_next  = vector.fma %in_vec, %k_vec, %acc : vector<8xf32>
  scf.yield %acc_next : vector<8xf32>
}
vector.store %acc_vec, %output[%n, %h, %w, %co_base] : memref<...xf32>, vector<8xf32>
```

`vector<8xf32>` 타입 하나가 "float 8개를 레지스터 하나에 나란히 담는다"는 걸 IR 수준에서 표현하고, `vector.fma`(곱하고 누적을 동시에)가 위에서 손으로 그렸던 `vfma` 명령에 정확히 대응합니다.

---

## 4. 이 단계에서도 하드웨어마다 결과가 갈린다

4편의 타일 크기가 캐시 크기에 종속적이었던 것처럼, 이 단계의 벡터 폭(`vector<8xf32>`)도 대상 하드웨어에 종속적입니다. 같은 `linalg.generic` + 타일링 결과를 두고도:

- x86 AVX2 타겟이라면 `vector<8xf32>`(256비트)를 고를 수 있고,
- ARM NEON 타겟이라면 `vector<4xf32>`(128비트)가 자연스러우며,
- GPU 타겟이라면 애초에 "벡터 레지스터"라는 개념 대신 "스레드 여러 개가 각자 원소 하나씩 맡는다"는 전혀 다른 병렬화 모델(`gpu.thread_id`로 인덱싱)을 씁니다.

즉 여기까지(`vector` dialect)는 아직 "CPU에 벡터 명령을 쓴다"는 하나의 큰 방향 안에서의 선택이고, 6편에서 다룰 진짜 하드웨어별 최종 낮추기는 이 방향 자체가 GPU나 커스텀 가속기로 완전히 갈라지는 지점입니다.

---

## 5. 지금까지의 흐름 정리

1편부터 여기까지, 우리 예제 하나가 거쳐온 변환을 신뢰의 관점이 아니라 **"무엇이 새로 정해졌는가"**의 관점으로 다시 정리하면:

- **[2편](../02-importing-onnx-and-shape-inference/)**: ONNX 노드가 `onnx` dialect 오퍼레이션으로, 물음표였던 shape가 구체적인 숫자로 확정됨.
- **[3편](../03-graph-level-optimization/)**: 세 오퍼레이션이 하나로 융합되고, 상수 계산이 미리 끝나고, 레이아웃이 `NHWC`로 통일됨.
- **[4편](../04-lowering-to-linalg-and-tiling/)**: 그 하나의 오퍼레이션이 7겹 반복문으로 펼쳐지고, 캐시 크기에 맞는 32×32 타일로 쪼개지고, 텐서가 메모리 버퍼로 바뀜.
- **[5편(이 글)](../05-vectorization/)**: 타일 안쪽 반복문이 하드웨어의 벡터 폭에 맞춰 SIMD 명령으로 접힘.

다음 편(마지막)에서는 이 `vector` dialect 표현을 실제로 서로 다른 두 타겟 — 범용 CPU/GPU 경로와, 우리가 가정할 작은 커스텀 NPU 가속기 경로 — 로 각각 낮추면서, 6편까지 쌓아온 모든 결정(융합, 타일 크기, 벡터 폭)이 최종 명령 스트림에서 어떻게 구체적인 형태로 드러나는지 확인합니다.
