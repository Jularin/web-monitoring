"""
#To run celery:
#celery -A tasks worker
#celery -A tasks beat
"""
import celery
from datetime import datetime
import time
import threading

import os
from django.core.wsgi import get_wsgi_application
os.environ['DJANGO_SETTINGS_MODULE'] = 'djangoProject.settings'
application = get_wsgi_application()
from monitoring.models import Url
import requests as r
from monitoring.views import time_processing


app = celery.Celery('tasks')


@app.task
def check():
    time_processing()


app.conf.beat_schedule = {
    'urls-update': {
        'task': 'tasks.check',
        'schedule': 120.0
    }
}
