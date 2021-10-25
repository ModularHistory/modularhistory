#!/bin/bash

wait-for-it.sh postgres:5432 -- wait-for-it.sh elasticsearch:9200 --

# python manage.py cleanup_django_defender  # TODO

# update dependencies in dev to avoid requiring image rebuild
[[ "$ENVIRONMENT" = dev ]] && poetry install

# Create a db backup, if there are any migrations to apply.
python manage.py migrate --check || {
    [[ "$ENVIRONMENT" = prod ]] && {
        invoke db.backup || {
            echo "Failed to create db backup."
            exit 1
        }
    }
}

# Apply migrations.
python manage.py migrate || {
    echo "Failed to run db migrations."
    exit 1
}

# Collect static files.
python manage.py collectstatic --no-input || {
    echo "Failed to collect static files."
    exit 1
}

# Rebuild indexes.
python manage.py search_index --rebuild -f || {
    echo "Failed to rebuild elasticsearch indexes."
    exit 1
}

if [ "$ENVIRONMENT" = prod ]; then
    gunicorn core.asgi:application \
      --user www-data --bind 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker \
      --workers 9 --max-requests 100 --max-requests-jitter 50
else
    # Create superuser if necessary.
    python manage.py createsuperuser --no-input --username="$DJANGO_SUPERUSER_EMAIL" --email="$DJANGO_SUPERUSER_EMAIL" &>/dev/null
    # Run the dev server.
    python manage.py runserver 0.0.0.0:8000
fi
