import logging
from uuid import UUID

from app.users.models import (
    User,
)
from app.users.repository import UserRepository
from app.users.schemas import (
    UserUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class UserServiceBase:
    """
    Base class for user-related operations.

    Attributes:
        repository: The user repository to be used for operations.
    """

    def __init__(self, repository: UserRepository):
        self.repository = repository


class UserService(UserServiceBase):
    """
    Class for user-related operations.
    Attributes:
        repository: The user repository to be used for operations.
    """

    def __init__(self, repository: UserRepository):
        super().__init__(repository)

    async def update_user_password(
        self, session: AsyncSession, id: UUID, data: UserUpdate
    ) -> User:
        """
        Update a user's password.

        Dedidacated method for password updates. If other data besides password information is
        present, it is ignored.
        Args:
            session: The database session to be used for the operation.
            id: The ID of the user to update.
            data: The data to be used for updating the user.
        Returns:
            The updated user.
        """
        data.username = None
        data.roles = None
        logger.debug(f"Updating password for user with ID: {id}")
        updated_user: User = await self.repository.update_by_attribute(
            session, data, id
        )
        logger.info(f"Password updated for user with ID: {id}")
        return updated_user


class UserAdminService(UserServiceBase):
    """
    Class for user-related operations.
    Attributes:
        repository: The user repository to be used for operations.
    """

    def __init__(self, repository: UserRepository):
        super().__init__(repository)

    async def update_user_username(
        self, session: AsyncSession, id: UUID, data: UserUpdate
    ) -> User:
        """
        Update a user's username.

        Dedidacated method for username updates. If other data besides username is
        present, it is ignored.
        Args:
            session: The database session to be used for the operation.
            id: The ID of the user to update.
            data: The data to be used for updating the user.
        Returns:
            The updated user.
        """
        data.confirm_password = None
        data.new_password = None
        data.old_password = None
        data.roles = None
        logger.debug(f"Updating username for user with ID: {id}")
        updated_user: User = await self.repository.update_by_attribute(
            session, data, id
        )
        logger.info(f"Username updated for user with ID: {id}")
        return updated_user

    async def update_user_roles(
        self, session: AsyncSession, id: UUID, data: UserUpdate
    ) -> User:
        """
        Update a user's roles.

        Dedidacated method for role updates. If other data besides roles is
        present, it is ignored.
        Args:
            session: The database session to be used for the operation.
            id: The ID of the user to update.
            data: The data to be used for updating the user.
        Returns:
            The updated user.
        """
        data.username = None
        data.confirm_password = None
        data.new_password = None
        data.old_password = None
        logger.debug(f"Updating roles for user with ID: {id}")
        updated_user: User = await self.repository.update_by_attribute(
            session, data, id
        )
        logger.info(f"Username roles for user with ID: {id}")
        return updated_user
