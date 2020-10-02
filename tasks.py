"""
These "tasks" or commands can be invoked from the console with an `invoke ` preface.  For example:
    invoke setup
    invoke lint
    invoke test

Note: Invoke must first be installed by running setup.sh or `poetry install`.

See Invoke's documentation: http://docs.pyinvoke.org/en/stable/.
"""

import os

from invoke import task


@task
def commit(context):
    """Commit code changes."""
    # Check that the branch is correct
    context.run('git branch')
    print()
    print(f'Current branch: ')
    branch = context.run('git branch --show-current').stdout
    print()
    input('If you are on the intended branch, hit enter to continue. ')

    # Stage files, if needed
    context.run('git status')
    while input('Do files need to be staged? [Y/n] ') != 'n':
        files_to_stage = input('Enter filenames and/or patterns: ')
        context.run(f'git add {files_to_stage}')
        print()
        context.run('git status')

    # Set the commit message
    commit_msg = None
    request_commit_msg = True
    while request_commit_msg:
        commit_msg = input('Enter a commit message (without double quotes): ')
        if commit_msg and '"' not in commit_msg:
            request_commit_msg = False
    print(f'\n{commit_msg}\n')
    if input('Is this commit message correct? [Y/n] ') != 'n':
        context.run(f'git commit -m "{commit_msg}"')
    print()
    if input('Push changes to remote branch? [Y/n] ') != 'n':
        context.run(f'git push')
        print(f'View diff: https://github.com/ModularHistory/modularhistory/compare/{branch}')
    else:
        print('To push your changes to the repository, use the following command:')
        print('git push')


@task
def lint(context, *args):
    """Run linters."""
    # Run Flake8
    flake8_cmd = ' '.join(['flake8', *args])
    context.run(flake8_cmd)

    # Run MyPy
    mypy_cmd = ' '.join(['mypy', *args, '--show-error-codes'])
    context.run(mypy_cmd)


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
def squash_migrations(context):
    """
    Squash migrations.

    See https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html.
    """
    prod_db_env_var = 'USE_PROD_DB'
    prod_db_env_var_values = (
        ('local', ''),
        ('production', 'True')
    )

    # Connect to production db
    context.run('cloud_sql_proxy --help')

    # Make sure models fit the current db schema
    for environment, prod_db_env_var_value in prod_db_env_var_values:
        os.environ[prod_db_env_var] = prod_db_env_var_value
        print(f'Making sure that models fit the current {environment} db schema...')
        context.run('python manage.py makemigrations && python manage.py migrate')
        input('Continue? [Y/n] ')
        del os.environ[prod_db_env_var]

    # Show current migrations
    print('Migrations before squashing:')
    context.run('python manage.py showmigrations')
    input('Continue? [Y/n] ')

    # Clear the migrations history for each app
    apps_with_migrations = (
        'account',
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
    for app in apps_with_migrations:
        for environment, prod_db_env_var_value in prod_db_env_var_values:
            os.environ[prod_db_env_var] = prod_db_env_var_value
            print(f'Clearing migration history for the {app} app in {environment} ...')
            context.run(f'python manage.py migrate --fake {app} zero')
            del os.environ[prod_db_env_var]
        input('Proceed to delete migration files? [Y/n] ')
        context.run(f'find {app} -path migrations/*.py -not -name "__init__.py" -delete')
        context.run(f'find {app} -path migrations/*.pyc" -delete')
        input('Continue? [Y/n] ')
    print()

    # Regenerate migrations
    print('Regenerating migrations...')
    context.run('python manage.py makemigrations')
    input('Continue? [Y/n] ')

    # Fake the migrations
    for environment, prod_db_env_var_value in prod_db_env_var_values:
        os.environ[prod_db_env_var] = prod_db_env_var_value
        print(f'Running fake migrations for {environment} db...')
        context.run('python manage.py migrate --fake-initial')
        del os.environ[prod_db_env_var]
        print()
    print('Migrations after squashing:')
    context.run('python manage.py showmigrations')

    # Done
    print('Successfully squashed migrations.')


@task
def test(context):
    """Run tests."""
    context.run('pytest -n 3 --hypothesis-show-statistics')


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
