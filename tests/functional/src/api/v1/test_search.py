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
            {'query': 'Mashed potato'},
            {'status': 404, 'length': 1}
        )
    ]
)
@pytest.mark.asyncio
async def test_search(make_get_request, es_write_data, es_data: list[dict], query_data: dict, expected_answer: dict):
    await es_write_data(es_data, test_settings.es_index_mapping)
    response = await make_get_request('/films', '/search', query_data)
    assert response['status'] == expected_answer['status']
    assert len(response['body']) == expected_answer['length']
