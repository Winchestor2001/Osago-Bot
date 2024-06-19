from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def photo_done_btn():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
        KeyboardButton(text="✅ Готово"),
        KeyboardButton(text="🔙 Назад"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)
