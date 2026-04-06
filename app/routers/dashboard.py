from fastapi.responses import HTMLResponse
from pathlib import Path
from fastapi import APIRouter


router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

# Dashboard HTML endpoint
@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the custom monitoring dashboard"""
    dashboard_path = Path("app/templates/dashboard.html")
    
    if dashboard_path.exists():
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(
            content="<h1>Dashboard not found. Please create dashboard.html</h1>", 
            status_code=404
        )