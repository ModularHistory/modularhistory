#!/bin/bash

# Note: Environment variables are set in production environment 
# before this script is run.

echo "" && echo "Updating PyInvoke config..."
cp config/invoke.yaml "$HOME/.invoke.yaml"
echo "" && echo "Logging in to the container registry..."
echo "$CR_PAT" | docker login ghcr.io -u iacobfred --password-stdin || {
    echo "GHCR login failed."; exit 1
}
echo "Pulling images..."
docker-compose pull --include-deps -q django react webserver || {
    echo "Failed to pull required images."; exit 1
}
echo "" && echo "Stopping containers..."
docker-compose down --remove-orphans
echo "" && echo "Restarting containers..."
docker-compose up -d webserver
echo "" && docker-compose ps
echo "" && docker-compose logs
echo ""
healthy=false; timeout=300; interval=20; waited=0
while [[ "$healthy" = false ]]; do
    healthy=true
    [[ "$(docker-compose ps)" =~ (Exit|unhealthy|starting) ]] && healthy=false
    [[ ! "$(docker-compose ps)" =~ webserver ]] && healthy=false && docker-compose up -d webserver
    if [[ "$healthy" = false ]]; then 
        docker-compose logs --tail 20; echo ""; docker-compose ps; echo ""
        echo "Waiting for containers (${waited}s) ..."; echo ""
        sleep $interval; waited=$((waited + interval))
        if [[ $waited -gt $timeout ]]; then 
            echo "Timed out."; docker-compose logs; exit 1
        fi
    fi
done
docker-compose ps
[[ ! "$(docker-compose ps)" =~ webserver ]] && exit 1
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
