from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from django.core import management

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'history.settings')

app = Celery('history')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))
#
#     RUN_AT_TIMES = ['6:00', '18:00']
#     schedule = Schedule(run_at_times=RUN_AT_TIMES)
#     code = 'my_app.Backup'
#
#     def do(self):
#         management.call_command('dbbackup')
