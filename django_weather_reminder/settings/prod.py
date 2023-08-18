from .base import *

DEBUG = False

ALLOWED_HOSTS = [env.str('ALLOWED_HOSTS')]

DATABASES = {
    'default': env.db('DATABASE_URL')
}
