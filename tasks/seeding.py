"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

import json
import logging
import os
import re
from os.path import join
from pprint import pprint
from typing import Optional
from zipfile import BadZipFile, ZipFile

import django
import requests
from dotenv import load_dotenv

from modularhistory.constants.environments import Environments
from modularhistory.constants.strings import NEGATIVE
from modularhistory.utils import commands

from .command import command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modularhistory.settings')
django.setup()

from django.conf import settings  # noqa: E402

BACKUPS_DIR = settings.BACKUPS_DIR
DB_INIT_FILE = join(BACKUPS_DIR, 'init.sql')
MEDIA_INIT_FILE = join(BACKUPS_DIR, 'media.tar.gz')

GITHUB_API_BASE_URL = 'https://api.github.com'
OWNER = 'modularhistory'
REPO = 'modularhistory'
GITHUB_ACTIONS_BASE_URL = f'{GITHUB_API_BASE_URL}/repos/{OWNER}/{REPO}/actions'
GITHUB_CREDENTIALS_FILE = '.github/.credentials'

SEEDS = {'env-file': '.env', 'init-sql': '.backups/init.sql'}


def pat_is_valid(context, username: str, pat: str) -> bool:
    """Return a bool reflecting whether the PAT is valid."""
    pat_validity_check = (
        f'curl -u {username}:{pat} '
        '-s -o /dev/null -I -w "%{http_code}" '
        f'https://api.github.com/user'
    )
    return '200' in context.run(pat_validity_check, hide='out').stdout


@command
def seed(
    context,
    remote: bool = False,
    dry: bool = False,
    username: Optional[str] = None,
    pat: Optional[str] = None,
):
    """Seed a dev database, media directory, and env file."""
    workflow = 'seed.yml'
    n_expected_new_artifacts = 2
    if username or pat:
        if username and pat:
            signature = f'{username}:{pat}'
        else:
            raise ValueError('Specify both or neither of --username and --pat.')
    elif os.path.exists(GITHUB_CREDENTIALS_FILE):
        print('Reading credentials...')
        with open(GITHUB_CREDENTIALS_FILE, 'r') as personal_access_token:
            signature = personal_access_token.read()
            username, pat = signature.split(':')
    else:
        print()
        print(
            'To proceed, you will need a GitHub personal access token (PAT) '
            'with "repo" and "workfow" permissions. For instructions on acquiring '
            'a PAT, see the GitHub PAT documentation: \n'
            '    https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token'  # noqa: E501
        )
        print()
        username = input('Enter your GitHub username/email: ')
        pat = input('Enter your GitHub personal access token: ')
        signature = f'{username}:{pat}'
        while not pat_is_valid(context, username, pat):
            print('Invalid GitHub credentials.')
            username = input('Enter your GitHub username/email: ')
            pat = input('Enter your Personal Access Token: ')
            signature = f'{username}:{pat}'
        with open(GITHUB_CREDENTIALS_FILE, 'w') as file:
            file.write(signature)
    session = requests.Session()
    session.auth = (username, pat)
    session.headers.update({'Accept': 'application/vnd.github.v3+json'})
    artifacts_url = f'{GITHUB_ACTIONS_BASE_URL}/artifacts'
    artifacts = session.get(
        artifacts_url,
    ).json()['artifacts']
    latest_artifacts = latest_extant_artifacts = artifacts[:n_expected_new_artifacts]
    print('Dispatching workflow...')
    session.post(
        f'{GITHUB_ACTIONS_BASE_URL}/workflows/{workflow}/dispatches',
        data=json.dumps({'ref': 'main'}),
    )
    while any(artifact in latest_artifacts for artifact in latest_extant_artifacts):
        print('Waiting for artifacts...')
        context.run('sleep 15')
        artifacts = session.get(artifacts_url).json()['artifacts']
        latest_artifacts = artifacts[:n_expected_new_artifacts]
    artifacts = latest_artifacts
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
                soft_deleted_path = f'{dest_path}.prior'
                if os.path.exists(dest_path):
                    if input(f'Overwrite existing {dest_path}? [Y/n] ') != NEGATIVE:
                        context.run(f'mv {dest_path} {soft_deleted_path}')
                archive.extractall()
                if os.path.exists(dest_path) and os.path.exists(soft_deleted_path):
                    print(f'Removing prior {dest_path} ...')
                    os.remove(soft_deleted_path)
            context.run(f'rm {zip_file}')
        except BadZipFile as err:
            print(f'Could not extract from {zip_file} due to {err}')
        if '/' in dest_path:
            dest_dir, filename = os.path.dirname(dest_path), os.path.basename(dest_path)
        else:
            dest_dir, filename = '.', dest_path
        if dest_dir != '.':
            context.run(f'mv {filename} {dest_path}')

    # Seed the db
    db_volume = 'modularhistory_postgres_data'
    seed_exists = os.path.exists(DB_INIT_FILE) and os.path.isfile(DB_INIT_FILE)
    if not seed_exists:
        raise Exception('Seed does not exist')
    # Remove the data volume, if it exists
    print('Wiping postgres data volume...')
    context.run('docker-compose down', warn=True)
    context.run(f'docker volume rm {db_volume}', warn=True, hide='both')
    # Start up the postgres container to automatically run init.sql
    print('Initializing postgres data...')
    context.run('docker-compose up -d postgres')

    # Seed the media directory
    context.run(f'mkdir -p {settings.MEDIA_ROOT}', warn=True)
    print('Syncing media... \n')
    print(
        'This could take a while. Leave this shell running until you '
        'see a "Finished" message. In the meantime, feel free to open '
        'a new shell and start up the app with the following command: \n'
        '    docker-compose up -d dev\n\n'
        '..........................'
    )
    commands.sync_media(context, push=False)
    restore_from_tar = False
    if restore_from_tar and os.path.exists(join(BACKUPS_DIR, 'media.tar.gz')):
        context.run(
            f'python manage.py mediarestore -z --noinput -i {MEDIA_INIT_FILE} -q'
        )
    print('Finished.')


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
        for var_name, var_value in sorted(env_vars.items()):
            env_file.write(f'{var_name}={var_value}\n')
    if dry:
        context.run(f'cat {destination_file} && rm {destination_file}')
