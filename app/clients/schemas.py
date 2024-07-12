from app.auth.schemas import Token
from app.schemas import Base


class AppError(Base):
    error: str


class AppStats(Base):
    active_users: int


class WebsocketMessage(Base):
    action: str
    data: Token | AppError | AppStats | None = None
