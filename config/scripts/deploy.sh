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
docker-compose pull --include-deps -q django next webserver || {
    echo "Failed to pull required images."; exit 1
}

reload_nginx() {
  docker exec webserver /usr/sbin/nginx -s reload
}

green="_1"; blue="_2"
new=$blue; old="$green"
docker-compose ps | grep --quiet "$blue" && {
    new=$green; old=$blue
}

containers=("django" "celery" "celery_beat" "next")
declare -A old_container_ids
for container in "${containers[@]}"; do
    old_container_ids[$container]=$(docker ps -f name=$container -q | tail -n1)
    docker-compose up -d --no-deps --scale ${container}=2 --no-recreate "$container"
    new_container_id=$(docker ps -f name=$service_name -q | head -n1)
    new_container_ip=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $new_container_id)
    docker-compose ps
    healthy=false; timeout=300; interval=20; waited=0
    while [[ "$healthy" = false ]]; do
        healthy=true
        [[ "$(docker-compose ps | grep $new)" =~ (Exit|unhealthy|starting) ]] && healthy=false
        if [[ "$healthy" = false ]]; then 
            docker-compose logs --tail 20; echo ""; docker-compose ps | grep $new; echo ""
            echo "Waiting for containers (${waited}s) ..."; echo ""
            sleep $interval; waited=$((waited + interval))
            if [[ $waited -gt $timeout ]]; then 
                echo "Timed out."; docker-compose logs; exit 1
            fi
        fi
    done
done

# echo "" && echo "Starting new containers..."
# # Bring new containers online, with nginx continuing to route only to the old containers.
# echo "> docker-compose up -d --no-deps --scale ${containers[@]/%/=2} --no-recreate ${containers[@]}"
# docker-compose up -d --no-deps --scale "${containers[@]/%/=2}" --no-recreate "${containers[@]}"

# echo "" && docker-compose ps && echo "" && docker-compose logs
# healthy=false; timeout=300; interval=20; waited=0
# while [[ "$healthy" = false ]]; do
#     healthy=true
#     [[ "$(docker-compose ps)" =~ (Exit|unhealthy|starting) ]] && healthy=false
#     [[ ! "$(docker-compose ps)" =~ webserver ]] && healthy=false && docker-compose up -d webserver
#     if [[ "$healthy" = false ]]; then 
#         docker-compose logs --tail 20; echo ""; docker-compose ps; echo ""
#         echo "Waiting for containers (${waited}s) ..."; echo ""
#         sleep $interval; waited=$((waited + interval))
#         if [[ $waited -gt $timeout ]]; then 
#             echo "Timed out."; docker-compose logs; exit 1
#         fi
#     fi
# done
# docker-compose ps
# [[ ! "$(docker-compose ps)" =~ webserver ]] && exit 1

echo "" && echo "Taking old containers offline..."
for old_container_id in "${old_container_ids[@]}"; do
    docker stop $old_container_id
    docker rm $old_container_id
done

for container in "${containers[@]}"; do
    docker-compose up -d --no-deps --scale ${container}=1 --no-recreate "$container"
done

# echo "" && echo "Reloading nginx..."
# reload_nginx

echo "" && echo "Pruning (https://docs.docker.com/config/pruning/) ..."
docker image prune -a -f
docker system prune -f

echo "" && echo "Done."
