# osago_max


celery -A celery_service.app worker --loglevel=info


celery -A celery_service.app beat --loglevel=info
