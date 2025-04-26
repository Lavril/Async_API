from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Path

from services.film import FilmService, get_film_service
from .models import FilmFullResponse

# Объект router, в котором регистрируем обработчики
router = APIRouter()


@router.get(
    '/{film_id}',
    response_model=FilmFullResponse,
    summary="Получить информацию о кинопроизведении",
    description="Возвращает полную информацию о кинопроизведении по его идентификатору",
    response_description="Объект с информацией о кинопроизведении",)
async def film_details(
        film_id: str = Path(..., example="3d825f60-9fff-4dfe-b294-1a45fa1e115d", description="UUID фильма"),
        film_service: FilmService = Depends(get_film_service)
) -> FilmFullResponse:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return FilmFullResponse(
        uuid=film.uuid,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genres=[genre.model_dump() for genre in film.genres] if film.genres else None,
        actors=[actor.model_dump() for actor in film.actors] if film.actors else None,
        writers=[writer.model_dump() for writer in film.writers] if film.writers else None,
        directors=[director.model_dump() for director in film.directors] if film.directors else None
    )
