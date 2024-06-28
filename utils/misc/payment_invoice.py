import asyncio
import os

import aiohttp

from database.connections import update_user_balance, get_user_invoice, delete_user_invoice
from loader import bot
import hashlib
from urllib.parse import urlencode
from data.config import SECRET_KEY1, API_KEY, MERCHANT_ID
from uuid import uuid4


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


# async def check_user_invoice(request_data):
#     context = f'✅ Ваш баланс пополнен на сумму: {request_data["amount"]}₽'
#     user = await get_user_invoice(request_data['order_id'])
#     await update_user_balance(user['user_id'], float(request_data["amount"]), incriment=True)
#     await delete_user_invoice(user['user_id'])
#     await bot.send_message(chat_id=user['user_id'], text=context)


async def check_user_invoice(user_id: int, bill_id: str):
    url = 'https://aaio.so/api/info-pay'
    params = {
        'merchant_id': MERCHANT_ID,
        'order_id': bill_id
    }

    headers = {
        'Accept': 'application/json',
        'X-Api-Key': API_KEY
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params, headers=headers) as response:
            if response.status == 200:
                response = await response.json()
                if response['status'] in ["success", "hold"]:
                    context = f'✅ Ваш баланс пополнен на сумму: {response["amount"]}₽'
                    await update_user_balance(user_id, float(response["amount"]), incriment=True)
                    await delete_user_invoice(user_id)
                    return context

                elif response['status'] == "expired":
                    context = f"🗑 Ссылка для оплаты просрочен и удален."
                    await delete_user_invoice(user_id)
                    return context
            else:
                await bot.send_message(591250245, f'{response} == {bill_id}')
