from uuid import UUID
from sqlmodel import Field, SQLModel
from app.game.config import MAX_TRIES


class GameBase(SQLModel):
    player_id: UUID = Field(index=True, foreign_key="player.id", unique=True)


class Game(GameBase, table=True):
    id: UUID | None = Field(default=None, primary_key=True)
    word_to_guess: str
    guessed_positions: list[int]
    guessed_letters: list[str]
    tries_left: int = Field(default=MAX_TRIES)
    successful_guesses: int
    game_status: int


class GameCreate(GameBase):
    player_id: UUID


class GameRead(GameBase):
    id: UUID
    word_to_guess: str
    guessed_positions: list[int]
    guessed_letters: list[str]
    tries_left: int
    successful_guesses: int
    game_status: int
