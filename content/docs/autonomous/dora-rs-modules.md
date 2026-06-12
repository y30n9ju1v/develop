---
title: "DORA 모듈: 재사용 가능한 노드 서브그래프"
date: 2026-06-13T00:00:00+09:00
draft: false
tags: ["robotics", "dora", "modules", "yaml"]
categories: ["autonomous"]
description: "DORA 모듈로 노드 서브그래프를 재사용하는 방법 — 정의, 파라미터, 중첩, 확장(expand)까지 정리합니다."
---

> 이 글은 [DORA 모듈 문서](https://dora-rs.ai/dora/concepts/modules.html)를 참고해 작성했습니다.

---

## 1. 모듈이란?

모듈은 **노드들의 서브그래프를 재사용 가능한 단위로 묶는 컴파일 타임 추상화**입니다.

핵심: **모듈은 런타임에 존재하지 않습니다.** `dora build` 또는 `dora run` 시 모듈이 인라인으로 전개(expand)되어, 런타임은 일반 노드들만 봅니다. 이는 추상화 비용이 전혀 없다는 의미입니다.

---

## 2. 모듈 정의

모듈 파일은 `.module.yml` 확장자를 사용합니다.

```yaml
# modules/navigation.module.yml

name: navigation          # 모듈 식별자

inputs:
  - goal_pose             # 필수 입력 포트
  - map                   # 필수 입력 포트

inputs_optional:
  - initial_pose          # 연결하지 않아도 되는 선택적 입력

outputs:
  - cmd_vel               # 부모 데이터플로우에 노출할 출력

nodes:
  - id: planner
    path: ./planner
    inputs:
      goal: _mod/goal_pose    # _mod/포트명 → 모듈 입력 포트 참조
      map: _mod/map
    outputs:
      - path

  - id: controller
    path: ./controller
    inputs:
      path: planner/path
      pose: _mod/initial_pose
    outputs:
      - cmd_vel               # 이 출력이 모듈의 cmd_vel로 노출됨
```

`_mod/포트명` 구문으로 모듈 입력 포트를 참조합니다. 전개 시 부모 데이터플로우의 실제 연결로 교체됩니다.

---

## 3. 모듈 사용

```yaml
# dataflow.yml

nodes:
  - id: localization
    path: ./localization
    outputs:
      - goal
      - map

  - id: nav_stack           # 모듈 인스턴스
    module: modules/navigation.module.yml
    inputs:
      goal_pose: localization/goal   # 모듈 입력 포트에 연결
      map: localization/map

  - id: motor_driver
    path: ./motor_driver
    inputs:
      cmd: nav_stack/cmd_vel         # 모듈 출력은 <모듈ID>/<출력명>으로 접근
```

`path:` 대신 `module:`을 쓰고, 모듈의 입력 포트를 `inputs:`으로 연결합니다. 모듈 출력은 `<모듈ID>/<출력명>` 형식으로 참조합니다.

---

## 4. 파라미터

모듈에 설정값을 주입할 수 있습니다.

```yaml
# 사용 측
- id: fast_nav
  module: modules/navigation.module.yml
  inputs:
    goal_pose: localization/goal
    map: localization/map
  params:
    speed: "2.0"
    mode: turbo
```

모듈 내부에서는 `$PARAM_<대문자키>` 형식으로 참조합니다.

```yaml
# modules/navigation.module.yml 내부

nodes:
  - id: planner
    path: ./planner
    args: --speed $PARAM_SPEED --mode $PARAM_MODE
```

파라미터는 환경 변수로도 주입되므로, `args` 외에 노드 코드에서 `os.environ["PARAM_SPEED"]`로도 읽을 수 있습니다.

파라미터 키는 **영문자, 숫자, 밑줄**만 허용됩니다.

---

## 5. 중첩 모듈

모듈 안에서 다른 모듈을 참조할 수 있습니다. 최대 8단계까지 중첩 가능합니다.

```yaml
# modules/full_stack.module.yml

name: full_stack

inputs:
  - sensor_data

outputs:
  - cmd_vel

nodes:
  - id: perception
    module: modules/perception.module.yml
    inputs:
      raw: _mod/sensor_data
    outputs:
      - detections

  - id: nav
    module: modules/navigation.module.yml
    inputs:
      obstacles: perception/detections
    outputs:
      - cmd_vel
```

전개 후 노드 ID는 `outer.inner.some_node` 형식으로 완전히 한정됩니다.

---

## 6. 모듈 전개 확인

`dora expand`로 모듈이 어떻게 인라인으로 펼쳐지는지 확인할 수 있습니다.

```bash
# 데이터플로우 전체 전개
dora expand dataflow.yml

# 모듈 단독 검증
dora expand --module modules/navigation.module.yml
```

전개 과정:
1. 노드 ID 앞에 모듈 ID 접두사 추가
2. `_mod/` 참조를 부모의 실제 연결로 교체
3. 내부 교차 참조 재작성
4. 모듈 출력을 내부 노드 출력으로 매핑
5. 파라미터를 `args`에 치환

---

## 7. 모듈 수준 빌드

모듈 파일에 `build:` 명령을 추가하면, 내부 노드 빌드 전에 먼저 실행됩니다.

```yaml
# modules/navigation.module.yml

name: navigation
build: pip install -r requirements.txt

inputs:
  - goal_pose

outputs:
  - cmd_vel

nodes:
  - ...
```

---

## 8. 시각화

```bash
dora graph dataflow.yml
```

모듈 경계가 Mermaid 서브그래프로 렌더링되어 전체 아키텍처를 한눈에 볼 수 있습니다.

---

## 9. 보안 제약

| 제약 | 값 |
|------|----|
| 모듈 파일 최대 크기 | 1 MB |
| 최대 중첩 깊이 | 8단계 |
| 파라미터 키 허용 문자 | 영문자, 숫자, 밑줄 |
| 경로 제한 | 베이스 디렉터리 외부 디렉터리 탐색 불가 |

---

## 10. 정리

| 상황 | 모듈 활용법 |
|------|-------------|
| 반복되는 노드 조합 | 모듈로 묶어 재사용 |
| 알고리즘 교체 실험 | 같은 인터페이스, 다른 내부 구현 |
| 속도/모드 설정 변경 | `params:`로 주입 |
| 대형 파이프라인 관리 | 중첩 모듈로 계층화 |

모듈은 런타임 오버헤드 없이 코드 재사용과 파이프라인 구조화를 동시에 달성하는 DORA의 핵심 추상화입니다.
