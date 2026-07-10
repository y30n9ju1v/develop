---
title: "시뮬레이션 오케스트레이션"
---

수천 개 자율주행 시나리오를 클라우드에서 병렬로 실행하는 오케스트레이션 구조를 다룹니다.

1. **[시뮬레이션 회귀 테스트, 클라우드에서 뭘로 오케스트레이션할까: K8s vs Ray vs Slurm](cloud-orchestrator-comparison/)** — K8s, Ray, Slurm의 설계 철학 차이와, 실전에서 왜 세 가지를 조합해 쓰게 되는지 정리합니다.
2. **[Kubernetes로 시뮬레이션 배치 돌리기: Job, 오토스케일링, Kueue 실전](k8s-batch-scheduling-with-kueue/)** — Indexed Job으로 시나리오를 배치 실행하고, Cluster Autoscaler/Karpenter로 GPU 노드를 늘리고, Kueue로 워크로드 큐를 분리하는 구성을 정리합니다.
3. **[Ray/KubeRay 입문: 시나리오 단위로 CPU/GPU 태스크 쪼개 스케줄링하기](ray-kuberay-for-beginners/)** — Ray의 태스크 기반 스케줄링, fractional GPU 할당, KubeRay로 K8s 위에 Ray 클러스터를 올리는 방법을 정리합니다.
4. **[Slurm으로 온프레미스 GPU 팜에서 시뮬레이션 회귀 테스트 돌리기](slurm-batch-scheduling/)** — job array와 gang scheduling, QoS/fair-share 큐 정책, 클라우드 버스트 구성을 정리합니다.
5. **[CPU/GPU 혼합 시뮬레이션 워크로드, 배치 스케줄링이 까다로운 이유](cpu-gpu-mixed-batch-scheduling/)** — 파이프라인을 CPU/GPU 단계로 쪼개고, fractional GPU 할당과 LPT 정렬로 실행 시간 편차를 흡수하는 방법을 정리합니다.
6. **[스팟 인스턴스로 GPU 비용 아끼면서 회귀 테스트 재현성 지키기](spot-cost-reproducibility-queue-priority/)** — 비용 절감과 재현성 사이의 절충, PR 검증과 야간 풀 회귀가 GPU 큐를 두고 충돌하지 않게 만드는 우선순위 설계를 정리합니다.
