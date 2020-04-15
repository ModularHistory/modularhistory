from __future__ import absolute_import, unicode_literals

import os
from glob import glob

from celery import Celery
from django.core import management
from paramiko import SSHClient
from scp import SCPClient

from history import settings

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
def debug(self):
    print('Request: {0!r}'.format(self.request))


@app.task(bind=True)
def back_up_db(self):
    """Create a database backup file."""
    print(f'Received request to back up database: {self.request}')

    # Create backup file
    management.call_command('dbbackup')

    # Select latest backup file
    os.chdir(os.path.join(f'{settings.BASE_DIR}', 'history/backups/'))
    files = glob("*sql")  # .psql or .sql files
    if not files:
        return None
    backup_file = max(files, key=os.path.getmtime)

    # Connect to Jacob's MacBook
    ssh = SSHClient()
    ssh.load_system_host_keys()
    # ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect('smb://192.168.12.8')
    # ssh.connect(server, username='username', password='password')

    with SCPClient(ssh.get_transport()) as scp:
        scp.put(backup_file, f'~/history/history/backups/{backup_file}')
        # scp.get('test2.txt')
