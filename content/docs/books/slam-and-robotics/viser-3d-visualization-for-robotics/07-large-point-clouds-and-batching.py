import time

import numpy as np
import viser

server = viser.ViserServer()
server.scene.world_axes.visible = True

rng = np.random.default_rng(seed=0)

# 100,000개 점을 가진 "가짜 라이다 스캔" 만들기: 구형으로 퍼진 노이즈 섞인 표면
num_points = 100_000
theta = rng.uniform(0, np.pi, num_points)
phi = rng.uniform(0, 2 * np.pi, num_points)
radius = 3.0 + rng.normal(0, 0.05, num_points)

x = radius * np.sin(theta) * np.cos(phi)
y = radius * np.sin(theta) * np.sin(phi)
z = radius * np.cos(theta)
points = np.stack([x, y, z], axis=1).astype(np.float32)

# 높이(z)에 따라 색을 입혀서 구조를 눈으로 구분하기 쉽게 만든다
z_normalized = (z - z.min()) / (z.max() - z.min())
colors = np.zeros((num_points, 3), dtype=np.uint8)
colors[:, 0] = (255 * z_normalized).astype(np.uint8)
colors[:, 2] = (255 * (1.0 - z_normalized)).astype(np.uint8)

start = time.perf_counter()
cloud = server.scene.add_point_cloud(
    "/lidar_scan",
    points=points,
    colors=colors,
    point_size=0.01,
    point_shape="circle",
)
elapsed = time.perf_counter() - start

assert cloud.points.shape == (num_points, 3)
assert cloud.colors.shape == (num_points, 3)
print(f"scene update for {num_points} points took {elapsed * 1000:.1f} ms")

# 여러 카메라 프레임을 한 번에 인스턴싱하는 batched axes:
# 로봇 궤적을 따라 100개 프레임을 개별 add_frame 호출 없이 한 번에 그린다
num_frames = 100
trajectory_angle = np.linspace(0, 4 * np.pi, num_frames)
trajectory_positions = np.stack(
    [
        4.0 * np.cos(trajectory_angle),
        4.0 * np.sin(trajectory_angle),
        np.linspace(0.0, 2.0, num_frames),
    ],
    axis=1,
)
identity_wxyzs = np.tile(np.array([1.0, 0.0, 0.0, 0.0]), (num_frames, 1))

batched = server.scene.add_batched_axes(
    "/trajectory_frames",
    batched_wxyzs=identity_wxyzs,
    batched_positions=trajectory_positions,
    axes_length=0.15,
    axes_radius=0.01,
)

assert batched.batched_positions.shape == (num_frames, 3)
assert batched.batched_wxyzs.shape == (num_frames, 4)

server.stop()
