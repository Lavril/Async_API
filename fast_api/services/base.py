from abc import ABC, abstractmethod


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
