from celery import Celery
from app.core.config.config import settings


def create_celery_app() -> Celery:
   
    celery = Celery("Congrats Email Sender", broker=settings.REDIS_BROKER_URL, backend=settings.REDIS_RESULT_BACKEND)
    celery.conf.include = ["app.tasks.email_task"]
    celery.conf.update({'timezone': 'UTC'})
    celery.conf.enable_utc = True
    from app.tasks.celery_beat_shedule import CELERYBEAT_SCHEDULE
    celery.conf.beat_schedule = CELERYBEAT_SCHEDULE
    return celery

celery_app = create_celery_app()