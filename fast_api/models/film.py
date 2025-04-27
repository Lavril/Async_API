from typing import Optional, List

from .base import BaseDocument
from .genre import Genre
from .person import Person


class Film(BaseDocument):
    """Модель фильмов"""
    title: str
    imdb_rating: Optional[float] = None
    description: Optional[str] = None
    genres: Optional[List[Genre]] = None
    actors: Optional[List[Person]] = None
    writers: Optional[List[Person]] = None
    directors: Optional[List[Person]] = None
