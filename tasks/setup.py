"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

import json
import logging
import os
import re
from datetime import datetime
from os.path import join
from pprint import pformat
from typing import List, Optional
from zipfile import BadZipFile, ZipFile

from django.conf import settings
from dotenv import load_dotenv

from modularhistory.constants.strings import NEGATIVE
from modularhistory.utils import db as db_utils
from modularhistory.utils import files as file_utils
from modularhistory.utils import github as github_utils

from .command import command

GITHUB_ACTIONS_BASE_URL = github_utils.GITHUB_ACTIONS_BASE_URL
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
    username, pat = github_utils.accept_credentials(username, pat)
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
        context.run(f'sleep {wait_interval}')
        time_waited += wait_interval
        workflow_runs = session.get(
            f'{GITHUB_ACTIONS_BASE_URL}/runs?event=workflow_dispatch&per_page=10&page=1'
        ).json()['workflow_runs']
        workflow_runs = [
            workflow_run
            for workflow_run in workflow_runs
            if workflow_run['name'] == 'seed'
            and datetime.fromisoformat(workflow_run['created_at'].replace('Z', ''))
            >= time_posted
        ]
        if time_waited > timeout and not workflow_runs:
            print(
                'Timed out while attempting to retrieve workflow run. '
                f'Latest workflows retrieved: {pformat(workflow_runs)} \n\n'
                'Try selecting the workflow manually by following these steps: \n'
                '1. Go to https://github.com/ModularHistory/modularhistory/actions \n'
                '2. Click into your "seed" workflow (at/near the top of the list of '
                'workflow runs), if it is present. Otherwise, exit these steps. \n'
                '3. Copy your workflow run ID (something like 613236414) from the URL '
                '(which should resemble https://github.com/ModularHistory/modularhistory/actions/runs/613236414) \n'  # noqa: E501
            )
            while True:
                answer = input('Were you able to find your workflow run ID? [y/n] ')
                if answer in ('y, Y'):
                    workflow_run_id = input('Enter the workflow run ID: ')
                    response = session.get(
                        f'{GITHUB_ACTIONS_BASE_URL}/runs/{workflow_run_id}'
                    )
                    if response.status_code != 200:
                        # TODO: Offer more instructions
                        print('Unable to retrieve a workflow run with that ID.')
                        continue
                    workflow_run = response.json()
                    workflow_runs = [workflow_run]
                    break
                elif answer in ('n', 'N'):
                    # TODO: Offer more instructions
                    raise TimeoutError(
                        'Timed out while attempting to retrieve workflow run.'
                    )
    workflow_run = workflow_runs[0]
    workflow_run_url = f'{GITHUB_ACTIONS_BASE_URL}/runs/{workflow_run["id"]}'
    status = initial_status = workflow_run['status']
    artifacts_url = workflow_run['artifacts_url']
    while status == initial_status != 'completed':
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
            f'curl -u {username}:{pat} -L {dl_urls[seed_name]} --output {zip_file} '
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
    db_utils.seed(context)
    print('Finished.')


@command
def write_env_file(context, dev: bool = False, dry: bool = False):
    """Write a .env file."""
    destination_file = '.env'
    dry_destination_file = '.env.tmp'
    config_dir = settings.CONFIG_DIR
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
