from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base, UuidMixin


class User(Base, UuidMixin):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(index=True, unique=True)
    hashed_password: Mapped[str] = mapped_column()
    roles: Mapped[str] = mapped_column(default="")
