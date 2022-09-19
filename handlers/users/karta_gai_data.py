from typing import List

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import *

from bot_context import *
from database.connections import get_products, get_user_info, save_user_product, send_orders_to_admins, \
    update_user_balance
from keyboards.any_btns.user_btns import product_btn, remove_btn, \
    finish_questionnaire_btn
from states.AllStates import UserStates


async def karta_gai_callback(c: CallbackQuery):
    await c.answer()
    btn = await product_btn('karta_gai')
    await c.message.edit_text(karta_gai_text, reply_markup=btn)


async def select_karta_gai_callback(c: CallbackQuery, state: FSMContext):
    user_id = c.from_user.id
    product = await get_products('karta_gai', slug=c.data.split(":")[1])
    await state.set_data({'product': product[0]['product_name'], 'price': product[0]['product_price']})
    user = await get_user_info(user_id)
    if user[0]['user_balance'] >= product[0]['product_price']:
        await c.answer()
        btn = await finish_questionnaire_btn()
        await c.message.delete()
        await c.message.answer(karta_gai_product_photo_text, reply_markup=btn)
        await UserStates.karta_vu_gai.set()
    else:
        await c.answer(not_enough_money, show_alert=True)


async def karta_gai_photo_questionnaire_state(message: Message, state: FSMContext, album: List[Message] = None):
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


def register_karta_gai_data_py(dp: Dispatcher):
    dp.register_callback_query_handler(karta_gai_callback, text='karta_gai')
    dp.register_callback_query_handler(select_karta_gai_callback, text_contains='karta_gai:')

    dp.register_message_handler(karta_gai_photo_questionnaire_state, content_types=['photo', 'text'], state=UserStates.karta_vu_gai)

