from database.connections import get_all_channels
from aiogram.exceptions import TelegramForbiddenError, TelegramAPIError
from data.config import ADMINS
from loader import bot
from .send_msg_admins import send_to_admins


async def is_subscribed(user_id):
    channels = await get_all_channels()
    not_subscribed_channels = []
    for channel in channels:
        try:
            chat_member = await bot.get_chat_member(channel['channel_id'], user_id)
            if chat_member.status not in ['member', 'administrator', 'creator']:
                not_subscribed_channels.append(channel)
        except TelegramForbiddenError as er:
            text = f"Ошибка при проверке подписки на канал {channel['channel_name']}({channel['channel_url']}): {er}"
            await send_to_admins(text)
            continue
        except TelegramAPIError as e:
            text = f"Ошибка при проверке подписки на канал {channel['channel_name']}({channel['channel_url']}): {e}"
            await send_to_admins(text)

    return not_subscribed_channels
