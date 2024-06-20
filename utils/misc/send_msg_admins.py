from database.connections import get_all_admins
from loader import bot


async def send_to_admins(text):
    admins = await get_all_admins()
    for i in admins:
        await bot.send_message(chat_id=i['admin_id'], text=text)
