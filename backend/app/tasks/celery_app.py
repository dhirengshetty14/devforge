from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "devforge",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.github_sync",
        "app.tasks.analysis",
        "app.tasks.ai_tasks",
        "app.tasks.generation",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.celery_task_timeout,
    task_soft_time_limit=settings.celery_task_timeout,
    task_default_retry_delay=5,
    broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    result_expires=3600,
)
