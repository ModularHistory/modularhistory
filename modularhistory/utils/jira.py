import logging

from decouple import config
from jira import JIRA

JIRA_USERNAME = config('JIRA_USERNAME', default='')
JIRA_TOKEN = config('JIRA_TOKEN', default='')

# https://jira.readthedocs.io/en/latest/examples.html#initialization
try:
    jira_client = JIRA(
        'https://modularhistory.atlassian.net',
        basic_auth=(JIRA_USERNAME, JIRA_TOKEN),
    )
except Exception as err:
    logging.error(f'Unable to authenticate Jira client: {err}')
    jira_client = None
