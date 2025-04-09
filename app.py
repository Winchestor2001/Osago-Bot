import asyncio
import logging
import sys

from aiogram.types import Update
from pydantic import BaseModel

from data.config import NICEPAY_SECRET_KEY
from loader import dp, bot, config
import middlewares, filters, handlers
from utils.misc.payment_invoice import check_user_invoice
from utils.misc.useful_functions import generate_nicepay_hash
from utils.set_bot_commands import set_default_commands
from fastapi import FastAPI, Form, HTTPException
from fastapi.requests import Request
import uvicorn
from contextlib import asynccontextmanager


class PaymentRequest(BaseModel):
    merchant_id: str
    invoice_id: str
    order_id: str
    amount: float
    currency: str
    profit: float
    commission: float
    commission_client: float
    commission_type: str
    sign: str
    method: str
    desc: str
    email: str
    us_key: str


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


@app.get("/payments/nicepay/")
async def payments_webhook(request: Request):
    full_query = dict(request.query_params)
    if full_query.get("result") == "success":
        await check_user_invoice(full_query)
        return {"message": "ok"}
    return {"message": full_query["result"]}


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )

    uvicorn.run("app:app", host="0.0.0.0", port=8001)
