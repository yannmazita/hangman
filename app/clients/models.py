from pydantic import BaseModel
from app.auth.models import Token


class AppError(BaseModel):
    error: str


class AppStats(BaseModel):
    active_users: int


class WebsocketMessage(BaseModel):
    action: str
    data: Token | AppError | AppStats | None = None
