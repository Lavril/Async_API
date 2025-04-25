from contextlib import contextmanager
import logging
from typing import Any, Generator

import elasticsearch
from elasticsearch import Elasticsearch

from core.backoff import backoff


class ElasticConnector:
    """Elasticsearch context manager connector."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.logger = logging.getLogger(__name__)

    @backoff(elasticsearch.ConnectionError)
    def _create_client(self) -> Elasticsearch:
        """Create Elasticsearch client with backoff."""
        client = Elasticsearch(self.dsn)
        if not client.ping():
            raise elasticsearch.ConnectionError("Elasticsearch don't response")
        return client

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
