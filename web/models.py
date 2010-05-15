import re
import logging
import datetime
import urlparse

import rdflib
from django.db import models as m

from linkypedia import links

class Link(m.Model):
    created = m.DateTimeField(auto_now=True)
    source = m.TextField()
    target = m.TextField()
    website = m.ForeignKey('Website', related_name='links')
    resource_type = m.TextField(null=True)
    resource_checked = m.DateTimeField()

    def fetch_resource_type(self):
        path = urlparse.urlparse(self.source).path
        match = re.match(r'/wiki/([^:]+)$', path)
        if match:
            self.resource_checked = datetime.datetime.now()
            dbpedia = rdflib.URIRef("http://dbpedia.org/resource/%s" %
                    match.group(1))
            logging.info("fetching info from dbpedia: %s" % dbpedia)
            graph = rdflib.Graph()
            graph.parse(dbpedia)
            dbtype = graph.value(subject=dbpedia, predicate=rdflib.RDF.type)
            if dbtype:
                self.resource_type = dbtype.split('/')[-1]
                self.save()
                logging.info("got resource type of %s" % self.resource_type)
            else:
                logging.warn("unable to get resource type for %s" % dbpedia)

class Website(m.Model):
    url = m.TextField()
    name = m.TextField()
    favicon_url = m.TextField()
    created = m.DateTimeField(auto_now=True)

    @m.permalink
    def get_absolute_url(self):
        return ('website', (), {'website_id': str(self.id)})

    def last_checked(self):
        if self.crawls.filter(finished__isnull=False).count() > 0:
            return self.crawls.all()[0].finished
        return None

class Crawl(m.Model):
    started = m.DateTimeField(null=True)
    finished = m.DateTimeField(null=True)
    website = m.ForeignKey('Website', related_name='crawls')

    def run(self):
        """
        Execute a crawl, but only if it hasn't been started already.
        """
        if self.started:
            loging.error("crawl %s for %s already started" % (crawl.id,
                crawl.website.url))
            raise Exception("crawl already started")

        logging.info("starting crawl for %s" % self.website.url)
        self.started = datetime.datetime.now()
        self.save()
        for source, target in links.links(self.website.url):
            link, created = Link.objects.get_or_create(
                    website=self.website, 
                    source=source,
                    target=target)
            if created:
                logging.info("created link: %s -> %s" % (source, target))
            else:
                logging.info("updated link: %s -> %s" % (source, target))
            link.last_checked = datetime.datetime.now()
            link.save()

        self.finished = datetime.datetime.now()
        self.save()
        logging.info("finished crawl for %s" % self.website.url)

    class Meta:
        ordering = ['-started', '-finished']
