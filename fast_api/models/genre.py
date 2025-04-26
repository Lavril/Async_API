from typing import Optional

from .base import BaseDocument


class Genre(BaseDocument):
    name: str
    description: Optional[str] = None
