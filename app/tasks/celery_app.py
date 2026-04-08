# app/tasks/celery_app.py - ONE FILE TO RULE THEM ALL
from celery import Celery
from celery.schedules import crontab
from app.core.config.config import settings

# Create Celery app
celery_app = Celery(
    "tasks",
    broker=settings.REDIS_BROKER_URL,
    backend=settings.REDIS_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)

# ✅ BEAT SCHEDULE - Right here in the same file
celery_app.conf.beat_schedule = {
    "send-congrats-emails-monthly": {
        "task": "send_congrats_emails",
        "schedule": crontab(day_of_month=1, hour=9, minute=0),  # 1st of month at 9 AM
        # "schedule": crontab(minute="*"),  # Uncomment for testing (every minute)
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks(['app.tasks'])
