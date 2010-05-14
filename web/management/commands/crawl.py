import time
import logging
import urlparse

from django.core.management.base import BaseCommand

from linkypedia import links
from linkypedia.web import models as m

logging.basicConfig(
        filename="crawl.log", 
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s")

class Command(BaseCommand):

    def handle(self, **options):
        logging.info("starting crawl daemon")
        while True:
            # look for new websites to crawl
            new_websites = m.Website.objects.filter(crawls=None)
            for website in new_websites:
                logging.info("found new website to crawl: %s" % website.name)
                crawl = m.Crawl(website=website)
                crawl.run()
            time.sleep(10)
