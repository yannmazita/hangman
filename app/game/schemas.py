from uuid import UUID

from app.game.config import MAX_TRIES
from app.schemas import Base, UuidMixin


class Game(Base, UuidMixin):
    player_id: UUID
    word_to_guess: str = ""
    word_progress: str = ""
    guessed_positions: list[int] = []
    guessed_letters: list[str] = []
    tries_left: int = MAX_TRIES
    successful_guesses: int = 0
    game_status: int = 0


class GameBase(Base):
    player_id: UUID


class GameCreate(GameBase):
    pass


class GameRead(GameBase, UuidMixin):
    word_progress: str
    guessed_letters: list[str] = []
    tries_left: int
    successful_guesses: int
    game_status: int


class GameUpdate(Base):
    word_to_guess: str | None = None
    word_progress: str | None = None
    guessed_positions: list[int] | None = None
    guessed_letters: list[str] | None = None
    tries_left: int | None = None
    successful_guesses: int | None = None
    game_status: int | None = None
    player_id: UUID | None = None
