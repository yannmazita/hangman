from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.clients.schemas import (
    AppStats,
    WebsocketMessage,
)
from app.clients.services import (
    on_client_connect,
    on_client_disconnect,
    validate_message,
)
from app.clients.utils import Connections

router = APIRouter(
    prefix="/ws",
    tags=["ws"],
)

client_connections: Connections = Connections()
user_connections: Connections = Connections()


@router.websocket("/client")
async def client_endpoint(websocket: WebSocket, client_id: UUID):
    await websocket.accept()  # Accept the websocket connection

    try:
        await on_client_connect(client_connections, websocket, client_id)

        while True:
            message: WebsocketMessage | None = await validate_message(
                websocket, client_id, client_connections
            )
            if message is None:
                continue
            else:
                action: str = message.action

                if action == "server_stats":
                    stats: AppStats = AppStats(
                        active_users=client_connections.get_number_of_connections()
                    )
                    stats_message: WebsocketMessage = WebsocketMessage(
                        action="server_stats", data=stats
                    )
                    await client_connections.send(client_id, stats_message)

    except WebSocketDisconnect:
        await on_client_disconnect(client_connections, websocket, client_id)
