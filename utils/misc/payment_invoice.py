import aiohttp

from database.connections import update_user_balance, delete_user_invoice, get_user_invoice
import hashlib
from urllib.parse import urlencode
from data.config import SECRET_KEY1, API_KEY, MERCHANT_ID, BOT_TOKEN
from uuid import uuid4

from keyboards.default.user_btn import start_menu_btn
from loader import bot


async def create_user_invoice(amount):
    currency = "RUB"
    lang = "ru"
    order_id = uuid4()
    sign = f':'.join([
        str(MERCHANT_ID),
        str(amount),
        str(currency),
        str(SECRET_KEY1),
        str(order_id)
    ])

    params = {
        'merchant_id': MERCHANT_ID,
        'amount': amount,
        'currency': currency,
        'order_id': order_id,
        'sign': hashlib.sha256(sign.encode('utf-8')).hexdigest(),
        'desc': "Osago BOT",
        'lang': lang
    }
    return "https://aaio.so/merchant/pay?" + urlencode(params), order_id


async def check_user_invoice(amount, user_id):
    context = f'✅ Ваш баланс пополнен на сумму: {amount}₽'
    await update_user_balance(user_id, amount, incriment=True)
    await delete_user_invoice(user_id)
    btn = await start_menu_btn()
    await bot.send_message(chat_id=user_id, text=context, reply_markup=btn)
