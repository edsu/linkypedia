import time
import logging
import urlparse

from django.core.management.base import BaseCommand

from linkypedia import links
from linkypedia.web import models as m

logging.basicConfig(
        filename="dbpedia.log", 
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s")

class Command(BaseCommand):

    def handle(self, **options):
        logging.info("starting dbpedia daemon")
        while True:
            # look for new websites to crawl
            new_links = m.Link.objects.filter(resource_type=None)
            for link in new_links:
                link.fetch_resource_type()
            time.sleep(10)
