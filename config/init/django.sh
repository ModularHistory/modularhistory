#!/bin/sh

wait-for-it.sh postgres:5432 -- invoke dbbackup --redact --push
python manage.py migrate

if [ "$ENVIRONMENT" = prod ]; then
    python manage.py collectstatic --no-input &&
    python manage.py cleanup_django_defender &&
    gunicorn modularhistory.asgi:application \
      --user www-data --bind 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker \
      --workers 9 --max-requests 100 --max-requests-jitter 50 --lifespan=off
else
    python manage.py runserver 0.0.0.0:8000
fi
