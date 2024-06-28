from celery_service.app import celery
from database.models import Payments


@celery.task
def test():
    payments = Payments.select()
    for payment in payments:
        print(payment.user_id)
        print(payment.bill_id)
