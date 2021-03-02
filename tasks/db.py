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

from modularhistory.constants.environments import Environments
from modularhistory.utils import db

from .command import command

django.setup()

from django.conf import settings  # noqa: E402

BACKUPS_DIR = settings.BACKUPS_DIR
DB_INIT_FILE = join(BACKUPS_DIR, 'init.sql')
SERVER: Optional[str] = config('SERVER', default=None)
SERVER_SSH_PORT: Optional[int] = config('SERVER_SSH_PORT', default=22)
SERVER_USERNAME: Optional[str] = config('SERVER_USERNAME', default=None)
SERVER_PASSWORD: Optional[str] = config('SERVER_PASSWORD', default=None)

GITHUB_API_BASE_URL = 'https://api.github.com'
OWNER = 'modularhistory'
REPO = 'modularhistory'
GITHUB_ACTIONS_BASE_URL = f'{GITHUB_API_BASE_URL}/repos/{OWNER}/{REPO}/actions'
GITHUB_CREDENTIALS_FILE = '.github/.credentials'

SEEDS = {'env-file': '.env', 'init-sql': '.backups/init.sql'}


@command
def backup(
    context, redact: bool = False, push: bool = False, filename: Optional[str] = None
):
    """Create a database backup file."""
    db.backup(context, redact=redact, push=push, filename=filename)


@command
def get_backup(context, env: str = Environments.DEV):
    """Get latest db backup from remote storage."""
    context.run(f'mkdir -p {BACKUPS_DIR}', warn=True)
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
            scp.get(BACKUPS_DIR, './', recursive=True)
        latest_backup = max(iglob(join(BACKUPS_DIR, '*sql')), key=os.path.getctime)
        print(latest_backup)
        context.run(f'cp {latest_backup} {DB_INIT_FILE}')
    else:
        from modularhistory.storage.mega_storage import mega_clients  # noqa: E402

        mega_client = mega_clients[env]
        pprint(mega_client.get_user())
        init_file = 'init.sql'
        init_file_path = join(BACKUPS_DIR, init_file)
        if os.path.exists(init_file_path):
            context.run(f'mv {init_file_path} {init_file_path}.prior', warn=True)
        backup_file = mega_client.find(init_file, exclude_deleted=True)
        if backup_file:
            mega_client.download(backup_file)
            context.run(f'mv {init_file} {init_file_path}')
        else:
            print(f'Could not find {init_file}.')


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
def squash_migrations(context, dry: bool = True):
    """Squash migrations."""
    db.squash_migrations(context, dry)
