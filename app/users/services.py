import logging
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.exc import (
    IntegrityError,
    MultipleResultsFound,
    NoResultFound,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from app.auth.exceptions import incorrect_password
from app.auth.utils import get_password_hash, verify_password
from app.users.exceptions import (
    multiple_users_found,
    user_already_exists,
    user_not_found,
)
from app.users.models import (
    User,
    UserCreate,
    UserPasswordUpdate,
    UserRolesUpdate,
    UserUsernameUpdate,
)
from app.users.schemas import UserAttribute

logger = logging.getLogger(__name__)


class UserServiceBase:
    """
    Base class for user-related operations.

    Attributes:
        session: The database session to be used for operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: UserCreate) -> User:
        """
        Create a new user.
        Args:
            user: The user data.
        Returns:
            The created user.
        """
        try:
            logger.debug(f"Attempting to create user: {user.username}")
            query = select(User).where(User.username == user.username)
            response = await self.session.execute(query)
            existing_user: User | None = response.scalar_one_or_none()

            if existing_user:
                logger.warning(f"User already exists: {user.username}")
                raise user_already_exists

            hashed_password = get_password_hash(user.password)
            new_user = User(
                id=uuid4(), username=user.username, hashed_password=hashed_password
            )
            db_user = User.model_validate(new_user)

            logger.debug(f"Adding new user to session: {db_user}")
            self.session.add(db_user)

            logger.debug("Committing session")
            await self.session.commit()

            logger.debug("Refreshing session")
            await self.session.refresh(db_user)

            logger.info(f"User created successfully: {db_user.username}")
            return db_user
        except IntegrityError as e:
            logger.error(f"IntegrityError occurred: {e}", exc_info=False)
            raise e
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except HTTPException as e:
            logger.error(f"HTTPException occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e

    async def get_user_by_attribute(self, attribute: UserAttribute, value: str) -> User:
        """
        Get a user by a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
        Returns:
            The user with the specified attribute and value.
        """
        try:
            logger.debug(f"Attempting to get user by {attribute.value}: {value}")
            query = select(User).where(getattr(User, attribute.value) == value)
            response = await self.session.execute(query)
            user = response.scalar_one()
            logger.info(f"User found: {user.username}")
            return user
        except MultipleResultsFound:
            logger.error(
                f"Multiple users found for {attribute.value} = {value}", exc_info=False
            )
            raise multiple_users_found
        except NoResultFound:
            logger.warning(
                f"No user found for {attribute.value} = {value}", exc_info=False
            )
            raise user_not_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e

    async def update_user_by_attribute(
        self, attribute: UserAttribute, value: str, user: UserCreate
    ) -> User:
        """
        Update a user using a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
            user: The new user data.
        Returns:
            The updated user.
        """
        try:
            logger.debug(f"Attempting to update user by {attribute.value}: {value}")
            user_db = await self.get_user_by_attribute(attribute, value)
            user_data = user.model_dump()
            for key, value in user_data.items():
                setattr(user_db, key, value)
            self.session.add(user_db)
            await self.session.commit()
            await self.session.refresh(user_db)
            logger.info(f"User updated successfully: {user_db.username}")
            return user_db
        except NoResultFound:
            logger.warning(
                f"No user found for {attribute.value} = {value}", exc_info=False
            )
            raise user_not_found
        except MultipleResultsFound:
            logger.error(
                f"Multiple users found for {attribute.value} = {value}", exc_info=False
            )
            raise multiple_users_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e

    async def delete_user(self, user: User) -> User:
        """
        Delete a user.
        Args:
            user: The user to delete.
        Returns:
            The deleted user.
        """
        try:
            logger.debug(f"Attempting to delete user: {user.username}")
            await self.session.delete(user)
            await self.session.commit()
            logger.info(f"User deleted successfully: {user.username}")
            return user
        except NoResultFound:
            logger.warning(f"No user found to delete: {user.username}", exc_info=False)
            raise user_not_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e

    async def delete_user_by_attribute(
        self, attribute: UserAttribute, value: str
    ) -> User:
        """
        Delete a user using a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
        Returns:
            The deleted user.
        """
        try:
            logger.debug(f"Attempting to delete user by {attribute.value}: {value}")
            user = await self.get_user_by_attribute(attribute, value)
            await self.session.delete(user)
            await self.session.commit()
            logger.info(f"User deleted successfully: {user.username}")
            return user
        except NoResultFound:
            logger.warning(
                f"No user found for {attribute.value} = {value}", exc_info=False
            )
            raise user_not_found
        except MultipleResultsFound:
            logger.error(
                f"Multiple users found for {attribute.value} = {value}", exc_info=False
            )
            raise multiple_users_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e

    async def get_users(self, offset: int = 0, limit: int = 100):
        """
        Get all users.
        Args:
            offset: The number of users to skip.
            limit: The maximum number of users to return.
        Returns:
            The list of users.
        """
        try:
            logger.debug(f"Fetching users with offset: {offset}, limit: {limit}")
            total_count_query = select(func.count()).select_from(User)
            total_count_response = await self.session.execute(total_count_query)
            total_count: int = total_count_response.scalar_one()

            users_query = select(User).offset(offset).limit(limit)
            users_response = await self.session.execute(users_query)
            users = users_response.scalars().all()
            logger.info(f"Fetched {len(users)} users")
            return users, total_count
        except NoResultFound:
            logger.warning("No users found", exc_info=False)
            raise user_not_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e


class UserService(UserServiceBase):
    """
    Class for user-related operations.
    Attributes:
        session: The database session to be used for operations.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def update_user_password(
        self, user: User, password_data: UserPasswordUpdate
    ) -> None:
        """
        Update a user's password.
        Args:
            user: The user.
            password_data: The new password data.
        """
        try:
            logger.debug(f"Updating password for user: {user.username}")
            if not verify_password(password_data.old_password, user.hashed_password):
                logger.warning(f"Incorrect password for user: {user.username}")
                raise incorrect_password
            user.hashed_password = get_password_hash(password_data.new_password)
            self.session.add(user)
            await self.session.commit()
            logger.info(f"Password updated for user: {user.username}")
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e


class UserAdminService(UserServiceBase):
    """
    Class for user-related operations.
    Attributes:
        session: The database session to be used for operations.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def update_user_username_by_attribute(
        self, attribute: UserAttribute, value: str, new_username: UserUsernameUpdate
    ) -> User:
        """
        Update a user's username using a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
            new_username: The new username.
        Returns:
            The updated user.
        """
        try:
            logger.debug(f"Updating username for user with {attribute.value}: {value}")
            user = await self.get_user_by_attribute(attribute, value)
            user.username = new_username.username
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            logger.info(
                f"Username updated to {new_username.username} for user: {user.username}"
            )
            return user
        except NoResultFound:
            logger.warning(
                f"No user found for {attribute.value} = {value}", exc_info=False
            )
            raise user_not_found
        except MultipleResultsFound:
            logger.error(
                f"Multiple users found for {attribute.value} = {value}", exc_info=False
            )
            raise multiple_users_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e

    async def update_user_roles_by_attribute(
        self, attribute: UserAttribute, value: str, new_roles: UserRolesUpdate
    ) -> User:
        """
        Update a user's roles using a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
            new_roles: The new roles.
        Returns:
            The updated user.
        """
        try:
            logger.debug("Starting update_user_roles_by_attribute")
            user = await self.get_user_by_attribute(attribute, value)
            logger.debug(f"User found: {user}")

            user.roles = new_roles.roles
            self.session.add(user)
            logger.debug(f"User added to session: {user}")

            await self.session.commit()
            logger.debug("Session committed")

            await self.session.refresh(user)
            logger.debug("Session refreshed")
            return user
        except NoResultFound:
            logger.error("User not found", exc_info=False)
            raise user_not_found
        except MultipleResultsFound:
            logger.error("Multiple users found", exc_info=False)
            raise multiple_users_found
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error occurred", exc_info=False)
            raise e
        except Exception as e:
            logger.error("Unexpected error occurred", exc_info=False)
            raise e
