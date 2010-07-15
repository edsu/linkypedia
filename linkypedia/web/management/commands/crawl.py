import time
import logging
import datetime
import urlparse

from django.core.management.base import BaseCommand

from linkypedia.crawl import crawl
from linkypedia.web import models as m

logging.basicConfig(
        filename="crawl.log", 
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s")

class Command(BaseCommand):

    def handle(self, **options):
        logging.info("starting crawl daemon")
        while True:
            recently = datetime.datetime.now() - datetime.timedelta(hours=4)
            websites = m.Website.objects.all()
            for website in websites:
                if website.last_crawl() \
                    and website.last_crawl().finished > recently:
                    continue
                logging.info("found a website to crawl: %s" % website.name)
                crawl(website)
            time.sleep(10)
