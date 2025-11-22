import os
from logging import config as logging_config
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Загружаем .env до создания настроек
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


class Settings(BaseSettings):
    # Переменные прокидываются в окружение контейнера на этапе сборки
    debug: bool = False
    base_dir: Path = Path(__file__).resolve().parent.parent
    project_name: str = os.getenv('PROJECT_NAME', 'auth')

    redis_host: str = os.getenv('REDIS_HOST', '127.0.0.1')
    redis_port: int = int(os.getenv('REDIS_PORT', 6379))

    postgres_user: str = os.getenv('POSTGRES_USER', 'postgres')
    postgres_password: str = os.getenv('POSTGRES_PASSWORD')
    postgres_host: str = os.getenv('POSTGRES_HOST', '127.0.0.1')
    postgres_port: int = int(os.getenv('POSTGRES_PORT', 5432))
    postgres_db: str = os.getenv('POSTGRES_DB', 'auth')


settings = Settings()
