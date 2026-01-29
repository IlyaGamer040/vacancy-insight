from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "vacancy_tasks",
    broker=settings.REDIS_URL if hasattr(settings, "REDIS_URL") else "redis://localhost:6379/0",
    backend=settings.REDIS_URL if hasattr(settings, "REDIS_URL") else "redis://localhost:6379/0",
    include=["app.tasks.parsing", "app.tasks.notifications"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
)