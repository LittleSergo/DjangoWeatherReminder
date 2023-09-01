import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'django_weather_reminder.settings.dev')

app = Celery('django_weather_reminder')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send_email_every_10_minute': {
        'task': 'weather_reminder.tasks.weather_dispatch',
        'schedule': crontab(minute='*/10')
    },
}
