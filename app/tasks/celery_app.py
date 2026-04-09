# app/tasks/celery_app.py
from celery import Celery
from app.core.config.config import settings
from app.tasks.celery_beat_shedule import CELERYBEAT_SCHEDULE

def create_celery_app() -> Celery:
    celery = Celery(
        "Congrats Email Sender", 
        broker=settings.REDIS_BROKER_URL, 
        backend=settings.REDIS_RESULT_BACKEND
    )
    
    celery.conf.include = ["app.tasks.email_task"]
    celery.conf.update({'timezone': 'UTC'})
    celery.conf.enable_utc = True
    
    # Enable events for Flower monitoring
    celery.conf.update(
        worker_send_task_events=True,  # Required for Flower
        task_send_sent_event=True,
        task_track_started=True,
    )

    celery.conf.beat_schedule = CELERYBEAT_SCHEDULE
    
    return celery

celery_app = create_celery_app()