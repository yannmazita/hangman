from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.game.models import Game
from app.game.schemas import GameCreate, Game as GameSchema
from app.repository import DatabaseRepository


class GameRepository(DatabaseRepository):
    """
    Repository for performing database queries on games.
    """

    def __init__(self):
        super().__init__(Game)

    async def create(self, session: AsyncSession, data: GameCreate) -> Game:
        new_game = GameSchema(id=uuid4(), player_id=data.player_id)
        return await super().create(session, new_game)
