import re
from io import StringIO

import stringcase
from django.core import management
from watchman.decorators import check

# https://github.com/KristianOellegaard/django-health-check#django-command
HEALTH_CHECK_COMMAND = 'health_check'

HEALTHY = 'ok'


@check
def check_health_checks():
    """Check health checks listed under `health_check` in INSTALLED_APPS."""
    stati = {'debug': {HEALTHY: True}}
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
        stati[key] = {HEALTHY: status == 'working'}
    return stati
