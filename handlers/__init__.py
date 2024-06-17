from . import users
from . import admins


routers_list = [
    users.users.router,
    users.profile.router,
]

__all__ = [
    "routers_list",
]

