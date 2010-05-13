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

    def handle(self, target, **options):
        host_name = urlparse.urlparse(target).netloc
        host, created = m.Host.objects.get_or_create(name=host_name)
        crawl = m.Crawl(host=host)
        crawl.run()
