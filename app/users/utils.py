import logging
from app.database import sessionmanager
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate
from app.users.services import UserAdminService
from app.users.repository import UserRepository

logger = logging.getLogger(__name__)


async def create_superuser():
    async with sessionmanager.session() as session:
        repository = UserRepository()
        admin_service = UserAdminService(repository)
        try:
            logger.info("Creating superuser with username 'admin'")
            admin_user: User = await repository.create(
                session, UserCreate(username="admin", password="secret")
            )
            await admin_service.update_user_roles(
                session, admin_user.id, UserUpdate(roles="admin")
            )
        except Exception:
            logger.warning("Failed to create")
            pass
