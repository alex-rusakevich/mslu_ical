from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from src.api.endpoints import router
from src.config.logging import setup_logging
from src.config.settings import settings
from src.utils.project_version import get_project_version


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(settings.REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix=settings.REDIS_PREFIX, expire=settings.REDIS_DEFAULT_TIMEOUT)
    yield


setup_logging()
app = FastAPI(
    title="MSLU ICal",
    description="MSLU ICal API documentation",
    version=get_project_version(),
    lifespan=lifespan
)
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Welcome to the API",
        "documentation": "/docs",
        "redoc": "/redoc"
    }
