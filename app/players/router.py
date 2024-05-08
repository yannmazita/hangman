from typing import Annotated
from uuid import UUID
from fastapi import Depends, APIRouter, HTTPException, Security, status
from sqlmodel import Session
from app.database import get_session
from app.auth.dependencies import validate_token
from app.auth.models import TokenData
from app.players.dependencies import get_own_player
from app.players.models import (
    Player,
    PlayerCreate,
    PlayerRead,
    PlayerPlayernameUpdate,
)
from app.players.services import PlayerService, PlayerAdminService
from app.players.schemas import PlayerAttribute

router = APIRouter(
    prefix="/players",
    tags=["players"],
)


@router.post("/", response_model=PlayerRead)
async def create_player(
    player: PlayerCreate,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Session = Depends(get_session),
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
    session: Annotated[Session, Depends(get_session)],
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
    session: Annotated[Session, Depends(get_session)],
    offset: int = 0,
    limit: int = 100,
):
    service = PlayerService(session)
    try:
        players, total_count = service.get_players(offset, limit)
        print(total_count)
        return players, total_count
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put("/id/{id}", response_model=PlayerRead)
async def update_player_by_id(
    id: UUID,
    player: PlayerCreate,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[Session, Depends(get_session)],
):
    service = PlayerService(session)
    try:
        updated_player = service.update_player_by_attribute(
            PlayerAttribute.ID, str(id), player
        )
        return updated_player
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete("/id/{id}", response_model=PlayerRead)
async def delete_player_by_id(
    id: UUID,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[Session, Depends(get_session)],
):
    service = PlayerService(session)
    try:
        player = service.delete_player_by_attribute(PlayerAttribute.ID, str(id))
        return player
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.patch("/id/{id}/playername", response_model=PlayerRead)
async def update_player_playername_by_id(
    id: UUID,
    playername_data: PlayerPlayernameUpdate,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[Session, Depends(get_session)],
):
    admin_service = PlayerAdminService(session)
    try:
        updated_player = admin_service.update_player_playername_by_attribute(
            PlayerAttribute.ID, str(id), playername_data
        )
        return updated_player
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/me", response_model=PlayerRead)
async def get_own_player(player: Annotated[Player, Depends(get_own_player)]):
    return player


@router.delete("/me", response_model=PlayerRead)
async def delete_own_player(
    player: Annotated[Player, Depends(get_own_player)],
    session: Annotated[Session, Depends(get_session)],
):
    service = PlayerService(session)
    try:
        service.delete_player(player)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    return player
