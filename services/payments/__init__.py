from database.connections import update_user_balance, delete_user_invoice
from keyboards.default.user_btn import start_menu_btn
from loader import bot


async def check_user_invoice(amount, user_id):
    context = f'✅ Ваш баланс пополнен на сумму: {amount}₽'
    await update_user_balance(user_id, amount, incriment=True)
    await delete_user_invoice(user_id)
    btn = await start_menu_btn()
    await bot.send_message(chat_id=user_id, text=context, reply_markup=btn)


def translate_crystalpay_type(en_type: str):
    invoice_types = {
        "notpayed": "❌ Не оплачено",
        "processing": "♻️ В обработке",
        "wrongamount": "💸 Требуется доплата",
        "failed": "⚠️ Ошибка, подробнее на странице",
        "payed": "✅ Оплачено",
        "unavailable": "🚫 Способ оплаты недоступен",
    }
    return invoice_types.get(en_type)