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
import logging
import os
import re
from glob import glob, iglob
from os.path import join
from pprint import pprint
from typing import Any, Callable, Optional, TypeVar
from zipfile import BadZipFile, ZipFile

import django
import requests
from decouple import config
from dotenv import load_dotenv
from paramiko import SSHClient
from scp import SCPClient

from modularhistory.constants.environments import Environments
from modularhistory.constants.strings import NEGATIVE, SPACE

try:
    from modularhistory.linters import flake8 as lint_with_flake8
    from modularhistory.linters import mypy as lint_with_mypy
except ModuleNotFoundError:
    print('Skipped importing nonexistent linting modules.')
from modularhistory.utils import commands
from modularhistory.utils.files import relativize
from monkeypatch import fix_annotations

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modularhistory.settings')
django.setup()

from django.conf import settings  # noqa: E402

if fix_annotations():
    import invoke

TaskFunction = TypeVar('TaskFunction', bound=Callable[..., Any])

BACKUPS_DIR = '.backups'
DB_INIT_FILE = join(BACKUPS_DIR, 'init.sql')
MEDIA_INIT_FILE = join(BACKUPS_DIR, 'media.tar.gz')
SERVER: Optional[str] = config('SERVER', default=None)
SERVER_SSH_PORT: Optional[int] = config('SERVER_SSH_PORT', default=22)
SERVER_USERNAME: Optional[str] = config('SERVER_USERNAME', default=None)
SERVER_PASSWORD: Optional[str] = config('SERVER_PASSWORD', default=None)

GITHUB_API_BASE_URL = 'https://api.github.com'
OWNER = 'modularhistory'
REPO = 'modularhistory'
GITHUB_ACTIONS_BASE_URL = f'{GITHUB_API_BASE_URL}/repos/{OWNER}/{REPO}/actions'
GITHUB_CREDENTIALS_FILE = '.github/.credentials'

SEEDS = {
    'env-file': '.env',
    'init-sql': '.backups/init.sql',
    'media': '.backups/media.tar.gz',
}


def command(task_function: TaskFunction) -> TaskFunction:
    """Wrap invoke.task to enable type annotations."""
    task_function.__annotations__ = {}
    return invoke.task(task_function)


@command
def autoformat(context):
    """Safely run autoformatters against all Python files."""
    commands.autoformat(context)


@command
def build(
    context,
    github_actor: str,
    access_token: str,
    sha: str,
    push: bool = False,
    # default environment is delegated to ARG statement in Dockerfile
    environment: Optional[str] = None,
):
    """Build the Docker images used by ModularHistory."""
    if not access_token:
        access_token = config('CR_PAT', default=None)
    if not all([github_actor, access_token, sha]):
        raise ValueError('Missing one or more required args: github_actor, access_token, sha.')
    if push and environment != Environments.PROD:
        raise ValueError(f'Cannot push image built for {environment} environment.')
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
        build_command = (
            f'docker build . -f Dockerfile.{image_name} -t {image}:{sha} '
            f'--build-arg ENVIRONMENT={environment}'
        )
        if extant:
            build_command = f'{build_command} --cache-from {image}:latest'
        print(build_command)
        context.run(build_command)
        context.run(f'docker tag {image}:{sha} {image}:latest')
        context.run(f'docker run -d {image}:{sha}')
        if push:
            print(f'Pushing new image ({image}:{sha}) to the container registry..."')
            context.run(f'docker push {image}:{sha} && docker push {image}:latest')


@command
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


@command
def dbbackup(context, redact: bool = False, push: bool = False):
    """Create a database backup file."""
    # based on https://github.com/django-dbbackup/django-dbbackup#dbbackup
    commands.back_up_db(context, redact=redact, push=push)


@command
def flake8(context, *args):
    """Run flake8 linter."""
    lint_with_flake8(interactive=True)


@command
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


@command
def get_db_backup(context, env: str = Environments.DEV):
    """Get latest db backup from remote storage."""
    if SERVER and SERVER_SSH_PORT and SERVER_USERNAME and SERVER_PASSWORD:
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
        from modularhistory.storage.mega_storage import mega_clients  # noqa: E402

        mega_client = mega_clients[env]
        pprint(mega_client.get_user())
        init_file = 'init.sql'
        init_file_path = join(BACKUPS_DIR, init_file)
        if os.path.exists(init_file_path):
            context.run(f'mv {init_file_path} {init_file_path}.prior', warn=True)
        backup_file = mega_client.find(init_file, exclude_deleted=True)
        if backup_file:
            mega_client.download(backup_file)
            context.run(f'mv {init_file} {init_file_path}', warn=True)
        else:
            print(f'Could not find {init_file}.')


@command
def get_media_backup(context, env: str = Environments.DEV):
    """Seed latest media backup from remote storage."""
    from modularhistory.storage.mega_storage import mega_clients  # noqa: E402

    mega_client = mega_clients[env]
    pprint(mega_client.get_user())
    media_archive_name = 'media.tar.gz'
    media_archive = mega_client.find(media_archive_name, exclude_deleted=True)
    if media_archive:
        mega_client.download(media_archive)
        context.run(f'mv {media_archive_name} {join(BACKUPS_DIR, media_archive_name)}', warn=True)
    else: 
        print(f'Could not find {media_archive_name}')


def pat_is_valid(context, username: str, pat: str) -> bool:
    """Return a bool reflecting whether the PAT is valid."""
    pat_validity_check = (
        f'curl -u {username}:{pat} '
        '-s -o /dev/null -I -w "%{http_code}" '
        f'https://api.github.com/user'
    )
    return '200' in context.run(pat_validity_check, hide='out').stdout


@command
def mediabackup(context, redact: bool = False, push: bool = False):
    """Create a media backup file."""
    # based on https://github.com/django-dbbackup/django-dbbackup#mediabackup
    commands.back_up_media(context, redact=redact, push=push)


@command
def mypy(context, *args):
    """Run mypy static type checker."""
    lint_with_mypy()


@command
def lint(context, *args):
    """Run linters."""
    # Run Flake8
    print('Running flake8...')
    lint_with_flake8(interactive=True)

    # Run MyPy
    print('Running mypy...')
    lint_with_mypy()


@command
def makemigrations(context, noninteractive: bool = False):
    """Safely create migrations."""
    commands.makemigrations(context, noninteractive=noninteractive)


@command
def migrate(context, *args, noninteractive: bool = False):
    """Safely run db migrations."""
    commands.migrate(context, *args, noninteractive=noninteractive)


@command
def restore_squashed_migrations(context):
    """Restore migrations with squashed_migrations."""
    commands.restore_squashed_migrations(context)


@command
def seed(context, remote: bool = False):
    """Seed a dev database, media directory, and env file."""
    workflow = 'seed.yml'
    n_expected_new_artifacts = 3
    if os.path.exists(GITHUB_CREDENTIALS_FILE):
        print('Reading credentials...')
        with open(GITHUB_CREDENTIALS_FILE, 'r') as personal_access_token:
            credentials = personal_access_token.read()
            username, pat = credentials.split(':')
    else:
        username = input('Enter your GitHub username/email: ')
        pat = input('Enter your Personal Access Token: ')
        while not pat_is_valid(context, username, pat):
            print('Invalid GitHub credentials.')
            username = input('Enter your GitHub username/email: ')
            pat = input('Enter your Personal Access Token: ')
        with open(GITHUB_CREDENTIALS_FILE, 'w') as file:
            file.write(f'{username}:{pat}')
    session = requests.Session()
    session.auth = signature = (username, pat)
    session.headers.update({'Accept': 'application/vnd.github.v3+json'})
    artifacts_url = f'{GITHUB_ACTIONS_BASE_URL}/artifacts'
    artifacts = extant_artifacts = session.get(
        artifacts_url,
    ).json()['artifacts']
    n_extant_artifacts = len(extant_artifacts)
    print('Dispatching workflow...')
    response = session.post(
        f'{GITHUB_ACTIONS_BASE_URL}/workflows/{workflow}/dispatches',
        data=json.dumps({'ref': 'main'}),
    ).json()
    print(response)
    while len(artifacts) < n_extant_artifacts + n_expected_new_artifacts:
        print('Waiting for artifacts...')
        context.run('sleep 15')
        artifacts = session.get(
            artifacts_url,
        ).json()['artifacts']
    artifacts = artifacts[:n_expected_new_artifacts]
    dl_urls = {}
    zip_dl_url_key = 'archive_download_url'
    for artifact in artifacts:
        artifact_name = artifact['name']
        if artifact_name not in SEEDS:
            logging.error(f'Unexpected artifact name: "{artifact_name}"')
            continue
        dl_urls[artifact_name] = artifact[zip_dl_url_key]
    for seed_name, dest_path in SEEDS.items():
        zip_file = f'{seed_name}.zip'
        context.run(
            f'curl -u {signature} -L {dl_urls[seed_name]} --output {zip_file} '
            f'&& sleep 3 && echo "Downloaded {zip_file}"'
        )
        try:
            with ZipFile(zip_file, 'r') as archive:
                if os.path.exists(dest_path):
                    if os.path.isfile(dest_path):
                        context.run(f'mv {dest_path} {dest_path}.prior')
                    else:
                        print(f'{dest_path} already exists; skipping {zip_file}')
                        continue
                archive.extractall()
            context.run(f'rm {zip_file}')
        except BadZipFile as err:
            print(f'Could not extract from {zip_file} due to {err}')
        if '/' in dest_path:
            dest_dir, filename = os.path.dirname(dest_path), os.path.basename(dest_path)
        else:
            dest_dir, filename = '.', dest_path
        if dest_dir != '.':
            context.run(f'mv {filename} {dest_path}')
    db_volume = 'modularhistory_postgres_data'
    seed_exists = os.path.exists(DB_INIT_FILE) and os.path.isfile(DB_INIT_FILE)
    if not seed_exists:
        raise Exception('Seed does not exist')

    # Seed the db
    context.run(f'docker-compose down; docker volume rm {db_volume}')
    context.run('docker-compose up -d postgres')

    # Seed the media directory only if needed
    if not len(glob('media/*')):
        context.run(
            f'python manage.py mediarestore -z --noinput -i {MEDIA_INIT_FILE} -q'
        )


@command
def setup(context, noninteractive: bool = False):
    """Install all dependencies; set up the ModularHistory application."""
    args = [relativize('setup.sh')]
    if noninteractive:
        args.append('--noninteractive')
    command = SPACE.join(args).strip()
    context.run(command)
    context.run('rm -r modularhistory.egg-info')


@command
def squash_migrations(context, dry: bool = True):
    """Squash migrations."""
    commands.squash_migrations(context, dry)


@command
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
    context.run('coverage combine')


@command
def push_seeds(context):
    """Push db and media seeds to the cloud."""
    commands.push_seeds()


@command
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
