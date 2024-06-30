from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove

from database.connections import admin_get_all_products


async def admin_menu_btn():
    admin_menu = InlineKeyboardMarkup(row_width=2)
    admin_menu.add(
        InlineKeyboardButton('💵 Изменить цены', callback_data='change_prices'),
        InlineKeyboardButton('📮 Рассылка юзерам', callback_data='sending_all'),
        InlineKeyboardButton('👥 Список админов', callback_data='all_admins')
    )
    return admin_menu


async def products_btn():
    products = InlineKeyboardMarkup(row_width=1)
    all_products = await admin_get_all_products()
    products.add(
        *[InlineKeyboardButton(f"{item['product_name']}|{item['product_price']}руб.", callback_data=f"edit_price:{item['product_slug']}") for item in all_products],
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_admin")
    )
    return products
