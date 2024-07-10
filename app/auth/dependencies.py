from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.config import OAUTH_SCOPES
from app.auth.schemas import TokenData
from app.config import settings
from app.database import get_session
from app.users.models import User
from app.users.repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login",
    scopes=OAUTH_SCOPES,
    auto_error=True,
)


async def validate_token(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[UserRepository, Depends()],
) -> TokenData:
    """Validate token and check if it has the required scopes.
    Args:
        security_scopes: Scopes required by the dependent.
        token: Token to validate.
        session: Database session.
        repository: User repository.
    Returns:
        A TokenData instance representing the token data.
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    permissions_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not enough permissions",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception

    try:
        user: User = await repository.get_by_attribute(
            session, token_data.username, "username"
        )
        user_scopes: list[str] = user.roles.split(" ")
        # Allow admin users to act as if they have any scope
        if "admin" in user_scopes:
            return token_data
        # Iterating through token scopes against scopes defined in user instance.
        for scope in token_data.scopes:
            if scope not in user_scopes:
                print(f"scope {scope} not in {user_scopes}")
                raise permissions_exception
    except HTTPException as e:
        raise e

    # Iterating through dependent's scopes against scopes defined in token.
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise permissions_exception
    return token_data
