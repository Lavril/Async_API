import asyncio

from elasticsearch import AsyncElasticsearch
import pytest_asyncio
from elasticsearch.helpers import async_bulk

from .settings import test_settings


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(name='es_client', scope='session')
async def es_client():
    es_client = AsyncElasticsearch(hosts=test_settings.elastic_settings.get_host(), verify_certs=False)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name='es_write_data')
async def es_write_data(es_client):
    """Фикстура для записи тестовых данных в Elasticsearch"""
    async def inner(data: list[dict], MAPPING_MOVIES=None):
        if await es_client.indices.exists(index=test_settings.es_index):
            await es_client.indices.delete(index=test_settings.es_index)
        await es_client.indices.create(index=test_settings.es_index, **MAPPING_MOVIES)

        updated, errors = await async_bulk(client=es_client, actions=data)
        await es_client.indices.refresh()

        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner
