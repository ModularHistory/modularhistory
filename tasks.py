"""
These "tasks" or commands can be invoked from the console via the "invoke" command.

For example:
``
invoke lint
invoke test
``

Note: Invoke must first be installed by running setup.sh or `poetry install`.

See Invoke's documentation: http://docs.pyinvoke.org/en/stable/.
"""

import os
from os.path import join
from glob import glob, iglob
from typing import Any, Callable, Optional, TypeVar

import django
from django.core.management import call_command
from django.db import transaction

from modularhistory.linters import flake8 as lint_with_flake8, mypy as lint_with_mypy
from monkeypatch import fix_annotations

if fix_annotations():
    import invoke

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modularhistory.settings')
django.setup()

PROD_DB_ENV_VAR = 'USE_PROD_DB'
MIGRATIONS_DIRNAME = 'migrations'
SQUASHED_MIGRATIONS_DIRNAME = 'squashed_migrations'
MAX_MIGRATION_COUNT = 3
BASH_PLACEHOLDER = '{}'  # noqa: P103
NEGATIVE = 'n'
AFFIRMATIVE = 'y'
SPACE = ' '
LOCAL = 'local'
PRODUCTION = 'production'
APPS_WITH_MIGRATIONS = (
    # 'account',  # affected by social_django
    'entities',
    'images',
    'markup',
    'occurrences',
    'places',
    'quotes',
    'search',
    'sources',
    'staticpages',
    'topics',
)

TaskFunction = TypeVar('TaskFunction', bound=Callable[..., Any])


def task(task_function: TaskFunction) -> TaskFunction:
    """Wrap invoke.task to enable type annotations."""
    task_function.__annotations__ = {}
    return invoke.task(task_function)


@task
def blacken(context):
    """Safely run `black` code formatter against all Python files."""
    for filename in iglob('[!.]**/*.py', recursive=True):
        print(f'Checking {filename}...')
        diff_output = context.run(f'black {filename} --diff', pty=True).stdout
        print(diff_output)
        if 'file would be left unchanged' not in diff_output:
            if input('Overwrite file? [Y/n] ') != NEGATIVE:
                context.run(f'black {filename}')


@task
def commit(context):
    """Commit and (optionally) push code changes."""
    # Check that the branch is correct
    context.run('git branch')
    print()
    print('Current branch: ')
    branch = context.run('git branch --show-current').stdout
    print()
    if input('Continue? [Y/n] ') == NEGATIVE:
        return

    # Stage files, if needed
    context.run('git status')
    print()
    if input('Stage all changed files? [Y/n] ') == NEGATIVE:
        while input('Do files need to be staged? [Y/n] ') != NEGATIVE:
            files_to_stage = input('Enter filenames and/or patterns: ')
            context.run(f'git add {files_to_stage}')
            print()
            context.run('git status')
    else:
        context.run('git add .')

    # Set the commit message
    commit_msg = None
    request_commit_msg = True
    while request_commit_msg:
        print()
        commit_msg = input('Enter a commit message (without double quotes): ')
        if commit_msg and '"' not in commit_msg:
            request_commit_msg = False
    print(f'\n{commit_msg}\n')

    # Commit the changes
    if input('Is this commit message correct? [Y/n] ') != NEGATIVE:
        context.run(f'git commit -m "{commit_msg}"')
    print()

    # Push the changes, if desired
    if input('Push changes to remote branch? [Y/n] ') == NEGATIVE:
        print('To push your changes to the repository, use the following command:')
        print('git push')
    else:
        context.run('git push')
        print()
        diff_link = f'https://github.com/ModularHistory/modularhistory/compare/{branch}'
        print(f'Create pull request / view diff: {diff_link}')


@task
def flake8(context, *args):
    """Run flake8 linter."""
    lint_with_flake8()


@task
def mypy(context, *args):
    """Run mypy static type checker."""
    lint_with_mypy()


@task
def lint(context, *args):
    """Run linters."""
    # Run Flake8
    print('Running flake8...')
    lint_with_flake8()

    # Run MyPy
    print('Running mypy...')
    lint_with_mypy()


@task
def makemigrations(context, noninteractive: bool = False):
    """Safely create migrations."""
    _makemigrations(context, noninteractive=noninteractive)


def _makemigrations(context, noninteractive: bool = False):
    interactive = not noninteractive
    make_migrations = True
    if interactive:
        print('Doing a dry run first...')
        context.run('python manage.py makemigrations --dry-run')
        make_migrations = input('^ Do these changes look OK? [Y/n]') != NEGATIVE
    if make_migrations:
        context.run('python manage.py makemigrations')


@task
def migrate(context, *args, noninteractive: bool = False):
    """Safely run db migrations."""
    _migrate(context, *args, noninteractive=noninteractive)


def _migrate(context, *args, environment=LOCAL, noninteractive: bool = False):
    interactive = not noninteractive
    _set_prod_db_env_var(PROD_DB_ENV_VAR_VALUES.get(environment))
    if interactive and input('Create db backup? [Y/n] ') != NEGATIVE:
        context.run('python manage.py dbbackup')
    print('Running migrations...')
    with transaction.atomic():
        call_command('migrate', *args)
    print()
    context.run('python manage.py showmigrations')
    print()
    if interactive and input('Did migrations run successfully? [Y/n] ') == NEGATIVE:
        context.run('python manage.py dbrestore')


@task
def nox(context, *args):
    """Run linters and tests in multiple environments using nox."""
    nox_cmd = SPACE.join(['nox', *args])
    context.run(nox_cmd)
    context.run('rm -r modularhistory.egg-info')


@task
def setup(context, noninteractive: bool = False):
    """Install all dependencies; set up the ModularHistory application."""
    args = [_relativize('setup.sh')]
    if noninteractive:
        args.append('--noninteractive')
    command = SPACE.join(args).strip()
    context.run(command)
    context.run('rm -r modularhistory.egg-info')


@task
def squash_migrations(context, dry: bool = True):
    """Squash migrations."""
    _squash_migrations(context, dry)


PROD_DB_ENV_VAR_VALUES = {LOCAL: '', PRODUCTION: 'True'}


def _squash_migrations(context, dry: bool = True):
    """
    Squash migrations.

    See https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html.
    """
    _escape_prod_db()
    # By default, only squash migrations in dev environment
    prod_db_env_var_values = (
        [(LOCAL, '')] if dry else [(LOCAL, ''), (PRODUCTION, 'True')]
    )

    # Create a db backup
    if dry and input('Create db backup? [Y/n] ') != NEGATIVE:
        context.run('python manage.py dbbackup')

    # Make sure models fit the current db schema
    context.run('python manage.py makemigrations')
    for environment, _prod_db_env_var_value in prod_db_env_var_values:
        _migrate(context, environment=environment, noninteractive=True)
        # Clear the migrations history for each app
        _clear_migration_history(context, environment=environment)
    _escape_prod_db()

    # Regenerate migration files.
    _makemigrations(context, noninteractive=True)
    if input('\n Continue? [Y/n] ') == NEGATIVE:
        return

    # Fake the migrations.
    for environment, _ in prod_db_env_var_values:
        print(f'\n Running fake migrations for {environment} db...')
        _migrate(
            context, '--fake-initial', environment=environment, noninteractive=True
        )
    _escape_prod_db()

    if dry:
        input(
            'Completed dry run of squashing migrations.\n'
            'Take a minute to test the app locally, then press any key '
            'to proceed to squash migrations in production environment.'
        )
        context.run('python manage.py dbrestore --database="default" --noinput')
        _restore_squashed_migrations(context)
        if input('Squash migrations for real (in production db)? [Y/n] ') != NEGATIVE:
            _squash_migrations(context, dry=False)


def _clear_migration_history(context, environment: str = LOCAL):
    """."""
    with transaction.atomic():
        for app in APPS_WITH_MIGRATIONS:
            n_migrations = (
                len(os.listdir(path=_relativize(join(app, MIGRATIONS_DIRNAME)))) - 1
            )
            if n_migrations > MAX_MIGRATION_COUNT:
                # Fake reverting all migrations.
                _set_prod_db_env_var(PROD_DB_ENV_VAR_VALUES.get(environment))
                print(
                    f'\n Clearing migration history for the {app} app in {environment} ...'
                )
                _revert_to_migration_zero(context, app)
            else:
                print(
                    f'Skipping {app} since there are only {n_migrations} migration files...'
                )
    # Remove old migration files.
    if input('\n Proceed to remove migration files? [Y/n] ') != NEGATIVE:
        _remove_migrations(context)


def _remove_migrations(context, app: Optional[str] = None, hard: bool = False):
    """Remove migration files."""
    apps = [app] if app else APPS_WITH_MIGRATIONS
    print(f'Removing migrations from {apps}...')
    for app in apps:
        _remove_migrations_from_app(context, app, hard=hard)


def _remove_migrations_from_app(context, app: str, hard: bool = False):
    # Remove the squashed_migrations directory
    migrations_path = _relativize(join(app, MIGRATIONS_DIRNAME))
    squashed_migrations_path = _relativize(join(app, SQUASHED_MIGRATIONS_DIRNAME))
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
        print('Files to remove:')
        context.run(
            f'find . -type f -path "./{app}/migrations/*.py" -not -name "__init__.py" '
            f'-exec echo "{BASH_PLACEHOLDER}" \;'  # noqa: W605
        )
        squashed_migrations_dir = _relativize(join(app, SQUASHED_MIGRATIONS_DIRNAME))
        command = (
            f'find . -type f -path "./{app}/migrations/*.py" -not -name "__init__.py" '
            f'-exec mv {BASH_PLACEHOLDER} {squashed_migrations_dir}/ \;'  # noqa: W605
        )
        print(command)
        context.run(command)
        if not glob(_relativize(f'{join(app, SQUASHED_MIGRATIONS_DIRNAME)}/*.py')):
            raise Exception(
                f'Could not move migration files to {SQUASHED_MIGRATIONS_DIRNAME} dir.'
            )
    command = (
        f'find {_relativize(app)} -path "migrations/*.pyc" '
        f'-exec rm {BASH_PLACEHOLDER} \;'  # noqa: W605
    )
    print(command)
    context.run(command)
    print(f'Removed migration files from {app}.')


def _revert_to_migration_zero(context, app: str):
    """Spoofreverting migrations by running a fake migration to `zero`."""
    context.run(f'python manage.py migrate {app} zero --fake')
    print()
    print('Migrations after fake reversion:')
    context.run('python manage.py showmigrations')
    print()


def _restore_squashed_migrations(context):
    """Restore migrations with squashed_migrations."""
    for app in APPS_WITH_MIGRATIONS:
        squashed_migrations_dir = _relativize(join(app, SQUASHED_MIGRATIONS_DIRNAME))
        # TODO: only do this if there are files in the squashed_migrations dir
        squashed_migrations_exist = os.path.exists(
            squashed_migrations_dir
        ) and os.listdir(path=squashed_migrations_dir)
        if squashed_migrations_exist:
            # Remove the replacement migrations
            migration_files_path = _relativize(f'{app}/migrations/*.py')
            context.run(
                f'find . -type f -path "{migration_files_path}" '
                f'-not -name "__init__.py" '
                f'-exec rm {BASH_PLACEHOLDER} \;'  # noqa: W605
            )
            # Restore the squashed migrations
            migrations_dir = _relativize(f'{join(app, MIGRATIONS_DIRNAME)}')
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


@task
def restore_squashed_migrations(context):
    """Restore migrations with squashed_migrations."""
    _restore_squashed_migrations(context)


@task
def test(context):
    """Run tests."""
    pytest_args = [
        '-n 3',
        # '-x',
        '--maxfail=2',
        # '--hypothesis-show-statistics',
    ]
    _escape_prod_db()
    context.run(f'coverage run -m pytest {" ".join(pytest_args)}')
    context.run('coverage combine')


def _set_prod_db_env_var(env_var_value: str):
    """Setthe env var that specifies whether to use the production database."""
    os.environ[PROD_DB_ENV_VAR] = env_var_value


def _escape_prod_db():
    """Removethe env var that specifies whether to use the production database."""
    try:
        del os.environ[PROD_DB_ENV_VAR]
    except KeyError:
        pass


# TODO
# @task
# def deploy(context):
#     """Run linters."""
#     context.run('python manage.py collectstatic')
#     app_file = 'gc_app.yaml'
#     env_file = 'gc_env.yaml'
#     perm_env_file = 'gc_env.yaml.perm'
#     temp_env_file = 'gc_env.yaml.tmp'
#     # TODO: load secrets to env
#     context.run(
#         f'cp {env_file} {perm_env_file} && envsubst < {env_file} > {temp_env_file} '
#         f'&& mv {temp_env_file} {env_file} && gcloud app deploy {app_file}'
#     )
#     context.run(f'mv {perm_env_file} {env_file}')


def _relativize(relative_path: str):
    return join('.', relative_path)
