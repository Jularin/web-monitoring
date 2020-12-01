from .models import Url
import requests as r
from datetime import datetime
import threading
import time


connection_timeout = 10
max_threads_count = 100
timeout = 200


def time_processing():
    """This func check's datetime from db and if past more than variable timeout,
    add in list urls_to_update urls which need to update"""
    models_in_db = Url.objects.all()
    data = [models_in_db[x] for x in range(len(models_in_db))]
    urls_to_update = []
    for i in range(len(models_in_db)):
        url_last_check_time = data[i].last_check_time
        if (datetime.now() - datetime(  # *args where args it is a list with int of time
                *list(map(int, url_last_check_time[:url_last_check_time.index(" ")].split("-"))) +
                 list(map(int, url_last_check_time[url_last_check_time.index(" ") + 1:].split(":"))))
        ).seconds > timeout:  # if time from last check more than variable timeout
            urls_to_update.append(data[i])
    for url in urls_to_update:
        while threading.active_count() > max_threads_count:
            time.sleep(10)  # script sleeping
        check_old_url(url)


# TODO add logging!
def check_new_site(url: str):
    """Get request to site"""
    Url.objects.create(url=url, last_check_time='1970-01-01 00:00:00', status_code=0,
                       status='null', error='null', final_url='null')  # creating new model with null values


def check_old_url(url: Url):
    result = send_request(url)
    url.last_check_time = result['last_check_time']
    url.status_code = result['status_code']
    url.status = result['status']
    url.final_url = result['final_url']
    url.error = result['error']
    url.save()


def add_new_url_in_db(urls):
    for url in urls:
        while threading.active_count() > max_threads_count:
            time.sleep(10)  # script sleeping
        threading.Thread(target=check_new_site, args=[url]).start()  # creating thread


def checking_in_db(url):
    data = Url.objects.all()
    for url_in_db in list(data[x].url for x in range(len(data))):
        if url_in_db == url:
            return True
    return False


def send_request(url: Url):
    """Get request to site"""
    current_time = str(datetime.now())[:-7]
    error = 'null'
    status = 'ok'
    try:
        if not checking_in_db(url):
            response = r.get(url.url, allow_redirects=True, timeout=connection_timeout)
            try:
                response.raise_for_status()  # trying call error
            except Exception as e:
                status = 'error'
                error = e
            return {'url': url, 'last_check_time': current_time, 'status_code': response.status_code, 'status': status,
                    'error': error,
                    'final_url': response.url}

    except Exception as e:
        status = 'error'
        print(e)
        return {'url': url, 'last_check_time': current_time, 'status_code': 'null', 'status': status, 'error': e,
                'final_url': 'null'}
