#!/bin/sh

wait-for-it.sh redis:6379 -- 
until timeout 15 celery -A modularhistory inspect ping; do
    >&2 echo "Celery workers not available; waiting..."
done

# --url_prefix=flower
flower -A modularhistory --port=5555 --broker=redis://redis:6379/0
