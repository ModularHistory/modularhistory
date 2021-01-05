"""Constants usable throughout the ModularHistory application."""

from aenum import Constant


class Environments(Constant):
    """Environments."""

    PROD = 'prod'
    GITHUB_TEST = 'test'
    DEV = 'dev'


LOCAL = 'local'
PRODUCTION = 'production'
