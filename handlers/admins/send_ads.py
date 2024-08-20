import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError

from database.connections import get_all_users
from filters.is_admin import IsAdmin
from handlers.admins.start import intro_admin
from keyboards.default.user_btn import cancel_btn, remove_btn
from loader import bot
from states.admin_states import Admin

router = Router()


@router.callback_query(F.data == "admin:sending_msg", IsAdmin())
async def handle_admin(call: CallbackQuery, state: FSMContext):
    btn = await cancel_btn()
    await call.message.delete()
    await call.message.answer("Отправьте сообщения для рассылки:", reply_markup=btn)
    await state.set_state(Admin.send_msg)


@router.message(Admin.send_msg, IsAdmin())
async def send_message(message: Message, state: FSMContext):
    text = message.text
    admin_user_id = message.from_user.id
    text_type = message.content_type
    text_caption = message.caption
    html_text = message.html_text
    reply_btn = message.reply_markup
    sends = 0
    sends_error = 0
    users = await get_all_users()

    btn = remove_btn
    if text in ["❌ Отменить", "/start", "/menu", "/admin", "/cancel"]:
        await state.clear()
        await message.answer("❌ Процесс отменен", reply_markup=btn)
        await intro_admin(message, state)
        return

    await message.answer("⌛️ Отправка начился....", reply_markup=btn)
    await state.clear()

    for user in users:
        user_id = user["user_id"]
        try:
            if text_type == 'sticker':
                return
            elif text_type == 'text':
                await bot.send_message(chat_id=user_id, text=text, reply_markup=reply_btn)
                await asyncio.sleep(0.05)
            elif text_type == 'video':
                await bot.send_video(user_id, message.video.file_id, caption=text_caption, reply_markup=reply_btn)
                await asyncio.sleep(0.05)
            elif text_type == 'photo':
                await bot.send_photo(user_id, message.photo[-1].file_id, caption=text_caption, reply_markup=reply_btn)
                await asyncio.sleep(0.05)
            elif text_type == 'audio':
                await bot.send_audio(user_id, message.audio, reply_markup=reply_btn)
                await asyncio.sleep(0.05)
            elif text_type == 'location':
                lat = message.location['latitude']
                lon = message.location['longitude']
                await bot.send_location(chat_id=user_id, latitude=lat, longitude=lon, reply_markup=reply_btn)
                await asyncio.sleep(0.05)
            sends += 1
        except TelegramAPIError:
            sends_error += 1
            continue
    await bot.delete_message(chat_id=admin_user_id, message_id=message.message_id + 1)
    if sends == 0:
        await bot.send_message(admin_user_id, "⚠️ Сообщение не дошло никому")
    else:
        await bot.send_message(admin_user_id,
                               f"Рассылка отправлено: <b>{sends + sends_error}</b> юзерам\n"
                               f"Активных юзеров: <b>{sends}</b>\n"
                               f"Не активных юзеров: <b>{sends_error}</b>")

    # await intro_admin(message, state)
