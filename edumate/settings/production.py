from kombu.utils.url import safequote

from .base import *

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = '/var/www/edumate/static/'
STATIC_URL = '/static/'

MEDIA_ROOT = '/var/www/edumate/media/'
MEDIA_URL = '/media/'

# Email 
# https://docs.djangoproject.com/en/2.2/topics/email/#email-backends

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('SENDGRID_API_KEY')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_USE_TLS = config('EMAIL_USE_TLS')

AZURE_STORAGE_KEY = config('AZURE_STORAGE_KEY')
AZURE_STORAGE_ACCOUNT = config('AZURE_STORAGE_ACCOUNT')

BROKER_URL = "azurestoragequeues://:" + safequote(f'{AZURE_STORAGE_KEY}@{AZURE_STORAGE_ACCOUNT}', safe = "=@")

BROKER_TRANSPORT_OPTIONS = {
    'polling_interval': 10,
    'visibility_timeout': 3600
}
