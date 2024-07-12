from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base, UuidMixin


class Player(Base, UuidMixin):
    __tablename__ = "players"
    playername: Mapped[str] = mapped_column(index=True, unique=True)
    username: Mapped[str] = mapped_column(ForeignKey("users.username"), nullable=True)
    points: Mapped[int] = mapped_column(default=0)
    games_played: Mapped[int] = mapped_column(default=0)
    games_won: Mapped[int] = mapped_column(default=0)
