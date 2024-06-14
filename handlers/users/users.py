import logging
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.deep_linking import create_deep_link

from keyboards.inline.channels import mandatory_channel_btn
from loader import bot
from utils.bot_context import *
from database.connections import *
from utils.misc.is_subscribed import is_subscribed

router = Router()


@router.message(CommandStart(deep_link=True))
async def start_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(start_text)
    user_id, full_name, username = message.from_user.id, message.from_user.full_name, message.from_user.username
    await add_user(user_id=user_id, full_name=full_name, username=username, from_link="Yandex")
    args = message.text.split()[1]
    check = await check_user(user_id)
    # if args and check:


@router.message(Command(commands=['start', 'menu', 'cancel']))
async def start_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(start_text)
    user_id, full_name, username = message.from_user.id, message.from_user.full_name, message.from_user.username
    check = await check_user(user_id)
    await add_user(user_id=user_id, full_name=full_name, username=username, from_link="Yandex")


@router.message()
async def sss(message: Message):
    await message.send_copy(chat_id=message.chat.id)


# check whether user subscribed to all channels or not
@router.callback_query(F.data == "check_subscribed")
async def check_subscribed(call: CallbackQuery):
    user_id = call.from_user.id
    channels = await is_subscribed(user_id)

    if channels:
        await call.answer("Подпишитесь на наш канал 👇", show_alert=True)
        keyboard = await mandatory_channel_btn(channels)
        await call.message.delete()
        await call.message.answer(
            "Подпишитесь на наш канал 👇",
            reply_markup=keyboard
        )
    else:
        await call.answer("Благодарим вас за подписку на все необходимые каналы!")
        await call.message.delete()
        await call.message.answer(start_text)
