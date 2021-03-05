from watchman import constants as watchman_constants
from modularhistory.environment import ENVIRONMENT
from modularhistory.constants.environments import Environments

MIN_MEMORY = {Environments.DEV: 50, Environments.PROD: 100}

# https://github.com/KristianOellegaard/django-health-check
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # percent
    'MEMORY_MIN': MIN_MEMORY.get(ENVIRONMENT) or 100,  # in MB
}

# https://django-watchman.readthedocs.io/en/latest/
WATCHMAN_AUTH_DECORATOR = 'django.contrib.admin.views.decorators.staff_member_required'

WATCHMAN_CHECKS = watchman_constants.DEFAULT_CHECKS + (
    'modularhistory.config._watchman.check_health_checks',
)
