from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from services.genre import GenreService, get_genre_service
from .models import Genre

# Объект router, в котором регистрируем обработчики
router = APIRouter()


@router.get(
    '/{genre_id}',
    response_model=Genre,
    summary="Получить информацию о жанре",
    description="Возвращает полную информацию о жанре по его идентификатору",
    response_description="Объект с информацией о жанре")
async def genre_details(
        genre_id: str = Path(..., example="3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff", description="UUID жанра"),
        genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    """Получение информацию о жанре по идентификатору"""
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return Genre(
        uuid=genre.uuid,
        name=genre.name,
        description=genre.description,
    )


@router.get(
    '/',
    response_model=List[Genre],
    summary="Получить список жанров",
    description="Возвращает список жанров с их уникальными идентификаторами",
    response_description="Список жанров",)
async def list_genres(
        page: int = Query(
            1,
            ge=1,
            description="Номер страницы"
        ),
        size: int = Query(
            50,
            ge=1,
            le=100,
            description="Количество элементов на странице (1-100)"
        ),
        genre_service: GenreService = Depends(get_genre_service)
) -> List[Genre]:
    """
    Получить список жанров с возможностью:
    - Пагинации
    """
    genres = await genre_service.get(
        page=page,
        size=size
    )
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genres not found')

    result = []
    for source in genres:
        result.append(Genre(
            uuid=source.uuid,
            name=source.name,
            description=source.description
        ))

    return result
