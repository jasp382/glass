"""
Django settings for firerest project.

Generated by 'django-admin startproject' using Django 3.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import json
import os
from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# CONTEXT SETTINGS
CTX = json.load(open(os.path.join(BASE_DIR, 'ctx.json'), 'r'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_random_secret_key()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = CTX["DEBUG"]

ALLOWED_HOSTS = CTX["HOSTS"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # database backup
    'dbbackup',
    # django rest
    'rest_framework',
    # OAuth2
    'oauth2_provider',
    # CORS configuration
    'corsheaders',
    # Swagger
    'drf_yasg',
    # Project modules
    'authapi.apps.AuthapiConfig',
    'contrib.apps.ContribConfig',
    'detect.apps.DetectConfig',
    'events.apps.EventsConfig',
    'georef.apps.GeorefConfig',
    'georst.apps.GeorstConfig',
    'geosat.apps.GeosatConfig',
    'geosrv.apps.GeosrvConfig',
    'geovec.apps.GeovecConfig',
    'geovis.apps.GeovisConfig',
    'logs.apps.LogsConfig',
    'meteo.apps.MeteoConfig'
]

MIDDLEWARE = [
    # CORS HEADERS #
    'corsheaders.middleware.CorsMiddleware',
    ## 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'firerest.urls'

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

WSGI_APPLICATION = 'firerest.wsgi.application'

# Swagger Settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        "Authorize token (Write 'Bearer ' before code)": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header"
        }
    }
}


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = CTX["DATABASES"]


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# CORS
CORS_ORIGIN_ALLOW_ALL = True

# ADMIN Access
ADMIN_URL = CTX["ADMIN"]

# Rest Framework variables
PRETTY_VIEW = CTX["REST_PRETTY_VIEW"]

OAUTH2_PROVIDER = {
    # this is the list of available scopes
    'SCOPES': {
        'read'   : 'Read scope',
        'write'  : 'Write scope',
        'groups' : 'Access to your groups'
    },
    'ACCESS_TOKEN_EXPIRE_SECONDS': CTX["TOKEN_EXPIRE"],
    #'OAUTH_SINGLE_ACCESS_TOKEN': True,
    #'OAUTH_DELETE_EXPIRED': True
}

if DEBUG and PRETTY_VIEW:
    REST_FRAMEWORK = {
        'EXCEPTION_HANDLER': 'firerest.except.custom_exception',
        'DEFAULT_RENDERER_CLASSES' : (
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ),
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'oauth2_provider.contrib.rest_framework.OAuth2Authentication'
        ]
    }

else:
    REST_FRAMEWORK = {
        'EXCEPTION_HANDLER': 'firerest.except.custom_exception',
        'DEFAULT_RENDERER_CLASSES' : (
            'rest_framework.renderers.JSONRenderer',
        ),
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'oauth2_provider.contrib.rest_framework.OAuth2Authentication'
        ]
    }

# Applicatons tokens
APPS_TOKEN = [
    # Mobile APP
    "nxdqF6cOP9NQMUWEfxBl0okw5OOnVO7dS6elD3wVv1jUZZE5N8",
    # Web Dashboard
    "kghifo414aN94ddJDGDOGRD12ERakw1euyiflxwaZY19qw4dm6"
]

# GEOMEDIA PATH
GEOMEDIA = "/geomedia/" if "GEOMEDIA" not in CTX else CTX["GEOMEDIA"]

GEOMEDIA_FOLDERS = {
    "CTB_PHOTOS"    : os.path.join(GEOMEDIA, 'photos'),
    "CTB_CLSPHOTOS" : os.path.join(GEOMEDIA, 'clsphotos'),
    "CTB_RASTER"    : os.path.join(GEOMEDIA, 'fxrst'),
    "FLOC_RASTER"   : os.path.join(GEOMEDIA, 'flocrst')
}

PRJ_EPSG = 3763

# Database backup related
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': CTX["DB_DUMPS"]}

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'