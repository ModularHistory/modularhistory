from core.config.redis import REDIS_BASE_URL
from core.environment import DOCKERIZED, IS_PROD

# https://github.com/jazzband/django-defender
USE_DEFENDER = False  # TODO
if USE_DEFENDER:
    DEFENDER_REDIS_URL = f'{REDIS_BASE_URL}/0'
    if IS_PROD or DOCKERIZED:
        # https://github.com/jazzband/django-defender#customizing-django-defender
        DEFENDER_BEHIND_REVERSE_PROXY = True
