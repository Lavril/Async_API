import pytest

from tests.functional.settings import test_settings


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
            {'query': 'The Star', 'size': 2},
            {'status': 200, 'length': 2}
        ),
        (
            {'query': 'The Star', 'size': 62},
            {'status': 200, 'length': 60}
        ),
        (
            {'query': 'The Star', 'size': 101},
            {'status': 422, 'length': 1}
        ),
        (
            {'query': 'Mashed potato'},
            {'status': 404, 'length': 1}
        ),
        (
            {'query': ''},
            {'status': 422, 'length': 1}
        ),
        (
            {},
            {'status': 422, 'length': 1}
        ),
        (
            {'page': 0},
            {'status': 422, 'length': 1}
        ),
        (
            {'size': 0},
            {'status': 422, 'length': 1}
        ),
    ]
)
@pytest.mark.asyncio
async def test_search_films(make_get_request, es_write_data, es_data_movies: list[dict], query_data: dict, expected_answer: dict):
    await es_write_data(es_data_movies, 'movies')
    response = await make_get_request('/films', '/search', query_data)
    assert response['status'] == expected_answer['status']
    assert len(response['body']) == expected_answer['length']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'query': 'Stan'},
            {'status': 200, 'length': 10}
        ),
        (
            {'query': 'Stan', 'size': 2},
            {'status': 200, 'length': 2}
        ),
        (
            {'query': 'Stan', 'size': 12},
            {'status': 200, 'length': 10}
        ),
        (
            {'query': 'Stan', 'size': 101},
            {'status': 422, 'length': 1}
        ),
        (
            {'query': 'Ron'},
            {'status': 404, 'length': 1}
        ),
        (
            {'query': ''},
            {'status': 422, 'length': 1}
        ),
        (
            {},
            {'status': 422, 'length': 1}
        ),
        (
            {'page': 0},
            {'status': 422, 'length': 1}
        ),
        (
            {'size': 0},
            {'status': 422, 'length': 1}
        ),
    ]
)
@pytest.mark.asyncio
async def test_search_persons(make_get_request, es_write_data, es_data_persons: list[dict], query_data: dict, expected_answer: dict):
    await es_write_data(es_data_persons, 'persons')
    response = await make_get_request('/persons', '/search', query_data)
    assert response['status'] == expected_answer['status']
    assert len(response['body']) == expected_answer['length']
