"""
These "tasks" or commands can be invoked from the console with an `invoke ` preface.  For example:
    invoke setup
    invoke lint
    invoke test

Note: Invoke must first be installed by running setup.sh or `poetry install`.

See Invoke's documentation: http://docs.pyinvoke.org/en/stable/.
"""

from invoke import task


@task
def commit(context):
    """Commit code changes."""
    # Check that the branch is correct
    context.run('git branch')
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
    """Run nox (to run linters and tests in multiple environments)."""
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
