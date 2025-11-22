from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from core.config import settings
from db import redis_db as redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Подключаемся к базам при старте сервера
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    yield
    # Отключаемся от баз при завершении работы
    await redis.redis.close()

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    redoc_url="/api/redoc",
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)
