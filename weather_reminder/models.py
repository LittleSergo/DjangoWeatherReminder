from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models


class City(models.Model):
    """City model. Contains city address, latitude and longitude."""
    address = models.CharField(max_length=250, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()


class Service(models.Model):
    """Service model. Contains service name, url and api key."""
    name = models.CharField(max_length=150, unique=True)
    url = models.CharField(max_length=250)
    api_key = models.CharField(max_length=250)


class Subscription(models.Model):
    """Subscription model. Contains user who belong to this
    subscription, is this subscription active, notification period -
    how often user will be receiving emails, time when was sent """
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE,
                             related_name='subscriptions')
    active = models.BooleanField(default=True)
    notification_period = models.IntegerField(choices=[
        (1, 1), (3, 3), (6, 6), (12, 12)
    ])
    notification_last_sent = models.DateTimeField(auto_now_add=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE,
                             related_name='subscriptions', )
    services = models.ManyToManyField(Service,
                                      related_name='subscriptions')
