from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='postgres_')
    host: str = Field(..., alias='POSTGRES_HOST')
    port: int = Field(..., alias='POSTGRES_PORT')
    dbname: str = Field(..., alias='POSTGRES_DB')
    user: str = ...
    password: str = ...

    dbschema: str = 'content'
    tables: list[dict] = [
        {'name': 'film_work', 'batch_size': 100},
        {'name': 'genre', 'batch_size': 1},
        {'name': 'person', 'batch_size': 100},
    ]
    main_table: str = 'film_work'

    def get_dsn(self) -> dict[str, Any]:
        return self.model_dump(
            include={'host', 'port', 'dbname', 'user', 'password'})


class ElasticSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='elastic_')
    host: str = ...
    port: str = ...

    indices: list[str] = ['movies', 'genres', 'persons']

    def get_host(self) -> str:
        return f'http://{self.host}:{self.port}'


class Settings(BaseSettings):
    debug: bool = Field(...)
    main_loop_time: int = 15 * 60
    backoff_time: int = 3 * 60
    state_path: Path = BASE_DIR / 'storage/state_storage.json'
    postgres_settings: PostgresSettings = PostgresSettings()
    elastic_settings: ElasticSettings = ElasticSettings()


settings = Settings()
