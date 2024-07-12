from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import validate_token
from app.auth.schemas import TokenData
from app.database import get_session
from app.users.dependencies import get_own_user
from app.users.models import (
    User,
)
from app.users.repository import UserRepository
from app.users.schemas import (
    UserCreate,
    UserRead,
    UserUpdate,
)
from app.users.services import UserAdminService, UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", response_model=UserRead)
async def create_user(
    data: UserCreate,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[UserRepository, Depends()],
):
    new_user = await repository.create(session, data)
    return new_user


@router.get("/id/{id}", response_model=UserRead)
async def get_user_by_id(
    id: UUID,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[UserRepository, Depends()],
):
    user = await repository.get_by_attribute(session, id)
    return user


@router.get("/all", response_model=tuple[list[UserRead], int])
async def get_all_users(
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[UserRepository, Depends()],
    offset: int = 0,
    limit: int = 100,
):
    users, total_count = await repository.get_all(session, offset, limit)
    return users, total_count


@router.put("/id/{id}", response_model=UserRead)
async def update_user_by_id(
    id: UUID,
    data: UserUpdate,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[UserRepository, Depends()],
):
    updated_user = await repository.update_by_attribute(session, data, id)
    return updated_user


@router.delete("/id/{id}", response_model=UserRead)
async def delete_user_by_id(
    id: UUID,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[UserRepository, Depends()],
):
    user = await repository.delete(session, id)
    return user


@router.patch("/id/{id}/username", response_model=UserRead)
async def update_user_username_by_id(
    id: UUID,
    data: UserUpdate,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[UserRepository, Depends()],
):
    admin_service = UserAdminService(repository)
    updated_user = await admin_service.update_user_username(session, id, data)
    return updated_user


@router.patch("/id/{id}/roles", response_model=UserRead)
async def update_user_roles_by_id(
    id: UUID,
    data: UserUpdate,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[UserRepository, Depends()],
):
    admin_service = UserAdminService(repository)
    updated_user = await admin_service.update_user_roles(session, id, data)
    return updated_user


@router.get("/me", response_model=UserRead)
async def get_own_user(user: Annotated[User, Depends(get_own_user)]):
    return user


@router.delete("/me", response_model=UserRead)
async def delete_own_user(
    user: Annotated[User, Depends(get_own_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[UserRepository, Depends()],
):
    if user.id is not None:
        user = await repository.delete(session, user.id)
        return user
    else:
        # raise something
        pass


@router.patch("/me/password", response_model=UserRead)
async def update_own_password(
    user: Annotated[User, Depends(get_own_user)],
    data: UserUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[UserRepository, Depends()],
):
    service = UserService(repository)
    if user.id is not None:
        updated_user = await service.update_user_password(session, user.id, data)
        return updated_user
    else:
        # raise something
        pass
