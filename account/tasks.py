# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.decorators import task
from django.core.mail import send_mail

# @task(name='____')
# def process_registration(event_id, user_id, division_ids=None, data={}):
#     pass
