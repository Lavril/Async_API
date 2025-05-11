import os
import time
import redis

ELASTIC_HOST = os.getenv('REDIS_HOST', 'redis')
ELASTIC_PORT = os.getenv('REDIS_PORT', '6379')

if __name__ == '__main__':
    # TODO: заменить hosts на переменную окружения
    redis_client = redis.Redis(host=ELASTIC_HOST, port=ELASTIC_PORT)
    while True:
        try:
            if redis_client.ping():
                print("Redis is ready.")
                break
        except redis.ConnectionError:
            time.sleep(1)
