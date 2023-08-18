import ssl

import certifi
import geopy

from geopy.geocoders import Nominatim
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .serializers import (
    UserRegisterSerializer, CitySerializer,
    CreateSubscriptionSerializer, SubscriptionSerializer
)
from .models import Subscription, City

ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx
geolocator = Nominatim(user_agent='django_weather_reminder')


def get_or_create_city_obj(city: str):
    """Find city if exists or create new.
    :param city:
    :return:
    """
    location = geolocator.geocode(city, language='en-gb')
    found_city = City.objects.filter(address=location.address)
    return City.objects.create(
        address=location.address,
        latitude=location.latitude,
        longitude=location.longitude
    ) if not found_city.exists() else found_city[0]


class UserRegistrationView(generics.CreateAPIView):
    """User registration view."""
    queryset = get_user_model().objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny, )


class SubscriptionView(viewsets.ModelViewSet):
    """View for subscriptions. User can create subscription,
    get all subscriptions or special one, update and delete
    subscriptions."""
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """Show only authorized users subscriptions"""
        return self.request.user.subscriptions.all()

    def create(self, request, *args, **kwargs):
        """Check if posted data is valid, create or find city, and
        create subscription for authorized user.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = CreateSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        city = get_or_create_city_obj(request.data['city'])
        subscription = Subscription.objects.create(
            user=request.user,
            notification_period=request.data[
                'notification_period'
            ],
            city=city,
        )
        subscription.services.set(request.data['services'])
        subscription.save()
        return Response({
            'subscription': SubscriptionSerializer(subscription).data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Find subscription and change posted data.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        subscription = Subscription.objects.get(pk=kwargs['pk'])
        serializer = SubscriptionSerializer(data=request.data)
        city = get_or_create_city_obj(request.data['city'])

        serializer.initial_data['city'] = city.id
        serializer.is_valid(raise_exception=True)

        subscription.city = city
        subscription.active = request.data['active']
        subscription.notification_period = request.data['notification_period']
        subscription.services.set(request.data['services'])
        subscription.save()

        return Response({
            'Updated': SubscriptionSerializer(subscription).data
        })


class RetrieveCityView(generics.RetrieveAPIView):
    """View for retrieving cities."""
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = (IsAuthenticated, )
