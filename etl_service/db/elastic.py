from contextlib import contextmanager
import logging
from typing import Any, Generator

import elasticsearch
from elasticsearch import Elasticsearch, ConnectionError as ESConnectionError

from core.backoff import backoff

#вынесем создание клиента отдельно
class ElasticClientFactory:
    """Create Elasticsearch client with backoff."""
    def __init__(self, dsn: str):
        self.dsn = dsn

    @backoff(ESConnectionError)
    def create(self) -> Elasticsearch:
        client = Elasticsearch(self.dsn)
        if not client.ping():
            raise ESConnectionError("Elasticsearch don't response")
        return client


class ElasticConnector:
    """Elasticsearch context manager connector."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.logger = logging.getLogger(__name__)

    @contextmanager
    def connect(self) -> Generator[Elasticsearch, Any, None]:
        """Elasticsearch context manager."""
        client = None
        try:
            client = self._create_client()
            self.logger.info('Successful connection to Elasticsearch')
            yield client
        except elasticsearch.ConnectionError:
            self.logger.exception('Get connection error from Elasticsearch')
            raise
        finally:
            if client:
                client.close()
                self.logger.info('Close connection with Elasticsearch')
