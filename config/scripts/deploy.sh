#!/bin/bash

# Note: Environment variables are set in production environment 
# before this script is run.

[ -z "$SHA" ] && echo "SHA is not set." && exit 1

echo "" && echo "Updating PyInvoke config..."
cp config/invoke.yaml "$HOME/.invoke.yaml"

echo "" && echo "Logging in to the container registry..."
echo "$CR_PAT" | docker login ghcr.io -u iacobfred --password-stdin || {
    echo "GHCR login failed."; exit 1
}

echo "" && echo "Extant containers:" && docker-compose ps

image_names=("django" "next" "webserver")
echo "" && echo "Pulling images for version $SHA ..."
docker-compose pull --include-deps -q "${image_names[@]}" || {
    echo "Failed to pull required images."; exit 1
}
for image_name in "${image_names[@]}"; do
    docker image inspect "ghcr.io/modularhistory/${image_name}:${SHA}" >/dev/null 2>&1 || {
        echo "${image_name}:${SHA} is not present."; exit 1
    }
done

green="_1"; blue="_2"
new=$blue; docker-compose ps | grep --quiet "$blue" && new=$green

containers=("django" "celery" "celery_beat" "next")
declare -A old_container_ids
for container in "${containers[@]}"; do
    old_container_ids[$container]=$(docker ps -f name=$container -q | tail -n1)
    docker-compose up -d --no-deps --scale ${container}=2 --no-recreate "$container"
    # new_container_id=$(docker ps -f name=$service_name -q | head -n1)
    # new_container_ip=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $new_container_id)
    docker-compose ps | grep $new | grep "Exit 127" && exit 1
    healthy=false; timeout=300; interval=30; waited=0
    while [[ "$healthy" = false ]]; do
        healthy=true
        [[ "$(docker-compose ps | grep $new)" =~ (Exit|unhealthy|starting) ]] && healthy=false
        if [[ "$healthy" = false ]]; then 
            docker-compose logs --tail 20 "$container"
            echo ""; docker-compose ps | grep $new; echo ""
            echo "Waiting for $container to be healthy (${waited}s) ..."; echo ""
            sleep $interval; waited=$((waited + interval))
            if [[ $waited -gt $timeout ]]; then 
                echo "Timed out."; docker-compose logs; exit 1
            fi
        fi
    done
done

echo "" && echo "Taking old containers offline..."
for old_container_id in "${old_container_ids[@]}"; do
    docker stop "$old_container_id"
    docker rm "$old_container_id"
done

for container in "${containers[@]}"; do
    docker-compose up -d --no-deps --scale ${container}=1 --no-recreate "$container"
done

echo "" && docker-compose ps

# Reload the nginx configuration file without downtime.
# https://nginx.org/en/docs/beginners_guide.html#control 
docker-compose exec webserver nginx -s reload || {
    echo "Failed to reload nginx config file."; exit 1
}

echo "" && echo "Pruning (https://docs.docker.com/config/pruning/) ..."
docker image prune -a -f
docker system prune -f

echo "" && echo "Done."
