from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
import logging

from app.tasks.celery_app import celery_app
from app.core.config.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

@router.get("/")
async def monitoring_info():
    return {
        "message": "Celery Task Monitoring Dashboard",
        "flower_dashboard": f"http://localhost:{settings.FLOWER_PORT}",
        "api_endpoints": {
            "task_status": "/monitoring/tasks/{task_id}",
            "all_tasks": "/monitoring/tasks",
            "active_tasks": "/monitoring/active-tasks",
            "worker_stats": "/monitoring/workers",
            "scheduled_tasks": "/monitoring/scheduled-tasks",
            "task_history": "/monitoring/task-history",
            "revoke_task": "/monitoring/tasks/{task_id}/revoke"
        }
    }

@router.get("/tasks")
async def get_all_tasks(limit: int = 100):
    try:
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active() or {}
        scheduled_tasks = inspect.scheduled() or {}
        reserved_tasks = inspect.reserved() or {}
        all_tasks = {
            "active": active_tasks,
            "scheduled": scheduled_tasks,
            "reserved": reserved_tasks,
            "total_active_count": sum(len(tasks) for tasks in active_tasks.values()),
            "total_scheduled_count": sum(len(tasks) for tasks in scheduled_tasks.values()),
            "total_reserved_count": sum(len(tasks) for tasks in reserved_tasks.values())
        }
        return all_tasks
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get detailed status of a specific task"""
    task_result  = AsyncResult(task_id, app=celery_app)  #it is celery onject that fatches the status of task ie pending or not etc
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
        "ready": task_result.ready(), #either success or none
        "successful": task_result.successful() if task_result.ready() else None,
        "failed": task_result.failed() if task_result.ready() else None,
    }
    
    # Add result if available
    if task_result.ready() and task_result.successful():
        response["result"] = task_result.result
        response["runtime"] = getattr(task_result, "runtime", None)
    
    # Add error if failed
    if task_result.failed():
        response["error"] = str(task_result.info)
        response["traceback"] = task_result.traceback if hasattr(task_result, 'traceback') else None
    
    # Add task info if available
    if task_result.info and isinstance(task_result.info, dict):
        if "current" in task_result.info:
            response["progress"] = task_result.info
    
    # Get task metadata
    try:
        # This requires celery.result.backend to support get_task_meta
        if hasattr(task_result, '_get_task_meta'):
            meta = task_result._get_task_meta()
            response["metadata"] = {
                "date_done": str(meta.get('date_done', '')),
                "worker": meta.get('worker', ''),
                "retries": meta.get('retries', 0)
            }
    except:
        pass
    
    return response

@router.get("/active-tasks")
async def get_active_tasks():
    """Get all currently running tasks"""
    try:
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active() or {}
        
        # Format the response
        formatted_tasks = []
        for worker, tasks in active_tasks.items():
            for task in tasks:
                formatted_tasks.append({
                    "worker": worker,
                    "task_id": task.get("id"),
                    "name": task.get("name"),
                    "args": task.get("args"),
                    "kwargs": task.get("kwargs"),
                    "started_at": task.get("time_start"),
                    "hostname": task.get("hostname")
                })
        
        return {
            "count": len(formatted_tasks),
            "tasks": formatted_tasks
        }
    except Exception as e:
        logger.error(f"Error fetching active tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scheduled-tasks")
async def get_scheduled_tasks():
    """Get all scheduled/queued tasks"""
    try:
        inspect = celery_app.control.inspect()
        scheduled_tasks = inspect.scheduled() or {}
        reserved_tasks = inspect.reserved() or {}
        
        return {
            "scheduled": scheduled_tasks,
            "reserved": reserved_tasks,
            "total_scheduled": sum(len(tasks) for tasks in scheduled_tasks.values()),
            "total_reserved": sum(len(tasks) for tasks in reserved_tasks.values())
        }
    except Exception as e:
        logger.error(f"Error fetching scheduled tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workers")
async def get_worker_stats():
    """Get statistics about all Celery workers"""
    try:
        inspect = celery_app.control.inspect()
        
        stats = {
            "available_workers": [],
            "stats": {},
            "active_queues": {},
            "registered_tasks": {},
            "total_workers": 0
        }
        
        # Get worker stats
        worker_stats = inspect.stats() or {}
        stats["stats"] = worker_stats
        stats["total_workers"] = len(worker_stats)
        
        # Get active queues
        active_queues = inspect.active_queues() or {}
        stats["active_queues"] = active_queues
        
        # Get registered tasks
        registered = inspect.registered() or {}
        stats["registered_tasks"] = registered
        
        # Get worker ping
        ping_response = celery_app.control.ping()
        stats["available_workers"] = [w.get('hostname') for w in ping_response if w]
        
        # Format detailed worker info
        workers_detail = []
        for worker_name in worker_stats.keys():
            workers_detail.append({
                "name": worker_name,
                "stats": worker_stats.get(worker_name, {}),
                "queues": active_queues.get(worker_name, []),
                "registered_tasks_count": len(registered.get(worker_name, [])),
                "status": "online" if worker_name in stats["available_workers"] else "offline"
            })
        
        stats["workers_detail"] = workers_detail
        
        return stats
    except Exception as e:
        logger.error(f"Error fetching worker stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/{task_id}/revoke")
async def revoke_task(task_id: str, terminate: bool = False):
    """Revoke/cancel a running or pending task"""
    try:
        celery_app.control.revoke(task_id, terminate=terminate)
        
        return {
            "task_id": task_id,
            "status": "revoked",
            "terminate": terminate,
            "message": f"Task {task_id} has been {'terminated' if terminate else 'revoked'}"
        }
    except Exception as e:
        logger.error(f"Error revoking task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/email/send-now")
async def trigger_email_task_manually(background_tasks: BackgroundTasks):
    """Manually trigger the congrats email task (for testing)"""
    # Run task asynchronously
    task = celery_app.send_task('app.tasks.email_task.send_congrats_to_top_posters')
    return {
        "message": "Email task triggered manually",
        "task_id": task.id,
        "status": "started",
        "monitor_url": f"http://localhost:{settings.FLOWER_PORT}/task/{task.id}"
    }

@router.get("/queue-length")
async def get_queue_length():
    """Get approximate queue length"""
    try:
        inspect = celery_app.control.inspect()
        
        # Get active and reserved tasks
        active = inspect.active() or {}
        reserved = inspect.reserved() or {}
        
        active_count = sum(len(tasks) for tasks in active.values())
        reserved_count = sum(len(tasks) for tasks in reserved.values())
        
        # Try to get queue size from broker (Redis)
        redis_queue_size = 0
        try:
            import redis
            redis_client = redis.from_url(settings.REDIS_BROKER_URL)
            # Get queue size from default queue
            redis_queue_size = redis_client.llen('celery') or 0
        except:
            pass
        
        return {
            "active_tasks": active_count,
            "reserved_tasks": reserved_count,
            "total_pending": active_count + reserved_count,
            "redis_queue_size": redis_queue_size,
            "workers_available": len(active.keys())
        }
    except Exception as e:
        logger.error(f"Error getting queue length: {e}")
        return {"error": str(e)}

@router.get("/task-history")
async def get_task_history(limit: int = 50):
    """
    Get recent task history (requires result backend)
    Note: This is limited - for full history, use Flower's API
    """
    try:
        # This is a simplified version
        # For production, consider storing task results in a database
        inspect = celery_app.control.inspect()
        
        # Get recently completed tasks from stats
        stats = inspect.stats() or {}
        
        history = []
        for worker, worker_stats in stats.items():
            history.append({
                "worker": worker,
                "total_tasks": worker_stats.get('total', 0),
                "tasks_by_type": worker_stats.get('tasks', {}),
                "broker_messages": worker_stats.get('broker', {}).get('messages', 0)
            })
        
        return {
            "limit": limit,
            "history": history,
            "note": "For detailed task history, use Flower dashboard or implement custom storage"
        }
    except Exception as e:
        logger.error(f"Error fetching task history: {e}")
        return {"error": str(e)}

@router.get("/flower")
async def redirect_to_flower():
    """Redirect to Flower dashboard"""
    flower_url = f"http://{settings.FLOWER_HOST}:{settings.FLOWER_PORT}"
    return RedirectResponse(url=flower_url)

