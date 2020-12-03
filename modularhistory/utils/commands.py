# pylint: disable=anomalous-backslash-in-string

import os
from glob import glob, iglob
from os.path import join
from typing import Any, Callable, Iterable, Optional, TypeVar

from django.db import transaction
from invoke.context import Context

from modularhistory.constants.misc import (
    APPS_WITH_MIGRATIONS,
    LOCAL,
    MAX_MIGRATION_COUNT,
    MIGRATIONS_DIRNAME,
    PROD_DB_ENV_VAR,
    PROD_DB_ENV_VAR_VALUES,
    PRODUCTION,
    SQUASHED_MIGRATIONS_DIRNAME,
)
from modularhistory.constants.strings import BASH_PLACEHOLDER, NEGATIVE
from modularhistory.utils.files import relativize

TaskFunction = TypeVar('TaskFunction', bound=Callable[..., Any])

CONTEXT = Context()


def autoformat(context: Context = CONTEXT, files: Optional[Iterable[str]] = None):
    """Autoformat all of ModularHistory's Python code."""
    commands = (
        (
            'autoflake --imports=apps,django,requests,typing,urllib3 '
            '--ignore-init-module-imports --in-place {filename}'
        ),
        ('unify --in-place {filename}'),
        ('isort {filename}'),
        ('black {filename}'),
    )
    file_names = files or iglob('[!.]**/*.py', recursive=True)
    for filename in file_names:
        print(f'Formatting {filename}...')
        for command in commands:
            context.run(command.format(filename=filename))


def clear_migration_history(context: Context = CONTEXT, environment: str = LOCAL):
    """."""
    with transaction.atomic():
        for app in APPS_WITH_MIGRATIONS:
            n_migrations = (
                len(os.listdir(path=relativize(join(app, MIGRATIONS_DIRNAME)))) - 1
            )
            if n_migrations > MAX_MIGRATION_COUNT:
                # Fake reverting all migrations.
                set_prod_db_env_var(PROD_DB_ENV_VAR_VALUES.get(environment))
                print(
                    f'\n Clearing migration history for the {app} app in {environment} ...'
                )
                revert_to_migration_zero(context, app)
            else:
                print(
                    f'Skipping {app} since there are only {n_migrations} migration files...'
                )
    # Remove old migration files.
    if input('\n Proceed to remove migration files? [Y/n] ') != NEGATIVE:
        remove_migrations(context)


def escape_prod_db():
    """Remove the env var that specifies whether to use the production database."""
    try:
        del os.environ[PROD_DB_ENV_VAR]
    except KeyError:
        pass


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


def migrate(
    context: Context = CONTEXT, *args, environment=LOCAL, noninteractive: bool = False
):
    """Safely run db migrations."""
    interactive = not noninteractive
    set_prod_db_env_var(PROD_DB_ENV_VAR_VALUES.get(environment))
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


def set_prod_db_env_var(env_var_value: str):
    """Set the env var that specifies whether to use the production database."""
    os.environ[PROD_DB_ENV_VAR] = env_var_value


def squash_migrations(context: Context = CONTEXT, dry: bool = True):
    """
    Squash migrations.

    See https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html.
    """
    escape_prod_db()
    # By default, only squash migrations in dev environment
    prod_db_env_var_values = (
        [(LOCAL, '')] if dry else [(LOCAL, ''), (PRODUCTION, 'True')]
    )

    # Create a db backup
    if dry and input('Create db backup? [Y/n] ') != NEGATIVE:
        context.run('python manage.py dbbackup')

    # Make sure models fit the current db schema
    context.run('python manage.py makemigrations')
    if input('Run db migrations? [Y/n] ') != NEGATIVE:
        for environment, _prod_db_env_var_value in prod_db_env_var_values:
            migrate(context, environment=environment, noninteractive=True)

    # Clear the migrations history for each app
    context.run('')
    for pyc in iglob('**/migrations/*.pyc'):
        os.remove(pyc)
    for environment, _prod_db_env_var_value in prod_db_env_var_values:
        clear_migration_history(context, environment=environment)
    escape_prod_db()

    # Regenerate migration files.
    makemigrations(context, noninteractive=True)
    if input('\n Continue? [Y/n] ') == NEGATIVE:
        return

    # Fake the migrations.
    for environment, _ in prod_db_env_var_values:  # noqa: WPS441
        print(f'\n Running fake migrations for {environment} db...')  # noqa: WPS441
        migrate(
            context,
            '--fake-initial',
            environment=environment,  # noqa: WPS441
            noninteractive=True,
        )
    escape_prod_db()

    if dry:
        input(
            'Completed dry run of squashing migrations.\n'
            'Take a minute to test the app locally, then press any key '
            'to proceed to squash migrations in production environment.'
        )
        context.run('python manage.py dbrestore --database="default" --noinput')
        restore_squashed_migrations(context)
        if input('Squash migrations for real (in production db)? [Y/n] ') != NEGATIVE:
            squash_migrations(context, dry=False)
