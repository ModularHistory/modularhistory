"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

from typing import TYPE_CHECKING, Optional

import django

from commands.command import command
from core.utils import db

if TYPE_CHECKING:
    from invoke.context import Context

django.setup()

GITHUB_API_BASE_URL = 'https://api.github.com'
OWNER = 'modularhistory'
REPO = 'modularhistory'
GITHUB_ACTIONS_BASE_URL = f'{GITHUB_API_BASE_URL}/repos/{OWNER}/{REPO}/actions'
GITHUB_CREDENTIALS_FILE = '.github/.credentials'


@command
def backup(
    context: 'Context',
    redact: bool = False,
    push: bool = False,
    filename: Optional[str] = None,
):
    """Create a database backup file."""
    db.backup(context, redact=redact, push=push, filename=filename)


@command
def makemigrations(context: 'Context', noninteractive: bool = False):
    """Safely create migrations."""
    db.makemigrations(context, noninteractive=noninteractive)


@command
def migrate(context: 'Context', *args, noninteractive: bool = False):
    """Safely run db migrations."""
    db.migrate(context, *args, noninteractive=noninteractive)


@command
def restore_squashed_migrations(context: 'Context'):
    """Restore migrations with squashed_migrations."""
    db.restore_squashed_migrations(context)


@command
def seed(context: 'Context', remote: bool = False, migrate: bool = False):
    """Seed the database."""
    db.seed(context, remote=remote, migrate=migrate)


@command
def squash_migrations(context: 'Context', dry: bool = False):
    """Squash migrations."""
    db.squash_migrations(context, dry=dry)
