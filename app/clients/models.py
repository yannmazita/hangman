from pydantic import BaseModel
from app.auth.models import Token


class AppError(BaseModel):
    error: str


class GameUpdate(BaseModel):
    word_progress: str
    guessed_letters: list[str]
    tries_left: int
    successful_guesses: int
    max_tries: int
    game_status: int = 0


class GameGuess(BaseModel):
    letter: str


class GameStats(BaseModel):
    active_players: int


class WebsocketMessage(BaseModel):
    action: str
    data: Token | AppError | GameGuess | GameStats | GameUpdate | None = None
