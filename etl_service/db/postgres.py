from contextlib import contextmanager
import logging

import psycopg
from psycopg import connect, ClientCursor
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row

from core.backoff import backoff


class PostgresConnector:
    """Подключение к PostgreSQL"""

    def __init__(self, dsn: dict):
        self.dsn = make_conninfo(**dsn)
        self.logger = logging.getLogger(__name__)

    @backoff(psycopg.OperationalError, max_time=100)
    def _create_connection(self):
        """Функция подключения с повторными попытками"""
        return connect(self.dsn, row_factory=dict_row, cursor_factory=ClientCursor)

    @contextmanager
    def connect(self):
        """Контекстный менеджер для подключения к PostgreSQL."""
        conn = None
        try:
            conn = self._create_connection()
            self.logger.info("Соединение с PostgreSQL установлено.")
            yield conn
        except psycopg.OperationalError:
            self.logger.exception("Ошибка при подключении к PostgreSQL")
            raise
        finally:
            if conn:
                conn.close()
                self.logger.info("Соединение с PostgreSQL закрыто")
