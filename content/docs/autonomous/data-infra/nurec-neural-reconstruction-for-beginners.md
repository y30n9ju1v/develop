---
title: "NuRec 입문: 3D Gaussian Splatting으로 주행 로그를 시뮬레이션 환경으로"
date: 2026-07-14T00:00:00+09:00
draft: false
tags: ["autonomous", "nvidia", "nurec", "neural-reconstruction", "gaussian-splatting", "simulation", "omniverse"]
categories: ["autonomous"]
description: "NVIDIA NuRec가 카메라·라이다 로그를 3D Gaussian Splatting으로 재구성해 시뮬레이션 가능한 환경을 만드는 원리, CARLA/Isaac Sim과의 연동 구조, novel view synthesis와 Cosmos 기반 보정 도구를 초보자 기준으로 정리합니다."
---

> 이 글은 [NVIDIA Omniverse NuRec 공식 페이지](https://developer.nvidia.com/omniverse/nurec), [NVIDIA 기술 블로그: Accelerating AV Simulation with Neural Reconstruction and World Foundation Models](https://developer.nvidia.com/blog/accelerating-av-simulation-with-neural-reconstruction-and-world-foundation-models/), [CARLA 공식 문서의 NuRec 연동 가이드](https://carla.readthedocs.io/en/0.9.16/nvidia_nurec/)를 참고해 작성했습니다.
> NuRec가 입력으로 받는 데이터 포맷은 [NCore V4 입문](../ncore-v4-for-beginners/)에서 다뤘습니다. 이 글은 그 데이터를 받아 NuRec가 실제로 무엇을 계산하는지에 집중합니다.

---

## 1. 문제: 시뮬레이터의 가상 세계는 손으로 만들어진다

[CARLA와 DORA 연동 편](../../dora/dora-rs-simulator-integration/)에서 다룬 CARLA 같은 전통적인 시뮬레이터는 도로, 건물, 나무 같은 3D 에셋을 사람이 미리 만들어서 배치합니다. 이 방식의 한계는 명확합니다 — 실제 세상은 무한히 다양한데, 에셋은 사람이 손으로 만든 만큼만 존재합니다. 특히 **희귀하거나 위험한 상황**(갑자기 튀어나오는 보행자, 흔치 않은 도로 구조, 특이한 날씨)은 "실제로 수집하고 라벨링하는 것 자체가 불가능"한 경우가 많습니다.

**NuRec**는 이 문제를 정반대 방향에서 풉니다 — 에셋을 사람이 새로 그리는 대신, **실제로 차를 몰고 다니며 찍은 카메라·라이다 로그를 3D 환경으로 그대로 재구성**합니다. 실제 세상을 시뮬레이터 안에 복사해 넣는 셈입니다.

---

## 2. NuRec가 하는 일: 센서 로그 → 3D 장면

NuRec 공식 문서는 이 라이브러리를 이렇게 소개합니다.

> "a set of agent-friendly, 3D Gaussian splatting libraries that ingest real sensor data to reconstruct and render interactive simulation in OpenUSD"

풀어보면 3단계입니다.

```
카메라 + 라이다 로그 (NCore V4 포맷)
   ↓ 재구성(Reconstruction)
USD 장면 (물체 궤적 등 메타데이터 포함)
   ↓ 렌더링 (gsplat 기반 Gaussian Splatting)
어느 시점, 어느 각도에서도 다시 볼 수 있는 인터랙티브 3D 환경
```

입력은 [NCore V4 입문](../ncore-v4-for-beginners/)에서 다룬 바로 그 포맷입니다 — NuRec 문서가 "open NCore data standard"를 언급하며 "재구성 워크플로우에 데이터를 입력하는 일관된 방법"이라고 설명하는 이유가 여기 있습니다. 재구성된 결과는 **USD**(Universal Scene Description, Pixar가 만들고 Omniverse가 표준으로 쓰는 3D 장면 포맷)로 나오고, 이 USD 장면을 실제로 화면에 그려내는 게 **gsplat**(오픈소스 Gaussian Splatting 렌더링 라이브러리)입니다.

---

## 3. 왜 폴리곤이 아니라 "Gaussian"인가

전통적인 3D 그래픽스는 물체를 삼각형(폴리곤) 메시로 표현합니다. 사람이 직접 모델링한 자동차나 건물은 이 방식이 잘 맞습니다. 하지만 카메라로 찍은 실제 나뭇잎, 흐릿한 그림자, 반사되는 유리창 같은 걸 폴리곤으로 정확히 재구성하려면 엄청나게 많은 삼각형이 필요하고, 애초에 "정확한 형태"를 알아내는 것 자체가 어렵습니다.

**3D Gaussian Splatting**은 다른 접근을 씁니다 — 장면을 딱딱한 표면(메시) 대신, 공간에 흩뿌려진 수많은 **반투명한 타원체(3D 가우시안)** 뭉치로 표현합니다. 각 가우시안은 위치, 크기, 방향, 색, 투명도를 가지고 있고, 카메라 앵글에서 이 타원체들을 겹쳐 그리면(splat, "찍어 바르다") 사진처럼 보이는 이미지가 나옵니다.

```
전통 방식: 물체 표면 = 삼각형 메시
              하나의 정확한 형태를 미리 알아야 함

3D Gaussian Splatting: 물체 = 반투명 타원체(가우시안) 수십만~수백만 개
                        여러 각도에서 찍은 사진들이 서로 앞뒤가 안 맞지 않도록
                        각 가우시안의 위치/색/투명도를 최적화로 맞춰나감
```

이 방식이 "재구성"에 유리한 이유는, 애초에 물체의 정확한 기하 구조를 몰라도 — **여러 각도에서 찍은 사진들과 앞뒤가 맞도록 가우시안들을 최적화**하기만 하면 된다는 점입니다. 실제 주행 중 카메라가 자연스럽게 여러 각도에서 같은 장면을 스쳐 지나가며 찍기 때문에, 이 최적화에 필요한 "여러 시점의 사진"이 자연스럽게 확보됩니다.

---

## 4. 진짜 어려운 부분: 원래 안 찍힌 각도를 보여주기 (Novel View Synthesis)

재구성 자체는 "원래 카메라가 지나간 경로를 그대로 재생"하는 거라면 비교적 쉽습니다. 하지만 시뮬레이션에서 진짜 필요한 건 **원래 차량이 가지 않았던 경로**(차선을 바꿨다면, 조금 더 빨리 갔다면, 다른 차와 다르게 반응했다면)를 보여주는 것 — 이걸 **Novel View Synthesis**(새로운 시점 합성)라고 부릅니다.

문제는 원래 카메라가 그 각도를 한 번도 찍은 적이 없다는 것입니다. NVIDIA 기술 블로그는 이 문제를 이렇게 설명합니다.

> "When rendering a reconstructed scene from a novel view, there can be gaps in the reconstruction, which could lead to artifacts."

즉 차선을 바꿔서 보면, 원래 카메라가 못 본 각도라 가우시안이 부족한 부분에 구멍이나 흐릿한 얼룩(아티팩트)이 생깁니다. 이걸 메우는 도구가 **Fixer**(Harmonizer라고도 불림)입니다 — NVIDIA의 생성 AI 플랫폼 **Cosmos** 기반의 생성 모델로, 구멍 난 부분을 그럴듯하게 "그려 채워 넣는(inpaint)" 역할을 합니다. 여기에 더해 **Cosmos Transfer**는 같은 장면을 다른 조명·날씨 조건으로 변주해서 생성할 수 있게 해주는 diffusion 기반 생성 모델입니다 — "비 오는 날의 같은 도로"처럼, 실제로는 그 조건에서 찍지 않은 장면도 만들어낼 수 있습니다.

또 다른 도구인 **Asset Harvester**는 반대 방향의 작업입니다 — 재구성된 장면에서 특정 물체(예: 주차된 차 한 대)만 오려내서, 다른 장면에 재사용할 수 있는 독립된 에셋으로 만듭니다.

---

## 5. CARLA와 어떻게 연결되는가

[CARLA와 DORA 연동 편](../../dora/dora-rs-simulator-integration/)에서 CARLA는 자체 렌더링 엔진으로 씬을 그린다고 봤는데, NuRec을 붙이면 이 렌더링을 완전히 대체하는 게 아니라 **병렬 렌더링 파이프라인**으로 동작합니다. CARLA 공식 문서가 설명하는 구조는 이렇습니다.

```
Python 리플레이 스크립트
   ├─→ CARLA API   → CARLA 서버가 맵/액터 상태를 관리
   └─→ NuRec gRPC API → NuRec 컨테이너가 그 상태에 맞는 프레임을 렌더링
```

즉 **CARLA가 "무엇이 어디에 있는지"(시뮬레이션 상태)를 계속 관리**하고, **NuRec은 그 상태를 받아 "그게 실제로 어떻게 보이는지"(포토리얼리스틱 렌더링)만 담당**합니다. 이 구조 덕분에 CARLA의 물리·충돌·액터 관리 로직은 그대로 두고, 화면에 그려지는 결과물만 재구성된 실제 장면으로 바꿔치기할 수 있습니다. CARLA 문서는 이 조합으로 "시나리오를 바꾸고, 합성 물체를 추가하고, 무작위 변화를 준다(예: 공을 쫓아 도로로 뛰어드는 아이)"는 시나리오 증강이 가능하다고 설명합니다.

---

## 6. 이 시리즈의 다른 조각들과 어떻게 이어지는가

- [NCore V4 입문](../ncore-v4-for-beginners/): NuRec이 입력으로 받는 센서 데이터 포맷.
- [py123d → NVIDIA NuRec(NCore)](../py123d-to-nurec/): nuScenes·Waymo 같은 공개 데이터셋이나 사내 데이터를 NCore V4로 변환해 NuRec 파이프라인에 실제로 넣는 방법.
- [CARLA 시뮬레이터와 DORA 연동하기](../../dora/dora-rs-simulator-integration/): NuRec 없이 CARLA 자체 렌더링만으로 DORA와 클로즈 루프를 구성하는 기본 구조 — NuRec은 이 구조의 "그림을 그리는 부분"만 실제 장면으로 바꿔 끼우는 것입니다.
- [Arrow로 관통하는 E2E 회귀 테스트 파이프라인](../closed-loop-regression-with-dora/): 여기까지 쌓은 조각들이 py123d → FiftyOne → DORA → Rerun으로 이어지는 하나의 회귀 테스트 파이프라인으로 합쳐지는 지점입니다.
- [Sim-to-Real 검증 방법론](../sim-to-real-validation-methodology/): 이 글이 다룬 재구성이 "사진처럼 정확한가"를 넘어, 그 위에서 낸 시뮬레이션 성능이 실제로 실차 성능을 예측하는지를 정량적으로 검증하는 방법을 다룹니다.

---

## 7. 정리

- NuRec은 사람이 손으로 만드는 3D 에셋 대신, **실제 주행 중 카메라·라이다로 찍은 로그를 그대로 3D 환경으로 재구성**하는 NVIDIA의 신경 재구성 라이브러리입니다.
- 재구성은 폴리곤 메시가 아니라 **3D Gaussian Splatting** — 공간에 흩뿌려진 반투명 타원체들을 여러 각도의 사진과 맞도록 최적화하는 방식으로 이루어집니다.
- 원래 카메라가 지나가지 않은 각도(차선 변경 등)를 보여주는 **Novel View Synthesis**가 핵심 난제이며, Cosmos 기반 **Fixer**가 그 과정에서 생기는 구멍·아티팩트를 메꿔줍니다. **Asset Harvester**는 재구성된 장면에서 개별 물체를 오려내 재사용 가능한 에셋으로 만듭니다.
- CARLA와 연동할 때 NuRec은 시뮬레이션 상태 관리(CARLA)와 화면 렌더링(NuRec, gRPC로 연결)을 분리하는 병렬 파이프라인으로 동작합니다.
- 입력 포맷([NCore V4](../ncore-v4-for-beginners/))부터 데이터 변환([py123d → NuRec](../py123d-to-nurec/)), 실제 시뮬레이터 연동([CARLA-DORA](../../dora/dora-rs-simulator-integration/))까지, 이 시리즈의 조각들이 하나의 파이프라인으로 맞물립니다.
