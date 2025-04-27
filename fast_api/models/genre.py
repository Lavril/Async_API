from typing import Optional

from .base import BaseDocument


class Genre(BaseDocument):
    """Модель жанров"""
    name: str
    description: Optional[str] = None
