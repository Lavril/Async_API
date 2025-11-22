from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from core.config import settings
from db import redis_db as redis
from db import postgres
from routes import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Подключаемся к базам при старте сервера
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)

    # В проде нужно использовать миграции вместо этого. Это только для разработки и тестов
    from models.entity import User  # noqa: F401
    await postgres.create_database()

    yield

    await postgres.purge_database()
    # Отключаемся от баз при завершении работы
    await redis.redis.close()
    await postgres.engine.dispose()


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    redoc_url="/api/redoc",
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


app.include_router(users.router, tags=["Пользователи"])
