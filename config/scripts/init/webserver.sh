#!/bin/bash

echo 'Initializing webserver...'

REDIRECTS_MAP_PATH=/modularhistory/_volumes/redirects/redirects.map

if [[ ! -f "$REDIRECTS_MAP_PATH" ]]; then
    touch "$REDIRECTS_MAP_PATH"
fi

if [ "$ENVIRONMENT" = prod ]; then 
    echo 'Starting ddclient...' && 
    envsubst < /etc/ddclient/ddclient.conf > /etc/ddclient/ddclient.conf.tmp && 
    mv /etc/ddclient.conf.tmp /etc/ddclient/ddclient.conf && 
    ddclient -daemon -pid /var/run/ddclient.pid;
    echo 'Renewing SSL certificates...' && 
    certbot certonly --standalone --agree-tos -m "jacob@modularhistory.com" -n -d "${DOMAINS}";
    echo 'Starting cron daemon...' && 
    cron; 
fi;

nginx -g 'daemon off;'
