from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.game import Games
from app.clients.models import (
    GameStats,
    WebsocketMessage,
)
from app.clients.utils import Connections
from app.clients.services import (
    on_user_connect,
    on_user_disconnect,
    on_client_connect,
    on_client_disconnect,
    validate_message,
    start_game,
    continue_game,
    guess_letter,
    send_server_stats,
)

router = APIRouter(
    prefix="/ws",
    tags=["ws"],
)

client_connections: Connections = Connections()
user_connections: Connections = Connections()
games: Games = Games()


@router.websocket("/user")
async def user_endpoint(websocket: WebSocket, user_id: UUID):
    await websocket.accept()  # Accept the websocket connection

    try:
        await on_user_connect(user_connections, websocket, user_id)

        while True:
            message: WebsocketMessage | None = await validate_message(
                websocket, user_id, user_connections
            )
            if message is None:
                continue
            else:
                action: str = message.action

                if action == "start_game":
                    await start_game(games, user_connections, user_id)
                if action == "continue_game":
                    await continue_game(games, user_connections, user_id)
                if action == "end_game":
                    # for now when client/user disconnects the websocket,
                    # on_client_disconnect/on_user_disconnect handles client/user purging
                    pass
                if action == "guess_letter":
                    await guess_letter(games, user_connections, message.data, user_id)
                if action == "server_stats":
                    await send_server_stats(user_connections, user_id)

    except WebSocketDisconnect:
        games.remove_game_instance(user_id)
        await on_user_disconnect(user_connections, websocket, user_id)


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
                    stats: GameStats = GameStats(
                        active_players=client_connections.get_number_of_connections()
                    )
                    stats_message: WebsocketMessage = WebsocketMessage(
                        action="server_stats", data=stats
                    )
                    await client_connections.send(client_id, stats_message)

    except WebSocketDisconnect:
        await on_client_disconnect(client_connections, websocket, client_id)
