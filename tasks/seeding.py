"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

import json
import logging
import os
import re
from datetime import datetime
from os.path import join
from typing import List, Optional
from zipfile import BadZipFile, ZipFile

import requests
from django.conf import settings
from dotenv import load_dotenv

from modularhistory.constants.strings import NEGATIVE
from modularhistory.utils import files as file_utils
from modularhistory.utils import github as github_utils

from .command import command

BACKUPS_DIR = settings.BACKUPS_DIR
DB_INIT_FILE = join(BACKUPS_DIR, 'init.sql')
MEDIA_INIT_FILE = join(BACKUPS_DIR, 'media.tar.gz')

GITHUB_API_BASE_URL = 'https://api.github.com'
OWNER = 'modularhistory'
REPO = 'modularhistory'
GITHUB_ACTIONS_BASE_URL = f'{GITHUB_API_BASE_URL}/repos/{OWNER}/{REPO}/actions'
GITHUB_CREDENTIALS_FILE = '.github/.credentials'

SEEDS = {'env-file': '.env', 'init-sql': '.backups/init.sql'}


@command
def seed(
    context,
    username: Optional[str] = None,
    pat: Optional[str] = None,
):
    """Seed a dev database, media directory, and env file."""
    workflow = 'seed.yml'
    n_expected_artifacts = 2
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
        username, pat = github_utils.accept_credentials()
    session = github_utils.initialize_session(username=username, pat=pat)
    print('Dispatching workflow...')
    time_posted = datetime.utcnow().replace(microsecond=0)
    session.post(
        f'{GITHUB_ACTIONS_BASE_URL}/workflows/{workflow}/dispatches',
        data=json.dumps({'ref': 'main'}),
    )
    context.run('sleep 5')
    # https://docs.github.com/en/rest/reference/actions#list-workflow-runs-for-a-repository
    workflow_runs: List[dict] = []
    time_waited, wait_interval, timeout = 0, 5, 30
    while not workflow_runs:
        if time_waited > timeout:
            raise TimeoutError('Timed out while attempting to retrieve workflow run.')
        context.run(f'sleep {wait_interval}')
        time_waited += wait_interval
        workflow_runs = session.get(
            f'{GITHUB_ACTIONS_BASE_URL}/runs?event=workflow_dispatch&per_page=5&page=1'
        ).json()['workflow_runs']
        workflow_runs = [
            workflow_run
            for workflow_run in workflow_runs
            if workflow_run['name'] == 'seed'
            and datetime.fromisoformat(workflow_run['created_at'].replace('Z', ''))
            >= time_posted
        ]
    workflow_run = workflow_runs[0]
    workflow_run_url = f'{GITHUB_ACTIONS_BASE_URL}/runs/{workflow_run["id"]}'
    status = initial_status = workflow_run['status']
    artifacts_url = workflow_run['artifacts_url']
    while status == initial_status:
        print(f'Waiting for artifacts... status: {status}')
        context.run('sleep 9')
        status = session.get(workflow_run_url).json().get('status')
    artifacts = session.get(artifacts_url).json().get('artifacts')
    while len(artifacts) < n_expected_artifacts:
        print(f'Waiting for artifacts... status: {status}')
        context.run('sleep 9')
        artifacts = session.get(artifacts_url).json().get('artifacts')
        status = session.get(workflow_run_url).json().get('status')
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
            dest_dir, filename = settings.BASE_DIR, dest_path
        if dest_dir != settings.BASE_DIR:
            context.run(f'mv {filename} {dest_path}')
    # Seed the db
    db_volume = 'modularhistory_postgres_data'
    seed_exists = os.path.exists(DB_INIT_FILE) and os.path.isfile(DB_INIT_FILE)
    if not seed_exists:
        raise Exception('Seed does not exist')
    # Remove the data volume, if it exists
    print('Wiping postgres data volume...')
    context.run('docker-compose down')
    context.run(f'docker volume rm {db_volume}', warn=True)
    # Start up the postgres container to automatically run init.sql
    print('Initializing postgres data...')
    context.run('docker-compose up -d postgres')
    print('Finished.')


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
        else file_utils.envsubst(template_file)
    ).splitlines()
    if dev:
        vars += (
            context.run(f'envsubst < {dev_overrides_file}', hide='out').stdout
            if envsubst
            else file_utils.envsubst(dev_overrides_file)
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
