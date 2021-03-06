import os
import dj_database_url

from decouple import config
from django.utils.log import DEFAULT_LOGGING

from .utils import cast_supported_languages
from .utils import cast_empty_str_to_none


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='*',
    cast=lambda v: [s.strip() for s in v.split(',')])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'corsheaders',
    'bothub.authentication',
    'bothub.common',
    'bothub.api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bothub.urls'

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

WSGI_APPLICATION = 'bothub.wsgi.application'


# Database

DATABASES = {}
DATABASES['default'] = dj_database_url.parse(
    config(
        'DEFAULT_DATABASE',
        default='sqlite:///db.sqlite3'))


# Auth

AUTH_USER_MODEL = 'authentication.User'


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.' +
        'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.' +
        'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.' +
        'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.' +
        'NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = config('LANGUAGE_CODE', default='en-us')

TIME_ZONE = config('TIME_ZONE', default='UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = config('STATIC_URL', default='/static/')

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# rest framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.' +
    'LimitOffsetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_METADATA_CLASS': 'bothub.api.v1.metadata.Metadata',
}


# cors headers

CORS_ORIGIN_ALLOW_ALL = True


# mail

envvar_EMAIL_HOST = config(
    'EMAIL_HOST',
    default=None,
    cast=cast_empty_str_to_none)

ADMINS = config(
    'ADMINS',
    default='',
    cast=lambda v: [
        (
            s.strip().split('|')[0],
            s.strip().split('|')[1],
        ) for s in v.split(',')] if v else [])
EMAIL_SUBJECT_PREFIX = '[bothub] '
DEFAULT_FROM_EMAIL = config(
    'DEFAULT_FROM_EMAIL',
    default='webmaster@localhost')
SERVER_EMAIL = config('SERVER_EMAIL', default='root@localhost')

if envvar_EMAIL_HOST:
    EMAIL_HOST = envvar_EMAIL_HOST
    EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
    EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SEND_EMAILS = config('SEND_EMAILS', default=True, cast=bool)


# webapp

BOTHUB_WEBAPP_BASE_URL = config(
    'BOTHUB_WEBAPP_BASE_URL',
    default='http://localhost:8080/')


# NLP

BOTHUB_NLP_BASE_URL = config(
    'BOTHUB_NLP_BASE_URL',
    default='http://localhost:2657/')


# CSRF

CSRF_COOKIE_DOMAIN = config(
    'CSRF_COOKIE_DOMAIN',
    default=None,
    cast=cast_empty_str_to_none)

CSRF_COOKIE_SECURE = config(
    'CSRF_COOKIE_SECURE',
    default=False,
    cast=bool)


# Logging

LOGGING = DEFAULT_LOGGING
LOGGING['formatters']['bothub.health'] = {
    'format': '[bothub.health] {message}',
    'style': '{',
}
LOGGING['handlers']['bothub.health'] = {
    'level': 'DEBUG',
    'class': 'logging.StreamHandler',
    'formatter': 'bothub.health',
}
LOGGING['loggers']['bothub.health.checks'] = {
    'handlers': ['bothub.health'],
    'level': 'DEBUG',
}


# Supported Languages

SUPPORTED_LANGUAGES = config(
    'SUPPORTED_LANGUAGES',
    default='en|pt',
    cast=cast_supported_languages)


# SECURE PROXY SSL HEADER

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
