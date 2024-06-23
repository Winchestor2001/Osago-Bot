from . import users
from . import admins


routers_list = [
    admins.send_ads.router,
    admins.change_prices.router,
    users.users.router,
    users.services.router,
    users.profile.router,
    users.contact.router,
    admins.start.router,
    admins.manage_admin.router,
    admins.other_funcs.router,
]

__all__ = [
    "routers_list",
]

