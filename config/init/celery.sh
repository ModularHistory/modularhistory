#!/bin/sh

wait-for-it.sh redis:6379 -- 
test -w /modularhistory/.backups || {
    echo "Celery lacks permission to write in .backups; exiting."
    exit 1
}
celery -A modularhistory worker --hostname=%h --loglevel=info
