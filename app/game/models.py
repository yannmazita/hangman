from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import ARRAY, Integer, String
from app.game.config import MAX_TRIES
from app.models import Base, UuidMixin


class Game(Base, UuidMixin):
    __tablename__ = "games"
    player_id: Mapped[UUID] = mapped_column(ForeignKey("players.id"))
    word_to_guess: Mapped[str] = mapped_column(default="")
    word_progress: Mapped[str] = mapped_column(default="")
    guessed_positions: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=[])
    guessed_letters: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    tries_left: Mapped[int] = mapped_column(default=MAX_TRIES)
    successful_guesses: Mapped[int] = mapped_column(default=0)
    game_status: Mapped[int] = mapped_column(default=0)
