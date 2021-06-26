#!/bin/bash

echo 'Initializing webserver...'

if [ ! "$ENVIRONMENT" = dev ]; then 
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
