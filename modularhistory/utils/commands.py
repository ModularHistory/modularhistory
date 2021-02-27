# pylint: disable=anomalous-backslash-in-string

import logging
import os
import re
from glob import glob, iglob
from os.path import join
from pprint import pformat
from typing import Any, Callable, Iterable, Optional, TypeVar
from zipfile import ZipFile
from decouple import config
from django.conf import settings
from django.db import transaction
from invoke.context import Context

from modularhistory.constants.environments import Environments
from modularhistory.constants.misc import (
    APPS_WITH_MIGRATIONS,
    MAX_MIGRATION_COUNT,
    MIGRATIONS_DIRNAME,
    SQUASHED_MIGRATIONS_DIRNAME,
)
from modularhistory.constants.strings import BASH_PLACEHOLDER, NEGATIVE
from modularhistory.utils.files import relativize

TaskFunction = TypeVar('TaskFunction', bound=Callable[..., Any])

CONTEXT = Context()
DAYS_TO_KEEP_BACKUP = 7
SECONDS_IN_DAY = 86400
SECONDS_TO_KEEP_BACKUP = DAYS_TO_KEEP_BACKUP * SECONDS_IN_DAY


def autoformat(context: Context = CONTEXT, files: Optional[Iterable[str]] = None):
    """Autoformat all of ModularHistory's Python code."""
    commands = (
        (
            'autoflake --imports=apps,django,requests,typing,urllib3 '
            '--ignore-init-module-imports --in-place {filename}'
        ),
        ('unify --in-place {filename}'),
        ('black {filename}'),
    )
    file_names = files or iglob('[!.]**/*.py', recursive=True)
    for filename in file_names:
        print(f'Formatting {filename}...')
        for command in commands:
            context.run(command.format(filename=filename))
    context.run('isort .')


def clear_migration_history(context: Context = CONTEXT):
    """."""
    with transaction.atomic():
        for app in APPS_WITH_MIGRATIONS:
            n_migrations = (
                len(os.listdir(path=relativize(join(app, MIGRATIONS_DIRNAME)))) - 1
            )
            if n_migrations > MAX_MIGRATION_COUNT:
                # Fake reverting all migrations.
                print(f'\n Clearing migration history for the {app} app...')
                revert_to_migration_zero(context, app)
            else:
                print(
                    f'Skipping {app} since there are only {n_migrations} migration files...'
                )
    # Remove old migration files.
    if input('\n Proceed to remove migration files? [Y/n] ') != NEGATIVE:
        remove_migrations(context)


def back_up_db(
    context: Context = CONTEXT,
    redact: bool = False,
    zip: bool = False,
    push: bool = False,
    filename: Optional[str] = None,
):
    """Create a database backup file."""
    backups_dir = settings.BACKUPS_DIR
    backup_files_pattern = join(backups_dir, '*sql')
    # https://github.com/django-dbbackup/django-dbbackup#dbbackup
    context.run('python manage.py dbbackup --quiet --noinput', hide='out')
    backup_files = glob(backup_files_pattern)
    temp_file = max(backup_files, key=os.path.getctime)
    backup_file = temp_file.replace('.psql', '.sql')
    if filename:
        backup_file = backup_file.replace(os.path.basename(backup_file), filename)
    print('Processing backup file...')
    with open(temp_file, 'r') as unprocessed_backup:
        with open(backup_file, 'w') as processed_backup:
            previous_line = ''  # falsy; compatible with `startswith`
            for line in unprocessed_backup:
                drop_conditions = [
                    line.startswith('ALTER '),
                    line.startswith('DROP '),
                    line == '\n' == previous_line,
                    all(
                        [
                            redact,
                            previous_line.startswith('COPY public.account_user'),
                            not line.startswith(r'\.'),
                        ]
                    ),
                ]
                if any(drop_conditions):
                    continue
                processed_backup.write(line)
                previous_line = line
    context.run(f'rm {temp_file}')
    if zip:
        print(f'Zipping up {backup_file}...')
        zipped_backup_file = f'{backup_file}.zip'
        with ZipFile(zipped_backup_file, 'x') as archive:
            archive.write(backup_file)
        backup_file = zipped_backup_file
    print(f'Finished creating backup file: {backup_file}')
    if push:
        upload_to_mega(file=backup_file, account=Environments.DEV)
    # Remove old backup files
    logging.info('Removing old backup files...')
    end = '{} \;'  # noqa: W605, P103
    context.run(
        f'find {backup_files_pattern} -mtime +{DAYS_TO_KEEP_BACKUP} -exec rm {end}'
    )


def back_up_media(
    context: Context = CONTEXT,
    redact: bool = False,
    push: bool = False,
    filename: Optional[str] = None,
):
    """Create a media backup file."""
    backups_dir, media_dir = settings.BACKUPS_DIR, settings.MEDIA_ROOT
    backup_files_pattern = join(backups_dir, '*.tar.gz')
    account_media_dir = join(media_dir, 'account')
    temp_dir = join(settings.BASE_DIR, 'account_media')
    exclude_account_media = redact and os.path.exists(account_media_dir)
    if exclude_account_media:
        context.run(f'mv {account_media_dir} {temp_dir}')
        context.run(f'mkdir {account_media_dir}')
    # https://github.com/django-dbbackup/django-dbbackup#mediabackup
    context.run('python manage.py mediabackup -z --noinput', hide='out')
    if exclude_account_media:
        context.run(f'rm -r {account_media_dir}')
        context.run(f'mv {temp_dir} {account_media_dir}')
    backup_files = glob(backup_files_pattern)
    backup_file = max(backup_files, key=os.path.getctime)
    if filename:
        context.run(f'mv {backup_file} {join(backups_dir, filename)}')
        backup_file = join(backups_dir, filename)
    print(f'Finished creating backup file: {backup_file}')
    if push:
        upload_to_mega(file=backup_file, account=Environments.DEV)


def envsubst(input_file) -> str:
    """Python implementation of envsubst."""
    with open(input_file, 'r') as base:
        content_after = content_before = base.read()
        for match in re.finditer(r'\$\{?(.+?)\}?', content_before):
            env_var = match.group(1)
            env_var_value = os.getenv(env_var)
            content_after = content_before.replace(match.group(0), env_var_value or '')
    return content_after


def makemigrations(context: Context = CONTEXT, noninteractive: bool = False):
    """Safely create migrations."""
    interactive = not noninteractive
    make_migrations = True
    if interactive:
        print('Doing a dry run first...')
        context.run('python manage.py makemigrations --dry-run')
        make_migrations = input('^ Do these changes look OK? [Y/n]') != NEGATIVE
    if make_migrations:
        context.run('python manage.py makemigrations')


def migrate(context: Context = CONTEXT, *args, noninteractive: bool = False):
    """Safely run db migrations."""
    interactive = not noninteractive
    if interactive and input('Create db backup? [Y/n] ') != NEGATIVE:
        context.run('python manage.py dbbackup')
    print('Running migrations...')
    with transaction.atomic():
        context.run(f'python manage.py migrate {" ".join(args)}')
    print()
    context.run('python manage.py showmigrations')
    print()
    if interactive and input('Did migrations run successfully? [Y/n] ') == NEGATIVE:
        context.run('python manage.py dbrestore')


def push_seeds(context: Context = CONTEXT):
    """Push db and media seeds to the cloud."""
    back_up_db(context, redact=True, push=True, filename='init.sql')
    back_up_media(context, redact=True, push=True, filename='media.tar.gz')


def restore_squashed_migrations(context: Context = CONTEXT):
    """Restore migrations with squashed_migrations."""
    for app in APPS_WITH_MIGRATIONS:
        squashed_migrations_dir = relativize(join(app, SQUASHED_MIGRATIONS_DIRNAME))
        # TODO: only do this if there are files in the squashed_migrations dir
        squashed_migrations_exist = os.path.exists(
            squashed_migrations_dir
        ) and os.listdir(path=squashed_migrations_dir)
        if squashed_migrations_exist:
            # Remove the replacement migrations
            migration_files_path = relativize(f'{app}/migrations/*.py')
            context.run(
                f'find . -type f -path "{migration_files_path}" '
                f'-not -name "__init__.py" '
                f'-exec rm {BASH_PLACEHOLDER} \;'  # noqa: W605
            )
            # Restore the squashed migrations
            migrations_dir = relativize(f'{join(app, MIGRATIONS_DIRNAME)}')
            context.run(
                f'find {squashed_migrations_dir} -type f -name "*.py" '
                f'-exec mv {BASH_PLACEHOLDER} {migrations_dir}/ \;'  # noqa: W605
            )
            # Remove the squashed_migrations directory
            if os.path.exists(squashed_migrations_dir):
                context.run(f'rm -r {squashed_migrations_dir}')
            print(f'Removed squashed migrations from {app}.')
        else:
            print(f'There are no squashed migrations to remove from {app}.')


def remove_migrations(
    context: Context = CONTEXT, app: Optional[str] = None, hard: bool = False
):
    """Remove migration files."""
    apps = [app] if app else APPS_WITH_MIGRATIONS
    print(f'Removing migrations from {apps}...')
    for app in apps:
        remove_migrations_from_app(context, app, hard=hard)


def remove_migrations_from_app(
    context: Context = CONTEXT, app: str = '', hard: bool = False
):
    """Remove migrations from a specific app."""
    app = app or input('App name: ')
    # Remove the squashed_migrations directory
    migrations_path = relativize(join(app, MIGRATIONS_DIRNAME))
    squashed_migrations_path = relativize(join(app, SQUASHED_MIGRATIONS_DIRNAME))
    if os.path.exists(squashed_migrations_path):
        print(f'Removing {squashed_migrations_path}...')
        context.run(f'rm -r {squashed_migrations_path}')
        print(f'Removed {squashed_migrations_path}')
    # Clear migration files from the migrations directory
    if hard:
        # Delete the migration files
        command = (
            f'find {migrations_path} -type f -name "*.py" -not -name "__init__.py" '
            f'-exec rm {BASH_PLACEHOLDER} \;'  # noqa: W605
        )
        print(command)
        context.run(command)
    else:
        context.run(f'mkdir {squashed_migrations_path}')
        # Move the migration files to the squashed_migrations directory
        context.run(
            f'find . -type f -path "./{app}/migrations/*.py" -not -name "__init__.py" '
            f'-exec echo "{BASH_PLACEHOLDER}" \;'  # noqa: W605
        )
        squashed_migrations_dir = relativize(join(app, SQUASHED_MIGRATIONS_DIRNAME))
        command = (
            f'find . -type f -path "./{app}/migrations/*.py" -not -name "__init__.py" '
            f'-exec mv {BASH_PLACEHOLDER} {squashed_migrations_dir}/ \;'  # noqa: W605
        )
        print(command)
        context.run(command)
        if not glob(relativize(f'{join(app, SQUASHED_MIGRATIONS_DIRNAME)}/*.py')):
            print(
                'ERROR: Could not move migration files '
                f'to {SQUASHED_MIGRATIONS_DIRNAME}'
            )
    command = (
        f'find {relativize(app)} -path "migrations/*.pyc" '
        f'-exec rm {BASH_PLACEHOLDER} \;'  # noqa: W605
    )
    print(command)
    context.run(command)
    print(f'Removed migration files from {app}.')


def revert_to_migration_zero(context: Context = CONTEXT, app: str = ''):
    """Spoof reverting migrations by running a fake migration to `zero`."""
    app = app or input('App name: ')
    context.run(f'python manage.py migrate {app} zero --fake')
    print()
    print('Migrations after fake reversion:')
    context.run('python manage.py showmigrations')
    print()


def squash_migrations(context: Context = CONTEXT, dry: bool = True):
    """
    Squash migrations.

    See https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html.
    """
    # Create a db backup
    if dry and input('Create db backup? [Y/n] ') != NEGATIVE:
        context.run('python manage.py dbbackup')

    # Make sure models fit the current db schema
    context.run('python manage.py makemigrations')
    if input('Run db migrations? [Y/n] ') != NEGATIVE:
        migrate(context, noninteractive=True)

    # Clear the migrations history for each app
    context.run('')
    for pyc in iglob('**/migrations/*.pyc'):
        os.remove(pyc)
    clear_migration_history(context)

    # Regenerate migration files.
    makemigrations(context, noninteractive=True)
    if input('\n Continue? [Y/n] ') == NEGATIVE:
        return

    # Fake the migrations.
    print()
    print('Running fake migrations...')  # noqa: WPS441
    migrate(
        context,
        '--fake-initial',
        noninteractive=True,
    )

    if dry:
        input(
            'Completed dry run of squashing migrations.\n'
            'Take a minute to test the app locally, then press any key '
            'to proceed to squash migrations for real.'
        )
        context.run('python manage.py dbrestore --database="default" --noinput')
        restore_squashed_migrations(context)
        if input('Squash migrations for real? [Y/n] ') != NEGATIVE:
            squash_migrations(context, dry=False)


def sync_media(
    context: Context = CONTEXT, push: bool = False, max_transfer: str = '5G'
):
    """Sync media from source to destination, modifying destination only."""
    # TODO: refactor
    mega_username = config(
        'MEGA_DEV_USERNAME', default=config('MEGA_USERNAME', default=None)
    )
    mega_password = config(
        'MEGA_DEV_PASSWORD', default=config('MEGA_PASSWORD', default=None)
    )
    local_media_dir = settings.MEDIA_ROOT
    mega_media_dir = 'mega:/media/'
    source, destination = (
        (local_media_dir, mega_media_dir) if push else (mega_media_dir, local_media_dir)
    )
    use_gdrive=False  # TODO
    if use_gdrive:
        command = (
            f'rclone sync {source} {destination} '
            f'--drive-client-id=... '
            f'--drive-client-secret=...'
        )
    else:
        # https://rclone.org/drive/#standard-options
        command = (
            f'rclone sync {source} {destination} '
            # https://rclone.org/flags/
            f'--max-transfer={max_transfer} --order-by="size,ascending" --progress '
            f'--config {join(settings.BASE_DIR, "config/rclone/rclone.conf")} '
            f'--mega-user={mega_username} '
            f'--mega-pass=$(echo "{mega_password}" | rclone obscure -)'
        )
    if push:
        command = f'{command} --drive-stop-on-upload-limit'
    else:
        command = f'{command} --drive-stop-on-download-limit'
    context.run(command)


def upload_to_mega(file: str, account: str = 'default'):
    """Upload a file to Mega."""
    from modularhistory.storage.mega_storage import mega_clients  # noqa: E402

    mega_client = mega_clients[account]
    logging.info(f'Pushing {file} to Mega ({account}) ...')
    extant_file = mega_client.find(file, exclude_deleted=True)
    if extant_file:
        logging.info(f'Found extant backup: {extant_file}')
    result = mega_client.upload(file)
    logging.info(f'Upload result: {pformat(result)}')
    uploaded_file = mega_client.find(os.path.basename(file))
    if not uploaded_file:
        raise Exception(f'{file} was not found in Mega ({account}) after uploading.')
    return uploaded_file
