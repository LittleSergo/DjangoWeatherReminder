from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Subscription, City


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for validation user registration data."""
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password']


class CreateSubscriptionSerializer(serializers.Serializer):
    """Serializer for validation data while user create subscription"""
    city = serializers.CharField()
    notification_period = serializers.ChoiceField(
        choices=[1, 3, 6, 12]
    )
    services = serializers.ListField()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription model"""
    class Meta:
        model = Subscription
        fields = ['id', 'active', 'notification_period',
                  'notification_last_sent', 'city', 'services']
        read_only_fields = ['notification_last_sent', 'id']


class CitySerializer(serializers.ModelSerializer):
    """Serializer for City model"""
    class Meta:
        model = City
        fields = ['address']
