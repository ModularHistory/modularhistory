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

import json
import os
import re
from glob import glob, iglob
from os.path import join
from typing import Any, Callable, Optional, TypeVar
from zipfile import BadZipFile, ZipFile

import django
from decouple import config
from dotenv import load_dotenv
from paramiko import SSHClient
from scp import SCPClient

from modularhistory.constants.environments import Environments
from modularhistory.constants.strings import NEGATIVE, SPACE
from modularhistory.linters import flake8 as lint_with_flake8
from modularhistory.linters import mypy as lint_with_mypy
from modularhistory.utils import commands
from modularhistory.utils.files import relativize
from monkeypatch import fix_annotations

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modularhistory.settings')
django.setup()

from django.conf import settings  # noqa: E402

from modularhistory.storage.mega_storage import mega_client  # noqa: E402

if fix_annotations():
    import invoke

TaskFunction = TypeVar('TaskFunction', bound=Callable[..., Any])

BACKUPS_DIR = '.backups'
DB_INIT_FILE = join(BACKUPS_DIR, 'init.sql')
SERVER: Optional[str] = config('SERVER', default=None)
SERVER_SSH_PORT: Optional[int] = config('SERVER_SSH_PORT', default=22)
SERVER_USERNAME: Optional[str] = config('SERVER_USERNAME', default=None)
SERVER_PASSWORD: Optional[str] = config('SERVER_PASSWORD', default=None)


def task(task_function: TaskFunction) -> TaskFunction:
    """Wrap invoke.task to enable type annotations."""
    task_function.__annotations__ = {}
    return invoke.task(task_function)


@task
def autoformat(context):
    """Safely run autoformatters against all Python files."""
    commands.autoformat(context)


@task
def build(context, github_actor: str, access_token: str, sha: str, push: bool = False):
    """Build the Docker images used by ModularHistory."""
    if not access_token:
        access_token = config('CR_PAT', default=None)
    if not all([github_actor, access_token, sha]):
        raise ValueError
    print('Logging in to GitHub container registry...')
    context.run(
        f'echo {access_token} | docker login ghcr.io -u {github_actor} --password-stdin'
    )
    for image_name in ('django', 'react'):
        image = f'ghcr.io/modularhistory/{image_name}'
        print(f'Pulling {image}:latest...')
        context.run(f'docker pull {image}:latest', warn=True)
        print(f'Building {image}:{sha}...')
        extant = context.run(f'docker inspect {image}:latest', warn=True).exited == 0
        build_command = f'docker build . -f Dockerfile.{image_name} -t {image}:{sha}'
        if extant:
            build_command = f'{build_command} --cache-from {image}:latest'
        print(build_command)
        context.run(build_command)
        context.run(f'docker tag {image}:{sha} {image}:latest')
        context.run(f'docker run -d {image}:{sha}')
        if push:
            print(f'Pushing new image ({image}:{sha}) to the container registry..."')
            context.run(f'docker push {image}:{sha} && docker push {image}:latest')


@task
def commit(context):
    """Commit and (optionally) push code changes."""
    # Check that the branch is correct
    context.run('git branch')
    print('\nCurrent branch: ')
    branch = context.run('git branch --show-current').stdout
    if input('\nContinue? [Y/n] ') == NEGATIVE:
        return

    # Stage files, if needed
    context.run('git status')
    if input('\nStage all changed files? [Y/n] ') == NEGATIVE:
        while input('Do files need to be staged? [Y/n] ') != NEGATIVE:
            files_to_stage = input('Enter filenames and/or patterns: ')
            context.run(f'git add {files_to_stage}')
            context.run('echo "" && git status')
    else:
        context.run('git add .')

    # Commit the changes
    commit_msg = None
    while commit_msg is None:
        commit_msg_input = input('\nEnter a commit message (without double quotes): ')
        if commit_msg_input and '"' not in commit_msg_input:
            commit_msg = commit_msg_input
            break
    print(f'\n{commit_msg}\n')
    if input('Is this commit message correct? [Y/n] ') != NEGATIVE:
        context.run(f'git commit -m "{commit_msg}"')

    # Push the changes, if desired
    if input('\nPush changes to remote branch? [Y/n] ') == NEGATIVE:
        print(
            'To push your changes to the repository, use the following command: \n'
            'git push'
        )
    else:
        context.run('git push')
        diff_link = f'https://github.com/ModularHistory/modularhistory/compare/{branch}'
        print(f'\nCreate pull request / view diff: {diff_link}')


@task
def dbbackup(context, redact: bool = True):
    """Create a database backup file."""
    backups_dir = '.backups'
    context.run('python manage.py dbbackup --noinput')
    temp_file = max(glob(f'{backups_dir}/*'), key=os.path.getctime)
    backup_file = temp_file.replace('.psql', '.sql')
    print('Processing backup file...')
    with open(temp_file, 'r') as unprocessed_backup:
        with open(backup_file, 'w') as processed_backup:
            for line in unprocessed_backup:
                if any(
                    [
                        line.startswith('ALTER '),
                        line.startswith('DROP '),
                    ]
                ):
                    continue
                elif redact and any(['sha256$' in line]):  # TODO
                    continue
                else:
                    processed_backup.write(line)
    print(f'Finished creating backup file: {backup_file}')


@task
def flake8(context, *args):
    """Run flake8 linter."""
    lint_with_flake8(interactive=True)


@task
def generate_artifacts(context):
    """Generate artifacts."""
    from django.db.models import Count
    from wordcloud import WordCloud

    from apps.topics.models import Topic

    print('Building topics.txt...')
    ordered_topics = (
        Topic.objects.prefetch_related('topic_relations')
        .annotate(num_quotes=Count('topic_relations'))
        .order_by('-num_quotes')
    )
    text = '\n'.join([topic.key for topic in ordered_topics])
    with open(join(settings.BASE_DIR, 'topics/topics.txt'), mode='w+') as artifact:
        artifact.write(text)

    print('Building topic_cloud.png...')
    # https://github.com/amueller/word_cloud
    word_cloud = WordCloud(
        background_color=None,
        mode='RGBA',
        width=1200,
        height=700,
        min_font_size=6,
        collocations=False,
        normalize_plurals=False,
        regexp=r'\w[\w\' ]+',
    ).generate(text)
    word_cloud.to_file(join(settings.BASE_DIR, 'static', '_topic_cloud.png'))
    print('Done.')


def _get_db_backup(context):
    """Get latest db backup from server."""
    if SERVER:
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(
            SERVER,
            port=SERVER_SSH_PORT,
            username=SERVER_USERNAME,
            password=SERVER_PASSWORD,
        )
        with SCPClient(ssh.get_transport()) as scp:
            scp.get(BACKUPS_DIR, './', recursive=True)
        latest_backup = max(iglob(join(BACKUPS_DIR, '*sql')), key=os.path.getctime)
        print(latest_backup)
        context.run(f'cp {latest_backup} {DB_INIT_FILE}')
    else:
        init_file = 'init.sql'
        init_archive = f'{init_file}.zip'
        mega_client.download(mega_client.find(init_archive), dest_path=BACKUPS_DIR)
        init_archive_path = f'{BACKUPS_DIR}/{init_archive}'
        init_file_path = f'{BACKUPS_DIR}/{init_file}'
        try:
            with ZipFile(init_archive_path, 'r') as archive:
                if os.path.exists(init_file_path):
                    context.run(f'mv {init_file_path} {init_file_path}.prior')
                archive.extractall()
            context.run(f'rm {init_archive_path}')
        except BadZipFile as err:
            print(f'Could not extract init.sql from {init_archive_path} due to {err}')


@task
def get_db_backup(context):
    """Get latest db backup from server."""
    _get_db_backup(context)


def pat_is_valid(context, username: str, pat: str) -> bool:
    """Return a bool reflecting whether the PAT is valid."""
    pat_validity_check = (
        f'curl -u {username}:{pat} '
        '-s -o /dev/null -I -w "%{http_code}" '
        f'https://api.github.com/user'
    )
    return '200' in context.run(pat_validity_check, hide='out').stdout


@task
def get_env_file(context, dev: bool = False, dry: bool = False):
    """Get a .env file for dev environment."""
    workflow = 'setup.yml'
    owner = 'modularhistory'
    repo = 'modularhistory'
    pat_file = '.github/.pat'
    api_base_url = 'https://api.github.com'
    repo_actions_base_url = f'{api_base_url}/repos/{owner}/{repo}/actions'
    username = input('Enter your GitHub username/email: ')
    if os.path.exists(pat_file):
        print('Reading personal access token...')
        with open(pat_file, 'r') as personal_access_token:
            pat = personal_access_token.read()
    else:
        pat = input('Enter your Personal Access Token: ')
        while not pat_is_valid(context, username, pat):
            print('Invalid GitHub credentials.')
            username = input('Enter your GitHub username/email: ')
            pat = input('Enter your Personal Access Token: ')
        with open(pat_file, 'w') as credentials_file:
            credentials_file.write(pat)
    signature = f'{username}:{pat}'
    default_request_args = f'-u {signature} -H "Accept: application/vnd.github.v3+json"'
    request_for_artifacts = (
        f'curl {default_request_args} {repo_actions_base_url}/artifacts'
    )
    artifacts = extant_artifacts = context.run(request_for_artifacts, hide='out').stdout
    print('Dispatching workflow...')
    context.run(
        f'curl -X POST {default_request_args} '
        f'{repo_actions_base_url}/workflows/{workflow}/dispatches '
        '-d \'{"ref":"main"}\''
    )
    print('Waiting for the .env file...')
    while artifacts == extant_artifacts:
        context.run('sleep 15')
        artifacts = context.run(request_for_artifacts, hide='out').stdout
    artifact = json.loads(artifacts[artifacts.index('{') :])['artifacts'][0]
    archive_download_url = artifact['archive_download_url']
    print(f'Extracted artifact download URL: {archive_download_url}')
    zip_file = 'env-file.zip'
    context.run(
        f'curl -u {signature} -L {archive_download_url} --output {zip_file} '
        f'&& sleep 3 && echo "Downloaded {zip_file}"'
    )
    try:
        with ZipFile(zip_file, 'r') as archive:
            if os.path.exists('.env'):
                context.run('mv .env .env.prior')
            archive.extractall()
        context.run(f'rm {zip_file}')
    except BadZipFile as err:
        print(f'Could not extract .env from {zip_file} due to error: {err}')


@task
def mypy(context, *args):
    """Run mypy static type checker."""
    lint_with_mypy()


@task
def lint(context, *args):
    """Run linters."""
    # Run Flake8
    print('Running flake8...')
    lint_with_flake8(interactive=True)

    # Run MyPy
    print('Running mypy...')
    lint_with_mypy()


@task
def makemigrations(context, noninteractive: bool = False):
    """Safely create migrations."""
    commands.makemigrations(context, noninteractive=noninteractive)


@task
def migrate(context, *args, noninteractive: bool = False):
    """Safely run db migrations."""
    commands.migrate(context, *args, noninteractive=noninteractive)


@task
def restore_squashed_migrations(context):
    """Restore migrations with squashed_migrations."""
    commands.restore_squashed_migrations(context)


def _seed(context):
    """Seed the dev database and media directory."""
    if input('Remove existing database and reinitialize? [Y/n] ') != NEGATIVE:
        seeded = False
        if os.path.exists(DB_INIT_FILE):
            if os.path.isfile(DB_INIT_FILE):
                context.run('docker-compose down')
                context.run('docker volume rm modularhistory_postgres_data')
                context.run('docker-compose up postgres')
                seeded = True
            else:
                context.run(f'rm -r {DB_INIT_FILE}')
        if not seeded:
            _get_db_backup(context)
            _seed(context)
    zipped_media_filename = 'media.zip'
    zipped_media_file = mega_client.find(zipped_media_filename)
    mega_client.download(zipped_media_file, dest_path='.')
    try:
        with ZipFile(zipped_media_filename, 'r') as archive:
            if os.path.exists(f'./{zipped_media_file}'):
                context.run('rm -r media', warn=True, hide='both')
            archive.extractall()
        context.run(f'rm {zipped_media_filename}')
    except BadZipFile as err:
        print(f'Could not extract media from {zipped_media_filename} due to {err}')


@task
def seed(context):
    """Seed the dev database and media directory."""
    _seed(context)


@task
def setup(context, noninteractive: bool = False):
    """Install all dependencies; set up the ModularHistory application."""
    args = [relativize('setup.sh')]
    if noninteractive:
        args.append('--noninteractive')
    command = SPACE.join(args).strip()
    context.run(command)
    context.run('rm -r modularhistory.egg-info')


@task
def squash_migrations(context, dry: bool = True):
    """Squash migrations."""
    commands.squash_migrations(context, dry)


@task
def test(context, docker=False):
    """Run tests."""
    pytest_args = [
        '-v',
        '-n 7',
        # '-x',
        '--maxfail=2',
        # '--hypothesis-show-statistics',
    ]
    command = f'coverage run -m pytest {" ".join(pytest_args)}'
    if settings.ENVIRONMENT == Environments.DEV:
        input('Make sure the dev server is running, then hit Enter/Return.')
    print(command)
    if docker:
        context.run(
            'docker build -t modularhistory/modularhistory . && docker-compose up'
        )
    context.run(command)
    context.run('coverage combine; rm -r archived_logs; mv latest_logs .selenium')


@task
def write_env_file(context, dev: bool = False, dry: bool = False):
    """Write a .env file."""
    destination_file = '.env'
    dry_destination_file = '.env.tmp'
    config_dir = os.path.abspath('config')
    template_file = join(config_dir, 'env.yaml')
    dev_overrides_file = join(config_dir, 'env.dev.yaml')
    if dry and os.path.exists(destination_file):
        load_dotenv(dotenv_path=destination_file)
    elif os.path.exists(destination_file):
        print(f'{destination_file} already exists.')
        return
    envsubst = context.run('envsubst -V &>/dev/null && echo ""', warn=True).exited == 0
    # Write temporary YAML file
    vars = (
        context.run(f'envsubst < {template_file}', hide='out').stdout
        if envsubst
        else commands.envsubst(template_file)
    ).splitlines()
    if dev:
        vars += (
            context.run(f'envsubst < {dev_overrides_file}', hide='out').stdout
            if envsubst
            else commands.envsubst(dev_overrides_file)
        ).splitlines()
    env_vars = {}
    for line in vars:
        match = re.match(r'([A-Z_]+): (.*)', line.strip())
        if not match:
            continue
        var_name, var_value = match.group(1), match.group(2)
        env_vars[var_name] = var_value
    destination_file = dry_destination_file if dry else destination_file
    with open(destination_file, 'w') as env_file:
        for var_name, var_value in env_vars.items():
            env_file.write(f'{var_name}={var_value}\n')
    if dry:
        context.run(f'cat {destination_file} && rm {destination_file}')
