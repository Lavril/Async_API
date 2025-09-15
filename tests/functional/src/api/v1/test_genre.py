import pytest

from tests.functional.settings import test_settings


@pytest.mark.parametrize(
    'input_data, expected_answer',
    [
        (
            {'genre_id': '2fec4f4f-7f84-475c-ad28-791ce135bd2e'},
            {'status': 200, 'name': 'TestGenre'}
        ),
        (
            {'genre_id': '00000000-0000-0000-0000-000000000000'},
            {'status': 404, 'detail': "genre not found"}
        ),
        (
            {'genre_id': '00000000-0000-0000-0000-0000000000000'},
            {'status': 400, 'detail': "Invalid genre ID format. Must be a valid UUID v4."}
        )
    ]
)
@pytest.mark.asyncio
async def test_get_genre_details(es_write_data, es_data_genres, make_get_request, input_data: dict, expected_answer: dict):
    """Тест получения информации о жанре"""
    await es_write_data(es_data_genres, 'genres')
    genre_id = input_data['genre_id']
    response = await make_get_request('/genres', f'/{genre_id}')
    assert response['status'] == expected_answer['status']
    if response['status'] == 200:
        assert response['body']["uuid"] == genre_id
        assert response['body']["name"] == expected_answer['name']
    else:
        assert response['body']["detail"] == expected_answer['detail']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {},
            {'status': 200, "length": 3}
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
    ]
)
@pytest.mark.asyncio
async def test_list_genres(es_write_data, es_data_genres, make_get_request, query_data: dict, expected_answer: dict):
    """Тест получения списка жанров"""
    await es_write_data(es_data_genres, 'genres')
    response = await make_get_request('/genres', '', query_data)
    assert response['status'] == expected_answer['status']
    assert len(response["body"]) == expected_answer['length']
