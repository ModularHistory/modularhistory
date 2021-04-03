#!/bin/sh

python -m actions_includes ./.github/workflows-src/cleanup.yml ./.github/workflows/cleanup.yml &&
python -m actions_includes ./.github/workflows-src/delivery.yml ./.github/workflows/delivery.yml &&
python -m actions_includes ./.github/workflows-src/integration.yml ./.github/workflows/integration.yml &&
python -m actions_includes ./.github/workflows-src/seed.yml ./.github/workflows/seed.yml
