from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def start_menu_btn():
    start_menu = ReplyKeyboardBuilder()
    start_menu.add(
        KeyboardButton(text='📂 Наши услуги'), KeyboardButton(text='👤 Профиль'),
        KeyboardButton(text='☎️ Обратная связь'), KeyboardButton(text='💥Телеграм канал')
    )
    start_menu.adjust(2)
    return start_menu.as_markup(resize_keyboard=True)
