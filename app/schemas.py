from uuid import UUID

from pydantic import BaseModel


class UuidMixin:
    id: UUID | None = None


class Base(BaseModel):
    pass
