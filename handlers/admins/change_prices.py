import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError
from database.connections import update_config_price, update_product_price

from filters.is_admin import IsAdmin
from handlers.admins.start import intro_admin
from keyboards.default.user_btn import cancel_btn, remove_btn
from keyboards.inline.admin import admin_edit_products_btn
from states.admin_states import Admin
from loader import bot

router = Router()


@router.callback_query(F.data == "admin:change_prices", IsAdmin())
async def handle_admin(call: CallbackQuery, state: FSMContext):
    btn = await admin_edit_products_btn()
    await call.message.delete()
    await call.message.answer("Все услуги:", reply_markup=btn)


@router.callback_query(F.data.startswith("edit_price:"))
async def edit_price_handler(call: CallbackQuery, state: FSMContext):
    data = call.data.split(":")
    if len(data) >= 2:
        if len(data) == 2:
            await state.update_data(product_id=data[1])
        elif len(data) == 3:
            await state.update_data(config=data[2])
        btn = await cancel_btn()
        await call.message.delete()
        await call.message.answer("Введите сумму:", reply_markup=btn)
        await state.set_state(Admin.change_product_price)


@router.message(Admin.change_product_price, IsAdmin())
async def change_product_price_handler(message: Message, state: FSMContext):
    text = message.text
    btn = remove_btn
    if text == '❌ Отменить':
        await message.answer("❌ Отменино", reply_markup=btn)
        await intro_admin(message, state)
        await state.clear()
        return
    if text.isdigit():
        data = await state.get_data()
        if "product_id" in data.keys():
            await update_product_price(data['product_id'], text)
        elif "config":
            if data["config"] == "ref_sum":
                await update_config_price(sequence=1, price=text)
            elif data["config"] == "min_sum":
                await update_config_price(sequence=2, price=text)
        await message.answer('Сохранено ✅', reply_markup=btn)
        await intro_admin(message, state)
        await state.clear()
    else:
        await message.answer("Введите цифру")
        return 