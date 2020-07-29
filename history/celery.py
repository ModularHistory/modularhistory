from __future__ import absolute_import, unicode_literals

import os
from getpass import getuser
from glob import glob
from sys import stderr

from celery import Celery
# noinspection PyPackageRequirements
# from decouple import config
from django.core import management
# from paramiko import SSHClient
# from scp import SCPClient
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

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
    print('Debugging....')
    print('Request: {0!r}'.format(self.request))
    print(f'User: {getuser()}', file=stderr)


@app.task(bind=True)
def back_up_db(self):
    """Create a database backup file."""
    print(f'Received request to back up database: {self.request}')
    if not settings.DEBUG:
        print(f'Backing up database....')
        # Create backup file
        management.call_command('dbbackup --clean')
        # Select latest backup file
        os.chdir(os.path.join(f'{settings.BASE_DIR}', 'history/backups/'))
        files = glob('*sql')  # .psql or .sql files
        if not files:
            print(f'Could not find a db backup file.')
            return None
        backup_file = max(files, key=os.path.getmtime)

        # # Connect to remote backup server
        # server = config('REMOTE_BACKUP_SERVER', default=None)
        # username = config('REMOTE_BACKUP_SERVER_USERNAME', default=None)
        # password = config('REMOTE_BACKUP_SERVER_PASSWORD', default=None)
        # ssh_client = SSHClient()
        # ssh_client.load_system_host_keys()
        # # ssh_client.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        # if server:
        #     print(f'Connecting to remote backup location: {server}')
        #     ssh_client.connect(server, username=username, password=password)
        #     # ssh_client.connect(server, username='username', password='password')
        #     with SCPClient(ssh_client.get_transport()) as scp_client:
        #         scp_client.put(backup_file, f'~/history/history/backups/{backup_file}')
        #         # scp_client.get('test2.txt')
        #     print(f'Completed remote db backup.')

        # TODO: set up Google Drive API after getting 501(c)3 status
        google_drive_api_is_enabled = False
        if google_drive_api_is_enabled:
            g_auth = GoogleAuth()
            g_auth.LocalWebserverAuth()  # Create local webserver and handle authentication
            drive = GoogleDrive(g_auth)
            file_to_upload = drive.CreateFile({'title': backup_file})
            file_to_upload.SetContentFile(backup_file)
            file_to_upload.Upload()
