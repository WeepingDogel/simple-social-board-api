#!/bin/bash

# Set proper Python path for local development
export PYTHONPATH=$(pwd)

echo "Running database migrations..."
python src/migrate_profiles.py

if [ $? -eq 0 ]; then
    echo "Migration completed successfully"
    exit 0
else
    echo "Migration failed"
    exit 1
fi 