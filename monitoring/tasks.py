"""
To run celery:
celery -A tasks worker
celery -A tasks beat
"""
import os

from djangoProject.celery import app

from monitoring.services import time_processing


@app.task
def check():
    time_processing()


"""
Подходы по распараллеливанию

1. Celery Beat + отдельные таски (.delay):
- запускается beat
- создает кучу тасков на каждый сайт
- таски выполняются параллельно с помощью celery

2. Celery Beat + multiprocessing (multiprocessing.Pool().map())
- запускается beat
- в мультипроцессинге выполняет операции

лучше второй способ, потому что мы не загружаем брокер сообщений
"""
