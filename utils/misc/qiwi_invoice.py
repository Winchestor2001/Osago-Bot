import asyncio
import os

import aiohttp
from pyqiwip2p import QiwiP2P, AioQiwiP2P
import typing

from database.connections import get_all_bot_configs, update_user_balance, get_all_users_payments, \
    delete_user_payment_bill
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
            try:
                response = await response.json()
                # await bot.send_message(591250245, f'{response} == {bill_id}')
                if response['status'] == "success":
                    context = f'✅ Ваш баланс пополнен на сумму: {response["amount"]}₽'
                    await update_user_balance(user_id, float(response["amount"]), incriment=True)
                    await delete_user_payment_bill(bill_id)
                    return context

                elif response['status'] == "expired":
                    context = f"🗑 Ссылка для оплаты просрочен и удален."
                    await delete_user_payment_bill(bill_id)
                    return context
            except:
                await bot.send_message(591250245, f'{response} == {bill_id}')


async def check_users_payment():
    payments = await get_all_users_payments()
    try:
        for payment in payments:
            user_id = payment['user_id']['user_id']
            bill_id = payment['bill_id']
            message = await check_user_invoice(user_id=user_id, bill_id=bill_id)
            await bot.send_chat_action(user_id, 'typing')
            # await bot.send_message(user_id, payments)
            if message:
                await bot.send_message(user_id, message)
                await asyncio.sleep(.3)
    except Exception as ex:
        # print(ex)
        await bot.send_message(591250245, ex)
        pass
    