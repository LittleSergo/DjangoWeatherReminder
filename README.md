# DjangoWeatherReminder - Task 16 - Decompose project

## План роботи:

### 1. Створити та налаштувати проект.

### 2. Створити та налаштувати додаток 'weather_reminder':
1. Створити моделі subscriprion, city та service:

```python
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='subscription',
                             unique=True)
    active = models.BooleanField(default=False)
    notification_period = models.DurationField(blank=True)
    notification_last_sent = models.DateTimeField(auto_now_add=True)


class City(models.Model):
    subscription = models.ManyToManyField(Subscription, related_name='cities')
    address = models.CharField(unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    
class Service(models.Model):
    name = models.CharField(max_lenght=150, unique=True)
    url = models.CharField()
    api = models.CharField()
```

2. Створити темплейти, views та urls для реєстрації та логіну користувачів.
3. Створити сторінку профілю користувача де він може редагувати профіль та налаштувати підписку.
4. Написати функції send_email, get_weather та темплейт для листа які будуть брати погоду з API сервісу та відправляти її.
5. Додати до проекту та налаштувати celery.
6. Написати task та графік виконання таску.

tasks.py:
```python
@app.task
def weather_dispatch():
    for sub in Subscription.objects.filter(active=True):
        if datetime.now() <= sub.notification_last_sent + sub.notification_period:
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
