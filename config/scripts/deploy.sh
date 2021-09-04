#!/bin/bash

# Note: Environment variables are set in production environment 
# before this script is run.

[ -z "$SHA" ] && echo "SHA is not set." && exit 1

# NOTE: The webserver image is pulled but not automatically deployed.
# TODO: Pull and deploy the webserver image only if necessary?
images_to_pull=("django" "next" "webserver")

# Specify containers to deploy, in order of startup.
containers_to_deploy=("django" "celery" "celery_beat" "next")

# List extant containers.
echo "" && echo "Extant containers:" && docker-compose ps

# Login to the container registry.
echo "" && echo "Logging in to the container registry..."
echo "$CR_PAT" | docker login ghcr.io -u iacobfred --password-stdin || {
    echo "GHCR login failed."; exit 1
}

# Pull new images.
echo "" && echo "Pulling images for version $SHA ..."
docker-compose pull --include-deps -q "${images_to_pull[@]}" || {
    echo "Failed to pull required images."; exit 1
}
for image_name in "${images_to_pull[@]}"; do
    docker image inspect "ghcr.io/modularhistory/${image_name}:${SHA}" >/dev/null 2>&1 || {
        echo "${image_name}:${SHA} is not present."; exit 1
    }
done

# Deploy new containers.
green="_1"; blue="_2" && new=$blue
docker-compose ps | grep --quiet "$blue" && new=$green
declare -A old_container_ids
for container in "${containers_to_deploy[@]}"; do
    old_container_ids[$container]=$(docker ps -f name=$container -q | tail -n1)
    docker-compose up -d --no-deps --scale ${container}=2 --no-recreate "$container"
    docker-compose ps | grep $new | grep "Exit 127" && exit 1
    healthy=false; timeout=300; interval=20; waited=0
    while [[ "$healthy" = false ]]; do
        healthy=true
        [[ "$(docker-compose ps | grep $new)" =~ (Exit|unhealthy|starting) ]] && healthy=false
        if [[ "$healthy" = false ]]; then 
            docker-compose logs --tail 20 "$container"
            echo ""; docker-compose ps | grep $new; echo ""
            echo "Waiting for $container to be healthy (total: ${waited}s) ..."; echo ""
            sleep $interval; waited=$((waited + interval))
            if [[ $waited -gt $timeout ]]; then 
                docker-compose logs; echo "Timed out."; exit 1
            fi
        fi
    done
done

# Stop the old containers.
echo "" && echo "Taking old containers offline..."
for old_container_id in "${old_container_ids[@]}"; do
    docker stop "$old_container_id"
    docker rm "$old_container_id"
done
echo "" && docker-compose ps

# Remove the old containers.
for container in "${containers_to_deploy[@]}"; do
    docker-compose up -d --no-deps --scale ${container}=1 --no-recreate "$container"
done
echo "" && docker-compose ps

# Reload the nginx configuration file without downtime.
# https://nginx.org/en/docs/beginners_guide.html#control
docker-compose exec -T webserver nginx -s reload || {
    echo "Failed to reload nginx config file."; exit 1
}

# Prune images.
echo "" && echo "Pruning (https://docs.docker.com/config/pruning/) ..."
docker image prune -a -f; docker system prune -f

# Update config files as necessary.
echo "" && echo "Updating PyInvoke config..."
cp config/invoke.yaml "$HOME/.invoke.yaml"

echo "" && echo "Done."
