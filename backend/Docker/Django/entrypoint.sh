#!/bin/sh
set -e

if [ "$DATABASE" = "postgres" ]
then
    echo "Verifying PostgreSQL connectivity..."
    while ! nc -z $DB_HOST $DB_PORT; do
      echo "Postgres is unavailable - sleeping"
      sleep 1
    done
    echo "PostgreSQL started and accepting connections!"
fi

# Move into the core folder where manage.py lives to execute operations
cd /app/core

echo "Executing production migrations..."
python manage.py migrate --noinput

echo "Collecting static assets..."
python manage.py collectstatic --noinput

# Pass execution back over to the CMD (Uvicorn launcher)
exec "$@"
