#!/bin/bash
set -e

echo "🚀 Starting SwimPro Initialization..."

echo "🔄 Running database migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser"
python manage.py createsuperuser

case "$SERVER_TYPE" in
    wsgi)
        echo "🟢 Starting Gunicorn (WSGI) server..."
        exec gunicorn --bind 0.0.0.0:8000 app.wsgi:application
        ;;
    asgi)
        echo "🟢 Starting Daphne (ASGI) server..."
        exec daphne -b 0.0.0.0 -p 8000 app.asgi:application
        ;;
    *)
        echo "❌ Invalid SERVER_TYPE: $SERVER_TYPE. Using default (asgi)"
        exec daphne -b 0.0.0.0 -p 8000 app.asgi:application
        ;;
esac