from pathlib import Path
import os
import environ
import logging

logger = logging.getLogger(__name__)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
print('BASE_DIR', BASE_DIR)

# 1) Create an Env instance ONCE, with default casting if needed.
env = environ.Env(
    # Example: set casting and default values
    DEBUG=(bool, False),
)

# 2) Read the .env file ONCE.
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# 3) Now retrieve environment variables from `env`.
DEBUG = env('DEBUG')
SECRET_KEY = env('DJANGO_SECRET_KEY')
APPLICATION_ENV = env('APPLICATION_ENV')
print('APPLICATION_ENV', APPLICATION_ENV)

AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='')
TMPDIR = env('TMPDIR', default='/tmp')

# 4) AWS SES / Email configuration from env variables
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
AWS_SES_REGION_NAME = env('AWS_REGION', default='us-east-1')
AWS_SES_REGION_ENDPOINT = env('AWS_SES_REGION_ENDPOINT', default='email.us-east-1.amazonaws.com')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='no-reply@atlanta24communitymedia.com')

# EMAIL_BACKEND = 'ch24app.custom_smtp_backend.DebugSMTPEmailBackend'
# EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
# EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')

logger.info(f'TMPDIR: {TMPDIR}')
print(f'TMPDIR: {TMPDIR}')

import tempfile
print(tempfile.gettempdir()) 
logger.info(f'tempfile.gettempdir(): {tempfile.gettempdir()}')

for item in os.environ:
    logger.info(f'{item}: {os.environ[item]}')
    print(f'{item}: {os.environ[item]}')
# SECURITY WARNING: don't run with debug turned on in production!

# Email notification settings
SUPPORT_NOTIFICATION_EMAILS = [
    'jpound@AtlantaGa.Gov',
]

ALLOWED_HOSTS = ['127.0.0.1', 
                '18.116.97.242',
                '3.88.237.43', 
                '3.90.216.73',
                '52.23.245.241',
                '0.0.0.0', 
                'localhost',
                'atlanta24communitymedia.com',
                'www.atlanta24communitymedia.com',
]

TIME_ZONE = 'America/New_York'

DEFAULT_USER_TIMEZONE = 'America/New_York'

if APPLICATION_ENV == 'production':
    os.environ['TMPDIR'] = "/mnt/data/tmp"
    MEDIA_ROOT = '/mnt/data/media/'
    FILE_UPLOAD_TEMP_DIR = '/mnt/data/tmp' 
    FILE_UPLOAD_HANDLERS = [
        'django.core.files.uploadhandler.TemporaryFileUploadHandler',
    ]


if APPLICATION_ENV == 'development':
    MEDIA_ROOT = '/tmp'
    os.environ['TMPDIR'] = "/tmp"
    FILE_UPLOAD_TEMP_DIR = '/tmp' 
    

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

# Base logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',  # existing console handler (for most logs)
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        # New console handler for debugging botocore and django_ses
        'console_debug': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 5 * 1024 * 1024,  # 5 MB
            'backupCount': 5,
        },
        'scheduling_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': os.path.join(BASE_DIR, 'logs', 'scheduling.log'),
            'maxBytes': 5 * 1024 * 1024,  # 5 MB
            'backupCount': 5,
        },
        'email_file': {
            'level': 'DEBUG',  # Now capturing DEBUG messages
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': os.path.join(BASE_DIR, 'logs', 'email.log'),
            'maxBytes': 5 * 1024 * 1024,  # 5 MB
            'backupCount': 5,
        },
        'botocore_file': {
            'level': 'DEBUG',  # Now capturing DEBUG messages
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': os.path.join(BASE_DIR, 'logs', 'botocore.log'),
            'maxBytes': 5 * 1024 * 1024,  # 5 MB
            'backupCount': 5,
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'console_debug': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'urllib3': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'ch24app.scheduling': {  # Scheduling-specific logger
            'handlers': ['console', 'scheduling_file'],
            'level': 'INFO',
            'propagate': False,
        },
        # New logger for botocore
        'botocore': {
            'handlers': ['console_debug', 'botocore_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # New logger for django_ses
        'django_ses': {
            'handlers': ['console_debug', 'email_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.core.mail': {  # Email-specific logger
            'handlers': ['console', 'email_file'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}

# Production environment override
if APPLICATION_ENV == 'production':
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
            },
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'level': 'WARNING',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
            'console_debug': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': '/mnt/data/logs/django.log',
                'maxBytes': 5 * 1024 * 1024,
                'backupCount': 5,
            },
            'scheduling_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'standard',
                'filename': '/mnt/data/logs/scheduling.log',
                'maxBytes': 5 * 1024 * 1024,  # 5 MB
                'backupCount': 5,
            },
            'email_file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'standard',
                'filename': '/mnt/data/logs/email.log',
                'maxBytes': 5 * 1024 * 1024,  # 5 MB
                'backupCount': 5,
            },
            'botocore_file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'standard',
                'filename': '/mnt/data/logs/botocore.log',
                'maxBytes': 5 * 1024 * 1024,  # 5 MB
                'backupCount': 5,
            }
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
            'django': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.request': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.db.backends': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
            'urllib3': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
            'ch24app.scheduling': {  # Scheduling-specific logger
                'handlers': ['console', 'scheduling_file'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.core.mail': {  # Email-specific logger
                'handlers': ['console', 'email_file'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'botocore': {
                'handlers': ['console_debug', 'botocore_file'],
                'level': 'DEBUG',
                'propagate': False,
            }
        }
    }

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
    'django_ses',
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
