from typing import Annotated

from fastapi import Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import validate_token
from app.auth.models import TokenData
from app.database import get_session
from app.users.models import User
from app.users.schemas import UserAttribute
from app.users.services import UserService


async def get_own_user(
    token_data: Annotated[TokenData, Security(validate_token, scopes=["user:own"])],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """Get own user.
    Args:
        token_data: Token data.
        session: The database session.
    Returns:
        A User instance representing own user.
    """
    service = UserService(session)
    assert token_data.username is not None
    try:
        user = await service.get_user_by_attribute(
            UserAttribute.USERNAME, token_data.username
        )
    except Exception as e:
        raise e

    return user
