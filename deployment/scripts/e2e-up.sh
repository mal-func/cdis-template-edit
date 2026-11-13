#!/usr/bin/env bash
# Brings up the canonical monorepo Compose stack and prepares its database.
# Set CDIS_BACKEND=fastapi to exercise the alternative backend through the
# same frontend and browser suite; Express remains the default.
#
# Usage: ./scripts/e2e-up.sh or CDIS_BACKEND=fastapi ./scripts/e2e-up.sh
# Requires compose/.env to exist first (copy env/production.env.example).

set -euo pipefail
cd "$(dirname "$0")/../compose"

COMPOSE_FILES=(-f compose.yaml)
case "${CDIS_BACKEND:-express}" in
  express) ;;
  fastapi) COMPOSE_FILES+=(-f compose.fastapi.yaml) ;;
  *)
    echo "CDIS_BACKEND must be 'express' or 'fastapi'." >&2
    exit 2
    ;;
esac

echo "==> Building and starting the ${CDIS_BACKEND:-express} stack..."
docker compose "${COMPOSE_FILES[@]}" up -d --build

echo "==> Waiting for the backend to answer /health..."
HEALTHY=0
for _ in $(seq 1 30); do
  if curl -sf -m 2 "http://localhost:8080/health" > /dev/null 2>&1; then
    HEALTHY=1
    break
  fi
  sleep 2
done

if [ "$HEALTHY" -ne 1 ]; then
  echo "==> Backend never became healthy — dumping Compose logs:" >&2
  docker compose "${COMPOSE_FILES[@]}" logs >&2
  exit 1
fi

echo "==> Applying migrations and seed data..."
# The one-off `migrate` service (tools profile): same image as backend,
# non-root, reads DATABASE_URL/SEED_ADMIN_* from its own environment —
# no .env file inside the container, no root.
docker compose "${COMPOSE_FILES[@]}" run --rm migrate

echo "==> Stack is up: http://localhost:8080"
