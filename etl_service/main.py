#!/usr/bin/env python
import time

import elasticsearch
import psycopg

from core.backoff import backoff
from core.logger import logger
from core.settings import settings

from db.elastic import ElasticConnector
from db.postgres import PostgresConnector



@backoff(psycopg.OperationalError, max_time=100)
def check_pg(conn_):
    return conn_.execute('SELECT COUNT(*) FROM content.film_work').fetchall()


@backoff(elasticsearch.ConnectionError, max_time=100)
def check_es(conn_):
    return conn_.indices.exists(index='movies')


def load_from_postgres_to_elastic():
    postgres = PostgresConnector(settings.postgres_settings.get_dsn())
    elastic = ElasticConnector(settings.elastic_settings.get_host())
    with postgres.connect() as pg_conn, elastic.connect() as es_conn:
        pg = check_pg(pg_conn)
        logger.info(pg)
        es = check_es(es_conn)
        logger.info(es)


if __name__ == '__main__':
    logger.info('Start ETL application')
    load_from_postgres_to_elastic()
    logger.info('Stop ETL application')
