"""
Celery is incompatible with Google Cloud.

: /

TODO:
https://eshlox.net/2020/05/08/google-app-engine-cloud-tasks-and-django-rest-framework-permissions
"""

import json
import os
import time
from getpass import getuser
from sys import stderr
from typing import Any, Dict

from google.cloud import tasks_v2 as tasks
from google.protobuf.timestamp_pb2 import Timestamp

from modularhistory import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modularhistory.settings')

QUEUE_NAME = settings.GC_QUEUE


class TaskMixin:
    """TODO: add docstring."""

    def send_task(
        self,
        url: str,
        queue_name=QUEUE_NAME,
        http_method='POST',
        payload=None,
        schedule_time=None,
        name=None,
    ):
        """Send task to be executed."""
        if not settings.IS_GCP:
            # TODO: Execute the task here instead of using Cloud Tasks
            return
        parent = self._cloud_task_client.queue_path(
            settings.GC_PROJECT, settings.GC_REGION, queue_name
        )

        task: Dict[str, Any] = {
            'app_engine_http_request': {'http_method': http_method, 'relative_uri': url}
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

    @property
    def _cloud_task_client(self):
        """TODO: add docstring."""
        return tasks.CloudTasksClient()


def _debug(self) -> None:
    """TODO: write docstring."""
    print('Debugging....')
    if hasattr(self, 'request'):
        print('Request: {0!r}'.format(self.request))
    print(f'User: {getuser()}', file=stderr)


# if settings.ENABLE_CELERY:
#     from celery import Celery
#     # If not running in Google Cloud
#     # Set the default Django settings module for the 'celery' program.
#     app = Celery('modularhistory')
#
#     # Using a string here means the worker doesn't have to serialize
#     # the configuration obj to child processes.
#     # namespace='CELERY' means all celery-related configuration keys
#     # should have a `CELERY_` prefix.
#     app.config_from_object('django.conf:settings', namespace='CELERY')
#
#     # Load task modules from all registered Django app configs.
#     app.autodiscover_tasks()
#
#     @app.task(bind=True)
#     def debug(self):
#         """TODO: add docstring."""
#         _debug(self)
app = None
