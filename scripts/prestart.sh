#! /usr/bin/env bash

# Let the DB start
echo "Waiting for database..."
sleep 2

# Run migrations
echo "Running migrations..."
alembic upgrade head

# Create initial data (if separate script exists)
# python src/initial_data.py
