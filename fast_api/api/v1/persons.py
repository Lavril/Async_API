from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from services.person import PersonService, get_person_service
from .models import PersonFullResponse, PersonFilms

# Объект router, в котором регистрируем обработчики
router = APIRouter()


@router.get(
    '/{person_id}',
    response_model=PersonFullResponse,
    summary="Получить информацию о персоне",
    description="Возвращает информацию о персоне по его идентификатору",
    response_description="Объект с информацией о персоне")
async def person_details(
        person_id: str = Path(..., example="5b4bf1bc-3397-4e83-9b17-8b10c6544ed1", description="UUID персоны"),
        person_service: PersonService = Depends(get_person_service)
) -> PersonFullResponse:
    """Получение информацию о person по идентификатору"""
    try:
        UUID(person_id, version=4)
    except ValueError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid person ID format. Must be a valid UUID v4."
        )
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return PersonFullResponse(
        uuid=person.uuid,
        full_name=person.full_name,
        films=[film for film in person.films] if person.films else None,
    )


@router.get(
    '/{person_id}/films',
    response_model=list[PersonFilms],
    summary="Получить список фильмов персоны",
    description="Возвращает список из короткой информации по кинопроизведениям персоны",
    response_description="Список кинопроизведений персоны с короткой информацией",)
async def list_films(
        person_id: str = Path(..., example="5b4bf1bc-3397-4e83-9b17-8b10c6544ed1", description="UUID персоны"),
        person_service: PersonService = Depends(get_person_service)
) -> list[PersonFilms]:
    try:
        UUID(person_id, version=4)
    except ValueError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid person ID format. Must be a valid UUID v4."
        )

    films = await person_service.get_film_by_id(person_id)

    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')

    result = []
    for source in films:
        result.append(PersonFilms(
            uuid=source.uuid,
            title=source.title,
            imdb_rating=source.imdb_rating
        ))

    return result


@router.get(
    "/search/",
    response_model=list[PersonFullResponse],
    summary="Поиск персон",
    description="Полнотекстовый поиск персон по имени",
    response_description="Роли и фильмы персон",
)
async def search_films(
        query: str = Query(..., min_length=2, description="Поисковый запрос"),
        page: int = Query(1, ge=1, description="Номер страницы"),
        size: int = Query(50, ge=1, le=100, description="Количество элементов"),
        person_service: PersonService = Depends(get_person_service)
) -> list[PersonFullResponse]:

    persons = await person_service.search(
        query=query,
        page=page,
        size=size
    )

    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')

    result = []
    for source in persons:
        result.append(PersonFullResponse(
            uuid=source.uuid,
            full_name=source.full_name,
            films=source.films
        ))

    return result
