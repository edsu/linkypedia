import time
import logging
import datetime
import urlparse

from django.core.management.base import BaseCommand

from linkypedia.wikipedia.crawl import crawl
from linkypedia.web import models as m

logging.basicConfig(
        filename="crawl.log", 
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s")

class Command(BaseCommand):

    def handle(self, **options):
        logging.info("starting crawl daemon")

        logging.info("setting any unfinished crawls to finished")
        for c in m.Crawl.objects.filter(finished=None):
            c.finished = datetime.datetime.now()
            c.save()

        while True:
           
            # look for websites that haven't been updated in the last 4 hrs 
            # TODO: make 4 hours configurable in settings.py

            recently = datetime.datetime.now() - datetime.timedelta(hours=4)
            for website in m.Website.objects.all():

                # first look for any new websites that haven't been crawled yet
                # in the interim, since updating a bunch of sites could
                # cause new sites not to be crawled for quite a bit of time
                for new_website in m.Website.objects.filter(crawls=None):
                    logging.info("new website to crawl: %s" % new_website.name)
                    crawl(new_website)

                # now crawl any sites that need to be updated 
                last_crawl = website.last_crawl()
                if last_crawl and last_crawl.finished < recently:
                    logging.info("refreshing links for %s" % website.name)
                    crawl(website)

                # TODO: should be configurable in settings.py
                time.sleep(10)
