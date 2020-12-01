"""
#To run celery:
#celery -A tasks worker
#celery -A tasks beat
"""
import celery
import os
from django.core.wsgi import get_wsgi_application
os.environ['DJANGO_SETTINGS_MODULE'] = 'djangoProject.settings'
application = get_wsgi_application()
from monitoring.requests_to_urls import time_processing


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
