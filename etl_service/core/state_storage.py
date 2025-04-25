import abc
import json
from json import JSONDecodeError
import logging
import os
from pathlib import Path
from typing import Any

from filelock import FileLock

from core.settings import settings


class BaseStorage(abc.ABC):
    """Abstract state storage."""
    @abc.abstractmethod
    def save_state(self, state: dict[str, Any]) -> None:
        ...

    @abc.abstractmethod
    def retrieve_state(self) -> dict[str, Any]:
        ...


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


class JsonFileStorage(BaseStorage):
    """Storage realization based on JSON file."""

    def __init__(self, file_path: str | Path = settings.state_path) -> None:
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)
        create_directory('./storage')

    def save_state(self, state: dict[str, Any]) -> None:
        """Save state into storage."""
        lock = FileLock(f'{self.file_path}.lock')
        with lock:
            with open(file=self.file_path, mode='w', encoding='utf-8') as json_storage:
                json.dump(state, json_storage)

    def retrieve_state(self) -> dict[str, Any]:
        """Get state from storage."""
        try:
            lock = FileLock(f'{self.file_path}.lock')
            with lock:
                with open(file=self.file_path, mode='r', encoding='utf-8') as json_storage:
                    return json.load(json_storage)
        except (FileNotFoundError, JSONDecodeError):
            self.logger.warning('No state file provided. Continue with default file')
            return {}
        except Exception as e:
            self.logger.exception(e)
            raise e


class StateManager:
    """Class for work with state."""

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage
        self.state = self.storage.retrieve_state()

    def set_state(self, key: str, value: Any) -> None:
        self.state.update({key: value})
        self.storage.save_state(self.state)

    def get_state(self, key: str) -> Any:
        if self.state.__contains__(key):
            return self.state[key]
        return None
