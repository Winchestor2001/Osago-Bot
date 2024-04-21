import asyncio

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import *

from data.config import BOT_CHANNEL_ID
from database.connections import add_user, check_user, get_user_info, get_user_history, clear_user_history, \
    save_user_invoice, delete_user_payment_by_id, get_ref_sum, update_user_balance, update_unique_referal
from keyboards.any_btns.user_btns import from_link_btn, start_menu_btn, user_profile_btn, services_btn, channel_btn, \
    show_history_btn, remove_btn, cancel_btn, payment_btn
from loader import dp, bot
from bot_context import *
from states.AllStates import UserStates
from utils.misc.qiwi_invoice import create_user_invoice
from aiogram.utils.deep_linking import get_start_link


async def bot_start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    check = await check_user(user_id)
    args = message.get_args()
    if check and args != user_id:
        await state.update_data(referer=args)
    if check:
        btn = await from_link_btn()
        await message.answer(f"<b>Откуда вы узнали про нас?</b>", reply_markup=btn)
    else:
        is_subscribe = await bot.get_chat_member(BOT_CHANNEL_ID, user_id)
        if is_subscribe.status != 'left':
            btn = await start_menu_btn()
            await message.answer(start_text, reply_markup=btn)
        else:
            btn = await channel_btn()
            await message.answer("Подпишитесь на наш канал👇", reply_markup=btn)


async def from_link_callback(c: CallbackQuery, state: FSMContext):
    user_id = c.from_user.id
    username = c.from_user.username
    cd = c.data.split(":")[1]
    await add_user(user_id, cd, username)
    await c.message.delete()
    btn = await start_menu_btn()
    await c.message.answer(start_text, reply_markup=btn)
    data = await state.get_data()
    if 'referer' in data.keys():
        if len(data['referer']) < 30:
            ref_sum = await get_ref_sum()
            await update_user_balance(int(data['referer']), ref_sum['ref_sum'], incriment=True)
            await bot.send_message(data['referer'], f"Вам начилсено реферальный бонус {ref_sum['ref_sum']}руб.")
        else:
            await update_unique_referal(data['referer'])


async def check_subscribe_callback(c: CallbackQuery):
    user_id = c.from_user.id
    is_subscribe = await bot.get_chat_member(BOT_CHANNEL_ID, user_id)
    if is_subscribe.status != 'left':
        btn = await start_menu_btn()
        await c.message.delete()
        await c.message.answer(start_text, reply_markup=btn)
    else:
        await c.answer("Подпишитесь на наш канал👇", show_alert=True)


async def user_profile_handler(message: Message):
    user_id = message.from_user.id
    ref_link = await get_start_link(user_id)
    user = await get_user_info(user_id)
    btn = await user_profile_btn(user_id)
    context = f"👤 Ваш Профиль\n\n" \
              f"🆔 ID: {user_id}\n" \
              f"💰 Баланс: {user[0]['user_balance']} руб.\n\n" \
              f"Реф.ссылка: {ref_link}"
    await message.answer(context, reply_markup=btn, disable_web_page_preview=True)


async def services_handler(message: Message):
    btn = await services_btn()
    await message.answer("🌐 Наши услуги", reply_markup=btn)


async def support_handler(message: Message):
    await message.answer(support_text)


async def channel_link_handler(message: Message):
    await message.answer(channel_text)


async def back_callback(c: CallbackQuery):
    await c.answer()
    btn = await services_btn()
    await c.message.edit_text("🌐 Наши услуги", reply_markup=btn)


async def show_user_history_callback(c: CallbackQuery):
    user_id = c.from_user.id
    history = await get_user_history(user_id)
    if len(history) != 0:
        context = '🧰 Вашы заказа:\n\n'
        for item in history:
            context += f"{item['order_name']} | {item['price']}руб | {item['date']}\n"

        btn = await show_history_btn()
        await c.message.edit_text(context, reply_markup=btn)
    else:
        await c.answer("История заказов пуст")


async def clear_user_history_callback(c: CallbackQuery):
    user_id = c.from_user.id
    ref_link = await get_start_link(user_id)
    await clear_user_history(user_id)
    await c.answer("История очищена")
    user = await get_user_info(user_id)
    btn = await user_profile_btn(user_id)
    context = f"👤 Ваш Профиль\n\n" \
              f"🆔 ID: {user_id}\n" \
              f"💰 Баланс: {user[0]['user_balance']} руб.\n\n" \
              f"Реф.ссылка: {ref_link}"
    await c.message.edit_text(context, reply_markup=btn)


async def back_to_profile_callback(c: CallbackQuery):
    user_id = c.from_user.id
    ref_link = await get_start_link(user_id)
    user = await get_user_info(user_id)
    btn = await user_profile_btn(user_id)
    context = f"👤 Ваш Профиль\n\n" \
              f"🆔 ID: {user_id}\n" \
              f"💰 Баланс: {user[0]['user_balance']} руб.\n\n" \
              f"Реф.ссылка: {ref_link}"
    await c.message.edit_text(context, reply_markup=btn)


async def user_depozite_callback(c: CallbackQuery):
    btn = await cancel_btn()
    await c.answer()
    await c.message.delete()
    await c.message.answer(depozite_text, reply_markup=btn)
    await UserStates.depozit.set()


async def user_depozite_state(message: Message, state: FSMContext):
    text = message.text
    user_id = message.from_user.id
    btn = await remove_btn()
    if text in ['❌ Отменить', '/start', '/menu', '/cancel']:
        await message.answer("Процесс отменен", reply_markup=btn)
        await state.finish()
        return
    if text.isdigit():
        invoice = await create_user_invoice(int(text))
        await save_user_invoice(user_id, invoice[1])
        await message.answer("Минутку....", reply_markup=btn)
        await asyncio.sleep(1.5)
        btn = await payment_btn(invoice[0])
        await bot.delete_message(user_id, message_id=message.message_id + 1)
        await message.answer(f"✅ Ссылка для оплаты создан <em>(у вас 15 минут чтобы перевести {text}руб.)</em>", reply_markup=btn)
        await state.finish()
    else:
        await message.answer(error_text)


async def cancel_invoice_callback(c: CallbackQuery):
    user_id = c.from_user.id
    await c.message.delete()
    await c.answer("Процесс оплаты отменен!", show_alert=True)
    await delete_user_payment_by_id(user_id)


def register_users_py(dp: Dispatcher):
    dp.register_message_handler(bot_start_handler, commands=['start', 'menu', 'cancel'])
    dp.register_message_handler(support_handler, text='☎️ Обратная связь')
    dp.register_message_handler(channel_link_handler, text='💥Телеграм канал')
    dp.register_message_handler(user_profile_handler, text='👤 Профиль')
    dp.register_message_handler(services_handler, text='📂 Наши услуги')

    dp.register_message_handler(user_depozite_state, state=UserStates.depozit)

    dp.register_callback_query_handler(from_link_callback, text_contains='from:')
    dp.register_callback_query_handler(check_subscribe_callback, text='subscribed')
    dp.register_callback_query_handler(back_callback, text='back')
    dp.register_callback_query_handler(show_user_history_callback, text='user_history')
    dp.register_callback_query_handler(back_to_profile_callback, text='back_profile')
    dp.register_callback_query_handler(clear_user_history_callback, text='clear_history')
    dp.register_callback_query_handler(user_depozite_callback, text='depozit')
    dp.register_callback_query_handler(cancel_invoice_callback, text='cancel_invoice')
