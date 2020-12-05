#!/bin/bash

python manage.py collectstatic --noinput
python manage.py migrate
gunicorn modularhistory.wsgi --user www-data --bind 0.0.0.0:8000 --workers 9
# daphne modularhistory.asgi --user www-data --bind 0.0.0.0:8000
