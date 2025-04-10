from aiogram.types import InlineKeyboardButton
from data.config import FROM_LINK
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.connections import get_user_history


async def from_link_btn():
    from_link = InlineKeyboardBuilder()
    from_link.add(
        *[InlineKeyboardButton(text=FROM_LINK[item], callback_data=f"from:{item}") for item in FROM_LINK]
    )
    from_link.adjust(2)
    return from_link.as_markup()


async def user_profile_btn(user_id):
    keyboard = InlineKeyboardBuilder()
    user_history = await get_user_history(user_id)
    keyboard.add(
        InlineKeyboardButton(text=f"💳 Пополнить баланс", callback_data=f"user_profile:depozit"),
        InlineKeyboardButton(text=f"🧰 История заказов ({len(user_history)})", callback_data="user_profile:user_history")
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def user_deposit_types_btn():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text=f"💳 Карта/СБП", callback_data=f"deposit:nicepay"),
        InlineKeyboardButton(text=f"🤑 Крипто", callback_data=f"deposit:crystalpay"),
        InlineKeyboardButton(text=f"🔙 Назад", callback_data=f"deposit:back"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def cancel_inline_btn():
    btn = InlineKeyboardBuilder()
    btn.add(
        InlineKeyboardButton(text="❌ Отменить", callback_data="user_profile:cancel")
    )
    btn.adjust(1)
    return btn.as_markup()


async def payment_btn(bill_url: str, deposit_type: str, invoice_id: str):
    payment = InlineKeyboardBuilder()
    payment.add(
        InlineKeyboardButton(text="💸 Оплатить", url=bill_url)
    )
    if deposit_type == "crystalpay":
        payment.add(InlineKeyboardButton(text="♻️ Проверить", callback_data=f"check_invoice:{invoice_id}"))
    payment.adjust(1)
    return payment.as_markup()


async def show_history_btn():
    show_history = InlineKeyboardBuilder()
    show_history.add(
        InlineKeyboardButton(text="🗑 Очистить", callback_data="user_history:clear_history"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="user_history:back_profile"),
    )
    show_history.adjust(1)
    return show_history.as_markup()
