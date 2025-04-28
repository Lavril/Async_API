from typing import Optional, List
from .base import BaseDocument


class Person(BaseDocument):
    """Модель персон"""
    full_name: str
    films: Optional[List] = None
