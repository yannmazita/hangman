from uuid import UUID
from pydantic import validate_call
from sqlmodel import Field, SQLModel
from sqlalchemy.ext.asyncio import AsyncAttrs


class PlayerBase(AsyncAttrs, SQLModel):
    playername: str = Field(index=True, unique=True)
    username: str | None = Field(default=None, index=True, foreign_key="user.username")


class Player(PlayerBase, table=True):
    id: UUID | None = Field(default=None, primary_key=True)
    points: int = 0
    games_played: int = 0
    games_won: int = 0


class PlayerCreate(PlayerBase):
    pass


class PlayerRead(PlayerBase):
    id: UUID
    points: int = 0
    games_played: int = 0
    games_won: int = 0


class PlayerPlayernameUpdate(SQLModel, table=False):
    username: str

    @validate_call
    def __init__(self, **data):
        super().__init__(**data)
        self.validate_username()

    def validate_username(self):
        # add these constants to local config.py
        if len(self.username) < 3:
            raise ValueError("Playername must be at least 3 characters")
        if len(self.username) > 50:
            raise ValueError("Playername must be at most 50 characters")
