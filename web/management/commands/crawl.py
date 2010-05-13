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
            # look for new hosts to crawl
            new_hosts = m.Host.objects.filter(crawls=None)
            for host in new_hosts:
                logging.info("found new host to crawl: %s" % host.name)
                crawl = m.Crawl(host=host)
                crawl.run()
            time.sleep(10)
