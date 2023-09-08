celery -A django_weather_reminder worker -l INFO -P solo & celery -A django_weather_reminder beat -l INFO & gunicorn --bind=0.0.0.0 --timeout 600 django_weather_reminder.wsgi
