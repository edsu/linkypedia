import urlparse

from django.core.management.base import BaseCommand

from linkypedia import links
from linkypedia.web import models as m

class Command(BaseCommand):

    def handle(self, target, **options):
        host_name = urlparse.urlparse(target).netloc
        try:
            host = m.Host.objects.get(name=host_name)
        except m.Host.DoesNotExist:
            host = m.Host(name=host_name)
            host.save()

        crawl = m.Crawl(host=host)
        crawl.save()

        for source, target in links.links(host.name):
            try:
                link = m.Link.objects.get(host=host, source=source,
                        target=target)
            except m.Link.DoesNotExist:
                m.Link.objects.create(host=host, source=source, target=target)
