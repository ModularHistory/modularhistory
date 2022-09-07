#!/bin/bash

# Note: Environment variables are set in production environment 
# before this script is run.

[ -z "$SHA" ] && echo "SHA is not set." && exit 1
[ -z "$GHCR_PASSWORD" ] && echo "GHCR_PASSWORD is not set." && exit 1

images_to_pull=("frontend" "backend")

# Specify containers to start IF NOT ALREADY RUNNING, in order of startup.
containers_to_start=("postgres" "redis" "elasticsearch" "django" "celery" "celery_beat" "next")

# Specify containers to deploy with zero downtime, in order of startup.
# NOTE: These containers will briefly have two instances running simultaneously.
# This means celery_beat cannot be included and must be deployed separately (with downtime).
containers_to_deploy_without_downtime=("django" "celery" "next")

reload_nginx () {
    # Reload the nginx configuration file without downtime.
    # https://nginx.org/en/docs/beginners_guide.html#control
    nginx -s reload || {
        echo "Failed to reload nginx config file."; exit 1
    }
}

wait_for_health () {
    healthy=false; timeout=300; interval=15; waited=0
    while [[ "$healthy" = false ]]; do
        healthy=true
        [[ "$(docker compose ps)" =~ (Exit 1|unhealthy|starting) ]] && healthy=false
        if [[ "$healthy" = false ]]; then
            if [[ $waited -gt $timeout ]]; then 
                docker compose logs; echo "Timed out."; exit 1
            fi
            [[ $((waited%2)) -eq 0 ]] && docker compose logs --tail 20 "$1"
            echo ""; docker compose ps; echo ""
            echo "Waiting for $1 to be healthy (total waited: ${waited}s) ..."
            sleep $interval; waited=$((waited + interval))
        fi
    done
}

# List extant containers.
echo "" && echo "Extant containers:" && docker compose ps

# Login to the container registry.
echo "" && echo "Logging in to the container registry..."
docker login ghcr.io -u iacobfred -p "$GHCR_PASSWORD" || {
    echo "GHCR login failed."; exit 1
}

# Pull new images.
echo "" && echo "Pulling images for version $SHA ..."
docker compose pull --quiet || {
    echo "Failed to pull required images."; exit 1
}
for image_name in "${images_to_pull[@]}"; do
    docker image inspect "ghcr.io/modularhistory/${image_name}:${SHA}" >/dev/null 2>&1 || {
        echo "${image_name}:${SHA} is not present."; exit 1
    }
done

declare -a started_containers

# If containers are not already running, start them up.
for container in "${containers_to_start[@]}"; do
    docker compose ps | grep "$container" | grep -q "Up" || {
        docker compose up -d --no-recreate "$container"
        started_containers+=("${container}")
    }
done

# Take down celery_beat to avoid triggering a periodic task during the deploy.
docker compose rm --stop --force celery_beat

# Deploy new containers.
declare -A old_container_ids
for container in "${containers_to_deploy_without_downtime[@]}"; do
    if [[ ! " ${started_containers[*]} " =~ " ${container} " ]]; then
        echo "" && echo "Deploying $container ..."
        old_container_ids[$container]=$(docker ps -f "name=${container}" -q | tail -n1)
        docker compose up -d --no-deps --scale "${container}=2" --no-recreate "$container"
        container_name=$(docker ps -f "name=${container}" --format '{{.Names}}' | tail -n1)
        # new_container_name="${container_name/modularhistory_/modularhistory_${new}_}"
        # docker rename "$container_name" "$new_container_name"
        docker compose ps | grep "Exit 1" && exit 1
        wait_for_health "$container_name"
    fi
done

# Start celery_beat.
docker compose up -d --no-deps --no-recreate "celery_beat"
wait_for_health "celery_beat"

echo "" && echo "Finished deploying new containers."
echo "" && docker compose ps

# Reload nginx to begin sending traffic to the new containers.
reload_nginx

# Stop and remove the old containers.
echo "" && echo "Taking old containers offline..."
for old_container_id in "${old_container_ids[@]}"; do
    docker stop "$old_container_id"
    docker rm "$old_container_id"
done
for container in "${containers_to_deploy_without_downtime[@]}"; do
    docker compose up -d --no-deps --scale "${container}=1" --no-recreate "$container"
done
echo "" && echo "Finished removing old containers."
echo "" && docker compose ps

# Reload nginx to stop trying to send traffic to the old containers.
reload_nginx

# Confirm all containers are running.
for container in "${containers_to_start[@]}"; do
    docker compose ps | grep "$container" | grep -q "Up" || {
        echo "WARNING: ${container} unexpectedly is not running. Starting..."
        docker compose up -d "$container"
        wait_for_health "$container"
    }
done

# Prune images.
echo "" && echo "Pruning (https://docs.docker.com/config/pruning/) ..."
docker image prune -a -f; docker system prune -f

# Update config files as necessary.
echo "" && echo "Updating PyInvoke config..."
cp .config/invoke.yaml "$HOME/.invoke.yaml"

echo "" && docker compose ps
echo "" && echo "Done."
