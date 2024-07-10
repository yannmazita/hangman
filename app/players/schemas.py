from uuid import UUID
from pydantic import BaseModel, validate_call

from app.schemas import Base, UuidMixin


class Player(Base, UuidMixin):
    points: int = 0
    games_played: int = 0
    games_won: int = 0


class PlayerBase(Base):
    playername: str
    username: str | None = None


class PlayerCreate(PlayerBase):
    pass


class PlayerRead(PlayerBase, UuidMixin):
    points: int = 0
    games_played: int = 0
    games_won: int = 0


class PlayerUpdate(Base):
    playername: str | None = None
    username: str | None = None
    points: int | None = None
    games_played: int | None = None
    games_won: int | None = None

    @validate_call
    def __init__(self, **data):
        super().__init__(**data)
        self.validate_username()

    def validate_username(self):
        if self.username is not None:
            if len(self.username) < 3:
                raise ValueError("Playername must be at least 3 characters")
            if len(self.username) > 50:
                raise ValueError("Playername must be at most 50 characters")


class Players(BaseModel):
    users: list[PlayerRead]
    total: int
