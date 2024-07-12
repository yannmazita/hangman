from typing import Annotated

from fastapi import Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import validate_token
from app.auth.schemas import TokenData
from app.database import get_session
from app.players.models import Player
from app.players.repository import PlayerRepository


async def get_own_player(
    token_data: Annotated[TokenData, Security(validate_token, scopes=["player:own"])],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[PlayerRepository, Depends()],
) -> Player:
    """Get own player.
    Args:
        token_data: Token data.
        session: The database session.
        repository: Player repository.
    Returns:
        Own player.
    """
    player: Player = await repository.get_by_attribute(
        session, token_data.username, "username"
    )
    return player
