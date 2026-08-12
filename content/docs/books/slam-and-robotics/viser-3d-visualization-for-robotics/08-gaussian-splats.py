import numpy as np
import viser
from scipy.spatial.transform import Rotation

server = viser.ViserServer()
server.scene.world_axes.visible = True

rng = np.random.default_rng(seed=1)

# 3DGS는 각 가우시안을 중심 mu, 스케일 s(x,y,z), 회전 R로 표현하고
# 공분산은 Sigma = R @ diag(s^2) @ R^T 로 구성한다
num_gaussians = 2_000
centers = rng.normal(0.0, 0.6, size=(num_gaussians, 3)).astype(np.float32)

scales = rng.uniform(0.01, 0.05, size=(num_gaussians, 3))
random_rotations = Rotation.random(num_gaussians, random_state=rng)
rotation_matrices = random_rotations.as_matrix()

covariances = np.einsum(
    "nij,njk,nlk->nil",
    rotation_matrices,
    np.eye(3)[None, :, :] * (scales[:, None, :] ** 2),
    rotation_matrices,
).astype(np.float32)

# 공분산 행렬이 대칭이고 양의 준정부호(PSD)인지 검증한다 —
# 3DGS 공분산은 항상 이 두 성질을 만족해야 타원체로 해석할 수 있다
sample = covariances[0]
assert np.allclose(sample, sample.T, atol=1e-6)
eigenvalues = np.linalg.eigvalsh(sample)
assert np.all(eigenvalues >= -1e-8)

# 중심으로부터 거리에 따라 반투명도가 줄어들도록 opacity 구성
distance = np.linalg.norm(centers, axis=1)
opacities = np.clip(1.0 - distance / distance.max(), 0.1, 1.0).reshape(-1, 1).astype(np.float32)

# 중심 위치를 그대로 RGB로 매핑해 색이 위치를 반영하게 한다
rgbs = ((centers - centers.min()) / (centers.max() - centers.min())).astype(np.float32)

splat_handle = server.scene.add_gaussian_splats(
    "/toy_splats",
    centers=centers,
    covariances=covariances,
    rgbs=rgbs,
    opacities=opacities,
)

assert splat_handle.name == "/toy_splats"

server.stop()
