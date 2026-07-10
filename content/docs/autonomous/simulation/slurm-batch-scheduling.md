---
title: "Slurm으로 온프레미스 GPU 팜에서 시뮬레이션 회귀 테스트 돌리기"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["autonomous", "slurm", "simulation", "batch-scheduling", "gpu-scheduling", "hpc"]
categories: ["autonomous"]
description: "Slurm의 job array와 gang scheduling, QoS/fair-share 큐 정책, GPU 토폴로지를 고려한 배치, 그리고 클라우드 버스트로 K8s/Ray와 연결하는 구성을 정리합니다."
---

[K8s vs Ray vs Slurm 비교 글](../cloud-orchestrator-comparison/)에서 온프레미스 GPU 자산이 있는 조직은 Slurm을 클라우드 오케스트레이션의 버스트 대상으로 연결하는 구조를 언급했습니다. 이 글은 Slurm이 배치 스케줄링에서 강한 이유와, 실제로 시나리오 회귀 테스트를 Slurm 위에서 어떻게 구성하는지를 다룹니다.

---

## 1. Slurm이 HPC 진영에서 검증된 이유

Slurm은 K8s나 Ray보다 훨씬 오래된, 슈퍼컴퓨팅 클러스터를 위해 설계된 배치 스케줄러입니다. 시뮬레이션 회귀 테스트에 유용한 특징 몇 가지:

- **Gang scheduling**: 작업에 필요한 모든 리소스(예: 8개 GPU 노드)를 한 번에 확보한 뒤에만 작업을 시작합니다. 일부만 확보된 채로 시작해 나머지를 기다리며 자원을 낭비하는 상황을 막습니다.
- **성숙한 fair-share 정책**: 사용자/그룹별로 과거 사용량에 따라 우선순위를 자동 조정합니다. 한 팀이 GPU를 몰아 쓰고 나면 다음번엔 우선순위가 낮아져, 별도 쿼터 설정 없이도 장기적으로 공정한 배분이 이뤄집니다.
- **GPU 토폴로지 인지 배치**: NVLink로 연결된 GPU들을 같은 작업에 묶어 배치하는 등, 하드웨어 토폴로지를 고려한 스케줄링이 성숙해 있습니다.

---

## 2. Job Array로 시나리오 배치 던지기

K8s의 Indexed Job에 대응하는 것이 Slurm의 job array입니다.

```bash
#!/bin/bash
#SBATCH --job-name=scenario-regression
#SBATCH --array=0-1999%200
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=logs/scenario_%a.log

SCENARIO_ID=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" scenario_manifest.txt)
python run_scenario.py --scenario-id "$SCENARIO_ID"
```

`--array=0-1999%200`은 2,000개 시나리오를 인덱스 0~1999로 던지되 동시 실행은 200개로 제한합니다. `$SLURM_ARRAY_TASK_ID`로 각 태스크가 자신이 맡을 시나리오를 매니페스트에서 찾아옵니다.

GPU가 필요한 단계는 별도 job로 분리하고 `--gres`로 GPU를 요청합니다.

```bash
#!/bin/bash
#SBATCH --job-name=scenario-render
#SBATCH --array=0-1999%50
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --partition=gpu

SCENARIO_ID=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" scenario_manifest.txt)
python render_sensors.py --scenario-id "$SCENARIO_ID"
```

CPU 단계 job이 끝난 뒤 GPU 단계 job이 시작되도록 의존성을 걸려면 `--dependency`를 씁니다.

```bash
PHYSICS_JOB=$(sbatch --parsable physics_job.sh)
sbatch --dependency=afterok:$PHYSICS_JOB render_job.sh
```

---

## 3. QoS로 PR 검증과 야간 배치 분리하기

fair-share만으로는 "지금 당장 급한 PR 검증"을 보장하기 부족할 수 있습니다. Slurm의 QoS(Quality of Service)로 큐별 우선순위와 최대 리소스를 명시적으로 나눌 수 있습니다.

```bash
# 관리자가 사전에 QoS 정의
sacctmgr add qos pr-verification priority=1000 MaxTRESPerUser=gres/gpu=8
sacctmgr add qos nightly-regression priority=100 MaxTRESPerUser=gres/gpu=64
```

```bash
#SBATCH --qos=pr-verification
#SBATCH --gres=gpu:1
```

`pr-verification` QoS는 우선순위가 높아 큐에서 먼저 스케줄링되고, 사용자당 최대 8개 GPU로 제한되어 있어 한 번에 클러스터를 독점하지 못합니다. `nightly-regression`은 우선순위는 낮지만 최대 64개까지 GPU를 쓸 수 있어, 유휴 시간대에 대규모 배치를 흡수합니다. 이 패턴은 [K8s Kueue 글](../k8s-batch-scheduling-with-kueue/)에서 다룬 `nominalQuota`/`borrowingLimit` 구조와 개념적으로 동일합니다 — 도구는 다르지만 "보장 쿼터 + 유휴 자원 차용"이라는 설계는 같습니다.

---

## 4. 클라우드 버스트: 온프레미스가 가득 찼을 때

온프레미스 GPU가 다 찼는데 시나리오는 계속 쌓인다면, 넘치는 물량을 클라우드로 흘려보내는 것이 클라우드 버스트입니다.

- 가장 단순한 방법은 job submission 스크립트에서 온프레미스 큐 길이(`squeue`로 대기 중인 job 수 확인)를 체크해, 일정 임계치를 넘으면 같은 시나리오 매니페스트를 [K8s + Ray 클러스터](../ray-kuberay-for-beginners/) 쪽 제출 큐로 보내는 라우팅 레이어를 앞단에 두는 것입니다.
- [Slurm-on-Kubernetes](https://slinky.schedmd.com/) 같은 최신 통합 프로젝트는 Slurm 컨트롤 플레인이 K8s 파드를 워커로 관리하게 해, 온프레미스와 클라우드 노드를 하나의 Slurm 클러스터처럼 다루게 해주기도 합니다. 다만 이런 통합 레이어를 도입하기 전에는, 시나리오 매니페스트와 결과 스키마를 온프레미스/클라우드 양쪽에서 동일하게 유지하는 것만으로도 실전에서는 충분히 버스트 라우팅을 굴릴 수 있습니다.

---

## 5. 정리

Slurm은 gang scheduling, 성숙한 fair-share/QoS, GPU 토폴로지 인지 배치라는 강점 덕분에 온프레미스 GPU 팜을 이미 운영 중인 조직에서 자연스러운 선택지입니다. Job array + `--dependency`로 CPU/GPU 단계를 분리하고, QoS로 PR 검증과 야간 배치 큐를 나누는 패턴은 [K8s Kueue](../k8s-batch-scheduling-with-kueue/)에서 다룬 설계와 본질적으로 같습니다. 온프레미스 자원이 부족할 때는 같은 시나리오 매니페스트를 [K8s + Ray 클러스터](../ray-kuberay-for-beginners/)로 라우팅하는 클라우드 버스트로 확장할 수 있습니다.
