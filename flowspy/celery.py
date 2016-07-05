from __future__ import absolute_import

import os

from celery import Celery
from celery.schedules import crontab

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowspy.settings')

app = Celery('flowspy')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(settings.INSTALLED_APPS, related_name='tasks')

app.conf.CELERYBEAT_SCHEDULE = {
    "every-day-sync": {
        "task": "flowspec.tasks.check_sync",
        "schedule": crontab(minute=01, hour=01),
        "args": (),
    },
    "notify-expired": {
        "task": "flowspec.tasks.notify_expired",
        "schedule": crontab(minute=01, hour=02),
        "args": (),
    },
}
