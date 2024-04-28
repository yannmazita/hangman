from typing import Annotated
from fastapi import Depends, APIRouter
from sqlmodel import Session
from app.database import get_session
from app.game.models import GameRead
from app.game.services import GameService

router = APIRouter(
    prefix="/game",
    tags=["game"],
)


@router.get("/start", response_model=GameRead)
async def start_game(
    player_id: Annotated[UUID, Depend(valid_player_id)],
    session: Annotated[Session, Depends(get_session)],
):
    game_service = GameService(session)
