from aiogram import types
from aiogram.filters.base import Filter
from database.connections import get_all_admins


class IsAdmin(Filter):

    async def __call__(self, message: types.Message) -> bool:
        admins_data = await get_all_admins()
        admins = [item['admin_id'] for item in admins_data if item.get("admin_id")]
        return message.from_user.id in admins
