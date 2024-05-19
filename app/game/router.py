from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.game.models import GameRead
from app.game.services import GameService

router = APIRouter(
    prefix="/game",
    tags=["game"],
)


@router.get("/start", response_model=GameRead)
async def start_game(
    # player_id: Annotated[UUID, Depends(valid_player_id)],
    player_id: Annotated[UUID, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = GameService(session)
