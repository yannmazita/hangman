from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, Session, SQLModel

from .database import engine


class Token(BaseModel):
    access_token: str | None
    token_type: str | None


class AppError(BaseModel):
    error: str


class GameUpdate(BaseModel):
    word_progress: str
    guessed_positions: list[int]
    tries_left: int
    successful_guesses: int
    game_over: bool = False


class GameGuess(BaseModel):
    letter: str


class GameStats(BaseModel):
    active_players: int


class WebsocketMessage(BaseModel):
    action: str
    data: Token | AppError | GameGuess | GameStats | GameUpdate | None = None


class TokenData(SQLModel):
    username: str | None = None
    scopes: list[str] = []


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    player_id: UUID | None = Field(default=None, foreign_key="player.id")


class User(UserBase, table=True):
    id: UUID | None = Field(default=None, primary_key=True)
    hashed_password: str
    banned: bool = Field(default=False)
    roles: str = Field(
        default="user.create user:own user:own.write user:own:player user:own:player.write user:others:player:points user:others:player:playername websockets"
    )


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: UUID


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


def create_fake_users():
    user1: User = User(
        id=uuid4(),
        username="user1",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        player_id=UUID("123e4567-e89b-12d3-a456-426614174000", version=4),
    )
    user2: User = User(
        id=uuid4(),
        username="user2",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        player_id=UUID("455f6170-238e-401f-8077-2121c72412bf", version=4),
    )
    db_user1 = User.model_validate(user1)
    db_user2 = User.model_validate(user2)
    session = Session(engine)
    session.add(db_user1)
    session.add(db_user2)
    try:
        session.commit()
    except IntegrityError:
        pass


def create_admin_user():
    user: User = User(
        id=uuid4(),
        username="admin",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        roles="admin",
    )
    db_user = User.model_validate(user)
    session = Session(engine)
    session.add(db_user)
    try:
        session.commit()
    except IntegrityError:
        pass
