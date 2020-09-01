"""
Celery is incompatible with Google Cloud.  : /

TODO: https://eshlox.net/2020/05/08/google-app-engine-cloud-tasks-and-django-rest-framework-permissions
"""

import json
import os
import time
from getpass import getuser
from glob import glob
from sys import stderr

from celery import Celery
from django.core import management
from google.cloud import tasks_v2 as tasks
from google.protobuf.timestamp_pb2 import Timestamp
# from paramiko import SSHClient
# from scp import SCPClient
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from typing import Any, Dict
from history import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'history.settings')

QUEUE_NAME = settings.GC_QUEUE


class TaskMixin:
    @property
    def _cloud_task_client(self):
        return tasks.CloudTasksClient()

    def send_task(self, url, queue_name=QUEUE_NAME, http_method='POST', payload=None, schedule_time=None, name=None):
        """Send task to be executed."""
        if not settings.IS_GCP:
            # TODO: Execute the task here instead of using Cloud Tasks
            return
        parent = self._cloud_task_client.queue_path(settings.GC_PROJECT, settings.GC_REGION, queue_name)

        task: Dict[str, Any] = {
            'app_engine_http_request': {
                'http_method': http_method,
                'relative_uri': url
            }
        }

        if name:
            task['name'] = name

        if isinstance(payload, dict):
            payload = json.dumps(payload)

        # Construct the request body.
        if payload is not None:
            # The API expects a payload of type bytes.
            converted_payload = payload.encode()
            # Add the payload to the request.
            task['app_engine_http_request']['body'] = converted_payload

        if schedule_time is not None:
            now = time.time() + schedule_time
            seconds = int(now)
            nanos = int((now - seconds) * 10 ** 9)

            # Create Timestamp protobuf.
            timestamp = Timestamp(seconds=seconds, nanos=nanos)

            # Add the timestamp to the task.
            task['schedule_time'] = timestamp

        response = self._cloud_task_client.create_task(parent, task)
        print(f'Created task: {response.name}')


def _debug(self) -> None:
    print('Debugging....')
    if hasattr(self, 'request'):
        print('Request: {0!r}'.format(self.request))
    print(f'User: {getuser()}', file=stderr)


if not settings.IS_GCP:
    # Set the default Django settings module for the 'celery' program.
    app = Celery('history')

    # Using a string here means the worker doesn't have to serialize
    # the configuration object to child processes.
    # namespace='CELERY' means all celery-related configuration keys
    # should have a `CELERY_` prefix.
    app.config_from_object('django.conf:settings', namespace='CELERY')

    # Load task modules from all registered Django app configs.
    app.autodiscover_tasks()


    @app.task(bind=True)
    def debug(self):
        _debug(self)


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
