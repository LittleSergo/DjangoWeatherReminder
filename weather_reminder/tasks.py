import datetime
import requests
from datetime import timedelta
from pytz import timezone

from django.template.loader import render_to_string
from django.db import transaction

from django_weather_reminder.celery import app
from django.core.mail import EmailMessage

from weather_reminder.models import Subscription, City, Service
from weather_reminder.serializers import SubscriptionSerializer


def build_weather_data_from_weatherapi(json_response: dict) -> list:
    """Build data from WeatherAPI service response."""
    weather_info = json_response['current']['condition']['text']
    weather_data = {
        'Temperature': json_response['current']['temp_c'],
        'Feels like': json_response['current']['feelslike_c'],
        'Wind speed': str(json_response['current']['wind_kph']) + ' km/h',
        'Gusts of wind': str(json_response['current']['gust_kph']) + ' km/h',
        'Pressure': json_response['current']['pressure_mb'],
        'Humidity': json_response['current']['humidity'],
    }
    return [weather_info, weather_data]


def build_weather_data_from_openweather(json_response: dict) -> list:
    """Build data from OpenWeather service response."""
    weather_info = json_response['weather'][0]['main']
    weather_data = {
        'Temperature': json_response['main']['temp'],
        'Feels like': json_response['main']['feels_like'],
        'Wind speed': str(json_response['wind']['speed']) + ' m/s',
        'Gusts of wind': str(json_response['wind']['gust']) + ' m/s',
        'Pressure': json_response['main']['pressure'],
        'Humidity': json_response['main']['humidity'],
    }
    return [weather_info, weather_data]


def retrieve_weather(city: City, service: Service) -> list:
    """Get the weather info from the service and build data for email."""
    response = requests.get(service.url.format(
        key=service.api_key,
        lat=city.latitude,
        lon=city.longitude
    ))
    if service.name == 'WeatherAPI':
        weather_data = build_weather_data_from_weatherapi(
            response.json())
        weather_data.append(service.name)
        return weather_data
    if service.name == 'OpenWeather':
        weather_data = build_weather_data_from_openweather(
            response.json())
        weather_data.append(service.name)
        return weather_data


@app.task
def send_email(email: str, subscription_data: dict):
    """Build a html email and send it.
    :param email:
    :param subscription_data:
    :return:
    """
    with transaction.atomic():
        city = City.objects.get(pk=subscription_data['city'])
        weather_data = [retrieve_weather(
            city, Service.objects.get(pk=service_id)
        ) for service_id in subscription_data['services']]
    title_width = len(weather_data) * 240 + (len(weather_data) - 1) * 3
    message = render_to_string('weather_reminder/mail_template.html',
                               context={
                                   'address': city.address,
                                   'weather_data': weather_data,
                                   'title_width': title_width
                               })
    mail = EmailMessage(subject='Weather',
                        body=message,
                        to=[email])
    mail.content_subtype = 'html'
    mail.send()


@app.task
def weather_dispatch():
    """Check for every active subscription is it time to email subscriber,
    and send it if it is."""
    for sub in Subscription.objects.filter(active=True):
        if datetime.datetime.now(
                tz=timezone('EET')) >= sub.notification_last_sent + timedelta(
                    hours=sub.notification_period):
            send_email.delay(sub.user.email, SubscriptionSerializer(sub).data)
            sub.notification_last_sent = datetime.datetime.now(
                tz=timezone('EET'))
            sub.save()
