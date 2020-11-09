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

import requests
from google.cloud import tasks_v2 as tasks
from google.protobuf.timestamp_pb2 import Timestamp

from admin.admin_site import admin_site
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

if settings.ENABLE_CELERY:
    from django_celery_beat.admin import CrontabSchedule, IntervalSchedule, PeriodicTask
    from django_celery_beat.admin import PeriodicTaskAdmin as BasePeriodicTaskAdmin
    from django_celery_beat.admin import SolarSchedule
    from django_celery_results.admin import TaskResult, TaskResultAdmin

    IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.DAYS)
    CrontabSchedule.objects.get_or_create(
        hour='1',
        day_of_week='1',
        day_of_month='*',
        month_of_year='*',
    )
    latitude = '40.23380'
    longitude = '-111.65850'
    address = settings.SERVER_LOCATION
    api_key = settings.GOOGLE_MAPS_API_KEY
    response = requests.get(
        f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'
    ).json()
    if response['status'] == 'OK':
        latitude = response['results'][0]['geometry']['location']['lat']
        longitude = response['results'][0]['geometry']['location']['lng']
    SolarSchedule.objects.get_or_create(
        event='sunset',
        latitude=latitude,
        longitude=longitude,
    )

    class PeriodicTaskAdmin(BasePeriodicTaskAdmin):
        """Admin for periodic Celery tasks."""

        fieldsets = (
            (
                None,
                {
                    u'fields': (
                        u'name',
                        u'regtask',
                        u'task',
                        u'enabled',
                        u'description',
                    ),
                    u'classes': (u'extrapretty', u'wide'),
                },
            ),
            (
                u'Schedule',
                {
                    u'fields': (u'interval', u'crontab', u'solar'),
                    u'classes': (u'extrapretty', u'wide'),
                },
            ),
            (
                u'Arguments',
                {
                    u'fields': (u'args', u'kwargs'),
                    u'classes': (u'extrapretty', u'wide', u'collapse', u'in'),
                },
            ),
            (
                u'Execution Options',
                {
                    u'fields': (u'expires', u'queue', u'exchange', u'routing_key'),
                    u'classes': (u'extrapretty', u'wide', u'collapse', u'in'),
                },
            ),
        )

    admin_site.register(PeriodicTask, PeriodicTaskAdmin)
    admin_site.register(SolarSchedule)
    admin_site.register(IntervalSchedule)
    admin_site.register(CrontabSchedule)
    admin_site.register(TaskResult, TaskResultAdmin)
