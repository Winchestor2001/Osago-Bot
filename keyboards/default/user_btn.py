from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder


remove_btn = ReplyKeyboardRemove()


async def start_menu_btn():
    start_menu = ReplyKeyboardBuilder()
    start_menu.add(
        KeyboardButton(text='📂 Наши услуги'), KeyboardButton(text='👤 Профиль'),
        KeyboardButton(text='☎️ Обратная связь'), KeyboardButton(text='💥Телеграм канал')
    )
    start_menu.adjust(2)
    return start_menu.as_markup(resize_keyboard=True)


async def cancel_btn():
    btn = ReplyKeyboardBuilder()
    btn.add(
        KeyboardButton(text="❌ Отменить")
    )
    btn.adjust(1)
    return btn.as_markup(resize_keyboard=True)
