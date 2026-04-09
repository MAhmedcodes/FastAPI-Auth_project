import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.tasks.celery_app import celery_app
from app.database.database import Sessionlocal
from app import models
from app.services.email_service import send_email
from app.utils.email_builder import build_congrats_email_html

logger = logging.getLogger(__name__)

@celery_app.task(
    bind=True,
    name="app.tasks.email_task.send_congrats_to_top_posters",
    max_retries=3,
    default_retry_delay=60,
)
def send_congrats_to_top_posters(self):
    logger.info("🚀 [Task Started] send_congrats_to_top_posters")
    
    # DB session is only created here; no need to assign None initially
    try:
        with Sessionlocal() as db:  # context manager auto-closes session
            top_posters = (
                db.query(
                    models.Users,
                    func.count(models.Votes.post_id).label("total_votes")
                )
                .join(models.Post, models.Post.user_id == models.Users.id)
                .join(models.Votes, models.Votes.post_id == models.Post.id)
                .group_by(models.Users.id)
                .having(func.count(models.Votes.post_id) >= 1000)
                .all()
            )

            if not top_posters:
                logger.info("i️  No users with 1000+ votes found. Skipping.")
                return {"status": "skipped", "reason": "no qualifying users"}

            logger.info(f"✅ Found {len(top_posters)} user(s) with 1000+ votes.")
            for user, total in top_posters:
                html_content = build_congrats_email_html(
                    username=user.email.split("@")[0],  # fallback username
                    email=user.email,
                    total_votes=total,
                )
                send_email(
                    to_email=user.email,
                    subject="🎉 Congratulations! Your posts are on fire!",
                    html_body=html_content,
                )

                logger.info(
                    f"📧 Congrats email sent to {user.email} "
                    f"(total votes: {total})"
                )

            return {"status": "success", "emails_sent": len(top_posters)}

    except Exception as exc:
        logger.error(f"❌ Task failed: {exc}", exc_info=True)
        raise self.retry(exc=exc)
