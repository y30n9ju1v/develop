import numpy as np
import viser
from scipy.spatial.transform import Rotation

server = viser.ViserServer()
server.scene.world_axes.visible = True


def quat_wxyz(rotation: Rotation) -> tuple[float, float, float, float]:
    x, y, z, w = rotation.as_quat()
    return (w, x, y, z)


robot_rotation = Rotation.from_euler("z", 45, degrees=True)
robot_frame = server.scene.add_frame(
    "/robot",
    wxyz=quat_wxyz(robot_rotation),
    position=(1.0, 0.0, 0.0),
    axes_length=0.4,
    axes_radius=0.01,
)

camera_frame = server.scene.add_frame(
    "/robot/camera",
    wxyz=quat_wxyz(Rotation.identity()),
    position=(0.2, 0.0, 0.3),
    axes_length=0.2,
    axes_radius=0.008,
)

assert robot_frame.name == "/robot"
assert camera_frame.name == "/robot/camera"

robot_world_R = robot_rotation.as_matrix()
robot_world_t = np.array([1.0, 0.0, 0.0])
camera_local_t = np.array([0.2, 0.0, 0.3])

camera_world_t = robot_world_R @ camera_local_t + robot_world_t
print("camera world position:", camera_world_t)
expected = np.array([1.0 + 0.2 / np.sqrt(2), 0.2 / np.sqrt(2), 0.3])
assert np.allclose(camera_world_t, expected, atol=1e-10)

server.stop()
