from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.game.models import GameRead
from app.game.services import GameService
from app.players.models import Player

router = APIRouter(
    prefix="/game",
    tags=["game"],
)


@router.post("/start", response_model=GameRead)
async def start_game(
    player: Player,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = GameService(session)
    try:
        await service.start_game(player)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
