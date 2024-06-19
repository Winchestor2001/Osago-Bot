import asyncio
from typing import List

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.users.users import start_command
from database.connections import get_single_service_by_id, get_user_info, get_product_by_service, get_product_by_id
from keyboards.default.services import photo_done_btn
from keyboards.default.user_btn import start_menu_btn, remove_btn
from keyboards.inline.services import services_btn, products_btn, choose_proccess_btn
from states.all_states import Data
from utils.bot_context import *
from loader import bot

router = Router()


@router.message(F.text == "📂 Наши услуги")
async def services_handler(message: Message, state: FSMContext):
    await state.clear()
    btn = await services_btn()
    await message.answer("📂 Наши услуги", reply_markup=btn)


@router.callback_query(F.data.startswith("services:"))
async def services_handler_call(call: CallbackQuery, state: FSMContext):
    data = call.data.split(":")[1]
    if data == "back_to_main_menu":
        await call.message.delete()
        btn = await start_menu_btn()
        await call.message.answer(start_text, reply_markup=btn)
    elif data.isdigit():
        service = await get_single_service_by_id(data)
        btn = await products_btn(data)
        await call.message.edit_text(service[0]["text"], reply_markup=btn)


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
        await call.message.answer("qolda yoz !!!")


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
    if text == "🔙 Назад":
        await state.clear()
        await message.answer("❌ Процесс отменен", reply_markup=btn)
        await services_handler(message, state)
    elif text == "✅ Готово":
        data = await state.get_data()
        if 'photos' in data.keys():
            # await save_user_product(user_id, data)
            await message.answer(soon_send_offer, reply_markup=btn)
            await start_command(message, state)
            # await update_user_balance(user_id, value=data['price'], incriment=False)
            # await send_orders_to_admins()
            await state.clear()
        else:
            await message.answer("Вы еще не отправили фото.")
