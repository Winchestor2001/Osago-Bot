from aiogram.filters.state import StatesGroup, State


class Admin(StatesGroup):
    send_msg = State()
