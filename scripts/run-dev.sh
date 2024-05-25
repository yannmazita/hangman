#!/bin/bash
# It either this or changing up the context in docker-compose to the parent directory
cp poetry.lock app/poetry.lock
cp pyproject.toml app/pyproject.toml

docker compose --profile dev up "$@"
