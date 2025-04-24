#!/bin/bash

set -e

# Wait for the database to be ready
echo "Waiting for database to be ready..."
PYTHONPATH=/app python -c "
import time
import sys
from src.app.services.database import wait_for_db

max_retries = 60
retry_interval = 2

for i in range(max_retries):
    print(f'Attempt {i+1}/{max_retries}...')
    if wait_for_db(max_retries=1, retry_interval=1):
        print('Database is ready!')
        sys.exit(0)
    time.sleep(retry_interval)

print('Database connection failed after max retries')
sys.exit(1)
"

# Initialize the database tables first
echo "Initializing database tables..."
PYTHONPATH=/app python -c "
from src.app.models.model import Base
from src.app.services.database import engine

# Create all tables
Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
"

# Run migrations
echo "Running database migrations..."
PYTHONPATH=/app python /app/src/migrate_profiles.py

# Start the application
echo "Starting FastAPI application..."
exec "$@" 