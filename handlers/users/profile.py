import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link

from database.connections import get_user_info, get_bot_configs, get_user_history, clear_user_history, add_user_invoice, \
    delete_user_invoice
from handlers.users.users import start_command
from keyboards.default.user_btn import cancel_btn, remove_btn, start_menu_btn
from keyboards.inline.user_btn import payment_btn, user_profile_btn, cancel_inline_btn, show_history_btn
from services.nicepay import NicepayInvoiceCreator
from states.all_states import UserStates
from utils.bot_context import *
from loader import bot
from utils.misc.payment_invoice import create_user_invoice
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
        await call.message.delete()
        btn = await cancel_btn()
        bot_configs = await get_bot_configs()
        bot_configs = bot_configs[-1]['min_sum']
        await call.message.answer(depozite_text.format(bot_configs), reply_markup=btn)
        await state.set_state(UserStates.depozit)
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
    # invoice_url, bill_id = await create_user_invoice(int(text))
    invoice = await NicepayInvoiceCreator().create_invoice(
        order_id=str(user_id),
        customer=str(user_id),
        amount=int(text),
    )
    await add_user_invoice(user_id, invoice.get("payment_id"))
    btn = remove_btn
    await message.answer("⌛️", reply_markup=btn)
    await asyncio.sleep(.5)
    btn = await payment_btn(invoice.get("link"))
    await bot.delete_message(user_id, message_id=message.message_id + 1)
    await message.answer(f"✅ Ссылка для оплаты создан <em>(у вас 15 минут чтобы перевести {text}руб.)</em>", reply_markup=btn)
    await state.clear()


@router.callback_query(F.data == "cancel_invoice")
async def cancel_invoice_handler(call: CallbackQuery):
    await call.answer("Процесс оплаты отменен!", show_alert=True)
    await call.message.delete()
    btn = await start_menu_btn()
    await call.message.answer(start_text, reply_markup=btn)
    await delete_user_invoice(call.from_user.id)
