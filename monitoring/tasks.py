import celery
from datetime import datetime
import time
import threading
'''
import os
from django.core.wsgi import get_wsgi_application
os.environ['DJANGO_SETTINGS_MODULE'] = 'djangoProject.settings'
application = get_wsgi_application()
'''
from .models import Url
import requests as r


app = celery.Celery('tasks')


@app.task
def check():
    updating_class = UrlUpdating(timeout=15, max_threads_count=100, connection_timeout=10)
    updating_class.time_processing()


app.conf.beat_schedule = {
    'run-me-every-ten-seconds': {
        'task': 'tasks.check',
        'schedule': 10.0
    }
}


class UrlUpdating:
    def __init__(self, timeout, max_threads_count, connection_timeout):
        self.connection_timeout = connection_timeout
        self.max_threads_count = max_threads_count
        self.timeout = timeout
        self.data = Url.objects.all()

    def time_processing(self):
        """This func check's datetime from db and if past more than variable timeout,
        add in list urls_to_update urls which need to update"""
        data = [self.data[x] for x in range(len(self.data))]
        urls_to_update = []
        for i in range(len(self.data)):
            url_last_check_time = data[i].last_check_time
            if (datetime.now() - datetime(  # *args where args it is a list with int of time
                    *list(map(int, url_last_check_time[:url_last_check_time.index(" ")].split("-"))) +
                     list(map(int, url_last_check_time[url_last_check_time.index(" ") + 1:].split(":"))))
            ).seconds > self.timeout:  # if time from last check more than variable timeout
                urls_to_update.append(data[i])  # add Url class into urls_to_update
        for url in urls_to_update:
            while threading.active_count() > self.max_threads_count:
                time.sleep(10)  # script sleeping
            self.check_site(url)

    def check_site(self, url: Url):
        """Get request to site"""
        #        logging.debug('Checking {}'.format(url))
        current_time = str(datetime.now())[:-7]
        error = 'None'
        status = 'ok'
        try:
            response = r.get(url.url, allow_redirects=True, timeout=self.connection_timeout)
            try:
                response.raise_for_status()  # trying call error
            except Exception as e:
                status = 'error'
                error = e

            url.last_check_time = current_time
            url.status_code = response.status_code
            url.status = status
            url.final_url = response.url
            url.error = error
            url.save()
            self.data = Url.objects.all()  # updating data
        except Exception as e:
            print(e)
