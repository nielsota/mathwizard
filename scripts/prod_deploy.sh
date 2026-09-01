#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_FILE="docker-compose.prod.yml"

cd "$ROOT_DIR"

if [ ! -f env.prod ]; then
    echo "Missing env.prod. Create it with TUNNEL_TOKEN and production overrides."
    echo "See docs/docker.md."
    exit 1
fi

echo "Building and starting the production stack..."
docker compose -f "$COMPOSE_FILE" up -d --build --remove-orphans --pull always --wait

echo ""
echo "Production stack is up."
docker compose -f "$COMPOSE_FILE" ps
