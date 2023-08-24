import ssl
import certifi
import geopy

from geopy.geocoders import Nominatim
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Subscription, City

ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx
geolocator = Nominatim(user_agent='django_weather_reminder')


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for validation user registration data."""
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription model"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Subscription
        fields = ['id', 'active', 'user', 'notification_period',
                  'notification_last_sent', 'city', 'services']
        read_only_fields = ['notification_last_sent', 'id']


class CitySerializer(serializers.ModelSerializer):
    """Serializer for City model"""
    class Meta:
        model = City
        fields = ['id', 'address']

    def create(self, validated_data):
        location = geolocator.geocode(validated_data['address'], language='en-gb')
        return City.objects.create(
            address=location.address,
            latitude=location.latitude,
            longitude=location.longitude
        )
