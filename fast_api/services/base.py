from abc import ABC, abstractmethod
from collections.abc import Awaitable
from datetime import timedelta


class Service(ABC):
    """Абстрактный класс для работы с сущностями API."""
    @abstractmethod
    async def get_by_id(self, item_id: str):
        pass


class GetMixin(ABC):
    """Миксин для функции получения нескольких сущностей."""
    @abstractmethod
    async def get(self, *args, **kwargs):
        pass


class SearchMixin(ABC):
    """Миксин для функции поиска сущности."""
    @abstractmethod
    async def search(self, *args, **kwargs):
        pass


class Cache(ABC):
    """Абстрактный класс для работы с кэшем."""
    @abstractmethod
    async def get(self,
            name: bytes | str | memoryview) -> Awaitable:
        pass

    @abstractmethod
    async def set(self,
            name: bytes | str | memoryview,
            value: bytes | memoryview | str | int | float,
            ex: int | timedelta | None = None) -> Awaitable:
        pass
