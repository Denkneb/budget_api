from .base import *

DEBUG = False
ALLOWED_HOSTS = ['budgets.domain']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'budget',
        'USER': 'budget',
        'PASSWORD': 'budget',
        'HOST': 'postgres',
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_URL = 'redis://redis'

BROKER_URL = '{}/{}'.format(REDIS_URL, '0')
CELERY_RESULT_BACKEND = '{}/{}'.format(REDIS_URL, '0')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
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
            'level': 'ERROR',
        }
    },
}