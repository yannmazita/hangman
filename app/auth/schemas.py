from app.schemas import Base


class Token(Base):
    access_token: str | None
    token_type: str | None


class TokenData(Base):
    username: str | None = None
    scopes: list[str] = []
