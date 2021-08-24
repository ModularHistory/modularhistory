import os
import sys

from decouple import config

from core.constants.environments import Environments

VERSION = config('SHA', default='')

if os.environ.get('GITHUB_WORKFLOW'):
    ENVIRONMENT = Environments.GITHUB_TEST
else:
    ENVIRONMENT = config('ENVIRONMENT', default=Environments.DEV)

IS_PROD = ENVIRONMENT == Environments.PROD
IS_DEV = ENVIRONMENT == Environments.DEV
DOCKERIZED = config('DOCKERIZED', cast=bool, default=True)
TESTING: bool = (
    os.getenv('TESTING', None)
    or 'test' in sys.argv
    or any(['pytest' in arg for arg in sys.argv])
)
