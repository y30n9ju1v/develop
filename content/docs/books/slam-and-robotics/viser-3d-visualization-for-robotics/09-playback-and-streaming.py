import threading
import time

import numpy as np
import viser

server = viser.ViserServer()
server.scene.world_axes.visible = True

rng = np.random.default_rng(seed=2)

# 원형 궤적을 따라 이동하는 로봇의 T개 타임스텝 자세를 미리 계산해둔다
num_steps = 50
angles = np.linspace(0, 2 * np.pi, num_steps, endpoint=False)
trajectory_positions = np.stack(
    [3.0 * np.cos(angles), 3.0 * np.sin(angles), np.zeros(num_steps)], axis=1
)

# 각 타임스텝에서 로봇 주변에 관측된 "지역 스캔" 점들을 미리 만들어둔다
local_scan = rng.normal(0.0, 0.15, size=(300, 3))

robot_frame = server.scene.add_frame(
    "/robot",
    axes_length=0.3,
    axes_radius=0.02,
    position=tuple(trajectory_positions[0]),
)
scan_cloud = server.scene.add_point_cloud(
    "/robot/local_scan",
    points=local_scan,
    colors=(80, 200, 120),
    point_size=0.02,
)

frame_slider = server.gui.add_slider(
    "Timestep", min=0, max=num_steps - 1, step=1, initial_value=0
)
play_button = server.gui.add_button("Play")


def set_timestep(index: int) -> None:
    robot_frame.position = tuple(trajectory_positions[index])


@frame_slider.on_update
def _(_event) -> None:
    set_timestep(frame_slider.value)


playback_log: list[int] = []


def play_all_steps() -> None:
    for i in range(num_steps):
        frame_slider.value = i
        playback_log.append(i)


@play_button.on_click
def _(_event) -> None:
    thread = threading.Thread(target=play_all_steps, daemon=True)
    thread.start()
    thread.join(timeout=5.0)


# 1) 슬라이더를 직접 특정 값으로 옮기면 로봇 프레임이 정확히 그 타임스텝의 위치로 이동하는지 검증
frame_slider.value = 10
assert np.allclose(robot_frame.position, trajectory_positions[10], atol=1e-10)

frame_slider.value = 25
assert np.allclose(robot_frame.position, trajectory_positions[25], atol=1e-10)

# 2) "Play" 버튼(백그라운드 스레드로 전체 궤적을 순차 재생)을 눌렀을 때
#    모든 타임스텝을 순서대로 거쳐 마지막 위치에 도달하는지 검증
play_button.value = True
assert playback_log == list(range(num_steps))
assert np.allclose(robot_frame.position, trajectory_positions[-1], atol=1e-10)

# 지역 스캔은 로봇 프레임의 자식이므로 세계 좌표는 로봇 위치 + 지역 스캔 좌표가 된다
assert scan_cloud.name == "/robot/local_scan"

server.stop()
