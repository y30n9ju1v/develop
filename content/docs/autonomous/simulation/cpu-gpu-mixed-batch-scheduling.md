---
title: "CPU/GPU 혼합 시뮬레이션 워크로드, 배치 스케줄링이 까다로운 이유"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["autonomous", "ray", "kubernetes", "simulation", "gpu-scheduling", "batch-scheduling"]
categories: ["autonomous"]
description: "자율주행 시뮬레이션 파이프라인을 CPU/GPU 단계로 쪼개고, fractional GPU 할당과 LPT 정렬로 실행 시간 편차를 흡수하는 실전 배치 스케줄링 전략을 정리합니다."
---

[이전 글](../cloud-orchestrator-comparison/)에서 K8s + Ray(KubeRay) 조합이 수천 개 시나리오를 병렬 실행하기 위한 현실적인 오케스트레이션 기반이라는 결론을 냈습니다. 이 글은 그 위에서 실제로 **CPU/GPU 혼합 워크로드를 어떻게 쪼개고 배치해야 자원 낭비가 없는지**를 다룹니다.

---

## 1. 파이프라인을 단계별로 쪼개야 한다

시나리오 하나의 실행을 하나의 모놀리식 Job으로 던지면, GPU가 필요 없는 CPU 단계(물리 시뮬레이션, 시나리오 파싱) 동안에도 GPU 노드를 점유하게 됩니다. 이건 비싼 GPU를 낭비하는 가장 흔한 실수입니다.

DAG로 단계를 쪼개는 것이 기본 전략입니다.

```
[시나리오 로드 (CPU)] → [물리 시뮬레이션 (CPU)] → [센서 렌더링 (GPU)] → [인지 추론 (GPU)] → [메트릭 집계 (CPU)]
```

Ray라면 각 단계를 별도 태스크로 만들어 `num_gpus=0` / `num_gpus=1`로 명시하면, Ray 스케줄러가 CPU 전용 태스크는 CPU 노드 풀에, GPU 필요 태스크는 GPU 노드 풀에 각각 배치합니다.

```python
@ray.remote(num_cpus=2)
def run_physics(scenario):
    ...

@ray.remote(num_gpus=1)
def render_sensors(sim_state):
    ...
```

K8s만으로 이 파이프라인을 구성한다면 노드 풀을 CPU 전용/GPU 전용으로 분리하고, taint/toleration + nodeSelector로 강제 분리하는 것이 기본입니다. 다만 K8s Job 자체는 태스크 간 데이터 전달(중간 결과를 다음 단계로 넘기는 것)을 직접 지원하지 않으므로, Argo Workflows 같은 DAG 엔진을 얹거나 Ray의 태스크 체이닝에 맡기는 편이 낫습니다.

---

## 2. GPU 노드는 fractional하게 나눠 써야 손해가 안 난다

렌더링·추론 단계도 시나리오마다 GPU 사용량이 제각각입니다. 단순 카메라 렌더링은 GPU 메모리 1~2GB면 충분한데, Job당 GPU 1개를 통째로 할당하면 GPU가 놀게 됩니다.

- MIG(Multi-Instance GPU)나 MPS(Multi-Process Service)로 GPU 하나를 여러 파티션으로 쪼개 여러 시나리오가 동시에 나눠 쓰게 하는 방식이 유효합니다.
- Ray는 `num_gpus=0.25` 같은 fractional 지정을 지원해, 가벼운 렌더링 태스크 4개를 GPU 하나에 동시에 스케줄링할 수 있습니다.

```python
@ray.remote(num_gpus=0.25)
def render_light_scenario(sim_state):
    ...
```

단, 실제 메모리 격리는 애플리케이션(또는 MPS)이 보장해야 하며 Ray가 프로세스 간 GPU 메모리 충돌을 막아주지는 않습니다. fractional 할당은 "스케줄링 슬롯"을 나누는 것이지 하드웨어 격리를 제공하는 것이 아니라는 점을 팀 내에 명확히 해둬야, 나중에 OOM 디버깅에 시간을 뺏기지 않습니다.

---

## 3. 실행 시간 편차 때문에 bin-packing이 필요하다

수천 개 시나리오를 단순히 큐에 순서대로 넣으면, 마지막에 긴 시나리오 몇 개가 몰려서 전체 배치가 늦게 끝나는 롱테일 문제가 생깁니다.

- 과거 실행 이력(시나리오 메타데이터에 예상 실행 시간을 태깅)을 기반으로 **긴 시나리오부터 먼저 스케줄링**하는 LPT(Longest Processing Time first) 휴리스틱이 간단하면서도 효과적입니다. 직관적으로, 짧은 작업들은 어느 워커에 넣어도 뒤늦게 합류해 빈틈을 메울 수 있지만 긴 작업은 먼저 자리를 잡아야 전체 완료 시각(makespan)이 짧아집니다.
- Ray의 경우 태스크 큐 자체가 동적이라 워커가 놀면 바로 다음 태스크를 당겨오므로, 정적 배치보다 자연스럽게 로드밸런싱됩니다. Slurm/K8s Job 기반이라면 예상 실행 시간으로 사전 정렬한 뒤 제출하는 것이 중요합니다.

---

## 4. 정리

CPU/GPU 혼합 워크로드를 낭비 없이 스케줄링하는 핵심은 세 가지입니다.

1. 파이프라인을 CPU/GPU 단계로 명시적으로 쪼개서, GPU 노드가 CPU 작업 동안 놀지 않게 한다.
2. 시나리오별 GPU 사용량 편차를 fractional 할당(MIG/MPS, Ray `num_gpus=0.25`)으로 흡수한다.
3. 시나리오별 실행 시간 편차는 LPT 정렬이나 Ray의 동적 태스크 큐로 흡수해 롱테일을 줄인다.

이렇게 자원을 최대한 촘촘히 채우고 나면 남는 문제는 비용과 재현성입니다. 다음 글에서 [스팟 인스턴스 비용 절감과 재현성, 큐 우선순위](../spot-cost-reproducibility-queue-priority/)를 다룹니다.
