#!/bin/bash

python manage.py collectstatic --noinput
python manage.py migrate
(gunicorn modularhistory.wsgi --user www-data --bind 0.0.0.0:8010 --workers 9) & nginx -g "daemon off;"
# (daphne modularhistory.asgi --user www-data --bind 0.0.0.0:8000) & nginx -g "daemon off;"
