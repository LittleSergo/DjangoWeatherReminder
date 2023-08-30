from .base import *

DEBUG = False

ALLOWED_HOSTS = [env.str('ALLOWED_HOSTS')]

DATABASES = {
    'default': env.db('DATABASE_URL')
}

# REDIS related settings
CELERY_BROKER_URL = env.str('CELERY_BROKER_URL')
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = env.str('CELERY_BROKER_URL')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
