import time
import logging
import datetime
import urlparse

from django.db.models import Max
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

        logging.info("setting any unfinished crawls to finished")
        for c in m.Crawl.objects.filter(finished=None):
            c.finished = datetime.datetime.now()
            c.save()

        # crawl brand new websites first
        for new_website in m.Website.objects.filter(crawls=None):
            logging.info("new website to crawl: %s" % new_website.name)
            crawl(new_website)

        # now crawl the rest
        websites = m.Website.objects.all()
        websites = websites.annotate(most_recent_crawl=Max("crawls__started"))
        websites = websites.order_by("most_recent_crawl")
        for website in websites:
            crawl(website)
