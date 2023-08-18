from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import (
    City, Service, Subscription
)


class ModelsTests(TestCase):
    def setUp(self):
        self.city = City.objects.create(
            address='Kyiv, Ukraine',
            latitude=50.4500336,
            longitude=30.5241361
        )
        self.service = Service.objects.create(
            name='weatherapi',
            url='api.weather.com',
            api_key='123456789'
        )

    def test_city_model(self):
        """Create City object get it and check."""
        city = City.objects.get(address='Kyiv, Ukraine')
        self.assertEquals(city.latitude, 50.4500336)

    def test_service_model(self):
        """Create Service object get it and check."""
        service = Service.objects.get(name='weatherapi')
        self.assertEquals(service.api_key, '123456789')

    def test_subscription_model(self):
        """Create Subscription object get it and check."""
        user = get_user_model().objects.create_user(username='testuser')
        sub = Subscription.objects.create(
            user=user,
            active=True,
            notification_period=3,
            city=self.city
        )
        sub.services.add(self.service)

        sub = Subscription.objects.get(user=user)
        self.assertEquals(sub.city, self.city)
