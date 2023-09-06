from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .serializers import (
    UserRegisterSerializer, CitySerializer,
    geolocator, SubscriptionSerializer
)
from .models import Subscription, City


def get_city_obj_if_exists(city: str):
    """Find and return city if exists, else return None.
    :param city:
    :return:
    """
    location = geolocator.geocode(city, language='en-gb')
    found_city = City.objects.filter(address=location.address)
    return found_city[0] if found_city.exists() else None


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


class CityView(viewsets.ModelViewSet):
    """View for cities."""
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = (IsAuthenticated, )

    def list(self, request, *args, **kwargs):
        """If the parameter 'search' passed return City object if exists,
        and return the message 'The city doesn't exist' if not.
        Or return all cities if its simple get request.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        if 'search' in request.query_params:
            city = get_city_obj_if_exists(request.query_params['search'])
            if city:
                return Response(CitySerializer(city).data)
            return Response({'message': 'City does not exists, '
                                        'create new one.'})
        return Response(
            CitySerializer(City.objects.all(), many=True).data
        )

    def destroy(self, request, *args, **kwargs):
        """Don't allow user to delete the cities."""
        return Response({'detail': 'Method not allowed for DELETE.'},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)
