#!/bin/bash
set -e

echo "Waiting for database to be ready..."
# Give PostgreSQL more time to start and initialize
sleep 10

# Try to ping the database
MAX_RETRIES=30
COUNT=0
until pg_isready -h db -U postgres || [ $COUNT -eq $MAX_RETRIES ]; do
  echo "Waiting for database connection ($COUNT/$MAX_RETRIES)..."
  sleep 2
  COUNT=$((COUNT+1))
done

if [ $COUNT -eq $MAX_RETRIES ]; then
  echo "Database connection timed out!"
  exit 1
fi

echo "Database is ready!"

# Create schema if it doesn't exist
echo "Ensuring database schema exists..."
PGPASSWORD=postgres psql -h db -U postgres -d social_board -c "CREATE SCHEMA IF NOT EXISTS public;" || true

echo "Running database initialization..."
python /app/src/init_db.py

echo "Starting FastAPI application..."
exec uvicorn src.app.main:app --host 0.0.0.0 --port 8000 