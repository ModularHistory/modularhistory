"""
These "tasks" or commands can be invoked from the console with an `invoke ` preface.  For example:
``
invoke lint
invoke test
``
Note: Invoke must first be installed by running setup.sh or `poetry install`.

See Invoke's documentation: http://docs.pyinvoke.org/en/stable/.
"""

import os
from glob import glob

import django
from django.core.management import call_command
from django.db import transaction
from invoke import task

from modularhistory.linters import flake8, mypy

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modularhistory.settings')
django.setup()

PROD_DB_ENV_VAR = 'USE_PROD_DB'
SQUASHED_MIGRATIONS_DIRNAME = 'squashed_migrations'
MAX_MIGRATION_COUNT = 3
BASH_PLACEHOLDER = '{}'  # noqa: P103
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
    'topics'
)


@task
def commit(context):
    """Commit and (optionally) push code changes."""
    # Check that the branch is correct
    context.run('git branch')
    print()
    print('Current branch: ')
    branch = context.run('git branch --show-current').stdout
    print()
    if input('Continue? [Y/n] ') == 'n':
        return

    # Stage files, if needed
    context.run('git status')
    print()
    if input('Stage all changed files? [Y/n] ') == 'n':
        while input('Do files need to be staged? [Y/n] ') != 'n':
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
    if input('Is this commit message correct? [Y/n] ') != 'n':
        context.run(f'git commit -m "{commit_msg}"')
    print()

    # Push the changes, if desired
    if input('Push changes to remote branch? [Y/n] ') == 'n':
        print('To push your changes to the repository, use the following command:')
        print('git push')
    else:
        context.run('git push')
        print()
        diff_link = f'https://github.com/ModularHistory/modularhistory/compare/{branch}'
        print(f'Create pull request / view diff: {diff_link}')


@task
def lint(context, *args):
    """Run linters."""
    # Run Flake8
    print('Running flake8...')
    flake8()

    # Run MyPy
    print('Running mypy...')
    mypy()


@task
def makemigrations(context):
    """Safely create migrations."""
    print('Doing a dry run first...')
    context.run('python manage.py makemigrations --dry-run')
    if input('^ Do these changes look OK? [Y/n]') != 'n':
        context.run('python manage.py makemigrations')


@task
def migrate(context):
    """Safely run db migrations."""
    if input('Create db backup? [Y/n] ') == 'n':
        context.run('python manage.py dbbackup')
    print('Running migrations...')
    with transaction.atomic():
        call_command('migrate')
    if input('Did migrations run successfully? [Y/n] ') == 'n':
        context.run('python manage.py dbrestore')


@task
def nox(context, *args):
    """Run linters and tests in multiple environments using nox."""
    nox_cmd = ' '.join(['nox', *args])
    context.run(nox_cmd)
    context.run('rm -r modularhistory.egg-info')


@task
def setup(context, noninteractive=False):
    """Install all dependencies; set up the ModularHistory application."""
    args = ['./setup.sh']
    if noninteractive:
        args.append('--noninteractive')
    command = ' '.join(args).strip()
    context.run(command)
    context.run('rm -r modularhistory.egg-info')


@task
def squash_migrations(context, dry=True):
    """Invokable version of _squash_migrations."""
    _squash_migrations(context, dry)


def _squash_migrations(context, dry=True):
    """
    Squash migrations.

    See https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html.
    """
    try:
        del os.environ[PROD_DB_ENV_VAR]
    except KeyError:
        pass

    # By default, only squash migrations in dev environment
    prod_db_env_var_values = [
        ('local', '')
    ] if dry else [
        ('local', ''),
        ('production', 'True')
    ]

    # Create a db backup
    if dry and input('Create db backup? [Y/n] ') != 'n':
        context.run('python manage.py dbbackup')

    # Make sure models fit the current db schema
    context.run('python manage.py makemigrations')
    for _environment, prod_db_env_var_value in prod_db_env_var_values:
        print()
        _set_prod_db_env_var(prod_db_env_var_value)
        context.run('python manage.py migrate')
        del os.environ[PROD_DB_ENV_VAR]

    # Show current migrations
    print('\n Migrations before squashing:')
    context.run('python manage.py showmigrations')

    # Clear the migrations history for each app
    _clear_migration_history(context, prod_db_env_var_values)

    # Regenerate migration files.
    print('\n Regenerating migrations...')
    context.run('python manage.py makemigrations')
    if input('\n Continue? [Y/n] ') == 'n':
        return

    # Fake the migrations.
    for environment, prod_db_env_var_value in prod_db_env_var_values:
        _set_prod_db_env_var(prod_db_env_var_value)
        print(f'\n Running fake migrations for {environment} db...')
        context.run('python manage.py migrate --fake-initial')
        del os.environ[PROD_DB_ENV_VAR]

    # Display the regenerated migrations.
    print('\n Migrations after squashing:')
    context.run('python manage.py showmigrations')

    if dry:
        input(
            'Completed dry run of squashing migrations.\n'
            'Take a minute to test the app locally, then press any key '
            'to proceed to squash migrations in production environment.'
        )
        context.run('python manage.py dbrestore --database="default" --noinput')
        _restore_squashed_migrations(context)
        if input('Squash migrations for real (in production db)? [Y/n] ') != 'n':
            _squash_migrations(context, dry=False)


def _clear_migration_history(context, prod_db_env_var_values):
    """."""
    with transaction.atomic():
        for app in APPS_WITH_MIGRATIONS:
            n_migrations = len(os.listdir(path=f'./{app}/migrations')) - 1
            if n_migrations > MAX_MIGRATION_COUNT:
                # Fake reverting all migrations.
                for environment, prod_db_env_var_value in prod_db_env_var_values:
                    _set_prod_db_env_var(prod_db_env_var_value)
                    print(f'\n Clearing migration history for the {app} app in {environment} ...')
                    _revert_to_migration_zero(context, app)
                    del os.environ[PROD_DB_ENV_VAR]
            else:
                print(f'Skipping {app} since there are only {n_migrations} migration files...')
    # Remove old migration files.
    if input('\n Proceed to remove migration files? [Y/n] ') != 'n':
        _remove_migrations(context)


def _remove_migrations(context, app=None, hard=False):
    """Remove migration files."""
    apps = [app] if app else APPS_WITH_MIGRATIONS
    print(f'Removing migrations from {apps}...')
    for app in apps:
        # Remove the squashed_migrations directory
        migrations_path = f'./{app}/migrations'
        squashed_migrations_path = f'./{app}/{SQUASHED_MIGRATIONS_DIRNAME}'
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
            command = (
                f'find . -type f -path "./{app}/migrations/*.py" -not -name "__init__.py" '
                f'-exec mv {BASH_PLACEHOLDER} ./{app}/{SQUASHED_MIGRATIONS_DIRNAME}/ \;'  # noqa: W605
            )
            print(command)
            context.run(command)
            if not glob(f'./{app}/{SQUASHED_MIGRATIONS_DIRNAME}/*.py'):
                raise Exception(f'Could not move migration files to {SQUASHED_MIGRATIONS_DIRNAME} dir.')
        command = (
            f'find ./{app} -path "migrations/*.pyc" '
            f'-exec rm {BASH_PLACEHOLDER} \;'  # noqa: W605
        )
        print(command)
        context.run(command)
        print(f'Removed migration files from {app}.')


def _revert_to_migration_zero(context, app):
    """Spoofs reverting migrations by running a fake migration to `zero`."""
    context.run(f'python manage.py migrate {app} zero --fake')
    print()
    print('Migrations after fake reversion:')
    context.run('python manage.py showmigrations')
    print()


def _restore_squashed_migrations(context):
    """Restore migrations with squashed_migrations."""
    for app in APPS_WITH_MIGRATIONS:
        squashed_migrations_dir = f'./{app}/{SQUASHED_MIGRATIONS_DIRNAME}'
        # TODO: only do this if there are files in the squashed_migrations dir
        if os.path.exists(squashed_migrations_dir) and os.listdir(path=squashed_migrations_dir):
            # Remove the replacement migrations
            context.run(
                f'find . -type f -path "./{app}/migrations/*.py" -not -name "__init__.py" '
                f'-exec rm {BASH_PLACEHOLDER} \;'  # noqa: W605
            )
            # Restore the squashed migrations
            context.run(
                f'find {squashed_migrations_dir} -type f -name "*.py" '
                f'-exec mv {BASH_PLACEHOLDER} ./{app}/migrations/ \;'  # noqa: W605
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
    context.run(f'coverage run -m pytest {" ".join(pytest_args)}')
    context.run('coverage combine')


def _set_prod_db_env_var(value: str):
    """Set the env var that specifies whether to use the production database."""
    os.environ[PROD_DB_ENV_VAR] = value


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
