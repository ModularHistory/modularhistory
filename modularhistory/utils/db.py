import logging
import os
import re
from glob import glob, iglob
from os.path import join
from time import sleep
from typing import Optional
from zipfile import ZipFile

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
from modularhistory.utils.files import relativize, upload_to_mega

CONTEXT = Context()
DAYS_TO_KEEP_BACKUP = 7
SECONDS_IN_DAY = 86400
SECONDS_TO_KEEP_BACKUP = DAYS_TO_KEEP_BACKUP * SECONDS_IN_DAY


def backup(
    context: Context = CONTEXT,
    redact: bool = False,
    zip: bool = False,
    push: bool = False,
    filename: Optional[str] = None,
):
    """Create a database backup file."""
    backup_files_pattern = join(settings.BACKUPS_DIR, '*sql')
    # https://github.com/django-dbbackup/django-dbbackup#dbbackup
    context.run('python manage.py dbbackup --noinput')
    backup_files = glob(backup_files_pattern)
    temp_file = max(backup_files, key=os.path.getctime)
    backup_filename = temp_file.replace('.psql', '.sql')
    if filename:
        backup_filename = backup_filename.replace(
            os.path.basename(backup_filename), filename
        )
    with open(temp_file, 'r') as unprocessed_backup:
        if os.path.isdir(backup_filename):
            os.rmdir(backup_filename)
        with open(backup_filename, 'w') as processed_backup:
            previous_line = ''  # falsy and compatible with `startswith`
            for line in unprocessed_backup:
                discard_conditions = [
                    line == '\n' and re.match(r'(\n|--\n)', previous_line),
                    re.match(r'(.*DROP\ |--\n?$)', line),
                    # fmt: off
                    redact and not line.startswith(r'\.') and re.match(
                        r'COPY public\.(users_user|.+user_id)', previous_line
                    )
                    # fmt: on
                ]
                if any(discard_conditions):
                    continue
                processed_backup.write(line)
                previous_line = line
    context.run(f'rm {temp_file}')
    if zip:
        print(f'Zipping up {backup_filename} ...')
        zipped_backup_file = f'{backup_filename}.zip'
        with ZipFile(zipped_backup_file, 'x') as archive:
            archive.write(backup_filename)
        backup_filename = zipped_backup_file
    print(f'Finished creating backup file: {backup_filename}')
    if push:
        print(f'Uploading {backup_filename} to Mega ...')
        upload_to_mega(backup_filename, account=Environments.DEV)
        print(f'Finished uploading {backup_filename} to Mega.')
    # Remove old backup files
    logging.info('Removing old backup files ...')
    end = '{} \;'  # noqa: W605, P103
    context.run(
        f'find {backup_files_pattern} -mtime +{DAYS_TO_KEEP_BACKUP} -exec rm {end}',
        warn=True,
    )


def clear_migration_history(context: Context = CONTEXT):
    """Delete all migration files."""
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


def revert_to_migration_zero(context: Context = CONTEXT, app: str = ''):
    """Spoof reverting migrations by running a fake migration to `zero`."""
    app = app or input('App name: ')
    context.run(f'python manage.py migrate {app} zero --fake')
    print()
    print('Migrations after fake reversion:')
    context.run('python manage.py showmigrations')
    print()


def seed(context: Context = CONTEXT, migrate: bool = False):
    """Seed the database."""
    db_volume = 'modularhistory_postgres_data'
    if not os.path.isfile(settings.DB_INIT_FILEPATH):
        raise Exception('Seed does not exist.')
    # Remove the data volume, if it exists
    print('Stopping containers...')
    context.run('docker-compose down')
    print('Wiping postgres data volume...')
    context.run(f'docker volume rm {db_volume}', warn=True)
    # Start up the postgres container, automatically running init.sql.
    print('Initializing postgres data...')
    context.run('docker-compose up -d postgres')
    print('Waiting for Postgres to finish recreating the database...')
    sleep(10)  # Give postgres time to recreate the database.
    if migrate:
        context.run('docker-compose run django python manage.py migrate')
    context.run('docker-compose up -d dev')


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
