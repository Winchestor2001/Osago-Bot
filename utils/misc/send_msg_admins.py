from data.config import ADMINS
from loader import bot


async def send_to_admins(text):
    for i in ADMINS:
        await bot.send_message(chat_id=i, text=text)
