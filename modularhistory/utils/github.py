import os
from getpass import getpass
from os.path import join
from typing import Optional, Tuple

import requests
from django.conf import settings

BACKUPS_DIR = settings.BACKUPS_DIR
DB_INIT_FILE = join(BACKUPS_DIR, 'init.sql')
MEDIA_INIT_FILE = join(BACKUPS_DIR, 'media.tar.gz')

GITHUB_API_BASE_URL = 'https://api.github.com'
OWNER = 'modularhistory'
REPO = 'modularhistory'
GITHUB_ACTIONS_BASE_URL = f'{GITHUB_API_BASE_URL}/repos/{OWNER}/{REPO}/actions'
GITHUB_CREDENTIALS_FILE = '.github/.credentials'

SEEDS = {'env-file': '.env', 'init-sql': '.backups/init.sql'}


def pat_is_valid(username: str, pat: str) -> bool:
    """Return a bool reflecting whether the PAT is valid."""
    pat_validity_check = requests.get(
        'https://api.github.com/user',
        auth=(username, pat),
        headers={'Accept': 'application/vnd.github.v3+json'},
    )
    return pat_validity_check.status_code == 200


def accept_credentials(
    username: Optional[str] = None, pat: Optional[str] = None
) -> Tuple[str, str]:
    """Accept a GitHub username and password/PAT as input and store for future use."""
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
        pat = getpass('Enter your GitHub personal access token: ')
        signature = f'{username}:{pat}'
        while not pat_is_valid(username, pat):
            print('Invalid GitHub credentials.')
            username = input('Enter your GitHub username/email: ')
            pat = input('Enter your Personal Access Token: ')
            signature = f'{username}:{pat}'
        with open(GITHUB_CREDENTIALS_FILE, 'w') as file:
            file.write(signature)
    return username, pat


def initialize_session(username: str, pat: str) -> requests.Session:
    """Initialize and return a requests session to interact with the GitHub API."""
    session = requests.Session()
    session.auth = (username, pat)
    session.headers.update({'Accept': 'application/vnd.github.v3+json'})
    return session
