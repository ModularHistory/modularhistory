from core.environment import DOCKERIZED

REDIS_HOST = 'redis' if DOCKERIZED else 'localhost'
REDIS_PORT = '6379'
REDIS_BASE_URL = REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'
