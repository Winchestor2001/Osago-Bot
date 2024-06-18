from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link

from database.connections import get_user_info, get_bot_configs
from keyboards.default.user_btn import cancel_btn
from keyboards.inline.user_btn import user_profile_btn, cancel_inline_btn
from states.all_states import UserStates
from utils.bot_context import *
from loader import bot
from utils.misc.useful_functions import get_user_context

router = Router()


@router.message(F.text == "👤 Профиль")
async def user_profile_handler(message: Message):
    user_id = message.from_user.id
    context, btn = await get_user_context(user_id)
    await message.answer(context, reply_markup=btn, disable_web_page_preview=True)


@router.callback_query(F.data.startswith("user_profile:"))
async def user_handler(call: CallbackQuery, state: FSMContext):
    data = call.data.split(":")[1]
    await call.answer()
    await call.message.delete()
    if data == "depozit":
        btn = await cancel_inline_btn()
        bot_configs = await get_bot_configs()
        bot_configs = bot_configs[-1]['ref_sum']
        await call.message.answer(depozite_text.format(bot_configs), reply_markup=btn)
        await state.set_state(UserStates.depozit)
    elif data == "user_history":
        await call.message.answer("dddd")
    elif data == "cancel":
        context, btn = await get_user_context(call.from_user.id)
        await call.message.answer(context, reply_markup=btn, disable_web_page_preview=True)


@router.message(UserStates.depozit)
async def depozit_handler(message: Message, state: FSMContext):
    text = message.text

    if text.isdigit():
        print(text)

