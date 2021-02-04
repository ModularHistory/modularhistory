import logging
import os

from celery import Celery
from invoke.context import Context

from modularhistory.utils import commands

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modularhistory.settings')

app = Celery('modularhistory')

# Using a string for the config object means the worker doesn't have to serialize
# the configuration object to child processes. Setting the namespace to 'CELERY'
# means all celery-related configuration keys should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

CONTEXT = Context()


@app.task(bind=True)
def debug(self):
    """Print request info to debug/test Celery."""
    logging.info(f'Request: {self.request!r}')


@app.task(bind=True)
def dbbackup(self):
    """Create a database backup file."""
    logging.info(f'dbbackup received request: {self.request!r}')
    commands.back_up_db()


@app.task(bind=True)
def mediabackup(self):
    """Create a media backup file."""
    logging.info(f'mediabackup received request: {self.request!r}')
    commands.back_up_media()


@app.task(bind=True)
def push_seeds(self):
    """Push db and media seeds to the cloud."""
    logging.info(f'push_seeds received request: {self.request!r}')
    commands.back_up_db(redact=True, push=True)
    commands.back_up_media(redact=True, push=True)
