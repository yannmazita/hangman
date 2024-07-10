from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.game.models import Game
from app.game.schemas import GameRead
from app.game.services import GameService
from app.game.repository import GameRepository
from app.players.repository import PlayerRepository

router = APIRouter(
    prefix="/game",
    tags=["game"],
)


@router.post("/start/player_id/{player_id}", response_model=GameRead)
async def start_game(
    player_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    game_repository: Annotated[GameRepository, Depends()],
    player_repository: Annotated[PlayerRepository, Depends()],
):
    service: GameService = GameService(game_repository, player_repository)
    game: Game = await service.start_game(session, player_id)
    return game


@router.post("/end/player_id/{player_id}", response_model=GameRead)
async def end_game(
    player_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    game_repository: Annotated[GameRepository, Depends()],
    player_repository: Annotated[PlayerRepository, Depends()],
):
    service: GameService = GameService(game_repository, player_repository)
    game: Game = await service.end_game(session, player_id)
    return game


@router.post("/continue/player_id/{player_id}", response_model=GameRead)
async def continue_game(
    player_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    game_repository: Annotated[GameRepository, Depends()],
    player_repository: Annotated[PlayerRepository, Depends()],
):
    service: GameService = GameService(game_repository, player_repository)
    game: Game = await service.continue_game(session, player_id)
    return game


@router.post("/guess/game_id/{game_id}", response_model=GameRead)
async def guess_character(
    game_id: UUID,
    character: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    game_repository: Annotated[GameRepository, Depends()],
    player_repository: Annotated[PlayerRepository, Depends()],
):
    service: GameService = GameService(game_repository, player_repository)
    game: Game = await service.update_game_state(session, game_id, character)
    return game
