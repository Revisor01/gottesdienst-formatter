#!/bin/bash
set -e

# Schema nur über Migrationen, nie db.create_all()
echo "Running database migrations..."
flask db upgrade

# Ein Worker, sonst liefe der APScheduler mehrfach
echo "Starting Gunicorn..."
exec gunicorn "app:create_app()" \
    --bind 0.0.0.0:5000 \
    --workers 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
