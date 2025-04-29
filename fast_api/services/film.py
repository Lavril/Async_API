import json
from functools import lru_cache
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError, BadRequestError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    """Бизнес-логика по работе с фильмами."""
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Film | None:
        """
        Возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе.

        :param film_id: ID кинопроизведения
        :return: Модель кинопроизведения
        """
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм в кеш
            await self._put_film_to_cache(film)

        return film

    async def get(
            self,
            sort: str,
            genre: UUID | None,
            page: int,
            size: int
    ) -> list[Film] | None:
        """
        Возвращает список фильмов по заданным критериям.

        :param sort: Сортировка по рейтингу IMDB
        :param genre: Жанр
        :param page: Номер страницы
        :param size: Количество записей
        :return: Список фильмов
        """
        return await self._get_films_by_filters(sort, genre, page, size)

    async def search(
            self,
            query: str,
            page: int,
            size: int
    ) -> list[Film] | None:
        """Возвращает список найденных фильмов"""
        query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "description"],
                    "fuzziness": "AUTO"
                }
            },
            "from": (page - 1) * size,
            "size": size
        }

        try:
            doc = await self.elastic.search(
                index="movies",
                body=query
            )
        except BadRequestError:
            return None
        except NotFoundError:
            return None

        return [Film(**hit["_source"]) for hit in doc["hits"]["hits"]]

    async def _get_films_by_filters(
        self,
        sort: str = "-imdb_rating",
        genre: UUID | None = None,
        page: int = 1,
        size: int = 50
    ) -> list[Film] | None:
        """Поиск фильмов по критериям"""
        # Проверяем кэш
        cache_key = await self._get_films_cache_key(sort, genre, page, size)
        cached_films = await self._films_from_cache(cache_key)
        if cached_films:
            return cached_films

        films = await self._get_films_from_elastic(sort, genre, page, size)
        if not films:
            return None

        # Сохраняем в кэш
        await self._put_films_to_cache(cache_key, films)

        return films

    async def _get_films_from_elastic(
            self,
            sort: str,
            genre: UUID | None,
            page: int,
            size: int
    ) -> list[Film] | None:
        """Получение фильмов из elasticsearch по заданным критериям"""
        # Настройки сортировки
        sort_order = "desc" if sort.startswith("-") else "asc"
        sort_field = sort.lstrip("-")

        # Базовый запрос
        query = {
            "query": {
                "bool": {
                    "must": []
                }
            },
            "sort": [
                {sort_field: {"order": sort_order}}
            ],
            "from": (page - 1) * size,
            "size": size
        }

        # Фильтр по жанру
        if genre:
            query["query"]["bool"]["must"].append({
                "nested": {
                    "path": "genres",
                    "query": {
                        "term": {"genres.uuid": str(genre)}
                    }
                }
            })

        try:
            doc = await self.elastic.search(
                index="movies",
                body=query
            )
        except BadRequestError:
            return None
        except NotFoundError:
            return None

        return [Film(**hit["_source"]) for hit in doc["hits"]["hits"]]

    async def _get_film_from_elastic(self, film_id: str) -> Film | None:
        """Получение фильма по ID из elasticsearch"""
        try:
            doc = await self.elastic.get(index='movies', id=film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Film | None:
        """Поиск фильма по ID в кэше redis"""
        data = await self.redis.get(f"film_{film_id}")
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        """Сохранение фильма в кэш redis"""
        await self.redis.set(f"film_{film.uuid}", film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _get_films_cache_key(self, sort: str, genre: UUID | None, page: int, size: int) -> str:
        """Генерация ключа кэша"""
        genre_part = f":genre_{genre}" if genre else ""
        return f"films:sort_{sort}{genre_part}:page_{page}:size_{size}"

    async def _films_from_cache(self, cache_key: str) -> list[Film] | None:
        """Получение фильмов из кэша"""
        data = await self.redis.get(cache_key)
        if not data:
            return None
        return [Film.parse_raw(item) for item in json.loads(data)]

    async def _put_films_to_cache(self, cache_key: str, films: list[Film]):
        """Сохранение фильмов в кэш redis"""
        await self.redis.set(cache_key, json.dumps([film.json() for film in films]), FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    """Провайдер FilmService"""
    return FilmService(redis, elastic)
