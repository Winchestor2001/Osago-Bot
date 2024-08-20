from aiogram.filters.state import StatesGroup, State


class Admin(StatesGroup):
    send_msg = State()
    change_product_price = State()
    change_bot_config = State()
