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
    print(f'Request: {self.request!r}')


@app.task(bind=True)
def dbbackup(context: Context = CONTEXT):
    """Create a database backup file."""
    commands.dbbackup()


@app.task(bind=True)
def mediabackup(context: Context = CONTEXT):
    """Create a media backup file."""
    commands.mediabackup()
