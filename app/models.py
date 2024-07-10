from uuid import UUID, uuid4
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


class UuidMixin:
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)


class Base(AsyncAttrs, DeclarativeBase):
    pass
