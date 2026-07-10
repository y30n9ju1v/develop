---
title: "Kubernetes로 시뮬레이션 배치 돌리기: Job, 오토스케일링, Kueue 실전"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["autonomous", "kubernetes", "kueue", "simulation", "batch-scheduling", "gpu-scheduling"]
categories: ["autonomous"]
description: "K8s Indexed Job으로 수천 개 시나리오를 배치 실행하고, Cluster Autoscaler로 GPU 노드를 탄력적으로 늘리고, Kueue로 워크로드 큐를 분리하는 실전 구성을 정리합니다."
---

[K8s vs Ray vs Slurm 비교 글](../cloud-orchestrator-comparison/)에서 K8s를 "클러스터의 기반 레이어"로 두는 조합을 추천했습니다. 이 글은 그 기반 레이어를 실제로 어떻게 구성하는지 — Job으로 시나리오를 배치 실행하고, 노드를 오토스케일링하고, Kueue로 큐를 분리하는 구체적인 설정을 다룹니다.

---

## 1. Indexed Job으로 시나리오 배치 던지기

K8s에서 "시나리오 N개를 병렬로 돌린다"는 요구에 가장 잘 맞는 기본 오브젝트는 `Job`의 `Indexed` 완료 모드입니다. 각 파드가 `JOB_COMPLETION_INDEX` 환경 변수를 받아 자신이 몇 번째 시나리오를 맡았는지 알 수 있습니다.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: scenario-batch-001
spec:
  completions: 2000
  parallelism: 200
  completionMode: Indexed
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: sim-runner
          image: registry.internal/sim-runner:latest
          command: ["python", "run_scenario.py"]
          env:
            - name: SCENARIO_INDEX
              valueFrom:
                fieldRef:
                  fieldPath: metadata.annotations['batch.kubernetes.io/job-completion-index']
          resources:
            requests:
              cpu: "2"
              memory: "4Gi"
            limits:
              cpu: "2"
              memory: "4Gi"
```

`parallelism: 200`은 동시에 200개 파드까지만 뜨게 제한합니다. 시나리오 인덱스와 실제 시나리오 목록의 매핑은 러너 스크립트 안에서 (예: S3에 올려둔 시나리오 매니페스트를 인덱스로 조회하는 방식으로) 처리합니다. GPU가 필요한 렌더링/추론 단계는 별도 Job으로 분리하고, `nodeSelector`와 `tolerations`로 GPU 노드 풀에만 스케줄링되게 강제합니다.

```yaml
      nodeSelector:
        node-pool: gpu
      tolerations:
        - key: "nvidia.com/gpu"
          operator: "Exists"
          effect: "NoSchedule"
      resources:
        limits:
          nvidia.com/gpu: 1
```

---

## 2. Cluster Autoscaler / Karpenter로 GPU 노드 탄력적으로 늘리기

수천 개 시나리오가 한꺼번에 몰릴 때마다 GPU 노드를 상시 띄워두는 건 비용 낭비입니다. 오토스케일러가 큐에 쌓인 Pending 파드를 보고 노드를 자동으로 추가/제거하게 합니다.

- **Cluster Autoscaler**: 클라우드 제공자의 관리형 노드 그룹(예: AWS EKS Managed Node Group, GKE Node Pool)을 스케일링합니다. GPU 노드 그룹은 별도 Auto Scaling Group으로 분리하고, `min=0`으로 설정해 유휴 시 완전히 0으로 스케일 다운되게 합니다.
- **Karpenter**: 노드 그룹을 미리 정의하지 않고 Pending 파드의 리소스 요청을 보고 즉석에서 알맞은 인스턴스 타입을 골라 프로비저닝합니다. 시나리오마다 GPU 요구량이 다른 워크로드에서는 Karpenter가 인스턴스 타입 선택의 유연성 면에서 유리합니다.

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: gpu-sim
spec:
  template:
    spec:
      requirements:
        - key: karpenter.k8s.aws/instance-family
          operator: In
          values: ["g5", "g6"]
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
      nodeClassRef:
        name: gpu-sim-class
  limits:
    cpu: 1000
    nvidia.com/gpu: 64
```

`capacity-type`에 `spot`과 `on-demand`를 둘 다 넣어두면, 가용한 쪽으로 자동 배치됩니다. 스팟 회수와 재현성 트레이드오프는 [스팟 비용·재현성 글](../spot-cost-reproducibility-queue-priority/)에서 다뤘습니다.

---

## 3. Kueue로 PR 검증 큐와 야간 배치 큐 분리하기

기본 K8s 스케줄러는 파드를 FIFO에 가깝게 처리하기 때문에, 야간에 던진 2,000개짜리 회귀 배치가 GPU 노드를 다 점유하고 있으면 낮에 급하게 들어온 PR 검증 10개가 몇 시간을 기다리게 됩니다. [Kueue](https://kueue.sigs.k8s.io/)는 이 문제를 위해 만들어진 K8s 네이티브 배치 큐 매니저입니다.

```yaml
apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
  name: pr-verification
spec:
  namespaceSelector: {}
  resourceGroups:
    - coveredResources: ["cpu", "memory", "nvidia.com/gpu"]
      flavors:
        - name: gpu-flavor
          resources:
            - name: "nvidia.com/gpu"
              nominalQuota: 8
---
apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
  name: nightly-regression
spec:
  namespaceSelector: {}
  resourceGroups:
    - coveredResources: ["cpu", "memory", "nvidia.com/gpu"]
      flavors:
        - name: gpu-flavor
          resources:
            - name: "nvidia.com/gpu"
              nominalQuota: 4
              borrowingLimit: 56
```

`pr-verification` 큐는 GPU 8개를 항상 보장받고, `nightly-regression` 큐는 기본 4개만 갖되 `borrowingLimit`으로 유휴 자원을 최대 56개까지 빌려 쓸 수 있습니다. 낮 시간대 PR 검증이 몰리면 야간 배치가 자원을 반납하고, 밤에는 야간 배치가 전체 GPU를 활용하는 식으로 자연스럽게 균형이 맞춰집니다. Job에는 `kueue.x-k8s.io/queue-name` 라벨만 붙이면 됩니다.

```yaml
metadata:
  labels:
    kueue.x-k8s.io/queue-name: nightly-regression
```

---

## 4. 정리

K8s를 시뮬레이션 배치의 기반 레이어로 쓸 때 필요한 세 조각은 명확합니다.

1. Indexed Job으로 시나리오 인덱스를 파드에 나눠주고, CPU/GPU 단계를 별도 Job과 노드 풀로 분리한다.
2. Cluster Autoscaler(관리형 노드 그룹) 또는 Karpenter(유연한 인스턴스 선택)로 GPU 노드를 필요할 때만 띄운다.
3. Kueue로 워크로드 클래스별 큐와 쿼터를 나눠, 급한 검증이 대규모 배치에 밀리지 않게 한다.

여기까지가 K8s 단독으로 할 수 있는 범위입니다. 시나리오 단위의 세밀한 CPU/GPU 태스크 스케줄링과 결과 체이닝은 [Ray/KubeRay 실전](../ray-kuberay-for-beginners/)에서 이어집니다.
