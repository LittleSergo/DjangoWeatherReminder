from .base import *

DEBUG = env.str('DEBUG') in ['1', 'true']

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS')

SECURE_SSL_REDIRECT = \
    env.str('SECURE_SSL_REDIRECT', '0').lower() in ['true', 't', '1']
if SECURE_SSL_REDIRECT:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

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
CELERY_BROKER_URL = env.str('AZURE_REDIS_CONNECTIONSTRING')
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = env.str('AZURE_REDIS_CONNECTIONSTRING')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
