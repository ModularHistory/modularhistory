"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

import io
import json
import logging
import os
import re
from contextlib import redirect_stdout
from datetime import datetime
from glob import iglob
from os.path import join
from pprint import pformat
from time import sleep
from typing import TYPE_CHECKING, Optional
from zipfile import BadZipFile, ZipFile

from colorama import Style
from commands.command import command
from core.constants.strings import NEGATIVE
from core.utils import db as db_utils
from core.utils import files as file_utils
from core.utils import github as github_utils
from django.conf import settings
from dotenv import dotenv_values, load_dotenv
from requests import Session

if TYPE_CHECKING:
    from invoke.context import Context

NEWLINE = '\n'
GITHUB_ACTIONS_BASE_URL = github_utils.GITHUB_ACTIONS_BASE_URL
SEEDS = {'dotenv-file': '.env', 'init-sql': os.path.join(settings.DB_INIT_DIR, 'init.sql')}
HOSTS_FILEPATH = '/etc/hosts'
WSL_HOSTS_FILEPATH = '/mnt/c/Windows/System32/drivers/etc/hosts'


def dispatch_and_get_workflow(context: 'Context', session: Session, email: str) -> dict:
    """Dispatch the seed workflow in GitHub, and return the workflow run id."""
    # https://docs.github.com/en/rest/reference/actions#list-workflow-runs-for-a-repository
    workflow_id = 'seed.yml'
    time_posted = datetime.utcnow().replace(microsecond=0)
    session.post(
        f'{GITHUB_ACTIONS_BASE_URL}/workflows/{workflow_id}/dispatches',
        data=json.dumps({'ref': 'main', 'inputs': {'email': email}}),
    )
    sleep(5)
    workflow_runs: list[dict] = []
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
                    raise TimeoutError('Timed out while attempting to retrieve workflow run.')
    return workflow_runs[0]


def seed_dotenv_file(context: 'Context', username: str, pat: str):
    """Acquire a .env file."""
    username, pat = github_utils.accept_credentials(username, pat)
    session = github_utils.initialize_session(username=username, pat=pat)
    print('Dispatching workflow...')
    workflow_run = dispatch_and_get_workflow(
        context=context,
        session=session,
        email=username,
    )
    workflow_run_id = workflow_run['id']
    workflow_run_url = f'{GITHUB_ACTIONS_BASE_URL}/runs/{workflow_run_id}'
    status = workflow_run['status']
    artifacts_url = workflow_run['artifacts_url']
    # Wait for up to 10 minutes, pinging every 9 seconds.
    timeout, ping_interval, waited_seconds = 600, 10, 0
    artifacts = []
    while status and waited_seconds < timeout:
        print(
            f'Waiting for artifacts... status: {status} ' f'(total wait: {waited_seconds}s)'
        )
        sleep(ping_interval)
        waited_seconds += ping_interval
        status = session.get(workflow_run_url).json().get('status')
        if status in ('success', 'completed'):
            artifacts = session.get(artifacts_url).json().get('artifacts')
            if artifacts:
                break
    else:
        raise TimeoutError(
            'Failed to complete workflow: '
            f'https://github.com/ModularHistory/modularhistory/runs/{workflow_run_id}'
        )
    seed_name, dest_filepath = 'dotenv-file', '.env'
    for artifact in artifacts:
        artifact_name = artifact['name']
        if artifact_name != seed_name:
            logging.error(f'Unexpected artifact: "{artifact_name}"')
            continue
        dl_url = artifact['archive_download_url']
    zip_filename = f'{seed_name}.zip'
    context.run(
        f'curl -u {username}:{pat} -L {dl_url} --output {zip_filename} '
        f'&& sleep 3 && echo "Downloaded {zip_filename}"'
    )
    extract_zip(context, zip_filename, dest_filepath=dest_filepath)


def extract_zip(context: 'Context', filename: str, dest_filepath: Optional[str] = None):
    """Extract the specified zip file to the specified destination."""
    try:
        with ZipFile(filename, 'r') as archive:
            soft_deleted_path = f'{dest_filepath}.prior'
            if os.path.exists(dest_filepath):
                if input(f'Overwrite existing {dest_filepath}? [Y/n] ') != NEGATIVE:
                    context.run(f'mv {dest_filepath} {soft_deleted_path}')
            archive.extractall()
            if os.path.exists(dest_filepath) and os.path.exists(soft_deleted_path):
                print(f'Removing prior {dest_filepath} ...')
                os.remove(soft_deleted_path)
        context.run(f'rm {filename}')
    except BadZipFile as err:
        print(f'Could not extract from {filename} due to {err}')
    if '/' in dest_filepath:
        dest_dir, filename = os.path.dirname(dest_filepath), os.path.basename(dest_filepath)
    else:
        dest_dir, filename = settings.BASE_DIR, dest_filepath
    if dest_dir != settings.BASE_DIR:
        context.run(f'mv {filename} {dest_filepath}')


@command
def seed(
    context: 'Context',
    username: Optional[str] = None,
    pat: Optional[str] = None,
    db: bool = True,
    dotenv_file: bool = True,
):
    """Seed a dev database, media directory, and env file."""
    dotenv_file = dotenv_file and input('Seed .env file? [Y/n] ') != NEGATIVE
    db = db and (not dotenv_file or input('Seed database? [Y/n] ') != NEGATIVE)
    if not dotenv_file and not db:
        print('Seeded nothing.')
        return
    if dotenv_file:
        seed_dotenv_file(context, username, pat)
    if db:
        # Pull the db init file from remote storage and seed the db.
        db_utils.seed(context, remote=True, migrate=True)
    print('Finished seeding.')


@command
def update_hosts(context: 'Context'):
    """Ensure /etc/hosts contains extra hosts defined in config/hosts."""
    with open(os.path.join(settings.CONFIG_DIR, 'hosts.txt')) as hosts_file:
        required_hosts = [host for host in hosts_file.read().splitlines() if host]
    if os.path.exists(WSL_HOSTS_FILEPATH):
        while True:
            with open(WSL_HOSTS_FILEPATH, 'r') as hosts_file:
                extant_hosts = hosts_file.read()
                hosts_to_write = [host for host in required_hosts if host not in extant_hosts]
            if hosts_to_write:
                input(
                    f'{Style.BRIGHT}\n'
                    'Please update your Windows hosts file to include the following:\n'
                    f'{NEWLINE.join(hosts_to_write)}\n\n'
                    'To do so, follow the instructions at '
                    'https://www.howtogeek.com/howto/27350/beginner-geek-how-to-edit-your-hosts-file/ \n'  # noqa: E501
                    'After updating your hosts file, press Enter to continue.'
                    f'{Style.RESET_ALL}'
                )
            else:
                break
    with open(HOSTS_FILEPATH, 'r') as hosts_file:
        extant_hosts = hosts_file.read()
    hosts_to_write = [host for host in required_hosts if host not in extant_hosts]
    if hosts_to_write:
        print(f'Updating {HOSTS_FILEPATH} ...')
        for host in hosts_to_write:
            context.run(f'sudo echo "{host}" | sudo tee -a /etc/hosts')
    print('Hosts file is up to date.')


@command
def update_git_hooks(context: 'Context'):
    """Update git hooks."""
    for filepath in iglob(os.path.join(settings.ROOT_DIR, '.config/hooks/*')):
        filename = os.path.basename(filepath)
        # fmt: off
        context.run(f'''
            cmp --silent ".git/hooks/{filename}" "{filepath}" || {{
                cat "{filepath}" > ".git/hooks/{filename}"
                sudo chmod +x ".git/hooks/{filename}"
                echo "Updated {filename} hook."
            }}
        ''')
        # fmt: on
