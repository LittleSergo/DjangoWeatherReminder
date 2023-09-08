celery -A django_weather_reminder worker -l INFO -B & gunicorn --bind=0.0.0.0 --timeout 600 django_weather_reminder.wsgi
