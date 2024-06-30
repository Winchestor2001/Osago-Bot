from typing import List

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import *

from bot_context import *
from database.connections import get_products, get_user_info, save_user_product, send_orders_to_admins, \
    update_user_balance, save_kasko_bank_data, \
    send_kasko_bank_data_to_admins
from keyboards.any_btns.user_btns import product_btn, choose_proccess_btn, remove_btn, cancel_btn, \
    finish_questionnaire_btn
from states.AllStates import UserStates


async def kasko_bank_callback(c: CallbackQuery):
    await c.answer()
    btn = await product_btn('kasko_bank')
    await c.message.edit_text(kasko_bank_text, reply_markup=btn)


async def select_kasko_bank_callback(c: CallbackQuery, state: FSMContext):
    user_id = c.from_user.id
    product = await get_products('kasko_bank', slug=c.data.split(":")[1])
    await state.set_data({'product': product[0]['product_name'], 'price': product[0]['product_price']})
    user = await get_user_info(user_id)
    if user[0]['user_balance'] >= product[0]['product_price']:
        await c.answer()
        btn = await choose_proccess_btn('kaskobank')
        await c.message.edit_text("Выберите процесс заполнение анкеты:", reply_markup=btn)
    else:
        await c.answer(not_enough_money, show_alert=True)


async def kasko_bank_questionnaire_callback(c: CallbackQuery):
    await c.answer()
    cd = c.data.split("_")[1]
    if cd == 'photo':
        btn = await finish_questionnaire_btn()
        await c.message.delete()
        await c.message.answer(kasko_bank_product_photo_text, reply_markup=btn)
        await UserStates.kasko_bank_photo.set()
    else:
        btn = await cancel_btn()
        await c.message.delete()
        await c.message.answer(kasko_bank_product_text, reply_markup=btn)
        await UserStates.kasko_bank.set()


async def kasko_bank_photo_questionnaire_state(message: Message, state: FSMContext, album: List[Message] = None):
    text = message.text
    user_id = message.from_user.id
    btn = await remove_btn()
    if text == '✅ Готово':
        data = await state.get_data()
        if 'photos' in data.keys():
            await save_user_product(user_id, data)
            await message.answer(soon_send_offer, reply_markup=btn)
            await update_user_balance(user_id, value=data['price'], incriment=False)
            await send_orders_to_admins()
            await state.finish()
        else:
            await message.answer("Вы еще не отправили фото.")

    elif text in ['/start', '/menu', '/cancel']:
        await message.answer("❌ Процесс отменен", reply_markup=btn)
        await state.finish()
        return

    elif message.content_type == 'photo':
        file_ids = [message.photo[-1].file_id]
        if album:
            file_ids.clear()
            for obj in album:
                if obj.photo:
                    file_ids.append(obj.photo[-1].file_id)
                else:
                    file_ids.append(obj[obj.content_type].file_id)
        photos = await state.get_data()
        if 'photos' in photos.keys():
            photos2 = photos
            for i in file_ids:
                photos2['photos'].append(i)
            await state.set_data(photos2)
        else:
            await state.update_data({'photos': [item for item in file_ids]})
        photos = await state.get_data()
        await message.answer(f"{len(photos['photos'])} фото получен.")


async def kasko_bank_questionnaire_state(message: Message, state: FSMContext):
    text = message.text
    user_id = message.from_user.id
    btn = await remove_btn()
    if text in ['/start', '/menu', '/cancel']:
        await message.answer("❌ Процесс отменен", reply_markup=btn)
        await state.finish()
        return
    if text == '❌ Отменить':
        await message.answer("❌ Процесс отменен", reply_markup=btn)
        await state.finish()
    if len(text) >= 150:
        data = await state.get_data()
        await save_kasko_bank_data(user_id, text, data)
        await message.answer(soon_send_offer, reply_markup=btn)
        await update_user_balance(user_id, value=data['price'], incriment=False)
        await send_kasko_bank_data_to_admins()
        await state.finish()
    else:
        await message.answer(error_text)


def register_kasko_bank_data_py(dp: Dispatcher):
    dp.register_callback_query_handler(kasko_bank_callback, text='kasko_bank')
    dp.register_callback_query_handler(select_kasko_bank_callback, text_contains='kasko_bank:')
    dp.register_callback_query_handler(kasko_bank_questionnaire_callback, text='kaskobank_photo')
    dp.register_callback_query_handler(kasko_bank_questionnaire_callback, text='kaskobank_simple')
    #
    dp.register_message_handler(kasko_bank_photo_questionnaire_state, content_types=['photo', 'text'],
                                state=UserStates.kasko_bank_photo)
    dp.register_message_handler(kasko_bank_questionnaire_state, content_types=['text'],
                                state=UserStates.kasko_bank)
