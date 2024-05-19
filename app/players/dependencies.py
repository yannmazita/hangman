from typing import Annotated

from fastapi import Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import validate_token
from app.auth.models import TokenData
from app.database import get_session
from app.players.models import Player
from app.players.schemas import PlayerAttribute
from app.players.services import PlayerService


async def get_own_player(
    token_data: Annotated[TokenData, Security(validate_token, scopes=["player:own"])],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Player:
    """Get own player.
    Args:
        token_data: Token data.
        session: The database session.
    Returns:
        A Player instance representing own player.
    """
    service = PlayerService(session)
    assert token_data.playername is not None
    try:
        player = await service.get_player_by_attribute(
            PlayerAttribute.USERNAME, token_data.playername
        )
    except Exception as e:
        raise e

    return player
