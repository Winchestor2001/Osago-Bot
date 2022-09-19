from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from data.config import FROM_LINK, BOT_CHANNEL_LINK
from database.connections import get_user_history, get_products


async def start_menu_btn():
    start_menu = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    start_menu.row('📂 Наши услуги', '👤 Профиль')
    start_menu.row('☎️ Обратная связь', '💥Телеграм канал')
    return start_menu


async def from_link_btn():
    from_link = InlineKeyboardMarkup(row_width=2)
    from_link.add(
        *[InlineKeyboardButton(f"{FROM_LINK[item]}", callback_data=f"from:{item}") for item in FROM_LINK]
    )
    return from_link


async def user_profile_btn(user_id: int):
    user_profile = InlineKeyboardMarkup(row_width=1)
    history = await get_user_history(user_id)
    user_profile.add(
        InlineKeyboardButton(f"💳 Пополнить баланс", callback_data=f"depozit"),
        InlineKeyboardButton(f"🧰 История заказов ({len(history)})", callback_data="user_history")
    )
    return user_profile


async def show_history_btn():
    show_history = InlineKeyboardMarkup(row_width=1)
    show_history.add(
        InlineKeyboardButton("Очистить", callback_data="clear_history"),
        InlineKeyboardButton("Назад", callback_data="back_profile"),
    )
    return show_history


async def services_btn():
    services = InlineKeyboardMarkup(row_width=2)
    services.add(
        InlineKeyboardButton("📑Купить ОСАГО", callback_data="osago"),
        InlineKeyboardButton("📋Техосмотр", callback_data="dk"),
        InlineKeyboardButton("📃Мед Справка на права", callback_data="auto_med"),
        InlineKeyboardButton("🏦КАСКО для банка", callback_data="kasko_bank"),
        InlineKeyboardButton("🏪Карта учета ГИБДД", callback_data="karta_gibdd"),
        InlineKeyboardButton("🚓Карта ВУ по базе ГАИ", callback_data="karta_gai"),
        InlineKeyboardButton("🔎Поиск по базе Солярис", callback_data="search_solary"),
    )
    return services


async def channel_btn():
    channel = InlineKeyboardMarkup(row_width=1)
    channel.add(
        InlineKeyboardButton("Подписаться 🌐", url=BOT_CHANNEL_LINK),
        InlineKeyboardButton("Готово ✅", callback_data="subscribed"),
    )
    return channel


async def product_btn(value: str):
    product = InlineKeyboardMarkup(row_width=1)
    products = await get_products(value)
    product.add(
        *[InlineKeyboardButton(f"{item['product_name']} | {item['product_price']}руб.", callback_data=f"{item['product_id']}:{item['product_slug']}") for item in products],
        InlineKeyboardButton("🔙 Назад", callback_data="back")
    )
    return product


async def choose_proccess_btn(value: str):
    choose_proccess = InlineKeyboardMarkup(row_width=1)
    choose_proccess.add(
        InlineKeyboardButton("По фото 📸", callback_data=f"{value}_photo"),
        InlineKeyboardButton("В ручную ✍️", callback_data=f"{value}_simple"),
    )
    return choose_proccess


async def cancel_btn():
    cancel = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel.row("❌ Отменить")
    return cancel


async def remove_btn():
    remove = ReplyKeyboardRemove()
    return remove


async def finish_questionnaire_btn():
    finish_questionnaire = ReplyKeyboardMarkup(resize_keyboard=True)
    finish_questionnaire.row('✅ Готово')

    return finish_questionnaire


async def payment_btn(bill_url: str):
    payment = InlineKeyboardMarkup(row_width=1)
    payment.add(
        InlineKeyboardButton("💸 Оплатить", url=bill_url),
        InlineKeyboardButton("❌ Отменить", callback_data=f"cancel_invoice"),
    )
    return payment
