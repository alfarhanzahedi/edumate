from .base import *

# Django Debug Toolbar
# https://django-debug-toolbar.readthedocs.io/en/latest/

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'staticfiles')
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join('static'),
]

# Email 
# https://docs.djangoproject.com/en/2.2/topics/email/#email-backends

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'
