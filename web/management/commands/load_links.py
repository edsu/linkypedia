import urlparse

from django.core.management.base import BaseCommand

from linkypedia import links
from linkypedia.web import models as m

class Command(BaseCommand):

    def handle(self, site, **options):
        for source, target in links.links(site):
            print "%s -> %s" % (source, target)
            host = urlparse.urlparse(target).netloc
            m.Link.objects.create(host=host, source=source, target=target)


