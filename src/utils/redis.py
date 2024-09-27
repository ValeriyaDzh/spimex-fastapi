from redis import asyncio as aioredis

from src.config import settings

redis = aioredis.from_url(
    f"redis://{settings.redis.HOST}", encoding="utf8", decode_responses=True
)
