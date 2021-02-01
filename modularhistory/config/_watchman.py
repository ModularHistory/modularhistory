from watchman.decorators import check
from django.core import management
from io import StringIO
import re

HEALTH_CHECK_COMMAND = 'health_check'
HEALTHY = 'ok'


@check
def check_health_checks():
    """Check health checks listed under `health_check` in INSTALLED_APPS."""
    stati = {'debug': {HEALTHY: True}}
    output = StringIO()
    management.call_command(HEALTH_CHECK_COMMAND, stdout=output)
    result = output.getvalue()
    # Example output:
    # DiskUsage                ... working
    # MemoryUsage              ... working
    # MigrationsHealthCheck    ... working
    # RedisHealthCheck         ... working
    for line in result.splitlines():
        match = re.match(r'(\S+)\s+\.{3}\ (\S+)', line)
        if not match:
            continue
        key, status = match.group(1), match.group(2)
        stati[key] = {HEALTHY: status == 'working'}
    return stati


# @check
# def check_redis():
#     """Check that the Redis connection is working."""
#     r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
#     r.set('foo', 'bar')
#     r.ping()
#     return {'redis': {'ok': True}}
