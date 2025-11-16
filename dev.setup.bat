python manage.py migrate
gunicorn 'app.wsgi' --bind=0.0.0.0:8000 --reload