from django.shortcuts import render
from .models import Url
from .forms import UrlForm
import requests as r
from datetime import datetime
import threading
import time
from django.views.decorators.csrf import csrf_exempt


def index(request):
    urls = Url.objects.all()
    return render(request, 'monitoring/index.html', {'title': 'Main page', 'urls': urls})


@csrf_exempt  # чтобы Post запрос без csrf token
def add(request):
    if request.method == 'POST':
        form = UrlForm(request.POST)
        Monitoring1 = Monitoring(urls=form.data['url'].split(), timeout_between_requests=10, connection_timeout=10,
                                 max_threads_count=100, data=Url.objects.all())
        Monitoring1.add_new_url_in_db()
    form = UrlForm()
    context = {
        'form': form
    }
    return render(request, 'monitoring/urls.html', context)


# replace this class to tasks.py
class Monitoring:
    def __init__(self, timeout_between_requests, urls, connection_timeout, max_threads_count,
                 data):
        self.timeout = timeout_between_requests
        self.urls = urls
        self.data = data
        self.connection_timeout = connection_timeout
        self.max_threads_count = max_threads_count

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
                urls_to_update.append(data[i].url)
        for url in urls_to_update:
            while threading.active_count() > self.max_threads_count:
                time.sleep(10)  # script sleeping
            self.check_site(str(url))

    # TODO add logging!
    def check_site(self, url: str):
        """Get request to site"""
        #        logging.debug('Checking {}'.format(url))
        current_time = str(datetime.now())[:-7]
        error = 'None'
        status = 'ok'
        try:
            if not self.checking_in_db(url):
                response = r.get(url, allow_redirects=True, timeout=self.connection_timeout)
                try:
                    response.raise_for_status()  # trying call error
                except Exception as e:
                    status = 'error'
                    error = e

                my_url = Url(url=url, last_check_time=current_time, status_code=response.status_code,
                             status=status, error=error, final_url=response.url)
                my_url.save()
                self.data = Url.objects.all()  # updating data
        except Exception as e:
            print(e)

    def add_new_url_in_db(self):
        for url in self.urls:
            while threading.active_count() > self.max_threads_count:
                time.sleep(10)  # script sleeping
            threading.Thread(target=self.check_site, args=[url]).start()  # creating thread

    def checking_in_db(self, url):
        for url_in_db in list(self.data[x].url for x in range(len(self.data))):
            if url_in_db == url:
                return True
        return False



