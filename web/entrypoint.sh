#!/bin/bash
set -e

# Datenbankmigrationen ausfuehren (Pitfall 2: nie db.create_all())
echo "Running database migrations..."
flask db upgrade

# Gunicorn starten -- Single Worker (Pitfall 5: APScheduler in Phase 6)
echo "Starting Gunicorn..."
exec gunicorn "app:create_app()" \
    --bind 0.0.0.0:5000 \
    --workers 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
