import numpy as np

# 1. 내부 파라미터 행렬 K 정의
fx, fy = 800.0, 800.0   # 초점거리(픽셀 단위, 가로/세로 축 각각)
cx, cy = 320.0, 240.0   # 주점(이미지 중심 픽셀 좌표)
K = np.array([
    [fx, 0,  cx],
    [0,  fy, cy],
    [0,  0,  1],
])

def project(K, X_cam):
    """카메라 좌표계에서의 3D 점을 픽셀 좌표로 투영한다."""
    x_h = K @ X_cam          # 동차좌표 (Z를 아직 나누지 않음)
    return x_h[:2] / x_h[2]  # Z로 나눠서 픽셀 좌표를 얻음

# 2. 3D 점 투영 및 수동 계산 검증
X_cam = np.array([0.5, 0.25, 2.0])
pixel = project(K, X_cam)
print("pixel:", pixel)   # [520. 340.]

expected_u = fx * (0.5 / 2.0) + cx
expected_v = fy * (0.25 / 2.0) + cy
assert np.allclose(pixel, [expected_u, expected_v])

# 3. 광축 위의 점과 깊이 무관성 확인
on_axis = project(K, np.array([0.0, 0.0, 5.0]))
assert np.allclose(on_axis, [cx, cy])

p_near = project(K, np.array([0.5, 0.25, 2.0]))
p_far  = project(K, np.array([1.0, 0.5, 4.0]))
assert np.allclose(p_near, p_far)

# 4. 초점거리 변경(2배 확대) 시 오프셋 변화 확인
K2 = np.array([
    [1600.0, 0,      cx],
    [0,      1600.0, cy],
    [0,      0,      1],
])
pixel2 = project(K2, X_cam)
print("pixel2:", pixel2)  # [720. 440.]

offset1 = pixel - np.array([cx, cy])   # [200. 100.] (fx=800일 때의 오프셋)
offset2 = pixel2 - np.array([cx, cy])  # [400. 200.] (fx=1600일 때의 오프셋, 정확히 2배)
assert np.allclose(offset2, 2 * offset1)