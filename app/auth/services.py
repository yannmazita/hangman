import logging
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.auth.exceptions import incorrect_username_or_password
from app.auth.schemas import Token
from app.auth.utils import verify_password
from app.config import settings
from app.users.models import User
from app.users.repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class AuthServiceBase:
    def __init__(self, repository: UserRepository):
        self.repository = repository


class AuthService(AuthServiceBase):
    def __init__(self, repository: UserRepository):
        super().__init__(repository)

    async def authenticate_user(
        self, session: AsyncSession, username: str, password: str
    ):
        user: User = await self.repository.get_by_attribute(
            session, username, "username"
        )
        if not verify_password(password, user.hashed_password):
            raise incorrect_username_or_password
        logger.info(f"User {username} has been authenticated.")
        return user

    async def create_access_token(
        self,
        session: AsyncSession,
        scopes: list[str],
        username: str,
        password: str | None = None,
    ) -> str:
        if password:
            user: User = await self.authenticate_user(session, username, password)
            to_encode: dict = {"sub": user.username, "scopes": scopes}
        else:
            to_encode: dict = {"sub": username, "scopes": scopes}
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return encoded_jwt

    async def get_access_token(
        self,
        session: AsyncSession,
        scopes: list[str],
        username: str,
        password: str | None = None,
    ) -> Token:
        encoded_jwt: str = await self.create_access_token(
            session, scopes, username, password
        )
        token: Token = Token(access_token=encoded_jwt, token_type="bearer")
        return token
