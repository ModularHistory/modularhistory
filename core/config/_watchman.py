import logging
import os
import re
from io import StringIO

import stringcase
from django.conf import settings
from django.core import management
from watchman.decorators import check

# https://github.com/KristianOellegaard/django-health-check#django-command
HEALTH_CHECK_COMMAND = 'health_check'

HEALTHY = 'ok'


@check
def check_file_permissions():
    """Check file permissions."""
    volume_dirs = ('db/backups', 'db/init', 'static', 'media', 'redirects')
    statuses = {}
    for dir_name in volume_dirs:
        dir_path = os.path.join(settings.VOLUMES_DIR, dir_name)
        try:
            statuses[dir_path] = {HEALTHY: os.access(dir_path, os.W_OK)}
        except Exception as err:
            logging.error(err)
            statuses[dir_path] = {HEALTHY: False}
    return statuses


@check
def check_health_checks():
    """Check health checks listed under `health_check` in INSTALLED_APPS."""
    statuses = {'debug': {HEALTHY: True}}
    output = StringIO()
    # https://github.com/KristianOellegaard/django-health-check#django-command
    management.call_command(HEALTH_CHECK_COMMAND, stdout=output)
    result = output.getvalue()
    # Example output:
    # DiskUsage                ... working
    # MemoryUsage              ... working
    # MigrationsHealthCheck    ... working
    # RedisHealthCheck         ... working
    for line in result.splitlines():
        match = re.match(r'(\S+)\s+\.{3}\ (.+)', line)
        if not match:
            continue
        key, status = match.group(1), match.group(2)
        key = stringcase.snakecase(key.replace('HealthCheck', ''))
        statuses[key] = {HEALTHY: status == 'working'}
    return statuses
