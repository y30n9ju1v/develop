---
title: "VS Code에서 Lean 4 + Mathlib4 셋업하기"
date: 2026-07-17T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "mathlib", "vscode", "setup"]
categories: ["programming"]
description: "elan으로 Lean 4 툴체인을 설치하고, VS Code Lean 4 확장과 lake new 템플릿으로 Mathlib4가 붙은 프로젝트를 표준 방식으로 셋업하는 방법을 정리합니다."
---

Lean 4는 VS Code를 표준 개발 환경으로 삼습니다. Infoview가 커서 위치에 따라 증명 상태(goal, hypothesis, 오류)를 실시간으로 보여주는 방식이 핵심이라, 셀을 실행해야만 결과를 보는 다른 환경보다 증명을 시행착오하며 다듬는 작업에 훨씬 잘 맞습니다. 이 글은 `elan` → VS Code 확장 → `lake new`로 Mathlib4가 붙은 프로젝트를 만드는, Lean 팀과 Mathlib 커뮤니티가 직접 유지보수하는 표준 경로를 정리합니다.

## 1. elan으로 Lean 4 툴체인 설치

`elan`은 Lean 버전 매니저입니다. 프로젝트마다 다른 Lean 버전을 요구할 수 있는데(`lean-toolchain` 파일로 지정), `elan`이 그 파일을 보고 알맞은 버전을 자동으로 골라 씁니다.

```bash
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
source ~/.profile
lean --version
```

> **Apple Silicon(M1/M2/M3 등) Mac 기준**: `elan`/Lean 4 자체는 arm64 네이티브로 잘 동작합니다. 뒤에서 받는 Mathlib 바이너리 캐시(`lake exe cache get`)도 arm64를 지원하니, 이 경로에서는 별도 우회가 필요 없습니다.

## 2. VS Code에 Lean 4 확장 설치

VS Code를 열고 확장 탭(`Cmd+Shift+X`)에서 `lean4`를 검색해, `leanprover`가 배포하는 공식 **Lean 4** 확장을 설치합니다. 이 확장이 Infoview, 구문 강조, `#eval`/`#check` 결과 표시, 진행 상황(파일 하단 바)까지 다 처리합니다.

## 3. Mathlib이 포함된 프로젝트 생성

`lake new` 명령에 `math` 템플릿을 지정하면, Mathlib4를 의존성으로 미리 잡아둔 프로젝트가 생성됩니다.

```bash
lake +v4.24.0 new my_project math
```

`+v4.24.0` 부분은 사용할 Lean 버전을 지정하는 `elan` 문법입니다 — [Mathlib4 저장소](https://github.com/leanprover-community/mathlib4)의 `lean-toolchain` 파일을 확인해서 Mathlib이 현재 어떤 버전을 쓰는지 맞춰주는 것이 안전합니다(버전이 어긋나면 뒤의 `lake update`/`lake exe cache get` 단계에서 캐시가 안 맞아 처음부터 컴파일하게 될 수 있습니다).

`math` 템플릿이 만들어주는 프로젝트는 다음을 이미 갖추고 있습니다:

- `lakefile.toml`(또는 `lakefile.lean`)에 Mathlib4를 `require`로 추가
- Mathlib4가 사용하는 것과 같은 버전을 가리키는 `lean-toolchain`

기존 프로젝트에 나중에 Mathlib을 추가하고 싶다면, `lakefile.toml`에 아래를 넣으면 됩니다.

```toml
[[require]]
name = "mathlib"
scope = "leanprover-community"
```

(`lakefile.lean` 형식을 쓰는 구버전 프로젝트라면 `require "leanprover-community" / "mathlib" @ git "v4.24.0"` 같은 문법을 씁니다 — 버전 문자열은 목표하는 Mathlib 릴리스에 맞춰 바꿉니다.)

## 4. 의존성 받고 바이너리 캐시 내려받기

```bash
cd my_project
lake update
lake exe cache get
```

`lake update`가 `lakefile`에 적힌 의존성(Mathlib4 및 그 하위 의존성)을 실제로 받아옵니다. `lake exe cache get`은 Mathlib을 처음부터 컴파일하는 대신 미리 빌드된 바이너리(`.olean`) 캐시를 내려받습니다 — 이 단계를 건너뛰면 `lake build`가 Mathlib 전체를 소스에서 컴파일하느라 수십 분 이상 걸리니 반드시 실행하세요.

## 5. VS Code로 열고 확인하기

```bash
code .
```

또는 VS Code에서 File → Open Folder로 `my_project` 폴더를 엽니다. 확장이 로드되면 파일 하단에 Lean 서버 상태(진행률 바)가 표시됩니다 — 처음 파일을 열 때 프로젝트를 elaboration하느라 시간이 좀 걸릴 수 있습니다.

새 파일(`Test.lean` 등)을 만들어 Mathlib을 실제로 써봅니다.

```lean
import Mathlib.Data.Real.Basic
import Mathlib.Analysis.MeanInequalities

example (a b : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b) : a * b ≤ (a ^ 2 + b ^ 2) / 2 := by
  nlinarith [sq_nonneg (a - b)]
```

커서를 `by` 다음 줄에 두면 오른쪽(또는 별도 탭의) Infoview에 남은 목표(goal)가 실시간으로 뜨고, 증명이 끝나면 목표가 사라집니다. 이 실시간 피드백이 VS Code 워크플로우의 핵심입니다.

## 6. 알아둘 점

- **버전을 맞추는 것이 중요합니다.** `lean-toolchain`이 가리키는 Lean 버전과 `lakefile`이 요구하는 Mathlib 버전이 서로 호환되지 않으면 `lake update`/`cache get` 단계에서 문제가 생깁니다. `lake +v버전 new` 명령의 버전 태그를 Mathlib4 저장소의 최신 `lean-toolchain`과 맞추는 것으로 시작하세요.
- **`lake exe cache get`은 프로젝트를 바꿀 때마다 다시 필요할 수 있습니다.** Mathlib 버전을 업데이트(`lake update` 후 커밋 해시가 바뀜)하면 캐시도 그 시점 것으로 다시 받아야 컴파일을 피할 수 있습니다.
- **Loogle 등 검색 도구를 함께 씁니다.** Mathlib은 정리 개수가 매우 많아서, 원하는 정리를 이름으로 못 찾을 때가 흔합니다. VS Code 명령 팔레트의 "Loogle: Search"(또는 웹의 [loogle.lean-lang.org](https://loogle.lean-lang.org))로 타입 시그니처 기반 검색을 해보는 것이 빠릅니다.
