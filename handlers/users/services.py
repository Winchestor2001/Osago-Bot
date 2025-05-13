import asyncio
from typing import List

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from handlers.users.users import start_command
from database.connections import get_single_service_by_id, get_user_info, get_product_by_service, get_product_by_id, \
    create_order, create_photo, update_user_balance, create_user_history
from keyboards.default.services import photo_done_btn
from keyboards.default.user_btn import start_menu_btn, remove_btn, cancel_btn
from keyboards.inline.services import services_btn, products_btn, choose_proccess_btn
from keyboards.inline.user_btn import necessary_btn
from states.all_states import Data
from utils.bot_context import *
from loader import bot
from utils.misc.send_msg_admins import send_to_admins
from utils.misc.useful_functions import send_media_group_to_admin

router = Router()


@router.message(F.text == "📂 Наши услуги")
async def services_handler(message: Message, state: FSMContext):
    await state.clear()
    btn = await services_btn()
    img = FSInputFile("images/services_preview.jpg")
    await message.answer_photo(photo=img, caption="📂 Наши услуги", reply_markup=btn)


@router.callback_query(F.data.startswith("services:"))
async def services_handler_call(call: CallbackQuery, state: FSMContext):
    data = call.data.split(":")[1]
    await call.message.delete()
    if data == "back_to_main_menu":
        btn = await start_menu_btn()
        await call.message.answer(start_text, reply_markup=btn)
    elif data.isdigit():
        service = await get_single_service_by_id(data)
        btn = await products_btn(data)
        await call.message.answer(service[0]["text"], reply_markup=btn)


@router.callback_query(F.data.startswith("products:"))
async def products_handler(call: CallbackQuery, state: FSMContext):
    data = call.data.split(":")[1]
    user_id = call.from_user.id
    if data == "back_to_services":
        btn = await services_btn()
        await call.message.edit_text("📂 Наши услуги", reply_markup=btn)
    elif data.isdigit():
        product = await get_product_by_id(data)
        user = await get_user_info(user_id)
        if not user[0]['user_balance'] >= product[0]['price']:
            await call.answer(not_enough_money, show_alert=True)
            return
        await state.update_data(product=product)
        btn = await choose_proccess_btn()
        await call.message.edit_text("Выберите процесс заполнение анкеты:", reply_markup=btn)


@router.callback_query(F.data.startswith("by:"))
async def process(call: CallbackQuery, state: FSMContext):
    data = call.data.split(":")[1]
    if data == "cancel":
        btn = await services_btn()
        await call.message.edit_text("📂 Наши услуги", reply_markup=btn)
    elif data == "photo":
        template_photo = (await state.get_data())["product"][0]["template_photo"]
        btn = await photo_done_btn()
        await call.message.delete()
        await call.message.answer(template_photo, reply_markup=btn)
        await state.set_state(Data.photo)
    elif data == "hand":
        template_text = (await state.get_data())["product"][0]["template_text"]
        btn = await cancel_btn()
        await call.message.delete()
        await call.message.answer(template_text, reply_markup=btn)
        await state.set_state(Data.text)


@router.message(F.content_type.in_({"text"}), Data.text)
async def get_text(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.strip()
    data = await state.get_data()
    btn = remove_btn

    # Проверка на отмену
    if text == "❌ Отменить":
        await state.clear()
        await message.answer("❌ Процесс отменен", reply_markup=btn)
        await start_command(message, state)
        return

    min_char = data["product"][0]["min_char"]

    if len(text) < min_char:
        await message.answer(error_text + ", Следуйте шаблону")
        return

    order = await create_order(user_id=user_id, product=data["product"][0]["id"])
    context = (f"<a href='tg://user?id={order['user_id']['user_id']}'>Клиент ЛС</a>\n\n"
               f"<b>Данные:</b>\n{text}\n\n"
               f"<b>Услуга:</b> {order['product']['name']} - {order['product']['price']}\n"
               f"<b>Клиент:</b> <code>{order['user_id']['user_id']}</code>")

    await send_to_admins(context)
    await message.answer(soon_send_offer, reply_markup=btn)
    await start_command(message, state)

    await update_user_balance(user_id, value=order['product']['price'], incriment=False)
    await create_user_history(user_id=user_id, order_name=order['product']['name'],
                              price=order['product']['price'])
    await state.clear()



@router.message(F.content_type.in_({"photo"}), Data.photo)
async def get_photos(message: Message, state: FSMContext, album: List[Message] = None):
    file_ids = [message.photo[-1].file_id]
    if album:
        file_ids.clear()
        for obj in album:
            if obj.photo:
                file_ids.append(obj.photo[-1].file_id)
            else:
                file_ids.append(obj[obj.content_type].file_id)
    data = await state.get_data()
    if "photos" in data.keys():
        new_data = data
        for i in file_ids:
            new_data['photos'].append(i)
        await state.set_data(new_data)
    else:
        await state.update_data({'photos': [item for item in file_ids]})
    photos = await state.get_data()
    await message.answer(f"{len(photos['photos'])} фото получен.")


@router.message(F.content_type.in_({"text"}), Data.photo)
async def back_to_main(message: Message, state: FSMContext):
    text = message.text
    btn = remove_btn
    user_id = message.from_user.id
    if text == "❌ Отменить":
        await state.clear()
        await message.answer("❌ Процесс отменен", reply_markup=btn)
        await start_command(message, state)
    elif text == "✅ Готово":
        data = await state.get_data()
        photos = []
        if 'photos' in data.keys():
            order = await create_order(user_id=user_id, product=data["product"][0]["id"])
            for i in data["photos"]:
                photo = await create_photo(order=order["id"], photo_id=i)
                photos.append(photo)

            await send_media_group_to_admin(photos)
            await message.answer(soon_send_offer, reply_markup=btn)
            await start_command(message, state)
            await update_user_balance(user_id, value=order['product']['price'], incriment=False)
            await create_user_history(user_id=user_id, order_name=order['product']['name'], price=order['product']['price'])
            await state.clear()
        else:
            await message.answer("Вы еще не отправили фото.")


@router.message(F.text == "📌 Выжное")
async def necessary_handler(message: Message, state: FSMContext):
    btn = await necessary_btn()
    await message.answer(text="<b>Выберите необходимый пункт:</b>", reply_markup=btn)
