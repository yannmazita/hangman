from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import Token
from app.auth.services import AuthService
from app.database import get_session
from app.users.repository import UserRepository

router = APIRouter(tags=["tokens"])


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[UserRepository, Depends()],
):
    service = AuthService(repository)
    token: Token = await service.get_access_token(
        session, form_data.scopes, form_data.username, form_data.password
    )
    return token


@router.post("/register", response_model=Token)
async def register_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[UserRepository, Depends()],
):
    service = AuthService(repository)

    # Implement deeper registration logic (email service?)
    token: Token = await service.get_access_token(
        session, form_data.scopes, form_data.username
    )
    return token
