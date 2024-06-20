from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.exceptions import TelegramAPIError

from database.connections import get_user_info, get_all_admins
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


async def send_media_group_to_admin(photos):
    media = MediaGroupBuilder()
    admins = await get_all_admins()
    for k, photo in enumerate(photos, start=0):
        client_link = f"<a href='tg://user?id={photo['order']['user_id']['user_id']}'>Клиент ЛС</a>"
        context = (f"{client_link}\n\n<b>Услуга:</b> {photo['order']['product']['name']} - {photo['order']['product']['price']}руб.\n"
                   f"<b>Клиент:</b> <code>{photo['order']['user_id']['user_id']}</code>")
        if k == 0:
            media.add_photo(photo['photo_id'], caption=context)
        else:
            media.add_photo(photo['photo_id'])

    try:
        for admin in admins:
            await bot.send_media_group(chat_id=admin['admin_id'], media=media.build())
    except TelegramAPIError:
        pass
