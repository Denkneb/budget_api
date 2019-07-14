from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'budget',
        'USER': 'budget',
        'PASSWORD': 'budget',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

INSTALLED_APPS += ['debug_toolbar', 'django_extensions']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

AUTH_PASSWORD_VALIDATORS = []

# https://django-debug-toolbar.readthedocs.io/en/stable/configuration.html?highlight=SHOW_TOOLBAR_CALLBACK
# default ‘debug_toolbar.middleware.show_toolbar’ use this to activate self
INTERNAL_IPS = ('127.0.0.1', )


REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_URL = 'redis://127.0.0.1:6379'

BROKER_URL = '{}/{}'.format(REDIS_URL, '0')
CELERY_RESULT_BACKEND = '{}/{}'.format(REDIS_URL, '0')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(levelname)s] %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '[%(asctime)s] %(levelname)s [%(module)s:%(lineno)d]  %(message)s'
        },
        'medium': {
            'format': '[%(levelname)s %(module)s %(lineno)d] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'app': {
            'handlers': ['console'],
            'level': 'DEBUG',
        }
    },
}