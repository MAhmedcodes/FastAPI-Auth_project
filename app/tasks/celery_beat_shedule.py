from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {

    "send-congrats-email-to-top-vote_getter": {

        "task": "app.tasks.email_task.send_congrats_to_top_posters",
        # "schedule": crontab(),  # every minute — TESTING

        # ── MONTHLY (uncomment when ready for prod) ──
        "schedule": crontab(day_of_month=1, hour=9, minute=0),
        # ↑ Runs on the 1st of every month at 9:00 AM UTC
    },
}
