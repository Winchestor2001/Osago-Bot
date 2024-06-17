from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.deep_linking import create_start_link

from database.connections import get_user_info
from keyboards.inline.user_btn import user_profile_btn
from loader import bot


router = Router()


@router.message(F.text == "👤 Профиль")
async def user_profile_handler(message: Message):
    user_id = message.from_user.id
    ref_link = await create_start_link(bot=bot, payload=str(user_id))
    user = await get_user_info(user_id)
    btn = await user_profile_btn(user_id)
    context = f"👤 Ваш Профиль\n\n" \
              f"🆔 ID: {user_id}\n" \
              f"💰 Баланс: {user[0]['user_balance']} руб.\n" \
              f"👥 Реф.кол: {user[0]['referals']}\n\n" \
              f"🔗 Реф.ссылка: {ref_link}"
    await message.answer(context, reply_markup=btn, disable_web_page_preview=True)
