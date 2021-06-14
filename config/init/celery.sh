#!/bin/bash

wait-for-it.sh redis:6379 --
writable_dirs=( ".backups" ".init" "_static" "_media" )
for writable_dir in "${writable_dirs[@]}"; do
    test -w "/modularhistory/$writable_dir" || {
        echo "Celery lacks permission to write in ${writable_dir}."
        [[ "$ENVIRONMENT" = dev ]] && exit 1
    }
done
celery -A -E core worker --hostname=%h --loglevel=info
