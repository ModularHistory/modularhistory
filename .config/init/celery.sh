#!/bin/bash

wait-for-it.sh redis:6379 -- 
writable_dirs=( ".backups" "media" "static" "frontend/.next" )
for writable_dir in "${writable_dirs[@]}"; do
    test -w "/modularhistory/$writable_dir" || {
        echo "Celery lacks permission to write in $writable_dir; exiting."
        exit 1
    }
done
celery -A modularhistory worker --hostname=%h --loglevel=info
