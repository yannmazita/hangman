from uuid import UUID
from sqlmodel import Field, SQLModel
from app.game.config import MAX_TRIES


class GameBase(SQLModel):
    player_id: UUID | None = Field(default=None, index=True, foreign_key="player.id", unique=True)


class Game(GameBase, table=True):
    id: UUID | None = Field(default=None, primary_key=True)
    word_to_guess: str = Field(default="")
    word_progress: str = Field(default="")
    guessed_positions: list[int] = Field(default=[])
    guessed_letters: list[str] = Field(default=[])
    tries_left: int = Field(default=MAX_TRIES)
    successful_guesses: int = Field(default=0)
    game_status: int = Field(default=0)


class GameRead(GameBase):
    id: UUID
    word_to_guess: str
    word_progress: str
    guessed_positions: list[int]
    guessed_letters: list[str]
    tries_left: int
    successful_guesses: int
    game_status: int
