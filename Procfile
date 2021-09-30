web: python manage.py migrate && python manage.py compilescss && waitress-serve --port=$PORT config.wsgi:application
celery-worker: celery -A config worker -l INFO
celery-beat: celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
