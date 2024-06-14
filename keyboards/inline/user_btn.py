from aiogram.types import InlineKeyboardButton
from data.config import FROM_LINK
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def from_link_btn():
    from_link = InlineKeyboardBuilder()
    from_link.add(
        *[InlineKeyboardButton(text=FROM_LINK[item], callback_data=f"from:{item}") for item in FROM_LINK]
    )
    from_link.adjust(2)
    return from_link.as_markup()
