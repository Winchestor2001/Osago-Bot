import asyncio

from psycopg2 import InterfaceError

from celery_service.app import celery
from database.models import Payments
from utils.misc.payment_invoice import check_user_invoice
from loader import bot


@celery.task
def test():
    try:
        payments = Payments.select()
        for payment in payments:
            asyncio.run(check_user_invoice(payment.user_id, payment.bill_id, bot))
    except InterfaceError:
        print("Cursor already closed")
