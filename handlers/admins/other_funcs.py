import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError

from database.connections import get_all_users, get_user_info, get_all_admins, update_user_balance
from filters.is_admin import IsAdmin
from handlers.admins.start import intro_admin
from keyboards.default.user_btn import cancel_btn, remove_btn
from loader import bot
from utils.bot_context import success_order_text

router = Router()


@router.message(F.text.regexp(r'/info'), IsAdmin())
async def about_user(message: Message):
    text = message.text.split()
    if len(text) == 2 and text[1].isdigit():
        user = await get_user_info(int(text[1]))
        if not user:
            await message.answer("Неверный ID")
            return

        context = (f"ID: <code>{user[0]['user_id']}</code>\n"
                   f"Имя: {user[0]['full_name']}\n"
                   f"Баланс: {user[0]['user_balance']}руб.")
        await message.answer(context)
    else:
        await message.answer("Неверный ID")


@router.message(F.text.regexp(r'/money'), IsAdmin())
async def admin_update_user_balance(message: Message):
    text = message.text.split()
    if len(text) == 3:
        await update_user_balance(user_id=int(text[1]), value=int(text[2]), sett=True)
        await message.answer("Баланс изменен!")


@router.message(F.content_type.in_({'document', 'photo'}), IsAdmin())
async def admin_send_orders_handler(message: Message):
    admins = await get_all_admins()
    content_type = message.content_type
    caption = message.caption
    if content_type == 'document' and caption:
        await bot.send_document(chat_id=int(caption), document=message.document.file_id, caption=success_order_text)
    elif content_type == 'photo' and caption:
        await bot.send_photo(chat_id=int(caption), photo=message.photo[-1].file_id, caption=success_order_text)

    for admin in admins:
        await bot.send_message(admin['admin_id'], f"✅ Отправлено. <code>{caption}</code>")
