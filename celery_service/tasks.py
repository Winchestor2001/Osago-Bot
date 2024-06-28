import logging

from celery_service.app import celery


@celery.task
def test():
    return "Worked"
