#!/bin/bash

echo 'Initializing webserver...'

REDIRECTS_MAP_PATH=/modularhistory/_volumes/redirects/redirects.map

if [[ ! -f "$REDIRECTS_MAP_PATH" ]]; then
    touch "$REDIRECTS_MAP_PATH" || {
        echo "Failed to create $REDIRECTS_MAP_PATH"; exit 1
    }
fi

if [[ "$ENVIRONMENT" = prod ]]; then
    if [[ ! -f /etc/letsencrypt/live/modularhistory.com/fullchain.pem ]]; then
        echo 'Getting SSL certificate...' && 
        certbot certonly --standalone --agree-tos -m "jacob@modularhistory.com" -n -d "${DOMAINS}";
    fi
    echo 'Starting ddclient...' && 
    envsubst < /etc/ddclient/ddclient.conf > /etc/ddclient/ddclient.conf.tmp && 
    mv /etc/ddclient.conf.tmp /etc/ddclient/ddclient.conf && 
    ddclient -daemon -pid /var/run/ddclient.pid;
    echo 'Starting cron daemon...' && 
    cron; 
fi;

nginx -g 'daemon off;'
