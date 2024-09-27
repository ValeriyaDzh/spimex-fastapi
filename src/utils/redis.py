from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from src.config import settings

redis = aioredis.from_url(
    f"redis://{settings.redis.HOST}", encoding="utf8", decode_responses=True
)


def init_redis_cache() -> None:
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
