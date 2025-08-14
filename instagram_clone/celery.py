from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_clone.settings')

app = Celery('instagram_clone')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.broker_connection_retry_on_startup = True

app.conf.beat_schedule = {
    'archive-stories': {
        'task': 'posts.tasks.check_stories_status',
        'schedule': crontab(minute='*/1') # runs every 30 minutes
    }
}

app.conf.timezone = 'Asia/Tashkent'
