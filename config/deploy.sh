#!/bin/bash

# Note: Environment variables are set in production environment 
# before this script is run.

echo "" && echo "Logging in to the container registry..."
echo "$CR_PAT" | docker login ghcr.io -u iacobfred --password-stdin
echo "Pulling images to $SERVER..."
docker-compose pull --include-deps django flower react
echo "" && echo "Restarting server..."
docker-compose down --remove-orphans
docker-compose up -d django flower react
echo "Removing all images not used by existing containers... (https://docs.docker.com/config/pruning/#prune-images)"
docker image prune -a -f
docker system prune -f
# Only reload Nginx if necessary.
[ -f nginx.conf.sha ] || touch nginx.conf.sha
if ! grep "$(shasum nginx.conf)" < nginx.conf.sha > /dev/null; then 
    echo "" && echo "Updating Nginx config..." && 
    lxc file push nginx.conf webserver/etc/nginx/sites-available/default && 
    echo "" && echo "Restarting Nginx server..." && 
    lxc exec webserver -- service nginx reload
fi
shasum nginx.conf > nginx.conf.sha
echo "" && echo "Done."
