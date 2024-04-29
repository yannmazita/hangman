from typing import Annotated
from fastapi import Depends, Security
from sqlmodel import Session
from app.auth.dependencies import validate_token
from app.auth.models import TokenData
from app.database import get_session
from app.players.models import Player
from app.players.services import PlayerService
from app.players.schemas import PlayerAttribute


async def get_own_player(
    token_data: Annotated[TokenData, Security(validate_token, scopes=["player:own"])],
    session: Annotated[Session, Depends(get_session)],
) -> Player:
    """Get own player.
    Args:
        token_data: Token data.
    Returns:
        A Player instance representing own player.
    """
    service = PlayerService(session)
    assert token_data.playername is not None
    player: Player = service.get_player_by_attribute(
        PlayerAttribute.USERNAME, token_data.username
    )

    return player
