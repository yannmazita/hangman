from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import validate_token
from app.auth.models import TokenData
from app.database import get_session
from app.players.dependencies import get_own_player
from app.players.models import (
    Player,
    PlayerCreate,
    PlayerPlayernameUpdate,
    PlayerRead,
)
from app.players.schemas import PlayerAttribute
from app.players.services import PlayerAdminService, PlayerService

router = APIRouter(
    prefix="/players",
    tags=["players"],
)


@router.post("/", response_model=PlayerRead)
async def create_player(
    player: PlayerCreate,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: AsyncSession = Depends(get_session),
):
    service = PlayerService(session)
    try:
        new_player = service.create_player(player)
        return new_player
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/id/{id}", response_model=PlayerRead)
async def get_player_by_id(
    id: UUID,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = PlayerService(session)
    try:
        player = service.get_player_by_attribute(PlayerAttribute.ID, str(id))
        return player
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/all", response_model=tuple[list[PlayerRead], int])
async def get_all_players(
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
    offset: int = 0,
    limit: int = 100,
):
    service = PlayerService(session)
    try:
        players, total_count = await service.get_players(offset, limit)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return players, total_count


@router.put("/id/{id}", response_model=PlayerRead)
async def update_player_by_id(
    id: UUID,
    player: PlayerCreate,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = PlayerService(session)
    try:
        updated_player = await service.update_player_by_attribute(
            PlayerAttribute.ID, str(id), player
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return updated_player


@router.delete("/id/{id}", response_model=PlayerRead)
async def delete_player_by_id(
    id: UUID,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = PlayerService(session)
    try:
        player = await service.delete_player_by_attribute(PlayerAttribute.ID, str(id))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return player


@router.patch("/id/{id}/playername", response_model=PlayerRead)
async def update_player_playername_by_id(
    id: UUID,
    playername_data: PlayerPlayernameUpdate,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    admin_service = PlayerAdminService(session)
    try:
        updated_player = await admin_service.update_player_playername_by_attribute(
            PlayerAttribute.ID, str(id), playername_data
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return updated_player


@router.get("/me", response_model=PlayerRead)
async def get_own_player(player: Annotated[Player, Depends(get_own_player)]):
    return player


@router.delete("/me", response_model=PlayerRead)
async def delete_own_player(
    player: Annotated[Player, Depends(get_own_player)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = PlayerService(session)
    try:
        await service.delete_player(player)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return player
