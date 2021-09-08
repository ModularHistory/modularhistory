from watchman import constants as watchman_constants

from core.constants.environments import Environments
from core.environment import ENVIRONMENT

MIN_MEMORY = {Environments.DEV: 50, Environments.PROD: 100}

# https://github.com/KristianOellegaard/django-health-check
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # percent
    'MEMORY_MIN': MIN_MEMORY.get(ENVIRONMENT) or 100,  # in MB
}

# https://django-watchman.readthedocs.io/en/latest/
WATCHMAN_AUTH_DECORATOR = 'django.contrib.admin.views.decorators.staff_member_required'

WATCHMAN_CHECKS = watchman_constants.DEFAULT_CHECKS + (
    'core.config._watchman.check_health_checks',
    # 'core.config._watchman.check_file_permissions',  # TODO
)
