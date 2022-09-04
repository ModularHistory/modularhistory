from typing import Any

from decouple import config

from core.config.redis import REDIS_BASE_URL
from core.constants.environments import Environments
from core.environment import ENVIRONMENT, IS_DEV

# Caching settings
use_dummy_cache = config('DUMMY_CACHE', cast=bool, default=False)
Cache = dict[str, Any]
CACHES: dict[str, Cache]

REDIS_CACHE = {
    'BACKEND': 'django_redis.cache.RedisCache',
    'LOCATION': f'{REDIS_BASE_URL}/0',
    'OPTIONS': {
        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
    },
}

# https://github.com/jazzband/django-redis
if IS_DEV and use_dummy_cache:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        },
        'cachalot': REDIS_CACHE,
    }
else:
    CACHES = {
        'default': REDIS_CACHE,
    }
    # https://github.com/jazzband/django-redis
    # https://docs.djangoproject.com/en/dev/topics/http/sessions/#using-cached-sessions
    SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
    SESSION_CACHE_ALIAS = 'default'

# Cachalot settings:
# https://django-cachalot.readthedocs.io/en/latest/quickstart.html#settings
CACHALOT_ENABLED = ENVIRONMENT != Environments.GITHUB_TEST and not use_dummy_cache
CACHALOT_CACHE = 'default'  # cache name
CACHALOT_CACHE_RANDOM = False  # caching of random order queries, i.e order_by('?')
CACHALOT_UNCACHABLE_TABLES = frozenset(
    (
        'django_migrations',  # migrations must not be cached
        'django_session',
        'django_admin_log',
        # celery tables
        'django_celery_beat_clockedschedule',
        'django_celery_beat_crontabschedule',
        'django_celery_beat_intervalschedule',
        'django_celery_beat_periodictask',
        'django_celery_beat_solarschedule',
        'django_celery_results_chordcounter',
        'django_celery_results_taskresult',
        'health_check_db_testmodel',
    )
)
