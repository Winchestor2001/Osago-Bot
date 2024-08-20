from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def mandatory_channel_btn(channels):
    buttons = [
        InlineKeyboardButton(
            text=f"{channel['channel_name']}",
            url=channel['channel_url']
        ) for channel in channels
    ]
    buttons.append(InlineKeyboardButton(
        text="Готово ✅",
        callback_data="check_subscribed"
    ))
    keyboard = InlineKeyboardBuilder()
    keyboard.add(*buttons)
    keyboard.adjust(1)
    return keyboard.as_markup()
