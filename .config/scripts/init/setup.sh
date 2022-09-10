#!/bin/bash

if [[ -z "$WORKSPACE" ]]; then
    echo "WORKSPACE is not set."
    exit 1
fi

mkdir -p _volumes/nginx

for filepath in .config/nginx/*.conf; do
    filename=$(basename "$filepath")
    # shellcheck disable=SC2016
    envsubst '$WORKSPACE' < "$filepath" > "_volumes/nginx/${filename}"
done

