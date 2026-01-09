#!/usr/bin/env bash
set -euo pipefail
# Minimal startup for Replit: use SQLite demo DB in repo (will be created if missing)
export DATABASE_URL=${DATABASE_URL:-sqlite:///backend/data.db}
export REDIS_URL=${REDIS_URL:-}
export S3_ENDPOINT_URL=${S3_ENDPOINT_URL:-}
echo "Starting BizNooks backend: DATABASE_URL=$DATABASE_URL"
exec uvicorn backend.app.main:app --host=0.0.0.0 --port 8000
