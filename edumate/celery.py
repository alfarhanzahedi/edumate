import os
from celery import Celery
 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edumate.settings.development')

app = Celery('edumate')
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
