import logging
import sys

from core.settings import settings


if settings.debug:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

logging.getLogger('elastic_transport.transport').setLevel(logging.ERROR)


handlers = [logging.StreamHandler(stream=sys.stdout),]

logging.basicConfig(
    handlers=handlers,
    level=log_level,
    format='%(asctime)s - [%(levelname)s] - %(name)s: %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S%z',
)

logger = logging.getLogger('postgres_to_elastic')
