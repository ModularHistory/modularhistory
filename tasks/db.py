"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

import os
from glob import iglob
from os.path import join
from pprint import pprint
from typing import Optional

import django
from decouple import config
from paramiko import SSHClient
from scp import SCPClient

from core.constants.environments import Environments
from core.utils import db

from .command import command

django.setup()

from django.conf import settings  # noqa: E402

SERVER: Optional[str] = config('SERVER', default=None)
SERVER_SSH_PORT: Optional[int] = config('SERVER_SSH_PORT', default=22)
SERVER_USERNAME: Optional[str] = config('SERVER_USERNAME', default=None)
SERVER_PASSWORD: Optional[str] = config('SERVER_PASSWORD', default=None)

GITHUB_API_BASE_URL = 'https://api.github.com'
OWNER = 'modularhistory'
REPO = 'modularhistory'
GITHUB_ACTIONS_BASE_URL = f'{GITHUB_API_BASE_URL}/repos/{OWNER}/{REPO}/actions'
GITHUB_CREDENTIALS_FILE = '.github/.credentials'


@command
def backup(
    context, redact: bool = False, push: bool = False, filename: Optional[str] = None
):
    """Create a database backup file."""
    db.backup(context, redact=redact, push=push, filename=filename)


@command
def get_backup(context, env: str = Environments.DEV):
    """Get latest db backup from remote storage."""
    context.run(f'mkdir -p {settings.BACKUPS_DIR} {settings.DB_INIT_DIR}')
    if SERVER and SERVER_SSH_PORT and SERVER_USERNAME and SERVER_PASSWORD:
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(
            SERVER,
            port=SERVER_SSH_PORT,
            username=SERVER_USERNAME,
            password=SERVER_PASSWORD,
        )
        with SCPClient(ssh.get_transport()) as scp:
            scp.get(settings.BACKUPS_DIR, './', recursive=True)
        latest_backup = max(
            iglob(join(settings.BACKUPS_DIR, '*sql')), key=os.path.getctime
        )
        print(latest_backup)
        context.run(f'cp {latest_backup} {settings.DB_INIT_FILEPATH}')
    else:
        from core.storage.mega_storage import mega_clients  # noqa: E402

        mega_client = mega_clients[env]
        pprint(mega_client.get_user())
        backup_file = mega_client.find(settings.DB_INIT_FILENAME, exclude_deleted=True)
        if backup_file:
            print(f'Found {settings.DB_INIT_FILENAME} in Mega storage.')
            if os.path.exists(settings.DB_INIT_FILEPATH):
                print(
                    f'Renaming extant {settings.DB_INIT_FILEPATH} '
                    f'to {settings.DB_INIT_FILEPATH}.prior ...'
                )
                context.run(
                    f'mv {settings.DB_INIT_FILEPATH} {settings.DB_INIT_FILEPATH}.prior',
                    warn=True,
                )
            mega_client.download(backup_file)
            context.run(f'mv {settings.DB_INIT_FILENAME} {settings.DB_INIT_FILEPATH}')
        else:
            print(f'Could not find {settings.DB_INIT_FILENAME} in Mega storage.')


@command
def makemigrations(context, noninteractive: bool = False):
    """Safely create migrations."""
    db.makemigrations(context, noninteractive=noninteractive)


@command
def migrate(context, *args, noninteractive: bool = False):
    """Safely run db migrations."""
    db.migrate(context, *args, noninteractive=noninteractive)


@command
def restore_squashed_migrations(context):
    """Restore migrations with squashed_migrations."""
    db.restore_squashed_migrations(context)


@command
def seed(context, migrate: bool = False):
    """Seed the database."""
    db.seed(context, migrate=migrate)


@command
def squash_migrations(context, dry: bool = True):
    """Squash migrations."""
    db.squash_migrations(context, dry)
