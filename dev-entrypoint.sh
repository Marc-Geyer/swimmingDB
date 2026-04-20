#!/bin/bash
set -e

echo 'Starting setup...'
python manage.py makemessages -a --i manage.py --i node_modules --i venv --i static || true

echo 'Running migrations...'
python manage.py migrate

echo 'Creating superuser...'
python manage.py createsuperuser --noinput || true

echo 'Loading fixtures...'
python manage.py loaddata locations_base user_test_data calendar_test_data

echo 'Starting Daphne server for HTTP & WebSockets with debugger...'
# Start debugpy listener, then exec daphne
# -m debugpy --listen 0.0.0.0:5678 --wait-for-client
python -m daphne -b 0.0.0.0 -p 8000 app.asgi:application