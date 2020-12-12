from django.core.management.base import BaseCommand, CommandError

from monitoring.services import time_processing


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        pass
