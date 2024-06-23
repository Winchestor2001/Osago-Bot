import asyncio
import logging
import sys

from aiogram.types import Update

from loader import dp, bot, config
import middlewares, filters, handlers
from utils.set_bot_commands import set_default_commands
from fastapi import FastAPI
from fastapi.requests import Request
import uvicorn
from contextlib import asynccontextmanager


async def on_startup():
    await set_default_commands(bot)

    dp.include_routers(*handlers.routers_list)
    dp.message.middleware(middlewares.subscription.SubscriptionMiddleware())
    dp.message.middleware(middlewares.album.AlbumMiddleware())


@asynccontextmanager
async def lifespan(app: FastAPI):
    url_webhook = config.WEBHOOK_URL + config.WEBHOOK_PATH
    await on_startup()
    await bot.set_webhook(url=url_webhook,
                          allowed_updates=dp.resolve_used_update_types(),
                          drop_pending_updates=True)
    yield
    await bot.delete_webhook()


app = FastAPI(lifespan=lifespan)


@app.post(config.WEBHOOK_PATH)
async def webhook(request: Request) -> None:
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)


@app.post("/payments")
async def payments_webhook(request: Request) -> None:
    request_data = await request.json()
    logging.info(request_data)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )

    uvicorn.run("app:app", host="0.0.0.0", port=8001)
