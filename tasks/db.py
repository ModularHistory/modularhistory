"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

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
def seed(context, remote: bool = False, migrate: bool = False):
    """Seed the database."""
    db.seed(context, remote=remote, migrate=migrate)


@command
def squash_migrations(context, dry: bool = False):
    """Squash migrations."""
    db.squash_migrations(context, dry=dry)
