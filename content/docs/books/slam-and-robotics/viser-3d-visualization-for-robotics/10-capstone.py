import numpy as np
import viser
from scipy.spatial.transform import Rotation

server = viser.ViserServer()
server.scene.world_axes.visible = True


def quat_wxyz(rotation: Rotation) -> tuple[float, float, float, float]:
    x, y, z, w = rotation.as_quat()
    return (w, x, y, z)


# --- 1. 재구성된 장면: 노이즈 섞인 구형 포인트클라우드 (7장) ---
rng = np.random.default_rng(seed=3)
num_points = 20_000
theta = rng.uniform(0, np.pi, num_points)
phi = rng.uniform(0, 2 * np.pi, num_points)
radius = 2.0 + rng.normal(0, 0.03, num_points)
scene_points = np.stack(
    [
        radius * np.sin(theta) * np.cos(phi),
        radius * np.sin(theta) * np.sin(phi),
        radius * np.cos(theta),
    ],
    axis=1,
).astype(np.float32)
z_normalized = (scene_points[:, 2] - scene_points[:, 2].min()) / (
    scene_points[:, 2].max() - scene_points[:, 2].min()
)
scene_colors = np.zeros((num_points, 3), dtype=np.uint8)
scene_colors[:, 0] = (255 * z_normalized).astype(np.uint8)
scene_colors[:, 2] = (255 * (1.0 - z_normalized)).astype(np.uint8)

point_cloud = server.scene.add_point_cloud(
    "/reconstruction/points",
    points=scene_points,
    colors=scene_colors,
    point_size=0.015,
    point_shape="circle",
)

# --- 2. 재구성에 쓰인 카메라들: look-at 프러스텀 (3장) ---
num_cameras = 6
fov_y = 2.0 * np.arctan(480 / 2.0 / 800.0)
aspect = 640 / 480
camera_positions = np.stack(
    [
        3.5 * np.cos(np.linspace(0, 2 * np.pi, num_cameras, endpoint=False)),
        3.5 * np.sin(np.linspace(0, 2 * np.pi, num_cameras, endpoint=False)),
        np.full(num_cameras, 0.8),
    ],
    axis=1,
)

status_text = server.gui.add_text("Selected camera", initial_value="none")
frustum_handles = []
click_handlers = []
selected_log: list[int] = []

for i in range(num_cameras):
    position = camera_positions[i]
    forward = -position / np.linalg.norm(position)
    world_up = np.array([0.0, 0.0, 1.0])
    right = np.cross(forward, world_up)
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    R_cam_to_world = np.stack([right, -up, forward], axis=1)

    handle = server.scene.add_camera_frustum(
        f"/reconstruction/cameras/cam_{i}",
        fov=fov_y,
        aspect=aspect,
        scale=0.3,
        wxyz=quat_wxyz(Rotation.from_matrix(R_cam_to_world)),
        position=tuple(position),
        color=(230, 160, 30),
    )

    def make_click_handler(index: int):
        def _handler(_event) -> None:
            status_text.value = f"cam_{index}"
            selected_log.append(index)

        return _handler

    click_handler = make_click_handler(i)
    handle.on_click(click_handler)
    frustum_handles.append(handle)
    click_handlers.append(click_handler)

# --- 3. GUI 컨트롤 패널 (5장) ---
with server.gui.add_folder("Controls"):
    point_size_slider = server.gui.add_slider(
        "Point size", min=0.002, max=0.05, step=0.001, initial_value=0.015
    )
    show_cameras_checkbox = server.gui.add_checkbox("Show cameras", initial_value=True)


@point_size_slider.on_update
def _(_event) -> None:
    point_cloud.point_size = point_size_slider.value


@show_cameras_checkbox.on_update
def _(_event) -> None:
    for handle in frustum_handles:
        handle.visible = show_cameras_checkbox.value


# --- 검증: 각 부분이 올바르게 연결되었는지 확인 ---
assert point_cloud.points.shape == (num_points, 3)
assert len(frustum_handles) == num_cameras

point_size_slider.value = 0.03
assert np.isclose(point_cloud.point_size, 0.03)

show_cameras_checkbox.value = False
assert all(not h.visible for h in frustum_handles)
show_cameras_checkbox.value = True
assert all(h.visible for h in frustum_handles)

# 프러스텀 클릭 콜백을 직접 호출해 상태 텍스트와 로그가 갱신되는지 검증
click_handlers[2](None)
click_handlers[5](None)

assert status_text.value == "cam_5"
assert selected_log == [2, 5]

server.stop()
