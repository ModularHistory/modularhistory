#!/bin/sh

python -m actions_includes ./.github/workflows-src/cleanup.yml ./.github/tmp/cleanup.yml &&
python -m actions_includes ./.github/workflows-src/delivery.yml ./.github/tmp/delivery.yml &&
python -m actions_includes ./.github/workflows-src/integration.yml ./.github/tmp/integration.yml &&
python -m actions_includes ./.github/workflows-src/seed.yml ./.github/tmp/seed.yml
