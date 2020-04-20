import os

from django.contrib.messages import constants as messages

import dj_database_url
from decouple import config
from decouple import Csv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = os.path.dirname(BASE_DIR)

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default = True, cast = bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast = Csv())

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'widget_tweaks',
    'ckeditor',
    'ckeditor_uploader',
    'cacheops',

    'apps.accounts',
    'apps.classroom',
    'apps.exams',
    'apps.pages',
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

ROOT_URLCONF = 'edumate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), 'templates'],
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

WSGI_APPLICATION = 'edumate.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default = config('DATABASE_URL')
    )
}



# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATICFILES_DIRS = [
    os.path.join('static'),
]

# Miscellaneous 

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = '/accounts/signin/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

from ckeditor.configs import DEFAULT_CONFIG

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_THUMBNAIL_SIZE = (300, 300)
CKEDITOR_IMAGE_QUALITY = 40
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_ALLOW_NONIMAGE_FILES = True

CUSTOM_TOOLBAR = [
    {
        'name': 'document',
        'items': [
            'Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', '-',
            'TextColor', 'BGColor',  '-',
            'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock',
        ],
    },
    {
        'name': 'widgets',
        'items': [
            'Undo', 'Redo', '-',
            'NumberedList', 'BulletedList', '-',
            'Outdent', 'Indent', '-',
            'Link', 'Unlink', '-',
            'Image', 'Mathjax', 'CodeSnippet', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', '-',
            'Blockquote', '-',
            'ShowBlocks', 'Maximize',
        ],
    }
]

CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        'toolbar': CUSTOM_TOOLBAR,
        'toolbarGroups': None,
        'mathJaxLib': '//cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_HTML',
        'extraPlugins': ','.join(['image2', 'codesnippet', 'mathjax']),
        'removePlugins': ','.join(['image']),
        'codeSnippet_theme': 'xcode',
    },
}


CACHEOPS_REDIS = config('CACHE_LOCATION')

CACHEOPS_DEFAULTS = {
    'timeout': 2 * 24 * 60 * 60
}

CACHEOPS = {
    'accounts.*': {'ops': 'all'},
    'classroom.*': {'ops': 'all'},
    'exams.*': {'ops': 'all'},
}

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'


# Logging
# https://docs.djangoproject.com/en/3.0/topics/logging/

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'development_logfile': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': 'logs/development.log',
            'formatter': 'verbose'
        },
        'production_logfile': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/production.log',
            'maxBytes' : 1024 * 1024 * 5,
            'backupCount' : 5,
            'formatter': 'simple'
        },
        'celery': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/celery.log',
            'maxBytes' : 1024 * 1024 * 5,
            'backupCount' : 5,
            'formatter': 'verbose'
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
    'loggers': {
        'apps.exams.tasks': {
            'handlers': ['celery'],
        },
        'apps': {
            'handlers': ['development_logfile', 'production_logfile'],
        },
        'django': {
            'handlers': ['development_logfile', 'production_logfile'],
        },
        'py.warnings': {
            'handlers': ['development_logfile'],
        },
    }
}
