#!/bin/sh 

if [ "$ENVIRONMENT" = prod ]; then
    python manage.py collectstatic --no-input &&
    config/wait-for-it.sh postgres:5432 -- python manage.py migrate &&
    python manage.py cleanup_django_defender &&
    gunicorn modularhistory.asgi:application --user www-data --bind 0.0.0.0:8001 -k uvicorn.workers.UvicornWorker --workers 9 --max-requests 100 --max-requests-jitter 50
else
    python manage.py migrate && python manage.py runserver 0.0.0.0:8001
fi
