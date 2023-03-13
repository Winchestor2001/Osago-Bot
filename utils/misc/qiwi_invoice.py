import asyncio
import os

from pyqiwip2p import QiwiP2P, AioQiwiP2P
import typing

from database.connections import get_all_bot_configs, update_user_balance, get_all_users_payments, \
    delete_user_payment_bill
from loader import bot


async def create_user_invoice(user_id: int, money: typing.Union[int, float]):
    qiwi = await get_all_bot_configs()
    p2p = AioQiwiP2P(auth_key=qiwi[0]['qiwi_token'])
    bill = await p2p.bill(amount=money, lifetime=15, comment=f"{user_id}")
    return bill


async def check_user_invoice(user_id: int, bill_id: str):
    qiwi = await get_all_bot_configs()
    p2p = AioQiwiP2P(auth_key=qiwi[0]['qiwi_token'])
    check_bill = await p2p.check(bill_id)
    if check_bill.status == "PAID":
        context = f'✅ Ваш баланс пополнен на сумму: {check_bill.amount}₽'
        await update_user_balance(user_id, float(check_bill.amount), incriment=True)
        await delete_user_payment_bill(bill_id)
        return context

    elif check_bill.status == "EXPIRED":
        await p2p.reject(bill_id=bill_id)
        context = f"🗑 Ссылка для оплаты просрочен и удален."
        await delete_user_payment_bill(bill_id)
        return context

    return None


async def check_users_payment():
    payments = await get_all_users_payments()
    try:
        for payment in payments:
            user_id = payment['user_id']['user_id']
            bill_id = payment['bill_id']
            message = await check_user_invoice(user_id=user_id, bill_id=bill_id)
            await bot.send_chat_action(user_id, 'typing')
            await bot.send_message(user_id, payments)
            if message:
                await bot.send_message(user_id, message)
                await asyncio.sleep(.5)
    except Exception as ex:
        print(ex)


async def clear_qiwi_files():
    files = os.scandir()
    for file in files:
        if file.name.startswith('QiwiCrash'):
            try:
                os.unlink(file.name)
            except:
                continue
