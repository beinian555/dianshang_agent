#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until pg_isready -h db -p 5432 -U postgres 2>/dev/null; do
  sleep 1
done
echo "PostgreSQL is ready."

echo "Running migrations..."
alembic upgrade head

echo "Starting backend..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
