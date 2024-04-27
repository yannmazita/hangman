from typing import Any
from uuid import UUID
from fastapi import WebSocket
from pydantic import ValidationError
from app.exceptions import GameOver
from app.clients.models import (
    GameGuess,
    GameStats,
    GameUpdate,
    AppError,
    WebsocketMessage,
)
from app.clients.utils import Connections
from app.game import Games


async def verify_websocket_token(websocket: WebSocket) -> None:
    """
    Verifies the websocket token.

    The websocket token is the first message sent by the user.
    It contains the access token and token type. This function verifies
    the token and closes the websocket if it is invalint
    Args:
        websocket: The websocket to verify.
    """

    try:
        # do things to actually verify the token
        pass
    except ValidationError:
        await websocket.close()
        print("Invalid token format.")


async def on_user_connect(
    user_connections: Connections, websocket: WebSocket, user_id: UUID
) -> None:
    """
    Handles actions when a websocket is connected.

    Args:
        user_connections: The object that holds the websocket connections.
        websocket: The websocket to connect.
        user_id: The id of the user.
    """
    user_connections.connect(websocket, user_id)
    await verify_websocket_token(websocket)


async def on_user_disconnect(
    user_connections: Connections, websocket: WebSocket, user_id: UUID
) -> None:
    """
    Handles actions when a websocket is disconnected.

    Args:
        user_connections: The object that holds the websocket connections.
        websocket: The websocket to disconnect.
        user_id: The id of the user.
    """
    user_connections.disconnect(user_id)


async def on_client_connect(
    client_connections: Connections, websocket: WebSocket, client_id: UUID
) -> None:
    """
    Handles actions when a websocket is connected.

    Args:
        client_connections: The object that holds the websocket connections.
        websocket: The websocket to connect.
        client_id: The id of the client.
    """
    client_connections.connect(websocket, client_id)
    stats = GameStats(active_players=client_connections.get_number_of_connections())
    stats_message = WebsocketMessage(action="server_stats", data=stats)
    await client_connections.broadcast(stats_message)


async def on_client_disconnect(
    client_connections: Connections, websocket: WebSocket, client_id: UUID
) -> None:
    """
    Handles actions when a websocket is disconnected.

    Args:
        client_connections: The object that holds the websocket connections.
        websocket: The websocket to disconnect.
        client_id: The id of the client.
    """
    client_connections.disconnect(client_id)
    stats = GameStats(active_players=client_connections.get_number_of_connections())
    stats_message = WebsocketMessage(action="server_stats", data=stats)
    await client_connections.broadcast(stats_message)


async def send_server_stats(user_connections: Connections, user_id: UUID) -> None:
    """
    Sends server stats to the user.

    Args:
        user_id: The id of the user.
    """
    stats = GameStats(active_players=user_connections.get_number_of_connections())
    stats_message = WebsocketMessage(action="server_stats", data=stats)
    await user_connections.send(user_id, stats_message)


async def validate_message(
    websocket: WebSocket, id: UUID, connections: Connections
) -> WebsocketMessage | None:
    """
    Validates a message received from the websocket.

    This function receives a message from the websocket, validates it,
    and sends back an error message if the message is invalid.

    Args:
        websocket: The websocket to receive the message from.
        id: The id of the websocket connection.
        connections: The object that holds the websocket connections.
    """
    raw_message: str = await websocket.receive_text()
    try:
        message: WebsocketMessage = WebsocketMessage.model_validate_json(raw_message)
        return message
    except ValidationError as e:
        error: AppError = AppError(error=str(e))
        error_message = WebsocketMessage(action="error", data=error)
        await connections.send(id, error_message)
        return None


async def start_game(
    games: Games, user_connections: Connections, user_id: UUID
) -> None:
    """
    Starts a new game for the user.

    This function starts a new game for the user and sends the game update to the user.
    Args:
        games: The object that holds the game instances.
        user_connections: The object that holds the websocket connections.
        user_id: The id of the user.
    """
    try:
        await games.start_game(user_id)

        game = games.get_game_instance(user_id)
        game_start = GameUpdate(
            word_progress=game.word_progress,
            guessed_letters=game.guessed_letters,
            tries_left=game.tries_left,
            max_tries=game.MAX_TRIES,
            successful_guesses=game.successful_guesses,
        )
        game_message = WebsocketMessage(action="game_started", data=game_start)

        await user_connections.send(user_id, game_message)
    except ValidationError as e:
        error: AppError = AppError(error=str(e))
        error_message = WebsocketMessage(action="error", data=error)
        await user_connections.send(user_id, error_message)


async def guess_letter(
    games: Games, user_connections: Connections, messageData: Any, user_id: UUID
) -> None:
    """
    Guesses a letter in the game.

    This function guesses a letter in the game and sends the game update to the user.

    Args:
        games: The object that holds the game instances.
        user_connections: The object that holds the websocket connections.
        messageData: The data of the message.
        user_id: The id of the user.
    """
    try:
        guess: GameGuess = GameGuess.model_validate(messageData)
        games.update_game(user_id, guess.letter)
    except ValidationError as e:
        error: AppError = AppError(error=str(e))
        error_message = WebsocketMessage(action="error", data=error)
        await user_connections.send(user_id, error_message)
    except GameOver as e:
        # handle game state when party is over
        pass

    game = games.get_game_instance(user_id)
    game_update = GameUpdate(
        word_progress=game.word_progress,
        guessed_letters=game.guessed_letters,
        tries_left=game.tries_left,
        max_tries=game.MAX_TRIES,
        successful_guesses=game.successful_guesses,
        game_status=game.game_status,
    )
    game_message: WebsocketMessage = WebsocketMessage(
        action="game_started", data=game_update
    )
    await user_connections.send(user_id, game_message)


async def continue_game(
    games: Games, user_connections: Connections, user_id: UUID
) -> None:
    """
    Continues the game for the user.
    This function continues the game for the user and sends the game update to the user.
    Args:
        games: The object that holds the game instances.
        user_connections: The object that holds the websocket connections.
        user_id: The id of the user.
    """
    try:
        await games.continue_game(user_id)
        game = games.get_game_instance(user_id)
        game_start = GameUpdate(
            word_progress=game.word_progress,
            guessed_letters=game.guessed_letters,
            tries_left=game.tries_left,
            max_tries=game.MAX_TRIES,
            successful_guesses=game.successful_guesses,
        )
        game_message = WebsocketMessage(action="game_started", data=game_start)
        await user_connections.send(user_id, game_message)
    except ValidationError as e:
        error: AppError = AppError(error=str(e))
        error_message = WebsocketMessage(action="error", data=error)
        await user_connections.send(user_id, error_message)
