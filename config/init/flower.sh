#!/bin/bash

wait-for-it.sh redis:6379 -- 
until timeout 15 celery -A core inspect ping; do
    >&2 echo "Celery workers not available; waiting..."
    sleep 3
done

# --url_prefix=flower
flower -A core --port=5555 --broker=redis://redis:6379/0
