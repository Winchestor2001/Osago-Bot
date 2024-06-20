from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    depozit = State()


class Data(StatesGroup):
    photo = State()
    text = State()
