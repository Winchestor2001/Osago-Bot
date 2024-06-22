from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from filters.is_admin import IsAdmin
from keyboards.default.user_btn import remove_btn
from utils.misc.useful_functions import get_admin_context

router = Router()


@router.message(Command(commands=["admin"]), IsAdmin())
async def intro_admin(message: Message, state: FSMContext):
    await state.clear()
    context, btn = await get_admin_context()
    await message.answer("Ты находитесь в панели администратора", reply_markup=remove_btn)
    await message.answer(context, reply_markup=btn)
