from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.models import Base
from app.config import settings


# use pydantic url validation abilities instead
ASYNC_POSTGRES_URL: str = (
    "postgresql+asyncpg://"
    + f"{settings.postgres_user}:"
    + f"{settings.postgres_password}"
    + f"@{settings.postgres_host}:"
    + f"{settings.postgres_port}/"
    + f"{settings.postgres_db or ''}"
)


class DatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}):
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(
            autocommit=False, bind=self._engine, expire_on_commit=False
        )

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(
    ASYNC_POSTGRES_URL, {"echo": settings.postgres_echo}
)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with sessionmanager.session() as session:
        yield session


async def create_db_and_tables():
    async with sessionmanager._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
