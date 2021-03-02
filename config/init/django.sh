#!/bin/sh

wait-for-it.sh postgres:5432 -- 
# These commands must be run by a www-data user:
test -w /modularhistory/.backups || {
    echo "Django lacks permission to write in .backups; exiting."
    exit 1
}
invoke db.backup || {
    echo "Failed to create db backup."
    exit 1
}
python manage.py migrate || {
    echo "Failed to run db migrations."
    exit 1
}
python manage.py collectstatic --no-input || {
    echo "Failed to collect static files."
    exit 1
}
# python manage.py cleanup_django_defender  # TODO

if [ "$ENVIRONMENT" = prod ]; then
    gunicorn modularhistory.asgi:application \
      --user www-data --bind 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker \
      --workers 9 --max-requests 100 --max-requests-jitter 50
else
    # Run dev server.
    python manage.py runserver 0.0.0.0:8000
fi
