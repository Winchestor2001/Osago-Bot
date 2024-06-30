import asyncio
import sys
import uuid

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import *

from bot_context import success_order_text
from database.connections import get_all_admins, update_user_balance, count_users, edited_product_price, \
    get_all_bot_configs, update_qiwi_token, get_all_users_for_mailing, add_admin, del_admin, get_user_info, \
    save_unique_link, get_unique_link, update_ref_sum, get_ref_sum, delete_user_payment_bill
from keyboards.any_btns.admin_btns import admin_menu_btn, products_btn
from keyboards.any_btns.user_btns import remove_btn, cancel_btn
from loader import dp, bot
from states.AllStates import AdminStates
from aiogram.utils.deep_linking import get_start_link


async def admin_start(message: Message):
    user_id = message.from_user.id
    admins = await get_all_admins()
    if user_id in admins:
        users, yandex, google, telegram, whatsapp, vkontakte, friend = await count_users()
        ref_sum = await get_ref_sum()
        btn = await admin_menu_btn()
        await message.answer(f"Юзеры: {users}чел.\n\n"
                             f"Реф.бонус: {ref_sum['ref_sum']}руб\n"
                             f"Yandex: {yandex}чел.\n"
                             f"Google: {google}чел.\n"
                             f"Telegram: {telegram}чел.\n"
                             f"WhatsApp: {whatsapp}чел.\n"
                             f"Vkontakte: {vkontakte}чел.\n"
                             f"От друга: {friend}чел.", reply_markup=btn)


async def admin_send_orders_handler(message: Message):
    admins = await get_all_admins()
    user_id = message.from_user.id
    if user_id in admins:
        content_type = message.content_type
        caption = message.caption
        if content_type == 'document' and not caption is None:
            await bot.send_document(chat_id=int(caption), document=message.document.file_id, caption=success_order_text)
        elif content_type == 'photo' and not caption is None:
            await bot.send_photo(chat_id=int(caption), photo=message.photo[-1].file_id, caption=success_order_text)

        for admin in admins:
            await bot.send_message(admin, f"✅ Отправлено. <code>{caption}</code>")


async def admin_update_user_balance(message: Message):
    admins = await get_all_admins()
    user_id = message.from_user.id
    text = message.text.split()
    if user_id in admins and len(text) == 3:
        await update_user_balance(user_id=int(text[1]), value=int(text[2]), sett=True)
        await message.answer("Баланс изменен!")


async def admin_get_user_info(message: Message):
    admins = await get_all_admins()
    user_id = message.from_user.id
    text = message.text.split()
    if user_id in admins and len(text) == 2:
        user = await get_user_info(int(text[1]))
        await message.answer(f"ID: <code>{user[0]['user_id']}</code>\n"
                             f"Баланс: {user[0]['user_balance']}руб.")


async def add_admin_handler(message: Message):
    admins = await get_all_admins()
    user_id = message.from_user.id
    text = message.text.split()
    if user_id in admins:
        if len(text) == 2 and text[1].isdigit():
            await add_admin(int(text[1]))
            await message.answer("Админ добавлен!")


async def del_admin_handler(message: Message):
    admins = await get_all_admins()
    user_id = message.from_user.id
    if user_id in admins:
        text = message.text.split()
        if len(text) == 2 and text[1].isdigit():
            await del_admin(int(text[1]))
            await message.answer("Админ удален!")


async def back_to_admin_callback(c: CallbackQuery):
    users, yandex, google, telegram, whatsapp, vkontakte, friend = await count_users()
    btn = await admin_menu_btn()
    await c.message.edit_text(f"Юзеры: {users}чел.\n\n"
                              f"Yandex: {yandex}чел.\n"
                              f"Google: {google}чел.\n"
                              f"Telegram: {telegram}чел.\n"
                              f"WhatsApp: {whatsapp}чел.\n"
                              f"Vkontakte: {vkontakte}чел.\n"
                              f"От друга: {friend}чел.", reply_markup=btn)


async def update_products_price_callback(c: CallbackQuery):
    btn = await products_btn()
    await c.message.edit_text("Все услуги:", reply_markup=btn)


async def select_product_price_callback(c: CallbackQuery, state: FSMContext):
    cd = c.data.split(":")[1]
    await state.set_data({'slug': cd})
    btn = await cancel_btn()
    await c.message.delete()
    await c.message.answer("Введите сумму:", reply_markup=btn)
    await AdminStates.update_product_price.set()


async def select_product_price_state(message: Message, state: FSMContext):
    text = message.text
    btn = await remove_btn()
    if text == '❌ Отменить':
        await message.answer("❌ Отменино", reply_markup=btn)
        btn = await products_btn()
        await message.answer("Все услуги:", reply_markup=btn)
        await state.finish()
        return
    if text.isdigit():
        slug = await state.get_data()
        await edited_product_price(slug['slug'], text)
        await message.answer('Сохранено', reply_markup=btn)
        btn = await products_btn()
        await message.answer("Все услуги:", reply_markup=btn)
        await state.finish()
    else:
        await message.answer("Введите цифру")

async def edit_qiwi_configs_state(message: Message, state: FSMContext):
    text = message.text
    btn = await remove_btn()
    if text == '❌ Отменить':
        await message.answer("Процесс отменен", reply_markup=btn)
        await state.finish()
        return

    await update_qiwi_token(text)
    await message.answer("✅ Qiwi Токен изменен!", reply_markup=btn)
    users, yandex, google, telegram, whatsapp, vkontakte, friend = await count_users()
    qiwi_info = await get_all_bot_configs()
    btn = await admin_menu_btn()
    await message.answer(f"Юзеры: {users}чел.\n\n"
                         f"Yandex: {yandex}чел.\n"
                         f"Google: {google}чел.\n"
                         f"Telegram: {telegram}чел.\n"
                         f"WhatsApp: {whatsapp}чел.\n"
                         f"Vkontakte: {vkontakte}чел.\n"
                         f"От друга: {friend}чел.\n\n"
                         f"QIWI TOKEN:\n<code>{qiwi_info[0]['qiwi_token']}</code>", reply_markup=btn)
    await state.finish()


async def show_all_admins(c: CallbackQuery):
    admins = await get_all_admins()
    context = "Админы:\n\n"
    for n, admin in enumerate(admins, start=1):
        context += f"<a href='tg://user?id={admin}'>{n}-Admin</a>\n"
    btn = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_admin"))
    await c.message.edit_text(context, reply_markup=btn)


async def mailing_callback(c: CallbackQuery):
    btn = await cancel_btn()
    await c.message.delete()
    await c.message.answer("Отправьте сообщения для рассылки:", reply_markup=btn)
    await AdminStates.sending_to_users.set()


async def mailing_state(message: Message, state: FSMContext):
    users = await get_all_users_for_mailing()
    user_id = message.from_user.id
    text_type = message.content_type
    text = message.text
    text_caption = message.caption
    rep_btn = message.reply_markup
    sends = 0
    sends_error = 0
    btn = await remove_btn()

    if text == '❌ Отменить':
        await message.answer("Процесс отменен", reply_markup=btn)
        await state.finish()
        return

    await message.answer("Отправка начился....", reply_markup=btn)
    await state.finish()
    for u in users:
        try:
            if text_type == 'text':
                await bot.send_message(u['user_id'], text, reply_markup=rep_btn)
                sends += 1
                await asyncio.sleep(0.03)

            elif text_type == "photo":
                await bot.send_photo(u['user_id'], message.photo[-1].file_id, caption=text_caption,
                                     reply_markup=rep_btn)
                sends += 1
                await asyncio.sleep(0.03)

            elif text_type == "video":
                await bot.send_video(u['user_id'], message.video.file_id, caption=text_caption, reply_markup=rep_btn)
                sends += 1
                await asyncio.sleep(0.03)

            elif text_type == "document":
                await bot.send_document(u['user_id'], message.document.file_id, caption=text_caption,
                                        reply_markup=rep_btn)
                sends += 1
                await asyncio.sleep(0.03)

            elif text_type == "animation":
                await bot.send_animation(u['user_id'], message.animation.file_id, caption=text_caption,
                                         reply_markup=rep_btn)
                sends += 1
                await asyncio.sleep(0.03)


        except Exception as ex:
            # print(f'{type(ex).__name__}: {ex} | Line: {sys.exc_info()[-1].tb_lineno} ****** {ex}')
            sends_error += 1
            continue

    if sends == 0:
        await bot.send_message(user_id, "⚠️ Сообщение не дошло никому")
    else:
        await bot.send_message(user_id,
                               f"Рассылка отправлено: <b>{sends + sends_error}</b> юзерам\n"
                               f"Активных юзеров: <b>{sends}</b>\n"
                               f"Не активных юзеров: <b>{sends_error}</b>")


async def make_unique_link_command(message: Message):
    text = message.text.split()
    user_id = message.from_user.id
    admins = await get_all_admins()
    if len(text) == 2 and user_id in admins:
        unique_link = str(uuid.uuid4().hex)
        await save_unique_link(unique_link, text[1])
        ref_link = await get_start_link(unique_link)
        await message.answer(f"Уникальная реф.ссылка: {ref_link}\n\n"
                             f"Для статистики: /ref_stat <code>{unique_link}</code>")


async def get_ref_stat_command(message: Message):
    text = message.text.split()
    user_id = message.from_user.id
    admins = await get_all_admins()
    if len(text) == 2 and user_id in admins:
        total_refs = await get_unique_link(text[1])
        if total_refs:
            ref_link = await get_start_link(total_refs[0]['referal_id'])
            context = f"{total_refs[0]['referer']} позвал {total_refs[0]['referals']} человек\n\n" \
                      f"Уникальная реф.ссылка: {ref_link}"
        else:
            context = "Неверные данные указали..."
        await message.reply(context)


async def set_ref_sum_command(message: Message):
    text = message.text.split()
    user_id = message.from_user.id
    admins = await get_all_admins()
    if len(text) == 2 and user_id in admins:
        await update_ref_sum(float(text[1]))
        await message.answer("Реф. бонус изменен.")


async def delelte_payment_invoice_command(message: Message):
    text = message.text.split()
    user_id = message.from_user.id
    admins = await get_all_admins()
    if user_id in admins:
        await delete_user_payment_bill(text[-1])
        await message.answer(f"Payment invoicec: <code>{text[-1]}</code> deleted!")


def register_admins_py(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=['admin'])
    dp.register_message_handler(make_unique_link_command, commands=['ref_link'])
    dp.register_message_handler(get_ref_stat_command, commands=['ref_stat'])
    dp.register_message_handler(set_ref_sum_command, commands=['ref_sum'])
    dp.register_message_handler(admin_update_user_balance, regexp='/money')
    dp.register_message_handler(admin_get_user_info, regexp='/info')
    dp.register_message_handler(add_admin_handler, regexp='/addadmin')
    dp.register_message_handler(del_admin_handler, regexp='/deladmin')
    dp.register_message_handler(delelte_payment_invoice_command, regexp='/delbill')
    dp.register_message_handler(admin_send_orders_handler, content_types=['document', 'photo'])

    dp.register_message_handler(select_product_price_state, content_types=['text'],
                                state=AdminStates.update_product_price)
    dp.register_message_handler(mailing_state, content_types=ContentType.ANY, state=AdminStates.sending_to_users)

    dp.register_callback_query_handler(update_products_price_callback, text='change_prices')
    dp.register_callback_query_handler(back_to_admin_callback, text='back_to_admin')
    dp.register_callback_query_handler(select_product_price_callback, text_contains='edit_price:')
    dp.register_callback_query_handler(show_all_admins, text='all_admins')
    dp.register_callback_query_handler(mailing_callback, text='sending_all')
