web: python manage.py migrate && waitress-serve --port=$PORT config.wsgi:application
celery-worker: celery -A config worker -l INFO
