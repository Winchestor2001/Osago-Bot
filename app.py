import logging
from hashlib import sha256

from aiogram.types import Update

from data.config import AAIO_NOTIFICATION_SECRET_KEY
from loader import dp, bot, config
import middlewares, handlers
from services.payments import check_user_invoice
from utils.set_bot_commands import set_default_commands
from fastapi import FastAPI, HTTPException, Form
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


@app.get("/payments/nicepay/")
async def nicepay_webhook(request: Request):
    full_query = dict(request.query_params)
    if full_query.get("result") == "success":
        amount = full_query.get("amount")
        user_id = full_query.get("order_id")
        await check_user_invoice(amount=amount, user_id=user_id)
        return {"message": "ok"}
    return {"message": full_query["result"]}


@app.post("/payments/crystalpay/")
async def crystalpay_webhook(request: Request):
    payload = await request.json()

    state = payload.get("state")
    if state == "payed":
        user_id = payload.get("extra")
        amount = float(payload.get("rub_amount", 0))
        await check_user_invoice(amount=amount, user_id=user_id)

    return {"message": "ok"}


@app.post("/payments/aaio/")
async def aaio_payment_webhook(
    status: str = Form(...),
    merchant_id: str = Form(...),
    order_id: str = Form(...),
    amount: float = Form(...),
    currency: str = Form(...),
    sign: str = Form(...),
    us_key: str = Form(...),
):
    """
    Webhook от AAIO об успешной оплате заказа
    """

    raw = f"{merchant_id}:{amount:.2f}:{currency}:{AAIO_NOTIFICATION_SECRET_KEY}:{order_id}"
    expected_sign = sha256(raw.encode()).hexdigest()

    if sign != expected_sign:
        logging.warning(f"[AAIO] Неверная подпись заказа: {sign}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    if status in ("success", "hold"):
        logging.info(us_key)
        logging.info(f"[AAIO] Заказ {order_id} успешно оплачен, сумма: {amount} {currency}")
        # Здесь твоя логика: зачисление, отметка заказа, вызов `check_user_invoice()` и т.д.
        # Пример:
        await check_user_invoice(amount=amount, user_id=us_key)

    return {"status": "ok"}

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )

    uvicorn.run("app:app", host="0.0.0.0", port=8002)
