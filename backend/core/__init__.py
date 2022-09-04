import os

# https://docs.djangoproject.com/en/dev/topics/settings/#envvar-DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from .celery import app as celery_app  # noqa: E402

__all__ = ('celery_app',)
