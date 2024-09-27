import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api import router
from src.utils.redis import init_redis_cache
from src.config import settings


settings.log.configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Init FastAPI cache")
    init_redis_cache()
    yield


app = FastAPI(title="Spimex", lifespan=lifespan)

app.include_router(router, prefix="/api")
