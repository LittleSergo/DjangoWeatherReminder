import faker

from random import choice
from django.db import IntegrityError
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model

from ...models import City, Subscription
from ...serializers import geolocator

fake = faker.Faker()
generators = {}
user_ids = []
cities = [
    'Харків, Україна', 'Львів, Україна', 'Дніпро, Україна',
    'Київ, Україна', 'Одеса, Україна'
]
city_objects = []


def generators_sort():
    """Sort generators dictionary by dependencies."""
    visited = set()
    stack = {}
    global generators

    def dfs(node):
        if node in visited:
            return
        visited.add(node)

        if node in generators:
            for dependency in generators[node][0]:
                dfs(dependency)

            stack[node] = generators[node]

    for node in generators:
        dfs(node)

    generators = stack


def register(deps: list = None):
    """Register function in generators dictionary and call
    sorting function.
    :param deps:
    :return:
    """
    if deps is None:
        deps = []

    def decorator(func):
        generators[func.__name__] = (deps, func)

        generators_sort()
        return func
    return decorator


@register()
def create_cities():
    """Create City objects from the cities list."""
    for city_name in cities:
        location = geolocator.geocode(city_name, language='en-gb')
        try:
            city = City.objects.create(
                address=location.address,
                latitude=location.latitude,
                longitude=location.longitude
            )
        except IntegrityError:
            city = City.objects.get(address=location.address)
        city_objects.append(city)


@register(deps=['create_fake_user', 'create_cities'])
def create_fake_subscriptions():
    """Create fake subscriptions.
    :return:
    """
    with transaction.atomic():
        for user_id in user_ids:
            user = get_user_model().objects.get(pk=user_id)
            for _ in range(2):
                sub = Subscription.objects.create(
                    user=user,
                    active=False,
                    notification_period=3,
                    city=choice(city_objects)
                )
                sub.services.set([1, 2])
                sub.save()


@register()
def create_fake_user():
    """Create 2 fake users.
    :return:
    """
    with transaction.atomic():
        for _ in range(2):
            user_data = fake.profile()
            user = get_user_model().objects.create_user(
                username=user_data['username'],
                email=user_data['mail'],
            )
            user_ids.append(user.id)


class Command(BaseCommand):
    """CLI command for adding fake users with fake subscriptions."""
    help = 'Add 2 fake users with fake subscriptions.'

    def handle(self, *args, **options):
        for name, (deps, func) in generators.items():
            func()
        self.stdout.write(
            self.style.SUCCESS('Successfully created.'))
