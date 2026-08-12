import time

import numpy as np
import viser

server = viser.ViserServer()
server.scene.world_axes.visible = True

points = np.random.uniform(-1.0, 1.0, size=(500, 3))
colors = np.random.randint(0, 256, size=(500, 3), dtype=np.uint8)

point_cloud = server.scene.add_point_cloud(
    name="/random_cloud",
    points=points,
    colors=colors,
    point_size=0.02,
)

print("scene node name:", point_cloud.name)
assert point_cloud.name == "/random_cloud"
assert point_cloud.points.shape == (500, 3)

server.stop()
