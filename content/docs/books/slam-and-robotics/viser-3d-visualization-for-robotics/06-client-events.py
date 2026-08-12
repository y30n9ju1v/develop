import viser

server = viser.ViserServer()
server.scene.world_axes.visible = True

sphere = server.scene.add_icosphere(
    "/target",
    radius=0.3,
    color=(90, 200, 255),
    position=(0.0, 0.0, 0.0),
)

status_text = server.gui.add_text("Status", initial_value="waiting for click")


@sphere.on_click
def _(event: viser.SceneNodePointerEvent) -> None:
    status_text.value = f"clicked by client {event.client_id}"


connected_clients: list[int] = []


@server.on_client_connect
def _(client: viser.ClientHandle) -> None:
    connected_clients.append(client.client_id)
    # 새로 접속한 클라이언트만 원하는 초기 시점으로 카메라를 옮긴다
    client.camera.position = (2.0, 2.0, 2.0)
    client.camera.look_at = (0.0, 0.0, 0.0)
    client.add_notification(
        title="Connected",
        body="씬에 접속했습니다.",
        auto_close=3000,
    )


disconnected_clients: list[int] = []


@server.on_client_disconnect
def _(client: viser.ClientHandle) -> None:
    disconnected_clients.append(client.client_id)


# 접속한 브라우저 클라이언트가 없는 상태에서도 콜백 배선과 서버 상태를 검증한다
assert callable(sphere.on_click)
assert server.get_clients() == {}
assert connected_clients == []
assert disconnected_clients == []
assert status_text.value == "waiting for click"

server.stop()
