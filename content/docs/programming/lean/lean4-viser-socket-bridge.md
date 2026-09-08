---
title: "Lean 4 계산을 소켓으로 viser에 띄우기"
date: 2026-09-08T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "viser", "3d-visualization", "slam", "socket"]
categories: ["programming"]
description: "Lean 4로 계산한 벡터·회전·궤적을 표준 라이브러리만으로 JSON 줄로 만들어 TCP 소켓으로 흘려보내고, 파이썬 브리지가 viser 씬으로 옮겨 브라우저에서 눈으로 확인하는 셋업을 정리합니다."
---

SLAM이나 선형대수를 Lean 4로 공부하다 보면 계산은 맞게 나온 것 같은데 "이게 실제로 어떤 모양인지"가 안 보입니다. 회전행렬을 하나 적용했을 때 점들이 정말 원하는 방향으로 도는지, SE(3) 궤적이 정말 그럴듯한 경로인지는 숫자만 봐서는 알기 어렵습니다.

이 글은 그 간극을 메우는 가장 단순한 셋업을 정리합니다 — **Lean 4가 계산 결과를 JSON 한 줄로 만들어 TCP 소켓으로 보내면, 파이썬 브리지가 그걸 받아 [viser](https://github.com/nerfstudio-project/viser) 씬으로 옮기고, 브라우저에서 마우스로 돌려보며 확인**합니다.

> **검증 메모.** 아래 Lean 코드는 표준 라이브러리(`IO`, `IO.FS`, `IO.Process`)만 씁니다 — Mathlib도, JSON 라이브러리도 필요 없습니다. 최근 Lean 4 v4 툴체인 기준으로 썼지만 실행해 검증하진 않았으니, 여러분의 툴체인에서 `lake exe`로 빌드해 확인하세요. 전송 예시는 `sh`와 `nc`가 있는 macOS·Linux(POSIX) 환경을 전제로 합니다. 파이썬 브리지는 [viser 현행 Scene API](https://viser.studio/main/api/core/scene_api/)(`points=` · `thickness=` · `world_axes.visible`)를 따르며, 부록 A의 C FFI 심은 여러분의 툴체인에서 빌드 확인이 필요한 선택 사항입니다.

## 전체 그림

```
 Lean 4 실행파일                파이썬 브리지                     브라우저
 (lake exe)                     (bridge.py)                      (viser 뷰어)
      │                              │                                │
      │  개행 구분 JSON               │   server.scene.add_*(...)       │
      │  127.0.0.1:7000  ─── TCP ──►  │  ───────  websocket  ────────►  │
      │  {"op":"point_cloud",...}\n   │                                │
```

핵심은 **브리지가 왜 필요한가**입니다. viser는 파이썬에서 씬을 스크립트하는 라이브러리이고, 브라우저를 상대하는 웹서버(HTTP + websocket)를 자기가 따로 띄웁니다. Lean이 viser의 websocket에 직접 말할 수는 없습니다. 그래서 중간에 파이썬 프로세스 하나가 필요합니다 — 이 프로세스가 viser 서버와 씬을 소유하면서, 별도의 TCP 포트로 Lean이 보내는 명령을 받아 `server.scene.add_point_cloud(...)` 같은 호출로 번역합니다.

전송을 stdout 파이프나 FIFO가 아니라 **TCP 소켓**으로 두는 이유는 공부 워크플로에 맞기 때문입니다. 뷰어(브리지 + 브라우저)는 한 번 띄워 놓고, Lean 쪽은 코드를 고치며 `lake exe`를 수십 번 다시 돌립니다. 매 실행이 소켓에 붙었다 떨어지면 그만이고, 브리지와 브라우저 상태는 유지됩니다.

## 메시지 프로토콜

한 줄에 명령 하나, 개행으로 구분되는 JSON입니다. 필요한 op은 여섯 개면 충분합니다.

| op | 필드 | viser에서 하는 일 |
|---|---|---|
| `clear` | — | 지금까지 추가한 노드 전부 제거 |
| `point_cloud` | `name`, `points` `[[x,y,z],…]`, `color` `[r,g,b]` 또는 `colors` `[[r,g,b],…]`, `size` | `add_point_cloud` |
| `frame` | `name`, `wxyz` `[w,x,y,z]`, `position` `[x,y,z]` | `add_frame` (좌표축) |
| `line` | `name`, `points` `[[x,y,z],…]`, 선택 `width` (월드 단위) | `add_spline_catmull_rom` |
| `label` | `name`, `text`, `position` | `add_label` |
| `sleep` | `seconds` | 브리지가 그만큼 멈춤 — 애니메이션 재생용 |

이름은 `/`로 시작하는 경로입니다(`/robot/camera`처럼). 슬래시가 씬 트리의 부모-자식을 정하고, 부모 프레임을 옮기면 자식이 함께 움직입니다. **같은 종류의** 노드에 같은 이름을 다시 보내면 갱신됩니다. 같은 이름을 다른 종류(`point_cloud` 뒤에 `frame` 등)로 쓰면 기존 노드를 지우고 새로 만듭니다. `frame`은 같은 종류일 때 자식을 지우지 않도록 자세(`wxyz`·`position`)만 갱신합니다. `line`은 점 2개면 직선, 3개 이상이면 Catmull–Rom 곡선입니다.

> **좌표계.** viser 월드는 기본이 **+Z up**, 단위는 미터입니다. `frame`의 `wxyz`는 **w가 맨 앞**인 쿼터니언 순서입니다(단위 회전은 `[1,0,0,0]`). Lean 쪽에서 쓰는 규약과 축·순서를 맞춰 두세요.

## 브리지 (`bridge.py`)

```python
import asyncio
import json

import numpy as np
import viser

server = viser.ViserServer()  # http://localhost:8080
server.scene.world_axes.visible = True

# 우리가 추가한 노드의 종류와 핸들. clear·같은 이름의 교체에 사용한다.
handles: dict[str, tuple[str, object]] = {}


def remove_all() -> None:
    for _, handle in list(handles.values()):
        try:
            handle.remove()           # 부모를 지우면 자식도 함께 사라질 수 있다 — 중복 remove 는 무시
        except Exception:
            pass
    handles.clear()


def replace(name: str, kind: str, handle) -> None:
    if name in handles:
        handles[name][1].remove()
    handles[name] = (kind, handle)


def apply(cmd: dict) -> None:
    op = cmd.get("op")

    if op == "clear":
        remove_all()

    elif op == "point_cloud":
        points = np.asarray(cmd["points"], dtype=np.float32).reshape(-1, 3)
        if "color" in cmd:
            colors = tuple(cmd["color"])                       # 하나의 (r, g, b)
        else:
            colors = np.asarray(cmd.get("colors", []), dtype=np.uint8).reshape(-1, 3)
        replace(cmd["name"], "point_cloud", server.scene.add_point_cloud(
            cmd["name"], points=points, colors=colors,
            point_size=cmd.get("size", 0.02),
        ))

    elif op == "frame":
        name = cmd["name"]
        wxyz = tuple(cmd.get("wxyz", (1.0, 0.0, 0.0, 0.0)))
        position = tuple(cmd.get("position", (0.0, 0.0, 0.0)))
        entry = handles.get(name)
        if entry is not None and entry[0] == "frame":
            handle = entry[1]
            handle.wxyz = wxyz            # 자식 노드를 지우지 않고 자세만 갱신 (애니메이션·프레임 체이닝)
            handle.position = position
        else:
            replace(name, "frame", server.scene.add_frame(
                name, wxyz=wxyz, position=position,
                axes_length=cmd.get("axes_length", 0.3),
                axes_radius=cmd.get("axes_radius", 0.02),
            ))

    elif op == "line":
        points = np.asarray(cmd["points"], dtype=np.float32).reshape(-1, 3)
        replace(cmd["name"], "line", server.scene.add_spline_catmull_rom(
            cmd["name"], points=points,
            thickness=cmd.get("width", 0.01), thickness_units="world",
        ))

    elif op == "label":
        replace(cmd["name"], "label", server.scene.add_label(
            cmd["name"], text=cmd["text"],
            position=tuple(cmd.get("position", (0.0, 0.0, 0.0))),
        ))

    else:
        print("[bridge] 모르는 op:", cmd)


async def handle_conn(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    peer = writer.get_extra_info("peername")
    print(f"[bridge] 접속: {peer}")
    while True:
        raw = await reader.readline()
        if not raw:
            break
        line = raw.decode("utf-8").strip()
        if not line:
            continue
        try:
            cmd = json.loads(line)
        except json.JSONDecodeError as exc:
            print(f"[bridge] JSON 파싱 실패: {exc}: {line[:120]}")
            continue
        if cmd.get("op") == "sleep":
            await asyncio.sleep(float(cmd.get("seconds", 0.5)))
            continue
        try:
            apply(cmd)
        except Exception as exc:  # 공부용 — 한 줄 실패로 전체를 죽이지 않는다
            print(f"[bridge] 적용 실패: {exc}: {line[:120]}")
    writer.close()
    print(f"[bridge] 종료: {peer}")


async def main() -> None:
    srv = await asyncio.start_server(handle_conn, "127.0.0.1", 7000)
    print("[bridge] 127.0.0.1:7000 에서 대기 — viser: http://localhost:8080")
    async with srv:
        await srv.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
```

viser의 `ViserServer()`는 자기 이벤트 루프를 별도 스레드에서 돌리므로, 메인 스레드에서 우리 TCP 서버용 `asyncio.run(main())`을 따로 돌려도 서로 간섭하지 않습니다.

실행:

```bash
pip install viser numpy
python bridge.py
# 출력된 http://localhost:8080 을 브라우저로 연다
```

## Lean 쪽: 표준 라이브러리만으로

`lake new viser-lean`으로 만든 기본 실행 프로젝트의 `Main.lean` 하나면 됩니다. JSON은 문자열 조립으로 만들고, `nc`가 그 줄들을 TCP로 보냅니다.

```lean
-- Main.lean  ·  표준 라이브러리만 사용. Mathlib 불필요.

abbrev Vec3 := Float × Float × Float

/-- z축 둘레로 θ(라디안)만큼 회전. 순수 대수, 라이브러리 없음. -/
def rotZ (θ : Float) : Vec3 → Vec3
  | (x, y, z) =>
    (Float.cos θ * x - Float.sin θ * y,
     Float.sin θ * x + Float.cos θ * y,
     z)

/-- 5×5 격자를 xy평면에 깔아 둔다. -/
def grid : Array Vec3 := Id.run do
  let mut pts : Array Vec3 := #[]
  for i in [0:5] do
    for j in [0:5] do
      pts := pts.push (Float.ofNat i * 0.2, Float.ofNat j * 0.2, 0.0)
  return pts

-- 아래는 전부 문자열 조립이다. JSON 문자열에는 반드시 이스케이프를 적용한다.

def hexDigit (n : Nat) : Char :=
  let d := n % 16
  if d < 10 then Char.ofNat ('0'.toNat + d)
  else Char.ofNat ('a'.toNat + (d - 10))

def hex4 (n : Nat) : String :=
  String.mk [
    hexDigit (n / 4096), hexDigit (n / 256),
    hexDigit (n / 16), hexDigit n
  ]

def quote (s : String) : String :=
  "\"" ++ s.foldl (fun acc c =>
    acc ++ match c with
      | '\"' => "\\\""
      | '\\' => "\\\\"
      | '\n' => "\\n"
      | '\r' => "\\r"
      | '\t' => "\\t"
      | '\x08' => "\\b"
      | '\x0c' => "\\f"
      | _ => if c.toNat < 0x20 then "\\u" ++ hex4 c.toNat else String.singleton c
  ) "" ++ "\""

def jsonNum (x : Float) : String := toString x

def jsonVec3 : Vec3 → String
  | (x, y, z) => s!"[{jsonNum x},{jsonNum y},{jsonNum z}]"

def jsonArray (items : Array String) : String :=
  "[" ++ String.intercalate "," items.toList ++ "]"

def field (key val : String) : String := quote key ++ ":" ++ val

def obj (fields : Array String) : String :=
  "{" ++ String.intercalate "," fields.toList ++ "}"

def clearMsg : String := obj #[field "op" (quote "clear")]

def pointCloudMsg (name : String) (pts : Array Vec3)
    (color : Nat × Nat × Nat) (size : Float) : String :=
  let (r, g, b) := color
  obj #[
    field "op" (quote "point_cloud"),
    field "name" (quote name),
    field "points" (jsonArray (pts.map jsonVec3)),
    field "color" s!"[{r},{g},{b}]",
    field "size" (jsonNum size)
  ]

def frameMsg (name : String) (wxyz : Float × Float × Float × Float)
    (pos : Vec3) : String :=
  let (w, x, y, z) := wxyz
  obj #[
    field "op" (quote "frame"),
    field "name" (quote name),
    field "wxyz" s!"[{jsonNum w},{jsonNum x},{jsonNum y},{jsonNum z}]",
    field "position" (jsonVec3 pos)
  ]

def lineMsg (name : String) (pts : Array Vec3) : String :=
  obj #[
    field "op" (quote "line"),
    field "name" (quote name),
    field "points" (jsonArray (pts.map jsonVec3))
  ]

def labelMsg (name text : String) (pos : Vec3) : String :=
  obj #[
    field "op" (quote "label"),
    field "name" (quote name),
    field "text" (quote text),
    field "position" (jsonVec3 pos)
  ]

def sleepMsg (seconds : Float) : String :=
  obj #[field "op" (quote "sleep"), field "seconds" (jsonNum seconds)]

/-- 줄들을 실행마다 다른 임시 파일에 쓰고 `nc`로 브리지에 흘려보낸다. -/
def sendToBridge (lines : Array String) : IO Unit := do
  let nonce ← IO.rand 0 4294967295
  let tmp : System.FilePath := s!"/tmp/viser-lean-{nonce}.jsonl"
  IO.FS.writeFile tmp (String.intercalate "\n" lines.toList ++ "\n")
  try
    let result ← IO.Process.output {
      cmd  := "sh"
      args := #["-c", s!"nc -w 1 127.0.0.1 7000 < {tmp}"]
    }
    if result.exitCode != 0 then
      IO.eprintln s!"[viser] 전송 실패 ({result.exitCode}): {result.stderr}"
  finally
    IO.FS.removeFile tmp

def main : IO Unit := do
  let source := grid
  let rotated := source.map (rotZ 0.6)
  sendToBridge #[
    clearMsg,
    frameMsg "/world" (1.0, 0.0, 0.0, 0.0) (0.0, 0.0, 0.0),
    pointCloudMsg "/original" source (80, 140, 255) 0.03,
    pointCloudMsg "/rotated"  rotated (255, 120, 80) 0.03
  ]
  IO.println "보냄. 브라우저에서 http://localhost:8080 확인"
```

```bash
lake exe viser-lean
```

브라우저에 파란 격자와, `z`축 둘레로 0.6 rad 돈 주황 격자가 겹쳐 나타납니다. `rotZ`의 각도만 바꿔 다시 실행하면 뷰어는 그대로 두고 격자만 갱신됩니다.

## 첫 실행: 두 터미널로 끝내기

처음에는 아래 순서만 그대로 따르세요. `bridge.py`와 Lean 프로그램은 서로 다른 터미널에서 실행합니다.

1. **터미널 1**에서 위의 파이썬 코드를 `bridge.py`로 저장하고 브리지를 켭니다.

   ```bash
   pip install viser numpy
   python bridge.py
   ```

   `[bridge] 127.0.0.1:7000 에서 대기`라는 줄과 viser URL이 보이면 준비가 끝났습니다. 그 URL(보통 `http://localhost:8080`)을 브라우저로 엽니다.

2. **터미널 2**에서 Lean 실행 프로젝트를 만들고, 위 Lean 코드를 `viser-lean/Main.lean`에 붙여 넣습니다.

   ```bash
   lake new viser-lean
   cd viser-lean
   lake exe viser-lean
   ```

3. 브라우저에 **파란 5×5 격자**, 그 위에 겹친 **주황 격자**, 원점의 **좌표축**이 보이면 성공입니다. 터미널 2를 다시 실행해도 브리지와 브라우저는 그대로 두면 됩니다.

안 보일 때는 이 순서로 확인하세요.

* 터미널 1이 아직 실행 중이고 `127.0.0.1:7000`에서 대기 중인지 확인합니다. 터미널 2에 `[viser] 전송 실패`가 나오면 대개 브리지가 꺼졌거나 포트가 다릅니다.
* 브라우저 주소는 추측하지 말고 브리지가 출력한 URL을 사용합니다. 8080이 이미 사용 중이면 viser가 다른 포트를 선택할 수 있습니다.
* `nc -h`가 동작하는지 확인합니다. 없다면 설치하거나, 바로 아래 설명처럼 `socat`으로 전송 명령을 바꿉니다.
* 브리지가 `적용 실패`를 출력하면 그 줄의 JSON과 op 이름을 먼저 확인합니다. 파이썬 traceback을 무시하고 Lean 코드만 고치기 시작하면 원인을 놓치기 쉽습니다.

왜 `nc`에 맡기는가: Lean 표준 라이브러리에는 TCP 소켓이 없습니다. 실행마다 다른 임시 파일에 JSON 줄을 쓰고 `nc -w 1 127.0.0.1 7000 < file`로 보낸 뒤 파일을 지웁니다. 씬 갱신은 브리지가 줄을 받는 즉시 반영되지만, 일부 `nc` 구현은 stdin EOF 뒤에도 연결을 유지합니다. 그래서 `-w 1`로 약 1초 안에 끝내며, 매 실행 끝의 이 지연은 정상입니다. `-N`의 뜻은 구현마다 다릅니다. **`nc -h` 또는 `man nc`에서 `-N`이 “stdin EOF 때 소켓을 닫는다”라고 명시된 경우에만** `nc -N 127.0.0.1 7000 < file`로 바꿔 지연을 없애세요. `nc`가 없으면 `socat - TCP:127.0.0.1:7000`. 브리지가 안 떠 있으면 연결이 거부되어 즉시 실패하고 위 `IO.eprintln` 경고가 찍힙니다. Lean이 직접 소켓을 오래 잡게 하려면 부록 A를 보세요.

> **숫자 주의.** `toString (x : Float)`는 `inf`·`nan`을 그대로 문자열로 내보내는데 이건 유효한 JSON이 아닙니다. 발산할 수 있는 계산이라면 보내기 전에 값을 검사하거나 클램프하세요.

> **뒤 예제의 사용법.** 아래 두 예제는 첫 번째 `Main.lean`의 `Vec3`, JSON 메시지 함수, `sendToBridge`를 그대로 사용합니다. 공통 정의는 남기고, 시험할 예제 하나의 정의를 그 아래에 더한 뒤 **기존 `def main`만 그 예제의 `main`으로 교체**하세요. 두 예제의 `main`을 한 파일에 함께 붙이면 이름이 중복됩니다.

## SLAM 예: 프레임 체이닝으로 SE(3) 감각 잡기

포즈를 `(q, t)` — `(w, x, y, z)` 순서의 단위 쿼터니언과 평행이동 — 로 다룹니다. 핵심은 **씬 트리로 SE(3) 합성을 대신하는 것**입니다. 카메라를 로봇 로컬 좌표계에서 한 번만 정의해 `/robot`의 자식(`/robot/camera`)으로 두면, 이후 `/robot`의 자세만 갱신해도 카메라의 월드 자세는 뷰어가 `T_world_robot · T_robot_camera`로 합성해 줍니다. viser 책 2장(프레임과 변환), 9장(재생)과 곧장 이어집니다.

```lean
abbrev Quat := Float × Float × Float × Float   -- (w, x, y, z)
abbrev Pose := Quat × Vec3

/-- z축 yaw 회전을 단위 쿼터니언 (w, x, y, z) 로. -/
def yawQuat (angle : Float) : Quat :=
  let h := angle / 2.0
  (Float.cos h, 0.0, 0.0, Float.sin h)

/-- 반지름 3인 원을 돌며 진행 방향을 바라보는 로봇의 월드 포즈. n=0이면 빈 궤적. -/
def circleTrajectory (n : Nat) : Array Pose :=
  if n == 0 then #[]
  else Id.run do
    let mut poses := #[]
    for k in [0:n] do
      let t := 2.0 * 3.141592653589793 * Float.ofNat k / Float.ofNat n
      let pos : Vec3 := (3.0 * Float.cos t, 3.0 * Float.sin t, 0.0)
      poses := poses.push (yawQuat (t + 3.141592653589793 / 2.0), pos)
    return poses

def trajectoryMsgs (poses : Array Pose) : Array String := Id.run do
  let mut msgs := #[clearMsg]
  -- 로봇 프레임을 먼저 만들고, 그 자식으로 카메라를 로봇 로컬 좌표에 한 번만 정의한다.
  msgs := msgs.push (frameMsg "/robot" (yawQuat 0.0) (0.0, 0.0, 0.0))
  msgs := msgs.push (frameMsg "/robot/camera" (yawQuat 0.0) (0.3, 0.0, 0.2))
  let mut path : Array Vec3 := #[]
  for (q, pos) in poses do
    msgs := msgs.push (frameMsg "/robot" q pos)   -- 이후엔 /robot 자세만 갱신 — 카메라가 딸려온다
    path := path.push pos
    msgs := msgs.push (sleepMsg 0.04)
  msgs := msgs.push (lineMsg "/path" path)
  return msgs

def main : IO Unit :=
  sendToBridge (trajectoryMsgs (circleTrajectory 60))
```

`/robot`이 원을 도는 동안 `/robot/camera`는 코드에서 한 번도 다시 계산하지 않는데도 로봇에 붙어 함께 돕니다 — 이게 부모 프레임에 자식 프레임을 매다는 SE(3) 합성입니다. `frameMsg "/robot" q pos`를 매 스텝 보내지만 브리지가 기존 핸들의 `wxyz`·`position`만 갱신하므로 자식은 지워지지 않습니다. `circleTrajectory 0`은 로봇·카메라만 있는 정지 장면을 보냅니다.

## 선형대수 예: Gram–Schmidt를 눈으로

세 벡터에 순서대로 그람-슈미트를 돌리면서, 각 단계의 원본 벡터와 정규직교화된 결과를 차례로 내보냅니다. Lean은 부분 결과를 줄로 뱉기만 하고, 재생 속도는 브리지의 `sleep`이 맡습니다.

```lean
def dot : Vec3 → Vec3 → Float
  | (a, b, c), (x, y, z) => a * x + b * y + c * z

def scale (k : Float) : Vec3 → Vec3
  | (x, y, z) => (k * x, k * y, k * z)

def vsub : Vec3 → Vec3 → Vec3
  | (a, b, c), (x, y, z) => (a - x, b - y, c - z)

def norm (v : Vec3) : Float := Float.sqrt (dot v v)

/-- v 를 단위벡터 u 위로 정사영. -/
def project (u v : Vec3) : Vec3 := scale (dot v u) u

/-- 기저를 순서대로 그람-슈미트. 각 단계의 원본과 정규직교 결과를 메시지로 남긴다. -/
def gramSchmidtMsgs (input : Array Vec3) : Array String := Id.run do
  let mut msgs : Array String := #[clearMsg]
  let mut basis : Array Vec3 := #[]
  let mut i := 0
  for v in input do
    msgs := msgs.push (lineMsg s!"/gs/raw{i}" #[(0.0, 0.0, 0.0), v])
    msgs := msgs.push (sleepMsg 0.6)
    let mut w := v
    for u in basis do
      w := vsub w (project u w)          -- 이미 만든 방향 성분을 뺀다
    let len := norm w
    if len < 0.000001 then
      -- 종속 벡터는 새 기저 방향을 만들지 못한다. 0으로 나누어 NaN을 만들지 않는다.
      msgs := msgs.push (labelMsg s!"/gs/skip{i}" "dependent: skipped" (0.0, 0.0, 0.0))
    else
      let q := scale (1.0 / len) w        -- 정규화
      basis := basis.push q
      msgs := msgs.push (lineMsg s!"/gs/q{i}" #[(0.0, 0.0, 0.0), q])
      msgs := msgs.push (sleepMsg 0.6)
    i := i + 1
  return msgs

def main : IO Unit :=
  sendToBridge (gramSchmidtMsgs #[(2.0, 1.0, 0.3), (1.0, 2.0, 0.2), (0.2, 0.1, 1.5)])
```

원본 벡터가 하나 뜨면, 곧바로 그 벡터에서 앞서 만든 직교 방향들을 뺀 뒤 정규화한 `q`가 나타납니다. 세 번 반복하면 서로 직각인 단위벡터 셋이 남습니다 — `dot`으로 0을 확인하는 것과, 축들이 실제로 직각인 걸 뷰어에서 보는 것은 이해에 주는 무게가 다릅니다. 입력이 선형종속이면 새 방향 대신 `dependent: skipped` 레이블이 나타납니다.

## 한계와 업그레이드 경로

- **배치 전송입니다.** 한 번 `lake exe` = 한 번 연결해서 줄들을 쏟고 끊습니다. 긴 증명 세션에서 `#eval`을 눌러가며 조금씩 밀어 넣는 방식은 지속 연결이 필요하고, 그건 Lean이 소켓을 직접 잡아야 합니다(부록 A).
- **단방향입니다.** 브라우저에서 슬라이더를 움직여 Lean에 되먹이는 상호작용은 이 셋업 밖입니다. 그런 건 파이썬 브리지 안에서 viser GUI 콜백으로 처리하고, Lean은 데이터 공급자로만 두는 편이 낫습니다.
- **좌표계 실수가 가장 흔한 버그입니다.** 축 순서, `wxyz` 대 `xyzw`, up 방향(+Z/+Y), 도/라디안 — 뭔가 이상하면 여기부터 의심하세요.

## 부록 A: `nc` 없이 — Lean에서 직접 소켓 열기 (스케치)

지속 연결이나 스트리밍이 필요하면 C FFI로 POSIX 소켓을 감쌉니다. 아래는 뼈대이며, 여러분의 툴체인에서 빌드를 확인해야 합니다(참고: [Lean FFI 문서](https://lean-lang.org/lean4/doc/dev/ffi.html)).

```c
// c/socket_shim.c
#include <lean/lean.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

// 127.0.0.1:port 로 connect. 성공하면 fd(>=0)를 UInt32 로 돌려준다.
LEAN_EXPORT lean_obj_res lean_viser_connect(b_lean_obj_arg host, uint32_t port, lean_obj_arg world) {
    (void)world;
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0)
        return lean_io_result_mk_error(lean_mk_io_user_error(lean_mk_string("socket() 실패")));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons((uint16_t) port);
    if (inet_pton(AF_INET, lean_string_cstr(host), &addr.sin_addr) != 1) {
        close(fd);
        return lean_io_result_mk_error(lean_mk_io_user_error(lean_mk_string("잘못된 IPv4 주소")));
    }

    if (connect(fd, (struct sockaddr *) &addr, sizeof(addr)) < 0) {
        close(fd);
        return lean_io_result_mk_error(lean_mk_io_user_error(lean_mk_string("connect() 실패")));
    }
    return lean_io_result_mk_ok(lean_box_uint32((uint32_t) fd));
}

LEAN_EXPORT lean_obj_res lean_viser_send(uint32_t fd, b_lean_obj_arg data, lean_obj_arg world) {
    (void)world;
    const char *buf = lean_string_cstr(data);
    size_t len = strlen(buf), off = 0;
    while (off < len) {
        ssize_t n = write((int) fd, buf + off, len - off);
        if (n <= 0)
            return lean_io_result_mk_error(lean_mk_io_user_error(lean_mk_string("write() 실패")));
        off += (size_t) n;
    }
    return lean_io_result_mk_ok(lean_box(0));
}

LEAN_EXPORT lean_obj_res lean_viser_close(uint32_t fd, lean_obj_arg world) {
    (void)world;
    close((int) fd);
    return lean_io_result_mk_ok(lean_box(0));
}
```

```lean
-- ViserSocket.lean
@[extern "lean_viser_connect"]
opaque viserConnect (host : String) (port : UInt32) : IO UInt32

@[extern "lean_viser_send"]
opaque viserSend (fd : UInt32) (data : String) : IO Unit

@[extern "lean_viser_close"]
opaque viserClose (fd : UInt32) : IO Unit

def withBridge (act : (String → IO Unit) → IO Unit) : IO Unit := do
  let fd ← viserConnect "127.0.0.1" 7000
  try
    act (fun line => viserSend fd (line ++ "\n"))
  finally
    viserClose fd
```

`lakefile.lean`에서 C 타깃을 빌드해 실행파일에 링크합니다:

```lean
import Lake
open Lake DSL

package «viser-lean»

target socketShim pkg : FilePath := do
  let src := pkg.dir / "c" / "socket_shim.c"
  let oFile := pkg.buildDir / "socket_shim.o"
  buildO oFile (← inputTextFile src) #["-I", (← getLeanIncludeDir).toString] #[] "cc"

extern_lib libsocketShim pkg := do
  let name := nameToStaticLib "socketShim"
  let ffiO ← socketShim.fetch
  buildStaticLib (pkg.nativeLibDir / name) #[ffiO]

@[default_target]
lean_exe «viser-lean» where root := `Main
```

이렇게 하면 `nc` 없이 `withBridge`로 한 연결을 오래 잡고 여러 번에 나눠 보낼 수 있습니다.

## 부록 B: 왜 책이 아니라 이 글인가

이건 레시피 하나 + 왜 이렇게 짰는지이고, 챕터로 쪼갤 개념적 깊이는 없습니다. 게다가 viser의 `server.scene.*` API와 Lean 쪽 소켓 수단은 버전을 타서, 책으로 박아 두면 유지보수 부채가 됩니다. 이 브리지를 여러 Lean 교재(선형대수, 동차좌표 등)에서 실제로 재사용하게 되면, 그때 안정된 버전만 추려 짧은 부록으로 승격하는 편이 낫습니다.
