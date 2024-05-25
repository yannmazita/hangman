import logging
from app.database import sessionmanager
from app.users.models import UserCreate, UserRolesUpdate
from app.users.schemas import UserAttribute
from app.users.services import UserAdminService, UserService

loggeer = logging.getLogger(__name__)


async def create_superuser():
    async with sessionmanager.session() as session:
        service = UserService(session)
        admin_service = UserAdminService(session)
        admin_user = UserCreate(username="admin", password="secret")
        try:
            await service.create_user(admin_user)
            await admin_service.update_user_roles_by_attribute(
                UserAttribute.USERNAME, "admin", UserRolesUpdate(roles="admin")
            )
        except Exception:
            # handled earlier
            pass
