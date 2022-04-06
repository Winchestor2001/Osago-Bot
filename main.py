import datetime
import sys

import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message, BotCommand, InputMediaPhoto
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

import asyncio

from config import bot_token, from_links, osago_data_list, bot_admins, dk_data_list, med_auto_data_list, \
    kasko_bank_data_list
from models import MainDB
from keyboards import menu, user_from_btn, buy_osago_btn, cencel_btn, remove, pay_btn, send_order_btn, \
    service_products_btn, user_profile_btn, history_back_btn, buy_Dk, med_auto_btn, kasko_bank_btn, karta_gibdd_btn, \
    karta_vu_gai_btn, poisk_solariy_btn, admin_panel_btn, change_service_products_btn

from pyqiwip2p import QiwiP2P



logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=bot_token, parse_mode='html')
dp = Dispatcher(bot, storage=storage)
db = MainDB()
db.createTable()
product_row = []




class MyStates(StatesGroup):
    osago_data = State()
    depozit = State()
    dk_data = State()
    dk_photo_1 = State()
    dk_photo_2 = State()
    dk_photo_3 = State()
    dk_photo_4 = State()
    med_auto = State()
    kasko_bank = State()
    karta_gibdd = State()
    karta_vu_gai = State()
    poisk_solariy = State()
    sending_to_users = State()
    default_text_handler = State()
    update_qiwi_data = State()
    update_product_price = State()




@dp.callback_query_handler(lambda c: True)
async def queryCallBackFunc(c):
    user_id = c.from_user.id
    msg = c.message.chat.id
    cd = c.data
    back_btn = types.InlineKeyboardButton("🔙 Назад", callback_data="back")
    if cd in from_links:
        db.addUser(user_id, cd)

        await bot.answer_callback_query(c.id)
        await bot.delete_message(msg, c.message.message_id)
        await bot.send_message(msg, f"<b>🙋‍♀️Привет дорогой друг!</b>\n"
                                        f"<b>Меня зовут Осаго Макс</b>\n\n"
                                        f"Я был создан, чтобы помочь тебе оформить Электронный осаго и диагностические карты  на твой автомобиль.\n\n"
                                        f"<em>Обещаю не занимать у тебя много времени, <b>время</b> = <b>деньги</b>, поэтому все будет очень просто, быстро и максимально понятно.</em>\n\n"
                                        f"⏳Заказы обрабатываются: <b>с 09:00 до 22:00 по Московскому времени, а принимаются 24/7</b>\n\n"
                                        f"Выбери нужный пункт из меню и я с радостью тебе помогу😌", reply_markup=menu)


    elif cd == 'back':
        await bot.answer_callback_query(c.id)
        await bot.edit_message_text(
            chat_id=msg,
            message_id=c.message.message_id,
            text=f"🌐 Наши услуги",
            reply_markup=service_products_btn
        )


    elif cd == 'back_to_admin_panel':
        qiwi_data = db.getQiwiConfig()
        await bot.answer_callback_query(c.id)
        text = f"<b>👤 Админ Панель:</b>\n\n" \
               f"<b>Статистика бота:</b> <em>{db.getBotUsers()[0]}</em> человек\n" \
               f"<b>Qiwi Номер:</b> <code>{qiwi_data[0]}</code>\n" \
               f"<b>Qiwi Токен:</b> <code>{qiwi_data[1]}</code>"
        await bot.edit_message_text(
            chat_id=msg,
            message_id=c.message.message_id,
            text=text,
            reply_markup=admin_panel_btn
        )


    elif cd == 'back_to_profile':
        await bot.answer_callback_query(c.id)
        user_info = db.getUserInfo(user_id)
        text = f"🆔 ID: {user_id}\n" \
               f"💰 Баланс: {user_info[1]} руб."
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=c.message.message_id,
            text=f"👤 Ваш Профиль\n\n{text}",
            reply_markup=user_profile_btn)


    elif cd == 'myHistory':
        try:
            userHistory = db.getUserHistory(user_id)
            if userHistory != []:
                history = ''
                for his in userHistory:
                    ord = his[1]
                    pri = his[2]
                    dat = his[3]
                    tot = f"<b>{ord}</b> - <code>{pri}</code> - {dat}\n"
                    history += tot
                await bot.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text=f"🧰 Вашы заказа:\n\n{history}",
                    reply_markup=history_back_btn
                )
            else:
                await bot.answer_callback_query(c.id, "😦У вас еще нет покупок!", show_alert=True)


        except Exception as ex:
            await bot.answer_callback_query(c.id, "😦У вас еще нет покупок!", show_alert=True)


    elif cd == 'clear_history':
        db.clearHistory(user_id)
        await bot.answer_callback_query(c.id, 'История очищена!', show_alert=True)
        user_info = db.getUserInfo(user_id)
        text = f"🆔 ID: {user_id}\n" \
               f"💰 Баланс: {user_info[1]} руб."
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=c.message.message_id,
            text=f"👤 Ваш Профиль\n\n{text}",
            reply_markup=user_profile_btn)


    elif cd == 'depozit':
        await bot.answer_callback_query(c.id)
        await MyStates.depozit.set()
        await bot.send_message(user_id, f"✍️ Введите сумму <em>(минимум 100 руб.)</em>:", reply_markup=cencel_btn)


    elif cd == "check_pay":
        p2p = QiwiP2P(auth_key=db.getQiwiConfig()[1])
        bill_id = db.checkPayment(user_id)
        user_info = db.getUserInfo(user_id)

        if p2p.check(bill_id).status == "PAID":
            await bot.edit_message_text(
                chat_id=user_id,
                message_id=c.message.message_id,
                text=f"✅ Ваш баланс пополнен на сумму: {user_info[3]}₽")

            db.updateUserBalance(user_id, item='user_balance', value=f'user_balance+{user_info[3]}')

        elif p2p.check(bill_id).status == "WAITING":
            await bot.answer_callback_query(c.id, f"⚠️ Вы еще не перевели {user_info[3]} руб.", show_alert=True)


        elif p2p.check(bill_id).status == "EXPIRED":
            await bot.answer_callback_query(c.id, f"🗑 Ссылка просрочен", show_alert=True)
            await bot.delete_message(c.message.chat.id, c.message.message_id)



    elif cd == 'osago_data_send_to_admin':
        user_info = db.getUserInfo(user_id)
        order_info = db.getAllUserOrderProduct(user_id, user_info[6])
        db.updateUserHistory(user_id, user_info[4], user_info[5])
        db.updateUserInfo(user_id, 'user_balance', round(int(user_info[1]) - int(user_info[5]), 2))
        db_admins = db.getAdminsId()
        all_admins = []
        if not db_admins is None:
            for adm in bot_admins:
                all_admins.append(adm)
            for adm in db_admins:
                all_admins.append(adm[0])
        else:
            for adm in bot_admins:
                all_admins.append(adm)

        userLink = f"<a href='tg://user?id={order_info[0]}'>USER</a>"

        sending_text = f"<b>├ ФИО СТРАХОВАТЕЛЯ:</b> <em>{order_info[1]}</em>\n" \
                        f"<b>├ ФИО СОБСТВЕННИКА:</b> <em>{order_info[2]}</em>\n" \
                        f"<b>├ МАРКА/МОДЕЛЬ АВТО:</b> <em>{order_info[3]}</em>\n" \
                        f"<b>├ VIN НОМЕР/РАМА/КУЗОВ:</b> <em>{order_info[4]}</em>\n" \
                        f"<b>├ НОМЕР ПТС:</b> <em>{order_info[5]}</em>\n" \
                        f"<b>├ НОМЕР АВТО:</b> <em>{order_info[6]}</em>\n" \
                        f"<b>├ ПАСПОРТ ДАННЫЕ:</b> <em>{order_info[7]}</em>\n\n" \
                        f"<b>ID:</b> <code>{user_id}</code>\n" \
                        f"<b>ТАРИФ:</b> <em>{user_info[4]}</em>\n\n" \
                        f"Для отправки заказа, Отправьте файл с caption ID"

        await bot.delete_message(user_id, c.message.message_id)
        await bot.send_message(user_id, f'✅ <em>Скоро мы отправим ваш заказ!</em>', reply_markup=menu)
        try:
            for sending in all_admins:
                await bot.send_message(sending, f"{userLink}\n\n"
                                                f"{sending_text}")
                await asyncio.sleep(0.03)
        except Exception as ex:
            print(ex)


    elif cd == 'dk_data_send_to_admin':
        user_info = db.getUserInfo(user_id)
        order_info = db.getAllUserOrderProduct(user_id, user_info[6])
        db.updateUserHistory(user_id, user_info[4], user_info[5])
        db.updateUserInfo(user_id, 'user_balance', round(int(user_info[1]) - int(user_info[5]), 2))
        db_admins = db.getAdminsId()
        all_admins = []
        if not db_admins is None:
            for adm in bot_admins:
                all_admins.append(adm)
            for adm in db_admins:
                all_admins.append(adm[0])
        else:
            for adm in bot_admins:
                all_admins.append(adm)

        userLink = f"<a href='tg://user?id={order_info[0]}'>USER</a>"

        await bot.delete_message(user_id, c.message.message_id)
        for i in range(1, 5):
            await bot.delete_message(user_id, c.message.message_id - i)
        await bot.send_message(user_id, f'✅ <em>Скоро мы отправим ваш заказ!</em>', reply_markup=menu)
        try:
            for sending in all_admins:
                pics = db.getDkData(user_id)
                text = f"{userLink}\n\n"\
                       f"├<b>ФИО:</b> <em>{pics[1]}</em>\n" \
                       f'├Примерный пробег: <em>{pics[2]}</em>\n' \
                       f'├Марка шин: <em>{pics[3]}</em>\n' \
                       f'├Тип топлива: <em>{pics[4]}</em>\n\n' \
                       f"<b>ID:</b> <code>{user_id}</code>\n" \
                       f"<b>ТАРИФ:</b> <em>{user_info[4]}</em>\n\n" \
                       f"Для отправки заказа, Отправьте файл с caption ID"
                media_group = [InputMediaPhoto(pics[5], caption=text, parse_mode='html'), InputMediaPhoto(pics[6]),
                               InputMediaPhoto(pics[7]), InputMediaPhoto(pics[8])]
                await bot.send_media_group(sending, media_group)
                await asyncio.sleep(0.03)
        except Exception as ex:
            print(ex)


    elif cd == 'med_auto_send_to_admin':
        user_info = db.getUserInfo(user_id)
        order_info = db.getAllUserOrderProduct(user_id, user_info[6])
        db.updateUserHistory(user_id, user_info[4], user_info[5])
        db.updateUserInfo(user_id, 'user_balance', round(int(user_info[1]) - int(user_info[5]), 2))
        db_admins = db.getAdminsId()
        all_admins = []
        if not db_admins is None:
            for adm in bot_admins:
                all_admins.append(adm)
            for adm in db_admins:
                all_admins.append(adm[0])
        else:
            for adm in bot_admins:
                all_admins.append(adm)

        userLink = f"<a href='tg://user?id={order_info[0]}'>USER</a>"

        sending_text = f"<b>├ ФИО:</b> <em>{order_info[1]}</em>\n" \
                           f"<b>├ Дата рож-ния:</b> <em>{order_info[2]}</em>\n" \
                           f"<b>├ Серия номер паспорта:</b> <em>{order_info[3]}</em>\n" \
                           f"<b>├ Кем когда выдан:</b> <em>{order_info[4]}</em>\n" \
                           f"<b>├ Категория прав (B, C, D):</b> <em>{order_info[5]}</em>\n" \
                           f"<b>ID:</b> <code>{user_id}</code>\n" \
                           f"<b>ТАРИФ:</b> <em>{user_info[4]}</em>\n\n" \
                           f"Для отправки заказа, Отправьте файл с caption ID"

        await bot.delete_message(user_id, c.message.message_id)
        await bot.send_message(user_id, f'✅ <em>Скоро мы отправим ваш заказ!</em>', reply_markup=menu)
        try:
            for sending in all_admins:
                await bot.send_message(sending, f"{userLink}\n\n"
                                                    f"{sending_text}")
                await asyncio.sleep(0.03)
        except Exception as ex:
            print(ex)


    elif cd == 'kasko_bank_send_to_admin':
        user_info = db.getUserInfo(user_id)
        order_info = db.getAllUserOrderProduct(user_id, user_info[6])
        db.updateUserHistory(user_id, user_info[4], user_info[5])
        db.updateUserInfo(user_id, 'user_balance', round(int(user_info[1]) - int(user_info[5]), 2))
        db_admins = db.getAdminsId()
        all_admins = []
        if not db_admins is None:
            for adm in bot_admins:
                all_admins.append(adm)
            for adm in db_admins:
                all_admins.append(adm[0])
        else:
            for adm in bot_admins:
                all_admins.append(adm)

        userLink = f"<a href='tg://user?id={order_info[0]}'>USER</a>"

        sending_text = f"<b>├ФИО:</b> {order_info[1]}\n" \
                           f"<b>├ДАТА РОЖДЕНИЯ:</b> {order_info[2]}\n" \
                           f"<b>├ВУ:</b> {order_info[3]}\n" \
                           f"<b>├СТАЖ ВОЖДЕНИЕ:</b> {order_info[4]}\n" \
                           f"<b>├ТС ДАННЫЕ:</b> {order_info[5]}\n" \
                           f'<b>├НАИМЕНОВАНИЕ БАНКА:</b> {order_info[6]}\n' \
                           f'<b>├ДЕЙСТВИТЕЛЬНАЯ СТОИМОСТЬ АВТОМОБИЛЯ:</b> {order_info[7]}\n' \
                           f'<b>├ТЕЛЕФОН НОМЕР:</b> {order_info[8]}\n\n' \
                           f"<b>ID:</b> <code>{user_id}</code>\n" \
                           f"<b>ТАРИФ:</b> <em>{user_info[4]}</em>\n\n" \
                           f"Для отправки заказа, Отправьте файл с caption ID"

        await bot.delete_message(user_id, c.message.message_id)
        await bot.send_message(user_id, f'✅ <em>Скоро мы отправим ваш заказ!</em>', reply_markup=menu)
        try:
            for sending in all_admins:
                await bot.send_message(sending, f"{userLink}\n\n"
                                                f"{sending_text}")
                await asyncio.sleep(0.03)
        except Exception as ex:
            print(ex)


    elif cd == 'karta_gibdd_send_to_admin':
        user_info = db.getUserInfo(user_id)
        order_info = db.getAllUserOrderProduct(user_id, user_info[6])
        db.updateUserHistory(user_id, user_info[4], user_info[5])
        db.updateUserInfo(user_id, 'user_balance', round(int(user_info[1]) - int(user_info[5]), 2))
        db_admins = db.getAdminsId()
        all_admins = []
        if not db_admins is None:
            for adm in bot_admins:
                all_admins.append(adm)
            for adm in db_admins:
                all_admins.append(adm[0])
        else:
            for adm in bot_admins:
                all_admins.append(adm)

        userLink = f"<a href='tg://user?id={order_info[0]}'>USER</a>"

        sending_text = f"<b>├Гос.Номер:</b> {order_info[1]}\n" \
                           f"<b>ID:</b> <code>{user_id}</code>\n" \
                           f"<b>ТАРИФ:</b> <em>{user_info[4]}</em>\n\n" \
                           f"Для отправки заказа, Отправьте файл с caption ID"

        await bot.delete_message(user_id, c.message.message_id)
        await bot.send_message(user_id, f'✅ <em>Скоро мы отправим ваш заказ!</em>', reply_markup=menu)
        try:
            for sending in all_admins:
                await bot.send_message(sending, f"{userLink}\n\n"
                                                    f"{sending_text}")
                await asyncio.sleep(0.03)
        except Exception as ex:
            print(ex)


    elif cd == 'karta_vu_gai_send_to_admin':
        user_info = db.getUserInfo(user_id)
        order_info = db.getAllUserOrderProduct(user_id, user_info[6])
        db.updateUserHistory(user_id, user_info[4], user_info[5])
        db.updateUserInfo(user_id, 'user_balance', round(int(user_info[1]) - int(user_info[5]), 2))
        db_admins = db.getAdminsId()
        all_admins = []
        if not db_admins is None:
            for adm in bot_admins:
                all_admins.append(adm)
            for adm in db_admins:
                all_admins.append(adm[0])
        else:
            for adm in bot_admins:
                all_admins.append(adm)

        userLink = f"<a href='tg://user?id={order_info[0]}'>USER</a>"

        sending_text = f"<b>ID:</b> <code>{user_id}</code>\n" \
                           f"<b>ТАРИФ:</b> <em>{user_info[4]}</em>\n\n" \
                           f"Для отправки заказа, Отправьте файл с caption ID"

        await bot.delete_message(user_id, c.message.message_id)
        await bot.send_message(user_id, f'✅ <em>Скоро мы отправим ваш заказ!</em>', reply_markup=menu)
        try:
            for sending in all_admins:
                await bot.send_photo(sending, order_info[1], caption=f"{userLink}\n\n"
                                                    f"{sending_text}")
                await asyncio.sleep(0.03)
        except Exception as ex:
            print(ex)


    elif cd == 'poisk_solariy_send_to_admin':
        user_info = db.getUserInfo(user_id)
        order_info = db.getAllUserOrderProduct(user_id, user_info[6])
        db.updateUserHistory(user_id, user_info[4], user_info[5])
        db.updateUserInfo(user_id, 'user_balance', round(int(user_info[1]) - int(user_info[5]), 2))
        db_admins = db.getAdminsId()
        all_admins = []
        if not db_admins is None:
            for adm in bot_admins:
                all_admins.append(adm)
            for adm in db_admins:
                all_admins.append(adm[0])
        else:
            for adm in bot_admins:
                all_admins.append(adm)

        userLink = f"<a href='tg://user?id={order_info[0]}'>USER</a>"

        sending_text = f"<b>├ФИО:</b> {order_info[1]}\n" \
                           f"<b>├ДАТА РОЖДЕНИЯ:</b> {order_info[2]}\n\n" \
                           f"<b>ID:</b> <code>{user_id}</code>\n" \
                           f"<b>ТАРИФ:</b> <em>{user_info[4]}</em>\n\n" \
                           f"Для отправки заказа, Отправьте файл с caption ID"

        await bot.delete_message(user_id, c.message.message_id)
        await bot.send_message(user_id, f'✅ <em>Скоро мы отправим ваш заказ!</em>', reply_markup=menu)
        try:
            for sending in all_admins:
                await bot.send_message(sending, f"{userLink}\n\n"
                                                    f"{sending_text}")
                await asyncio.sleep(0.03)
        except Exception as ex:
            print(ex)




# 1 category
    elif cd == "buy_osago":
        await bot.answer_callback_query(c.id)

        await bot.edit_message_text(
            chat_id=msg,
            message_id=c.message.message_id,
            text=f"<b>📑Электронный полис ОСАГО с занесением вашего VIN в базу РСА.</b>\n\n"
                 f"<b>Оформим ОСАГО для ЛЮБОГО УЧЕТА.</b>\n"
                 f"<em>Беларусь 🇧🇾 Армения 🇦🇲 Россия 🇷🇺  и тд.</em>\n\n"
                 f"<b>На любой вид транспорта:</b>\n"
                 f"<em>Мотоцикл 🏍 Автомобиль 🚙</em>\n"
                 f"<em>Трактор 🚜  Авто с прицепом 🚗</em>\n"
                 f"<em>Грузовой автомобиль 🚛</em>\n"
                 f"<em>А так же такси 🚕</em>\n\n"
                 f"<b>❗️Все Е-ОСАГО без выплат️ при ДТП</b>\n\n"
                 f"<em>⏳Сроки выполнения заказа от 30 мин до 2х часов при нормальной работе РСА, возможны задержки в зависимости от работы баз ЕАИСТО и РСА</em>\n\n"
                 f"<em>Свой заказ Вы получите по готовности прямо в боте. Мы гарантируем максимально возможную скорость и качество обработки ваших заказов</em>\n\n"
                 f"<em>🎁В качестве бонуса, абсолютно все полисы в бланке будут БЕЗ ОГРАНИЧЕНИЙ НА ИСПОЛЬЗОВАНИЕ ТС</em>",
            reply_markup=buy_osago_btn)


    elif cd == "buy_osago_year":
        product_info = db.getProductsInfo(rowid=1)
        user_info = db.getUserInfo(user_id)
        # print(user_info[1], product_info[1])
        if int(user_info[1]) >= int(product_info[1]):
            await MyStates.osago_data.set()
            db.updateOsagoData(user_id, item='price', value=product_info[1])
            db.updateUserInfo(user_id, 'now_product', product_info[0])
            db.updateUserInfo(user_id, 'now_price', product_info[1])

            await bot.answer_callback_query(c.id)
            await bot.delete_message(msg, c.message.message_id)
            await bot.send_message(
                chat_id=msg,
                text=f'<b>Для отмены нажмите</b> "Отменить"\n\n'
                     f'├ФИО СТРАХОВАТЕЛЯ\n'
                     f'├ФИО СОБСТВЕННИКА\n'
                     f'├МАРКА/МОДЕЛЬ АВТО\n'
                     f'├VIN НОМЕР/РАМА/КУЗОВ\n'
                     f'├НОМЕР ПТС\n'
                     f'├НОМЕР АВТО\n'
                     f'├ПАСПОРТ ДАННЫЕ\n\n'
                     f'<b>❗️ Отправьте все данные в таком порядке</b>:\n'
                     f'<em>Иванов Иван Иванович\n'
                     f'Иванов Юрий Иванович\n'
                     f'ГАЗ 33021\n'
                     f'XTЕ222210Y1766420 331210Y1776033 330530Y0051022\n'
                     f'71 MT 122911\n'
                     f'К777РВ77\n'
                     f'Иванов Иван Иванович\n'
                     f'10.02.1999\n'
                     f'15.02.2019\n'
                     f'36 18 619487</em>',
                reply_markup=cencel_btn
            )

        else:
            await bot.answer_callback_query(c.id, '❗️ У вас недостаточно средств', show_alert=True)


    elif cd == "buy_osago_month":
        user_info = db.getUserInfo(user_id)
        product_info = db.getProductsInfo(rowid=2)

        if int(user_info[1]) >= int(product_info[1]):
            await MyStates.osago_data.set()
            db.updateOsagoData(user_id, item='price', value=product_info[1])
            db.updateUserInfo(user_id, 'now_product', product_info[0])
            db.updateUserInfo(user_id, 'now_price', product_info[1])

            await bot.answer_callback_query(c.id)
            await bot.delete_message(msg, c.message.message_id)
            await bot.send_message(
                chat_id=msg,
                text=f'<b>Для отмены нажмите</b> "Отменить"\n\n'
                     f'├ФИО СТРАХОВАТЕЛЯ\n'
                     f'├ФИО СОБСТВЕННИКА\n'
                     f'├МАРКА/МОДЕЛЬ АВТО\n'
                     f'├VIN НОМЕР/РАМА/КУЗОВ\n'
                     f'├НОМЕР ПТС\n'
                     f'├НОМЕР АВТО\n'
                     f'├ПАСПОРТ ДАННЫЕ\n\n'
                    f'<b>❗️ Отправьте все данные в таком порядке</b>:\n'
                     f'<em>Иванов Иван Иванович\n'
                     f'Иванов Юрий Иванович\n'
                     f'ГАЗ 33021\n'
                     f'XTЕ222210Y1766420 331210Y1776033 330530Y0051022\n'
                     f'71 MT 122911\n'
                     f'К777РВ77\n'
                     f'Иванов Иван Иванович\n'
                     f'10.02.1999\n'
                     f'15.02.2019\n'
                     f'36 18 619487</em>',
                reply_markup=cencel_btn
            )

        else:
            await bot.answer_callback_query(c.id, '❗️ У вас недостаточно средств', show_alert=True)


    elif cd == "buy_osago_nodb":
        user_info = db.getUserInfo(user_id)
        product_info = db.getProductsInfo(rowid=3)

        if int(user_info[1]) >= int(product_info[1]):
            await MyStates.osago_data.set()
            db.updateOsagoData(user_id, item='price', value=product_info[1])
            db.updateUserInfo(user_id, 'now_product', product_info[0])
            db.updateUserInfo(user_id, 'now_price', product_info[1])

            await bot.answer_callback_query(c.id)
            await bot.delete_message(msg, c.message.message_id)
            await bot.send_message(
                chat_id=msg,
                text=f'<b>Для отмены нажмите</b> "Отменить"\n\n'
                     f'├ФИО СТРАХОВАТЕЛЯ\n'
                     f'├ФИО СОБСТВЕННИКА\n'
                     f'├МАРКА/МОДЕЛЬ АВТО\n'
                     f'├VIN НОМЕР/РАМА/КУЗОВ\n'
                     f'├НОМЕР ПТС\n'
                     f'├НОМЕР АВТО\n'
                     f'├ПАСПОРТ ДАННЫЕ\n\n'
                     f'<b>❗️ Отправьте все данные в таком порядке</b>:\n'
                     f'<em>Иванов Иван Иванович\n'
                     f'Иванов Юрий Иванович\n'
                     f'ГАЗ 33021\n'
                     f'XTЕ222210Y1766420 331210Y1776033 330530Y0051022\n'
                     f'71 MT 122911\n'
                     f'К777РВ77\n'
                     f'Иванов Иван Иванович\n'
                     f'10.02.1999\n'
                     f'15.02.2019\n'
                     f'36 18 619487</em>',
                reply_markup=cencel_btn
            )

        else:
            await bot.answer_callback_query(c.id, '❗️ У вас недостаточно средств', show_alert=True)

# 2 category
    elif cd == 'buy_dk':
        await bot.answer_callback_query(c.id)
        buy_Dk.inline_keyboard.clear()
        bd2 = types.InlineKeyboardButton(f"Диагностическая карта без базы 1 ГОД | {db.getProductsInfo(rowid=5)[1]} RUB",
                                         callback_data="buy_texosmotr_no_db")
        bd3 = types.InlineKeyboardButton(f"Диагностическая карта B | {db.getProductsInfo(rowid=6)[1]} RUB",
                                         callback_data="buy_texosmotr_b")
        bd4 = types.InlineKeyboardButton(f"Диагностическая карта C | {db.getProductsInfo(rowid=7)[1]} RUB",
                                         callback_data="buy_texosmotr_c")
        buy_Dk.add(bd2, bd3, bd4, back_btn)
        await bot.edit_message_text(
            chat_id=msg,
            message_id=c.message.message_id,
            text=f"<b>📑Диагностическая карта на любое авто. Оформление Техосмотр для ЮР, ФИЗ лиц и иностранных граждан.</b>\n\n"
                 f"<b>Любая категория авто (A, B, C, D, ПРИЦЕП)</b>\n"
                 f"<em>🚖Такси</em>\n"
                 f"<em>🚘Учебная машина</em>\n"
                 f"<em>⚠️Опасные грузы</em>\n\n\n"
                 f"<code>⏳Срок выполнения заказа до 1 часа.</code>",
            reply_markup=buy_Dk
        )


    # elif cd == 'buy_texosmotr':
    #     product_info = db.getProductsInfo(rowid=4)
    #     user_info = db.getUserInfo(user_id)
    #
    #     if int(user_info[1]) >= int(product_info[1]):
    #         db.updateDkData(user_id, item='price', value=product_info[1])
    #         db.updateUserInfo(user_id, 'now_product', product_info[0])
    #         db.updateUserInfo(user_id, 'now_price', product_info[1])
    #
    #         await MyStates.dk_data.set()
    #         await bot.answer_callback_query(c.id)
    #         await bot.delete_message(user_id, c.message.message_id)
    #         await bot.send_message(
    #             chat_id=user_id,
    #             text=f'<b>Для отмены нажмите</b> "Отменить"\n\n'
    #                  f"├ФИО\n"
    #                  f'├Примерный пробег\n'
    #                  f'├Марка шин\n'
    #                  f'├Тип топлива\n'
    #                  f'<b>❗️ Отправьте все данные в таком порядке</b>',
    #             reply_markup=cencel_btn
    #         )
    #     else:
    #         await bot.answer_callback_query(c.id, '❗️ У вас недостаточно средств', show_alert=True)


    elif cd == 'buy_texosmotr_no_db':
        product_info = db.getProductsInfo(rowid=5)
        user_info = db.getUserInfo(user_id)

        if int(user_info[1]) >= int(product_info[1]):
            db.updateDkData(user_id, item='price', value=product_info[1])
            db.updateUserInfo(user_id, 'now_product', product_info[0])
            db.updateUserInfo(user_id, 'now_price', product_info[1])

            await MyStates.dk_data.set()
            await bot.answer_callback_query(c.id)
            await bot.delete_message(user_id, c.message.message_id)
            await bot.send_message(
                chat_id=user_id,
                text=f'<b>Для отмены нажмите</b> "Отменить"\n\n'
                     f"├ФИО\n" 
                     f'├Примерный пробег\n'
                     f'├Марка шин\n'
                     f'├Тип топлива\n'
                     f'<b>❗️ Отправьте все данные в таком порядке</b>:\n'
                     f'<em>Иванов Иван Иванович\n'
                     f'251000\n'
                     f'Continental\n'
                     f'БЕНЗИН</em>',
                reply_markup=cencel_btn
            )
        else:
            await bot.answer_callback_query(c.id, '❗️ У вас недостаточно средств', show_alert=True)


    elif cd == 'buy_texosmotr_b':
        product_info = db.getProductsInfo(rowid=6)
        user_info = db.getUserInfo(user_id)

        if int(user_info[1]) >= int(product_info[1]):
            db.updateDkData(user_id, item='price', value=product_info[1])
            db.updateUserInfo(user_id, 'now_product', product_info[0])
            db.updateUserInfo(user_id, 'now_price', product_info[1])


            await MyStates.dk_data.set()
            await bot.answer_callback_query(c.id)
            await bot.delete_message(user_id, c.message.message_id)
            await bot.send_message(
                chat_id=user_id,
                text=f'<b>Для отмены нажмите</b> "Отменить"\n\n'
                     f"├ФИО\n" 
                     f'├Примерный пробег\n'
                     f'├Марка шин\n'
                     f'├Тип топлива\n'
                     f'<b>❗️ Отправьте все данные в таком порядке</b>:\n'
                     f'<em>Иванов Иван Иванович\n'
                     f'251000\n'
                     f'Continental\n'
                     f'БЕНЗИН</em>',
                reply_markup=cencel_btn
            )
        else:
            await bot.answer_callback_query(c.id, '❗️ У вас недостаточно средств', show_alert=True)


    elif cd == 'buy_texosmotr_c':
        product_info = db.getProductsInfo(rowid=7)
        user_info = db.getUserInfo(user_id)

        if int(user_info[1]) >= int(product_info[1]):
            db.updateDkData(user_id, item='price', value=product_info[1])
            db.updateUserInfo(user_id, 'now_product', product_info[0])
            db.updateUserInfo(user_id, 'now_price', product_info[1])

            await MyStates.dk_data.set()
            await bot.answer_callback_query(c.id)
            await bot.delete_message(user_id, c.message.message_id)
            await bot.send_message(
                chat_id=user_id,
                text=f'<b>Для отмены нажмите</b> "Отменить"\n\n'
                     f"├ФИО\n" 
                     f'├Примерный пробег\n'
                     f'├Марка шин\n'
                     f'├Тип топлива\n'
                     f'<b>❗️ Отправьте все данные в таком порядке</b>:\n'
                     f'<em>Иванов Иван Иванович\n'
                     f'251000\n'
                     f'Continental\n'
                     f'БЕНЗИН</em>',
                reply_markup=cencel_btn
            )
        else:
            await bot.answer_callback_query(c.id, '❗️ У вас недостаточно средств', show_alert=True)

# 3 category
    elif cd == 'medAuto':
        await bot.answer_callback_query(c.id)
        await bot.edit_message_text(
            chat_id=msg,
            message_id=c.message.message_id,
            text=f"📃Медицинские справки формы 003-В/у. Для получение/замены водительского удостоверения. Без необходимости посещения НД/ПНД. За 15 минут! Возможна отправка СДЭК по Москве, МО и в регионы!!!\n"
                 f"<b>Возможно продажа оптом, цена договорная!!!</b>\n\n"
                 f"<em>⏳Сроки выполнения заказа 24 часов</em>",
            reply_markup=med_auto_btn
        )


    elif cd == 'buy_med_auto':
        product_info = db.getProductsInfo(rowid=9)
        user_info = db.getUserInfo(user_id)
        med_auto_btn.inline_keyboard.clear()
        med_auto_btn.row(
            types.InlineKeyboardButton(f'Купить Мед Справку на права | {db.getProductsInfo(rowid=9)[1]} RUB',
                                       callback_data='buy_med_auto'))
        med_auto_btn.add(back_btn)

        if int(user_info[1]) >= int(product_info[1]):
            db.updateMedAutoData(user_id, item='price', value=product_info[1])
            db.updateUserInfo(user_id, 'now_product', product_info[0])
            db.updateUserInfo(user_id, 'now_price', product_info[1])

            await MyStates.med_auto.set()
            await bot.answer_callback_query(c.id)
            await bot.delete_message(user_id, c.message.message_id)
            await bot.send_message(
                chat_id=user_id,
                text=f'<b>Для отмены нажмите</b> "Отменить"\n\n'
                     f"├ФИО\n"
                     f'├Дата рож-ния\n'
                     f'├Серия номер паспорта\n'
                     f'├Кем когда выдан\n'
                     f'├Категория прав (B, C, D)\n'
                     f'<b>❗️ Отправьте все данные в таком порядке</b>',
                reply_markup=cencel_btn
            )
        else:
            await bot.answer_callback_query(c.id, '❗️ У вас недостаточно средств', show_alert=True)

# 4 category
    elif cd == 'kaskoBank':
        await bot.answer_callback_query(c.id)
        kasko_bank_btn.inline_keyboard.clear()
        kasko_bank_btn.row(types.InlineKeyboardButton(f'Купить КАСКО {db.getProductsInfo(rowid=8)[1]} RUB',
                                                      callback_data='buy_kasko_bank'))
        kasko_bank_btn.add(back_btn)
        await bot.edit_message_text(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            text=f"🏦Для оформления полиса.\n\n"
                 f"1)ФИО, дата рож-ния, серия номер паспорта, кем когда выдан, адрес регистрации, конт.номер телефона.\n"
                 f"2)Лица допущенные к управлению( если не без огранич.)ФИО, дата рождения, ВУ, стаж вождения. \n"
                 f"3)По ТС: марка, год выпуска, Vin, птс, гос номер, л.с, рмм.\n"
                 f"4)Наименование банка.\n"
                 f"5)Действительная стоимость автомобиля.\n\n"
                 f"<em>Телефон получателя и адрес отправка (сдек)</em>\n\n"
                 f"<em>⏳Сроки выполнения заказа от 1 до 3х суток</em>",
            reply_markup=kasko_bank_btn
        )


    elif cd == 'buy_kasko_bank':
        product_info = db.getProductsInfo(rowid=8)
        user_info = db.getUserInfo(user_id)

        if int(user_info[1]) >= int(product_info[1]):
            db.updateKaskoBankData(user_id, item='price', value=product_info[1])
            db.updateUserInfo(user_id, 'now_product', product_info[0])
            db.updateUserInfo(user_id, 'now_price', product_info[1])

            await MyStates.kasko_bank.set()
            await bot.answer_callback_query(c.id)
            await bot.delete_message(user_id, c.message.message_id)
            await bot.send_message(
                chat_id=user_id,
                text=f'<b>Для отмены нажмите</b> "Отменить"\n\n'
                     f"├ФИО\n"
                     f"├ДАТА РОЖДЕНИЯ\n"
                     f"├ВУ\n"
                     f"├СТАЖ ВОЖДЕНИЕ\n"
                     f"├ТС ДАННЫЕ\n"
                     f'├НАИМЕНОВАНИЕ БАНКА\n'
                     f'├ДЕЙСТВИТЕЛЬНАЯ СТОИМОСТЬ АВТОМОБИЛЯ\n'
                     f'├ТЕЛЕФОН НОМЕР\n\n'
                     f'<b>❗️ Отправьте все данные в таком порядке</b>:\n'
                     f'<em>Иванов Иван Иванович\n'
                     f'10.02.1999\n'
                     f'123123 2131\n'
                     f'3 лет\n'
                     f'71 MT 122911\n'
                     f'тинькофф\n'
                     f'5000000 руб\n'
                     f'+79633693636</em>',
                reply_markup=cencel_btn
            )
        else:
            await bot.answer_callback_query(c.id, '❗️ У вас недостаточно средств', show_alert=True)

# 5 category
    elif cd == 'kartaGibdd':
        karta_gibdd_btn.inline_keyboard.clear()
        karta_gibdd_btn.row(
            types.InlineKeyboardButton(f'Купить Карта учета ГИБДД {db.getProductsInfo(rowid=10)[1]} RUB',
                                       callback_data='buy_karta_gibdd'))
        karta_gibdd_btn.add(back_btn)
        await bot.edit_message_text(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            text=f"<b>Карта учёта гос номера</b>",
            reply_markup=karta_gibdd_btn
        )


    elif cd == 'buy_karta_gibdd':
        product_info = db.getProductsInfo(rowid=10)
        user_info = db.getUserInfo(user_id)
        karta_vu_gai_btn.inline_keyboard.clear()
        karta_vu_gai_btn.row(types.InlineKeyboardButton(f'Купить ВУ по базе ГАИ {db.getProductsInfo(rowid=11)[1]} RUB',
                                                        callback_data='buy_karta_vu_gai'))
        karta_vu_gai_btn.add(back_btn)

        if int(user_info[1]) >= int(product_info[1]):
            db.updateKartaGibddData(user_id, item='price', value=product_info[1])
            db.updateUserInfo(user_id, 'now_product', product_info[0])
            db.updateUserInfo(user_id, 'now_price', product_info[1])

            await MyStates.karta_gibdd.set()
            await bot.answer_callback_query(c.id)
            await bot.delete_message(user_id, c.message.message_id)
            await bot.send_message(
                chat_id=user_id,
                text=f'<b>Для отмены нажмите</b> "Отменить"\n\n'
                     f"├Введите Гос.Номер\n",
                reply_markup=cencel_btn
            )
        else:
            await bot.answer_callback_query(c.id, '❗️ У вас недостаточно средств', show_alert=True)

# 6 category
    elif cd == 'kartaVUgai':
        await bot.edit_message_text(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            text=f"<b>Карта ву фото прав</b>",
            reply_markup=karta_vu_gai_btn
        )


    elif cd == 'buy_karta_vu_gai':
        product_info = db.getProductsInfo(rowid=11)
        user_info = db.getUserInfo(user_id)

        if int(user_info[1]) >= int(product_info[1]):
            db.updateKartaVUGaiData(user_id, item='price', value=product_info[1])
            db.updateUserInfo(user_id, 'now_product', product_info[0])
            db.updateUserInfo(user_id, 'now_price', product_info[1])

            await MyStates.karta_vu_gai.set()
            await bot.answer_callback_query(c.id)
            await bot.delete_message(user_id, c.message.message_id)
            await bot.send_message(
                chat_id=user_id,
                text=f'<b>Для отмены нажмите</b> "Отменить"\n\n'
                     f"├Отправьте фото водительское права\n",
                reply_markup=cencel_btn
            )
        else:
            await bot.answer_callback_query(c.id, '❗️ У вас недостаточно средств', show_alert=True)

# 7 category
    elif cd == 'poiskSolariy':
        poisk_solariy_btn.inline_keyboard.clear()
        poisk_solariy_btn.row(
            types.InlineKeyboardButton(f'Купить Поиск по базе Солярис {db.getProductsInfo(rowid=12)[1]} RUB',
                                       callback_data='buy_poisk_solariy'))
        poisk_solariy_btn.add(back_btn)
        await bot.edit_message_text(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            text=f"<b>Солярис нужные данные: ФИО, ГОД РОЖДЕНИЯ</b>",
            reply_markup=poisk_solariy_btn
        )


    elif cd == 'buy_poisk_solariy':
        product_info = db.getProductsInfo(rowid=12)
        user_info = db.getUserInfo(user_id)

        if int(user_info[1]) >= int(product_info[1]):
            db.updatePoiskSolariyData(user_id, item='price', value=product_info[1])
            db.updateUserInfo(user_id, 'now_product', product_info[0])
            db.updateUserInfo(user_id, 'now_price', product_info[1])

            await MyStates.poisk_solariy.set()
            await bot.answer_callback_query(c.id)
            await bot.delete_message(user_id, c.message.message_id)
            await bot.send_message(
                chat_id=user_id,
                text=f'<b>Для отмены нажмите</b> "Отменить"\n\n'
                     f"├ФИО\n"
                     f"├ДАТА РОЖДЕНИЯ\n\n"
                     f'<b>❗️ Отправьте все данные в таком порядке</b>'
                     f'<em>Иванов Иван Иванович\n'
                     f'10.02.1999</em>',
                reply_markup=cencel_btn
            )
        else:
            await bot.answer_callback_query(c.id, '❗️ У вас недостаточно средств', show_alert=True)

# admin panel
    elif cd == 'change_prices':
        await bot.answer_callback_query(c.id)
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=c.message.message_id,
            text=f"<b>Cписок услуг:</b>",
            reply_markup=change_service_products_btn
        )


    elif cd == 'change_qiwi_configs':
        if user_id in bot_admins:
            await MyStates.update_qiwi_data.set()
            await bot.send_message(user_id, f"<b>Отправьте номер и токен от QIWI.</b>\n\n"
                                            f"<em>Пример:</em>\n"
                                            f"79632587456\n"
                                            f"eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF..........")
        else:
            await bot.answer_callback_query(c.id, f"Это функция только для Гл.Админам!")


    elif cd == 'sending_all':
        await bot.answer_callback_query(c.id)
        await MyStates.sending_to_users.set()
        await bot.send_message(user_id, "Отправьте сообщения для рассылки:", reply_markup=cencel_btn)


    elif cd == 'all_admins':
        db_admins = db.getAdminsId()
        text = "<b>Все админы:</b>\n\n"
        for adm in db_admins:
            text += f"<a href='tg://user?id={adm[0]}'>Admin</a> - <code>{adm[0]}</code>\n"

        await bot.answer_callback_query(c.id)
        await bot.send_message(user_id, text)


    elif cd.split("_")[0] == 'change':
        await MyStates.update_product_price.set()
        product_row.append(int(cd.split("_")[1]))
        await bot.answer_callback_query(c.id)
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=c.message.message_id,
            text="<b>Введите сумму:</b>"
        )



@dp.message_handler(commands=['start', 'menu', 'cancel'])
async def welcome(message: Message):
    user_id = message.from_user.id
    msg = message.chat.id

    bot_commands = [
        BotCommand(command="/start", description='Запустить бота'),
        BotCommand(command="/menu", description='Главный меню бота'),
        BotCommand(command="/cancel", description='Отменить/Назад')
    ]
    await bot.set_my_commands(bot_commands)


    if db.checkUser(user_id) is None:
        await bot.send_message(user_id, f"<b>Откуда вы узнали про нас?</b>", reply_markup=user_from_btn)

    else:
        video_id = "BAACAgIAAxkBAAJJN2IznZqg5u_B-1xUkbTEGK0zHXpdAALeGAACmoWgScyGfFS0EYncIwQ"
        await bot.send_video(user_id, video_id, caption=f"<b>🙋‍♀️Привет дорогой друг!</b>\n"
                                      f"<b>Меня зовут Осаго Макс</b>\n\n"
                                      f"Я был создан, чтобы помочь тебе оформить Электронный осаго и диагностические карты  на твой автомобиль.\n\n"
                                      f"<em>Обещаю не занимать у тебя много времени, <b>время</b> = <b>деньги</b>, поэтому все будет очень просто, быстро и максимально понятно.</em>\n\n"
                                      f"⏳Заказы обрабатываются: <b>с 09:00 до 22:00 по Московскому времени, а принимаются 24/7</b>\n\n"
                                      f"Выбери нужный пункт из меню и я с радостью тебе помогу😌", reply_markup=menu)



@dp.message_handler(commands=['admin'])
async def adminPanel(message: Message):
    user_id = message.from_user.id
    db_admins = db.getAdminsId()
    qiwi_data = db.getQiwiConfig()
    all_admins = []
    if not db_admins is None:
        for adm in bot_admins:
            all_admins.append(adm)
        for adm in db_admins:
            all_admins.append(adm[0])
    else:
        for adm in bot_admins:
            all_admins.append(adm)

    if user_id in all_admins:
        from_data = db.getFromUsersData()
        text = f"<b>👤 Админ Панель:</b>\n\n" \
               f"<b>Статистика бота:</b> <em>{db.getBotUsers()[0]}</em> человек\n" \
               f"<b>Qiwi Номер:</b> <code>{qiwi_data[0]}</code>\n" \
               f"<b>Qiwi Токен:</b> <code>{qiwi_data[1]}</code>\n\n" \
               f"<b>Yandex:</b> <em>{from_data[0]} чел.</em>\n" \
               f"<b>Google:</b> <em>{from_data[1]} чел.</em>\n" \
               f"<b>Telegram:</b> <em>{from_data[2]} чел.</em>\n" \
               f"<b>WhatsApp:</b> <em>{from_data[3]} чел.</em>\n" \
               f"<b>Vkontakte:</b> <em>{from_data[4]} чел.</em>\n" \
               f"<b>От друга:</b> <em>{from_data[5]} чел.</em>\n"

        await bot.send_message(user_id, text, reply_markup=admin_panel_btn)


@dp.message_handler(commands=['setadmin'])
async def setAdminInBot(message: Message):
    user_id = message.from_user.id
    text = message.text.split(' ')[1]
    db_admins = db.getAdminsId()
    all_admins = []
    if not db_admins is None:
        for adm in bot_admins:
            all_admins.append(adm)
        for adm in db_admins:
            all_admins.append(adm[0])
    else:
        for adm in bot_admins:
            all_admins.append(adm)

    if user_id in all_admins:
        db.setNewAdmin(int(text))
        await bot.send_message(user_id, f"✅ Админ добавлен в базу данных")



@dp.message_handler(commands=['deladmin'])
async def delAdminInBot(message: Message):
    user_id = message.from_user.id
    text = message.text.split(' ')[1]
    db_admins = db.getAdminsId()
    all_admins = []
    if not db_admins is None:
        for adm in bot_admins:
            all_admins.append(adm)
        for adm in db_admins:
            all_admins.append(adm[0])
    else:
        for adm in bot_admins:
            all_admins.append(adm)

    if user_id in all_admins:
        db.delNewAdmin(text)
        await bot.send_message(user_id, f"✅ Админ удален из базу данных")





@dp.message_handler(commands=['info'])
async def getUserInfoHandler(message: Message):
    user_id = message.from_user.id
    text = message.text.split(' ')[1]
    user_info = db.getUserInfo(text)
    db_admins = db.getAdminsId()
    all_admins = []
    if not db_admins is None:
        for adm in bot_admins:
            all_admins.append(adm)
        for adm in db_admins:
            all_admins.append(adm[0])
    else:
        for adm in bot_admins:
            all_admins.append(adm)

    if user_id in all_admins:
        await bot.send_message(user_id, f"ID: {user_info[0]}\n"
                                    f"Баланс: {user_info[1]}\n"
                                    f"Последняя депозитная сумма: {user_info[3]}\n"
                                    f"Последний выбранный продукт: {user_info[4]}\n"
                                    f"Цена последнего выбранного продукта: {user_info[5]}")



@dp.message_handler(commands=['money'])
async def setMoneyAdminHandler(message: Message):
    user_id = message.from_user.id
    text = message.text
    db_admins = db.getAdminsId()
    vals = text.split(" ")
    all_admins = []
    if not db_admins is None:
        for adm in bot_admins:
            all_admins.append(adm)
        for adm in db_admins:
            all_admins.append(adm[0])
    else:
        for adm in bot_admins:
            all_admins.append(adm)

    if user_id in all_admins:
        if len(vals) > 1:
            db.updateUserMoney(user_id=vals[1], money=vals[2])
            await message.reply("Выполнено ✅")





@dp.message_handler(regexp='❌ Отменить')
async def cenceledBtnFunc(message: Message):
    user_id = message.from_user.id
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.delete_message(message.chat.id, message.message_id - 1)
    await bot.send_message(user_id, "Отменено!", reply_markup=remove)
    await bot.send_message(user_id, f"<b>🙋‍♀️Привет дорогой друг!</b>\n"
                                    f"<b>Меня зовут Осаго Макс</b>\n\n"
                                    f"Я был создан, чтобы помочь тебе оформить Электронный осаго и диагностические карты  на твой автомобиль.\n\n"
                                    f"<em>Обещаю не занимать у тебя много времени, <b>время</b> = <b>деньги</b>, поэтому все будет очень просто, быстро и максимально понятно.</em>\n\n"
                                    f"⏳Заказы обрабатываются: <b>с 09:00 до 22:00 по Московскому времени, а принимаются 24/7</b>\n\n"
                                    f"Выбери нужный пункт из меню и я с радостью тебе помогу😌", reply_markup=menu)



@dp.message_handler(regexp='📂 Наши услуги')
async def serviceProductsHandler(message: Message):
    user_id = message.from_user.id
    buy_osago_btn.inline_keyboard.clear()
    back_btn = types.InlineKeyboardButton("🔙 Назад", callback_data="back")
    buy_osago_btn1 = types.InlineKeyboardButton(f"Е-осаго на 1 ГОД | {db.getProductsInfo(rowid=1)[1]} RUB",
                                                callback_data="buy_osago_year")
    buy_osago_btn2 = types.InlineKeyboardButton(f"Е-осаго на 3 МЕС | {db.getProductsInfo(rowid=2)[1]} RUB",
                                                callback_data="buy_osago_month")
    buy_osago_btn3 = types.InlineKeyboardButton(f"Е-осаго БЕЗ БАЗЫ | {db.getProductsInfo(rowid=3)[1]} RUB",
                                                callback_data="buy_osago_nodb")
    buy_osago_btn.add(buy_osago_btn1, buy_osago_btn2, buy_osago_btn3, back_btn)
    await bot.send_message(user_id, f"🌐 Наши услуги", reply_markup=service_products_btn)


@dp.message_handler(regexp='👤 Профиль')
async def serviceProductsHandler(message: Message):
    user_id = message.from_user.id
    user_info = db.getUserInfo(user_id)
    text = f"🆔 ID: {user_id}\n" \
           f"💰 Баланс: {user_info[1]} руб."
    await bot.send_message(user_id, f"👤 Ваш Профиль\n\n{text}", reply_markup=user_profile_btn)


@dp.message_handler(regexp='☎️ Обратная связь')
async def serviceProductsHandler(message: Message):
    user_id = message.from_user.id
    await bot.send_message(user_id, f"✳️ Гл.Админ бота: @osagomakc")


@dp.message_handler(regexp='💥Телеграм канал')
async def serviceProductsHandler(message: Message):
    user_id = message.from_user.id
    await bot.send_message(user_id, f"✳️ Наш канал: @osagomax")


# @dp.message_handler(regexp='📑 Инструкция по боту')
# async def serviceProductsHandler(message: Message):
#     user_id = message.from_user.id
#     await bot.send_message(user_id, f"✳️ Наш канал: @osagomax")


@dp.message_handler(content_types=['text', 'photo', 'document', 'video'])
async def sendinUserOrderFunc(message: Message):
    user_id = message.from_user.id
    text = message.caption
    db_admins = db.getAdminsId()
    all_admins = []
    if not db_admins is None:
        for adm in bot_admins:
            all_admins.append(adm)
        for adm in db_admins:
            all_admins.append(adm[0])
    else:
        for adm in bot_admins:
            all_admins.append(adm)

    try:
        if text.isdigit() and user_id in all_admins:
            if message.content_type == 'photo':
                await bot.send_photo(text, message.photo[-1].file_id, caption="✅ Ваш заказ завершен!")

            elif message.content_type == 'document':
                await bot.send_document(text, message.document.file_id, caption="✅ Ваш заказ завершен!")

            try:
                for sending in all_admins:
                    await bot.send_message(sending, f"✅ Заказ отправлен! (<code>{text}</code>)")
                    await asyncio.sleep(0.03)
            except Exception as ex:
                print(ex)
    except Exception as e:
        pass
        # print(f'{type(e).__name__}: {e} | Line: {sys.exc_info()[-1].tb_lineno}')
    #     await bot.send_message(user_id, f"Юзер с таким ({text}) ID не найден в базе данных")





@dp.message_handler(state=MyStates.depozit)
async def userDepozitFunc(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    pay_btn.inline_keyboard.clear()

    if text == '❌ Отменить':
        await bot.delete_message(message.chat.id, message.message_id - 1)
        await bot.send_message(user_id, "Отменено!", reply_markup=menu)
        await state.finish()
    else:
        p2p = QiwiP2P(auth_key=db.getQiwiConfig()[1])
        bill = p2p.bill(amount=text, lifetime=30, comment=f"{user_id}")
        db.createPayment(user_id, bill.bill_id)

        pay_btn.row(types.InlineKeyboardButton("💸 Оплатить", url=bill.pay_url))
        pay_btn.row(types.InlineKeyboardButton("♻️ Проверить оплату", callback_data='check_pay'))
        pay_btn.row(types.InlineKeyboardButton("❌ Отменить", callback_data="back"))

        if text.isdigit() and int(text) > 100:
            db.updateUserInfo(user_id, item='depozit', value=text)
            await bot.delete_message(user_id, message.message_id)
            await bot.delete_message(user_id, message.message_id - 1)
            await bot.send_message(user_id, f"✅ Ссылка для оплаты создан", reply_markup=remove)
            await bot.send_message(user_id, f"Нажмите кнопку <b>💸 Оплатить</b>", reply_markup=pay_btn)
            await state.finish()
        else:
            await bot.send_message(user_id, f"❗️ Некорректный ввод")



@dp.message_handler(state=MyStates.osago_data)
async def osagoDataFunc(message: Message, state: FSMContext):
    user_id = message.from_user.id
    msg = message.chat.id
    text = message.text
    send_order_btn.inline_keyboard.clear()

    try:
        if text == '❌ Отменить':
            await bot.send_message(user_id, "Отменено!", reply_markup=menu)
            await state.finish()
        else:
            spliting = text.split('\n')
            pass_data = ''
            for item in spliting[6:]:
                pass_data += f"\n{item}"

            if len(spliting) >= 8:
                await bot.send_message(msg, '⏳', reply_markup=remove)
                await asyncio.sleep(3)
                await bot.delete_message(msg, message.message_id + 1)
                send_order_btn.row(types.InlineKeyboardButton("✅ Отправить", callback_data=f"osago_data_send_to_admin"))
                send_order_btn.row(types.InlineKeyboardButton("❌ Отменить", callback_data=f"back"))


                await bot.send_message(
                    msg,
                    f"<b>Проверьте правильность введенных данных:</b>\n\n" 
                    f"<b>├ ФИО СТРАХОВАТЕЛЯ:</b> <em>{spliting[0]}</em>\n" 
                    f"<b>├ ФИО СОБСТВЕННИКА:</b> <em>{spliting[1]}</em>\n" 
                    f"<b>├ МАРКА/МОДЕЛЬ АВТО:</b> <em>{spliting[2]}</em>\n" 
                    f"<b>├ VIN НОМЕР/РАМА/КУЗОВ:</b> <em>{spliting[3]}</em>\n" 
                    f"<b>├ НОМЕР ПТС:</b> <em>{spliting[4]}</em>\n"
                    f"<b>├ НОМЕР АВТО:</b> <em>{spliting[5]}</em>\n"
                    f"<b>├ ПАСПОРТ ДАННЫЕ:</b> <em>{pass_data}</em>\n\n"
                    f'<em>Если данные верны, нажмите "Оплатить заказ"</em>',
                    reply_markup=send_order_btn
                )

                for item, value in zip(osago_data_list, spliting[:6]):
                    db.updateOsagoData(user_id, item=item, value=value)
                db.updateOsagoData(user_id, item='pass_data', value=pass_data)
                db.updateUserInfo(user_id, 'product_name', 'osago_data')

                await state.finish()
            else:
                await bot.send_message(user_id, f"Не все данные введены или вы ввели не нужные данный!")
    except Exception as ex:
        print(ex)
        await bot.send_message(user_id, f"Не все данные введены или вы ввели не нужные данный!")



@dp.message_handler(state=MyStates.dk_data)
async def dkDataFunc(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text

    try:
        if text == '❌ Отменить':
            await bot.delete_message(message.chat.id, message.message_id - 1)
            await bot.send_message(user_id, "Отменено!", reply_markup=menu)
            await state.finish()
        else:
            spliting = text.split('\n')
            if len(spliting) == 4:
                await MyStates.dk_photo_1.set()
                await bot.send_message(user_id, f"├Отправьте фото СТС или ПТС с двух сторон\n<b>❗️(фото отправьте по одному)</b>")

                for item, value in zip(dk_data_list, spliting):
                    db.updateDkData(user_id, item=item, value=value)
                db.updateUserInfo(user_id, 'product_name', 'dk_data')
            else:
                await bot.send_message(user_id, f"Не все данные введены или вы ввели не нужные данный!")


    except Exception as ex:
        print(ex)
        await bot.send_message(user_id, f"Не все данные введены или вы ввели не нужные данный!")



@dp.message_handler(state=MyStates.dk_photo_1, content_types=['photo', 'document', 'text'])
async def dkDataPic1Func(message: Message, state: FSMContext):
    user_id = message.from_user.id

    try:
        if message.text == '❌ Отменить':
            await bot.delete_message(message.chat.id, message.message_id - 1)
            await bot.send_message(user_id, "Отменено!", reply_markup=menu)
            await state.finish()
        else:
            if message.content_type in ['photo', 'document']:
                pic_id = message.photo[-1].file_id
                await MyStates.dk_photo_2.set()
                db.updateDkData(user_id, item='sts_or_pts_photo1', value=pic_id)
                await bot.send_message(user_id, f'Теперь отправьте второй фото')
            else:
                await bot.send_message(user_id, f"Это не фото, пожалуста отправьте фото!")

    except Exception as ex:
        print(ex)



@dp.message_handler(state=MyStates.dk_photo_2, content_types=['photo', 'document', 'text'])
async def dkDataPic1Func(message: Message, state: FSMContext):
    user_id = message.from_user.id

    try:
        if message.text == '❌ Отменить':
            await bot.delete_message(message.chat.id, message.message_id - 1)
            await bot.send_message(user_id, "Отменено!", reply_markup=menu)
            await state.finish()
        else:
            if message.content_type in ['photo', 'document']:
                pic_id = message.photo[-1].file_id
                await MyStates.dk_photo_3.set()
                db.updateDkData(user_id, item='sts_or_pts_photo2', value=pic_id)
                await bot.send_message(user_id, f'Отправьте фото машины спереди и сзади. <em>Лучше всего делать на крытой парковке, боксе, гараже, под навесом, или возле какой нибудь стены. На фоне не должно быть травы, деревьев, неба, солнца.</em>\n\n'
                                                f'<b>❗️(фото отправьте по одному)</b>')
            else:
                await bot.send_message(user_id, f"Это не фото, пожалуста отправьте фото!")

    except Exception as ex:
        print(ex)



@dp.message_handler(state=MyStates.dk_photo_3, content_types=['photo', 'document', 'text'])
async def dkDataPic1Func(message: Message, state: FSMContext):
    user_id = message.from_user.id

    try:
        if message.text == '❌ Отменить':
            await bot.delete_message(message.chat.id, message.message_id - 1)
            await bot.send_message(user_id, "Отменено!", reply_markup=menu)
            await state.finish()
        else:
            if message.content_type in ['photo', 'document']:
                pic_id = message.photo[-1].file_id
                await MyStates.dk_photo_4.set()
                db.updateDkData(user_id, item='photo1', value=pic_id)
                await bot.send_message(user_id, f'Теперь отправьте второй фото')
            else:
                await bot.send_message(user_id, f"Это не фото, пожалуста отправьте фото!")

    except Exception as ex:
        print(ex)



@dp.message_handler(state=MyStates.dk_photo_4, content_types=['photo', 'document', 'text'])
async def dkDataPic1Func(message: Message, state: FSMContext):
    user_id = message.from_user.id
    send_order_btn.inline_keyboard.clear()

    if message.text == '❌ Отменить':
        await bot.send_message(user_id, "Отменено!", reply_markup=menu)
        await state.finish()
    else:
        send_order_btn.row(types.InlineKeyboardButton("✅ Отправить", callback_data=f"dk_data_send_to_admin"))
        send_order_btn.row(types.InlineKeyboardButton("❌ Отменить", callback_data=f"back"))

        if message.content_type in ['photo', 'document']:
            pic_id = message.photo[-1].file_id
            await bot.send_message(user_id, '⏳', reply_markup=remove)
            await asyncio.sleep(2)
            await bot.delete_message(user_id, message.message_id + 1)
            try:
                pics = db.getDkData(user_id)
                text = f"├<b>Проверьте правильность введенных данных:</b>\n\n" \
                       f"├<b>ФИО:</b> <em>{pics[1]}</em>\n" \
                       f'├Примерный пробег: <em>{pics[2]}</em>\n' \
                       f'├Марка шин: <em>{pics[3]}</em>\n' \
                       f'├Тип топлива: <em>{pics[4]}</em>'

                db.updateDkData(user_id, item='photo2', value=pic_id)
                media_group = [InputMediaPhoto(pics[5], caption=text, parse_mode='html'), InputMediaPhoto(pics[6]), InputMediaPhoto(pics[7]), InputMediaPhoto(pics[8])]
                await bot.send_media_group(user_id, media_group)
                await bot.send_message(user_id, f'<em>Если данные верны, нажмите "Оплатить заказ"</em>', reply_markup=send_order_btn)

                await state.finish()

            except Exception as ex:
                print(ex)

        else:
            await bot.send_message(user_id, f"Это не фото, пожалуста отправьте фото!")





@dp.message_handler(state=MyStates.med_auto)
async def medAutoDataFunc(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    send_order_btn.inline_keyboard.clear()

    try:
        if message.text == '❌ Отменить':
            await bot.send_message(user_id, "Отменено!", reply_markup=menu)
            await state.finish()
        else:
            spliting = text.split('\n')
            if len(spliting) == 5:
                await bot.send_message(user_id, '⏳', reply_markup=remove)
                await asyncio.sleep(3)
                await bot.delete_message(user_id, message.message_id + 1)

                send_order_btn.row(types.InlineKeyboardButton("✅ Отправить", callback_data=f"med_auto_send_to_admin"))
                send_order_btn.row(types.InlineKeyboardButton("❌ Отменить", callback_data=f"back"))

                await bot.send_message(
                    chat_id=user_id,
                    text=f"├<b>Проверьте правильность введенных данных:</b>\n\n" \
                         f"<b>├ФИО:</b> {spliting[0]}\n"
                         f'<b>├Дата рож-ния:</b> {spliting[1]}\n'
                         f'<b>├Серия номер паспорта:</b> {spliting[2]}\n'
                         f'<b>├Кем когда выдан:</b> {spliting[3]}\n'
                         f'<b>├Категория прав (B, C, D):</b> {spliting[4]}\n\n'
                         f'<em>Если данные верны, нажмите "Оплатить заказ"</em>',
                    reply_markup=send_order_btn
                )

                for item, value in zip(med_auto_data_list, spliting):
                    db.updateMedAutoData(user_id, item=item, value=value)
                db.updateUserInfo(user_id, 'product_name', 'auto_med_data')

                await state.finish()

            else:
                await bot.send_message(user_id, f"Не все данные введены или вы ввели не нужные данный!", message.message_id)
    except Exception as ex:
        print(ex)



@dp.message_handler(state=MyStates.kasko_bank)
async def kaskoBankDataFunc(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    send_order_btn.inline_keyboard.clear()

    try:
        if message.text == '❌ Отменить':
            await bot.send_message(user_id, "Отменено!", reply_markup=menu)
            await state.finish()
        else:
            spliting = text.split('\n')
            if len(spliting) == 8:
                await bot.send_message(user_id, '⏳', reply_markup=remove)
                await asyncio.sleep(3)
                await bot.delete_message(user_id, message.message_id + 1)

                send_order_btn.row(types.InlineKeyboardButton("✅ Отправить", callback_data=f"kasko_bank_send_to_admin"))
                send_order_btn.row(types.InlineKeyboardButton("❌ Отменить", callback_data=f"back"))

                await bot.send_message(
                    chat_id=user_id,
                    text=f"├<b>Проверьте правильность введенных данных:</b>\n\n" \
                         f"<b>├ФИО:</b> {spliting[0]}\n"
                         f"<b>├ДАТА РОЖДЕНИЯ:</b> {spliting[1]}\n"
                         f"<b>├ВУ:</b> {spliting[2]}\n"
                         f"<b>├СТАЖ ВОЖДЕНИЕ:</b> {spliting[3]}\n"
                         f"<b>├ТС ДАННЫЕ:</b> {spliting[4]}\n"
                         f'<b>├НАИМЕНОВАНИЕ БАНКА:</b> {spliting[5]}\n'
                         f'<b>├ДЕЙСТВИТЕЛЬНАЯ СТОИМОСТЬ АВТОМОБИЛЯ:</b> {spliting[6]}\n'
                         f'<b>├ТЕЛЕФОН НОМЕР:</b> {spliting[7]}\n\n'
                         f'<em>Если данные верны, нажмите "Оплатить заказ"</em>',
                    reply_markup=send_order_btn
                )

                for item, value in zip(kasko_bank_data_list, spliting):
                    db.updateKaskoBankData(user_id, item=item, value=value)
                db.updateUserInfo(user_id, 'product_name', 'kasko_bank_data')

                await state.finish()

            else:
                await bot.send_message(user_id, f"Не все данные введены или вы ввели не нужные данный!")

    except Exception as ex:
        print(ex)



@dp.message_handler(state=MyStates.karta_gibdd)
async def kartaGibddDataFunc(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    send_order_btn.inline_keyboard.clear()

    try:
        if message.text == '❌ Отменить':
            await bot.send_message(user_id, "Отменено!", reply_markup=menu)
            await state.finish()
        else:
            await bot.send_message(user_id, '⏳', reply_markup=remove)
            await asyncio.sleep(3)
            await bot.delete_message(user_id, message.message_id + 1)

            send_order_btn.row(types.InlineKeyboardButton("✅ Отправить", callback_data=f"karta_gibdd_send_to_admin"))
            send_order_btn.row(types.InlineKeyboardButton("❌ Отменить", callback_data=f"back"))

            await bot.send_message(
                chat_id=user_id,
                text=f"├<b>Проверьте правильность введенных данных:</b>\n\n" \
                     f"<b>├Гос.Номер:</b> {text}\n\n"
                     f'<em>Если данные верны, нажмите "Оплатить заказ"</em>',
                reply_markup=send_order_btn
            )

            db.updateKartaGibddData(user_id, item='gos_nomer', value=text)
            db.updateUserInfo(user_id, 'product_name', 'karta_gibdd_data')

            await state.finish()

    except Exception as ex:
        print(ex)



@dp.message_handler(state=MyStates.karta_vu_gai, content_types=['photo', 'document', 'text'])
async def kartaVUGaiDataFunc(message: Message, state: FSMContext):
    user_id = message.from_user.id
    send_order_btn.inline_keyboard.clear()

    if message.text == '❌ Отменить':
        await bot.send_message(user_id, "Отменено!", reply_markup=menu)
        await state.finish()
    else:
        send_order_btn.row(types.InlineKeyboardButton("✅ Отправить", callback_data=f"karta_vu_gai_send_to_admin"))
        send_order_btn.row(types.InlineKeyboardButton("❌ Отменить", callback_data=f"back"))

        if message.content_type in ['photo', 'document']:
            pic_id = message.photo[-1].file_id
            await bot.send_message(user_id, '⏳', reply_markup=remove)
            await asyncio.sleep(2)
            await bot.delete_message(user_id, message.message_id + 1)
            try:


                db.updateKartaVUGaiData(user_id, item='prava_photo', value=pic_id)
                await bot.send_photo(user_id, pic_id, caption=f'<em>Нажмите "Оплатить заказ"</em>', reply_markup=send_order_btn)
                db.updateUserInfo(user_id, 'product_name', 'karta_gai_data')

                await state.finish()


            except Exception as ex:
                print(ex)

        else:
            await bot.send_message(user_id, f"Это не фото, пожалуста отправьте фото!")


@dp.message_handler(state=MyStates.poisk_solariy)
async def posikSolariyDataFunc(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    send_order_btn.inline_keyboard.clear()

    try:
        if message.text == '❌ Отменить':
            await bot.send_message(user_id, "Отменено!", reply_markup=menu)
            await state.finish()
        else:
            spliting = text.split('\n')
            if len(spliting) == 2:
                await bot.send_message(user_id, '⏳', reply_markup=remove)
                await asyncio.sleep(3)
                await bot.delete_message(user_id, message.message_id + 1)

                send_order_btn.row(types.InlineKeyboardButton("✅ Отправить", callback_data=f"poisk_solariy_send_to_admin"))
                send_order_btn.row(types.InlineKeyboardButton("❌ Отменить", callback_data=f"back"))

                await bot.send_message(
                    chat_id=user_id,
                    text=f"├<b>Проверьте правильность введенных данных:</b>\n\n" \
                         f"<b>├ФИО:</b> {spliting[0]}\n"
                         f"<b>├ДАТА РОЖДЕНИЯ:</b> {spliting[1]}\n\n"
                         f'<em>Если данные верны, нажмите "Оплатить заказ"</em>',
                    reply_markup=send_order_btn
                )

                db.updatePoiskSolariyData(user_id, item='fio', value=spliting[0])
                db.updatePoiskSolariyData(user_id, item='birthday', value=spliting[1])
                db.updateUserInfo(user_id, 'product_name', 'search_solary_data')

                await state.finish()

            else:
                await bot.send_message(user_id, f"Не все данные введены или вы ввели не нужные данный!", message.message_id)

    except Exception as ex:
        print(ex)





@dp.message_handler(state=MyStates.sending_to_users, content_types=['text', 'photo', 'document', 'video', 'animation'])
async def sendingToUsersFunc(message: Message, state: FSMContext):
    users = db.getUsers()
    user_id = message.from_user.id
    text_type = message.content_type
    text = message.text
    text_caption = message.caption
    rep_btn = message.reply_markup
    sends = 0
    sends_error = 0

    if message.text == '❌ Отменить':
        await bot.delete_message(message.chat.id, message.message_id - 1)
        await bot.send_message(user_id, "Отменено!", reply_markup=remove)
        await state.finish()
    else:
        await bot.send_message(user_id, "Отправка начился....", reply_markup=remove)
        await state.finish()

        start_time = datetime.datetime.now()
        for u in users:
            try:
                if text_type == 'text':
                    await bot.send_message(u[0], text, reply_markup=rep_btn)
                    sends += 1
                    await asyncio.sleep(0.03)

                elif text_type == "photo":
                    await bot.send_photo(u[0], message.photo[-1].file_id, caption=text_caption,
                                         reply_markup=rep_btn)
                    sends += 1
                    await asyncio.sleep(0.03)

                elif text_type == "video":
                    await bot.send_video(u[0], message.video.file_id, caption=text_caption, reply_markup=rep_btn)
                    sends += 1
                    await asyncio.sleep(0.03)

                elif text_type == "document":
                    await bot.send_document(u[0], message.document.file_id, caption=text_caption, reply_markup=rep_btn)
                    sends += 1
                    await asyncio.sleep(0.03)

                elif text_type == "animation":
                    await bot.send_animation(u[0], message.animation.file_id, caption=text_caption, reply_markup=rep_btn)
                    sends += 1
                    await asyncio.sleep(0.03)



            except Exception as ex:
                # print(f'{type(ex).__name__}: {ex} | Line: {sys.exc_info()[-1].tb_lineno} ****** {ex}')
                sends_error += 1
                continue

        if sends == 0:
            await bot.send_message(user_id, "⚠️ Сообщение не дошло никому")
        else:
            end_time = datetime.datetime.now()
            await bot.send_message(user_id,
                                   f"Рассылка отправлено: <b>{sends + sends_error}</b> юзерам\n"
                                   f"Активных юзеров: <b>{sends}</b>\n"
                                   f"Не активных юзеров: <b>{sends_error}</b>\n\n"
                                   f"Начало: {start_time.hour}:{start_time.minute}:{start_time.second}\n"
                                   f"Конец: {end_time.hour}:{end_time.minute}:{end_time.second}")




@dp.message_handler(state=MyStates.default_text_handler, content_types=['text', 'photo', 'document', 'video'])
async def defaultTextFunc(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.caption
    db_admins = db.getAdminsId()
    qiwi_data = db.getQiwiConfig()
    all_admins = []
    if not db_admins is None:
        for adm in bot_admins:
            all_admins.append(adm)
        for adm in db_admins:
            all_admins.append(adm[0])
    else:
        for adm in bot_admins:
            all_admins.append(adm)

    try:
        if text.isdigit() and user_id in all_admins:
            if message.content_type == 'photo':
                await bot.send_photo(text, message.photo[-1].file_id, caption="✅ Ваш заказ завершен!")

            elif message.content_type == 'document':
                await bot.send_document(text, message.document.file_id, caption="✅ Ваш заказ завершен!")

            try:
                for sending in all_admins:
                    await bot.send_message(sending, f"✅ Заказ отправлен! (<code>{text}</code>)")
                    await asyncio.sleep(0.03)
            except Exception as ex:
                print(ex)
    except Exception as e:
        print(f'{type(e).__name__}: {e} | Line: {sys.exc_info()[-1].tb_lineno}')
        # await bot.send_message(user_id, f"Юзер с таким ({text}) ID не найден в базе данных")
    finally:
        await state.finish()


@dp.message_handler(state=MyStates.update_qiwi_data)
async def updateQiwiDataFunc(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.split('\n')

    if len(text) == 2:
        db.updateQiwiConfig('qiwi_number', text[0])
        db.updateQiwiConfig('qiwi_token', text[1])

        await bot.send_message(user_id, f"✅ Qiwi данные сохранены.")

    else:
        await bot.send_message(user_id, "⚠️ Вы ввели некорректно!")

    await state.finish()



@dp.message_handler(state=MyStates.update_product_price)
async def updateProductPriceFunc(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    change_service_products_btn.inline_keyboard.clear()

    if text.isdigit():
        db.updateProductsInfo(rowid=product_row[0], sum=text)
        product_row.clear()
        await bot.delete_message(user_id, message.message_id)
        await bot.delete_message(user_id, message.message_id - 1)

        chsp1 = types.InlineKeyboardButton(f"Е-осаго на 1 ГОД | {db.getProductsInfo(rowid=1)[1]} RUB",
                                           callback_data="change_1")
        chsp2 = types.InlineKeyboardButton(f"Е-осаго на 3 МЕС | {db.getProductsInfo(rowid=2)[1]} RUB",
                                           callback_data="change_2")
        chsp3 = types.InlineKeyboardButton(f"Е-осаго БЕЗ БАЗЫ | {db.getProductsInfo(rowid=3)[1]} RUB",
                                           callback_data="change_3")
        chsp5 = types.InlineKeyboardButton(f"Диагностическая карта 1 ГОД | {db.getProductsInfo(rowid=4)[1]} RUB",
                                           callback_data="change_4")
        chsp6 = types.InlineKeyboardButton(
            f"Диагностическая карта без базы 1 ГОД | {db.getProductsInfo(rowid=5)[1]} RUB", callback_data="change_5")
        chsp7 = types.InlineKeyboardButton(f"Диагностическая карта B | {db.getProductsInfo(rowid=6)[1]} RUB",
                                           callback_data="change_6")
        chsp8 = types.InlineKeyboardButton(f"Диагностическая карта C | {db.getProductsInfo(rowid=7)[1]} RUB",
                                           callback_data="change_7")
        chsp9 = types.InlineKeyboardButton(f'Купить Мед Справку на права | {db.getProductsInfo(rowid=9)[1]} RUB',
                                           callback_data='change_8')
        chsp10 = types.InlineKeyboardButton(f'Купить КАСКО {db.getProductsInfo(rowid=8)[1]} RUB',
                                            callback_data='change_9')
        chsp11 = types.InlineKeyboardButton(f'Купить Карта учета ГИБДД {db.getProductsInfo(rowid=10)[1]} RUB',
                                            callback_data='change_10')
        chsp12 = types.InlineKeyboardButton(f'Купить ВУ по базе ГАИ {db.getProductsInfo(rowid=11)[1]} RUB',
                                            callback_data='change_11')
        chsp13 = types.InlineKeyboardButton(f'Купить Поиск по базе Солярис {db.getProductsInfo(rowid=12)[1]} RUB',
                                            callback_data='change_12')
        change_service_products_btn.add(chsp1, chsp2, chsp3, chsp5, chsp6, chsp7, chsp8, chsp9, chsp10, chsp11, chsp12,
                                        chsp13)
        change_service_products_btn.row(types.InlineKeyboardButton('🔙 Назад', callback_data='back_to_admin_panel'))

        await bot.send_message(user_id, "✅ Цена изменена", reply_markup=change_service_products_btn)
    else:
        await bot.send_message(user_id, "⚠️ Вы ввели некорректно.")

    await state.finish()






if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)