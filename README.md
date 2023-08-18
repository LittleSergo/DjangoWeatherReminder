# DjangoWeatherReminder - Task 16 - Decompose project

## План роботи:

### 1. Створити та налаштувати проект.

### 2. Створити та налаштувати додаток 'weather_reminder':
1. Створити моделі subscription, city та service.   --Виконано
2. Створити view та url для реєстрації користувачів.  --Виконано
3. Додати simple-jwt до проєкту.  --Виконано
4. Створити ендпоінт для підписок де можна створювати та корегувати підписки.  --Виконано
5. Написати функції send_email, get_weather та темплейт для листа які будуть брати погоду з API сервісу та відправляти її.
6. Додати до проекту та налаштувати celery.
7. Написати task та графік виконання таску.

tasks.py:
```python
@app.task
def weather_dispatch():
    for sub in Subscription.objects.filter(active=True):
        if datetime.now() <= sub.notification_last_sent + \
                timedelta(sub.notification_period):
            send_email(sub.user, sub.cities)
            sub.notification_last_sent = datetime.now()
            sub.save()
```
celery.py:
```python
# ...
from selery.schedules import crontab

app.conf.beat_schedule = {
    'task': 'weather_reminder.tasks.weather_dispatch',
    'schedule': crontab(minute='*/10'),
}
```
