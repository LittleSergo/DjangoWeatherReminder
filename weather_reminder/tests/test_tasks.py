from datetime import datetime, timedelta
from pytz import timezone
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from unittest.mock import patch, MagicMock

from ..models import Service, City, Subscription
from ..tasks import (
    build_weather_data_from_weatherapi, build_weather_data_from_openweather,
    retrieve_weather, send_email, weather_dispatch
)

weatherapi_response = {
    'location': {'name': 'Kiev', 'region': "Kyyivs'ka Oblast'",
                 'country': 'Ukraine', 'lat': 50.45,
                 'lon': 30.52, 'tz_id': 'Europe/Kiev',
                 'localtime_epoch': 1692954357,
                 'localtime': '2023-08-25 12:05'},
    'current': {'last_updated_epoch': 1692954000,
                'last_updated': '2023-08-25 12:00', 'temp_c': 26.7,
                'temp_f': 80.1, 'is_day': 1,
                'condition': {'text': 'Partly cloudy',
                              'icon': '//cdn.weatherapi.com/'
                                      'weather/64x64/day/116.png',
                              'code': 1003},
                'wind_mph': 6.3, 'wind_kph': 10.1, 'wind_degree': 311,
                'wind_dir': 'NW', 'pressure_mb': 1015.0,
                'pressure_in': 29.98, 'precip_mm': 0.0,
                'precip_in': 0.0, 'humidity': 34, 'cloud': 34,
                'feelslike_c': 26.2, 'feelslike_f': 79.2,
                'vis_km': 10.0, 'vis_miles': 6.0, 'uv': 7.0,
                'gust_mph': 7.2, 'gust_kph': 11.5}
}
openweather_response = {
    'coord': {'lon': 30.5241, 'lat': 50.45},
    'weather': [{'id': 804, 'main': 'Clouds',
                 'description': 'overcast clouds', 'icon': '04d'}],
    'base': 'stations',
    'main': {'temp': 27.41, 'feels_like': 27.75,
             'temp_min': 25.13, 'temp_max': 27.41, 'pressure': 1014,
             'humidity': 49}, 'visibility': 10000,
    'wind': {'speed': 0.89, 'deg': 288, 'gust': 2.68},
    'clouds': {'all': 92}, 'dt': 1692954123,
    'sys': {'type': 2, 'id': 2003742, 'country': 'UA',
            'sunrise': 1692932458, 'sunset': 1692982784},
    'timezone': 10800, 'id': 696050,
    'name': 'Pushcha-Vodytsya', 'cod': 200
}
proper_data_form_weatherapi = [
    'Partly cloudy',
    {'Temperature': 26.7,
     'Feels like': 26.2,
     'Wind speed': '10.1 km/h',
     'Gusts of wind': '11.5 km/h',
     'Pressure': 1015.0,
     'Humidity': 34}
]
proper_data_form_openweather = [
    'Clouds',
    {'Temperature': 27.41,
     'Feels like': 27.75,
     'Wind speed': '0.89 m/s',
     'Gusts of wind': '2.68 m/s',
     'Pressure': 1014,
     'Humidity': 49}
]


class TestTasks(TestCase):
    def setUp(self):
        self.weatherapi = Service.objects.create(
            name='WeatherAPI',
            url='https://some_url.com/',
            api_key='some_api_key'
        )
        self.openweather = Service.objects.create(
            name='OpenWeather',
            url='https://some_url.com/',
            api_key='some_api_key'
        )
        self.city = City(
            address='Kyiv',
            latitude=52,
            longitude=32
        )
        self.city.save()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@gmail.com'
        )
        self.subscription = Subscription.objects.create(
            user=self.user,
            active=True,
            notification_period=1,
            city=self.city
        )
        self.subscription.services.add(self.weatherapi)
        self.subscription.save()

    def test_build_weather_data_from_weatherapi(self):
        """Check building proper data from weatherapi response."""
        weather_data = build_weather_data_from_weatherapi(weatherapi_response)
        self.assertEquals(weather_data, proper_data_form_weatherapi)

    def test_build_weather_data_from_openweather(self):
        """Check building proper data from openweather response."""
        weather_data = build_weather_data_from_openweather(openweather_response)
        self.assertEquals(weather_data, proper_data_form_openweather)

    @patch('requests.get')
    def test_retrieve_weather_from_weatherapi(self, mock_requests):
        """Check if the retrieve_weather works properly with weatherapi."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = weatherapi_response

        mock_requests.return_value = mock_response
        weather_data = retrieve_weather(self.city, self.weatherapi)
        proper_data_form_weatherapi.append('WeatherAPI')
        self.assertEquals(weather_data, proper_data_form_weatherapi)

    @patch('requests.get')
    def test_retrieve_weather_from_openweather(self, mock_requests):
        """Check if the retrieve_weather works properly with openweather."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = openweather_response

        mock_requests.return_value = mock_response
        weather_data = retrieve_weather(self.city, self.openweather)
        proper_data_form_openweather.append('OpenWeather')
        self.assertEquals(weather_data, proper_data_form_openweather)

    @patch('weather_reminder.tasks.retrieve_weather')
    def test_send_email(self, mock):
        """Check for sending email function."""
        mock.return_value = proper_data_form_weatherapi
        send_email('test@gmail.com', self.city,
                   self.subscription.services)
        self.assertEquals(len(mail.outbox), 1)

    @patch('weather_reminder.tasks.send_email.delay', send_email)
    @patch('weather_reminder.tasks.retrieve_weather')
    def test_dispatch_weather_is_sent(self, mock):
        """Check that weather_dispatch filters subscriptions properly
        and send emails as needed."""
        mock.return_value = proper_data_form_weatherapi
        self.subscription.notification_last_sent = datetime.now(
            tz=timezone('EET')) - timedelta(hours=2)
        self.subscription.save()
        weather_dispatch()
        self.assertEquals(len(mail.outbox), 1)

    @patch('weather_reminder.tasks.send_email.delay', send_email)
    @patch('weather_reminder.tasks.retrieve_weather')
    def test_dispatch_weather_is_not_sent(self, mock):
        """Check that weather_dispatch filters subscriptions properly
        and doesn't send emails unnecessarily."""
        mock.return_value = proper_data_form_weatherapi
        weather_dispatch()
        self.assertEquals(len(mail.outbox), 0)
