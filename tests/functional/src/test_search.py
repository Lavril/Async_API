import uuid

import aiohttp
import pytest

from ..settings import test_settings


#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий.

@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'query': 'The Star'},
            {'status': 200, 'length': 50}
        ),
        (
            {'query': 'Mashed potato'},
            {'status': 404, 'length': 1}
        )
    ]
)
@pytest.mark.asyncio
async def test_search(es_write_data, query_data, expected_answer):
    # 1. Генерируем данные для ES
    es_data = [{
        'uuid': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'title': 'The Star',
        'description': 'New World',
        'genres': [{'uuid': str(uuid.uuid4()), 'name': 'Action'}, {'uuid': str(uuid.uuid4()), 'name': 'Sci-Fi'}],
        'directors': [{'uuid': str(uuid.uuid4()), 'full_name': 'Stan'}],
        'actors': [
            {'uuid': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'full_name': 'Ann'},
            {'uuid': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'full_name': 'Bob'}
        ],
        'writers': [
            {'uuid': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'full_name': 'Ben'},
            {'uuid': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'full_name': 'Howard'}
        ],
        'directors_names': ['Stan'],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard']
    } for _ in range(60)]

    bulk_query: list[dict] = []
    for row in es_data:
        data = {'_index': 'movies', '_id': row['uuid']}
        data.update({'_source': row})
        bulk_query.append(data)

    # 2. Загружаем данные в ES
    await es_write_data(bulk_query, test_settings.es_index_mapping)

    # 3. Запрашиваем данные из ES по API

    session = aiohttp.ClientSession()
    url = test_settings.fastapi_settings.get_host() + '/api/v1/films/search/'
    async with session.get(url, params=query_data) as response:
        body = await response.json()
        # headers = response.headers
        status = response.status
    await session.close()

    # 4. Проверяем ответ

    assert status == expected_answer['status']
    assert len(body) == expected_answer['length']
