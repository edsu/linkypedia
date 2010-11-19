from django.core.management.base import BaseCommand

from linkypedia.wikipedia import start_update_stream

class Command(BaseCommand):

    def handle(self, **options):
        start_update_stream("linkypedia")

