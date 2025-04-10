import logging
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram.exceptions import TelegramAPIError
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.default.user_btn import start_menu_btn
from keyboards.inline.channels import mandatory_channel_btn
from keyboards.inline.user_btn import from_link_btn, user_deposit_types_btn
from loader import bot
from states.all_states import UserStates
from utils.bot_context import *
from database.connections import *
from utils.misc.is_subscribed import is_subscribed

router = Router()

@router.message(Command(commands="buy_subscription"))
async def send_invoice_handler(message: Message):
    prices = [LabeledPrice(label="Пополнение балансу", amount=3000)]
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Пополнить 3000 ⭐️", pay=True)

    await message.answer_invoice(
        title="Авто услуги",
        description="Пополнить баланс",
        prices=prices,
        provider_token="",
        payload="subscription_payment",
        currency="XTR",
        reply_markup=keyboard.as_markup(),
    )

@router.message(CommandStart(deep_link=True))
async def start_command(message: Message, state: FSMContext):
    await state.clear()
    user_id, full_name, username = message.from_user.id, message.from_user.full_name, message.from_user.username
    args = message.text.split()[1] if message.text.split()[1] else 0
    check = await check_user(user_id)
    if type(args) == int and int(args) != user_id and not check:
        await state.update_data(referer=args)
    else:
        btn = await start_menu_btn()
        await message.answer(start_text, reply_markup=btn)

    if not check:
        btn = await from_link_btn()
        await message.answer(f"<b>Откуда вы узнали про нас?</b>", reply_markup=btn)


@router.callback_query(F.data.startswith("from:"))
async def from_link_callback(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    from_link = call.data.split(":")[1]
    user_id, full_name, username = call.from_user.id, call.from_user.full_name, call.from_user.username
    await add_user(user_id=user_id, full_name=full_name, username=username, from_link=from_link)
    btn = await start_menu_btn()
    await call.message.delete()
    await call.message.answer(start_text, reply_markup=btn)
    if "referer" in data.keys():
        referer = data["referer"]
        bot_configs = await get_bot_configs()
        bot_configs = bot_configs[-1]['ref_sum']
        await update_user_balance(user_id=referer, value=bot_configs, incriment=True, referer=True)
        try:
            await bot.send_message(referer, f"Вам начилсено реферальный бонус {bot_configs}руб.")
        except TelegramAPIError:
            pass


@router.message(Command(commands=['start', 'menu', 'cancel']))
async def start_command(message: Message, state: FSMContext):
    await state.clear()
    check = await check_user(message.from_user.id)
    if not check:
        btn = await from_link_btn()
        await message.answer(f"<b>Откуда вы узнали про нас?</b>", reply_markup=btn)
    else:
        btn = await start_menu_btn()
        await message.answer(start_text, reply_markup=btn)


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


@router.message(F.text == "💰 Пополнить баланс")
async def user_deposit_handler(message: Message, state: FSMContext):
    btn = await user_deposit_types_btn()
    await message.answer(text="💰 Выбери способ пополнения:", reply_markup=btn)
    await state.set_state(UserStates.deposit_types)