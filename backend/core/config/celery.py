from decouple import config

from core.config.redis import REDIS_BASE_URL

USE_CELERY: bool = config('USE_CELERY', cast=bool, default=True)

# https://docs.celeryproject.org/en/stable/django/
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_BROKER_URL = f'{REDIS_BASE_URL}/0'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
# https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html#django-celery-results-using-the-django-orm-cache-as-a-result-backend
CELERY_RESULT_BACKEND = 'django-cache'
CELERY_CACHE_BACKEND = 'default'
