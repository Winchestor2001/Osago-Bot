from . import users
from . import admins


routers_list = [
    users.users.router,
    users.services.router,
    users.profile.router,
    users.contact.router,
    admins.start.router,
    admins.manage_admin.router,
]

__all__ = [
    "routers_list",
]

