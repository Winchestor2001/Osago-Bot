from database.connections import get_all_channels
from loader import bot


async def is_subscribed(user_id):
    channels = await get_all_channels()
    not_subscribed_channels = []
    for channel in channels:
        chat_member = await bot.get_chat_member(channel['channel_id'], user_id)
        if chat_member.status not in ['member', 'administrator', 'creator']:
            not_subscribed_channels.append(channel)

    return not_subscribed_channels
