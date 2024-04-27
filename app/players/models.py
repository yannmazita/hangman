from uuid import UUID
from sqlmodel import Field, SQLModel


class PlayerBase(SQLModel):
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
