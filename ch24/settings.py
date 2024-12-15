"""
Django settings for ch24 project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
import environ
import logging

logger = logging.getLogger(__name__)

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Set the project base directory
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
print('BASE_DIR', BASE_DIR)

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
# False if not in os.environ because of casting above
DEBUG = env('DEBUG')

AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
# print('AWS_STORAGE_BUCKET_NAME', AWS_STORAGE_BUCKET_NAME)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY')

APPLICATION_ENV = env('APPLICATION_ENV')
print('APPLICATION_ENV', APPLICATION_ENV)


# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = ['127.0.0.1', 
                '18.116.97.242',
                '3.88.237.43', 
                '3.90.216.73',
                '52.23.245.241',
                '0.0.0.0', 
                'localhost',
                'atlanta24communitymedia.com',
                'www.atlanta24communitymedia.com',
                'atlanta24communitymediatest.com',
                'www.atlanta24communitymediatest.com',
]

TIME_ZONE = 'America/New_York'
MEDIA_ROOT = '/mnt/data/media/'
# MEDIA_ROOT = '/tmp'

if APPLICATION_ENV == 'development':
    MEDIA_ROOT = '/tmp'
    # MEDIA_URL = '/media/'


# Add STATIC_ROOT setting
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# URL to use when referring to static files located in STATIC_ROOT
STATIC_URL = '/static/'

# Additional directories to look for static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# settings.py

import logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 5 * 1024 * 1024,  # 5 MB
            'backupCount': 5,
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'urllib3': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

if APPLICATION_ENV == 'production':
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,  # Keeps existing loggers active
        'formatters': {
            'standard': {
                'format': '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'WARNING',  # Adjust as needed
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
            },
            'file': {
                'level': 'INFO',  # Captures INFO and above
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'standard',
                'filename': '/mnt/data/logs/django.log',  # Log file on EBS
                'maxBytes': 5 * 1024 * 1024,  # 5 MB
                'backupCount': 5,
            },
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'file'],  # Logs to both console and file
                'level': 'INFO',  # Minimum log level
                'propagate': True,
            },
            'django': {
                'handlers': ['console', 'file'],
                'level': 'INFO',  # Only log errors from Django
                'propagate': True,
            },
            'django.request': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': True,
            },
            'django.db.backends': {
                'handlers': ['console', 'file'],
                'level': 'ERROR',
                'propagate': False,
            },
            'urllib3': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
            # Add your application's logger if necessary
            'ch24app': {  # Replace with your actual app name
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': True,
            },
        }
    }

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,  # Keeps existing loggers active
#     'formatters': {
#         'standard': {
#             'format': '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
#         },
#     },
#     'handlers': {
#         'console': {
#             'level': 'WARNING',  # Adjust as needed
#             'class': 'logging.StreamHandler',
#             'formatter': 'standard',
#         },
#         'file': {
#             'level': 'INFO',  # Adjust as needed
#             'class': 'logging.handlers.RotatingFileHandler',
#             'formatter': 'standard',
#             'filename': '/mnt/data/logs/django.log',  # Path to log file
#             'maxBytes': 5 * 1024 * 1024,  # 5 MB
#             'backupCount': 5,  # Number of backups to keep
#         },
#     },
#     'loggers': {
#         '': {  # Root logger
#             'handlers': ['console', 'file'],  # Logs to both console and file
#             'level': 'INFO',  # Minimum log level
#             'propagate': True,
#         },
#         'django': {
#             'handlers': ['console', 'file'],
#             'level': 'ERROR',  # Only log errors from Django
#             'propagate': False,
#         },
#         'django.request': {
#             'handlers': ['console', 'file'],
#             'level': 'ERROR',
#             'propagate': False,
#         },
#         'django.db.backends': {
#             'handlers': ['console', 'file'],
#             'level': 'ERROR',
#             'propagate': False,
#         },
#         'urllib3': {
#             'handlers': ['console', 'file'],
#             'level': 'ERROR',
#             'propagate': False,
#         },
#     }
# }

logger.error("Testing logging")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ch24app',
    'creators',
    'django_otp',
    'django_otp.plugins.otp_totp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_otp.middleware.OTPMiddleware',
]

ROOT_URLCONF = 'ch24.urls'

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

WSGI_APPLICATION = 'ch24.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# 

DATABASE_ENGINE = env('DATABASE_ENGINE')
DATABASE_NAME = env('DATABASE_NAME')
DATABASE_USER = env('DATABASE_USER')
DATABASE_PASSWORD = env('DATABASE_PASSWORD')
DATABASE_HOST = env('DATABASE_HOST')
DATABASE_PORT = env('DATABASE_PORT')


DATABASES = {
    'default': {    
        'ENGINE': DATABASE_ENGINE,
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': DATABASE_PORT,
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = [
    'https://atlanta24communitymedia.com',
    'https://www.atlanta24communitymedia.com',
    'https://atlanta24communitymediatest.com',
    'https://www.atlanta24communitymediatest.com',
]
