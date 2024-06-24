from data.config import ADMINS
from database.connections import get_all_admins
from loader import bot


async def send_to_admins(text):
    admins = await get_all_admins()
    admins = [item['admin_id'] for item in admins if item.get("admin_id")]
    admins.extend(ADMINS)
    for i in admins:
        await bot.send_message(chat_id=i, text=text)
