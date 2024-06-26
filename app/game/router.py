from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.game.models import Game, GameRead
from app.game.services import GameService

router = APIRouter(
    prefix="/game",
    tags=["game"],
)


@router.post("/start/player_id/{player_id}", response_model=GameRead)
async def start_game(
    player_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = GameService(session)
    try:
        game = await service.start_game(player_id)
        return game
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/end/player_id/{player_id}", response_model=GameRead)
async def end_game(
    player_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = GameService(session)
    try:
        game: Game = await service.end_game(player_id)
        return game
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/continue/player_id/{player_id}", response_model=GameRead)
async def continue_game(
    player_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = GameService(session)
    try:
        game: Game = await service.continue_game(player_id)
        return game
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/guess/game_id/{game_id}", response_model=GameRead)
async def guess_character(
    game_id: UUID,
    character: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = GameService(session)
    try:
        game: Game = await service.update_game_state(game_id, character)
        return game
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
