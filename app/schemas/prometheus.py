from pydantic import BaseModel

class AlertWebhook(BaseModel):
    status: str
    alerts: list = []
