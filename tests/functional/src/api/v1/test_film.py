import pytest

from tests.functional.settings import test_settings


@pytest.mark.parametrize(
    'input_data, expected_answer',
    [
        (
            {'film_id': '608c4567-0b8a-49a0-88fb-82770c5b2f61'},
            {'status': 200, 'title': 'The movie'}
        ),
        (
            {'film_id': '00000000-0000-0000-0000-000000000000'},
            {'status': 404, 'detail': "film not found"}
        ),
        (
            {'film_id': '00000000-0000-0000-0000-0000000000000'},
            {'status': 400, 'detail': "Invalid film ID format. Must be a valid UUID v4."}
        )
    ]
)
@pytest.mark.asyncio
async def test_get_film_details(es_write_data, es_data_movies, make_get_request, input_data: dict, expected_answer: dict):
    """Тест получения информации о фильме"""
    await es_write_data(es_data_movies, 'movies')
    film_id = input_data['film_id']
    response = await make_get_request('/films', f'/{film_id}')
    assert response['status'] == expected_answer['status']
    if response['status'] == 200:
        assert response['body']["uuid"] == film_id
        assert response['body']["title"] == expected_answer['title']
    else:
        assert response['body']["detail"] == expected_answer['detail']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {},
            {'status': 200, "length": 50}
        ),
        (
            {"genre": '2fec4f4f-7f84-475c-ad28-791ce135bd2e'},
            {'status': 200, "length": 1}
        ),
        (
            {"genre": '00000000-0000-0000-0000-000000000000'},
            {'status': 404, "length": 1}
        ),
        (
            {"genre": '00000000-0000-0000-0000-0000000000000'},
            {'status': 422, "length": 1}
        ),
        (
            {"page": 0},
            {'status': 422, "length": 1}
        ),
        (
            {"page": 10000},
            {'status': 404, "length": 1}
        ),
        (
            {"size": 0},
            {'status': 422, "length": 1}
        ),
        (
            {"size": 2},
            {'status': 200, "length": 2}
        ),
        (
            {"size": 101},
            {'status': 422, "length": 1}
        ),
        (
            {"sort": "random"},
            {'status': 422, "length": 1}
        )
    ]
)
@pytest.mark.asyncio
async def test_list_films(es_write_data, es_data_movies, make_get_request, query_data: dict, expected_answer: dict):
    """Тест получения списка фильмов"""
    await es_write_data(es_data_movies, 'movies')
    response = await make_get_request('/films', '', query_data)
    assert response['status'] == expected_answer['status']
    assert len(response["body"]) == expected_answer['length']
