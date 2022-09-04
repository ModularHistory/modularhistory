import logging
import os

from celery import Task

from core.celery import app
from core.constants.environments import Environments
from core.utils import db, media


@app.task(bind=True)
def debug(self: Task):
    """Print request info to debug/test Celery."""
    logging.info(f'Request: {self.request!r}')


@app.task(bind=True)
def dbbackup(self: Task, *args, **kwargs):
    """Create a database backup file."""
    db.backup(*args, **kwargs)


@app.task(bind=True)
def mediabackup(self: Task, *args, **kwargs):
    """Create a media backup file."""
    media.backup(*args, **kwargs)


@app.task(bind=True)
def upload_db_seed(self: Task, *args, **kwargs):
    """Make and upload a db seed file."""
    environment = os.getenv('ENVIRONMENT')
    if environment == Environments.PROD:
        kwargs = {**{'redact': True, 'push': True, 'filename': 'init.sql'}, **kwargs}
        db.backup(*args, **kwargs)
    else:
        print(
            'Ignored request to upload db seed, since '
            f'{environment} != {Environments.PROD}'
        )


@app.task(bind=True)
def sync_media(self: Task, *args, **kwargs):
    """Sync media."""
    environment = os.getenv('ENVIRONMENT')
    if environment == Environments.PROD:
        # Synchronize remote media to local media.
        media.sync(push=True)
    elif environment == Environments.DEV:
        # Synchronize local media to remote media.
        media.sync(push=False)
    else:
        print(
            f'Ignored request to sync media, since environment "{environment}"'
            f'is not "{Environments.PROD}" or "{Environments.DEV}".'
        )
