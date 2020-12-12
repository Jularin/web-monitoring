from django.core.management.base import BaseCommand, CommandError
import time

from monitoring.services import time_processing


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        while 1:
            time_processing()
            time.sleep(60)
