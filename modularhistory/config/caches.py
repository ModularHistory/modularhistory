from typing import Any, Dict

from decouple import config

from modularhistory.config.redis import REDIS_BASE_URL
from modularhistory.environment import IS_DEV

# Caching settings
use_dummy_cache = config('DUMMY_CACHE', cast=bool, default=False)
Cache = Dict[str, Any]
CACHES: Dict[str, Cache]

# https://github.com/jazzband/django-redis
if IS_DEV and use_dummy_cache:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f'{REDIS_BASE_URL}/0',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
        }
    }
    # https://github.com/jazzband/django-redis
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
