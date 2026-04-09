# app/tasks/metrics.py
from prometheus_client import Counter, Gauge, Histogram
from celery.signals import task_postrun, task_prerun
from app.tasks.celery_app import celery_app

CELERY_TASKS_TOTAL = Counter('celery_tasks_total', 'Total number of tasks', ['task_name', 'status'])
CELERY_TASKS_ACTIVE = Gauge('celery_tasks_active', 'Number of active tasks')
CELERY_TASK_DURATION = Histogram('celery_task_duration_seconds', 'Task duration', ['task_name'])
CELERY_QUEUE_SIZE = Gauge('celery_queue_size', 'Size of Celery queue')

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, **kw):
    CELERY_TASKS_ACTIVE.inc()

@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, state=None, **kw):
    CELERY_TASKS_ACTIVE.dec()
    if task:
        CELERY_TASKS_TOTAL.labels(task_name=task.name, status=state).inc()
        