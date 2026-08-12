import numpy as np
import viser

server = viser.ViserServer()
server.scene.world_axes.visible = True

sphere = server.scene.add_icosphere(
    "/sphere",
    radius=0.3,
    color=(90, 200, 255),
    position=(0.0, 0.0, 0.0),
)

radius_slider = server.gui.add_slider(
    "Radius",
    min=0.1,
    max=1.0,
    step=0.05,
    initial_value=0.3,
)

color_slider = server.gui.add_rgb(
    "Color",
    initial_value=(90, 200, 255),
)

reset_button = server.gui.add_button("Reset")

event_log = []


@radius_slider.on_update
def _(_event) -> None:
    sphere.radius = radius_slider.value
    event_log.append(("radius", radius_slider.value))


@color_slider.on_update
def _(_event) -> None:
    sphere.color = color_slider.value
    event_log.append(("color", color_slider.value))


@reset_button.on_click
def _(_event) -> None:
    radius_slider.value = 0.3
    color_slider.value = (90, 200, 255)
    event_log.append(("reset", None))


# 콜백을 등록만 하고 실제 클라이언트 없이도, 값을 직접 바꾸면 콜백이 호출되는지 검증한다
radius_slider.value = 0.6
assert np.isclose(sphere.radius, 0.6)
assert event_log[-1] == ("radius", 0.6)

color_slider.value = (255, 0, 0)
assert sphere.color == (255, 0, 0)
assert event_log[-1] == ("color", (255, 0, 0))

reset_button.value = True
assert np.isclose(radius_slider.value, 0.3)
assert color_slider.value == (90, 200, 255)
assert event_log[-1] == ("reset", None)

server.stop()
