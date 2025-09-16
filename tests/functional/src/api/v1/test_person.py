from http import HTTPStatus

import pytest

from tests.functional.settings import test_settings


@pytest.mark.parametrize(
    'input_data, expected_answer',
    [
        (
            {'person_id': '3a6ed55e-6aef-4cd2-932c-808495182425'},
            {'status': HTTPStatus.OK, 'full_name': 'James'}
        ),
        (
            {'person_id': '00000000-0000-0000-0000-000000000000'},
            {'status': HTTPStatus.NOT_FOUND, 'detail': "person not found"}
        ),
        (
            {'person_id': '00000000-0000-0000-0000-0000000000000'},
            {'status': HTTPStatus.BAD_REQUEST, 'detail': "Invalid person ID format. Must be a valid UUID v4."}
        )
    ]
)
@pytest.mark.asyncio
async def test_get_person_details(es_write_data, es_data_persons, make_get_request, input_data: dict, expected_answer: dict):
    """Тест получения информации о персоне."""
    await es_write_data(es_data_persons, 'persons')
    person_id = input_data['person_id']
    response = await make_get_request('/persons', f'/{person_id}')
    assert response['status'] == expected_answer['status']
    if response['status'] == HTTPStatus.OK:
        assert response['body']["uuid"] == person_id
        assert response['body']["full_name"] == expected_answer['full_name']
    else:
        assert response['body']["detail"] == expected_answer['detail']


@pytest.mark.parametrize(
    'input_data, expected_answer',
    [
        (
            {'person_id': '88c78458-54c8-455f-846e-82734dc1967f'},
            {'status': HTTPStatus.OK, 'full_name': 'Maxim', 'title': 'The movie', 'imdb_rating': 8.7}
        ),
        (
            {'person_id': '00000000-0000-0000-0000-000000000000'},
            {'status': HTTPStatus.NOT_FOUND, 'detail': "films not found"}
        ),
        (
            {'person_id': '00000000-0000-0000-0000-0000000000000'},
            {'status': HTTPStatus.BAD_REQUEST, 'detail': "Invalid person ID format. Must be a valid UUID v4."}
        ),
        (
            {'person_id': '3a6ed55e-6aef-4cd2-932c-808495182425'},
            {'status': HTTPStatus.NOT_FOUND, 'detail': "films not found"}
        )
    ]
)
@pytest.mark.asyncio
async def test_person_films(es_write_data, es_data_movies, make_get_request, input_data: dict, expected_answer: dict):
    """Тест получения списка фильмов"""
    await es_write_data(es_data_movies, 'movies')
    person_id = input_data['person_id']
    response = await make_get_request('/persons', f'/{person_id}/films')
    assert response['status'] == expected_answer['status']
    if response['status'] == HTTPStatus.OK:
        film_response = response['body'][0]
        assert film_response["uuid"] == '608c4567-0b8a-49a0-88fb-82770c5b2f61'
        assert film_response["title"] == expected_answer['title']
        assert film_response["imdb_rating"] == expected_answer['imdb_rating']
    else:
        assert response['body']["detail"] == expected_answer['detail']
