from .base import BaseDocument


class Person(BaseDocument):
    """Модель персон"""
    full_name: str
    films: list | None = None
