#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT_DIR"

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Working tree has uncommitted changes. Commit or stash them before updating."
    exit 1
fi

echo "Pulling origin/main..."
git fetch origin
git checkout main
git pull --ff-only origin main

echo ""
echo "Updated to $(git rev-parse --short HEAD)."
echo ""

"$ROOT_DIR/scripts/prod_deploy.sh"
