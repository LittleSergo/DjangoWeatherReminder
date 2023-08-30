from django.contrib.auth import get_user_model
from django.test import TestCase
from django.db import transaction

from ..models import Subscription, City, Service


class TestUserRegistrationView(TestCase):
    def test_register_user_view(self):
        """Test register view."""
        response = self.client.post('/api/v1/users/register/', data={
            "username": "testuser",
            "email": "test@email.com",
            "password": "testpassword"
        })

        self.assertEquals(response.json()['username'], 'testuser')
        user = get_user_model().objects.get(username='testuser')
        self.assertEquals(user.email, "test@email.com")


class TestSubscriptionView(TestCase):
    def setUp(self):
        with transaction.atomic():
            self.user = get_user_model().objects.create_user(
                username='testuser',
                password='testpass1234',
                email='test@email.com'
            )
            self.city = City.objects.create(
                address='Kyiv, Ukraine',
                latitude=50.4500336,
                longitude=30.5241361
            )
            self.subscription = Subscription.objects.create(
                user=self.user,
                active=True,
                notification_period=3,
                city=self.city
            )
            self.service = Service.objects.create(
                name='weatherapi',
                url='api.weather.com',
                api_key='123456789'
            )
        self.access_token = self.client.post('/api/v1/token/', data={
            'username': 'testuser',
            'password': 'testpass1234'
        }).json()['access']

    def test_get_subscriptions_unauthorized(self):
        """Try to get subscriptions unauthorized."""
        response = self.client.get('/api/v1/subscriptions/')
        self.assertEquals(response.json(), {
            'detail': 'Authentication credentials were not provided.'
        })

    def test_get_subscriptions_authorized(self):
        """Get subscriptions of authorized user"""
        response = self.client.get(
            '/api/v1/subscriptions/',
            headers={'Authorization': 'Bearer ' + self.access_token}
        )
        self.assertEquals(response.json()[0]['notification_period'], 3)

    def test_post_subscriptions(self):
        """Create new subscription"""
        response = self.client.post(
            '/api/v1/subscriptions/',
            data={
                'city': self.city.id,
                'notification_period': 6,
                'services': [self.service.id]
            },
            headers={'Authorization': 'Bearer ' + self.access_token}
        )
        self.assertEquals(
            response.json()['notification_period'], 6
        )

    def test_retrieve_subscription(self):
        """Get one subscription."""
        response = self.client.get(
            f'/api/v1/subscriptions/{self.subscription.id}/',
            headers={'Authorization': 'Bearer ' + self.access_token},
        )
        self.assertEquals(response.json()['notification_period'], 3)

    def test_put_subscription(self):
        """Change special subscription data."""
        response = self.client.put(
            f'/api/v1/subscriptions/{self.subscription.id}/',
            headers={'Authorization': 'Bearer ' + self.access_token},
            data={
                'active': True,
                'notification_period': 12,
                'city': self.city.id,
                'services': [self.service.id]
            },
            content_type='application/json'
        )
        self.assertEquals(
            response.json()['notification_period'], 12
        )

    def test_retrieve_city(self):
        """Get one city object."""
        response = self.client.get(
            f'/api/v1/cities/{self.city.id}/',
            headers={'Authorization': 'Bearer ' + self.access_token},
            content_type='application/json'
        )
        self.assertEquals(response.json()['address'], 'Kyiv, Ukraine')

    def test_search_city(self):
        """Search city by name."""
        response = self.client.get(
            f'/api/v1/cities/?search=Kyiv',
            headers={'Authorization': 'Bearer ' + self.access_token},
            content_type='application/json'
        )
        self.assertEquals(response.json()['address'], 'Kyiv, Ukraine')

    def test_get_cities(self):
        """Get all City objects."""
        response = self.client.get(
            f'/api/v1/cities/',
            headers={'Authorization': 'Bearer ' + self.access_token},
            content_type='application/json'
        )
        self.assertEquals(response.json()[0]['address'], 'Kyiv, Ukraine')

    def test_post_cities(self):
        """Post and create new one city."""
        response = self.client.post(
            f'/api/v1/cities/',
            headers={'Authorization': 'Bearer ' + self.access_token},
            data={"address": 'New York, USA'},
            content_type='application/json'
        )
        self.assertEquals(response.json()['address'],
                          'New York, United States')
