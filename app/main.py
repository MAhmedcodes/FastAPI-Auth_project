from fastapi import FastAPI, Request, Response
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.sessions import SessionMiddleware  # Add this import

from app import models
from app.core.config.config import settings
from .database.database import engine
from .routers import users, posts, auth, votes, monitoring, dashboard, prometheus_webhook, oauth  # Add oauth here
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge
import time

# models.Base.metadata.create_all(bind=engine) no need beacuae of alembic

app = FastAPI(
    title="Blog App with Celery Monitoring",
    description="FastAPI Blog App with Background Jobs & Flower Dashboard",
    version="1.0.0") 

# Add SessionMiddleware - THIS IS IMPORTANT FOR OAUTH
app.add_middleware(SessionMiddleware, secret_key= settings.SESSION_SECRET_KEY)

app.include_router(users.router)
app.include_router(posts.router)
app.include_router(auth.router)
app.include_router(votes.router)
app.include_router(monitoring.router)
app.include_router(dashboard.router)
app.include_router(prometheus_webhook.router)
app.include_router(oauth.router)  # Add this line

@app.get("/home")
async def root():
    return {"message" : "Hello Welcome to BLog app",
            "monitoring": {
            "custom_dashboard": "/dashboard",
            "flower_dashboard": f"http://localhost:{settings.FLOWER_PORT}",
            "flower_path": settings.FLOWER_URL_PREFIX,
            "monitoring_api": "/monitoring"
            }
        }

# Create metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
ACTIVE_TASKS = Gauge('celery_active_tasks', 'Number of active Celery tasks')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method, 
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    # Update active tasks gauge
    from app.tasks.celery_app import celery_app
    inspect = celery_app.control.inspect()
    active = inspect.active() or {}
    active_count = sum(len(tasks) for tasks in active.values())
    ACTIVE_TASKS.set(active_count)
    
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
