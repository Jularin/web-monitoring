import threading
import time
from datetime import datetime

import requests as r

from .models import Url


connection_timeout = 10
max_threads_count = 100
timeout = 200


def time_processing():
    """
    This func check's datetime from db and if past more than variable timeout,
    add in list urls_to_update urls which need to update
    """
    urls = Url.objects.all()
    urls_to_update = []
    for url in urls:
        if (datetime.now() - url.last_check_time).seconds > timeout:
            urls_to_update.append(url)

    # TODO celery
    for url in urls_to_update:
        while threading.active_count() > max_threads_count:
            time.sleep(10)  # script sleeping
        check_old_url(url)


def process_new_url(url: str):
    """Adding new url in database"""
    # creating new model with null values
    Url.objects.create(
        url=url,
        last_check_time=None,
        status_code=0,
        status=None,  # TODO refactor to None
        error=None,
        final_url=None
    )


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
        threading.Thread(target=process_new_url, args=[url]).start()  # creating thread


def checking_in_db(url):
    return Url.objects.filter(url=url).exists()


def send_request(url: Url):
    """Get request to site"""
    current_time = datetime.now()
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
