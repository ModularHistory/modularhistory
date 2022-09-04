#!/bin/bash

wait-for-it.sh redis:6379 -- 
celery -A core beat -l INFO \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler \
    --pidfile /tmp/celerybeat.pid
