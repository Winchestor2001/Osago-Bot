import asyncio
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.connections import get_bot_configs, get_user_history, clear_user_history, add_user_invoice, \
    delete_user_invoice
from handlers.users.users import start_command
from keyboards.default.user_btn import cancel_btn, remove_btn, start_menu_btn
from keyboards.inline.user_btn import payment_btn, show_history_btn, \
    user_deposit_types_btn
from services.payments import translate_crystalpay_type
from services.payments.crystalpay import CrystalPayClient
from services.payments.nicepay import NicepayInvoiceCreator
from states.all_states import UserStates
from utils.bot_context import *
from loader import bot
from utils.misc.useful_functions import get_user_context

router = Router()


@router.message(F.text == "👤 Профиль")
async def user_profile_handler(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    context, btn = await get_user_context(user_id)
    await message.answer(context, reply_markup=btn, disable_web_page_preview=True)


@router.message(F.text == "❌ Отменить")
async def cancel_all_states(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Процесс отменен")
    await start_command(message, state)


@router.callback_query(F.data.startswith("user_profile:"))
async def user_handler(call: CallbackQuery, state: FSMContext):
    data = call.data.split(":")[1]
    user_id = call.from_user.id
    if data == "depozit":
        btn = await user_deposit_types_btn()
        await call.message.edit_text(text="💰 Выбери способ пополнения:", reply_markup=btn)
        await state.set_state(UserStates.deposit_types)

    elif data == "user_history":
        history = (await get_user_history(user_id))[-10:]
        if len(history) != 0:
            context = '🗂 Вашы заказа:\n\n'
            for k, item in enumerate(history, start=1):
                context += f"{k}) {item['order_name']} | {item['price']}руб | {item['date']}\n"

            btn = await show_history_btn()
            await call.message.edit_text(context, reply_markup=btn)
        else:
            await call.answer("История заказов пуст")


@router.callback_query(F.data.startswith("user_history:"))
async def back_to_profile(call: CallbackQuery, state: FSMContext):
    data = call.data.split(':')[1]
    await state.clear()
    user_id = call.from_user.id
    if data == "back_profile":
        await call.message.delete()
        context, btn = await get_user_context(user_id)
        await call.message.answer(context, reply_markup=btn, disable_web_page_preview=True)
    elif data == "clear_history":
        await clear_user_history(user_id)
        await call.answer("История очищена")
        await call.message.delete()
        context, btn = await get_user_context(user_id)
        await call.message.answer(context, reply_markup=btn, disable_web_page_preview=True)


@router.callback_query(UserStates.deposit_types, F.data.startswith("deposit:"))
async def deposit_types_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    data = call.data.split(":")[1]
    if data == "back":
        await call.message.delete()
        context, btn = await get_user_context(user_id)
        await call.message.answer(context, reply_markup=btn, disable_web_page_preview=True)
        await state.clear()
    else:
        await state.update_data(deposit_type=data)
        try:
            await call.message.delete()
        except TelegramBadRequest:
            pass
        btn = await cancel_btn()
        bot_configs = await get_bot_configs()
        bot_configs = bot_configs[-1]['min_sum']
        await call.message.answer(depozite_text.format(bot_configs), reply_markup=btn)
        await state.set_state(UserStates.depozit)


@router.message(UserStates.depozit)
async def deposit_handler(message: Message, state: FSMContext):
    text = message.text
    user_id = message.from_user.id
    bot_configs = await get_bot_configs()
    bot_configs = bot_configs[-1]['min_sum']

    if not text.isdigit():
        await message.answer("Введите число")
        return
    elif int(text) < bot_configs:
        await message.answer(f"Минимальная сумма {bot_configs}руб.")
        return

    state_data = await state.get_data()
    if state_data.get("deposit_type") == "nicepay":
        invoice = await NicepayInvoiceCreator().create_invoice(
            order_id=str(user_id),
            customer=str(user_id),
            amount=int(text),
        )
        invoice_link = invoice.get("link")
        invoice_id = invoice.get("payment_id")
        btn_type = 'nicepay'
    else:
        invoice = await CrystalPayClient().create_invoice(amount=int(text), extra=str(user_id))
        invoice_link = invoice.get("url")
        invoice_id = invoice.get("id")
        btn_type = 'crystalpay'

    await add_user_invoice(user_id, invoice_id)
    btn = remove_btn
    loader_msg = await message.answer("⌛️", reply_markup=btn)
    await asyncio.sleep(.5)
    btn = await payment_btn(invoice_link, btn_type, invoice_id)
    await bot.delete_message(user_id, message_id=loader_msg.message_id)
    await message.answer(f"✅ Ссылка для оплаты создан <em>(у вас 15 минут чтобы перевести {text}руб.)</em>",
                         reply_markup=btn)
    await state.clear()


@router.callback_query(F.data.startswith("check_invoice:"))
async def check_invoice_handler(call: CallbackQuery):
    _, invoice_id = call.data.split(':')
    invoice_info = await CrystalPayClient().get_invoice_info(invoice_id)
    invoice_status = translate_crystalpay_type(invoice_info.get("state"))
    await call.answer(invoice_status, show_alert=True)
    await delete_user_invoice(call.from_user.id)
