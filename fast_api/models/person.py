from uuid import UUID
from typing import List
from pydantic import BaseModel

from .base import BaseDocument


class PersonFilm(BaseModel):
    id: UUID
    roles: List[str]


class Person(BaseDocument):
    full_name: str
