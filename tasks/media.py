"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

import os
from os.path import join
from pprint import pprint

import django

from modularhistory.constants.environments import Environments
from modularhistory.utils import commands

from .command import command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modularhistory.settings')
django.setup()

from django.conf import settings  # noqa: E402

BACKUPS_DIR = settings.BACKUPS_DIR
DB_INIT_FILE = join(BACKUPS_DIR, 'init.sql')
MEDIA_INIT_FILE = join(BACKUPS_DIR, 'media.tar.gz')

GITHUB_API_BASE_URL = 'https://api.github.com'
OWNER = 'modularhistory'
REPO = 'modularhistory'
GITHUB_ACTIONS_BASE_URL = f'{GITHUB_API_BASE_URL}/repos/{OWNER}/{REPO}/actions'
GITHUB_CREDENTIALS_FILE = '.github/.credentials'

SEEDS = {'env-file': '.env', 'init-sql': '.backups/init.sql'}


@command
def backup(context, redact: bool = False, push: bool = False):
    """Create a media backup file."""
    # based on https://github.com/django-dbbackup/django-dbbackup#mediabackup
    commands.back_up_media(context, redact=redact, push=push)


@command
def get_backup(context, env: str = Environments.DEV):
    """Seed latest media backup from remote storage."""
    context.run(f'mkdir -p {BACKUPS_DIR}', warn=True)

    from modularhistory.storage.mega_storage import mega_clients  # noqa: E402

    mega_client = mega_clients[env]
    pprint(mega_client.get_user())
    media_archive_name = 'media.tar.gz'
    media_archive = mega_client.find(media_archive_name, exclude_deleted=True)
    if media_archive:
        mega_client.download(media_archive)
        context.run(
            f'mv {media_archive_name} {join(BACKUPS_DIR, media_archive_name)}',
            warn=True,
        )
    else:
        print(f'Could not find {media_archive_name}')


@command
def sync(context, push: bool = False):
    """Sync media from source to destination, modifying destination only."""
    context.run(f'mkdir -p {settings.MEDIA_ROOT}', warn=True)
    print(
        'Syncing media... \n\n'
        'This could take a while. Leave this shell running until you '
        'see a "Finished" message. In the meantime, feel free to open '
        'a new shell and start up the app with the following command: \n\n'
        '    docker-compose up -d dev\n\n'
        '..........................'
    )
    commands.sync_media(context, push=push)
    restore_from_tar = False
    if restore_from_tar and os.path.exists(join(BACKUPS_DIR, 'media.tar.gz')):
        context.run(
            f'python manage.py mediarestore -z --noinput -i {MEDIA_INIT_FILE} -q'
        )
    print('Media sync complete.')
