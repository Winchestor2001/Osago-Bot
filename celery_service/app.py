from celery import Celery
from data import config
from datetime import timedelta

celery = Celery('app', broker=f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_DB}')

celery.conf.beat_schedule = {
    'test-task': {
        'task': 'celery_service.tasks.test',
        'schedule': timedelta(seconds=20)
    },
}

celery.conf.timezone = 'UTC'
