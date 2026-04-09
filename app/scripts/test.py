# Run this in Python shell
from app.tasks import celery_app

# This will show you the task ID
result = celery_app.send_task('app.tasks.email_task.send_congrats_emails')
print(f"Your task ID is: {result.id}")