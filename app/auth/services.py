from datetime import datetime, timedelta, timezone

from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import incorrect_username_or_password
from app.auth.utils import verify_password
from app.config import settings
from app.users.schemas import UserAttribute
from app.users.services import UserService


async def authenticate_user(session: AsyncSession, username: str, password: str):
    service = UserService(session)
    try:
        user = await service.get_user_by_attribute(UserAttribute.USERNAME, username)
    except Exception as e:
        raise e
    if not verify_password(password, user.hashed_password):
        raise incorrect_username_or_password
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt
