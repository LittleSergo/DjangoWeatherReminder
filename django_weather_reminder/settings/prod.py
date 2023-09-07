from .base import *

DEBUG = env.str('DEBUG') in ['1', 'true']

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('DBNAME'),
        'HOST': env.str('DBHOST'),
        'USER': env.str('DBUSER'),
        'PASSWORD': env.str('DBPASS'),
        'OPTIONS': {'sslmode': 'require'},
    }
}

# REDIS related settings
CELERY_BROKER_URL = env.str('AZURE_REDIS_CONNECTIONSTRING'),
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = env.str('AZURE_REDIS_CONNECTIONSTRING'),
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
