from http import HTTPStatus

import pytest

from tests.functional.settings import test_settings


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'query': 'The Star'},
            {'status': HTTPStatus.OK, 'length': 50}
        ),
        (
            {'query': 'The Star', 'size': 2},
            {'status': HTTPStatus.OK, 'length': 2}
        ),
        (
            {'query': 'The Star', 'size': 62},
            {'status': HTTPStatus.OK, 'length': 60}
        ),
        (
            {'query': 'The Star', 'size': 101},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1}
        ),
        (
            {'query': 'Mashed potato'},
            {'status': HTTPStatus.NOT_FOUND, 'length': 1}
        ),
        (
            {'query': ''},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1}
        ),
        (
            {},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1}
        ),
        (
            {'page': 0},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1}
        ),
        (
            {'size': 0},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1}
        ),
    ]
)
@pytest.mark.asyncio
async def test_search_films(make_get_request, es_write_data, es_data_movies: list[dict], query_data: dict, expected_answer: dict):
    """Тест поиска фильма"""
    await es_write_data(es_data_movies, 'movies')

    response = await make_get_request('/films', '/search', query_data)

    assert response['status'] == expected_answer['status']
    assert len(response['body']) == expected_answer['length']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'query': 'Stan'},
            {'status': HTTPStatus.OK, 'length': 10}
        ),
        (
            {'query': 'Stan', 'size': 2},
            {'status': HTTPStatus.OK, 'length': 2}
        ),
        (
            {'query': 'Stan', 'size': 12},
            {'status': HTTPStatus.OK, 'length': 10}
        ),
        (
            {'query': 'Stan', 'size': 101},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1}
        ),
        (
            {'query': 'Ron'},
            {'status': HTTPStatus.NOT_FOUND, 'length': 1}
        ),
        (
            {'query': ''},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1}
        ),
        (
            {},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1}
        ),
        (
            {'page': 0},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1}
        ),
        (
            {'size': 0},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1}
        ),
    ]
)
@pytest.mark.asyncio
async def test_search_persons(make_get_request, es_write_data, es_data_persons: list[dict], query_data: dict, expected_answer: dict):
    """Тест поиска персоны"""
    await es_write_data(es_data_persons, 'persons')

    response = await make_get_request('/persons', '/search', query_data)

    assert response['status'] == expected_answer['status']
    assert len(response['body']) == expected_answer['length']
