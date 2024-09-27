import asyncio

from celery import Celery
from celery.schedules import crontab
from fastapi_cache import FastAPICache

from src.config import settings
from src.utils.redis import init_redis_cache


celery_app = Celery(
    "tasks", broker=f"redis://{settings.redis.HOST}:{settings.redis.PORT}/0"
)
celery_app.conf.timezone = "Europe/Moscow"


@celery_app.task
def clear_cache():
    init_redis_cache()
    asyncio.run(FastAPICache.clear())


celery_app.conf.beat_schedule = {
    "reset-cache-every-day-at-14-11": {
        "task": "src.utils.celery.clear_cache",
        "schedule": crontab(hour="14", minute="11"),
    },
}
