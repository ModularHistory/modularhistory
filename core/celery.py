import logging
import os

from celery import Celery

from core.utils import db, media

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Using a string for the config object means the worker doesn't have to serialize
# the configuration object to child processes. Setting the namespace to 'CELERY'
# means all celery-related configuration keys should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug(self):
    """Print request info to debug/test Celery."""
    logging.info(f'Request: {self.request!r}')


@app.task(bind=True)
def dbbackup(self, *args, **kwargs):
    """Create a database backup file."""
    db.backup(*args, **kwargs)


@app.task(bind=True)
def mediabackup(self, *args, **kwargs):
    """Create a media backup file."""
    media.backup(*args, **kwargs)


@app.task(bind=True)
def make_seed(self, *args, **kwargs):
    """Make and upload a db seed file."""
    db.backup(*args, redact=True, push=True, filename='init.sql', **kwargs)
