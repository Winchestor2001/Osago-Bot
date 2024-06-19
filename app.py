import asyncio
import logging
import sys

from loader import dp, bot
import middlewares, filters, handlers
from utils.set_bot_commands import set_default_commands


async def on_startup():
    await set_default_commands(bot)

    dp.include_routers(*handlers.routers_list)
    dp.message.middleware(middlewares.subscription.SubscriptionMiddleware())
    dp.message.middleware(middlewares.album.AlbumMiddleware())

    # await bot.delete_webhook(drop_pending_updates=True)  # skip_updates
    await dp.start_polling(bot)


if __name__ == '__main__':
    # logging.basicConfig(filename="logs/bot_error.log", level=logging.INFO, stream=sys.stdout)
    asyncio.run(on_startup())
