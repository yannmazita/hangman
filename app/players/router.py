from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import validate_token
from app.auth.models import TokenData
from app.database import get_session
from app.players.dependencies import get_own_player
from app.players.repository import PlayerRepository
from app.players.schemas import (
    PlayerCreate,
    PlayerUpdate,
    PlayerRead,
)
from app.players.models import Player
from app.players.services import PlayerAdminService

router = APIRouter(
    prefix="/players",
    tags=["players"],
)


@router.post("/", response_model=PlayerRead)
async def create_player(
    data: PlayerCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[PlayerRepository, Depends()],
):
    new_player = await repository.create(session, data)
    return new_player


@router.get("/id/{id}", response_model=PlayerRead)
async def get_player_by_id(
    id: UUID,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[PlayerRepository, Depends()],
):
    player = await repository.get_by_attribute(session, id)
    return player


@router.get("/all", response_model=tuple[list[PlayerRead], int])
async def get_all_players(
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[PlayerRepository, Depends()],
    offset: int = 0,
    limit: int = 100,
):
    players, total_count = await repository.get_all(session, offset, limit)
    return players, total_count


@router.put("/id/{id}", response_model=PlayerRead)
async def update_player_by_id(
    id: UUID,
    data: PlayerUpdate,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[PlayerRepository, Depends()],
):
    updated_player = await repository.update_by_attribute(session, data, id)
    return updated_player


@router.delete("/id/{id}", response_model=PlayerRead)
async def delete_player_by_id(
    id: UUID,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[PlayerRepository, Depends()],
):
    player = await repository.delete(session, id)
    return player


@router.patch("/id/{id}/playername", response_model=PlayerRead)
async def update_player_playername_by_id(
    id: UUID,
    data: PlayerUpdate,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[PlayerRepository, Depends()],
):
    admin_service = PlayerAdminService(repository)
    updated_player = await admin_service.update_player_playername(session, id, data)
    return updated_player


@router.get("/me", response_model=PlayerRead)
async def get_own_player(player: Annotated[Player, Depends(get_own_player)]):
    return player


@router.delete("/me", response_model=PlayerRead)
async def delete_own_player(
    player: Annotated[Player, Depends(get_own_player)],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[PlayerRepository, Depends()],
):
    player = await repository.delete(session, player.id)
