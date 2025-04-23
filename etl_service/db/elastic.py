from contextlib import contextmanager
import logging

import elasticsearch
from elasticsearch import Elasticsearch

from core.backoff import backoff


class ElasticConnector:
    """Подключение к Elasticsearch."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.logger = logging.getLogger(__name__)

    @backoff(elasticsearch.ConnectionError, max_time=100)
    def _create_client(self):
        """Метод для подключения с backoff."""
        client = Elasticsearch(self.dsn)
        if not client.ping():
            raise elasticsearch.ConnectionError("Elasticsearch не доступен")
        return client

    @contextmanager
    def connect(self):
        """Контекстный менеджер для подключения к Elasticsearch."""
        client = None
        try:
            client = self._create_client()
            self.logger.info("Подключение с Elasticsearch установлено")
            yield client
        except elasticsearch.ConnectionError:
            self.logger.exception("Ошибка в Elasticsearch")
            raise
        finally:
            if client:
                client.close()
                self.logger.info("Соединение с Elasticsearch закрыто")

    def create_index_if_not_exists(self, index: str, index_body: dict):
        """Создать индекс если он не существует."""
        with self.connect() as client:
            try:
                if not client.indices.exists(index=index):
                    client.indices.create(index=index, body=index_body)
                    self.logger.info(f"Created index {index}")
            except Exception:
                self.logger.exception("Failed to create index")
                raise
