import datetime as dt
import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


MIN_DT = dt.datetime(1, 1, 1, 0, 0)
START_DT = dt.datetime.now()

BASE_DIR = Path(__file__).resolve().parent.parent


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='postgres_')
    host: str = Field(..., alias='POSTGRES_HOST')
    port: int = Field(..., alias='POSTGRES_PORT')
    dbname: str = Field(..., alias='POSTGRES_DB')
    user: str = ...
    password: str = ...

    postgres_schema: str = 'content'

    def get_dsn(self) -> dict:
        return self.model_dump(
            include={'host', 'port', 'dbname', 'user', 'password'}
        )


class ElasticSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='elastic_')
    host: str = ...
    port: str = ...

    indies: list[str] = ['movies']

    def get_host(self):
        return f'http://{self.host}:{self.port}'


class Settings(BaseSettings):
    debug: bool = Field(...)
    postgres_settings: PostgresSettings = PostgresSettings()
    elastic_settings: ElasticSettings = ElasticSettings()


settings = Settings()


MAIN_TABLE = {
        'name': 'film_work',
        'batch_size': 100
    }
RELATED_TABLES = [
    {
        'name': 'person',
        'batch_size': 100
    },
    {
        'name': 'genre',
        'batch_size': 1
    },
]
PERSON_ROLES = [
    'director',
    'actor',
    'writer'
]

STATE_STORAGE = BASE_DIR / 'state/state_storage.json'
STATE_SCHEMA = {
    'main_key': ('last_filmwork', dt.datetime.min),
    'additional_keys': [
        ('last_person', dt.datetime.min),
        ('last_genre', dt.datetime.min),
    ]
}

BASE_BATCH_SIZE = 100

MAIN_LOOP_TIME = 900
BACKOFF_TIME = 300
