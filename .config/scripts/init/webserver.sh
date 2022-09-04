#!/bin/bash

echo 'Initializing webserver...'

REDIRECTS_MAP_DIR=/modularhistory/_volumes/redirects
REDIRECTS_MAP_PATH="${REDIRECTS_MAP_DIR}/redirects.map"

if [[ ! -f "$REDIRECTS_MAP_PATH" ]]; then
    touch "$REDIRECTS_MAP_PATH" || {
        echo "Failed to create $REDIRECTS_MAP_PATH"; exit 1
    }
fi

if [[ "$ENVIRONMENT" = prod ]]; then
    if [[ ! -f /etc/letsencrypt/live/modularhistory.orega.org/fullchain.pem ]]; then
        echo 'Getting SSL certificate...' && 
        certbot certonly --standalone --agree-tos -m "jacob@modularhistory.orega.org" -n -d "${DOMAINS}";
    fi
    echo 'Starting ddclient...' && 
    envsubst < /etc/ddclient/ddclient.conf > /etc/ddclient/ddclient.conf.tmp && 
    mv /etc/ddclient.conf.tmp /etc/ddclient/ddclient.conf && 
    ddclient -daemon -pid /var/run/ddclient.pid;
    echo 'Starting cron daemon...' && 
    cron; 
fi;

autoreload_redirects() {
    while true; do
        inotifywait --exclude .swp -e create -e modify -e delete -e move $REDIRECTS_MAP_DIR
        nginx -t && {
            echo "Detected Nginx configuration change. Reloading ..."
            nginx -s reload
        }
    done
}

autoreload_redirects & nginx -g 'daemon off;'
