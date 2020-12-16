from decouple import config
from modularhistory.constants.misc import Environments
import os

VERSION = config('SHA', default='')

if os.environ.get('GITHUB_WORKFLOW'):
    ENVIRONMENT = Environments.GITHUB_TEST
else:
    ENVIRONMENT = config('ENVIRONMENT', default=Environments.DEV)
