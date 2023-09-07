export LANG=C.UTF-8

gunicorn --bind=0.0.0.0 --timeout 600 django_weather_reminder.wsgi & celery -A django_weather_reminder worker -l INFO -B
