#!/usr/bin/env bash
set -euo pipefail
# Run alembic migrations against DATABASE_URL (defaults to sqlite demo DB)
DB_URL=${DATABASE_URL:-sqlite:///$(pwd)/backend/data.db}
export DATABASE_URL=$DB_URL
echo "Running migrations against $DATABASE_URL"
alembic upgrade head
echo "Migrations complete"
