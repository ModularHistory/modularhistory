import logging
import os
import re
from glob import glob, iglob
from os.path import join
from time import sleep
from typing import Optional
from zipfile import ZipFile

from celery import shared_task
from celery_singleton import Singleton
from django.conf import settings
from django.db import transaction
from invoke.context import Context

from core.constants.misc import (
    MAX_MIGRATION_COUNT,
    MIGRATIONS_DIRNAME,
    SQUASHED_MIGRATIONS_DIRNAME,
    RcloneStorageProviders,
)
from core.constants.strings import BASH_PLACEHOLDER, NEGATIVE
from core.environment import IS_DEV
from core.utils import files
from core.utils.string import redact as redact_string
from core.utils.sync import delay

DAYS_TO_KEEP_BACKUP = 7
SECONDS_IN_DAY = 86400
SECONDS_TO_KEEP_BACKUP = DAYS_TO_KEEP_BACKUP * SECONDS_IN_DAY
BACKUP_FILES_PATTERN = join(settings.BACKUPS_DIR, '*sql')
CONTEXT = Context()


@shared_task(base=Singleton)
def groom_backup_files():
    """Remove old and/or duplicate db backup files."""
    context = Context()
    logging.info('Pruning backup files ...')
    end = '{} \;'  # noqa: W605, P103
    context.run(
        f'find {BACKUP_FILES_PATTERN} -mtime +{DAYS_TO_KEEP_BACKUP} -exec rm {end}',
        warn=True,
    )
    # For each day, keep the first,
    logging.info('Deduping backup files ...')
    context.run(f'fdupes -rdIN {settings.BACKUPS_DIR}', warn=True)


def backup(
    context: Context = CONTEXT,
    redact: bool = False,
    zip: bool = False,
    push: bool = False,
    filename: Optional[str] = None,
):
    """Create a database backup file."""
    if filename and not filename.endswith('.sql'):
        raise ValueError(f'{filename} does not have a .sql extension.')
    # https://github.com/django-dbbackup/django-dbbackup#dbbackup
    context.run('python manage.py dbbackup --noinput')
    print('Changing backup file extension from psql to sql ...')
    backup_files = glob(BACKUP_FILES_PATTERN)
    temp_file = max(backup_files, key=os.path.getctime)
    backup_filepath = temp_file.replace('.psql', '.sql')
    if filename:
        backup_filepath = backup_filepath.replace(os.path.basename(backup_filepath), filename)
    else:
        filename = os.path.basename(backup_filepath)
    with open(temp_file, 'r') as unprocessed_backup:
        if os.path.isdir(backup_filepath):
            os.rmdir(backup_filepath)
        with open(backup_filepath, 'w') as processed_backup:
            previous_line = ''  # falsy and compatible with `startswith`
            for line in unprocessed_backup:
                discard = (
                    # fmt: off
                    (line == '\n' and re.match(r'(\n|--\n)', previous_line)) or
                    re.match(r'(.*DROP\ |--\n?$)', line) or
                    (redact and not line.startswith(r'\.') and re.match(
                        r'COPY public\.(silk_|users_socialaccount)', previous_line
                    ))
                    # fmt: on
                )
                if discard:
                    continue
                scrub = (
                    redact
                    and not line.startswith(r'\.')
                    and re.match(r'COPY public\.(users_user)', previous_line)
                )
                if scrub:
                    line = redact_string(line)
                processed_backup.write(line)
                previous_line = line
    context.run(f'rm {temp_file}')
    if zip:
        print(f'Zipping up {backup_filepath} ...')
        zipped_backup_file = f'{backup_filepath}.zip'
        with ZipFile(zipped_backup_file, 'x') as archive:
            archive.write(backup_filepath)
        backup_filepath = zipped_backup_file
    logging.info(f'Finished creating backup file: {backup_filepath}')
    if push:
        print('Pushing the backup to cloud storage ...')
        latest_backup_dir = join(settings.BACKUPS_DIR, 'latest')
        context.run(f'mkdir -p {latest_backup_dir}')
        context.run(
            f'cp {backup_filepath} '
            f'{join(latest_backup_dir, os.path.basename(backup_filepath))}'
        )
        logging.info(f'Uploading {latest_backup_dir} contents to remote storage ...')
        files.sync(
            local_dir=latest_backup_dir,
            remote_dir='/database/',
            push=True,
            storage_provider=RcloneStorageProviders.GOOGLE_DRIVE,
        )
        logging.info(f'Finished uploading {backup_filepath}.')
    # Asynchronously remove duplicate and/or old backup files.
    delay(groom_backup_files)


def clear_migration_history(context: Context = CONTEXT, app: str = ''):
    """Delete all migration files and fake reverting to migration zero."""
    app_name = app or input('App name: ')
    with transaction.atomic():
        migrations_dir = join(settings.BASE_DIR, 'apps', app_name, MIGRATIONS_DIRNAME)
        n_migrations = len(os.listdir(path=migrations_dir)) - 1
        if n_migrations > MAX_MIGRATION_COUNT:
            # Fake reverting all migrations.
            print(f'\n Clearing migration history for the {app_name} app...')
            result = context.run(
                f'python manage.py migrate {app_name} zero --fake', warn=True
            )
            print()
            print('Migrations after fake reversion:')
            context.run('python manage.py showmigrations')
            if result.ok:
                input('Press enter to continue.')
            else:
                raise Exception(
                    f'Failed to clear migration history for {app_name}: ' f'{result.stderr}'
                )
        else:
            print(f'Skipped {app_name} because it only has {n_migrations} migrations.')
    # Remove old migration files.
    if input('\n Proceed to remove migration files? [Y/n] ') != NEGATIVE:
        remove_migrations(context, app=app_name)


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
    app_name = app or input('App name: ')
    app_dir = join(settings.BASE_DIR, 'apps', app_name)
    migrations_dir = join(app_dir, MIGRATIONS_DIRNAME)
    squashed_migrations_dir = join(app_dir, SQUASHED_MIGRATIONS_DIRNAME)
    # Remove the squashed_migrations directory.
    if os.path.exists(squashed_migrations_dir):
        print(f'Removing {squashed_migrations_dir}...')
        context.run(f'rm -r {squashed_migrations_dir}')
        print(f'Removed {squashed_migrations_dir}')
    # Clear migration files from the migrations directory.
    if hard:
        # Delete the migration files.
        command = (
            f'find {migrations_dir} -type f -name "*.py" -not -name "__init__.py" '
            f'-exec rm {BASH_PLACEHOLDER} \;'  # noqa: W605
        )
        print(command)
        context.run(command)
    else:
        # Move the migration files to the squashed_migrations directory.
        context.run(f'mkdir {squashed_migrations_dir}')
        context.run(
            f'find . -type f -path "{app_dir}/migrations/*.py" -not -name "__init__.py" '
            f'-exec echo "{BASH_PLACEHOLDER}" \;'  # noqa: W605
        )
        command = (
            f'find . -type f -path "{app_dir}/migrations/*.py" -not -name "__init__.py" '
            f'-exec mv {BASH_PLACEHOLDER} {squashed_migrations_dir}/ \;'  # noqa: W605
        )
        print(command)
        context.run(command)
        if not glob(join(squashed_migrations_dir, '*.py')):
            print(f'ERROR: Failed to move migration files to {squashed_migrations_dir}')
    input('Press enter to continue.')
    command = (
        f'find {app_dir} -path "migrations/*.pyc" '
        f'-exec rm {BASH_PLACEHOLDER} \;'  # noqa: W605
    )
    print(command)
    context.run(command)
    print(f'Removed migration files from {app_name}.')


def restore_squashed_migrations(context: Context = CONTEXT, app: str = ''):
    """Restore migrations with squashed_migrations."""
    app_name = app or input('App name: ')
    app_dir = join(settings.BASE_DIR, 'apps', app_name)
    migrations_dir = join(app_dir, MIGRATIONS_DIRNAME)
    squashed_migrations_dir = join(app_dir, SQUASHED_MIGRATIONS_DIRNAME)
    # TODO: only do this if there are files in the squashed_migrations dir
    squashed_migrations_exist = os.path.exists(squashed_migrations_dir) and os.listdir(
        path=squashed_migrations_dir
    )
    if squashed_migrations_exist:
        # Remove the replacement migrations
        migration_files_path = f'{migrations_dir}/*.py'
        context.run(
            f'find . -type f -path "{migration_files_path}" '
            f'-not -name "__init__.py" '
            f'-exec rm {BASH_PLACEHOLDER} \;'  # noqa: W605
        )
        # Restore the squashed migrations
        context.run(
            f'find {squashed_migrations_dir} -type f -name "*.py" '
            f'-exec mv {BASH_PLACEHOLDER} {migrations_dir}/ \;'  # noqa: W605
        )
        # Remove the squashed_migrations directory
        if os.path.exists(squashed_migrations_dir):
            context.run(f'rm -r {squashed_migrations_dir}')
        print(f'Removed squashed migrations from {app_name}.')
    else:
        print(f'There are no squashed migrations to remove from {app_name}.')


def seed(
    context: Context = CONTEXT,
    remote: bool = False,
    migrate: bool = False,
    up: bool = False,
):
    """Seed the database."""
    db_volume = 'modularhistory_postgres_data'
    if remote:
        sync(context=context, push=False)
    elif not os.path.isfile(settings.DB_INIT_FILEPATH):
        raise Exception(f'Seed does not exist at {settings.DB_INIT_FILEPATH}.')
    with context.cd(settings.ROOT_DIR):
        # Remove the data volume, if it exists
        print('Stopping containers...')
        stop_containers = context.run('docker compose down', warn=True)
        while not stop_containers.ok:
            input(
                'Failed to stop containers. Something might be wrong with the Docker '
                'environment. Here are a couple things to try (in a separate shell):\n'
                '  - Rerun this command: docker compose down\n'
                '  - Manually restart docker, then try again to run the same command\n'
                'Once `docker compose down` is successful, hit enter to continue. '
            )
            stop_containers = context.run('docker compose down', warn=True)
        print('Wiping postgres data volume...')
        context.run(f'docker volume rm {db_volume}', warn=True)
        # Start up the postgres container, automatically running init.sql.
        print('Initializing postgres data...')
        context.run('docker compose up -d postgres')
        print('Waiting for Postgres to finish recreating the database...')
        sleep(15)  # Give postgres time to recreate the database.
        if migrate:
            context.run('docker compose run django python manage.py migrate')
        if IS_DEV:
            email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
            context.run(
                "docker compose run django bash -c '"
                'python manage.py createsuperuser --no-input '
                f'--username={email} --email={email} &>/dev/null'
                "'",
                pty=True,
            )
        if up:
            context.run('docker compose up -d django next')


def squash_migrations(context: Context = CONTEXT, app: str = '', dry: bool = False):
    """
    Squash migrations.

    See https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html.
    """
    app_name = app or input('App name: ')

    # Create a db backup
    if dry and input('Create db backup? [Y/n] ') != NEGATIVE:
        context.run('python manage.py dbbackup')

    # Make sure models fit the current db schema
    context.run('python manage.py makemigrations')
    if input('Run db migrations? [Y/n] ') != NEGATIVE:
        migrate(context, noninteractive=True)

    # Remove any compiled Python files.
    for pyc in iglob('**/migrations/*.pyc'):
        os.remove(pyc)

    # Clear the migrations history for each app
    clear_migration_history(context, app=app_name)

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
            'Finished squashing migrations.\n'
            'Take a minute to test the app locally, then press any key '
            'to restore the squashed migrations.'
        )
        context.run('python manage.py dbrestore --database="default" --noinput')
        restore_squashed_migrations(context)


def sync(
    context: Context = CONTEXT,
    push: bool = False,
):
    """Sync the db seed from source to destination, modifying destination only."""
    files.sync(
        local_dir=settings.DB_INIT_DIR,
        remote_dir='/database/',
        push=push,
        context=context,
    )
