from typing import Annotated

from fastapi import Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import validate_token
from app.auth.schemas import TokenData
from app.database import get_session
from app.users.models import User
from app.users.repository import UserRepository


async def get_own_user(
    token_data: Annotated[TokenData, Security(validate_token, scopes=["user:own"])],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[UserRepository, Depends()],
) -> User:
    """Get own user.
    Args:
        token_data: Token data.
        session: The database session.
        repository: User repository.
    Returns:
        Own user.
    """
    user: User = await repository.get_by_attribute(
        session, token_data.username, "username"
    )
    return user
