from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.connections import get_all_services, get_product_by_service


async def services_btn():
    keyboard = InlineKeyboardBuilder()
    services = await get_all_services()
    keyboard.add(
        *[InlineKeyboardButton(text=f"{item['name']}", callback_data=f"services:{item['id']}") for item in services]
    )
    keyboard.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="services:back_to_main_menu"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def products_btn(service_id):
    keyboard = InlineKeyboardBuilder()
    products = await get_product_by_service(service_id)
    keyboard.add(
        *[InlineKeyboardButton(text=f"{i['name']} | {i['price']}руб", callback_data=f"products:{i['id']}") for i in
          products]
    )
    keyboard.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="products:back_to_services"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def choose_proccess_btn():
    choose_proccess = InlineKeyboardBuilder()
    choose_proccess.add(
        InlineKeyboardButton(text="По фото 📸", callback_data=f"by:photo"),
        InlineKeyboardButton(text="В ручную ✍️", callback_data=f"by:hand"),
        InlineKeyboardButton(text="🔙 Назад", callback_data=f"by:cancel"),
    )
    choose_proccess.adjust(1)
    return choose_proccess.as_markup()
