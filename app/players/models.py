from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, Session, SQLModel

from app.database import engine


class PlayerBase(SQLModel):
    playername: str = Field(index=True, unique=True)
    username: str = Field(index=True, foreign_key="user.username")
    points: int = 0
    games_played: int = 0
    games_won: int = 0


class Player(PlayerBase, table=True):
    id: UUID | None = Field(default=None, primary_key=True)


class PlayerCreate(PlayerBase):
    pass


class PlayerRead(PlayerBase):
    id: UUID


def create_fake_players():
    player1: Player = Player(
        playername="player1",
        username="user1",
        points=1337,
        games_played=1,
        games_won=1,
        id=UUID("123e4567-e89b-12d3-a456-426614174000", version=4),
    )
    player2: Player = Player(
        playername="player2",
        username="user2",
        points=7331,
        games_played=1,
        games_won=1,
        id=UUID("455f6170-238e-401f-8077-2121c72412bf", version=4),
    )
    db_player1 = Player.model_validate(player1)
    db_player2 = Player.model_validate(player2)
    session = Session(engine)
    session.add(db_player1)
    session.add(db_player2)
    try:
        session.commit()
    except IntegrityError:
        pass
