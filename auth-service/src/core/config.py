from logging import config as logging_config
from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import field_validator

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    # Переменные прокидываются в окружение контейнера на этапе сборки
    debug: bool = False
    base_dir: Path = Path(__file__).resolve().parent.parent
    project_name: str = 'auth'

    redis_host: str = '127.0.0.1'
    redis_port: int = 6379

    postgres_user: str = 'postgres'
    postgres_password: str = ""
    postgres_host: str = '127.0.0.1'
    postgres_port: int = 5432
    postgres_db: str = 'auth'

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v or v.strip() == "" or v.strip() == "your-secret-key-change-in-production":
            raise ValueError("SECRET_KEY environment variable must be set to a secure value")
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }


settings = Settings()
