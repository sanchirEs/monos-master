"""
monoscelery Configuration
"""
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monos.settings')

app = Celery('monos', include=['monosbot.celery_tasks', 'monos.celery_scheduled_tasks'])

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'run-each-hour': {
        'task': 'monos.celery_scheduled_tasks.each_ten',
        'schedule': crontab(minute='*/10'),
        # 'schedule': crontab(minute=0, hour=1),
    },
    'run-each-minutes': {
        'task': 'monos.celery_scheduled_tasks.each_minutes',
        'schedule': crontab(),
        # 'schedule': crontab(minute='*/10'),
    },
    'run-every-day': {
        'task': 'monos.celery_scheduled_tasks.summarize_daily',
        'schedule': crontab(minute=0, hour=0),
        # 'schedule': crontab(minute='*/10'),
    },
    'run-every-week': {
        'task': 'monos.celery_scheduled_tasks.summarize_weekly',
        'schedule': crontab(minute=59, hour=23, day_of_week=0),
        # 'schedule': crontab(minute='*/10'),
    },
    'run-every-month': {
        'task': 'monos.celery_scheduled_tasks.summarize_monthly',
        'schedule': crontab(minute=1, hour=0, day_of_month=1),
        # 'schedule': crontab(minute='*/10'),
    },
    'run-every-month-image': {
        'task': 'monos.celery_scheduled_tasks.update_fb_image',
        'schedule': crontab(minute=1, hour=0, day_of_month=1),
    },
    'run-every-day-buman-midnight': {
        'task': 'monos.celery_scheduled_tasks.buman_it_every_midnight',
        'schedule': crontab(minute=0, hour=15),
    },

}

app.conf.timezone = 'Asia/Ulaanbaatar'

@app.task(bind=True)
def debug_task(self):
    """
    debug
    """
    print('Request: {0!r}'.format(self.request))
