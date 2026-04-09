# app/tasks/__init__.py
from app.tasks.celery_app import celery_app
from app.tasks.email_task import send_congrats_emails

__all__ = ['celery_app', 'send_congrats_emails']
