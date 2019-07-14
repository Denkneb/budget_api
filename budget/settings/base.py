"""
Django settings for budget project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

from celery.schedules import crontab
from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve().parent.parent

VAR_PATH = BASE_DIR.parent / 'var'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_r!_61%-$=v_4479g_0-yjm1+&81(#gzxeu!g66wut%r%z_=d_'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'user',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'budget.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'budget.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (
    ('en', _('English')),
    ('ru', _('Russian')),
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR.parent, 'staticfiles')

MEDIA_ROOT = os.path.join(BASE_DIR.parent, 'media')
MEDIA_URL = '/media/'
FILE_UPLOAD_PERMISSIONS = 0o644

STATICFILES_DIRS = [
    os.path.join(BASE_DIR.parent, 'static'),
]


# Auth
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-user-model

AUTH_USER_MODEL = 'user.User'

LOGIN_URL = '/user/login/'
CSRF_FAILURE_VIEW = 'budget.user.views.csrf_failure'

JWT_AUTH = {
    'JWT_SECRET_KEY': '2f0ebae919f01a259dad72925ed52f7f1335c76471c0cfd09379aa279a75af4h',
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': timedelta(seconds=60 * 120),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
    'JWT_ALGORITHM': 'HS512',
    'JWT_PAYLOAD_GET_USERNAME_HANDLER': 'user.tools.jwt_get_username_from_payload_handler',
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'user.tools.jwt_response_payload_handler',
    'JWT_GET_USER_SECRET_KEY': 'user.tools.jwt_get_user_secret_key',
    'JWT_AUTH_COOKIE': None
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),

    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '200/minute',
        'user': '500/minute',
        'obtain-token': '200/day',
        'verify-token': '5000/day',
        'refresh-token': '5000/day',
        'verify-email': '10/minute',
        'reset-pass': '10/minute',
    },
    'SEARCH_PARAM': 'search',
    'ORDERING_PARAM': 'ordering',

    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    )
}

APPEND_SLASH = False

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
BROKER_TRANSPORT_OPTIONS = {'fanout_prefix': True, 'fanout_patterns': True}
CELERY_STORE_ERRORS_EVEN_IF_IGNORED = False


CELERYBEAT_SCHEDULE = {
    'update_fias_addrs_from_dbf': {
        'task': 'fias.tasks.update_fias_addrs_from_dbf',
        'schedule': crontab(minute=0, hour=0, day_of_week=[1, 2, 3, 4, 5]),
    },
}

# Request timeout
# http://docs.python-requests.org/en/master/user/advanced/#timeouts
REQUEST_TIMEOUT_SECONDS = 30
