---
title: "Ray/KubeRay 입문: 시나리오 단위로 CPU/GPU 태스크 쪼개 스케줄링하기"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["autonomous", "ray", "kuberay", "simulation", "batch-scheduling", "gpu-scheduling"]
categories: ["autonomous"]
description: "Ray의 태스크 기반 스케줄링 모델과 num_gpus fractional 할당, KubeRay로 K8s 위에 Ray 클러스터를 올리는 방법, 그리고 Ray Data로 시뮬레이션 결과를 이어붙이는 패턴을 정리합니다."
---

[K8s vs Ray vs Slurm 비교 글](../cloud-orchestrator-comparison/)에서 Ray를 "시나리오 단위 태스크 스케줄링과 CPU/GPU 이종 자원 배분"을 맡는 레이어로 소개했습니다. 이 글은 Ray가 왜 그 역할에 적합한지, 그리고 [K8s 위에 KubeRay로 어떻게 얹는지](../k8s-batch-scheduling-with-kueue/)를 코드 수준에서 정리합니다.

---

## 1. Ray의 태스크 모델: 함수 하나가 곧 스케줄링 단위

Ray는 파이썬 함수에 `@ray.remote` 데코레이터를 붙이면 그 함수가 클러스터 어디서든 실행될 수 있는 태스크가 됩니다. K8s Job처럼 YAML로 리소스를 선언하는 게 아니라, 코드 안에서 리소스 요구량을 직접 지정합니다.

```python
import ray

ray.init(address="auto")

@ray.remote(num_cpus=2)
def run_physics(scenario_id: str):
    # 물리 시뮬레이션, CPU 바운드
    ...
    return sim_state

@ray.remote(num_gpus=1)
def render_sensors(sim_state):
    # 카메라/LiDAR 렌더링, GPU 필요
    ...
    return sensor_data

@ray.remote(num_gpus=1)
def run_perception(sensor_data):
    # 인지 모델 추론
    ...
    return metrics
```

CPU 단계와 GPU 단계를 각각 다른 함수로 선언하면, Ray 스케줄러가 `num_gpus=0`인 태스크는 CPU 노드에, `num_gpus>0`인 태스크는 GPU 노드에 자동으로 배치합니다. 파이프라인 체이닝은 futures를 그대로 다음 함수에 넘기면 됩니다.

```python
scenario_ids = load_scenario_manifest()  # 수천 개

results = []
for scenario_id in scenario_ids:
    sim_state = run_physics.remote(scenario_id)
    sensor_data = render_sensors.remote(sim_state)
    metrics = run_perception.remote(sensor_data)
    results.append(metrics)

all_metrics = ray.get(results)
```

Ray는 `sim_state`가 GPU 태스크의 인자로 쓰이는 것을 보고 의존성 그래프를 자동으로 추적하며, `run_physics`가 끝나야 `render_sensors`가 시작되도록 스케줄링합니다. 별도의 DAG 엔진 없이도 파이프라인 의존성이 코드 자체에서 드러납니다.

---

## 2. Fractional GPU와 커스텀 리소스

시나리오마다 GPU 사용량이 다르면 `num_gpus`에 소수를 지정해 GPU 하나를 여러 태스크가 나눠 쓰게 할 수 있습니다.

```python
@ray.remote(num_gpus=0.25)
def render_light_scenario(sim_state):
    ...
```

GPU 세대나 특정 하드웨어 기능(예: 특정 시나리오만 필요한 레이 트레이싱 코어)에 따라 노드를 구분하고 싶다면 커스텀 리소스를 씁니다.

```python
# 클러스터 시작 시 노드에 커스텀 리소스 태깅
# ray start --resources='{"raytracing_gpu": 4}'

@ray.remote(resources={"raytracing_gpu": 1})
def render_with_raytracing(sim_state):
    ...
```

---

## 3. KubeRay로 K8s 위에 Ray 클러스터 올리기

Ray 단독 클러스터는 오토스케일링, 장애 복구, 멀티테넌시가 K8s만큼 성숙하지 않습니다. [KubeRay](https://github.com/ray-project/kuberay)는 `RayCluster` CRD로 Ray 클러스터를 K8s 오브젝트처럼 선언하고, K8s의 오토스케일러·노드 풀·RBAC을 그대로 활용하게 해줍니다.

```yaml
apiVersion: ray.io/v1
kind: RayCluster
metadata:
  name: sim-regression-cluster
spec:
  headGroupSpec:
    rayStartParams: {}
    template:
      spec:
        containers:
          - name: ray-head
            image: registry.internal/ray-sim:latest
            resources:
              requests: { cpu: "2", memory: "4Gi" }
  workerGroupSpecs:
    - groupName: cpu-workers
      replicas: 20
      minReplicas: 0
      maxReplicas: 200
      rayStartParams: {}
      template:
        spec:
          nodeSelector:
            node-pool: cpu
          containers:
            - name: ray-worker
              image: registry.internal/ray-sim:latest
              resources:
                requests: { cpu: "2", memory: "4Gi" }
    - groupName: gpu-workers
      replicas: 2
      minReplicas: 0
      maxReplicas: 32
      rayStartParams: {}
      template:
        spec:
          nodeSelector:
            node-pool: gpu
          tolerations:
            - key: "nvidia.com/gpu"
              operator: "Exists"
              effect: "NoSchedule"
          containers:
            - name: ray-worker
              image: registry.internal/ray-sim:latest
              resources:
                requests: { cpu: "4", memory: "16Gi" }
                limits: { nvidia.com/gpu: 1 }
```

CPU 워커 그룹과 GPU 워커 그룹을 분리해두면, Ray Autoscaler가 대기 중인 태스크의 리소스 요구량을 보고 각 그룹을 독립적으로 늘리고 줄입니다. `minReplicas: 0`으로 GPU 워커 그룹을 유휴 시 완전히 0으로 내릴 수 있어, [K8s 글](../k8s-batch-scheduling-with-kueue/)에서 다룬 Cluster Autoscaler/Karpenter와 자연스럽게 맞물립니다.

---

## 4. Ray Data로 결과를 다음 단계로 흘려보내기

시뮬레이션 결과(메트릭, 실패 케이스)를 파일로 떨어뜨리고 별도 배치로 다시 읽어들이는 대신, Ray Data를 쓰면 시뮬레이션 → 집계 → 다음 학습 파이프라인까지 하나의 Ray 클러스터 안에서 스트리밍으로 이어붙일 수 있습니다.

```python
import ray.data

ds = ray.data.from_items(scenario_ids)
ds = ds.map(run_physics_fn) \
       .map(render_sensors_fn) \
       .map(run_perception_fn)

ds.write_parquet("s3://bucket/regression-results/")
```

이렇게 얻은 Parquet 결과는 [Arrow 기반 데이터 스택](../../data-infra/closed-loop-regression-with-dora/)의 py123d/FiftyOne/Rerun 파이프라인으로 바로 이어서 분석할 수 있습니다.

---

## 5. 정리

Ray/KubeRay가 K8s 단독 대비 갖는 강점은 **리소스 요구량을 코드 레벨에서 태스크 단위로 세밀하게 선언**할 수 있고, **태스크 간 의존성이 futures 체이닝만으로 자연스럽게 DAG를 이룬다**는 점입니다. K8s가 노드 프로비저닝과 큐 격리(Kueue)를 맡고, 그 위에서 Ray가 시나리오 단위 CPU/GPU 스케줄링을 맡는 조합이 실전에서 가장 균형 잡힌 구성입니다.

온프레미스 GPU 팜을 함께 쓰는 조직이라면, 이 조합에 [Slurm을 클라우드 버스트 대상으로 연결](../slurm-batch-scheduling/)하는 것도 고려해볼 만합니다.
