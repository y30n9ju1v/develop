import numpy as np
import viser
from scipy.spatial.transform import Rotation

server = viser.ViserServer()
server.scene.world_axes.visible = True

# 1장 핀홀 카메라 모델 책의 내부 파라미터를 그대로 사용
fx, fy = 800.0, 800.0
width, height = 640, 480
fov_y = 2.0 * np.arctan(height / 2.0 / fy)
aspect = width / height


def quat_wxyz(rotation: Rotation) -> tuple[float, float, float, float]:
    x, y, z, w = rotation.as_quat()
    return (w, x, y, z)


# 세 대의 카메라가 원점을 중심으로 원을 그리며 서로 다른 위치/방향에서 바라본다
camera_handles = []
for i, angle_deg in enumerate([0.0, 120.0, 240.0]):
    angle = np.deg2rad(angle_deg)
    radius = 2.0
    position = np.array([radius * np.cos(angle), radius * np.sin(angle), 0.5])

    # 카메라가 항상 원점을 바라보도록 하는 방향(look-at) 계산
    forward = -position / np.linalg.norm(position)
    world_up = np.array([0.0, 0.0, 1.0])
    right = np.cross(forward, world_up)
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    # 카메라 좌표계 관례: x=right, y=down, z=forward
    R_cam_to_world = np.stack([right, -up, forward], axis=1)
    rotation = Rotation.from_matrix(R_cam_to_world)

    handle = server.scene.add_camera_frustum(
        f"/cameras/cam_{i}",
        fov=fov_y,
        aspect=aspect,
        scale=0.3,
        wxyz=quat_wxyz(rotation),
        position=tuple(position),
        color=(200, 60, 60),
    )
    camera_handles.append(handle)

assert len(camera_handles) == 3
assert camera_handles[0].name == "/cameras/cam_0"
assert np.isclose(camera_handles[0].aspect, aspect)

# 회전행렬이 직교(RᵀR=I)하고 행렬식이 +1인 진짜 회전인지 검증
assert np.allclose(R_cam_to_world.T @ R_cam_to_world, np.eye(3), atol=1e-10)
assert np.isclose(np.linalg.det(R_cam_to_world), 1.0)

# 카메라의 forward(z) 방향이 실제로 원점을 향하는지 검증
last_position = np.array(
    [2.0 * np.cos(np.deg2rad(240.0)), 2.0 * np.sin(np.deg2rad(240.0)), 0.5]
)
forward_check = R_cam_to_world @ np.array([0.0, 0.0, 1.0])
to_origin_direction = -last_position / np.linalg.norm(last_position)
assert np.allclose(forward_check[:2], to_origin_direction[:2], atol=1e-10)

server.stop()
