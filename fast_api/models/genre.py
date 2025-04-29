from .base import BaseDocument


class Genre(BaseDocument):
    """Модель жанров"""
    name: str
    description: str | None = None
