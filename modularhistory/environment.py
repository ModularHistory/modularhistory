import os

from decouple import config

from modularhistory.constants.environments import Environments

VERSION = config('SHA', default='')

if os.environ.get('GITHUB_WORKFLOW'):
    environment = Environments.GITHUB_TEST
else:
    environment = config('ENVIRONMENT', default=Environments.DEV)
