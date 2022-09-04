"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

import os
from os.path import join
from typing import TYPE_CHECKING

import django

from commands.command import command
from core.utils import media

if TYPE_CHECKING:
    from invoke.context import Context

django.setup()

from django.conf import settings  # noqa: E402

BACKUPS_DIR = settings.BACKUPS_DIR
MEDIA_INIT_FILE = join(BACKUPS_DIR, 'media.tar.gz')

GITHUB_API_BASE_URL = 'https://api.github.com'
OWNER = 'modularhistory'
REPO = 'modularhistory'
GITHUB_ACTIONS_BASE_URL = f'{GITHUB_API_BASE_URL}/repos/{OWNER}/{REPO}/actions'
GITHUB_CREDENTIALS_FILE = '.github/.credentials'


@command
def backup(context: 'Context', redact: bool = False, push: bool = False):
    """Create a media backup file."""
    # based on https://github.com/django-dbbackup/django-dbbackup#mediabackup
    media.backup(context, redact=redact, push=push)


@command
def sync(context: 'Context', push: bool = False):
    """Sync media from source to destination, modifying destination only."""
    context.run(f'mkdir -p {settings.MEDIA_ROOT}', warn=True)
    print(
        'Syncing media... \n\n'
        'This could take a while. Leave this shell running until you '
        'see a "Finished" message. In the meantime, feel free to open '
        'a new shell and start up the app with the following command: \n\n'
        '    docker compose up -d django next\n\n'
        '..........................'
    )
    media.sync(context, push=push)
    restore_from_tar = False
    if restore_from_tar and os.path.exists(join(BACKUPS_DIR, 'media.tar.gz')):
        context.run(f'python manage.py mediarestore -z --noinput -i {MEDIA_INIT_FILE} -q')
    print('Media sync complete.')
