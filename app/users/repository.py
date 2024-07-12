from uuid import UUID, uuid4

from app.repository import DatabaseRepository
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.auth.utils import get_password_hash, verify_password
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate, User as UserSchema


class UserRepository(DatabaseRepository):
    """
    Repository for performing database queries on users.
    """

    def __init__(self):
        super().__init__(User)

    async def create(self, session: AsyncSession, data: UserCreate) -> User:
        hashed_password: str = get_password_hash(data.password)
        new_user = UserSchema(
            id=uuid4(), username=data.username, hashed_password=hashed_password
        )
        return await super().create(session, new_user)

    async def update_by_attribute(
        self,
        session,
        data: UserUpdate,
        value: UUID | str,
        column: str = "id",
        none_replace: bool = False,
    ) -> User:
        db_user: User = await super().get_by_attribute(session, value, column, True)

        # Allow password updates only if password data is correctly input
        if data.old_password is not None:
            if not verify_password(data.old_password, db_user.hashed_password):
                raise ValueError("Incorrect password.")
            elif data.new_password is not None:
                db_user.hashed_password = get_password_hash(data.new_password)
        return await super().update_by_attribute(
            session, data, value, column, none_replace
        )
