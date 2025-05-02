from .base import BaseDocument
from .genre import Genre
from .person import Person


class Film(BaseDocument):
    """Модель фильмов"""
    title: str
    imdb_rating: float | None = None
    description: str | None = None
    genres: list[Genre] | None = None
    actors: list[Person] | None = None
    writers: list[Person] | None = None
    directors: list[Person] | None = None


class FilmShort(BaseDocument):
    title: str
    imdb_rating: float | None = None
    roles: list[str] = None
