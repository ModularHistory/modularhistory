#!/bin/bash

# Note: Environment variables are set in production environment 
# before this script is run.

shopt -s expand_aliases
alias compose='docker-compose -f docker-compose.yml -f docker-compose.prod.yml'

echo "" && echo "Updating PyInvoke config..."
cp config/invoke.yaml "$HOME/.invoke.yaml"
echo "" && echo "Logging in to the container registry..."
echo "$CR_PAT" | docker login ghcr.io -u iacobfred --password-stdin || {
    echo "GHCR login failed."; exit 1
}
echo "Pulling images..."
compose pull --include-deps django react webserver || {
    echo "Failed to pull required images."; exit 1
}
echo "" && echo "Restarting server..."
compose down --remove-orphans
containers=( "django" "celery_beat" "react" "webserver" )
for container in "${containers[@]}"; do
    compose up -d "$container"
done
sleep 10
healthy=false
while [[ "$healthy" = false ]]; do
    healthy=true
    [[ "$(compose ps)" =~ (Exit|unhealthy|starting) ]] && healthy=false
    if [[ "$healthy" = false ]]; then echo "Waiting for containers to be healthy..."; sleep 20; fi
done
echo "Removing all images not used by existing containers... (https://docs.docker.com/config/pruning/#prune-images)"
docker image prune -a -f
docker system prune -f
# Only reload Nginx if necessary.
# [ -f nginx.conf.sha ] || touch nginx.conf.sha
# last_conf_sha="$(cat nginx.conf.sha)"
# current_conf_sha="$(shasum config/nginx/prod/nginx.conf)"
# if [[ ! "$current_conf_sha" = "$last_conf_sha" ]]; then
#     echo "
#     Current nginx.conf hash ($current_conf_sha) does not match 
#     the last hash ($last_conf_sha); i.e., the config has changed.
#     "
#     echo "" && echo "Updating Nginx config..." && 
#     lxc file push nginx.conf webserver/etc/nginx/sites-available/default && 
#     echo "" && echo "Restarting Nginx server..." && 
#     lxc exec webserver -- service nginx reload
# fi
# shasum config/nginx/prod/nginx.conf > nginx.conf.sha
echo "" && echo "Done."
