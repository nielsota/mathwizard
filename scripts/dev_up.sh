#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo ""
    echo "Stopping local development servers..."

    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID"
    fi

    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID"
    fi

    wait 2>/dev/null || true
}

trap cleanup EXIT INT TERM

cd "$ROOT_DIR"

echo "Starting local development environment with hot reload..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Warning: .env not found. Create it from .env.example"
    echo ""
fi

echo "Starting backend at http://localhost:8001..."
uv run uvicorn mathwizard.app.main:app --reload --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!
echo ""

echo "Starting frontend at http://localhost:3001..."
(
    cd frontend
    npm run dev -- --host 0.0.0.0 --port 3001
) &
FRONTEND_PID=$!
echo ""

echo "Local development servers are running."
echo "Backend:  http://localhost:8001"
echo "Frontend: http://localhost:3001"
echo "Press Ctrl+C to stop both servers."
echo ""

wait "$BACKEND_PID" "$FRONTEND_PID"

