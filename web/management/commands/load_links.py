import logging
import urlparse

from django.core.management.base import BaseCommand

from linkypedia import links
from linkypedia.web import models as m

logging.basicConfig(
        filename="load-links.log", 
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s")

class Command(BaseCommand):

    def handle(self, website_url, **options):
        website, created = m.Website.objects.get_or_create(url=website_url)
        crawl = m.Crawl(website=website)
        crawl.run()
