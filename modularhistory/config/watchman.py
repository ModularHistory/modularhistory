from watchman import constants as watchman_constants

# https://django-watchman.readthedocs.io/en/latest/
WATCHMAN_AUTH_DECORATOR = 'django.contrib.admin.views.decorators.staff_member_required'

WATCHMAN_CHECKS = watchman_constants.DEFAULT_CHECKS + (
    'modularhistory.config._watchman.check_health_checks',
)
