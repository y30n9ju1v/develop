import numpy as np
import viser

server = viser.ViserServer()
server.scene.world_axes.visible = True

# 정사면체(tetrahedron)를 정점 4개 + 삼각형 면 4개로 직접 정의
vertices = np.array(
    [
        [1.0, 1.0, 1.0],
        [1.0, -1.0, -1.0],
        [-1.0, 1.0, -1.0],
        [-1.0, -1.0, 1.0],
    ]
)
faces = np.array(
    [
        [0, 1, 2],
        [0, 3, 1],
        [0, 2, 3],
        [1, 3, 2],
    ]
)

mesh_handle = server.scene.add_mesh_simple(
    "/tetrahedron",
    vertices=vertices,
    faces=faces,
    color=(90, 200, 255),
    position=(0.0, 0.0, 0.0),
)

assert mesh_handle.vertices.shape == (4, 3)
assert mesh_handle.faces.shape == (4, 3)
# 모든 면 인덱스가 정점 개수 범위 안에 있는지 검증
assert faces.max() < len(vertices)


def triangle_normal(v0, v1, v2):
    return np.cross(v1 - v0, v2 - v0)


# 정사면체의 각 면이 만드는 법선이 모두 바깥쪽을 향하는지 확인
# (정점 순서가 반시계 방향이면 법선이 무게중심 반대 방향을 향해야 한다)
centroid = vertices.mean(axis=0)
for face in faces:
    v0, v1, v2 = vertices[face]
    normal = triangle_normal(v0, v1, v2)
    face_center = (v0 + v1 + v2) / 3.0
    outward = face_center - centroid
    assert np.dot(normal, outward) > 0.0

# 조명 없이는 표면의 굴곡이 잘 안 보이므로 방향광을 추가한다
server.scene.configure_default_lights(enabled=False)
light = server.scene.add_light_directional(
    "/sun",
    color=(255, 255, 255),
    intensity=2.0,
    position=(3.0, 3.0, 5.0),
)

box_handle = server.scene.add_box(
    "/ground_marker",
    color=(120, 120, 120),
    dimensions=(2.0, 2.0, 0.05),
    position=(0.0, 0.0, -1.5),
)

assert light.intensity == 2.0
assert box_handle.dimensions == (2.0, 2.0, 0.05)

server.stop()
