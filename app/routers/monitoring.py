# app/routers/monitoring.py
from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from app.tasks.celery_app import celery_app
from app.tasks.email_task import send_congrats_emails

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

@router.get("/")
async def monitoring_info():
    """Simple monitoring info"""
    return {
        "message": "Celery Task Monitor",
        "flower_url": "http://localhost:5555",
        "endpoints": {
            "trigger_email": "POST /monitoring/trigger-email",
            "task_status": "GET /monitoring/task/{task_id}",
            "all_tasks": "GET /monitoring/tasks",
            "schedules": "GET /monitoring/schedules"
        }
    }

@router.get("/schedules")
async def get_schedules():
    """View current beat schedule"""
    schedule = celery_app.conf.beat_schedule
    return {
        "schedules": {
            name: {
                "task": config["task"],
                "schedule": str(config["schedule"]),
                "enabled": True
            }
            for name, config in schedule.items()
        }
    }

@router.get("/tasks")
async def get_all_tasks():
    """Get all running tasks"""
    try:
        inspect = celery_app.control.inspect()
        
        active = inspect.active() or {}
        scheduled = inspect.scheduled() or {}
        reserved = inspect.reserved() or {}
        
        return {
            "active_tasks": active,
            "scheduled_tasks": scheduled,
            "reserved_tasks": reserved,
            "stats": {
                "active_count": sum(len(t) for t in active.values()),
                "scheduled_count": sum(len(t) for t in scheduled.values()),
                "reserved_count": sum(len(t) for t in reserved.values())
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a specific task"""
    task = AsyncResult(task_id, app=celery_app)
    
    result = {
        "task_id": task_id,
        "status": task.status,
        "ready": task.ready(),
    }
    
    if task.ready():
        if task.successful():
            result["result"] = task.result
        else:
            result["error"] = str(task.info)
    
    return result

@router.post("/trigger-email")
async def trigger_email_task():
    """Manually trigger the email task"""
    task = celery_app.send_task('app.tasks.email_task.send_congrats_to_top_posters')
    return {
        "message": "Email task started",
        "task_id": task.id,
        "check_status": f"/monitoring/task/{task.id}"
    }
