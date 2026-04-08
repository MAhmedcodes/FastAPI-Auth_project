from fastapi import APIRouter, HTTPException
from app import schemas
from app.tasks.celery_app import celery_app

router = APIRouter(prefix="/prometheus", tags=["Prometheus"])


@router.post("/webhook")
async def prometheus_webhook(alert: schemas.AlertWebhook):
    """Trigger tasks when Prometheus alert fires"""
    for alert_item in alert.alerts:
        labels = alert_item.get('labels', {})
        
        # Trigger email task when queue is empty
        if labels.get('alertname') == 'CeleryQueueEmpty':
            task = celery_app.send_task('app.tasks.email_task.send_congrats_to_top_posters')
            return {"triggered": True, "task_id": task.id}
    
    return {"triggered": False}

@router.post("/trigger/{task_name}")
async def trigger_task(task_name: str):
    """Manually trigger task from Prometheus"""
    if task_name == "send_congrats_to_top_posters":
        task = celery_app.send_task('app.tasks.email_task.send_congrats_to_top_posters')
        return {"task_id": task.id, "status": "started"}
    
    raise HTTPException(404, "Task not found")
