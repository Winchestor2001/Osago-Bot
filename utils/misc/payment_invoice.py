import aiohttp

from database.connections import update_user_balance, delete_user_invoice, get_user_invoice
import hashlib
from urllib.parse import urlencode
from data.config import SECRET_KEY1, API_KEY, MERCHANT_ID, BOT_TOKEN
from uuid import uuid4

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


async def check_user_invoice(request_data):
    context = f'✅ Ваш баланс пополнен на сумму: {request_data.get("amount")}₽'
    user = (await get_user_invoice(request_data.get("order_id")))['user_id']
    await update_user_balance(user['user_id'], float(request_data.get("amount")), incriment=True)
    await delete_user_invoice(user['user_id'])
    await bot.send_message(chat_id=user['user_id'], text=context)


# async def check_user_invoice(user_id: int, bill_id: str, bot):
#     url = 'https://aaio.so/api/info-pay'
#     params = {
#         'merchant_id': MERCHANT_ID,
#         'order_id': bill_id
#     }
#
#     headers = {
#         'Accept': 'application/json',
#         'Content-Type': 'application/x-www-form-urlencoded',
#         'X-Api-Key': API_KEY
#     }
#
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url, data=params, headers=headers) as response:
#             if response.status == 200:
#                 response = await response.json()
#                 if response['status'] not in ["success", "hold"]:
#                     context = f'✅ Ваш баланс пополнен на сумму: {response["amount"]}₽'
#                     await update_user_balance(user_id, float(response["amount"]), incriment=True)
#                     await delete_user_invoice(user_id)
#                     return await send_telegram_message(user_id, context)
#
#                 elif response['status'] == "expired":
#                     context = f"🗑 Ссылка для оплаты просрочен и удален."
#                     await delete_user_invoice(user_id)
#                     return await send_telegram_message(user_id, context)
#             else:
#                 await send_telegram_message(591250245, f'{response} == {bill_id}')
#                 # await delete_user_invoice(user_id)
#
#
# async def send_telegram_message(chat_id: int, text: str):
#     url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
#     payload = {
#         'chat_id': chat_id,
#         'text': text
#     }
#
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url, data=payload) as response:
#             if response.status == 200:
#                 response_data = await response.json()
#                 return response_data
#             else:
#                 error_message = await response.text()
#                 raise Exception(f'Failed to send message: {error_message}')
