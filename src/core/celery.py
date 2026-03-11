from celery import Celery

from src.core.config import srcsettings

celery_app = Celery(
    "task_tracker",
    broker=srcsettings.REDIS_URL,
    backend=srcsettings.REDIS_URL,
    include=["src.services.task_email"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)

celery_app.conf.beat_schedule = {
    "send-daily-summary-email": {
        "task": "src.services.task_email.send_daily_summary_email",
        "schedule": 10.0,
    }
}
