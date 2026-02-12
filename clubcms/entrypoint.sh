#!/bin/bash
set -e

echo "Waiting for database..."
while ! python -c "
import os, psycopg
conn = psycopg.connect(os.environ['DATABASE_URL'])
conn.close()
" 2>/dev/null; do
    sleep 1
done
echo "Database ready."

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating cache table..."
python manage.py createcachetable --database default 2>/dev/null || true

echo "Starting application..."
exec "$@"
