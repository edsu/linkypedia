import datetime
import logging

from django.db import models as m

from linkypedia import links

class Link(m.Model):
    created = m.DateTimeField(auto_now=True)
    source = m.TextField()
    target = m.TextField()
    host = m.ForeignKey('Host', related_name='links')

class Host(m.Model):
    name = m.TextField(primary_key=True)
    created = m.DateTimeField(auto_now=True)

    def last_checked(self):
        if self.crawls.count() > 0:
            return self.crawls.all()[0].started
        return None

class Crawl(m.Model):
    started = m.DateTimeField(null=True)
    finished = m.DateTimeField(null=True)
    host = m.ForeignKey('Host', related_name='crawls')

    def run(self):
        """
        Execute a crawl, but only if it hasn't been started already.
        """
        if self.started:
            loging.error("crawl %s for %s already started" % (crawl.id,
                crawl.host.name))
            raise Exception("crawl already started")

        logging.info("starting crawl for %s" % self.host.name)
        self.started = datetime.datetime.now()
        self.save()
        for source, target in links.links(self.host.name):
            link, created = Link.objects.get_or_create(
                    host=self.host, 
                    source=source,
                    target=target)
            if created:
                logging.info("created link: %s -> %s" % (source, target))
            else:
                logging.info("updated link: %s -> %s" % (source, target))
            link.last_checked = datetime.datetime.now()
        self.finshed = datetime.datetime.now()
        self.save()
        logging.info("finished crawl for %s" % self.host.name)

    class Meta:
        ordering = ['-started', '-finished']
