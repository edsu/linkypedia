import re

from django.core.management.base import BaseCommand

from linkypedia import wikipedia


class Command(BaseCommand):

    def handle(self, filename, **options):
        wikipedia.load_links_dump(filename)
