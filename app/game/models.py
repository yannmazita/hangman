from uuid import UUID
from sqlalchemy import Integer
from sqlmodel import ARRAY, Column, Field, SQLModel, String
from app.game.config import MAX_TRIES
from sqlalchemy.ext.asyncio import AsyncAttrs


class GameBase(AsyncAttrs, SQLModel):
    player_id: UUID | None = Field(
        default=None, index=True, foreign_key="player.id", unique=True
    )


class Game(GameBase, table=True):
    id: UUID | None = Field(default=None, primary_key=True)
    word_to_guess: str = Field(default="")
    word_progress: str = Field(default="")
    guessed_positions: list[int] = Field(default=[], sa_column=Column(ARRAY(Integer())))
    guessed_letters: list[str] = Field(default=[], sa_column=Column(ARRAY(String())))
    tries_left: int = Field(default=MAX_TRIES)
    successful_guesses: int = Field(default=0)
    game_status: int = Field(default=0)


class GameCreate(GameBase):
    pass


class GameRead(GameBase):
    id: UUID
    word_to_guess: str
    word_progress: str
    guessed_positions: list[int] = Field(default=[], sa_column=Column(ARRAY(Integer())))
    guessed_letters: list[str] = Field(default=[], sa_column=Column(ARRAY(String())))
    tries_left: int
    successful_guesses: int
    game_status: int
