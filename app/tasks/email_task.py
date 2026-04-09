# app/tasks/email_task.py
import logging
from sqlalchemy import func
from app.tasks.celery_app import celery_app
from app.database.database import Sessionlocal
from app import models
from app.services.email_service import send_email
from app.utils.email_builder import build_congrats_email_html

logger = logging.getLogger(__name__)

@celery_app.task(name="send_congrats_emails")
def send_congrats_emails():
    """Send congratulatory emails to users with 1000+ votes"""
    logger.info("🚀 Monthly email task started")
    
    db = Sessionlocal()
    try:
        # Find users with 1000+ votes
        top_users = db.query(
            models.Users,
            func.count(models.Votes.post_id).label("total_votes")
        ).join(
            models.Post, models.Post.user_id == models.Users.id
        ).join(
            models.Votes, models.Votes.post_id == models.Post.id
        ).group_by(
            models.Users.id
        ).having(
            func.count(models.Votes.post_id) >= 1000
        ).all()
        
        if not top_users:
            logger.info("No users with 1000+ votes found")
            return {"status": "skipped", "reason": "no qualifying users"}
        
        emails_sent = 0
        for user, vote_count in top_users:
            html_content = build_congrats_email_html(
                username=user.email.split("@")[0],
                email=user.email,
                total_votes=vote_count
            )
            
            send_email(
                to_email=user.email,
                subject="🎉 Congratulations! Your posts reached 1000+ votes!",
                html_body=html_content
            )
            emails_sent += 1
            logger.info(f"✅ Email sent to {user.email} ({vote_count} votes)")
        
        return {
            "status": "success",
            "emails_sent": emails_sent,
            "message": f"Sent {emails_sent} congratulatory emails"
        }
        
    except Exception as e:
        logger.error(f"❌ Task failed: {e}")
        raise
    finally:
        db.close()
        