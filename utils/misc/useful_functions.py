from aiogram.utils.deep_linking import create_start_link

from database.connections import get_user_info
from keyboards.inline.user_btn import user_profile_btn
from loader import bot


async def get_user_context(user_id):
    ref_link = await create_start_link(bot=bot, payload=str(user_id))
    user = await get_user_info(user_id)
    btn = await user_profile_btn(user_id)
    context = f"👤 Ваш Профиль\n\n" \
              f"🆔 ID: {user_id}\n" \
              f"💰 Баланс: {user[0]['user_balance']} руб.\n" \
              f"👥 Реф.кол: {user[0]['referals']}\n\n" \
              f"🔗 Реф.ссылка: {ref_link}"
    return context, btn
