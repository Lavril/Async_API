from http import HTTPStatus
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.film import FilmService, get_film_service

# Объект router, в котором регистрируем обработчики
router = APIRouter()

# FastAPI в качестве моделей использует библиотеку pydantic
# https://pydantic-docs.helpmanual.io
# У неё есть встроенные механизмы валидации, сериализации и десериализации
# Также она основана на дата-классах


class Person(BaseModel):
    uuid: str
    full_name: str


class Genre(BaseModel):
    uuid: str
    name: str
    description: Optional[str] = None


# Модель ответа API
class Film(BaseModel):
    uuid: str
    title: str
    imdb_rating: Optional[float] = None
    pg_rating: Optional[float] = None
    description: Optional[str] = None
    genres: Optional[List[Genre]] = None
    actors: Optional[List[Person]] = None
    writers: Optional[List[Person]] = None
    directors: Optional[List[Person]] = None


# С помощью декоратора регистрируем обработчик film_details
# На обработку запросов по адресу <some_prefix>/some_id
# Позже подключим роутер к корневому роутеру
# И адрес запроса будет выглядеть так — /api/v1/film/some_id
# В сигнатуре функции указываем тип данных, получаемый из адреса запроса (film_id: str)
# И указываем тип возвращаемого объекта — Film
@router.get(
    '/{film_id}',
    response_model=Film,
    summary="Поиск кинопроизведений по UUID",
    description="Поиск кинопроизведений по UUID",
    response_description="Название и рейтинг фильма",)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    print(f"Film object: {film}")  # Для отладки
    print(f"Film type: {type(film)}")  # Для отладки
    print(f"Film type: {film.uuid}")  # Для отладки
    print(f"Film type: {type(film.uuid)}")  # Для отладки
    print(f"Film type: {film.title}")  # Для отладки
    print(f"Film type: {type(film.title)}")  # Для отладки
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum    # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    # Перекладываем данные из models.Film в Film
    # Обратите внимание, что у модели бизнес-логики есть поле description,
    # которое отсутствует в модели ответа API.
    # Если бы использовалась общая модель для бизнес-логики и формирования ответов API,
    # вы бы предоставляли клиентам данные, которые им не нужны
    # и, возможно, данные, которые опасно возвращать
    return Film(
        uuid=film.uuid,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genres=[genre.model_dump() for genre in film.genres] if film.genres else None,
        actors=[actor.model_dump() for actor in film.actors] if film.actors else None,
        writers=[writer.model_dump() for writer in film.writers] if film.writers else None,
        directors=[director.model_dump() for director in film.directors] if film.directors else None
    )
