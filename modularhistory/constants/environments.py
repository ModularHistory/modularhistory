"""Constants usable throughout the ModularHistory application."""

from aenum import Constant


class Environments(Constant):
    """Environments."""

    PROD = 'prod'
    GITHUB_TEST = 'test'
    DEV = 'dev'
    DEV_DOCKER = 'dev_docker'


LOCAL = 'local'
PRODUCTION = 'production'
