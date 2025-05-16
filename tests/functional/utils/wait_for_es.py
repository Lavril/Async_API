import os
import time

from elasticsearch import Elasticsearch

ELASTIC_HOST = os.getenv('ELASTIC_HOST', 'elasticsearch')
ELASTIC_PORT = os.getenv('ELASTIC_PORT', '9200')

if __name__ == '__main__':
    # TODO: заменить hosts на переменную окружения
    es_client = Elasticsearch(hosts=f'http://{ELASTIC_HOST}:{ELASTIC_PORT}', verify_certs=False, ssl_show_warn=False)
    while True:
        if es_client.ping():
            print("Elastic is ready.")
            break
        time.sleep(1)
