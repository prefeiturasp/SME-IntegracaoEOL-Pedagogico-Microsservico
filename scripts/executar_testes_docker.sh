#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

docker compose -f docker-compose-dev.yml build pedagogico

docker compose -f docker-compose-dev.yml run --rm pedagogico \
  python -m coverage run --source=apps manage.py test --no-input

docker compose -f docker-compose-dev.yml run --rm pedagogico \
  python -m coverage report --show-missing --fail-under=80