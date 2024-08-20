from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    depozit = State()


class Data(StatesGroup):
    photo = State()
    text = State()


class AdminStates(StatesGroup):
    add_admin_text = State()
