import threading
import time
from datetime import datetime
import multiprocessing
import os
# я понимаю что так нельзя, но я не смог запустить без этого celery worker
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoProject.settings")
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import requests as r

from .models import Url

connection_timeout = 10
timeout = 200


def time_processing():
    """
    This func check's datetime from db and if past more than variable timeout,
    add in list urls_to_update urls which need to update
    """
    urls = Url.objects.all()
    urls_to_update = []
    for url in urls:
        # TODO refactor with objects(filter=)
        if (datetime.now() - url.last_check_time).seconds > timeout:
            urls_to_update.append(url)

    if urls_to_update:
        try:
            with multiprocessing.Pool() as p:
               p.map(check_old_url, urls_to_update)
        except Exception as e:
            print(e)


def process_new_url(url: str):
    """Adding new url in database"""
    # creating new model with null values
    Url.objects.create(
        url=url,
        last_check_time=None,
        status_code=0,
        status=None,
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
        process_new_url(url)


def send_request(url: Url):
    """Get request to site"""
    current_time = datetime.now()
    error = None
    status = 'ok'
    try:
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
        return {'url': url, 'last_check_time': current_time, 'status_code': None, 'status': status, 'error': e,
                'final_url': None}
