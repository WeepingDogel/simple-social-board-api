#!/bin/bash

set -e

# Set environment variables for local development
export PYTHONPATH=$(pwd)
export DATABASE_URL=${DATABASE_URL:-"sqlite:///./database.db"}
export SECRET_KEY=${SECRET_KEY:-"your_secret_dev_key"}

echo "Using database: $DATABASE_URL"

# Create tables and apply migrations
echo "Initializing database tables..."
python -c "
from src.app.models.model import Base
from src.app.services.database import engine

# Create all tables
Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
"

# Run migrations
echo "Running database migrations..."
python src/migrate_profiles.py

# Start the application with reload
echo "Starting FastAPI application in development mode..."
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000 