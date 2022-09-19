from pyqiwip2p import QiwiP2P
import typing

from database.connections import get_all_bot_configs, update_user_balance


async def create_user_invoice(user_id: int, money: typing.Union[int, float]):
    qiwi = await get_all_bot_configs()
    p2p = QiwiP2P(auth_key=qiwi[0]['qiwi_token'])
    bill = p2p.bill(amount=money, lifetime=15, comment=f"{user_id}")
    return bill


async def check_user_invoice(user_id: int, bill_id: str):
    qiwi = await get_all_bot_configs()
    p2p = QiwiP2P(auth_key=qiwi[0]['qiwi_token'])
    check_bill = p2p.check(bill_id)

    if check_bill.status == "PAID":
        context = f'✅ Ваш баланс пополнен на сумму: {check_bill.amount}₽'
        await update_user_balance(user_id, float(check_bill.amount), incriment=True)
        return context

    elif p2p.check(bill_id).status == "EXPIRED":
        context = f"🗑 Ссылка для оплаты просрочен и удален."
        return context

