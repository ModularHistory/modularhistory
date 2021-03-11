#!/bin/bash

sleep 3 && wait-for-it.sh postgres:5432 -- 
writable_dirs=( ".backups" "media" "static" "frontend/.next" )
for writable_dir in "${writable_dirs[@]}"; do
    # Must be run by a www-data user:
    test -w "/modularhistory/$writable_dir" || {
        echo "Django lacks permission to write in $writable_dir; exiting."
        exit 1
    }
done

# python manage.py cleanup_django_defender  # TODO

invoke db.backup || {
    echo "Failed to create db backup."
    exit 1
}

python manage.py migrate || {
    echo "Failed to run db migrations."
    exit 1
}

python manage.py makemigrations --no-input --dry-run || {
    echo "Uh oh. Unable to make migrations..."
    exit 1
}

python manage.py collectstatic --no-input || {
    echo "Failed to collect static files."
    exit 1
}

if [ "$ENVIRONMENT" = prod ]; then
    gunicorn modularhistory.asgi:application \
      --user www-data --bind 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker \
      --workers 9 --max-requests 100 --max-requests-jitter 50
else
    # Run dev server.
    python manage.py runserver 0.0.0.0:8000
fi
